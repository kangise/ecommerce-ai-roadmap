"""Tenant-safe marketplace connector account lifecycle."""

from __future__ import annotations

import os
import re
from typing import Any, Callable, Mapping
from urllib.request import urlopen

from .auth import AuthService
from .connectors.amazon_spapi import (
    AMAZON_MARKETPLACES,
    AmazonSPAPIReportsConnector,
    validate_amazon_marketplaces,
)
from .connectors.amazon_ads import AmazonAdsConnector, validate_amazon_ads_config
from .connectors.shopify import ShopifyConnector
from .errors import (
    ConnectorError,
    ConnectorRateLimitError,
    MissingCredentialError,
    ValidationError,
)
from .storage import Database, Principal


PROVIDER_CATALOG = (
    {
        "id": "amazon_spapi",
        "name": "Amazon Selling Partner API",
        "detail_fields": ["region", "marketplace_ids"],
        "credential_fields": [
            "lwa_client_id_ref",
            "lwa_client_secret_ref",
            "lwa_refresh_token_ref",
        ],
    },
    {
        "id": "amazon_ads",
        "name": "Amazon Ads API",
        "detail_fields": ["region", "profile_id"],
        "credential_fields": [
            "lwa_client_id_ref",
            "lwa_client_secret_ref",
            "lwa_refresh_token_ref",
        ],
    },
    {
        "id": "shopify",
        "name": "Shopify Admin API",
        "detail_fields": ["shop_domain", "api_version"],
        "credential_fields": ["credential_ref"],
    },
)

_PROVIDER_FIELDS = {
    "amazon_spapi": {
        "details": {"region", "marketplace_ids"},
        "credentials": {
            "lwa_client_id_ref",
            "lwa_client_secret_ref",
            "lwa_refresh_token_ref",
        },
    },
    "amazon_ads": {
        "details": {"region", "profile_id"},
        "credentials": {
            "lwa_client_id_ref",
            "lwa_client_secret_ref",
            "lwa_refresh_token_ref",
        },
    },
    "shopify": {
        "details": {"shop_domain", "api_version"},
        "credentials": {"credential_ref"},
    },
}
_SECRET_FIELDS = {
    "access_token",
    "refresh_token",
    "client_secret",
    "token",
    "password",
    "api_key",
    "secret",
}
_REFERENCE_RE = re.compile(r"[A-Z][A-Z0-9_]{2,127}")
_EXTERNAL_ACCOUNT_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:@/-]{0,199}")


class MarketplaceAccountService:
    """Account management, authorization, redaction, and live health checks."""

    def __init__(
        self,
        db: Database,
        auth: AuthService,
        *,
        environ: Mapping[str, str] | None = None,
        transport: Callable[..., Any] = urlopen,
        amazon_transport: Callable[..., Any] | None = None,
        shopify_transport: Callable[..., Any] | None = None,
    ):
        self.db = db
        self.auth = auth
        self.environ = environ if environ is not None else os.environ
        self.amazon_transport = amazon_transport or transport
        self.shopify_transport = shopify_transport or transport

    @staticmethod
    def catalog() -> dict[str, Any]:
        return {
            "connector_providers": [dict(item) for item in PROVIDER_CATALOG],
            "amazon_marketplaces": [dict(item) for item in AMAZON_MARKETPLACES],
        }

    @staticmethod
    def _external_account_id(value: Any) -> str:
        normalized = str(value).strip()
        if not _EXTERNAL_ACCOUNT_RE.fullmatch(normalized):
            raise ValidationError("external_account_id is invalid")
        return normalized

    @staticmethod
    def _config(provider: Any, value: Any) -> tuple[str, dict[str, Any]]:
        normalized_provider = str(provider).strip().lower()
        fields = _PROVIDER_FIELDS.get(normalized_provider)
        if fields is None:
            raise ValidationError("unsupported connector provider")
        if not isinstance(value, dict):
            raise ValidationError("config must be an object")
        lowered = {str(key).lower() for key in value}
        if lowered & _SECRET_FIELDS:
            raise ValidationError(
                "connector config cannot contain secret values; store environment references only"
            )
        required = fields["details"] | fields["credentials"]
        extra = sorted(set(value) - required)
        missing = sorted(required - set(value))
        if missing:
            raise ValidationError(f"missing connector config fields: {', '.join(missing)}")
        if extra:
            raise ValidationError(f"unknown connector config fields: {', '.join(extra)}")
        if any(
            not isinstance(value[key], str) or not _REFERENCE_RE.fullmatch(value[key])
            for key in fields["credentials"]
        ):
            raise ValidationError(
                "connector credential references must be environment variable names"
            )
        config = dict(value)
        if normalized_provider == "amazon_spapi":
            region, marketplace_ids = validate_amazon_marketplaces(
                config["region"], config["marketplace_ids"]
            )
            config["region"] = region
            config["marketplace_ids"] = marketplace_ids
        elif normalized_provider == "amazon_ads":
            region, profile_id = validate_amazon_ads_config(
                config["region"], config["profile_id"]
            )
            config["region"] = region
            config["profile_id"] = profile_id
        else:
            domain = str(config["shop_domain"]).lower().strip().rstrip("/")
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*\.myshopify\.com", domain):
                raise ValidationError(
                    "shop_domain must be a canonical *.myshopify.com host"
                )
            api_version = str(config["api_version"]).strip()
            if not re.fullmatch(r"20\d{2}-\d{2}", api_version):
                raise ValidationError("api_version must be an explicit YYYY-MM version")
            config["shop_domain"] = domain
            config["api_version"] = api_version
        return normalized_provider, config

    @staticmethod
    def _safe(account: dict[str, Any]) -> dict[str, Any]:
        config = account["config"]
        fields = _PROVIDER_FIELDS[account["provider"]]
        return {
            "id": account["id"],
            "tenant_id": account["tenant_id"],
            "provider": account["provider"],
            "external_account_id": account["external_account_id"],
            "provider_details": {
                key: config[key] for key in sorted(fields["details"])
            },
            "credential_refs": {
                key: "present" for key in sorted(fields["credentials"])
            },
            "health_status": account["health_status"],
            "health_checked_at": account["health_checked_at"],
            "health_error_code": account["health_error_code"],
            "health_error_message": account["health_error_message"],
            "created_at": account["created_at"],
            "updated_at": account["updated_at"],
        }

    def list(self, principal: Principal) -> list[dict[str, Any]]:
        self.auth.require(principal, "viewer")
        return [
            self._safe(account)
            for account in self.db.list_connector_accounts(principal.tenant_id)
        ]

    def get(self, principal: Principal, account_id: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        return self._safe(
            self.db.get_connector_account(principal.tenant_id, account_id)
        )

    def create(
        self,
        principal: Principal,
        provider: Any,
        external_account_id: Any,
        config: Any,
        request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "admin")
        provider, config = self._config(provider, config)
        account = self.db.create_connector_account(
            principal.tenant_id,
            provider,
            self._external_account_id(external_account_id),
            config,
        )
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "marketplace_account.create",
            "connector_account",
            account["id"],
            "succeeded",
            {"provider": provider},
        )
        return self._safe(account)

    def update(
        self,
        principal: Principal,
        account_id: str,
        external_account_id: Any,
        config: Any,
        request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "admin")
        existing = self.db.get_connector_account(principal.tenant_id, account_id)
        provider, config = self._config(existing["provider"], config)
        account = self.db.update_connector_account(
            principal.tenant_id,
            account_id,
            external_account_id=self._external_account_id(external_account_id),
            config=config,
        )
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "marketplace_account.update",
            "connector_account",
            account_id,
            "succeeded",
            {"provider": provider},
        )
        return self._safe(account)

    def _health_connector(self, account: dict[str, Any]) -> Any:
        config = account["config"]
        if account["provider"] == "amazon_spapi":
            return AmazonSPAPIReportsConnector(
                config,
                environ=self.environ,
                transport=self.amazon_transport,
            )
        if account["provider"] == "amazon_ads":
            return AmazonAdsConnector(
                config,
                environ=self.environ,
                transport=self.amazon_transport,
            )
        if account["provider"] == "shopify":
            return ShopifyConnector(
                config,
                environ=self.environ,  # type: ignore[arg-type]
                transport=self.shopify_transport,
            )
        # Defensive handling for data created by an earlier release.
        raise ValidationError("unsupported connector provider")

    def health_probe(
        self,
        principal: Principal,
        account_id: str,
    ) -> dict[str, Any]:
        """Run the account's real health adapter and expose safe probe metadata."""
        self.auth.require(principal, "operator")
        account = self.db.get_connector_account(principal.tenant_id, account_id)
        connector = self._health_connector(account)
        status = "healthy"
        error_code = None
        error_message = None
        provider_request_id = None
        retry_after_seconds = None
        try:
            result = connector.health_check()
            candidate = result.get("provider_request_id") if isinstance(result, dict) else None
            if isinstance(candidate, str) and re.fullmatch(
                r"[A-Za-z0-9._:-]{1,200}", candidate
            ):
                provider_request_id = candidate
        except MissingCredentialError:
            status = "misconfigured"
            error_code = "missing_credential"
            error_message = "required credential is not configured"
        except ValidationError as exc:
            status = "misconfigured"
            error_code = "invalid_configuration"
            error_message = str(exc)
        except ConnectorRateLimitError as exc:
            status = "unhealthy"
            error_code = "rate_limited"
            error_message = "provider rate limit is active"
            retry_after_seconds = exc.retry_after
        except ConnectorError as exc:
            status = "unhealthy"
            error_code = "external_service_error"
            error_message = str(exc)
        account = self.db.set_connector_account_health(
            principal.tenant_id,
            account_id,
            status,
            error_code=error_code,
            error_message=error_message,
        )
        return {
            "account": self._safe(account),
            "provider_request_id": provider_request_id,
            "provider_status": status,
            "error_code": error_code,
            "retry_after_seconds": retry_after_seconds,
        }

    def health_check(
        self, principal: Principal, account_id: str, request_id: str
    ) -> dict[str, Any]:
        result = self.health_probe(principal, account_id)
        account = result["account"]
        # The outcome records that the diagnostic completed; the external
        # connectivity result remains explicit in health_status metadata.
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "marketplace_account.health_check",
            "connector_account",
            account_id,
            "succeeded",
            {"provider": account["provider"], "health_status": account["health_status"]},
        )
        return account
