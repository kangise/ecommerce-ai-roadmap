"""Read-only Shopify Admin API connector.

Tokens are never accepted from or persisted in action payloads.  The account
configuration stores only an environment-variable reference; the value is
resolved at execution time so a database export does not contain credentials.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urlencode, urlparse
from urllib.request import Request, urlopen

from ecommerce_ai_skills import USER_AGENT

from ..errors import (
    ConnectorRateLimitError,
    ExternalServiceError,
    MissingCredentialError,
    ValidationError,
)


MAX_JSON_BYTES = 65_536


@dataclass(frozen=True)
class ShopifyConnector:
    config: dict[str, Any]
    environ: dict[str, str] | None = None
    transport: Callable[..., Any] = urlopen

    def _credential(self) -> str:
        ref = self.config.get("credential_ref")
        if not isinstance(ref, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{2,127}", ref):
            raise ValidationError("credential_ref must be an environment variable name")
        token = (self.environ if self.environ is not None else os.environ).get(ref, "")
        if not token:
            raise MissingCredentialError(f"credential environment variable {ref} is not set")
        return token

    def _url(self, limit: int, page_info: str | None) -> str:
        return self._admin_url("products.json", {"limit": str(max(1, min(limit, 250))), **({"page_info": page_info} if page_info else {})})

    def _admin_url(self, resource: str, params: dict[str, str] | None = None) -> str:
        domain = str(self.config.get("shop_domain", "")).lower().strip().rstrip("/")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*\.myshopify\.com", domain):
            raise ValidationError("shop_domain must be a canonical *.myshopify.com host")
        api_version = str(self.config.get("api_version", "")).strip()
        if not re.fullmatch(r"20\d{2}-\d{2}", api_version):
            raise ValidationError("api_version must be an explicit YYYY-MM version")
        query = f"?{urlencode(params)}" if params else ""
        return f"https://{domain}/admin/api/{api_version}/{resource}{query}"

    @staticmethod
    def _rate_limit(headers: Any) -> ConnectorRateLimitError:
        value = headers.get("Retry-After", "60") if hasattr(headers, "get") else "60"
        try:
            retry_after = int(str(value).strip())
        except ValueError:
            retry_after = 60
        return ConnectorRateLimitError(
            "Shopify returned HTTP 429",
            retry_after=retry_after,
            headers=dict(headers.items()) if hasattr(headers, "items") else {},
        )

    def _get_json_response(self, resource: str) -> tuple[dict[str, Any], Any]:
        request = Request(
            self._admin_url(resource),
            headers={"X-Shopify-Access-Token": self._credential(), "Accept": "application/json", "User-Agent": USER_AGENT},
            method="GET",
        )
        try:
            with self.transport(request, timeout=30) as response:
                status = getattr(response, "status", 200)
                headers = getattr(response, "headers", {}) or {}
                body = response.read(MAX_JSON_BYTES + 1)
        except HTTPError as exc:
            if exc.code == 429:
                raise self._rate_limit(exc.headers) from exc
            raise ExternalServiceError(f"Shopify returned HTTP {exc.code}") from exc
        except URLError as exc:
            raise ExternalServiceError(f"Shopify request failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise ExternalServiceError("Shopify request timed out") from exc
        if status == 429:
            raise self._rate_limit(headers)
        if status < 200 or status >= 300:
            raise ExternalServiceError(f"Shopify returned HTTP {status}")
        if len(body) > MAX_JSON_BYTES:
            raise ExternalServiceError(
                f"Shopify response exceeded {MAX_JSON_BYTES} bytes"
            )
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ExternalServiceError("Shopify returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ExternalServiceError("Shopify returned a non-object response")
        return payload, headers

    def _get_json(self, resource: str) -> dict[str, Any]:
        payload, _ = self._get_json_response(resource)
        return payload

    def health_check(self) -> dict[str, Any]:
        payload, headers = self._get_json_response("shop.json")
        shop = payload.get("shop")
        if not isinstance(shop, dict):
            raise ExternalServiceError("Shopify response did not contain shop")
        provider_request_id = None
        if hasattr(headers, "items"):
            provider_request_id = next(
                (
                    str(value)
                    for key, value in headers.items()
                    if str(key).lower() in {"x-request-id", "x-shopify-request-id"}
                    and re.fullmatch(r"[A-Za-z0-9._:-]{1,200}", str(value))
                ),
                None,
            )
        return {"shop_id": shop.get("id"), "provider_request_id": provider_request_id}

    def list_products(self, *, limit: int = 50, page_info: str | None = None) -> dict[str, Any]:
        token = self._credential()
        request = Request(
            self._url(limit, page_info),
            headers={"X-Shopify-Access-Token": token, "Accept": "application/json", "User-Agent": USER_AGENT},
            method="GET",
        )
        try:
            with self.transport(request, timeout=30) as response:
                status = getattr(response, "status", 200)
                headers = getattr(response, "headers", {}) or {}
                body = response.read()
        except HTTPError as exc:
            raise ExternalServiceError(f"Shopify returned HTTP {exc.code}") from exc
        except URLError as exc:
            raise ExternalServiceError(f"Shopify request failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise ExternalServiceError("Shopify request timed out") from exc
        if status < 200 or status >= 300:
            raise ExternalServiceError(f"Shopify returned HTTP {status}")
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ExternalServiceError("Shopify returned invalid JSON") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("products"), list):
            raise ExternalServiceError("Shopify response did not contain products[]")
        return {"products": payload["products"], "next_page_info": self._next_page_info(headers)}

    @staticmethod
    def _next_page_info(headers: Any) -> str | None:
        link = headers.get("Link", "") if hasattr(headers, "get") else ""
        for entry in str(link).split(","):
            if 'rel="next"' not in entry:
                continue
            match = re.search(r"<([^>]+)>", entry)
            if not match:
                continue
            query = parse_qs(urlparse(unquote(match.group(1))).query)
            values = query.get("page_info")
            if values:
                return values[0]
        return None
