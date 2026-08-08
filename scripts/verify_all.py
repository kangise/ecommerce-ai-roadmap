#!/usr/bin/env python3
"""Unified gate suite — run all checks across all scripts.

Usage:
  python3 scripts/verify_all.py            # all gates
  python3 scripts/verify_all.py --sustain  # E1/E2 only
"""

import subprocess
import sys
import re
from pathlib import Path

ROOT_V = Path(__file__).resolve().parent.parent

# Each check runs a full sub-script (no --only fragments).
CHECKS = [
    ("Content",   "python3", "scripts/verify_content.py"),
    ("Ontology",  "python3", "scripts/verify_ontology.py"),
    ("Skills",    "python3", "scripts/verify_skills.py"),
    ("Knowledge", "python3", "scripts/verify_all.py", "--k1"),
    ("Routing",   "python3", "scripts/verify_all.py", "--r1"),
    ("Dist",      "python3", "scripts/build_dist.py"),
]

SCAFFOLD_SCRIPTS = [
    "scripts/new_chapter.py",
    "scripts/new_platform.py",
    "scripts/new_prompt.py",
    "scripts/new_constraint.py",
]


def _parse_total(stdout: str) -> int:
    """Extract total count from a gate script's output (strips ANSI codes)."""
    import re as _re
    clean = _re.sub(r'\x1b\[[0-9;]*m', '', stdout)
    for line in clean.strip().split("\n"):
        m = _re.search(r"^\s+total\s+(\d+)", line)
        if m:
            return int(m.group(1))
    return 0


def gate_e1() -> tuple[int, list[str]]:
    problems = []
    for s in SCAFFOLD_SCRIPTS:
        if not (ROOT_V / s).exists():
            problems.append(f"{s}: missing")
    return len(problems), problems


def gate_e2() -> tuple[int, list[str]]:
    problems = []
    contrib = ROOT_V / "CONTRIBUTING.md"
    if not contrib.exists():
        return 1, ["CONTRIBUTING.md: missing"]
    text = contrib.read_text(encoding="utf-8")
    cmds = set(re.findall(r'`python3 scripts/([a-z_]+\.py)`', text))
    for cmd in cmds:
        if not (ROOT_V / "scripts" / cmd).exists():
            problems.append(f"CONTRIBUTING.md references scripts/{cmd} which does not exist")
    return len(problems), problems


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sustain", action="store_true")
    ap.add_argument("--k1", action="store_true", help="Knowledge index coverage check")
    ap.add_argument("--r1", action="store_true", help="Routing accuracy check")
    args = ap.parse_args()

    if args.r1:
        import yaml as _yaml
        cases_path = ROOT_V / "tests" / "routing-cases.yaml"
        if not cases_path.exists():
            print("  [FAIL] R1          1 (tests/routing-cases.yaml missing)")
            return 1
        with open(cases_path) as f:
            cases = _yaml.safe_load(f) or []

        # Build routing rules from manifest triggers
        manifests = {}
        for mf_path in sorted((ROOT_V / "skills").glob("*/manifest.yaml")):
            with open(mf_path) as f:
                mf = _yaml.safe_load(f)
            sid = mf.get("name", "")
            triggers = mf.get("triggers", {})
            keywords = triggers.get("keywords", []) if isinstance(triggers, dict) else []
            manifests[sid] = keywords

        errors = []
        for i, case in enumerate(cases):
            query = case.get("query", "")
            expected = case.get("expect", "")
            if not query or not expected:
                continue
            # Routing logic (same as what the agent prompt describes):
            # - If applicability keywords match, always route to applicability
            #   (overrides domain keywords — user is asking "should I use AI?")
            # - Otherwise, highest keyword match wins
            app_kws = manifests.get("ecom-applicability", [])
            is_app_question = any(kw.lower() in query.lower() for kw in app_kws if len(kw) >= 3)
            if is_app_question:
                best_match = "ecom-applicability"
            else:
                best_match = None
                best_score = 0
                for sid, keywords in manifests.items():
                    if sid == "ecom-applicability":
                        continue  # already checked above
                    score = sum(1 for kw in keywords if kw.lower() in query.lower())
                    if score > best_score:
                        best_score = score
                        best_match = sid
            if best_match != expected:
                errors.append(f"case {i+1}: '{query[:40]}...' routed to {best_match} (expected {expected})")

        total = len(errors)
        mark = "ok " if total == 0 else "FAIL"
        print(f"  [{mark}] R1          {total}/{len(cases)}")
        for e in errors:
            print(f"           {e}")
        return 0 if total == 0 else 1

    if args.k1:
        import json as _json
        idx_path = ROOT_V / "dist" / "knowledge" / "index.json"
        if not idx_path.exists():
            print(f"  [FAIL] K1          1 (dist/knowledge/index.json missing)")
            return 1
        with open(idx_path) as f:
            index = _json.load(f)
        problems = []
        total_chapters = len([p for p in (ROOT_V / "src").rglob("*.md") if p.name not in ("SUMMARY.md", "README.md")])
        for entry in index:
            if not isinstance(entry, dict):
                continue
            path = entry.get("path", "")
            title = entry.get("title", "")
            entities = entry.get("key_entities", [])
            if not title:
                problems.append(f"index entry for {path}: missing title")
            # Resource and case-studies chapters are reference docs with few entities
            # awesome-ai-skills is a pure curated list with no domain entities
            is_ref = path.startswith("resources/") or path.startswith("case-studies/")
            is_skills_list = path == "resources/awesome-ai-skills.md"
            min_entities = 0 if is_skills_list else (1 if is_ref else 3)
            if len(entities) < min_entities:
                problems.append(f"{path}: only {len(entities)} key_entities (need >={min_entities})")
        uncovered = total_chapters - len(index)
        if uncovered > 0:
            problems.append(f"{uncovered} chapters not in index")
        total = len(problems)
        mark = "ok " if total == 0 else "FAIL"
        print(f"  [{mark}] K1          {total}")
        for p in problems:
            print(f"           {p}")
        return 0 if total == 0 else 1

    if args.sustain:
        total = 0
        for gid, fn in [("E1", gate_e1), ("E2", gate_e2)]:
            count, problems = fn()
            total += count
            mark = "ok " if count == 0 else "FAIL"
            print(f"  [{mark}] {gid:12s} {count}")
            for p in problems:
                print(f"           {p}")
        print(f"  {'─' * 16}")
        print(f"  total       {total}")
        return 0 if total == 0 else 1

    grand_total = 0
    for label, *cmd in CHECKS:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        count = _parse_total(result.stdout)

        # Trust returncode over stdout parsing
        if result.returncode != 0 and count == 0:
            # Script failed but reported 0 — likely a crash
            print(f"  [FAIL] {label:12s} crashed (exit {result.returncode})")
            for line in result.stderr.strip().split("\n")[-5:]:
                print(f"           {line}")
            grand_total += 1
        else:
            grand_total += count
            mark = "ok " if count == 0 else "FAIL"
            print(f"  [{mark}] {label:12s} {count}")
            if result.returncode != 0 and result.stderr.strip():
                # Non-zero exit but gate reported real count — show stderr briefly
                for line in result.stderr.strip().split("\n")[:3]:
                    print(f"           {line}")

    print(f"  {'─' * 16}")
    print(f"  total       {grand_total}")
    if grand_total:
        print("\n  Run individual scripts with --list for details.")
    return 0 if grand_total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
