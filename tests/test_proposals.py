from __future__ import annotations

import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.message import Message
from pathlib import Path

import pytest

from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.errors import (
    AuthorizationError,
    ConflictError,
    ExternalServiceError,
    NotFoundError,
    ValidationError,
)
from ecommerce_ai_skills.runtime.proposals import ProposalService
from ecommerce_ai_skills.runtime.storage import Database


class Provider:
    def configuration(self):
        return "proposal_fixture", "proposal-fixture-v1"

    def complete(self, *, agent_name, payload, **_):
        if agent_name == "store_manager":
            source = payload["evidence_catalog"][0]
            return {
                "executive_summary": "One controlled priority.",
                "priorities": [{
                    "rank": 1, "title": "Review current performance",
                    "why_now": "Current evidence requires a controlled follow-up.",
                    "evidence_refs": [source["source_id"]],
                    "platforms": [source["platform"]],
                    "expected_impact": "Validate the operating response.",
                    "confidence": "medium", "recommended_owner": "human_operator",
                    "downstream_action": "Prepare a proposal.",
                    "action_type": "external_change", "requires_approval": True,
                    "metric_claim": {"operation": "none", "observation_refs": []},
                }],
                "risks": [], "limitations": ["Limited to the selected source."],
            }
        if agent_name == "operations_reviewer":
            source = payload["evidence_catalog"][0]
            return {
                "verdict": "approved", "issues": [],
                "evidence_refs": [source["source_id"]],
                "limitations": payload["manager_report"]["limitations"],
            }
        platform = payload["target_platform"]
        evidence = payload.get("evidence") or []
        source_id = evidence[0]["source_id"] if evidence else next(
            finding["evidence_refs"][0]
            for result in payload["specialist_findings"].values()
            for finding in result["findings"]
        )
        return {
            "platform": platform, "summary": "Bound finding.",
            "findings": [{
                "title": "Review", "severity": "warning", "confidence": "medium",
                "evidence_refs": [source_id], "recommendation": "Review it.",
            }], "data_gaps": [],
        }


def make_context(tmp_path: Path, *, platform: str = "amazon"):
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"), agent_provider=Provider())
    bootstrap = app.bootstrap("Proposal tenant", "owner@example.com")
    owner = app.auth.authenticate(bootstrap["api_key"])
    report_type = "amazon_business_report" if platform == "amazon" else "shopify_orders"
    graph = app.agent_graphs.ensure_default(owner)
    schedule = app.daily_ops.create(
        owner, name=f"{platform} daily", platform=platform,
        objective="Review the current operating priorities for today.",
        timezone_name="UTC", local_time="00:01", graph_version_id=graph["id"],
        evidence_selectors=[{"report_type": report_type}], max_source_age_hours=72,
        enabled=True, request_id="schedule",
    )
    today = datetime.now(timezone.utc).date()
    observed = (datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
                - timedelta(hours=1)).isoformat(timespec="seconds")
    evidence, _ = app.db.create_evidence_import(
        owner.tenant_id, owner.user_id, "source", platform=platform,
        report_type=report_type, filename="daily.csv", observed_at=observed,
        sha256="a" * 64, delimiter=",", rows=[{"id": "1", "value": "10"}],
        columns=["id", "value"], column_mapping={"id": "id", "value": "value"},
        blank_rows_skipped=0, formula_cells=0, media_type="text/csv", byte_size=10,
        object_key="objects/source", sheet_name=None,
    )
    run = app.daily_ops.trigger(owner, schedule["id"], "trigger", datetime.now(timezone.utc).date().isoformat())
    completed = app.daily_ops.execute(owner, run["id"], "execute")
    if completed["status"] != "completed":
        raise AssertionError(repr(app.db.get_agent_run_bundle(owner.tenant_id, completed["agent_run_id"])))
    return app, owner, completed, ProposalService(app.db, app.auth, app.actions)


def expiry(days: int = 1) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat(timespec="seconds")


def create_proposal(
    service, owner, run, *, key="proposal", risk="low", operation="human.review",
    payload=None, expires_at=None,
):
    return service.create(
        owner, daily_ops_run_id=run["id"], priority_rank=1, operation=operation,
        payload=payload or {"instructions": "Review and record the decision."}, risk=risk,
        rollback_plan="No external change; close the review record.",
        idempotency_key=key, expires_at=expires_at or expiry(), request_id=f"create-{key}",
    )


def admin(app, owner, email: str):
    user = app.auth.create_user(owner, email, "admin")
    return app.db.principal_for_user(owner.tenant_id, user["id"])


def test_schema_v17_migrates_to_v18_and_tenant_constraints(tmp_path: Path):
    path = tmp_path / "migration.sqlite"
    db = Database(path)
    with db.connect() as conn:
        conn.execute("DROP TABLE proposal_executions")
        conn.execute("DROP TABLE proposal_decisions")
        conn.execute("DROP TABLE proposal_versions")
        conn.execute("DROP TABLE proposals")
        conn.execute("UPDATE runtime_meta SET value='17' WHERE key='schema_version'")
    migrated = Database(path)
    assert migrated.readiness()["schema_version"] == 20
    app, owner, run, service = make_context(tmp_path / "source")
    other = app.bootstrap("Other", "other@example.com")
    outsider = app.auth.authenticate(other["api_key"])
    with pytest.raises(NotFoundError):
        service.create(
            outsider, daily_ops_run_id=run["id"], priority_rank=1,
            operation="human.review", payload={"instructions": "Review it."}, risk="low",
            rollback_plan="Close it.", idempotency_key="cross", expires_at=expiry(), request_id="cross",
        )
    proposal = create_proposal(service, owner, run)
    with app.db.connect() as conn, pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE proposal_versions SET risk='critical' WHERE id=?", (proposal["version_id"],))


def test_create_idempotency_hash_validation_and_persistence(tmp_path: Path):
    app, owner, run, service = make_context(tmp_path)
    original_expiry = expiry()
    first = create_proposal(service, owner, run, expires_at=original_expiry)
    replay = create_proposal(service, owner, run, expires_at=original_expiry)
    assert replay["id"] == first["id"]
    assert len(first["payload_hash"]) == len(first["content_hash"]) == 64
    with pytest.raises(ConflictError, match="different proposal content"):
        create_proposal(
            service, owner, run, payload={"instructions": "Different review."},
            expires_at=original_expiry,
        )
    with pytest.raises(ValidationError, match="credentials"):
        create_proposal(service, owner, run, key="secret", payload={"instructions": "Review", "api_key": "bad"})
    with pytest.raises(ValidationError, match="NaN"):
        create_proposal(
            service, owner, run, key="nan", operation="amazon_ads.campaign_update",
            payload={"external_account_id": "ads", "campaign_id": "c", "changes": {"budget": float("nan")}},
        )
    with pytest.raises(ValidationError, match="not installed"):
        create_proposal(
            service, owner, run, key="report-type", operation="amazon_spapi.import_report",
            payload={"external_account_id": "sp", "report_id": "r", "evidence_report_type": "unknown"},
        )
    reloaded = ProposalService(Database(app.db.path), app.auth, app.actions)
    assert reloaded.get(owner, first["id"])["content_hash"] == first["content_hash"]
    revised = service.revise(
        owner, first["id"], expected_version=1,
        title="Revised after the original idempotent create", request_id="revise-after-create",
    )
    original_replay = create_proposal(service, owner, run, expires_at=original_expiry)
    assert original_replay["id"] == first["id"]
    assert original_replay["version"] == revised["version"] == 2


def test_self_approval_quorum_revision_rejection_and_expiry(tmp_path: Path, monkeypatch):
    app, owner, run, service = make_context(tmp_path)
    one, two = admin(app, owner, "one@example.com"), admin(app, owner, "two@example.com")
    low = create_proposal(service, owner, run, key="low")
    low = service.submit(owner, low["id"], expected_version=1, request_id="submit-low")
    with pytest.raises(AuthorizationError):
        service.decide(owner, low["id"], expected_version=1, decision="approve", comment="self", request_id="self")
    low = service.decide(one, low["id"], expected_version=1, decision="approve", comment="approved", request_id="approve-low")
    assert low["status"] == "approved" and low["approval_count"] == 1
    replay = service.decide(one, low["id"], expected_version=1, decision="approve", comment="approved", request_id="approve-low-replay")
    assert replay["approval_count"] == 1

    high = create_proposal(service, owner, run, key="high", risk="high")
    service.submit(owner, high["id"], expected_version=1, request_id="submit-high")
    partial = service.decide(one, high["id"], expected_version=1, decision="approve", comment="first", request_id="first")
    assert partial["status"] == "submitted" and partial["approval_count"] == 1
    with app.db.connect() as conn, pytest.raises(sqlite3.IntegrityError, match="quorum"):
        conn.execute("UPDATE proposals SET status='approved' WHERE id=?", (high["id"],))
    approved = service.decide(two, high["id"], expected_version=1, decision="approve", comment="second", request_id="second")
    assert approved["status"] == "approved" and approved["approval_count"] == 2

    rejected = create_proposal(service, owner, run, key="reject")
    service.submit(owner, rejected["id"], expected_version=1, request_id="submit-reject")
    rejected = service.decide(one, rejected["id"], expected_version=1, decision="revision_required", comment="add rollback", request_id="revise-decision")
    revised = service.revise(owner, rejected["id"], expected_version=1, rollback_plan="A materially revised rollback plan.", request_id="revise")
    assert revised["version"] == 2 and revised["status"] == "draft" and revised["approval_count"] == 0
    assert [item["version"] for item in revised["versions"]] == [1, 2]
    assert revised["content_hash"] != rejected["content_hash"]
    service.submit(owner, revised["id"], expected_version=2, request_id="submit-revised")
    future_now = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(timespec="seconds")
    monkeypatch.setattr("ecommerce_ai_skills.runtime.proposals.utc_now", lambda: future_now)
    assert service.get(owner, revised["id"])["status"] == "submitted"
    with app.db.connect() as conn:
        assert conn.execute("SELECT status FROM proposals WHERE id=?", (revised["id"],)).fetchone()[0] == "submitted"
    with pytest.raises(ConflictError):
        service.decide(one, revised["id"], expected_version=2, decision="approve", comment="late", request_id="late")
    with app.db.connect() as conn:
        assert conn.execute("SELECT status FROM proposals WHERE id=?", (revised["id"],)).fetchone()[0] == "expired"


def test_only_creator_can_revise_or_submit(tmp_path: Path, monkeypatch):
    app, owner, run, service = make_context(tmp_path)
    operator_user = app.auth.create_user(owner, "operator@example.com", "operator")
    operator = app.db.principal_for_user(owner.tenant_id, operator_user["id"])
    proposal = create_proposal(service, owner, run)
    with pytest.raises(AuthorizationError):
        service.revise(operator, proposal["id"], expected_version=1, title="Unauthorized edit", request_id="edit")
    with pytest.raises(AuthorizationError):
        service.submit(operator, proposal["id"], expected_version=1, request_id="submit")
    future_now = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(timespec="seconds")
    monkeypatch.setattr("ecommerce_ai_skills.runtime.proposals.utc_now", lambda: future_now)
    with pytest.raises(ConflictError):
        service.submit(owner, proposal["id"], expected_version=1, request_id="expired-submit")
    assert service.get(owner, proposal["id"])["status"] == "expired"
    with pytest.raises(ConflictError):
        service.revise(owner, proposal["id"], expected_version=1, title="Cannot revive", request_id="expired-revise")


def test_concurrent_approvals_ads_block_and_fenced_execution(tmp_path: Path):
    app, owner, run, service = make_context(tmp_path)
    one, two = admin(app, owner, "one@example.com"), admin(app, owner, "two@example.com")
    proposal = create_proposal(
        service, owner, run, key="ads", risk="high", operation="amazon_ads.campaign_update",
        payload={"external_account_id": "ads-1", "campaign_id": "c-1", "changes": {"state": "paused"}},
    )
    service.submit(owner, proposal["id"], expected_version=1, request_id="submit")
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(
            lambda item: service.decide(item[0], proposal["id"], expected_version=1,
                                        decision="approve", comment=item[1], request_id=item[1]),
            [(one, "one"), (two, "two")],
        ))
    assert any(item["status"] == "approved" for item in results)
    calls = []
    service.actions.request = lambda *a, **k: calls.append("request")  # type: ignore[method-assign]
    blocked = service.execute(owner, proposal["id"], expected_version=1, idempotency_key="execute-ads", request_id="execute")
    assert blocked["status"] == "blocked" and blocked["error_code"] == "AMAZON_ADS_CAPABILITY_UNAVAILABLE"
    assert calls == []

    human = create_proposal(service, owner, run, key="fence")
    service.submit(owner, human["id"], expected_version=1, request_id="human-submit")
    service.decide(one, human["id"], expected_version=1, decision="approve", comment="go", request_id="human-approve")
    executed = service.execute(owner, human["id"], expected_version=1, idempotency_key="human-execute", request_id="human-execute")
    assert executed["status"] == "executed"
    assert service.execute(owner, human["id"], expected_version=1, idempotency_key="human-execute", request_id="replay")["id"] == executed["id"]


def test_safe_action_path_is_reused_without_bypass(tmp_path: Path):
    app, owner, run, service = make_context(tmp_path)
    approver = admin(app, owner, "approver@example.com")
    proposal = create_proposal(
        service, owner, run, key="safe", operation="amazon_spapi.import_report",
        payload={"external_account_id": "sp-1", "report_id": "r-1", "evidence_report_type": "amazon_business_report"},
    )
    service.submit(owner, proposal["id"], expected_version=1, request_id="submit")
    service.decide(approver, proposal["id"], expected_version=1, decision="approve", comment="go", request_id="approve")
    account_id = app.db.add_connector_account(
        owner.tenant_id, "amazon_spapi", "sp-1",
        {"region": "na", "marketplace_ids": ["ATVPDKIKX0DER"],
         "lwa_client_id_ref": "TEST_LWA_CLIENT_ID",
         "lwa_client_secret_ref": "TEST_LWA_CLIENT_SECRET",
         "lwa_refresh_token_ref": "TEST_LWA_REFRESH_TOKEN"},
    )
    app.db.set_connector_account_health(owner.tenant_id, account_id, "healthy")
    assert service.get(owner, proposal["id"])["capability_status"] == "available"
    calls = []
    def request(principal, operation, payload, key, request_id):
        calls.append(("request", principal.user_id, operation, key))
        action, _ = app.db.create_action(
            principal.tenant_id, key, operation, payload, principal.user_id
        )
        return action
    def approve(principal, action_id, request_id):
        calls.append(("approve", principal.user_id, action_id))
        return app.db.transition_action(
            principal.tenant_id, action_id, "requested", "approved",
            approved_by=principal.user_id,
        )
    def execute(principal, action_id, request_id):
        calls.append(("execute", principal.user_id, action_id))
        return {"id": action_id, "status": "executed", "result": {"records": 3}}
    service.actions.request, service.actions.approve, service.actions.execute = request, approve, execute  # type: ignore[method-assign]
    result = service.execute(owner, proposal["id"], expected_version=1, idempotency_key="safe-execute", request_id="execute")
    assert result["status"] == "executed"
    assert [item[0] for item in calls] == ["request", "approve", "execute"]
    assert calls[0][1] == owner.user_id and calls[1][1] == approver.user_id
    with pytest.raises(ConflictError, match="another Idempotency-Key"):
        service.execute(owner, proposal["id"], expected_version=1, idempotency_key="another-key", request_id="execute-again")
    assert len(calls) == 3


def test_unavailable_safe_connector_blocks_before_action_calls(tmp_path: Path):
    app, owner, run, service = make_context(tmp_path)
    approver = admin(app, owner, "approver@example.com")
    proposal = create_proposal(
        service, owner, run, key="missing", operation="amazon_spapi.import_report",
        payload={"external_account_id": "missing", "report_id": "r-1", "evidence_report_type": "amazon_business_report"},
    )
    service.submit(owner, proposal["id"], expected_version=1, request_id="submit")
    service.decide(approver, proposal["id"], expected_version=1, decision="approve", comment="go", request_id="approve")
    calls = []
    service.actions.request = lambda *args, **kwargs: calls.append("request")  # type: ignore[method-assign]
    assert service.get(owner, proposal["id"])["capability_status"] == "unavailable"
    execution = service.execute(owner, proposal["id"], expected_version=1, idempotency_key="missing-execute", request_id="execute")
    assert execution["status"] == "blocked"
    assert execution["error_code"] == "CONNECTOR_CAPABILITY_UNAVAILABLE"
    assert execution["capability_block"]["connector_calls"] == 0
    assert calls == []


def test_execution_lease_fencing_and_attempt_exhaustion(tmp_path: Path):
    app, owner, run, service = make_context(tmp_path)
    approver = admin(app, owner, "approver@example.com")
    proposal = create_proposal(service, owner, run, key="lease")
    service.submit(owner, proposal["id"], expected_version=1, request_id="submit")
    service.decide(approver, proposal["id"], expected_version=1, decision="approve", comment="go", request_id="approve")
    original = service._run_execution
    service._run_execution = lambda principal, execution, request_id: execution  # type: ignore[method-assign]
    pending = service.execute(owner, proposal["id"], expected_version=1, idempotency_key="lease-execute", request_id="enqueue")
    service._run_execution = original  # type: ignore[method-assign]
    with app.db.connect() as conn, pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE proposal_executions SET status='executed' WHERE id=?", (pending["id"],))
    first = service._claim_execution(owner.tenant_id, pending["id"])
    assert first is not None and first["lease_token"]
    assert service._claim_execution(owner.tenant_id, pending["id"]) is None
    with pytest.raises(ConflictError, match="lease was lost"):
        service._finish_execution(owner.tenant_id, pending["id"], attempt=first["attempt_count"], token="wrong", status="executed", result={})
    with app.db.connect() as conn:
        conn.execute(
            """UPDATE proposal_executions SET attempt_count=max_attempts,lease_until=?
               WHERE id=?""",
            ((datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat(), pending["id"]),
        )
    assert service._claim_execution(owner.tenant_id, pending["id"]) is None
    exhausted = service.get_execution(owner, pending["id"])
    assert exhausted["status"] == "failed" and exhausted["error_code"] == "MAX_ATTEMPTS_EXHAUSTED"
    assert "lease_token" not in exhausted
    with app.db.connect() as conn, pytest.raises(sqlite3.IntegrityError, match="only permits retry"):
        conn.execute(
            """UPDATE proposal_executions SET status='pending',last_retry_idempotency_key='raw-bypass',
                      error_code=NULL,error_message=NULL,completed_at=NULL
               WHERE id=?""",
            (pending["id"],),
        )
    with app.db.connect() as conn, pytest.raises(sqlite3.IntegrityError, match="durable retry intent"):
        conn.execute("UPDATE proposals SET status='approved' WHERE id=?", (proposal["id"],))
    with pytest.raises(ConflictError, match="attempt limit"):
        service.retry(owner, proposal["id"], expected_version=1, idempotency_key="retry-max", request_id="retry")


def test_expiry_discovered_inside_mutation_transaction_commits_and_audits(tmp_path: Path, monkeypatch):
    app, owner, run, service = make_context(tmp_path)
    approver = admin(app, owner, "boundary-approver@example.com")

    def cross_boundary(proposal):
        deadline = datetime.fromisoformat(proposal["expires_at"])
        instants = iter([
            (deadline - timedelta(seconds=1)).isoformat(timespec="seconds"),
            (deadline + timedelta(seconds=1)).isoformat(timespec="seconds"),
        ])
        monkeypatch.setattr("ecommerce_ai_skills.runtime.proposals.utc_now", lambda: next(instants))

    submit_candidate = create_proposal(service, owner, run, key="submit-boundary")
    cross_boundary(submit_candidate)
    with pytest.raises(ConflictError, match="expired"):
        service.submit(owner, submit_candidate["id"], expected_version=1, request_id="submit-boundary")
    with app.db.connect() as conn:
        assert conn.execute("SELECT status FROM proposals WHERE id=?", (submit_candidate["id"],)).fetchone()[0] == "expired"

    monkeypatch.undo()
    revise_candidate = create_proposal(service, owner, run, key="revise-boundary")
    cross_boundary(revise_candidate)
    with pytest.raises(ConflictError, match="expired"):
        service.revise(
            owner, revise_candidate["id"], expected_version=1,
            title="A revision crossing the expiry boundary", request_id="revise-boundary",
        )
    with app.db.connect() as conn:
        assert conn.execute("SELECT status FROM proposals WHERE id=?", (revise_candidate["id"],)).fetchone()[0] == "expired"
        assert conn.execute("SELECT COUNT(*) FROM proposal_versions WHERE proposal_id=?", (revise_candidate["id"],)).fetchone()[0] == 1
    monkeypatch.undo()
    decision_candidate = create_proposal(service, owner, run, key="decision-boundary")
    service.submit(owner, decision_candidate["id"], expected_version=1, request_id="decision-submit")
    cross_boundary(decision_candidate)
    with pytest.raises(ConflictError, match="expired"):
        service.decide(
            approver, decision_candidate["id"], expected_version=1,
            decision="approve", comment="too late", request_id="decision-boundary",
        )
    assert service.get(owner, decision_candidate["id"])["status"] == "expired"
    monkeypatch.undo()
    execution_candidate = create_proposal(service, owner, run, key="execution-boundary")
    service.submit(owner, execution_candidate["id"], expected_version=1, request_id="execution-submit")
    service.decide(
        approver, execution_candidate["id"], expected_version=1,
        decision="approve", comment="approved", request_id="execution-approve",
    )
    cross_boundary(execution_candidate)
    with pytest.raises(ConflictError, match="expired"):
        service.execute(
            owner, execution_candidate["id"], expected_version=1,
            idempotency_key="execution-boundary", request_id="execution-boundary",
        )
    assert service.get(owner, execution_candidate["id"])["status"] == "expired"
    assert service.list_executions(owner, proposal_id=execution_candidate["id"]) == []
    expirations = [event for event in app.db.list_audit(owner.tenant_id, 500) if event["action"] == "proposal.expire"]
    assert {event["resource_id"] for event in expirations} >= {
        submit_candidate["id"], revise_candidate["id"],
        decision_candidate["id"], execution_candidate["id"],
    }


def test_status_filter_is_pushed_down_beyond_201_newer_rows(tmp_path: Path):
    app, owner, run, service = make_context(tmp_path)
    oldest_draft = create_proposal(service, owner, run, key="oldest-draft")
    for index in range(202):
        proposal = create_proposal(service, owner, run, key=f"newer-{index}")
        service.submit(owner, proposal["id"], expected_version=1, request_id=f"submit-{index}")
    drafts = service.list(owner, status="draft", limit=10)
    assert [item["id"] for item in drafts] == [oldest_draft["id"]]


def test_proposal_http_end_to_end_rbac_tenant_idempotency_and_retry(tmp_path: Path):
    app, owner, run, _ = make_context(tmp_path)
    owner_key = app.auth.issue_key(owner.tenant_id, owner.user_id)
    admin_user = app.auth.create_user(owner, "api-admin@example.com", "admin")
    admin_key = app.auth.issue_key(owner.tenant_id, admin_user["id"])
    viewer_user = app.auth.create_user(owner, "api-viewer@example.com", "viewer")
    viewer_key = app.auth.issue_key(owner.tenant_id, viewer_user["id"])
    outsider = app.bootstrap("API outsider", "outsider@example.com")

    class Handler(_Handler):
        def __init__(self, method, path, key, body=None, idempotency="proposal-api"):
            self.path = path
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {key}"
            self.headers["Idempotency-Key"] = idempotency
            self.method = method
            self.body = body or {}
            self.out = None

        @property
        def app(self):
            return app

        def _body(self):
            return self.body

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value)

        def run(self):
            getattr(self, f"do_{self.method}")()
            return self.out

    expires_at = expiry()
    create_body = {
        "daily_ops_run_id": run["id"], "priority_rank": 1,
        "operation": "human.review",
        "payload": {"instructions": "Review the API-created priority."},
        "risk": "low", "rollback_plan": "Close the local review record.",
        "expires_at": expires_at,
    }
    assert Handler("POST", "/v1/proposals", viewer_key, create_body).run()[0] == 403
    created = Handler("POST", "/v1/proposals", owner_key, create_body).run()
    assert created[0] == 201 and created[1]["status"] == "draft"
    proposal_id = created[1]["id"]
    conflicting = {**create_body, "rollback_plan": "Different content must conflict."}
    assert Handler("POST", "/v1/proposals", owner_key, conflicting).run()[0] == 409
    assert Handler("GET", f"/v1/proposals/{proposal_id}", outsider["api_key"]).run()[0] == 404
    assert Handler(
        "POST", f"/v1/proposals/{proposal_id}/submit", owner_key,
        {"expected_version": 1, "unexpected": True},
    ).run()[0] == 422

    revised = Handler(
        "PATCH", f"/v1/proposals/{proposal_id}", owner_key,
        {"expected_version": 1, "title": "API revised controlled priority"},
    ).run()
    assert revised[0] == 200 and revised[1]["version"] == 2
    assert Handler(
        "POST", f"/v1/proposals/{proposal_id}/submit", owner_key,
        {"expected_version": 2},
    ).run()[0] == 200
    assert Handler(
        "POST", f"/v1/proposals/{proposal_id}/decisions", viewer_key,
        {"expected_version": 2, "decision": "approve", "comment": "viewer"},
    ).run()[0] == 403
    revision_required = Handler(
        "POST", f"/v1/proposals/{proposal_id}/decisions", admin_key,
        {"expected_version": 2, "decision": "revision_required", "comment": "clarify"},
    ).run()
    assert revision_required[0] == 200 and revision_required[1]["status"] == "revision_required"
    revised_again = Handler(
        "PATCH", f"/v1/proposals/{proposal_id}", owner_key,
        {"expected_version": 2, "rollback_plan": "Clarified local-only rollback plan."},
    ).run()
    assert revised_again[0] == 200 and revised_again[1]["version"] == 3
    Handler("POST", f"/v1/proposals/{proposal_id}/submit", owner_key, {"expected_version": 3}).run()
    approved = Handler(
        "POST", f"/v1/proposals/{proposal_id}/decisions", admin_key,
        {"expected_version": 3, "decision": "approve", "comment": "approved"},
    ).run()
    assert approved[0] == 200 and approved[1]["status"] == "approved"
    executed = Handler(
        "POST", f"/v1/proposals/{proposal_id}/execute", owner_key,
        {"expected_version": 3}, idempotency="proposal-api-execute",
    ).run()
    assert executed[0] == 201 and executed[1]["status"] == "executed"
    replay = Handler(
        "POST", f"/v1/proposals/{proposal_id}/execute", owner_key,
        {"expected_version": 3}, idempotency="proposal-api-execute",
    ).run()
    assert replay[1]["id"] == executed[1]["id"]

    rejected = Handler(
        "POST", "/v1/proposals", owner_key, create_body, idempotency="proposal-api-reject"
    ).run()[1]
    Handler("POST", f"/v1/proposals/{rejected['id']}/submit", owner_key, {"expected_version": 1}).run()
    rejected = Handler(
        "POST", f"/v1/proposals/{rejected['id']}/decisions", admin_key,
        {"expected_version": 1, "decision": "reject", "comment": "rejected"},
    ).run()
    assert rejected[0] == 200 and rejected[1]["status"] == "rejected"

    account_id = app.db.add_connector_account(
        owner.tenant_id, "amazon_spapi", "api-sp",
        {"region": "na", "marketplace_ids": ["ATVPDKIKX0DER"],
         "lwa_client_id_ref": "API_LWA_CLIENT_ID",
         "lwa_client_secret_ref": "API_LWA_CLIENT_SECRET",
         "lwa_refresh_token_ref": "API_LWA_REFRESH_TOKEN"},
    )
    app.db.set_connector_account_health(owner.tenant_id, account_id, "healthy")
    safe_body = {
        **create_body,
        "operation": "amazon_spapi.import_report",
        "payload": {"external_account_id": "api-sp", "report_id": "R-API",
                    "evidence_report_type": "amazon_business_report"},
    }
    safe = Handler("POST", "/v1/proposals", owner_key, safe_body, idempotency="proposal-api-safe").run()[1]
    Handler("POST", f"/v1/proposals/{safe['id']}/submit", owner_key, {"expected_version": 1}).run()
    Handler(
        "POST", f"/v1/proposals/{safe['id']}/decisions", admin_key,
        {"expected_version": 1, "decision": "approve", "comment": "safe"},
    ).run()
    original_execute = app.actions.execute
    app.actions.execute = lambda *args, **kwargs: (_ for _ in ()).throw(
        ExternalServiceError("simulated connector failure")
    )  # type: ignore[method-assign]
    failed = Handler(
        "POST", f"/v1/proposals/{safe['id']}/execute", owner_key,
        {"expected_version": 1}, idempotency="proposal-api-safe-execute",
    ).run()
    assert failed[0] == 502
    assert app.proposals.get(owner, safe["id"])["status"] == "failed"
    retry_a_failed = Handler(
        "POST", f"/v1/proposals/{safe['id']}/retry", owner_key,
        {"expected_version": 1}, idempotency="proposal-api-retry-a",
    ).run()
    assert retry_a_failed[0] == 502
    failed_after_a = app.proposals.get(owner, safe["id"])["executions"][0]
    with app.db.connect() as conn, pytest.raises(sqlite3.IntegrityError, match="only permits retry"):
        conn.execute(
            """UPDATE proposal_executions SET status='pending',
                      error_code=NULL,error_message=NULL,completed_at=NULL
               WHERE id=?""",
            (failed_after_a["id"],),
        )
    app.actions.execute = lambda principal, action_id, request_id: {
        "id": action_id, "status": "executed", "result": {"records": 1}
    }  # type: ignore[method-assign]
    retried = Handler(
        "POST", f"/v1/proposals/{safe['id']}/retry", owner_key,
        {"expected_version": 1}, idempotency="proposal-api-retry-b",
    ).run()
    assert retried[0] == 201 and retried[1]["status"] == "executed"
    final_attempt = retried[1]["attempt_count"]
    replay_old_key = Handler(
        "POST", f"/v1/proposals/{safe['id']}/retry", owner_key,
        {"expected_version": 1}, idempotency="proposal-api-retry-a",
    ).run()
    assert replay_old_key[0] == 201
    assert replay_old_key[1]["attempt_count"] == final_attempt
    app.actions.execute = original_execute  # type: ignore[method-assign]
    assert Handler(
        "GET", f"/v1/proposal-executions?proposal_id={proposal_id}", outsider["api_key"]
    ).run()[0] == 404


def test_pending_execution_expires_before_claim_and_makes_zero_connector_calls(tmp_path: Path, monkeypatch):
    app, owner, run, service = make_context(tmp_path)
    approver = admin(app, owner, "expiry-approver@example.com")
    proposal = create_proposal(service, owner, run, key="pending-expiry")
    service.submit(owner, proposal["id"], expected_version=1, request_id="submit")
    service.decide(approver, proposal["id"], expected_version=1, decision="approve", comment="go", request_id="approve")
    original_runner = service._run_execution
    service._run_execution = lambda principal, execution, request_id: execution  # type: ignore[method-assign]
    pending = service.execute(owner, proposal["id"], expected_version=1, idempotency_key="pending-expiry-execute", request_id="queue")
    service._run_execution = original_runner  # type: ignore[method-assign]
    calls = []
    service.actions.request = lambda *args, **kwargs: calls.append("request")  # type: ignore[method-assign]
    after_expiry = (datetime.fromisoformat(proposal["expires_at"]) + timedelta(seconds=1)).isoformat(timespec="seconds")
    monkeypatch.setattr("ecommerce_ai_skills.runtime.proposals.utc_now", lambda: after_expiry)
    with pytest.raises(ConflictError, match="expired before execution claim"):
        service.execute(owner, proposal["id"], expected_version=1, idempotency_key="pending-expiry-execute", request_id="resume")
    terminal = service.get_execution(owner, pending["id"])
    assert terminal["status"] == "failed" and terminal["error_code"] == "PROPOSAL_EXPIRED"
    assert service.get(owner, proposal["id"])["status"] == "expired"
    assert calls == []


def test_stale_unlinked_claim_expires_without_recovery_and_retry_does_not(tmp_path: Path, monkeypatch):
    app, owner, run, service = make_context(tmp_path)
    approver = admin(app, owner, "recovery-approver@example.com")
    proposal = create_proposal(service, owner, run, key="stale-recovery")
    service.submit(owner, proposal["id"], expected_version=1, request_id="submit")
    service.decide(approver, proposal["id"], expected_version=1, decision="approve", comment="go", request_id="approve")
    original_runner = service._run_execution
    service._run_execution = lambda principal, execution, request_id: execution  # type: ignore[method-assign]
    pending = service.execute(owner, proposal["id"], expected_version=1, idempotency_key="stale-execute", request_id="queue")
    service._run_execution = original_runner  # type: ignore[method-assign]
    claimed = service._claim_execution(owner.tenant_id, pending["id"], actor_user_id=owner.user_id)
    assert claimed is not None
    with app.db.connect() as conn:
        conn.execute(
            "UPDATE proposal_executions SET lease_until=? WHERE id=?",
            ((datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat(), pending["id"]),
        )
    after_expiry = (datetime.fromisoformat(proposal["expires_at"]) + timedelta(seconds=1)).isoformat(timespec="seconds")
    monkeypatch.setattr("ecommerce_ai_skills.runtime.proposals.utc_now", lambda: after_expiry)
    recovered = service.worker_run_once()["execution"]
    assert recovered["status"] == "failed"
    assert recovered["error_code"] == "PROPOSAL_EXPIRED"
    assert service.get(owner, proposal["id"])["status"] == "expired"

    monkeypatch.undo()
    retry_proposal = create_proposal(service, owner, run, key="retry-expiry")
    service.submit(owner, retry_proposal["id"], expected_version=1, request_id="retry-submit")
    service.decide(approver, retry_proposal["id"], expected_version=1, decision="approve", comment="go", request_id="retry-approve")
    service._run_execution = lambda principal, execution, request_id: execution  # type: ignore[method-assign]
    retry_pending = service.execute(owner, retry_proposal["id"], expected_version=1, idempotency_key="retry-expiry-execute", request_id="queue")
    service._run_execution = original_runner  # type: ignore[method-assign]
    retry_claim = service._claim_execution(owner.tenant_id, retry_pending["id"], actor_user_id=owner.user_id)
    service._finish_execution(
        owner.tenant_id, retry_pending["id"], attempt=retry_claim["attempt_count"],
        token=retry_claim["lease_token"], status="failed", error_code="TEST_FAILURE",
        error_message="failed before retry", actor_user_id=owner.user_id,
    )
    after_retry_expiry = (datetime.fromisoformat(retry_proposal["expires_at"]) + timedelta(seconds=1)).isoformat(timespec="seconds")
    monkeypatch.setattr("ecommerce_ai_skills.runtime.proposals.utc_now", lambda: after_retry_expiry)
    with pytest.raises(ConflictError):
        service.retry(owner, retry_proposal["id"], expected_version=1, idempotency_key="expired-retry", request_id="retry")
    assert service.get(owner, retry_proposal["id"])["status"] == "expired"


def test_stale_linked_action_reconciles_after_expiry_without_rebinding(tmp_path: Path, monkeypatch):
    app, owner, run, service = make_context(tmp_path)
    approver = admin(app, owner, "linked-approver@example.com")
    account_id = app.db.add_connector_account(
        owner.tenant_id, "amazon_spapi", "linked-sp",
        {"region": "na", "marketplace_ids": ["ATVPDKIKX0DER"],
         "lwa_client_id_ref": "LINKED_LWA_CLIENT_ID",
         "lwa_client_secret_ref": "LINKED_LWA_CLIENT_SECRET",
         "lwa_refresh_token_ref": "LINKED_LWA_REFRESH_TOKEN"},
    )
    app.db.set_connector_account_health(owner.tenant_id, account_id, "healthy")
    payload = {"external_account_id": "linked-sp", "report_id": "R-LINKED",
               "evidence_report_type": "amazon_business_report"}
    proposal = create_proposal(
        service, owner, run, key="linked-recovery",
        operation="amazon_spapi.import_report", payload=payload,
    )
    service.submit(owner, proposal["id"], expected_version=1, request_id="submit")
    service.decide(approver, proposal["id"], expected_version=1, decision="approve", comment="go", request_id="approve")
    original_runner = service._run_execution
    service._run_execution = lambda principal, execution, request_id: execution  # type: ignore[method-assign]
    pending = service.execute(owner, proposal["id"], expected_version=1, idempotency_key="linked-execute", request_id="queue")
    service._run_execution = original_runner  # type: ignore[method-assign]
    claim = service._claim_execution(owner.tenant_id, pending["id"], actor_user_id=owner.user_id)
    action = app.actions.request(
        owner, "amazon_spapi.import_report", payload,
        f"proposal-execution:{pending['id']}", "linked-action-request",
    )
    action = app.actions.approve(approver, action["id"], "linked-action-approve")
    with app.db.connect() as conn:
        conn.execute(
            """UPDATE proposal_executions SET action_id=?,lease_until=?
               WHERE id=? AND lease_token=?""",
            (action["id"], (datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat(),
             pending["id"], claim["lease_token"]),
        )
    calls = []
    app.actions.execute = lambda principal, action_id, request_id: (
        calls.append(action_id) or {"id": action_id, "status": "executed", "result": {"records": 1}}
    )  # type: ignore[method-assign]
    after_expiry = (datetime.fromisoformat(proposal["expires_at"]) + timedelta(seconds=1)).isoformat(timespec="seconds")
    monkeypatch.setattr("ecommerce_ai_skills.runtime.proposals.utc_now", lambda: after_expiry)
    recovered = service.worker_run_once()["execution"]
    assert recovered["status"] == "executed" and recovered["action_id"] == action["id"]
    assert calls == [action["id"]]


def test_l9_audit_write_failure_rolls_back_state_and_is_retryable(tmp_path: Path, monkeypatch):
    app, owner, run, service = make_context(tmp_path)
    original_audit = app.db.append_audit_tx

    def fail_create(conn, tenant_id, actor_user_id, request_id, action, *args, **kwargs):
        if action == "proposal.create":
            raise RuntimeError("audit unavailable")
        return original_audit(conn, tenant_id, actor_user_id, request_id, action, *args, **kwargs)

    monkeypatch.setattr(app.db, "append_audit_tx", fail_create)
    with pytest.raises(RuntimeError, match="audit unavailable"):
        create_proposal(service, owner, run, key="audit-create")
    assert service.list(owner) == []
    monkeypatch.setattr(app.db, "append_audit_tx", original_audit)
    proposal = create_proposal(service, owner, run, key="audit-create")

    def fail_submit(conn, tenant_id, actor_user_id, request_id, action, *args, **kwargs):
        if action == "proposal.submit":
            raise RuntimeError("audit unavailable")
        return original_audit(conn, tenant_id, actor_user_id, request_id, action, *args, **kwargs)

    monkeypatch.setattr(app.db, "append_audit_tx", fail_submit)
    with pytest.raises(RuntimeError, match="audit unavailable"):
        service.submit(owner, proposal["id"], expected_version=1, request_id="submit-fail")
    assert service.get(owner, proposal["id"])["status"] == "draft"
    monkeypatch.setattr(app.db, "append_audit_tx", original_audit)
    assert service.submit(owner, proposal["id"], expected_version=1, request_id="submit-retry")["status"] == "submitted"

    approver = admin(app, owner, "audit-approver@example.com")
    service.decide(approver, proposal["id"], expected_version=1, decision="approve", comment="go", request_id="approve")
    original_runner = service._run_execution
    service._run_execution = lambda principal, execution, request_id: execution  # type: ignore[method-assign]
    pending = service.execute(owner, proposal["id"], expected_version=1, idempotency_key="audit-execute", request_id="queue")
    service._run_execution = original_runner  # type: ignore[method-assign]

    def fail_terminal(conn, tenant_id, actor_user_id, request_id, action, resource_type, *args, **kwargs):
        if action == "proposal.execute" and resource_type == "proposal_execution":
            raise RuntimeError("terminal audit unavailable")
        return original_audit(
            conn, tenant_id, actor_user_id, request_id, action, resource_type, *args, **kwargs
        )

    monkeypatch.setattr(app.db, "append_audit_tx", fail_terminal)
    with pytest.raises(RuntimeError, match="terminal audit unavailable"):
        service._run_execution(owner, pending, "terminal-audit-fail")
    in_flight = service.get_execution(owner, pending["id"])
    assert in_flight["status"] == "executing" and in_flight["completed_at"] is None
    monkeypatch.setattr(app.db, "append_audit_tx", original_audit)
    with app.db.connect() as conn:
        conn.execute(
            "UPDATE proposal_executions SET lease_until=? WHERE id=?",
            ((datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat(), pending["id"]),
        )
    recovered = service.worker_run_once()["execution"]
    assert recovered["status"] == "executed"


def test_active_proposal_roles_and_terminal_execution_are_db_guarded(tmp_path: Path):
    app, owner, run, service = make_context(tmp_path)
    operator_user = app.auth.create_user(owner, "guard-operator@example.com", "operator")
    operator = app.db.principal_for_user(owner.tenant_id, operator_user["id"])
    approver = admin(app, owner, "guard-admin@example.com")
    proposal = create_proposal(service, operator, run, key="role-guard")
    with pytest.raises(ConflictError, match="active proposals"):
        app.auth.update_user_role(owner, operator.user_id, "viewer")
    with app.db.connect() as conn, pytest.raises(sqlite3.IntegrityError, match="role downgrade"):
        conn.execute("UPDATE users SET role='viewer' WHERE id=?", (operator.user_id,))
    with app.db.connect() as conn, pytest.raises(sqlite3.IntegrityError, match="immutable"):
        conn.execute("UPDATE proposals SET idempotency_key='changed' WHERE id=?", (proposal["id"],))
    service.submit(operator, proposal["id"], expected_version=1, request_id="submit")
    service.decide(approver, proposal["id"], expected_version=1, decision="approve", comment="go", request_id="approve")
    with pytest.raises(ConflictError, match="approved by this user"):
        app.auth.update_user_role(owner, approver.user_id, "operator")
    execution = service.execute(operator, proposal["id"], expected_version=1, idempotency_key="guard-execute", request_id="execute")
    with app.db.connect() as conn, pytest.raises(sqlite3.IntegrityError, match="immutable"):
        conn.execute("UPDATE proposal_executions SET result_json='{}' WHERE id=?", (execution["id"],))
    with app.db.connect() as conn, pytest.raises(sqlite3.IntegrityError, match="immutable"):
        conn.execute("DELETE FROM proposal_executions WHERE id=?", (execution["id"],))


def test_proposal_worker_cli_once_is_operable(tmp_path: Path):
    path = tmp_path / "worker.sqlite"
    result = subprocess.run(
        [sys.executable, "-m", "ecommerce_ai_skills.cli", "proposal-worker", "--db", str(path), "--once"],
        cwd=Path(__file__).resolve().parents[1], text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert Database(path).readiness()["schema_version"] == 20


def test_worker_survives_durable_connector_failure_and_processes_next_tick(tmp_path: Path, monkeypatch):
    app, owner, run, service = make_context(tmp_path)
    approver = admin(app, owner, "worker-approver@example.com")
    account_id = app.db.add_connector_account(
        owner.tenant_id, "amazon_spapi", "worker-sp",
        {"region": "na", "marketplace_ids": ["ATVPDKIKX0DER"],
         "lwa_client_id_ref": "WORKER_LWA_CLIENT_ID",
         "lwa_client_secret_ref": "WORKER_LWA_CLIENT_SECRET",
         "lwa_refresh_token_ref": "WORKER_LWA_REFRESH_TOKEN"},
    )
    app.db.set_connector_account_health(owner.tenant_id, account_id, "healthy")
    safe = create_proposal(
        service, owner, run, key="worker-first",
        operation="amazon_spapi.import_report",
        payload={"external_account_id": "worker-sp", "report_id": "R-WORKER",
                 "evidence_report_type": "amazon_business_report"},
    )
    human = create_proposal(service, owner, run, key="worker-second")
    for proposal in (safe, human):
        service.submit(owner, proposal["id"], expected_version=1, request_id=f"submit-{proposal['id']}")
        service.decide(approver, proposal["id"], expected_version=1, decision="approve", comment="go", request_id=f"approve-{proposal['id']}")
    original_runner = service._run_execution
    service._run_execution = lambda principal, execution, request_id: execution  # type: ignore[method-assign]
    earlier = (datetime.now(timezone.utc) - timedelta(seconds=2)).isoformat(timespec="seconds")
    monkeypatch.setattr("ecommerce_ai_skills.runtime.proposals.utc_now", lambda: earlier)
    first_pending = service.execute(owner, safe["id"], expected_version=1, idempotency_key="worker-first-execute", request_id="queue-first")
    monkeypatch.undo()
    second_pending = service.execute(owner, human["id"], expected_version=1, idempotency_key="worker-second-execute", request_id="queue-second")
    service._run_execution = original_runner  # type: ignore[method-assign]
    app.actions.execute = lambda *args, **kwargs: (_ for _ in ()).throw(
        ExternalServiceError("worker connector failure")
    )  # type: ignore[method-assign]
    first_tick = service.worker_run_once()
    assert first_tick["execution"]["id"] == first_pending["id"]
    assert first_tick["execution"]["status"] == "failed"
    second_tick = service.worker_run_once()
    assert second_tick["execution"]["id"] == second_pending["id"]
    assert second_tick["execution"]["status"] == "executed"
