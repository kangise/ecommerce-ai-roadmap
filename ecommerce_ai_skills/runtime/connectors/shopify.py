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

from ..errors import ExternalServiceError, MissingCredentialError, ValidationError


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
        domain = str(self.config.get("shop_domain", "")).lower().strip().rstrip("/")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*\.myshopify\.com", domain):
            raise ValidationError("shop_domain must be a canonical *.myshopify.com host")
        api_version = str(self.config.get("api_version", "")).strip()
        if not re.fullmatch(r"20\d{2}-\d{2}", api_version):
            raise ValidationError("api_version must be an explicit YYYY-MM version")
        params: dict[str, str] = {"limit": str(max(1, min(limit, 250)))}
        if page_info:
            params["page_info"] = page_info
        return f"https://{domain}/admin/api/{api_version}/products.json?{urlencode(params)}"

    def list_products(self, *, limit: int = 50, page_info: str | None = None) -> dict[str, Any]:
        token = self._credential()
        request = Request(
            self._url(limit, page_info),
            headers={"X-Shopify-Access-Token": token, "Accept": "application/json", "User-Agent": "ecommerce-ai-skills/1.2"},
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
