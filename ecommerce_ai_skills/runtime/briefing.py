"""Evidence-backed operating brief for the Mission Control home screen.

The briefing is a read model over existing tenant-owned runtime records.  It
never invents dashboard values: metrics are calculated only from recognized
columns in imported Evidence, while recommendations and agent state come from
persisted Weekly Ops artifacts and tasks.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Any

from .agents import PlatformRegistry, WeeklyOpsCouncil
from .auth import AuthService
from .errors import RuntimeErrorBase, ValidationError
from .storage import Database, Principal


METRIC_META: dict[str, dict[str, str]] = {
    "revenue": {
        "label": "销售额",
        "format": "amount",
        "trend_mode": "higher_is_better",
    },
    "units_ordered": {
        "label": "订购件数",
        "format": "integer",
        "trend_mode": "higher_is_better",
    },
    "sessions": {
        "label": "Sessions",
        "format": "integer",
        "trend_mode": "context_only",
    },
    "conversion_rate": {
        "label": "转化率",
        "format": "percent",
        "trend_mode": "higher_is_better",
    },
    "ad_spend": {
        "label": "广告花费",
        "format": "amount",
        "trend_mode": "context_only",
    },
    "stockout_skus": {
        "label": "缺货 SKU",
        "format": "integer",
        "trend_mode": "higher_is_risk",
    },
    "return_requests": {
        "label": "退货记录",
        "format": "integer",
        "trend_mode": "higher_is_risk",
    },
    "listing_items": {
        "label": "Listing 条目",
        "format": "integer",
        "trend_mode": "context_only",
    },
}

METRIC_ORDER = (
    "revenue",
    "conversion_rate",
    "ad_spend",
    "stockout_skus",
    "units_ordered",
    "sessions",
    "return_requests",
    "listing_items",
)


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _action_platform(action: dict[str, Any]) -> str | None:
    payload = action.get("payload") or {}
    explicit = payload.get("platform") if isinstance(payload, dict) else None
    if isinstance(explicit, str):
        return explicit
    operation = str(action.get("operation", ""))
    prefix = operation.split(".", 1)[0]
    if prefix.endswith("_spapi"):
        prefix = prefix[: -len("_spapi")]
    return prefix or None


class BriefingService:
    """Build a tenant-safe, evidence-backed daily operating brief."""

    def __init__(
        self,
        db: Database,
        auth: AuthService,
        *,
        platform_registry: PlatformRegistry | None = None,
    ):
        self.db = db
        self.auth = auth
        self.platform_registry = platform_registry or PlatformRegistry()

    def _approved_bundle(
        self, tenant_id: str, run: dict[str, Any]
    ) -> dict[str, Any] | None:
        if (
            run.get("status") != "completed"
            or run.get("review_status") != "approved"
            or not run.get("graph_version_id")
            or not run.get("graph_version_hash")
        ):
            return None
        if not self.db.agent_run_downstream_eligible(tenant_id, run["id"]):
            return None
        bundle = self.db.get_agent_run_bundle(tenant_id, run["id"])
        attempt = int(run.get("attempt_count") or 0)
        reviewers = [task for task in bundle["tasks"] if task.get("role") == "reviewer"]
        reviewer = reviewers[0] if len(reviewers) == 1 else None
        verdicts = [
            artifact for artifact in bundle["artifacts"]
            if artifact["kind"] == "reviewer_verdict"
            and reviewer is not None
            and artifact.get("task_id") == reviewer["id"]
            and int(artifact.get("attempt") or 0)
            == int(reviewer.get("attempt_count") or 0)
        ]
        reports = [
            artifact for artifact in bundle["artifacts"]
            if artifact["kind"] == "weekly_ops_report"
            and int(artifact.get("attempt") or 0) == attempt
        ]
        if (
            len(reviewers) != 1
            or reviewers[0]["status"] != "completed"
            or len(verdicts) != 1
            or verdicts[0]["content"].get("verdict") != "approved"
            or len(reports) != 1
        ):
            return None
        source_platforms = {
            source["source_id"]: source["platform"] for source in bundle["run"]["evidence"]
        }
        valid_owners = {
            task["agent_name"]
            for task in bundle["tasks"]
            if task.get("role") in {
                "evidence_analyst", "platform_specialist", "cross_controller"
            }
        } | {"human_operator"}
        try:
            WeeklyOpsCouncil._validate_refs(
                reports[0]["content"],
                source_platforms,
                manager=True,
                valid_owners=valid_owners,
            )
            WeeklyOpsCouncil._validate_manager_metric_claims(
                reports[0]["content"], bundle["run"]["evidence"]
            )
            WeeklyOpsCouncil._validate_reviewer(
                verdicts[0]["content"], source_platforms, reports[0]["content"]
            )
        except (RuntimeErrorBase, KeyError, TypeError, ValueError):
            return None
        return bundle

    @staticmethod
    def _metric_payload(key: str, points: list[dict[str, Any]]) -> dict[str, Any]:
        ordered = sorted(points, key=lambda point: _timestamp(point["period_end"]))[-7:]
        current = Decimal(str(ordered[-1]["value"]))
        previous = Decimal(str(ordered[-2]["value"])) if len(ordered) > 1 else None
        change_percent = None
        comparable = False
        if len(ordered) > 1:
            previous_start = _timestamp(ordered[-2]["period_start"])
            previous_end = _timestamp(ordered[-2]["period_end"])
            current_start = _timestamp(ordered[-1]["period_start"])
            current_end = _timestamp(ordered[-1]["period_end"])
            previous_duration = previous_end - previous_start
            current_duration = current_end - current_start
            comparable = (
                previous_duration == current_duration
                and previous_end <= current_start
                and (current_duration.total_seconds() > 0 or previous_end < current_start)
            )
        if comparable and previous not in {None, Decimal(0)}:
            change_percent = float((current - previous) / abs(previous) * Decimal(100))
        display_multiplier = Decimal(100) if METRIC_META[key]["format"] == "percent" else Decimal(1)
        display_series = [
            {
                **point,
                "value": float(Decimal(str(point["value"])) * display_multiplier),
            }
            for point in ordered
        ]
        return {
            "key": key,
            **METRIC_META[key],
            "value": float(current * display_multiplier),
            "change_percent": change_percent,
            "observed_at": ordered[-1]["period_end"],
            "source_import_id": ordered[-1]["source_import_id"],
            "series": display_series,
        }

    def get(self, principal: Principal, platform: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        entries = self.platform_registry.entries()
        if platform not in entries:
            raise ValidationError(f"unsupported platform: {platform}")

        metadata = [
            item
            for item in self.db.list_evidence_imports(principal.tenant_id, 200)
            if item["platform"] == platform
        ]
        observations, _ = self.db.list_metric_observations(
            principal.tenant_id, limit=200, platform=platform
        )
        metric_points: dict[
            tuple[str, str, str | None, str, str], list[dict[str, Any]]
        ] = (
            defaultdict(list)
        )
        for observation in observations:
            key = str(observation["metric_key"])
            if key not in METRIC_META:
                continue
            series = (
                key,
                str(observation["series_key"]),
                observation.get("currency"),
                str(observation["unit"]),
                str(observation["time_grain"]),
            )
            metric_points[series].append(
                {
                    "observed_at": observation["period_end"],
                    "period_start": observation["period_start"],
                    "period_end": observation["period_end"],
                    "value": float(Decimal(str(observation["value_decimal"]))),
                    "source_import_id": observation["evidence_import_id"],
                    "dimensions": observation["dimensions"],
                }
            )
        metrics = []
        for key in METRIC_ORDER:
            matching = sorted(
                (
                    (series, points)
                    for series, points in metric_points.items()
                    if series[0] == key
                ),
                key=lambda item: (item[0][2] or "", item[0][1], item[0][4]),
            )
            for series, points in matching:
                payload = self._metric_payload(key, points)
                payload["currency"] = series[2]
                payload["unit"] = series[3]
                payload["time_grain"] = series[4]
                payload["dimensions"] = points[-1]["dimensions"]
                payload["series_id"] = hashlib.sha256(
                    f"{series[1]}|{series[4]}".encode("utf-8")
                ).hexdigest()[:24]
                metrics.append(payload)

        relevant_runs = [
            run
            for run in self.db.list_agent_runs(principal.tenant_id, limit=50)
            if platform in run.get("platforms", [])
        ]
        latest_run = relevant_runs[0] if relevant_runs else None
        completed_run = None
        bundle = None
        for candidate in relevant_runs:
            candidate_bundle = self._approved_bundle(principal.tenant_id, candidate)
            if candidate_bundle is not None:
                completed_run = candidate
                bundle = candidate_bundle
                break
        report = None
        if bundle:
            report = next(
                (
                    artifact["content"]
                    for artifact in reversed(bundle.get("artifacts", []))
                    if artifact["kind"] == "weekly_ops_report"
                ),
                None,
            )
        priorities = sorted(
            (report or {}).get("priorities", []), key=lambda item: item.get("rank", 999)
        )[:5]
        agents = []
        for task in (bundle or {}).get("tasks", []):
            agents.append(
                {
                    "id": task["id"],
                    "name": task["agent_name"],
                    "status": task["status"],
                    "updated_at": task.get("completed_at")
                    or task.get("started_at")
                    or task["created_at"],
                    "skill_ids": task.get("skill_ids", []),
                }
            )

        approvals = [
            action
            for action in self.db.list_actions(
                principal.tenant_id, status="requested", limit=100
            )
            if _action_platform(action) in {platform, "cross_platform"}
        ][:20]
        platform_entry = entries[platform]
        latest_observed_at = (
            max((item["observed_at"] for item in metadata), key=_timestamp)
            if metadata
            else None
        )
        return {
            "platform": {
                "id": platform,
                "label": platform_entry.get("label", {}),
            },
            "evidence": {
                "source_count": len(metadata),
                "row_count": sum(int(item["row_count"]) for item in metadata),
                "latest_observed_at": latest_observed_at,
                "report_types": sorted({item["report_type"] for item in metadata}),
            },
            "metrics": metrics,
            "latest_run": latest_run,
            "brief_run_id": completed_run["id"] if completed_run else None,
            "executive_summary": (report or {}).get("executive_summary"),
            "priorities": priorities,
            "risks": (report or {}).get("risks", [])[:5],
            "limitations": (report or {}).get("limitations", [])[:10],
            "agents": agents,
            "approvals": approvals,
        }
