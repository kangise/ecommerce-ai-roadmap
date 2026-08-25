from __future__ import annotations

import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from email.message import Message
from pathlib import Path
from threading import Barrier

import pytest

from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.agent_graphs import default_graph_definition
from ecommerce_ai_skills.runtime.errors import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from ecommerce_ai_skills.runtime.storage import Database


class DailyProvider:
    def __init__(self, verdict: str = "approved", fail: bool = False):
        self.verdict = verdict
        self.fail = fail
        self.calls = []

    def configuration(self):
        return "daily_fixture", "daily-fixture-v1"

    def complete(self, *, agent_name, instructions, payload, output_schema, safety_identifier):
        self.calls.append((agent_name, payload))
        if self.fail:
            raise RuntimeError("fixture provider failure")
        if agent_name == "store_manager":
            source = payload["evidence_catalog"][0]
            return {
                "executive_summary": "Review the date-bound operating evidence.",
                "priorities": [{
                    "rank": 1, "title": "Review current performance",
                    "why_now": "The scheduled source is eligible.",
                    "evidence_refs": [source["source_id"]],
                    "platforms": [source["platform"]],
                    "expected_impact": "Clarify the next decision.", "confidence": "medium",
                    "recommended_owner": f"platform_{source['platform']}_operator",
                    "downstream_action": "Prepare a proposal.",
                    "action_type": "external_change", "requires_approval": True,
                    "metric_claim": {"operation": "none", "observation_refs": []},
                }],
                "risks": [], "limitations": ["Only scheduled evidence was reviewed."],
            }
        if agent_name == "operations_reviewer":
            source = payload["evidence_catalog"][0]
            issues = [] if self.verdict == "approved" else [{
                "code": "needs_revision", "message": "Revise the brief.",
                "severity": "warning", "evidence_refs": [source["source_id"]],
                "platforms": [source["platform"]],
            }]
            return {
                "verdict": self.verdict, "issues": issues,
                "evidence_refs": [source["source_id"]],
                "limitations": payload["manager_report"]["limitations"],
            }
        platform = payload["target_platform"]
        evidence = payload.get("evidence") or []
        source_id = evidence[0]["source_id"] if evidence else next(
            finding["evidence_refs"][0]
            for result in payload["specialist_findings"].values()
            for finding in result["findings"]
        )
        return {
            "platform": platform, "summary": "Evidence-bound daily finding.",
            "findings": [{
                "title": "Review performance", "severity": "warning",
                "confidence": "medium", "evidence_refs": [source_id],
                "recommendation": "Review before changing operations.",
            }],
            "data_gaps": [],
        }


def make_app(tmp_path: Path, provider=None):
    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"), agent_provider=provider or DailyProvider()
    )
    bootstrap = app.bootstrap("Daily tenant", "owner@example.com")
    return app, app.auth.authenticate(bootstrap["api_key"])


def create_schedule(app, owner, **overrides):
    graph_version_id = overrides.get("graph_version_id")
    if graph_version_id is None:
        graph_version_id = app.agent_graphs.ensure_default(owner)["id"]
    values = {
        "name": "Amazon daily review", "platform": "amazon",
        "objective": "Review Amazon operating priorities for this local business day.",
        "timezone_name": "America/New_York", "local_time": "08:00",
        "graph_version_id": graph_version_id,
        "evidence_selectors": [{"report_type": "amazon_business_report"}],
        "max_source_age_hours": 48, "enabled": True, "request_id": "schedule-create",
    }
    values.update(overrides)
    return app.daily_ops.create(owner, **values)


def insert_evidence(app, owner, *, observed_at="2026-08-25T12:00:00+00:00", key="daily-source"):
    evidence, _ = app.db.create_evidence_import(
        owner.tenant_id, owner.user_id, key,
        platform="amazon", report_type="amazon_business_report", filename="daily.csv",
        observed_at=observed_at, sha256=(key.encode().hex() + "0" * 64)[:64],
        delimiter=",", rows=[{"asin": "A1", "sessions": "10"}],
        columns=["asin", "sessions"], column_mapping={"asin": "asin", "sessions": "sessions"},
        blank_rows_skipped=0, formula_cells=0, media_type="text/csv", byte_size=10,
        object_key=f"objects/{key}", sheet_name=None,
    )
    return evidence


def test_schema_v16_migrates_to_v17_and_composite_tenant_integrity(tmp_path: Path):
    path = tmp_path / "migration.sqlite"
    db = Database(path)
    with db.connect() as conn:
        conn.execute("DROP TABLE daily_ops_runs")
        conn.execute("DROP TABLE daily_ops_schedules")
        conn.execute("UPDATE runtime_meta SET value='16' WHERE key='schema_version'")
    migrated = Database(path)
    assert migrated.readiness()["schema_version"] == 17
    app = RuntimeApplication(migrated, agent_provider=DailyProvider())
    one = app.bootstrap("One", "one@example.com")
    two = app.bootstrap("Two", "two@example.com")
    owner = app.auth.authenticate(one["api_key"])
    outsider = app.auth.authenticate(two["api_key"])
    schedule = create_schedule(app, owner)
    graph = app.agent_graphs.get_version(owner, schedule["graph_version_id"])
    with migrated.connect() as conn, pytest.raises(
        sqlite3.IntegrityError, match="graph binding"
    ):
        conn.execute(
            """INSERT INTO daily_ops_runs(
               id,tenant_id,schedule_id,local_date,timezone,scheduled_for,status,
               graph_version_id,graph_version_hash,schedule_config_json,
               schedule_config_hash,created_at,updated_at
               ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                "bad-hash", owner.tenant_id, schedule["id"], "2026-08-24", "UTC",
                "2026-08-24T00:00:00+00:00", "scheduled",
                schedule["graph_version_id"], "0" * 64,
                "{}", "0" * 64,
                "2026-08-24T00:00:00Z", "2026-08-24T00:00:00Z",
            ),
        )
    with migrated.connect() as conn, pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO daily_ops_runs(
               id,tenant_id,schedule_id,local_date,timezone,scheduled_for,status,
               graph_version_id,graph_version_hash,schedule_config_json,
               schedule_config_hash,created_at,updated_at
               ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            ("bad", outsider.tenant_id, schedule["id"], "2026-08-25", "UTC",
             "2026-08-25T00:00:00+00:00", "scheduled", schedule["graph_version_id"],
             graph["definition_hash"], "{}", "0" * 64,
             "2026-08-25T00:00:00Z", "2026-08-25T00:00:00Z"),
        )


def test_schedule_rbac_tenant_update_and_persistence(tmp_path: Path):
    app, owner = make_app(tmp_path)
    viewer_id = app.db.create_user(owner.tenant_id, "viewer@example.com", "viewer")
    viewer = app.db.principal_for_user(owner.tenant_id, viewer_id)
    with pytest.raises(AuthorizationError):
        create_schedule(app, viewer)
    with pytest.raises(ValidationError, match="cannot be selected"):
        create_schedule(app, owner, name="Wrong platform", platform="shopify")
    schedule = create_schedule(app, owner)
    assert app.daily_ops.get_schedule(viewer, schedule["id"])["timezone"] == "America/New_York"
    updated = app.daily_ops.update(
        owner, schedule["id"], request_id="update", local_time="09:15",
        evidence_selectors=[{"report_type": "amazon_business_report"}],
    )
    assert updated["local_time"] == "09:15"
    other = app.bootstrap("Other", "other@example.com")
    outsider = app.auth.authenticate(other["api_key"])
    with pytest.raises(NotFoundError):
        app.daily_ops.get_schedule(outsider, schedule["id"])
    reloaded = RuntimeApplication(Database(app.db.path), agent_provider=DailyProvider())
    assert reloaded.daily_ops.get_schedule(owner, schedule["id"])["local_time"] == "09:15"


def test_occurrence_freezes_schedule_config_and_hash(tmp_path: Path):
    provider = DailyProvider()
    app, owner = make_app(tmp_path, provider)
    schedule = create_schedule(
        app, owner, timezone_name="UTC", local_time="00:00"
    )
    insert_evidence(
        app, owner, observed_at="2026-08-24T23:00:00+00:00", key="snapshot-source"
    )
    run = app.daily_ops.trigger(
        owner, schedule["id"], "snapshot-trigger", "2026-08-25"
    )
    assert len(run["schedule_config_hash"]) == 64
    assert run["schedule_config"]["objective"] == schedule["objective"]
    with app.db.connect() as conn, pytest.raises(
        sqlite3.IntegrityError, match="identity is immutable"
    ):
        conn.execute(
            "UPDATE daily_ops_runs SET schedule_config_json='{}' WHERE id=?",
            (run["id"],),
        )
    app.daily_ops.update(
        owner,
        schedule["id"],
        request_id="mutate-schedule",
        name="Changed Shopify plan",
        platform="shopify",
        objective="Use a changed objective that must not affect the existing occurrence.",
        evidence_selectors=[{"report_type": "platform_generic"}],
    )
    completed = app.daily_ops.execute(owner, run["id"], "snapshot-execute")
    assert completed["brief"]["schedule"] == {
        "id": schedule["id"],
        "name": schedule["name"],
        "platform": "amazon",
    }
    manager_payload = next(
        payload for agent_name, payload in provider.calls if agent_name == "store_manager"
    )
    assert manager_payload["objective"] == schedule["objective"]
    disabled = create_schedule(app, owner, name="Disabled", enabled=False)
    with pytest.raises(ConflictError, match="disabled"):
        app.daily_ops.trigger(owner, disabled["id"], "disabled", "2026-08-25")
    disabled = app.db.advance_daily_ops_schedule(
        owner.tenant_id,
        disabled["id"],
        expected_local_date=disabled["next_local_date"],
        next_local_date="2020-01-01",
    )
    reenabled = app.daily_ops.update(
        owner, disabled["id"], request_id="reenable", enabled=True
    )
    assert reenabled["next_local_date"] != "2020-01-01"


def test_trigger_is_date_idempotent_empty_and_late_arrival_retry(tmp_path: Path):
    app, owner = make_app(tmp_path)
    schedule = create_schedule(app, owner)
    empty = app.daily_ops.trigger(owner, schedule["id"], "empty", "2026-08-25")
    assert empty["status"] == "empty"
    assert empty["brief"]["status"] == "empty"
    replay = app.daily_ops.trigger(owner, schedule["id"], "replay", "2026-08-25")
    assert replay["id"] == empty["id"]
    insert_evidence(app, owner, key="late-source")
    retried = app.daily_ops.retry(owner, empty["id"], "retry")
    assert retried["status"] == "scheduled"
    assert retried["selected_evidence_import_ids"]
    assert app.daily_ops.retry(owner, empty["id"], "retry-replay")["id"] == empty["id"]
    completed = app.daily_ops.execute(owner, empty["id"], "execute")
    assert completed["status"] == "completed"
    assert completed["brief"]["review_status"] == "approved"
    assert completed["brief"]["local_date"] == "2026-08-25"
    child = app.agent_runs.get(owner, completed["agent_run_id"])["run"]
    assert child["origin"] == "daily_ops"
    assert child["parent_daily_ops_run_id"] == completed["id"]
    assert child["parent_daily_ops_attempt"] == completed["attempt_count"]
    reloaded = RuntimeApplication(Database(app.db.path), agent_provider=DailyProvider())
    assert reloaded.daily_ops.get_brief(owner, empty["id"])["brief"] == completed["brief"]


def test_concurrent_trigger_creates_one_local_date_occurrence(tmp_path: Path):
    app, owner = make_app(tmp_path)
    schedule = create_schedule(app, owner)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda request_id: app.daily_ops.trigger(
                    owner, schedule["id"], request_id, "2026-08-25"
                ),
                ("concurrent-a", "concurrent-b"),
            )
        )
    assert len({result["id"] for result in results}) == 1
    assert len(app.daily_ops.list_runs(owner, schedule_id=schedule["id"])) == 1


def test_stale_graph_blocks_occurrence_and_retry_rebinds_reviewed_version(tmp_path: Path):
    app, owner = make_app(tmp_path)
    schedule = create_schedule(app, owner)
    with app.db.transaction() as conn:
        conn.execute(
            """UPDATE agent_graph_versions
               SET status='retired',retired_at='2026-08-25T00:00:00Z'
               WHERE tenant_id=? AND id=?""",
            (owner.tenant_id, schedule["graph_version_id"]),
        )
    blocked = app.daily_ops.trigger(
        owner, schedule["id"], "stale-graph-trigger", "2026-08-25"
    )
    assert blocked["status"] == "blocked"
    assert blocked["error_code"] == "GRAPH_NOT_EXECUTABLE"

    replacement = app.agent_graphs.create(
        owner, "Daily replacement graph", default_graph_definition(), "replacement-create"
    )
    published = app.agent_graphs.publish(
        owner,
        replacement["graph"]["id"],
        replacement["versions"][0]["id"],
        "replacement-publish",
    )
    app.daily_ops.update(
        owner,
        schedule["id"],
        request_id="replacement-schedule",
        graph_version_id=published["id"],
    )
    insert_evidence(app, owner)
    with pytest.raises(ConflictError, match="published graph"):
        app.daily_ops.retry(owner, blocked["id"], "replacement-retry")
    replacement_schedule = create_schedule(
        app,
        owner,
        name="Replacement schedule",
        graph_version_id=published["id"],
        request_id="replacement-schedule-create",
    )
    replacement_run = app.daily_ops.trigger(
        owner,
        replacement_schedule["id"],
        "replacement-trigger",
        "2026-08-25",
    )
    assert replacement_run["status"] == "scheduled"
    assert replacement_run["graph_version_id"] == published["id"]
    assert replacement_run["id"] != blocked["id"]


def test_dst_ambiguous_fold_zero_and_nonexistent_blocks(tmp_path: Path):
    app, owner = make_app(tmp_path)
    ambiguous = create_schedule(
        app, owner, name="Ambiguous", local_time="01:30",
        evidence_selectors=[{"report_type": "amazon_returns"}],
    )
    run = app.daily_ops.trigger(owner, ambiguous["id"], "ambiguous", "2026-11-01")
    assert run["scheduled_for"] == "2026-11-01T05:30:00+00:00"
    nonexistent = create_schedule(
        app, owner, name="Nonexistent", local_time="02:30",
        evidence_selectors=[{"report_type": "amazon_returns"}],
    )
    blocked = app.daily_ops.trigger(owner, nonexistent["id"], "nonexistent", "2026-03-08")
    assert blocked["status"] == "blocked"
    assert blocked["error_code"] == "NONEXISTENT_LOCAL_TIME"
    with pytest.raises(ConflictError, match="frozen local time"):
        app.daily_ops.retry(owner, blocked["id"], "retry-before-correction")
    app.daily_ops.update(
        owner, nonexistent["id"], request_id="correct-time", local_time="03:30"
    )
    with pytest.raises(ConflictError, match="frozen local time"):
        app.daily_ops.retry(owner, blocked["id"], "retry-after-correction")
    corrected_schedule = create_schedule(
        app,
        owner,
        name="Corrected",
        local_time="03:30",
        evidence_selectors=[{"report_type": "amazon_returns"}],
        request_id="corrected-create",
    )
    corrected = app.daily_ops.trigger(
        owner, corrected_schedule["id"], "corrected-trigger", "2026-03-08"
    )
    assert corrected["status"] == "empty"
    assert corrected["scheduled_for"] == "2026-03-08T07:30:00+00:00"


def test_normalized_metrics_replace_raw_import_and_input_limit_blocks(tmp_path: Path):
    app, owner = make_app(tmp_path)
    schedule = create_schedule(app, owner)
    imported = insert_evidence(app, owner)
    with app.db.connect() as conn:
        conn.execute(
            """INSERT INTO metric_materializations(
               id,tenant_id,evidence_import_id,created_by,idempotency_key,calculation_version,
               status,observation_count,quarantine_count,currencies_json,quality_flags_json,
               issues_json,created_at,updated_at,completed_at
               ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            ("mat", owner.tenant_id, imported["id"], owner.user_id, "mat", "v1",
             "succeeded", 1, 0, "[]", "[]", "[]", "2026-08-25T13:00:00Z",
             "2026-08-25T13:00:00Z", "2026-08-25T13:00:00Z"),
        )
        conn.execute(
            """INSERT INTO metric_observations(
               id,tenant_id,materialization_id,evidence_import_id,platform,report_type,
               metric_key,series_key,value_decimal,currency,unit,time_grain,period_start,
               period_end,observed_at,dimensions_json,provenance_json,quality_json,
               calculation_version,created_at
               ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            ("obs", owner.tenant_id, "mat", imported["id"], "amazon",
             "amazon_business_report", "sessions", "sessions:all", "10", None,
             "count", "day", "2026-08-25", "2026-08-25", "2026-08-25T12:00:00Z",
             "{}", "{}", "[]", "v1", "2026-08-25T13:00:00Z"),
        )
    run = app.daily_ops.trigger(owner, schedule["id"], "metric", "2026-08-25")
    assert run["selected_evidence_import_ids"] == []
    assert run["selected_metric_observation_ids"] == ["obs"]
    with app.db.connect() as conn:
        for index in range(1, 21):
            conn.execute(
                """INSERT INTO metric_observations(
                   id,tenant_id,materialization_id,evidence_import_id,platform,report_type,
                   metric_key,series_key,value_decimal,currency,unit,time_grain,period_start,
                   period_end,observed_at,dimensions_json,provenance_json,quality_json,
                   calculation_version,created_at
                   ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (f"obs-{index}", owner.tenant_id, "mat", imported["id"], "amazon",
                 "amazon_business_report", "sessions", f"sessions:{index}", str(index), None,
                 "count", "day", "2026-08-25", "2026-08-25", "2026-08-25T12:00:00Z",
                 "{}", "{}", "[]", "v1", "2026-08-25T13:00:00Z"),
            )
    over_limit_schedule = create_schedule(app, owner, name="Too many metrics")
    blocked = app.daily_ops.trigger(
        owner, over_limit_schedule["id"], "over-limit", "2026-08-25"
    )
    assert blocked["status"] == "blocked"
    assert blocked["error_code"] == "SOURCE_SELECTION_INVALID"


@pytest.mark.parametrize(
    ("provider", "expected", "code"),
    [(DailyProvider("revision_required"), "blocked", "REVIEW_NOT_APPROVED"),
     (DailyProvider(fail=True), "failed", "ExternalServiceError")],
)
def test_reviewer_and_provider_failures_are_terminal_and_safe(tmp_path: Path, provider, expected, code):
    app, owner = make_app(tmp_path, provider)
    schedule = create_schedule(app, owner)
    insert_evidence(app, owner, observed_at="2026-08-24T23:00:00+00:00")
    run = app.daily_ops.trigger(owner, schedule["id"], "trigger", "2026-08-25")
    result = app.daily_ops.execute(owner, run["id"], "execute")
    assert result["status"] == expected
    assert result["error_code"] == code
    assert (result["brief"] is not None) == (expected == "blocked")


def test_scheduler_due_gate_worker_and_atomic_claim(tmp_path: Path):
    app, owner = make_app(tmp_path)
    schedule = create_schedule(app, owner, timezone_name="UTC", local_time="08:00")
    schedule = app.db.advance_daily_ops_schedule(
        owner.tenant_id,
        schedule["id"],
        expected_local_date=schedule["next_local_date"],
        next_local_date="2026-08-25",
    )
    eligible = insert_evidence(
        app, owner, observed_at="2026-08-25T07:00:00+00:00", key="before-cutoff"
    )
    lookahead = insert_evidence(
        app, owner, observed_at="2026-08-25T18:00:00+00:00", key="after-cutoff"
    )
    assert app.daily_ops.scheduler_run_once(datetime(2026, 8, 25, 7, 59, tzinfo=timezone.utc)) is None
    run = app.daily_ops.scheduler_run_once(datetime(2026, 8, 25, 8, 0, tzinfo=timezone.utc))
    assert run and run["status"] == "scheduled"
    assert run["selected_evidence_import_ids"] == [eligible["id"]]
    assert lookahead["id"] not in run["selected_evidence_import_ids"]
    assert app.daily_ops.scheduler_run_once(datetime(2026, 8, 25, 9, 0, tzinfo=timezone.utc)) is None
    first = app.db.claim_daily_ops_run(tenant_id=owner.tenant_id, run_id=run["id"])
    second = app.db.claim_daily_ops_run(tenant_id=owner.tenant_id, run_id=run["id"])
    assert first is not None and second is None
    with app.db.connect() as conn, pytest.raises(
        sqlite3.IntegrityError, match="terminal state"
    ):
        conn.execute(
            "UPDATE daily_ops_runs SET status='completed' WHERE id=?",
            (run["id"],),
        )
    app.db.update_daily_ops_run(
        owner.tenant_id,
        run["id"],
        {"lease_until": "2000-01-01T00:00:00+00:00"},
    )
    completed = app.daily_ops.worker_run_once()
    assert completed and completed["status"] == "completed"


def test_expired_worker_is_fenced_from_new_attempt(tmp_path: Path):
    app, owner = make_app(tmp_path)
    schedule = create_schedule(
        app, owner, timezone_name="UTC", local_time="00:00", name="Fenced worker"
    )
    insert_evidence(
        app, owner, observed_at="2026-08-24T23:00:00+00:00", key="fence-source"
    )
    run = app.daily_ops.trigger(owner, schedule["id"], "fence-trigger", "2026-08-25")
    old = app.db.claim_daily_ops_run(tenant_id=owner.tenant_id, run_id=run["id"])
    assert old is not None and old["lease_token"]
    app.db.update_daily_ops_run(
        owner.tenant_id,
        run["id"],
        {"lease_until": "2000-01-01T00:00:00+00:00"},
    )
    current = app.db.claim_daily_ops_run(
        tenant_id=owner.tenant_id, run_id=run["id"]
    )
    assert current is not None
    assert current["attempt_count"] == old["attempt_count"] + 1
    assert current["lease_token"] != old["lease_token"]
    with pytest.raises(ConflictError, match="lease was lost"):
        app.db.update_claimed_daily_ops_run(
            owner.tenant_id,
            run["id"],
            attempt_count=old["attempt_count"],
            lease_token=old["lease_token"],
            values={"error_message": "stale worker overwrite"},
        )
    renewed = app.db.renew_daily_ops_lease(
        owner.tenant_id,
        run["id"],
        attempt_count=current["attempt_count"],
        lease_token=current["lease_token"],
    )
    assert renewed["status"] == "running"


def test_approved_orphan_agent_run_is_ineligible_downstream(tmp_path: Path):
    app, owner = make_app(tmp_path)
    schedule = create_schedule(
        app, owner, timezone_name="UTC", local_time="00:00", name="Orphan fencing"
    )
    insert_evidence(
        app, owner, observed_at="2026-08-24T23:00:00+00:00", key="orphan-source"
    )
    daily_run = app.daily_ops.trigger(
        owner, schedule["id"], "orphan-trigger", "2026-08-25"
    )
    old = app.db.claim_daily_ops_run(
        tenant_id=owner.tenant_id, run_id=daily_run["id"]
    )
    agent_run = app.agent_runs.request(
        owner,
        "weekly_ops",
        "Complete an old Daily Ops attempt after its lease is reclaimed.",
        None,
        "orphan-agent-run",
        "orphan-agent-run-request",
        evidence_import_ids=old["selected_evidence_import_ids"],
        metric_observation_ids=old["selected_metric_observation_ids"],
        graph_version_id=old["graph_version_id"],
        origin="daily_ops",
        parent_daily_ops_run_id=old["id"],
        parent_daily_ops_attempt=old["attempt_count"],
        parent_daily_ops_lease_token=old["lease_token"],
    )
    app.db.update_claimed_daily_ops_run(
        owner.tenant_id,
        old["id"],
        attempt_count=old["attempt_count"],
        lease_token=old["lease_token"],
        values={"agent_run_id": agent_run["id"]},
    )
    app.db.update_daily_ops_run(
        owner.tenant_id,
        old["id"],
        {"lease_until": "2000-01-01T00:00:00+00:00"},
    )
    current = app.db.claim_daily_ops_run(
        tenant_id=owner.tenant_id, run_id=old["id"]
    )
    completed_orphan = app.agent_runs.execute(
        owner, agent_run["id"], "orphan-agent-run-execute"
    )
    assert completed_orphan["run"]["review_status"] == "approved"
    app.db.update_claimed_daily_ops_run(
        owner.tenant_id,
        current["id"],
        attempt_count=current["attempt_count"],
        lease_token=current["lease_token"],
        values={
            "status": "failed",
            "lease_until": None,
            "lease_token": None,
            "completed_at": "2026-08-25T01:00:00+00:00",
            "error_code": "NEW_ATTEMPT_FAILED",
            "error_message": "new attempt failed safely",
        },
    )
    assert app.briefing.get(owner, "amazon")["brief_run_id"] is None
    assert app.evaluator.evaluate(
        owner, agent_run["id"], "orphan-agent-run-eval"
    )["passed"] is False


def test_expired_final_attempt_becomes_durable_failure(tmp_path: Path):
    app, owner = make_app(tmp_path)
    schedule = create_schedule(
        app, owner, timezone_name="UTC", local_time="00:00", name="Exhausted worker"
    )
    insert_evidence(
        app, owner, observed_at="2026-08-24T23:00:00+00:00", key="exhausted-source"
    )
    run = app.daily_ops.trigger(
        owner, schedule["id"], "exhausted-trigger", "2026-08-25"
    )
    with app.db.transaction() as conn:
        conn.execute(
            """UPDATE daily_ops_runs
               SET status='running',attempt_count=max_attempts,
                   lease_until='2000-01-01T00:00:00+00:00',lease_token='expired'
               WHERE tenant_id=? AND id=?""",
            (owner.tenant_id, run["id"]),
        )
    failed = app.daily_ops.worker_run_once()
    assert failed["id"] == run["id"]
    assert failed["status"] == "failed"
    assert failed["error_code"] == "ATTEMPTS_EXHAUSTED"


def test_scheduler_cursor_catches_up_missed_local_dates(tmp_path: Path):
    app, owner = make_app(tmp_path)
    schedule = create_schedule(app, owner, timezone_name="UTC", local_time="00:00")
    app.db.advance_daily_ops_schedule(
        owner.tenant_id,
        schedule["id"],
        expected_local_date=schedule["next_local_date"],
        next_local_date="2026-08-24",
    )
    now = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)
    caught_up = [app.daily_ops.scheduler_run_once(now) for _ in range(3)]
    assert [run["local_date"] for run in caught_up] == [
        "2026-08-24",
        "2026-08-25",
        "2026-08-26",
    ]
    assert app.daily_ops.scheduler_run_once(now) is None
    assert app.daily_ops.get_schedule(owner, schedule["id"])["next_local_date"] == (
        "2026-08-27"
    )


def test_execution_owner_demotion_is_guarded_and_worker_fails_safe(tmp_path: Path):
    app, owner = make_app(tmp_path)
    operator_id = app.db.create_user(owner.tenant_id, "daily-operator@example.com", "operator")
    operator = app.db.principal_for_user(owner.tenant_id, operator_id)
    guarded = create_schedule(app, operator, name="Guarded owner")
    with pytest.raises(ConflictError, match="Daily Ops work before demotion"):
        app.db.update_user_role(owner.tenant_id, operator_id, "viewer")
    app.daily_ops.update(
        operator, guarded["id"], request_id="disable-before-demotion", enabled=False
    )
    assert app.db.update_user_role(owner.tenant_id, operator_id, "viewer")["role"] == "viewer"
    with pytest.raises(ConflictError, match="creator must be operator"):
        app.daily_ops.update(
            owner, guarded["id"], request_id="unsafe-reenable", enabled=True
        )

    worker_id = app.db.create_user(owner.tenant_id, "worker-owner@example.com", "operator")
    worker_owner = app.db.principal_for_user(owner.tenant_id, worker_id)
    schedule = create_schedule(
        app,
        worker_owner,
        name="Defensive worker",
        timezone_name="UTC",
        local_time="00:00",
    )
    insert_evidence(
        app,
        worker_owner,
        observed_at="2026-08-24T23:00:00+00:00",
        key="worker-owner-source",
    )
    run = app.daily_ops.trigger(
        worker_owner, schedule["id"], "worker-owner-trigger", "2026-08-25"
    )
    with app.db.transaction() as conn:
        conn.execute(
            "UPDATE users SET role='viewer' WHERE tenant_id=? AND id=?",
            (owner.tenant_id, worker_id),
        )
    blocked = app.daily_ops.worker_run_once()
    assert blocked["id"] == run["id"]
    assert blocked["status"] == "blocked"
    assert blocked["error_code"] == "EXECUTION_PRINCIPAL_INACTIVE"


def test_retired_graph_does_not_block_safe_schedule_disable_and_demotion(tmp_path: Path):
    app, owner = make_app(tmp_path)
    operator_id = app.db.create_user(owner.tenant_id, "retired-owner@example.com", "operator")
    operator = app.db.principal_for_user(owner.tenant_id, operator_id)
    schedule = create_schedule(app, operator, name="Retired graph schedule")
    with app.db.transaction() as conn:
        conn.execute(
            """UPDATE agent_graph_versions
               SET status='retired',retired_at='2026-08-25T00:00:00Z'
               WHERE tenant_id=? AND id=?""",
            (owner.tenant_id, schedule["graph_version_id"]),
        )
    api_key = app.auth.issue_key(owner.tenant_id, owner.user_id)

    class PatchHandler(_Handler):
        def __init__(self):
            self.path = f"/v1/daily-ops-schedules/{schedule['id']}"
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {api_key}"
            self.out = None

        @property
        def app(self):
            return app

        def _body(self):
            return {
                "name": schedule["name"],
                "platform": schedule["platform"],
                "objective": schedule["objective"],
                "timezone_name": schedule["timezone"],
                "local_time": schedule["local_time"],
                "graph_version_id": schedule["graph_version_id"],
                "evidence_selectors": schedule["evidence_selectors"],
                "max_source_age_hours": schedule["max_source_age_hours"],
                "enabled": False,
            }

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value)

    handler = PatchHandler()
    handler.do_PATCH()
    assert handler.out[0] == 200
    disabled = handler.out[1]
    assert disabled["enabled"] is False
    assert app.db.update_user_role(owner.tenant_id, operator_id, "viewer")["role"] == "viewer"


def test_reenable_and_demotion_race_preserves_execution_role_invariant(tmp_path: Path):
    app, owner = make_app(tmp_path)
    operator_id = app.db.create_user(owner.tenant_id, "race-owner@example.com", "operator")
    operator = app.db.principal_for_user(owner.tenant_id, operator_id)
    schedule = create_schedule(app, operator, name="Role race", enabled=False)
    barrier = Barrier(2)

    def enable():
        barrier.wait()
        try:
            app.daily_ops.update(
                owner, schedule["id"], request_id="race-enable", enabled=True
            )
            return "enabled"
        except ConflictError:
            return "enable-blocked"

    def demote():
        barrier.wait()
        try:
            app.db.update_user_role(owner.tenant_id, operator_id, "viewer")
            return "demoted"
        except ConflictError:
            return "demotion-blocked"

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(enable), pool.submit(demote)]
        outcomes = {future.result() for future in futures}
    current_schedule = app.daily_ops.get_schedule(owner, schedule["id"])
    current_user = app.db.get_user(owner.tenant_id, operator_id)
    assert not (current_schedule["enabled"] and current_user["role"] == "viewer")
    assert "enable-blocked" in outcomes or "demotion-blocked" in outcomes


def test_daily_scheduler_and_worker_cli_once_are_operable(tmp_path: Path):
    path = tmp_path / "cli.sqlite"
    for command in ("daily-scheduler", "daily-worker"):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ecommerce_ai_skills.cli",
                command,
                "--db",
                str(path),
                "--once",
            ],
            cwd=Path(__file__).resolve().parents[1],
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
    assert Database(path).readiness()["schema_version"] == 17


def test_daily_ops_http_routes_rbac_tenant_and_brief_states(tmp_path: Path):
    app, owner = make_app(tmp_path)
    viewer_id = app.db.create_user(owner.tenant_id, "viewer-http@example.com", "viewer")
    viewer_key = app.auth.issue_key(owner.tenant_id, viewer_id)
    owner_key = app.auth.issue_key(owner.tenant_id, owner.user_id)
    other = app.bootstrap("Other HTTP", "other-http@example.com")
    graph = app.agent_graphs.ensure_default(owner)

    class Handler(_Handler):
        def __init__(self, method: str, path: str, api_key: str, body=None):
            self.path = path
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {api_key}"
            self.headers["Idempotency-Key"] = "daily-http"
            self.method = method
            self.body = body or {}
            self.out = None

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
        "/v1/daily-ops-schedules",
        owner_key,
        {
            "name": "HTTP daily",
            "platform": "amazon",
            "objective": "Review the HTTP-selected Amazon evidence each day.",
            "timezone_name": "UTC",
            "local_time": "00:00",
            "graph_version_id": graph["id"],
            "evidence_selectors": [{"report_type": "amazon_business_report"}],
            "max_source_age_hours": 48,
            "enabled": True,
        },
    ).run()
    assert created[0] == 201
    schedule_id = created[1]["id"]
    assert Handler("GET", "/v1/daily-ops-schedules", viewer_key).run()[0] == 200
    assert Handler(
        "POST",
        f"/v1/daily-ops-schedules/{schedule_id}/trigger",
        viewer_key,
        {"local_date": "2026-08-25"},
    ).run()[0] == 403
    insert_evidence(
        app, owner, observed_at="2026-08-24T23:00:00+00:00", key="http-source"
    )
    triggered = Handler(
        "POST",
        f"/v1/daily-ops-schedules/{schedule_id}/trigger",
        owner_key,
        {"local_date": "2026-08-25"},
    ).run()
    assert triggered[0] == 200 and triggered[1]["status"] == "scheduled"
    run_id = triggered[1]["id"]
    assert Handler("GET", f"/v1/daily-ops-runs/{run_id}", other["api_key"]).run()[0] == 404
    assert Handler("GET", f"/v1/daily-ops-runs/{run_id}/brief", owner_key).run()[0] == 409
    executed = Handler(
        "POST", f"/v1/daily-ops-runs/{run_id}/execute", owner_key, {}
    ).run()
    assert executed[0] == 200 and executed[1]["status"] == "completed"
    brief = Handler("GET", f"/v1/daily-ops-runs/{run_id}/brief", viewer_key).run()
    assert brief[0] == 200 and brief[1]["brief"]["status"] == "completed"
