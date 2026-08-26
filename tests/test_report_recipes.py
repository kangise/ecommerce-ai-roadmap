from __future__ import annotations

from email.message import Message
from pathlib import Path

import pytest

from ecommerce_ai_skills.demo_seed import seed_demo_database
from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.auth import AuthService
from ecommerce_ai_skills.runtime.errors import AuthorizationError, ConflictError, NotFoundError, ValidationError
from ecommerce_ai_skills.runtime.report_recipes import REPORT_RECIPE_CATALOG, ReportRecipeService
from ecommerce_ai_skills.runtime.storage import Database


NEXT_RUN = "2026-09-01T02:00:00+00:00"


def fixture(tmp_path: Path):
    db = Database(tmp_path / "runtime.sqlite")
    tenant, owner_id = db.create_tenant("A", "owner@example.com")
    auth = AuthService(db)
    owner = auth.authenticate(auth.issue_key(tenant, owner_id))
    principals = {}
    for role in ("operator", "viewer"):
        user_id = db.create_user(tenant, f"{role}@example.com", role)
        principals[role] = auth.authenticate(auth.issue_key(tenant, user_id))
    amazon_id = db.add_connector_account(
        tenant,
        "amazon_spapi",
        "seller",
        {
            "region": "na",
            "marketplace_ids": ["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"],
            "lwa_client_id_ref": "AMAZON_CLIENT_ID",
            "lwa_client_secret_ref": "AMAZON_CLIENT_SECRET",
            "lwa_refresh_token_ref": "AMAZON_REFRESH_TOKEN",
        },
    )
    shopify_id = db.add_connector_account(
        tenant,
        "shopify",
        "store",
        {
            "shop_domain": "demo.myshopify.com",
            "api_version": "2026-07",
            "credential_ref": "SHOPIFY_TOKEN",
        },
    )
    return db, auth, owner, principals, amazon_id, shopify_id


def values(**overrides):
    result = {
        "name": "Daily sales and traffic",
        "recipe_key": "sales_traffic_daily",
        "marketplace_ids": ["ATVPDKIKX0DER"],
        "interval_minutes": 1440,
        "lookback_days": 7,
        "enabled": True,
        "next_run_at": NEXT_RUN,
    }
    result.update(overrides)
    return result


def test_v11_migration_creates_report_recipe_table(tmp_path: Path) -> None:
    path = tmp_path / "runtime.sqlite"
    db = Database(path)
    with db.transaction() as conn:
        conn.execute("DROP TABLE report_recipes")
        conn.execute("UPDATE runtime_meta SET value='11' WHERE key='schema_version'")
    migrated = Database(path)
    assert migrated.readiness()["schema_version"] == 19
    with migrated.connect() as conn:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(report_recipes)")}
    assert {"connector_account_id", "marketplace_ids_json", "lookback_days"} <= columns


def test_recipe_persists_returns_derived_types_and_audits(tmp_path: Path) -> None:
    db, auth, _, principals, amazon_id, _ = fixture(tmp_path)
    service = ReportRecipeService(db, auth)
    created = service.create(
        principals["operator"], amazon_id, **values(), request_id="create"
    )
    assert created["amazon_report_type"] == "GET_SALES_AND_TRAFFIC_REPORT"
    assert created["evidence_report_type"] == "amazon_business_report"
    assert "config" not in created
    reopened = ReportRecipeService(Database(db.path), auth).get(
        principals["viewer"], created["id"]
    )
    assert reopened["marketplace_ids"] == ["ATVPDKIKX0DER"]
    assert db.list_audit(principals["operator"].tenant_id)[0]["action"] == "marketplace_report_recipe.create"


def test_rbac_tenant_isolation_and_non_amazon_rejection(tmp_path: Path) -> None:
    db, auth, owner, principals, amazon_id, shopify_id = fixture(tmp_path)
    service = ReportRecipeService(db, auth)
    with pytest.raises(AuthorizationError):
        service.create(principals["viewer"], amazon_id, **values(), request_id="denied")
    with pytest.raises(ValidationError, match="amazon_spapi"):
        service.create(principals["operator"], shopify_id, **values(), request_id="shopify")
    recipe = service.create(owner, amazon_id, **values(), request_id="create")
    other_tenant, other_owner_id = db.create_tenant("B", "b@example.com")
    other = auth.authenticate(auth.issue_key(other_tenant, other_owner_id))
    with pytest.raises(NotFoundError):
        service.get(other, recipe["id"])
    with pytest.raises(NotFoundError):
        service.update(other, recipe["id"], **values(), request_id="cross-tenant")


@pytest.mark.parametrize(
    "override,match",
    [
        ({"name": ""}, "name"),
        ({"recipe_key": "custom"}, "recipe_key"),
        ({"marketplace_ids": []}, "non-empty"),
        ({"marketplace_ids": ["ATVPDKIKX0DER"] * 2}, "duplicates"),
        ({"marketplace_ids": ["A1F83G8C2ARO7P"]}, "subset"),
        ({"interval_minutes": 59}, "interval_minutes"),
        ({"interval_minutes": 43_201}, "interval_minutes"),
        ({"lookback_days": 0}, "lookback_days"),
        ({"lookback_days": 31}, "lookback_days"),
        ({"enabled": 1}, "enabled"),
        ({"next_run_at": "2026-09-01T02:00:00"}, "timezone"),
    ],
)
def test_recipe_validation(tmp_path: Path, override: dict, match: str) -> None:
    db, auth, _, principals, amazon_id, _ = fixture(tmp_path)
    with pytest.raises(ValidationError, match=match):
        ReportRecipeService(db, auth).create(
            principals["operator"],
            amazon_id,
            **values(**override),
            request_id="invalid",
        )


def test_unique_name_and_full_update_survive_refresh(tmp_path: Path) -> None:
    db, auth, _, principals, amazon_id, _ = fixture(tmp_path)
    service = ReportRecipeService(db, auth)
    recipe = service.create(principals["operator"], amazon_id, **values(), request_id="create")
    with pytest.raises(ConflictError):
        service.create(principals["operator"], amazon_id, **values(), request_id="duplicate")
    updated = service.update(
        principals["operator"],
        recipe["id"],
        **values(
            name="Daily returns",
            recipe_key="returns_daily",
            interval_minutes=2880,
            lookback_days=14,
            enabled=False,
            next_run_at="2026-09-02T02:00:00+00:00",
        ),
        request_id="update",
    )
    assert updated["amazon_report_type"] == "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA"
    persisted = Database(db.path).get_report_recipe(principals["operator"].tenant_id, recipe["id"])
    assert persisted["name"] == "Daily returns" and persisted["enabled"] is False


def test_api_routes_strict_body_and_catalog(tmp_path: Path) -> None:
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    bootstrap = app.bootstrap("A", "owner@example.com")
    principal = app.auth.authenticate(bootstrap["api_key"])
    amazon_id = app.db.add_connector_account(
        principal.tenant_id,
        "amazon_spapi",
        "seller",
        {
            "region": "na",
            "marketplace_ids": ["ATVPDKIKX0DER"],
            "lwa_client_id_ref": "AMAZON_CLIENT_ID",
            "lwa_client_secret_ref": "AMAZON_CLIENT_SECRET",
            "lwa_refresh_token_ref": "AMAZON_REFRESH_TOKEN",
        },
    )

    class Handler(_Handler):
        def __init__(self, method, path, body=None):
            self.path = path
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {bootstrap['api_key']}"
            self.body = body or {}
            self.method = method
            self.out = None

        @property
        def app(self): return app

        def _body(self): return self.body

        def _json(self, status, value, request_id, **kwargs): self.out = (status, value)

        def run(self):
            getattr(self, f"do_{self.method}")()
            return self.out

    body = {"connector_account_id": amazon_id, **values()}
    created = Handler("POST", "/v1/report-recipes", body).run()
    assert created[0] == 201
    recipe_id = created[1]["id"]
    assert Handler("GET", "/v1/report-recipes").run()[1]["report_recipes"][0]["id"] == recipe_id
    assert Handler("GET", f"/v1/report-recipes/{recipe_id}").run()[0] == 200
    assert Handler("PATCH", f"/v1/report-recipes/{recipe_id}", values(enabled=False)).run()[1]["enabled"] is False
    assert Handler("POST", "/v1/report-recipes", {**body, "unknown": True}).run()[0] == 422
    catalog = Handler("GET", "/v1/catalog").run()[1]["report_recipe_types"]
    assert {item["key"] for item in catalog} == set(REPORT_RECIPE_CATALOG)


def test_demo_seed_creates_four_amazon_report_recipes(tmp_path: Path) -> None:
    result = seed_demo_database(tmp_path / "demo.sqlite")
    assert result["report_recipes"] == 4
    app = RuntimeApplication(Database(result["database"]))
    owner = app.auth.authenticate(result["owner_api_key"])
    recipes = app.report_recipes.list(owner)
    assert len(recipes) == 4
    assert {recipe["recipe_key"] for recipe in recipes} == set(REPORT_RECIPE_CATALOG)
