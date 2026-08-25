"""Durable worker and interval scheduler for agent workflows."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .agents import WeeklyOpsCouncil
from .auth import AuthService
from .evidence import REPORT_SPECS
from .errors import ValidationError
from .storage import Database, Principal


@dataclass
class JobService:
    db: Database
    auth: AuthService
    agent_runs: WeeklyOpsCouncil

    def enqueue_agent_run(
        self,
        principal: Principal,
        run_id: str,
        idempotency_key: str,
        request_id: str,
        *,
        max_attempts: int = 3,
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        self.db.get_agent_run(principal.tenant_id, run_id)
        job, replayed = self.db.create_job(
            principal.tenant_id,
            principal.user_id,
            idempotency_key,
            "agent_run.execute",
            {"run_id": run_id},
            max_attempts=max_attempts,
        )
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "job.enqueue",
            "job",
            job["id"],
            "replayed" if replayed else "accepted",
            {"kind": job["kind"], "run_id": run_id},
        )
        return job

    def list(self, principal: Principal, limit: int = 100) -> list[dict[str, Any]]:
        self.auth.require(principal, "viewer")
        return self.db.list_jobs(principal.tenant_id, limit)

    def get(self, principal: Principal, job_id: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        return self.db.get_job(principal.tenant_id, job_id)

    def run_once(self) -> dict[str, Any] | None:
        job = self.db.claim_job()
        if job is None:
            return None
        principal = self.db.principal_for_user(job["tenant_id"], job["created_by"])
        request_id = f"job:{job['id']}:attempt:{job['attempt_count']}"
        try:
            if job["kind"] != "agent_run.execute":
                raise RuntimeError(f"unsupported persisted job kind: {job['kind']}")
            bundle = self.agent_runs.execute(
                principal, str(job["payload"]["run_id"]), request_id
            )
            result = {
                "run_id": bundle["run"]["id"],
                "run_status": bundle["run"]["status"],
            }
            completed = self.db.complete_job(job["tenant_id"], job["id"], result)
            self.db.append_audit(
                job["tenant_id"],
                principal.user_id,
                request_id,
                "job.execute",
                "job",
                job["id"],
                "succeeded",
                result,
            )
            return completed
        except Exception as exc:
            failed = self.db.fail_job(job["tenant_id"], job["id"], str(exc))
            self.db.append_audit(
                job["tenant_id"],
                principal.user_id,
                request_id,
                "job.execute",
                "job",
                job["id"],
                "failed",
                {"error_type": type(exc).__name__, "next_status": failed["status"]},
            )
            return failed


@dataclass
class ScheduleService:
    db: Database
    auth: AuthService
    agent_runs: WeeklyOpsCouncil
    jobs: JobService

    def create(
        self,
        principal: Principal,
        *,
        name: str,
        objective: str,
        evidence_import_ids: list[str],
        evidence_selectors: list[dict[str, str]],
        interval_minutes: int,
        next_run_at: str,
        request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        platform_ids = self.agent_runs.platform_registry.entries()
        for selector in evidence_selectors:
            if selector.get("platform") not in platform_ids:
                raise ValidationError("schedule evidence selector uses an unknown platform")
            if selector.get("report_type") not in REPORT_SPECS:
                raise ValidationError("schedule evidence selector uses an unknown report type")
        schedule = self.db.create_schedule(
            principal.tenant_id,
            principal.user_id,
            name=name,
            objective=objective,
            evidence_import_ids=evidence_import_ids,
            evidence_selectors=evidence_selectors,
            interval_minutes=interval_minutes,
            next_run_at=next_run_at,
        )
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "schedule.create",
            "schedule",
            schedule["id"],
            "accepted",
            {"interval_minutes": interval_minutes},
        )
        return schedule

    def list(self, principal: Principal) -> list[dict[str, Any]]:
        self.auth.require(principal, "viewer")
        return self.db.list_schedules(principal.tenant_id)

    def set_enabled(
        self, principal: Principal, schedule_id: str, enabled: bool, request_id: str
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        schedule = self.db.set_schedule_enabled(
            principal.tenant_id, schedule_id, enabled
        )
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "schedule.enable" if enabled else "schedule.disable",
            "schedule",
            schedule_id,
            "succeeded",
            {},
        )
        return schedule

    def tick_once(self) -> dict[str, Any] | None:
        schedule = self.db.claim_due_schedule()
        if schedule is None:
            return None
        principal = self.db.principal_for_user(
            schedule["tenant_id"], schedule["created_by"]
        )
        occurrence = re.sub(r"[^0-9A-Za-z]+", "-", schedule["next_run_at"]).strip("-")
        request_id = f"schedule:{schedule['id']}:{occurrence}"
        try:
            run = self.agent_runs.request(
                principal,
                "weekly_ops",
                schedule["objective"],
                None,
                request_id,
                request_id,
                evidence_import_ids=self.db.resolve_schedule_evidence(schedule),
            )
            job = self.jobs.enqueue_agent_run(
                principal,
                run["id"],
                request_id,
                request_id,
            )
            self.db.advance_schedule(schedule["tenant_id"], schedule["id"])
            self.db.append_audit(
                schedule["tenant_id"],
                principal.user_id,
                request_id,
                "schedule.tick",
                "schedule",
                schedule["id"],
                "succeeded",
                {"run_id": run["id"], "job_id": job["id"]},
            )
            return {"schedule_id": schedule["id"], "run": run, "job": job}
        except Exception as exc:
            self.db.release_schedule(schedule["tenant_id"], schedule["id"])
            self.db.append_audit(
                schedule["tenant_id"],
                principal.user_id,
                request_id,
                "schedule.tick",
                "schedule",
                schedule["id"],
                "failed",
                {"error_type": type(exc).__name__},
            )
            raise
