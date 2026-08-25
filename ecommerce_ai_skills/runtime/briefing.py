"""Evidence-backed operating brief for the Mission Control home screen.

The briefing is a read model over existing tenant-owned runtime records.  It
never invents dashboard values: metrics are calculated only from recognized
columns in imported Evidence, while recommendations and agent state come from
persisted Weekly Ops artifacts and tasks.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from .agents import PlatformRegistry
from .auth import AuthService
from .errors import ValidationError
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


def _number(value: Any) -> Decimal | None:
    """Parse common marketplace numeric/currency/percentage cells safely."""

    if value is None:
        return None
    text = str(value).strip()
    if not text or text in {"-", "--", "N/A", "n/a"}:
        return None
    negative = text.startswith("(") and text.endswith(")")
    normalized = re.sub(r"[^0-9.+-]", "", text.replace(",", ""))
    if not normalized or normalized in {"+", "-", "."}:
        return None
    try:
        parsed = Decimal(normalized)
    except InvalidOperation:
        return None
    return -parsed if negative else parsed


def _sum(rows: list[dict[str, str]], field: str) -> Decimal | None:
    values = [_number(row.get(field)) for row in rows]
    present = [value for value in values if value is not None]
    return sum(present, Decimal(0)) if present else None


def _extract_metrics(imported: dict[str, Any]) -> dict[str, Decimal]:
    rows = imported.get("rows") or []
    report_type = imported.get("report_type")
    result: dict[str, Decimal] = {}
    if report_type == "amazon_business_report":
        revenue = _sum(rows, "ordered_product_sales")
        units = _sum(rows, "units_ordered")
        sessions = _sum(rows, "sessions")
        if revenue is not None:
            result["revenue"] = revenue
        if units is not None:
            result["units_ordered"] = units
        if sessions is not None:
            result["sessions"] = sessions
        if units is not None and sessions not in {None, Decimal(0)}:
            result["conversion_rate"] = units / sessions * Decimal(100)
        elif rows:
            percentages = [
                _number(row.get("unit_session_percentage")) for row in rows
            ]
            present = [value for value in percentages if value is not None]
            if present:
                result["conversion_rate"] = sum(present, Decimal(0)) / len(present)
    elif report_type == "amazon_ads_search_term":
        spend = _sum(rows, "spend")
        if spend is not None:
            result["ad_spend"] = spend
    elif report_type == "amazon_fba_inventory":
        quantities = [_number(row.get("fulfillable_quantity")) for row in rows]
        result["stockout_skus"] = Decimal(
            sum(1 for value in quantities if value is not None and value <= 0)
        )
    elif report_type == "amazon_returns":
        result["return_requests"] = Decimal(len(rows))
    elif report_type == "amazon_listing":
        result["listing_items"] = Decimal(len(rows))
    return result


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

    MAX_IMPORTS_WITH_ROWS = 20

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

    @staticmethod
    def _metric_payload(key: str, points: list[dict[str, Any]]) -> dict[str, Any]:
        ordered = sorted(points, key=lambda point: _timestamp(point["observed_at"]))[-7:]
        current = Decimal(str(ordered[-1]["value"]))
        previous = Decimal(str(ordered[-2]["value"])) if len(ordered) > 1 else None
        change_percent = None
        if previous not in {None, Decimal(0)}:
            change_percent = float((current - previous) / abs(previous) * Decimal(100))
        return {
            "key": key,
            **METRIC_META[key],
            "value": float(current),
            "change_percent": change_percent,
            "observed_at": ordered[-1]["observed_at"],
            "source_import_id": ordered[-1]["source_import_id"],
            "series": ordered,
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
        detailed = [
            self.db.get_evidence_import(
                principal.tenant_id, item["id"], include_rows=True
            )
            for item in metadata[: self.MAX_IMPORTS_WITH_ROWS]
        ]
        metric_points: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for imported in detailed:
            for key, value in _extract_metrics(imported).items():
                metric_points[key].append(
                    {
                        "observed_at": imported["observed_at"],
                        "value": float(value),
                        "source_import_id": imported["id"],
                    }
                )
        metrics = [
            self._metric_payload(key, metric_points[key])
            for key in METRIC_ORDER
            if metric_points.get(key)
        ]

        relevant_runs = [
            run
            for run in self.db.list_agent_runs(principal.tenant_id, limit=50)
            if platform in run.get("platforms", [])
        ]
        latest_run = relevant_runs[0] if relevant_runs else None
        completed_run = next(
            (run for run in relevant_runs if run["status"] == "completed"), None
        )
        bundle = (
            self.db.get_agent_run_bundle(principal.tenant_id, completed_run["id"])
            if completed_run
            else None
        )
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
