"""Durable evaluation and security assurance checks."""
from __future__ import annotations

import json,os
import logging
import re
from typing import Any

from .auth import AuthService
from .errors import ValidationError
from .evals import WorkflowEvaluator
from .storage import Database, Principal

log = logging.getLogger("ecommerce_ai_skills.assurance")
SECRET_KEY = re.compile(r"(?:secret|password|access.?token|refresh.?token|api.?key|authorization|credential)$",re.I)
REQUIRED_TRIGGERS = {
    "audit_events_chain_insert","audit_events_actor_insert","audit_events_shape_insert","audit_events_immutable_update","audit_events_immutable_delete",
    "assurance_runs_actor_insert","assurance_runs_initial_insert","assurance_runs_terminal_transition","assurance_runs_terminal_update","assurance_runs_identity_update","assurance_runs_delete",
    "mission_events_cursor_insert","mission_events_safe_metadata_insert","mission_events_resource_binding_insert","mission_events_immutable_update","mission_events_bounded_delete",
    "proposal_executions_status_transition","daily_ops_runs_status_transition",
    "provider_smoke_tests_actor_insert","provider_smoke_tests_connector_insert",
    "provider_smoke_tests_initial_insert","provider_smoke_tests_terminal_transition",
    "provider_smoke_tests_lease_reclaim","provider_smoke_tests_identity_update",
    "provider_smoke_tests_terminal_update","provider_smoke_tests_delete",
}


class AssuranceService:
    def __init__(self, db: Database, auth: AuthService, *, environ: dict[str,str]|None=None):
        self.db,self.auth=db,auth; self.environ=dict(os.environ if environ is None else environ)

    def list(self, principal: Principal, limit: int=100) -> list[dict[str,Any]]:
        self.auth.require(principal,"viewer")
        return self.db.list_assurance_runs(principal.tenant_id,limit)

    def get(self, principal: Principal, run_id: str) -> dict[str,Any]:
        self.auth.require(principal,"viewer")
        return self.db.get_assurance_run(principal.tenant_id,run_id)

    @staticmethod
    def _contains_secret_key(value: Any) -> bool:
        if isinstance(value,dict):
            return any(SECRET_KEY.search(str(k)) or AssuranceService._contains_secret_key(v) for k,v in value.items())
        if isinstance(value,list):
            return any(AssuranceService._contains_secret_key(v) for v in value)
        return False

    def _security_checks(self, tenant_id: str) -> list[dict[str,Any]]:
        checks=[]
        with self.db.connect() as conn:
            quick=conn.execute("PRAGMA quick_check").fetchone()[0]
            fk=conn.execute("PRAGMA foreign_key_check").fetchall()
            triggers={row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='trigger'")}
            configs=conn.execute("SELECT config_json FROM connector_accounts WHERE tenant_id=?",(tenant_id,)).fetchall()
            payloads=conn.execute("SELECT payload_json FROM proposal_versions WHERE tenant_id=?",(tenant_id,)).fetchall()
        chain=self.db.verify_audit_chain(tenant_id)
        checks.append({"name":"database_integrity","status":"passed" if quick=="ok" else "failed","code":"OK" if quick=="ok" else "QUICK_CHECK_FAILED"})
        checks.append({"name":"foreign_keys","status":"passed" if not fk else "failed","code":"OK" if not fk else "FOREIGN_KEY_VIOLATION","count":len(fk)})
        checks.append({"name":"audit_chain","status":"passed" if chain["valid"] else "failed","code":"OK" if chain["valid"] else "AUDIT_CHAIN_BROKEN","count":chain["event_count"]})
        missing=sorted(REQUIRED_TRIGGERS-triggers)
        checks.append({"name":"required_triggers","status":"passed" if not missing else "failed","code":"OK" if not missing else "REQUIRED_TRIGGER_MISSING","count":len(missing)})
        documents=[row[0] for row in [*configs,*payloads]]
        referenced=[]
        for row in configs:
            value=json.loads(row[0]); referenced.extend(v for k,v in value.items() if k.endswith("_ref") or k=="credential_ref")
        secret_names=set(name for name in referenced if isinstance(name,str))
        secret_names.update(name for name in self.environ if re.search(r"(?:SECRET|TOKEN|PASSWORD|API_KEY)$",name,re.I))
        secret_values=[self.environ.get(name,"") for name in secret_names]
        leaked=sum(self._contains_secret_key(json.loads(document)) for document in documents)
        leaked+=sum(1 for document in documents if any(len(secret)>=8 and secret in document for secret in secret_values))
        leaked+=sum(1 for document in documents if re.search(r"(?:eai_[A-Za-z0-9._~-]{16,}|Atza\|[A-Za-z0-9._~-]{8,}|sk-[A-Za-z0-9_-]{12,})",document))
        checks.append({"name":"credential_persistence","status":"passed" if not leaked else "failed","code":"OK" if not leaked else "CREDENTIAL_FIELD_PERSISTED","count":leaked})
        return checks

    def _eval_checks(self, tenant_id: str) -> list[dict[str,Any]]:
        with self.db.connect() as conn:
            eligible_rows=conn.execute("""SELECT a.id FROM agent_runs a LEFT JOIN daily_ops_runs d
              ON d.tenant_id=a.tenant_id AND d.id=a.parent_daily_ops_run_id
              WHERE a.tenant_id=? AND a.status='completed' AND a.review_status='approved'
                AND a.graph_version_id IS NOT NULL AND (a.origin='manual' OR
                 (a.origin='daily_ops' AND d.status='completed' AND d.agent_run_id=a.id
                  AND d.attempt_count=a.parent_daily_ops_attempt))""",(tenant_id,)).fetchall()
            latest=[]
            for eligible_row in eligible_rows:
                row=conn.execute("""SELECT passed,evaluator_version FROM agent_evaluations
                  WHERE tenant_id=? AND run_id=? ORDER BY rowid DESC LIMIT 1""",(tenant_id,eligible_row["id"])).fetchone()
                latest.append(row)
            eligible=len(eligible_rows); coverage=sum(row is not None for row in latest)
            current=sum(bool(row and row["evaluator_version"]==WorkflowEvaluator.VERSION) for row in latest)
            evaluated=sum(bool(row and row["evaluator_version"]==WorkflowEvaluator.VERSION and row["passed"]==1) for row in latest)
            bad_daily=conn.execute("""SELECT COUNT(*) FROM daily_ops_runs d LEFT JOIN agent_runs a
              ON a.tenant_id=d.tenant_id AND a.id=d.agent_run_id WHERE d.tenant_id=?
              AND d.status='completed' AND (a.id IS NULL OR a.review_status!='approved'
                OR a.origin!='daily_ops' OR a.parent_daily_ops_run_id!=d.id
                OR a.parent_daily_ops_attempt!=d.attempt_count)""",(tenant_id,)).fetchone()[0]
            bad_proposals=conn.execute("""SELECT COUNT(*) FROM proposals p JOIN daily_ops_runs d
              ON d.tenant_id=p.tenant_id AND d.id=p.daily_ops_run_id JOIN agent_runs a
              ON a.tenant_id=p.tenant_id AND a.id=p.agent_run_id WHERE p.tenant_id=?
              AND (d.status!='completed' OR a.review_status!='approved' OR d.agent_run_id!=a.id)""",(tenant_id,)).fetchone()[0]
        if eligible==0:
            return [{"name":"eligible_workflows","status":"blocked","code":"NO_ELIGIBLE_WORKFLOW_DATA","count":0}]
        return [
            {"name":"eligible_workflows","status":"passed","code":"OK","count":eligible},
            {"name":"evaluation_coverage","status":"passed" if coverage==eligible else "failed","code":"OK" if coverage==eligible else "EVALUATION_COVERAGE_MISSING","count":coverage},
            {"name":"evaluation_current_version","status":"passed" if current==eligible else "failed","code":"OK" if current==eligible else "EVALUATOR_VERSION_STALE","count":current},
            {"name":"latest_evaluation_pass","status":"passed" if evaluated==eligible else "failed","code":"OK" if evaluated==eligible else "LATEST_EVALUATION_FAILED","count":evaluated},
            {"name":"daily_reviewer_lineage","status":"passed" if bad_daily==0 else "failed","code":"OK" if bad_daily==0 else "DAILY_LINEAGE_INVALID","count":bad_daily},
            {"name":"proposal_reviewer_lineage","status":"passed" if bad_proposals==0 else "failed","code":"OK" if bad_proposals==0 else "PROPOSAL_LINEAGE_INVALID","count":bad_proposals},
        ]

    def run(self, principal: Principal, kind: str, idempotency_key: str, request_id: str) -> dict[str,Any]:
        self.auth.require(principal,"admin")
        if kind not in {"eval","security"}: raise ValidationError("kind must be eval or security")
        run,replayed=self.db.create_assurance_run(principal.tenant_id,kind,idempotency_key,principal.user_id)
        if replayed:
            if run["status"]!="running": return self.db.get_assurance_run(principal.tenant_id,run["id"])
            claimed=self.db.claim_assurance_run(principal.tenant_id,run["id"])
            if not claimed: return self.db.get_assurance_run(principal.tenant_id,run["id"])
            run=claimed
        try:
            checks=self._eval_checks(principal.tenant_id) if kind=="eval" else self._security_checks(principal.tenant_id)
            statuses={item["status"] for item in checks}
            status="failed" if "failed" in statuses else ("blocked" if "blocked" in statuses else "passed")
            result=self.db.finish_assurance_run(principal.tenant_id,run["id"],status,checks,{"check_count":len(checks),"passed_count":sum(c["status"]=="passed" for c in checks)},expected_attempt=run["attempt_count"],lease_token=run["lease_token"],audit_actor_user_id=principal.user_id,audit_request_id=request_id)
        except Exception as exc:
            log.error("assurance_run_failed kind=%s error_type=%s",kind,type(exc).__name__)
            result=self.db.finish_assurance_run(principal.tenant_id,run["id"],"failed",[{"name":"execution","status":"failed","code":"INTERNAL_ERROR","error_type":type(exc).__name__}],{"check_count":1,"passed_count":0},expected_attempt=run["attempt_count"],lease_token=run["lease_token"],audit_actor_user_id=principal.user_id,audit_request_id=request_id)
        return result
