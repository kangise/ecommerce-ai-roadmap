#!/usr/bin/env python3
"""Fact review queue — what needs re-verifying, and when.

Usage:
  python3 scripts/fact_review.py                  # the whole queue
  python3 scripts/fact_review.py --batch amazon-and-commerce
  python3 scripts/fact_review.py --due-within 90  # exit 1 if anything lands inside the window
  python3 scripts/fact_review.py --cliff          # expiry-cliff report only
  python3 scripts/fact_review.py --json           # machine-readable

Why this exists
---------------
`M7` in verify_content.py already enforces the *discipline*: every dated fact
maps to exactly one review batch, and each batch is due before its facts hit the
18-month shelf life. But M7 only speaks up in a failure state — a batch already
overdue, or a fact already expired. Between those two cliffs it is silent, so a
maintainer has no way to ask "what should I be reviewing this quarter?" without
reading the YAML and doing date arithmetic by hand.

This script answers that question, and reports one thing M7 structurally cannot:
the *expiry cliff*. Facts stamped in the same month expire in the same month, so
a bulk re-verification pass quietly schedules its own repeat. Staggering is a
judgment call for a maintainer, but they have to be able to see it first.

This is a report, not a gate — it exits non-zero only with --due-within, so CI
can use it as a scheduled reminder without turning a future date into a red build.
"""

from __future__ import annotations

import argparse
import collections
import datetime
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PLAN_PATH = ROOT / "maintenance" / "fact-review-plan.yaml"
CONSTRAINTS_PATH = ROOT / "ontology" / "constraints.yaml"
SRC = ROOT / "src"

CLAIMS_PATTERN = re.compile(r"<!--\s*claims:\s*verified\s+(\d{4}-\d{2})\s*-->")

# Kept in step with verify_content.py's M7 gate. If that shelf life moves, this
# report is describing a different deadline than the gate enforces.
SHELF_LIFE_MONTHS = 18


def add_months(date: datetime.date, months: int) -> datetime.date:
    month_index = date.year * 12 + date.month - 1 + months
    year, month_zero = divmod(month_index, 12)
    return datetime.date(year, month_zero + 1, 1)


def month_date(value: str) -> datetime.date | None:
    try:
        return datetime.date.fromisoformat(str(value) + "-01")
    except (ValueError, TypeError):
        return None


def load_plan() -> dict:
    if not PLAN_PATH.exists():
        sys.exit("maintenance/fact-review-plan.yaml missing")
    return yaml.safe_load(PLAN_PATH.read_text(encoding="utf-8")) or {}


def collect_facts() -> tuple[list[dict], list[dict]]:
    """Return (constraints, content_claims), each carrying its verified month."""
    constraints = []
    if CONSTRAINTS_PATH.exists():
        raw = yaml.safe_load(CONSTRAINTS_PATH.read_text(encoding="utf-8")) or []
        for c in raw:
            if not isinstance(c, dict) or not c.get("verified"):
                continue
            verified = month_date(c["verified"])
            if verified is None:
                continue
            cid = str(c.get("id", ""))
            constraints.append({
                "id": cid,
                "prefix": cid.split(".", 1)[0],
                "verified": verified,
                "verified_str": str(c["verified"]),
            })

    claims = []
    for md in sorted(SRC.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        for m in CLAIMS_PATTERN.finditer(text):
            verified = month_date(m.group(1))
            if verified is None:
                continue
            claims.append({
                "path": f"src/{md.relative_to(SRC)}",
                "line": text[:m.start()].count("\n") + 1,
                "verified": verified,
                "verified_str": m.group(1),
            })
    return constraints, claims


def assign(plan: dict, constraints: list[dict], claims: list[dict]) -> list[dict]:
    """Group facts under the batch that owns them, mirroring M7's matching."""
    batches = []
    for batch in plan.get("batches", []):
        if not isinstance(batch, dict):
            continue
        due = month_date(batch.get("due", ""))
        prefixes = batch.get("constraint_prefixes") or []
        paths = batch.get("content_path_prefixes") or []

        owned_constraints = [c for c in constraints if c["prefix"] in prefixes]
        owned_claims = [
            c for c in claims
            if any(c["path"] == p or c["path"].startswith(p.rstrip("/") + "/") for p in paths)
        ]
        batches.append({
            "id": batch.get("id", "?"),
            "owner": batch.get("owner", "?"),
            "due": due,
            "due_str": str(batch.get("due", "?")),
            "constraints": owned_constraints,
            "claims": owned_claims,
        })
    batches.sort(key=lambda b: (b["due"] or datetime.date.max))
    return batches


def deadline_of(batch: dict, lead_months: int) -> datetime.date | None:
    """Earliest date a fact in this batch goes stale, minus the review lead time.

    M7 checks the same quantity per constraint; here it is aggregated so a
    maintainer sees how much slack the batch as a whole actually has.
    """
    facts = batch["constraints"] + batch["claims"]
    if not facts:
        return None
    earliest = min(f["verified"] for f in facts)
    return add_months(earliest, SHELF_LIFE_MONTHS - lead_months)


def cliff_report(constraints: list[dict], claims: list[dict]) -> list[tuple[str, int]]:
    """How many dated facts share each verified month."""
    counter = collections.Counter()
    for f in constraints + claims:
        counter[f["verified_str"]] += 1
    return sorted(counter.items())


def main() -> int:
    ap = argparse.ArgumentParser(description="Fact review queue")
    ap.add_argument("--batch", help="show one batch by id")
    ap.add_argument("--due-within", type=int, metavar="DAYS",
                    help="exit 1 if any batch is due inside this many days")
    ap.add_argument("--cliff", action="store_true", help="expiry-cliff report only")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--list", action="store_true", help="list every fact per batch")
    args = ap.parse_args()

    today = datetime.date.today()
    plan = load_plan()
    lead_months = plan.get("policy", {}).get("review_lead_months", 0) or 0
    constraints, claims = collect_facts()
    batches = assign(plan, constraints, claims)
    cliff = cliff_report(constraints, claims)

    if args.batch:
        batches = [b for b in batches if b["id"] == args.batch]
        if not batches:
            sys.exit(f"no batch with id {args.batch!r}")

    if args.as_json:
        print(json.dumps({
            "today": today.isoformat(),
            "shelf_life_months": SHELF_LIFE_MONTHS,
            "review_lead_months": lead_months,
            "batches": [{
                "id": b["id"],
                "owner": b["owner"],
                "due": b["due_str"],
                "days_remaining": (b["due"] - today).days if b["due"] else None,
                "constraints": len(b["constraints"]),
                "content_claims": len(b["claims"]),
                "stale_deadline": (d.isoformat() if (d := deadline_of(b, lead_months)) else None),
            } for b in batches],
            "expiry_cliff": [{"month": m, "facts": n} for m, n in cliff],
        }, indent=2))
        return 0

    if args.cliff:
        print_cliff(cliff, len(constraints) + len(claims))
        return 0

    print(f"  fact review queue — {today:%Y-%m-%d}")
    print(f"  shelf life {SHELF_LIFE_MONTHS} months · review lead {lead_months} months")
    print()
    print(f"  {'batch':<28} {'due':<9} {'in':>7}  {'facts':>6}  {'slack':>6}  owner")
    print(f"  {'─' * 88}")

    soon = []
    tight = []
    for b in batches:
        days = (b["due"] - today).days if b["due"] else None
        n = len(b["constraints"]) + len(b["claims"])
        if days is None:
            when, flag = "?", "  "
        elif days < 0:
            when, flag = f"{-days}d ago", "!!"
            soon.append(b)
        else:
            when, flag = f"{days}d", "  "
            if args.due_within is not None and days <= args.due_within:
                soon.append(b)
                flag = "->"
        # Slack: months between the batch due date and the point its oldest fact
        # goes stale. M7 allows 0 (it compares with `>`), but 0 means the first
        # slipped month becomes a gate failure, so it is worth seeing.
        stale = deadline_of(b, lead_months)
        if stale and b["due"]:
            slack_months = (stale.year * 12 + stale.month) - (b["due"].year * 12 + b["due"].month)
            slack = f"{slack_months}mo" if slack_months else "none"
            if slack_months <= 0:
                tight.append(b)
        else:
            slack = "-"
        print(f"{flag} {b['id']:<28} {b['due_str']:<9} {when:>7}  {n:>6}  {slack:>6}  {b['owner']}")

        if args.list:
            for c in b["constraints"]:
                print(f"      constraint  {c['id']}  (verified {c['verified_str']})")
            for c in b["claims"]:
                print(f"      content     {c['path']}:{c['line']}  (verified {c['verified_str']})")

    unowned = (len(constraints) + len(claims)) - sum(
        len(b["constraints"]) + len(b["claims"]) for b in batches)
    print()
    print(f"  {len(constraints)} constraints · {len(claims)} content claims"
          + (f" · {unowned} unassigned" if unowned and not args.batch else ""))

    if tight:
        print()
        print(f"  {len(tight)} batch(es) scheduled with no slack — due the same month"
              " their oldest fact goes stale:")
        for b in tight:
            print(f"    - {b['id']} (due {b['due_str']}, owner {b['owner']})")
        print("    Legal under M7, but one slipped month turns each into a gate failure.")

    print()
    print_cliff(cliff, len(constraints) + len(claims))

    if args.due_within is not None:
        print()
        if soon:
            print(f"  {len(soon)} batch(es) due within {args.due_within} days:")
            for b in soon:
                print(f"    - {b['id']} ({b['due_str']}, owner {b['owner']})")
            return 1
        print(f"  nothing due within {args.due_within} days")
    return 0


def print_cliff(cliff: list[tuple[str, int]], total: int) -> None:
    print("  expiry cliff — dated facts by verified month")
    for month, n in cliff:
        share = n / total * 100 if total else 0
        expires = add_months(month_date(month), SHELF_LIFE_MONTHS)
        bar = "█" * max(1, round(share / 4))
        print(f"    {month}  {n:>4} facts ({share:4.0f}%)  expires {expires:%Y-%m}  {bar}")
    if len(cliff) == 1 and total > 1:
        print("    ^ every dated fact shares one month, so they all expire together.")
        print("      Stagger re-verification as batches come up, or the next pass")
        print("      rebuilds the same cliff 18 months out.")


if __name__ == "__main__":
    sys.exit(main())
