"""Installed command-line entry point."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

from .runtime.api import RuntimeApplication, serve
from .runtime.storage import Database


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
    serve(app, args.host, args.port, allow_public=args.allow_public)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
