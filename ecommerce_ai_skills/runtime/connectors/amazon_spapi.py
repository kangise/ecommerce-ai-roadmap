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

from ..errors import ExternalServiceError, MissingCredentialError, ValidationError


REGION_ENDPOINTS = {
    "na": "https://sellingpartnerapi-na.amazon.com",
    "eu": "https://sellingpartnerapi-eu.amazon.com",
    "fe": "https://sellingpartnerapi-fe.amazon.com",
}


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
        region = str(self.config.get("region", "")).lower().strip()
        endpoint = REGION_ENDPOINTS.get(region)
        if endpoint is None:
            raise ValidationError("Amazon SP-API region must be na, eu, or fe")
        marketplaces = self.config.get("marketplace_ids")
        if not isinstance(marketplaces, list) or not marketplaces or not all(
            isinstance(value, str) and re.fullmatch(r"[A-Z0-9]{5,20}", value)
            for value in marketplaces
        ):
            raise ValidationError("marketplace_ids must contain Amazon marketplace identifiers")
        return endpoint

    @staticmethod
    def _json(body: bytes, service: str) -> dict[str, Any]:
        try:
            value = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ExternalServiceError(f"{service} returned invalid JSON") from exc
        if not isinstance(value, dict):
            raise ExternalServiceError(f"{service} returned a non-object response")
        return value

    def _send(self, request: Request, service: str, *, max_bytes: int = 1_000_000) -> tuple[bytes, Any, str]:
        try:
            with self.transport(request, timeout=self.timeout_seconds) as response:
                status = getattr(response, "status", 200)
                body = response.read(max_bytes + 1)
                headers = getattr(response, "headers", {}) or {}
                final_url = response.geturl() if hasattr(response, "geturl") else request.full_url
        except HTTPError as exc:
            raise ExternalServiceError(f"{service} returned HTTP {exc.code}") from exc
        except URLError as exc:
            raise ExternalServiceError(f"{service} request failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise ExternalServiceError(f"{service} request timed out") from exc
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

    @staticmethod
    def _validate_id(value: str, label: str) -> str:
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{1,200}", value):
            raise ValidationError(f"{label} is invalid")
        return value

    @staticmethod
    def _validate_document_url(url: str) -> None:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        allowed = (
            host == "amazonaws.com"
            or host.endswith(".amazonaws.com")
            or host == "cloudfront.net"
            or host.endswith(".cloudfront.net")
            or host == "amazon.com"
            or host.endswith(".amazon.com")
        )
        if parsed.scheme != "https" or not allowed or parsed.username or parsed.password:
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
