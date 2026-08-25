from __future__ import annotations

import json
from email.message import Message
from pathlib import Path

import pytest

from ecommerce_ai_skills.runtime.accounts import MarketplaceAccountService
from ecommerce_ai_skills.runtime.ads_gates import AdsCapabilityGateService
from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.auth import AuthService
from ecommerce_ai_skills.runtime.connectors.amazon_ads import (
    AmazonAdsConnector,
    AmazonAdsHTTPError,
)
from ecommerce_ai_skills.runtime.errors import (
    AuthorizationError,
    ConflictError,
    ExternalServiceError,
    NotFoundError,
    ValidationError,
)
from ecommerce_ai_skills.runtime.storage import Database


ADS_CONFIG = {
    "region": "na",
    "profile_id": "1234567890",
    "lwa_client_id_ref": "ADS_CLIENT_ID",
    "lwa_client_secret_ref": "ADS_CLIENT_SECRET",
    "lwa_refresh_token_ref": "ADS_REFRESH_TOKEN",
}
CREDENTIALS = {
    "ADS_CLIENT_ID": "client-id",
    "ADS_CLIENT_SECRET": "client-secret",
    "ADS_REFRESH_TOKEN": "refresh-token",
}


class Response:
    def __init__(self, value, *, status=200, headers=None):
        self.status = status
        self.headers = headers or {}
        self.body = value if isinstance(value, bytes) else json.dumps(value).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, amount=-1):
        return self.body if amount < 0 else self.body[:amount]


def setup_runtime(tmp_path: Path):
    db = Database(tmp_path / "runtime.sqlite")
    tenant_id, owner_id = db.create_tenant("A", "owner@example.com")
    auth = AuthService(db)
    owner = auth.authenticate(auth.issue_key(tenant_id, owner_id))
    principals = {}
    for role in ("admin", "operator", "viewer"):
        user_id = db.create_user(tenant_id, f"{role}@example.com", role)
        principals[role] = auth.authenticate(auth.issue_key(tenant_id, user_id))
    account_id = db.add_connector_account(
        tenant_id, "amazon_ads", "ads-profile", ADS_CONFIG
    )
    return db, auth, owner, principals, account_id


def successful_transport(seen: list | None = None):
    calls = seen if seen is not None else []

    def transport(request, timeout):
        calls.append(request)
        if request.full_url == "https://api.amazon.com/auth/o2/token":
            return Response({"access_token": "access-token"})
        if request.full_url.endswith("/v2/profiles"):
            return Response(
                [{"profileId": 1234567890, "countryCode": "US"}],
                headers={"x-amz-rid": "profiles-request"},
            )
        return Response(
            {"campaigns": [{"campaignId": "must-not-persist"}]},
            headers={"x-amzn-requestid": "campaign-request"},
        )

    return transport


def test_v14_migration_installs_tenant_owned_ads_gate(tmp_path: Path) -> None:
    path = tmp_path / "runtime.sqlite"
    db = Database(path)
    with db.transaction() as conn:
        conn.execute("DROP TABLE ads_capability_gates")
        conn.execute("UPDATE runtime_meta SET value='14' WHERE key='schema_version'")
    migrated = Database(path)
    assert migrated.readiness()["schema_version"] == 18
    with migrated.connect() as conn:
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(ads_capability_gates)")
        }
    assert {
        "tenant_id",
        "connector_account_id",
        "lease_until",
        "attempt_count",
        "attestation_reference",
        "request_ids_json",
    } <= columns


def test_amazon_ads_account_validation_redaction_catalog_and_profiles_health(
    tmp_path: Path,
) -> None:
    db, auth, owner, principals, _ = setup_runtime(tmp_path)
    seen = []
    service = MarketplaceAccountService(
        db,
        auth,
        environ=CREDENTIALS,
        transport=successful_transport(seen),
    )
    account = service.create(owner, "amazon_ads", "second-profile", ADS_CONFIG, "create")
    assert account["provider_details"] == {"profile_id": "1234567890", "region": "na"}
    assert account["credential_refs"] == {
        "lwa_client_id_ref": "present",
        "lwa_client_secret_ref": "present",
        "lwa_refresh_token_ref": "present",
    }
    assert "ADS_CLIENT" not in json.dumps(account)
    healthy = service.health_check(principals["operator"], account["id"], "health")
    assert healthy["health_status"] == "healthy"
    assert [request.full_url for request in seen] == [
        "https://api.amazon.com/auth/o2/token",
        "https://advertising-api.amazon.com/v2/profiles",
    ]
    assert "amazon_ads" in {item["id"] for item in service.catalog()["connector_providers"]}
    for config in (
        {**ADS_CONFIG, "profile_id": "abc"},
        {**ADS_CONFIG, "region": "us"},
        {**ADS_CONFIG, "client_secret": "literal"},
    ):
        with pytest.raises(ValidationError):
            service.create(owner, "amazon_ads", "invalid", config, "invalid")


def test_connector_reuses_lwa_and_sends_exact_read_only_headers(tmp_path: Path) -> None:
    seen = []
    connector = AmazonAdsConnector(
        ADS_CONFIG, environ=CREDENTIALS, transport=successful_transport(seen)
    )
    result = connector.probe()
    assert result["observed_capabilities"] == [
        "lwa",
        "profiles_read",
        "campaigns_list_read",
    ]
    assert sum(r.full_url == "https://api.amazon.com/auth/o2/token" for r in seen) == 1
    profiles, campaign = seen[1], seen[2]
    assert profiles.method == "GET"
    assert profiles.get_header("Amazon-advertising-api-clientid") == "client-id"
    assert profiles.get_header("Authorization") == "Bearer access-token"
    assert campaign.method == "POST"
    assert campaign.full_url == "https://advertising-api.amazon.com/sp/campaigns/list"
    assert campaign.get_header("Amazon-advertising-api-scope") == "1234567890"
    assert campaign.get_header("Accept") == "application/vnd.spCampaign.v3+json"
    assert campaign.get_header("Content-type") == "application/vnd.spCampaign.v3+json"
    assert json.loads(campaign.data) == {"maxResults": 1}


def test_pass_requires_all_live_reads_and_safe_attestation_and_persists_safely(
    tmp_path: Path,
) -> None:
    db, auth, owner, _, account_id = setup_runtime(tmp_path)
    service = AdsCapabilityGateService(
        db, auth, environ=CREDENTIALS, transport=successful_transport()
    )
    passed = service.check(
        owner, account_id, "https://governance.example/ADS-42", "gate-1", "request-1"
    )
    assert passed["status"] == "passed"
    assert set(passed) == {
        "id",
        "tenant_id",
        "connector_account_id",
        "created_by",
        "status",
        "region",
        "profile_id",
        "required_capabilities",
        "observed_capabilities",
        "checks",
        "attestation_reference",
        "request_ids",
        "retry_after_seconds",
        "error_code",
        "error_message",
        "created_at",
        "updated_at",
        "checked_at",
    }
    assert sorted(passed["observed_capabilities"]) == sorted(passed["required_capabilities"])
    assert {check["name"] for check in passed["checks"]} == {
        "lwa",
        "profiles_read",
        "target_profile",
        "campaigns_list_read",
        "external_attestation",
    }
    assert all(check["status"] == "passed" for check in passed["checks"])
    assert passed["request_ids"] == ["campaign-request", "profiles-request"]
    assert passed["checked_at"] and "idempotency_key" not in passed and "lease_until" not in passed
    raw = db.get_ads_capability_gate(owner.tenant_id, passed["id"])
    assert Database(db.path).get_ads_capability_gate(owner.tenant_id, passed["id"])["status"] == "passed"
    assert "must-not-persist" not in json.dumps(raw)
    assert "client-secret" not in json.dumps(db.list_audit(owner.tenant_id))
    assert b"client-secret" not in db.path.read_bytes()
    assert b"refresh-token" not in db.path.read_bytes()


def test_missing_attestation_still_runs_live_probe_then_blocks(tmp_path: Path) -> None:
    db, auth, owner, _, account_id = setup_runtime(tmp_path)
    seen = []
    service = AdsCapabilityGateService(
        db, auth, environ=CREDENTIALS, transport=successful_transport(seen)
    )
    gate = service.check(owner, account_id, None, "no-attest", "request")
    assert gate["status"] == "blocked"
    assert gate["error_code"] == "attestation_required"
    assert gate["observed_capabilities"] == ["lwa", "profiles_read", "campaigns_list_read"]
    assert len(seen) == 3
    assert next(c for c in gate["checks"] if c["name"] == "external_attestation")["status"] == "blocked"


def test_rbac_tenant_idempotency_attestation_conflict_and_lease(tmp_path: Path) -> None:
    db, auth, owner, principals, account_id = setup_runtime(tmp_path)
    seen = []
    service = AdsCapabilityGateService(
        db, auth, environ=CREDENTIALS, transport=successful_transport(seen)
    )
    with pytest.raises(AuthorizationError):
        service.check(principals["operator"], account_id, "ticket://1", "op", "r")
    first = service.check(owner, account_id, "ticket://ADS-1", "same", "r1")
    replay = service.check(owner, account_id, "ticket://ADS-1", "same", "r2")
    assert replay["id"] == first["id"] and len(seen) == 3
    with pytest.raises(ConflictError, match="attestation"):
        service.check(owner, account_id, "ticket://ADS-2", "same", "r3")
    other_tenant, other_owner_id = db.create_tenant("B", "b@example.com")
    other = auth.authenticate(auth.issue_key(other_tenant, other_owner_id))
    with pytest.raises(NotFoundError):
        service.get(other, first["id"])
    with pytest.raises(NotFoundError):
        service.check(other, account_id, "ticket://ADS-X", "cross", "cross")
    pending, _ = db.create_ads_capability_gate(
        owner.tenant_id,
        owner.user_id,
        account_id,
        "lease",
        region="na",
        profile_id="1234567890",
        required_capabilities=["lwa"],
        attestation_reference="ticket://lease",
    )
    db.claim_ads_capability_gate(owner.tenant_id, pending["id"])
    with pytest.raises(ConflictError, match="not available"):
        db.claim_ads_capability_gate(owner.tenant_id, pending["id"])


def test_stale_lease_reclaims_and_max_attempts_terminal(tmp_path: Path) -> None:
    db, auth, owner, _, account_id = setup_runtime(tmp_path)
    service = AdsCapabilityGateService(
        db, auth, environ=CREDENTIALS, transport=successful_transport()
    )
    stale, _ = db.create_ads_capability_gate(
        owner.tenant_id,
        owner.user_id,
        account_id,
        "stale",
        region="na",
        profile_id="1234567890",
        required_capabilities=["lwa"],
        attestation_reference="ticket://stale",
    )
    db.claim_ads_capability_gate(owner.tenant_id, stale["id"])
    with db.transaction() as conn:
        conn.execute(
            "UPDATE ads_capability_gates SET lease_until='2000-01-01T00:00:00+00:00' WHERE id=?",
            (stale["id"],),
        )
    reclaimed = service.check(
        owner, account_id, "ticket://stale", "stale", "reclaim"
    )
    assert reclaimed["status"] == "passed"

    exhausted, _ = db.create_ads_capability_gate(
        owner.tenant_id,
        owner.user_id,
        account_id,
        "exhausted",
        region="na",
        profile_id="1234567890",
        required_capabilities=["lwa"],
        attestation_reference="ticket://exhausted",
        max_attempts=1,
    )
    db.claim_ads_capability_gate(owner.tenant_id, exhausted["id"])
    with db.transaction() as conn:
        conn.execute(
            "UPDATE ads_capability_gates SET lease_until='2000-01-01T00:00:00+00:00' WHERE id=?",
            (exhausted["id"],),
        )
    terminal = service.check(
        owner, account_id, "ticket://exhausted", "exhausted", "terminal"
    )
    assert terminal["status"] == "failed"
    assert terminal["error_code"] == "max_attempts"


@pytest.mark.parametrize(
    "case,expected_code",
    [
        ("missing", "missing_credential"),
        ("empty", "profile_validation_failed"),
        ("mismatch", "profile_validation_failed"),
        ("401", "amazon_ads_unauthorized"),
        ("403", "amazon_ads_forbidden"),
        ("429", "rate_limited"),
    ],
)
def test_blocking_failure_classification(tmp_path: Path, case: str, expected_code: str) -> None:
    db, auth, owner, _, account_id = setup_runtime(tmp_path)
    environ = {} if case == "missing" else CREDENTIALS

    def transport(request, timeout):
        if request.full_url == "https://api.amazon.com/auth/o2/token":
            return Response({"access_token": "token"})
        if request.full_url.endswith("/v2/profiles"):
            if case in {"401", "403", "429"}:
                return Response(
                    {},
                    status=int(case),
                    headers={"Retry-After": "37", "x-amz-rid": f"rid-{case}"},
                )
            if case == "empty":
                return Response([], headers={"x-amz-rid": "rid-empty"})
            if case == "mismatch":
                return Response([{"profileId": 999}], headers={"x-amz-rid": "rid-mismatch"})
        return Response({"campaigns": []})

    service = AdsCapabilityGateService(db, auth, environ=environ, transport=transport)
    gate = service.check(owner, account_id, "ticket://ADS-1", f"gate-{case}", "request")
    assert gate["status"] == "blocked" and gate["error_code"] == expected_code
    assert {item["name"] for item in gate["checks"]} == {
        "lwa", "profiles_read", "target_profile", "campaigns_list_read", "external_attestation"
    }
    if case == "429":
        assert gate["retry_after_seconds"] == 37
        assert gate["request_ids"] == ["rid-429"]


def test_5xx_and_unexpected_fail_persist_and_propagate(tmp_path: Path) -> None:
    db, auth, owner, _, account_id = setup_runtime(tmp_path)

    def five_hundred(request, timeout):
        if request.full_url == "https://api.amazon.com/auth/o2/token":
            return Response({"access_token": "token"})
        return Response({}, status=500, headers={"x-amz-rid": "rid-500"})

    service = AdsCapabilityGateService(db, auth, environ=CREDENTIALS, transport=five_hundred)
    with pytest.raises(AmazonAdsHTTPError):
        service.check(owner, account_id, "ticket://ADS-1", "http-500", "request")
    assert service.list(owner)[0]["status"] == "failed"

    def crash(request, timeout):
        raise RuntimeError("secret crash detail")

    service.transport = crash
    with pytest.raises(ExternalServiceError, match="unexpectedly"):
        service.check(owner, account_id, "ticket://ADS-2", "crash", "request")
    failed = service.list(owner)[0]
    assert failed["status"] == "failed"
    assert "secret crash detail" not in json.dumps(failed)


@pytest.mark.parametrize("case", ["403", "500", "invalid_json"])
def test_campaign_stage_failures_preserve_prior_checks_and_request_ids(
    tmp_path: Path, case: str
) -> None:
    db, auth, owner, _, account_id = setup_runtime(tmp_path)

    def transport(request, timeout):
        if request.full_url == "https://api.amazon.com/auth/o2/token":
            return Response({"access_token": "token"})
        if request.full_url.endswith("/v2/profiles"):
            return Response(
                [{"profileId": 1234567890}],
                headers={"x-amz-rid": "profiles-rid"},
            )
        if case == "invalid_json":
            return Response(b"not-json", headers={"x-amz-rid": "campaign-rid"})
        return Response(
            {}, status=int(case), headers={"x-amz-rid": "campaign-rid"}
        )

    service = AdsCapabilityGateService(db, auth, environ=CREDENTIALS, transport=transport)
    if case == "403":
        gate = service.check(
            owner, account_id, "ticket://campaign", f"campaign-{case}", "request"
        )
        assert gate["status"] == "blocked"
    else:
        with pytest.raises(ExternalServiceError):
            service.check(
                owner, account_id, "ticket://campaign", f"campaign-{case}", "request"
            )
        gate = service.list(owner)[0]
        assert gate["status"] == "failed"
    statuses = {item["name"]: item["status"] for item in gate["checks"]}
    assert statuses["lwa"] == "passed"
    assert statuses["profiles_read"] == "passed"
    assert statuses["target_profile"] == "passed"
    assert statuses["campaigns_list_read"] in {"blocked", "failed"}
    assert gate["request_ids"] == ["campaign-rid", "profiles-rid"]


def test_ads_capability_gate_api_routes_and_limit_validation(tmp_path: Path) -> None:
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    bootstrap = app.bootstrap("A", "owner@example.com")
    owner = app.auth.authenticate(bootstrap["api_key"])
    account_id = app.db.add_connector_account(
        owner.tenant_id, "amazon_ads", "profile", ADS_CONFIG
    )
    app.ads_gates.environ = CREDENTIALS
    app.ads_gates.transport = successful_transport()

    class Handler(_Handler):
        def __init__(self, method: str, path: str, body=None, idem="api-gate"):
            self.path = path
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {bootstrap['api_key']}"
            self.headers["Idempotency-Key"] = idem
            self.body = body or {}
            self.out = None

        @property
        def app(self):
            return app

        def _body(self):
            return self.body

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value)

    post = Handler(
        "POST",
        "/v1/ads-capability-gates",
        {
            "connector_account_id": account_id,
            "attestation_reference": "ticket://ADS-1",
        },
    )
    post.do_POST()
    assert post.out[0] == 201 and post.out[1]["status"] == "passed"
    gate_id = post.out[1]["id"]
    listed = Handler("GET", "/v1/ads-capability-gates")
    listed.do_GET()
    assert listed.out[1]["ads_capability_gates"][0]["id"] == gate_id
    detail = Handler("GET", f"/v1/ads-capability-gates/{gate_id}")
    detail.do_GET()
    assert detail.out[0] == 200
    invalid = Handler("GET", "/v1/ads-capability-gates?limit=nope")
    invalid.do_GET()
    assert invalid.out[0] == 422
