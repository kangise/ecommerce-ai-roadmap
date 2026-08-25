from __future__ import annotations

import io
import json
import sqlite3
from email.message import Message
from pathlib import Path

import pytest

from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.errors import (
    AuthorizationError,
    NotFoundError,
    ValidationError,
)
from ecommerce_ai_skills.runtime.storage import Database


def _app(tmp_path: Path):
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    bootstrap = app.bootstrap("Metric tenant", "owner@example.com")
    owner = app.auth.authenticate(bootstrap["api_key"])
    viewer_user = app.auth.create_user(owner, "viewer@example.com", "viewer")
    viewer = app.auth.authenticate(app.auth.issue_for_user(owner, viewer_user["id"]))
    other = app.bootstrap("Other", "other@example.com")
    outsider = app.auth.authenticate(other["api_key"])
    return app, owner, viewer, outsider, bootstrap["api_key"]


def _import(
    app: RuntimeApplication,
    principal,
    filename: str,
    raw: bytes,
    *,
    report_type: str = "amazon_business_report",
    observed_at: str = "2026-08-20T00:00:00Z",
):
    return app.evidence_imports.import_csv(
        principal,
        raw=raw,
        platform="amazon",
        report_type=report_type,
        filename=filename,
        observed_at=observed_at,
        idempotency_key=f"evidence:{filename}",
        request_id=f"evidence:{filename}",
    )


def test_schema_v14_tables_and_cross_tenant_constraints(tmp_path: Path) -> None:
    app, owner, _, outsider, _ = _app(tmp_path)
    imported = _import(
        app,
        owner,
        "schema.csv",
        b"ASIN,Sessions,Units Ordered\nA,10,2\n",
    )
    result = app.metric_observations.materialize(
        owner, imported["id"], "schema-materialize", "schema-materialize"
    )
    assert app.db.readiness()["schema_version"] == 15
    with app.db.connect() as connection:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert {"metric_materializations", "metric_observations"} <= tables
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """INSERT INTO metric_observations(
                   id,tenant_id,materialization_id,evidence_import_id,platform,
                   report_type,metric_key,series_key,value_decimal,currency,unit,
                   time_grain,period_start,period_end,observed_at,dimensions_json,
                   provenance_json,quality_json,calculation_version,created_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    "cross-tenant",
                    outsider.tenant_id,
                    result["id"],
                    imported["id"],
                    "amazon",
                    "amazon_business_report",
                    "sessions",
                    "sessions|-|-|{}",
                    "1",
                    None,
                    "count",
                    "snapshot",
                    "2026-08-20T00:00:00Z",
                    "2026-08-20T00:00:00Z",
                    "2026-08-20T00:00:00Z",
                    "{}",
                    "{}",
                    "{}",
                    "amazon-metrics-v2",
                    "2026-08-20T00:00:00Z",
                ),
            )


def test_schema_v13_migrates_to_v14_without_runtime_seed_data(tmp_path: Path) -> None:
    path = tmp_path / "migration.sqlite"
    db = Database(path)
    with db.transaction() as connection:
        connection.execute("DROP TABLE metric_observations")
        connection.execute("DROP TABLE metric_materializations")
        connection.execute(
            "UPDATE runtime_meta SET value='13' WHERE key='schema_version'"
        )
    migrated = Database(path)
    assert migrated.readiness()["schema_version"] == 15
    with migrated.connect() as connection:
        assert connection.execute(
            "SELECT count(*) FROM metric_materializations"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT count(*) FROM metric_observations"
        ).fetchone()[0] == 0


def test_currency_isolation_conversion_rounding_and_quarantine(tmp_path: Path) -> None:
    app, owner, _, _, _ = _app(tmp_path)
    imported = _import(
        app,
        owner,
        "mixed.csv",
        (
            b"ASIN,Sessions,Units Ordered,Ordered Product Sales,Currency Code\n"
            b"A,3,1,10.25,USD\n"
            b"B,3,1,20.50,EUR\n"
            b"C,3,1,$30.00,\n"
        ),
    )
    materialization = app.metric_observations.materialize(
        owner, imported["id"], "mixed", "mixed"
    )
    assert materialization["status"] == "partial"
    assert materialization["quarantine_count"] == 1
    assert materialization["currencies"] == ["EUR", "USD"]
    assert "missing_or_invalid_currency" in materialization["quality_summary"]["flags"]
    page = app.metric_observations.list_observations(
        owner, evidence_import_id=imported["id"]
    )
    observations = page["observations"]
    revenue = sorted(
        (item["currency"], item["value_decimal"])
        for item in observations
        if item["metric_key"] == "revenue"
    )
    assert revenue == [("EUR", "20.5"), ("USD", "10.25")]
    conversion = next(
        item for item in observations if item["metric_key"] == "conversion_rate"
    )
    assert conversion["value_decimal"] == "0.333333333"
    assert "mixed_currency_isolated" in next(
        item for item in observations if item["metric_key"] == "revenue"
    )["quality"]["flags"]
    assert "period_scope_unknown" in conversion["quality"]["flags"]
    replay = app.metric_observations.materialize(
        owner, imported["id"], "mixed", "mixed-replay"
    )
    assert replay["id"] == materialization["id"]
    assert len(app.metric_observations.list_observations(owner)["observations"]) == 5
    reloaded = Database(app.db.path)
    assert len(reloaded.list_metric_observations(owner.tenant_id)[0]) == 5


def test_invalid_decimals_and_missing_currency_are_never_silently_accepted(
    tmp_path: Path,
) -> None:
    app, owner, _, _, _ = _app(tmp_path)
    imported = _import(
        app,
        owner,
        "invalid.csv",
        (
            b"ASIN,Ordered Product Sales,Currency Code\n"
            b"A,1e40,USD\nB,12.1234567891,USD\nC,10.00,\n"
            b'D,10.00,ZZZ\nE,"1,2",USD\n'
        ),
    )
    result = app.metric_observations.materialize(
        owner, imported["id"], "invalid", "invalid"
    )
    assert result["status"] == "quarantined"
    assert result["observation_count"] == 0
    assert result["quarantine_count"] == 5
    assert set(result["quality_summary"]["flags"]) >= {
        "invalid_number",
        "too_precise",
        "missing_or_invalid_currency",
    }
    replay = app.metric_observations.materialize(
        owner, imported["id"], "invalid", "invalid-replay"
    )
    assert replay["id"] == result["id"] and replay["status"] == "quarantined"


def test_conversion_uses_only_rows_with_valid_units_and_sessions(
    tmp_path: Path,
) -> None:
    app, owner, _, _, _ = _app(tmp_path)
    imported = _import(
        app,
        owner,
        "paired-conversion.csv",
        b"ASIN,Sessions,Units Ordered\nA,bad,10\nB,10,2\n",
    )
    result = app.metric_observations.materialize(
        owner, imported["id"], "paired-conversion", "paired-conversion"
    )
    assert result["status"] == "partial"
    observations = app.metric_observations.list_observations(
        owner, evidence_import_id=imported["id"]
    )["observations"]
    conversion = next(
        item for item in observations if item["metric_key"] == "conversion_rate"
    )
    assert conversion["value_decimal"] == "0.2"
    assert "incomplete_conversion_pair" in result["quality_summary"]["flags"]


def test_stale_running_materialization_is_reclaimed_with_bounded_attempts(
    tmp_path: Path,
) -> None:
    app, owner, _, _, _ = _app(tmp_path)
    imported = _import(
        app,
        owner,
        "lease.csv",
        b"ASIN,Sessions,Units Ordered\nA,10,2\n",
    )
    running, replayed = app.db.start_metric_materialization(
        owner.tenant_id,
        owner.user_id,
        imported["id"],
        "lease-key",
        calculation_version=app.metric_observations.CALCULATION_VERSION,
    )
    assert running["status"] == "running" and replayed is False
    fresh, replayed = app.db.start_metric_materialization(
        owner.tenant_id,
        owner.user_id,
        imported["id"],
        "lease-key",
        calculation_version=app.metric_observations.CALCULATION_VERSION,
    )
    assert fresh["attempt_count"] == 1 and replayed is True
    with app.db.transaction() as connection:
        connection.execute(
            "UPDATE metric_materializations SET lease_until=? WHERE id=?",
            ("2000-01-01T00:00:00+00:00", running["id"]),
        )
    reclaimed, replayed = app.db.start_metric_materialization(
        owner.tenant_id,
        owner.user_id,
        imported["id"],
        "lease-key",
        calculation_version=app.metric_observations.CALCULATION_VERSION,
    )
    assert reclaimed["status"] == "running"
    assert reclaimed["attempt_count"] == 2 and replayed is False
    with app.db.transaction() as connection:
        connection.execute(
            """UPDATE metric_materializations
               SET attempt_count=max_attempts,lease_until=? WHERE id=?""",
            ("2000-01-01T00:00:00+00:00", running["id"]),
        )
    exhausted, replayed = app.db.start_metric_materialization(
        owner.tenant_id,
        owner.user_id,
        imported["id"],
        "lease-key",
        calculation_version=app.metric_observations.CALCULATION_VERSION,
    )
    assert replayed is True
    assert exhausted["status"] == "failed"
    assert exhausted["error_code"] == "max_attempts"


def test_rbac_tenant_scope_filters_and_cursor_pages(tmp_path: Path) -> None:
    app, owner, viewer, outsider, _ = _app(tmp_path)
    first = _import(
        app,
        owner,
        "first.csv",
        b"ASIN,Sessions,Units Ordered\nA,10,2\n",
    )
    second = _import(
        app,
        owner,
        "second.csv",
        b"ASIN,Sessions,Units Ordered\nA,20,4\n",
        observed_at="2026-08-21T00:00:00Z",
    )
    with pytest.raises(AuthorizationError):
        app.metric_observations.materialize(
            viewer, first["id"], "viewer", "viewer"
        )
    app.metric_observations.materialize(owner, first["id"], "first", "first")
    app.metric_observations.materialize(owner, second["id"], "second", "second")
    page_one = app.metric_observations.list_observations(
        viewer, limit=1, metric_key="sessions"
    )
    assert len(page_one["observations"]) == 1 and page_one["next_cursor"]
    page_two = app.metric_observations.list_observations(
        viewer,
        limit=1,
        metric_key="sessions",
        cursor=page_one["next_cursor"],
    )
    assert len(page_two["observations"]) == 1
    assert app.metric_observations.list_observations(outsider)["observations"] == []
    with pytest.raises(NotFoundError):
        app.metric_observations.get_observation(
            outsider, page_one["observations"][0]["id"]
        )
    with pytest.raises(ValidationError):
        app.metric_observations.list_observations(viewer, currency="usd")
    with pytest.raises(ValidationError):
        app.metric_observations.list_observations(viewer, platform="unknown")
    with pytest.raises(ValidationError):
        app.metric_observations.list_observations(viewer, cursor="x" * 201)


def test_backfill_is_bounded_cursor_resumable_and_keeps_item_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app, owner, _, _, _ = _app(tmp_path)
    older = _import(
        app,
        owner,
        "older.csv",
        b"ASIN,Sessions,Units Ordered\nA,10,2\n",
    )
    newer = _import(
        app,
        owner,
        "newer.csv",
        b"ASIN,Sessions,Units Ordered\nA,20,4\n",
    )
    original = app.metric_observations._extract

    def fail_one(imported, source):
        if imported["id"] == newer["id"]:
            raise RuntimeError("test extractor failure")
        return original(imported, source)

    monkeypatch.setattr(app.metric_observations, "_extract", fail_one)
    first = app.metric_observations.backfill(
        owner, limit=1, cursor=None, request_id="backfill-1"
    )
    assert first["processed"] == 1
    assert first["materializations"][0]["status"] == "failed"
    assert first["next_cursor"] == newer["id"]
    second = app.metric_observations.backfill(
        owner, limit=1, cursor=first["next_cursor"], request_id="backfill-2"
    )
    assert second["materializations"][0]["evidence_import_id"] == older["id"]
    assert second["materializations"][0]["status"] == "succeeded"
    with pytest.raises(ValidationError):
        app.metric_observations.backfill(
            owner, limit=101, cursor=None, request_id="too-large"
        )


def test_briefing_reads_isolated_observation_series_and_safe_period_changes(
    tmp_path: Path,
) -> None:
    app, owner, _, _, _ = _app(tmp_path)
    for index, (value, currency, observed) in enumerate(
        (("10", "USD", "2026-08-20T00:00:00Z"), ("20", "USD", "2026-08-21T00:00:00Z"), ("8", "EUR", "2026-08-21T00:00:00Z"))
    ):
        imported = _import(
            app,
            owner,
            f"brief-{index}.csv",
            (
                "ASIN,Ordered Product Sales,Currency Code\n"
                f"A,{value},{currency}\n"
            ).encode(),
            observed_at=observed,
        )
        app.metric_observations.materialize(
            owner, imported["id"], f"brief-{index}", f"brief-{index}"
        )
    revenue = [
        metric
        for metric in app.briefing.get(owner, "amazon")["metrics"]
        if metric["key"] == "revenue"
    ]
    assert [(item["currency"], item["value"]) for item in revenue] == [
        ("EUR", 8.0),
        ("USD", 20.0),
    ]
    assert len({item["series_id"] for item in revenue}) == 2
    usd = revenue[1]
    assert usd["change_percent"] == 100.0
    assert all(point["period_start"] == point["period_end"] for point in usd["series"])


def test_briefing_never_compares_overlapping_or_different_grain_series(
    tmp_path: Path,
) -> None:
    app, owner, _, _, _ = _app(tmp_path)
    periods = [
        ("2026-08-01T00:00:00Z", "2026-08-08T00:00:00Z", "range", "scope-a"),
        ("2026-08-05T00:00:00Z", "2026-08-12T00:00:00Z", "range", "scope-a"),
        ("2026-08-12T00:00:00Z", "2026-08-12T00:00:00Z", "snapshot", "scope-b"),
    ]
    for index, (start, end, grain, scope) in enumerate(periods):
        imported = app.evidence_imports.import_csv(
            owner,
            raw=b"key,value\nrevenue,1\n",
            platform="amazon",
            report_type="platform_generic",
            filename=f"period-{index}.csv",
            observed_at=end,
            idempotency_key=f"period-evidence-{index}",
            request_id=f"period-evidence-{index}",
        )
        running, _ = app.db.start_metric_materialization(
            owner.tenant_id,
            owner.user_id,
            imported["id"],
            f"period-materialization-{index}",
            calculation_version=app.metric_observations.CALCULATION_VERSION,
        )
        app.db.complete_metric_materialization(
            owner.tenant_id,
            running["id"],
            status="succeeded",
            issues=[],
            observations=[
                {
                    "connector_account_id": None,
                    "marketplace_id": None,
                    "platform": "amazon",
                    "report_type": "platform_generic",
                    "metric_key": "revenue",
                    "series_key": f"revenue|USD|{scope}",
                    "value_decimal": str(100 + index * 10),
                    "currency": "USD",
                    "unit": "currency",
                    "time_grain": grain,
                    "period_start": start,
                    "period_end": end,
                    "observed_at": end,
                    "dimensions": {"scope": scope},
                    "provenance": {
                        "source_sha256": imported["sha256"],
                        "source_row": 1,
                        "source_field": "value",
                        "mapping_version": "amazon-metrics-v2",
                    },
                    "quality_flags": {"status": "accepted", "flags": []},
                }
            ],
        )
    revenue = [
        item
        for item in app.briefing.get(owner, "amazon")["metrics"]
        if item["key"] == "revenue"
    ]
    assert len(revenue) == 2
    range_series = next(item for item in revenue if item["time_grain"] == "range")
    assert len(range_series["series"]) == 2
    assert range_series["change_percent"] is None
    snapshot_series = next(
        item for item in revenue if item["time_grain"] == "snapshot"
    )
    assert len(snapshot_series["series"]) == 1


def test_metric_http_endpoints_and_validation(tmp_path: Path) -> None:
    app, owner, _, _, api_key = _app(tmp_path)
    imported = _import(
        app,
        owner,
        "api.csv",
        b"ASIN,Sessions,Units Ordered\nA,10,2\n",
    )

    class Handler(_Handler):
        def __init__(self, method: str, path: str, body: dict | None = None):
            self.command = method
            self.path = path
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {api_key}"
            raw = json.dumps(body).encode() if body is not None else b""
            self.headers["Content-Length"] = str(len(raw))
            self.rfile = io.BytesIO(raw)
            self.out = None

        @property
        def app(self):
            return app

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value)

    create = Handler(
        "POST", f"/v1/evidence-imports/{imported['id']}/metric-materialization", {}
    )
    create.headers["Idempotency-Key"] = "api-materialize"
    create.do_POST()
    assert create.out[0] == 200
    listed = Handler("GET", "/v1/metric-observations?limit=1")
    listed.do_GET()
    assert listed.out[0] == 200 and len(listed.out[1]["observations"]) == 1
    filtered = Handler("GET", "/v1/metric-observations?platform=shopify")
    filtered.do_GET()
    assert filtered.out == (200, {"observations": [], "next_cursor": None})
    detail_id = listed.out[1]["observations"][0]["id"]
    detail = Handler("GET", f"/v1/metric-observations/{detail_id}")
    detail.do_GET()
    assert detail.out[0] == 200
    bad_limit = Handler("GET", "/v1/metric-observations?limit=nope")
    bad_limit.do_GET()
    assert bad_limit.out[0] == 422
    bad_backfill = Handler("POST", "/v1/metric-materializations/backfill", {"limit": True})
    bad_backfill.do_POST()
    assert bad_backfill.out[0] == 422
