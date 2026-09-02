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
import os
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from ecommerce_ai_skills import __version__

from .actions import ActionService
from .agent_graphs import AgentGraphService
from .accounts import MarketplaceAccountService
from .assurance import AssuranceService
from .ads_gates import AdsCapabilityGateService
from .ads_adapter_status import AdsAdapterStatusService
from .agents import (
    AgentProvider,
    AnthropicMessagesProvider,
    OpenAIResponsesProvider,
    WeeklyOpsCouncil,
)
from .auth import AuthService
from .briefing import BriefingService
from .daily_ops import DailyOpsService
from .evidence import CSVIngestor, EvidenceImportService, REPORT_SPECS, XLSXIngestor
from .evals import WorkflowEvaluator
from .jobs import JobService, ScheduleService
from .metric_observations import MetricObservationService, SUPPORTED_REPORT_TYPES
from .proposals import ProposalService
from .pilot import PilotService
from .provider_smoke import ProviderSmokeService
from .errors import AuthenticationError, AuthorizationError, ConflictError, ConnectorError, NotFoundError, RateLimitError, RuntimeErrorBase, ValidationError
from .observability import JsonFormatter, Metrics, RateLimiter
from .report_recipes import ReportRecipeService
from .report_syncs import ReportSyncService
from .storage import Database, Principal

log = logging.getLogger("ecommerce_ai_skills.api")
WEB_ROOT = Path(__file__).resolve().parent / "web"


class _MissionConnectionLimiter:
    """Single-process SSE admission control for the stdlib HTTP server."""

    def __init__(self, global_limit: int, tenant_limit: int):
        self.global_limit = max(1, int(global_limit))
        self.tenant_limit = max(1, int(tenant_limit))
        self._lock = threading.Lock()
        self._global_active = 0
        self._tenant_active: dict[str, int] = {}

    def acquire(self, tenant_id: str) -> None:
        with self._lock:
            tenant_active = self._tenant_active.get(tenant_id, 0)
            if self._global_active >= self.global_limit:
                log.warning("mission_stream_connection_rejected scope=global")
                raise RateLimitError(
                    "Mission Control SSE connection limit exceeded",
                    retry_after=5,
                )
            if tenant_active >= self.tenant_limit:
                log.warning("mission_stream_connection_rejected scope=tenant")
                raise RateLimitError(
                    "Mission Control SSE connection limit exceeded",
                    retry_after=5,
                )
            self._global_active += 1
            self._tenant_active[tenant_id] = tenant_active + 1

    def release(self, tenant_id: str) -> None:
        with self._lock:
            active = self._tenant_active.get(tenant_id, 0)
            if active <= 1:
                self._tenant_active.pop(tenant_id, None)
            else:
                self._tenant_active[tenant_id] = active - 1
            self._global_active = max(0, self._global_active - 1)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "global_active": self._global_active,
                "tenant_active": dict(self._tenant_active),
            }


def _default_agent_provider() -> AgentProvider:
    """Pick the provider from the environment, defaulting to OpenAI.

    EAI_AGENT_PROVIDER selects; an explicitly injected provider always wins over
    it. The default stays OpenAI so existing deployments are unaffected by the
    Anthropic provider merely existing. An unknown value fails loudly rather than
    silently falling back — a typo that quietly routes to a different vendor is
    worse than a startup error.
    """
    name = os.environ.get("EAI_AGENT_PROVIDER", "").strip().lower()
    if not name or name in {"openai", "openai_responses"}:
        return OpenAIResponsesProvider()
    if name in {"anthropic", "anthropic_messages"}:
        return AnthropicMessagesProvider()
    raise ValidationError(
        f"EAI_AGENT_PROVIDER must be 'openai' or 'anthropic', got {name!r}"
    )


class RuntimeApplication:
    def __init__(
        self,
        db: Database,
        *,
        rate_limit_per_minute: int = 120,
        agent_provider: AgentProvider | None = None,
        provider_smoke_openai_provider: OpenAIResponsesProvider | None = None,
        mission_event_poll_seconds: float = 1.0,
        mission_event_heartbeat_seconds: float = 15.0,
        mission_event_max_lifetime_seconds: float = 300.0,
        mission_event_batch_size: int = 100,
        mission_event_max_backlog: int = 500,
        mission_event_max_connections: int = 20,
        mission_event_max_connections_per_tenant: int = 4,
    ):
        self.db = db
        self.auth = AuthService(db)
        self.assurance = AssuranceService(db,self.auth)
        self.agent_graphs = AgentGraphService(db, self.auth)
        self.accounts = MarketplaceAccountService(db, self.auth)
        resolved_agent_provider = agent_provider or _default_agent_provider()
        smoke_openai_provider = provider_smoke_openai_provider
        if smoke_openai_provider is None and isinstance(
            resolved_agent_provider, OpenAIResponsesProvider
        ):
            smoke_openai_provider = resolved_agent_provider
        self.provider_smoke = ProviderSmokeService(
            db,
            self.auth,
            self.accounts,
            openai_provider=smoke_openai_provider,
        )
        self.ads_gates = AdsCapabilityGateService(db, self.auth)
        self.ads_adapter_status = AdsAdapterStatusService(db, self.auth)
        self.report_recipes = ReportRecipeService(db, self.auth)
        self.evidence_imports = EvidenceImportService(db, self.auth)
        self.metric_observations = MetricObservationService(db, self.auth)
        self.report_syncs = ReportSyncService(
            db, self.auth, self.evidence_imports, self.metric_observations
        )
        self.actions = ActionService(db, self.auth, self.evidence_imports)
        self.proposals = ProposalService(db, self.auth, self.actions)
        self.pilot = PilotService(db, self.auth)
        self.briefing = BriefingService(db, self.auth)
        self.agent_runs = WeeklyOpsCouncil(
            db,
            self.auth,
            resolved_agent_provider,
            evidence_resolver=self.evidence_imports.resolve,
            graph_service=self.agent_graphs,
        )
        self.daily_ops = DailyOpsService(db, self.auth, self.agent_runs)
        self.jobs = JobService(db, self.auth, self.agent_runs)
        self.schedules = ScheduleService(
            db, self.auth, self.agent_runs, self.jobs
        )
        self.evaluator = WorkflowEvaluator(db, self.auth)
        self.metrics = Metrics()
        self.rate_limiter = RateLimiter(rate_limit_per_minute)
        self.mission_event_poll_seconds = max(0.01, float(mission_event_poll_seconds))
        self.mission_event_heartbeat_seconds = max(
            0.01, float(mission_event_heartbeat_seconds)
        )
        self.mission_event_max_lifetime_seconds = max(
            0.01, float(mission_event_max_lifetime_seconds)
        )
        self.mission_event_batch_size = max(
            1, min(int(mission_event_batch_size), 200)
        )
        self.mission_event_max_backlog = max(
            1, min(int(mission_event_max_backlog), 10_000)
        )
        self.mission_connections = _MissionConnectionLimiter(
            mission_event_max_connections,
            mission_event_max_connections_per_tenant,
        )
        self.demo_session: dict[str, str] | None = None
        self.demo_key_id: str | None = None

    def bootstrap(self, name: str, email: str) -> dict[str, str]:
        tenant_id, user_id = self.db.create_tenant(name, email)
        # Install the tenant's required graph before issuing the one-time key;
        # failures before this point therefore cannot strand an undisclosed key.
        principal = self.db.principal_for_user(tenant_id, user_id)
        self.agent_graphs.ensure_default(principal)
        api_key = self.auth.issue_key(tenant_id, user_id)
        return {"tenant_id": tenant_id, "user_id": user_id, "api_key": api_key}

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
    server_version = f"EcommerceAI/{__version__}"

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
            "/app/i18n.js": ("i18n.js", "text/javascript; charset=utf-8"),
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

    @staticmethod
    def _query_int(
        params: dict[str, list[str]], name: str, *, default: int, minimum: int, maximum: int
    ) -> int:
        raw = params.get(name, [str(default)])[0]
        try:
            value = int(raw)
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"{name} must be an integer") from exc
        if not minimum <= value <= maximum:
            raise ValidationError(
                f"{name} must be between {minimum} and {maximum}"
            )
        return value

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

    @staticmethod
    def _mission_cursor(value: str, source: str) -> int:
        if not value or not value.isascii() or not value.isdigit():
            raise ValidationError(f"{source} must be a non-negative integer cursor")
        cursor = int(value)
        if cursor > 9_223_372_036_854_775_807:
            raise ValidationError(f"{source} is outside the supported cursor range")
        return cursor

    def _mission_after(self, parsed: Any) -> int:
        params = parse_qs(parsed.query, keep_blank_values=True)
        unknown = set(params) - {"after"}
        if unknown:
            raise ValidationError(
                "unknown query fields: " + ", ".join(sorted(unknown))
            )
        if len(params.get("after", [])) > 1:
            raise ValidationError("after must be provided at most once")
        query_after = 0
        if "after" in params:
            query_after = self._mission_cursor(params["after"][0], "after")

        get_all = getattr(self.headers, "get_all", None)
        if callable(get_all):
            header_values = get_all("Last-Event-ID", [])
        else:
            header = self.headers.get("Last-Event-ID")
            header_values = [header] if header is not None else []
        if len(header_values) > 1:
            raise ValidationError("Last-Event-ID must be provided at most once")
        if header_values:
            # The browser reconnect cursor is authoritative, but an explicitly
            # supplied query cursor is still parsed and validated above.
            return self._mission_cursor(header_values[0].strip(), "Last-Event-ID")
        return query_after

    @staticmethod
    def _sse_frame(event_id: int, event_type: str, data: dict[str, Any]) -> bytes:
        payload = json.dumps(
            data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return (
            f"id: {event_id}\nevent: {event_type}\ndata: {payload}\n\n"
        ).encode("utf-8")

    def _mission_event_stream(
        self, parsed: Any, principal: Principal, request_id: str
    ) -> None:
        self.app.auth.require(principal, "viewer")
        marker = self._mission_after(parsed)
        # Validate the tenant cursor and retention state before committing the
        # response to an event stream, so all setup failures remain JSON.
        page = self.app.db.read_mission_events(
            principal.tenant_id,
            after=marker,
            limit=self.app.mission_event_batch_size,
        )
        self.app.mission_connections.acquire(principal.tenant_id)
        established = False
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Request-ID", request_id)
            self.end_headers()
            established = True

            started = time.monotonic()
            last_write = started
            delivered = 0
            reconnect_reason = "lifetime_limit"
            while time.monotonic() - started < self.app.mission_event_max_lifetime_seconds:
                if page["reset_required"]:
                    marker = int(page["reset_cursor"])
                    self.wfile.write(
                        self._sse_frame(
                            marker,
                            "mission.reset",
                            {
                                "reason": "retention_gap",
                                "cursor": marker,
                                "snapshot_url": "/v1/mission-control",
                            },
                        )
                    )
                    self.wfile.flush()
                    last_write = time.monotonic()
                    page = self.app.db.read_mission_events(
                        principal.tenant_id,
                        after=marker,
                        limit=self.app.mission_event_batch_size,
                    )
                    continue

                for event in page["events"]:
                    event_id = int(event["cursor"])
                    self.wfile.write(
                        self._sse_frame(event_id, "mission.update", event)
                    )
                    marker = event_id
                    delivered += 1
                    last_write = time.monotonic()
                    if delivered >= self.app.mission_event_max_backlog:
                        reconnect_reason = "backlog_limit"
                        break
                if page["events"]:
                    self.wfile.flush()
                if delivered >= self.app.mission_event_max_backlog:
                    break

                if page["has_more"]:
                    page = self.app.db.read_mission_events(
                        principal.tenant_id,
                        after=marker,
                        limit=self.app.mission_event_batch_size,
                    )
                    continue

                now = time.monotonic()
                if now - last_write >= self.app.mission_event_heartbeat_seconds:
                    self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
                    last_write = now
                time.sleep(
                    min(
                        self.app.mission_event_poll_seconds,
                        max(
                            0.01,
                            self.app.mission_event_max_lifetime_seconds
                            - (time.monotonic() - started),
                        ),
                    )
                )
                page = self.app.db.read_mission_events(
                    principal.tenant_id,
                    after=marker,
                    limit=self.app.mission_event_batch_size,
                )
            self.wfile.write(
                self._sse_frame(
                    marker,
                    "mission.reconnect",
                    {
                        "reason": reconnect_reason,
                        "retry_after_seconds": 1,
                        "cursor": marker,
                    },
                )
            )
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError) as exc:
            log.info(
                "mission_stream_disconnected request_id=%s tenant_id=%s type=%s",
                request_id,
                principal.tenant_id,
                type(exc).__name__,
            )
        except Exception:
            if established:
                log.exception(
                    "mission_stream_failed request_id=%s tenant_id=%s",
                    request_id,
                    principal.tenant_id,
                )
            else:
                raise
        finally:
            self.close_connection = True
            self.app.mission_connections.release(principal.tenant_id)

    def do_GET(self) -> None:  # noqa: N802
        request_id = self._request_id()
        self.app.metrics.increment("http_requests_total")
        try:
            parsed = urlparse(self.path)
            if parsed.path in {"/app", "/app/", "/app/app.js", "/app/i18n.js", "/app/styles.css"} or parsed.path.startswith("/app/assets/"):
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
            if parsed.path == "/v1/mission-control/events":
                self._mission_event_stream(parsed, principal, request_id)
                return
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
            elif parsed.path == "/v1/provider-smoke-tests":
                params = parse_qs(parsed.query, keep_blank_values=True)
                unknown = set(params) - {"limit"}
                if unknown:
                    raise ValidationError(
                        "unknown query fields: " + ", ".join(sorted(unknown))
                    )
                self._json(
                    200,
                    {
                        "provider_smoke_tests": self.app.provider_smoke.list(
                            principal,
                            self._query_int(
                                params, "limit", default=100, minimum=1, maximum=200
                            ),
                        )
                    },
                    request_id,
                )
            elif parsed.path.startswith("/v1/provider-smoke-tests/") and len(parsed.path.split("/")) == 4:
                smoke_test_id = parsed.path.split("/")[3]
                self._json(
                    200,
                    self.app.provider_smoke.get(principal, smoke_test_id),
                    request_id,
                )
            elif parsed.path.startswith("/v1/connectors/") and len(parsed.path.split("/")) == 4:
                account_id = parsed.path.split("/")[3]
                self._json(200, self.app.accounts.get(principal, account_id), request_id)
            elif parsed.path == "/v1/ads-capability-gates":
                params = parse_qs(parsed.query, keep_blank_values=True)
                limit = self._query_int(
                    params, "limit", default=100, minimum=1, maximum=200
                )
                self._json(
                    200,
                    {"ads_capability_gates": self.app.ads_gates.list(principal, limit)},
                    request_id,
                )
            elif parsed.path == "/v1/ads-adapter-status":
                params = parse_qs(parsed.query, keep_blank_values=True)
                unknown = set(params) - {"connector_account_id"}
                if unknown:
                    raise ValidationError("unknown query fields: " + ", ".join(sorted(unknown)))
                connector_account_id = params.get("connector_account_id", [None])[0]
                self._json(
                    200,
                    self.app.ads_adapter_status.get(principal, connector_account_id),
                    request_id,
                )
            elif parsed.path.startswith("/v1/ads-capability-gates/") and len(parsed.path.split("/")) == 4:
                gate_id = parsed.path.split("/")[3]
                self._json(200, self.app.ads_gates.get(principal, gate_id), request_id)
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
            elif parsed.path == "/v1/metric-observations":
                params = parse_qs(parsed.query, keep_blank_values=True)
                self._json(
                    200,
                    self.app.metric_observations.list_observations(
                        principal,
                        limit=self._query_int(
                            params, "limit", default=100, minimum=1, maximum=200
                        ),
                        cursor=params.get("cursor", [None])[0],
                        evidence_import_id=params.get("evidence_import_id", [None])[0],
                        platform=params.get("platform", [None])[0],
                        metric_key=params.get("metric_key", [None])[0],
                        currency=params.get("currency", [None])[0],
                    ),
                    request_id,
                )
            elif parsed.path.startswith("/v1/metric-observations/") and len(parsed.path.split("/")) == 4:
                observation_id = parsed.path.split("/")[3]
                self._json(
                    200,
                    self.app.metric_observations.get_observation(
                        principal, observation_id
                    ),
                    request_id,
                )
            elif parsed.path == "/v1/metric-materializations":
                params = parse_qs(parsed.query, keep_blank_values=True)
                self._json(
                    200,
                    self.app.metric_observations.list_materializations(
                        principal,
                        limit=self._query_int(
                            params, "limit", default=100, minimum=1, maximum=200
                        ),
                        cursor=params.get("cursor", [None])[0],
                        evidence_import_id=params.get("evidence_import_id", [None])[0],
                        status=params.get("status", [None])[0],
                    ),
                    request_id,
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
            elif parsed.path == "/v1/agent-graphs":
                self._json(
                    200, {"graphs": self.app.agent_graphs.list(principal)}, request_id
                )
            elif parsed.path.startswith("/v1/agent-graphs/") and len(parsed.path.split("/")) == 4:
                graph_id = parsed.path.split("/")[3]
                self._json(200, self.app.agent_graphs.get(principal, graph_id), request_id)
            elif parsed.path.startswith("/v1/agent-graph-versions/") and len(parsed.path.split("/")) == 4:
                version_id = parsed.path.split("/")[3]
                self._json(
                    200, self.app.agent_graphs.get_version(principal, version_id), request_id
                )
            elif parsed.path == "/v1/daily-ops-schedules":
                self._json(
                    200,
                    {"schedules": self.app.daily_ops.list_schedules(principal)},
                    request_id,
                )
            elif parsed.path.startswith("/v1/daily-ops-schedules/") and len(parsed.path.split("/")) == 4:
                schedule_id = parsed.path.split("/")[3]
                self._json(
                    200, self.app.daily_ops.get_schedule(principal, schedule_id), request_id
                )
            elif parsed.path == "/v1/daily-ops-runs":
                params = parse_qs(parsed.query, keep_blank_values=True)
                self._json(
                    200,
                    {
                        "runs": self.app.daily_ops.list_runs(
                            principal,
                            schedule_id=params.get("schedule_id", [None])[0],
                            limit=self._query_int(
                                params, "limit", default=50, minimum=1, maximum=200
                            ),
                        )
                    },
                    request_id,
                )
            elif parsed.path.startswith("/v1/daily-ops-runs/") and parsed.path.endswith("/brief") and len(parsed.path.split("/")) == 5:
                run_id = parsed.path.split("/")[3]
                self._json(200, self.app.daily_ops.get_brief(principal, run_id), request_id)
            elif parsed.path.startswith("/v1/daily-ops-runs/") and len(parsed.path.split("/")) == 4:
                run_id = parsed.path.split("/")[3]
                self._json(200, self.app.daily_ops.get_run(principal, run_id), request_id)
            elif parsed.path == "/v1/agent-runs":
                limit = int(parse_qs(parsed.query).get("limit", [50])[0])
                self._json(200, {"runs": self.app.agent_runs.list(principal, limit)}, request_id)
            elif parsed.path == "/v1/proposals":
                params = parse_qs(parsed.query, keep_blank_values=True)
                self._json(
                    200,
                    {"proposals": self.app.proposals.list(
                        principal,
                        status=params.get("status", [None])[0] or None,
                        limit=self._query_int(params, "limit", default=100, minimum=1, maximum=200),
                    )},
                    request_id,
                )
            elif parsed.path.startswith("/v1/proposals/") and len(parsed.path.split("/")) == 4:
                proposal_id = parsed.path.split("/")[3]
                self._json(200, self.app.proposals.get(principal, proposal_id), request_id)
            elif parsed.path == "/v1/proposal-executions":
                params = parse_qs(parsed.query, keep_blank_values=True)
                self._json(
                    200,
                    {"executions": self.app.proposals.list_executions(
                        principal,
                        proposal_id=params.get("proposal_id", [None])[0] or None,
                        limit=self._query_int(params, "limit", default=100, minimum=1, maximum=200),
                    )},
                    request_id,
                )
            elif parsed.path.startswith("/v1/proposal-executions/") and len(parsed.path.split("/")) == 4:
                execution_id = parsed.path.split("/")[3]
                self._json(200, self.app.proposals.get_execution(principal, execution_id), request_id)
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
            elif parsed.path == "/v1/pilot-status":
                self._json(200, self.app.pilot.status(principal), request_id)
            elif parsed.path == "/v1/assurance-runs":
                params=parse_qs(parsed.query,keep_blank_values=True)
                unknown=set(params)-{"limit"}
                if unknown: raise ValidationError("unknown query fields: "+", ".join(sorted(unknown)))
                self._json(200,{"runs":self.app.assurance.list(principal,self._query_int(params,"limit",default=100,minimum=1,maximum=200))},request_id)
            elif parsed.path.startswith("/v1/assurance-runs/") and len(parsed.path.split("/"))==4:
                self._json(200,self.app.assurance.get(principal,parsed.path.split("/")[3]),request_id)
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
                        "metric_materialization_report_types": sorted(
                            SUPPORTED_REPORT_TYPES
                        ),
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
            if parsed.path == "/v1/assurance-runs":
                principal=self._principal()
                body=self._body_fields(required={"kind"},allowed={"kind"})
                key=self.headers.get("Idempotency-Key","")
                if not key: raise ValidationError("Idempotency-Key header is required")
                self._json(201,self.app.assurance.run(principal,str(body["kind"]),key,request_id),request_id); return
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
            if parsed.path == "/v1/provider-smoke-tests":
                principal = self._principal()
                body = self._body_fields(
                    required={"provider"},
                    allowed={"provider", "connector_account_id"},
                )
                idempotency_key = self.headers.get("Idempotency-Key", "")
                if not idempotency_key:
                    raise ValidationError("Idempotency-Key header is required")
                self._json(
                    201,
                    self.app.provider_smoke.execute(
                        principal,
                        provider=body["provider"],
                        connector_account_id=body.get("connector_account_id"),
                        idempotency_key=idempotency_key,
                        request_id=request_id,
                    ),
                    request_id,
                )
                return
            if parsed.path == "/v1/ads-capability-gates":
                principal = self._principal()
                body = self._body_fields(
                    required={"connector_account_id"},
                    allowed={"connector_account_id", "attestation_reference"},
                )
                self._json(
                    201,
                    self.app.ads_gates.check(
                        principal,
                        body["connector_account_id"],
                        body.get("attestation_reference"),
                        self.headers.get("Idempotency-Key", ""),
                        request_id,
                    ),
                    request_id,
                )
                return
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
            if parsed.path.startswith("/v1/evidence-imports/") and parsed.path.endswith("/metric-materialization") and len(parsed.path.split("/")) == 5:
                principal = self._principal()
                self._body_fields(required=set(), allowed=set())
                import_id = parsed.path.split("/")[3]
                self._json(
                    200,
                    self.app.metric_observations.materialize(
                        principal,
                        import_id,
                        self.headers.get("Idempotency-Key", ""),
                        request_id,
                    ),
                    request_id,
                )
                return
            if parsed.path == "/v1/metric-materializations/backfill":
                principal = self._principal()
                body = self._body_fields(
                    required={"limit"}, allowed={"limit", "cursor"}
                )
                self._json(
                    200,
                    self.app.metric_observations.backfill(
                        principal,
                        limit=body["limit"],
                        cursor=body.get("cursor"),
                        request_id=request_id,
                    ),
                    request_id,
                )
                return
            principal = self._principal()
            if parsed.path == "/v1/daily-ops-schedules":
                body = self._body_fields(
                    required={
                        "name", "platform", "objective", "timezone_name", "local_time",
                        "graph_version_id", "evidence_selectors",
                    },
                    allowed={
                        "name", "platform", "objective", "timezone_name", "local_time",
                        "graph_version_id", "evidence_selectors", "max_source_age_hours", "enabled",
                    },
                )
                self._json(
                    201,
                    self.app.daily_ops.create(
                        principal,
                        name=body["name"],
                        platform=body["platform"],
                        objective=body["objective"],
                        timezone_name=body["timezone_name"],
                        local_time=body["local_time"],
                        graph_version_id=body["graph_version_id"],
                        evidence_selectors=body["evidence_selectors"],
                        max_source_age_hours=body.get("max_source_age_hours", 48),
                        enabled=body.get("enabled", True),
                        request_id=request_id,
                    ),
                    request_id,
                )
            elif parsed.path.startswith("/v1/daily-ops-schedules/") and parsed.path.endswith("/trigger") and len(parsed.path.split("/")) == 5:
                body = self._body_fields(required=set(), allowed={"local_date"})
                idempotency_key = self.headers.get("Idempotency-Key", "")
                if not idempotency_key:
                    raise ValidationError("Idempotency-Key header is required")
                schedule_id = parsed.path.split("/")[3]
                self._json(
                    200,
                    self.app.daily_ops.trigger(
                        principal,
                        schedule_id,
                        request_id,
                        local_date=body.get("local_date"),
                    ),
                    request_id,
                )
            elif parsed.path.startswith("/v1/daily-ops-runs/") and parsed.path.endswith("/execute") and len(parsed.path.split("/")) == 5:
                self._body_fields(required=set(), allowed=set())
                run_id = parsed.path.split("/")[3]
                self._json(
                    200, self.app.daily_ops.execute(principal, run_id, request_id), request_id
                )
            elif parsed.path.startswith("/v1/daily-ops-runs/") and parsed.path.endswith("/retry") and len(parsed.path.split("/")) == 5:
                self._body_fields(required=set(), allowed=set())
                idempotency_key = self.headers.get("Idempotency-Key", "")
                if not idempotency_key:
                    raise ValidationError("Idempotency-Key header is required")
                run_id = parsed.path.split("/")[3]
                self._json(
                    200, self.app.daily_ops.retry(principal, run_id, request_id), request_id
                )
            elif parsed.path == "/v1/agent-graphs":
                body = self._body_fields(required={"name", "definition"})
                self._json(
                    201,
                    self.app.agent_graphs.create(
                        principal, body["name"], body["definition"], request_id
                    ),
                    request_id,
                )
            elif parsed.path.startswith("/v1/agent-graphs/") and parsed.path.endswith("/versions") and len(parsed.path.split("/")) == 5:
                graph_id = parsed.path.split("/")[3]
                body = self._body_fields(required={"definition"})
                self._json(
                    201,
                    self.app.agent_graphs.create_version(
                        principal, graph_id, body["definition"], request_id
                    ),
                    request_id,
                )
            elif parsed.path.startswith("/v1/agent-graphs/") and parsed.path.endswith("/publish") and len(parsed.path.split("/")) == 7 and parsed.path.split("/")[4] == "versions":
                parts = parsed.path.split("/")
                self._body_fields(required=set(), allowed=set())
                self._json(
                    200,
                    self.app.agent_graphs.publish(
                        principal, parts[3], parts[5], request_id
                    ),
                    request_id,
                )
            elif parsed.path.startswith("/v1/agent-graph-versions/") and parsed.path.endswith("/publish") and len(parsed.path.split("/")) == 5:
                version_id = parsed.path.split("/")[3]
                self._body_fields(required=set(), allowed=set())
                version = self.app.agent_graphs.get_version(principal, version_id)
                self._json(
                    200,
                    self.app.agent_graphs.publish(
                        principal, version["graph_id"], version_id, request_id
                    ),
                    request_id,
                )
            elif parsed.path == "/v1/actions":
                body = self._body()
                result = self.app.actions.request(principal, str(body.get("operation", "")), body.get("payload", {}), self.headers.get("Idempotency-Key", ""), request_id)
                self._json(200, result, request_id)
            elif parsed.path == "/v1/proposals":
                body = self._body_fields(
                    required={
                        "daily_ops_run_id", "priority_rank", "operation", "payload",
                        "risk", "rollback_plan", "expires_at",
                    },
                    allowed={
                        "daily_ops_run_id", "priority_rank", "operation", "payload",
                        "risk", "rollback_plan", "expires_at",
                    },
                )
                self._json(
                    201,
                    self.app.proposals.create(
                        principal,
                        daily_ops_run_id=body["daily_ops_run_id"],
                        priority_rank=body["priority_rank"],
                        operation=body["operation"],
                        payload=body["payload"],
                        risk=body["risk"],
                        rollback_plan=body["rollback_plan"],
                        idempotency_key=self.headers.get("Idempotency-Key", ""),
                        expires_at=body["expires_at"],
                        request_id=request_id,
                    ),
                    request_id,
                )
            elif parsed.path.startswith("/v1/proposals/") and parsed.path.endswith("/submit") and len(parsed.path.split("/")) == 5:
                proposal_id = parsed.path.split("/")[3]
                body = self._body_fields(required={"expected_version"}, allowed={"expected_version"})
                self._json(200, self.app.proposals.submit(principal, proposal_id, request_id=request_id, **body), request_id)
            elif parsed.path.startswith("/v1/proposals/") and parsed.path.endswith("/decisions") and len(parsed.path.split("/")) == 5:
                proposal_id = parsed.path.split("/")[3]
                body = self._body_fields(
                    required={"expected_version", "decision", "comment"},
                    allowed={"expected_version", "decision", "comment"},
                )
                self._json(200, self.app.proposals.decide(principal, proposal_id, request_id=request_id, **body), request_id)
            elif parsed.path.startswith("/v1/proposals/") and parsed.path.endswith("/execute") and len(parsed.path.split("/")) == 5:
                proposal_id = parsed.path.split("/")[3]
                body = self._body_fields(required={"expected_version"}, allowed={"expected_version"})
                self._json(
                    201,
                    self.app.proposals.execute(
                        principal, proposal_id, idempotency_key=self.headers.get("Idempotency-Key", ""),
                        request_id=request_id, **body,
                    ),
                    request_id,
                )
            elif parsed.path.startswith("/v1/proposals/") and parsed.path.endswith("/retry") and len(parsed.path.split("/")) == 5:
                proposal_id = parsed.path.split("/")[3]
                body = self._body_fields(required={"expected_version"}, allowed={"expected_version"})
                self._json(
                    201,
                    self.app.proposals.retry(
                        principal, proposal_id, idempotency_key=self.headers.get("Idempotency-Key", ""),
                        request_id=request_id, **body,
                    ),
                    request_id,
                )
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
                    allowed={
                        "workflow", "objective", "evidence", "evidence_import_ids",
                        "graph_version_id", "metric_observation_ids",
                    },
                )
                run = self.app.agent_runs.request(
                    principal,
                    str(body["workflow"]),
                    body["objective"],
                    body.get("evidence"),
                    self.headers.get("Idempotency-Key", ""),
                    request_id,
                    evidence_import_ids=body.get("evidence_import_ids"),
                    graph_version_id=body.get("graph_version_id"),
                    metric_observation_ids=body.get("metric_observation_ids"),
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
            if parsed.path.startswith("/v1/proposals/") and len(parsed.path.split("/")) == 4:
                proposal_id = parsed.path.split("/")[3]
                body = self._body_fields(
                    required={"expected_version"},
                    allowed={
                        "expected_version", "title", "rationale", "expected_impact",
                        "rollback_plan", "operation", "payload", "risk", "expires_at",
                    },
                )
                self._json(
                    200,
                    self.app.proposals.revise(
                        principal, proposal_id, request_id=request_id, **body
                    ),
                    request_id,
                )
            elif parsed.path.startswith("/v1/users/") and len(parsed.path.split("/")) == 4:
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
            elif parsed.path.startswith("/v1/daily-ops-schedules/") and len(parsed.path.split("/")) == 4:
                schedule_id = parsed.path.split("/")[3]
                body = self._body_fields(
                    required={
                        "name", "platform", "objective", "timezone_name", "local_time",
                        "graph_version_id", "evidence_selectors", "max_source_age_hours", "enabled",
                    },
                    allowed={
                        "name", "platform", "objective", "timezone_name", "local_time",
                        "graph_version_id", "evidence_selectors", "max_source_age_hours", "enabled",
                    },
                )
                self._json(
                    200,
                    self.app.daily_ops.update(
                        principal,
                        schedule_id,
                        name=body["name"],
                        platform=body["platform"],
                        objective=body["objective"],
                        timezone_name=body["timezone_name"],
                        local_time=body["local_time"],
                        graph_version_id=body["graph_version_id"],
                        evidence_selectors=body["evidence_selectors"],
                        max_source_age_hours=body["max_source_age_hours"],
                        enabled=body["enabled"],
                        request_id=request_id,
                    ),
                    request_id,
                )
            else:
                raise NotFoundError("route not found")
        except Exception as exc:
            self._error(exc, request_id)

    def log_message(self, fmt: str, *args: Any) -> None:
        # BaseHTTPRequestHandler's default format includes the full request
        # target. Never place query values (including rejected credentials) in
        # access logs.
        request_path = urlparse(getattr(self, "path", "")).path or "/"
        status = args[1] if len(args) > 1 else "unknown"
        log.info(
            "http method=%s path=%s status=%s",
            getattr(self, "command", "unknown"),
            request_path,
            status,
        )


def build_server(
    app: RuntimeApplication,
    host: str = "127.0.0.1",
    port: int = 8787,
    *,
    allow_public: bool = False,
) -> ThreadingHTTPServer:
    RuntimeApplication._validate_bind_host(host, allow_public)
    httpd = ThreadingHTTPServer((host, port), _Handler)
    httpd.app = app  # type: ignore[attr-defined]
    return httpd


def serve(
    app: RuntimeApplication,
    host: str = "127.0.0.1",
    port: int = 8787,
    *,
    allow_public: bool = False,
    stop_event: threading.Event | None = None,
    httpd: ThreadingHTTPServer | None = None,
) -> None:
    RuntimeApplication._validate_bind_host(host, allow_public)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        root.addHandler(handler)
    if allow_public:
        log.warning("public bind explicitly enabled; terminate TLS and add an authenticated reverse proxy")
    httpd = httpd or build_server(
        app, host, port, allow_public=allow_public
    )
    if stop_event is not None:
        def stop_server() -> None:
            stop_event.wait()
            httpd.shutdown()

        threading.Thread(
            target=stop_server,
            name="pilot-http-shutdown",
            daemon=True,
        ).start()
    log.info("runtime API listening on http://%s:%d", host, port)
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
