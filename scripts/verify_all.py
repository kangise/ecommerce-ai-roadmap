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
    args = ap.parse_args()

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
