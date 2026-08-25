from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from email.message import Message
from pathlib import Path

import pytest

from ecommerce_ai_skills.demo_seed import open_demo_runtime, seed_demo_database
from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.errors import ValidationError
from ecommerce_ai_skills.runtime.storage import Database


def test_demo_seed_creates_isolated_visible_full_product_state(tmp_path: Path) -> None:
    path = tmp_path / "demo.sqlite"
    result = seed_demo_database(path)
    assert result["warning"].startswith("DEMO DATA ONLY")
    assert result["tenant_mode"] == "demo"
    assert result["evidence_imports"] == 10
    assert result["metric_materializations"] == 9
    assert result["approval_actions"] == 2
    assert result["marketplace_accounts"] == 3
    assert result["ads_capability_gate_status"] == "blocked"
    assert result["job_status"] == "succeeded"
    assert result["daily_ops_run_status"] == "completed"
    assert result["proposal_count"] == 2
    assert result["human_review_proposal_status"] == "executed"
    assert result["amazon_ads_proposal_status"] == "blocked"

    app = RuntimeApplication(Database(path))
    reviewer = app.auth.authenticate(result["reviewer_api_key"])
    owner = app.auth.authenticate(result["owner_api_key"])
    assert reviewer.role == "admin"
    assert owner.role == "owner"
    assert app.db.get_tenant(reviewer.tenant_id)["mode"] == "demo"
    assert {account["provider"] for account in app.accounts.list(reviewer)} == {
        "amazon_spapi",
        "shopify",
        "amazon_ads",
    }

    class MeHandler(_Handler):
        def __init__(self):
            self.path = "/v1/me"
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {result['reviewer_api_key']}"
            self.out = None

        @property
        def app(self):
            return app

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value)

    me = MeHandler()
    me.do_GET()
    assert me.out[0] == 200
    assert me.out[1]["tenant_mode"] == "demo"
    assert me.out[1]["tenant_name"] == "Commerce Agent OS Demo"

    briefing = app.briefing.get(reviewer, "amazon")
    assert len(briefing["metrics"]) >= 4
    assert len(briefing["metrics"][0]["series"]) == 7
    assert len(briefing["priorities"]) == 3
    assert len(briefing["approvals"]) == 2
    assert len(briefing["agents"]) >= 5
    assert app.jobs.list(reviewer)[0]["status"] == "succeeded"
    assert len(app.schedules.list(reviewer)) == 1
    assert len(app.daily_ops.list_schedules(reviewer)) == 1
    assert app.daily_ops.get_brief(
        reviewer, result["daily_ops_run_id"]
    )["brief"]["status"] == "completed"
    evaluations = app.evaluator.list(reviewer, result["agent_run_id"])
    assert evaluations[0]["passed"] is True
    proposals = app.proposals.list(reviewer)
    assert {item["status"] for item in proposals} == {"executed", "blocked"}
    human = app.proposals.get(reviewer, result["human_review_proposal_id"])
    ads_proposal = app.proposals.get(reviewer, result["amazon_ads_proposal_id"])
    assert human["daily_ops_run_id"] == result["daily_ops_run_id"]
    assert human["approval_count"] == 1
    assert human["executions"][0]["status"] == "executed"
    assert ads_proposal["approval_count"] == 1
    assert ads_proposal["executions"][0]["status"] == "blocked"
    assert ads_proposal["executions"][0]["capability_block"]["connector_calls"] == 0
    reopened = open_demo_runtime(path)
    reopened_reviewer = reopened.auth.authenticate(reopened.demo_session["api_key"])
    assert len(reopened.proposals.list(reopened_reviewer)) == 2
    assert any(event["action"] == "demo.seed" for event in app.db.list_audit(reviewer.tenant_id))


def test_demo_provider_executes_a_metric_only_graph_run(tmp_path: Path) -> None:
    path = tmp_path / "demo.sqlite"
    seeded = seed_demo_database(path)
    app = open_demo_runtime(path)
    owner = app.auth.authenticate(seeded["owner_api_key"])
    observation = app.metric_observations.list_observations(owner)["observations"][0]
    run = app.agent_runs.request(
        owner,
        "weekly_ops",
        "Review one selected Demo metric without assuming other report types.",
        None,
        "demo-metric-only",
        "demo-metric-only-request",
        metric_observation_ids=[observation["id"]],
    )
    completed = app.agent_runs.execute(owner, run["id"], "demo-metric-only-execute")
    assert completed["run"]["status"] == "completed"
    assert completed["run"]["review_status"] == "approved"
    assert any(
        artifact["kind"] == "reviewer_verdict"
        for artifact in completed["artifacts"]
    )


def test_demo_seed_refuses_every_existing_database_path(tmp_path: Path) -> None:
    path = tmp_path / "existing.sqlite"
    path.write_bytes(b"do-not-overwrite")
    with pytest.raises(ValidationError, match="new database path"):
        seed_demo_database(path)
    assert path.read_bytes() == b"do-not-overwrite"


def test_production_tenant_is_default_and_mode_is_validated(tmp_path: Path) -> None:
    db = Database(tmp_path / "runtime.sqlite")
    tenant_id, _ = db.create_tenant("Production", "owner@example.com")
    assert db.get_tenant(tenant_id)["mode"] == "production"
    with pytest.raises(ValidationError, match="tenant mode"):
        db.create_tenant("Invalid", "owner@example.com", mode="fixture")


def test_schema_v9_migrates_existing_tenants_to_production_mode(tmp_path: Path) -> None:
    path = tmp_path / "v9.sqlite"
    with sqlite3.connect(path) as connection:
        connection.executescript(
            """
            CREATE TABLE tenants(id TEXT PRIMARY KEY,name TEXT NOT NULL,created_at TEXT NOT NULL);
            INSERT INTO tenants(id,name,created_at) VALUES('tenant-1','Existing','2026-08-22T00:00:00+00:00');
            CREATE TABLE runtime_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            INSERT INTO runtime_meta(key,value) VALUES('schema_version','9');
            """
        )
    db = Database(path)
    assert db.readiness()["schema_version"] == 18
    assert db.get_tenant("tenant-1")["mode"] == "production"


def test_demo_seed_cli_prints_one_time_connection_payload(tmp_path: Path) -> None:
    path = tmp_path / "cli-demo.sqlite"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ecommerce_ai_skills.cli",
            "demo-seed",
            "--db",
            str(path),
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["database"] == str(path.resolve())
    assert payload["tenant_mode"] == "demo"
    assert payload["reviewer_api_key"].startswith("eai_")


def test_demo_runtime_exposes_session_only_for_explicit_demo_app(tmp_path: Path) -> None:
    production = RuntimeApplication(Database(tmp_path / "production.sqlite"))
    production.bootstrap("Production", "owner@example.com")
    demo = open_demo_runtime(tmp_path / "auto-demo.sqlite")

    class SessionHandler(_Handler):
        def __init__(self, app):
            self._app = app
            self.path = "/v1/demo-session"
            self.headers = Message()
            self.out = None

        @property
        def app(self):
            return self._app

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value, kwargs)

    production_session = SessionHandler(production)
    production_session.do_GET()
    assert production_session.out[0] == 404

    demo_session = SessionHandler(demo)
    demo_session.do_GET()
    assert demo_session.out[0] == 200
    assert demo_session.out[1]["tenant_mode"] == "demo"
    assert demo_session.out[1]["api_key"].startswith("eai_")
    assert demo_session.out[2]["extra_headers"]["Cache-Control"] == "no-store"


def test_demo_runtime_rejects_production_or_multi_tenant_database(tmp_path: Path) -> None:
    path = tmp_path / "wrong.sqlite"
    db = Database(path)
    db.create_tenant("Production", "owner@example.com")
    with pytest.raises(ValidationError, match="exactly one Demo tenant"):
        open_demo_runtime(path)


def test_demo_cli_is_discoverable() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ecommerce_ai_skills.cli", "demo", "--help"],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "automatic loopback-only UI access" in result.stdout
