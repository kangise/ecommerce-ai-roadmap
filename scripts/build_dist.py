#!/usr/bin/env python3
"""Build the distributable agent package from source + ontology + skills.

Reads the single source of truth (src/ + ontology/ + skills/) and produces
dist/ — the installable agent artifact. Only ADDITIVE: regenerates dist/
completely on each run.

Usage:
  python3 scripts/build_dist.py
"""

import json
import pathlib
import shutil
import sys
import yaml
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SRC = ROOT / "src"
ONT = ROOT / "ontology"
SKILLS = ROOT / "skills"

FM_PATTERN = re.compile(r"^---\s*\n(.*?)\n---", re.S)


def main():
    # Clean and recreate
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / "references").mkdir(exist_ok=True)

    # 1. ontology.json — machine-readable domain model
    ontology = {}
    for yf in ["entities.yaml", "relations.yaml", "constraints.yaml", "platforms.yaml", "processes.yaml"]:
        path = ONT / yf
        if path.exists():
            ontology[yf.replace(".yaml", "")] = yaml.safe_load(path.read_text(encoding="utf-8"))
    (DIST / "ontology.json").write_text(
        json.dumps(ontology, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 2. prompts.json — all prompts, trilingual
    prompts = []
    prompt_tags = {
        "src": ["<角色>", "<任务>", "<数据纪律>", "<文案纪律>", "<输入数据边界>", "<自检>", "<输出格式>"],
        "i18n/en/src": ["<role>", "<task>", "<data_discipline>", "<copy_discipline>", "<input_boundary>", "<self_check>", "<output_format>"],
        "i18n/ja/src": ["<役割>", "<タスク>", "<データ規律>", "<コピー規律>", "<入力データ境界>", "<セルフチェック>", "<出力形式>"],
    }
    for tree in ("src", "i18n/en/src", "i18n/ja/src"):
        tags = prompt_tags[tree]
        for md in sorted((ROOT / tree).rglob("*.md")):
            if md.name in ("SUMMARY.md", "README.md"):
                continue
            text = md.read_text(encoding="utf-8")
            for m in re.finditer(r"```[a-z]*\n(.*?)```", text, re.S):
                body = m.group(1)
                found_tags = sum(1 for t in tags if t in body)
                if found_tags >= 2:
                    prompts.append({
                        "source": f"{tree}/{md.relative_to(ROOT / tree)}",
                        "body": body,
                        "language": {"src": "zh", "i18n/en/src": "en", "i18n/ja/src": "ja"}[tree],
                    })
    (DIST / "prompts.json").write_text(
        json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 3. skills/ — recursive copy
    shutil.copytree(SKILLS, DIST / "skills", dirs_exist_ok=True)

    # 4. references/
    for ref_name in ["glossary.md", "boundaries.md"]:
        src_path = SRC / "resources" / ref_name
        if src_path.exists():
            shutil.copy2(src_path, DIST / "references" / ref_name)

    # 5. SKILL.md — agent entry point with routing generated from manifests
    # Load manifests to build routing table
    capabilities = []
    routing_rules = []
    for skill_dir in sorted(SKILLS.iterdir()):
        if not skill_dir.is_dir():
            continue
        mf_path = skill_dir / "manifest.yaml"
        if not mf_path.exists():
            continue
        manifest = yaml.safe_load(mf_path.read_text(encoding="utf-8"))
        sid = manifest.get("name", skill_dir.name)
        desc = manifest.get("description", "")
        capabilities.append(f"  - {sid}: {desc}")
        # Build routing rule from triggers
        triggers = manifest.get("triggers", {})
        keywords = triggers.get("keywords", [])
        intent = triggers.get("intent", "")
        if keywords:
            keyword_pattern = "|".join(keywords[:15])  # Top 15 keywords for compactness
            routing_rules.append(f"  - trigger: \"{keyword_pattern}\"\n    skill: {sid}")
        if intent:
            routing_rules.append(f"  - intent: {intent}\n    skill: {sid}")

    capabilities_yaml = "\n".join(capabilities)
    routing_yaml = "\n".join(routing_rules)
    prompt_count = len(prompts)  # Total across all languages

    root_skill = f"""---
name: opc-ecommerce-infrastructure
description: >
  OPC e-commerce operations infrastructure. Provides a 67-chapter knowledge base,
  80-entity domain ontology, 184 platform constraints, 7 domain skills,
  and {prompt_count} production prompts (trilingual zh/en/ja).
  Load this package to give any agent native cross-border e-commerce operational capability.
capabilities:
{capabilities_yaml}
routing:
{routing_yaml}
---

# OPC E-Commerce Operations Agent

You are an e-commerce operations agent powered by the OPC (One Person Company) infrastructure. You have access to:

## Your Capabilities

1. **Domain Skills** — 7 callable skills covering the full e-commerce operating chain:
   - `ecom-listing` — Listing creation and optimization (Amazon, Shopify, TikTok Shop)
   - `ecom-advertising` — PPC campaign diagnosis and optimization
   - `ecom-inventory` — Demand forecasting and replenishment planning
   - `ecom-compliance` — Compliance checks, HS codes, IP risk screening
   - `ecom-pricing` — Competitive pricing and profitability analysis
   - `ecom-research` — Product research and market opportunity discovery
   - `ecom-applicability` — AI readiness assessment (should I use AI for X?)

2. **Domain Ontology** — Machine-readable domain model (`ontology.json`):
   - 80 entities with attributes (listing, campaign, inventory, compliance, etc.)
   - 78 relationships between entities
   - 184 platform-specific constraints (Amazon, Shopify, TikTok Shop, etc.)
   - 8 formal business processes (new product launch, replenishment, compliance review, etc.)

3. **Prompt Library** — `prompts.json` contains {prompt_count} production prompts across 3 languages.
   Each prompt includes self-check blocks with constraint references.

4. **Knowledge Index** — `knowledge/index.json` covers all 67 source chapters with entity and constraint cross-references.

## How to Route Requests

Use the frontmatter `routing:` rules to determine which skill handles a user request.
Match triggers (keywords) against the user's query. When there is ambiguity, ask the user to clarify.

## How to Use a Skill

When a skill is selected:
1. Read `skills/<skill>/manifest.yaml` for input/output schema
2. Read `skills/<skill>/references/constraints.md` for platform rules
3. Select a prompt template from `skills/<skill>/references/playbook.md`
4. Read `skills/<skill>/references/boundaries.md` to check when NOT to use this skill
5. Execute the prompt, verify with the self-check block, and deliver results

## Data Files

- `ontology.json` — Domain model (entities, relations, constraints, processes)
- `prompts.json` — {prompt_count} prompts, trilingual with constraint references
- `knowledge/index.json` — Chapter index with entity and constraint cross-references
- `references/glossary.md` — Trilingual term definitions

## Integration

See `integration/` for framework-specific setup guides.
"""
    (DIST / "SKILL.md").write_text(root_skill)

    print(f"dist/ built: {len(prompts)} prompts, {len(ontology)} ontology files, 7 skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
