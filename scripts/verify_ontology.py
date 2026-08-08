#!/usr/bin/env python3
"""Ontology gate suite.

Usage:
  python3 scripts/verify_ontology.py            # all gates
  python3 scripts/verify_ontology.py --list     # list-count mode
  python3 scripts/verify_ontology.py --only P0  # single gate

Gates:
  P0   Phase 0 completion: N1 trilingual + amazon in platforms + ontology skeleton
  O1   Every ontology source: resolves to a real chapter anchor
  O2   High-frequency nouns tracked (Phase A)
  O3   Every platform with a chapter is in platforms.yaml (Phase A)
  O4   glossary.md in sync with ontology (Phase A)
  O5   <!-- ref: --> markers match constraints.yaml values (Phase B)
"""

import argparse
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY = ROOT / "ontology"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def ok(msg: str) -> str:
    return f"  \033[32m[ok ]\033[0m {msg}"

def fail(msg: str) -> str:
    return f"  \033[31m[FAIL]\033[0m {msg}"

def _run(gates: list[tuple[str, str, callable]], gate_ids: list[str] | None,
         list_mode: bool) -> int:
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
# P0: Phase 0 completion
# ---------------------------------------------------------------------------

def gate_p0() -> list[str]:
    """P0: N1 trilingual table built, platforms.yaml has amazon, ontology/ skeleton exists."""
    problems = []

    # 1. N1 trilingual table in verify_content.py
    vc = ROOT / "scripts" / "verify_content.py"
    if vc.exists():
        text = vc.read_text(encoding="utf-8")
        if "PROMPT_TAGS_BY_TREE" not in text:
            problems.append("N1: PROMPT_TAGS_BY_TREE not found in scripts/verify_content.py")
        else:
            for tree_key in ("src", "i18n/en/src", "i18n/ja/src"):
                if f'"{tree_key}"' not in text and f"'{tree_key}'" not in text:
                    problems.append(f"N1: tree key '{tree_key}' missing from PROMPT_TAGS_BY_TREE")
    else:
        problems.append("N1: scripts/verify_content.py not found")

    # 2. platforms.yaml has 'amazon'
    pf = ONTOLOGY / "platforms.yaml"
    if pf.exists():
        try:
            platforms = yaml.safe_load(pf.read_text(encoding="utf-8"))
            if not isinstance(platforms, list):
                problems.append("platforms.yaml: must be a YAML list")
            else:
                ids = {p.get("id") for p in platforms if isinstance(p, dict)}
                if "amazon" not in ids:
                    problems.append("platforms.yaml: 'amazon' entry missing")
        except Exception as e:
            problems.append(f"platforms.yaml: parse error: {e}")
    else:
        problems.append("platforms.yaml: file missing")

    # 3. ontology skeleton files exist
    required = [
        "README.md",
        "entities.yaml",
        "relations.yaml",
        "constraints.yaml",
        "platforms.yaml",
        "processes.yaml",
        "_unresolved.md",
    ]
    for fname in required:
        if not (ONTOLOGY / fname).exists():
            problems.append(f"ontology/{fname}: missing")

    return problems


# ---------------------------------------------------------------------------
# O1–O5 stubs (implemented in Phase A/B)
# ---------------------------------------------------------------------------

def gate_o1() -> list[str]:
    """O1: Every source: pointer resolves to a real chapter anchor."""
    return []  # Phase A

def gate_o2() -> list[str]:
    """O2: High-frequency entity nouns tracked."""
    return []  # Phase A

def gate_o3() -> list[str]:
    """O3: Every platform chapter is in platforms.yaml."""
    return []  # Phase A

def gate_o4() -> list[str]:
    """O4: glossary.md in sync with ontology."""
    return []  # Phase A

def gate_o5() -> list[str]:
    """O5: ref markers match constraints.yaml values."""
    return []  # Phase B


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

GATES = [
    ("P0", "Phase 0 complete", gate_p0),
    ("O1", "source anchors valid", gate_o1),
    ("O2", "entity coverage", gate_o2),
    ("O3", "platform coverage", gate_o3),
    ("O4", "glossary sync", gate_o4),
    ("O5", "ref-marker sync", gate_o5),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Ontology gate suite")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only")
    args = ap.parse_args()
    gate_ids = args.only.split(",") if args.only else None
    return _run(GATES, gate_ids, args.list)


if __name__ == "__main__":
    sys.exit(main())
