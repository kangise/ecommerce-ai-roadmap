"""Installed command-line entry point."""

from __future__ import annotations

import argparse
import importlib.util
import json
import signal
import sys
import threading
import time
from pathlib import Path

from .runtime.api import RuntimeApplication, build_server, serve
from .runtime.storage import Database


def _run_pilot(args: argparse.Namespace) -> int:
    from .runtime.pilot import PilotService, PilotSupervisor

    db_path = Path(args.db).expanduser().resolve()
    if args.check:
        result = PilotService.check_path(db_path)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
        return 0 if result["status"] == "ready" else 1
    if not isinstance(args.port, int) or isinstance(args.port, bool) or not 1 <= args.port <= 65535:
        print(
            json.dumps({
                "status": "blocked",
                "blockers": [{"code": "PORT_INVALID", "component": "http"}],
            }, sort_keys=True),
            flush=True,
        )
        return 2
    try:
        RuntimeApplication._validate_bind_host(args.host, args.allow_public)
    except Exception as exc:
        print(
            json.dumps({
                "status": "blocked",
                "error_type": type(exc).__name__,
                "blockers": [{"code": "BIND_HOST_INVALID", "component": "http"}],
            }, sort_keys=True),
            flush=True,
        )
        return 2
    if bool(args.name) != bool(args.email):
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "blockers": [{
                        "code": "BOOTSTRAP_NAME_EMAIL_REQUIRED",
                        "component": "tenant",
                    }],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 2
    if args.name and (
        not args.name.strip() or len(args.name.strip()) > 200
        or not args.email.strip() or len(args.email.strip()) > 320
        or "@" not in args.email
    ):
        print(
            json.dumps({
                "status": "blocked",
                "blockers": [{
                    "code": "BOOTSTRAP_IDENTITY_INVALID", "component": "tenant"
                }],
            }, sort_keys=True),
            flush=True,
        )
        return 2
    if not db_path.exists() and not (args.name and args.email):
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "blockers": [{
                        "code": "DATABASE_MISSING_BOOTSTRAP_REQUIRED",
                        "component": "tenant",
                    }],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 2

    try:
        app = RuntimeApplication(Database(db_path))
    except Exception as exc:
        print(
            json.dumps({
                "status": "blocked",
                "error_type": type(exc).__name__,
                "blockers": [{"code": "DATABASE_OPEN_FAILED", "component": "schema"}],
            }, sort_keys=True),
            flush=True,
        )
        return 2
    tenants = app.db.list_tenants()
    bootstrap: dict[str, str] | None = None
    if not tenants:
        if not (args.name and args.email):
            print(
                json.dumps(
                    {
                        "status": "blocked",
                        "blockers": [{
                            "code": "TENANT_MISSING_BOOTSTRAP_REQUIRED",
                            "component": "tenant",
                        }],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            return 2
    try:
        httpd = build_server(
            app, args.host, args.port, allow_public=args.allow_public
        )
    except OSError as exc:
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "error_type": type(exc).__name__,
                    "blockers": [{"code": "PILOT_BIND_FAILED", "component": "http"}],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 2
    pilot_phase = "bootstrap" if not tenants else "preflight"
    try:
        if not tenants:
            bootstrap = app.bootstrap(args.name, args.email)
            pilot_phase = "preflight"
        preflight = app.pilot.check_all()
    except Exception as exc:
        httpd.server_close()
        result: dict[str, object] = {
            "status": "blocked",
            "error_type": type(exc).__name__,
            "blockers": [{
                "code": (
                    "PILOT_PREFLIGHT_FAILED" if pilot_phase == "preflight"
                    else "PILOT_BOOTSTRAP_FAILED"
                ),
                "component": "tenant",
            }],
        }
        if bootstrap is not None:
            result["bootstrap"] = bootstrap
        print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
        return 2
    stop_event = threading.Event()
    supervisor = PilotSupervisor(app, stop_event=stop_event)
    previous_handlers: dict[int, object] = {}

    def request_stop(signum, frame) -> None:
        stop_event.set()

    for signum in (signal.SIGINT, signal.SIGTERM):
        previous_handlers[signum] = signal.getsignal(signum)
        signal.signal(signum, request_stop)
    try:
        boot = supervisor.start()
    except Exception as exc:
        httpd.server_close()
        for signum, previous in previous_handlers.items():
            signal.signal(signum, previous)
        result: dict[str, object] = {
            "status": "blocked",
            "error_type": type(exc).__name__,
            "blockers": [{"code": "PILOT_START_FAILED", "component": "pilot_runtime"}],
        }
        if bootstrap is not None:
            result["bootstrap"] = bootstrap
        print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
        return 2

    launch: dict[str, object] = {
        "status": "starting",
        "url": f"http://{args.host}:{args.port}",
        "boot_id": boot["boot_id"],
        "preflight": preflight,
    }
    if bootstrap is not None:
        launch["bootstrap"] = bootstrap
    print(json.dumps(launch, ensure_ascii=False, sort_keys=True), flush=True)

    shutdown_clean = True
    serve_error: Exception | None = None
    stop_reason = "graceful_shutdown"
    try:
        serve(
            app,
            args.host,
            args.port,
            allow_public=args.allow_public,
            stop_event=stop_event,
            httpd=httpd,
        )
    except KeyboardInterrupt:
        stop_event.set()
    except Exception as exc:
        serve_error = exc
        stop_reason = "startup_failure"
        stop_event.set()
    finally:
        stop_event.set()
        shutdown_clean = supervisor.stop(reason=stop_reason)
        for signum, previous in previous_handlers.items():
            signal.signal(signum, previous)
    if serve_error is not None:
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "error_type": type(serve_error).__name__,
                    "blockers": [{
                        "code": "PILOT_SERVER_FAILED", "component": "http"
                    }],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 2
    if not shutdown_clean:
        print(
            json.dumps(
                {
                    "status": "degraded",
                    "error_type": "ShutdownTimeout",
                    "boot_id": supervisor.boot_id,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 3
    return 0


def _package_data() -> Path:
    candidate = Path(__file__).resolve().parent / "package_data"
    if (candidate / "dist").is_dir():
        return candidate
    return Path.cwd()


def _load_mcp_module():
    path = _package_data() / "dist" / "integration" / "mcp-server.py"
    if not path.is_file():
        path = Path.cwd() / "integration" / "mcp-server.py"
    spec = importlib.util.spec_from_file_location("ecommerce_ai_skills._mcp_server", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load MCP adapter from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(prog="opc-ecommerce")
    sub = parser.add_subparsers(dest="command", required=True)
    mcp = sub.add_parser("mcp", help="run or validate the read-only MCP knowledge adapter")
    mcp.add_argument("--dist", default=None)
    mcp.add_argument("--cli", action="store_true")
    mcp.add_argument("--validate", action="store_true")
    init = sub.add_parser("init", help="create a tenant and print a one-time API key")
    init.add_argument("--db", required=True)
    init.add_argument("--name", required=True)
    init.add_argument("--email", required=True)
    demo_seed = sub.add_parser(
        "demo-seed",
        help="create a new isolated Demo database with clearly marked sample data",
    )
    demo_seed.add_argument(
        "--db", required=True, help="must be a new database path"
    )
    demo = sub.add_parser(
        "demo",
        help="serve an isolated Demo database with automatic loopback-only UI access",
        description="Serve an isolated Demo database with automatic loopback-only UI access.",
    )
    demo.add_argument("--db", required=True)
    demo.add_argument("--port", type=int, default=8788)
    api = sub.add_parser("api", help="serve the authenticated runtime API")
    api.add_argument("--db", required=True)
    api.add_argument("--host", default="127.0.0.1")
    api.add_argument("--port", type=int, default=8787)
    api.add_argument("--allow-public", action="store_true", help="allow non-loopback bind; use only behind TLS/authenticated proxy")
    worker = sub.add_parser("worker", help="execute durable queued jobs")
    worker.add_argument("--db", required=True)
    worker.add_argument("--once", action="store_true")
    worker.add_argument("--poll-seconds", type=float, default=5.0)
    scheduler = sub.add_parser("scheduler", help="materialize due schedules into jobs")
    scheduler.add_argument("--db", required=True)
    scheduler.add_argument("--once", action="store_true")
    scheduler.add_argument("--poll-seconds", type=float, default=15.0)
    report_worker = sub.add_parser(
        "report-worker", help="execute durable Amazon report sync transitions"
    )
    report_worker.add_argument("--db", required=True)
    report_worker.add_argument("--once", action="store_true")
    report_worker.add_argument("--poll-seconds", type=float, default=15.0)
    daily_scheduler = sub.add_parser(
        "daily-scheduler", help="materialize due calendar-day Daily Ops occurrences"
    )
    daily_scheduler.add_argument("--db", required=True)
    daily_scheduler.add_argument("--once", action="store_true")
    daily_scheduler.add_argument("--poll-seconds", type=float, default=15.0)
    daily_worker = sub.add_parser(
        "daily-worker", help="execute due durable Daily Ops occurrences"
    )
    daily_worker.add_argument("--db", required=True)
    daily_worker.add_argument("--once", action="store_true")
    daily_worker.add_argument("--poll-seconds", type=float, default=5.0)
    proposal_worker = sub.add_parser(
        "proposal-worker", help="expire proposals and recover durable proposal executions"
    )
    proposal_worker.add_argument("--db", required=True)
    proposal_worker.add_argument("--once", action="store_true")
    proposal_worker.add_argument("--poll-seconds", type=float, default=5.0)
    pilot = sub.add_parser(
        "pilot", help="run the production API and all durable Pilot workers"
    )
    pilot.add_argument("--db", required=True)
    pilot.add_argument("--host", default="127.0.0.1")
    pilot.add_argument("--port", type=int, default=8787)
    pilot.add_argument("--name")
    pilot.add_argument("--email")
    pilot.add_argument("--allow-public", action="store_true")
    pilot.add_argument(
        "--check", action="store_true", help="read-only readiness check; do not start"
    )
    backup = sub.add_parser("backup",help="create a verified runtime backup")
    backup.add_argument("--db",required=True); backup.add_argument("--output",required=True)
    restore = sub.add_parser("restore",help="verify or restore a runtime backup")
    restore.add_argument("--backup",required=True); restore.add_argument("--db",required=True)
    restore.add_argument("--verify-only",action="store_true")
    args = parser.parse_args()
    if args.command == "mcp":
        module = _load_mcp_module()
        dist = Path(args.dist).resolve() if args.dist else _package_data() / "dist"
        argv = ["opc-ecommerce", "--dist", str(dist)]
        if args.cli: argv.append("--cli")
        if args.validate: argv.append("--validate")
        old = sys.argv; sys.argv = argv
        try: return int(module.main())
        finally: sys.argv = old
    if args.command == "demo-seed":
        from .demo_seed import seed_demo_database

        print(json.dumps(seed_demo_database(args.db), ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "demo":
        from .demo_seed import open_demo_runtime

        app = open_demo_runtime(args.db)
        print(
            json.dumps(
                {
                    "url": f"http://127.0.0.1:{args.port}/app",
                    "tenant_mode": "demo",
                    "warning": "DEMO DATA ONLY",
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            flush=True,
        )
        try:
            serve(app, "127.0.0.1", args.port)
        except KeyboardInterrupt:
            pass
        finally:
            if app.demo_key_id and app.demo_session:
                app.db.revoke_api_key(
                    app.demo_session["tenant_id"], app.demo_key_id
                )
        return 0
    if args.command == "pilot":
        return _run_pilot(args)
    if args.command in {"backup","restore"}:
        from .runtime.recovery import RecoveryService
        try:
            result=(RecoveryService.backup(args.db,args.output) if args.command=="backup"
                    else RecoveryService.restore(args.backup,args.db,verify_only=args.verify_only))
            safe=({"status":"succeeded","backup_id":result["backup_id"],"schema_version":result["schema_version"],"evidence_object_count":len(result["evidence_objects"])}
                  if args.command=="backup" else {key:value for key,value in result.items() if key not in {"database","tenant_ids","manifest"}})
            print(json.dumps(safe,ensure_ascii=False,sort_keys=True),flush=True); return 0
        except Exception as exc:
            print(json.dumps({"status":"failed","error_code":("BACKUP_FAILED" if args.command=="backup" else "RESTORE_FAILED"),"error_type":type(exc).__name__},sort_keys=True),flush=True)
            return 2
    app = RuntimeApplication(Database(args.db))
    if args.command == "init":
        print(app.bootstrap(args.name, args.email))
        return 0
    if args.command == "worker":
        if args.poll_seconds < 0.25 or args.poll_seconds > 300:
            raise ValueError("poll-seconds must be between 0.25 and 300")
        while True:
            result = app.jobs.run_once()
            if result is not None:
                print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            if args.once:
                return 0
            if result is None:
                time.sleep(args.poll_seconds)
    if args.command == "scheduler":
        if args.poll_seconds < 0.25 or args.poll_seconds > 300:
            raise ValueError("poll-seconds must be between 0.25 and 300")
        while True:
            result = app.schedules.tick_once()
            if result is not None:
                print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            if args.once:
                return 0
            if result is None:
                time.sleep(args.poll_seconds)
    if args.command == "report-worker":
        if args.poll_seconds < 0.25 or args.poll_seconds > 300:
            raise ValueError("poll-seconds must be between 0.25 and 300")
        while True:
            result = app.report_syncs.run_once()
            if result is not None:
                print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            if args.once:
                return 0
            if result is None:
                time.sleep(args.poll_seconds)
    if args.command == "daily-scheduler":
        if args.poll_seconds < 0.25 or args.poll_seconds > 300:
            raise ValueError("poll-seconds must be between 0.25 and 300")
        while True:
            result = app.daily_ops.scheduler_run_once()
            if result is not None:
                print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            if args.once:
                return 0
            if result is None:
                time.sleep(args.poll_seconds)
    if args.command == "daily-worker":
        if args.poll_seconds < 0.25 or args.poll_seconds > 300:
            raise ValueError("poll-seconds must be between 0.25 and 300")
        while True:
            result = app.daily_ops.worker_run_once()
            if result is not None:
                print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            if args.once:
                return 0
            if result is None:
                time.sleep(args.poll_seconds)
    if args.command == "proposal-worker":
        if args.poll_seconds < 0.25 or args.poll_seconds > 300:
            raise ValueError("poll-seconds must be between 0.25 and 300")
        while True:
            result = app.proposals.worker_run_once()
            if result["execution"] is not None or result["expired"]:
                print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            if args.once:
                return 0
            if result["execution"] is None and not result["expired"]:
                time.sleep(args.poll_seconds)
    serve(app, args.host, args.port, allow_public=args.allow_public)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
