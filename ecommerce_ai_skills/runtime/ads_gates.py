"""Tenant-safe Amazon Ads read-capability contract gate."""

from __future__ import annotations

import os
import re
from typing import Any, Callable, Mapping
from urllib.request import urlopen

from .auth import AuthService
from .connectors.amazon_ads import (
    AmazonAdsConnector,
    AmazonAdsHTTPError,
    AmazonAdsRateLimitError,
    AmazonAdsServiceError,
    validate_amazon_ads_config,
)
from .errors import (
    ConflictError,
    ExternalServiceError,
    MissingCredentialError,
    ValidationError,
)
from .storage import Database, Principal


REQUIRED_CAPABILITIES = [
    "lwa",
    "profiles_read",
    "campaigns_list_read",
    "external_attestation",
]
_ATTESTATION_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/#-]{2,255}")


class AdsCapabilityGateService:
    def __init__(
        self,
        db: Database,
        auth: AuthService,
        *,
        environ: Mapping[str, str] | None = None,
        transport: Callable[..., Any] = urlopen,
    ):
        self.db = db
        self.auth = auth
        self.environ = environ if environ is not None else os.environ
        self.transport = transport

    @staticmethod
    def _attestation(value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValidationError("attestation_reference must be a string")
        normalized = value.strip()
        if not normalized:
            return None
        if not _ATTESTATION_RE.fullmatch(normalized):
            raise ValidationError(
                "attestation_reference must be a safe reference without query data"
            )
        return normalized

    def list(self, principal: Principal, limit: int = 100) -> list[dict[str, Any]]:
        self.auth.require(principal, "viewer")
        return [
            self._safe(item)
            for item in self.db.list_ads_capability_gates(principal.tenant_id, limit)
        ]

    def get(self, principal: Principal, gate_id: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        return self._safe(
            self.db.get_ads_capability_gate(principal.tenant_id, gate_id)
        )

    @staticmethod
    def _safe(gate: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": gate["id"],
            "tenant_id": gate["tenant_id"],
            "connector_account_id": gate["connector_account_id"],
            "created_by": gate["created_by"],
            "status": gate["status"],
            "region": gate["region"],
            "profile_id": gate["profile_id"],
            "required_capabilities": gate["required_capabilities"],
            "observed_capabilities": gate["observed_capabilities"],
            "checks": gate["checks"],
            "attestation_reference": gate["attestation_reference"],
            "request_ids": gate["request_ids"],
            "retry_after_seconds": gate["retry_after_seconds"],
            "error_code": gate["error_code"],
            "error_message": gate["error_message"],
            "created_at": gate["created_at"],
            "updated_at": gate["updated_at"],
            "checked_at": gate["completed_at"],
        }

    @staticmethod
    def _check_states(
        attested: bool,
        *,
        stopped_at: str | None = None,
        stopped_status: str = "blocked",
    ) -> list[dict[str, str]]:
        live = ["lwa", "profiles_read", "target_profile", "campaigns_list_read"]
        states: list[dict[str, str]] = []
        stopped = False
        for name in live:
            if stopped:
                status = "skipped"
            elif name == stopped_at:
                status = stopped_status
                stopped = True
            else:
                status = "passed"
            states.append({"name": name, "status": status})
        states.append(
            {
                "name": "external_attestation",
                "status": "passed" if attested else "blocked",
            }
        )
        return states

    @staticmethod
    def _stage_name(stage: str) -> str:
        return {
            "Amazon LWA": "lwa",
            "Amazon Ads profiles": "profiles_read",
            "Amazon Ads sponsored products": "campaigns_list_read",
        }.get(stage, "lwa")

    @staticmethod
    def _observed_before(stage: str, attested: bool) -> list[str]:
        observed: list[str] = []
        if stage != "lwa":
            observed.append("lwa")
        if stage == "campaigns_list_read":
            observed.append("profiles_read")
        if attested:
            observed.append("external_attestation")
        return observed

    def check(
        self,
        principal: Principal,
        connector_account_id: Any,
        attestation_reference: Any,
        idempotency_key: str,
        request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "admin")
        if not isinstance(connector_account_id, str) or not connector_account_id:
            raise ValidationError("connector_account_id is required")
        account = self.db.get_connector_account(
            principal.tenant_id, connector_account_id
        )
        if account["provider"] != "amazon_ads":
            raise ValidationError(
                "ads capability gate requires an amazon_ads connector account"
            )
        config = account["config"]
        region, profile_id = validate_amazon_ads_config(
            config.get("region"), config.get("profile_id")
        )
        attestation = self._attestation(attestation_reference)
        gate, replayed = self.db.create_ads_capability_gate(
            principal.tenant_id,
            principal.user_id,
            connector_account_id,
            idempotency_key,
            region=region,
            profile_id=profile_id,
            required_capabilities=REQUIRED_CAPABILITIES,
            attestation_reference=attestation,
        )
        if replayed:
            if gate["status"] != "checking":
                return self._safe(gate)
        try:
            claimed = self.db.claim_ads_capability_gate(
                principal.tenant_id, str(gate["id"])
            )
        except ConflictError:
            # An idempotent replay while another request holds a fresh lease
            # reports the durable checking state without starting a duplicate.
            return self._safe(
                self.db.get_ads_capability_gate(principal.tenant_id, str(gate["id"]))
            )
        if claimed["status"] != "checking":
            return self._safe(claimed)
        connector = AmazonAdsConnector(
            config, environ=self.environ, transport=self.transport
        )
        try:
            result = connector.probe()
        except MissingCredentialError:
            return self._finish(
                principal,
                claimed,
                request_id,
                status="blocked",
                error_code="missing_credential",
                error_message="required Amazon Ads credential is not configured",
                checks=self._check_states(
                    attestation is not None, stopped_at="lwa"
                ),
                observed_capabilities=(
                    ["external_attestation"] if attestation is not None else []
                ),
            )
        except ValidationError as exc:
            return self._finish(
                principal,
                claimed,
                request_id,
                status="blocked",
                error_code="profile_validation_failed",
                error_message=str(exc),
                checks=self._check_states(
                    attestation is not None, stopped_at="target_profile"
                ),
                observed_capabilities=["lwa", "profiles_read"]
                + (["external_attestation"] if attestation is not None else []),
                request_ids=list(getattr(exc, "request_ids", [])),
            )
        except AmazonAdsRateLimitError as exc:
            stage = self._stage_name(exc.stage)
            return self._finish(
                principal,
                claimed,
                request_id,
                status="blocked",
                error_code="rate_limited",
                error_message="Amazon Ads requested a retry later",
                request_ids=exc.request_ids,
                retry_after_seconds=exc.retry_after,
                checks=self._check_states(
                    attestation is not None,
                    stopped_at=stage,
                ),
                observed_capabilities=self._observed_before(
                    stage, attestation is not None
                ),
            )
        except AmazonAdsHTTPError as exc:
            stage = self._stage_name(exc.stage)
            if exc.status_code in {401, 403}:
                return self._finish(
                    principal,
                    claimed,
                    request_id,
                    status="blocked",
                    error_code=(
                        "amazon_ads_unauthorized"
                        if exc.status_code == 401
                        else "amazon_ads_forbidden"
                    ),
                    error_message=f"Amazon Ads access was rejected with HTTP {exc.status_code}",
                    request_ids=exc.request_ids,
                    checks=self._check_states(
                        attestation is not None,
                        stopped_at=stage,
                    ),
                    observed_capabilities=self._observed_before(
                        stage, attestation is not None
                    ),
                )
            self._finish(
                principal,
                claimed,
                request_id,
                status="failed",
                error_code="amazon_ads_http_error",
                error_message=f"Amazon Ads returned HTTP {exc.status_code}",
                request_ids=exc.request_ids,
                checks=self._check_states(
                    attestation is not None,
                    stopped_at=stage,
                    stopped_status="failed",
                ),
                observed_capabilities=self._observed_before(
                    stage, attestation is not None
                ),
            )
            raise
        except AmazonAdsServiceError as exc:
            stage = self._stage_name(exc.stage)
            self._finish(
                principal,
                claimed,
                request_id,
                status="failed",
                error_code="external_service_error",
                error_message="Amazon Ads capability check failed",
                request_ids=exc.request_ids,
                checks=self._check_states(
                    attestation is not None,
                    stopped_at=stage,
                    stopped_status="failed",
                ),
                observed_capabilities=self._observed_before(
                    stage, attestation is not None
                ),
            )
            raise
        except Exception:
            self._finish(
                principal,
                claimed,
                request_id,
                status="failed",
                error_code="internal_error",
                error_message="Amazon Ads capability check failed unexpectedly",
                checks=self._check_states(
                    attestation is not None, stopped_at="lwa", stopped_status="failed"
                ),
                observed_capabilities=(
                    ["external_attestation"] if attestation is not None else []
                ),
            )
            raise ExternalServiceError(
                "Amazon Ads capability check failed unexpectedly"
            )
        observed = list(result["observed_capabilities"])
        if attestation is None:
            return self._finish(
                principal,
                claimed,
                request_id,
                status="blocked",
                error_code="attestation_required",
                error_message="a safe attestation_reference is required",
                observed_capabilities=observed,
                checks=list(result["checks"])
                + [{
                    "name": "external_attestation",
                    "status": "blocked",
                }],
                request_ids=list(result["request_ids"]),
            )
        observed.append("external_attestation")
        if sorted(observed) != sorted(REQUIRED_CAPABILITIES):
            return self._finish(
                principal,
                claimed,
                request_id,
                status="blocked",
                error_code="capability_mismatch",
                error_message="required Amazon Ads read capabilities were not observed",
                observed_capabilities=observed,
                checks=list(result["checks"])
                + [{"name": "external_attestation", "status": "passed"}],
                request_ids=list(result["request_ids"]),
            )
        return self._finish(
            principal,
            claimed,
            request_id,
            status="passed",
            observed_capabilities=observed,
            checks=list(result["checks"])
            + [{"name": "external_attestation", "status": "passed"}],
            request_ids=list(result["request_ids"]),
        )

    def _finish(
        self,
        principal: Principal,
        gate: dict[str, Any],
        request_id: str,
        *,
        status: str,
        observed_capabilities: list[str] | None = None,
        checks: list[dict[str, Any]] | None = None,
        request_ids: list[str] | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
        retry_after_seconds: int | None = None,
    ) -> dict[str, Any]:
        finished = self.db.finish_ads_capability_gate(
            principal.tenant_id,
            str(gate["id"]),
            status=status,
            observed_capabilities=observed_capabilities or [],
            checks=checks or [],
            request_ids=request_ids or [],
            error_code=error_code,
            error_message=error_message,
            retry_after_seconds=retry_after_seconds,
        )
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "amazon_ads.capability_gate.check",
            "ads_capability_gate",
            str(gate["id"]),
            status,
            {
                "provider": "amazon_ads",
                "status": status,
                "error_code": error_code,
                "request_ids": request_ids or [],
            },
        )
        return self._safe(finished)
