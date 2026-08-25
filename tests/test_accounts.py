from __future__ import annotations

import json
from email.message import Message
from pathlib import Path

import pytest

from ecommerce_ai_skills.runtime.accounts import MarketplaceAccountService
from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.auth import AuthService
from ecommerce_ai_skills.runtime.errors import AuthorizationError, NotFoundError, ValidationError
from ecommerce_ai_skills.runtime.storage import Database


AMAZON_CONFIG = {
    "region": "na",
    "marketplace_ids": ["ATVPDKIKX0DER"],
    "lwa_client_id_ref": "AMAZON_CLIENT_ID",
    "lwa_client_secret_ref": "AMAZON_CLIENT_SECRET",
    "lwa_refresh_token_ref": "AMAZON_REFRESH_TOKEN",
}
SHOPIFY_CONFIG = {
    "shop_domain": "demo.myshopify.com",
    "api_version": "2025-10",
    "credential_ref": "SHOPIFY_TOKEN",
}


def principals(tmp_path: Path):
    db = Database(tmp_path / "runtime.sqlite")
    tenant, owner_id = db.create_tenant("A", "owner@example.com")
    auth = AuthService(db)
    owner = auth.authenticate(auth.issue_key(tenant, owner_id))
    users = {}
    for role in ("admin", "operator", "viewer"):
        user_id = db.create_user(tenant, f"{role}@example.com", role)
        users[role] = auth.authenticate(auth.issue_key(tenant, user_id))
    return db, auth, owner, users


def test_schema_v10_connector_accounts_migrate_with_safe_health_defaults(tmp_path: Path) -> None:
    path = tmp_path / "runtime.sqlite"
    db = Database(path)
    tenant, _ = db.create_tenant("A", "owner@example.com")
    db.add_connector_account(tenant, "shopify", "store", SHOPIFY_CONFIG)
    with db.transaction() as conn:
        conn.execute("ALTER TABLE connector_accounts RENAME TO connector_accounts_v11")
        conn.execute(
            """CREATE TABLE connector_accounts (
               id TEXT PRIMARY KEY,
               tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
               provider TEXT NOT NULL,
               external_account_id TEXT NOT NULL,
               config_json TEXT NOT NULL,
               created_at TEXT NOT NULL,
               UNIQUE(tenant_id, provider, external_account_id))"""
        )
        conn.execute(
            """INSERT INTO connector_accounts
               SELECT id,tenant_id,provider,external_account_id,config_json,created_at
               FROM connector_accounts_v11"""
        )
        conn.execute("DROP TABLE connector_accounts_v11")
        conn.execute("UPDATE runtime_meta SET value='10' WHERE key='schema_version'")
    migrated = Database(path)
    account = migrated.list_connector_accounts(tenant)[0]
    assert migrated.readiness()["schema_version"] == 12
    assert account["updated_at"] == account["created_at"]
    assert account["health_status"] == "unchecked"


def test_accounts_persist_and_are_redacted_from_responses_and_audit(tmp_path: Path) -> None:
    db, auth, owner, _ = principals(tmp_path)
    service = MarketplaceAccountService(db, auth)
    created = service.create(owner, "shopify", "store", SHOPIFY_CONFIG, "req-create")
    assert created["credential_refs"] == {"credential_ref": "present"}
    assert "config" not in created
    assert "SHOPIFY_TOKEN" not in json.dumps(created)
    assert service.get(owner, created["id"])["id"] == created["id"]
    assert Database(db.path).list_connector_accounts(owner.tenant_id)[0]["id"] == created["id"]
    assert "SHOPIFY_TOKEN" not in json.dumps(db.list_audit(owner.tenant_id))


def test_rbac_and_cross_tenant_accounts_fail_closed(tmp_path: Path) -> None:
    db, auth, owner, users = principals(tmp_path)
    service = MarketplaceAccountService(db, auth)
    account = service.create(owner, "shopify", "store", SHOPIFY_CONFIG, "req")
    with pytest.raises(AuthorizationError):
        service.create(users["viewer"], "shopify", "other", SHOPIFY_CONFIG, "req")
    with pytest.raises(AuthorizationError):
        service.health_check(users["viewer"], account["id"], "req")
    other_tenant, other_owner_id = db.create_tenant("B", "b@example.com")
    other = auth.authenticate(auth.issue_key(other_tenant, other_owner_id))
    with pytest.raises(NotFoundError):
        service.get(other, account["id"])
    with pytest.raises(NotFoundError):
        service.health_check(other, account["id"], "req")


@pytest.mark.parametrize(
    "config,match",
    [
        ({**AMAZON_CONFIG, "marketplace_ids": ["A1F83G8C2ARO7P"]}, "does not belong"),
        ({**AMAZON_CONFIG, "marketplace_ids": ["ATVPDKIKX0DER"] * 2}, "duplicates"),
        ({**AMAZON_CONFIG, "marketplace_ids": ["UNKNOWN"]}, "unknown"),
    ],
)
def test_amazon_marketplace_directory_validation(tmp_path: Path, config: dict, match: str) -> None:
    db, auth, owner, _ = principals(tmp_path)
    with pytest.raises(ValidationError, match=match):
        MarketplaceAccountService(db, auth).create(
            owner, "amazon_spapi", "seller", config, "req"
        )


@pytest.mark.parametrize(
    "config",
    [
        {**SHOPIFY_CONFIG, "shop_domain": "https://demo.myshopify.com"},
        {**SHOPIFY_CONFIG, "api_version": "latest"},
        {**SHOPIFY_CONFIG, "access_token": "secret"},
        {**SHOPIFY_CONFIG, "unknown": "value"},
    ],
)
def test_shopify_and_strict_secret_validation(tmp_path: Path, config: dict) -> None:
    db, auth, owner, _ = principals(tmp_path)
    with pytest.raises(ValidationError):
        MarketplaceAccountService(db, auth).create(
            owner, "shopify", "store", config, "req"
        )


class Response:
    status = 200
    headers = {}

    def __init__(self, body: dict):
        self.body = json.dumps(body).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, *_args):
        return self.body


def test_shopify_health_states_persist_and_update_resets(tmp_path: Path) -> None:
    db, auth, owner, users = principals(tmp_path)
    healthy = MarketplaceAccountService(
        db,
        auth,
        environ={"SHOPIFY_TOKEN": "token"},
        transport=lambda request, timeout: Response({"shop": {"id": 1}}),
    )
    account = healthy.create(owner, "shopify", "store", SHOPIFY_CONFIG, "create")
    result = healthy.health_check(users["operator"], account["id"], "health")
    assert result["health_status"] == "healthy"
    assert db.get_connector_account(owner.tenant_id, account["id"])["health_status"] == "healthy"
    updated = healthy.update(
        owner, account["id"], "store-2", SHOPIFY_CONFIG, "update"
    )
    assert updated["health_status"] == "unchecked"
    assert updated["health_checked_at"] is None
    unhealthy = MarketplaceAccountService(
        db,
        auth,
        environ={"SHOPIFY_TOKEN": "token"},
        transport=lambda request, timeout: Response({"not_shop": {}}),
    )
    failed = unhealthy.health_check(users["operator"], account["id"], "unhealthy")
    assert failed["health_status"] == "unhealthy"
    assert failed["health_error_code"] == "external_service_error"
    missing = MarketplaceAccountService(db, auth, environ={})
    assert missing.health_check(users["operator"], account["id"], "missing")["health_status"] == "misconfigured"


def test_amazon_health_uses_lwa_and_authorized_marketplaces(tmp_path: Path) -> None:
    db, auth, owner, users = principals(tmp_path)
    seen = []

    def transport(request, timeout):
        seen.append((request.method, request.full_url))
        if request.full_url == "https://api.amazon.com/auth/o2/token":
            return Response({"access_token": "access"})
        return Response(
            {"payload": [{"marketplace": {"id": "ATVPDKIKX0DER"}}]}
        )

    service = MarketplaceAccountService(
        db,
        auth,
        environ={
            "AMAZON_CLIENT_ID": "id",
            "AMAZON_CLIENT_SECRET": "secret",
            "AMAZON_REFRESH_TOKEN": "refresh",
        },
        transport=transport,
    )
    account = service.create(owner, "amazon_spapi", "seller", AMAZON_CONFIG, "create")
    checked = service.health_check(users["operator"], account["id"], "health")
    assert checked["health_status"] == "healthy"
    assert seen == [
        ("POST", "https://api.amazon.com/auth/o2/token"),
        ("GET", "https://sellingpartnerapi-na.amazon.com/sellers/v1/marketplaceParticipations"),
    ]


def test_connector_api_routes_and_catalog(tmp_path: Path) -> None:
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    bootstrap = app.bootstrap("A", "owner@example.com")

    class Handler(_Handler):
        def __init__(self, method: str, path: str, body: dict | None = None):
            self.path = path
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {bootstrap['api_key']}"
            self.body = body or {}
            self.out = None
            self.method = method

        @property
        def app(self):
            return app

        def _body(self):
            return self.body

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value)

        def run(self):
            getattr(self, f"do_{self.method}")()
            return self.out

    created = Handler(
        "POST",
        "/v1/connectors",
        {"provider": "shopify", "external_account_id": "store", "config": SHOPIFY_CONFIG},
    ).run()
    assert created[0] == 201
    account_id = created[1]["id"]
    assert Handler("GET", "/v1/connectors").run()[1]["connectors"][0]["id"] == account_id
    assert Handler("GET", f"/v1/connectors/{account_id}").run()[0] == 200
    assert Handler("PATCH", f"/v1/connectors/{account_id}", {"config": SHOPIFY_CONFIG}).run()[0] == 200
    assert Handler("POST", f"/v1/connectors/{account_id}/health-check").run()[1]["health_status"] == "misconfigured"
    catalog = Handler("GET", "/v1/catalog").run()[1]
    assert {item["id"] for item in catalog["connector_providers"]} == {"amazon_spapi", "shopify"}
    assert any(item["id"] == "ATVPDKIKX0DER" for item in catalog["amazon_marketplaces"])
