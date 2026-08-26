from __future__ import annotations

import io
import json
import sqlite3
import logging
from datetime import datetime, timedelta, timezone
from email.message import Message
from pathlib import Path

import pytest

from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.storage import (
    MISSION_EVENT_RETENTION,
    Database,
    utc_now,
)


def _published_graph(app: RuntimeApplication, tenant_id: str) -> tuple[str, str]:
    with app.db.connect() as conn:
        row = conn.execute(
            """SELECT id,definition_hash FROM agent_graph_versions
                 WHERE tenant_id=? AND status='published'""",
            (tenant_id,),
        ).fetchone()
    assert row is not None
    return row["id"], row["definition_hash"]


def _frames(raw: bytes) -> list[dict[str, object]]:
    frames = []
    for block in raw.decode().split("\n\n"):
        if not block or block.startswith(":"):
            continue
        fields: dict[str, object] = {}
        for line in block.splitlines():
            name, value = line.split(":", 1)
            value = value.lstrip()
            fields[name] = json.loads(value) if name == "data" else value
        frames.append(fields)
    return frames


class _StreamHandler(_Handler):
    def __init__(
        self,
        app: RuntimeApplication,
        path: str,
        token: str | None,
        *,
        last_event_id: str | None = None,
        wfile: io.BytesIO | None = None,
    ):
        self._app = app
        self.path = path
        self.headers = Message()
        if token is not None:
            self.headers["Authorization"] = f"Bearer {token}"
        if last_event_id is not None:
            self.headers["Last-Event-ID"] = last_event_id
        self.wfile = wfile or io.BytesIO()
        self.status = None
        self.response_headers: dict[str, str] = {}
        self.json_response = None
        self.client_address = ("127.0.0.1", 1234)
        self.close_connection = False

    @property
    def app(self) -> RuntimeApplication:
        return self._app

    def send_response(self, status: int, *args: object) -> None:
        self.status = status

    def send_header(self, name: str, value: str) -> None:
        self.response_headers[name] = value

    def end_headers(self) -> None:
        pass

    def _json(self, status, value, request_id, **kwargs):
        self.status = status
        self.json_response = value
        self.response_headers.update(kwargs.get("extra_headers") or {})


def test_schema_19_ledger_tracks_real_resource_paths_without_payload_leaks(
    tmp_path: Path,
) -> None:
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    bootstrap = app.bootstrap("A", "owner@example.com")
    tenant_id, owner_id = bootstrap["tenant_id"], bootstrap["user_id"]
    owner = app.auth.authenticate(bootstrap["api_key"])
    admin_id = app.db.create_user(tenant_id, "admin@example.com", "admin")
    admin = app.auth.authenticate(app.auth.issue_key(tenant_id, admin_id))
    version_id, version_hash = _published_graph(app, tenant_id)

    account_id = app.db.add_connector_account(
        tenant_id,
        "amazon_spapi",
        "seller-1",
        {
            "region": "na",
            "marketplace_ids": ["ATVPDKIKX0DER"],
            "lwa_client_id_ref": "CLIENT_ID_ENV_NAME",
            "lwa_client_secret_ref": "SECRET_ENV_NAME",
            "lwa_refresh_token_ref": "REFRESH_ENV_NAME",
        },
    )
    recipe = app.db.create_report_recipe(
        tenant_id,
        owner_id,
        connector_account_id=account_id,
        name="Daily report",
        recipe_key="amazon_sales_and_traffic",
        marketplace_ids=["ATVPDKIKX0DER"],
        interval_minutes=1440,
        lookback_days=7,
        enabled=True,
        next_run_at=utc_now(),
    )
    sync, _ = app.db.create_report_sync(
        tenant_id,
        owner_id,
        recipe["id"],
        "sync-1",
        period_start="2026-08-20T00:00:00+00:00",
        period_end="2026-08-26T00:00:00+00:00",
    )
    claimed_sync = app.db.claim_report_sync()
    assert claimed_sync and claimed_sync["id"] == sync["id"]
    app.db.mark_report_sync_polling(
        tenant_id, sync["id"], amazon_report_id="report-1"
    )

    schedule = app.db.create_daily_ops_schedule(
        tenant_id,
        owner_id,
        name="Daily Ops",
        platform="amazon",
        objective="Review operational evidence",
        timezone_name="UTC",
        local_time="08:00",
        graph_version_id=version_id,
        evidence_selectors=[],
        max_source_age_hours=48,
        enabled=True,
        next_local_date="2026-08-27",
    )
    daily, _ = app.db.create_daily_ops_run(
        tenant_id,
        schedule["id"],
        local_date="2026-08-26",
        timezone_name="UTC",
        scheduled_for=utc_now(),
        status="scheduled",
        evidence_import_ids=[],
        metric_observation_ids=[],
        graph_version_id=version_id,
        graph_version_hash=version_hash,
        schedule_config={"platform": "amazon"},
        schedule_config_hash="schedule-hash",
        source_gaps=[],
    )
    claimed_daily = app.db.claim_daily_ops_run(
        tenant_id=tenant_id, run_id=daily["id"]
    )
    assert claimed_daily is not None
    run, _ = app.db.create_agent_run(
        tenant_id,
        owner_id,
        "daily-agent-1",
        "weekly_ops",
        "secret objective must not enter the mission ledger",
        [{"source_id": "evidence-1", "raw_secret": "never-in-events"}],
        ["amazon"],
        provider="fixture",
        graph_version_id=version_id,
        graph_version_hash=version_hash,
        origin="daily_ops",
        parent_daily_ops_run_id=daily["id"],
        parent_daily_ops_attempt=claimed_daily["attempt_count"],
        parent_daily_ops_lease_token=claimed_daily["lease_token"],
    )
    app.db.claim_agent_run(tenant_id, run["id"], provider="fixture", model="fixture")
    app.db.prepare_agent_tasks(
        tenant_id,
        run["id"],
        [{
            "agent_name": "manager",
            "graph_node_key": "manager",
            "role": "manager",
            "tool_policy": {"allowed_tools": [], "max_tool_calls": 0},
            "skill_ids": [],
        }],
    )
    app.db.start_agent_task(tenant_id, run["id"], "manager")
    manager_report = {
        "priorities": [{
            "rank": 1,
            "title": "Review decision",
            "why_now": "Evidence needs an owner decision.",
            "expected_impact": "A documented operating decision.",
            "requires_approval": True,
            "evidence_refs": ["evidence-1"],
            "metric_claim": {"observation_refs": []},
        }]
    }
    app.db.complete_agent_task(
        tenant_id, run["id"], "manager", manager_report,
        artifact_kind="manager_synthesis",
    )
    app.db.complete_agent_run(
        tenant_id, run["id"], manager_report, review_status="approved"
    )
    app.db.update_claimed_daily_ops_run(
        tenant_id,
        daily["id"],
        attempt_count=claimed_daily["attempt_count"],
        lease_token=claimed_daily["lease_token"],
        values={
            "status": "completed",
            "agent_run_id": run["id"],
            "brief_json": json.dumps({"status": "complete"}),
            "lease_until": None,
            "lease_token": None,
            "completed_at": utc_now(),
        },
    )

    job, _ = app.db.create_job(
        tenant_id,
        owner_id,
        "job-1",
        "agent_run.execute",
        {"run_id": run["id"], "authorization": "never-in-events"},
    )
    claimed_job = app.db.claim_job()
    assert claimed_job and claimed_job["id"] == job["id"]

    expiry = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(
        timespec="seconds"
    )
    proposal = app.proposals.create(
        owner,
        daily_ops_run_id=daily["id"],
        priority_rank=1,
        operation="human.review",
        payload={"instructions": "Review this real proposal"},
        risk="low",
        rollback_plan="Record no approval if rejected.",
        idempotency_key="proposal-1",
        expires_at=expiry,
        request_id="proposal-create",
    )
    app.proposals.submit(
        owner, proposal["id"], expected_version=1, request_id="proposal-submit"
    )
    app.proposals.decide(
        admin,
        proposal["id"],
        expected_version=1,
        decision="approve",
        comment="Approved",
        request_id="proposal-approve",
    )
    app.proposals.execute(
        owner,
        proposal["id"],
        expected_version=1,
        idempotency_key="proposal-execution-1",
        request_id="proposal-execute",
    )

    page = app.db.read_mission_events(tenant_id, after=0, limit=200)
    resource_types = {event["resource_type"] for event in page["events"]}
    assert resource_types == {
        "agent_run", "agent_task", "report_sync", "job",
        "daily_ops_run", "proposal", "proposal_execution",
    }
    serialized = json.dumps(page, sort_keys=True)
    assert "never-in-events" not in serialized
    assert "secret objective" not in serialized
    assert "Review this real proposal" not in serialized
    assert any(
        event["resource_id"] == job["id"]
        and event["previous_status"] == "queued"
        and event["status"] == "running"
        for event in page["events"]
    )

    before = app.db.mission_event_cursor(tenant_id)["latest_cursor"]
    with app.db.transaction() as conn:
        conn.execute(
            "UPDATE jobs SET lease_until=?,updated_at=? WHERE tenant_id=? AND id=?",
            (utc_now(), utc_now(), tenant_id, job["id"]),
        )
    assert app.db.mission_event_cursor(tenant_id)["latest_cursor"] == before
    snapshot = app.db.mission_control(tenant_id)
    assert snapshot["event_cursor"]["latest_cursor"] == before
    assert snapshot["counts"]["report_syncs"]["polling"] == 1
    assert snapshot["counts"]["daily_ops_runs"]["completed"] == 1
    assert sum(snapshot["counts"]["proposals"].values()) == 1
    assert set(snapshot["counts"]["proposals"]) <= {"executing", "executed"}
    assert sum(snapshot["counts"]["proposal_executions"].values()) == 1
    assert set(snapshot["counts"]["proposal_executions"]) <= {"pending", "executed"}


def test_ledger_is_bounded_immutable_tenant_scoped_and_persistent(tmp_path: Path) -> None:
    path = tmp_path / "runtime.sqlite"
    db = Database(path)
    tenant_a, owner_a = db.create_tenant("A", "a@example.com")
    tenant_b, owner_b = db.create_tenant("B", "b@example.com")
    now = utc_now()
    with db.transaction() as conn:
        conn.executemany(
            """INSERT INTO jobs(
                   id,tenant_id,idempotency_key,kind,payload_json,status,
                   available_at,max_attempts,created_by,created_at,updated_at
               ) VALUES(?,?,?,?,?,'queued',?,?,?,?,?)""",
            [
                (
                    f"job-{index}", tenant_a, f"job-{index}",
                    "agent_run.execute", "{}", now, 3, owner_a, now, now,
                )
                for index in range(MISSION_EVENT_RETENTION + 1)
            ],
        )
    job_b, _ = db.create_job(
        tenant_b, owner_b, "job-b", "agent_run.execute", {"run_id": "b"}
    )
    with db.connect() as conn:
        assert conn.execute(
            "SELECT COUNT(*) FROM mission_events WHERE tenant_id=?", (tenant_a,)
        ).fetchone()[0] == MISSION_EVENT_RETENTION
        cursor = conn.execute(
            "SELECT MIN(cursor) FROM mission_events WHERE tenant_id=?", (tenant_a,)
        ).fetchone()[0]
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            conn.execute(
                "UPDATE mission_events SET status='failed' WHERE tenant_id=? AND cursor=?",
                (tenant_a, cursor),
            )
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            conn.execute(
                "DELETE FROM mission_events WHERE tenant_id=? AND cursor=?",
                (tenant_a, cursor),
            )

    gap = db.read_mission_events(tenant_a, after=0)
    assert gap["reset_required"] is True
    assert gap["reset_cursor"] == gap["latest_cursor"]
    assert db.read_mission_events(tenant_b, after=0)["events"][0]["resource_id"] == job_b["id"]
    assert all(
        event["resource_id"] != job_b["id"]
        for event in db.read_mission_events(
            tenant_a, after=gap["pruned_through_cursor"], limit=200
        )["events"]
    )
    reopened = Database(path)
    assert reopened.mission_event_cursor(tenant_a) == db.mission_event_cursor(tenant_a)
    app = RuntimeApplication(
        reopened,
        mission_event_poll_seconds=0.01,
        mission_event_max_lifetime_seconds=0.01,
    )
    key = app.auth.issue_key(tenant_a, owner_a)
    reset_stream = _StreamHandler(
        app, "/v1/mission-control/events?after=0", key
    )
    reset_stream.do_GET()
    reset_frames = _frames(reset_stream.wfile.getvalue())
    assert reset_frames[0]["event"] == "mission.reset"
    assert reset_frames[0]["data"]["reason"] == "retention_gap"
    assert reset_frames[0]["id"] == str(gap["latest_cursor"])


def test_interleaved_tenants_receive_private_contiguous_cursors(tmp_path: Path) -> None:
    db = Database(tmp_path / "runtime.sqlite")
    tenant_a, owner_a = db.create_tenant("A", "a@example.com")
    tenant_b, owner_b = db.create_tenant("B", "b@example.com")
    db.create_job(tenant_a, owner_a, "a-1", "agent_run.execute", {"run_id": "a"})
    db.create_job(tenant_b, owner_b, "b-1", "agent_run.execute", {"run_id": "b"})
    db.create_job(tenant_a, owner_a, "a-2", "agent_run.execute", {"run_id": "a"})
    db.create_job(tenant_b, owner_b, "b-2", "agent_run.execute", {"run_id": "b"})
    events_a = db.read_mission_events(tenant_a, after=0)["events"]
    events_b = db.read_mission_events(tenant_b, after=0)["events"]
    assert [event["cursor"] for event in events_a] == [1, 2]
    assert [event["cursor"] for event in events_b] == [1, 2]
    assert all("sequence" not in event and "tenant_id" not in event for event in events_a + events_b)
    assert {event["resource_id"] for event in events_a} == {
        db.list_jobs(tenant_a)[0]["id"], db.list_jobs(tenant_a)[1]["id"]
    }
    assert not {event["resource_id"] for event in events_a} & {
        event["resource_id"] for event in events_b
    }
    tenant_c, owner_c = db.create_tenant("C", "c@example.com")
    job_c, _ = db.create_job(
        tenant_c, owner_c, "c-1", "agent_run.execute", {"run_id": "c"}
    )
    with db.connect() as conn:
        for tenant_id, cursor, resource_id in (
            (tenant_c, 3, job_c["id"]),
            (tenant_a, 1, events_a[0]["resource_id"]),
        ):
            with pytest.raises(sqlite3.IntegrityError, match="not contiguous"):
                conn.execute(
                    """INSERT INTO mission_events(
                           tenant_id,cursor,event_type,resource_type,resource_id,
                           status,previous_status,metadata_json,created_at
                       ) VALUES(?,?,?,?,?,?,?,?,?)""",
                    (
                        tenant_id, cursor, "job.created", "job", resource_id,
                        "queued", None, "{}", utc_now(),
                    ),
                )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """INSERT INTO mission_events(
                       tenant_id,cursor,event_type,resource_type,resource_id,
                       status,previous_status,metadata_json,created_at
                   ) VALUES(?,?,?,?,?,?,?,?,?)""",
                (
                    tenant_c, 2, "job.created", "job", job_c["id"],
                    "queued", None, "[]", utc_now(),
                ),
            )
        with pytest.raises(sqlite3.IntegrityError, match="resource binding"):
            conn.execute(
                """INSERT INTO mission_events(
                       tenant_id,cursor,event_type,resource_type,resource_id,
                       status,previous_status,metadata_json,created_at
                   ) VALUES(?,?,?,?,?,?,?,?,?)""",
                (
                    tenant_c, 2, "job.created", "job", events_a[0]["resource_id"],
                    "queued", None, "{}", utc_now(),
                ),
            )


def test_sse_wire_contract_cursor_precedence_heartbeat_and_reconnect(tmp_path: Path) -> None:
    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"),
        mission_event_poll_seconds=0.002,
        mission_event_heartbeat_seconds=0.002,
        mission_event_max_lifetime_seconds=0.035,
        mission_event_batch_size=1,
        mission_event_max_backlog=10,
    )
    bootstrap = app.bootstrap("A", "owner@example.com")
    app.db.create_job(
        bootstrap["tenant_id"], bootstrap["user_id"], "job-1",
        "agent_run.execute", {"run_id": "run-1", "api_key": "must-not-leak"},
    )
    handler = _StreamHandler(
        app,
        "/v1/mission-control/events?after=999999",
        bootstrap["api_key"],
        last_event_id="0",
    )
    handler.do_GET()
    assert handler.status == 200
    assert handler.response_headers["Content-Type"].startswith("text/event-stream")
    assert handler.response_headers["Cache-Control"] == "no-store"
    raw = handler.wfile.getvalue()
    frames = _frames(raw)
    assert frames[0]["event"] == "mission.update"
    assert frames[0]["id"].isdigit()
    assert frames[0]["data"]["event_type"] == "job.created"
    assert frames[-1]["event"] == "mission.reconnect"
    assert frames[-1]["data"] == {
        "cursor": int(frames[-1]["id"]),
        "reason": "lifetime_limit",
        "retry_after_seconds": 1,
    }
    assert b": heartbeat\n\n" in raw
    assert b"must-not-leak" not in raw
    assert app.mission_connections.snapshot()["global_active"] == 0

    invalid = _StreamHandler(
        app,
        "/v1/mission-control/events?after=invalid",
        bootstrap["api_key"],
        last_event_id="0",
    )
    invalid.do_GET()
    assert invalid.status == 422
    token_query = _StreamHandler(
        app,
        "/v1/mission-control/events?token=secret",
        bootstrap["api_key"],
    )
    token_query.do_GET()
    assert token_query.status == 422
    unauthenticated = _StreamHandler(
        app, "/v1/mission-control/events", None
    )
    unauthenticated.do_GET()
    assert unauthenticated.status == 401


def test_sse_backlog_limit_rate_limit_and_disconnect_release(tmp_path: Path) -> None:
    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"),
        mission_event_max_backlog=1,
        mission_event_max_lifetime_seconds=0.02,
        mission_event_max_connections=1,
        mission_event_max_connections_per_tenant=1,
    )
    bootstrap = app.bootstrap("A", "owner@example.com")
    app.db.create_job(
        bootstrap["tenant_id"], bootstrap["user_id"], "job-1",
        "agent_run.execute", {"run_id": "run-1"},
    )
    handler = _StreamHandler(
        app, "/v1/mission-control/events", bootstrap["api_key"]
    )
    handler.do_GET()
    frames = _frames(handler.wfile.getvalue())
    assert [frame["event"] for frame in frames] == [
        "mission.update", "mission.reconnect"
    ]
    assert frames[-1]["data"]["reason"] == "backlog_limit"

    app.mission_connections.acquire(bootstrap["tenant_id"])
    limited = _StreamHandler(
        app, "/v1/mission-control/events", bootstrap["api_key"]
    )
    limited.do_GET()
    assert limited.status == 429
    assert limited.response_headers["Retry-After"] == "5"
    assert "global" not in limited.json_response["error"]["message"].lower()
    assert "tenant" not in limited.json_response["error"]["message"].lower()
    app.mission_connections.release(bootstrap["tenant_id"])

    class BrokenWriter(io.BytesIO):
        def write(self, value: bytes) -> int:
            raise BrokenPipeError("client disconnected")

    disconnected = _StreamHandler(
        app,
        "/v1/mission-control/events",
        bootstrap["api_key"],
        wfile=BrokenWriter(),
    )
    disconnected.do_GET()
    assert app.mission_connections.snapshot()["global_active"] == 0


def test_viewer_setup_errors_established_failures_and_access_logs_are_safe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"),
        mission_event_poll_seconds=0.01,
        mission_event_max_lifetime_seconds=0.03,
    )
    bootstrap = app.bootstrap("A", "owner@example.com")
    viewer_id = app.db.create_user(
        bootstrap["tenant_id"], "viewer@example.com", "viewer"
    )
    viewer_key = app.auth.issue_key(bootstrap["tenant_id"], viewer_id)
    viewer = _StreamHandler(
        app, "/v1/mission-control/events", viewer_key
    )
    viewer.do_GET()
    assert viewer.status == 200

    ahead = _StreamHandler(
        app, "/v1/mission-control/events?after=1", viewer_key
    )
    ahead.do_GET()
    assert ahead.status == 422 and ahead.response_headers == {}

    duplicate = _StreamHandler(
        app, "/v1/mission-control/events", viewer_key
    )
    duplicate.headers.add_header("Last-Event-ID", "0")
    duplicate.headers.add_header("Last-Event-ID", "0")
    duplicate.do_GET()
    assert duplicate.status == 422 and duplicate.response_headers == {}

    original_read = app.db.read_mission_events
    calls = 0

    def fail_after_setup(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls > 1:
            raise RuntimeError("unexpected established stream failure")
        return original_read(*args, **kwargs)

    monkeypatch.setattr(app.db, "read_mission_events", fail_after_setup)
    failed = _StreamHandler(
        app, "/v1/mission-control/events", viewer_key
    )
    with caplog.at_level(logging.ERROR, logger="ecommerce_ai_skills.api"):
        failed.do_GET()
    assert failed.status == 200
    assert app.mission_connections.snapshot()["global_active"] == 0
    assert "mission_stream_failed" in caplog.text

    caplog.clear()
    failed.command = "GET"
    failed.path = "/v1/mission-control/events?token=eai_super_secret"
    with caplog.at_level(logging.INFO, logger="ecommerce_ai_skills.api"):
        failed.log_message('"%s" %s %s', failed.path, "422", "-")
    assert "/v1/mission-control/events" in caplog.text
    assert "eai_super_secret" not in caplog.text
    assert "token=" not in caplog.text
