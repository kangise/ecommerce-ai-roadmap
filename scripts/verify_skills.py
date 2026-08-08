#!/usr/bin/env python3
"""Skill gate suite.

Usage:
  python3 scripts/verify_skills.py            # all gates
  python3 scripts/verify_skills.py --list     # list-count mode
  python3 scripts/verify_skills.py --only S1  # single gate

Gates:
  S1   SKILL.md has valid frontmatter (name + description) and no description conflicts
  S2   Skill references trace back to source files
  S3   All 7 domain skills exist and are non-empty
"""

import argparse
import re
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

REQUIRED_SKILLS = [
    "ecom-listing", "ecom-advertising", "ecom-inventory",
    "ecom-compliance", "ecom-pricing", "ecom-research", "ecom-applicability",
]

FM_PATTERN = re.compile(r"^---\s*\n(.*?)\n---", re.S)


def ok(msg: str) -> str:
    return f"  \033[32m[ok ]\033[0m {msg}"

def fail(msg: str) -> str:
    return f"  \033[31m[FAIL]\033[0m {msg}"

def _run(gates, gate_ids, list_mode):
    total = 0
    for gid, label, fn in gates:
        if gate_ids and gid not in gate_ids:
            continue
        problems = fn()
        if list_mode:
            for p in problems:
                print(f"{fail(gid):40s} {p}")
        if not problems:
            print(f"{ok(gid):40s} 0")
        else:
            print(f"{fail(gid):40s} {len(problems)}")
        total += len(problems)
    if total == 0:
        print(f"\n  total 0")
    return 0 if total == 0 else 1


# ---------------------------------------------------------------------------
# S1: valid frontmatter
# ---------------------------------------------------------------------------

def gate_s1() -> list[str]:
    """Each SKILL.md has valid frontmatter with name + description, no conflicts."""
    problems = []
    descriptions = {}

    for sid in REQUIRED_SKILLS:
        smd = SKILLS / sid / "SKILL.md"
        if not smd.exists():
            problems.append(f"{sid}/SKILL.md: missing")
            continue
        text = smd.read_text(encoding="utf-8")
        m = FM_PATTERN.match(text)
        if not m:
            problems.append(f"{sid}/SKILL.md: no frontmatter")
            continue
        fm_text = m.group(1)
        try:
            fm = yaml.safe_load(fm_text)
        except Exception:
            problems.append(f"{sid}/SKILL.md: invalid YAML frontmatter")
            continue
        if not isinstance(fm, dict):
            problems.append(f"{sid}/SKILL.md: frontmatter is not a dict")
            continue

        name = fm.get("name", "")
        desc = fm.get("description", "")
        if not name:
            problems.append(f"{sid}/SKILL.md: missing 'name' in frontmatter")
        if not desc:
            problems.append(f"{sid}/SKILL.md: missing 'description' in frontmatter")
        if name:
            descriptions[name] = desc

    # Check for description overlap (conflicting trigger words)
    desc_words = {}
    for name, desc in descriptions.items():
        words = set(re.findall(r'\b[a-z][a-z-]+\b', desc.lower()))
        desc_words[name] = words

    skill_names = list(descriptions.keys())
    for i in range(len(skill_names)):
        for j in range(i + 1, len(skill_names)):
            a, b = skill_names[i], skill_names[j]
            # Filter out common stop words before checking overlap
            stop_words = {"and", "or", "for", "use", "when", "the", "to", "of", "in", "a", "an", "is", "with", "by", "on", "as", "at"}
            a_terms = {w for w in desc_words[a] if w not in stop_words and len(w) > 2}
            b_terms = {w for w in desc_words[b] if w not in stop_words and len(w) > 2}
            overlap = a_terms & b_terms
            if len(overlap) > 5:
                problems.append(f"SKILL.md: '{a}' and '{b}' descriptions overlap: {sorted(overlap)[:5]}...")

    return problems


# ---------------------------------------------------------------------------
# S2: references trace back to source
# ---------------------------------------------------------------------------

def gate_s2() -> list[str]:
    """Skill references must point to files that exist in src/ or ontology/."""
    problems = []

    for sid in REQUIRED_SKILLS:
        skill_dir = SKILLS / sid
        if not skill_dir.exists():
            continue
        for ref_file in skill_dir.rglob("*.md"):
            if ref_file.name == "SKILL.md":
                continue
            text = ref_file.read_text(encoding="utf-8")
            # Check for references to source chapters
            refs = re.findall(r'`([a-z0-9_./-]+\.(?:yaml|md))`', text)
            refs += re.findall(r'src/[a-z0-9_./-]+\.md', text)
            for ref in set(refs):
                target = ROOT / ref
                if not target.exists():
                    problems.append(f"{ref_file.relative_to(ROOT)}: references '{ref}' which does not exist")

    return problems


# ---------------------------------------------------------------------------
# S3: all 7 skills exist
# ---------------------------------------------------------------------------

def gate_s3() -> list[str]:
    """All 7 domain skills exist and have non-empty SKILL.md."""
    problems = []
    for sid in REQUIRED_SKILLS:
        smd = SKILLS / sid / "SKILL.md"
        if not smd.exists():
            problems.append(f"{sid}/SKILL.md: missing")
        elif smd.stat().st_size < 100:
            problems.append(f"{sid}/SKILL.md: too small ({smd.stat().st_size} bytes)")
    return problems


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

GATES = [
    ("S1", "skill frontmatter", gate_s1),
    ("S2", "skill traceability", gate_s2),
    ("S3", "skill existence", gate_s3),
]


def main():
    ap = argparse.ArgumentParser(description="Skill gate suite")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only")
    args = ap.parse_args()
    gate_ids = args.only.split(",") if args.only else None
    return _run(GATES, gate_ids, args.list)


if __name__ == "__main__":
    sys.exit(main())
