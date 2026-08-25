"""Tenant-safe materialization of Evidence rows into normalized metric facts."""

from __future__ import annotations

import json
import re
import uuid
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from typing import Any

from .agents import PlatformRegistry
from .auth import AuthService
from .errors import ValidationError
from .storage import Database, Principal


SUPPORTED_REPORT_TYPES = {
    "amazon_business_report",
    "amazon_ads_search_term",
    "amazon_fba_inventory",
    "amazon_returns",
    "amazon_listing",
}

# Currencies for the Amazon marketplaces exposed by the runtime catalog. A
# merely three-letter token is not accepted as ISO 4217 business evidence.
SUPPORTED_AMAZON_CURRENCY_CODES = {
    "AED",
    "AUD",
    "BRL",
    "CAD",
    "EGP",
    "EUR",
    "GBP",
    "INR",
    "JPY",
    "MXN",
    "PLN",
    "SAR",
    "SEK",
    "SGD",
    "TRY",
    "USD",
}


class MetricObservationService:
    """Create durable, provenance-bearing metric observations from Evidence."""

    CALCULATION_VERSION = "amazon-metrics-v2"
    MAX_ABSOLUTE_VALUE = Decimal("1e29")
    MAX_FRACTIONAL_DIGITS = 9
    MAX_ISSUES = 100

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
    def _validate_evidence_id(value: str | None) -> None:
        if value is None:
            return
        if not isinstance(value, str) or not 1 <= len(value) <= 200:
            raise ValidationError("evidence_import_id must be a non-empty UUID")
        try:
            parsed = uuid.UUID(value)
        except (ValueError, AttributeError) as exc:
            raise ValidationError("evidence_import_id must be a UUID") from exc
        if str(parsed) != value.lower():
            raise ValidationError("evidence_import_id must use canonical UUID format")

    @staticmethod
    def _safe_materialization(value: dict[str, Any]) -> dict[str, Any]:
        issues = value.get("issues") or []
        flags = sorted(
            set(value.get("quality_flags") or [])
            | {
                str(issue.get("code"))
                for issue in issues
                if isinstance(issue, dict) and issue.get("code")
            }
        )[:50]
        return {
            "id": value["id"],
            "tenant_id": value["tenant_id"],
            "evidence_import_id": value["evidence_import_id"],
            "idempotency_key": value["idempotency_key"],
            "status": value["status"],
            "observation_count": value["observation_count"],
            "quarantine_count": value["quarantine_count"],
            "currencies": value.get("currencies", []),
            "quality_summary": {
                "accepted": value["observation_count"],
                "quarantined": value["quarantine_count"],
                "flags": flags,
            },
            "error_code": value.get("error_code"),
            "error_message": value.get("error_message"),
            "created_by": value["created_by"],
            "created_at": value["created_at"],
            "updated_at": value["updated_at"],
        }

    @staticmethod
    def _safe_observation(value: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": value["id"],
            "tenant_id": value["tenant_id"],
            "materialization_id": value["materialization_id"],
            "evidence_import_id": value["evidence_import_id"],
            "platform": value["platform"],
            "metric_key": value["metric_key"],
            "value_decimal": value["value_decimal"],
            "unit": value["unit"],
            "currency": value["currency"],
            "period_start": value["period_start"],
            "period_end": value["period_end"],
            "time_grain": value["time_grain"],
            "dimensions": value["dimensions"],
            "provenance": value["provenance"],
            "quality": value["quality_flags"],
            "created_at": value["created_at"],
        }

    @staticmethod
    def _decimal_text(value: Decimal) -> str:
        text = format(value, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text or "0"

    @classmethod
    def _parse_decimal(cls, value: Any) -> Decimal:
        if value is None:
            raise ValueError("missing")
        text = str(value).strip()
        if not text:
            raise ValueError("missing")
        if text.startswith("="):
            raise ValueError("formula")
        negative = text.startswith("(") and text.endswith(")")
        if negative:
            text = text[1:-1].strip()
            if text.startswith(("+", "-")):
                raise ValueError("invalid_number")
        normalized = re.sub(r"^[\s$€£¥]+|[\s$€£¥]+$", "", text)
        if not re.fullmatch(
            r"[+-]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d*)?|\.\d+)",
            normalized,
        ):
            raise ValueError("invalid_number")
        normalized = normalized.replace(",", "")
        try:
            parsed = Decimal(normalized)
        except InvalidOperation as exc:
            raise ValueError("invalid_number") from exc
        if not parsed.is_finite() or abs(parsed) >= cls.MAX_ABSOLUTE_VALUE:
            raise ValueError("out_of_bounds")
        fractional_digits = max(0, -parsed.as_tuple().exponent)
        if fractional_digits > cls.MAX_FRACTIONAL_DIGITS:
            raise ValueError("too_precise")
        if len(parsed.as_tuple().digits) > 38:
            raise ValueError("too_many_significant_digits")
        return -parsed if negative else parsed

    @classmethod
    def _bounded_result(cls, value: Decimal) -> Decimal:
        if max(0, -value.as_tuple().exponent) > cls.MAX_FRACTIONAL_DIGITS:
            value = value.quantize(Decimal("0.000000001"), rounding=ROUND_HALF_EVEN)
        if (
            not value.is_finite()
            or abs(value) >= cls.MAX_ABSOLUTE_VALUE
            or len(value.as_tuple().digits) > 38
        ):
            raise ValidationError("calculated metric exceeds the decimal contract")
        return value

    @staticmethod
    def _currency(row: dict[str, Any]) -> str | None:
        explicit = str(row.get("currency_code") or row.get("currency") or "").strip().upper()
        return explicit if explicit in SUPPORTED_AMAZON_CURRENCY_CODES else None

    @staticmethod
    def _time_context(imported: dict[str, Any], source: dict[str, Any]) -> tuple[str, str, str]:
        start = source.get("period_start") or imported["observed_at"]
        end = source.get("period_end") or imported["observed_at"]
        if start == end:
            return start, end, "snapshot"
        try:
            start_at = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
            end_at = datetime.fromisoformat(str(end).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValidationError("metric source period is not valid ISO-8601") from exc
        if start_at.tzinfo is None or end_at.tzinfo is None or end_at <= start_at:
            raise ValidationError(
                "metric source period must be timezone-aware and end after start"
            )
        return start, end, "day" if (end_at - start_at).total_seconds() <= 86400 else "range"

    def _extract(
        self, imported: dict[str, Any], source: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
        report_type = str(imported["report_type"])
        rows = imported.get("rows") or []
        issues: list[dict[str, Any]] = []
        issue_count = 0

        def issue(code: str, metric_key: str, row_number: int | None, column: str) -> None:
            nonlocal issue_count
            issue_count += 1
            if len(issues) < self.MAX_ISSUES:
                issues.append(
                    {
                        "code": code,
                        "metric_key": metric_key,
                        "row_number": row_number,
                        "column": column,
                    }
                )

        def values_by_row(field: str, metric_key: str) -> dict[int, Decimal]:
            parsed: dict[int, Decimal] = {}
            for index, row in enumerate(rows, start=2):
                if field not in row:
                    continue
                try:
                    parsed[index] = self._parse_decimal(row.get(field))
                except ValueError as exc:
                    issue(str(exc), metric_key, index, field)
            return parsed

        aggregates: list[tuple[str, Decimal, str | None, str, str]] = []
        if report_type == "amazon_business_report":
            units_by_row = values_by_row("units_ordered", "units_ordered")
            sessions_by_row = values_by_row("sessions", "sessions")
            units = list(units_by_row.values())
            sessions = list(sessions_by_row.values())
            if units:
                aggregates.append(("units_ordered", sum(units, Decimal(0)), None, "count", "sum(units_ordered)"))
            if sessions:
                aggregates.append(("sessions", sum(sessions, Decimal(0)), None, "count", "sum(sessions)"))
            paired_rows = sorted(set(units_by_row) & set(sessions_by_row))
            if set(units_by_row) != set(sessions_by_row):
                issue(
                    "incomplete_conversion_pair",
                    "conversion_rate",
                    None,
                    "units_ordered,sessions",
                )
            paired_units = sum(
                (units_by_row[index] for index in paired_rows), Decimal(0)
            )
            paired_sessions = sum(
                (sessions_by_row[index] for index in paired_rows), Decimal(0)
            )
            if paired_rows and paired_sessions != 0:
                conversion = self._bounded_result(
                    paired_units / paired_sessions
                )
                aggregates.append(("conversion_rate", conversion, None, "percent", "sum(units_ordered)/sum(sessions)"))
            elif paired_rows:
                issue("zero_denominator", "conversion_rate", None, "sessions")
            revenue_by_currency: dict[str, Decimal] = defaultdict(Decimal)
            for index, row in enumerate(rows, start=2):
                if "ordered_product_sales" not in row:
                    continue
                raw = row.get("ordered_product_sales")
                try:
                    amount = self._parse_decimal(raw)
                except ValueError as exc:
                    issue(str(exc), "revenue", index, "ordered_product_sales")
                    continue
                currency = self._currency(row)
                if currency is None:
                    issue("missing_or_invalid_currency", "revenue", index, "currency_code")
                    continue
                revenue_by_currency[currency] += amount
            for currency, amount in sorted(revenue_by_currency.items()):
                aggregates.append(("revenue", amount, currency, "amount", "sum(ordered_product_sales) by currency"))
        elif report_type == "amazon_ads_search_term":
            spend_by_currency: dict[str, Decimal] = defaultdict(Decimal)
            for index, row in enumerate(rows, start=2):
                raw = row.get("spend")
                try:
                    amount = self._parse_decimal(raw)
                except ValueError as exc:
                    issue(str(exc), "ad_spend", index, "spend")
                    continue
                currency = self._currency(row)
                if currency is None:
                    issue("missing_or_invalid_currency", "ad_spend", index, "currency_code")
                    continue
                spend_by_currency[currency] += amount
            for currency, amount in sorted(spend_by_currency.items()):
                aggregates.append(("ad_spend", amount, currency, "amount", "sum(spend) by currency"))
        elif report_type == "amazon_fba_inventory":
            quantities = list(
                values_by_row("fulfillable_quantity", "stockout_skus").values()
            )
            if quantities:
                aggregates.append(("stockout_skus", Decimal(sum(value <= 0 for value in quantities)), None, "count", "count(fulfillable_quantity<=0)"))
        elif report_type == "amazon_returns":
            aggregates.append(("return_requests", Decimal(len(rows)), None, "count", "count(rows)"))
        elif report_type == "amazon_listing":
            aggregates.append(("listing_items", Decimal(len(rows)), None, "count", "count(rows)"))
        else:
            issue("unsupported_report_type", "none", None, "report_type")

        if issue_count > len(issues):
            issues.append(
                {
                    "code": "additional_quarantined_values",
                    "count": issue_count - len(issues),
                    "metric_key": "multiple",
                    "row_number": None,
                    "column": "multiple",
                }
            )

        period_start, period_end, time_grain = self._time_context(imported, source)
        marketplace_ids = source.get("marketplace_ids") or []
        marketplace_id = marketplace_ids[0] if len(marketplace_ids) == 1 else None
        dimensions = (
            {"marketplace_scope": ",".join(str(item) for item in marketplace_ids)}
            if len(marketplace_ids) > 1
            else {}
        )
        shared_quality_flags: list[str] = []
        if source.get("report_sync_id") is None:
            shared_quality_flags.append("period_scope_unknown")
        if len(marketplace_ids) > 1:
            shared_quality_flags.append("multi_marketplace_scope")
        amount_currencies = {
            currency
            for _, _, currency, unit, _ in aggregates
            if unit == "amount" and currency is not None
        }
        mixed_currency = len(amount_currencies) > 1
        observations = []
        for metric_key, value, currency, unit, formula in aggregates:
            value = self._bounded_result(value)
            quality_flags = list(shared_quality_flags)
            if mixed_currency and unit == "amount":
                quality_flags.append("mixed_currency_isolated")
            observations.append(
                {
                    "connector_account_id": source.get("connector_account_id"),
                    "marketplace_id": marketplace_id,
                    "platform": imported["platform"],
                    "report_type": report_type,
                    "metric_key": metric_key,
                    "value_decimal": self._decimal_text(value),
                    "currency": currency,
                    "unit": {"amount": "currency", "percent": "ratio"}.get(unit, unit),
                    "time_grain": time_grain,
                    "period_start": period_start,
                    "period_end": period_end,
                    "observed_at": imported["observed_at"],
                    "dimensions": dimensions,
                    "provenance": {
                        "source_sha256": imported["sha256"],
                        "source_row": 1,
                        "source_field": formula[:200],
                        "mapping_version": self.CALCULATION_VERSION,
                    },
                    "quality_flags": {
                        "status": "accepted",
                        "flags": sorted(set(quality_flags)),
                    },
                }
            )
            observations[-1]["series_key"] = "|".join(
                [
                    metric_key,
                    currency or "-",
                    str(marketplace_id or "-"),
                    json.dumps(dimensions, sort_keys=True, separators=(",", ":")),
                ]
            )
        return observations, issues, issue_count

    def materialize(
        self,
        principal: Principal,
        evidence_import_id: str,
        idempotency_key: str,
        request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        imported = self.db.get_evidence_import(
            principal.tenant_id, evidence_import_id, include_rows=True
        )
        materialization, replayed = self.db.start_metric_materialization(
            principal.tenant_id,
            principal.user_id,
            evidence_import_id,
            idempotency_key,
            calculation_version=self.CALCULATION_VERSION,
        )
        if replayed:
            self._audit(principal, request_id, materialization, "replayed")
            return self._safe_materialization(materialization)
        try:
            source = self.db.metric_source_context(principal.tenant_id, evidence_import_id)
            observations, issues, quarantine_count = self._extract(imported, source)
            if not observations and any(
                issue.get("code") == "unsupported_report_type" for issue in issues
            ):
                materialization = self.db.fail_metric_materialization(
                    principal.tenant_id,
                    materialization["id"],
                    error_code="no_usable_metrics",
                    error_message="Evidence contained no usable supported metrics",
                    issues=issues,
                    quarantine_count=quarantine_count,
                )
            elif not observations:
                materialization = self.db.complete_metric_materialization(
                    principal.tenant_id,
                    materialization["id"],
                    status="quarantined",
                    issues=issues,
                    observations=[],
                    quarantine_count=quarantine_count,
                )
            else:
                materialization = self.db.complete_metric_materialization(
                    principal.tenant_id,
                    materialization["id"],
                    status="partial" if issues else "succeeded",
                    issues=issues,
                    observations=observations,
                    quarantine_count=quarantine_count,
                )
        except Exception as exc:
            if self.db.get_metric_materialization(
                principal.tenant_id, materialization["id"]
            )["status"] == "running":
                self.db.fail_metric_materialization(
                    principal.tenant_id,
                    materialization["id"],
                    error_code="materialization_error",
                    error_message="metric materialization failed before completion",
                )
            raise
        self._audit(principal, request_id, materialization, materialization["status"])
        return self._safe_materialization(materialization)

    def _audit(
        self,
        principal: Principal,
        request_id: str,
        materialization: dict[str, Any],
        outcome: str,
    ) -> None:
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "metric_materialization.create",
            "metric_materialization",
            materialization["id"],
            outcome,
            {
                "evidence_import_id": materialization["evidence_import_id"],
                "status": materialization["status"],
                "observation_count": materialization["observation_count"],
                "quarantine_count": materialization["quarantine_count"],
                "calculation_version": materialization["calculation_version"],
            },
        )

    def list_observations(
        self,
        principal: Principal,
        *,
        limit: int = 100,
        platform: str | None = None,
        metric_key: str | None = None,
        cursor: str | None = None,
        evidence_import_id: str | None = None,
        currency: str | None = None,
    ) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        if cursor is not None and (
            not isinstance(cursor, str) or not 1 <= len(cursor) <= 200
        ):
            raise ValidationError("cursor must be a string between 1 and 200 characters")
        self._validate_evidence_id(evidence_import_id)
        if platform is not None and platform not in self.platform_registry.entries():
            raise ValidationError("unsupported platform")
        if metric_key is not None and (
            not isinstance(metric_key, str)
            or re.fullmatch(r"[a-z][a-z0-9_.-]{0,79}", metric_key) is None
        ):
            raise ValidationError("metric_key has an invalid format")
        if currency is not None and not re.fullmatch(r"[A-Z]{3}", currency):
            raise ValidationError("currency must be an uppercase ISO 4217 code")
        observations, next_cursor = self.db.list_metric_observations(
            principal.tenant_id,
            limit=limit,
            cursor=cursor,
            evidence_import_id=evidence_import_id,
            platform=platform,
            metric_key=metric_key,
            currency=currency,
        )
        return {
            "observations": [self._safe_observation(item) for item in observations],
            "next_cursor": next_cursor,
        }

    def get_observation(
        self, principal: Principal, observation_id: str
    ) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        return self._safe_observation(
            self.db.get_metric_observation(principal.tenant_id, observation_id)
        )

    def list_materializations(
        self,
        principal: Principal,
        limit: int = 100,
        *,
        cursor: str | None = None,
        evidence_import_id: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        if cursor is not None and (
            not isinstance(cursor, str) or not 1 <= len(cursor) <= 200
        ):
            raise ValidationError("cursor must be a string between 1 and 200 characters")
        self._validate_evidence_id(evidence_import_id)
        if status is not None and status not in {
            "running",
            "succeeded",
            "partial",
            "quarantined",
            "failed",
        }:
            raise ValidationError("invalid metric materialization status")
        items, next_cursor = self.db.list_metric_materializations(
            principal.tenant_id,
            limit,
            cursor=cursor,
            evidence_import_id=evidence_import_id,
            status=status,
        )
        return {
            "materializations": [self._safe_materialization(item) for item in items],
            "next_cursor": next_cursor,
        }

    def backfill(
        self,
        principal: Principal,
        *,
        limit: int,
        cursor: str | None,
        request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "admin")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
            raise ValidationError("limit must be an integer between 1 and 100")
        if cursor is not None and (
            not isinstance(cursor, str) or not 1 <= len(cursor) <= 200
        ):
            raise ValidationError("cursor must be a string between 1 and 200 characters")
        imports, next_cursor = self.db.page_evidence_imports(
            principal.tenant_id, limit=limit, cursor=cursor
        )
        results = []
        for imported in imports:
            try:
                results.append(
                    self.materialize(
                        principal,
                        imported["id"],
                        f"metric-backfill:{self.CALCULATION_VERSION}:{imported['id']}",
                        f"{request_id}:{imported['id']}",
                    )
                )
            except Exception as exc:
                persisted, _ = self.db.list_metric_materializations(
                    principal.tenant_id,
                    1,
                    evidence_import_id=imported["id"],
                )
                if not persisted or persisted[0]["status"] != "failed":
                    raise
                results.append(self._safe_materialization(persisted[0]))
                self.db.append_audit(
                    principal.tenant_id,
                    principal.user_id,
                    f"{request_id}:{imported['id']}:failed",
                    "metric_materialization.backfill_item_failed",
                    "metric_materialization",
                    persisted[0]["id"],
                    "failed",
                    {
                        "evidence_import_id": imported["id"],
                        "error_type": type(exc).__name__,
                    },
                )
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "metric_materialization.backfill",
            "metric_materialization",
            None,
            "completed",
            {"processed": len(results), "limit": limit, "next_cursor": next_cursor},
        )
        return {
            "materializations": results,
            "processed": len(results),
            "next_cursor": next_cursor,
        }
