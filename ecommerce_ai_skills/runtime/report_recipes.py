"""Configuration-only Amazon marketplace report recipes."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .auth import AuthService
from .errors import ValidationError
from .storage import Database, Principal


REPORT_RECIPE_CATALOG: dict[str, dict[str, str]] = {
    "sales_traffic_daily": {
        "label": "Daily sales and traffic",
        "amazon_report_type": "GET_SALES_AND_TRAFFIC_REPORT",
        "evidence_report_type": "amazon_business_report",
    },
    "fba_inventory_daily": {
        "label": "Daily FBA inventory",
        "amazon_report_type": "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA",
        "evidence_report_type": "amazon_fba_inventory",
    },
    "listings_daily": {
        "label": "Daily listings snapshot",
        "amazon_report_type": "GET_MERCHANT_LISTINGS_ALL_DATA",
        "evidence_report_type": "amazon_listing",
    },
    "returns_daily": {
        "label": "Daily customer returns",
        "amazon_report_type": "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
        "evidence_report_type": "amazon_returns",
    },
}


class ReportRecipeService:
    """Validate and persist report schedules without calling Amazon."""

    def __init__(self, db: Database, auth: AuthService):
        self.db = db
        self.auth = auth

    @staticmethod
    def catalog() -> list[dict[str, str]]:
        return [
            {"key": key, **details}
            for key, details in REPORT_RECIPE_CATALOG.items()
        ]

    @staticmethod
    def _safe(recipe: dict[str, Any]) -> dict[str, Any]:
        derived = REPORT_RECIPE_CATALOG[recipe["recipe_key"]]
        return {
            "id": recipe["id"],
            "tenant_id": recipe["tenant_id"],
            "connector_account_id": recipe["connector_account_id"],
            "created_by": recipe["created_by"],
            "name": recipe["name"],
            "recipe_key": recipe["recipe_key"],
            "marketplace_ids": recipe["marketplace_ids"],
            "interval_minutes": recipe["interval_minutes"],
            "lookback_days": recipe["lookback_days"],
            "enabled": recipe["enabled"],
            "next_run_at": recipe["next_run_at"],
            "amazon_report_type": derived["amazon_report_type"],
            "evidence_report_type": derived["evidence_report_type"],
            "created_at": recipe["created_at"],
            "updated_at": recipe["updated_at"],
        }

    @staticmethod
    def _validate_values(
        account: dict[str, Any],
        *,
        name: Any,
        recipe_key: Any,
        marketplace_ids: Any,
        interval_minutes: Any,
        lookback_days: Any,
        enabled: Any,
        next_run_at: Any,
    ) -> dict[str, Any]:
        if account["provider"] != "amazon_spapi":
            raise ValidationError("report recipes require an amazon_spapi connector account")
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
            raise ValidationError("report recipe name must be between 1 and 100 characters")
        if not isinstance(recipe_key, str) or recipe_key not in REPORT_RECIPE_CATALOG:
            raise ValidationError("unknown report recipe_key")
        if (
            not isinstance(marketplace_ids, list)
            or not marketplace_ids
            or not all(isinstance(value, str) and value for value in marketplace_ids)
        ):
            raise ValidationError("marketplace_ids must be a non-empty list of identifiers")
        if len(set(marketplace_ids)) != len(marketplace_ids):
            raise ValidationError("marketplace_ids must not contain duplicates")
        configured = account["config"].get("marketplace_ids")
        if not isinstance(configured, list) or not set(marketplace_ids).issubset(configured):
            raise ValidationError(
                "marketplace_ids must be a subset of the connector account marketplaces"
            )
        if (
            not isinstance(interval_minutes, int)
            or isinstance(interval_minutes, bool)
            or not 60 <= interval_minutes <= 43_200
        ):
            raise ValidationError("interval_minutes must be between 60 and 43200")
        if (
            not isinstance(lookback_days, int)
            or isinstance(lookback_days, bool)
            or not 1 <= lookback_days <= 30
        ):
            raise ValidationError("lookback_days must be between 1 and 30")
        if not isinstance(enabled, bool):
            raise ValidationError("enabled must be boolean")
        if not isinstance(next_run_at, str) or not next_run_at.strip():
            raise ValidationError("next_run_at must be a timezone-aware ISO timestamp")
        try:
            parsed = datetime.fromisoformat(next_run_at.strip().replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValidationError("next_run_at must be a timezone-aware ISO timestamp") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValidationError("next_run_at must include a timezone")
        return {
            "name": name.strip(),
            "recipe_key": recipe_key,
            "marketplace_ids": list(marketplace_ids),
            "interval_minutes": interval_minutes,
            "lookback_days": lookback_days,
            "enabled": enabled,
            "next_run_at": next_run_at.strip(),
        }

    def list(self, principal: Principal) -> list[dict[str, Any]]:
        self.auth.require(principal, "viewer")
        return [
            self._safe(recipe)
            for recipe in self.db.list_report_recipes(principal.tenant_id)
        ]

    def get(self, principal: Principal, recipe_id: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        return self._safe(self.db.get_report_recipe(principal.tenant_id, recipe_id))

    def create(
        self,
        principal: Principal,
        connector_account_id: str,
        name: Any,
        recipe_key: Any,
        marketplace_ids: Any,
        interval_minutes: Any,
        lookback_days: Any,
        enabled: Any,
        next_run_at: Any,
        request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        if not isinstance(connector_account_id, str) or not connector_account_id.strip():
            raise ValidationError("connector_account_id is required")
        account = self.db.get_connector_account(
            principal.tenant_id, connector_account_id.strip()
        )
        values = self._validate_values(
            account,
            name=name,
            recipe_key=recipe_key,
            marketplace_ids=marketplace_ids,
            interval_minutes=interval_minutes,
            lookback_days=lookback_days,
            enabled=enabled,
            next_run_at=next_run_at,
        )
        recipe = self.db.create_report_recipe(
            principal.tenant_id,
            principal.user_id,
            connector_account_id=connector_account_id.strip(),
            **values,
        )
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "marketplace_report_recipe.create",
            "report_recipe",
            recipe["id"],
            "succeeded",
            {"recipe_key": recipe_key},
        )
        return self._safe(recipe)

    def update(
        self,
        principal: Principal,
        recipe_id: str,
        name: Any,
        recipe_key: Any,
        marketplace_ids: Any,
        interval_minutes: Any,
        lookback_days: Any,
        enabled: Any,
        next_run_at: Any,
        request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        existing = self.db.get_report_recipe(principal.tenant_id, recipe_id)
        account = self.db.get_connector_account(
            principal.tenant_id, existing["connector_account_id"]
        )
        values = self._validate_values(
            account,
            name=name,
            recipe_key=recipe_key,
            marketplace_ids=marketplace_ids,
            interval_minutes=interval_minutes,
            lookback_days=lookback_days,
            enabled=enabled,
            next_run_at=next_run_at,
        )
        recipe = self.db.update_report_recipe(
            principal.tenant_id, recipe_id, **values
        )
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "marketplace_report_recipe.update",
            "report_recipe",
            recipe_id,
            "succeeded",
            {"recipe_key": recipe_key},
        )
        return self._safe(recipe)
