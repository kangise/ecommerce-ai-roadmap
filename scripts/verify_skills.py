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
    "ecom-customer-service",
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
        print(f"\n  total {total}")
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

def gate_s4() -> list[str]:
    """References must have substance (not empty shells or placeholder text).

    1. references/*.md files must have >= 8 lines of actual content
       (excluding headers and generation markers), unless marked
       `<!-- intentionally-empty: reason -->`
    2. SKILL.md must not reference non-existent or empty directories
    3. playbook.md must contain prompt structure tags or an explicit reason
    """
    problems = []
    INTENTIONALLY_EMPTY = re.compile(r"<!--\s*intentionally-empty:.*-->")
    PROMPT_TAGS = re.compile(r"<(?:角色|任务|役割|role|task|タスク|データ規律|data_discipline|数据纪律)>")
    PLACEHOLDER_PATTERNS = [
        r"^_\w.*_$",               # _No domain-specific constraints._
        r"^_No specific prompts\._$",
        r"^_Applicability skill:.*_$",
        r"^_TBD_$",
    ]
    PLACEHOLDER_RE = re.compile("|".join(PLACEHOLDER_PATTERNS))

    for sid in REQUIRED_SKILLS:
        skill_dir = SKILLS / sid
        if not skill_dir.exists():
            continue

        # Check references/*.md
        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            for ref_file in sorted(refs_dir.rglob("*.md")):
                text = ref_file.read_text(encoding="utf-8")
                if INTENTIONALLY_EMPTY.search(text):
                    continue
                # Count substantive lines (not headers, not comments, not generation markers)
                lines = [l for l in text.split("\n")
                         if l.strip()
                         and not l.strip().startswith("#")
                         and not l.strip().startswith("<!--")
                         and not PLACEHOLDER_RE.match(l.strip())]
                # Also check: every non-header line that looks like a placeholder
                for line in text.split("\n"):
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#") and PLACEHOLDER_RE.match(stripped):
                        problems.append(
                            f"{ref_file.relative_to(ROOT)}: placeholder text '{stripped[:50]}'"
                        )
                if len(lines) < 8:
                    problems.append(
                        f"{ref_file.relative_to(ROOT)}: only {len(lines)} substantive lines (need >=8)"
                    )

        # Check SKILL.md doesn't reference empty/non-existent paths
        smd = skill_dir / "SKILL.md"
        if smd.exists():
            text = smd.read_text(encoding="utf-8")
            # Find references to internal paths
            for m in re.finditer(r'`(assets/templates/|references/)([^`]+)`', text):
                ref_path = skill_dir / m.group(0).strip("`")
                if not ref_path.exists():
                    problems.append(f"{sid}/SKILL.md: references '{m.group(0)}' which does not exist")
                elif ref_path.is_dir() and not any(ref_path.iterdir()):
                    problems.append(f"{sid}/SKILL.md: references empty directory '{m.group(0)}'")

        # Check playbook.md has real prompt content
        playbook = skill_dir / "references" / "playbook.md"
        if playbook.exists():
            text = playbook.read_text(encoding="utf-8")
            # Must contain prompt tags OR explicit statement this skill doesn't need them
            has_tags = bool(PROMPT_TAGS.search(text))
            has_explicit = bool(re.search(
                r"boundary.reasoning|boundary.condition|this skill (uses|performs|applies)|See boundaries",
                text, re.I
            ))
            if not has_tags and not has_explicit:
                problems.append(f"{playbook.relative_to(ROOT)}: no prompt content or explicit reasoning statement")
            elif not has_tags and has_explicit:
                # Explicitly stated as non-prompt skill — this is valid
                pass

    return problems


def gate_m8() -> list[str]:
    """M8: dist/SKILL.md frontmatter + source manifest.yaml validity.

    1. dist/SKILL.md must have frontmatter with name, description, capabilities, routing
    2. All 7 skills must have source manifest.yaml with name, description, triggers, inputs, outputs
    3. dist/SKILL.md routing must mention all 7 skill names (not stale)
    """
    problems = []

    # 1. Check dist/SKILL.md
    dist_skill = ROOT / "dist" / "SKILL.md"
    if dist_skill.exists():
        text = dist_skill.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
        if not fm_match:
            problems.append("dist/SKILL.md: missing frontmatter")
        else:
            fm_text = fm_match.group(1)
            try:
                fm = yaml.safe_load(fm_text)
            except Exception:
                problems.append("dist/SKILL.md: invalid YAML frontmatter")
                fm = {}
            if isinstance(fm, dict):
                for key in ["name", "description", "capabilities", "routing"]:
                    if key not in fm:
                        problems.append(f"dist/SKILL.md: missing '{key}' in frontmatter")
                    elif key == "capabilities" and (not isinstance(fm[key], list) or len(fm[key]) < len(REQUIRED_SKILLS)):
                        problems.append(f"dist/SKILL.md: capabilities < {len(REQUIRED_SKILLS)} ({len(fm.get(key, []))} found)")
                    elif key == "routing" and (not isinstance(fm[key], list) or len(fm[key]) < len(REQUIRED_SKILLS)):
                        problems.append(f"dist/SKILL.md: routing < {len(REQUIRED_SKILLS)} ({len(fm.get(key, []))} found)")
                # Check routing mentions all 7 skills
                routing_text = yaml.dump(fm.get("routing", []), allow_unicode=True)
                for sid in REQUIRED_SKILLS:
                    if f"skill: {sid}" not in routing_text:
                        problems.append(f"dist/SKILL.md: routing missing skill '{sid}'")
    else:
        problems.append("dist/SKILL.md: missing (run build_dist.py)")

    # 2. Check source manifest.yaml for all 7 skills
    for sid in REQUIRED_SKILLS:
        mf = SKILLS / sid / "manifest.yaml"
        if not mf.exists():
            problems.append(f"skills/{sid}/manifest.yaml: missing")
            continue
        try:
            mf_data = yaml.safe_load(mf.read_text(encoding="utf-8"))
        except Exception:
            problems.append(f"skills/{sid}/manifest.yaml: invalid YAML")
            continue
        if not isinstance(mf_data, dict):
            problems.append(f"skills/{sid}/manifest.yaml: must be a YAML mapping")
            continue
        for key in ["name", "description", "triggers", "inputs", "outputs"]:
            if key not in mf_data:
                problems.append(f"skills/{sid}/manifest.yaml: missing '{key}'")
        triggers = mf_data.get("triggers", {})
        if isinstance(triggers, dict):
            if "keywords" not in triggers or not triggers["keywords"]:
                problems.append(f"skills/{sid}/manifest.yaml: triggers.keywords empty")
        inputs = mf_data.get("inputs", [])
        if isinstance(inputs, list) and not inputs:
            problems.append(f"skills/{sid}/manifest.yaml: inputs empty")

    return problems


def gate_s5() -> list[str]:
    """S5: Prompt coverage — chapters with >=5 prompts but no skill coverage."""
    import json as _json
    problems = []

    EXEMPT = {
        # Meta/reference chapters (real filenames verified)
        "f2-prompt-engineering.md",
        "c3-roi-evaluation.md", "c4-ai-risk-governance.md",
        "c5-competitive-intelligence.md", "c2-team-building.md",
        "b2-prediction-models.md",
        # Tool/resource comparison
        "f6-ai-tools-comparison.md",
        # Case studies (illustrative, not operational domains)
        "ai-listing-optimization.md", "ai-review-to-product.md",
        "f5-rpa-automation.md",
        # Social media line — documented gap, needs ecom-social skill
        "e1-instagram-facebook-ai-guide.md", "e2-youtube-ai-guide.md",
        "e3-xiaohongshu-ai-guide.md", "e4-pinterest-ai-guide.md",
        "e5-whatsapp-business-ai-guide.md", "e6-reddit-ai-guide.md",
        "e7-social-media-cross-channel.md",
    }
    # SELF-CHECK: every exempted filename MUST exist in src/
    import pathlib as _pl
    real_files = {p.name for p in _pl.Path(ROOT / "src").rglob("*.md")}
    phantom = [exc for exc in EXEMPT if exc not in real_files]
    if phantom:
        problems.append(f"S5 EXEMPT list contains {len(phantom)} phantom file(s): {', '.join(phantom)}")

    # Count prompts per chapter
    chapter_counts = {}
    prompts_path = ROOT / "dist" / "prompts.json"
    if prompts_path.exists():
        with open(prompts_path) as f:
            prompts = _json.load(f)
        for p in prompts:
            src = p.get("source", "")
            # Strip line number suffix, language prefix
            src = src.split(":")[0].replace("src/", "").replace("i18n/en/src/", "").replace("i18n/ja/src/", "")
            chapter = src.split("/")[-1] if "/" in src else src
            if chapter.endswith(".md"):
                chapter_counts[chapter] = chapter_counts.get(chapter, 0) + 1

    # Find covered chapters from playbook source references
    covered = set()
    for skill_dir in sorted(SKILLS.glob("*/")):
        if not skill_dir.is_dir():
            continue
        playbook = skill_dir / "references" / "playbook.md"
        if not playbook.exists():
            continue
        text = playbook.read_text(encoding="utf-8")
        for m in re.finditer(r"source:\s*(?:src/)?(?:[a-z0-9_-]+/)*([a-z0-9_-]+\.md)", text):
            covered.add(m.group(1))

    for ch, count in sorted(chapter_counts.items(), key=lambda x: -x[1]):
        if count < 5:
            continue
        if ch in EXEMPT:
            continue
        if ch.startswith("0-"):
            continue
        if ch not in covered:
            problems.append(f"{ch}: {count} prompts, no skill coverage")

    return problems


GATES = [
    ("S1", "skill frontmatter", gate_s1),
    ("S2", "skill traceability", gate_s2),
    ("S3", "skill existence", gate_s3),
    ("S4", "reference substance", gate_s4),
    ("M8", "manifest + SKILL.md", gate_m8),
    ("S5", "prompt coverage", gate_s5),
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
