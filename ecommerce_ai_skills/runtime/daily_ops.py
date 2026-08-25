"""Tenant-safe, date-bound daily operations scheduling and execution."""

from __future__ import annotations

import json
import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .agents import WeeklyOpsCouncil
from .auth import AuthService
from .evidence import REPORT_SPECS
from .errors import ConflictError, ValidationError
from .storage import ROLE_LEVEL, Database, Principal, utc_now


_SAFE_IDENTIFIER = re.compile(r"[a-z0-9._-]{1,80}")
_LOCAL_TIME = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d")


@dataclass
class DailyOpsService:
    db: Database
    auth: AuthService
    agent_runs: WeeklyOpsCouncil

    @staticmethod
    def _timezone(value: Any) -> ZoneInfo:
        if not isinstance(value, str) or not 1 <= len(value) <= 100:
            raise ValidationError("timezone must be an IANA timezone name")
        try:
            return ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValidationError("timezone must be a recognized IANA timezone name") from exc

    @staticmethod
    def _time(value: Any) -> str:
        if not isinstance(value, str) or not _LOCAL_TIME.fullmatch(value):
            raise ValidationError("local_time must use 24-hour HH:MM format")
        return value

    @staticmethod
    def _date(value: Any) -> date:
        if not isinstance(value, str):
            raise ValidationError("local_date must use YYYY-MM-DD format")
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise ValidationError("local_date must use YYYY-MM-DD format") from exc
        if parsed.isoformat() != value:
            raise ValidationError("local_date must use YYYY-MM-DD format")
        return parsed

    @classmethod
    def _selectors(cls, value: Any) -> list[dict[str, str]]:
        if not isinstance(value, list) or not 1 <= len(value) <= 20:
            raise ValidationError("evidence_selectors must contain between 1 and 20 selectors")
        normalized: list[dict[str, str]] = []
        seen: set[str] = set()
        for selector in value:
            if not isinstance(selector, dict) or set(selector) != {"report_type"}:
                raise ValidationError("each evidence selector must contain only report_type")
            report_type = selector.get("report_type")
            if not isinstance(report_type, str) or not _SAFE_IDENTIFIER.fullmatch(report_type):
                raise ValidationError("selector report_type must be a lowercase identifier")
            if report_type not in REPORT_SPECS:
                raise ValidationError("selector report_type is not an installed evidence report type")
            if report_type in seen:
                raise ValidationError("evidence selectors must be unique")
            seen.add(report_type)
            normalized.append({"report_type": report_type})
        return normalized

    def _published_graph(self, principal: Principal, graph_version_id: Any) -> dict[str, Any]:
        if not isinstance(graph_version_id, str) or not graph_version_id:
            raise ValidationError("graph_version_id is required")
        return self.agent_runs.graph_service.resolve_published(principal, graph_version_id)

    def _validated_schedule_values(
        self,
        principal: Principal,
        *,
        name: Any,
        platform: Any,
        objective: Any,
        timezone_name: Any,
        local_time: Any,
        graph_version_id: Any,
        evidence_selectors: Any,
        max_source_age_hours: Any,
        enabled: Any,
        require_published_graph: bool = True,
    ) -> dict[str, Any]:
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 120:
            raise ValidationError("name must be between 1 and 120 characters")
        if (
            not isinstance(platform, str)
            or platform == "cross_platform"
            or platform not in self.agent_runs.platform_registry.ids()
        ):
            raise ValidationError("platform must be an installed marketplace platform")
        if not isinstance(objective, str) or not 5 <= len(objective.strip()) <= 1000:
            raise ValidationError("objective must be between 5 and 1000 characters")
        self._timezone(timezone_name)
        self._time(local_time)
        version = (
            self._published_graph(principal, graph_version_id)
            if require_published_graph
            else self.agent_runs.graph_service.get_version(principal, graph_version_id)
        )
        selectors = self._selectors(evidence_selectors)
        if platform != "amazon" and any(
            selector["report_type"].startswith("amazon_") for selector in selectors
        ):
            raise ValidationError(
                "Amazon report types cannot be selected for another marketplace"
            )
        if any(
            REPORT_SPECS[selector["report_type"]].platform not in {None, platform}
            for selector in selectors
        ):
            raise ValidationError("evidence selector report type does not match schedule platform")
        if (
            not isinstance(max_source_age_hours, int)
            or isinstance(max_source_age_hours, bool)
            or not 1 <= max_source_age_hours <= 8760
        ):
            raise ValidationError("max_source_age_hours must be between 1 and 8760")
        if not isinstance(enabled, bool):
            raise ValidationError("enabled must be a boolean")
        return {
            "name": name.strip(),
            "platform": platform,
            "objective": objective.strip(),
            "timezone_name": timezone_name,
            "local_time": local_time,
            "graph_version_id": version["id"],
            "evidence_selectors": selectors,
            "max_source_age_hours": max_source_age_hours,
            "enabled": enabled,
        }

    @staticmethod
    def _config_hash(config: dict[str, Any]) -> str:
        raw = json.dumps(
            config, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @classmethod
    def _schedule_config(
        cls,
        schedule: dict[str, Any],
        graph: dict[str, Any],
        *,
        local_date: str,
        scheduled_for: str,
    ) -> tuple[dict[str, Any], str]:
        config = {
            "schema_version": 1,
            "tenant_id": schedule["tenant_id"],
            "schedule_id": schedule["id"],
            "name": schedule["name"],
            "platform": schedule["platform"],
            "objective": schedule["objective"],
            "timezone": schedule["timezone"],
            "local_time": schedule["local_time"],
            "local_date": local_date,
            "scheduled_for": scheduled_for,
            "graph_version_id": graph["id"],
            "graph_version_hash": graph["definition_hash"],
            "evidence_selectors": schedule["evidence_selectors"],
            "max_source_age_hours": schedule["max_source_age_hours"],
        }
        return config, cls._config_hash(config)

    @classmethod
    def _verified_run_config(cls, run: dict[str, Any]) -> dict[str, Any]:
        config = run.get("schedule_config")
        if (
            not isinstance(config, dict)
            or cls._config_hash(config) != run.get("schedule_config_hash")
            or config.get("tenant_id") != run.get("tenant_id")
            or config.get("schedule_id") != run.get("schedule_id")
            or config.get("local_date") != run.get("local_date")
            or config.get("timezone") != run.get("timezone")
            or config.get("scheduled_for") != run.get("scheduled_for")
            or config.get("graph_version_id") != run.get("graph_version_id")
            or config.get("graph_version_hash") != run.get("graph_version_hash")
        ):
            raise ConflictError("daily ops schedule snapshot is invalid")
        return config

    def create(
        self,
        principal: Principal,
        *,
        name: Any,
        platform: Any,
        objective: Any,
        timezone_name: Any,
        local_time: Any,
        graph_version_id: Any,
        evidence_selectors: Any,
        max_source_age_hours: Any = 48,
        enabled: Any = True,
        request_id: str,
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        values = self._validated_schedule_values(
            principal,
            name=name,
            platform=platform,
            objective=objective,
            timezone_name=timezone_name,
            local_time=local_time,
            graph_version_id=graph_version_id,
            evidence_selectors=evidence_selectors,
            max_source_age_hours=max_source_age_hours,
            enabled=enabled,
        )
        next_local_date = datetime.now(
            self._timezone(values["timezone_name"])
        ).date().isoformat()
        schedule = self.db.create_daily_ops_schedule(
            principal.tenant_id,
            principal.user_id,
            **values,
            next_local_date=next_local_date,
        )
        self.db.append_audit(
            principal.tenant_id, principal.user_id, request_id,
            "daily_ops.schedule.create", "daily_ops_schedule", schedule["id"], "succeeded",
            {"platform": schedule["platform"], "graph_version_id": schedule["graph_version_id"]},
        )
        return schedule

    def update(
        self, principal: Principal, schedule_id: str, *, request_id: str, **changes: Any
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        current = self.db.get_daily_ops_schedule(principal.tenant_id, schedule_id)
        aliases = {
            "timezone_name": "timezone",
            "evidence_selectors": "evidence_selectors_json",
        }
        unknown = set(changes) - {
            "name", "platform", "objective", "timezone_name", "local_time",
            "graph_version_id", "evidence_selectors", "max_source_age_hours", "enabled",
        }
        if unknown or not changes:
            raise ValidationError("daily ops schedule update contains unsupported fields")
        merged = {
            "name": current["name"], "platform": current["platform"],
            "objective": current["objective"], "timezone_name": current["timezone"],
            "local_time": current["local_time"], "graph_version_id": current["graph_version_id"],
            "evidence_selectors": current["evidence_selectors"],
            "max_source_age_hours": current["max_source_age_hours"], "enabled": current["enabled"],
        }
        merged.update(changes)
        values = self._validated_schedule_values(
            principal,
            **merged,
            require_published_graph=bool(merged["enabled"]),
        )
        if not current["enabled"] and values["enabled"]:
            execution_user = self.db.get_user(
                principal.tenant_id, current["created_by"]
            )
            if ROLE_LEVEL.get(execution_user["role"], 0) < ROLE_LEVEL["operator"]:
                raise ConflictError(
                    "Daily Ops schedule creator must be operator before re-enabling"
                )
        stored = {
            aliases.get(key, key): (
                json.dumps(value, ensure_ascii=False, sort_keys=True)
                if key == "evidence_selectors" else int(value) if key == "enabled" else value
            )
            for key, value in values.items()
            if key in changes or (key == "timezone_name" and "timezone_name" in changes)
        }
        if (
            "timezone_name" in changes
            or (not current["enabled"] and values["enabled"])
        ):
            stored["next_local_date"] = datetime.now(
                self._timezone(values["timezone_name"])
            ).date().isoformat()
        schedule = self.db.update_daily_ops_schedule(principal.tenant_id, schedule_id, stored)
        self.db.append_audit(
            principal.tenant_id, principal.user_id, request_id,
            "daily_ops.schedule.update", "daily_ops_schedule", schedule_id, "succeeded",
            {"fields": sorted(changes)},
        )
        return schedule

    def list_schedules(self, principal: Principal) -> list[dict[str, Any]]:
        self.auth.require(principal, "viewer")
        return self.db.list_daily_ops_schedules(principal.tenant_id)

    def get_schedule(self, principal: Principal, schedule_id: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        return self.db.get_daily_ops_schedule(principal.tenant_id, schedule_id)

    def list_runs(
        self, principal: Principal, schedule_id: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        self.auth.require(principal, "viewer")
        if schedule_id is not None:
            self.db.get_daily_ops_schedule(principal.tenant_id, schedule_id)
        return self.db.list_daily_ops_runs(
            principal.tenant_id, schedule_id=schedule_id, limit=limit
        )

    def get_run(self, principal: Principal, run_id: str) -> dict[str, Any]:
        self.auth.require(principal, "viewer")
        return self.db.get_daily_ops_run(principal.tenant_id, run_id)

    def get_brief(self, principal: Principal, run_id: str) -> dict[str, Any]:
        run = self.get_run(principal, run_id)
        if run["brief"] is None:
            raise ConflictError("daily ops brief is not available for this run")
        return {"run": run, "brief": run["brief"]}

    @classmethod
    def _scheduled_for(
        cls, local_date: date, timezone_name: str, local_time: str
    ) -> tuple[datetime, bool]:
        zone = cls._timezone(timezone_name)
        hour, minute = (int(part) for part in local_time.split(":"))
        naive = datetime.combine(local_date, time(hour, minute))
        # PEP 495 fold=0 is the explicitly selected first occurrence on fall-back days.
        candidate = naive.replace(tzinfo=zone, fold=0)
        round_trip = candidate.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None)
        return candidate, round_trip != naive

    @staticmethod
    def _parse_instant(value: str) -> datetime:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValidationError("stored evidence observed_at must include a timezone")
        return parsed.astimezone(timezone.utc)

    def _resolve_sources(
        self,
        schedule: dict[str, Any],
        cutoff: datetime,
    ) -> tuple[list[str], list[str], list[dict[str, Any]]]:
        if cutoff.tzinfo is None:
            raise ValidationError("daily ops evidence cutoff must include a timezone")
        cutoff_utc = cutoff.astimezone(timezone.utc)
        oldest = cutoff_utc - timedelta(hours=schedule["max_source_age_hours"])
        chosen: list[dict[str, Any]] = []
        gaps: list[dict[str, Any]] = []
        for selector in schedule["evidence_selectors"]:
            with self.db.connect() as conn:
                row = conn.execute(
                    """SELECT * FROM evidence_imports
                       WHERE tenant_id=? AND platform=? AND report_type=?
                         AND julianday(observed_at)>=julianday(?)
                         AND julianday(observed_at)<=julianday(?)
                       ORDER BY julianday(observed_at) DESC,rowid DESC LIMIT 1""",
                    (
                        schedule["tenant_id"], schedule["platform"], selector["report_type"],
                        oldest.isoformat(timespec="seconds"), cutoff_utc.isoformat(timespec="seconds"),
                    ),
                ).fetchone()
            if row is None:
                gaps.append(
                    {
                        "code": "SOURCE_NOT_FOUND",
                        "platform": schedule["platform"],
                        "report_type": selector["report_type"],
                        "as_of": cutoff_utc.isoformat(timespec="seconds"),
                        "max_source_age_hours": schedule["max_source_age_hours"],
                    }
                )
                continue
            chosen.append(row)

        chosen_ids = list(dict.fromkeys(str(row["id"]) for row in chosen))
        metric_ids: list[str] = []
        raw_ids: list[str] = []
        with self.db.connect() as conn:
            for import_id in chosen_ids:
                materialization = conn.execute(
                    """SELECT id FROM metric_materializations
                       WHERE tenant_id=? AND evidence_import_id=?
                         AND status IN ('succeeded','partial')
                       ORDER BY completed_at DESC,rowid DESC LIMIT 1""",
                    (schedule["tenant_id"], import_id),
                ).fetchone()
                if materialization is None:
                    raw_ids.append(import_id)
                    continue
                observations = conn.execute(
                    """SELECT id FROM metric_observations
                       WHERE tenant_id=? AND materialization_id=? ORDER BY rowid""",
                    (schedule["tenant_id"], materialization["id"]),
                ).fetchall()
                if observations:
                    metric_ids.extend(str(row["id"]) for row in observations)
                else:
                    raw_ids.append(import_id)
        if len(raw_ids) + len(metric_ids) > 20:
            raise ValidationError("daily ops source selection exceeds the 20-input agent limit")
        return raw_ids, metric_ids, gaps

    @staticmethod
    def _empty_brief(
        schedule: dict[str, Any], local_date: str, scheduled_for: str,
        gaps: list[dict[str, Any]], graph_hash: str
    ) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "kind": "daily_ops_brief",
            "status": "empty",
            "local_date": local_date,
            "timezone": schedule["timezone"],
            "scheduled_for": scheduled_for,
            "generated_at": utc_now(),
            "schedule": {
                "id": schedule.get("id") or schedule["schedule_id"],
                "name": schedule["name"],
                "platform": schedule["platform"],
            },
            "graph": {"version_id": schedule["graph_version_id"], "definition_hash": graph_hash},
            "source_gaps": gaps,
            "report": None,
        }

    def trigger(
        self, principal: Principal, schedule_id: str, request_id: str,
        local_date: str | None = None
    ) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        schedule = self.db.get_daily_ops_schedule(principal.tenant_id, schedule_id)
        zone = self._timezone(schedule["timezone"])
        run_date = self._date(local_date) if local_date is not None else datetime.now(zone).date()
        scheduled, nonexistent = self._scheduled_for(
            run_date, schedule["timezone"], schedule["local_time"]
        )
        scheduled_for = scheduled.astimezone(timezone.utc).isoformat(timespec="seconds")
        with self.db.connect() as conn:
            existing = conn.execute(
                """SELECT * FROM daily_ops_runs
                   WHERE tenant_id=? AND schedule_id=? AND local_date=?""",
                (principal.tenant_id, schedule_id, run_date.isoformat()),
            ).fetchone()
        if existing is not None:
            replayed_run = self.db._daily_ops_run_dict(existing)
            self.db.append_audit(
                principal.tenant_id,
                principal.user_id,
                request_id,
                "daily_ops.run.trigger",
                "daily_ops_run",
                replayed_run["id"],
                "replayed",
                {"schedule_id": schedule_id, "local_date": run_date.isoformat()},
            )
            return replayed_run
        if not schedule["enabled"]:
            raise ConflictError("disabled daily ops schedules cannot be triggered")
        try:
            graph = self._published_graph(principal, schedule["graph_version_id"])
        except (ConflictError, ValidationError) as exc:
            stale_graph = self.agent_runs.graph_service.get_version(
                principal, schedule["graph_version_id"]
            )
            schedule_config, schedule_config_hash = self._schedule_config(
                schedule,
                stale_graph,
                local_date=run_date.isoformat(),
                scheduled_for=scheduled_for,
            )
            blocked, replayed = self.db.create_daily_ops_run(
                principal.tenant_id,
                schedule_id,
                local_date=run_date.isoformat(),
                timezone_name=schedule["timezone"],
                scheduled_for=scheduled_for,
                status="blocked",
                evidence_import_ids=[],
                metric_observation_ids=[],
                graph_version_id=stale_graph["id"],
                graph_version_hash=stale_graph["definition_hash"],
                schedule_config=schedule_config,
                schedule_config_hash=schedule_config_hash,
                source_gaps=[{"code": "GRAPH_NOT_EXECUTABLE"}],
                error_code="GRAPH_NOT_EXECUTABLE",
                error_message=str(exc),
            )
            self.db.append_audit(
                principal.tenant_id,
                principal.user_id,
                request_id,
                "daily_ops.run.trigger",
                "daily_ops_run",
                blocked["id"],
                "replayed" if replayed else "blocked",
                {
                    "schedule_id": schedule_id,
                    "local_date": run_date.isoformat(),
                    "error_type": type(exc).__name__,
                },
            )
            return blocked
        schedule_config, schedule_config_hash = self._schedule_config(
            schedule,
            graph,
            local_date=run_date.isoformat(),
            scheduled_for=scheduled_for,
        )
        if nonexistent:
            gaps = [{"code": "NONEXISTENT_LOCAL_TIME", "local_time": schedule["local_time"]}]
            run, replayed = self.db.create_daily_ops_run(
                principal.tenant_id, schedule_id, local_date=run_date.isoformat(),
                timezone_name=schedule["timezone"], scheduled_for=scheduled_for,
                status="blocked", evidence_import_ids=[], metric_observation_ids=[],
                graph_version_id=graph["id"], graph_version_hash=graph["definition_hash"],
                schedule_config=schedule_config,
                schedule_config_hash=schedule_config_hash,
                source_gaps=gaps, error_code="NONEXISTENT_LOCAL_TIME",
                error_message="scheduled local time does not exist on this date",
            )
        else:
            try:
                raw_ids, metric_ids, gaps = self._resolve_sources(
                    schedule, scheduled.astimezone(timezone.utc)
                )
                if not raw_ids and not metric_ids:
                    brief = self._empty_brief(
                        schedule, run_date.isoformat(), scheduled_for, gaps,
                        graph["definition_hash"],
                    )
                    status, code, message = "empty", "NO_ELIGIBLE_SOURCES", "no eligible evidence was available"
                else:
                    brief, status, code, message = None, "scheduled", None, None
                run, replayed = self.db.create_daily_ops_run(
                    principal.tenant_id, schedule_id, local_date=run_date.isoformat(),
                    timezone_name=schedule["timezone"], scheduled_for=scheduled_for,
                    status=status, evidence_import_ids=raw_ids,
                    metric_observation_ids=metric_ids, graph_version_id=graph["id"],
                    graph_version_hash=graph["definition_hash"], source_gaps=gaps,
                    schedule_config=schedule_config,
                    schedule_config_hash=schedule_config_hash,
                    error_code=code, error_message=message, brief=brief,
                )
            except ValidationError as exc:
                run, replayed = self.db.create_daily_ops_run(
                    principal.tenant_id, schedule_id, local_date=run_date.isoformat(),
                    timezone_name=schedule["timezone"], scheduled_for=scheduled_for,
                    status="blocked", evidence_import_ids=[], metric_observation_ids=[],
                    graph_version_id=graph["id"], graph_version_hash=graph["definition_hash"],
                    schedule_config=schedule_config,
                    schedule_config_hash=schedule_config_hash,
                    source_gaps=[], error_code="SOURCE_SELECTION_INVALID", error_message=str(exc),
                )
        self.db.append_audit(
            principal.tenant_id, principal.user_id, request_id,
            "daily_ops.run.trigger", "daily_ops_run", run["id"],
            "replayed" if replayed else run["status"],
            {"schedule_id": schedule_id, "local_date": run_date.isoformat()},
        )
        return run

    @staticmethod
    def _report(bundle: dict[str, Any]) -> dict[str, Any]:
        attempt = bundle["run"]["attempt_count"]
        reviewer_tasks = [
            task for task in bundle["tasks"]
            if task.get("role") == "reviewer"
        ]
        if (
            len(reviewer_tasks) != 1
            or reviewer_tasks[0]["status"] != "completed"
            or bundle["run"].get("review_status") != "approved"
            or not bundle["run"].get("graph_version_id")
            or not bundle["run"].get("graph_version_hash")
        ):
            raise ConflictError("final agent attempt has no completed reviewer task")
        reviewer_task = reviewer_tasks[0]
        reviewers = [artifact for artifact in bundle["artifacts"] if (
            artifact["kind"] == "reviewer_verdict"
            and artifact["task_id"] == reviewer_task["id"]
            and artifact["attempt"] == reviewer_task["attempt_count"]
        )]
        if len(reviewers) != 1 or reviewers[0]["content"].get("verdict") != "approved":
            raise ConflictError("final agent attempt has no approved reviewer artifact")
        reports = [
            artifact["content"] for artifact in bundle["artifacts"]
            if artifact["kind"] == "weekly_ops_report" and artifact["attempt"] == attempt
        ]
        if len(reports) != 1:
            raise ConflictError("approved agent run has no report artifact")
        report = reports[0]
        source_platforms = {
            source["source_id"]: source["platform"]
            for source in bundle["run"]["evidence"]
        }
        valid_owners = {
            task["agent_name"]
            for task in bundle["tasks"]
            if task.get("role") in {
                "evidence_analyst", "platform_specialist", "cross_controller"
            }
        } | {"human_operator"}
        WeeklyOpsCouncil._validate_refs(
            report, source_platforms, manager=True, valid_owners=valid_owners
        )
        WeeklyOpsCouncil._validate_manager_metric_claims(
            report, bundle["run"]["evidence"]
        )
        WeeklyOpsCouncil._validate_reviewer(
            reviewers[0]["content"], source_platforms, report
        )
        return report

    def execute(self, principal: Principal, run_id: str, request_id: str) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        claimed = self.db.claim_daily_ops_run(tenant_id=principal.tenant_id, run_id=run_id)
        if claimed is None:
            current = self.db.get_daily_ops_run(principal.tenant_id, run_id)
            if current["status"] in {"completed", "empty", "blocked", "failed"}:
                return current
            if (
                current["status"] == "scheduled"
                and self._parse_instant(current["scheduled_for"]) > datetime.now(timezone.utc)
            ):
                raise ConflictError("daily ops run is not due yet")
            raise ConflictError(f"daily ops run cannot execute from status {current['status']}")
        schedule = self._verified_run_config(claimed)
        claim_attempt = int(claimed["attempt_count"])
        lease_token = str(claimed["lease_token"])

        def persist(values: dict[str, Any]) -> dict[str, Any]:
            return self.db.update_claimed_daily_ops_run(
                principal.tenant_id,
                run_id,
                attempt_count=claim_attempt,
                lease_token=lease_token,
                values=values,
            )

        try:
            self.db.renew_daily_ops_lease(
                principal.tenant_id,
                run_id,
                attempt_count=claim_attempt,
                lease_token=lease_token,
            )
            agent_run = self.agent_runs.request(
                principal, "weekly_ops", schedule["objective"], None,
                f"daily-ops:{claimed['id']}:attempt:{claimed['attempt_count']}",
                request_id,
                evidence_import_ids=claimed["selected_evidence_import_ids"],
                metric_observation_ids=claimed["selected_metric_observation_ids"],
                graph_version_id=claimed["graph_version_id"],
                origin="daily_ops",
                parent_daily_ops_run_id=claimed["id"],
                parent_daily_ops_attempt=claim_attempt,
                parent_daily_ops_lease_token=lease_token,
            )
            persist({"agent_run_id": agent_run["id"]})
            self.db.renew_daily_ops_lease(
                principal.tenant_id,
                run_id,
                attempt_count=claim_attempt,
                lease_token=lease_token,
            )
            bundle = self.agent_runs.execute(principal, agent_run["id"], request_id)
            review_status = bundle["run"].get("review_status")
            if review_status != "approved":
                reviewer = next(
                    (
                        artifact["content"] for artifact in reversed(bundle["artifacts"])
                        if artifact["kind"] == "reviewer_verdict"
                    ),
                    {"verdict": review_status, "issues": [], "limitations": []},
                )
                blocked_brief = {
                    "schema_version": 1, "kind": "daily_ops_brief", "status": "blocked",
                    "local_date": claimed["local_date"], "timezone": claimed["timezone"],
                    "scheduled_for": claimed["scheduled_for"], "generated_at": utc_now(),
                    "schedule": {"id": schedule["schedule_id"], "name": schedule["name"], "platform": schedule["platform"]},
                    "graph": {"version_id": claimed["graph_version_id"], "definition_hash": claimed["graph_version_hash"]},
                    "inputs": {"evidence_import_ids": claimed["selected_evidence_import_ids"],
                               "metric_observation_ids": claimed["selected_metric_observation_ids"]},
                    "source_gaps": claimed["source_gaps"], "agent_run_id": agent_run["id"],
                    "review_status": review_status, "reviewer": reviewer, "report": None,
                }
                result = persist(
                    {
                        "status": "blocked", "lease_until": None,
                        "lease_token": None,
                        "completed_at": utc_now(), "error_code": "REVIEW_NOT_APPROVED",
                        "error_message": f"independent reviewer verdict was {review_status}",
                        "brief_json": json.dumps(blocked_brief, ensure_ascii=False, sort_keys=True),
                        "source_gaps_json": json.dumps(
                            [*claimed["source_gaps"], {"code": "REVIEW_NOT_APPROVED", "verdict": review_status}],
                            sort_keys=True,
                        ),
                    }
                )
            else:
                brief = {
                    "schema_version": 1, "kind": "daily_ops_brief", "status": "completed",
                    "local_date": claimed["local_date"], "timezone": claimed["timezone"],
                    "scheduled_for": claimed["scheduled_for"], "generated_at": utc_now(),
                    "schedule": {"id": schedule["schedule_id"], "name": schedule["name"], "platform": schedule["platform"]},
                    "graph": {"version_id": claimed["graph_version_id"], "definition_hash": claimed["graph_version_hash"]},
                    "inputs": {
                        "evidence_import_ids": claimed["selected_evidence_import_ids"],
                        "metric_observation_ids": claimed["selected_metric_observation_ids"],
                    },
                    "source_gaps": claimed["source_gaps"], "agent_run_id": agent_run["id"],
                    "review_status": review_status, "report": self._report(bundle),
                }
                result = persist(
                    {
                        "status": "completed", "lease_until": None, "completed_at": utc_now(),
                        "lease_token": None,
                        "error_code": None, "error_message": None,
                        "brief_json": json.dumps(brief, ensure_ascii=False, sort_keys=True),
                    }
                )
            self.db.append_audit(
                principal.tenant_id, principal.user_id, request_id,
                "daily_ops.run.execute", "daily_ops_run", run_id, result["status"],
                {"agent_run_id": result["agent_run_id"], "review_status": review_status},
            )
            return result
        except Exception as exc:
            try:
                result = persist(
                    {
                        "status": "failed",
                        "lease_until": None,
                        "lease_token": None,
                        "completed_at": utc_now(),
                        "error_code": type(exc).__name__,
                        "error_message": str(exc)[:2000],
                    }
                )
            except ConflictError:
                self.db.append_audit(
                    principal.tenant_id,
                    principal.user_id,
                    request_id,
                    "daily_ops.run.execute",
                    "daily_ops_run",
                    run_id,
                    "lease_lost",
                    {"attempt_count": claim_attempt},
                )
                return self.db.get_daily_ops_run(principal.tenant_id, run_id)
            self.db.append_audit(
                principal.tenant_id, principal.user_id, request_id,
                "daily_ops.run.execute", "daily_ops_run", run_id, "failed",
                {"error_type": type(exc).__name__},
            )
            return result

    def retry(self, principal: Principal, run_id: str, request_id: str) -> dict[str, Any]:
        self.auth.require(principal, "operator")
        run = self.db.get_daily_ops_run(principal.tenant_id, run_id)
        if run["status"] == "scheduled":
            self.db.append_audit(
                principal.tenant_id,
                principal.user_id,
                request_id,
                "daily_ops.run.retry",
                "daily_ops_run",
                run_id,
                "replayed",
                {},
            )
            return run
        if run["status"] not in {"failed", "blocked", "empty"}:
            raise ConflictError(f"daily ops run cannot retry from status {run['status']}")
        if run["attempt_count"] >= run["max_attempts"]:
            raise ConflictError("daily ops run exhausted its retry attempts")
        schedule = self._verified_run_config(run)
        graph = self._published_graph(principal, schedule["graph_version_id"])
        if graph["definition_hash"] != schedule["graph_version_hash"]:
            raise ConflictError("daily ops frozen graph hash no longer matches")
        if run["error_code"] == "NONEXISTENT_LOCAL_TIME":
            raise ConflictError(
                "a nonexistent frozen local time cannot be retried; create a corrected schedule"
            )
        scheduled_for = run["scheduled_for"]
        raw_ids = run["selected_evidence_import_ids"]
        metric_ids = run["selected_metric_observation_ids"]
        gaps = run["source_gaps"]
        if not raw_ids and not metric_ids:
            try:
                raw_ids, metric_ids, gaps = self._resolve_sources(
                    schedule, self._parse_instant(scheduled_for)
                )
            except ValidationError as exc:
                result = self.db.update_daily_ops_run(
                    principal.tenant_id, run_id,
                    {"status": "blocked", "error_code": "SOURCE_SELECTION_INVALID",
                     "error_message": str(exc), "completed_at": utc_now()},
                )
                self.db.append_audit(
                    principal.tenant_id, principal.user_id, request_id,
                    "daily_ops.run.retry", "daily_ops_run", run_id, "blocked",
                    {"error_type": type(exc).__name__},
                )
                return result
            if not raw_ids and not metric_ids:
                brief = self._empty_brief(
                    schedule, run["local_date"], scheduled_for, gaps,
                    graph["definition_hash"],
                )
                result = self.db.update_daily_ops_run(
                    principal.tenant_id, run_id,
                    {"status": "empty", "source_gaps_json": json.dumps(gaps, sort_keys=True),
                     "brief_json": json.dumps(brief, sort_keys=True),
                     "error_code": "NO_ELIGIBLE_SOURCES",
                     "error_message": "no eligible evidence was available", "completed_at": utc_now()},
                )
                self.db.append_audit(
                    principal.tenant_id, principal.user_id, request_id,
                    "daily_ops.run.retry", "daily_ops_run", run_id, "empty",
                    {"source_gap_count": len(gaps)},
                )
                return result
        prepared = self.db.update_daily_ops_run(
            principal.tenant_id, run_id,
            {
                "status": "scheduled",
                "selected_evidence_import_ids_json": json.dumps(raw_ids, sort_keys=True),
                "selected_metric_observation_ids_json": json.dumps(metric_ids, sort_keys=True),
                "agent_run_id": None, "brief_json": None,
                "source_gaps_json": json.dumps(gaps, sort_keys=True),
                "error_code": None, "error_message": None, "lease_until": None,
                "lease_token": None,
                "completed_at": None,
            },
        )
        self.db.append_audit(
            principal.tenant_id, principal.user_id, request_id,
            "daily_ops.run.retry", "daily_ops_run", run_id, "accepted",
            {
                "retained_inputs": bool(
                    run["selected_evidence_import_ids"]
                    or run["selected_metric_observation_ids"]
                ),
                "graph_version_id": graph["id"],
            },
        )
        return prepared

    def scheduler_run_once(self, now: datetime | None = None) -> dict[str, Any] | None:
        instant = now or datetime.now(timezone.utc)
        if instant.tzinfo is None:
            raise ValidationError("scheduler time must include a timezone")
        candidates: list[tuple[datetime, dict[str, Any], date]] = []
        for tenant in self.db.list_tenants():
            for schedule in self.db.list_daily_ops_schedules(tenant["id"]):
                if not schedule["enabled"]:
                    continue
                local_date = self._date(schedule["next_local_date"])
                scheduled, _ = self._scheduled_for(
                    local_date, schedule["timezone"], schedule["local_time"]
                )
                if scheduled.astimezone(timezone.utc) <= instant.astimezone(timezone.utc):
                    candidates.append((scheduled.astimezone(timezone.utc), schedule, local_date))
        for _, schedule, local_date in sorted(candidates, key=lambda item: (item[0], item[1]["id"])):
            principal = self.db.principal_for_user(schedule["tenant_id"], schedule["created_by"])
            scheduler_request_id = f"daily-ops-scheduler:{schedule['id']}:{local_date.isoformat()}"
            try:
                result = self.trigger(
                    principal, schedule["id"], scheduler_request_id, local_date.isoformat(),
                )
            except Exception as exc:
                scheduled, _ = self._scheduled_for(
                    local_date, schedule["timezone"], schedule["local_time"]
                )
                with self.db.connect() as conn:
                    graph = conn.execute(
                        """SELECT id,definition_hash FROM agent_graph_versions
                           WHERE tenant_id=? AND id=?""",
                        (schedule["tenant_id"], schedule["graph_version_id"]),
                    ).fetchone()
                if graph is None:  # protected by the schedule FK; defensive only
                    raise
                scheduled_for = scheduled.astimezone(timezone.utc).isoformat(
                    timespec="seconds"
                )
                schedule_config, schedule_config_hash = self._schedule_config(
                    schedule,
                    dict(graph),
                    local_date=local_date.isoformat(),
                    scheduled_for=scheduled_for,
                )
                blocked, _ = self.db.create_daily_ops_run(
                    schedule["tenant_id"], schedule["id"],
                    local_date=local_date.isoformat(), timezone_name=schedule["timezone"],
                    scheduled_for=scheduled_for,
                    status="blocked", evidence_import_ids=[], metric_observation_ids=[],
                    graph_version_id=graph["id"], graph_version_hash=graph["definition_hash"],
                    schedule_config=schedule_config,
                    schedule_config_hash=schedule_config_hash,
                    source_gaps=[{"code": "SCHEDULER_TRIGGER_FAILED"}],
                    error_code="SCHEDULER_TRIGGER_FAILED", error_message=str(exc)[:2000],
                )
                self.db.append_audit(
                    schedule["tenant_id"], principal.user_id, scheduler_request_id,
                    "daily_ops.run.trigger", "daily_ops_run", blocked["id"], "blocked",
                    {"error_type": type(exc).__name__},
                )
                result = blocked
            try:
                self.db.advance_daily_ops_schedule(
                    schedule["tenant_id"],
                    schedule["id"],
                    expected_local_date=local_date.isoformat(),
                    next_local_date=(local_date + timedelta(days=1)).isoformat(),
                )
            except ConflictError:
                # A concurrent scheduler already advanced the same durable cursor.
                pass
            return result
        return None

    def worker_run_once(self) -> dict[str, Any] | None:
        exhausted = self.db.fail_exhausted_daily_ops_run()
        if exhausted is not None:
            schedule = self.db.get_daily_ops_schedule(
                exhausted["tenant_id"], exhausted["schedule_id"]
            )
            self.db.append_audit(
                exhausted["tenant_id"],
                schedule["created_by"],
                f"daily-ops-worker:{exhausted['id']}:exhausted",
                "daily_ops.run.execute",
                "daily_ops_run",
                exhausted["id"],
                "failed",
                {"error_code": "ATTEMPTS_EXHAUSTED"},
            )
            return exhausted
        now = utc_now()
        with self.db.connect() as conn:
            candidate = conn.execute(
                """SELECT r.id,r.tenant_id,r.schedule_id
                   FROM daily_ops_runs r
                   WHERE (
                       (r.status='scheduled' AND r.scheduled_for<=?)
                       OR (r.status='running' AND r.lease_until IS NOT NULL AND r.lease_until<?)
                   ) AND r.attempt_count<r.max_attempts
                   ORDER BY r.scheduled_for,r.rowid LIMIT 1""",
                (now, now),
            ).fetchone()
        if candidate is None:
            return None
        schedule = self.db.get_daily_ops_schedule(candidate["tenant_id"], candidate["schedule_id"])
        principal = self.db.principal_for_user(candidate["tenant_id"], schedule["created_by"])
        if ROLE_LEVEL.get(principal.role, 0) < ROLE_LEVEL["operator"]:
            claimed = self.db.claim_daily_ops_run(
                tenant_id=candidate["tenant_id"], run_id=candidate["id"]
            )
            if claimed is None:
                return self.db.get_daily_ops_run(candidate["tenant_id"], candidate["id"])
            blocked = self.db.update_claimed_daily_ops_run(
                candidate["tenant_id"],
                candidate["id"],
                attempt_count=claimed["attempt_count"],
                lease_token=claimed["lease_token"],
                values={
                    "status": "blocked",
                    "lease_until": None,
                    "lease_token": None,
                    "completed_at": utc_now(),
                    "error_code": "EXECUTION_PRINCIPAL_INACTIVE",
                    "error_message": "Daily Ops execution principal no longer has operator role",
                },
            )
            self.db.append_audit(
                candidate["tenant_id"],
                principal.user_id,
                f"daily-ops-worker:{candidate['id']}",
                "daily_ops.run.execute",
                "daily_ops_run",
                candidate["id"],
                "blocked",
                {"error_code": "EXECUTION_PRINCIPAL_INACTIVE"},
            )
            return blocked
        return self.execute(
            principal, candidate["id"],
            f"daily-ops-worker:{candidate['id']}",
        )
