"""Durable Amazon report synchronization state machine."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Mapping
from urllib.request import urlopen

from .auth import AuthService
from .connectors.amazon_spapi import AmazonSPAPIReportsConnector
from .errors import (
    ConnectorError,
    ConnectorRateLimitError,
    ExternalServiceError,
    MissingCredentialError,
    ValidationError,
)
from .evidence import EvidenceImportService
from .report_recipes import REPORT_RECIPE_CATALOG
from .storage import Database, Principal


class ReportSyncService:
    """Enqueue and execute retry-safe report imports one transition at a time."""

    MAX_ATTEMPTS = 12
    POLL_BACKOFF_MIN = 15
    POLL_BACKOFF_MAX = 900

    def __init__(
        self,
        db: Database,
        auth: AuthService,
        evidence_imports: EvidenceImportService,
        *,
        environ: Mapping[str, str] | None = None,
        transport: Callable[..., Any] = urlopen,
        clock: Callable[[], datetime] | None = None,
    ):
        self.db = db
        self.auth = auth
        self.evidence_imports = evidence_imports
        self.environ = environ if environ is not None else os.environ
        self.transport = transport
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    @staticmethod
    def _utc_iso(value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        )

    def _safe(self, sync: dict[str, Any]) -> dict[str, Any]:
        recipe = self.db.get_report_recipe(sync["tenant_id"], sync["recipe_id"])
        report_types = REPORT_RECIPE_CATALOG[recipe["recipe_key"]]
        return {
            "id": sync["id"],
            "tenant_id": sync["tenant_id"],
            "recipe_id": sync["recipe_id"],
            "connector_account_id": sync["connector_account_id"],
            "created_by": sync["created_by"],
            "amazon_report_id": sync["amazon_report_id"],
            "status": sync["status"],
            "processing_status": sync["processing_status"],
            "period_start": sync["period_start"],
            "period_end": sync["period_end"],
            "available_at": sync["available_at"],
            "lease_until": sync["lease_until"],
            "attempt_count": sync["attempt_count"],
            "max_attempts": sync["max_attempts"],
            "evidence_import_id": sync["evidence_import_id"],
            "error_code": sync["error_code"],
            "error_message": sync["error_message"],
            "recipe_key": recipe["recipe_key"],
            "amazon_report_type": report_types["amazon_report_type"],
            "evidence_report_type": report_types["evidence_report_type"],
            "created_at": sync["created_at"],
            "updated_at": sync["updated_at"],
            "completed_at": sync["completed_at"],
        }

    def list(self, principal: Principal, limit: int = 100) -> list[dict[str, Any]]:
        self.auth.require(principal, "viewer")
        return [
            self._safe(sync)
            for sync in self.db.list_report_syncs(principal.tenant_id, limit)
        ]

    def get(self, principal: Principal, sync_id: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        return self._safe(self.db.get_report_sync(principal.tenant_id, sync_id))

    def enqueue(
        self,
        principal: Principal,
        recipe_id: str,
        idempotency_key: str,
        request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        recipe = self.db.get_report_recipe(principal.tenant_id, recipe_id)
        if not recipe["enabled"]:
            raise ValidationError("report recipe is disabled")
        account = self.db.get_connector_account(
            principal.tenant_id, recipe["connector_account_id"]
        )
        if account["provider"] != "amazon_spapi":
            raise ValidationError("report sync requires an amazon_spapi connector account")
        if account["health_status"] != "healthy":
            raise ValidationError(
                "amazon_spapi connector account must be healthy before report sync"
            )
        now = self.clock()
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValidationError("report sync clock must be timezone-aware")
        period_end = now.astimezone(timezone.utc)
        period_start = period_end - timedelta(days=recipe["lookback_days"])
        sync, replayed = self.db.create_report_sync(
            principal.tenant_id,
            principal.user_id,
            recipe_id,
            idempotency_key,
            period_start=self._utc_iso(period_start),
            period_end=self._utc_iso(period_end),
            max_attempts=self.MAX_ATTEMPTS,
        )
        self.db.append_audit(
            principal.tenant_id,
            principal.user_id,
            request_id,
            "marketplace_report_sync.enqueue",
            "report_sync",
            sync["id"],
            "replayed" if replayed else "accepted",
            {"recipe_id": recipe_id},
        )
        return self._safe(sync)

    @classmethod
    def _backoff(cls, attempt_count: int) -> int:
        return min(
            cls.POLL_BACKOFF_MIN * (2 ** max(0, attempt_count - 1)),
            cls.POLL_BACKOFF_MAX,
        )

    def _connector(self, config: dict[str, Any]) -> AmazonSPAPIReportsConnector:
        return AmazonSPAPIReportsConnector(
            config,
            environ=self.environ,
            transport=self.transport,
        )

    def _audit_terminal(self, sync: dict[str, Any]) -> None:
        self.db.append_audit(
            sync["tenant_id"],
            sync["created_by"],
            f"report-sync:{sync['id']}:attempt:{sync['attempt_count']}",
            "marketplace_report_sync.succeeded"
            if sync["status"] == "succeeded"
            else "marketplace_report_sync.failed",
            "report_sync",
            sync["id"],
            sync["status"],
            {
                "processing_status": sync["processing_status"],
                "error_code": sync["error_code"],
                "evidence_import_id": sync["evidence_import_id"],
            },
        )

    def _reschedule(
        self,
        sync: dict[str, Any],
        *,
        delay_seconds: int,
        processing_status: str | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> dict[str, Any]:
        updated = self.db.reschedule_report_sync(
            sync["tenant_id"],
            sync["id"],
            delay_seconds=delay_seconds,
            processing_status=processing_status,
            error_code=error_code,
            error_message=error_message,
        )
        if updated["status"] == "failed":
            self._audit_terminal(updated)
        return self._safe(updated)

    def _fail(
        self,
        sync: dict[str, Any],
        code: str,
        message: str,
        *,
        processing_status: str | None = None,
    ) -> dict[str, Any]:
        failed = self.db.fail_report_sync(
            sync["tenant_id"],
            sync["id"],
            error_code=code,
            error_message=message,
            processing_status=processing_status,
        )
        self._audit_terminal(failed)
        return self._safe(failed)

    def _import_done(
        self,
        sync: dict[str, Any],
        recipe: dict[str, Any],
        retrieved: dict[str, Any],
    ) -> dict[str, Any]:
        report_types = REPORT_RECIPE_CATALOG[recipe["recipe_key"]]
        expected_type = report_types["amazon_report_type"]
        if retrieved["amazon_report_type"] != expected_type:
            raise ValidationError(
                "Amazon returned a different report type than the persisted recipe"
            )
        principal = self.db.principal_for_user(sync["tenant_id"], sync["created_by"])
        common = {
            "principal": principal,
            "raw": retrieved["content"],
            "observed_at": retrieved["observed_at"],
            "idempotency_key": f"report-sync:{sync['id']}:evidence",
            "request_id": f"report-sync:{sync['id']}:evidence",
        }
        filename_id = str(sync["amazon_report_id"])[:120]
        if recipe["recipe_key"] == "sales_traffic_daily":
            imported = self.evidence_imports.import_amazon_sales_traffic_json(
                filename=f"amazon-sales-traffic-{filename_id}.json",
                **common,
            )
        else:
            imported = self.evidence_imports.import_csv(
                platform="amazon",
                report_type=report_types["evidence_report_type"],
                filename=f"amazon-{recipe['recipe_key']}-{filename_id}.txt",
                media_type="text/tab-separated-values",
                **common,
            )
        completed = self.db.complete_report_sync(
            sync["tenant_id"], sync["id"], str(imported["id"])
        )
        self._audit_terminal(completed)
        return self._safe(completed)

    def run_once(self) -> dict[str, Any] | None:
        sync = self.db.claim_report_sync()
        if sync is None:
            return None
        try:
            recipe = self.db.get_report_recipe(sync["tenant_id"], sync["recipe_id"])
            account = self.db.get_connector_account(
                sync["tenant_id"], sync["connector_account_id"]
            )
            connector = self._connector(account["config"])
            report_types = REPORT_RECIPE_CATALOG[recipe["recipe_key"]]
            if sync["amazon_report_id"] is None:
                created = connector.create_report(
                    report_types["amazon_report_type"],
                    recipe["marketplace_ids"],
                    sync["period_start"],
                    sync["period_end"],
                )
                updated = self.db.mark_report_sync_polling(
                    sync["tenant_id"],
                    sync["id"],
                    created["report_id"],
                    delay_seconds=self._backoff(sync["attempt_count"]),
                )
                return self._safe(updated)
            status = connector.get_report_status(sync["amazon_report_id"])
            processing_status = status["processing_status"]
            if processing_status in {"IN_QUEUE", "IN_PROGRESS"}:
                return self._reschedule(
                    sync,
                    delay_seconds=self._backoff(sync["attempt_count"]),
                    processing_status=processing_status,
                )
            if processing_status == "DONE":
                retrieved = connector.retrieve_report(sync["amazon_report_id"])
                return self._import_done(sync, recipe, retrieved)
            if processing_status in {"CANCELLED", "FATAL"}:
                return self._fail(
                    sync,
                    "amazon_report_terminal",
                    f"Amazon report ended with processing status {processing_status}",
                    processing_status=processing_status,
                )
            return self._fail(
                sync,
                "amazon_report_status_unknown",
                "Amazon report returned an unsupported processing status",
                processing_status=processing_status,
            )
        except ConnectorRateLimitError as exc:
            return self._reschedule(
                sync,
                delay_seconds=exc.retry_after,
                error_code="rate_limited",
                error_message="Amazon rate limited the report sync",
            )
        except MissingCredentialError:
            return self._fail(
                sync,
                "missing_credential",
                "required Amazon credential is not configured",
            )
        except ExternalServiceError as exc:
            return self._reschedule(
                sync,
                delay_seconds=self._backoff(sync["attempt_count"]),
                error_code="external_service_error",
                error_message=str(exc),
            )
        except ConnectorError as exc:
            return self._reschedule(
                sync,
                delay_seconds=self._backoff(sync["attempt_count"]),
                error_code="connector_error",
                error_message=str(exc),
            )
        except ValidationError as exc:
            return self._fail(sync, "invalid_report_data", str(exc))
        except Exception as exc:
            # Do not leave an unexpected initialization or transition failure
            # leased until timeout. Persist a non-sensitive retry state, then
            # re-raise so process monitoring still observes the real failure.
            try:
                self.db.reschedule_report_sync(
                    sync["tenant_id"],
                    sync["id"],
                    delay_seconds=self._backoff(sync["attempt_count"]),
                    error_code="worker_internal_error",
                    error_message="report sync worker failed before completing a transition",
                )
            except Exception as release_error:
                raise release_error from exc
            raise
