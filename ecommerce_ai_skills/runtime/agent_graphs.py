"""Tenant-owned, immutable published domain-agent graph contracts."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from .auth import AuthService
from .errors import ConflictError, NotFoundError, ValidationError
from .storage import Database, Principal, utc_now


KNOWN_ROLES = {
    "evidence_analyst",
    "platform_specialist",
    "cross_controller",
    "manager",
    "reviewer",
}
KNOWN_EXPANSIONS = {"singleton", "each_input_marketplace", "multiple_marketplaces"}
STRICT_TOOL_POLICY = {"allowed_tools": [], "max_tool_calls": 0}
KNOWN_INSTRUCTION_KEYS = {
    "evidence_analyst": "weekly_ops.evidence_analyst.v1",
    "platform_specialist": "weekly_ops.platform_specialist.v1",
    "cross_controller": "weekly_ops.cross_controller.v1",
    "manager": "weekly_ops.manager.v1",
    "reviewer": "weekly_ops.reviewer.v1",
}


def default_graph_definition() -> dict[str, Any]:
    """Return the versioned L7 graph; callers receive a fresh object."""
    return {
        "schema_version": 1,
        "nodes": [
            {
                "key": "evidence_analyst",
                "role": "evidence_analyst",
                "expansion": "singleton",
                "optional": False,
                "skill_ids": ["ecom-applicability"],
                "instruction_key": KNOWN_INSTRUCTION_KEYS["evidence_analyst"],
                "tool_policy": dict(STRICT_TOOL_POLICY),
            },
            {
                "key": "platform_specialist",
                "role": "platform_specialist",
                "expansion": "each_input_marketplace",
                "optional": False,
                "skill_ids": [],
                "instruction_key": KNOWN_INSTRUCTION_KEYS["platform_specialist"],
                "tool_policy": dict(STRICT_TOOL_POLICY),
            },
            {
                "key": "cross_controller",
                "role": "cross_controller",
                "expansion": "multiple_marketplaces",
                "optional": True,
                "skill_ids": ["ecom-applicability", "ecom-listing"],
                "instruction_key": KNOWN_INSTRUCTION_KEYS["cross_controller"],
                "tool_policy": dict(STRICT_TOOL_POLICY),
            },
            {
                "key": "manager",
                "role": "manager",
                "expansion": "singleton",
                "optional": False,
                "skill_ids": [],
                "instruction_key": KNOWN_INSTRUCTION_KEYS["manager"],
                "tool_policy": dict(STRICT_TOOL_POLICY),
            },
            {
                "key": "reviewer",
                "role": "reviewer",
                "expansion": "singleton",
                "optional": False,
                "skill_ids": [],
                "instruction_key": KNOWN_INSTRUCTION_KEYS["reviewer"],
                "tool_policy": dict(STRICT_TOOL_POLICY),
            },
        ],
        "edges": [
            {"from": "evidence_analyst", "to": "cross_controller"},
            {"from": "platform_specialist", "to": "cross_controller"},
            {"from": "evidence_analyst", "to": "manager"},
            {"from": "platform_specialist", "to": "manager"},
            {"from": "cross_controller", "to": "manager"},
            {"from": "manager", "to": "reviewer"},
        ],
    }


class AgentGraphService:
    DEFAULT_NAME = "Weekly Ops Domain Graph"
    MAX_DEFINITION_BYTES = 100_000

    def __init__(self, db: Database, auth: AuthService):
        self.db = db
        self.auth = auth

    @staticmethod
    def _installed_skills() -> set[str]:
        root = Path(__file__).resolve().parents[1] / "package_data" / "dist" / "skills"
        return {path.parent.name for path in root.glob("*/manifest.yaml")}

    @classmethod
    def execution_contract_hash(cls) -> str:
        """Fingerprint every installed input that can change graph execution."""
        package_root = Path(__file__).resolve().parents[1]
        dist_root = package_root / "package_data" / "dist"
        paths = [
            Path(__file__).resolve(),
            Path(__file__).resolve().with_name("agents.py"),
            dist_root / "ontology.json",
            *sorted((dist_root / "skills").glob("*/manifest.yaml")),
        ]
        digest = hashlib.sha256()
        for path in paths:
            if not path.is_file():
                raise ValidationError(
                    f"agent execution contract input is missing: {path.name}"
                )
            try:
                label = path.relative_to(package_root).as_posix()
            except ValueError:  # pragma: no cover - production paths share package_root
                label = path.name
            digest.update(label.encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        return digest.hexdigest()

    @classmethod
    def validate_definition(
        cls, definition: Any
    ) -> tuple[dict[str, Any], str, str]:
        if not isinstance(definition, dict) or set(definition) != {
            "schema_version", "nodes", "edges"
        }:
            raise ValidationError(
                "graph definition fields must be schema_version, nodes, and edges"
            )
        if definition["schema_version"] != 1:
            raise ValidationError("graph schema_version must be 1")
        nodes = definition["nodes"]
        edges = definition["edges"]
        if not isinstance(nodes, list) or not 4 <= len(nodes) <= 20:
            raise ValidationError("graph nodes must contain between 4 and 20 nodes")
        if not isinstance(edges, list) or not 3 <= len(edges) <= 100:
            raise ValidationError("graph edges must contain between 3 and 100 edges")
        installed_skills = cls._installed_skills()
        normalized_nodes: list[dict[str, Any]] = []
        keys: set[str] = set()
        roles: list[str] = []
        for node in nodes:
            required = {
                "key", "role", "expansion", "optional", "skill_ids", "instruction_key", "tool_policy"
            }
            if not isinstance(node, dict) or set(node) != required:
                raise ValidationError("each graph node must use the complete known node schema")
            key = node["key"]
            role = node["role"]
            if not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z0-9_]{1,63}", key):
                raise ValidationError("graph node key must be a lowercase safe identifier")
            if key in keys:
                raise ValidationError(f"duplicate graph node key: {key}")
            keys.add(key)
            if role not in KNOWN_ROLES:
                raise ValidationError(f"unknown graph role: {role}")
            if key != role:
                raise ValidationError(f"role {role} must use known node key {role}")
            roles.append(role)
            expansion = node["expansion"]
            if expansion not in KNOWN_EXPANSIONS:
                raise ValidationError(f"unknown graph node expansion: {expansion}")
            expected_expansion = {
                "platform_specialist": "each_input_marketplace",
                "cross_controller": "multiple_marketplaces",
            }.get(role, "singleton")
            if expansion != expected_expansion:
                raise ValidationError(f"role {role} requires expansion {expected_expansion}")
            if not isinstance(node["optional"], bool) or node["optional"] != (
                role == "cross_controller"
            ):
                raise ValidationError(
                    "cross_controller must be optional and every other role must be required"
                )
            skill_ids = node["skill_ids"]
            if not isinstance(skill_ids, list) or len(skill_ids) > 30 or not all(
                isinstance(item, str) and item in installed_skills for item in skill_ids
            ):
                raise ValidationError("graph node skill_ids must name installed skills")
            if len(skill_ids) != len(set(skill_ids)):
                raise ValidationError("graph node skill_ids must be unique")
            if role in {"platform_specialist", "manager", "reviewer"} and skill_ids:
                raise ValidationError(
                    f"role {role} uses runtime-resolved or no skills and must declare an empty skill_ids"
                )
            if node["instruction_key"] != KNOWN_INSTRUCTION_KEYS[role]:
                raise ValidationError(f"role {role} must use its known instruction_key")
            if node["tool_policy"] != STRICT_TOOL_POLICY:
                raise ValidationError("L7 graph tool_policy must disable all tool calls")
            normalized_nodes.append(
                {
                    **node,
                    "skill_ids": sorted(skill_ids),
                    "tool_policy": dict(STRICT_TOOL_POLICY),
                }
            )
        required_roles = set(KNOWN_ROLES)
        if not required_roles <= set(roles):
            raise ValidationError("graph is missing a required domain role")
        for unique_role in required_roles:
            count = roles.count(unique_role)
            if count != 1:
                raise ValidationError(f"graph must contain exactly one {unique_role} role")

        normalized_edges: list[dict[str, str]] = []
        edge_pairs: set[tuple[str, str]] = set()
        outgoing = {key: set() for key in keys}
        incoming = {key: set() for key in keys}
        for edge in edges:
            if not isinstance(edge, dict) or set(edge) != {"from", "to"}:
                raise ValidationError("each graph edge must contain from and to")
            source, target = edge["from"], edge["to"]
            if source not in keys or target not in keys or source == target:
                raise ValidationError("graph edge references an unknown or identical node")
            pair = (source, target)
            if pair in edge_pairs:
                raise ValidationError("graph edges must be unique")
            edge_pairs.add(pair)
            outgoing[source].add(target)
            incoming[target].add(source)
            normalized_edges.append({"from": source, "to": target})

        by_role = {node["role"]: node["key"] for node in normalized_nodes}
        manager_key, reviewer_key = by_role["manager"], by_role["reviewer"]
        evidence_key = by_role["evidence_analyst"]
        platform_key = by_role["platform_specialist"]
        expected_edges = {
            (evidence_key, manager_key),
            (platform_key, manager_key),
            (manager_key, reviewer_key),
        }
        cross_key = by_role["cross_controller"]
        expected_edges |= {
            (evidence_key, cross_key),
            (platform_key, cross_key),
            (cross_key, manager_key),
        }
        if edge_pairs != expected_edges:
            raise ValidationError(
                "graph edges must match the supported Weekly Ops execution topology"
            )
        if (manager_key, reviewer_key) not in edge_pairs:
            raise ValidationError("graph must contain a direct manager to reviewer edge")
        terminals = {key for key, targets in outgoing.items() if not targets}
        if terminals != {reviewer_key}:
            raise ValidationError("every graph terminal path must end at reviewer")
        # Kahn's algorithm verifies acyclicity and also proves every node is in
        # the traversable DAG rather than an opaque recursive component.
        degrees = {key: len(incoming[key]) for key in keys}
        queue = sorted(key for key, degree in degrees.items() if degree == 0)
        visited: list[str] = []
        while queue:
            key = queue.pop(0)
            visited.append(key)
            for target in sorted(outgoing[key]):
                degrees[target] -= 1
                if degrees[target] == 0:
                    queue.append(target)
        if len(visited) != len(keys):
            raise ValidationError("graph must be acyclic")
        normalized = {
            "schema_version": 1,
            "nodes": sorted(normalized_nodes, key=lambda item: item["key"]),
            "edges": sorted(normalized_edges, key=lambda item: (item["from"], item["to"])),
        }
        raw = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if len(raw.encode("utf-8")) > cls.MAX_DEFINITION_BYTES:
            raise ValidationError("graph definition exceeds 100 KB")
        execution_contract_hash = cls.execution_contract_hash()
        definition_hash = hashlib.sha256(
            raw.encode("utf-8") + b"\0" + execution_contract_hash.encode("ascii")
        ).hexdigest()
        return normalized, definition_hash, execution_contract_hash

    @staticmethod
    def _graph(row: sqlite3.Row) -> dict[str, Any]:
        return dict(row)

    @staticmethod
    def _version(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["definition"] = json.loads(result.pop("definition_json"))
        return result

    def ensure_default(self, principal: Principal) -> dict[str, Any]:
        """Idempotently ensure this tenant has one published default graph."""
        self.auth.require(principal, "operator")
        with self.db.connect() as conn:
            row = conn.execute(
                """SELECT v.* FROM agent_graph_versions v
                   JOIN agent_graphs g ON g.id=v.graph_id AND g.tenant_id=v.tenant_id
                   WHERE v.tenant_id=? AND g.name=? AND v.status='published'
                   ORDER BY v.version DESC LIMIT 1""",
                (principal.tenant_id, self.DEFAULT_NAME),
            ).fetchone()
        if row is not None:
            if row["execution_contract_hash"] != self.execution_contract_hash():
                raise ConflictError(
                    "default graph execution contract changed; an admin must publish a new version"
                )
            return self._version(row)
        definition, definition_hash, execution_contract_hash = self.validate_definition(
            default_graph_definition()
        )
        now = utc_now()
        ensured_version_id: str | None = None
        with self.db.transaction() as conn:
            graph = conn.execute(
                "SELECT * FROM agent_graphs WHERE tenant_id=? AND name=?",
                (principal.tenant_id, self.DEFAULT_NAME),
            ).fetchone()
            if graph is None:
                graph_id = self.db._id()
                conn.execute(
                    """INSERT INTO agent_graphs(
                       id,tenant_id,name,created_by,created_at,updated_at
                       ) VALUES(?,?,?,?,?,?)""",
                    (
                        graph_id, principal.tenant_id, self.DEFAULT_NAME,
                        principal.user_id, now, now,
                    ),
                )
            else:
                graph_id = str(graph["id"])
            existing = conn.execute(
                """SELECT * FROM agent_graph_versions
                   WHERE tenant_id=? AND graph_id=? AND definition_hash=?""",
                (principal.tenant_id, graph_id, definition_hash),
            ).fetchone()
            if existing is None:
                version_id = self.db._id()
                version_number = int(
                    conn.execute(
                        "SELECT COALESCE(MAX(version),0)+1 n FROM agent_graph_versions WHERE tenant_id=? AND graph_id=?",
                        (principal.tenant_id, graph_id),
                    ).fetchone()["n"]
                )
                conn.execute(
                    """INSERT INTO agent_graph_versions(
                       id,tenant_id,graph_id,version,definition_json,definition_hash,
                       execution_contract_hash,status,created_by,created_at,published_at
                       ) VALUES(?,?,?,?,?,?,?,'published',?,?,?)""",
                    (
                        version_id, principal.tenant_id, graph_id, version_number,
                        json.dumps(definition, ensure_ascii=False, sort_keys=True),
                        definition_hash, execution_contract_hash,
                        principal.user_id, now, now,
                    ),
                )
                ensured_version_id = version_id
            elif existing["status"] != "published":
                conn.execute(
                    "UPDATE agent_graph_versions SET status='published',published_at=? WHERE tenant_id=? AND id=?",
                    (now, principal.tenant_id, existing["id"]),
                )
                ensured_version_id = str(existing["id"])
        if ensured_version_id is not None:
            self.db.append_audit(
                principal.tenant_id,
                principal.user_id,
                f"agent-graph-default:{ensured_version_id}",
                "agent_graph.default.ensure",
                "agent_graph_version",
                ensured_version_id,
                "succeeded",
                {"graph_id": graph_id, "definition_hash": definition_hash},
            )
        return self.get_published(principal, graph_id)

    def create(
        self, principal: Principal, name: Any, definition: Any, request_id: str
    ) -> dict[str, Any]:
        self.auth.require(principal, "admin")
        if not isinstance(name, str) or not 3 <= len(name.strip()) <= 120:
            raise ValidationError("graph name must contain 3-120 characters")
        normalized, definition_hash, execution_contract_hash = self.validate_definition(
            definition
        )
        graph_id, version_id, now = self.db._id(), self.db._id(), utc_now()
        try:
            with self.db.transaction() as conn:
                conn.execute(
                    "INSERT INTO agent_graphs(id,tenant_id,name,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                    (graph_id, principal.tenant_id, name.strip(), principal.user_id, now, now),
                )
                conn.execute(
                    """INSERT INTO agent_graph_versions(
                       id,tenant_id,graph_id,version,definition_json,definition_hash,
                       execution_contract_hash,status,created_by,created_at
                       ) VALUES(?,?,?,?,?,?,?,'draft',?,?)""",
                    (
                        version_id, principal.tenant_id, graph_id, 1,
                        json.dumps(normalized, ensure_ascii=False, sort_keys=True),
                        definition_hash, execution_contract_hash, principal.user_id, now,
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("graph name or definition already exists for this tenant") from exc
        self.db.append_audit(
            principal.tenant_id, principal.user_id, request_id,
            "agent_graph.create", "agent_graph", graph_id, "succeeded",
            {"version_id": version_id, "definition_hash": definition_hash},
        )
        return self.get(principal, graph_id)

    def create_version(
        self, principal: Principal, graph_id: str, definition: Any, request_id: str
    ) -> dict[str, Any]:
        self.auth.require(principal, "admin")
        normalized, definition_hash, execution_contract_hash = self.validate_definition(
            definition
        )
        version_id, now = self.db._id(), utc_now()
        try:
            with self.db.transaction() as conn:
                graph = conn.execute(
                    "SELECT id FROM agent_graphs WHERE tenant_id=? AND id=?",
                    (principal.tenant_id, graph_id),
                ).fetchone()
                if graph is None:
                    raise NotFoundError("agent graph not found")
                version = int(
                    conn.execute(
                        "SELECT COALESCE(MAX(version),0)+1 n FROM agent_graph_versions WHERE tenant_id=? AND graph_id=?",
                        (principal.tenant_id, graph_id),
                    ).fetchone()["n"]
                )
                conn.execute(
                    """INSERT INTO agent_graph_versions(
                       id,tenant_id,graph_id,version,definition_json,definition_hash,
                       execution_contract_hash,status,created_by,created_at
                       ) VALUES(?,?,?,?,?,?,?,'draft',?,?)""",
                    (
                        version_id, principal.tenant_id, graph_id, version,
                        json.dumps(normalized, ensure_ascii=False, sort_keys=True),
                        definition_hash, execution_contract_hash, principal.user_id, now,
                    ),
                )
                conn.execute(
                    "UPDATE agent_graphs SET updated_at=? WHERE tenant_id=? AND id=?",
                    (now, principal.tenant_id, graph_id),
                )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("this graph definition already exists for the tenant") from exc
        self.db.append_audit(
            principal.tenant_id, principal.user_id, request_id,
            "agent_graph.version.create", "agent_graph_version", version_id, "succeeded",
            {"graph_id": graph_id, "definition_hash": definition_hash},
        )
        return self.get_version(principal, version_id)

    def publish(
        self, principal: Principal, graph_id: str, version_id: str, request_id: str
    ) -> dict[str, Any]:
        self.auth.require(principal, "admin")
        now = utc_now()
        with self.db.transaction() as conn:
            row = conn.execute(
                """SELECT * FROM agent_graph_versions
                   WHERE tenant_id=? AND graph_id=? AND id=?""",
                (principal.tenant_id, graph_id, version_id),
            ).fetchone()
            if row is None:
                raise NotFoundError("agent graph version not found")
            if row["status"] == "retired":
                raise ConflictError("retired graph versions cannot be republished")
            if row["status"] != "published":
                conn.execute(
                    """UPDATE agent_graph_versions
                       SET status='retired',retired_at=?
                       WHERE tenant_id=? AND graph_id=? AND status='published'""",
                    (now, principal.tenant_id, graph_id),
                )
                conn.execute(
                    """UPDATE agent_graph_versions
                       SET status='published',published_at=?
                       WHERE tenant_id=? AND graph_id=? AND id=? AND status='draft'""",
                    (now, principal.tenant_id, graph_id, version_id),
                )
        self.db.append_audit(
            principal.tenant_id, principal.user_id, request_id,
            "agent_graph.version.publish", "agent_graph_version", version_id, "succeeded",
            {"graph_id": graph_id},
        )
        return self.get_version(principal, version_id)

    def list(self, principal: Principal) -> list[dict[str, Any]]:
        self.auth.require(principal, "viewer")
        with self.db.connect() as conn:
            rows = conn.execute(
                """SELECT g.*,
                          (SELECT id FROM agent_graph_versions v
                           WHERE v.tenant_id=g.tenant_id AND v.graph_id=g.id
                             AND v.status='published' LIMIT 1) published_version_id
                   FROM agent_graphs g WHERE g.tenant_id=? ORDER BY g.created_at,g.id""",
                (principal.tenant_id,),
            ).fetchall()
        return [self._graph(row) for row in rows]

    def get(self, principal: Principal, graph_id: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        with self.db.connect() as conn:
            graph = conn.execute(
                "SELECT * FROM agent_graphs WHERE tenant_id=? AND id=?",
                (principal.tenant_id, graph_id),
            ).fetchone()
            versions = conn.execute(
                """SELECT * FROM agent_graph_versions
                   WHERE tenant_id=? AND graph_id=? ORDER BY version DESC""",
                (principal.tenant_id, graph_id),
            ).fetchall()
        if graph is None:
            raise NotFoundError("agent graph not found")
        return {"graph": self._graph(graph), "versions": [self._version(row) for row in versions]}

    def get_version(self, principal: Principal, version_id: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM agent_graph_versions WHERE tenant_id=? AND id=?",
                (principal.tenant_id, version_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("agent graph version not found")
        return self._version(row)

    def get_published(self, principal: Principal, graph_id: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        with self.db.connect() as conn:
            row = conn.execute(
                """SELECT * FROM agent_graph_versions
                   WHERE tenant_id=? AND graph_id=? AND status='published'""",
                (principal.tenant_id, graph_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("published agent graph version not found")
        return self._version(row)

    def resolve_published(
        self, principal: Principal, version_id: Any = None
    ) -> dict[str, Any]:
        if version_id is None:
            return self.ensure_default(principal)
        if not isinstance(version_id, str) or not re.fullmatch(r"[0-9a-f-]{36}", version_id):
            raise ValidationError("graph_version_id must be a UUID")
        version = self.get_version(principal, version_id)
        if version["status"] != "published":
            raise ConflictError("agent runs require a published graph version")
        if version["execution_contract_hash"] != self.execution_contract_hash():
            raise ConflictError(
                "agent graph execution contract changed; an admin must publish a new version"
            )
        return version
