from __future__ import annotations
import json,os,shutil,sqlite3,stat,subprocess,sys
from pathlib import Path
import pytest
from ecommerce_ai_skills.runtime.api import RuntimeApplication
from ecommerce_ai_skills.runtime.errors import ConflictError,ValidationError
from ecommerce_ai_skills.runtime.recovery import RecoveryService
from ecommerce_ai_skills.runtime.storage import Database

def seeded(path:Path):
    app=RuntimeApplication(Database(path)); boot=app.bootstrap("A","a@example.com"); owner=app.auth.authenticate(boot["api_key"])
    imported=app.evidence_imports.import_csv(owner,raw=b"sku,note\nA,real\n",platform="amazon",report_type="platform_generic",filename="real.csv",observed_at="2026-08-26T00:00:00Z",idempotency_key="e1",request_id="e1")
    return app,boot,imported

def test_online_backup_restore_objects_permissions_and_assurance(tmp_path:Path)->None:
    source=tmp_path/"source.sqlite"; app,boot,imported=seeded(source); backup=tmp_path/"backup"
    objects=source.parent/f"{source.name}.evidence_objects"; extra=objects/"unreferenced-extra"; extra.write_bytes(b"must-not-back-up")
    wal_conn=app.db.connect(); wal_conn.execute("PRAGMA wal_autocheckpoint=0"); wal_conn.execute("BEGIN IMMEDIATE")
    app.db.append_audit_tx(wal_conn,boot["tenant_id"],boot["user_id"],"wal-committed","wal.test","resource",None,"passed",{})
    wal_conn.commit(); wal_path=Path(str(source)+"-wal")
    assert wal_path.is_file() and wal_path.stat().st_size>0
    before_audit=len(app.db.list_audit(boot["tenant_id"])); manifest=RecoveryService.backup(source,backup); wal_conn.close()
    assert len(manifest["evidence_objects"])==1 and not any("unreferenced" in item["path"] for item in manifest["evidence_objects"])
    with sqlite3.connect(backup/"database.sqlite") as snapshot:
        assert snapshot.execute("SELECT COUNT(*) FROM audit_events WHERE request_id='wal-committed'").fetchone()[0]==1
    assert stat.S_IMODE(backup.stat().st_mode)==0o700
    assert stat.S_IMODE((backup/"database.sqlite").stat().st_mode)==0o600
    assert stat.S_IMODE((backup/"manifest.json").stat().st_mode)==0o600
    assert RecoveryService.verify(backup)["backup_id"]==manifest["backup_id"]
    assert len(app.db.list_audit(boot["tenant_id"]))==before_audit
    existing=tmp_path/"existing.sqlite"; existing.write_bytes(b"unchanged")
    assert RecoveryService.restore(backup,existing,verify_only=True)["valid"] is True
    assert existing.read_bytes()==b"unchanged"
    target=tmp_path/"restored.sqlite"; result=RecoveryService.restore(backup,target)
    assert result["restored"] is True and stat.S_IMODE(target.stat().st_mode)==0o600
    restored=Database(target); runs=restored.list_assurance_runs(boot["tenant_id"])
    assert runs[0]["kind"]=="restore" and runs[0]["status"]=="passed"
    assert restored.verify_audit_chain(boot["tenant_id"])["valid"] is True
    row=restored.get_evidence_import(boot["tenant_id"],imported["id"],include_rows=False)
    object_path=target.parent/f"{target.name}.evidence_objects"/row["object_key"]
    assert object_path.read_bytes()==b"sku,note\nA,real\n"
    assert stat.S_IMODE(object_path.stat().st_mode)==0o600
    assert not list(tmp_path.glob(".*.restore-*")) and not list(tmp_path.glob(".*.evidence-restore-*"))

def test_backup_rejects_symlinks_overlap_and_existing_output(tmp_path:Path)->None:
    source=tmp_path/"source.sqlite"; seeded(source)
    link=tmp_path/"source-link.sqlite"; link.symlink_to(source)
    with pytest.raises(ValidationError,match="symlink"): RecoveryService.backup(link,tmp_path/"b1")
    objects=source.parent/f"{source.name}.evidence_objects"; evil=objects/"backup"
    with pytest.raises(ValidationError,match="overlaps"): RecoveryService.backup(source,evil)
    output=tmp_path/"exists"; output.mkdir()
    with pytest.raises(ConflictError): RecoveryService.backup(source,output)
    symlink_object=next(path for path in objects.rglob("*") if path.is_file())
    replacement=tmp_path/"replacement"; replacement.write_bytes(symlink_object.read_bytes()); symlink_object.unlink(); symlink_object.symlink_to(replacement)
    with pytest.raises(ValidationError,match="symlink"): RecoveryService.backup(source,tmp_path/"b2")

def test_symlinked_parent_alias_is_allowed_for_regular_final_paths(tmp_path:Path)->None:
    actual=tmp_path/"actual"; actual.mkdir(); alias=tmp_path/"alias"; alias.symlink_to(actual,target_is_directory=True)
    source=actual/"source.sqlite"; seeded(source)
    manifest=RecoveryService.backup(alias/"source.sqlite",alias/"backup")
    assert manifest["schema_version"]==22 and (actual/"backup").is_dir()
    result=RecoveryService.restore(alias/"backup",alias/"restored.sqlite")
    assert result["restored"] is True and (actual/"restored.sqlite").is_file()

def test_verify_rejects_corruption_traversal_and_restore_never_overwrites(tmp_path:Path)->None:
    source=tmp_path/"source.sqlite"; seeded(source); backup=tmp_path/"backup"; RecoveryService.backup(source,backup)
    corrupt=tmp_path/"corrupt"; shutil.copytree(backup,corrupt)
    with (corrupt/"database.sqlite").open("ab") as stream: stream.write(b"tamper")
    with pytest.raises(ValidationError,match="checksum"): RecoveryService.verify(corrupt)
    traversal=tmp_path/"traversal"; shutil.copytree(backup,traversal)
    manifest=json.loads((traversal/"manifest.json").read_text()); manifest["evidence_objects"][0]["path"]="../escape"
    (traversal/"manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValidationError,match="unsafe path"): RecoveryService.verify(traversal)
    target=tmp_path/"target.sqlite"; target.write_bytes(b"keep")
    with pytest.raises(ConflictError): RecoveryService.restore(backup,target)
    assert target.read_bytes()==b"keep"
    with pytest.raises(ValidationError,match="overlaps"): RecoveryService.restore(backup,backup/"nested.sqlite")

def test_restore_rolls_back_objects_when_database_install_fails(tmp_path:Path,monkeypatch:pytest.MonkeyPatch)->None:
    from ecommerce_ai_skills.runtime import recovery
    source=tmp_path/"source.sqlite"; seeded(source); backup=tmp_path/"backup"; RecoveryService.backup(source,backup)
    target=tmp_path/"target.sqlite"; object_target=target.parent/f"{target.name}.evidence_objects"; original=recovery.os.replace
    def fail_database(source_path,destination_path):
        if Path(destination_path)==target: raise OSError("injected install failure")
        return original(source_path,destination_path)
    monkeypatch.setattr(recovery.os,"replace",fail_database)
    with pytest.raises(OSError): RecoveryService.restore(backup,target)
    assert not target.exists() and not object_target.exists()
    assert not list(tmp_path.glob(f".{target.name}.restore-*")) and not list(tmp_path.glob(f".{target.name}.evidence-restore-*"))
    assert not list(tmp_path.glob(f".{target.name}.restore-*-wal")) and not list(tmp_path.glob(f".{target.name}.restore-*-shm"))

def test_cli_backup_restore_and_structured_failure(tmp_path:Path)->None:
    source=tmp_path/"source.sqlite"; seeded(source); backup=tmp_path/"backup"; root=Path(__file__).resolve().parents[1]
    made=subprocess.run([sys.executable,"-m","ecommerce_ai_skills.cli","backup","--db",str(source),"--output",str(backup)],cwd=root,text=True,capture_output=True)
    assert made.returncode==0 and json.loads(made.stdout)["schema_version"]==22
    target=tmp_path/"target.sqlite"
    verified=subprocess.run([sys.executable,"-m","ecommerce_ai_skills.cli","restore","--backup",str(backup),"--db",str(source),"--verify-only"],cwd=root,text=True,capture_output=True)
    assert verified.returncode==0 and not target.exists()
    restored=subprocess.run([sys.executable,"-m","ecommerce_ai_skills.cli","restore","--backup",str(backup),"--db",str(target)],cwd=root,text=True,capture_output=True)
    assert restored.returncode==0 and target.exists()
    failed=subprocess.run([sys.executable,"-m","ecommerce_ai_skills.cli","restore","--backup",str(backup),"--db",str(target)],cwd=root,text=True,capture_output=True)
    payload=json.loads(failed.stdout); assert failed.returncode==2 and payload["error_code"]=="RESTORE_FAILED" and str(target) not in failed.stdout
