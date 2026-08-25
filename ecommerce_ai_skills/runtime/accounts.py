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
from .connectors.shopify import ShopifyConnector
from .errors import ConnectorError, MissingCredentialError, ValidationError
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

    def health_check(
        self, principal: Principal, account_id: str, request_id: str
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        account = self.db.get_connector_account(principal.tenant_id, account_id)
        config = account["config"]
        if account["provider"] == "amazon_spapi":
            connector = AmazonSPAPIReportsConnector(
                config,
                environ=self.environ,
                transport=self.amazon_transport,
            )
        elif account["provider"] == "shopify":
            connector = ShopifyConnector(
                config,
                environ=self.environ,  # type: ignore[arg-type]
                transport=self.shopify_transport,
            )
        else:  # Defensive handling for data created by an earlier release.
            raise ValidationError("unsupported connector provider")
        status = "healthy"
        error_code = None
        error_message = None
        try:
            connector.health_check()
        except MissingCredentialError:
            status = "misconfigured"
            error_code = "missing_credential"
            error_message = "required credential is not configured"
        except ValidationError as exc:
            status = "misconfigured"
            error_code = "invalid_configuration"
            error_message = str(exc)
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
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "marketplace_account.health_check",
            "connector_account",
            account_id,
            "succeeded",
            {"provider": account["provider"], "health_status": status},
        )
        return self._safe(account)
