"""Tenant-owned, audited live connectivity checks for external providers."""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from typing import Any

from .accounts import MarketplaceAccountService
from .agents import OpenAIResponsesProvider
from .auth import AuthService
from .errors import (
    ConnectorError,
    ConnectorNotConfiguredError,
    MissingCredentialError,
    ValidationError,
)
from .storage import Database, Principal


log = logging.getLogger("ecommerce_ai_skills.provider_smoke")


class ProviderSmokeService:
    """Execute explicit provider probes without persisting credentials or bodies."""

    PROVIDERS = {"openai", "amazon_spapi", "shopify"}
    CONNECTOR_PROVIDERS = {"amazon_spapi", "shopify"}
    _SAFE_TOKEN = re.compile(r"[A-Za-z0-9._:-]{1,200}")
    _IDEMPOTENCY_KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,199}")

    def __init__(
        self,
        db: Database,
        auth: AuthService,
        accounts: MarketplaceAccountService,
        *,
        openai_provider: OpenAIResponsesProvider | None = None,
    ):
        self.db = db
        self.auth = auth
        self.accounts = accounts
        self.openai_provider = openai_provider or OpenAIResponsesProvider()

    @classmethod
    def _request(
        cls, provider: Any, connector_account_id: Any
    ) -> tuple[str, str | None]:
        if not isinstance(provider, str) or provider not in cls.PROVIDERS:
            raise ValidationError(
                "provider must be openai, amazon_spapi, or shopify"
            )
        if provider == "openai":
            if connector_account_id is not None:
                raise ValidationError(
                    "connector_account_id must not be supplied for openai"
                )
            return provider, None
        if (
            not isinstance(connector_account_id, str)
            or not connector_account_id.strip()
            or len(connector_account_id) > 200
        ):
            raise ValidationError(
                "connector_account_id is required for marketplace providers"
            )
        return provider, connector_account_id.strip()

    @classmethod
    def _idempotency_key(cls, value: Any) -> str:
        if not isinstance(value, str) or not cls._IDEMPOTENCY_KEY.fullmatch(value):
            raise ValidationError(
                "Idempotency-Key must contain 1 to 200 safe identifier characters"
            )
        return value

    @staticmethod
    def _fingerprint(provider: str, connector_account_id: str | None) -> str:
        payload = json.dumps(
            {
                "provider": provider,
                "connector_account_id": connector_account_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def _safe_token(cls, value: Any, fallback: str) -> str:
        normalized = str(value or "").strip()
        return normalized if cls._SAFE_TOKEN.fullmatch(normalized) else fallback

    @classmethod
    def _safe_request_id(cls, value: Any) -> str | None:
        normalized = str(value or "").strip()
        return normalized if cls._SAFE_TOKEN.fullmatch(normalized) else None

    @staticmethod
    def _safe(record: dict[str, Any]) -> dict[str, Any]:
        return {
            key: record[key]
            for key in (
                "id",
                "tenant_id",
                "provider",
                "connector_account_id",
                "created_by",
                "status",
                "provider_request_id",
                "provider_status",
                "http_status",
                "retry_after_seconds",
                "latency_ms",
                "error_code",
                "created_at",
                "completed_at",
            )
        }

    def list(self, principal: Principal, limit: int = 100) -> list[dict[str, Any]]:
        self.auth.require(principal, "viewer")
        return [
            self._safe(item)
            for item in self.db.list_provider_smoke_tests(principal.tenant_id, limit)
        ]

    def get(self, principal: Principal, smoke_test_id: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        return self._safe(
            self.db.get_provider_smoke_test(principal.tenant_id, smoke_test_id)
        )

    def _openai_result(self) -> tuple[str, dict[str, Any]]:
        result = self.openai_provider.smoke_check()
        if not isinstance(result, dict):
            raise TypeError("OpenAI smoke adapter returned a non-object")
        if result.get("ok") is True:
            status = "succeeded"
            error_code = None
        elif result.get("blocked") is True:
            status = "blocked"
            error_code = self._safe_token(
                result.get("error_code"), "provider_blocked"
            )
        else:
            status = "failed"
            error_code = self._safe_token(
                result.get("error_code"), "provider_request_failed"
            )
        http_status = result.get("http_status")
        if not isinstance(http_status, int) or isinstance(http_status, bool):
            http_status = None
        retry_after_seconds = result.get("retry_after_seconds")
        if (
            not isinstance(retry_after_seconds, int)
            or isinstance(retry_after_seconds, bool)
            or not 1 <= retry_after_seconds <= 3600
        ):
            retry_after_seconds = None
        return status, {
            "provider_request_id": self._safe_request_id(
                result.get("provider_request_id")
            ),
            "provider_status": self._safe_token(
                result.get("provider_status"), "unknown"
            ),
            "http_status": http_status,
            "retry_after_seconds": retry_after_seconds,
            "error_code": error_code,
        }

    def _marketplace_result(
        self, principal: Principal, connector_account_id: str
    ) -> tuple[str, dict[str, Any]]:
        result = self.accounts.health_probe(principal, connector_account_id)
        provider_status = result["provider_status"]
        if provider_status == "healthy":
            status, error_code = "succeeded", None
        elif provider_status == "misconfigured":
            status = "blocked"
            error_code = self._safe_token(
                result.get("error_code"), "missing_credential"
            )
        else:
            status = "failed"
            error_code = self._safe_token(
                result.get("error_code"), "external_service_error"
            )
        return status, {
            "provider_request_id": self._safe_request_id(
                result.get("provider_request_id")
            ),
            "provider_status": provider_status,
            "http_status": None,
            "retry_after_seconds": result.get("retry_after_seconds"),
            "error_code": error_code,
        }

    def execute(
        self,
        principal: Principal,
        *,
        provider: Any,
        connector_account_id: Any = None,
        idempotency_key: Any,
        request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        provider, connector_account_id = self._request(
            provider, connector_account_id
        )
        key = self._idempotency_key(idempotency_key)

        # Resolve through the caller's tenant before reserving the operation.
        # A cross-tenant identifier therefore remains indistinguishable from
        # an unknown connector and cannot create an orphan smoke record.
        if connector_account_id is not None:
            account = self.db.get_connector_account(
                principal.tenant_id, connector_account_id
            )
            if account["provider"] != provider:
                raise ValidationError(
                    "connector_account_id does not match the requested provider"
                )

        record, replay, lease_token = self.db.reserve_provider_smoke_test(
            principal.tenant_id,
            principal.user_id,
            provider,
            connector_account_id,
            key,
            self._fingerprint(provider, connector_account_id),
        )
        if replay:
            return self._safe(record)
        if lease_token is None:
            raise RuntimeError("provider smoke reservation did not return a lease token")

        started = time.monotonic()
        status = "failed"
        result: dict[str, Any]
        try:
            if provider == "openai":
                status, result = self._openai_result()
            else:
                status, result = self._marketplace_result(
                    principal, connector_account_id or ""
                )
        except MissingCredentialError:
            status = "blocked"
            result = {
                "provider_request_id": None,
                "provider_status": "misconfigured",
                "http_status": None,
                "retry_after_seconds": None,
                "error_code": "missing_credential",
            }
        except ConnectorNotConfiguredError:
            status = "blocked"
            result = {
                "provider_request_id": None,
                "provider_status": "misconfigured",
                "http_status": None,
                "retry_after_seconds": None,
                "error_code": "missing_configuration",
            }
        except ValidationError:
            status = "blocked"
            result = {
                "provider_request_id": None,
                "provider_status": "misconfigured",
                "http_status": None,
                "retry_after_seconds": None,
                "error_code": "invalid_configuration",
            }
        except ConnectorError:
            status = "failed"
            result = {
                "provider_request_id": None,
                "provider_status": "external_error",
                "http_status": None,
                "retry_after_seconds": None,
                "error_code": "external_service_error",
            }
        except Exception as exc:
            # Record a safe terminal fact so an unexpected adapter defect does
            # not strand the idempotency key.  The exception text is excluded
            # from logs and persistence because a transport can include secrets.
            log.error(
                "provider_smoke_unexpected_failure request_id=%s provider=%s type=%s",
                request_id,
                provider,
                type(exc).__name__,
            )
            status = "failed"
            result = {
                "provider_request_id": None,
                "provider_status": "internal_error",
                "http_status": None,
                "retry_after_seconds": None,
                "error_code": "internal_probe_error",
            }
        latency_ms = max(0, int((time.monotonic() - started) * 1000))
        completed = self.db.complete_provider_smoke_test(
            principal.tenant_id,
            record["id"],
            lease_token=lease_token,
            actor_user_id=principal.user_id,
            request_id=request_id,
            status=status,
            provider_request_id=result["provider_request_id"],
            provider_status=result["provider_status"],
            http_status=result["http_status"],
            retry_after_seconds=result.get("retry_after_seconds"),
            latency_ms=latency_ms,
            error_code=result["error_code"],
        )
        return self._safe(completed)
