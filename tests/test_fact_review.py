"""fact_review.py — the review queue behind M7.

M7 enforces the discipline but only speaks in failure states. These tests pin
the reporting contract that makes the cadence actionable: the queue is ordered,
every dated fact is accounted for, --due-within is a usable CI signal, and the
numbers agree with the gate that enforces them.
"""

from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/fact_review.py", *args],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def queue() -> dict:
    result = run("--json")
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def test_reports_every_batch_in_the_plan() -> None:
    plan = yaml.safe_load((ROOT / "maintenance" / "fact-review-plan.yaml").read_text())
    planned = {b["id"] for b in plan["batches"]}
    assert {b["id"] for b in queue()["batches"]} == planned


def test_batches_are_ordered_by_due_date() -> None:
    dues = [b["due"] for b in queue()["batches"]]
    assert dues == sorted(dues)


def test_every_dated_fact_is_owned_by_exactly_one_batch() -> None:
    """M7 fails the build when a fact matches != 1 batch; the queue must agree.

    If these totals drift apart, the report is quietly hiding facts that the
    gate is still holding someone responsible for.
    """
    data = queue()
    assigned = sum(b["constraints"] + b["content_claims"] for b in data["batches"])

    constraints = yaml.safe_load((ROOT / "ontology" / "constraints.yaml").read_text()) or []
    dated = [c for c in constraints if isinstance(c, dict) and c.get("verified")]
    claims = sum(
        md.read_text(encoding="utf-8").count("claims: verified")
        for md in (ROOT / "src").rglob("*.md")
    )
    assert assigned == len(dated) + claims


def test_shelf_life_matches_the_gate_that_enforces_it() -> None:
    """A report describing a different deadline than M7 enforces is worse than none."""
    gate = (ROOT / "scripts" / "verify_content.py").read_text(encoding="utf-8")
    assert "SHELF_LIFE_MONTHS = 18" in gate
    assert queue()["shelf_life_months"] == 18


def test_stale_deadline_respects_the_review_lead_time() -> None:
    data = queue()
    lead = data["review_lead_months"]
    assert lead >= 1
    for batch in data["batches"]:
        if not batch["stale_deadline"] or not batch["constraints"] + batch["content_claims"]:
            continue
        due = datetime.date.fromisoformat(batch["due"] + "-01")
        stale = datetime.date.fromisoformat(batch["stale_deadline"])
        # M7 compares with `>`, so landing exactly on the deadline is legal —
        # zero slack, but not a violation. The report must agree with the gate
        # rather than invent a stricter rule of its own.
        assert due <= stale, batch["id"]


def test_zero_slack_batches_are_flagged() -> None:
    """A batch due exactly on its deadline passes M7 but has no room to slip.

    evidence-and-social sits there today. The queue has to say so, or the first
    delay turns a silent condition into a hard gate failure.
    """
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr
    data = queue()
    tight = [
        b["id"] for b in data["batches"]
        if b["stale_deadline"]
        and datetime.date.fromisoformat(b["due"] + "-01")
        == datetime.date.fromisoformat(b["stale_deadline"])
    ]
    for batch_id in tight:
        assert batch_id in result.stdout
    if tight:
        assert "no slack" in result.stdout


def test_due_within_is_a_usable_ci_signal() -> None:
    """A batch inside the window flags; one outside it does not.

    Deliberately does not assume a clean window exists. An overdue batch enters
    `soon` unconditionally, so once any batch passes its due date no --due-within
    value can return 0 — the first assertion still holds, the second stops being
    meaningful. The plan's earliest due date is 2027-02, so this would have begun
    failing on that day rather than reporting anything real.
    """
    batches = queue()["batches"]
    soonest = min(b["days_remaining"] for b in batches)

    inside = run("--due-within", str(soonest + 1))
    assert inside.returncode == 1, "a batch inside the window must be flagged"
    assert "due within" in inside.stdout

    if soonest <= 0:
        # Something is already overdue; a quiet window cannot exist by design.
        assert run("--due-within", "0").returncode == 1
        return

    outside = run("--due-within", str(soonest - 1))
    assert outside.returncode == 0, outside.stdout + outside.stderr
    assert "nothing due within" in outside.stdout


def test_cliff_accounts_for_all_dated_facts() -> None:
    data = queue()
    total = sum(entry["facts"] for entry in data["expiry_cliff"])
    assigned = sum(b["constraints"] + b["content_claims"] for b in data["batches"])
    assert total == assigned


def test_unknown_batch_fails_loudly() -> None:
    assert run("--batch", "no-such-batch").returncode != 0
