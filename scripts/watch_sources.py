#!/usr/bin/env python3
"""Watch upstream API specs for changes that would invalidate this repo.

Usage:
  python3 scripts/watch_sources.py              # report drift against the stored state
  python3 scripts/watch_sources.py --update     # fetch, report, and record the new state
  python3 scripts/watch_sources.py --list       # show the watchlist without any network
  python3 scripts/watch_sources.py --json

What this does and does not cover
---------------------------------
`fact-review-plan.yaml` schedules humans to re-verify platform *rules* on a clock.
That is the right mechanism for policy, because policy lives on pages that cannot
be fetched: Amazon Seller Central help redirects to login, Shopify's help centre
answers 403 to automated requests, and OpenAI's docs render client-side. A hash
watcher pointed at those URLs would never fire and would quietly imply coverage
that does not exist.

This watches the other half — the machine-readable API surface the runtime is
written against, where a change is both detectable and actionable. When the SP-API
models repo moves, someone should look at the Amazon connector.

It reports; it does not judge. An upstream commit is not automatically a problem,
so this never fails a build unless you ask it to with --fail-on-change.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WATCHLIST = ROOT / "maintenance" / "source-watch.yaml"
STATE = ROOT / "maintenance" / "source-watch-state.json"
TIMEOUT = 20


def load_watchlist() -> dict:
    if not WATCHLIST.exists():
        sys.exit(f"{WATCHLIST.relative_to(ROOT)} missing")
    return yaml.safe_load(WATCHLIST.read_text(encoding="utf-8")) or {}


def load_state() -> dict:
    if not STATE.exists():
        return {}
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _request(url: str, user_agent: str, accept: str) -> bytes:
    headers = {"User-Agent": user_agent, "Accept": accept}
    # A token only raises the rate limit; the watchlist is public data either way.
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read()


def probe(source: dict, user_agent: str) -> tuple[dict | None, str | None]:
    """Return (fingerprint, error). A fingerprint is whatever identifies 'current'."""
    kind = source.get("kind")
    try:
        if kind == "github":
            repo = source["repo"]
            url = f"https://api.github.com/repos/{repo}/commits?per_page=1"
            if source.get("path"):
                url += f"&path={source['path']}"
            payload = json.loads(_request(url, user_agent, "application/vnd.github+json"))
            if not isinstance(payload, list) or not payload:
                return None, f"{repo}: no commits returned (repo renamed or private?)"
            head = payload[0]
            return {
                "revision": head["sha"],
                "at": head["commit"]["committer"]["date"],
                "url": head.get("html_url", f"https://github.com/{repo}"),
            }, None

        if kind == "http":
            import hashlib
            body = _request(source["url"], user_agent, "*/*")
            return {
                "revision": hashlib.sha256(body).hexdigest(),
                "at": None,
                "url": source["url"],
            }, None

        return None, f"unknown kind {kind!r}"
    except urllib.error.HTTPError as exc:
        hint = " (rate limited — set GITHUB_TOKEN)" if exc.code in (403, 429) else ""
        return None, f"HTTP {exc.code}{hint}"
    except urllib.error.URLError as exc:
        # A local trust-store problem is not an upstream outage, and reporting it
        # as "unreachable" sends the reader to check the wrong thing. Common on
        # macOS python.org installs, where no CA bundle is wired up.
        if "CERTIFICATE_VERIFY_FAILED" in str(exc.reason):
            return None, ("TLS trust store not configured locally — this is a "
                          "client problem, not an upstream one. Try: "
                          "pip install certifi && export "
                          "SSL_CERT_FILE=$(python3 -m certifi)")
        return None, f"unreachable: {exc.reason}"
    except (TimeoutError, KeyError, json.JSONDecodeError) as exc:
        return None, f"probe failed: {exc}"


def affected_lines(source: dict) -> list[str]:
    affects = source.get("affects") or {}
    out = []
    prefixes = affects.get("constraint_prefixes") or []
    if prefixes:
        out.append("constraints: " + ", ".join(f"{p}.*" for p in prefixes))
    for key, label in (("code", "code"), ("chapters", "chapters")):
        for item in affects.get(key) or []:
            out.append(f"{label}: {item}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Watch upstream API specs")
    ap.add_argument("--update", action="store_true", help="record the fetched state")
    ap.add_argument("--list", action="store_true", dest="just_list",
                    help="print the watchlist without touching the network")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--fail-on-change", action="store_true",
                    help="exit 1 when an upstream moved (off by default)")
    args = ap.parse_args()

    watchlist = load_watchlist()
    sources = watchlist.get("sources") or []
    user_agent = (watchlist.get("policy") or {}).get("user_agent", "opc-source-watch")
    state = load_state()

    if args.just_list:
        for s in sources:
            print(f"  {s['id']:<24} {s.get('kind'):<8} {s.get('repo') or s.get('url')}")
            for line in affected_lines(s):
                print(f"      {line}")
        return 0

    results, changed, errors = [], [], []
    for source in sources:
        sid = source["id"]
        fingerprint, error = probe(source, user_agent)
        previous = state.get(sid) or {}
        if error:
            errors.append((sid, error))
            results.append({"id": sid, "status": "error", "detail": error})
            continue
        if not previous:
            status = "new"
        elif previous.get("revision") != fingerprint["revision"]:
            status = "changed"
            changed.append((source, previous, fingerprint))
        else:
            status = "unchanged"
        results.append({"id": sid, "status": status,
                        "previous": previous.get("revision"), **fingerprint})
        state[sid] = {**fingerprint, "checked_at": datetime.datetime.now(
            datetime.timezone.utc).isoformat(timespec="seconds")}

    if args.as_json:
        print(json.dumps({"results": results}, indent=2))
    else:
        print(f"  upstream watch — {datetime.date.today():%Y-%m-%d}")
        print()
        for r in results:
            mark = {"changed": "->", "error": "!!", "new": "..", "unchanged": "  "}[r["status"]]
            rev = (r.get("revision") or "")[:10]
            print(f"{mark} {r['id']:<24} {r['status']:<10} {rev}  {r.get('at') or ''}")
            if r["status"] == "error":
                print(f"      {r['detail']}")

        for source, previous, current in changed:
            print()
            print(f"  {source['id']} moved "
                  f"{(previous.get('revision') or '?')[:10]} -> {current['revision'][:10]}")
            print(f"    {current['url']}")
            why = " ".join((source.get("why") or "").split())
            if why:
                print(f"    why it matters: {why}")
            for line in affected_lines(source):
                print(f"    review {line}")

        print()
        if changed:
            print(f"  {len(changed)} upstream(s) moved. An upstream commit is not by itself"
                  " a problem — check whether it touches what is listed above.")
        elif not errors:
            print("  no upstream moved since the last recorded state")
        if errors:
            print(f"  {len(errors)} source(s) could not be probed; state left unchanged for them")

    if args.update:
        STATE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"  state written to {STATE.relative_to(ROOT)}")

    return 1 if (changed and args.fail_on_change) else 0


if __name__ == "__main__":
    sys.exit(main())
