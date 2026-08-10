#!/usr/bin/env python3
"""Ontology gate suite.

Usage:
  python3 scripts/verify_ontology.py            # all gates
  python3 scripts/verify_ontology.py --list     # list-count mode
  python3 scripts/verify_ontology.py --only O1  # single gate

Gates:
  P0   Phase 0 completion: N1 trilingual + amazon in platforms + ontology skeleton
  O1   Every ontology source: resolves to a real chapter anchor
  O2   High-frequency entity nouns tracked
  O3   Every platform chapter is in platforms.yaml
  O4   glossary.md in sync with ontology
  O5   <!-- ref: --> markers match constraints.yaml values (Phase B)
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
import unicodedata
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY = ROOT / "ontology"
SRC = ROOT / "src"
I18N_EN = ROOT / "i18n" / "en" / "src"
I18N_JA = ROOT / "i18n" / "ja" / "src"


# ---------------------------------------------------------------------------
# mdBook anchor helpers (same logic as verify_content.py)
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*?([^*]*)\*\*?", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("---", "\u2014").replace("--", "\u2013")
    text = text.strip().lower()
    out = []
    for ch in text:
        if ch in " \t":
            out.append("-")
        elif ch in "-_":
            out.append(ch)
        elif unicodedata.category(ch)[0] in ("L", "N"):
            out.append(ch)
    return "".join(out)


FENCE = re.compile(r"^```")
HTML_ID = re.compile(r'id="([^"]+)"')
HEADING = re.compile(r"^(#{1,6})\s+(.+)")


def page_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    seen: collections.Counter[str] = collections.Counter()
    in_fence = False
    for line in text.split("\n"):
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        anchors.update(HTML_ID.findall(line))
        m = HEADING.match(line)
        if not m:
            continue
        base = slugify(m.group(2))
        if not base:
            continue
        seen[base] += 1
        if seen[base] > 1:
            anchors.add(f"{base}-{seen[base] - 1}")
        anchors.add(base)
    return anchors


def _resolve_source(source_ref: str) -> str | None:
    """Given 'src/path#anchor', return None if valid or error string."""
    if "#" in source_ref:
        path_str, anchor = source_ref.rsplit("#", 1)
    else:
        path_str, anchor = source_ref, None
    fp = ROOT / path_str
    if not fp.exists():
        return f"file not found: {path_str}"
    if anchor:
        text = fp.read_text(encoding="utf-8")
        anchors = page_anchors(text)
        if anchor not in anchors:
            return f"anchor '#{anchor}' not found in {path_str}"
    return None


# ---------------------------------------------------------------------------
# yaml loading
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> list:
    if not path.exists():
        return []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def _all_source_refs() -> list[tuple[str, str, str]]:
    """Collect (file, id, source_ref) from entities/relations/constraints/processes."""
    refs = []
    for yf in ["entities.yaml", "relations.yaml", "constraints.yaml", "processes.yaml"]:
        data = _load_yaml(ONTOLOGY / yf)
        for entry in data:
            if not isinstance(entry, dict):
                continue
            eid = entry.get("id", "?")
            sources = entry.get("source", [])
            if isinstance(sources, str):
                sources = [sources]
            for src in sources:
                refs.append((yf, eid, src))
        # processes.yaml: each step carries its own source: pointer
        if yf == "processes.yaml":
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                pid = entry.get("id", "?")
                for i, step in enumerate(entry.get("steps") or [], 1):
                    if not isinstance(step, dict):
                        continue
                    src = step.get("source")
                    if src:
                        refs.append((yf, f"{pid}.step{i}", src))
    return refs


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def ok(msg: str) -> str:
    return f"  \033[32m[ok ]\033[0m {msg}"

def fail(msg: str) -> str:
    return f"  \033[31m[FAIL]\033[0m {msg}"

def _run(gates: list, gate_ids: list[str] | None, list_mode: bool) -> int:
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
    print(f"\n  total {total}")
    return 0 if total == 0 else 1


# ---------------------------------------------------------------------------
# P0: Phase 0 completion
# ---------------------------------------------------------------------------

def gate_p0() -> list[str]:
    problems = []
    vc = ROOT / "scripts" / "verify_content.py"
    if vc.exists():
        text = vc.read_text(encoding="utf-8")
        if "PROMPT_TAGS_BY_TREE" not in text:
            problems.append("N1: PROMPT_TAGS_BY_TREE not found in verify_content.py")
        else:
            for tree_key in ("src", "i18n/en/src", "i18n/ja/src"):
                if f'"{tree_key}"' not in text and f"'{tree_key}'" not in text:
                    problems.append(f"N1: tree key '{tree_key}' missing from PROMPT_TAGS_BY_TREE")
    else:
        problems.append("N1: verify_content.py not found")

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

    required = [
        "README.md", "entities.yaml", "relations.yaml", "constraints.yaml",
        "platforms.yaml", "processes.yaml", "_unresolved.md",
    ]
    for fname in required:
        if not (ONTOLOGY / fname).exists():
            problems.append(f"ontology/{fname}: missing")

    return problems


# ---------------------------------------------------------------------------
# O1: source anchor validation
# ---------------------------------------------------------------------------

def gate_o1() -> list[str]:
    """Every source: pointer resolves to a real file + anchor."""
    problems = []
    refs = _all_source_refs()
    for yf, eid, src_ref in refs:
        err = _resolve_source(src_ref)
        if err:
            problems.append(f"{yf} id={eid}: {err}")
    return problems


# ---------------------------------------------------------------------------
# O2: high-frequency entity coverage
# ---------------------------------------------------------------------------


def _load_text_set(path: Path) -> set[str]:
    """Load a newline-separated text file, skipping comments and blanks."""
    if not path.exists():
        return set()
    lines = []
    for line in path.read_text(encoding="utf-8").split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return set(lines)


def gate_o2() -> list[str]:
    """High-frequency nouns (>=20) in chapters not tracked in entities.yaml.

    Uses ontology/_entity_allowlist.txt and ontology/_not_entity.txt as the
    filter: words in neither list that appear >=20 times across chapters
    and are not in entities.yaml are reported as uncovered candidates.
    """
    not_entity = _load_text_set(ONTOLOGY / "_not_entity.txt")
    entity_allow = _load_text_set(ONTOLOGY / "_entity_allowlist.txt")

    # Count English entity-candidate words
    word_count = collections.Counter()
    for md in sorted(SRC.rglob("*.md")):
        if md.name == "SUMMARY.md":
            continue
        text = md.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", " ", text, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        words = re.findall(r'\b[A-Z]{2,6}\b|\b[A-Z][a-z]+(?:[- ][A-Z][a-z]+)*\b|\b[a-z]+(?:[- ][a-z]+)*\b', text)
        for w in words:
            wl = w.lower().replace(" ", "-")
            word_count[wl] += 1

    # Count CJK entity candidates
    cjk_pattern = re.compile(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]{2,6}')
    for md in sorted(SRC.rglob("*.md")):
        if md.name == "SUMMARY.md":
            continue
        text = md.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", " ", text, flags=re.S)
        for m in cjk_pattern.finditer(text):
            word_count[m.group()] += 1

    # Load entities.yaml IDs
    entity_ids = set()
    entities = _load_yaml(ONTOLOGY / "entities.yaml")
    for e in entities:
        if isinstance(e, dict) and "id" in e:
            entity_ids.add(e["id"])

    problems = []
    THRESHOLD = 20
    for word, count in word_count.most_common(500):
        if count < THRESHOLD:
            break
        if word in not_entity:
            continue
        if word in entity_allow:
            continue
        if word in entity_ids:
            continue
        if len(word) <= 2 and word.isascii():
            continue
        problems.append(f"{word} ({count}x): not in entities.yaml or allowlist")

    return problems


# ---------------------------------------------------------------------------
# O3: platform coverage
# ---------------------------------------------------------------------------

def gate_o3() -> list[str]:
    """Every platform with a chapter in src/d-platforms/ must be in platforms.yaml."""
    problems = []

    platforms_data = _load_yaml(ONTOLOGY / "platforms.yaml")
    registered_ids = {p.get("id") for p in platforms_data if isinstance(p, dict)}

    # Scan d-platforms chapters for platform IDs
    platform_files = sorted((SRC / "d-platforms").glob("*.md"))
    for pf in platform_files:
        if pf.name in ("README.md", "platform-comparison.md", "cross-platform-strategy.md"):
            continue
        text = pf.read_text(encoding="utf-8")
        # Find the platform name from the H1
        m = re.search(r'^#\s+(.+)', text, re.M)
        if not m:
            continue
        title = m.group(1)
        # Derive platform ID from filename
        stem = pf.stem  # e.g., shopify-ai-guide, d4-walmart-ai-guide
        # Map known filenames to platform IDs
        filename_to_id = {
            "shopify-ai-guide": "shopify",
            "tiktok-shop-ai-guide": "tiktok_shop",
            "d4-walmart-ai-guide": "walmart",
            "d5-temu-seller-guide": "temu",
            "d6-southeast-asia-ai-guide": ["shopee", "lazada"],
            "d7-mercado-libre-ai-guide": "mercado_libre",
            "d8-rakuten-japan-ai-guide": "rakuten",
            "d9-ebay-ai-guide": "ebay",
            "d10-aliexpress-ai-guide": "aliexpress",
            "d11-coupang-korea-ai-guide": "coupang",
            "d12-faire-wholesale-ai-guide": "faire",
            "d13-europe-marketplaces-guide": ["otto", "zalando"],
            "d0-amazon-index": "amazon",
        }
        expected = filename_to_id.get(stem)
        if not expected:
            continue
        if isinstance(expected, str):
            expected = [expected]
        for eid in expected:
            if eid not in registered_ids:
                problems.append(f"{pf.name}: platform '{eid}' not in platforms.yaml")

    # Must include amazon
    if "amazon" not in registered_ids:
        problems.append("platforms.yaml: 'amazon' entry missing")

    return problems


# ---------------------------------------------------------------------------
# O4: glossary sync
# ---------------------------------------------------------------------------

def _generate_glossary() -> str:
    """Generate glossary.md content from entities.yaml."""
    entities = _load_yaml(ONTOLOGY / "entities.yaml")
    if not entities:
        return "<!-- Generated from ontology/entities.yaml -->\n\n# Glossary\n\n_No entities defined yet._\n"

    lines = [
        "<!-- Generated from ontology/entities.yaml — do not edit by hand -->",
        "<!-- claims: verified 2026-08 -->",
        "",
        "# Glossary / 术语表 / 用語集",
        "",
    ]
    for e in entities:
        if not isinstance(e, dict):
            continue
        eid = e.get("id", "?")
        label = e.get("label", {})
        definition = e.get("definition", {})
        zh_label = label.get("zh", eid)
        en_label = label.get("en", eid)
        ja_label = label.get("ja", eid)
        zh_def = definition.get("zh", "")
        en_def = definition.get("en", "")

        lines.append(f"## {zh_label} / {en_label}")
        if ja_label and ja_label != en_label:
            lines.append(f"> {ja_label}")
        lines.append("")
        if zh_def:
            lines.append(f"- **ZH**: {zh_def}")
        if en_def:
            lines.append(f"- **EN**: {en_def}")
        lines.append("")

    return "\n".join(lines) + "\n"


def gate_o4() -> list[str]:
    """Glossary.md must match regenerated content from entities.yaml."""
    glossary_path = SRC / "resources" / "glossary.md"
    regenerated = _generate_glossary()

    if not glossary_path.exists():
        return ["src/resources/glossary.md: missing (run generation)"]

    current = glossary_path.read_text(encoding="utf-8")
    if current.strip() != regenerated.strip():
        return ["src/resources/glossary.md: out of sync with ontology/entities.yaml"]

    return []


# ---------------------------------------------------------------------------
# O5: ref marker sync (Phase B)
# ---------------------------------------------------------------------------

def gate_o5() -> list[str]:
    """Every <!-- ref: constraint_id --> refers to an existing constraint in constraints.yaml.

    Additionally, for numeric constraints, verify that the literal value on the same
    line as the ref marker matches the constraint's `value` field.
    """
    problems = []
    constraints = _load_yaml(ONTOLOGY / "constraints.yaml")
    constraint_ids = set()
    constraint_values = {}
    for c in constraints:
        if isinstance(c, dict):
            cid = c.get("id", "")
            if cid:
                constraint_ids.add(cid)
                constraint_values[cid] = c.get("value")

    REF_PATTERN = re.compile(r"<!--\s*ref:\s*([a-zA-Z0-9_.-]+)\s*-->")

    for tree in ("src", "i18n/en/src", "i18n/ja/src"):
        tree_root = ROOT / tree
        if not tree_root.exists():
            continue
        for md in sorted(tree_root.rglob("*.md")):
            text = md.read_text(encoding="utf-8")
            for i, line in enumerate(text.split("\n"), 1):
                for m in REF_PATTERN.finditer(line):
                    cid = m.group(1)
                    rel = f"{tree}/{md.relative_to(tree_root)}"
                    if cid not in constraint_ids:
                        problems.append(f"{rel}:{i} ref '{cid}' not found in constraints.yaml")
                    else:
                        # Check value consistency: extract a number from the line
                        # and compare with the constraint value
                        val = constraint_values.get(cid)
                        if val is not None and isinstance(val, (int, float)):
                            # Try to find the literal value on this line
                            nums = re.findall(r'(?<!\d)(\d+(?:\.\d+)?)', line)
                            if nums:
                                # Check if any number on this line matches the constraint value
                                found = False
                                for n in nums:
                                    try:
                                        if float(n) == float(val):
                                            found = True
                                            break
                                    except ValueError:
                                        continue
                                if not found:
                                    problems.append(
                                        f"{rel}:{i} ref '{cid}' value={val} "
                                        f"but line numbers={nums}"
                                    )
    return problems


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
