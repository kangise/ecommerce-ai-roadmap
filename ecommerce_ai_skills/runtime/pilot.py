"""Production Pilot readiness and single-process worker supervision."""

from __future__ import annotations

import logging
import json
import os
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .auth import AuthService
from .errors import ValidationError
from .storage import Database, PILOT_WORKERS, Principal, SCHEMA_VERSION


log = logging.getLogger("ecommerce_ai_skills.pilot")
PILOT_STALE_AFTER_SECONDS = 45
PILOT_LEASE_SECONDS = 30
AMAZON_HEALTH_MAX_AGE_SECONDS = 86_400


def _age_seconds(value: str, now: datetime) -> float:
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return float("inf")
    if instant.tzinfo is None:
        return float("inf")
    return max(0.0, (now - instant.astimezone(timezone.utc)).total_seconds())


class PilotService:
    def __init__(
        self,
        db: Database,
        auth: AuthService,
        *,
        environ: Mapping[str, str] | None = None,
        stale_after_seconds: int = PILOT_STALE_AFTER_SECONDS,
    ):
        self.db = db
        self.auth = auth
        self.environ = dict(os.environ if environ is None else environ)
        self.stale_after_seconds = max(5, min(int(stale_after_seconds), 3600))

    @staticmethod
    def _tenant_readiness_conn(
        conn: sqlite3.Connection,
        tenant_id: str,
        environ: Mapping[str, str],
    ) -> dict[str, Any]:
        tenant = conn.execute(
            "SELECT id,name,mode FROM tenants WHERE id=?", (tenant_id,)
        ).fetchone()
        if tenant is None:
            raise ValidationError("tenant does not exist")
        amazon = conn.execute(
            """SELECT health_status,health_checked_at,config_json
               FROM connector_accounts
               WHERE tenant_id=? AND provider='amazon_spapi'""",
            (tenant_id,),
        ).fetchall()
        amazon_counts: dict[str, int] = {}
        fresh_healthy = 0
        credential_ready = 0
        now = datetime.now(timezone.utc)
        for row in amazon:
            amazon_counts[row["health_status"]] = amazon_counts.get(row["health_status"], 0) + 1
            fresh = bool(
                row["health_status"] == "healthy"
                and row["health_checked_at"]
                and _age_seconds(row["health_checked_at"], now)
                <= AMAZON_HEALTH_MAX_AGE_SECONDS
            )
            if fresh:
                fresh_healthy += 1
                config = json.loads(row["config_json"])
                references = [
                    value for key, value in config.items()
                    if key.endswith("_ref") or key == "credential_ref"
                ]
                if references and all(
                    isinstance(reference, str)
                    and bool(environ.get(reference, "").strip())
                    for reference in references
                ):
                    credential_ready += 1
        amazon_total = len(amazon)
        graph_count = conn.execute(
            """SELECT COUNT(*) FROM agent_graph_versions
               WHERE tenant_id=? AND status='published'""",
            (tenant_id,),
        ).fetchone()[0]
        daily_count = conn.execute(
            """SELECT COUNT(*) FROM daily_ops_schedules
               WHERE tenant_id=? AND enabled=1""",
            (tenant_id,),
        ).fetchone()[0]
        latest_ads = conn.execute(
            """SELECT status,completed_at FROM ads_capability_gates
               WHERE tenant_id=? ORDER BY rowid DESC LIMIT 1""",
            (tenant_id,),
        ).fetchone()

        blockers: list[dict[str, str]] = []
        if amazon_total == 0:
            blockers.append({"code": "AMAZON_ACCOUNT_MISSING", "component": "amazon_spapi"})
            amazon_status = "missing"
        elif amazon_counts.get("healthy", 0) == 0:
            blockers.append({"code": "AMAZON_ACCOUNT_UNHEALTHY", "component": "amazon_spapi"})
            amazon_status = "unhealthy"
        elif fresh_healthy == 0:
            blockers.append({"code": "AMAZON_HEALTH_STALE", "component": "amazon_spapi"})
            amazon_status = "stale"
        elif credential_ready == 0:
            blockers.append({"code": "AMAZON_CREDENTIALS_MISSING", "component": "amazon_spapi"})
            amazon_status = "missing_credentials"
        else:
            amazon_status = "ready"
        if graph_count == 0:
            blockers.append({"code": "PUBLISHED_GRAPH_MISSING", "component": "agent_graph"})
        if daily_count == 0:
            blockers.append({"code": "DAILY_SCHEDULE_MISSING", "component": "daily_ops"})

        openai_key_present = bool(environ.get("OPENAI_API_KEY", "").strip())
        openai_model_present = bool(environ.get("EAI_OPENAI_MODEL", "").strip())
        if not openai_key_present:
            blockers.append({"code": "OPENAI_API_KEY_MISSING", "component": "openai"})
        if not openai_model_present:
            blockers.append({"code": "OPENAI_MODEL_MISSING", "component": "openai"})

        ads_passed = bool(
            latest_ads
            and latest_ads["status"] == "passed"
            and latest_ads["completed_at"]
            and _age_seconds(latest_ads["completed_at"], now)
            <= AMAZON_HEALTH_MAX_AGE_SECONDS
        )
        return {
            "tenant_id": tenant["id"],
            "tenant_name": tenant["name"],
            "tenant_mode": tenant["mode"],
            "status": "ready" if not blockers else "blocked",
            "blockers": blockers,
            "components": {
                "schema": {"required": True, "status": "ready", "version": SCHEMA_VERSION},
                "amazon_spapi": {
                    "required": True,
                    "status": amazon_status,
                    "account_count": amazon_total,
                    "healthy_count": amazon_counts.get("healthy", 0),
                    "fresh_healthy_count": fresh_healthy,
                    "credential_ready_count": credential_ready,
                    "health_max_age_seconds": AMAZON_HEALTH_MAX_AGE_SECONDS,
                },
                "agent_graph": {
                    "required": True,
                    "status": "ready" if graph_count else "missing",
                    "published_count": int(graph_count),
                },
                "daily_ops": {
                    "required": True,
                    "status": "ready" if daily_count else "missing",
                    "enabled_schedule_count": int(daily_count),
                },
                "openai": {
                    "required": True,
                    "status": (
                        "ready" if openai_key_present and openai_model_present else "missing"
                    ),
                    "api_key_present": openai_key_present,
                    "model_present": openai_model_present,
                },
                "amazon_ads_l5": {
                    "required": False,
                    "status": "passed" if ads_passed else "blocked",
                    "reason_code": (
                        None if ads_passed else "OPTIONAL_AMAZON_ADS_GATE_NOT_PASSED"
                    ),
                },
            },
        }

    def tenant_readiness(self, tenant_id: str) -> dict[str, Any]:
        with self.db.connect() as conn:
            conn.execute("BEGIN")
            return self._tenant_readiness_conn(conn, tenant_id, self.environ)

    def runtime_health(self) -> dict[str, Any]:
        record = self.db.get_pilot_runtime()
        if record is None:
            return {
                "status": "stopped",
                "boot_id": None,
                "generation": None,
                "started_at": None,
                "last_heartbeat_at": None,
                "workers": [],
            }
        now = datetime.now(timezone.utc)
        workers = []
        for worker in record["workers"]:
            effective = worker["status"]
            if (
                record["status"] in {"starting", "running"}
                and effective != "stopped"
                and _age_seconds(worker["last_heartbeat_at"], now)
                > self.stale_after_seconds
            ):
                effective = "stale"
            workers.append(
                {
                    "name": worker["worker_name"],
                    "status": effective,
                    "iteration_count": worker["iteration_count"],
                    "consecutive_failures": worker["consecutive_failures"],
                    "last_heartbeat_at": worker["last_heartbeat_at"],
                    "last_success_at": worker["last_success_at"],
                    "last_error_at": worker["last_error_at"],
                    "last_error_type": worker["last_error_type"],
                }
            )
        stored = record["status"]
        if stored in {"stopped", "superseded", "stopping"}:
            status = stored
        elif (
            not record["lease_until"]
            or datetime.fromisoformat(record["lease_until"]) <= now
            or _age_seconds(record["heartbeat_at"], now) > self.stale_after_seconds
        ):
            status = "stale"
        elif any(item["status"] == "stale" for item in workers):
            status = "stale"
        elif any(item["status"] == "degraded" for item in workers):
            status = "degraded"
        elif workers and all(item["status"] == "healthy" for item in workers):
            status = "healthy"
        else:
            status = "starting"
        return {
            "status": status,
            "boot_id": record["boot_id"],
            "generation": record["generation"],
            "started_at": record["started_at"],
            "last_heartbeat_at": record["heartbeat_at"],
            "stopped_at": record["stopped_at"],
            "stop_reason": record["stop_reason"],
            "workers": workers,
        }

    def status(self, principal: Principal) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        readiness = self.tenant_readiness(principal.tenant_id)
        runtime = self.runtime_health()
        blockers = list(readiness["blockers"])
        warnings: list[dict[str, str]] = []
        if runtime["status"] in {"stale", "stopped", "superseded", "stopping"}:
            blockers.append(
                {"code": "PILOT_RUNTIME_NOT_HEALTHY", "component": "pilot_runtime"}
            )
        elif runtime["status"] in {"degraded", "starting"}:
            warnings.append(
                {"code": "PILOT_RUNTIME_ATTENTION", "component": "pilot_runtime"}
            )
        status = "blocked" if blockers else ("attention" if warnings else "ready")
        return {
            "status": status,
            "blockers": blockers,
            "warnings": warnings,
            "runtime": runtime,
            "tenant": readiness,
        }

    def check_all(self) -> dict[str, Any]:
        readiness = [self.tenant_readiness(item["id"]) for item in self.db.list_tenants()]
        return {
            "status": "ready" if readiness and all(
                item["status"] == "ready" for item in readiness
            ) else "blocked",
            "schema": self.db.readiness(),
            "runtime": self.runtime_health(),
            "tenants": readiness,
        }

    @classmethod
    def check_path(
        cls, path: str | Path, *, environ: Mapping[str, str] | None = None
    ) -> dict[str, Any]:
        """Read-only preflight that never creates or migrates the database."""
        db_path = Path(path).expanduser().resolve()
        env = dict(os.environ if environ is None else environ)
        if not db_path.is_file():
            return {
                "status": "blocked",
                "schema": {"status": "missing", "expected_version": SCHEMA_VERSION},
                "runtime": {"status": "stopped", "workers": []},
                "tenants": [],
                "blockers": [{"code": "DATABASE_MISSING", "component": "schema"}],
            }
        uri = db_path.as_uri() + "?mode=ro"
        try:
            conn = sqlite3.connect(uri, uri=True, timeout=5)
            conn.row_factory = sqlite3.Row
            conn.execute("BEGIN")
            version_row = conn.execute(
                "SELECT value FROM runtime_meta WHERE key='schema_version'"
            ).fetchone()
            quick_check = conn.execute("PRAGMA quick_check").fetchone()[0]
            if quick_check != "ok":
                return {
                    "status": "blocked",
                    "schema": {"status": "corrupt", "expected_version": SCHEMA_VERSION},
                    "runtime": {"status": "unknown", "workers": []},
                    "tenants": [],
                    "blockers": [{"code": "DATABASE_INTEGRITY_FAILED", "component": "schema"}],
                }
            version = int(version_row["value"]) if version_row else None
            if version != SCHEMA_VERSION:
                return {
                    "status": "blocked",
                    "schema": {
                        "status": "unsupported",
                        "version": version,
                        "expected_version": SCHEMA_VERSION,
                    },
                    "runtime": {"status": "unknown", "workers": []},
                    "tenants": [],
                    "blockers": [{"code": "SCHEMA_VERSION_MISMATCH", "component": "schema"}],
                }
            tenants = [
                cls._tenant_readiness_conn(conn, row["id"], env)
                for row in conn.execute("SELECT id FROM tenants ORDER BY created_at,id")
            ]
            state = conn.execute(
                """SELECT b.status,b.boot_id,b.generation,b.heartbeat_at,b.lease_until
                   FROM pilot_runtime_state s LEFT JOIN pilot_boots b
                     ON b.boot_id=s.active_boot_id WHERE s.singleton=1"""
            ).fetchone()
            if state and state["boot_id"]:
                now = datetime.now(timezone.utc)
                workers = [dict(row) for row in conn.execute(
                    """SELECT worker_name,status,last_heartbeat_at,
                              consecutive_failures,last_error_type
                       FROM pilot_worker_heartbeats WHERE boot_id=?
                       ORDER BY worker_name""",
                    (state["boot_id"],),
                )]
                effective_workers = []
                for worker in workers:
                    status = worker["status"]
                    if (
                        status != "stopped"
                        and _age_seconds(worker["last_heartbeat_at"], now)
                        > PILOT_STALE_AFTER_SECONDS
                    ):
                        status = "stale"
                    effective_workers.append({
                        "name": worker["worker_name"],
                        "status": status,
                        "consecutive_failures": worker["consecutive_failures"],
                        "last_error_type": worker["last_error_type"],
                        "last_heartbeat_at": worker["last_heartbeat_at"],
                    })
                lease_stale = (
                    not state["lease_until"]
                    or datetime.fromisoformat(state["lease_until"])
                    <= now
                )
                if state["status"] == "stopping":
                    runtime_status = "stopping"
                elif lease_stale or _age_seconds(
                    state["heartbeat_at"], now
                ) > PILOT_STALE_AFTER_SECONDS or any(
                    item["status"] == "stale" for item in effective_workers
                ):
                    runtime_status = "stale"
                elif any(
                    item["status"] == "degraded" for item in effective_workers
                ):
                    runtime_status = "degraded"
                elif effective_workers and all(
                    item["status"] == "healthy" for item in effective_workers
                ):
                    runtime_status = "healthy"
                else:
                    runtime_status = "starting"
                runtime = {
                    "status": runtime_status,
                    "boot_id": state["boot_id"],
                    "generation": state["generation"],
                    "last_heartbeat_at": state["heartbeat_at"],
                    "workers": effective_workers,
                }
            else:
                runtime = {"status": "stopped", "workers": []}
            return {
                "status": "ready" if tenants and all(
                    item["status"] == "ready" for item in tenants
                ) else "blocked",
                "schema": {"status": "ready", "version": version},
                "runtime": runtime,
                "tenants": tenants,
                "blockers": (
                    [] if tenants else [{"code": "TENANT_MISSING", "component": "tenant"}]
                ),
            }
        except (sqlite3.Error, TypeError, ValueError) as exc:
            return {
                "status": "blocked",
                "schema": {"status": "unreadable", "expected_version": SCHEMA_VERSION},
                "runtime": {"status": "unknown", "workers": []},
                "tenants": [],
                "blockers": [
                    {"code": "DATABASE_UNREADABLE", "component": "schema",
                     "error_type": type(exc).__name__}
                ],
            }
        finally:
            if "conn" in locals():
                conn.close()


class PilotSupervisor:
    def __init__(
        self,
        app: Any,
        *,
        poll_seconds: float = 1.0,
        lease_seconds: int = PILOT_LEASE_SECONDS,
        stop_event: threading.Event | None = None,
        worker_functions: Mapping[str, Callable[[], Any]] | None = None,
    ):
        if not 0.01 <= float(poll_seconds) <= 300:
            raise ValidationError("pilot poll_seconds must be between 0.01 and 300")
        if not 5 <= int(lease_seconds) <= 300:
            raise ValidationError("pilot lease_seconds must be between 5 and 300")
        self.app = app
        self.db: Database = app.db
        self.poll_seconds = float(poll_seconds)
        self.lease_seconds = int(lease_seconds)
        self.stop_event = stop_event or threading.Event()
        self.worker_functions = dict(worker_functions or {
            "scheduler": app.schedules.tick_once,
            "job_worker": app.jobs.run_once,
            "report_worker": app.report_syncs.run_once,
            "daily_scheduler": app.daily_ops.scheduler_run_once,
            "daily_worker": app.daily_ops.worker_run_once,
            "proposal_worker": app.proposals.worker_run_once,
        })
        if set(self.worker_functions) != set(PILOT_WORKERS):
            raise ValidationError("pilot supervisor requires exactly the installed workers")
        self.boot_id: str | None = None
        self._threads: list[threading.Thread] = []

    def start(self) -> dict[str, Any]:
        if self.boot_id is not None:
            raise ValidationError("pilot supervisor is already started")
        boot = self.db.begin_pilot_boot(os.getpid(), lease_seconds=self.lease_seconds)
        self.boot_id = boot["boot_id"]
        if not self.db.mark_pilot_boot_running(
            self.boot_id, lease_seconds=self.lease_seconds
        ):
            self.db.finish_pilot_boot(self.boot_id, reason="startup_failure")
            raise ValidationError("pilot boot lost its fence during startup")
        try:
            for worker_name in PILOT_WORKERS:
                thread = threading.Thread(
                    target=self._run_worker,
                    name=f"pilot-{worker_name}",
                    args=(worker_name, self.worker_functions[worker_name]),
                    daemon=True,
                )
                thread.start()
                self._threads.append(thread)
        except Exception:
            self.stop_event.set()
            for thread in self._threads:
                thread.join(5.0)
            self.db.finish_pilot_boot(self.boot_id, reason="startup_failure")
            raise
        return self.db.get_pilot_boot(self.boot_id)

    def _run_worker(self, name: str, function: Callable[[], Any]) -> None:
        assert self.boot_id is not None
        while not self.stop_event.is_set():
            try:
                function()
                retained = self.db.record_pilot_worker_heartbeat(
                    self.boot_id,
                    name,
                    succeeded=True,
                    lease_seconds=self.lease_seconds,
                )
            except Exception as exc:
                log.error(
                    "pilot_worker_failed worker=%s error_type=%s",
                    name,
                    type(exc).__name__,
                )
                try:
                    retained = self.db.record_pilot_worker_heartbeat(
                        self.boot_id,
                        name,
                        succeeded=False,
                        error_type=type(exc).__name__,
                        lease_seconds=self.lease_seconds,
                    )
                except Exception as heartbeat_error:
                    log.error(
                        "pilot_worker_heartbeat_failed worker=%s error_type=%s",
                        name,
                        type(heartbeat_error).__name__,
                    )
                    self.stop_event.set()
                    return
            if not retained:
                log.warning("pilot_worker_fence_lost worker=%s", name)
                self.stop_event.set()
                return
            self.stop_event.wait(self.poll_seconds)

    def stop(
        self, *, reason: str = "graceful_shutdown", join_timeout: float = 130.0
    ) -> bool:
        self.stop_event.set()
        deadline = time.monotonic() + max(0.0, join_timeout)
        for thread in self._threads:
            thread.join(max(0.0, deadline - time.monotonic()))
        if self.boot_id is None:
            return False
        alive = [
            thread.name.removeprefix("pilot-")
            for thread in self._threads if thread.is_alive()
        ]
        if alive:
            self.db.mark_pilot_boot_stopping(
                self.boot_id, timed_out_workers=alive
            )
            return False
        return self.db.finish_pilot_boot(self.boot_id, reason=reason)
