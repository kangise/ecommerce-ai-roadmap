"""SQLite persistence with tenant ownership enforced at every query."""

from __future__ import annotations

import contextlib
import json
import re
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

from .errors import ConflictError, NotFoundError, ValidationError


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    user_id: str
    email: str
    role: str
    api_key_id: str


ROLE_LEVEL = {"viewer": 10, "operator": 20, "admin": 30, "owner": 40}
SCHEMA_VERSION = 15


class _Connection(sqlite3.Connection):
    """Connection that closes when used as a context manager."""

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


class Database:
    """Durable local store.

    SQLite is deliberately used as the first production slice: it gives
    transactional writes, foreign keys, WAL, and a zero-infrastructure local
    deployment.  A future Postgres adapter can implement the same service
    methods without changing API or authorization semantics.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10, isolation_level=None, factory=_Connection)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 10000")
        return conn

    @contextlib.contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        conn = self.connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.transaction() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS tenants (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    mode TEXT NOT NULL DEFAULT 'production' CHECK (mode IN ('production','demo')),
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    email TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('viewer','operator','admin','owner')),
                    created_at TEXT NOT NULL,
                    UNIQUE(tenant_id, email)
                );
                CREATE TABLE IF NOT EXISTS api_keys (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    key_prefix TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    revoked_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON api_keys(key_prefix);
                CREATE TABLE IF NOT EXISTS connector_accounts (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    provider TEXT NOT NULL,
                    external_account_id TEXT NOT NULL,
                    config_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    health_status TEXT NOT NULL DEFAULT 'unchecked'
                        CHECK (health_status IN ('unchecked','healthy','unhealthy','misconfigured')),
                    health_checked_at TEXT,
                    health_error_code TEXT,
                    health_error_message TEXT,
                    UNIQUE(tenant_id, provider, external_account_id)
                );
                CREATE TABLE IF NOT EXISTS report_recipes (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    connector_account_id TEXT NOT NULL REFERENCES connector_accounts(id) ON DELETE CASCADE,
                    created_by TEXT NOT NULL REFERENCES users(id),
                    name TEXT NOT NULL,
                    recipe_key TEXT NOT NULL,
                    marketplace_ids_json TEXT NOT NULL,
                    interval_minutes INTEGER NOT NULL,
                    lookback_days INTEGER NOT NULL,
                    enabled INTEGER NOT NULL CHECK (enabled IN (0,1)),
                    next_run_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(tenant_id, connector_account_id, name)
                );
                CREATE UNIQUE INDEX IF NOT EXISTS uq_users_tenant_id
                    ON users(tenant_id, id);
                CREATE UNIQUE INDEX IF NOT EXISTS uq_connector_accounts_tenant_id
                    ON connector_accounts(tenant_id, id);
                CREATE UNIQUE INDEX IF NOT EXISTS uq_report_recipes_tenant_id
                    ON report_recipes(tenant_id, id);
                CREATE INDEX IF NOT EXISTS idx_report_recipes_tenant_next
                    ON report_recipes(tenant_id, enabled, next_run_at);
                CREATE TABLE IF NOT EXISTS report_syncs (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    recipe_id TEXT NOT NULL,
                    connector_account_id TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    amazon_report_id TEXT,
                    status TEXT NOT NULL CHECK (status IN ('queued','polling','succeeded','failed')),
                    processing_status TEXT,
                    period_start TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    available_at TEXT NOT NULL,
                    lease_until TEXT,
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL,
                    evidence_import_id TEXT REFERENCES evidence_imports(id),
                    error_code TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    UNIQUE(tenant_id, idempotency_key),
                    FOREIGN KEY (tenant_id, recipe_id)
                        REFERENCES report_recipes(tenant_id, id) ON DELETE CASCADE,
                    FOREIGN KEY (tenant_id, connector_account_id)
                        REFERENCES connector_accounts(tenant_id, id) ON DELETE CASCADE,
                    FOREIGN KEY (tenant_id, created_by)
                        REFERENCES users(tenant_id, id)
                );
                CREATE INDEX IF NOT EXISTS idx_report_syncs_claim
                    ON report_syncs(status, available_at, lease_until);
                CREATE INDEX IF NOT EXISTS idx_report_syncs_tenant_time
                    ON report_syncs(tenant_id, created_at);
                CREATE TABLE IF NOT EXISTS ads_capability_gates (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    connector_account_id TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    status TEXT NOT NULL
                        CHECK (status IN ('checking','passed','blocked','failed')),
                    region TEXT NOT NULL CHECK (region IN ('na','eu','fe')),
                    profile_id TEXT NOT NULL,
                    required_capabilities_json TEXT NOT NULL,
                    observed_capabilities_json TEXT NOT NULL,
                    checks_json TEXT NOT NULL,
                    attestation_reference TEXT,
                    request_ids_json TEXT NOT NULL,
                    retry_after_seconds INTEGER,
                    available_at TEXT NOT NULL,
                    lease_until TEXT,
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL DEFAULT 3,
                    error_code TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    UNIQUE(tenant_id, idempotency_key),
                    FOREIGN KEY (tenant_id, connector_account_id)
                        REFERENCES connector_accounts(tenant_id, id) ON DELETE CASCADE,
                    FOREIGN KEY (tenant_id, created_by)
                        REFERENCES users(tenant_id, id)
                );
                CREATE UNIQUE INDEX IF NOT EXISTS uq_ads_capability_gates_tenant_id
                    ON ads_capability_gates(tenant_id, id);
                CREATE INDEX IF NOT EXISTS idx_ads_capability_gates_claim
                    ON ads_capability_gates(status, available_at, lease_until);
                CREATE INDEX IF NOT EXISTS idx_ads_capability_gates_tenant_time
                    ON ads_capability_gates(tenant_id, created_at);
                CREATE TABLE IF NOT EXISTS actions (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    idempotency_key TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    requested_by TEXT NOT NULL REFERENCES users(id),
                    approved_by TEXT REFERENCES users(id),
                    status TEXT NOT NULL CHECK (status IN ('requested','approved','executing','executed','failed','rejected')),
                    result_json TEXT,
                    error TEXT,
                    lease_until TEXT,
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    last_attempt_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(tenant_id, idempotency_key)
                );
                CREATE INDEX IF NOT EXISTS idx_actions_tenant_status ON actions(tenant_id, status);
                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    actor_user_id TEXT REFERENCES users(id),
                    request_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT,
                    outcome TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_audit_tenant_time ON audit_events(tenant_id, created_at);
                CREATE TABLE IF NOT EXISTS connector_records (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    provider TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    synced_at TEXT NOT NULL,
                    UNIQUE(tenant_id, provider, external_id)
                );
                CREATE INDEX IF NOT EXISTS idx_records_tenant_provider ON connector_records(tenant_id, provider);
                CREATE TABLE IF NOT EXISTS sync_cursors (
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    provider TEXT NOT NULL,
                    external_account_id TEXT NOT NULL,
                    cursor TEXT,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, provider, external_account_id)
                );
                CREATE TABLE IF NOT EXISTS agent_runs (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    idempotency_key TEXT NOT NULL,
                    workflow TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    evidence_json TEXT NOT NULL,
                    platforms_json TEXT NOT NULL,
                    requested_by TEXT NOT NULL REFERENCES users(id),
                    status TEXT NOT NULL CHECK (status IN ('requested','running','completed','failed')),
                    provider TEXT NOT NULL,
                    model TEXT,
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    UNIQUE(tenant_id, idempotency_key)
                );
                CREATE INDEX IF NOT EXISTS idx_agent_runs_tenant_status ON agent_runs(tenant_id, status, created_at);
                CREATE TABLE IF NOT EXISTS agent_tasks (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    run_id TEXT NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
                    agent_name TEXT NOT NULL,
                    skill_ids_json TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('pending','running','completed','failed')),
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    UNIQUE(run_id, agent_name)
                );
                CREATE INDEX IF NOT EXISTS idx_agent_tasks_run ON agent_tasks(tenant_id, run_id, status);
                CREATE TABLE IF NOT EXISTS agent_artifacts (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    run_id TEXT NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
                    task_id TEXT REFERENCES agent_tasks(id) ON DELETE SET NULL,
                    kind TEXT NOT NULL,
                    attempt INTEGER NOT NULL,
                    content_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_agent_artifacts_run ON agent_artifacts(tenant_id, run_id, created_at);
                CREATE TABLE IF NOT EXISTS agent_events (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    run_id TEXT NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
                    task_id TEXT REFERENCES agent_tasks(id) ON DELETE SET NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_agent_events_run ON agent_events(tenant_id, run_id, created_at);
                CREATE TABLE IF NOT EXISTS evidence_imports (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    idempotency_key TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    delimiter TEXT NOT NULL,
                    row_count INTEGER NOT NULL,
                    blank_rows_skipped INTEGER NOT NULL,
                    formula_cells INTEGER NOT NULL,
                    columns_json TEXT NOT NULL,
                    column_mapping_json TEXT NOT NULL,
                    rows_json TEXT NOT NULL,
                    media_type TEXT,
                    byte_size INTEGER,
                    object_key TEXT,
                    sheet_name TEXT,
                    created_by TEXT NOT NULL REFERENCES users(id),
                    created_at TEXT NOT NULL,
                    UNIQUE(tenant_id, idempotency_key)
                );
                CREATE INDEX IF NOT EXISTS idx_evidence_imports_tenant_time
                    ON evidence_imports(tenant_id, created_at);
                CREATE UNIQUE INDEX IF NOT EXISTS uq_evidence_imports_tenant_id
                    ON evidence_imports(tenant_id, id);
                CREATE TABLE IF NOT EXISTS metric_materializations (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    evidence_import_id TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    calculation_version TEXT NOT NULL,
                    status TEXT NOT NULL
                        CHECK (status IN ('running','succeeded','partial','quarantined','failed')),
                    attempt_count INTEGER NOT NULL DEFAULT 1 CHECK (attempt_count >= 1),
                    max_attempts INTEGER NOT NULL DEFAULT 5 CHECK (max_attempts BETWEEN 1 AND 20),
                    lease_until TEXT,
                    observation_count INTEGER NOT NULL CHECK (observation_count >= 0),
                    quarantine_count INTEGER NOT NULL CHECK (quarantine_count >= 0),
                    currencies_json TEXT NOT NULL,
                    quality_flags_json TEXT NOT NULL,
                    issues_json TEXT NOT NULL,
                    error_code TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    UNIQUE(tenant_id, idempotency_key),
                    UNIQUE(tenant_id, evidence_import_id, calculation_version),
                    FOREIGN KEY (tenant_id, evidence_import_id)
                        REFERENCES evidence_imports(tenant_id, id) ON DELETE CASCADE,
                    FOREIGN KEY (tenant_id, created_by)
                        REFERENCES users(tenant_id, id)
                );
                CREATE UNIQUE INDEX IF NOT EXISTS uq_metric_materializations_tenant_id
                    ON metric_materializations(tenant_id, id);
                CREATE INDEX IF NOT EXISTS idx_metric_materializations_tenant_time
                    ON metric_materializations(tenant_id, created_at);
                CREATE TABLE IF NOT EXISTS metric_observations (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    materialization_id TEXT NOT NULL,
                    evidence_import_id TEXT NOT NULL,
                    connector_account_id TEXT,
                    marketplace_id TEXT,
                    platform TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    metric_key TEXT NOT NULL,
                    series_key TEXT NOT NULL,
                    value_decimal TEXT NOT NULL,
                    currency TEXT,
                    unit TEXT NOT NULL CHECK (unit IN ('count','currency','ratio')),
                    time_grain TEXT NOT NULL CHECK (time_grain IN ('snapshot','day','range')),
                    period_start TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    dimensions_json TEXT NOT NULL,
                    provenance_json TEXT NOT NULL,
                    quality_json TEXT NOT NULL,
                    calculation_version TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    CHECK (
                        (unit='currency' AND currency IS NOT NULL
                         AND length(currency)=3 AND currency=upper(currency))
                        OR (unit!='currency' AND currency IS NULL)
                    ),
                    FOREIGN KEY (tenant_id, materialization_id)
                        REFERENCES metric_materializations(tenant_id, id) ON DELETE CASCADE,
                    FOREIGN KEY (tenant_id, evidence_import_id)
                        REFERENCES evidence_imports(tenant_id, id) ON DELETE CASCADE,
                    FOREIGN KEY (tenant_id, connector_account_id)
                        REFERENCES connector_accounts(tenant_id, id) ON DELETE RESTRICT,
                    UNIQUE(tenant_id, evidence_import_id, calculation_version, series_key)
                );
                CREATE INDEX IF NOT EXISTS idx_metric_observations_tenant_metric_time
                    ON metric_observations(tenant_id, platform, metric_key, observed_at);
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    idempotency_key TEXT NOT NULL,
                    kind TEXT NOT NULL CHECK (kind IN ('agent_run.execute')),
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('queued','running','succeeded','failed')),
                    available_at TEXT NOT NULL,
                    lease_until TEXT,
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL,
                    created_by TEXT NOT NULL REFERENCES users(id),
                    result_json TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    UNIQUE(tenant_id, idempotency_key)
                );
                CREATE INDEX IF NOT EXISTS idx_jobs_claim
                    ON jobs(status, available_at, lease_until);
                CREATE TABLE IF NOT EXISTS schedules (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    evidence_import_ids_json TEXT NOT NULL,
                    evidence_selectors_json TEXT NOT NULL,
                    interval_minutes INTEGER NOT NULL,
                    enabled INTEGER NOT NULL CHECK (enabled IN (0,1)),
                    next_run_at TEXT NOT NULL,
                    lease_until TEXT,
                    created_by TEXT NOT NULL REFERENCES users(id),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_run_at TEXT,
                    UNIQUE(tenant_id, name)
                );
                CREATE INDEX IF NOT EXISTS idx_schedules_due
                    ON schedules(enabled, next_run_at, lease_until);
                CREATE TABLE IF NOT EXISTS agent_evaluations (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    run_id TEXT NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
                    evaluator_version TEXT NOT NULL,
                    passed INTEGER NOT NULL CHECK (passed IN (0,1)),
                    score REAL NOT NULL,
                    details_json TEXT NOT NULL,
                    created_by TEXT NOT NULL REFERENCES users(id),
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_agent_evaluations_run
                    ON agent_evaluations(tenant_id, run_id, created_at);
                CREATE TABLE IF NOT EXISTS runtime_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            row = conn.execute("SELECT value FROM runtime_meta WHERE key='schema_version'").fetchone()
            if row is None:
                conn.execute("INSERT INTO runtime_meta(key,value) VALUES('schema_version',?)", (str(SCHEMA_VERSION),))
            else:
                try:
                    version = int(row["value"])
                except (TypeError, ValueError) as exc:
                    raise ValidationError(f"invalid runtime schema version: {row['value']}") from exc
                if version > SCHEMA_VERSION:
                    raise ValidationError(f"unsupported runtime schema version: {row['value']}")
                if version < SCHEMA_VERSION:
                    self._migrate(conn, version)

    @staticmethod
    def _migrate(conn: sqlite3.Connection, version: int) -> None:
        """Apply additive migrations for databases created by earlier releases."""
        if version == 1:
            columns = {row["name"] for row in conn.execute("PRAGMA table_info(actions)").fetchall()}
            if "lease_until" not in columns:
                conn.execute("ALTER TABLE actions ADD COLUMN lease_until TEXT")
            if "attempt_count" not in columns:
                conn.execute("ALTER TABLE actions ADD COLUMN attempt_count INTEGER NOT NULL DEFAULT 0")
            if "last_attempt_at" not in columns:
                conn.execute("ALTER TABLE actions ADD COLUMN last_attempt_at TEXT")
            conn.execute(
                """CREATE TABLE IF NOT EXISTS sync_cursors (
                   tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                   provider TEXT NOT NULL,
                   external_account_id TEXT NOT NULL,
                   cursor TEXT,
                   updated_at TEXT NOT NULL,
                   PRIMARY KEY (tenant_id, provider, external_account_id)
                )"""
            )
            version = 2
        if version == 2:
            # The idempotent CREATE TABLE statements in initialize() have
            # already installed the v3 agent-run tables inside this same
            # transaction. Advancing the marker makes the migration explicit
            # and keeps older files fail-closed if a later step is added.
            version = 3
        if version == 3:
            columns = {
                row["name"] for row in conn.execute("PRAGMA table_info(agent_runs)").fetchall()
            }
            if "platforms_json" not in columns:
                conn.execute(
                    "ALTER TABLE agent_runs ADD COLUMN platforms_json TEXT NOT NULL DEFAULT '[]'"
                )
            rows = conn.execute(
                "SELECT id,evidence_json,platforms_json FROM agent_runs"
            ).fetchall()
            for row in rows:
                if json.loads(row["platforms_json"] or "[]"):
                    continue
                platforms = set()
                for source in json.loads(row["evidence_json"] or "[]"):
                    declared = source.get("platform") if isinstance(source, dict) else None
                    source_type = str(source.get("source_type", "")) if isinstance(source, dict) else ""
                    if declared:
                        platforms.add(declared)
                    elif source_type.startswith("amazon"):
                        platforms.add("amazon")
                    elif source_type.startswith("shopify"):
                        platforms.add("shopify")
                    else:
                        platforms.add("cross_platform")
                conn.execute(
                    "UPDATE agent_runs SET platforms_json=? WHERE id=?",
                    (json.dumps(sorted(platforms)), row["id"]),
                )
            version = 4
        if version == 4:
            # initialize() has already created the additive evidence_imports
            # table in this transaction for v4 databases.
            version = 5
        if version == 5:
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(evidence_imports)").fetchall()
            }
            additions = {
                "column_mapping_json": "TEXT NOT NULL DEFAULT '{}'",
                "media_type": "TEXT",
                "byte_size": "INTEGER",
                "object_key": "TEXT",
                "sheet_name": "TEXT",
            }
            for name, declaration in additions.items():
                if name not in columns:
                    conn.execute(
                        f"ALTER TABLE evidence_imports ADD COLUMN {name} {declaration}"
                    )
            rows = conn.execute(
                "SELECT id,columns_json,column_mapping_json FROM evidence_imports"
            ).fetchall()
            for row in rows:
                if json.loads(row["column_mapping_json"] or "{}"):
                    continue
                columns_list = json.loads(row["columns_json"] or "[]")
                conn.execute(
                    "UPDATE evidence_imports SET column_mapping_json=? WHERE id=?",
                    (json.dumps({column: column for column in columns_list}), row["id"]),
                )
            version = 6
        if version == 6:
            # initialize() has already created the additive job and schedule
            # tables in this transaction for v6 databases.
            version = 7
        if version == 7:
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(schedules)").fetchall()
            }
            if "evidence_selectors_json" not in columns:
                conn.execute(
                    """ALTER TABLE schedules ADD COLUMN evidence_selectors_json
                       TEXT NOT NULL DEFAULT '[]'"""
                )
            version = 8
        if version == 8:
            # initialize() has already created agent_evaluations for v8 files.
            version = 9
        if version == 9:
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(tenants)").fetchall()
            }
            if "mode" not in columns:
                conn.execute(
                    "ALTER TABLE tenants ADD COLUMN mode TEXT NOT NULL DEFAULT 'production'"
                )
            version = 10
        if version == 10:
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(connector_accounts)").fetchall()
            }
            additions = {
                "updated_at": "TEXT",
                "health_status": "TEXT NOT NULL DEFAULT 'unchecked'",
                "health_checked_at": "TEXT",
                "health_error_code": "TEXT",
                "health_error_message": "TEXT",
            }
            for name, declaration in additions.items():
                if name not in columns:
                    conn.execute(
                        f"ALTER TABLE connector_accounts ADD COLUMN {name} {declaration}"
                    )
            conn.execute(
                "UPDATE connector_accounts SET updated_at=created_at WHERE updated_at IS NULL"
            )
            conn.execute(
                "UPDATE connector_accounts SET health_status='unchecked' "
                "WHERE health_status IS NULL OR health_status=''"
            )
            version = 11
        if version == 11:
            # initialize() creates the new tenant-owned table before the
            # version marker is advanced, making the migration transactional.
            version = 12
        if version == 12:
            # initialize() creates report_syncs transactionally before the
            # schema marker advances.
            version = 13
        if version == 13:
            # initialize() creates the tenant-owned materialization and
            # observation tables transactionally before advancing the marker.
            version = 14
        if version == 14:
            # initialize() creates ads_capability_gates transactionally before
            # the schema marker advances.
            version = 15
        if version != SCHEMA_VERSION:
            raise ValidationError(f"no migration path from runtime schema version {version}")
        conn.execute("UPDATE runtime_meta SET value=? WHERE key='schema_version'", (str(SCHEMA_VERSION),))

    @staticmethod
    def _id() -> str:
        return str(uuid.uuid4())

    def create_tenant(
        self, name: str, email: str, *, mode: str = "production"
    ) -> tuple[str, str]:
        name, email = name.strip(), email.strip().lower()
        if not name or not email or "@" not in email:
            raise ValidationError("tenant name and a valid owner email are required")
        if mode not in {"production", "demo"}:
            raise ValidationError("tenant mode must be production or demo")
        tenant_id, user_id = self._id(), self._id()
        now = utc_now()
        with self.transaction() as conn:
            conn.execute(
                "INSERT INTO tenants(id,name,mode,created_at) VALUES(?,?,?,?)",
                (tenant_id, name, mode, now),
            )
            conn.execute(
                "INSERT INTO users(id,tenant_id,email,role,created_at) VALUES(?,?,?,?,?)",
                (user_id, tenant_id, email, "owner", now),
            )
        return tenant_id, user_id

    def get_tenant(self, tenant_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id,name,mode,created_at FROM tenants WHERE id=?", (tenant_id,)
            ).fetchone()
        if row is None:
            raise NotFoundError("tenant not found")
        return dict(row)

    def list_tenants(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id,name,mode,created_at FROM tenants ORDER BY created_at,id"
            ).fetchall()
        return [dict(row) for row in rows]

    def create_user(self, tenant_id: str, email: str, role: str) -> str:
        email = email.strip().lower()
        if role not in ROLE_LEVEL or not email or "@" not in email:
            raise ValidationError("email and role (viewer/operator/admin/owner) are required")
        user_id = self._id()
        try:
            with self.transaction() as conn:
                self.require_tenant(conn, tenant_id)
                conn.execute(
                    "INSERT INTO users(id,tenant_id,email,role,created_at) VALUES(?,?,?,?,?)",
                    (user_id, tenant_id, email, role, utc_now()),
                )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("user already exists for this tenant") from exc
        return user_id

    def get_user(self, tenant_id: str, user_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id,tenant_id,email,role,created_at FROM users WHERE id=? AND tenant_id=?",
                (user_id, tenant_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("user not found")
        return dict(row)

    def list_users(self, tenant_id: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id,tenant_id,email,role,created_at FROM users WHERE tenant_id=? ORDER BY created_at,id",
                (tenant_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def principal_for_user(self, tenant_id: str, user_id: str) -> Principal:
        user = self.get_user(tenant_id, user_id)
        return Principal(
            tenant_id=user["tenant_id"],
            user_id=user["id"],
            email=user["email"],
            role=user["role"],
            api_key_id="internal-worker",
        )

    def update_user_role(self, tenant_id: str, user_id: str, role: str) -> dict[str, Any]:
        if role not in ROLE_LEVEL:
            raise ValidationError("role must be viewer, operator, admin, or owner")
        with self.transaction() as conn:
            row = conn.execute(
                "SELECT id,tenant_id,email,role,created_at FROM users WHERE id=? AND tenant_id=?",
                (user_id, tenant_id),
            ).fetchone()
            if row is None:
                raise NotFoundError("user not found")
            if row["role"] == "owner" and role != "owner":
                owners = conn.execute(
                    "SELECT COUNT(*) FROM users WHERE tenant_id=? AND role='owner'",
                    (tenant_id,),
                ).fetchone()[0]
                if owners <= 1:
                    raise ConflictError("cannot demote the tenant's last owner")
            conn.execute(
                "UPDATE users SET role=? WHERE id=? AND tenant_id=?",
                (role, user_id, tenant_id),
            )
            updated = conn.execute(
                "SELECT id,tenant_id,email,role,created_at FROM users WHERE id=? AND tenant_id=?",
                (user_id, tenant_id),
            ).fetchone()
        return dict(updated)

    @staticmethod
    def require_tenant(conn: sqlite3.Connection, tenant_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM tenants WHERE id=?", (tenant_id,)).fetchone()
        if row is None:
            raise NotFoundError("tenant not found")
        return row

    def readiness(self) -> dict[str, Any]:
        try:
            with self.connect() as conn:
                quick_check = conn.execute("PRAGMA quick_check").fetchone()[0]
                row = conn.execute("SELECT value FROM runtime_meta WHERE key='schema_version'").fetchone()
            if quick_check != "ok" or not row or int(row["value"]) != SCHEMA_VERSION:
                return {"status": "not_ready", "reason": "schema_check_failed"}
            return {"status": "ready", "schema_version": SCHEMA_VERSION}
        except (OSError, sqlite3.Error, TypeError, ValueError):
            return {"status": "not_ready", "reason": "database_check_failed"}

    def user_for_api_key(self, key_id: str) -> Principal | None:
        with self.connect() as conn:
            row = conn.execute(
                """SELECT k.id AS api_key_id,u.tenant_id,u.id AS user_id,u.email,u.role
                   FROM api_keys k JOIN users u ON u.id=k.user_id
                   WHERE k.id=? AND k.revoked_at IS NULL""",
                (key_id,),
            ).fetchone()
        if not row:
            return None
        return Principal(row["tenant_id"], row["user_id"], row["email"], row["role"], row["api_key_id"])

    def require_user(self, tenant_id: str, user_id: str) -> None:
        with self.connect() as conn:
            row = conn.execute("SELECT id FROM users WHERE id=? AND tenant_id=?", (user_id, tenant_id)).fetchone()
        if row is None:
            raise NotFoundError("user not found in tenant")

    def insert_api_key(self, tenant_id: str, user_id: str, prefix: str, key_hash: str) -> str:
        key_id = self._id()
        with self.transaction() as conn:
            row = conn.execute("SELECT tenant_id FROM users WHERE id=?", (user_id,)).fetchone()
            if not row or row["tenant_id"] != tenant_id:
                raise ValidationError("user does not belong to tenant")
            conn.execute(
                "INSERT INTO api_keys(id,tenant_id,user_id,key_prefix,key_hash,created_at) VALUES(?,?,?,?,?,?)",
                (key_id, tenant_id, user_id, prefix, key_hash, utc_now()),
            )
        return key_id

    def api_key_candidates(self, prefix: str) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM api_keys WHERE key_prefix=? AND revoked_at IS NULL", (prefix,)
            ).fetchall()

    def revoke_api_key(self, tenant_id: str, key_id: str, *, allow_last: bool = False) -> None:
        with self.transaction() as conn:
            active = conn.execute("SELECT COUNT(*) AS count FROM api_keys WHERE tenant_id=? AND revoked_at IS NULL", (tenant_id,)).fetchone()["count"]
            if active <= 1 and not allow_last:
                raise ConflictError("cannot revoke the last active API key; rotate first")
            result = conn.execute(
                "UPDATE api_keys SET revoked_at=? WHERE id=? AND tenant_id=? AND revoked_at IS NULL",
                (utc_now(), key_id, tenant_id),
            )
            if result.rowcount != 1:
                raise NotFoundError("API key not found")

    def list_api_keys(self, tenant_id: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT k.id,k.key_prefix,k.created_at,k.revoked_at,u.id AS user_id,u.email,u.role
                   FROM api_keys k JOIN users u ON u.id=k.user_id
                   WHERE k.tenant_id=? ORDER BY k.created_at DESC""",
                (tenant_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _validated_connector_config(provider: str, config: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(config, dict):
            raise ValidationError("connector config must be an object")
        if provider == "shopify":
            required = {"shop_domain", "api_version", "credential_ref"}
        elif provider == "amazon_spapi":
            required = {
                "region",
                "marketplace_ids",
                "lwa_client_id_ref",
                "lwa_client_secret_ref",
                "lwa_refresh_token_ref",
            }
        elif provider == "amazon_ads":
            required = {
                "region",
                "profile_id",
                "lwa_client_id_ref",
                "lwa_client_secret_ref",
                "lwa_refresh_token_ref",
            }
        else:
            raise ValidationError("unsupported connector provider")
        forbidden_keys = {
            "access_token", "refresh_token", "client_secret", "token", "password", "api_key"
        }
        if any(str(key).lower() in forbidden_keys for key in config):
            raise ValidationError(
                "connector config cannot contain secret values; store environment references only"
            )
        if set(config) != required:
            raise ValidationError(
                f"{provider} connector config requires exactly: {', '.join(sorted(required))}"
            )
        reference_keys = [key for key in config if key.endswith("_ref") or key == "credential_ref"]
        if not reference_keys or any(
            not isinstance(config[key], str)
            or not re.fullmatch(r"[A-Z][A-Z0-9_]{2,127}", config[key])
            for key in reference_keys
        ):
            raise ValidationError("connector credential references must be environment variable names")
        if provider == "amazon_spapi":
            from .connectors.amazon_spapi import validate_amazon_marketplaces

            region, marketplace_ids = validate_amazon_marketplaces(
                config["region"], config["marketplace_ids"]
            )
            config = {**config, "region": region, "marketplace_ids": marketplace_ids}
        elif provider == "amazon_ads":
            from .connectors.amazon_ads import validate_amazon_ads_config

            region, profile_id = validate_amazon_ads_config(
                config["region"], config["profile_id"]
            )
            config = {**config, "region": region, "profile_id": profile_id}
        else:
            domain = str(config["shop_domain"]).lower().strip().rstrip("/")
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*\.myshopify\.com", domain):
                raise ValidationError("shop_domain must be a canonical *.myshopify.com host")
            version = str(config["api_version"]).strip()
            if not re.fullmatch(r"20\d{2}-\d{2}", version):
                raise ValidationError("api_version must be an explicit YYYY-MM version")
            config = {**config, "shop_domain": domain, "api_version": version}
        return config

    def add_connector_account(self, tenant_id: str, provider: str, external_account_id: str, config: dict[str, Any]) -> str:
        if not provider or not isinstance(external_account_id, str) or not external_account_id.strip():
            raise ValidationError("provider, external account id, and config are required")
        external_account_id = external_account_id.strip()
        config = self._validated_connector_config(provider, config)
        account_id = self._id()
        now = utc_now()
        try:
            with self.transaction() as conn:
                self.require_tenant(conn, tenant_id)
                conn.execute(
                    """INSERT INTO connector_accounts(
                       id,tenant_id,provider,external_account_id,config_json,created_at,
                       updated_at,health_status)
                       VALUES(?,?,?,?,?,?,?,'unchecked')""",
                    (account_id, tenant_id, provider, external_account_id, json.dumps(config, sort_keys=True), now, now),
                )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("connector account already exists") from exc
        return account_id

    def create_connector_account(
        self, tenant_id: str, provider: str, external_account_id: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        account_id = self.add_connector_account(
            tenant_id, provider, external_account_id, config
        )
        return self.get_connector_account(tenant_id, account_id)

    @staticmethod
    def _connector_account_dict(row: sqlite3.Row) -> dict[str, Any]:
        account = dict(row)
        account["config"] = json.loads(account.pop("config_json"))
        return account

    def list_connector_accounts(self, tenant_id: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM connector_accounts WHERE tenant_id=? ORDER BY created_at,id",
                (tenant_id,),
            ).fetchall()
        return [self._connector_account_dict(row) for row in rows]

    def get_connector_account(self, tenant_id: str, account_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM connector_accounts WHERE tenant_id=? AND id=?",
                (tenant_id, account_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("connector account not found")
        return self._connector_account_dict(row)

    def update_connector_account(
        self,
        tenant_id: str,
        account_id: str,
        external_account_id: str,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        if not isinstance(external_account_id, str) or not external_account_id.strip():
            raise ValidationError("external_account_id and config are required")
        existing = self.get_connector_account(tenant_id, account_id)
        config = self._validated_connector_config(existing["provider"], config)
        now = utc_now()
        try:
            with self.transaction() as conn:
                result = conn.execute(
                    """UPDATE connector_accounts
                       SET external_account_id=?,config_json=?,updated_at=?,
                           health_status='unchecked',health_checked_at=NULL,
                           health_error_code=NULL,health_error_message=NULL
                       WHERE tenant_id=? AND id=?""",
                    (
                        external_account_id.strip(),
                        json.dumps(config, sort_keys=True),
                        now,
                        tenant_id,
                        account_id,
                    ),
                )
                if result.rowcount != 1:
                    raise NotFoundError("connector account not found")
        except sqlite3.IntegrityError as exc:
            raise ConflictError("connector account already exists") from exc
        return self.get_connector_account(tenant_id, account_id)

    def set_connector_account_health(
        self,
        tenant_id: str,
        account_id: str,
        status: str,
        *,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> dict[str, Any]:
        if status not in {"healthy", "unhealthy", "misconfigured"}:
            raise ValidationError("invalid connector health status")
        checked_at = utc_now()
        with self.transaction() as conn:
            result = conn.execute(
                """UPDATE connector_accounts
                   SET health_status=?,health_checked_at=?,health_error_code=?,
                       health_error_message=?,updated_at=?
                   WHERE tenant_id=? AND id=?""",
                (
                    status,
                    checked_at,
                    error_code,
                    error_message[:1000] if error_message else None,
                    checked_at,
                    tenant_id,
                    account_id,
                ),
            )
            if result.rowcount != 1:
                raise NotFoundError("connector account not found")
        return self.get_connector_account(tenant_id, account_id)

    def connector_account(self, tenant_id: str, provider: str, external_account_id: str) -> sqlite3.Row:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM connector_accounts WHERE tenant_id=? AND provider=? AND external_account_id=?",
                (tenant_id, provider, external_account_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("connector account not found")
        return row

    @staticmethod
    def _report_recipe_dict(row: sqlite3.Row) -> dict[str, Any]:
        recipe = dict(row)
        recipe["marketplace_ids"] = json.loads(recipe.pop("marketplace_ids_json"))
        recipe["enabled"] = bool(recipe["enabled"])
        return recipe

    def create_report_recipe(
        self,
        tenant_id: str,
        created_by: str,
        *,
        connector_account_id: str,
        name: str,
        recipe_key: str,
        marketplace_ids: list[str],
        interval_minutes: int,
        lookback_days: int,
        enabled: bool,
        next_run_at: str,
    ) -> dict[str, Any]:
        recipe_id = self._id()
        now = utc_now()
        try:
            with self.transaction() as conn:
                self.require_tenant(conn, tenant_id)
                actor = conn.execute(
                    "SELECT tenant_id FROM users WHERE id=?", (created_by,)
                ).fetchone()
                if actor is None or actor["tenant_id"] != tenant_id:
                    raise ValidationError("report recipe creator does not belong to tenant")
                account = conn.execute(
                    "SELECT tenant_id FROM connector_accounts WHERE id=? AND tenant_id=?",
                    (connector_account_id, tenant_id),
                ).fetchone()
                if account is None:
                    raise NotFoundError("connector account not found")
                conn.execute(
                    """INSERT INTO report_recipes(
                       id,tenant_id,connector_account_id,created_by,name,recipe_key,
                       marketplace_ids_json,interval_minutes,lookback_days,enabled,
                       next_run_at,created_at,updated_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        recipe_id,
                        tenant_id,
                        connector_account_id,
                        created_by,
                        name,
                        recipe_key,
                        json.dumps(marketplace_ids),
                        interval_minutes,
                        lookback_days,
                        int(enabled),
                        next_run_at,
                        now,
                        now,
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("report recipe name already exists for connector account") from exc
        return self.get_report_recipe(tenant_id, recipe_id)

    def list_report_recipes(self, tenant_id: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM report_recipes WHERE tenant_id=? ORDER BY created_at,id",
                (tenant_id,),
            ).fetchall()
        return [self._report_recipe_dict(row) for row in rows]

    def get_report_recipe(self, tenant_id: str, recipe_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM report_recipes WHERE tenant_id=? AND id=?",
                (tenant_id, recipe_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("report recipe not found")
        return self._report_recipe_dict(row)

    def update_report_recipe(
        self,
        tenant_id: str,
        recipe_id: str,
        *,
        name: str,
        recipe_key: str,
        marketplace_ids: list[str],
        interval_minutes: int,
        lookback_days: int,
        enabled: bool,
        next_run_at: str,
    ) -> dict[str, Any]:
        try:
            with self.transaction() as conn:
                result = conn.execute(
                    """UPDATE report_recipes
                       SET name=?,recipe_key=?,marketplace_ids_json=?,interval_minutes=?,
                           lookback_days=?,enabled=?,next_run_at=?,updated_at=?
                       WHERE tenant_id=? AND id=?""",
                    (
                        name,
                        recipe_key,
                        json.dumps(marketplace_ids),
                        interval_minutes,
                        lookback_days,
                        int(enabled),
                        next_run_at,
                        utc_now(),
                        tenant_id,
                        recipe_id,
                    ),
                )
                if result.rowcount != 1:
                    raise NotFoundError("report recipe not found")
        except sqlite3.IntegrityError as exc:
            raise ConflictError("report recipe name already exists for connector account") from exc
        return self.get_report_recipe(tenant_id, recipe_id)

    @staticmethod
    def _report_sync_dict(row: sqlite3.Row) -> dict[str, Any]:
        return dict(row)

    def create_report_sync(
        self,
        tenant_id: str,
        created_by: str,
        recipe_id: str,
        idempotency_key: str,
        *,
        period_start: str,
        period_end: str,
        max_attempts: int = 12,
        available_at: str | None = None,
    ) -> tuple[dict[str, Any], bool]:
        if not isinstance(idempotency_key, str) or not 1 <= len(idempotency_key) <= 200:
            raise ValidationError(
                "report sync idempotency_key is required and must be <= 200 characters"
            )
        if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or not 1 <= max_attempts <= 50:
            raise ValidationError("report sync max_attempts must be between 1 and 50")
        sync_id = self._id()
        now = utc_now()
        try:
            with self.transaction() as conn:
                recipe = conn.execute(
                    """SELECT connector_account_id FROM report_recipes
                       WHERE tenant_id=? AND id=?""",
                    (tenant_id, recipe_id),
                ).fetchone()
                if recipe is None:
                    raise NotFoundError("report recipe not found")
                actor = conn.execute(
                    "SELECT tenant_id FROM users WHERE id=?", (created_by,)
                ).fetchone()
                if actor is None or actor["tenant_id"] != tenant_id:
                    raise ValidationError("report sync creator does not belong to tenant")
                conn.execute(
                    """INSERT INTO report_syncs(
                       id,tenant_id,recipe_id,connector_account_id,created_by,
                       idempotency_key,status,period_start,period_end,available_at,
                       max_attempts,created_at,updated_at)
                       VALUES(?,?,?,?,?,?,'queued',?,?,?,?,?,?)""",
                    (
                        sync_id,
                        tenant_id,
                        recipe_id,
                        recipe["connector_account_id"],
                        created_by,
                        idempotency_key,
                        period_start,
                        period_end,
                        available_at or now,
                        max_attempts,
                        now,
                        now,
                    ),
                )
        except sqlite3.IntegrityError:
            with self.connect() as conn:
                row = conn.execute(
                    "SELECT * FROM report_syncs WHERE tenant_id=? AND idempotency_key=?",
                    (tenant_id, idempotency_key),
                ).fetchone()
            if row is None:
                raise ConflictError("report sync idempotency conflict")
            existing = self._report_sync_dict(row)
            if existing["recipe_id"] != recipe_id:
                raise ConflictError(
                    "idempotency key was used for a different report recipe"
                )
            return existing, True
        return self.get_report_sync(tenant_id, sync_id), False

    def get_report_sync(self, tenant_id: str, sync_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM report_syncs WHERE tenant_id=? AND id=?",
                (tenant_id, sync_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("report sync not found")
        return self._report_sync_dict(row)

    def list_report_syncs(self, tenant_id: str, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM report_syncs WHERE tenant_id=?
                   ORDER BY created_at DESC,id DESC LIMIT ?""",
                (tenant_id, limit),
            ).fetchall()
        return [self._report_sync_dict(row) for row in rows]

    def claim_report_sync(self, *, lease_seconds: int = 300) -> dict[str, Any] | None:
        now = utc_now()
        lease_until = self._lease_until(lease_seconds)
        with self.transaction() as conn:
            conn.execute(
                """UPDATE report_syncs SET status='failed',error_code='max_attempts',
                   error_message='report sync exhausted its retry budget',
                   lease_until=NULL,completed_at=?,updated_at=?
                   WHERE status IN ('queued','polling') AND attempt_count>=max_attempts
                     AND (lease_until IS NULL OR lease_until<?)""",
                (now, now, now),
            )
            row = conn.execute(
                """SELECT id FROM report_syncs
                   WHERE status IN ('queued','polling') AND available_at<=?
                     AND attempt_count<max_attempts
                     AND (lease_until IS NULL OR lease_until<?)
                   ORDER BY available_at,rowid LIMIT 1""",
                (now, now),
            ).fetchone()
            if row is None:
                return None
            result = conn.execute(
                """UPDATE report_syncs SET lease_until=?,attempt_count=attempt_count+1,
                   updated_at=? WHERE id=? AND status IN ('queued','polling')
                   AND available_at<=? AND attempt_count<max_attempts
                   AND (lease_until IS NULL OR lease_until<?)""",
                (lease_until, now, row["id"], now, now),
            )
            if result.rowcount != 1:
                return None
            claimed = conn.execute(
                "SELECT * FROM report_syncs WHERE id=?", (row["id"],)
            ).fetchone()
        return self._report_sync_dict(claimed)

    def mark_report_sync_polling(
        self,
        tenant_id: str,
        sync_id: str,
        amazon_report_id: str,
        *,
        processing_status: str = "IN_QUEUE",
        delay_seconds: int = 15,
    ) -> dict[str, Any]:
        available_at = (
            datetime.now(timezone.utc)
            + timedelta(seconds=max(1, min(delay_seconds, 3600)))
        ).isoformat(timespec="seconds")
        with self.transaction() as conn:
            result = conn.execute(
                """UPDATE report_syncs SET status='polling',amazon_report_id=?,
                   processing_status=?,available_at=?,lease_until=NULL,
                   error_code=NULL,error_message=NULL,updated_at=?
                   WHERE tenant_id=? AND id=? AND status='queued' AND lease_until IS NOT NULL""",
                (
                    amazon_report_id,
                    processing_status,
                    available_at,
                    utc_now(),
                    tenant_id,
                    sync_id,
                ),
            )
            if result.rowcount != 1:
                raise ConflictError("report sync is not a claimed queued sync")
        return self.get_report_sync(tenant_id, sync_id)

    def reschedule_report_sync(
        self,
        tenant_id: str,
        sync_id: str,
        *,
        delay_seconds: int,
        processing_status: str | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> dict[str, Any]:
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat(timespec="seconds")
        with self.transaction() as conn:
            row = conn.execute(
                """SELECT status,attempt_count,max_attempts FROM report_syncs
                   WHERE tenant_id=? AND id=? AND status IN ('queued','polling')
                     AND lease_until IS NOT NULL""",
                (tenant_id, sync_id),
            ).fetchone()
            if row is None:
                raise ConflictError("report sync is not claimed")
            if row["attempt_count"] >= row["max_attempts"]:
                conn.execute(
                    """UPDATE report_syncs SET status='failed',processing_status=?,
                       lease_until=NULL,error_code=?,error_message=?,completed_at=?,updated_at=?
                       WHERE tenant_id=? AND id=?""",
                    (
                        processing_status,
                        error_code or "max_attempts",
                        (error_message or "report sync exhausted its retry budget")[:2000],
                        now,
                        now,
                        tenant_id,
                        sync_id,
                    ),
                )
            else:
                available_at = (
                    now_dt + timedelta(seconds=max(1, min(delay_seconds, 3600)))
                ).isoformat(timespec="seconds")
                conn.execute(
                    """UPDATE report_syncs SET processing_status=COALESCE(?,processing_status),
                       available_at=?,lease_until=NULL,error_code=?,error_message=?,updated_at=?
                       WHERE tenant_id=? AND id=?""",
                    (
                        processing_status,
                        available_at,
                        error_code,
                        error_message[:2000] if error_message else None,
                        now,
                        tenant_id,
                        sync_id,
                    ),
                )
        return self.get_report_sync(tenant_id, sync_id)

    def fail_report_sync(
        self,
        tenant_id: str,
        sync_id: str,
        *,
        error_code: str,
        error_message: str,
        processing_status: str | None = None,
    ) -> dict[str, Any]:
        now = utc_now()
        with self.transaction() as conn:
            row = conn.execute(
                "SELECT status FROM report_syncs WHERE tenant_id=? AND id=?",
                (tenant_id, sync_id),
            ).fetchone()
            if row is None:
                raise NotFoundError("report sync not found")
            if row["status"] == "succeeded":
                raise ConflictError("succeeded report sync cannot fail")
            if row["status"] != "failed":
                conn.execute(
                    """UPDATE report_syncs SET status='failed',processing_status=?,
                       lease_until=NULL,error_code=?,error_message=?,completed_at=?,updated_at=?
                       WHERE tenant_id=? AND id=?""",
                    (
                        processing_status,
                        error_code,
                        error_message[:2000],
                        now,
                        now,
                        tenant_id,
                        sync_id,
                    ),
                )
        return self.get_report_sync(tenant_id, sync_id)

    def complete_report_sync(
        self, tenant_id: str, sync_id: str, evidence_import_id: str
    ) -> dict[str, Any]:
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat(timespec="seconds")
        with self.transaction() as conn:
            sync = conn.execute(
                """SELECT status,recipe_id,evidence_import_id FROM report_syncs
                   WHERE tenant_id=? AND id=?""",
                (tenant_id, sync_id),
            ).fetchone()
            if sync is None:
                raise NotFoundError("report sync not found")
            if sync["status"] == "succeeded":
                if sync["evidence_import_id"] != evidence_import_id:
                    raise ConflictError("report sync already completed with different evidence")
                return self.get_report_sync(tenant_id, sync_id)
            if sync["status"] not in {"queued", "polling"}:
                raise ConflictError("report sync cannot complete from its current status")
            evidence = conn.execute(
                "SELECT tenant_id FROM evidence_imports WHERE id=? AND tenant_id=?",
                (evidence_import_id, tenant_id),
            ).fetchone()
            if evidence is None:
                raise NotFoundError("evidence import not found")
            recipe = conn.execute(
                """SELECT next_run_at,interval_minutes FROM report_recipes
                   WHERE tenant_id=? AND id=?""",
                (tenant_id, sync["recipe_id"]),
            ).fetchone()
            if recipe is None:
                raise NotFoundError("report recipe not found")
            next_dt = datetime.fromisoformat(
                recipe["next_run_at"].replace("Z", "+00:00")
            ) + timedelta(minutes=recipe["interval_minutes"])
            while next_dt <= now_dt:
                next_dt += timedelta(minutes=recipe["interval_minutes"])
            conn.execute(
                """UPDATE report_syncs SET status='succeeded',processing_status='DONE',
                   evidence_import_id=?,lease_until=NULL,error_code=NULL,error_message=NULL,
                   completed_at=?,updated_at=? WHERE tenant_id=? AND id=?""",
                (evidence_import_id, now, now, tenant_id, sync_id),
            )
            conn.execute(
                "UPDATE report_recipes SET next_run_at=?,updated_at=? WHERE tenant_id=? AND id=?",
                (
                    next_dt.isoformat(timespec="seconds"),
                    now,
                    tenant_id,
                    sync["recipe_id"],
                ),
            )
        return self.get_report_sync(tenant_id, sync_id)

    @staticmethod
    def _ads_capability_gate_dict(row: sqlite3.Row) -> dict[str, Any]:
        value = dict(row)
        for field in (
            "required_capabilities",
            "observed_capabilities",
            "checks",
            "request_ids",
        ):
            value[field] = json.loads(value.pop(f"{field}_json"))
        return value

    def create_ads_capability_gate(
        self,
        tenant_id: str,
        created_by: str,
        connector_account_id: str,
        idempotency_key: str,
        *,
        region: str,
        profile_id: str,
        required_capabilities: list[str],
        attestation_reference: str | None,
        max_attempts: int = 3,
    ) -> tuple[dict[str, Any], bool]:
        if not isinstance(idempotency_key, str) or not 1 <= len(idempotency_key) <= 200:
            raise ValidationError(
                "ads capability gate idempotency_key is required and must be <= 200 characters"
            )
        if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or not 1 <= max_attempts <= 10:
            raise ValidationError("ads capability gate max_attempts must be between 1 and 10")
        gate_id = self._id()
        now = utc_now()
        try:
            with self.transaction() as conn:
                account = conn.execute(
                    "SELECT provider FROM connector_accounts WHERE tenant_id=? AND id=?",
                    (tenant_id, connector_account_id),
                ).fetchone()
                if account is None:
                    raise NotFoundError("connector account not found")
                if account["provider"] != "amazon_ads":
                    raise ValidationError(
                        "ads capability gate requires an amazon_ads connector account"
                    )
                actor = conn.execute(
                    "SELECT tenant_id FROM users WHERE id=?", (created_by,)
                ).fetchone()
                if actor is None or actor["tenant_id"] != tenant_id:
                    raise ValidationError(
                        "ads capability gate creator does not belong to tenant"
                    )
                conn.execute(
                    """INSERT INTO ads_capability_gates(
                       id,tenant_id,connector_account_id,created_by,idempotency_key,
                       status,region,profile_id,required_capabilities_json,
                       observed_capabilities_json,checks_json,attestation_reference,
                       request_ids_json,available_at,max_attempts,created_at,updated_at)
                       VALUES(?,?,?,?,?,'checking',?,?,?,'[]','[]',?,'[]',?,?,?,?)""",
                    (
                        gate_id,
                        tenant_id,
                        connector_account_id,
                        created_by,
                        idempotency_key,
                        region,
                        profile_id,
                        json.dumps(required_capabilities, sort_keys=True),
                        attestation_reference,
                        now,
                        max_attempts,
                        now,
                        now,
                    ),
                )
        except sqlite3.IntegrityError:
            with self.connect() as conn:
                row = conn.execute(
                    """SELECT * FROM ads_capability_gates
                       WHERE tenant_id=? AND idempotency_key=?""",
                    (tenant_id, idempotency_key),
                ).fetchone()
            if row is None:
                raise ConflictError("ads capability gate idempotency conflict")
            existing = self._ads_capability_gate_dict(row)
            if existing["connector_account_id"] != connector_account_id:
                raise ConflictError(
                    "idempotency key was used for a different connector account"
                )
            if existing["attestation_reference"] != attestation_reference:
                raise ConflictError(
                    "idempotency key was used with a different attestation_reference"
                )
            return existing, True
        return self.get_ads_capability_gate(tenant_id, gate_id), False

    def get_ads_capability_gate(
        self, tenant_id: str, gate_id: str
    ) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM ads_capability_gates WHERE tenant_id=? AND id=?",
                (tenant_id, gate_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("ads capability gate not found")
        return self._ads_capability_gate_dict(row)

    def list_ads_capability_gates(
        self, tenant_id: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM ads_capability_gates WHERE tenant_id=?
                   ORDER BY created_at DESC,id DESC LIMIT ?""",
                (tenant_id, limit),
            ).fetchall()
        return [self._ads_capability_gate_dict(row) for row in rows]

    def claim_ads_capability_gate(
        self, tenant_id: str, gate_id: str, *, lease_seconds: int = 300
    ) -> dict[str, Any]:
        now = utc_now()
        lease_until = self._lease_until(lease_seconds)
        with self.transaction() as conn:
            conn.execute(
                """UPDATE ads_capability_gates SET status='failed',lease_until=NULL,
                   error_code='max_attempts',
                   error_message='ads capability gate exhausted its retry budget',
                   completed_at=?,updated_at=?
                   WHERE tenant_id=? AND id=? AND status='checking'
                     AND attempt_count>=max_attempts
                     AND (lease_until IS NULL OR lease_until<?)""",
                (now, now, tenant_id, gate_id, now),
            )
            result = conn.execute(
                """UPDATE ads_capability_gates
                   SET lease_until=?,attempt_count=attempt_count+1,updated_at=?
                   WHERE tenant_id=? AND id=? AND status='checking'
                     AND available_at<=? AND attempt_count<max_attempts
                     AND (lease_until IS NULL OR lease_until<?)""",
                (lease_until, now, tenant_id, gate_id, now, now),
            )
        current = self.get_ads_capability_gate(tenant_id, gate_id)
        if result.rowcount != 1 and current["status"] == "checking":
            raise ConflictError("ads capability gate is not available for checking")
        return current

    def finish_ads_capability_gate(
        self,
        tenant_id: str,
        gate_id: str,
        *,
        status: str,
        observed_capabilities: list[str],
        checks: list[dict[str, Any]],
        request_ids: list[str],
        error_code: str | None = None,
        error_message: str | None = None,
        retry_after_seconds: int | None = None,
    ) -> dict[str, Any]:
        if status not in {"passed", "blocked", "failed"}:
            raise ValidationError("invalid ads capability gate terminal status")
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat(timespec="seconds")
        available_at = (
            now_dt + timedelta(seconds=max(1, min(retry_after_seconds, 3600)))
        ).isoformat(timespec="seconds") if retry_after_seconds is not None else now
        with self.transaction() as conn:
            result = conn.execute(
                """UPDATE ads_capability_gates SET status=?,
                   observed_capabilities_json=?,checks_json=?,request_ids_json=?,
                   retry_after_seconds=?,available_at=?,lease_until=NULL,error_code=?,
                   error_message=?,completed_at=?,updated_at=?
                   WHERE tenant_id=? AND id=? AND status='checking'
                     AND lease_until IS NOT NULL""",
                (
                    status,
                    json.dumps(observed_capabilities, sort_keys=True),
                    json.dumps(checks, sort_keys=True),
                    json.dumps(sorted(set(request_ids))[:16]),
                    retry_after_seconds,
                    available_at,
                    error_code,
                    error_message[:1000] if error_message else None,
                    now,
                    now,
                    tenant_id,
                    gate_id,
                ),
            )
            if result.rowcount != 1:
                raise ConflictError("ads capability gate is not actively checking")
        return self.get_ads_capability_gate(tenant_id, gate_id)

    def append_audit(self, tenant_id: str, actor_user_id: str | None, request_id: str, action: str,
                     resource_type: str, resource_id: str | None, outcome: str, metadata: dict[str, Any]) -> str:
        event_id = self._id()
        with self.transaction() as conn:
            self.require_tenant(conn, tenant_id)
            if actor_user_id is not None:
                actor = conn.execute("SELECT tenant_id FROM users WHERE id=?", (actor_user_id,)).fetchone()
                if actor is None or actor["tenant_id"] != tenant_id:
                    raise ValidationError("audit actor does not belong to tenant")
            conn.execute(
                """INSERT INTO audit_events(id,tenant_id,actor_user_id,request_id,action,resource_type,resource_id,outcome,metadata_json,created_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (event_id, tenant_id, actor_user_id, request_id, action, resource_type, resource_id,
                 outcome, json.dumps(metadata, ensure_ascii=False, sort_keys=True), utc_now()),
            )
        return event_id

    def list_audit(self, tenant_id: str, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 500))
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM audit_events WHERE tenant_id=? ORDER BY created_at DESC LIMIT ?",
                (tenant_id, limit),
            ).fetchall()
        events = []
        for row in rows:
            event = dict(row)
            event["metadata"] = json.loads(event.pop("metadata_json"))
            events.append(event)
        return events

    def create_action(self, tenant_id: str, idempotency_key: str, operation: str, payload: dict[str, Any], requested_by: str) -> tuple[dict[str, Any], bool]:
        if not idempotency_key or len(idempotency_key) > 200:
            raise ValidationError("idempotency_key is required and must be <= 200 characters")
        if not operation or not isinstance(payload, dict):
            raise ValidationError("operation and object payload are required")
        action_id = self._id()
        now = utc_now()
        try:
            with self.transaction() as conn:
                self.require_tenant(conn, tenant_id)
                requester = conn.execute("SELECT tenant_id FROM users WHERE id=?", (requested_by,)).fetchone()
                if requester is None or requester["tenant_id"] != tenant_id:
                    raise ValidationError("requesting user does not belong to tenant")
                conn.execute(
                    "INSERT INTO actions(id,tenant_id,idempotency_key,operation,payload_json,requested_by,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
                    (action_id, tenant_id, idempotency_key, operation, json.dumps(payload, ensure_ascii=False, sort_keys=True), requested_by, "requested", now, now),
                )
        except sqlite3.IntegrityError:
            with self.connect() as conn:
                row = conn.execute(
                    "SELECT * FROM actions WHERE tenant_id=? AND idempotency_key=?", (tenant_id, idempotency_key)
                ).fetchone()
            if row is None:
                raise ConflictError("action idempotency conflict")
            if row["operation"] != operation or json.loads(row["payload_json"]) != payload:
                raise ConflictError("idempotency key was already used with a different action")
            return self.action_dict(row), True
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM actions WHERE id=?", (action_id,)).fetchone()
        return self.action_dict(row), False

    @staticmethod
    def action_dict(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["payload"] = json.loads(result.pop("payload_json"))
        if result.get("result_json") is not None:
            result["result"] = json.loads(result.pop("result_json"))
        else:
            result.pop("result_json", None)
        return result

    def get_action(self, tenant_id: str, action_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM actions WHERE id=? AND tenant_id=?", (action_id, tenant_id)).fetchone()
        if row is None:
            raise NotFoundError("action not found")
        return self.action_dict(row)

    def list_actions(
        self, tenant_id: str, *, status: str | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self.connect() as conn:
            if status is None:
                rows = conn.execute(
                    "SELECT * FROM actions WHERE tenant_id=? ORDER BY rowid DESC LIMIT ?",
                    (tenant_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM actions WHERE tenant_id=? AND status=?
                       ORDER BY rowid DESC LIMIT ?""",
                    (tenant_id, status, limit),
                ).fetchall()
        return [self.action_dict(row) for row in rows]

    def transition_action(self, tenant_id: str, action_id: str, expected: str, status: str,
                          approved_by: str | None = None, result: dict[str, Any] | None = None,
                          error: str | None = None, expected_attempt: int | None = None) -> dict[str, Any]:
        if status not in {"approved", "executing", "executed", "failed", "rejected"}:
            raise ValidationError("invalid action status")
        with self.transaction() as conn:
            if approved_by is not None:
                approver = conn.execute("SELECT tenant_id FROM users WHERE id=?", (approved_by,)).fetchone()
                if approver is None or approver["tenant_id"] != tenant_id:
                    raise ValidationError("approving user does not belong to tenant")
            params: list[Any] = [status, utc_now()]
            updates = "status=?,updated_at=?"
            if status != "executing":
                updates += ",lease_until=NULL"
            if approved_by is not None:
                updates += ",approved_by=?"
                params.append(approved_by)
            if result is not None:
                updates += ",result_json=?"
                params.append(json.dumps(result, ensure_ascii=False, sort_keys=True))
            if error is not None:
                updates += ",error=?"
                params.append(error[:2000])
            params += [action_id, tenant_id, expected]
            where = "id=? AND tenant_id=? AND status=?"
            if expected_attempt is not None:
                where += " AND attempt_count=?"
                params.append(expected_attempt)
            cur = conn.execute(f"UPDATE actions SET {updates} WHERE {where}", params)
            if cur.rowcount != 1:
                row = conn.execute("SELECT status FROM actions WHERE id=? AND tenant_id=?", (action_id, tenant_id)).fetchone()
                if row is None:
                    raise NotFoundError("action not found")
                raise ConflictError(f"action is {row['status']}, expected {expected}")
        return self.get_action(tenant_id, action_id)

    @staticmethod
    def _lease_until(seconds: int) -> str:
        return (datetime.now(timezone.utc) + timedelta(seconds=max(1, min(seconds, 3600)))).isoformat(timespec="seconds")

    def claim_action(self, tenant_id: str, action_id: str, lease_seconds: int = 300) -> dict[str, Any]:
        """Atomically claim an approved action or an expired execution lease."""
        now = utc_now()
        lease_until = self._lease_until(lease_seconds)
        with self.transaction() as conn:
            cur = conn.execute(
                """UPDATE actions
                   SET status='executing', updated_at=?, lease_until=?,
                       attempt_count=attempt_count+1, last_attempt_at=?
                   WHERE id=? AND tenant_id=? AND (
                     status='approved' OR
                     (status='executing' AND lease_until IS NOT NULL AND lease_until < ?)
                   )""",
                (now, lease_until, now, action_id, tenant_id, now),
            )
            if cur.rowcount != 1:
                row = conn.execute("SELECT status,lease_until FROM actions WHERE id=? AND tenant_id=?", (action_id, tenant_id)).fetchone()
                if row is None:
                    raise NotFoundError("action not found")
                raise ConflictError(f"action is {row['status']}, lease_until={row['lease_until']}")
        return self.get_action(tenant_id, action_id)

    def retry_action(self, tenant_id: str, action_id: str) -> dict[str, Any]:
        """Re-queue a failed or expired approved action without bypassing approval."""
        now = utc_now()
        with self.transaction() as conn:
            cur = conn.execute(
                """UPDATE actions SET status='approved', updated_at=?, lease_until=NULL, error=NULL
                   WHERE id=? AND tenant_id=? AND approved_by IS NOT NULL AND (
                     status='failed' OR
                     (status='executing' AND lease_until IS NOT NULL AND lease_until < ?)
                   )""",
                (now, action_id, tenant_id, now),
            )
            if cur.rowcount != 1:
                row = conn.execute("SELECT status,approved_by FROM actions WHERE id=? AND tenant_id=?", (action_id, tenant_id)).fetchone()
                if row is None:
                    raise NotFoundError("action not found")
                raise ConflictError(f"action cannot be retried from status {row['status']}")
        return self.get_action(tenant_id, action_id)

    def get_sync_cursor(self, tenant_id: str, provider: str, external_account_id: str) -> str | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT cursor FROM sync_cursors WHERE tenant_id=? AND provider=? AND external_account_id=?",
                (tenant_id, provider, external_account_id),
            ).fetchone()
        return row["cursor"] if row else None

    def set_sync_cursor(self, tenant_id: str, provider: str, external_account_id: str, cursor: str | None) -> None:
        with self.transaction() as conn:
            self.require_tenant(conn, tenant_id)
            conn.execute(
                """INSERT INTO sync_cursors(tenant_id,provider,external_account_id,cursor,updated_at)
                   VALUES(?,?,?,?,?) ON CONFLICT(tenant_id,provider,external_account_id)
                   DO UPDATE SET cursor=excluded.cursor,updated_at=excluded.updated_at""",
                (tenant_id, provider, external_account_id, cursor, utc_now()),
            )

    def save_records(self, tenant_id: str, provider: str, records: list[dict[str, Any]]) -> int:
        now = utc_now()
        count = 0
        with self.transaction() as conn:
            self.require_tenant(conn, tenant_id)
            for record in records:
                external_id = str(record.get("id", "")).strip()
                if not external_id:
                    continue
                conn.execute(
                    """INSERT INTO connector_records(id,tenant_id,provider,external_id,payload_json,synced_at)
                       VALUES(?,?,?,?,?,?) ON CONFLICT(tenant_id,provider,external_id)
                       DO UPDATE SET payload_json=excluded.payload_json,synced_at=excluded.synced_at""",
                    (self._id(), tenant_id, provider, external_id, json.dumps(record, ensure_ascii=False, sort_keys=True), now),
                )
                count += 1
        return count

    def list_records(self, tenant_id: str, provider: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 500))
        with self.connect() as conn:
            if provider:
                rows = conn.execute("SELECT * FROM connector_records WHERE tenant_id=? AND provider=? ORDER BY synced_at DESC LIMIT ?", (tenant_id, provider, limit)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM connector_records WHERE tenant_id=? ORDER BY synced_at DESC LIMIT ?", (tenant_id, limit)).fetchall()
        records = []
        for row in rows:
            record = dict(row)
            record["payload"] = json.loads(record.pop("payload_json"))
            records.append(record)
        return records

    @staticmethod
    def _evidence_import_dict(
        row: sqlite3.Row, *, include_rows: bool = False
    ) -> dict[str, Any]:
        result = dict(row)
        result["columns"] = json.loads(result.pop("columns_json"))
        result["column_mapping"] = json.loads(result.pop("column_mapping_json"))
        rows_json = result.pop("rows_json")
        if include_rows:
            result["rows"] = json.loads(rows_json)
        return result

    def create_evidence_import(
        self,
        tenant_id: str,
        created_by: str,
        idempotency_key: str,
        *,
        platform: str,
        report_type: str,
        filename: str,
        observed_at: str,
        sha256: str,
        delimiter: str,
        rows: list[dict[str, str]],
        columns: list[str],
        column_mapping: dict[str, str],
        blank_rows_skipped: int,
        formula_cells: int,
        media_type: str,
        byte_size: int,
        object_key: str,
        sheet_name: str | None,
    ) -> tuple[dict[str, Any], bool]:
        if not idempotency_key or len(idempotency_key) > 200:
            raise ValidationError("idempotency_key is required and must be <= 200 characters")
        import_id = self._id()
        now = utc_now()
        rows_json = json.dumps(rows, ensure_ascii=False, sort_keys=True)
        columns_json = json.dumps(columns, ensure_ascii=False)
        column_mapping_json = json.dumps(column_mapping, ensure_ascii=False, sort_keys=True)
        try:
            with self.transaction() as conn:
                self.require_tenant(conn, tenant_id)
                creator = conn.execute(
                    "SELECT tenant_id FROM users WHERE id=?", (created_by,)
                ).fetchone()
                if creator is None or creator["tenant_id"] != tenant_id:
                    raise ValidationError("importing user does not belong to tenant")
                conn.execute(
                    """INSERT INTO evidence_imports(
                       id,tenant_id,idempotency_key,platform,report_type,filename,
                       observed_at,sha256,delimiter,row_count,blank_rows_skipped,
                       formula_cells,columns_json,column_mapping_json,rows_json,
                       media_type,byte_size,object_key,sheet_name,created_by,created_at
                       ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        import_id,
                        tenant_id,
                        idempotency_key,
                        platform,
                        report_type,
                        filename,
                        observed_at,
                        sha256,
                        delimiter,
                        len(rows),
                        blank_rows_skipped,
                        formula_cells,
                        columns_json,
                        column_mapping_json,
                        rows_json,
                        media_type,
                        byte_size,
                        object_key,
                        sheet_name,
                        created_by,
                        now,
                    ),
                )
        except sqlite3.IntegrityError:
            with self.connect() as conn:
                row = conn.execute(
                    """SELECT * FROM evidence_imports
                       WHERE tenant_id=? AND idempotency_key=?""",
                    (tenant_id, idempotency_key),
                ).fetchone()
            if row is None:
                raise ConflictError("evidence import idempotency conflict")
            existing = self._evidence_import_dict(row, include_rows=True)
            if any(
                existing[key] != expected
                for key, expected in {
                    "platform": platform,
                    "report_type": report_type,
                    "filename": filename,
                    "observed_at": observed_at,
                    "sha256": sha256,
                }.items()
            ):
                raise ConflictError(
                    "idempotency key was already used with a different evidence import"
                )
            return existing, True
        return self.get_evidence_import(tenant_id, import_id, include_rows=True), False

    def get_evidence_import(
        self, tenant_id: str, import_id: str, *, include_rows: bool = False
    ) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM evidence_imports WHERE id=? AND tenant_id=?",
                (import_id, tenant_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("evidence import not found")
        return self._evidence_import_dict(row, include_rows=include_rows)

    def list_evidence_imports(self, tenant_id: str, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM evidence_imports WHERE tenant_id=?
                   ORDER BY rowid DESC LIMIT ?""",
                (tenant_id, limit),
            ).fetchall()
        return [self._evidence_import_dict(row) for row in rows]

    def page_evidence_imports(
        self, tenant_id: str, *, limit: int, cursor: str | None = None
    ) -> tuple[list[dict[str, Any]], str | None]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
            raise ValidationError("limit must be an integer between 1 and 100")
        with self.connect() as conn:
            if cursor:
                anchor = conn.execute(
                    "SELECT rowid FROM evidence_imports WHERE tenant_id=? AND id=?",
                    (tenant_id, cursor),
                ).fetchone()
                if anchor is None:
                    raise NotFoundError("metric backfill cursor not found")
                rows = conn.execute(
                    """SELECT * FROM evidence_imports
                       WHERE tenant_id=? AND rowid < ?
                       ORDER BY rowid DESC LIMIT ?""",
                    (tenant_id, anchor["rowid"], limit + 1),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM evidence_imports WHERE tenant_id=?
                       ORDER BY rowid DESC LIMIT ?""",
                    (tenant_id, limit + 1),
                ).fetchall()
        page = rows[:limit]
        next_cursor = str(page[-1]["id"]) if len(rows) > limit and page else None
        return [self._evidence_import_dict(row) for row in page], next_cursor

    @staticmethod
    def _metric_materialization_dict(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["currencies"] = json.loads(result.pop("currencies_json"))
        result["quality_flags"] = json.loads(result.pop("quality_flags_json"))
        result["issues"] = json.loads(result.pop("issues_json"))
        return result

    @staticmethod
    def _metric_observation_dict(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["dimensions"] = json.loads(result.pop("dimensions_json"))
        result["provenance"] = json.loads(result.pop("provenance_json"))
        result["quality_flags"] = json.loads(result.pop("quality_json"))
        return result

    def metric_source_context(
        self, tenant_id: str, evidence_import_id: str
    ) -> dict[str, Any]:
        self.get_evidence_import(tenant_id, evidence_import_id)
        with self.connect() as conn:
            row = conn.execute(
                """SELECT rs.connector_account_id,rr.marketplace_ids_json,
                          rs.period_start,rs.period_end,rs.id AS report_sync_id
                   FROM report_syncs rs
                   JOIN report_recipes rr
                     ON rr.tenant_id=rs.tenant_id AND rr.id=rs.recipe_id
                   WHERE rs.tenant_id=? AND rs.evidence_import_id=?
                         AND rs.status='succeeded'
                   ORDER BY rs.completed_at DESC LIMIT 1""",
                (tenant_id, evidence_import_id),
            ).fetchone()
        if row is None:
            return {
                "connector_account_id": None,
                "marketplace_ids": [],
                "period_start": None,
                "period_end": None,
                "report_sync_id": None,
            }
        result = dict(row)
        result["marketplace_ids"] = json.loads(result.pop("marketplace_ids_json"))
        return result

    def start_metric_materialization(
        self,
        tenant_id: str,
        created_by: str,
        evidence_import_id: str,
        idempotency_key: str,
        *,
        calculation_version: str,
    ) -> tuple[dict[str, Any], bool]:
        if not isinstance(idempotency_key, str) or not 1 <= len(idempotency_key) <= 200:
            raise ValidationError(
                "idempotency_key is required and must be <= 200 characters"
            )
        materialization_id = self._id()
        now = utc_now()
        try:
            with self.transaction() as conn:
                self.require_tenant(conn, tenant_id)
                creator = conn.execute(
                    "SELECT tenant_id FROM users WHERE id=?", (created_by,)
                ).fetchone()
                if creator is None or creator["tenant_id"] != tenant_id:
                    raise ValidationError(
                        "metric materialization creator does not belong to tenant"
                    )
                evidence = conn.execute(
                    "SELECT tenant_id FROM evidence_imports WHERE tenant_id=? AND id=?",
                    (tenant_id, evidence_import_id),
                ).fetchone()
                if evidence is None:
                    raise NotFoundError("evidence import not found")
                conn.execute(
                    """INSERT INTO metric_materializations(
                       id,tenant_id,evidence_import_id,created_by,idempotency_key,
                       calculation_version,status,attempt_count,max_attempts,lease_until,observation_count,
                       quarantine_count,currencies_json,quality_flags_json,issues_json,error_code,error_message,
                       created_at,updated_at,completed_at)
                       VALUES(?,?,?,?,?,?,'running',1,5,?,0,0,'[]','[]','[]',NULL,NULL,?,?,NULL)""",
                    (
                        materialization_id,
                        tenant_id,
                        evidence_import_id,
                        created_by,
                        idempotency_key,
                        calculation_version,
                        (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(
                            timespec="seconds"
                        ),
                        now,
                        now,
                    ),
                )
        except sqlite3.IntegrityError as exc:
            with self.connect() as conn:
                same_key = conn.execute(
                    """SELECT * FROM metric_materializations
                       WHERE tenant_id=? AND idempotency_key=?""",
                    (tenant_id, idempotency_key),
                ).fetchone()
                semantic = conn.execute(
                    """SELECT * FROM metric_materializations
                       WHERE tenant_id=? AND evidence_import_id=?
                             AND calculation_version=?""",
                    (tenant_id, evidence_import_id, calculation_version),
                ).fetchone()
            existing = same_key or semantic
            if same_key is not None:
                if (
                    same_key["evidence_import_id"] != evidence_import_id
                    or same_key["calculation_version"] != calculation_version
                ):
                    raise ConflictError(
                        "idempotency key was already used for another metric materialization"
                    ) from exc
                if same_key["status"] != "running":
                    return self._metric_materialization_dict(same_key), True
            if existing is not None:
                if existing["status"] == "running":
                    lease_until = datetime.fromisoformat(
                        str(existing["lease_until"]).replace("Z", "+00:00")
                    )
                    if lease_until > datetime.now(timezone.utc):
                        return self._metric_materialization_dict(existing), True
                    if existing["attempt_count"] >= existing["max_attempts"]:
                        with self.transaction() as conn:
                            conn.execute(
                                """UPDATE metric_materializations
                                   SET status='failed',lease_until=NULL,
                                       error_code='max_attempts',
                                       error_message='metric materialization exhausted recovery attempts',
                                       updated_at=?,completed_at=?
                                   WHERE tenant_id=? AND id=? AND status='running'""",
                                (now, now, tenant_id, existing["id"]),
                            )
                        return self.get_metric_materialization(
                            tenant_id, str(existing["id"])
                        ), True
                elif existing["status"] != "failed":
                    return self._metric_materialization_dict(existing), True
                elif existing["attempt_count"] >= existing["max_attempts"]:
                    return self._metric_materialization_dict(existing), True
                # A persisted failed materialization may be explicitly retried.
                # The stable row preserves provenance; attempt_count makes the
                # retry visible without producing duplicate observations.
                with self.transaction() as conn:
                    conn.execute(
                        """UPDATE metric_materializations
                           SET status='running',attempt_count=attempt_count+1,
                               lease_until=?,
                               issues_json='[]',error_code=NULL,error_message=NULL,
                               updated_at=?,completed_at=NULL
                           WHERE tenant_id=? AND id=?
                             AND status IN ('running','failed')
                             AND attempt_count < max_attempts""",
                        (
                            (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(
                                timespec="seconds"
                            ),
                            now,
                            tenant_id,
                            existing["id"],
                        ),
                    )
                return self.get_metric_materialization(
                    tenant_id, str(existing["id"])
                ), False
            raise ConflictError("metric materialization conflict") from exc
        return self.get_metric_materialization(tenant_id, materialization_id), False

    def complete_metric_materialization(
        self,
        tenant_id: str,
        materialization_id: str,
        *,
        status: str,
        issues: list[dict[str, Any]],
        observations: list[dict[str, Any]],
        quarantine_count: int | None = None,
    ) -> dict[str, Any]:
        if status not in {"succeeded", "partial", "quarantined"}:
            raise ValidationError(
                "completed materialization must be succeeded, partial, or quarantined"
            )
        now = utc_now()
        with self.transaction() as conn:
            materialization = conn.execute(
                """SELECT * FROM metric_materializations
                   WHERE tenant_id=? AND id=?""",
                (tenant_id, materialization_id),
            ).fetchone()
            if materialization is None:
                raise NotFoundError("metric materialization not found")
            if materialization["status"] != "running":
                raise ConflictError("metric materialization is not running")
            for observation in observations:
                connector_account_id = observation.get("connector_account_id")
                if connector_account_id is not None:
                    account = conn.execute(
                        """SELECT tenant_id FROM connector_accounts
                           WHERE tenant_id=? AND id=?""",
                        (tenant_id, connector_account_id),
                    ).fetchone()
                    if account is None:
                        raise NotFoundError("connector account not found")
                conn.execute(
                    """INSERT INTO metric_observations(
                       id,tenant_id,materialization_id,evidence_import_id,
                       connector_account_id,marketplace_id,platform,report_type,
                       metric_key,series_key,value_decimal,currency,unit,time_grain,
                       period_start,period_end,observed_at,dimensions_json,
                       provenance_json,quality_json,calculation_version,created_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        self._id(),
                        tenant_id,
                        materialization_id,
                        materialization["evidence_import_id"],
                        connector_account_id,
                        observation.get("marketplace_id"),
                        observation["platform"],
                        observation["report_type"],
                        observation["metric_key"],
                        observation["series_key"],
                        observation["value_decimal"],
                        observation.get("currency"),
                        observation["unit"],
                        observation["time_grain"],
                        observation["period_start"],
                        observation["period_end"],
                        observation["observed_at"],
                        json.dumps(
                            observation.get("dimensions", {}),
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                        json.dumps(
                            observation["provenance"],
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                        json.dumps(
                            observation.get("quality_flags", []),
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                        materialization["calculation_version"],
                        now,
                    ),
                )
            conn.execute(
                """UPDATE metric_materializations
                   SET status=?,lease_until=NULL,observation_count=?,quarantine_count=?,currencies_json=?,quality_flags_json=?,issues_json=?,
                       error_code=NULL,error_message=NULL,updated_at=?,completed_at=?
                   WHERE tenant_id=? AND id=?""",
                (
                    status,
                    len(observations),
                    len(issues) if quarantine_count is None else quarantine_count,
                    json.dumps(
                        sorted(
                            {
                                str(item["currency"])
                                for item in observations
                                if item.get("currency")
                            }
                        )
                    ),
                    json.dumps(
                        sorted(
                            {
                                str(flag)
                                for item in observations
                                for flag in (
                                    item.get("quality_flags", {}).get("flags", [])
                                    if isinstance(item.get("quality_flags"), dict)
                                    else []
                                )
                            }
                        )[:50]
                    ),
                    json.dumps(issues, ensure_ascii=False, sort_keys=True),
                    now,
                    now,
                    tenant_id,
                    materialization_id,
                ),
            )
        return self.get_metric_materialization(tenant_id, materialization_id)

    def fail_metric_materialization(
        self,
        tenant_id: str,
        materialization_id: str,
        *,
        error_code: str,
        error_message: str,
        issues: list[dict[str, Any]] | None = None,
        quarantine_count: int | None = None,
    ) -> dict[str, Any]:
        if not error_code or not error_message:
            raise ValidationError("metric materialization failure requires an error")
        now = utc_now()
        with self.transaction() as conn:
            result = conn.execute(
                """UPDATE metric_materializations
                   SET status='failed',lease_until=NULL,observation_count=0,quarantine_count=?,
                       currencies_json='[]',quality_flags_json='[]',issues_json=?,error_code=?,error_message=?,updated_at=?,completed_at=?
                   WHERE tenant_id=? AND id=? AND status='running'""",
                (
                    len(issues or []) if quarantine_count is None else quarantine_count,
                    json.dumps(issues or [], ensure_ascii=False, sort_keys=True),
                    error_code[:100],
                    error_message[:1000],
                    now,
                    now,
                    tenant_id,
                    materialization_id,
                ),
            )
            if result.rowcount != 1:
                existing = conn.execute(
                    """SELECT status FROM metric_materializations
                       WHERE tenant_id=? AND id=?""",
                    (tenant_id, materialization_id),
                ).fetchone()
                if existing is None:
                    raise NotFoundError("metric materialization not found")
                raise ConflictError("metric materialization is not running")
        return self.get_metric_materialization(tenant_id, materialization_id)

    def get_metric_materialization(
        self, tenant_id: str, materialization_id: str
    ) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                """SELECT * FROM metric_materializations
                   WHERE tenant_id=? AND id=?""",
                (tenant_id, materialization_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("metric materialization not found")
        return self._metric_materialization_dict(row)

    def list_metric_materializations(
        self,
        tenant_id: str,
        limit: int = 100,
        *,
        cursor: str | None = None,
        evidence_import_id: str | None = None,
        status: str | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 200:
            raise ValidationError("limit must be an integer between 1 and 200")
        predicates = ["tenant_id=?"]
        values: list[Any] = [tenant_id]
        if cursor:
            with self.connect() as conn:
                anchor = conn.execute(
                    """SELECT rowid FROM metric_materializations
                       WHERE tenant_id=? AND id=?""",
                    (tenant_id, cursor),
                ).fetchone()
            if anchor is None:
                raise NotFoundError("metric materialization cursor not found")
            predicates.append("rowid < ?")
            values.append(anchor["rowid"])
        if evidence_import_id:
            predicates.append("evidence_import_id=?")
            values.append(evidence_import_id)
        if status:
            predicates.append("status=?")
            values.append(status)
        values.append(limit + 1)
        with self.connect() as conn:
            rows = conn.execute(
                f"""SELECT * FROM metric_materializations
                    WHERE {' AND '.join(predicates)}
                    ORDER BY rowid DESC LIMIT ?""",
                values,
            ).fetchall()
        page = rows[:limit]
        next_cursor = str(page[-1]["id"]) if len(rows) > limit and page else None
        return [self._metric_materialization_dict(row) for row in page], next_cursor

    def get_metric_observation(
        self, tenant_id: str, observation_id: str
    ) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                """SELECT * FROM metric_observations
                   WHERE tenant_id=? AND id=?""",
                (tenant_id, observation_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("metric observation not found")
        return self._metric_observation_dict(row)

    def list_metric_observations(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
        cursor: str | None = None,
        evidence_import_id: str | None = None,
        metric_key: str | None = None,
        currency: str | None = None,
        platform: str | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 200:
            raise ValidationError("limit must be an integer between 1 and 200")
        predicates = ["tenant_id=?"]
        values: list[Any] = [tenant_id]
        if cursor:
            with self.connect() as conn:
                anchor = conn.execute(
                    """SELECT rowid FROM metric_observations
                       WHERE tenant_id=? AND id=?""",
                    (tenant_id, cursor),
                ).fetchone()
            if anchor is None:
                raise NotFoundError("metric observation cursor not found")
            predicates.append("rowid < ?")
            values.append(anchor["rowid"])
        if evidence_import_id is not None:
            predicates.append("evidence_import_id=?")
            values.append(evidence_import_id)
        if platform is not None:
            predicates.append("platform=?")
            values.append(platform)
        if metric_key is not None:
            predicates.append("metric_key=?")
            values.append(metric_key)
        if currency is not None:
            predicates.append("currency=?")
            values.append(currency)
        values.append(limit + 1)
        with self.connect() as conn:
            rows = conn.execute(
                f"""SELECT * FROM metric_observations
                    WHERE {' AND '.join(predicates)}
                    ORDER BY rowid DESC LIMIT ?""",
                values,
            ).fetchall()
        page = rows[:limit]
        next_cursor = str(page[-1]["id"]) if len(rows) > limit and page else None
        return [self._metric_observation_dict(row) for row in page], next_cursor

    @staticmethod
    def _agent_run_dict(row: sqlite3.Row, *, include_evidence: bool = True) -> dict[str, Any]:
        result = dict(row)
        evidence_json = result.pop("evidence_json")
        result["platforms"] = json.loads(result.pop("platforms_json"))
        if include_evidence:
            result["evidence"] = json.loads(evidence_json)
        return result

    def create_agent_run(
        self,
        tenant_id: str,
        requested_by: str,
        idempotency_key: str,
        workflow: str,
        objective: str,
        evidence: list[dict[str, Any]],
        platforms: list[str],
        *,
        provider: str,
    ) -> tuple[dict[str, Any], bool]:
        if not idempotency_key or len(idempotency_key) > 200:
            raise ValidationError("idempotency_key is required and must be <= 200 characters")
        run_id = self._id()
        now = utc_now()
        serialized = json.dumps(evidence, ensure_ascii=False, sort_keys=True)
        try:
            with self.transaction() as conn:
                self.require_tenant(conn, tenant_id)
                requester = conn.execute(
                    "SELECT tenant_id FROM users WHERE id=?", (requested_by,)
                ).fetchone()
                if requester is None or requester["tenant_id"] != tenant_id:
                    raise ValidationError("requesting user does not belong to tenant")
                conn.execute(
                    """INSERT INTO agent_runs(
                       id,tenant_id,idempotency_key,workflow,objective,evidence_json,platforms_json,
                       requested_by,status,provider,created_at,updated_at
                       ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        run_id,
                        tenant_id,
                        idempotency_key,
                        workflow,
                        objective,
                        serialized,
                        json.dumps(platforms, sort_keys=True),
                        requested_by,
                        "requested",
                        provider,
                        now,
                        now,
                    ),
                )
                conn.execute(
                    """INSERT INTO agent_artifacts(
                       id,tenant_id,run_id,task_id,kind,attempt,content_json,created_at
                       ) VALUES(?,?,?,?,?,?,?,?)""",
                    (self._id(), tenant_id, run_id, None, "input_evidence", 0, serialized, now),
                )
                conn.execute(
                    """INSERT INTO agent_events(
                       id,tenant_id,run_id,task_id,event_type,payload_json,created_at
                       ) VALUES(?,?,?,?,?,?,?)""",
                    (
                        self._id(),
                        tenant_id,
                        run_id,
                        None,
                        "run.created",
                        json.dumps(
                            {"workflow": workflow, "platforms": platforms}, sort_keys=True
                        ),
                        now,
                    ),
                )
        except sqlite3.IntegrityError:
            with self.connect() as conn:
                row = conn.execute(
                    "SELECT * FROM agent_runs WHERE tenant_id=? AND idempotency_key=?",
                    (tenant_id, idempotency_key),
                ).fetchone()
            if row is None:
                raise ConflictError("agent run idempotency conflict")
            existing = self._agent_run_dict(row)
            if (
                existing["workflow"] != workflow
                or existing["objective"] != objective
                or existing["evidence"] != evidence
            ):
                raise ConflictError("idempotency key was already used with a different agent run")
            return existing, True
        return self.get_agent_run(tenant_id, run_id), False

    def get_agent_run(self, tenant_id: str, run_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM agent_runs WHERE id=? AND tenant_id=?", (run_id, tenant_id)
            ).fetchone()
        if row is None:
            raise NotFoundError("agent run not found")
        return self._agent_run_dict(row)

    def list_agent_runs(self, tenant_id: str, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM agent_runs WHERE tenant_id=?
                   ORDER BY rowid DESC LIMIT ?""",
                (tenant_id, limit),
            ).fetchall()
        return [self._agent_run_dict(row, include_evidence=False) for row in rows]

    def claim_agent_run(self, tenant_id: str, run_id: str, *, provider: str, model: str) -> dict[str, Any]:
        now = utc_now()
        with self.transaction() as conn:
            cur = conn.execute(
                """UPDATE agent_runs SET status='running',provider=?,model=?,
                   attempt_count=attempt_count+1,error=NULL,completed_at=NULL,updated_at=?
                   WHERE id=? AND tenant_id=? AND status IN ('requested','failed')""",
                (provider, model, now, run_id, tenant_id),
            )
            if cur.rowcount != 1:
                row = conn.execute(
                    "SELECT status FROM agent_runs WHERE id=? AND tenant_id=?", (run_id, tenant_id)
                ).fetchone()
                if row is None:
                    raise NotFoundError("agent run not found")
                raise ConflictError(f"agent run cannot execute from status {row['status']}")
            conn.execute(
                """INSERT INTO agent_events(
                   id,tenant_id,run_id,task_id,event_type,payload_json,created_at
                   ) VALUES(?,?,?,?,?,?,?)""",
                (
                    self._id(),
                    tenant_id,
                    run_id,
                    None,
                    "run.started",
                    json.dumps({"provider": provider, "model": model}, sort_keys=True),
                    now,
                ),
            )
        return self.get_agent_run(tenant_id, run_id)

    def prepare_agent_tasks(
        self, tenant_id: str, run_id: str, tasks: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        now = utc_now()
        with self.transaction() as conn:
            run = conn.execute(
                "SELECT status FROM agent_runs WHERE id=? AND tenant_id=?", (run_id, tenant_id)
            ).fetchone()
            if run is None:
                raise NotFoundError("agent run not found")
            if run["status"] != "running":
                raise ConflictError("agent run must be running before tasks are prepared")
            for task in tasks:
                conn.execute(
                    """INSERT INTO agent_tasks(
                       id,tenant_id,run_id,agent_name,skill_ids_json,status,created_at
                       ) VALUES(?,?,?,?,?,'pending',?)
                       ON CONFLICT(run_id,agent_name) DO UPDATE SET
                         skill_ids_json=excluded.skill_ids_json,status='pending',error=NULL,
                         started_at=NULL,completed_at=NULL""",
                    (
                        self._id(),
                        tenant_id,
                        run_id,
                        task["agent_name"],
                        json.dumps(task["skill_ids"], ensure_ascii=False, sort_keys=True),
                        now,
                    ),
                )
        return self.list_agent_tasks(tenant_id, run_id)

    @staticmethod
    def _agent_task_dict(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["skill_ids"] = json.loads(result.pop("skill_ids_json"))
        return result

    def list_agent_tasks(self, tenant_id: str, run_id: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM agent_tasks WHERE tenant_id=? AND run_id=?
                   ORDER BY rowid""",
                (tenant_id, run_id),
            ).fetchall()
        return [self._agent_task_dict(row) for row in rows]

    def start_agent_task(self, tenant_id: str, run_id: str, agent_name: str) -> dict[str, Any]:
        now = utc_now()
        with self.transaction() as conn:
            cur = conn.execute(
                """UPDATE agent_tasks SET status='running',attempt_count=attempt_count+1,
                   error=NULL,started_at=?,completed_at=NULL
                   WHERE tenant_id=? AND run_id=? AND agent_name=? AND status='pending'""",
                (now, tenant_id, run_id, agent_name),
            )
            if cur.rowcount != 1:
                raise ConflictError(f"agent task {agent_name} is not pending")
            row = conn.execute(
                "SELECT id FROM agent_tasks WHERE tenant_id=? AND run_id=? AND agent_name=?",
                (tenant_id, run_id, agent_name),
            ).fetchone()
            conn.execute(
                """INSERT INTO agent_events(
                   id,tenant_id,run_id,task_id,event_type,payload_json,created_at
                   ) VALUES(?,?,?,?,?,?,?)""",
                (
                    self._id(), tenant_id, run_id, row["id"], "task.started",
                    json.dumps({"agent_name": agent_name}, sort_keys=True), now,
                ),
            )
        return self.get_agent_task(tenant_id, run_id, agent_name)

    def get_agent_task(self, tenant_id: str, run_id: str, agent_name: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                """SELECT * FROM agent_tasks
                   WHERE tenant_id=? AND run_id=? AND agent_name=?""",
                (tenant_id, run_id, agent_name),
            ).fetchone()
        if row is None:
            raise NotFoundError("agent task not found")
        return self._agent_task_dict(row)

    def complete_agent_task(
        self,
        tenant_id: str,
        run_id: str,
        agent_name: str,
        content: dict[str, Any],
        *,
        artifact_kind: str = "specialist_finding",
    ) -> dict[str, Any]:
        now = utc_now()
        with self.transaction() as conn:
            row = conn.execute(
                """SELECT id,attempt_count FROM agent_tasks
                   WHERE tenant_id=? AND run_id=? AND agent_name=? AND status='running'""",
                (tenant_id, run_id, agent_name),
            ).fetchone()
            if row is None:
                raise ConflictError(f"agent task {agent_name} is not running")
            conn.execute(
                """UPDATE agent_tasks SET status='completed',completed_at=?
                   WHERE id=? AND tenant_id=?""",
                (now, row["id"], tenant_id),
            )
            conn.execute(
                """INSERT INTO agent_artifacts(
                   id,tenant_id,run_id,task_id,kind,attempt,content_json,created_at
                   ) VALUES(?,?,?,?,?,?,?,?)""",
                (
                    self._id(), tenant_id, run_id, row["id"], artifact_kind,
                    row["attempt_count"], json.dumps(content, ensure_ascii=False, sort_keys=True), now,
                ),
            )
            conn.execute(
                """INSERT INTO agent_events(
                   id,tenant_id,run_id,task_id,event_type,payload_json,created_at
                   ) VALUES(?,?,?,?,?,?,?)""",
                (
                    self._id(), tenant_id, run_id, row["id"], "task.completed",
                    json.dumps({"agent_name": agent_name}, sort_keys=True), now,
                ),
            )
        return self.get_agent_task(tenant_id, run_id, agent_name)

    def fail_agent_task(self, tenant_id: str, run_id: str, agent_name: str, error: str) -> None:
        now = utc_now()
        with self.transaction() as conn:
            row = conn.execute(
                """SELECT id FROM agent_tasks
                   WHERE tenant_id=? AND run_id=? AND agent_name=? AND status='running'""",
                (tenant_id, run_id, agent_name),
            ).fetchone()
            if row is None:
                return
            conn.execute(
                "UPDATE agent_tasks SET status='failed',error=?,completed_at=? WHERE id=? AND tenant_id=?",
                (error[:2000], now, row["id"], tenant_id),
            )
            conn.execute(
                """INSERT INTO agent_events(
                   id,tenant_id,run_id,task_id,event_type,payload_json,created_at
                   ) VALUES(?,?,?,?,?,?,?)""",
                (
                    self._id(), tenant_id, run_id, row["id"], "task.failed",
                    json.dumps({"agent_name": agent_name, "error_type": "AgentExecutionError"}, sort_keys=True), now,
                ),
            )

    def complete_agent_run(
        self, tenant_id: str, run_id: str, report: dict[str, Any]
    ) -> dict[str, Any]:
        now = utc_now()
        with self.transaction() as conn:
            row = conn.execute(
                "SELECT attempt_count FROM agent_runs WHERE id=? AND tenant_id=? AND status='running'",
                (run_id, tenant_id),
            ).fetchone()
            if row is None:
                raise ConflictError("agent run is not running")
            conn.execute(
                """UPDATE agent_runs SET status='completed',error=NULL,completed_at=?,updated_at=?
                   WHERE id=? AND tenant_id=?""",
                (now, now, run_id, tenant_id),
            )
            conn.execute(
                """INSERT INTO agent_artifacts(
                   id,tenant_id,run_id,task_id,kind,attempt,content_json,created_at
                   ) VALUES(?,?,?,?,?,?,?,?)""",
                (
                    self._id(), tenant_id, run_id, None, "weekly_ops_report",
                    row["attempt_count"], json.dumps(report, ensure_ascii=False, sort_keys=True), now,
                ),
            )
            conn.execute(
                """INSERT INTO agent_events(
                   id,tenant_id,run_id,task_id,event_type,payload_json,created_at
                   ) VALUES(?,?,?,?,?,?,?)""",
                (
                    self._id(), tenant_id, run_id, None, "run.completed",
                    json.dumps({"artifact_kind": "weekly_ops_report"}, sort_keys=True), now,
                ),
            )
        return self.get_agent_run_bundle(tenant_id, run_id)

    def fail_agent_run(self, tenant_id: str, run_id: str, error: str) -> None:
        now = utc_now()
        with self.transaction() as conn:
            cur = conn.execute(
                """UPDATE agent_runs SET status='failed',error=?,updated_at=?,completed_at=?
                   WHERE id=? AND tenant_id=? AND status='running'""",
                (error[:2000], now, now, run_id, tenant_id),
            )
            if cur.rowcount != 1:
                return
            conn.execute(
                """INSERT INTO agent_events(
                   id,tenant_id,run_id,task_id,event_type,payload_json,created_at
                   ) VALUES(?,?,?,?,?,?,?)""",
                (
                    self._id(), tenant_id, run_id, None, "run.failed",
                    json.dumps({"error_type": "AgentExecutionError"}, sort_keys=True), now,
                ),
            )

    def list_agent_artifacts(self, tenant_id: str, run_id: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM agent_artifacts WHERE tenant_id=? AND run_id=?
                   ORDER BY rowid""",
                (tenant_id, run_id),
            ).fetchall()
        artifacts = []
        for row in rows:
            artifact = dict(row)
            artifact["content"] = json.loads(artifact.pop("content_json"))
            artifacts.append(artifact)
        return artifacts

    def list_agent_events(self, tenant_id: str, run_id: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM agent_events WHERE tenant_id=? AND run_id=?
                   ORDER BY rowid""",
                (tenant_id, run_id),
            ).fetchall()
        events = []
        for row in rows:
            event = dict(row)
            event["payload"] = json.loads(event.pop("payload_json"))
            events.append(event)
        return events

    def list_agent_events_after(
        self,
        tenant_id: str,
        run_id: str,
        *,
        after: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Return an incremental, tenant-scoped event page for an operations UI."""
        self.get_agent_run(tenant_id, run_id)
        limit = max(1, min(limit, 500))
        try:
            marker = int(after) if after else 0
        except ValueError as exc:
            raise ValidationError("event cursor must be an integer") from exc
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT rowid AS sequence,* FROM agent_events
                   WHERE tenant_id=? AND run_id=? AND rowid>?
                   ORDER BY rowid LIMIT ?""",
                (tenant_id, run_id, marker, limit),
            ).fetchall()
        events = []
        for row in rows:
            event = dict(row)
            event["payload"] = json.loads(event.pop("payload_json"))
            events.append(event)
        next_cursor = str(events[-1]["sequence"]) if len(events) == limit else None
        return {"events": events, "next_cursor": next_cursor}

    def get_agent_run_bundle(self, tenant_id: str, run_id: str) -> dict[str, Any]:
        return {
            "run": self.get_agent_run(tenant_id, run_id),
            "tasks": self.list_agent_tasks(tenant_id, run_id),
            "artifacts": self.list_agent_artifacts(tenant_id, run_id),
            "events": self.list_agent_events(tenant_id, run_id),
            "evaluations": self.list_agent_evaluations(tenant_id, run_id),
        }

    def create_agent_evaluation(
        self,
        tenant_id: str,
        run_id: str,
        created_by: str,
        *,
        evaluator_version: str,
        passed: bool,
        score: float,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        evaluation_id = self._id()
        now = utc_now()
        with self.transaction() as conn:
            run = conn.execute(
                "SELECT tenant_id FROM agent_runs WHERE id=?", (run_id,)
            ).fetchone()
            user = conn.execute(
                "SELECT tenant_id FROM users WHERE id=?", (created_by,)
            ).fetchone()
            if run is None or run["tenant_id"] != tenant_id:
                raise NotFoundError("agent run not found")
            if user is None or user["tenant_id"] != tenant_id:
                raise ValidationError("evaluation creator does not belong to tenant")
            conn.execute(
                """INSERT INTO agent_evaluations(
                   id,tenant_id,run_id,evaluator_version,passed,score,
                   details_json,created_by,created_at
                   ) VALUES(?,?,?,?,?,?,?,?,?)""",
                (
                    evaluation_id,
                    tenant_id,
                    run_id,
                    evaluator_version,
                    1 if passed else 0,
                    score,
                    json.dumps(details, ensure_ascii=False, sort_keys=True),
                    created_by,
                    now,
                ),
            )
            row = conn.execute(
                "SELECT * FROM agent_evaluations WHERE id=?", (evaluation_id,)
            ).fetchone()
        return self._evaluation_dict(row)

    @staticmethod
    def _evaluation_dict(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["passed"] = bool(result["passed"])
        result["details"] = json.loads(result.pop("details_json"))
        return result

    def list_agent_evaluations(
        self, tenant_id: str, run_id: str
    ) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM agent_evaluations
                   WHERE tenant_id=? AND run_id=? ORDER BY rowid""",
                (tenant_id, run_id),
            ).fetchall()
        return [self._evaluation_dict(row) for row in rows]

    @staticmethod
    def _job_dict(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["payload"] = json.loads(result.pop("payload_json"))
        result_json = result.pop("result_json")
        if result_json is not None:
            result["result"] = json.loads(result_json)
        return result

    def create_job(
        self,
        tenant_id: str,
        created_by: str,
        idempotency_key: str,
        kind: str,
        payload: dict[str, Any],
        *,
        max_attempts: int = 3,
        available_at: str | None = None,
    ) -> tuple[dict[str, Any], bool]:
        if kind != "agent_run.execute":
            raise ValidationError("unsupported job kind")
        if not idempotency_key or len(idempotency_key) > 200:
            raise ValidationError("job idempotency_key is required and must be <= 200 characters")
        if not isinstance(payload, dict):
            raise ValidationError("job payload must be an object")
        if not 1 <= max_attempts <= 10:
            raise ValidationError("max_attempts must be between 1 and 10")
        job_id = self._id()
        now = utc_now()
        available_at = available_at or now
        try:
            with self.transaction() as conn:
                self.require_tenant(conn, tenant_id)
                user = conn.execute(
                    "SELECT tenant_id FROM users WHERE id=?", (created_by,)
                ).fetchone()
                if user is None or user["tenant_id"] != tenant_id:
                    raise ValidationError("job creator does not belong to tenant")
                conn.execute(
                    """INSERT INTO jobs(
                       id,tenant_id,idempotency_key,kind,payload_json,status,
                       available_at,max_attempts,created_by,created_at,updated_at
                       ) VALUES(?,?,?,?,?,'queued',?,?,?,?,?)""",
                    (
                        job_id,
                        tenant_id,
                        idempotency_key,
                        kind,
                        json.dumps(payload, ensure_ascii=False, sort_keys=True),
                        available_at,
                        max_attempts,
                        created_by,
                        now,
                        now,
                    ),
                )
        except sqlite3.IntegrityError:
            with self.connect() as conn:
                row = conn.execute(
                    "SELECT * FROM jobs WHERE tenant_id=? AND idempotency_key=?",
                    (tenant_id, idempotency_key),
                ).fetchone()
            if row is None:
                raise ConflictError("job idempotency conflict")
            existing = self._job_dict(row)
            if existing["kind"] != kind or existing["payload"] != payload:
                raise ConflictError("idempotency key was used with a different job")
            return existing, True
        return self.get_job(tenant_id, job_id), False

    def get_job(self, tenant_id: str, job_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM jobs WHERE id=? AND tenant_id=?", (job_id, tenant_id)
            ).fetchone()
        if row is None:
            raise NotFoundError("job not found")
        return self._job_dict(row)

    def list_jobs(self, tenant_id: str, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM jobs WHERE tenant_id=? ORDER BY rowid DESC LIMIT ?",
                (tenant_id, limit),
            ).fetchall()
        return [self._job_dict(row) for row in rows]

    def claim_job(self, *, lease_seconds: int = 300) -> dict[str, Any] | None:
        now = utc_now()
        lease_until = self._lease_until(lease_seconds)
        with self.transaction() as conn:
            row = conn.execute(
                """SELECT id FROM jobs WHERE
                   (status='queued' AND available_at<=?) OR
                   (status='running' AND lease_until IS NOT NULL AND lease_until<?)
                   ORDER BY rowid LIMIT 1""",
                (now, now),
            ).fetchone()
            if row is None:
                return None
            cur = conn.execute(
                """UPDATE jobs SET status='running',lease_until=?,
                   attempt_count=attempt_count+1,updated_at=?
                   WHERE id=? AND (
                     (status='queued' AND available_at<=?) OR
                     (status='running' AND lease_until IS NOT NULL AND lease_until<?)
                   )""",
                (lease_until, now, row["id"], now, now),
            )
            if cur.rowcount != 1:
                return None
            claimed = conn.execute("SELECT * FROM jobs WHERE id=?", (row["id"],)).fetchone()
        return self._job_dict(claimed)

    def complete_job(self, tenant_id: str, job_id: str, result: dict[str, Any]) -> dict[str, Any]:
        now = utc_now()
        with self.transaction() as conn:
            cur = conn.execute(
                """UPDATE jobs SET status='succeeded',result_json=?,error=NULL,
                   lease_until=NULL,completed_at=?,updated_at=?
                   WHERE id=? AND tenant_id=? AND status='running'""",
                (
                    json.dumps(result, ensure_ascii=False, sort_keys=True),
                    now,
                    now,
                    job_id,
                    tenant_id,
                ),
            )
            if cur.rowcount != 1:
                raise ConflictError("job is not running")
        return self.get_job(tenant_id, job_id)

    def fail_job(self, tenant_id: str, job_id: str, error: str) -> dict[str, Any]:
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat(timespec="seconds")
        with self.transaction() as conn:
            row = conn.execute(
                """SELECT attempt_count,max_attempts FROM jobs
                   WHERE id=? AND tenant_id=? AND status='running'""",
                (job_id, tenant_id),
            ).fetchone()
            if row is None:
                raise ConflictError("job is not running")
            terminal = row["attempt_count"] >= row["max_attempts"]
            if terminal:
                status = "failed"
                available_at = now
                completed_at = now
            else:
                status = "queued"
                delay = min(60 * (2 ** max(0, row["attempt_count"] - 1)), 3600)
                available_at = (now_dt + timedelta(seconds=delay)).isoformat(timespec="seconds")
                completed_at = None
            conn.execute(
                """UPDATE jobs SET status=?,available_at=?,lease_until=NULL,
                   error=?,completed_at=?,updated_at=? WHERE id=? AND tenant_id=?""",
                (
                    status,
                    available_at,
                    error[:2000],
                    completed_at,
                    now,
                    job_id,
                    tenant_id,
                ),
            )
        return self.get_job(tenant_id, job_id)

    @staticmethod
    def _schedule_dict(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["evidence_import_ids"] = json.loads(
            result.pop("evidence_import_ids_json")
        )
        result["evidence_selectors"] = json.loads(
            result.pop("evidence_selectors_json")
        )
        result["enabled"] = bool(result["enabled"])
        return result

    def create_schedule(
        self,
        tenant_id: str,
        created_by: str,
        *,
        name: str,
        objective: str,
        evidence_import_ids: list[str],
        evidence_selectors: list[dict[str, str]],
        interval_minutes: int,
        next_run_at: str,
    ) -> dict[str, Any]:
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
            raise ValidationError("schedule name must be between 1 and 100 characters")
        if not isinstance(objective, str) or not 5 <= len(objective.strip()) <= 1000:
            raise ValidationError("schedule objective must be between 5 and 1000 characters")
        if not isinstance(evidence_import_ids, list):
            raise ValidationError("schedule evidence_import_ids must be an array")
        if len(set(evidence_import_ids)) != len(evidence_import_ids):
            raise ValidationError("schedule evidence_import_ids must be unique")
        if not isinstance(evidence_selectors, list):
            raise ValidationError("schedule evidence_selectors must be an array")
        if not evidence_import_ids and not evidence_selectors:
            raise ValidationError("schedule requires evidence_import_ids or evidence_selectors")
        normalized_selectors = []
        for selector in evidence_selectors:
            if not isinstance(selector, dict) or set(selector) != {"platform", "report_type"}:
                raise ValidationError(
                    "each evidence selector requires platform and report_type"
                )
            if not all(isinstance(selector[key], str) and selector[key] for key in selector):
                raise ValidationError("evidence selector values must be non-empty strings")
            normalized_selectors.append(
                {"platform": selector["platform"], "report_type": selector["report_type"]}
            )
        if not 15 <= interval_minutes <= 43_200:
            raise ValidationError("interval_minutes must be between 15 and 43200")
        try:
            next_dt = datetime.fromisoformat(next_run_at.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise ValidationError("next_run_at must be ISO-8601") from exc
        if next_dt.tzinfo is None:
            raise ValidationError("next_run_at must include a timezone")
        schedule_id = self._id()
        now = utc_now()
        try:
            with self.transaction() as conn:
                self.require_tenant(conn, tenant_id)
                user = conn.execute(
                    "SELECT tenant_id FROM users WHERE id=?", (created_by,)
                ).fetchone()
                if user is None or user["tenant_id"] != tenant_id:
                    raise ValidationError("schedule creator does not belong to tenant")
                for import_id in evidence_import_ids:
                    evidence = conn.execute(
                        "SELECT tenant_id FROM evidence_imports WHERE id=?", (import_id,)
                    ).fetchone()
                    if evidence is None or evidence["tenant_id"] != tenant_id:
                        raise ValidationError("schedule evidence import does not belong to tenant")
                conn.execute(
                    """INSERT INTO schedules(
                       id,tenant_id,name,objective,evidence_import_ids_json,evidence_selectors_json,
                       interval_minutes,enabled,next_run_at,created_by,created_at,updated_at
                       ) VALUES(?,?,?,?,?,?,?,1,?,?,?,?)""",
                    (
                        schedule_id,
                        tenant_id,
                        name.strip(),
                        objective.strip(),
                        json.dumps(evidence_import_ids),
                        json.dumps(normalized_selectors, sort_keys=True),
                        interval_minutes,
                        next_run_at,
                        created_by,
                        now,
                        now,
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("schedule name already exists for tenant") from exc
        return self.get_schedule(tenant_id, schedule_id)

    def resolve_schedule_evidence(self, schedule: dict[str, Any]) -> list[str]:
        import_ids = list(schedule["evidence_import_ids"])
        with self.connect() as conn:
            for selector in schedule["evidence_selectors"]:
                row = conn.execute(
                    """SELECT id FROM evidence_imports
                       WHERE tenant_id=? AND platform=? AND report_type=?
                       ORDER BY rowid DESC LIMIT 1""",
                    (
                        schedule["tenant_id"],
                        selector["platform"],
                        selector["report_type"],
                    ),
                ).fetchone()
                if row is None:
                    raise ValidationError(
                        "schedule has no evidence for selector "
                        f"{selector['platform']}:{selector['report_type']}"
                    )
                import_ids.append(row["id"])
        return list(dict.fromkeys(import_ids))

    def get_schedule(self, tenant_id: str, schedule_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM schedules WHERE id=? AND tenant_id=?",
                (schedule_id, tenant_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("schedule not found")
        return self._schedule_dict(row)

    def list_schedules(self, tenant_id: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM schedules WHERE tenant_id=? ORDER BY rowid", (tenant_id,)
            ).fetchall()
        return [self._schedule_dict(row) for row in rows]

    def set_schedule_enabled(
        self, tenant_id: str, schedule_id: str, enabled: bool
    ) -> dict[str, Any]:
        with self.transaction() as conn:
            cur = conn.execute(
                """UPDATE schedules SET enabled=?,lease_until=NULL,updated_at=?
                   WHERE id=? AND tenant_id=?""",
                (1 if enabled else 0, utc_now(), schedule_id, tenant_id),
            )
            if cur.rowcount != 1:
                raise NotFoundError("schedule not found")
        return self.get_schedule(tenant_id, schedule_id)

    def claim_due_schedule(self, *, lease_seconds: int = 300) -> dict[str, Any] | None:
        now = utc_now()
        lease_until = self._lease_until(lease_seconds)
        with self.transaction() as conn:
            row = conn.execute(
                """SELECT id FROM schedules WHERE enabled=1 AND next_run_at<=?
                   AND (lease_until IS NULL OR lease_until<?)
                   ORDER BY next_run_at,rowid LIMIT 1""",
                (now, now),
            ).fetchone()
            if row is None:
                return None
            cur = conn.execute(
                """UPDATE schedules SET lease_until=?,updated_at=?
                   WHERE id=? AND enabled=1 AND next_run_at<=?
                   AND (lease_until IS NULL OR lease_until<?)""",
                (lease_until, now, row["id"], now, now),
            )
            if cur.rowcount != 1:
                return None
            claimed = conn.execute(
                "SELECT * FROM schedules WHERE id=?", (row["id"],)
            ).fetchone()
        return self._schedule_dict(claimed)

    def advance_schedule(self, tenant_id: str, schedule_id: str) -> dict[str, Any]:
        now_dt = datetime.now(timezone.utc)
        with self.transaction() as conn:
            row = conn.execute(
                """SELECT next_run_at,interval_minutes FROM schedules
                   WHERE id=? AND tenant_id=? AND lease_until IS NOT NULL""",
                (schedule_id, tenant_id),
            ).fetchone()
            if row is None:
                raise ConflictError("schedule is not claimed")
            previous = datetime.fromisoformat(row["next_run_at"].replace("Z", "+00:00"))
            base = max(previous, now_dt)
            next_run = (base + timedelta(minutes=row["interval_minutes"])).isoformat(
                timespec="seconds"
            )
            conn.execute(
                """UPDATE schedules SET next_run_at=?,last_run_at=?,lease_until=NULL,
                   updated_at=? WHERE id=? AND tenant_id=?""",
                (
                    next_run,
                    now_dt.isoformat(timespec="seconds"),
                    now_dt.isoformat(timespec="seconds"),
                    schedule_id,
                    tenant_id,
                ),
            )
        return self.get_schedule(tenant_id, schedule_id)

    def release_schedule(self, tenant_id: str, schedule_id: str) -> None:
        with self.transaction() as conn:
            conn.execute(
                "UPDATE schedules SET lease_until=NULL,updated_at=? WHERE id=? AND tenant_id=?",
                (utc_now(), schedule_id, tenant_id),
            )

    def mission_control(self, tenant_id: str) -> dict[str, Any]:
        def grouped(conn: sqlite3.Connection, table: str) -> dict[str, int]:
            rows = conn.execute(
                f"SELECT status,COUNT(*) AS count FROM {table} WHERE tenant_id=? GROUP BY status",
                (tenant_id,),
            ).fetchall()
            return {row["status"]: row["count"] for row in rows}

        with self.connect() as conn:
            self.require_tenant(conn, tenant_id)
            counts = {
                "evidence_imports": conn.execute(
                    "SELECT COUNT(*) FROM evidence_imports WHERE tenant_id=?", (tenant_id,)
                ).fetchone()[0],
                "enabled_schedules": conn.execute(
                    "SELECT COUNT(*) FROM schedules WHERE tenant_id=? AND enabled=1",
                    (tenant_id,),
                ).fetchone()[0],
                "failed_evaluations": conn.execute(
                    "SELECT COUNT(*) FROM agent_evaluations WHERE tenant_id=? AND passed=0",
                    (tenant_id,),
                ).fetchone()[0],
                "agent_runs": grouped(conn, "agent_runs"),
                "jobs": grouped(conn, "jobs"),
                "actions": grouped(conn, "actions"),
            }
        return {
            "counts": counts,
            "approval_inbox": self.list_actions(tenant_id, status="requested", limit=20),
            "failed_runs": [
                run for run in self.list_agent_runs(tenant_id, limit=50)
                if run["status"] == "failed"
            ][:20],
            "failed_jobs": [
                job for job in self.list_jobs(tenant_id, limit=50)
                if job["status"] == "failed"
            ][:20],
            "recent_runs": self.list_agent_runs(tenant_id, limit=10),
            "schedules": self.list_schedules(tenant_id),
        }
