"""Verified SQLite and evidence-object backup/restore."""
from __future__ import annotations
import hashlib,json,os,shutil,sqlite3,tempfile,uuid
from pathlib import Path
from typing import Any
from .errors import ConflictError,ValidationError
from .storage import Database,SCHEMA_VERSION,AUDIT_GENESIS_HASH,audit_event_hash,utc_now

def _hash(path: Path)->tuple[str,int]:
    digest=hashlib.sha256(); size=0
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            digest.update(chunk); size+=len(chunk)
    return digest.hexdigest(),size

def _safe_relative(value: str)->Path:
    path=Path(value)
    if not value or path.is_absolute() or ".." in path.parts or path.as_posix()!=value:
        raise ValidationError("backup manifest contains an unsafe path")
    return path

def _reject_symlinks(root: Path)->None:
    if root.is_symlink(): raise ValidationError("symlink paths are not allowed")
    if not root.exists(): return
    for path in root.rglob("*"):
        if path.is_symlink(): raise ValidationError("symlink paths are not allowed")

class RecoveryService:
    @classmethod
    def backup(cls, db_path: str|Path, output: str|Path)->dict[str,Any]:
        source_input=Path(db_path).expanduser().absolute()
        if source_input.is_symlink(): raise ValidationError("source database symlink is not allowed")
        source=source_input.resolve(); raw_target=Path(output).expanduser().absolute()
        if raw_target.is_symlink(): raise ValidationError("backup output symlink is not allowed")
        target=raw_target.resolve(strict=False)
        if not source.is_file(): raise ValidationError("source database must be a regular file")
        if not target.parent.resolve().is_dir(): raise ValidationError("backup parent must be a directory")
        objects=source.parent/f"{source.name}.evidence_objects"; _reject_symlinks(objects)
        resolved_target=target.resolve(strict=False)
        resolved_objects=objects.resolve(strict=False)
        if resolved_target==source or resolved_target==resolved_objects or resolved_objects in resolved_target.parents:
            raise ValidationError("backup output overlaps runtime source data")
        if target.exists(): raise ConflictError("backup output already exists")
        staging=Path(tempfile.mkdtemp(prefix=f".{target.name}.staging-",dir=target.parent)); os.chmod(staging,0o700)
        backup_id=str(uuid.uuid4())
        try:
            database=staging/"database.sqlite"
            src=sqlite3.connect(source.as_uri()+"?mode=ro",uri=True); dst=sqlite3.connect(database)
            try: src.backup(dst)
            finally: dst.close(); src.close()
            os.chmod(database,0o600); db_hash,db_size=_hash(database)
            snapshot=sqlite3.connect(database); snapshot.row_factory=sqlite3.Row
            try:
                if snapshot.execute("PRAGMA quick_check").fetchone()[0]!="ok" or snapshot.execute("PRAGMA foreign_key_check").fetchall():
                    raise ValidationError("source snapshot integrity failed")
                version=snapshot.execute("SELECT value FROM runtime_meta WHERE key='schema_version'").fetchone()
                if not version or int(version[0])!=SCHEMA_VERSION: raise ValidationError("source schema version is unsupported")
                references=[dict(row) for row in snapshot.execute("SELECT object_key,sha256,byte_size FROM evidence_imports WHERE object_key IS NOT NULL ORDER BY object_key")]
            finally: snapshot.close()
            evidence=[]
            for reference in references:
                relative=_safe_relative(reference["object_key"]); item=objects/relative
                if not item.is_file() or item.is_symlink(): raise ValidationError("referenced evidence object is missing")
                actual=_hash(item)
                if actual!=(reference["sha256"],reference["byte_size"]): raise ValidationError("source evidence object integrity failed")
                destination=staging/"evidence_objects"/relative
                destination.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                shutil.copyfile(item,destination); os.chmod(destination,0o600)
                digest,size=_hash(destination)
                evidence.append({"path":relative.as_posix(),"sha256":digest,"size":size})
            evidence_root=staging/"evidence_objects"
            if evidence_root.exists():
                for directory in [evidence_root,*[p for p in evidence_root.rglob("*") if p.is_dir()]]:
                    os.chmod(directory,0o700)
            manifest={"backup_id":backup_id,"created_at":utc_now(),"schema_version":SCHEMA_VERSION,
                      "database":{"path":"database.sqlite","sha256":db_hash,"size":db_size},
                      "evidence_objects":evidence}
            manifest_path=staging/"manifest.json"
            manifest_path.write_text(json.dumps(manifest,sort_keys=True,separators=(",",":")),encoding="utf-8")
            os.chmod(manifest_path,0o600); cls.verify(staging); os.replace(staging,target)
            return manifest
        except Exception:
            shutil.rmtree(staging,ignore_errors=True); raise

    @staticmethod
    def verify(backup: str|Path)->dict[str,Any]:
        root=Path(backup).expanduser().absolute(); _reject_symlinks(root)
        if not root.is_dir(): raise ValidationError("backup must be a directory")
        manifest_path=root/"manifest.json"
        if not manifest_path.is_file(): raise ValidationError("backup manifest is missing")
        if manifest_path.stat().st_size>2_000_000: raise ValidationError("backup manifest is too large")
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        if set(manifest)!={"backup_id","created_at","schema_version","database","evidence_objects"}:
            raise ValidationError("backup manifest fields are invalid")
        if not isinstance(manifest["backup_id"],str): raise ValidationError("backup id is invalid")
        uuid.UUID(manifest["backup_id"])
        if manifest["schema_version"]!=SCHEMA_VERSION: raise ValidationError("backup schema version is unsupported")
        database_meta=manifest["database"]
        if not isinstance(database_meta,dict) or set(database_meta)!={"path","sha256","size"} or database_meta.get("path")!="database.sqlite" or not isinstance(database_meta.get("sha256"),str) or len(database_meta["sha256"])!=64 or not isinstance(database_meta.get("size"),int) or database_meta["size"]<1: raise ValidationError("backup database path is invalid")
        database=root/"database.sqlite"
        digest,size=_hash(database)
        if (digest,size)!=(database_meta.get("sha256"),database_meta.get("size")): raise ValidationError("backup database checksum failed")
        if not isinstance(manifest["evidence_objects"],list) or len(manifest["evidence_objects"])>100000: raise ValidationError("evidence manifest is invalid")
        evidence_meta={}
        for item in manifest["evidence_objects"]:
            if not isinstance(item,dict) or set(item)!={"path","sha256","size"} or not isinstance(item["sha256"],str) or len(item["sha256"])!=64 or not isinstance(item["size"],int) or item["size"]<0: raise ValidationError("evidence manifest entry is invalid")
            relative=_safe_relative(item.get("path",""))
            if relative.as_posix() in evidence_meta: raise ValidationError("duplicate evidence object path")
            path=root/"evidence_objects"/relative
            if not path.is_file() or path.is_symlink(): raise ValidationError("evidence object is missing")
            actual=_hash(path)
            if actual!=(item.get("sha256"),item.get("size")): raise ValidationError("evidence object checksum failed")
            evidence_meta[relative.as_posix()]=item
        uri=database.as_uri()+"?mode=ro"; conn=sqlite3.connect(uri,uri=True); conn.row_factory=sqlite3.Row
        try:
            if conn.execute("PRAGMA quick_check").fetchone()[0]!="ok": raise ValidationError("backup database integrity failed")
            if conn.execute("PRAGMA foreign_key_check").fetchall(): raise ValidationError("backup foreign keys failed")
            version=conn.execute("SELECT value FROM runtime_meta WHERE key='schema_version'").fetchone()
            if not version or int(version[0])!=SCHEMA_VERSION: raise ValidationError("backup schema marker failed")
            referenced={}
            for row in conn.execute("SELECT object_key,sha256,byte_size FROM evidence_imports WHERE object_key IS NOT NULL"):
                relative=_safe_relative(row["object_key"]); referenced[relative.as_posix()]=(row["sha256"],row["byte_size"])
            if set(referenced)!=set(evidence_meta): raise ValidationError("evidence object manifest does not match database")
            for key,expected in referenced.items():
                if (evidence_meta[key]["sha256"],evidence_meta[key]["size"])!=expected: raise ValidationError("evidence object metadata mismatch")
            tenants=[row[0] for row in conn.execute("SELECT id FROM tenants ORDER BY id")]
            for tenant_id in tenants:
                previous=AUDIT_GENESIS_HASH
                for row in conn.execute("SELECT * FROM audit_events WHERE tenant_id=? ORDER BY rowid",(tenant_id,)):
                    digest=audit_event_hash(previous,row["tenant_id"],row["id"],row["actor_user_id"],row["request_id"],row["action"],row["resource_type"],row["resource_id"],row["outcome"],row["metadata_json"],row["created_at"])
                    if row["previous_hash"]!=previous or row["event_hash"]!=digest: raise ValidationError("backup audit chain failed")
                    previous=digest
        finally: conn.close()
        return {"valid":True,"backup_id":manifest["backup_id"],"schema_version":SCHEMA_VERSION,
                "tenant_ids":tenants,"evidence_object_count":len(evidence_meta),"manifest":manifest}

    @classmethod
    def restore(cls, backup: str|Path, db_path: str|Path, *, verify_only: bool=False)->dict[str,Any]:
        verified=cls.verify(backup); root=Path(backup).expanduser().absolute()
        if verify_only: return {key:value for key,value in verified.items() if key!="manifest"}
        raw_target=Path(db_path).expanduser().absolute()
        if raw_target.is_symlink(): raise ValidationError("restore target symlink is not allowed")
        target=raw_target.resolve(strict=False); object_target=target.parent/f"{target.name}.evidence_objects"
        resolved_target=target.resolve(strict=False); resolved_backup=root.resolve()
        if resolved_target==resolved_backup or resolved_backup in resolved_target.parents:
            raise ValidationError("restore target overlaps backup")
        if target.exists() or object_target.exists() or object_target.is_symlink(): raise ConflictError("restore target already exists")
        if not target.parent.resolve().is_dir(): raise ValidationError("restore parent must be a directory")
        temp_db=target.parent/f".{target.name}.restore-{uuid.uuid4().hex}"
        temp_objects=target.parent/f".{target.name}.evidence-restore-{uuid.uuid4().hex}"
        installed=[]
        try:
            shutil.copyfile(root/"database.sqlite",temp_db); os.chmod(temp_db,0o600)
            source_objects=root/"evidence_objects"; temp_objects.mkdir(mode=0o700)
            for item in verified["manifest"]["evidence_objects"]:
                relative=_safe_relative(item["path"]); destination=temp_objects/relative
                destination.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                shutil.copyfile(source_objects/relative,destination); os.chmod(destination,0o600)
            for directory in (path for path in temp_objects.rglob("*") if path.is_dir()):
                os.chmod(directory,0o700)
            database_meta=verified["manifest"]["database"]
            if _hash(temp_db)!=(database_meta["sha256"],database_meta["size"]):
                raise ValidationError("staged restore database checksum failed")
            for item in verified["manifest"]["evidence_objects"]:
                if _hash(temp_objects/_safe_relative(item["path"]))!=(item["sha256"],item["size"]):
                    raise ValidationError("staged restore evidence checksum failed")
            restored=Database(temp_db)
            for tenant in restored.list_tenants():
                run,_=restored.create_assurance_run(tenant["id"],"restore",verified["backup_id"],None)
                restored.finish_assurance_run(tenant["id"],run["id"],"passed",
                    [{"name":"restore_integrity","status":"passed","code":"OK"}],
                    {"backup_id":verified["backup_id"],"evidence_object_count":verified["evidence_object_count"],"check_count":1,"passed_count":1},
                    expected_attempt=run["attempt_count"],lease_token=run["lease_token"],
                    audit_actor_user_id=None,audit_request_id=f"restore:{verified['backup_id']}")
            with restored.connect() as conn:
                if conn.execute("PRAGMA quick_check").fetchone()[0]!="ok" or conn.execute("PRAGMA foreign_key_check").fetchall(): raise ValidationError("restored database validation failed")
            if any(not restored.verify_audit_chain(t["id"])["valid"] for t in restored.list_tenants()): raise ValidationError("restored audit chain validation failed")
            with restored.connect() as conn:
                checkpoint=conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
                if checkpoint[0]!=0: raise ValidationError("restored database checkpoint failed")
            for suffix in ("-wal","-shm"):
                try: Path(str(temp_db)+suffix).unlink()
                except FileNotFoundError: pass
            os.replace(temp_objects,object_target); installed.append(object_target)
            os.replace(temp_db,target); installed.append(target)
            return {"restored":True,"backup_id":verified["backup_id"],"database":str(target),
                    "tenant_count":len(verified["tenant_ids"]),"evidence_object_count":verified["evidence_object_count"]}
        except Exception:
            for path in reversed(installed):
                if path.is_dir(): shutil.rmtree(path,ignore_errors=True)
                else:
                    try: path.unlink()
                    except FileNotFoundError: pass
            try: temp_db.unlink()
            except FileNotFoundError: pass
            for suffix in ("-wal","-shm"):
                try: Path(str(temp_db)+suffix).unlink()
                except FileNotFoundError: pass
            shutil.rmtree(temp_objects,ignore_errors=True); raise
