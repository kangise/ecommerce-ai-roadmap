"""Deterministic, source-backed workflow evaluation for completed agent runs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agents import WeeklyOpsCouncil
from .auth import AuthService
from .errors import ConflictError, RuntimeErrorBase
from .storage import Database, Principal


@dataclass
class WorkflowEvaluator:
    db: Database
    auth: AuthService

    VERSION = "weekly-ops-v3"

    def evaluate(
        self, principal: Principal, run_id: str, request_id: str
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        bundle = self.db.get_agent_run_bundle(principal.tenant_id, run_id)
        run = bundle["run"]
        if run["status"] != "completed":
            raise ConflictError("only completed agent runs can be evaluated")
        attempt = int(run.get("attempt_count") or 0)
        reports = [
            artifact["content"]
            for artifact in bundle["artifacts"]
            if artifact["kind"] == "weekly_ops_report"
            and int(artifact.get("attempt") or 0) == attempt
        ]
        if len(reports) != 1:
            raise ConflictError(
                "completed run must have one weekly_ops_report for its final attempt"
            )
        report = reports[0]
        source_platforms = {
            source["source_id"]: source["platform"] for source in run["evidence"]
        }
        task_names = {task["agent_name"] for task in bundle["tasks"]}
        checks: list[dict[str, Any]] = []

        def record(name: str, passed: bool, detail: str) -> None:
            checks.append({"name": name, "passed": passed, "detail": detail})

        incomplete = [
            task["agent_name"] for task in bundle["tasks"] if task["status"] != "completed"
        ]
        record("all_tasks_completed", not incomplete, ", ".join(incomplete) or "all completed")

        reviewer_tasks = [
            task for task in bundle["tasks"] if task.get("role") == "reviewer"
        ]
        reviewer_task = reviewer_tasks[0] if len(reviewer_tasks) == 1 else None
        reviewer_artifacts = [
            artifact for artifact in bundle["artifacts"]
            if artifact["kind"] == "reviewer_verdict"
            and reviewer_task is not None
            and artifact.get("task_id") == reviewer_task["id"]
            and int(artifact.get("attempt") or 0)
            == int(reviewer_task.get("attempt_count") or 0)
        ]
        reviewer_contract_ok = False
        if len(reviewer_artifacts) == 1:
            try:
                WeeklyOpsCouncil._validate_reviewer(
                    reviewer_artifacts[0]["content"], source_platforms, report
                )
                reviewer_contract_ok = True
            except (RuntimeErrorBase, KeyError, TypeError, ValueError):
                reviewer_contract_ok = False
        reviewer_ok = (
            bool(run.get("graph_version_id"))
            and bool(run.get("graph_version_hash"))
            and run.get("review_status") == "approved"
            and len(reviewer_tasks) == 1
            and reviewer_tasks[0]["status"] == "completed"
            and len(reviewer_artifacts) == 1
            and reviewer_artifacts[0]["content"].get("verdict") == "approved"
            and reviewer_contract_ok
        )
        reviewer_detail = (
            "approved reviewer task, artifact, and graph lineage present"
            if reviewer_ok
            else f"review_status={run.get('review_status')}; graph/reviewer lineage incomplete"
        )
        record("reviewer_approval", reviewer_ok, reviewer_detail)

        priorities = report.get("priorities") if isinstance(report, dict) else None
        valid_priority_shape = isinstance(priorities, list) and len(priorities) <= 5
        if valid_priority_shape:
            ranks = [item.get("rank") for item in priorities if isinstance(item, dict)]
            valid_priority_shape = ranks == list(range(1, len(priorities) + 1))
        record(
            "priority_shape",
            valid_priority_shape,
            "at most five priorities with contiguous ranks",
        )

        evidence_errors = []
        platform_errors = []
        owner_errors = []
        approval_errors = []
        collections = []
        if isinstance(report, dict):
            collections.extend(report.get("priorities", []))
            collections.extend(report.get("risks", []))
        for item in collections:
            if not isinstance(item, dict):
                evidence_errors.append("non-object item")
                continue
            refs = item.get("evidence_refs")
            if not isinstance(refs, list) or not refs:
                evidence_errors.append(str(item.get("title") or item.get("risk") or "item"))
                continue
            unknown = set(refs) - set(source_platforms)
            if unknown:
                evidence_errors.extend(sorted(unknown))
            platforms = item.get("platforms")
            if isinstance(platforms, list):
                cited = {source_platforms[ref] for ref in refs if ref in source_platforms}
                for platform in platforms:
                    if (
                        platform != "cross_platform"
                        and platform not in cited
                        and "cross_platform" not in cited
                    ):
                        platform_errors.append(str(platform))
            if "recommended_owner" in item:
                owner = item.get("recommended_owner")
                if owner not in task_names | {"human_operator"}:
                    owner_errors.append(str(owner))
                action_type = item.get("action_type")
                if (
                    action_type not in {"analysis", "external_change"}
                    or item.get("requires_approval") is not True
                ):
                    approval_errors.append(str(item.get("title", "priority")))

        record("evidence_references", not evidence_errors, ", ".join(evidence_errors) or "valid")
        record("platform_isolation", not platform_errors, ", ".join(platform_errors) or "valid")
        record("owner_assignment", not owner_errors, ", ".join(owner_errors) or "valid")
        record("approval_policy", not approval_errors, ", ".join(approval_errors) or "valid")
        try:
            WeeklyOpsCouncil._validate_manager_metric_claims(report, run["evidence"])
            metric_claim_error = ""
        except (RuntimeErrorBase, KeyError, TypeError, ValueError) as exc:
            metric_claim_error = str(exc) or type(exc).__name__
        record("metric_claim_safety", not metric_claim_error, metric_claim_error or "valid")
        passed_count = sum(1 for check in checks if check["passed"])
        score = passed_count / len(checks)
        details = {"checks": checks, "passed_count": passed_count, "check_count": len(checks)}
        evaluation = self.db.create_agent_evaluation(
            principal.tenant_id,
            run_id,
            principal.user_id,
            evaluator_version=self.VERSION,
            passed=passed_count == len(checks),
            score=score,
            details=details,
        )
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "agent_run.evaluate",
            "agent_run",
            run_id,
            "succeeded" if evaluation["passed"] else "failed",
            {"evaluation_id": evaluation["id"], "score": score},
        )
        return evaluation

    def list(self, principal: Principal, run_id: str) -> list[dict[str, Any]]:
        self.auth.require(principal, "viewer")
        self.db.get_agent_run(principal.tenant_id, run_id)
        return self.db.list_agent_evaluations(principal.tenant_id, run_id)
