"""Approval, idempotency, and connector execution service."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .auth import AuthService
from .connectors import AmazonSPAPIReportsConnector, ShopifyConnector
from .evidence import EvidenceImportService, REPORT_SPECS
from .errors import AuthorizationError, ConnectorNotConfiguredError, ConflictError, ValidationError
from .storage import Database, Principal, ROLE_LEVEL


@dataclass
class ActionService:
    db: Database
    auth: AuthService
    evidence_imports: EvidenceImportService | None = None

    OPERATIONS = {"shopify.sync_products", "amazon_spapi.import_report"}

    def request(self, principal: Principal, operation: str, payload: dict[str, Any], idempotency_key: str, request_id: str) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        if operation not in self.OPERATIONS:
            raise ValidationError(
                "unsupported operation; available operations: "
                + ", ".join(sorted(self.OPERATIONS))
            )
        if not isinstance(payload, dict):
            raise ValidationError("payload must be an object")
        if "token" in json.dumps(payload).lower() or "access_token" in json.dumps(payload).lower():
            raise ValidationError("credentials must be configured as an environment reference, never in a payload")
        if operation == "shopify.sync_products":
            allowed = {"external_account_id", "limit", "page_info"}
            if "external_account_id" not in payload or set(payload) - allowed:
                raise ValidationError(
                    "shopify.sync_products payload requires external_account_id and only "
                    "accepts limit or page_info as optional fields"
                )
        elif operation == "amazon_spapi.import_report":
            required = {"external_account_id", "report_id", "evidence_report_type"}
            if set(payload) != required:
                raise ValidationError(
                    "amazon_spapi.import_report payload requires external_account_id, "
                    "report_id, and evidence_report_type"
                )
            if payload.get("evidence_report_type") not in REPORT_SPECS:
                raise ValidationError("unknown evidence_report_type")
        result, replayed = self.db.create_action(principal.tenant_id, idempotency_key, operation, payload, principal.user_id)
        self.db.append_audit(principal.tenant_id, principal.user_id, request_id, "action.request", "action", result["id"], "replayed" if replayed else "accepted", {"operation": operation})
        return result

    def approve(self, principal: Principal, action_id: str, request_id: str) -> dict[str, Any]:
        self.auth.require(principal, "admin")
        action = self.db.get_action(principal.tenant_id, action_id)
        if action["requested_by"] == principal.user_id:
            raise AuthorizationError("a second user must approve an action")
        result = self.db.transition_action(principal.tenant_id, action_id, "requested", "approved", approved_by=principal.user_id)
        self.db.append_audit(principal.tenant_id, principal.user_id, request_id, "action.approve", "action", action_id, "accepted", {})
        return result

    def execute(self, principal: Principal, action_id: str, request_id: str) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        action = self.db.get_action(principal.tenant_id, action_id)
        if action["status"] == "executed":
            return action
        if action["status"] != "approved" and action["status"] != "executing":
            raise ConflictError("action must be approved before execution")
        executing = self.db.claim_action(principal.tenant_id, action_id)
        try:
            result = self._run(
                principal,
                action_id,
                executing["operation"],
                executing["payload"],
                request_id,
            )
        except Exception as exc:
            self.db.transition_action(principal.tenant_id, action_id, "executing", "failed", error=str(exc), expected_attempt=executing["attempt_count"])
            self.db.append_audit(principal.tenant_id, principal.user_id, request_id, "action.execute", "action", action_id, "failed", {"error_type": type(exc).__name__})
            raise
        completed = self.db.transition_action(principal.tenant_id, action_id, "executing", "executed", result=result, expected_attempt=executing["attempt_count"])
        self.db.append_audit(principal.tenant_id, principal.user_id, request_id, "action.execute", "action", action_id, "succeeded", {"records": result.get("records", 0)})
        return completed

    def retry(self, principal: Principal, action_id: str, request_id: str) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        result = self.db.retry_action(principal.tenant_id, action_id)
        self.db.append_audit(principal.tenant_id, principal.user_id, request_id, "action.retry", "action", action_id, "accepted", {"attempt_count": result.get("attempt_count", 0)})
        return result

    def _run(
        self,
        principal: Principal,
        action_id: str,
        operation: str,
        payload: dict[str, Any],
        request_id: str,
    ) -> dict[str, Any]:
        tenant_id = principal.tenant_id
        external_account_id = payload.get("external_account_id")
        if not isinstance(external_account_id, str) or not external_account_id:
            raise ValidationError("payload.external_account_id is required")
        if operation == "amazon_spapi.import_report":
            if self.evidence_imports is None:
                raise ConnectorNotConfiguredError("evidence import service is not configured")
            account = self.db.connector_account(
                tenant_id, "amazon_spapi", external_account_id
            )
            config = json.loads(account["config_json"])
            report = AmazonSPAPIReportsConnector(config).retrieve_report(
                str(payload["report_id"])
            )
            safe_type = re.sub(r"[^A-Za-z0-9._-]+", "_", report["amazon_report_type"])
            safe_report_id = re.sub(r"[^A-Za-z0-9._-]+", "_", report["report_id"])
            imported = self.evidence_imports.import_csv(
                principal,
                raw=report["content"],
                platform="amazon",
                report_type=str(payload["evidence_report_type"]),
                filename=f"{safe_type}-{safe_report_id}.txt",
                observed_at=report["observed_at"],
                idempotency_key=f"amazon-spapi-action:{action_id}",
                request_id=request_id,
                media_type="text/tab-separated-values",
            )
            return {
                "provider": "amazon_spapi",
                "external_account_id": external_account_id,
                "report_id": report["report_id"],
                "report_document_id": report["report_document_id"],
                "amazon_report_type": report["amazon_report_type"],
                "evidence_import_id": imported["id"],
                "records": imported["row_count"],
            }
        account = self.db.connector_account(tenant_id, "shopify", external_account_id)
        config = json.loads(account["config_json"])
        connector = ShopifyConnector(config)
        page_info = payload.get("page_info") or self.db.get_sync_cursor(tenant_id, "shopify", external_account_id)
        response = connector.list_products(limit=int(payload.get("limit", 50)), page_info=page_info)
        products = response["products"]
        saved = self.db.save_records(tenant_id, "shopify", products)
        next_page_info = response.get("next_page_info")
        self.db.set_sync_cursor(tenant_id, "shopify", external_account_id, next_page_info)
        return {"provider": "shopify", "external_account_id": external_account_id, "records": saved, "next_page_info": next_page_info, "has_more": bool(next_page_info)}
