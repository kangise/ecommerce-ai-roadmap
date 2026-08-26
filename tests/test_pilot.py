from __future__ import annotations

import io
import argparse
import json
import os
import signal
import socket
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from email.message import Message
from pathlib import Path

import pytest

from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.errors import ConflictError
from ecommerce_ai_skills.runtime.pilot import PilotService, PilotSupervisor
from ecommerce_ai_skills.runtime.storage import Database, PILOT_WORKERS, utc_now


ENVIRONMENT = {
    "OPENAI_API_KEY": "test-openai-secret",
    "EAI_OPENAI_MODEL": "gpt-test",
    "AMAZON_CLIENT_ID": "client-id-secret",
    "AMAZON_CLIENT_SECRET": "client-secret",
    "AMAZON_REFRESH_TOKEN": "refresh-secret",
}


def _configure_ready_tenant(
    app: RuntimeApplication, bootstrap: dict[str, str]
) -> None:
    tenant_id, owner_id = bootstrap["tenant_id"], bootstrap["user_id"]
    account_id = app.db.add_connector_account(
        tenant_id,
        "amazon_spapi",
        "seller-1",
        {
            "region": "na",
            "marketplace_ids": ["ATVPDKIKX0DER"],
            "lwa_client_id_ref": "AMAZON_CLIENT_ID",
            "lwa_client_secret_ref": "AMAZON_CLIENT_SECRET",
            "lwa_refresh_token_ref": "AMAZON_REFRESH_TOKEN",
        },
    )
    app.db.set_connector_account_health(tenant_id, account_id, "healthy")
    with app.db.connect() as conn:
        graph = conn.execute(
            """SELECT id FROM agent_graph_versions
               WHERE tenant_id=? AND status='published'""",
            (tenant_id,),
        ).fetchone()
    assert graph is not None
    app.db.create_daily_ops_schedule(
        tenant_id,
        owner_id,
        name="Production Daily Ops",
        platform="amazon",
        objective="Run the production operating review.",
        timezone_name="UTC",
        local_time="08:00",
        graph_version_id=graph["id"],
        evidence_selectors=[],
        max_source_age_hours=48,
        enabled=True,
        next_local_date="2099-01-01",
    )


class _ApiHandler(_Handler):
    def __init__(self, app: RuntimeApplication, path: str, key: str | None):
        self._app = app
        self.path = path
        self.headers = Message()
        if key:
            self.headers["Authorization"] = f"Bearer {key}"
        self.client_address = ("127.0.0.1", 1234)
        self.out = None

    @property
    def app(self):
        return self._app

    def _json(self, status, value, request_id, **kwargs):
        self.out = (status, value)


def test_schema_20_boot_heartbeats_stale_takeover_and_fencing(tmp_path: Path) -> None:
    path = tmp_path / "runtime.sqlite"
    db = Database(path)
    assert db.readiness()["schema_version"] == 20
    with db.connect() as conn:
        tables = {
            row["name"] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert {"pilot_boots", "pilot_runtime_state", "pilot_worker_heartbeats"} <= tables
        worker_columns = {
            row["name"] for row in conn.execute(
                "PRAGMA table_info(pilot_worker_heartbeats)"
            )
        }
        assert not {"tenant_id", "payload_json", "error_message", "secret"} & worker_columns

    first = db.begin_pilot_boot(101, lease_seconds=5)
    assert db.mark_pilot_boot_running(first["boot_id"], lease_seconds=5)
    for worker in PILOT_WORKERS:
        assert db.record_pilot_worker_heartbeat(
            first["boot_id"], worker, succeeded=True, lease_seconds=5
        )
    service = PilotService(db, RuntimeApplication(db).auth, environ=ENVIRONMENT)
    assert service.runtime_health()["status"] == "healthy"
    with pytest.raises(ConflictError, match="already running"):
        db.begin_pilot_boot(202, lease_seconds=5)

    # The 30-second boot lease expires before the 45-second heartbeat stale
    # threshold; health must fail closed during that exact takeover window.
    past = (datetime.now(timezone.utc) - timedelta(seconds=31)).isoformat(
        timespec="seconds"
    )
    with db.transaction() as conn:
        conn.execute(
            "UPDATE pilot_boots SET heartbeat_at=?,lease_until=? WHERE boot_id=?",
            (past, past, first["boot_id"]),
        )
        conn.execute(
            "UPDATE pilot_worker_heartbeats SET last_heartbeat_at=? WHERE boot_id=?",
            (past, first["boot_id"]),
        )
    assert service.runtime_health()["status"] == "stale"
    assert PilotService.check_path(path, environ=ENVIRONMENT)["runtime"]["status"] == "stale"

    second = db.begin_pilot_boot(202, lease_seconds=5)
    assert second["generation"] == first["generation"] + 1
    assert db.get_pilot_boot(first["boot_id"])["status"] == "superseded"
    assert not db.record_pilot_worker_heartbeat(
        first["boot_id"], "scheduler", succeeded=True, lease_seconds=5
    )
    assert db.mark_pilot_boot_running(second["boot_id"], lease_seconds=5)
    assert db.record_pilot_worker_heartbeat(
        second["boot_id"], "scheduler", succeeded=True, lease_seconds=5
    )
    reopened = Database(path)
    assert reopened.get_pilot_runtime()["boot_id"] == second["boot_id"]
    assert reopened.finish_pilot_boot(second["boot_id"])
    assert Database(path).get_pilot_runtime()["status"] == "stopped"


def test_schema_19_migrates_without_runtime_seed_rows(tmp_path: Path) -> None:
    path = tmp_path / "legacy.sqlite"
    db = Database(path)
    with db.transaction() as conn:
        conn.execute("DROP TABLE pilot_runtime_state")
        conn.execute("DROP TABLE pilot_worker_heartbeats")
        conn.execute("DROP TABLE pilot_boots")
        conn.execute("UPDATE runtime_meta SET value='19' WHERE key='schema_version'")
    migrated = Database(path)
    assert migrated.readiness()["schema_version"] == 20
    with migrated.connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM pilot_boots").fetchone()[0] == 0
        assert conn.execute(
            "SELECT COUNT(*) FROM pilot_worker_heartbeats"
        ).fetchone()[0] == 0


def test_supervisor_stops_all_workers_when_boot_fence_is_lost(tmp_path: Path) -> None:
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    gate = threading.Event()
    supervisor = PilotSupervisor(
        app,
        poll_seconds=0.01,
        lease_seconds=5,
        worker_functions={worker: lambda: gate.wait(2) for worker in PILOT_WORKERS},
    )
    boot = supervisor.start()
    past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(
        timespec="seconds"
    )
    with app.db.transaction() as conn:
        conn.execute(
            "UPDATE pilot_boots SET lease_until=?,heartbeat_at=? WHERE boot_id=?",
            (past, past, boot["boot_id"]),
        )
    replacement = app.db.begin_pilot_boot(999, lease_seconds=5)
    gate.set()
    deadline = time.time() + 2
    while time.time() < deadline and not supervisor.stop_event.is_set():
        time.sleep(0.01)
    assert supervisor.stop_event.is_set()
    assert supervisor.stop(join_timeout=2) is False
    assert app.db.mark_pilot_boot_running(replacement["boot_id"], lease_seconds=5)
    assert app.db.finish_pilot_boot(replacement["boot_id"])


def test_tenant_readiness_is_real_isolated_fresh_and_secret_free(tmp_path: Path) -> None:
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    first = app.bootstrap("Ready", "ready@example.com")
    second = app.bootstrap("Blocked", "blocked@example.com")
    _configure_ready_tenant(app, first)
    app.pilot = PilotService(app.db, app.auth, environ=ENVIRONMENT)
    ready = app.pilot.tenant_readiness(first["tenant_id"])
    blocked = app.pilot.tenant_readiness(second["tenant_id"])
    assert ready["status"] == "ready" and ready["blockers"] == []
    assert ready["components"]["amazon_ads_l5"] == {
        "required": False,
        "status": "blocked",
        "reason_code": "OPTIONAL_AMAZON_ADS_GATE_NOT_PASSED",
    }
    assert blocked["status"] == "blocked"
    assert {item["code"] for item in blocked["blockers"]} >= {
        "AMAZON_ACCOUNT_MISSING", "DAILY_SCHEDULE_MISSING"
    }
    serialized = json.dumps({"ready": ready, "blocked": blocked}, sort_keys=True)
    assert all(value not in serialized for value in ENVIRONMENT.values())
    assert "AMAZON_CLIENT_SECRET" not in serialized
    missing_environment = dict(ENVIRONMENT)
    missing_environment.pop("AMAZON_REFRESH_TOKEN")
    missing_credentials = PilotService(
        app.db, app.auth, environ=missing_environment
    ).tenant_readiness(first["tenant_id"])
    assert "AMAZON_CREDENTIALS_MISSING" in {
        item["code"] for item in missing_credentials["blockers"]
    }

    viewer_id = app.db.create_user(first["tenant_id"], "viewer@example.com", "viewer")
    viewer_key = app.auth.issue_key(first["tenant_id"], viewer_id)
    handler = _ApiHandler(app, "/v1/pilot-status", viewer_key)
    handler.do_GET()
    assert handler.out[0] == 200
    assert handler.out[1]["tenant"]["tenant_id"] == first["tenant_id"]
    assert second["tenant_id"] not in json.dumps(handler.out[1])
    unauthenticated = _ApiHandler(app, "/v1/pilot-status", None)
    unauthenticated.do_GET()
    assert unauthenticated.out[0] == 401

    stale = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(
        timespec="seconds"
    )
    with app.db.transaction() as conn:
        conn.execute(
            """UPDATE connector_accounts SET health_checked_at=?
               WHERE tenant_id=? AND provider='amazon_spapi'""",
            (stale, first["tenant_id"]),
        )
    stale_status = app.pilot.tenant_readiness(first["tenant_id"])
    assert "AMAZON_HEALTH_STALE" in {
        item["code"] for item in stale_status["blockers"]
    }


def test_supervisor_isolates_worker_errors_and_marks_shutdown_timeout(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    bootstrap = app.bootstrap("A", "owner@example.com")
    _configure_ready_tenant(app, bootstrap)
    app.pilot = PilotService(app.db, app.auth, environ=ENVIRONMENT)
    counts = {worker: 0 for worker in PILOT_WORKERS}

    def function(worker: str):
        def run():
            counts[worker] += 1
            if worker == "report_worker":
                raise RuntimeError("super-secret-provider-body")
            return None
        return run

    supervisor = PilotSupervisor(
        app,
        poll_seconds=0.01,
        worker_functions={worker: function(worker) for worker in PILOT_WORKERS},
    )
    with caplog.at_level("ERROR", logger="ecommerce_ai_skills.pilot"):
        supervisor.start()
        deadline = time.time() + 2
        while time.time() < deadline:
            health = app.pilot.runtime_health()
            report = next(
                item for item in health["workers"] if item["name"] == "report_worker"
            )
            if report["status"] == "degraded" and counts["job_worker"] > 0:
                break
            time.sleep(0.01)
    assert health["status"] == "degraded"
    assert app.pilot.status(app.auth.authenticate(bootstrap["api_key"]))["status"] == "attention"
    assert report["last_error_type"] == "RuntimeError"
    assert report["consecutive_failures"] >= 1
    assert all(counts[worker] > 0 for worker in PILOT_WORKERS)
    persisted = json.dumps(app.db.get_pilot_runtime(), sort_keys=True)
    assert "super-secret-provider-body" not in persisted
    assert "super-secret-provider-body" not in caplog.text
    assert "pilot_worker_failed" in caplog.text
    assert supervisor.stop(join_timeout=2)
    assert app.pilot.runtime_health()["status"] == "stopped"

    release = threading.Event()
    functions = {worker: (lambda: None) for worker in PILOT_WORKERS}
    functions["report_worker"] = lambda: release.wait(2)
    timed = PilotSupervisor(
        app, poll_seconds=0.01, worker_functions=functions
    )
    timed.start()
    time.sleep(0.03)
    assert timed.stop(join_timeout=0.01) is False
    record = app.db.get_pilot_runtime()
    assert record["status"] == "stopping"
    timed_out = next(
        item for item in record["workers"] if item["worker_name"] == "report_worker"
    )
    assert timed_out["status"] == "degraded"
    assert timed_out["last_error_type"] == "ShutdownTimeout"
    release.set()


def test_check_is_read_only_and_reports_missing_or_mismatched_database(tmp_path: Path) -> None:
    missing = tmp_path / "missing.sqlite"
    result = PilotService.check_path(missing, environ={})
    assert result["status"] == "blocked"
    assert not missing.exists()

    path = tmp_path / "runtime.sqlite"
    app = RuntimeApplication(Database(path))
    app.bootstrap("A", "owner@example.com")
    before = path.stat().st_mtime_ns
    checked = PilotService.check_path(path, environ={})
    assert checked["status"] == "blocked"
    assert path.stat().st_mtime_ns == before
    with app.db.connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM pilot_boots").fetchone()[0] == 0
        conn.execute("UPDATE runtime_meta SET value='19' WHERE key='schema_version'")
    mismatch = PilotService.check_path(path, environ=ENVIRONMENT)
    assert mismatch["schema"]["status"] == "unsupported"
    with sqlite3.connect(path) as conn:
        assert conn.execute(
            "SELECT value FROM runtime_meta WHERE key='schema_version'"
        ).fetchone()[0] == "19"


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def test_pilot_cli_real_http_sigterm_and_persistent_stop(tmp_path: Path) -> None:
    path = tmp_path / "pilot.sqlite"
    port = _free_port()
    command = [
        sys.executable, "-m", "ecommerce_ai_skills.cli", "pilot",
        "--db", str(path), "--host", "127.0.0.1", "--port", str(port),
        "--name", "Pilot", "--email", "owner@example.com",
    ]
    process = subprocess.Popen(
        command,
        cwd=Path(__file__).resolve().parents[1],
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert process.stdout is not None
    launch = json.loads(process.stdout.readline())
    key = launch["bootstrap"]["api_key"]
    assert launch["status"] == "starting" and key.startswith("eai_")
    status = None
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            request = urllib.request.Request(
                f"http://127.0.0.1:{port}/v1/pilot-status",
                headers={"Authorization": f"Bearer {key}"},
            )
            with urllib.request.urlopen(request, timeout=2) as response:
                status = json.loads(response.read())
            if status["runtime"]["status"] == "healthy":
                break
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.05)
    assert status is not None and status["runtime"]["status"] == "healthy"
    process.send_signal(signal.SIGTERM)
    stdout, stderr = process.communicate(timeout=15)
    assert process.returncode == 0, stderr
    reopened = Database(path)
    persisted = reopened.get_pilot_runtime()
    assert persisted["status"] == "stopped"
    assert {item["status"] for item in persisted["workers"]} == {"stopped"}
    assert len(reopened.list_tenants()) == 1

    check = subprocess.run(
        [
            sys.executable, "-m", "ecommerce_ai_skills.cli", "pilot",
            "--db", str(path), "--check",
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    assert check.returncode == 1
    check_payload = json.loads(check.stdout)
    assert check_payload["schema"] == {"status": "ready", "version": 20}
    assert "eai_" not in check.stdout
    assert key not in check.stdout
    assert reopened.get_pilot_runtime()["status"] == "stopped"

    second_port = _free_port()
    existing = subprocess.Popen(
        [
            sys.executable, "-m", "ecommerce_ai_skills.cli", "pilot",
            "--db", str(path), "--port", str(second_port),
            "--name", "Must Not Duplicate", "--email", "new@example.com",
        ],
        cwd=Path(__file__).resolve().parents[1],
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert existing.stdout is not None
    existing_launch = json.loads(existing.stdout.readline())
    assert "bootstrap" not in existing_launch
    existing.send_signal(signal.SIGTERM)
    _, existing_stderr = existing.communicate(timeout=15)
    assert existing.returncode == 0, existing_stderr
    assert len(Database(path).list_tenants()) == 1

    absent = tmp_path / "absent.sqlite"
    missing = subprocess.run(
        [
            sys.executable, "-m", "ecommerce_ai_skills.cli", "pilot",
            "--db", str(absent),
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    assert missing.returncode == 2
    assert not absent.exists()


def test_pilot_cli_rejects_occupied_port_before_bootstrap(tmp_path: Path) -> None:
    path = tmp_path / "occupied.sqlite"
    with socket.socket() as occupied:
        occupied.bind(("127.0.0.1", 0))
        occupied.listen()
        result = subprocess.run(
            [
                sys.executable, "-m", "ecommerce_ai_skills.cli", "pilot",
                "--db", str(path), "--port", str(occupied.getsockname()[1]),
                "--name", "Pilot", "--email", "owner@example.com",
            ],
            cwd=Path(__file__).resolve().parents[1],
            text=True,
            capture_output=True,
            check=False,
        )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["blockers"] == [{"code": "PILOT_BIND_FAILED", "component": "http"}]
    db = Database(path)
    assert db.list_tenants() == []
    with db.connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM pilot_boots").fetchone()[0] == 0


def test_pilot_cli_reports_nonclean_shutdown_as_nonzero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from ecommerce_ai_skills import cli
    from ecommerce_ai_skills.runtime import pilot as pilot_module

    path = tmp_path / "runtime.sqlite"
    RuntimeApplication(Database(path)).bootstrap("A", "owner@example.com")

    class FakeServer:
        def server_close(self):
            pass

    class FakeSupervisor:
        def __init__(self, app, *, stop_event):
            self.boot_id = "safe-boot-id"

        def start(self):
            return {"boot_id": self.boot_id}

        def stop(self, **kwargs):
            return False

    monkeypatch.setattr(pilot_module, "PilotSupervisor", FakeSupervisor)
    monkeypatch.setattr(cli, "build_server", lambda *args, **kwargs: FakeServer())
    monkeypatch.setattr(cli, "serve", lambda *args, **kwargs: None)
    args = argparse.Namespace(
        db=str(path), check=False, host="127.0.0.1", port=8787,
        allow_public=False, name=None, email=None,
    )
    assert cli._run_pilot(args) == 3
    lines = capsys.readouterr().out.strip().splitlines()
    assert json.loads(lines[-1]) == {
        "status": "degraded",
        "error_type": "ShutdownTimeout",
        "boot_id": "safe-boot-id",
    }


def test_pilot_cli_closes_prebound_server_on_bootstrap_and_preflight_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from ecommerce_ai_skills import cli

    class FakeServer:
        def __init__(self):
            self.closed = False

        def server_close(self):
            self.closed = True

    args = argparse.Namespace(
        db=str(tmp_path / "bootstrap.sqlite"), check=False,
        host="127.0.0.1", port=8787, allow_public=False,
        name="Pilot", email="owner@example.com",
    )
    bootstrap_server = FakeServer()
    monkeypatch.setattr(cli, "build_server", lambda *a, **k: bootstrap_server)
    original_bootstrap = RuntimeApplication.bootstrap
    monkeypatch.setattr(
        RuntimeApplication,
        "bootstrap",
        lambda self, name, email: (_ for _ in ()).throw(RuntimeError("secret-bootstrap")),
    )
    assert cli._run_pilot(args) == 2
    bootstrap_payload = json.loads(capsys.readouterr().out)
    assert bootstrap_payload["blockers"][0]["code"] == "PILOT_BOOTSTRAP_FAILED"
    assert "secret-bootstrap" not in json.dumps(bootstrap_payload)
    assert "bootstrap" not in bootstrap_payload
    assert bootstrap_server.closed

    monkeypatch.setattr(RuntimeApplication, "bootstrap", original_bootstrap)
    args.db = str(tmp_path / "preflight.sqlite")
    preflight_server = FakeServer()
    monkeypatch.setattr(cli, "build_server", lambda *a, **k: preflight_server)
    monkeypatch.setattr(
        PilotService,
        "check_all",
        lambda self: (_ for _ in ()).throw(RuntimeError("secret-preflight")),
    )
    assert cli._run_pilot(args) == 2
    preflight_payload = json.loads(capsys.readouterr().out)
    assert preflight_payload["blockers"][0]["code"] == "PILOT_PREFLIGHT_FAILED"
    assert preflight_payload["bootstrap"]["api_key"].startswith("eai_")
    assert "secret-preflight" not in json.dumps(preflight_payload)
    assert preflight_server.closed
    with Database(args.db).connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM pilot_boots").fetchone()[0] == 0
