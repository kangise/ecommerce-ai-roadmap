from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from email.message import Message
from pathlib import Path

import pytest

from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.auth import AuthService
from ecommerce_ai_skills.runtime.connectors.amazon_spapi import AmazonSPAPIReportsConnector
from ecommerce_ai_skills.runtime.errors import (
    AuthorizationError,
    ConnectorRateLimitError,
    ExternalServiceError,
    NotFoundError,
    ValidationError,
)
from ecommerce_ai_skills.runtime.evidence import AmazonSalesTrafficJSONFlattener
from ecommerce_ai_skills.runtime.report_syncs import ReportSyncService
from ecommerce_ai_skills.runtime.storage import Database


AMAZON_CONFIG = {
    "region": "na",
    "marketplace_ids": ["ATVPDKIKX0DER"],
    "lwa_client_id_ref": "AMAZON_CLIENT_ID",
    "lwa_client_secret_ref": "AMAZON_CLIENT_SECRET",
    "lwa_refresh_token_ref": "AMAZON_REFRESH_TOKEN",
}
CREDENTIALS = {
    "AMAZON_CLIENT_ID": "client",
    "AMAZON_CLIENT_SECRET": "secret",
    "AMAZON_REFRESH_TOKEN": "refresh",
}
FIXED_NOW = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)


class Response:
    def __init__(self, payload, *, status=200, headers=None, url=None):
        self.status = status
        self.headers = headers or {}
        self.url = url
        self.body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()

    def __enter__(self): return self

    def __exit__(self, *args): return False

    def read(self, amount=-1): return self.body if amount < 0 else self.body[:amount]

    def geturl(self): return self.url


def setup_runtime(tmp_path: Path, *, recipe_key="sales_traffic_daily"):
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    bootstrap = app.bootstrap("A", "owner@example.com")
    owner = app.auth.authenticate(bootstrap["api_key"])
    operator_id = app.db.create_user(owner.tenant_id, "operator@example.com", "operator")
    viewer_id = app.db.create_user(owner.tenant_id, "viewer@example.com", "viewer")
    operator = app.auth.authenticate(app.auth.issue_key(owner.tenant_id, operator_id))
    viewer = app.auth.authenticate(app.auth.issue_key(owner.tenant_id, viewer_id))
    account_id = app.db.add_connector_account(
        owner.tenant_id, "amazon_spapi", "seller", AMAZON_CONFIG
    )
    app.db.set_connector_account_health(owner.tenant_id, account_id, "healthy")
    recipe = app.report_recipes.create(
        owner,
        account_id,
        f"Recipe {recipe_key}",
        recipe_key,
        ["ATVPDKIKX0DER"],
        1440,
        7,
        True,
        "2026-08-26T13:00:00+00:00",
        "recipe-create",
    )
    app.report_syncs.clock = lambda: FIXED_NOW
    return app, bootstrap, owner, operator, viewer, account_id, recipe


def make_polling_due(app, operator, recipe, *, key="sync-1"):
    sync = app.report_syncs.enqueue(operator, recipe["id"], key, "enqueue")
    claimed = app.db.claim_report_sync()
    app.db.mark_report_sync_polling(
        operator.tenant_id, claimed["id"], "REPORT-1", delay_seconds=1
    )
    with app.db.transaction() as conn:
        conn.execute(
            "UPDATE report_syncs SET available_at='2000-01-01T00:00:00+00:00' WHERE id=?",
            (sync["id"],),
        )
    return sync


def test_v12_migration_and_persistence(tmp_path: Path) -> None:
    path = tmp_path / "runtime.sqlite"
    db = Database(path)
    with db.transaction() as conn:
        conn.execute("DROP TABLE report_syncs")
        conn.execute("UPDATE runtime_meta SET value='12' WHERE key='schema_version'")
    migrated = Database(path)
    assert migrated.readiness()["schema_version"] == 15
    with migrated.connect() as conn:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(report_syncs)")}
    assert {"recipe_id", "amazon_report_id", "lease_until", "evidence_import_id"} <= columns


def test_report_sync_database_rejects_cross_tenant_relations(tmp_path: Path) -> None:
    app, _, owner, _, _, account_id, recipe = setup_runtime(tmp_path)
    other_tenant, other_owner_id = app.db.create_tenant("B", "b@example.com")
    with pytest.raises(sqlite3.IntegrityError):
        with app.db.transaction() as conn:
            conn.execute(
                """INSERT INTO report_syncs(
                   id,tenant_id,recipe_id,connector_account_id,created_by,
                   idempotency_key,status,period_start,period_end,available_at,
                   max_attempts,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,'queued',?,?,?,?,?,?)""",
                (
                    "cross-tenant-sync",
                    other_tenant,
                    recipe["id"],
                    account_id,
                    other_owner_id,
                    "cross-tenant",
                    "2026-08-19T12:00:00Z",
                    "2026-08-26T12:00:00Z",
                    "2026-08-26T12:00:00Z",
                    3,
                    "2026-08-26T12:00:00Z",
                    "2026-08-26T12:00:00Z",
                ),
            )
    assert app.db.get_report_recipe(owner.tenant_id, recipe["id"])["id"] == recipe["id"]


def test_enqueue_rbac_tenant_idempotency_and_healthy_gate(tmp_path: Path) -> None:
    app, _, owner, operator, viewer, account_id, recipe = setup_runtime(tmp_path)
    with pytest.raises(AuthorizationError):
        app.report_syncs.enqueue(viewer, recipe["id"], "viewer-key", "request")
    first = app.report_syncs.enqueue(operator, recipe["id"], "same-key", "request-1")
    replay = app.report_syncs.enqueue(operator, recipe["id"], "same-key", "request-2")
    assert replay["id"] == first["id"] and first["status"] == "queued"
    assert first["period_start"] == "2026-08-19T12:00:00Z"
    assert Database(app.db.path).get_report_sync(owner.tenant_id, first["id"])["id"] == first["id"]
    other_tenant, other_owner_id = app.db.create_tenant("B", "b@example.com")
    other = app.auth.authenticate(app.auth.issue_key(other_tenant, other_owner_id))
    with pytest.raises(NotFoundError):
        app.report_syncs.get(other, first["id"])
    app.db.set_connector_account_health(owner.tenant_id, account_id, "unhealthy")
    with pytest.raises(ValidationError, match="healthy"):
        app.report_syncs.enqueue(operator, recipe["id"], "unhealthy-key", "request")


def test_create_report_request_payload_and_polling_transition(tmp_path: Path) -> None:
    app, _, _, operator, _, _, recipe = setup_runtime(tmp_path)
    seen = []

    def transport(request, timeout):
        seen.append((request.method, request.full_url, request.data))
        if request.full_url == "https://api.amazon.com/auth/o2/token":
            return Response({"access_token": "access"}, url=request.full_url)
        return Response({"reportId": "REPORT-1"}, url=request.full_url)

    app.report_syncs.environ = CREDENTIALS
    app.report_syncs.transport = transport
    sync = app.report_syncs.enqueue(operator, recipe["id"], "create-key", "enqueue")
    result = app.report_syncs.run_once()
    assert result["id"] == sync["id"] and result["status"] == "polling"
    assert result["amazon_report_id"] == "REPORT-1"
    method, url, raw = seen[1]
    assert method == "POST" and url.endswith("/reports/2021-06-30/reports")
    payload = json.loads(raw)
    assert payload == {
        "reportType": "GET_SALES_AND_TRAFFIC_REPORT",
        "marketplaceIds": ["ATVPDKIKX0DER"],
        "dataStartTime": "2026-08-19T12:00:00Z",
        "dataEndTime": "2026-08-26T12:00:00Z",
        "reportOptions": {
            "dateGranularity": "DAY",
            "asinGranularity": "CHILD",
        },
    }


def test_poll_backoff_and_429_headers(tmp_path: Path) -> None:
    app, _, _, operator, _, _, recipe = setup_runtime(tmp_path)
    sync = make_polling_due(app, operator, recipe)

    def polling_transport(request, timeout):
        if request.full_url == "https://api.amazon.com/auth/o2/token":
            return Response({"access_token": "access"}, url=request.full_url)
        return Response(
            {"processingStatus": "IN_PROGRESS"}, url=request.full_url
        )

    app.report_syncs.environ = CREDENTIALS
    app.report_syncs.transport = polling_transport
    result = app.report_syncs.run_once()
    assert result["status"] == "polling"
    assert result["processing_status"] == "IN_PROGRESS"
    assert result["attempt_count"] == 2
    assert result["lease_until"] is None

    connector = AmazonSPAPIReportsConnector(
        AMAZON_CONFIG,
        environ=CREDENTIALS,
        transport=lambda request, timeout: Response(
            {}, status=429, headers={"Retry-After": "37", "x-amzn-RateLimit-Limit": "0.5"}, url=request.full_url
        ),
    )
    with pytest.raises(ConnectorRateLimitError) as caught:
        connector.create_report(
            "GET_SALES_AND_TRAFFIC_REPORT",
            ["ATVPDKIKX0DER"],
            "2026-08-19T12:00:00Z",
            "2026-08-26T12:00:00Z",
        )
    assert caught.value.retry_after == 37
    assert caught.value.headers["x-amzn-RateLimit-Limit"] == "0.5"
    assert app.db.get_report_sync(operator.tenant_id, sync["id"])["lease_until"] is None
    queued = app.report_syncs.enqueue(operator, recipe["id"], "rate-limited", "enqueue")
    app.report_syncs.transport = lambda request, timeout: Response(
        {}, status=429, headers={"Retry-After": "37"}, url=request.full_url
    )
    retried = app.report_syncs.run_once()
    assert retried["id"] == queued["id"] and retried["status"] == "queued"
    assert retried["error_code"] == "rate_limited"


def test_unexpected_worker_failure_releases_lease_and_remains_visible(
    tmp_path: Path,
) -> None:
    app, _, _, operator, _, _, recipe = setup_runtime(tmp_path)
    sync = app.report_syncs.enqueue(operator, recipe["id"], "unexpected", "enqueue")

    def fail_connector(config):
        raise RuntimeError("simulated worker crash")

    app.report_syncs._connector = fail_connector
    with pytest.raises(RuntimeError, match="simulated worker crash"):
        app.report_syncs.run_once()
    released = app.db.get_report_sync(operator.tenant_id, sync["id"])
    assert released["status"] == "queued"
    assert released["lease_until"] is None
    assert released["error_code"] == "worker_internal_error"
    assert "simulated worker crash" not in released["error_message"]


def test_report_document_url_rejects_nonstandard_https_ports() -> None:
    AmazonSPAPIReportsConnector._validate_document_url(
        "https://example.amazonaws.com/report.json"
    )
    with pytest.raises(ExternalServiceError, match="host validation"):
        AmazonSPAPIReportsConnector._validate_document_url(
            "https://example.amazonaws.com:8443/report.json"
        )


def test_done_json_report_imports_evidence_and_advances_recipe(tmp_path: Path) -> None:
    app, _, _, operator, _, _, recipe = setup_runtime(tmp_path)
    sync = make_polling_due(app, operator, recipe)
    document = json.dumps(
        {
            "salesAndTrafficByAsin": [
                {
                    "childAsin": "B001",
                    "trafficByAsin": {"sessions": 12, "unitSessionPercentage": 25.5},
                    "salesByAsin": {
                        "unitsOrdered": 3,
                        "orderedProductSales": {"amount": 42.5, "currencyCode": "USD"},
                    },
                }
            ]
        }
    ).encode()
    report_gets = 0

    def transport(request, timeout):
        nonlocal report_gets
        url = request.full_url
        if url == "https://api.amazon.com/auth/o2/token":
            return Response({"access_token": "access"}, url=url)
        if url.endswith("/reports/REPORT-1"):
            report_gets += 1
            return Response(
                {
                    "processingStatus": "DONE",
                    "reportDocumentId": "DOC-1",
                    "reportType": "GET_SALES_AND_TRAFFIC_REPORT",
                    "dataEndTime": "2026-08-26T12:00:00Z",
                },
                url=url,
            )
        if url.endswith("/documents/DOC-1"):
            return Response({"url": "https://example.amazonaws.com/report.json"}, url=url)
        if url == "https://example.amazonaws.com/report.json":
            return Response(document, url=url)
        raise AssertionError(url)

    app.report_syncs.environ = CREDENTIALS
    app.report_syncs.transport = transport
    result = app.report_syncs.run_once()
    assert result["id"] == sync["id"] and result["status"] == "succeeded"
    evidence = app.db.get_evidence_import(
        operator.tenant_id, result["evidence_import_id"], include_rows=True
    )
    assert evidence["report_type"] == "amazon_business_report"
    assert evidence["rows"] == [{
        "asin": "B001",
        "sessions": "12",
        "units_ordered": "3",
        "ordered_product_sales": "42.5",
        "unit_session_percentage": "25.5",
        "currency_code": "USD",
    }]
    advanced = app.db.get_report_recipe(operator.tenant_id, recipe["id"])
    assert advanced["next_run_at"] > recipe["next_run_at"]
    metric_page = app.metric_observations.list_observations(
        operator, evidence_import_id=evidence["id"]
    )
    assert {
        item["metric_key"] for item in metric_page["observations"]
    } == {"revenue", "units_ordered", "sessions", "conversion_rate"}
    assert all(
        "period_scope_unknown" not in item["quality"]["flags"]
        for item in metric_page["observations"]
    )
    assert report_gets == 2


def test_metric_failure_never_reverses_successful_report_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app, _, _, operator, _, _, recipe = setup_runtime(tmp_path)
    sync = make_polling_due(app, operator, recipe, key="metric-failure")

    def fail_materialization(*args, **kwargs):
        raise RuntimeError("test metric failure")

    monkeypatch.setattr(app.metric_observations, "materialize", fail_materialization)
    completed = app.report_syncs._import_done(
        sync,
        recipe,
        {
            "amazon_report_type": "GET_SALES_AND_TRAFFIC_REPORT",
            "observed_at": "2026-08-26T12:00:00Z",
            "content": json.dumps(
                {
                    "salesAndTrafficByAsin": [
                        {
                            "childAsin": "B001",
                            "trafficByAsin": {"sessions": 10},
                            "salesByAsin": {
                                "unitsOrdered": 2,
                                "orderedProductSales": {
                                    "amount": 20,
                                    "currencyCode": "USD",
                                },
                            },
                        }
                    ]
                }
            ).encode(),
        },
    )
    assert completed["status"] == "succeeded"
    assert app.db.get_evidence_import(
        operator.tenant_id, completed["evidence_import_id"]
    )["id"] == completed["evidence_import_id"]
    assert any(
        event["action"] == "marketplace_metric_materialization.failed"
        for event in app.db.list_audit(operator.tenant_id)
    )


def test_fatal_and_missing_credentials_are_terminal(tmp_path: Path) -> None:
    app, _, _, operator, _, _, recipe = setup_runtime(tmp_path)
    first = make_polling_due(app, operator, recipe, key="fatal")

    def fatal_transport(request, timeout):
        if request.full_url == "https://api.amazon.com/auth/o2/token":
            return Response({"access_token": "access"}, url=request.full_url)
        return Response({"processingStatus": "FATAL"}, url=request.full_url)

    app.report_syncs.environ = CREDENTIALS
    app.report_syncs.transport = fatal_transport
    failed = app.report_syncs.run_once()
    assert failed["id"] == first["id"] and failed["status"] == "failed"
    assert failed["processing_status"] == "FATAL"

    second = app.report_syncs.enqueue(operator, recipe["id"], "missing", "enqueue")
    app.report_syncs.environ = {}
    missing = app.report_syncs.run_once()
    assert missing["id"] == second["id"] and missing["status"] == "failed"
    assert missing["error_code"] == "missing_credential"
    assert "AMAZON_" not in missing["error_message"]

    exhausted = app.report_syncs.enqueue(operator, recipe["id"], "exhausted", "enqueue")
    with app.db.transaction() as conn:
        conn.execute("UPDATE report_syncs SET max_attempts=1 WHERE id=?", (exhausted["id"],))
    app.report_syncs.environ = CREDENTIALS
    app.report_syncs.transport = lambda request, timeout: Response(
        {}, status=503, url=request.full_url
    )
    terminal = app.report_syncs.run_once()
    assert terminal["id"] == exhausted["id"] and terminal["status"] == "failed"
    assert terminal["error_code"] == "external_service_error"


def test_sales_traffic_json_flattener_is_bounded() -> None:
    raw = json.dumps({"salesAndTrafficByAsin": [{"childAsin": "B001", "trafficByAsin": {"sessions": 1}, "salesByAsin": {}}]}).encode()
    parsed = AmazonSalesTrafficJSONFlattener.parse(
        raw,
        filename="report.json",
        observed_at="2026-08-26T12:00:00Z",
    )
    assert parsed["rows"][0]["asin"] == "B001"
    with pytest.raises(ValidationError, match="5000-row"):
        AmazonSalesTrafficJSONFlattener.parse(
            json.dumps({"salesAndTrafficByAsin": [{"childAsin": "B"}] * 5001}).encode(),
            filename="report.json",
            observed_at="2026-08-26T12:00:00Z",
        )
    with pytest.raises(ValidationError, match="ASIN"):
        AmazonSalesTrafficJSONFlattener.parse(
            json.dumps({"salesAndTrafficByAsin": [{"trafficByAsin": {}, "salesByAsin": {}}]}).encode(),
            filename="report.json",
            observed_at="2026-08-26T12:00:00Z",
        )
    with pytest.raises(ValidationError, match="finite"):
        AmazonSalesTrafficJSONFlattener.parse(
            json.dumps({"salesAndTrafficByAsin": [{"childAsin": "B001", "trafficByAsin": {"sessions": float("nan")}, "salesByAsin": {}}]}).encode(),
            filename="report.json",
            observed_at="2026-08-26T12:00:00Z",
        )


def test_report_sync_api_and_cli_once(tmp_path: Path) -> None:
    app, bootstrap, _, operator, _, _, recipe = setup_runtime(tmp_path)
    operator_key = app.auth.issue_key(operator.tenant_id, operator.user_id)

    class Handler(_Handler):
        def __init__(self, method, path, body=None):
            self.path = path
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {operator_key}"
            self.headers["Idempotency-Key"] = "api-sync"
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

    created = Handler("POST", f"/v1/report-recipes/{recipe['id']}/sync").run()
    assert created[0] == 202
    sync_id = created[1]["id"]
    assert Handler("GET", "/v1/report-syncs").run()[1]["report_syncs"][0]["id"] == sync_id
    assert Handler("GET", f"/v1/report-syncs/{sync_id}").run()[0] == 200
    command = subprocess.run(
        [sys.executable, "-m", "ecommerce_ai_skills.cli", "report-worker", "--db", str(tmp_path / "empty.sqlite"), "--once"],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    assert command.returncode == 0, command.stderr
