from __future__ import annotations
import io,json,sqlite3
from email.message import Message
from pathlib import Path
import pytest
from ecommerce_ai_skills.runtime.api import RuntimeApplication,_Handler
from ecommerce_ai_skills.runtime.assurance import AssuranceService
from ecommerce_ai_skills.runtime.errors import AuthorizationError,ConflictError
from ecommerce_ai_skills.runtime.storage import AUDIT_GENESIS_HASH,Database,audit_event_hash

def test_audit_chain_is_tenant_scoped_immutable_and_detects_tamper(tmp_path:Path)->None:
    db=Database(tmp_path/"runtime.sqlite")
    a,ua=db.create_tenant("A","a@example.com"); b,ub=db.create_tenant("B","b@example.com")
    db.append_audit(a,ua,"r1","one","resource",None,"passed",{"count":1})
    db.append_audit(a,ua,"r2","two","resource","x","passed",{})
    assert db.verify_audit_chain(a)=={"valid":True,"event_count":2,"broken_at":None}
    listed=db.list_audit(a); assert listed[0]["previous_hash"]==listed[1]["event_hash"]
    with db.connect() as conn:
        row=conn.execute("SELECT * FROM audit_events WHERE tenant_id=? ORDER BY rowid DESC LIMIT 1",(a,)).fetchone()
        with pytest.raises(sqlite3.IntegrityError,match="immutable"): conn.execute("UPDATE audit_events SET outcome='failed' WHERE id=?",(row["id"],))
        with pytest.raises(sqlite3.IntegrityError,match="immutable"): conn.execute("DELETE FROM audit_events WHERE id=?",(row["id"],))
        event_id="raw-cross"; created=row["created_at"]; metadata="{}"
        digest=audit_event_hash(row["event_hash"],a,event_id,ub,"raw","raw","resource",None,"passed",metadata,created)
        with pytest.raises(sqlite3.IntegrityError,match="actor binding"):
            conn.execute("""INSERT INTO audit_events(id,tenant_id,actor_user_id,request_id,action,resource_type,resource_id,outcome,metadata_json,created_at,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (event_id,a,ub,"raw","raw","resource",None,"passed",metadata,created,row["event_hash"],digest))
    with db.transaction() as conn:
        conn.execute("DROP TRIGGER audit_events_immutable_update")
        conn.execute("UPDATE audit_events SET metadata_json=? WHERE tenant_id=? AND id=?",(json.dumps({"tampered":True}),a,row["id"]))
    assert db.verify_audit_chain(a)["valid"] is False
    assert db.verify_audit_chain(b)["valid"] is True

def test_v20_audit_history_backfills_deterministically(tmp_path:Path)->None:
    path=tmp_path/"legacy.sqlite"; db=Database(path); tenant,user=db.create_tenant("A","a@example.com")
    db.append_audit(tenant,user,"legacy","legacy.action","resource",None,"passed",{"x":1})
    with db.transaction() as conn:
        for name in ("audit_events_chain_insert","audit_events_actor_insert","audit_events_immutable_update","audit_events_immutable_delete"):
            conn.execute(f"DROP TRIGGER {name}")
        conn.execute("ALTER TABLE audit_events RENAME TO audit_events_v21")
        conn.execute("""CREATE TABLE audit_events(id TEXT PRIMARY KEY,tenant_id TEXT NOT NULL REFERENCES tenants(id),actor_user_id TEXT REFERENCES users(id),request_id TEXT NOT NULL,action TEXT NOT NULL,resource_type TEXT NOT NULL,resource_id TEXT,outcome TEXT NOT NULL,metadata_json TEXT NOT NULL,created_at TEXT NOT NULL)""")
        conn.execute("""INSERT INTO audit_events(id,tenant_id,actor_user_id,request_id,action,resource_type,resource_id,outcome,metadata_json,created_at) SELECT id,tenant_id,actor_user_id,request_id,action,resource_type,resource_id,outcome,metadata_json,created_at FROM audit_events_v21""")
        conn.execute("DROP TABLE audit_events_v21")
        conn.execute("DROP TABLE assurance_runs")
        conn.execute("UPDATE runtime_meta SET value='20' WHERE key='schema_version'")
    migrated=Database(path)
    assert migrated.readiness()["schema_version"]==21
    assert migrated.verify_audit_chain(tenant)["valid"] is True
    with migrated.connect() as conn:
        first=conn.execute("SELECT previous_hash,event_hash FROM audit_events WHERE tenant_id=? ORDER BY rowid LIMIT 1",(tenant,)).fetchone()
    assert first["previous_hash"]==AUDIT_GENESIS_HASH and len(first["event_hash"])==64

def test_assurance_security_eval_idempotency_rbac_and_db_guards(tmp_path:Path)->None:
    app=RuntimeApplication(Database(tmp_path/"runtime.sqlite")); boot=app.bootstrap("A","owner@example.com")
    owner=app.auth.authenticate(boot["api_key"]); viewer_id=app.db.create_user(boot["tenant_id"],"v@example.com","viewer")
    viewer=app.auth.authenticate(app.auth.issue_key(boot["tenant_id"],viewer_id))
    security=app.assurance.run(owner,"security","security-1","req-1")
    assert security["status"]=="passed" and security["checks"]
    replay=app.assurance.run(owner,"security","security-1","req-2"); assert replay["id"]==security["id"] and "lease_token" not in replay
    with pytest.raises(ConflictError): app.assurance.run(owner,"eval","security-1","req-3")
    evaluation=app.assurance.run(owner,"eval","eval-1","req-4")
    assert evaluation["status"]=="blocked" and evaluation["checks"][0]["code"]=="NO_ELIGIBLE_WORKFLOW_DATA"
    with pytest.raises(AuthorizationError): app.assurance.run(viewer,"security","viewer-key","req")
    crashed,_=app.db.create_assurance_run(boot["tenant_id"],"security","crash-1",owner.user_id)
    with app.db.transaction() as conn:
        conn.execute("UPDATE assurance_runs SET lease_until='2000-01-01T00:00:00+00:00' WHERE id=?",(crashed["id"],))
    resumed=app.assurance.run(owner,"security","crash-1","resume")
    assert resumed["id"]==crashed["id"] and resumed["status"]=="passed" and resumed["attempt_count"]==2
    account=app.db.add_connector_account(boot["tenant_id"],"shopify","store",{"shop_domain":"demo.myshopify.com","api_version":"2025-10","credential_ref":"SHOPIFY_TOKEN"})
    secret="sk-this-is-a-real-secret-value"; config=app.db.get_connector_account(boot["tenant_id"],account)["config"]; config["shop_domain"]=secret
    with app.db.transaction() as conn: conn.execute("UPDATE connector_accounts SET config_json=? WHERE id=?",(json.dumps(config),account))
    secret_service=AssuranceService(app.db,app.auth,environ={"OPENAI_API_KEY":secret})
    leaked=secret_service.run(owner,"security","security-secret","req-secret")
    assert leaked["status"]=="failed" and next(c for c in leaked["checks"] if c["name"]=="credential_persistence")["count"]>=1
    assert app.assurance.get(viewer,security["id"])["tenant_id"]==boot["tenant_id"]
    with app.db.connect() as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""INSERT INTO assurance_runs(id,tenant_id,kind,idempotency_key,status,actor_user_id,checks_json,summary_json,created_at,completed_at) VALUES('fake',?,'security','fake','passed',?,'[]','{}','now','now')""",(boot["tenant_id"],viewer_id))
        with pytest.raises(sqlite3.IntegrityError,match="immutable"):
            conn.execute("UPDATE assurance_runs SET status='failed' WHERE id=?",(security["id"],))
    with app.db.transaction() as conn: conn.execute("DROP TRIGGER assurance_runs_identity_update")
    missing_trigger=app.assurance.run(owner,"security","security-missing-trigger","req-5")
    assert missing_trigger["status"]=="failed" and next(c for c in missing_trigger["checks"] if c["name"]=="required_triggers")["count"]==1

def test_eval_assurance_uses_latest_current_evaluation(tmp_path:Path)->None:
    app=RuntimeApplication(Database(tmp_path/"runtime.sqlite")); boot=app.bootstrap("A","a@example.com"); owner=app.auth.authenticate(boot["api_key"])
    with app.db.connect() as conn: graph=conn.execute("SELECT id,definition_hash FROM agent_graph_versions WHERE tenant_id=? AND status='published'",(boot["tenant_id"],)).fetchone()
    run,_=app.db.create_agent_run(boot["tenant_id"],boot["user_id"],"run","weekly_ops","objective",[{"source_id":"s","platform":"amazon"}],["amazon"],provider="fixture",graph_version_id=graph["id"],graph_version_hash=graph["definition_hash"])
    app.db.claim_agent_run(boot["tenant_id"],run["id"],provider="fixture",model="fixture")
    app.db.complete_agent_run(boot["tenant_id"],run["id"],{},review_status="approved")
    app.db.create_agent_evaluation(boot["tenant_id"],run["id"],boot["user_id"],evaluator_version="weekly-ops-v3",passed=True,score=1,details={})
    app.db.create_agent_evaluation(boot["tenant_id"],run["id"],boot["user_id"],evaluator_version="weekly-ops-v3",passed=False,score=0,details={})
    result=app.assurance.run(owner,"eval","eval-latest","req")
    assert result["status"]=="failed"
    latest=next(c for c in result["checks"] if c["name"]=="latest_evaluation_pass")
    assert latest["status"]=="failed" and latest["count"]==0

class Handler(_Handler):
    def __init__(self,app,path,key,method="GET",body=None,idem=None):
        self._app=app; self.path=path; self.headers=Message(); self.headers["Authorization"]=f"Bearer {key}"; self.client_address=("x",1); self.out=None; self.body=body or {}; self.method=method
        if idem:self.headers["Idempotency-Key"]=idem
    @property
    def app(self):return self._app
    def _body(self):return self.body
    def _json(self,status,value,request_id,**kwargs):self.out=(status,value)
    def run(self):getattr(self,f"do_{self.method}")();return self.out

def test_assurance_http_strict_and_tenant_scoped(tmp_path:Path)->None:
    app=RuntimeApplication(Database(tmp_path/"runtime.sqlite")); a=app.bootstrap("A","a@example.com"); b=app.bootstrap("B","b@example.com")
    created=Handler(app,"/v1/assurance-runs",a["api_key"],"POST",{"kind":"security"},"http-sec").run()
    assert created[0]==201
    assert Handler(app,"/v1/assurance-runs",a["api_key"]).run()[1]["runs"][0]["id"]==created[1]["id"]
    assert Handler(app,f"/v1/assurance-runs/{created[1]['id']}",b["api_key"]).run()[0]==404
    assert Handler(app,"/v1/assurance-runs",a["api_key"],"POST",{"kind":"security"}).run()[0]==422

def test_assurance_attempt_fencing_and_failure_precedence(tmp_path:Path,monkeypatch:pytest.MonkeyPatch)->None:
    app=RuntimeApplication(Database(tmp_path/"runtime.sqlite")); boot=app.bootstrap("A","a@example.com"); owner=app.auth.authenticate(boot["api_key"])
    first,_=app.db.create_assurance_run(boot["tenant_id"],"security","fence",owner.user_id)
    with app.db.transaction() as conn: conn.execute("UPDATE assurance_runs SET lease_until='2000-01-01T00:00:00+00:00' WHERE id=?",(first["id"],))
    second=app.db.claim_assurance_run(boot["tenant_id"],first["id"]); assert second and second["attempt_count"]==2 and second["lease_token"]!=first["lease_token"]
    with pytest.raises(ConflictError):
        app.db.finish_assurance_run(boot["tenant_id"],first["id"],"passed",[{"name":"x","status":"passed","code":"OK"}],{"check_count":1,"passed_count":1},expected_attempt=1,lease_token=first["lease_token"])
    app.db.finish_assurance_run(boot["tenant_id"],first["id"],"passed",[{"name":"x","status":"passed","code":"OK"}],{"check_count":1,"passed_count":1},expected_attempt=2,lease_token=second["lease_token"])
    monkeypatch.setattr(app.assurance,"_eval_checks",lambda tenant_id:[{"name":"failure","status":"failed","code":"FAIL"},{"name":"blocked","status":"blocked","code":"NO_DATA"}])
    mixed=app.assurance.run(owner,"eval","mixed","mixed")
    assert mixed["status"]=="failed"
    forged,_=app.db.create_assurance_run(boot["tenant_id"],"security","forged",owner.user_id)
    with pytest.raises(sqlite3.IntegrityError,match="terminal state"):
        app.db.finish_assurance_run(boot["tenant_id"],forged["id"],"passed",[{"name":"bad","status":"failed","code":"FAIL"}],{"check_count":1,"passed_count":0},expected_attempt=forged["attempt_count"],lease_token=forged["lease_token"])
