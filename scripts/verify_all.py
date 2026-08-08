#!/usr/bin/env python3
"""Unified gate suite — run all checks across all scripts.

Usage:
  python3 scripts/verify_all.py
"""

import subprocess
import sys
from pathlib import Path

CHECKS = [
    ("Structure",    "python3", "scripts/verify_content.py", "--only", "anchors,xanchors,links,python,parity"),
    ("Content",      "python3", "scripts/verify_content.py", "--only", "M1,M2,M4,M5,M6,M7,N1,N2,N3,N4,N5,N6"),
    ("Ontology",     "python3", "scripts/verify_ontology.py"),
    ("Skills",       "python3", "scripts/verify_skills.py"),
    ("Sustain",      "python3", "scripts/verify_all.py", "--sustain"),
    ("Dist Fresh",   "python3", "scripts/build_dist.py"),
]

SCAFFOLD_SCRIPTS = [
    "scripts/new_chapter.py",
    "scripts/new_platform.py",
    "scripts/new_prompt.py",
    "scripts/new_constraint.py",
]

ROOT_V = Path(__file__).resolve().parent.parent


def gate_e1() -> tuple[int, list[str]]:
    """E1: Four scaffolding scripts exist."""
    problems = []
    for s in SCAFFOLD_SCRIPTS:
        if not (ROOT_V / s).exists():
            problems.append(f"{s}: missing")
    return len(problems), problems


def gate_e2() -> tuple[int, list[str]]:
    """E2: CONTRIBUTING.md references real commands."""
    problems = []
    contrib = ROOT_V / "CONTRIBUTING.md"
    if not contrib.exists():
        return 1, ["CONTRIBUTING.md: missing"]
    text = contrib.read_text(encoding="utf-8")
    import re
    cmds = set(re.findall(r'`python3 scripts/([a-z_]+\.py)`', text))
    for cmd in cmds:
        if not (ROOT_V / "scripts" / cmd).exists():
            problems.append(f"CONTRIBUTING.md references scripts/{cmd} which does not exist")
    return len(problems), problems


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sustain", action="store_true", help="Run sustainability checks (E1/E2)")
    args = ap.parse_args()

    if args.sustain:
        total = 0
        for gid, fn in [("E1", gate_e1), ("E2", gate_e2)]:
            count, problems = fn()
            total += count
            mark = "ok " if count == 0 else "FAIL"
            print(f"  [{mark}] {gid:16s} {count}")
            for p in problems:
                print(f"           {p}")
        return 0 if total == 0 else 1

    total = 0
    sections = []
    for label, *cmd in CHECKS:
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Count total from last line
        lines = result.stdout.strip().split("\n")
        count = 0
        for line in lines:
            if "total" in line:
                try:
                    count = int(line.strip().split()[-1])
                except ValueError:
                    pass
        total += count
        mark = "ok " if count == 0 else "FAIL"
        print(f"  [{mark}] {label:14s} {sum(1 for _ in [])}  {count}")
        sections.append((label, count))

    print(f"  {'─' * 20}")
    print(f"  {'total':16s} {total}")
    if total:
        print("\n  Run individual scripts with --list for details.")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
