"""Authenticated JSON API for the runtime vertical slice.

This is intentionally a small standard-library server so the package can be
run in a clean Python environment.  It is a real API boundary, not an MCP
protocol implementation; the MCP adapter remains separately available.
"""

from __future__ import annotations

import json
import ipaddress
import logging
import mimetypes
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .actions import ActionService
from .accounts import MarketplaceAccountService
from .agents import AgentProvider, OpenAIResponsesProvider, WeeklyOpsCouncil
from .auth import AuthService
from .briefing import BriefingService
from .evidence import CSVIngestor, EvidenceImportService, REPORT_SPECS, XLSXIngestor
from .evals import WorkflowEvaluator
from .jobs import JobService, ScheduleService
from .errors import AuthenticationError, AuthorizationError, ConflictError, ConnectorError, NotFoundError, RateLimitError, RuntimeErrorBase, ValidationError
from .observability import JsonFormatter, Metrics, RateLimiter
from .report_recipes import ReportRecipeService
from .report_syncs import ReportSyncService
from .storage import Database, Principal

log = logging.getLogger("ecommerce_ai_skills.api")
WEB_ROOT = Path(__file__).resolve().parent / "web"


class RuntimeApplication:
    def __init__(
        self,
        db: Database,
        *,
        rate_limit_per_minute: int = 120,
        agent_provider: AgentProvider | None = None,
    ):
        self.db = db
        self.auth = AuthService(db)
        self.accounts = MarketplaceAccountService(db, self.auth)
        self.report_recipes = ReportRecipeService(db, self.auth)
        self.evidence_imports = EvidenceImportService(db, self.auth)
        self.report_syncs = ReportSyncService(
            db, self.auth, self.evidence_imports
        )
        self.actions = ActionService(db, self.auth, self.evidence_imports)
        self.briefing = BriefingService(db, self.auth)
        self.agent_runs = WeeklyOpsCouncil(
            db,
            self.auth,
            agent_provider or OpenAIResponsesProvider(),
            evidence_resolver=self.evidence_imports.resolve,
        )
        self.jobs = JobService(db, self.auth, self.agent_runs)
        self.schedules = ScheduleService(
            db, self.auth, self.agent_runs, self.jobs
        )
        self.evaluator = WorkflowEvaluator(db, self.auth)
        self.metrics = Metrics()
        self.rate_limiter = RateLimiter(rate_limit_per_minute)
        self.demo_session: dict[str, str] | None = None
        self.demo_key_id: str | None = None

    def bootstrap(self, name: str, email: str) -> dict[str, str]:
        tenant_id, user_id = self.db.create_tenant(name, email)
        return {"tenant_id": tenant_id, "user_id": user_id, "api_key": self.auth.issue_key(tenant_id, user_id)}

    @staticmethod
    def _validate_bind_host(host: str, allow_public: bool) -> None:
        if allow_public:
            return
        if host == "localhost":
            return
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            raise ValidationError("non-loopback host requires --allow-public")
        if not address.is_loopback:
            raise ValidationError("non-loopback host requires --allow-public")


class _Handler(BaseHTTPRequestHandler):
    server_version = "EcommerceAI/1.2"

    @property
    def app(self) -> RuntimeApplication:
        return self.server.app  # type: ignore[attr-defined]

    def _request_id(self) -> str:
        supplied = self.headers.get("X-Request-ID", "").strip()
        return supplied[:128] if supplied else secrets.token_hex(16)

    def _json(self, status: int, value: dict[str, Any], request_id: str, *, extra_headers: dict[str, str] | None = None) -> None:
        body = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Request-ID", request_id)
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _static(self, path: str, request_id: str) -> None:
        assets: dict[str, tuple[str, str]] = {
            "/app": ("mission-control.html", "text/html; charset=utf-8"),
            "/app/": ("mission-control.html", "text/html; charset=utf-8"),
            "/app/app.js": ("app.js", "text/javascript; charset=utf-8"),
            "/app/styles.css": ("styles.css", "text/css; charset=utf-8"),
        }
        asset = assets.get(path)
        if asset is None and path.startswith("/app/assets/"):
            relative = path.removeprefix("/app/")
            parts = Path(relative).parts
            if not parts or any(part in {"", ".", ".."} for part in parts):
                raise NotFoundError("route not found")
            guessed = mimetypes.guess_type(relative)[0] or "application/octet-stream"
            asset = (relative, guessed)
        if asset is None:
            raise NotFoundError("route not found")
        file_path = (WEB_ROOT / asset[0]).resolve()
        if not file_path.is_relative_to(WEB_ROOT.resolve()) or not file_path.is_file():
            raise NotFoundError("web application asset not found")
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", asset[1])
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; connect-src 'self'; img-src 'self' data:; "
            "script-src 'self'; style-src 'self'; object-src 'none'; "
            "base-uri 'none'; frame-ancestors 'none'",
        )
        self.send_header("X-Request-ID", request_id)
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise ValidationError("request body exceeds 1 MB")
        raw = self.rfile.read(length)
        if not raw:
            return {}
        value = json.loads(raw.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValidationError("JSON body must be an object")
        return value

    def _raw_body(self, *, max_bytes: int) -> bytes:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValidationError("Content-Length must be an integer") from exc
        if length < 1:
            raise ValidationError("request body is required")
        if length > max_bytes:
            raise ValidationError(f"request body exceeds {max_bytes} bytes")
        raw = self.rfile.read(length)
        if len(raw) != length:
            raise ValidationError("request body ended before Content-Length")
        return raw

    def _body_fields(self, *, required: set[str], allowed: set[str] | None = None) -> dict[str, Any]:
        body = self._body()
        allowed = allowed or required
        missing = sorted(required - set(body))
        extra = sorted(set(body) - allowed)
        if missing:
            raise ValidationError(f"missing required fields: {', '.join(missing)}")
        if extra:
            raise ValidationError(f"unknown fields: {', '.join(extra)}")
        return body

    def _principal(self) -> Principal:
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            raise AuthenticationError("Authorization: Bearer <eai_key> is required")
        return self.app.auth.authenticate(header[7:].strip())

    def _error(self, exc: Exception, request_id: str) -> None:
        self.app.metrics.increment("http_errors_total")
        status = 400
        if isinstance(exc, AuthenticationError): status = 401
        elif isinstance(exc, AuthorizationError): status = 403
        elif isinstance(exc, NotFoundError): status = 404
        elif isinstance(exc, ConflictError): status = 409
        elif isinstance(exc, ConnectorError): status = 502
        elif isinstance(exc, RateLimitError): status = 429
        elif isinstance(exc, RuntimeErrorBase): status = 422
        elif isinstance(exc, (json.JSONDecodeError, UnicodeDecodeError)): status = 400
        log.warning("request_failed request_id=%s error=%s type=%s", request_id, str(exc), type(exc).__name__)
        extra = {"Retry-After": str(exc.retry_after)} if isinstance(exc, RateLimitError) else None
        self._json(status, {"error": {"type": type(exc).__name__, "message": str(exc)}, "request_id": request_id}, request_id, extra_headers=extra)

    def _client_key(self) -> str:
        address = getattr(self, "client_address", ("local",))[0]
        return str(address)

    def _check_rate_limit(self) -> None:
        self.app.rate_limiter.check(self._client_key())

    def do_GET(self) -> None:  # noqa: N802
        request_id = self._request_id()
        self.app.metrics.increment("http_requests_total")
        try:
            parsed = urlparse(self.path)
            if parsed.path in {"/app", "/app/", "/app/app.js", "/app/styles.css"} or parsed.path.startswith("/app/assets/"):
                self._static(parsed.path, request_id)
                return
            if parsed.path not in {"/healthz", "/readyz"}:
                self._check_rate_limit()
            if parsed.path == "/healthz":
                self._json(200, {"status": "ok", "service": "ecommerce-ai-runtime"}, request_id)
                return
            if parsed.path == "/readyz":
                readiness = self.app.db.readiness()
                self._json(200 if readiness["status"] == "ready" else 503, readiness, request_id)
                return
            if parsed.path == "/v1/demo-session":
                if self.app.demo_session is None:
                    raise NotFoundError("route not found")
                self._json(
                    200,
                    self.app.demo_session,
                    request_id,
                    extra_headers={"Cache-Control": "no-store"},
                )
                return
            principal = self._principal()
            if parsed.path == "/v1/me":
                tenant = self.app.db.get_tenant(principal.tenant_id)
                self._json(200, {"tenant_id": principal.tenant_id, "tenant_name": tenant["name"], "tenant_mode": tenant["mode"], "user_id": principal.user_id, "email": principal.email, "role": principal.role}, request_id)
            elif parsed.path == "/v1/users":
                self._json(200, {"users": self.app.auth.list_users(principal)}, request_id)
            elif parsed.path == "/v1/audit":
                self.app.auth.require(principal, "viewer")
                limit = int(parse_qs(parsed.query).get("limit", [100])[0])
                self._json(200, {"events": self.app.db.list_audit(principal.tenant_id, limit)}, request_id)
            elif parsed.path == "/v1/records":
                self.app.auth.require(principal, "viewer")
                provider = parse_qs(parsed.query).get("provider", [None])[0]
                self._json(200, {"records": self.app.db.list_records(principal.tenant_id, provider)}, request_id)
            elif parsed.path == "/v1/metrics":
                self.app.auth.require(principal, "viewer")
                self._json(200, {"counters": self.app.metrics.snapshot()}, request_id)
            elif parsed.path == "/v1/api-keys":
                self.app.auth.require(principal, "admin")
                self._json(200, {"keys": self.app.db.list_api_keys(principal.tenant_id)}, request_id)
            elif parsed.path == "/v1/connectors":
                self._json(
                    200, {"connectors": self.app.accounts.list(principal)}, request_id
                )
            elif parsed.path.startswith("/v1/connectors/") and len(parsed.path.split("/")) == 4:
                account_id = parsed.path.split("/")[3]
                self._json(200, self.app.accounts.get(principal, account_id), request_id)
            elif parsed.path == "/v1/report-recipes":
                self._json(
                    200,
                    {"report_recipes": self.app.report_recipes.list(principal)},
                    request_id,
                )
            elif parsed.path.startswith("/v1/report-recipes/") and len(parsed.path.split("/")) == 4:
                recipe_id = parsed.path.split("/")[3]
                self._json(
                    200, self.app.report_recipes.get(principal, recipe_id), request_id
                )
            elif parsed.path == "/v1/report-syncs":
                limit = int(parse_qs(parsed.query).get("limit", [100])[0])
                self._json(
                    200,
                    {"report_syncs": self.app.report_syncs.list(principal, limit)},
                    request_id,
                )
            elif parsed.path.startswith("/v1/report-syncs/") and len(parsed.path.split("/")) == 4:
                sync_id = parsed.path.split("/")[3]
                self._json(
                    200, self.app.report_syncs.get(principal, sync_id), request_id
                )
            elif parsed.path == "/v1/evidence-imports":
                limit = int(parse_qs(parsed.query).get("limit", [100])[0])
                self._json(
                    200,
                    {"imports": self.app.evidence_imports.list(principal, limit)},
                    request_id,
                )
            elif parsed.path.startswith("/v1/evidence-imports/") and len(parsed.path.split("/")) == 4:
                import_id = parsed.path.split("/")[3]
                self._json(200, self.app.evidence_imports.get(principal, import_id), request_id)
            elif parsed.path == "/v1/agent-runs":
                limit = int(parse_qs(parsed.query).get("limit", [50])[0])
                self._json(200, {"runs": self.app.agent_runs.list(principal, limit)}, request_id)
            elif parsed.path.startswith("/v1/agent-runs/") and parsed.path.endswith("/events"):
                run_id = parsed.path.split("/")[3]
                params = parse_qs(parsed.query)
                self.app.auth.require(principal, "viewer")
                self._json(
                    200,
                    self.app.db.list_agent_events_after(
                        principal.tenant_id,
                        run_id,
                        after=params.get("after", [None])[0],
                        limit=int(params.get("limit", [100])[0]),
                    ),
                    request_id,
                )
            elif parsed.path.startswith("/v1/agent-runs/") and len(parsed.path.split("/")) == 4:
                run_id = parsed.path.split("/")[3]
                self._json(200, self.app.agent_runs.get(principal, run_id), request_id)
            elif parsed.path.startswith("/v1/agent-runs/") and parsed.path.endswith("/evaluations"):
                run_id = parsed.path.split("/")[3]
                self._json(
                    200,
                    {"evaluations": self.app.evaluator.list(principal, run_id)},
                    request_id,
                )
            elif parsed.path == "/v1/jobs":
                limit = int(parse_qs(parsed.query).get("limit", [100])[0])
                self._json(200, {"jobs": self.app.jobs.list(principal, limit)}, request_id)
            elif parsed.path.startswith("/v1/jobs/") and len(parsed.path.split("/")) == 4:
                job_id = parsed.path.split("/")[3]
                self._json(200, self.app.jobs.get(principal, job_id), request_id)
            elif parsed.path == "/v1/schedules":
                self._json(
                    200, {"schedules": self.app.schedules.list(principal)}, request_id
                )
            elif parsed.path == "/v1/approvals":
                self.app.auth.require(principal, "admin")
                self._json(
                    200,
                    {
                        "actions": self.app.db.list_actions(
                            principal.tenant_id, status="requested", limit=100
                        )
                    },
                    request_id,
                )
            elif parsed.path == "/v1/mission-control":
                self.app.auth.require(principal, "viewer")
                self._json(
                    200, self.app.db.mission_control(principal.tenant_id), request_id
                )
            elif parsed.path == "/v1/briefing":
                platform = parse_qs(parsed.query).get("platform", ["amazon"])[0]
                self._json(
                    200, self.app.briefing.get(principal, platform), request_id
                )
            elif parsed.path == "/v1/catalog":
                self.app.auth.require(principal, "viewer")
                platforms = sorted(
                    self.app.agent_runs.platform_registry.entries().values(),
                    key=lambda item: item["id"],
                )
                connector_catalog = self.app.accounts.catalog()
                self._json(
                    200,
                    {
                        "platforms": platforms,
                        "report_types": sorted(REPORT_SPECS),
                        "workflows": [WeeklyOpsCouncil.WORKFLOW],
                        "action_operations": sorted(ActionService.OPERATIONS),
                        "report_recipe_types": self.app.report_recipes.catalog(),
                        **connector_catalog,
                    },
                    request_id,
                )
            else:
                raise NotFoundError("route not found")
        except Exception as exc:
            self._error(exc, request_id)

    def do_POST(self) -> None:  # noqa: N802
        request_id = self._request_id()
        self.app.metrics.increment("http_requests_total")
        try:
            parsed = urlparse(self.path)
            self._check_rate_limit()
            if parsed.path == "/v1/api-keys/rotate":
                principal = self._principal()
                replacement = self.app.auth.rotate_current(principal)
                self.app.db.append_audit(principal.tenant_id, principal.user_id, request_id, "api_key.rotate", "api_key", principal.api_key_id, "succeeded", {})
                self._json(200, {"api_key": replacement}, request_id); return
            if parsed.path == "/v1/api-keys":
                principal = self._principal()
                body = self._body_fields(required={"user_id"})
                user_id = str(body["user_id"])
                key = self.app.auth.issue_for_user(principal, user_id)
                self.app.db.append_audit(principal.tenant_id, principal.user_id, request_id, "api_key.issue", "api_key", None, "succeeded", {"user_id": user_id})
                self._json(201, {"api_key": key, "user_id": user_id}, request_id); return
            if parsed.path == "/v1/users":
                principal = self._principal()
                body = self._body_fields(required={"email", "role"})
                user = self.app.auth.create_user(principal, str(body["email"]), str(body["role"]))
                self.app.db.append_audit(principal.tenant_id, principal.user_id, request_id, "user.create", "user", str(user["id"]), "succeeded", {"role": user["role"]})
                self._json(201, {"user": user}, request_id); return
            if parsed.path.startswith("/v1/api-keys/") and parsed.path.endswith("/revoke"):
                principal = self._principal()
                key_id = parsed.path.split("/")[3]
                self.app.auth.revoke(principal, key_id)
                self.app.db.append_audit(principal.tenant_id, principal.user_id, request_id, "api_key.revoke", "api_key", key_id, "succeeded", {})
                self._json(200, {"revoked": True, "key_id": key_id}, request_id); return
            if parsed.path == "/v1/connectors":
                principal = self._principal()
                body = self._body_fields(
                    required={"provider", "external_account_id", "config"}
                )
                account = self.app.accounts.create(
                    principal,
                    provider=body["provider"],
                    external_account_id=body["external_account_id"],
                    config=body["config"],
                    request_id=request_id,
                )
                self._json(201, account, request_id); return
            if parsed.path.startswith("/v1/connectors/") and parsed.path.endswith("/health-check") and len(parsed.path.split("/")) == 5:
                principal = self._principal()
                body = self._body_fields(required=set(), allowed=set())
                account_id = parsed.path.split("/")[3]
                self._json(
                    200,
                    self.app.accounts.health_check(
                        principal, account_id, request_id=request_id
                    ),
                    request_id,
                )
                return
            if parsed.path == "/v1/report-recipes":
                principal = self._principal()
                fields = {
                    "connector_account_id",
                    "name",
                    "recipe_key",
                    "marketplace_ids",
                    "interval_minutes",
                    "lookback_days",
                    "enabled",
                    "next_run_at",
                }
                body = self._body_fields(required=fields)
                self._json(
                    201,
                    self.app.report_recipes.create(
                        principal,
                        connector_account_id=body["connector_account_id"],
                        name=body["name"],
                        recipe_key=body["recipe_key"],
                        marketplace_ids=body["marketplace_ids"],
                        interval_minutes=body["interval_minutes"],
                        lookback_days=body["lookback_days"],
                        enabled=body["enabled"],
                        next_run_at=body["next_run_at"],
                        request_id=request_id,
                    ),
                    request_id,
                )
                return
            if parsed.path.startswith("/v1/report-recipes/") and parsed.path.endswith("/sync") and len(parsed.path.split("/")) == 5:
                principal = self._principal()
                self._body_fields(required=set(), allowed=set())
                recipe_id = parsed.path.split("/")[3]
                self._json(
                    202,
                    self.app.report_syncs.enqueue(
                        principal,
                        recipe_id,
                        self.headers.get("Idempotency-Key", ""),
                        request_id,
                    ),
                    request_id,
                )
                return
            if parsed.path == "/v1/evidence-imports":
                principal = self._principal()
                content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
                csv_types = {"text/csv", "text/tab-separated-values", "application/csv"}
                xlsx_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                common = {
                    "platform": self.headers.get("X-Evidence-Platform", ""),
                    "report_type": self.headers.get("X-Evidence-Type", ""),
                    "filename": self.headers.get("X-Evidence-Filename", ""),
                    "observed_at": self.headers.get("X-Evidence-Observed-At", ""),
                    "idempotency_key": self.headers.get("Idempotency-Key", ""),
                    "request_id": request_id,
                }
                if content_type in csv_types:
                    imported = self.app.evidence_imports.import_csv(
                        principal,
                        raw=self._raw_body(max_bytes=CSVIngestor.MAX_RAW_BYTES),
                        media_type=content_type,
                        **common,
                    )
                elif content_type == xlsx_type:
                    imported = self.app.evidence_imports.import_xlsx(
                        principal,
                        raw=self._raw_body(max_bytes=XLSXIngestor.MAX_RAW_BYTES),
                        sheet_name=self.headers.get("X-Evidence-Sheet") or None,
                        **common,
                    )
                else:
                    raise ValidationError("Content-Type must be CSV, TSV, or XLSX")
                self._json(200, imported, request_id); return
            principal = self._principal()
            if parsed.path == "/v1/actions":
                body = self._body()
                result = self.app.actions.request(principal, str(body.get("operation", "")), body.get("payload", {}), self.headers.get("Idempotency-Key", ""), request_id)
                self._json(200, result, request_id)
            elif parsed.path.startswith("/v1/actions/") and parsed.path.endswith("/approve"):
                action_id = parsed.path.split("/")[3]
                self._json(200, self.app.actions.approve(principal, action_id, request_id), request_id)
            elif parsed.path.startswith("/v1/actions/") and parsed.path.endswith("/execute"):
                action_id = parsed.path.split("/")[3]
                self._json(200, self.app.actions.execute(principal, action_id, request_id), request_id)
            elif parsed.path.startswith("/v1/actions/") and parsed.path.endswith("/retry"):
                action_id = parsed.path.split("/")[3]
                self._json(200, self.app.actions.retry(principal, action_id, request_id), request_id)
            elif parsed.path == "/v1/agent-runs":
                body = self._body_fields(
                    required={"workflow", "objective"},
                    allowed={"workflow", "objective", "evidence", "evidence_import_ids"},
                )
                run = self.app.agent_runs.request(
                    principal,
                    str(body["workflow"]),
                    body["objective"],
                    body.get("evidence"),
                    self.headers.get("Idempotency-Key", ""),
                    request_id,
                    evidence_import_ids=body.get("evidence_import_ids"),
                )
                self._json(200, run, request_id)
            elif parsed.path.startswith("/v1/agent-runs/") and parsed.path.endswith("/execute"):
                run_id = parsed.path.split("/")[3]
                self._json(200, self.app.agent_runs.execute(principal, run_id, request_id), request_id)
            elif parsed.path.startswith("/v1/agent-runs/") and parsed.path.endswith("/evaluate"):
                run_id = parsed.path.split("/")[3]
                self._json(
                    200,
                    self.app.evaluator.evaluate(principal, run_id, request_id),
                    request_id,
                )
            elif parsed.path == "/v1/jobs":
                body = self._body_fields(
                    required={"run_id"}, allowed={"run_id", "max_attempts"}
                )
                self._json(
                    200,
                    self.app.jobs.enqueue_agent_run(
                        principal,
                        str(body["run_id"]),
                        self.headers.get("Idempotency-Key", ""),
                        request_id,
                        max_attempts=int(body.get("max_attempts", 3)),
                    ),
                    request_id,
                )
            elif parsed.path == "/v1/schedules":
                body = self._body_fields(
                    required={
                        "name",
                        "objective",
                        "interval_minutes",
                        "next_run_at",
                    },
                    allowed={
                        "name",
                        "objective",
                        "evidence_import_ids",
                        "evidence_selectors",
                        "interval_minutes",
                        "next_run_at",
                    },
                )
                self._json(
                    201,
                    self.app.schedules.create(
                        principal,
                        name=str(body["name"]),
                        objective=str(body["objective"]),
                        evidence_import_ids=body.get("evidence_import_ids", []),
                        evidence_selectors=body.get("evidence_selectors", []),
                        interval_minutes=int(body["interval_minutes"]),
                        next_run_at=str(body["next_run_at"]),
                        request_id=request_id,
                    ),
                    request_id,
                )
            else:
                raise NotFoundError("route not found")
        except Exception as exc:
            self._error(exc, request_id)

    def do_PATCH(self) -> None:  # noqa: N802
        request_id = self._request_id()
        self.app.metrics.increment("http_requests_total")
        try:
            parsed = urlparse(self.path)
            self._check_rate_limit()
            principal = self._principal()
            if parsed.path.startswith("/v1/users/") and len(parsed.path.split("/")) == 4:
                user_id = parsed.path.split("/")[3]
                body = self._body_fields(required={"role"})
                user = self.app.auth.update_user_role(principal, user_id, str(body["role"]))
                self.app.db.append_audit(principal.tenant_id, principal.user_id, request_id, "user.role_update", "user", user_id, "succeeded", {"role": user["role"]})
                self._json(200, {"user": user}, request_id)
            elif parsed.path.startswith("/v1/connectors/") and len(parsed.path.split("/")) == 4:
                account_id = parsed.path.split("/")[3]
                body = self._body_fields(
                    required={"config"}, allowed={"external_account_id", "config"}
                )
                existing = self.app.accounts.get(principal, account_id)
                self._json(
                    200,
                    self.app.accounts.update(
                        principal,
                        account_id,
                        external_account_id=body.get(
                            "external_account_id", existing["external_account_id"]
                        ),
                        config=body["config"],
                        request_id=request_id,
                    ),
                    request_id,
                )
            elif parsed.path.startswith("/v1/report-recipes/") and len(parsed.path.split("/")) == 4:
                recipe_id = parsed.path.split("/")[3]
                fields = {
                    "name",
                    "recipe_key",
                    "marketplace_ids",
                    "interval_minutes",
                    "lookback_days",
                    "enabled",
                    "next_run_at",
                }
                body = self._body_fields(required=fields)
                self._json(
                    200,
                    self.app.report_recipes.update(
                        principal,
                        recipe_id,
                        name=body["name"],
                        recipe_key=body["recipe_key"],
                        marketplace_ids=body["marketplace_ids"],
                        interval_minutes=body["interval_minutes"],
                        lookback_days=body["lookback_days"],
                        enabled=body["enabled"],
                        next_run_at=body["next_run_at"],
                        request_id=request_id,
                    ),
                    request_id,
                )
            elif parsed.path.startswith("/v1/schedules/") and len(parsed.path.split("/")) == 4:
                schedule_id = parsed.path.split("/")[3]
                body = self._body_fields(required={"enabled"})
                if not isinstance(body["enabled"], bool):
                    raise ValidationError("enabled must be boolean")
                self._json(
                    200,
                    self.app.schedules.set_enabled(
                        principal, schedule_id, body["enabled"], request_id
                    ),
                    request_id,
                )
            else:
                raise NotFoundError("route not found")
        except Exception as exc:
            self._error(exc, request_id)

    def log_message(self, fmt: str, *args: Any) -> None:
        log.info("http %s", fmt % args)


def serve(app: RuntimeApplication, host: str = "127.0.0.1", port: int = 8787, *, allow_public: bool = False) -> None:
    RuntimeApplication._validate_bind_host(host, allow_public)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        root.addHandler(handler)
    if allow_public:
        log.warning("public bind explicitly enabled; terminate TLS and add an authenticated reverse proxy")
    httpd = ThreadingHTTPServer((host, port), _Handler)
    httpd.app = app  # type: ignore[attr-defined]
    log.info("runtime API listening on http://%s:%d", host, port)
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
