"""Read-only status for the deliberately uninstalled Amazon Ads adapter.

This module is a hard negative gate: a passed read-capability check can only
make the adapter *eligible for a future installation*.  It never registers an
adapter and it exposes no write operation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from .ads_gates import REQUIRED_CAPABILITIES
from .auth import AuthService
from .errors import ValidationError
from .storage import Database, Principal


def _instant(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else None


class AdsAdapterStatusService:
    """Evaluate installation eligibility without enabling any Ads writes."""

    MAX_AGE_SECONDS = 24 * 60 * 60

    def __init__(
        self,
        db: Database,
        auth: AuthService,
        *,
        clock: Callable[[], datetime] | None = None,
    ):
        self.db = db
        self.auth = auth
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def get(
        self, principal: Principal, connector_account_id: Any = None
    ) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        if connector_account_id is not None:
            if not isinstance(connector_account_id, str) or not connector_account_id.strip():
                raise ValidationError("connector_account_id must be a non-empty string")
            account_ids = [connector_account_id.strip()]
        else:
            account_ids = [
                item["id"]
                for item in self.db.list_connector_accounts(principal.tenant_id)
                if item["provider"] == "amazon_ads"
            ]

        evaluated_at = self.clock()
        if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
            raise ValidationError("adapter status clock must be timezone-aware")
        candidates = []
        for account_id in account_ids:
            account = self.db.get_connector_account(principal.tenant_id, account_id)
            if account["provider"] != "amazon_ads":
                raise ValidationError("connector_account_id must reference an amazon_ads account")
            gate = self.db.latest_ads_capability_gate(
                principal.tenant_id, account_id
            )
            candidates.append(self._evaluate(account, gate, evaluated_at))

        if candidates:
            # A tenant-wide read returns one deterministic aggregate.  A
            # selected account returns its complete per-account result.
            if connector_account_id is not None:
                return candidates[0]
            eligible = [item for item in candidates if item["status"] == "eligible_not_installed"]
            if eligible:
                return eligible[0]
            return candidates[0]

        return self._empty(evaluated_at)

    @staticmethod
    def _empty(evaluated_at: datetime) -> dict[str, Any]:
        return {
            "status": "blocked",
            "adapter_registered": False,
            "write_operations": [],
            "reason_codes": [
                "no_amazon_ads_account",
                "adapter_not_installed",
                "write_surface_disabled",
            ],
            "connector_account_id": None,
            "gate_id": None,
            "gate_checked_at": None,
            "account_updated_at": None,
            "profile_id": None,
            "region": None,
            "evaluated_at": evaluated_at.isoformat(timespec="seconds"),
        }

    def _evaluate(
        self, account: dict[str, Any], gate: dict[str, Any] | None, evaluated_at: datetime
    ) -> dict[str, Any]:
        reasons: list[str] = []
        if gate is None:
            reasons.append("no_capability_gate")
        else:
            if gate["status"] != "passed":
                reasons.append("gate_not_passed")
            required = set(gate.get("required_capabilities") or [])
            observed = set(gate.get("observed_capabilities") or [])
            expected = set(REQUIRED_CAPABILITIES)
            if required != expected or not expected.issubset(observed):
                reasons.append("required_capabilities_missing")
            config = account.get("config") or {}
            if gate.get("region") != config.get("region") or str(gate.get("profile_id")) != str(config.get("profile_id")):
                reasons.append("gate_account_config_mismatch")
            checked = _instant(gate.get("completed_at"))
            updated = _instant(account.get("updated_at"))
            if checked is None:
                reasons.append("gate_not_checked")
            else:
                if updated is not None and checked < updated:
                    reasons.append("gate_stale_account_changed")
                age_seconds = (evaluated_at - checked).total_seconds()
                if age_seconds < -300:
                    reasons.append("gate_checked_in_future")
                elif age_seconds > self.MAX_AGE_SECONDS:
                    reasons.append("gate_expired")
        status = "eligible_not_installed" if not reasons else "blocked"
        reason_codes = list(dict.fromkeys(
            reasons + ["adapter_not_installed", "write_surface_disabled"]
        ))
        config = account.get("config") or {}
        return {
            "status": status,
            "adapter_registered": False,
            "write_operations": [],
            "reason_codes": reason_codes,
            "connector_account_id": account["id"],
            "gate_id": gate["id"] if gate else None,
            "gate_checked_at": gate.get("completed_at") if gate else None,
            "account_updated_at": account.get("updated_at"),
            "profile_id": str(config.get("profile_id")) if config.get("profile_id") else None,
            "region": config.get("region"),
            "evaluated_at": evaluated_at.isoformat(timespec="seconds"),
        }
