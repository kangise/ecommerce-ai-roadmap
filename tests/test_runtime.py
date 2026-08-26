from __future__ import annotations

import json
import gzip
import threading
from pathlib import Path

import pytest

from ecommerce_ai_skills.runtime.actions import ActionService
from ecommerce_ai_skills.runtime.agents import (
    OpenAIResponsesProvider,
    PlatformRegistry,
    SPECIALIST_SCHEMA,
    SkillContextLoader,
    WeeklyOpsCouncil,
)
from ecommerce_ai_skills.runtime.auth import AuthService
from ecommerce_ai_skills.runtime.connectors.shopify import ShopifyConnector
from ecommerce_ai_skills.runtime.connectors.amazon_spapi import AmazonSPAPIReportsConnector
from ecommerce_ai_skills.runtime.evidence import CSVIngestor
from ecommerce_ai_skills.runtime.errors import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ConnectorNotConfiguredError,
    ExternalServiceError,
    MissingCredentialError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from ecommerce_ai_skills.runtime.observability import RateLimiter
from ecommerce_ai_skills.runtime.storage import Database


def test_api_keys_are_hashed_and_tenant_scoped(tmp_path: Path) -> None:
    db = Database(tmp_path / "runtime.sqlite")
    tenant_a, owner_a = db.create_tenant("A", "owner-a@example.com")
    tenant_b, owner_b = db.create_tenant("B", "owner-b@example.com")
    auth = AuthService(db)
    key_a = auth.issue_key(tenant_a, owner_a)
    key_b = auth.issue_key(tenant_b, owner_b)
    assert auth.authenticate(key_a).tenant_id == tenant_a
    assert auth.authenticate(key_b).tenant_id == tenant_b
    with db.connect() as conn:
        stored = conn.execute("SELECT key_hash FROM api_keys").fetchall()
    assert all("eai_" not in row[0] for row in stored)
    with pytest.raises(AuthenticationError):
        auth.authenticate(key_a[:-1] + "x")


def test_api_key_rotation_revokes_old_key_without_locking_out_tenant(tmp_path: Path) -> None:
    db = Database(tmp_path / "runtime.sqlite")
    tenant, owner = db.create_tenant("A", "owner@example.com")
    auth = AuthService(db)
    old_key = auth.issue_key(tenant, owner)
    replacement = auth.rotate_current(auth.authenticate(old_key))
    assert auth.authenticate(replacement).tenant_id == tenant
    with pytest.raises(AuthenticationError):
        auth.authenticate(old_key)
    with pytest.raises(ConflictError, match="last active"):
        db.revoke_api_key(tenant, auth.authenticate(replacement).api_key_id)


def test_approval_requires_second_actor_and_idempotency_replays(tmp_path: Path) -> None:
    db = Database(tmp_path / "runtime.sqlite")
    tenant, owner = db.create_tenant("A", "owner@example.com")
    operator = db.create_user(tenant, "operator@example.com", "operator")
    admin = db.create_user(tenant, "admin@example.com", "admin")
    auth = AuthService(db)
    service = ActionService(db, auth)
    op_principal = auth.authenticate(auth.issue_key(tenant, operator))
    admin_principal = auth.authenticate(auth.issue_key(tenant, admin))
    assert op_principal and admin_principal
    first = service.request(op_principal, "shopify.sync_products", {"external_account_id": "store"}, "request-1", "req-1")
    replay = service.request(op_principal, "shopify.sync_products", {"external_account_id": "store"}, "request-1", "req-2")
    assert replay["id"] == first["id"]
    with pytest.raises(AuthorizationError):
        service.approve(op_principal, first["id"], "req-3")
    approved = service.approve(admin_principal, first["id"], "req-4")
    assert approved["status"] == "approved"


def test_shopify_connector_requires_real_credential_and_builds_safe_request() -> None:
    connector = ShopifyConnector(
        {"shop_domain": "demo.myshopify.com", "api_version": "2025-10", "credential_ref": "SHOPIFY_TOKEN"},
        environ={},
    )
    with pytest.raises(MissingCredentialError):
        connector.list_products()

    seen = {}

    class Response:
        status = 200
        headers = {"Link": '<https://demo.myshopify.com/admin/api/2025-10/products.json?page_info=next-cursor>; rel="next"'}

        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b'{"products":[{"id": "p-1"}]}'

    def transport(request, timeout):
        seen["url"] = request.full_url
        seen["token"] = request.headers.get("X-shopify-access-token")
        seen["timeout"] = timeout
        return Response()

    payload = ShopifyConnector(
        {"shop_domain": "demo.myshopify.com", "api_version": "2025-10", "credential_ref": "SHOPIFY_TOKEN"},
        environ={"SHOPIFY_TOKEN": "real-token-from-test-fixture"},
        transport=transport,
    ).list_products(limit=3)
    assert payload["products"][0]["id"] == "p-1"
    assert payload["next_page_info"] == "next-cursor"
    assert seen == {
        "url": "https://demo.myshopify.com/admin/api/2025-10/products.json?limit=3",
        "token": "real-token-from-test-fixture",
        "timeout": 30,
    }


def _amazon_spapi_config() -> dict:
    return {
        "region": "na",
        "marketplace_ids": ["ATVPDKIKX0DER"],
        "lwa_client_id_ref": "AMAZON_LWA_CLIENT_ID",
        "lwa_client_secret_ref": "AMAZON_LWA_CLIENT_SECRET",
        "lwa_refresh_token_ref": "AMAZON_LWA_REFRESH_TOKEN",
    }


def test_amazon_spapi_reports_connector_uses_lwa_and_downloads_gzip_safely() -> None:
    from urllib.parse import parse_qs

    report_bytes = b"seller-sku\titem-name\nSKU-1\tReal product\n"
    compressed = gzip.compress(report_bytes)
    seen = []

    class Response:
        def __init__(self, body, url, headers=None):
            self.body = body
            self.status = 200
            self.url = url
            self.headers = headers or {}

        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, size=-1): return self.body if size < 0 else self.body[:size]
        def geturl(self): return self.url

    def transport(request, timeout):
        seen.append((request.full_url, dict(request.header_items()), request.data, timeout))
        if request.full_url == "https://api.amazon.com/auth/o2/token":
            values = parse_qs(request.data.decode())
            assert values["grant_type"] == ["refresh_token"]
            assert values["client_secret"] == ["client-secret"]
            return Response(b'{"access_token":"Atza|access","expires_in":3600}', request.full_url)
        if request.full_url.endswith("/reports/REPORT-1"):
            assert request.get_header("X-amz-access-token") == "Atza|access"
            return Response(
                json.dumps({
                    "payload": {
                        "reportId": "REPORT-1",
                        "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
                        "processingStatus": "DONE",
                        "dataEndTime": "2026-08-22T00:00:00Z",
                        "reportDocumentId": "DOC-1",
                    }
                }).encode(),
                request.full_url,
            )
        if request.full_url.endswith("/documents/DOC-1"):
            return Response(
                b'{"payload":{"url":"https://d123.cloudfront.net/report","compressionAlgorithm":"GZIP"}}',
                request.full_url,
            )
        if request.full_url == "https://d123.cloudfront.net/report":
            assert request.get_header("X-amz-access-token") is None
            return Response(compressed, request.full_url)
        raise AssertionError(request.full_url)

    connector = AmazonSPAPIReportsConnector(
        _amazon_spapi_config(),
        environ={
            "AMAZON_LWA_CLIENT_ID": "client-id",
            "AMAZON_LWA_CLIENT_SECRET": "client-secret",
            "AMAZON_LWA_REFRESH_TOKEN": "refresh-token",
        },
        transport=transport,
    )
    report = connector.retrieve_report("REPORT-1")
    assert report["content"] == report_bytes
    assert report["amazon_report_type"] == "GET_MERCHANT_LISTINGS_ALL_DATA"
    assert len(seen) == 4
    assert all(item[3] == 30 for item in seen)

    with pytest.raises(MissingCredentialError, match="AMAZON_LWA_CLIENT_SECRET"):
        AmazonSPAPIReportsConnector(
            _amazon_spapi_config(),
            environ={
                "AMAZON_LWA_CLIENT_ID": "client-id",
                "AMAZON_LWA_REFRESH_TOKEN": "refresh-token",
            },
            transport=transport,
        ).retrieve_report("REPORT-1")


def test_connector_registration_rejects_plaintext_secret(tmp_path: Path) -> None:
    db = Database(tmp_path / "runtime.sqlite")
    tenant, _ = db.create_tenant("A", "owner@example.com")
    with pytest.raises(ValidationError, match="secret"):
        db.add_connector_account(
            tenant,
            "shopify",
            "store",
            {"shop_domain": "demo.myshopify.com", "credential_ref": "SHOPIFY_TOKEN", "access_token": "never-store-me"},
        )


def test_database_fails_closed_on_unsupported_schema(tmp_path: Path) -> None:
    path = tmp_path / "runtime.sqlite"
    db = Database(path)
    with db.transaction() as conn:
        conn.execute("UPDATE runtime_meta SET value='1' WHERE key='schema_version'")
    migrated = Database(path)
    assert migrated.readiness()["schema_version"] == 21
    with db.transaction() as conn:
        conn.execute("UPDATE runtime_meta SET value='99' WHERE key='schema_version'")
    with pytest.raises(ValidationError, match="schema version"):
        Database(path)


def test_action_execution_persists_connector_records(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = Database(tmp_path / "runtime.sqlite")
    tenant, owner = db.create_tenant("A", "owner@example.com")
    admin = db.create_user(tenant, "admin@example.com", "admin")
    operator = db.create_user(tenant, "operator@example.com", "operator")
    db.add_connector_account(tenant, "shopify", "store", {"shop_domain": "demo.myshopify.com", "api_version": "2025-10", "credential_ref": "SHOPIFY_TOKEN"})
    monkeypatch.setenv("SHOPIFY_TOKEN", "token-present-only-for-test")
    auth = AuthService(db)
    service = ActionService(db, auth)
    op = auth.authenticate(auth.issue_key(tenant, operator))
    adm = auth.authenticate(auth.issue_key(tenant, admin))
    assert op and adm

    # The service uses the real transport by default; this test only replaces
    # the connector construction boundary with a fixture response.
    from ecommerce_ai_skills.runtime import actions

    class Connector:
        def __init__(self, config): pass
        def list_products(self, **kwargs): return {"products": [{"id": "p-1", "title": "real fixture"}], "next_page_info": "cursor-2"}

    monkeypatch.setattr(actions, "ShopifyConnector", Connector)
    requested = service.request(op, "shopify.sync_products", {"external_account_id": "store"}, "sync-1", "r1")
    service.approve(adm, requested["id"], "r2")
    executed = service.execute(op, requested["id"], "r3")
    assert executed["status"] == "executed"
    assert executed["result"]["records"] == 1
    assert executed["result"]["has_more"] is True
    assert db.get_sync_cursor(tenant, "shopify", "store") == "cursor-2"
    assert db.list_records(tenant, "shopify")[0]["payload"]["id"] == "p-1"
    assert len(db.list_audit(tenant)) == 3


def test_approved_amazon_spapi_report_action_creates_real_evidence_import(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ecommerce_ai_skills.runtime import actions
    from ecommerce_ai_skills.runtime.api import RuntimeApplication

    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"), agent_provider=_FixtureAgentProvider()
    )
    bootstrap = app.bootstrap("Amazon seller", "owner@example.com")
    admin_id = app.db.create_user(bootstrap["tenant_id"], "admin@example.com", "admin")
    owner = app.auth.authenticate(bootstrap["api_key"])
    admin = app.auth.authenticate(app.auth.issue_key(bootstrap["tenant_id"], admin_id))
    app.db.add_connector_account(
        bootstrap["tenant_id"], "amazon_spapi", "primary", _amazon_spapi_config()
    )

    class Connector:
        def __init__(self, config):
            assert config == _amazon_spapi_config()

        def retrieve_report(self, report_id):
            assert report_id == "REPORT-1"
            return {
                "content": b"seller-sku\titem-name\nSKU-1\tReal product\n",
                "report_id": "REPORT-1",
                "report_document_id": "DOC-1",
                "amazon_report_type": "GET_MERCHANT_LISTINGS_ALL_DATA",
                "observed_at": "2026-08-22T00:00:00Z",
                "compression": None,
            }

    monkeypatch.setattr(actions, "AmazonSPAPIReportsConnector", Connector)
    requested = app.actions.request(
        owner,
        "amazon_spapi.import_report",
        {
            "external_account_id": "primary",
            "report_id": "REPORT-1",
            "evidence_report_type": "amazon_listing",
        },
        "amazon-report-action-1",
        "request-1",
    )
    app.actions.approve(admin, requested["id"], "request-2")
    executed = app.actions.execute(owner, requested["id"], "request-3")
    assert executed["status"] == "executed"
    assert executed["result"]["provider"] == "amazon_spapi"
    imported = app.db.get_evidence_import(
        bootstrap["tenant_id"], executed["result"]["evidence_import_id"], include_rows=True
    )
    assert imported["platform"] == "amazon"
    assert imported["report_type"] == "amazon_listing"
    assert imported["rows"][0]["seller_sku"] == "SKU-1"
    stored_config = app.db.connector_account(
        bootstrap["tenant_id"], "amazon_spapi", "primary"
    )["config_json"]
    assert "client-secret" not in stored_config and "refresh-token" not in stored_config


def _weekly_evidence() -> list[dict]:
    return [
        {
            "source_id": "shopify-products-2026-08-22",
            "platform": "shopify",
            "source_type": "shopify_products",
            "observed_at": "2026-08-22T09:00:00+08:00",
            "data": [{"id": "p-1", "title": "Neck Fan", "status": "active"}],
        },
        {
            "source_id": "ads-report-2026-w34",
            "platform": "amazon",
            "source_type": "amazon_ads_export",
            "observed_at": "2026-08-22T09:05:00+08:00",
            "data": [{"campaign": "launch", "spend": 120, "sales": 240}],
        },
    ]


class _FixtureAgentProvider:
    def __init__(self, *, bad_ref: bool = False, bad_platform_ref: bool = False):
        self.bad_ref = bad_ref
        self.bad_platform_ref = bad_platform_ref
        self.calls = []
        self.lock = threading.Lock()

    def configuration(self):
        return "fixture_provider", "fixture-model"

    def complete(self, *, agent_name, instructions, payload, output_schema, safety_identifier):
        with self.lock:
            self.calls.append((agent_name, payload, safety_identifier))
        if agent_name == "operations_reviewer":
            return {
                "verdict": "approved",
                "issues": [],
                "evidence_refs": [
                    source["source_id"] for source in payload["evidence_catalog"]
                ],
                "limitations": payload["manager_report"].get("limitations", []),
            }
        if agent_name == "store_manager":
            platforms = payload["platforms"]
            primary_platform = "amazon" if "amazon" in platforms else platforms[0]
            source_by_platform = {
                source["platform"]: source["source_id"] for source in payload["evidence_catalog"]
            }
            primary_source = source_by_platform[primary_platform]
            risk_platform = "shopify" if "shopify" in platforms else primary_platform
            risk_source = source_by_platform[risk_platform]
            return {
                "executive_summary": "Prioritize the evidence-backed campaign review.",
                "priorities": [
                    {
                        "rank": 1,
                        "title": "Review launch campaign efficiency",
                        "why_now": "The supplied weekly ads export shows current spend and sales.",
                        "evidence_refs": [primary_source],
                        "platforms": [primary_platform],
                        "expected_impact": "Clarify whether budget should be reallocated.",
                        "confidence": "medium",
                        "recommended_owner": f"platform_{primary_platform}_operator",
                        "downstream_action": "Prepare a bid-change proposal without applying it.",
                        "action_type": "external_change",
                        "requires_approval": True,
                        "metric_claim": {"operation": "none", "observation_refs": []},
                    }
                ],
                "risks": [
                    {
                        "risk": "The evidence has no order or inventory history.",
                        "mitigation": "Import those exports before making replenishment decisions.",
                        "evidence_refs": [risk_source],
                        "platforms": [risk_platform],
                        "metric_claim": {"operation": "none", "observation_refs": []},
                    }
                ],
                "limitations": ["Only two user-supplied sources were available."],
            }
        platform = payload["target_platform"]
        evidence = payload.get("evidence", [])
        if evidence:
            candidates = [
                source for source in evidence
                if platform == "cross_platform" or source["platform"] in {platform, "cross_platform"}
            ]
            source_id = candidates[0]["source_id"]
        else:
            source_id = next(
                finding["evidence_refs"][0]
                for specialist in payload["specialist_findings"].values()
                for finding in specialist["findings"]
            )
        if self.bad_ref and agent_name == "evidence_analyst":
            source_id = "unknown-source"
        if self.bad_platform_ref and agent_name == "platform_amazon_operator":
            source_id = "shopify-products-2026-08-22"
        return {
            "platform": platform,
            "summary": f"{agent_name} completed an evidence-bound review.",
            "findings": [
                {
                    "title": "Review current campaign",
                    "severity": "warning",
                    "confidence": "medium",
                    "evidence_refs": [source_id],
                    "recommendation": "Validate profitability before changing bids.",
                }
            ],
            "data_gaps": ["Order history was not supplied."],
        }


def test_weekly_ops_council_persists_parallel_tasks_and_report(tmp_path: Path) -> None:
    from ecommerce_ai_skills.runtime.api import RuntimeApplication

    provider = _FixtureAgentProvider()
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"), agent_provider=provider)
    bootstrap = app.bootstrap("A", "owner@example.com")
    principal = app.auth.authenticate(bootstrap["api_key"])
    evidence = _weekly_evidence()

    run = app.agent_runs.request(
        principal,
        "weekly_ops",
        "Find the most important evidence-backed actions for this week.",
        evidence,
        "weekly-2026-w34",
        "request-1",
    )
    bundle = app.agent_runs.execute(principal, run["id"], "request-2")

    assert bundle["run"]["status"] == "completed"
    assert bundle["run"]["model"] == "fixture-model"
    assert {task["agent_name"] for task in bundle["tasks"]} == {
        "evidence_analyst",
        "platform_amazon_operator",
        "platform_shopify_operator",
        "cross_platform_controller",
        "store_manager",
        "operations_reviewer",
    }
    assert all(task["status"] == "completed" for task in bundle["tasks"])
    assert [artifact["kind"] for artifact in bundle["artifacts"]].count("specialist_finding") == 4
    assert {artifact["kind"] for artifact in bundle["artifacts"]} >= {
        "input_evidence",
        "manager_synthesis",
        "weekly_ops_report",
    }
    final_report = [
        artifact["content"] for artifact in bundle["artifacts"]
        if artifact["kind"] == "weekly_ops_report"
    ][0]
    assert final_report["priorities"][0]["requires_approval"] is True
    evaluation = app.evaluator.evaluate(principal, run["id"], "request-eval")
    assert evaluation["passed"] is True and evaluation["score"] == 1.0
    assert app.evaluator.list(principal, run["id"])[0]["id"] == evaluation["id"]
    assert {call[0] for call in provider.calls} == {
        "evidence_analyst",
        "platform_amazon_operator",
        "platform_shopify_operator",
        "cross_platform_controller",
        "store_manager",
        "operations_reviewer",
    }
    amazon_payload = next(
        call[1] for call in provider.calls if call[0] == "platform_amazon_operator"
    )
    amazon_skills = {contract["name"] for contract in amazon_payload["skill_contracts"]}
    assert {"ecom-listing", "ecom-advertising", "ecom-inventory", "ecom-compliance"} <= amazon_skills
    assert amazon_payload["target_platform"] == "amazon"
    assert {source["platform"] for source in amazon_payload["evidence"]} == {"amazon"}
    shopify_payload = next(
        call[1] for call in provider.calls if call[0] == "platform_shopify_operator"
    )
    assert {source["platform"] for source in shopify_payload["evidence"]} == {"shopify"}
    assert bundle["run"]["platforms"] == ["amazon", "shopify"]

    replay = app.agent_runs.request(
        principal,
        "weekly_ops",
        "Find the most important evidence-backed actions for this week.",
        evidence,
        "weekly-2026-w34",
        "request-3",
    )
    assert replay["id"] == run["id"]
    with pytest.raises(ConflictError, match="different agent run"):
        app.agent_runs.request(
            principal, "weekly_ops", "Use a different objective now.", evidence,
            "weekly-2026-w34", "request-4"
        )

    other = app.bootstrap("B", "other@example.com")
    other_principal = app.auth.authenticate(other["api_key"])
    with pytest.raises(NotFoundError):
        app.agent_runs.get(other_principal, run["id"])
    with pytest.raises(ValidationError, match="secret material"):
        app.agent_runs.validate_request(
            "weekly_ops",
            "Analyze this real source.",
            [{
                "source_id": "bad-source",
                "platform": "amazon",
                "source_type": "manual",
                "observed_at": "2026-08-22T09:00:00+08:00",
                "data": {"access_token": "must-not-be-stored"},
            }],
        )


def test_amazon_only_run_gets_full_amazon_skill_team_without_cross_platform_task(tmp_path: Path) -> None:
    from ecommerce_ai_skills.runtime.api import RuntimeApplication

    provider = _FixtureAgentProvider()
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"), agent_provider=provider)
    bootstrap = app.bootstrap("Amazon seller", "owner@example.com")
    principal = app.auth.authenticate(bootstrap["api_key"])
    amazon_evidence = [source for source in _weekly_evidence() if source["platform"] == "amazon"]
    run = app.agent_runs.request(
        principal,
        "weekly_ops",
        "Review the Amazon account with only supplied exports.",
        amazon_evidence,
        "amazon-weekly-1",
        "request-1",
    )
    bundle = app.agent_runs.execute(principal, run["id"], "request-2")
    assert {task["agent_name"] for task in bundle["tasks"]} == {
        "evidence_analyst", "platform_amazon_operator", "store_manager",
        "operations_reviewer",
    }
    amazon_payload = next(
        call[1] for call in provider.calls if call[0] == "platform_amazon_operator"
    )
    assert {contract["name"] for contract in amazon_payload["skill_contracts"]} == {
        "ecom-advertising",
        "ecom-applicability",
        "ecom-compliance",
        "ecom-customer-service",
        "ecom-inventory",
        "ecom-listing",
        "ecom-pricing",
        "ecom-research",
    }


def test_platform_registry_drives_supported_marketplaces_and_rejects_unknown_platform(tmp_path: Path) -> None:
    registry = PlatformRegistry()
    assert len(registry.entries()) == 15
    assert {"amazon", "shopify", "walmart", "tiktok_shop", "mercado_libre"} <= registry.ids()
    loader = SkillContextLoader()
    assert "ecom-advertising" in loader.skill_ids_for_platform("amazon")
    assert "ecom-listing" in loader.skill_ids_for_platform("walmart")
    assert "ecom-advertising" not in loader.skill_ids_for_platform("walmart")

    db = Database(tmp_path / "runtime.sqlite")
    tenant, owner = db.create_tenant("A", "owner@example.com")
    service = WeeklyOpsCouncil(db, AuthService(db), _FixtureAgentProvider())
    with pytest.raises(ValidationError, match="unsupported platform"):
        service.validate_request(
            "weekly_ops",
            "Review this unsupported marketplace.",
            [{
                "source_id": "etsy-export",
                "platform": "etsy",
                "source_type": "orders",
                "observed_at": "2026-08-22T09:00:00+08:00",
                "data": [{"id": "order-1"}],
            }],
        )
    assert tenant and owner


def _amazon_business_csv() -> bytes:
    return (
        "ASIN (Child),Sessions,Units Ordered,Ordered Product Sales\n"
        "B0REAL001,120,8,239.92\n"
        "B0REAL002,75,3,89.97\n"
    ).encode()


def _amazon_business_xlsx() -> bytes:
    import io
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Business Report"
    sheet.append(["ASIN (Child)", "Sessions", "Units Ordered", "Ordered Product Sales"])
    sheet.append(["B0REAL001", 120, 8, 239.92])
    sheet.append(["B0REAL002", 75, 3, "=10+2"])
    output = io.BytesIO()
    workbook.save(output)
    workbook.close()
    return output.getvalue()


def test_amazon_csv_import_persists_real_rows_and_drives_agent_run(tmp_path: Path) -> None:
    from ecommerce_ai_skills.runtime.api import RuntimeApplication

    provider = _FixtureAgentProvider()
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"), agent_provider=provider)
    bootstrap = app.bootstrap("Amazon seller", "owner@example.com")
    principal = app.auth.authenticate(bootstrap["api_key"])
    imported = app.evidence_imports.import_csv(
        principal,
        raw=_amazon_business_csv(),
        platform="amazon",
        report_type="amazon_business_report",
        filename="business-report.csv",
        observed_at="2026-08-22T10:00:00+08:00",
        idempotency_key="amazon-business-2026-w34",
        request_id="request-1",
    )
    assert imported["platform"] == "amazon"
    assert imported["row_count"] == 2
    assert imported["columns"] == [
        "child_asin", "sessions", "units_ordered", "ordered_product_sales"
    ]
    assert imported["column_mapping"]["ASIN (Child)"] == "child_asin"
    assert imported["media_type"] == "text/csv"
    object_path = app.db.path.parent / f"{app.db.path.name}.evidence_objects" / imported["object_key"]
    assert object_path.read_bytes() == _amazon_business_csv()
    assert "rows" not in imported
    stored = app.db.get_evidence_import(
        bootstrap["tenant_id"], imported["id"], include_rows=True
    )
    assert stored["rows"][0]["ordered_product_sales"] == "239.92"
    assert stored["rows"][0]["sessions"] == "120"

    replay = app.evidence_imports.import_csv(
        principal,
        raw=_amazon_business_csv(),
        platform="amazon",
        report_type="amazon_business_report",
        filename="business-report.csv",
        observed_at="2026-08-22T10:00:00+08:00",
        idempotency_key="amazon-business-2026-w34",
        request_id="request-2",
    )
    assert replay["id"] == imported["id"]
    with pytest.raises(ConflictError, match="different evidence import"):
        app.evidence_imports.import_csv(
            principal,
            raw=_amazon_business_csv().replace(b"239.92", b"249.92"),
            platform="amazon",
            report_type="amazon_business_report",
            filename="business-report.csv",
            observed_at="2026-08-22T10:00:00+08:00",
            idempotency_key="amazon-business-2026-w34",
            request_id="request-3",
        )

    run = app.agent_runs.request(
        principal,
        "weekly_ops",
        "Review this imported Amazon Business Report.",
        None,
        "amazon-import-run",
        "request-4",
        evidence_import_ids=[imported["id"]],
    )
    bundle = app.agent_runs.execute(principal, run["id"], "request-5")
    assert bundle["run"]["platforms"] == ["amazon"]
    amazon_payload = next(
        call[1] for call in provider.calls if call[0] == "platform_amazon_operator"
    )
    assert amazon_payload["evidence"][0]["source_id"] == f"evidence_import:{imported['id']}"
    assert amazon_payload["evidence"][0]["data"]["row_count"] == 2

    other = app.bootstrap("Other", "other@example.com")
    other_principal = app.auth.authenticate(other["api_key"])
    with pytest.raises(NotFoundError):
        app.evidence_imports.get(other_principal, imported["id"])


def test_amazon_xlsx_import_preserves_mapping_formula_and_object(tmp_path: Path) -> None:
    from ecommerce_ai_skills.runtime.api import RuntimeApplication

    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"), agent_provider=_FixtureAgentProvider()
    )
    bootstrap = app.bootstrap("Amazon seller", "owner@example.com")
    principal = app.auth.authenticate(bootstrap["api_key"])
    raw = _amazon_business_xlsx()
    imported = app.evidence_imports.import_xlsx(
        principal,
        raw=raw,
        platform="amazon",
        report_type="amazon_business_report",
        filename="business-report.xlsx",
        observed_at="2026-08-22T10:00:00+08:00",
        sheet_name="Business Report",
        idempotency_key="amazon-business-xlsx",
        request_id="request-1",
    )
    assert imported["row_count"] == 2
    assert imported["sheet_name"] == "Business Report"
    assert imported["formula_cells"] == 1
    assert imported["media_type"].endswith("spreadsheetml.sheet")
    assert imported["column_mapping"]["Ordered Product Sales"] == "ordered_product_sales"
    stored = app.db.get_evidence_import(
        bootstrap["tenant_id"], imported["id"], include_rows=True
    )
    assert stored["rows"][1]["ordered_product_sales"] == "=10+2"
    object_path = app.db.path.parent / f"{app.db.path.name}.evidence_objects" / imported["object_key"]
    assert object_path.read_bytes() == raw
    with pytest.raises(ValidationError, match="sheet not found"):
        app.evidence_imports.import_xlsx(
            principal,
            raw=raw,
            platform="amazon",
            report_type="amazon_business_report",
            filename="business-report.xlsx",
            observed_at="2026-08-22T10:00:00+08:00",
            sheet_name="Missing",
            idempotency_key="missing-sheet",
            request_id="request-2",
        )


def test_csv_import_validates_report_shape_pii_and_formula_cells(tmp_path: Path) -> None:
    from ecommerce_ai_skills.runtime.api import RuntimeApplication

    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"), agent_provider=_FixtureAgentProvider()
    )
    bootstrap = app.bootstrap("A", "owner@example.com")
    principal = app.auth.authenticate(bootstrap["api_key"])
    with pytest.raises(ValidationError, match="required columns"):
        app.evidence_imports.import_csv(
            principal,
            raw=b"Foo,Bar\na,b\n",
            platform="amazon",
            report_type="amazon_business_report",
            filename="bad.csv",
            observed_at="2026-08-22T10:00:00+08:00",
            idempotency_key="bad-columns",
            request_id="request-1",
        )
    with pytest.raises(ValidationError, match="personal or secret columns"):
        app.evidence_imports.import_csv(
            principal,
            raw=b"Order ID,Buyer Email\n1,buyer@example.com\n",
            platform="walmart",
            report_type="platform_generic",
            filename="pii.csv",
            observed_at="2026-08-22T10:00:00+08:00",
            idempotency_key="pii-columns",
            request_id="request-2",
        )

    imported = app.evidence_imports.import_csv(
        principal,
        raw=b'SKU,Note\nWM-1,"=SUM(1,2)"\n',
        platform="walmart",
        report_type="platform_generic",
        filename="walmart.tsv",
        observed_at="2026-08-22T10:00:00+08:00",
        idempotency_key="walmart-generic",
        request_id="request-3",
    )
    assert imported["formula_cells"] == 1
    stored = app.db.get_evidence_import(
        bootstrap["tenant_id"], imported["id"], include_rows=True
    )
    assert stored["rows"][0]["note"] == "=SUM(1,2)"
    localized = app.evidence_imports.import_csv(
        principal,
        raw="商品编号,销量\nSKU-1,3\n".encode(),
        platform="shopee",
        report_type="platform_generic",
        filename="shopee-localized.csv",
        observed_at="2026-08-22T10:00:00+08:00",
        idempotency_key="shopee-localized",
        request_id="request-4",
    )
    assert localized["columns"] == ["商品编号", "销量"]
    assert CSVIngestor.MAX_RAW_BYTES == 2_000_000


def test_schema_v3_agent_runs_migrate_platforms_and_remain_executable(tmp_path: Path) -> None:
    from ecommerce_ai_skills.runtime.api import RuntimeApplication

    path = tmp_path / "runtime.sqlite"
    app = RuntimeApplication(Database(path), agent_provider=_FixtureAgentProvider())
    bootstrap = app.bootstrap("A", "owner@example.com")
    principal = app.auth.authenticate(bootstrap["api_key"])
    run = app.agent_runs.request(
        principal, "weekly_ops", "Prepare a migration-safe weekly review.",
        _weekly_evidence(), "legacy-v3-run", "request-1"
    )
    legacy_evidence = []
    for source in _weekly_evidence():
        legacy = dict(source)
        legacy.pop("platform")
        legacy_evidence.append(legacy)
    with app.db.transaction() as conn:
        conn.execute(
            "UPDATE agent_runs SET evidence_json=?,platforms_json='[]' WHERE id=?",
            (json.dumps(legacy_evidence), run["id"]),
        )
        conn.execute("UPDATE runtime_meta SET value='3' WHERE key='schema_version'")

    provider = _FixtureAgentProvider()
    migrated_app = RuntimeApplication(Database(path), agent_provider=provider)
    migrated_principal = migrated_app.auth.authenticate(bootstrap["api_key"])
    migrated = migrated_app.agent_runs.get(migrated_principal, run["id"])
    assert migrated["run"]["platforms"] == ["amazon", "shopify"]
    completed = migrated_app.agent_runs.execute(migrated_principal, run["id"], "request-2")
    assert completed["run"]["status"] == "completed"


def test_weekly_ops_failure_is_persisted_and_explicitly_retryable(tmp_path: Path) -> None:
    from ecommerce_ai_skills.runtime.api import RuntimeApplication

    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"), agent_provider=_FixtureAgentProvider(bad_ref=True)
    )
    bootstrap = app.bootstrap("A", "owner@example.com")
    principal = app.auth.authenticate(bootstrap["api_key"])
    run = app.agent_runs.request(
        principal, "weekly_ops", "Review this week's evidence safely.",
        _weekly_evidence(), "retryable-run", "request-1"
    )
    with pytest.raises(ExternalServiceError, match="unknown evidence"):
        app.agent_runs.execute(principal, run["id"], "request-2")
    failed = app.agent_runs.get(principal, run["id"])
    assert failed["run"]["status"] == "failed"
    assert any(task["status"] == "failed" for task in failed["tasks"])
    assert not any(artifact["kind"] == "weekly_ops_report" for artifact in failed["artifacts"])

    app.agent_runs.provider = _FixtureAgentProvider()
    completed = app.agent_runs.execute(principal, run["id"], "request-3")
    assert completed["run"]["status"] == "completed"
    assert completed["run"]["attempt_count"] == 2
    attempts = {task["agent_name"]: task["attempt_count"] for task in completed["tasks"]}
    assert attempts["store_manager"] == 1
    assert attempts["cross_platform_controller"] == 1
    assert all(attempts[name] == 2 for name in {
        "evidence_analyst", "platform_amazon_operator", "platform_shopify_operator"
    })


def test_marketplace_agent_cannot_cite_another_platforms_evidence(tmp_path: Path) -> None:
    from ecommerce_ai_skills.runtime.api import RuntimeApplication

    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"),
        agent_provider=_FixtureAgentProvider(bad_platform_ref=True),
    )
    bootstrap = app.bootstrap("A", "owner@example.com")
    principal = app.auth.authenticate(bootstrap["api_key"])
    run = app.agent_runs.request(
        principal,
        "weekly_ops",
        "Keep Amazon and Shopify evidence isolated.",
        _weekly_evidence(),
        "platform-isolation-run",
        "request-1",
    )
    with pytest.raises(ExternalServiceError, match="amazon agent cited another platform"):
        app.agent_runs.execute(principal, run["id"], "request-2")
    assert app.agent_runs.get(principal, run["id"])["run"]["status"] == "failed"


def test_workflow_evaluator_persists_policy_regression(tmp_path: Path) -> None:
    from ecommerce_ai_skills.runtime.api import RuntimeApplication

    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"), agent_provider=_FixtureAgentProvider()
    )
    bootstrap = app.bootstrap("A", "owner@example.com")
    principal = app.auth.authenticate(bootstrap["api_key"])
    run = app.agent_runs.request(
        principal,
        "weekly_ops",
        "Evaluate approval-policy regressions.",
        _weekly_evidence(),
        "evaluation-run",
        "request-1",
    )
    app.agent_runs.execute(principal, run["id"], "request-2")
    with app.db.transaction() as conn:
        row = conn.execute(
            """SELECT id,content_json FROM agent_artifacts
               WHERE run_id=? AND kind='weekly_ops_report' ORDER BY rowid DESC LIMIT 1""",
            (run["id"],),
        ).fetchone()
        report = json.loads(row["content_json"])
        report["priorities"][0]["downstream_action"] = "Adjust campaign bid now"
        report["priorities"][0]["requires_approval"] = False
        conn.execute(
            "UPDATE agent_artifacts SET content_json=? WHERE id=?",
            (json.dumps(report), row["id"]),
        )
    evaluation = app.evaluator.evaluate(principal, run["id"], "request-3")
    assert evaluation["passed"] is False
    approval_check = next(
        check for check in evaluation["details"]["checks"]
        if check["name"] == "approval_policy"
    )
    assert approval_check["passed"] is False
    assert app.db.mission_control(bootstrap["tenant_id"])["counts"]["failed_evaluations"] == 1


def test_openai_responses_provider_requires_real_configuration_and_structured_output() -> None:
    with pytest.raises(MissingCredentialError, match="OPENAI_API_KEY"):
        OpenAIResponsesProvider(environ={}).configuration()
    with pytest.raises(ConnectorNotConfiguredError, match="EAI_OPENAI_MODEL"):
        OpenAIResponsesProvider(environ={"OPENAI_API_KEY": "real-key"}).configuration()

    seen = {}
    structured = {
        "platform": "cross_platform",
        "summary": "Evidence-bound result.",
        "findings": [{
            "title": "Finding",
            "severity": "info",
            "confidence": "high",
            "evidence_refs": ["source-1"],
            "recommendation": "Keep monitoring.",
        }],
        "data_gaps": [],
    }

    class Response:
        status = 200

        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self):
            return json.dumps({
                "status": "completed",
                "output": [{
                    "type": "message",
                    "content": [{"type": "output_text", "text": json.dumps(structured)}],
                }],
            }).encode()

    def transport(request, timeout):
        seen["url"] = request.full_url
        seen["authorization"] = request.get_header("Authorization")
        seen["timeout"] = timeout
        seen["body"] = json.loads(request.data.decode())
        return Response()

    result = OpenAIResponsesProvider(
        environ={"OPENAI_API_KEY": "real-key", "EAI_OPENAI_MODEL": "configured-model"},
        transport=transport,
    ).complete(
        agent_name="evidence_analyst",
        instructions="Inspect evidence.",
        payload={"evidence": [{"source_id": "source-1"}]},
        output_schema=SPECIALIST_SCHEMA,
        safety_identifier="eai_safe_identifier",
    )
    assert result == structured
    assert seen["url"] == "https://api.openai.com/v1/responses"
    assert seen["authorization"] == "Bearer real-key"
    assert seen["timeout"] == 120
    assert seen["body"]["store"] is False
    assert seen["body"]["text"]["format"]["type"] == "json_schema"
    assert seen["body"]["text"]["format"]["strict"] is True
    assert "tools" not in seen["body"]
    assert "real-key" not in json.dumps(seen["body"])


def test_http_agent_run_endpoints_use_tenant_runtime(tmp_path: Path) -> None:
    from email.message import Message

    from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler

    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"), agent_provider=_FixtureAgentProvider()
    )
    bootstrap = app.bootstrap("A", "owner@example.com")

    class DummyHandler(_Handler):
        def __init__(self, method, path, body=None, extra_headers=None):
            self.path = path
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {bootstrap['api_key']}"
            for name, value in (extra_headers or {}).items():
                self.headers[name] = value
            self.body = body or {}
            self.out = None
            self.method = method

        @property
        def app(self): return app

        def _body(self): return self.body

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value, request_id)

        def run(self):
            getattr(self, f"do_{self.method}")()
            return self.out

    created = DummyHandler(
        "POST",
        "/v1/agent-runs",
        {
            "workflow": "weekly_ops",
            "objective": "Find this week's evidence-backed priorities.",
            "evidence": _weekly_evidence(),
        },
        {"Idempotency-Key": "http-weekly-1"},
    ).run()
    assert created[0] == 200 and created[1]["status"] == "requested"
    run_id = created[1]["id"]

    listed = DummyHandler("GET", "/v1/agent-runs?limit=10").run()
    assert listed[0] == 200 and listed[1]["runs"][0]["id"] == run_id
    assert "evidence" not in listed[1]["runs"][0]

    executed = DummyHandler("POST", f"/v1/agent-runs/{run_id}/execute").run()
    assert executed[0] == 200 and executed[1]["run"]["status"] == "completed"

    fetched = DummyHandler("GET", f"/v1/agent-runs/{run_id}").run()
    assert fetched[0] == 200
    assert any(artifact["kind"] == "weekly_ops_report" for artifact in fetched[1]["artifacts"])

    first_events = DummyHandler("GET", f"/v1/agent-runs/{run_id}/events?limit=1").run()
    assert first_events[0] == 200 and first_events[1]["events"]
    assert first_events[1]["next_cursor"] is not None
    next_events = DummyHandler(
        "GET",
        f"/v1/agent-runs/{run_id}/events?after={first_events[1]['next_cursor']}",
    ).run()
    assert next_events[0] == 200
    assert all(event["sequence"] > int(first_events[1]["next_cursor"]) for event in next_events[1]["events"])

    invalid = DummyHandler(
        "POST",
        "/v1/agent-runs",
        {"workflow": "weekly_ops", "objective": "Missing evidence should fail.", "evidence": []},
        {"Idempotency-Key": "http-weekly-invalid"},
    ).run()
    assert invalid[0] == 422


def test_http_csv_import_and_agent_run_reference(tmp_path: Path) -> None:
    import io
    from email.message import Message

    from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler

    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"), agent_provider=_FixtureAgentProvider()
    )
    bootstrap = app.bootstrap("A", "owner@example.com")

    class DummyHandler(_Handler):
        def __init__(self, method, path, *, body=None, raw=None, extra_headers=None):
            self.path = path
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {bootstrap['api_key']}"
            for name, value in (extra_headers or {}).items():
                self.headers[name] = value
            self.body = body or {}
            self.rfile = io.BytesIO(raw or b"")
            if raw is not None:
                self.headers["Content-Length"] = str(len(raw))
            self.out = None
            self.method = method

        @property
        def app(self): return app

        def _body(self): return self.body

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value, request_id)

        def run(self):
            getattr(self, f"do_{self.method}")()
            return self.out

    uploaded = DummyHandler(
        "POST",
        "/v1/evidence-imports",
        raw=_amazon_business_csv(),
        extra_headers={
            "Content-Type": "text/csv",
            "X-Evidence-Platform": "amazon",
            "X-Evidence-Type": "amazon_business_report",
            "X-Evidence-Filename": "business-report.csv",
            "X-Evidence-Observed-At": "2026-08-22T10:00:00+08:00",
            "Idempotency-Key": "http-import-1",
        },
    ).run()
    assert uploaded[0] == 200 and uploaded[1]["row_count"] == 2
    import_id = uploaded[1]["id"]

    listed = DummyHandler("GET", "/v1/evidence-imports").run()
    assert listed[0] == 200 and listed[1]["imports"][0]["id"] == import_id

    uploaded_xlsx = DummyHandler(
        "POST",
        "/v1/evidence-imports",
        raw=_amazon_business_xlsx(),
        extra_headers={
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "X-Evidence-Platform": "amazon",
            "X-Evidence-Type": "amazon_business_report",
            "X-Evidence-Filename": "business-report.xlsx",
            "X-Evidence-Observed-At": "2026-08-22T10:00:00+08:00",
            "X-Evidence-Sheet": "Business Report",
            "Idempotency-Key": "http-import-xlsx",
        },
    ).run()
    assert uploaded_xlsx[0] == 200
    assert uploaded_xlsx[1]["sheet_name"] == "Business Report"

    run = DummyHandler(
        "POST",
        "/v1/agent-runs",
        body={
            "workflow": "weekly_ops",
            "objective": "Review the uploaded Amazon evidence.",
            "evidence_import_ids": [import_id],
        },
        extra_headers={"Idempotency-Key": "http-import-run"},
    ).run()
    assert run[0] == 200 and run[1]["platforms"] == ["amazon"]


def test_durable_job_worker_executes_and_explicitly_retries_agent_run(tmp_path: Path) -> None:
    from ecommerce_ai_skills.runtime.api import RuntimeApplication

    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"),
        agent_provider=_FixtureAgentProvider(bad_ref=True),
    )
    bootstrap = app.bootstrap("A", "owner@example.com")
    principal = app.auth.authenticate(bootstrap["api_key"])
    run = app.agent_runs.request(
        principal,
        "weekly_ops",
        "Execute this run through the durable worker.",
        _weekly_evidence(),
        "worker-run",
        "request-1",
    )
    job = app.jobs.enqueue_agent_run(
        principal, run["id"], "worker-job", "request-2", max_attempts=2
    )
    replay = app.jobs.enqueue_agent_run(
        principal, run["id"], "worker-job", "request-3", max_attempts=2
    )
    assert replay["id"] == job["id"]

    first = app.jobs.run_once()
    assert first["status"] == "queued"
    assert first["attempt_count"] == 1
    assert app.agent_runs.get(principal, run["id"])["run"]["status"] == "failed"

    with app.db.transaction() as conn:
        conn.execute(
            "UPDATE jobs SET available_at='2000-01-01T00:00:00+00:00' WHERE id=?",
            (job["id"],),
        )
    app.agent_runs.provider = _FixtureAgentProvider()
    second = app.jobs.run_once()
    assert second["status"] == "succeeded"
    assert second["attempt_count"] == 2
    assert second["result"]["run_status"] == "completed"
    assert app.jobs.run_once() is None


def test_scheduler_materializes_weekly_run_and_job_then_advances(tmp_path: Path) -> None:
    from ecommerce_ai_skills.runtime.api import RuntimeApplication

    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"), agent_provider=_FixtureAgentProvider()
    )
    bootstrap = app.bootstrap("A", "owner@example.com")
    principal = app.auth.authenticate(bootstrap["api_key"])
    imported = app.evidence_imports.import_csv(
        principal,
        raw=_amazon_business_csv(),
        platform="amazon",
        report_type="amazon_business_report",
        filename="business-report.csv",
        observed_at="2026-08-22T10:00:00+08:00",
        idempotency_key="schedule-evidence",
        request_id="request-1",
    )
    schedule = app.schedules.create(
        principal,
        name="Amazon weekly review",
        objective="Review the latest imported Amazon evidence every week.",
        evidence_import_ids=[],
        evidence_selectors=[
            {"platform": "amazon", "report_type": "amazon_business_report"}
        ],
        interval_minutes=10_080,
        next_run_at="2000-01-01T00:00:00+00:00",
        request_id="request-2",
    )
    tick = app.schedules.tick_once()
    assert tick["schedule_id"] == schedule["id"]
    assert tick["run"]["status"] == "requested"
    assert tick["job"]["status"] == "queued"
    assert app.schedules.tick_once() is None
    advanced = app.db.get_schedule(bootstrap["tenant_id"], schedule["id"])
    assert advanced["last_run_at"] is not None
    completed = app.jobs.run_once()
    assert completed["status"] == "succeeded"
    disabled = app.schedules.set_enabled(
        principal, schedule["id"], False, "request-3"
    )
    assert disabled["enabled"] is False


def test_mission_control_and_approval_inbox_are_real_tenant_views(tmp_path: Path) -> None:
    from email.message import Message
    from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler

    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"), agent_provider=_FixtureAgentProvider()
    )
    bootstrap = app.bootstrap("A", "owner@example.com")
    owner = app.auth.authenticate(bootstrap["api_key"])
    requested = app.actions.request(
        owner,
        "shopify.sync_products",
        {"external_account_id": "primary"},
        "approval-inbox-action",
        "request-1",
    )
    dashboard = app.db.mission_control(bootstrap["tenant_id"])
    assert dashboard["counts"]["actions"]["requested"] == 1
    assert dashboard["approval_inbox"][0]["id"] == requested["id"]

    class DummyHandler(_Handler):
        def __init__(self, path):
            self.path = path
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {bootstrap['api_key']}"
            self.out = None

        @property
        def app(self): return app

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value, request_id)

    mission = DummyHandler("/v1/mission-control")
    mission.do_GET()
    assert mission.out[0] == 200
    assert mission.out[1]["counts"]["actions"]["requested"] == 1
    approvals = DummyHandler("/v1/approvals")
    approvals.do_GET()
    assert approvals.out[0] == 200
    assert approvals.out[1]["actions"][0]["id"] == requested["id"]

    other = app.bootstrap("B", "other@example.com")
    assert app.db.mission_control(other["tenant_id"])["approval_inbox"] == []


def test_worker_and_scheduler_cli_once_exit_cleanly_without_work(tmp_path: Path) -> None:
    import subprocess
    import sys

    path = tmp_path / "runtime.sqlite"
    for command in ("worker", "scheduler"):
        result = subprocess.run(
            [sys.executable, "-m", "ecommerce_ai_skills.cli", command, "--db", str(path), "--once"],
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout == ""


def test_http_health_and_auth_boundary(tmp_path: Path) -> None:
    from email.message import Message

    from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler

    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    bootstrap = app.bootstrap("A", "owner@example.com")

    class DummyHandler(_Handler):
        def __init__(self, path: str, headers: Message):
            self.path = path
            self.headers = headers
            self.out = None

        @property
        def app(self):
            return app

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value, request_id)

    health = DummyHandler("/healthz", Message())
    health.do_GET()
    assert health.out[0] == 200 and health.out[1]["status"] == "ok"

    ready = DummyHandler("/readyz", Message())
    ready.do_GET()
    assert ready.out[0] == 200 and ready.out[1]["status"] == "ready"

    unauthorized = DummyHandler("/v1/me", Message())
    unauthorized.do_GET()
    assert unauthorized.out[0] == 401

    headers = Message()
    headers["Authorization"] = f"Bearer {bootstrap['api_key']}"
    authorized = DummyHandler("/v1/me", headers)
    authorized.do_GET()
    assert authorized.out[0] == 200
    assert authorized.out[1]["tenant_id"] == bootstrap["tenant_id"]
    assert authorized.out[1]["tenant_mode"] == "production"


def test_http_user_onboarding_closes_two_actor_approval_flow(tmp_path: Path) -> None:
    from email.message import Message

    from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler

    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    bootstrap = app.bootstrap("A", "owner@example.com")

    class DummyHandler(_Handler):
        def __init__(self, method: str, path: str, api_key: str, body: dict | None = None, extra_headers: dict | None = None):
            self.path = path
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {api_key}"
            for name, value in (extra_headers or {}).items():
                self.headers[name] = value
            self.body = body or {}
            self.out = None
            self.method = method

        @property
        def app(self):
            return app

        def _body(self):
            return self.body

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value, request_id)

        def run(self):
            getattr(self, f"do_{self.method}")()
            return self.out

    created = DummyHandler(
        "POST", "/v1/users", bootstrap["api_key"], {"email": "admin@example.com", "role": "admin"}
    ).run()
    assert created[0] == 201
    admin_id = created[1]["user"]["id"]

    issued = DummyHandler(
        "POST", "/v1/api-keys", bootstrap["api_key"], {"user_id": admin_id}
    ).run()
    assert issued[0] == 201
    admin_key = issued[1]["api_key"]

    listed = DummyHandler("GET", "/v1/users", bootstrap["api_key"]).run()
    assert listed[0] == 200
    assert {user["email"] for user in listed[1]["users"]} == {"owner@example.com", "admin@example.com"}

    requested = DummyHandler(
        "POST",
        "/v1/actions",
        bootstrap["api_key"],
        {"operation": "shopify.sync_products", "payload": {"external_account_id": "store"}},
        {"Idempotency-Key": "public-flow-1"},
    ).run()
    assert requested[0] == 200 and requested[1]["status"] == "requested"

    approved = DummyHandler(
        "POST", f"/v1/actions/{requested[1]['id']}/approve", admin_key
    ).run()
    assert approved[0] == 200 and approved[1]["status"] == "approved"

    viewer = DummyHandler(
        "POST", "/v1/users", bootstrap["api_key"], {"email": "viewer@example.com", "role": "viewer"}
    ).run()
    promoted = DummyHandler(
        "PATCH", f"/v1/users/{viewer[1]['user']['id']}", bootstrap["api_key"], {"role": "operator"}
    ).run()
    assert promoted[0] == 200 and promoted[1]["user"]["role"] == "operator"

    forbidden_owner_creation = DummyHandler(
        "POST", "/v1/users", admin_key, {"email": "owner-2@example.com", "role": "owner"}
    ).run()
    assert forbidden_owner_creation[0] == 403

    unknown_user_field = DummyHandler(
        "POST",
        "/v1/users",
        bootstrap["api_key"],
        {"email": "extra@example.com", "role": "viewer", "tenant_id": "other"},
    ).run()
    assert unknown_user_field[0] == 422

    self_demotion = DummyHandler(
        "PATCH", f"/v1/users/{bootstrap['user_id']}", bootstrap["api_key"], {"role": "viewer"}
    ).run()
    assert self_demotion[0] == 409

    other = app.bootstrap("B", "other-owner@example.com")
    other_users = DummyHandler("GET", "/v1/users", other["api_key"]).run()
    assert [user["email"] for user in other_users[1]["users"]] == ["other-owner@example.com"]
    cross_tenant_role_change = DummyHandler(
        "PATCH", f"/v1/users/{admin_id}", other["api_key"], {"role": "viewer"}
    ).run()
    assert cross_tenant_role_change[0] == 404

    with pytest.raises(ConflictError, match="last owner"):
        app.db.update_user_role(other["tenant_id"], other["user_id"], "viewer")

    audit_actions = {event["action"] for event in app.db.list_audit(bootstrap["tenant_id"])}
    assert {"user.create", "user.role_update", "api_key.issue", "action.request", "action.approve"} <= audit_actions


def test_metrics_are_disposable_and_visible_only_to_authenticated_viewers(tmp_path: Path) -> None:
    from email.message import Message
    from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler

    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    bootstrap = app.bootstrap("A", "owner@example.com")
    app.metrics.increment("http_requests_total", 3)

    class DummyHandler(_Handler):
        def __init__(self, headers: Message):
            self.path = "/v1/metrics"
            self.headers = headers
            self.out = None

        @property
        def app(self):
            return app

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value, request_id)

    headers = Message()
    headers["Authorization"] = f"Bearer {bootstrap['api_key']}"
    handler = DummyHandler(headers)
    handler.do_GET()
    assert handler.out[0] == 200
    assert handler.out[1]["counters"]["http_requests_total"] == 4


def test_rate_limiter_and_public_bind_guard(tmp_path: Path) -> None:
    limiter = RateLimiter(1)
    limiter.check("client-a")
    with pytest.raises(RateLimitError) as caught:
        limiter.check("client-a")
    assert caught.value.retry_after >= 1

    from ecommerce_ai_skills.runtime.api import RuntimeApplication
    RuntimeApplication._validate_bind_host("127.0.0.1", False)
    RuntimeApplication._validate_bind_host("::1", False)
    with pytest.raises(ValidationError, match="allow-public"):
        RuntimeApplication._validate_bind_host("0.0.0.0", False)
    RuntimeApplication._validate_bind_host("0.0.0.0", True)


def test_action_lease_expiry_and_explicit_retry(tmp_path: Path) -> None:
    db = Database(tmp_path / "runtime.sqlite")
    tenant, owner = db.create_tenant("A", "owner@example.com")
    admin = db.create_user(tenant, "admin@example.com", "admin")
    operator = db.create_user(tenant, "operator@example.com", "operator")
    auth = AuthService(db)
    service = ActionService(db, auth)
    op = auth.authenticate(auth.issue_key(tenant, operator))
    adm = auth.authenticate(auth.issue_key(tenant, admin))
    action = service.request(op, "shopify.sync_products", {"external_account_id": "store"}, "lease-1", "r1")
    service.approve(adm, action["id"], "r2")
    claimed = db.claim_action(tenant, action["id"], lease_seconds=1)
    assert claimed["status"] == "executing" and claimed["attempt_count"] == 1
    with db.transaction() as conn:
        conn.execute("UPDATE actions SET lease_until='2000-01-01T00:00:00+00:00' WHERE id=?", (action["id"],))
    reclaimed = db.claim_action(tenant, action["id"], lease_seconds=60)
    assert reclaimed["attempt_count"] == 2
    with pytest.raises(ConflictError, match="action is executing"):
        db.transition_action(tenant, action["id"], "executing", "failed", error="stale", expected_attempt=1)
    db.transition_action(tenant, action["id"], "executing", "failed", error="temporary")
    retried = service.retry(op, action["id"], "r3")
    assert retried["status"] == "approved"
