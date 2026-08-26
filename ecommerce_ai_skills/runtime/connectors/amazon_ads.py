"""Read-only Amazon Ads capability probe.

This boundary only verifies an Ads profile and sponsored-products campaign
read access.  Campaign response payloads are deliberately discarded.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ecommerce_ai_skills import USER_AGENT

from ..errors import (
    ConnectorRateLimitError,
    ExternalServiceError,
    MissingCredentialError,
    ValidationError,
)


ADS_REGION_ENDPOINTS = {
    "na": "https://advertising-api.amazon.com",
    "eu": "https://advertising-api-eu.amazon.com",
    "fe": "https://advertising-api-fe.amazon.com",
}
_REFERENCE_RE = re.compile(r"[A-Z][A-Z0-9_]{2,127}")
_PROFILE_RE = re.compile(r"[0-9]{1,32}")
_REQUEST_ID_HEADERS = {
    "x-amzn-requestid",
    "x-amzn-request-id",
    "x-amz-request-id",
    "x-amz-rid",
}


def validate_amazon_ads_config(region: Any, profile_id: Any) -> tuple[str, str]:
    normalized_region = str(region).strip().lower()
    normalized_profile = str(profile_id).strip()
    if normalized_region not in ADS_REGION_ENDPOINTS:
        raise ValidationError("Amazon Ads region must be na, eu, or fe")
    if not _PROFILE_RE.fullmatch(normalized_profile):
        raise ValidationError("Amazon Ads profile_id must be a numeric string")
    return normalized_region, normalized_profile


class AmazonAdsHTTPError(ExternalServiceError):
    """Safe, classified Amazon Ads HTTP failure without response payloads."""

    def __init__(self, status_code: int, request_ids: list[str], stage: str):
        super().__init__(f"Amazon Ads returned HTTP {status_code}")
        self.status_code = int(status_code)
        self.request_ids = list(request_ids)
        self.stage = stage


class AmazonAdsRateLimitError(ConnectorRateLimitError):
    def __init__(self, retry_after: int, request_ids: list[str], stage: str):
        super().__init__("Amazon Ads returned HTTP 429", retry_after=retry_after)
        self.request_ids = list(request_ids)
        self.stage = stage


class AmazonAdsServiceError(ExternalServiceError):
    def __init__(self, message: str, stage: str, request_ids: list[str] | None = None):
        super().__init__(message)
        self.stage = stage
        self.request_ids = list(request_ids or [])


@dataclass(frozen=True)
class AmazonAdsConnector:
    config: dict[str, Any]
    environ: Mapping[str, str] | None = None
    transport: Callable[..., Any] = urlopen
    timeout_seconds: int = 30
    max_response_bytes: int = 1_000_000

    def _environment(self) -> Mapping[str, str]:
        return self.environ if self.environ is not None else os.environ

    def _credential(self, key: str) -> str:
        ref = self.config.get(key)
        if not isinstance(ref, str) or not _REFERENCE_RE.fullmatch(ref):
            raise ValidationError(f"{key} must be an environment variable name")
        value = self._environment().get(ref, "")
        if not value:
            raise MissingCredentialError(
                f"credential environment variable {ref} is not set"
            )
        return value

    def _settings(self) -> tuple[str, str]:
        return validate_amazon_ads_config(
            self.config.get("region"), self.config.get("profile_id")
        )

    @staticmethod
    def _headers(value: Any) -> dict[str, str]:
        if hasattr(value, "items"):
            return {str(key): str(item) for key, item in value.items()}
        return {}

    @classmethod
    def _request_ids(cls, headers: Any) -> list[str]:
        values = []
        for key, value in cls._headers(headers).items():
            if key.lower() in _REQUEST_ID_HEADERS and value:
                values.append(value[:256])
        return sorted(set(values))[:8]

    @classmethod
    def _retry_after(cls, headers: Any) -> int:
        value = next(
            (
                item
                for key, item in cls._headers(headers).items()
                if key.lower() == "retry-after"
            ),
            "60",
        )
        try:
            return max(1, min(int(str(value).strip()), 3600))
        except ValueError:
            return 60

    def _send(self, request: Request, service: str) -> tuple[bytes, dict[str, str]]:
        try:
            with self.transport(request, timeout=self.timeout_seconds) as response:
                status = int(getattr(response, "status", 200))
                headers = self._headers(getattr(response, "headers", {}))
                body = response.read(self.max_response_bytes + 1)
        except HTTPError as exc:
            headers = self._headers(exc.headers)
            request_ids = self._request_ids(headers)
            if exc.code == 429:
                raise AmazonAdsRateLimitError(
                    self._retry_after(headers), request_ids, service
                ) from exc
            raise AmazonAdsHTTPError(exc.code, request_ids, service) from exc
        except URLError as exc:
            raise AmazonAdsServiceError(
                f"{service} request failed", service
            ) from exc
        except TimeoutError as exc:
            raise AmazonAdsServiceError(
                f"{service} request timed out", service
            ) from exc
        request_ids = self._request_ids(headers)
        if status == 429:
            raise AmazonAdsRateLimitError(
                self._retry_after(headers), request_ids, service
            )
        if status < 200 or status >= 300:
            raise AmazonAdsHTTPError(status, request_ids, service)
        if len(body) > self.max_response_bytes:
            raise AmazonAdsServiceError(
                f"{service} response exceeded {self.max_response_bytes} bytes",
                service,
                request_ids,
            )
        return body, headers

    @staticmethod
    def _json(
        body: bytes, service: str, request_ids: list[str] | None = None
    ) -> Any:
        try:
            return json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AmazonAdsServiceError(
                f"{service} returned invalid JSON", service, request_ids
            ) from exc

    def _access_token(self) -> str:
        request = Request(
            "https://api.amazon.com/auth/o2/token",
            data=urlencode(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": self._credential("lwa_refresh_token_ref"),
                    "client_id": self._credential("lwa_client_id_ref"),
                    "client_secret": self._credential("lwa_client_secret_ref"),
                }
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        raw, headers = self._send(request, "Amazon LWA")
        request_ids = self._request_ids(headers)
        value = self._json(raw, "Amazon LWA", request_ids)
        token = value.get("access_token") if isinstance(value, dict) else None
        if not isinstance(token, str) or not token:
            raise AmazonAdsServiceError(
                "Amazon LWA response did not contain access_token",
                "Amazon LWA",
                request_ids,
            )
        return token

    def list_profiles(
        self, access_token: str | None = None
    ) -> tuple[list[dict[str, str]], list[str]]:
        region, _ = self._settings()
        request = Request(
            ADS_REGION_ENDPOINTS[region] + "/v2/profiles",
            headers={
                "Amazon-Advertising-API-ClientId": self._credential(
                    "lwa_client_id_ref"
                ),
                "Authorization": f"Bearer {access_token or self._access_token()}",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
            method="GET",
        )
        raw, headers = self._send(request, "Amazon Ads profiles")
        request_ids = self._request_ids(headers)
        value = self._json(raw, "Amazon Ads profiles", request_ids)
        if not isinstance(value, list):
            raise AmazonAdsServiceError(
                "Amazon Ads profiles response was not a list",
                "Amazon Ads profiles",
                request_ids,
            )
        profiles: list[dict[str, str]] = []
        for item in value:
            if not isinstance(item, dict):
                continue
            profile_id = str(item.get("profileId", "")).strip()
            if _PROFILE_RE.fullmatch(profile_id):
                profiles.append({"profile_id": profile_id})
        return profiles, request_ids

    def check_campaign_read(self, access_token: str | None = None) -> list[str]:
        region, profile_id = self._settings()
        media_type = "application/vnd.spCampaign.v3+json"
        request = Request(
            ADS_REGION_ENDPOINTS[region] + "/sp/campaigns/list",
            data=b'{"maxResults":1}',
            headers={
                "Amazon-Advertising-API-ClientId": self._credential(
                    "lwa_client_id_ref"
                ),
                "Amazon-Advertising-API-Scope": profile_id,
                "Authorization": f"Bearer {access_token or self._access_token()}",
                "Accept": media_type,
                "Content-Type": media_type,
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        raw, headers = self._send(request, "Amazon Ads sponsored products")
        # Decode only to establish a valid API response. Never return or persist it.
        request_ids = self._request_ids(headers)
        if not isinstance(
            self._json(raw, "Amazon Ads sponsored products", request_ids), dict
        ):
            raise AmazonAdsServiceError(
                "Amazon Ads sponsored products response was not an object",
                "Amazon Ads sponsored products",
                request_ids,
            )
        return request_ids

    def probe(self) -> dict[str, Any]:
        _, profile_id = self._settings()
        access_token = self._access_token()
        profiles, profile_request_ids = self.list_profiles(access_token)
        if not profiles:
            error = ValidationError("Amazon Ads profiles response was empty")
            error.request_ids = profile_request_ids  # type: ignore[attr-defined]
            raise error
        if profile_id not in {item["profile_id"] for item in profiles}:
            error = ValidationError(
                "configured Amazon Ads profile_id was not authorized"
            )
            error.request_ids = profile_request_ids  # type: ignore[attr-defined]
            raise error
        try:
            campaign_request_ids = self.check_campaign_read(access_token)
        except (
            AmazonAdsHTTPError,
            AmazonAdsRateLimitError,
            AmazonAdsServiceError,
        ) as exc:
            exc.request_ids = sorted(
                set(profile_request_ids + exc.request_ids)
            )[:16]
            raise
        return {
            "observed_capabilities": [
                "lwa",
                "profiles_read",
                "campaigns_list_read",
            ],
            "checks": [
                {"name": "lwa", "status": "passed"},
                {"name": "profiles_read", "status": "passed"},
                {"name": "target_profile", "status": "passed"},
                {"name": "campaigns_list_read", "status": "passed"},
            ],
            "request_ids": sorted(
                set(profile_request_ids + campaign_request_ids)
            )[:16],
        }

    def health_check(self) -> dict[str, Any]:
        _, profile_id = self._settings()
        profiles, request_ids = self.list_profiles(self._access_token())
        if not profiles:
            raise ValidationError("Amazon Ads profiles response was empty")
        if profile_id not in {item["profile_id"] for item in profiles}:
            raise ValidationError("configured Amazon Ads profile_id was not authorized")
        return {
            "observed_capabilities": ["lwa", "profiles_read"],
            "request_ids": request_ids,
        }
