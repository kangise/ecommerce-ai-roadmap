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

    # 5. SKILL.md — root entry point routing to domain skills
    root_skill = """---
name: ecommerce-ai-roadmap
description: OPC e-commerce AI infrastructure — 67-chapter knowledge base, domain ontology, and installable skills for one-person company operations.
---

# E-Commerce AI Infrastructure

## Skills

| Skill | Domain |
|-------|--------|
| `ecom-listing` | Listing optimization (Amazon, Shopify, TikTok Shop) |
| `ecom-advertising` | PPC campaign diagnosis and optimization |
| `ecom-inventory` | Inventory forecasting and replenishment |
| `ecom-compliance` | Compliance checks, HS codes, IP risk |
| `ecom-pricing` | Competitive pricing and profitability |
| `ecom-research` | Product research and market analysis |
| `ecom-applicability` | AI applicability assessment (should I use AI?) |

## Data

- `ontology.json` — Machine-readable domain model (80 entities, 184 constraints)
- `prompts.json` — All {len(prompts)} prompts, trilingual (zh/en/ja)
- `references/glossary.md` — Trilingual term definitions

## Usage

Load this directory as a skill library. Each domain skill in `skills/` is self-contained with its own constraints, playbook, and boundary conditions.
""".replace("{len(prompts)}", str(len(prompts)))
    (DIST / "SKILL.md").write_text(root_skill)

    print(f"dist/ built: {len(prompts)} prompts, {len(ontology)} ontology files, 7 skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
