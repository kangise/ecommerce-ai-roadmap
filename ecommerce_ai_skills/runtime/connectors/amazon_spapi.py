"""Read-only Amazon Selling Partner API Reports connector.

The connector exchanges an environment-referenced LWA refresh token for an
access token, retrieves one completed report and its document metadata, then
downloads the report bytes from Amazon's short-lived pre-signed URL. It does
not request reports, access restricted PII via RDT, or perform marketplace
writes.
"""

from __future__ import annotations

import gzip
import io
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

from ..errors import (
    ConnectorRateLimitError,
    ExternalServiceError,
    MissingCredentialError,
    ValidationError,
)


REGION_ENDPOINTS = {
    "na": "https://sellingpartnerapi-na.amazon.com",
    "eu": "https://sellingpartnerapi-eu.amazon.com",
    "fe": "https://sellingpartnerapi-fe.amazon.com",
}

# This is the supported Selling Partner API marketplace directory.  It is
# shared by account validation and the public runtime catalog so a marketplace
# cannot be accepted by one boundary and rejected by another.
AMAZON_MARKETPLACES = (
    {"id": "ATVPDKIKX0DER", "name": "United States", "country_code": "US", "region": "na"},
    {"id": "A2EUQ1WTGCTBG2", "name": "Canada", "country_code": "CA", "region": "na"},
    {"id": "A1AM78C64UM0Y8", "name": "Mexico", "country_code": "MX", "region": "na"},
    {"id": "A2Q3Y263D00KWC", "name": "Brazil", "country_code": "BR", "region": "na"},
    {"id": "A1F83G8C2ARO7P", "name": "United Kingdom", "country_code": "GB", "region": "eu"},
    {"id": "A1PA6795UKMFR9", "name": "Germany", "country_code": "DE", "region": "eu"},
    {"id": "A13V1IB3VIYZZH", "name": "France", "country_code": "FR", "region": "eu"},
    {"id": "APJ6JRA9NG5V4", "name": "Italy", "country_code": "IT", "region": "eu"},
    {"id": "A1RKKUPIHCS9HS", "name": "Spain", "country_code": "ES", "region": "eu"},
    {"id": "A1805IZSGTT6HS", "name": "Netherlands", "country_code": "NL", "region": "eu"},
    {"id": "A2NODRKZP88ZB9", "name": "Sweden", "country_code": "SE", "region": "eu"},
    {"id": "A1C3SOZRARQ6R3", "name": "Poland", "country_code": "PL", "region": "eu"},
    {"id": "AMEN7PMS3EDWL", "name": "Belgium", "country_code": "BE", "region": "eu"},
    {"id": "A33AVAJ2PDY3EV", "name": "Turkey", "country_code": "TR", "region": "eu"},
    {"id": "A21TJRUUN4KGV", "name": "India", "country_code": "IN", "region": "eu"},
    {"id": "A17E79C6D8DWNP", "name": "Saudi Arabia", "country_code": "SA", "region": "eu"},
    {"id": "A2VIGQ35RCS4UG", "name": "United Arab Emirates", "country_code": "AE", "region": "eu"},
    {"id": "ARBP9OOSHTCHU", "name": "Egypt", "country_code": "EG", "region": "eu"},
    {"id": "A1VC38T7YXB528", "name": "Japan", "country_code": "JP", "region": "fe"},
    {"id": "A39IBJ37TRP1C6", "name": "Australia", "country_code": "AU", "region": "fe"},
    {"id": "A19VAU5U5O7RUS", "name": "Singapore", "country_code": "SG", "region": "fe"},
)
AMAZON_MARKETPLACE_BY_ID = {item["id"]: item for item in AMAZON_MARKETPLACES}


def validate_amazon_marketplaces(region: Any, marketplace_ids: Any) -> tuple[str, list[str]]:
    normalized_region = str(region).lower().strip()
    if normalized_region not in REGION_ENDPOINTS:
        raise ValidationError("Amazon SP-API region must be na, eu, or fe")
    if not isinstance(marketplace_ids, list) or not 1 <= len(marketplace_ids) <= 20:
        raise ValidationError("marketplace_ids must contain between 1 and 20 marketplace identifiers")
    if not all(isinstance(value, str) for value in marketplace_ids):
        raise ValidationError("marketplace_ids must contain Amazon marketplace identifiers")
    if len(set(marketplace_ids)) != len(marketplace_ids):
        raise ValidationError("marketplace_ids must not contain duplicates")
    unknown = [value for value in marketplace_ids if value not in AMAZON_MARKETPLACE_BY_ID]
    if unknown:
        raise ValidationError(f"unknown Amazon marketplace_id: {unknown[0]}")
    mismatched = [
        value
        for value in marketplace_ids
        if AMAZON_MARKETPLACE_BY_ID[value]["region"] != normalized_region
    ]
    if mismatched:
        raise ValidationError(
            f"Amazon marketplace_id {mismatched[0]} does not belong to region {normalized_region}"
        )
    return normalized_region, list(marketplace_ids)


@dataclass(frozen=True)
class AmazonSPAPIReportsConnector:
    config: dict[str, Any]
    environ: Mapping[str, str] | None = None
    transport: Callable[..., Any] = urlopen
    timeout_seconds: int = 30
    max_document_bytes: int = 2_000_000

    def _environment(self) -> Mapping[str, str]:
        return self.environ if self.environ is not None else os.environ

    def _credential(self, key: str) -> str:
        ref = self.config.get(key)
        if not isinstance(ref, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{2,127}", ref):
            raise ValidationError(f"{key} must be an environment variable name")
        value = self._environment().get(ref, "")
        if not value:
            raise MissingCredentialError(f"credential environment variable {ref} is not set")
        return value

    def _endpoint(self) -> str:
        region, _ = validate_amazon_marketplaces(
            self.config.get("region"), self.config.get("marketplace_ids")
        )
        return REGION_ENDPOINTS[region]

    @staticmethod
    def _json(body: bytes, service: str) -> dict[str, Any]:
        try:
            value = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ExternalServiceError(f"{service} returned invalid JSON") from exc
        if not isinstance(value, dict):
            raise ExternalServiceError(f"{service} returned a non-object response")
        return value

    @staticmethod
    def _header_dict(headers: Any) -> dict[str, str]:
        if headers is None:
            return {}
        if hasattr(headers, "items"):
            return {str(key): str(value) for key, value in headers.items()}
        return {}

    @classmethod
    def _rate_limit_error(cls, service: str, headers: Any) -> ConnectorRateLimitError:
        normalized = cls._header_dict(headers)
        retry_value = next(
            (value for key, value in normalized.items() if key.lower() == "retry-after"),
            "60",
        )
        try:
            retry_after = int(str(retry_value).strip())
        except ValueError:
            retry_after = 60
        return ConnectorRateLimitError(
            f"{service} returned HTTP 429",
            retry_after=retry_after,
            headers=normalized,
        )

    def _send(self, request: Request, service: str, *, max_bytes: int = 1_000_000) -> tuple[bytes, Any, str]:
        try:
            with self.transport(request, timeout=self.timeout_seconds) as response:
                status = getattr(response, "status", 200)
                body = response.read(max_bytes + 1)
                headers = getattr(response, "headers", {}) or {}
                final_url = response.geturl() if hasattr(response, "geturl") else request.full_url
        except HTTPError as exc:
            if exc.code == 429:
                raise self._rate_limit_error(service, exc.headers) from exc
            raise ExternalServiceError(f"{service} returned HTTP {exc.code}") from exc
        except URLError as exc:
            raise ExternalServiceError(f"{service} request failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise ExternalServiceError(f"{service} request timed out") from exc
        if status == 429:
            raise self._rate_limit_error(service, headers)
        if status < 200 or status >= 300:
            raise ExternalServiceError(f"{service} returned HTTP {status}")
        if len(body) > max_bytes:
            raise ExternalServiceError(f"{service} response exceeded {max_bytes} bytes")
        return body, headers, final_url

    def _access_token(self) -> str:
        body = urlencode(
            {
                "grant_type": "refresh_token",
                "refresh_token": self._credential("lwa_refresh_token_ref"),
                "client_id": self._credential("lwa_client_id_ref"),
                "client_secret": self._credential("lwa_client_secret_ref"),
            }
        ).encode("utf-8")
        request = Request(
            "https://api.amazon.com/auth/o2/token",
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Accept": "application/json",
                "User-Agent": "ecommerce-ai-skills/1.2",
            },
            method="POST",
        )
        raw, _, _ = self._send(request, "Amazon LWA")
        result = self._json(raw, "Amazon LWA")
        token = result.get("access_token")
        if not isinstance(token, str) or not token:
            raise ExternalServiceError("Amazon LWA response did not contain access_token")
        return token

    def _spapi_json(self, path: str, access_token: str) -> dict[str, Any]:
        request = Request(
            self._endpoint() + path,
            headers={
                "x-amz-access-token": access_token,
                "Accept": "application/json",
                "User-Agent": "ecommerce-ai-skills/1.2",
            },
            method="GET",
        )
        raw, _, _ = self._send(request, "Amazon SP-API")
        response = self._json(raw, "Amazon SP-API")
        payload = response.get("payload", response)
        if not isinstance(payload, dict):
            raise ExternalServiceError("Amazon SP-API payload was not an object")
        return payload

    def create_report(
        self,
        report_type: str,
        marketplace_ids: list[str],
        data_start_time: str,
        data_end_time: str,
    ) -> dict[str, Any]:
        if not isinstance(report_type, str) or not re.fullmatch(r"GET_[A-Z0-9_]{1,120}", report_type):
            raise ValidationError("Amazon report_type is invalid")
        region = self.config.get("region")
        _, configured = validate_amazon_marketplaces(
            region, self.config.get("marketplace_ids")
        )
        _, requested = validate_amazon_marketplaces(region, marketplace_ids)
        if not set(requested).issubset(configured):
            raise ValidationError(
                "Amazon report marketplace_ids must be configured on the connector"
            )
        for value, label in (
            (data_start_time, "data_start_time"),
            (data_end_time, "data_end_time"),
        ):
            if not isinstance(value, str) or not value:
                raise ValidationError(f"{label} is required")
        payload = {
            "reportType": report_type,
            "marketplaceIds": requested,
            "dataStartTime": data_start_time,
            "dataEndTime": data_end_time,
        }
        if report_type == "GET_SALES_AND_TRAFFIC_REPORT":
            payload["reportOptions"] = {
                "dateGranularity": "DAY",
                "asinGranularity": "CHILD",
            }
        request = Request(
            self._endpoint() + "/reports/2021-06-30/reports",
            data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            headers={
                "x-amz-access-token": self._access_token(),
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "ecommerce-ai-skills/1.2",
            },
            method="POST",
        )
        raw, _, _ = self._send(request, "Amazon SP-API")
        response = self._json(raw, "Amazon SP-API")
        result = response.get("payload", response)
        if not isinstance(result, dict):
            raise ExternalServiceError("Amazon SP-API payload was not an object")
        report_id = result.get("reportId")
        if not isinstance(report_id, str) or not report_id:
            raise ExternalServiceError("Amazon SP-API response did not contain reportId")
        return {"report_id": self._validate_id(report_id, "reportId")}

    def get_report_status(self, report_id: str) -> dict[str, Any]:
        report_id = self._validate_id(report_id, "report_id")
        report = self._spapi_json(
            f"/reports/2021-06-30/reports/{quote(report_id, safe='')}",
            self._access_token(),
        )
        status = report.get("processingStatus")
        if not isinstance(status, str) or not status:
            raise ExternalServiceError(
                "Amazon SP-API report response did not contain processingStatus"
            )
        return {
            "report_id": report_id,
            "processing_status": status,
            "report_document_id": report.get("reportDocumentId"),
            "amazon_report_type": report.get("reportType"),
            "data_start_time": report.get("dataStartTime"),
            "data_end_time": report.get("dataEndTime"),
        }

    def health_check(self) -> dict[str, Any]:
        """Verify LWA credentials and configured marketplace authorization."""
        _, configured = validate_amazon_marketplaces(
            self.config.get("region"), self.config.get("marketplace_ids")
        )
        request = Request(
            self._endpoint() + "/sellers/v1/marketplaceParticipations",
            headers={
                "x-amz-access-token": self._access_token(),
                "Accept": "application/json",
                "User-Agent": "ecommerce-ai-skills/1.2",
            },
            method="GET",
        )
        raw, _, _ = self._send(request, "Amazon SP-API")
        response = self._json(raw, "Amazon SP-API")
        payload = response.get("payload", response)
        participations = (
            payload.get("marketplaceParticipations")
            if isinstance(payload, dict)
            else payload
        )
        if not isinstance(participations, list):
            raise ExternalServiceError(
                "Amazon SP-API response did not contain marketplaceParticipations[]"
            )
        authorized: set[str] = set()
        for participation in participations:
            if not isinstance(participation, dict):
                continue
            marketplace = participation.get("marketplace")
            marketplace_id = (
                marketplace.get("id") if isinstance(marketplace, dict) else None
            ) or participation.get("marketplaceId")
            if isinstance(marketplace_id, str):
                authorized.add(marketplace_id)
        missing = [value for value in configured if value not in authorized]
        if missing:
            raise ExternalServiceError(
                f"Amazon credentials are not authorized for configured marketplace: {missing[0]}"
            )
        return {"authorized_marketplace_ids": sorted(authorized)}

    @staticmethod
    def _validate_id(value: str, label: str) -> str:
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{1,200}", value):
            raise ValidationError(f"{label} is invalid")
        return value

    @staticmethod
    def _validate_document_url(url: str) -> None:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        try:
            port = parsed.port
        except ValueError as exc:
            raise ExternalServiceError(
                "Amazon report document URL failed host validation"
            ) from exc
        allowed = (
            host == "amazonaws.com"
            or host.endswith(".amazonaws.com")
            or host == "cloudfront.net"
            or host.endswith(".cloudfront.net")
            or host == "amazon.com"
            or host.endswith(".amazon.com")
        )
        if (
            parsed.scheme != "https"
            or port not in {None, 443}
            or not allowed
            or parsed.username
            or parsed.password
        ):
            raise ExternalServiceError("Amazon report document URL failed host validation")

    def _download_document(self, url: str, compression: str | None) -> bytes:
        self._validate_document_url(url)
        request = Request(
            url,
            headers={"Accept": "*/*", "User-Agent": "ecommerce-ai-skills/1.2"},
            method="GET",
        )
        raw, _, final_url = self._send(
            request, "Amazon report document", max_bytes=self.max_document_bytes
        )
        self._validate_document_url(final_url)
        if compression is None:
            return raw
        if compression != "GZIP":
            raise ExternalServiceError(f"unsupported Amazon report compression: {compression}")
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as archive:
                decompressed = archive.read(self.max_document_bytes + 1)
        except (OSError, EOFError) as exc:
            raise ExternalServiceError("Amazon report GZIP content was invalid") from exc
        if len(decompressed) > self.max_document_bytes:
            raise ExternalServiceError(
                f"Amazon report decompressed content exceeded {self.max_document_bytes} bytes"
            )
        return decompressed

    def retrieve_report(self, report_id: str) -> dict[str, Any]:
        report_id = self._validate_id(report_id, "report_id")
        access_token = self._access_token()
        report = self._spapi_json(
            f"/reports/2021-06-30/reports/{quote(report_id, safe='')}", access_token
        )
        status = report.get("processingStatus")
        if status != "DONE":
            raise ExternalServiceError(f"Amazon report is not downloadable: {status or 'unknown'}")
        document_id = report.get("reportDocumentId")
        if not isinstance(document_id, str):
            raise ExternalServiceError("Amazon completed report has no reportDocumentId")
        document_id = self._validate_id(document_id, "reportDocumentId")
        document = self._spapi_json(
            f"/reports/2021-06-30/documents/{quote(document_id, safe='')}", access_token
        )
        url = document.get("url")
        if not isinstance(url, str):
            raise ExternalServiceError("Amazon report document response has no URL")
        content = self._download_document(url, document.get("compressionAlgorithm"))
        observed_at = report.get("dataEndTime") or report.get("processingEndTime")
        if not isinstance(observed_at, str):
            raise ExternalServiceError("Amazon report response has no observation timestamp")
        report_type = report.get("reportType")
        if not isinstance(report_type, str) or not report_type:
            raise ExternalServiceError("Amazon report response has no reportType")
        return {
            "content": content,
            "report_id": report_id,
            "report_document_id": document_id,
            "amazon_report_type": report_type,
            "observed_at": observed_at,
            "compression": document.get("compressionAlgorithm"),
        }
