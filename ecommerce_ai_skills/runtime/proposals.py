"""Versioned, human-approved execution control plane for Daily Ops proposals."""

from __future__ import annotations

import hashlib
import json
import math
import re
import secrets
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from .actions import ActionService
from .auth import AuthService
from .evidence import REPORT_SPECS
from .errors import AuthorizationError, ConflictError, NotFoundError, ValidationError
from .storage import Database, Principal, utc_now


_OPERATIONS = {
    "human.review",
    "shopify.sync_products",
    "amazon_spapi.import_report",
    "amazon_ads.campaign_update",
}
_RISKS = {"low", "medium", "high", "critical"}
_DECISIONS = {"approve", "reject", "revision_required"}
_SECRET_KEY = re.compile(r"(?:secret|password|credential|access.?token|refresh.?token|api.?key|authorization)", re.I)


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


@dataclass
class ProposalService:
    db: Database
    auth: AuthService
    actions: ActionService

    @staticmethod
    def _text(value: Any, field: str, minimum: int, maximum: int) -> str:
        if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
            raise ValidationError(f"{field} must be between {minimum} and {maximum} characters")
        return value.strip()

    @staticmethod
    def _instant(value: Any, *, future: bool = True) -> str:
        if not isinstance(value, str):
            raise ValidationError("expires_at must be an RFC 3339 timestamp")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValidationError("expires_at must be an RFC 3339 timestamp") from exc
        if parsed.tzinfo is None:
            raise ValidationError("expires_at must include a timezone")
        parsed = parsed.astimezone(timezone.utc)
        if future and parsed <= datetime.now(timezone.utc):
            raise ValidationError("expires_at must be in the future")
        if parsed > datetime.now(timezone.utc) + timedelta(days=30):
            raise ValidationError("expires_at cannot be more than 30 days in the future")
        return parsed.isoformat(timespec="seconds")

    @classmethod
    def _reject_secrets(cls, value: Any, path: str = "payload") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if not isinstance(key, str):
                    raise ValidationError(f"{path} keys must be strings")
                if _SECRET_KEY.search(key):
                    raise ValidationError("credentials must never be included in a proposal payload")
                cls._reject_secrets(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                cls._reject_secrets(child, f"{path}[{index}]")
        elif isinstance(value, float) and not math.isfinite(value):
            raise ValidationError(f"{path} must not contain NaN or infinity")
        elif not isinstance(value, (str, int, float, bool, type(None))):
            raise ValidationError(f"{path} contains an unsupported value")
        elif isinstance(value, str) and len(value) > 4000:
            raise ValidationError(f"{path} string values must be at most 4000 characters")

    @classmethod
    def _operation_payload(cls, operation: Any, payload: Any) -> tuple[str, dict[str, Any]]:
        if operation not in _OPERATIONS:
            raise ValidationError("unsupported proposal operation")
        if not isinstance(payload, dict) or len(_canonical(payload).encode("utf-8")) > 32_000:
            raise ValidationError("payload must be an object no larger than 32 KB")
        cls._reject_secrets(payload)
        if operation == "human.review":
            if set(payload) != {"instructions"}:
                raise ValidationError("human.review payload requires only instructions")
            cls._text(payload.get("instructions"), "payload.instructions", 3, 2000)
        elif operation == "shopify.sync_products":
            allowed = {"external_account_id", "limit", "page_info"}
            if "external_account_id" not in payload or set(payload) - allowed:
                raise ValidationError("shopify.sync_products payload is invalid")
            cls._text(payload.get("external_account_id"), "payload.external_account_id", 1, 200)
            if "limit" in payload and (
                not isinstance(payload["limit"], int) or isinstance(payload["limit"], bool)
                or not 1 <= payload["limit"] <= 250
            ):
                raise ValidationError("payload.limit must be between 1 and 250")
            if "page_info" in payload and not isinstance(payload["page_info"], str):
                raise ValidationError("payload.page_info must be a string")
        elif operation == "amazon_spapi.import_report":
            if set(payload) != {"external_account_id", "report_id", "evidence_report_type"}:
                raise ValidationError("amazon_spapi.import_report payload is invalid")
            for field in payload:
                cls._text(payload[field], f"payload.{field}", 1, 200)
            if payload["evidence_report_type"] not in REPORT_SPECS:
                raise ValidationError("payload.evidence_report_type is not installed")
        else:
            if set(payload) != {"external_account_id", "campaign_id", "changes"}:
                raise ValidationError("amazon_ads.campaign_update payload is invalid")
            cls._text(payload.get("external_account_id"), "payload.external_account_id", 1, 200)
            cls._text(payload.get("campaign_id"), "payload.campaign_id", 1, 200)
            if not isinstance(payload.get("changes"), dict) or not payload["changes"]:
                raise ValidationError("payload.changes must be a non-empty object")
        return operation, payload

    @staticmethod
    def _required_approvals(risk: str) -> int:
        return 1 if risk in {"low", "medium"} else 2

    @staticmethod
    def _version_content(
        source: dict[str, Any], *, title: str, rationale: str, expected_impact: str,
        rollback_plan: str, evidence_refs: list[str], metric_ids: list[str],
        operation: str, payload: dict[str, Any], risk: str, expires_at: str,
    ) -> dict[str, Any]:
        return {
            "source": {
                "daily_ops_run_id": source["daily_ops_run_id"],
                "agent_run_id": source["agent_run_id"],
                "graph_version_id": source["graph_version_id"],
                "graph_version_hash": source["graph_version_hash"],
                "priority_rank": source["priority_rank"],
            },
            "title": title,
            "rationale": rationale,
            "expected_impact": expected_impact,
            "rollback_plan": rollback_plan,
            "evidence_refs": evidence_refs,
            "metric_observation_ids": metric_ids,
            "operation": operation,
            "payload": payload,
            "risk": risk,
            "expires_at": expires_at,
        }

    def _source_priority(self, tenant_id: str, daily_ops_run_id: str, priority_rank: Any) -> tuple[dict[str, Any], dict[str, Any]]:
        if not isinstance(priority_rank, int) or isinstance(priority_rank, bool) or not 1 <= priority_rank <= 5:
            raise ValidationError("priority_rank must be between 1 and 5")
        with self.db.connect() as conn:
            row = conn.execute(
                """SELECT d.*,a.status AS agent_status,a.review_status,a.origin,
                          a.parent_daily_ops_run_id,a.parent_daily_ops_attempt,
                          a.graph_version_id AS agent_graph_version_id,
                          a.graph_version_hash AS agent_graph_version_hash,
                          a.attempt_count AS agent_attempt,a.evidence_json
                   FROM daily_ops_runs d JOIN agent_runs a
                     ON a.tenant_id=d.tenant_id AND a.id=d.agent_run_id
                   WHERE d.tenant_id=? AND d.id=?""",
                (tenant_id, daily_ops_run_id),
            ).fetchone()
            if row is None:
                raise NotFoundError("eligible Daily Ops run not found")
            eligible = (
                row["status"] == "completed" and row["agent_status"] == "completed"
                and row["review_status"] == "approved" and row["origin"] == "daily_ops"
                and row["parent_daily_ops_run_id"] == row["id"]
                and row["parent_daily_ops_attempt"] == row["attempt_count"]
                and row["graph_version_id"] == row["agent_graph_version_id"]
                and row["graph_version_hash"] == row["agent_graph_version_hash"]
            )
            if not eligible:
                raise ConflictError("Daily Ops run is not eligible for proposals")
            artifacts = conn.execute(
                """SELECT ar.content_json FROM agent_artifacts ar
                   JOIN agent_tasks t ON t.tenant_id=ar.tenant_id AND t.id=ar.task_id
                                      AND t.run_id=ar.run_id
                   WHERE ar.tenant_id=? AND ar.run_id=? AND ar.kind='manager_synthesis'
                     AND ar.attempt=? AND t.role='manager' AND t.status='completed'
                     AND t.attempt_count=ar.attempt ORDER BY ar.rowid""",
                (tenant_id, row["agent_run_id"], row["agent_attempt"]),
            ).fetchall()
        if len(artifacts) != 1:
            raise ConflictError("eligible run must have exactly one final Manager synthesis")
        report = json.loads(artifacts[0]["content_json"])
        priorities = report.get("priorities") if isinstance(report, dict) else None
        matches = [item for item in (priorities or []) if isinstance(item, dict) and item.get("rank") == priority_rank]
        if len(matches) != 1:
            raise ValidationError("priority_rank does not identify one Manager priority")
        priority = matches[0]
        if priority.get("requires_approval") is not True:
            raise ConflictError("Manager priority is not approval-controlled")
        refs = priority.get("evidence_refs")
        if not isinstance(refs, list) or not refs or any(not isinstance(item, str) for item in refs):
            raise ConflictError("Manager priority has invalid evidence references")
        catalog_ids = {
            item.get("source_id") for item in json.loads(row["evidence_json"])
            if isinstance(item, dict)
        }
        if not set(refs) <= catalog_ids:
            raise ConflictError("Manager priority cites evidence outside its Agent Run")
        metric_refs = priority.get("metric_claim", {}).get("observation_refs", [])
        if not isinstance(metric_refs, list) or any(not isinstance(item, str) for item in metric_refs):
            raise ConflictError("Manager priority has invalid metric references")
        metric_ids = [item.removeprefix("metric_observation:") for item in metric_refs]
        selected_metric_ids = set(json.loads(row["selected_metric_observation_ids_json"]))
        if not set(metric_ids) <= selected_metric_ids:
            raise ConflictError("Manager priority cites Metric Observations outside its Daily Ops run")
        source = {
            "daily_ops_run_id": row["id"], "agent_run_id": row["agent_run_id"],
            "graph_version_id": row["graph_version_id"],
            "graph_version_hash": row["graph_version_hash"], "priority_rank": priority_rank,
            "platform": json.loads(row["schedule_config_json"]).get("platform"),
        }
        return source, priority

    @staticmethod
    def _decode_version(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
        value = dict(row)
        value["evidence_refs"] = json.loads(value.pop("evidence_refs_json"))
        value["metric_observation_ids"] = json.loads(value.pop("metric_observation_ids_json"))
        value["payload"] = json.loads(value.pop("payload_json"))
        return value

    @staticmethod
    def _decode_execution(
        row: sqlite3.Row | dict[str, Any], *, include_lease_token: bool = False
    ) -> dict[str, Any]:
        value = dict(row)
        raw = value.pop("result_json", None)
        value["result"] = json.loads(raw) if raw else None
        if not include_lease_token:
            value.pop("lease_token", None)
        value["capability_block"] = (
            {
                "code": value.get("error_code"),
                "message": value.get("error_message"),
                "retryable": False,
                "connector_calls": 0,
            }
            if value.get("status") == "blocked"
            else None
        )
        return value

    def expire_due(self, *, limit: int = 100) -> int:
        """Persist due expirations as an explicit, audited worker operation."""
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 500:
            raise ValidationError("limit must be between 1 and 500")
        now = utc_now()
        with self.db.transaction() as conn:
            rows = conn.execute(
                """SELECT id,tenant_id FROM proposals
                   WHERE status IN ('draft','submitted','approved','rejected','revision_required','failed')
                     AND julianday(expires_at)<=julianday(?)
                   ORDER BY expires_at,id LIMIT ?""", (now, limit)
            ).fetchall()
            for row in rows:
                conn.execute(
                    "UPDATE proposals SET status='expired',updated_at=? WHERE id=? AND tenant_id=?",
                    (now, row["id"], row["tenant_id"]),
                )
                self.db.append_audit_tx(
                    conn, row["tenant_id"], None, "proposal-expiry-worker",
                    "proposal.expire", "proposal", row["id"], "expired", {},
                )
        return len(rows)

    def _persist_expired(self, principal: Principal, proposal_id: str, request_id: str) -> bool:
        now = utc_now()
        with self.db.transaction() as conn:
            changed = conn.execute(
                """UPDATE proposals SET status='expired',updated_at=?
                   WHERE tenant_id=? AND id=?
                     AND status IN ('draft','submitted','approved','rejected','revision_required','failed')
                     AND julianday(expires_at)<=julianday(?)""",
                (now, principal.tenant_id, proposal_id, now),
            )
            if changed.rowcount:
                self.db.append_audit_tx(
                    conn, principal.tenant_id, principal.user_id, request_id,
                    "proposal.expire", "proposal", proposal_id, "expired", {},
                )
        return bool(changed.rowcount)

    def _row(self, tenant_id: str, proposal_id: str) -> tuple[sqlite3.Row, sqlite3.Row]:
        with self.db.connect() as conn:
            proposal = conn.execute(
                "SELECT * FROM proposals WHERE tenant_id=? AND id=?", (tenant_id, proposal_id)
            ).fetchone()
            if proposal is None:
                raise NotFoundError("proposal not found")
            version = conn.execute(
                """SELECT * FROM proposal_versions
                   WHERE tenant_id=? AND proposal_id=? AND version=?""",
                (tenant_id, proposal_id, proposal["current_version"]),
            ).fetchone()
        if version is None:
            raise ConflictError("proposal current version is missing")
        return proposal, version

    def get(self, principal: Principal, proposal_id: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        proposal, version = self._row(principal.tenant_id, proposal_id)
        with self.db.connect() as conn:
            decisions = [dict(row) for row in conn.execute(
                """SELECT * FROM proposal_decisions WHERE tenant_id=? AND proposal_id=?
                   ORDER BY proposal_version,created_at,id""", (principal.tenant_id, proposal_id)
            ).fetchall()]
            executions = [self._decode_execution(row) for row in conn.execute(
                """SELECT * FROM proposal_executions WHERE tenant_id=? AND proposal_id=?
                   ORDER BY created_at,id""", (principal.tenant_id, proposal_id)
            ).fetchall()]
            version_rows = conn.execute(
                """SELECT * FROM proposal_versions WHERE tenant_id=? AND proposal_id=?
                   ORDER BY version""", (principal.tenant_id, proposal_id)
            ).fetchall()
        current = self._decode_version(version)
        current["version_id"] = current.pop("id")
        current.pop("tenant_id", None)
        current.pop("proposal_id", None)
        stored_version = current.pop("version")
        result = {**dict(proposal), **current}
        result["version"] = result.pop("current_version")
        if result["version"] != stored_version:
            raise ConflictError("proposal version binding is inconsistent")
        result["required_approvals"] = self._required_approvals(result["risk"])
        result["approval_count"] = sum(
            1 for item in decisions
            if item["proposal_version"] == result["version"]
            and item["content_hash"] == result["content_hash"]
            and item["decision"] == "approve"
        )
        result["decisions"] = decisions
        result["executions"] = executions
        result["versions"] = []
        for item in version_rows:
            decoded = self._decode_version(item)
            decoded["version_id"] = decoded.pop("id")
            decoded.pop("tenant_id", None)
            decoded.pop("proposal_id", None)
            result["versions"].append(decoded)
        if result["status"] in {"draft", "submitted", "approved", "rejected", "revision_required", "failed"} and datetime.fromisoformat(
            result["expires_at"]
        ) <= datetime.now(timezone.utc):
            result["status"] = "expired"
        if result["operation"] == "amazon_ads.campaign_update":
            result["capability_status"] = "blocked"
            result["capability_reason"] = "Amazon Ads write capability is not installed or approved"
        elif result["operation"] == "human.review":
            result["capability_status"] = "available"
            result["capability_reason"] = "Human review is recorded locally"
        else:
            provider = "amazon_spapi" if result["operation"].startswith("amazon_spapi") else "shopify"
            account_id = result["payload"].get("external_account_id")
            with self.db.connect() as conn:
                account = conn.execute(
                    """SELECT health_status FROM connector_accounts
                       WHERE tenant_id=? AND provider=? AND external_account_id=?""",
                    (principal.tenant_id, provider, account_id),
                ).fetchone()
            result["capability_status"] = (
                "available" if account is not None and account["health_status"] == "healthy"
                else "unavailable"
            )
            result["capability_reason"] = (
                f"{provider} connector account is healthy"
                if account is not None and account["health_status"] == "healthy"
                else (
                    f"{provider} connector account health is {account['health_status']}"
                    if account is not None else f"{provider} connector account is not configured"
                )
            )
        result["capability_block"] = (
            {
                "code": (
                    "AMAZON_ADS_CAPABILITY_UNAVAILABLE"
                    if result["operation"] == "amazon_ads.campaign_update"
                    else "CONNECTOR_CAPABILITY_UNAVAILABLE"
                ),
                "message": result["capability_reason"],
                "retryable": False,
                "connector_calls": 0,
            }
            if result["capability_status"] != "available"
            else None
        )
        return result

    def list(self, principal: Principal, status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        self.auth.require(principal, "viewer")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 200:
            raise ValidationError("limit must be between 1 and 200")
        valid_statuses = {
            "draft", "submitted", "approved", "rejected", "revision_required",
            "expired", "executing", "executed", "failed", "blocked",
        }
        if status is not None and status not in valid_statuses:
            raise ValidationError("unknown proposal status")
        active_statuses = {"draft", "submitted", "approved", "rejected", "revision_required", "failed"}
        now = utc_now()
        with self.db.connect() as conn:
            if status is None:
                rows = conn.execute(
                    """SELECT id FROM proposals WHERE tenant_id=?
                       ORDER BY updated_at DESC,id LIMIT ?""",
                    (principal.tenant_id, limit),
                ).fetchall()
            elif status == "expired":
                rows = conn.execute(
                    """SELECT id FROM proposals WHERE tenant_id=? AND (
                         status='expired' OR (
                           status IN ('draft','submitted','approved','rejected','revision_required','failed')
                           AND julianday(expires_at)<=julianday(?)
                         )
                       ) ORDER BY updated_at DESC,id LIMIT ?""",
                    (principal.tenant_id, now, limit),
                ).fetchall()
            elif status in active_statuses:
                rows = conn.execute(
                    """SELECT id FROM proposals WHERE tenant_id=? AND status=?
                         AND julianday(expires_at)>julianday(?)
                       ORDER BY updated_at DESC,id LIMIT ?""",
                    (principal.tenant_id, status, now, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT id FROM proposals WHERE tenant_id=? AND status=?
                       ORDER BY updated_at DESC,id LIMIT ?""",
                    (principal.tenant_id, status, limit),
                ).fetchall()
        return [self.get(principal, row["id"]) for row in rows]

    def create(
        self, principal: Principal, *, daily_ops_run_id: str, priority_rank: Any,
        operation: Any, payload: Any, risk: Any, rollback_plan: Any,
        idempotency_key: str, expires_at: Any, request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        if not isinstance(idempotency_key, str) or not 1 <= len(idempotency_key) <= 200:
            raise ValidationError("idempotency_key is required and must be at most 200 characters")
        operation, payload = self._operation_payload(operation, payload)
        if risk not in _RISKS:
            raise ValidationError("risk must be low, medium, high, or critical")
        expiry = self._instant(expires_at)
        rollback = self._text(rollback_plan, "rollback_plan", 3, 2000)
        source, priority = self._source_priority(principal.tenant_id, daily_ops_run_id, priority_rank)
        if operation.startswith("amazon") and source["platform"] != "amazon":
            raise ValidationError("Amazon operations require an Amazon Daily Ops source")
        if operation.startswith("shopify") and source["platform"] != "shopify":
            raise ValidationError("Shopify operations require a Shopify Daily Ops source")
        title = self._text(priority.get("title"), "Manager priority title", 1, 200)
        rationale = self._text(priority.get("why_now"), "Manager priority rationale", 1, 2000)
        expected = self._text(priority.get("expected_impact"), "Manager expected impact", 1, 2000)
        evidence_refs = list(dict.fromkeys(priority["evidence_refs"]))
        metric_ids = [
            item.removeprefix("metric_observation:")
            for item in priority.get("metric_claim", {}).get("observation_refs", [])
        ]
        content = self._version_content(
            source, title=title, rationale=rationale, expected_impact=expected,
            rollback_plan=rollback, evidence_refs=evidence_refs, metric_ids=metric_ids,
            operation=operation, payload=payload, risk=risk, expires_at=expiry,
        )
        payload_hash, content_hash = _sha(payload), _sha(content)
        proposal_id, version_id, now = self.db._id(), self.db._id(), utc_now()
        try:
            with self.db.transaction() as conn:
                conn.execute(
                    """INSERT INTO proposals(
                       id,tenant_id,idempotency_key,daily_ops_run_id,agent_run_id,
                       graph_version_id,graph_version_hash,priority_rank,current_version,
                       status,created_by,expires_at,created_at,updated_at
                       ) VALUES(?,?,?,?,?,?,?,?,1,'draft',?,?,?,?)""",
                    (proposal_id, principal.tenant_id, idempotency_key,
                     source["daily_ops_run_id"], source["agent_run_id"],
                     source["graph_version_id"], source["graph_version_hash"], priority_rank,
                     principal.user_id, expiry, now, now),
                )
                conn.execute(
                    """INSERT INTO proposal_versions(
                       id,tenant_id,proposal_id,version,title,rationale,expected_impact,
                       rollback_plan,evidence_refs_json,metric_observation_ids_json,
                       operation,payload_json,payload_hash,content_hash,risk,expires_at,
                       created_by,created_at
                       ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (version_id, principal.tenant_id, proposal_id, 1, title, rationale,
                     expected, rollback, _canonical(evidence_refs), _canonical(metric_ids),
                     operation, _canonical(payload), payload_hash, content_hash, risk, expiry,
                     principal.user_id, now),
                )
                self.db.append_audit_tx(
                    conn, principal.tenant_id, principal.user_id, request_id,
                    "proposal.create", "proposal", proposal_id, "accepted",
                    {"content_hash": content_hash, "operation": operation, "risk": risk},
                )
        except sqlite3.IntegrityError as exc:
            with self.db.connect() as conn:
                existing = conn.execute(
                    "SELECT id FROM proposals WHERE tenant_id=? AND idempotency_key=?",
                    (principal.tenant_id, idempotency_key),
                ).fetchone()
            if existing is None:
                raise ConflictError("proposal could not be persisted") from exc
            replay = self.get(principal, existing["id"])
            with self.db.connect() as conn:
                first = conn.execute(
                    """SELECT content_hash FROM proposal_versions
                       WHERE tenant_id=? AND proposal_id=? AND version=1""",
                    (principal.tenant_id, replay["id"]),
                ).fetchone()
            if first is None or first["content_hash"] != content_hash:
                raise ConflictError("idempotency key was used with different proposal content")
            return replay
        return self.get(principal, proposal_id)

    def revise(
        self, principal: Principal, proposal_id: str, *, expected_version: Any,
        title: Any | None = None, rationale: Any | None = None,
        expected_impact: Any | None = None, rollback_plan: Any | None = None,
        operation: Any | None = None, payload: Any | None = None,
        risk: Any | None = None, expires_at: Any | None = None, request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        self._persist_expired(principal, proposal_id, request_id)
        proposal, version_row = self._row(principal.tenant_id, proposal_id)
        if proposal["created_by"] != principal.user_id:
            raise AuthorizationError("only the proposal creator can revise it")
        if expected_version != proposal["current_version"]:
            raise ConflictError("proposal version changed; refresh before revising")
        if proposal["status"] not in {"draft", "rejected", "revision_required"}:
            raise ConflictError("proposal cannot be revised from its current status")
        current = self._decode_version(version_row)
        next_title = current["title"] if title is None else self._text(title, "title", 1, 200)
        next_rationale = current["rationale"] if rationale is None else self._text(rationale, "rationale", 1, 2000)
        next_impact = current["expected_impact"] if expected_impact is None else self._text(expected_impact, "expected_impact", 1, 2000)
        next_rollback = current["rollback_plan"] if rollback_plan is None else self._text(rollback_plan, "rollback_plan", 3, 2000)
        next_operation, next_payload = self._operation_payload(
            current["operation"] if operation is None else operation,
            current["payload"] if payload is None else payload,
        )
        next_risk = current["risk"] if risk is None else risk
        if next_risk not in _RISKS:
            raise ValidationError("risk must be low, medium, high, or critical")
        with self.db.connect() as conn:
            daily = conn.execute(
                "SELECT schedule_config_json FROM daily_ops_runs WHERE tenant_id=? AND id=?",
                (principal.tenant_id, proposal["daily_ops_run_id"]),
            ).fetchone()
        platform = json.loads(daily["schedule_config_json"]).get("platform") if daily else None
        if next_operation.startswith("amazon") and platform != "amazon":
            raise ValidationError("Amazon operations require an Amazon Daily Ops source")
        if next_operation.startswith("shopify") and platform != "shopify":
            raise ValidationError("Shopify operations require a Shopify Daily Ops source")
        next_expiry = proposal["expires_at"] if expires_at is None else self._instant(expires_at)
        source = {key: proposal[key] for key in (
            "daily_ops_run_id", "agent_run_id", "graph_version_id", "graph_version_hash", "priority_rank"
        )}
        content = self._version_content(
            source, title=next_title, rationale=next_rationale,
            expected_impact=next_impact, rollback_plan=next_rollback,
            evidence_refs=current["evidence_refs"], metric_ids=current["metric_observation_ids"],
            operation=next_operation, payload=next_payload, risk=next_risk,
            expires_at=next_expiry,
        )
        content_hash, payload_hash = _sha(content), _sha(next_payload)
        if content_hash == current["content_hash"]:
            raise ConflictError("revision must change proposal content")
        next_version, now = proposal["current_version"] + 1, utc_now()
        expired_during_revision = False
        try:
            with self.db.transaction() as conn:
                fresh = conn.execute(
                    """SELECT status,current_version,expires_at FROM proposals
                       WHERE tenant_id=? AND id=?""", (principal.tenant_id, proposal_id)
                ).fetchone()
                if fresh is None:
                    raise NotFoundError("proposal not found")
                if fresh["current_version"] != expected_version or fresh["status"] not in {
                    "draft", "rejected", "revision_required"
                }:
                    raise ConflictError("proposal changed while it was being revised")
                if datetime.fromisoformat(fresh["expires_at"]) <= datetime.fromisoformat(now):
                    conn.execute(
                        "UPDATE proposals SET status='expired',updated_at=? WHERE tenant_id=? AND id=?",
                        (now, principal.tenant_id, proposal_id),
                    )
                    expired_during_revision = True
                if not expired_during_revision:
                    conn.execute(
                        """INSERT INTO proposal_versions(
                           id,tenant_id,proposal_id,version,title,rationale,expected_impact,
                           rollback_plan,evidence_refs_json,metric_observation_ids_json,
                           operation,payload_json,payload_hash,content_hash,risk,expires_at,
                           created_by,created_at
                           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (self.db._id(), principal.tenant_id, proposal_id, next_version,
                         next_title, next_rationale, next_impact, next_rollback,
                         _canonical(current["evidence_refs"]), _canonical(current["metric_observation_ids"]),
                         next_operation, _canonical(next_payload), payload_hash, content_hash,
                         next_risk, next_expiry, principal.user_id, now),
                    )
                    changed = conn.execute(
                        """UPDATE proposals SET current_version=?,status='draft',expires_at=?,
                                  submitted_at=NULL,completed_at=NULL,updated_at=?
                           WHERE tenant_id=? AND id=? AND current_version=?
                             AND status IN ('draft','rejected','revision_required')""",
                        (next_version, next_expiry, now, principal.tenant_id, proposal_id, expected_version),
                    )
                    if changed.rowcount != 1:
                        raise ConflictError("proposal changed while it was being revised")
                self.db.append_audit_tx(
                    conn, principal.tenant_id, principal.user_id, request_id,
                    "proposal.expire" if expired_during_revision else "proposal.revise",
                    "proposal", proposal_id,
                    "expired" if expired_during_revision else "accepted",
                    {} if expired_during_revision else {
                        "version": next_version, "content_hash": content_hash
                    },
                )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("this proposal revision already exists") from exc
        if expired_during_revision:
            raise ConflictError("proposal has expired")
        return self.get(principal, proposal_id)

    def submit(self, principal: Principal, proposal_id: str, *, expected_version: Any, request_id: str) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        self._persist_expired(principal, proposal_id, request_id)
        proposal, _ = self._row(principal.tenant_id, proposal_id)
        if proposal["created_by"] != principal.user_id:
            raise AuthorizationError("only the proposal creator can submit it")
        if expected_version != proposal["current_version"]:
            raise ConflictError("proposal version changed; refresh before submitting")
        now = utc_now()
        expired_during_submit = False
        with self.db.transaction() as conn:
            fresh = conn.execute(
                """SELECT status,current_version,expires_at FROM proposals
                   WHERE tenant_id=? AND id=?""", (principal.tenant_id, proposal_id)
            ).fetchone()
            if fresh is None:
                raise NotFoundError("proposal not found")
            if fresh["status"] != "draft" or fresh["current_version"] != expected_version:
                raise ConflictError("only a current, unexpired draft can be submitted")
            if datetime.fromisoformat(fresh["expires_at"]) <= datetime.fromisoformat(now):
                conn.execute(
                    "UPDATE proposals SET status='expired',updated_at=? WHERE tenant_id=? AND id=?",
                    (now, principal.tenant_id, proposal_id),
                )
                expired_during_submit = True
            if not expired_during_submit:
                conn.execute(
                    """UPDATE proposals SET status='submitted',submitted_at=?,updated_at=?
                       WHERE tenant_id=? AND id=? AND current_version=? AND status='draft'""",
                    (now, now, principal.tenant_id, proposal_id, expected_version),
                )
            self.db.append_audit_tx(
                conn, principal.tenant_id, principal.user_id, request_id,
                "proposal.expire" if expired_during_submit else "proposal.submit",
                "proposal", proposal_id,
                "expired" if expired_during_submit else "accepted",
                {} if expired_during_submit else {"version": expected_version},
            )
        if expired_during_submit:
            raise ConflictError("proposal has expired")
        return self.get(principal, proposal_id)

    def decide(
        self, principal: Principal, proposal_id: str, *, expected_version: Any,
        decision: Any, comment: Any, request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "admin")
        self._persist_expired(principal, proposal_id, request_id)
        if decision not in _DECISIONS:
            raise ValidationError("decision must be approve, reject, or revision_required")
        comment = self._text(comment, "comment", 1, 2000)
        proposal, version = self._row(principal.tenant_id, proposal_id)
        if expected_version != proposal["current_version"]:
            raise ConflictError("proposal version changed; refresh before deciding")
        if decision == "approve" and proposal["created_by"] == principal.user_id:
            raise AuthorizationError("proposal creators cannot approve their own proposal")
        with self.db.connect() as conn:
            replay = conn.execute(
                """SELECT decision,comment,content_hash FROM proposal_decisions
                   WHERE tenant_id=? AND proposal_id=? AND proposal_version=? AND decided_by=?""",
                (principal.tenant_id, proposal_id, expected_version, principal.user_id),
            ).fetchone()
        if replay is not None:
            if dict(replay) == {
                "decision": decision, "comment": comment, "content_hash": version["content_hash"]
            }:
                return self.get(principal, proposal_id)
            raise ConflictError("this administrator already decided this proposal version")
        now = utc_now()
        expired_during_decision = False
        try:
            with self.db.transaction() as conn:
                current = conn.execute(
                    """SELECT status,current_version,expires_at FROM proposals
                       WHERE tenant_id=? AND id=?""", (principal.tenant_id, proposal_id)
                ).fetchone()
                if current is None:
                    raise NotFoundError("proposal not found")
                if current["status"] != "submitted" or current["current_version"] != expected_version:
                    raise ConflictError("proposal is not awaiting this version's decision")
                if datetime.fromisoformat(current["expires_at"]) <= datetime.fromisoformat(now):
                    conn.execute("UPDATE proposals SET status='expired',updated_at=? WHERE tenant_id=? AND id=?",
                                 (now, principal.tenant_id, proposal_id))
                    expired_during_decision = True
                if not expired_during_decision:
                    conn.execute(
                    """INSERT INTO proposal_decisions(
                       id,tenant_id,proposal_id,proposal_version,content_hash,
                       decided_by,decision,comment,created_at
                       ) VALUES(?,?,?,?,?,?,?,?,?)""",
                    (self.db._id(), principal.tenant_id, proposal_id, expected_version,
                     version["content_hash"], principal.user_id, decision, comment, now),
                )
                if not expired_during_decision and decision == "approve":
                    approvals = conn.execute(
                        """SELECT COUNT(DISTINCT decided_by) FROM proposal_decisions
                           WHERE tenant_id=? AND proposal_id=? AND proposal_version=?
                             AND content_hash=? AND decision='approve'""",
                        (principal.tenant_id, proposal_id, expected_version, version["content_hash"]),
                    ).fetchone()[0]
                    if approvals >= self._required_approvals(version["risk"]):
                        conn.execute("UPDATE proposals SET status='approved',updated_at=? WHERE tenant_id=? AND id=?",
                                     (now, principal.tenant_id, proposal_id))
                elif not expired_during_decision:
                    conn.execute("UPDATE proposals SET status=?,updated_at=? WHERE tenant_id=? AND id=?",
                                 ("rejected" if decision == "reject" else "revision_required",
                                  now, principal.tenant_id, proposal_id))
                self.db.append_audit_tx(
                    conn, principal.tenant_id, principal.user_id, request_id,
                    "proposal.expire" if expired_during_decision else "proposal.decide",
                    "proposal", proposal_id,
                    "expired" if expired_during_decision else str(decision),
                    {} if expired_during_decision else {
                        "version": expected_version,
                        "content_hash": version["content_hash"],
                    },
                )
        except sqlite3.IntegrityError as exc:
            with self.db.connect() as conn:
                existing = conn.execute(
                    """SELECT decision,comment,content_hash FROM proposal_decisions
                       WHERE tenant_id=? AND proposal_id=? AND proposal_version=? AND decided_by=?""",
                    (principal.tenant_id, proposal_id, expected_version, principal.user_id),
                ).fetchone()
            if existing and dict(existing) == {
                "decision": decision, "comment": comment, "content_hash": version["content_hash"]
            }:
                return self.get(principal, proposal_id)
            raise ConflictError("this administrator already decided this proposal version") from exc
        if expired_during_decision:
            raise ConflictError("proposal has expired")
        return self.get(principal, proposal_id)

    def get_execution(self, principal: Principal, execution_id: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM proposal_executions WHERE tenant_id=? AND id=?",
                (principal.tenant_id, execution_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("proposal execution not found")
        result = self._decode_execution(row)
        return result

    def list_executions(self, principal: Principal, proposal_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        self.auth.require(principal, "viewer")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 200:
            raise ValidationError("limit must be between 1 and 200")
        if proposal_id is not None:
            self._row(principal.tenant_id, proposal_id)
        with self.db.connect() as conn:
            if proposal_id:
                rows = conn.execute(
                    """SELECT * FROM proposal_executions WHERE tenant_id=? AND proposal_id=?
                       ORDER BY created_at DESC,id LIMIT ?""",
                    (principal.tenant_id, proposal_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM proposal_executions WHERE tenant_id=?
                       ORDER BY created_at DESC,id LIMIT ?""", (principal.tenant_id, limit)
                ).fetchall()
        return [self._decode_execution(row) for row in rows]

    def _claim_execution(
        self, tenant_id: str, execution_id: str, *,
        actor_user_id: str | None = None, request_id: str = "proposal-execution-claim",
    ) -> dict[str, Any] | None:
        now, token = utc_now(), secrets.token_urlsafe(24)
        lease = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(timespec="seconds")
        with self.db.transaction() as conn:
            bound = conn.execute(
                """SELECT e.status,e.proposal_id,e.action_id,e.lease_until,v.expires_at
                   FROM proposal_executions e JOIN proposal_versions v
                     ON v.tenant_id=e.tenant_id AND v.proposal_id=e.proposal_id
                    AND v.version=e.proposal_version
                   WHERE e.tenant_id=? AND e.id=?""", (tenant_id, execution_id)
            ).fetchone()
            if (
                bound is not None and (
                    bound["status"] == "pending" or (
                        bound["status"] == "executing" and bound["action_id"] is None
                        and bound["lease_until"] is not None
                        and datetime.fromisoformat(bound["lease_until"])
                        <= datetime.fromisoformat(now)
                    )
                )
                and datetime.fromisoformat(bound["expires_at"]) <= datetime.fromisoformat(now)
            ):
                conn.execute(
                    """UPDATE proposal_executions SET status='failed',
                              lease_until=NULL,lease_token=NULL,
                              error_code='PROPOSAL_EXPIRED',
                              error_message='proposal expired before execution claim',
                              updated_at=?,completed_at=?
                       WHERE tenant_id=? AND id=? AND status IN ('pending','executing')""",
                    (now, now, tenant_id, execution_id),
                )
                conn.execute(
                    """UPDATE proposals SET status='expired',updated_at=?,completed_at=?
                       WHERE tenant_id=? AND id=? AND status='executing'""",
                    (now, now, tenant_id, bound["proposal_id"]),
                )
                self.db.append_audit_tx(
                    conn, tenant_id, actor_user_id, request_id,
                    "proposal.expire", "proposal", bound["proposal_id"], "expired",
                    {"execution_id": execution_id, "connector_calls": 0},
                )
                return None
            exhausted = conn.execute(
                """SELECT proposal_id FROM proposal_executions
                   WHERE tenant_id=? AND id=? AND attempt_count>=max_attempts AND (
                     status='pending' OR
                     (status='executing' AND julianday(lease_until)<=julianday(?))
                   )""", (tenant_id, execution_id, now)
            ).fetchone()
            if exhausted is not None:
                conn.execute(
                    """UPDATE proposal_executions SET status='failed',lease_until=NULL,
                              lease_token=NULL,error_code='MAX_ATTEMPTS_EXHAUSTED',
                              error_message='proposal execution exhausted its attempt limit',
                              updated_at=?,completed_at=? WHERE tenant_id=? AND id=?""",
                    (now, now, tenant_id, execution_id),
                )
                conn.execute(
                    """UPDATE proposals SET status='failed',updated_at=?,completed_at=?
                       WHERE tenant_id=? AND id=? AND status='executing'""",
                    (now, now, tenant_id, exhausted["proposal_id"]),
                )
                self.db.append_audit_tx(
                    conn, tenant_id, actor_user_id, request_id,
                    "proposal.execute", "proposal_execution", execution_id, "failed",
                    {"error_code": "MAX_ATTEMPTS_EXHAUSTED"},
                )
                return None
            changed = conn.execute(
                """UPDATE proposal_executions SET status='executing',lease_until=?,lease_token=?,
                          attempt_count=attempt_count+1,updated_at=?,error_code=NULL,error_message=NULL
                   WHERE tenant_id=? AND id=? AND (
                     (status='pending' AND attempt_count<max_attempts) OR
                     (status='executing' AND julianday(lease_until)<=julianday(?)
                      AND attempt_count<max_attempts)
                   )""", (lease, token, now, tenant_id, execution_id, now)
            )
            if changed.rowcount != 1:
                return None
            row = conn.execute("SELECT * FROM proposal_executions WHERE tenant_id=? AND id=?",
                               (tenant_id, execution_id)).fetchone()
            self.db.append_audit_tx(
                conn, tenant_id, actor_user_id, request_id,
                "proposal.execute.intent", "proposal_execution", execution_id, "accepted",
                {"attempt": row["attempt_count"], "operation": row["operation"]},
            )
        return self._decode_execution(row, include_lease_token=True)

    def _finish_execution(
        self, tenant_id: str, execution_id: str, *, attempt: int, token: str,
        status: str, result: dict[str, Any] | None = None,
        error_code: str | None = None, error_message: str | None = None,
        actor_user_id: str | None = None,
        request_id: str = "proposal-execution-finish",
        audit_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        proposal_status = {"executed": "executed", "failed": "failed", "blocked": "blocked"}[status]
        now = utc_now()
        with self.db.transaction() as conn:
            row = conn.execute(
                """SELECT proposal_id FROM proposal_executions
                   WHERE tenant_id=? AND id=? AND status='executing'
                     AND attempt_count=? AND lease_token=?""",
                (tenant_id, execution_id, attempt, token),
            ).fetchone()
            if row is None:
                raise ConflictError("proposal execution lease was lost")
            conn.execute(
                """UPDATE proposal_executions SET status=?,result_json=?,error_code=?,
                          error_message=?,lease_until=NULL,lease_token=NULL,updated_at=?,completed_at=?
                   WHERE tenant_id=? AND id=? AND status='executing'
                     AND attempt_count=? AND lease_token=?""",
                (status, _canonical(result) if result is not None else None,
                 error_code, error_message[:2000] if error_message else None, now, now,
                 tenant_id, execution_id, attempt, token),
            )
            changed = conn.execute(
                """UPDATE proposals SET status=?,updated_at=?,completed_at=?
                   WHERE tenant_id=? AND id=? AND status='executing'""",
                (proposal_status, now, now, tenant_id, row["proposal_id"]),
            )
            if changed.rowcount != 1:
                raise ConflictError("proposal execution state changed")
            self.db.append_audit_tx(
                conn, tenant_id, actor_user_id, request_id,
                "proposal.execute", "proposal_execution", execution_id,
                "succeeded" if status == "executed" else status,
                {"attempt": attempt, **(audit_metadata or {})},
            )
        return self._execution_by_tenant(tenant_id, execution_id)

    def _execution_by_tenant(self, tenant_id: str, execution_id: str) -> dict[str, Any]:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM proposal_executions WHERE tenant_id=? AND id=?",
                               (tenant_id, execution_id)).fetchone()
        if row is None:
            raise NotFoundError("proposal execution not found")
        return self._decode_execution(row)

    def _run_execution(self, principal: Principal, execution: dict[str, Any], request_id: str) -> dict[str, Any]:
        # A durable intent may be resumed by the worker, but it still runs as
        # the proposal creator and must retain operator authority.
        self.auth.require(principal, "operator")
        claimed = self._claim_execution(
            principal.tenant_id, execution["id"],
            actor_user_id=principal.user_id, request_id=request_id,
        )
        if claimed is None:
            current = self.get_execution(principal, execution["id"])
            if current.get("error_code") == "PROPOSAL_EXPIRED":
                raise ConflictError("proposal expired before execution claim")
            return current
        attempt, token = claimed["attempt_count"], claimed["lease_token"]
        proposal = self.get(principal, claimed["proposal_id"])
        try:
            if claimed["operation"] == "amazon_ads.campaign_update":
                result = self._finish_execution(
                    principal.tenant_id, claimed["id"], attempt=attempt, token=token,
                    status="blocked", error_code="AMAZON_ADS_CAPABILITY_UNAVAILABLE",
                    error_message="Amazon Ads write capability is not installed or approved",
                    actor_user_id=principal.user_id, request_id=request_id,
                    audit_metadata={"operation": claimed["operation"], "connector_calls": 0},
                )
                return result
            if claimed["operation"] == "human.review":
                outcome = {"recorded": True, "instructions": proposal["payload"]["instructions"]}
            else:
                if proposal["capability_status"] != "available":
                    result = self._finish_execution(
                        principal.tenant_id, claimed["id"], attempt=attempt, token=token,
                        status="blocked", error_code="CONNECTOR_CAPABILITY_UNAVAILABLE",
                        error_message=proposal["capability_reason"],
                        actor_user_id=principal.user_id, request_id=request_id,
                        audit_metadata={"operation": claimed["operation"], "connector_calls": 0},
                    )
                    return result
                creator = self.db.principal_for_user(principal.tenant_id, proposal["created_by"])
                approval = next(item for item in proposal["decisions"] if (
                    item["proposal_version"] == proposal["version"] and item["decision"] == "approve"
                    and item["content_hash"] == proposal["content_hash"]
                ))
                approver = self.db.principal_for_user(principal.tenant_id, approval["decided_by"])
                action_key = f"proposal-execution:{claimed['id']}"
                action = self.actions.request(
                    creator, claimed["operation"], proposal["payload"], action_key,
                    f"{request_id}:action-request",
                )
                if action["status"] == "requested":
                    action = self.actions.approve(approver, action["id"], f"{request_id}:action-approve")
                elif action["status"] == "failed":
                    action = self.actions.retry(creator, action["id"], f"{request_id}:action-retry")
                if claimed.get("action_id") is None:
                    with self.db.transaction() as conn:
                        linked = conn.execute(
                            """UPDATE proposal_executions SET action_id=?,updated_at=?
                               WHERE tenant_id=? AND id=? AND status='executing'
                                 AND attempt_count=? AND lease_token=? AND action_id IS NULL""",
                            (action["id"], utc_now(), principal.tenant_id, claimed["id"], attempt, token),
                        )
                        if linked.rowcount != 1:
                            raise ConflictError("proposal execution lease was lost before action execution")
                elif claimed["action_id"] != action["id"]:
                    raise ConflictError("proposal execution is bound to another action")
                action = self.actions.execute(creator, action["id"], f"{request_id}:action-execute")
                outcome = {"action_id": action["id"], "action_status": action["status"],
                           "result": action.get("result")}
            result = self._finish_execution(
                principal.tenant_id, claimed["id"], attempt=attempt, token=token,
                status="executed", result=outcome,
                actor_user_id=principal.user_id, request_id=request_id,
                audit_metadata={"operation": claimed["operation"]},
            )
            return result
        except Exception as exc:
            try:
                self._finish_execution(
                    principal.tenant_id, claimed["id"], attempt=attempt, token=token,
                    status="failed", error_code=type(exc).__name__, error_message=str(exc),
                    actor_user_id=principal.user_id, request_id=request_id,
                    audit_metadata={"error_type": type(exc).__name__},
                )
            except ConflictError:
                pass
            raise

    def execute(
        self, principal: Principal, proposal_id: str, *, expected_version: Any,
        idempotency_key: str, request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        self._persist_expired(principal, proposal_id, request_id)
        if not isinstance(idempotency_key, str) or not 1 <= len(idempotency_key) <= 200:
            raise ValidationError("Idempotency-Key is required and must be at most 200 characters")
        proposal, version = self._row(principal.tenant_id, proposal_id)
        if expected_version != proposal["current_version"]:
            raise ConflictError("proposal version changed; refresh before executing")
        expired_during_execution = False
        transaction_now = utc_now()
        with self.db.transaction() as conn:
            existing = conn.execute(
                "SELECT * FROM proposal_executions WHERE tenant_id=? AND idempotency_key=?",
                (principal.tenant_id, idempotency_key),
            ).fetchone()
            if existing is not None:
                if (existing["proposal_id"], existing["proposal_version"], existing["approved_content_hash"]) != (
                    proposal_id, expected_version, version["content_hash"]
                ):
                    raise ConflictError("Idempotency-Key was used for another proposal execution")
                execution = self._decode_execution(existing)
            else:
                by_version = conn.execute(
                    """SELECT * FROM proposal_executions
                       WHERE tenant_id=? AND proposal_id=? AND proposal_version=?""",
                    (principal.tenant_id, proposal_id, expected_version),
                ).fetchone()
                if by_version is not None:
                    if by_version["approved_content_hash"] != version["content_hash"]:
                        raise ConflictError("proposal version already has a different execution binding")
                    if by_version["idempotency_key"] != idempotency_key:
                        raise ConflictError(
                            "proposal version already has an execution with another Idempotency-Key"
                        )
                    execution = self._decode_execution(by_version)
                    existing = by_version
                else:
                    if proposal["status"] != "approved":
                        raise ConflictError("proposal must have all required approvals before execution")
                    if datetime.fromisoformat(proposal["expires_at"]) <= datetime.fromisoformat(transaction_now):
                        conn.execute(
                            "UPDATE proposals SET status='expired',updated_at=? WHERE tenant_id=? AND id=? AND status='approved'",
                            (transaction_now, principal.tenant_id, proposal_id),
                        )
                        expired_during_execution = True
                    if not expired_during_execution:
                        approvals = conn.execute(
                            """SELECT COUNT(DISTINCT decided_by) FROM proposal_decisions
                               WHERE tenant_id=? AND proposal_id=? AND proposal_version=?
                                 AND content_hash=? AND decision='approve'""",
                            (principal.tenant_id, proposal_id, expected_version, version["content_hash"]),
                        ).fetchone()[0]
                        if approvals < self._required_approvals(version["risk"]):
                            raise ConflictError("proposal approval quorum is incomplete")
                        now, execution_id = transaction_now, self.db._id()
                        conn.execute(
                            """INSERT INTO proposal_executions(
                               id,tenant_id,proposal_id,proposal_version,approved_payload_hash,
                               approved_content_hash,operation,idempotency_key,status,created_by,
                               created_at,updated_at
                               ) VALUES(?,?,?,?,?,?,?,?, 'pending',?,?,?)""",
                            (execution_id, principal.tenant_id, proposal_id, expected_version,
                             version["payload_hash"], version["content_hash"], version["operation"],
                             idempotency_key, principal.user_id, now, now),
                        )
                        conn.execute(
                            """UPDATE proposals SET status='executing',updated_at=?
                               WHERE tenant_id=? AND id=? AND status='approved'""",
                            (now, principal.tenant_id, proposal_id),
                        )
                    self.db.append_audit_tx(
                        conn, principal.tenant_id, principal.user_id, request_id,
                        "proposal.expire" if expired_during_execution else "proposal.execute.queued",
                        "proposal" if expired_during_execution else "proposal_execution",
                        proposal_id if expired_during_execution else execution_id,
                        "expired" if expired_during_execution else "accepted",
                        {} if expired_during_execution else {
                            "proposal_id": proposal_id,
                            "version": expected_version,
                            "content_hash": version["content_hash"],
                        },
                    )
        if expired_during_execution:
            raise ConflictError("proposal has expired")
        if existing is None:
            execution = self._execution_by_tenant(principal.tenant_id, execution_id)
        return self._run_execution(principal, execution, request_id)

    def retry(
        self, principal: Principal, proposal_id: str, *, expected_version: Any,
        idempotency_key: str, request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        self._persist_expired(principal, proposal_id, request_id)
        if not isinstance(idempotency_key, str) or not 1 <= len(idempotency_key) <= 200:
            raise ValidationError("Idempotency-Key is required for retry")
        proposal, version = self._row(principal.tenant_id, proposal_id)
        if expected_version != proposal["current_version"]:
            raise ConflictError("proposal version changed; refresh before retrying")
        expired_during_retry = False
        now = utc_now()
        with self.db.transaction() as conn:
            execution = conn.execute(
                """SELECT * FROM proposal_executions
                   WHERE tenant_id=? AND proposal_id=? AND proposal_version=?""",
                (principal.tenant_id, proposal_id, expected_version),
            ).fetchone()
            if execution is None:
                raise NotFoundError("proposal execution not found")
            replay = conn.execute(
                """SELECT execution_id,proposal_id,proposal_version,approved_content_hash
                   FROM proposal_execution_retries
                   WHERE tenant_id=? AND idempotency_key=?""",
                (principal.tenant_id, idempotency_key),
            ).fetchone()
            if replay is not None:
                if (
                    replay["execution_id"] != execution["id"]
                    or replay["proposal_id"] != proposal_id
                    or replay["proposal_version"] != expected_version
                    or replay["approved_content_hash"] != version["content_hash"]
                ):
                    raise ConflictError("retry Idempotency-Key belongs to another execution")
                return self._decode_execution(execution)
            if execution["status"] != "failed" or proposal["status"] != "failed":
                raise ConflictError("only a failed proposal execution can be retried")
            if execution["attempt_count"] >= execution["max_attempts"]:
                raise ConflictError("proposal execution exhausted its attempt limit")
            if execution["approved_content_hash"] != version["content_hash"]:
                raise ConflictError("failed execution is not bound to the current approved content")
            if datetime.fromisoformat(version["expires_at"]) <= datetime.fromisoformat(now):
                conn.execute(
                    """UPDATE proposals SET status='expired',updated_at=?,completed_at=?
                       WHERE tenant_id=? AND id=? AND status='failed'""",
                    (now, now, principal.tenant_id, proposal_id),
                )
                self.db.append_audit_tx(
                    conn, principal.tenant_id, principal.user_id, request_id,
                    "proposal.expire", "proposal", proposal_id, "expired",
                    {"execution_id": execution["id"], "connector_calls": 0},
                )
                expired_during_retry = True
            try:
                if not expired_during_retry:
                    conn.execute(
                        """INSERT INTO proposal_execution_retries(
                           id,tenant_id,execution_id,proposal_id,proposal_version,
                           approved_content_hash,idempotency_key,created_by,created_at
                           ) VALUES(?,?,?,?,?,?,?,?,?)""",
                        (self.db._id(), principal.tenant_id, execution["id"], proposal_id,
                         expected_version, version["content_hash"], idempotency_key,
                         principal.user_id, now),
                    )
                    conn.execute(
                    """UPDATE proposal_executions SET status='pending',last_retry_idempotency_key=?,
                              error_code=NULL,error_message=NULL,completed_at=NULL,updated_at=?
                       WHERE tenant_id=? AND id=? AND status='failed'""",
                        (idempotency_key, now, principal.tenant_id, execution["id"]),
                    )
                    conn.execute("UPDATE proposals SET status='approved',completed_at=NULL,updated_at=? WHERE tenant_id=? AND id=? AND status='failed'",
                                 (now, principal.tenant_id, proposal_id))
                    transitioned = conn.execute(
                    """UPDATE proposals SET status='executing',updated_at=?
                       WHERE tenant_id=? AND id=? AND status='approved'""",
                        (now, principal.tenant_id, proposal_id),
                    )
                    if transitioned.rowcount != 1:
                        raise ConflictError("proposal could not enter retry execution")
                    self.db.append_audit_tx(
                        conn, principal.tenant_id, principal.user_id, request_id,
                        "proposal.retry", "proposal_execution", execution["id"], "accepted",
                        {"version": expected_version, "content_hash": version["content_hash"]},
                    )
            except sqlite3.IntegrityError as exc:
                raise ConflictError("retry Idempotency-Key was already used") from exc
        if expired_during_retry:
            raise ConflictError("proposal has expired")
        return self._run_execution(principal, self._execution_by_tenant(
            principal.tenant_id, execution["id"]), request_id)

    def worker_run_once(self) -> dict[str, Any]:
        """Expire due proposals and recover one pending or stale execution."""
        expired = self.expire_due(limit=100)
        now = utc_now()
        with self.db.connect() as conn:
            row = conn.execute(
                """SELECT e.id,p.tenant_id,p.created_by
                   FROM proposal_executions e JOIN proposals p
                     ON p.tenant_id=e.tenant_id AND p.id=e.proposal_id
                   WHERE e.status='pending' OR (
                     e.status='executing' AND e.lease_until IS NOT NULL
                     AND julianday(e.lease_until)<=julianday(?)
                   ) ORDER BY e.rowid LIMIT 1""", (now,)
            ).fetchone()
        if row is None:
            return {"expired": expired, "execution": None}
        principal = self.db.principal_for_user(row["tenant_id"], row["created_by"])
        execution = self._execution_by_tenant(row["tenant_id"], row["id"])
        try:
            result = self._run_execution(
                principal, execution, f"proposal-worker:{row['id']}"
            )
        except ConflictError:
            result = self._execution_by_tenant(row["tenant_id"], row["id"])
            if result.get("error_code") != "PROPOSAL_EXPIRED":
                raise
        except Exception:
            result = self._execution_by_tenant(row["tenant_id"], row["id"])
            with self.db.connect() as conn:
                audited = conn.execute(
                    """SELECT 1 FROM audit_events
                       WHERE tenant_id=? AND resource_type='proposal_execution'
                         AND resource_id=? AND action='proposal.execute'
                         AND outcome IN ('failed','blocked','succeeded') LIMIT 1""",
                    (row["tenant_id"], row["id"]),
                ).fetchone()
            if result["status"] not in {"failed", "blocked", "executed"} or audited is None:
                raise
        return {"expired": expired, "execution": result}
