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

    # 3. integration/ — copy adapter docs
    integration_src = ROOT / "integration"
    if integration_src.exists():
        shutil.copytree(integration_src, DIST / "integration", dirs_exist_ok=True)

    # 4. skills/ — recursive copy
    shutil.copytree(SKILLS, DIST / "skills", dirs_exist_ok=True)

    # 4b. knowledge/ — chapter index AND bodies for agent retrieval.
    #
    # The index alone shipped only a 300-char truncated summary per chapter.
    # First live acceptance proved that is not enough: an agent asked about
    # EU toy certification reported "dist/ has no EN 71" while
    # src/a-operators/a6-compliance.md does contain it. The content was in the
    # book, out of the package. Bodies ship here so a retrieval hit can be
    # followed to the actual text.
    (DIST / "knowledge").mkdir(exist_ok=True)
    chapters_dir = DIST / "knowledge" / "chapters"
    chapters_dir.mkdir(exist_ok=True)
    entities_data = ontology.get("entities", [])
    knowledge_index = []
    for md_path in sorted(SRC.rglob("*.md")):
        if md_path.name in ("SUMMARY.md", "README.md"):
            continue
        rel = str(md_path.relative_to(SRC))
        text = md_path.read_text(encoding="utf-8")

        # Extract title from first H1
        title_match = re.search(r"^#\s+(.+)", text, re.M)
        title = title_match.group(1) if title_match else rel

        # Extract first 200 chars of prose (skip headers, code, comments)
        prose = re.sub(r"```.*?```", " ", text, flags=re.S)
        prose = re.sub(r"<[^>]+>", " ", prose)
        prose = re.sub(r"#+\s+.*\n", " ", prose)
        prose = re.sub(r"<!--.*?-->", " ", prose, flags=re.S)
        prose = re.sub(r"\s+", " ", prose).strip()
        summary = prose[:300]

        # Find constraint references (<!-- ref: ... -->)
        constraint_refs = sorted(set(re.findall(r"<!--\s*ref:\s*([a-zA-Z0-9_.-]+)\s*-->", text)))

        # Find entity mentions (from ontology entities)
        entity_set = set()
        for e in entities_data:
            eid = e.get("id", "")
            label_zh = e.get("label", {}).get("zh", "")
            label_en = e.get("label", {}).get("en", "")
            for term in [eid, label_zh, label_en]:
                if term and len(term) > 2 and term in text:
                    entity_set.add(eid)
        key_entities = sorted(entity_set)[:15]

        # Extract boundary section summary
        boundary_match = re.search(r"## 什么时候这套不管用\n\n(.*?)(?:\n##|\Z)", text, re.S)
        boundary_summary = boundary_match.group(1).strip()[:200] if boundary_match else ""

        # Ship the body. Flatten the src/ tree into one filename so a chapter
        # id is a single token an agent can pass back through a tool call.
        chapter_id = rel[:-3].replace("/", "__") if rel.endswith(".md") else rel.replace("/", "__")
        body_rel = f"chapters/{chapter_id}.md"
        (chapters_dir / f"{chapter_id}.md").write_text(text, encoding="utf-8")

        knowledge_index.append({
            "id": chapter_id,
            "title": title,
            "path": rel,
            "body_path": body_rel,
            "body_chars": len(text),
            "summary": summary,
            "key_entities": key_entities,
            "constraint_refs": constraint_refs,
            "boundary_summary": boundary_summary,
        })

    with open(DIST / "knowledge" / "index.json", "w", encoding="utf-8") as f:
        json.dump(knowledge_index, f, ensure_ascii=False, indent=2)

    # query_guide.md
    query_guide = """# Knowledge Index Usage Guide

## For Agent Consumers

The `index.json` contains structured metadata for all {0} source chapters,
and `chapters/` contains their full text.

**The index is a router, not an answer.** Each entry's `summary` is the first
300 characters only. Never answer a factual question from `summary` alone and
never conclude "the package does not cover X" from an index miss — open
`body_path` and read the chapter first. A prior acceptance run reported
"no EN 71 in the package" while the chapter body did contain it.

Use it to answer domain questions:

1. **Question**: "What is Buy Box?"
   → Search index for `key_entities` containing "buy_box" or "price"
   → Return the matching chapter's `title` + `summary`
   → Also check `constraint_refs` for related constraints in `ontology.json`

2. **Question**: "What are Amazon listing requirements?"
   → Search for chapters with "amazon" and "listing" in constraints
   → Return `constraint_refs` and `boundary_summary` for context

3. **Question**: "Should I use AI for demand forecasting?"
   → Search for "inventory" or "forecast" in key_entities
   → Return `boundary_summary` — this is what the ecom-applicability skill uses

## Structure

Each entry:
- `id`: Chapter id — src path with `/` flattened to `__`, no extension
- `title`: Chapter title (first H1)
- `path`: Relative path from src/
- `body_path`: Full chapter text, relative to `knowledge/`. **Read this.**
- `body_chars`: Length of the body, for cost estimation before reading
- `summary`: First 300 characters of prose — routing hint only
- `key_entities`: Entity IDs from ontology that appear in this chapter
- `constraint_refs`: `<!-- ref: -->` markers found in this chapter
- `boundary_summary`: First 200 chars of "When this doesn't work" section

## Full-text search

`summary` covers 300 of ~35,000 characters per chapter, so a keyword absent
from the index is usually still present in the body. Grep `chapters/` before
concluding anything is missing.
""".format(len(knowledge_index))
    (DIST / "knowledge" / "query_guide.md").write_text(query_guide)

    # 5. references/
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

    # Scale facts, derived — never hand-written. These sat hardcoded as
    # "80 entities / 184 constraints / 67 chapters" through several releases
    # because D2 only scans repo-root READMEs, not generated dist/ files.
    n_entities = len(ontology.get("entities", []) or [])
    n_relations = len(ontology.get("relations", []) or [])
    n_constraints = len(ontology.get("constraints", []) or [])
    n_processes = len(ontology.get("processes", []) or [])
    n_platforms = len(ontology.get("platforms", []) or [])
    n_chapters = len(knowledge_index)
    n_body_chars = sum(e.get("body_chars", 0) for e in knowledge_index)

    root_skill = f"""---
name: opc-ecommerce-infrastructure
description: >
  OPC e-commerce operations infrastructure. Provides a {n_chapters}-chapter knowledge base,
  {n_entities}-entity domain ontology, {n_constraints} platform constraints, {len(capabilities)} domain skills,
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

1. **Domain Skills** — {len(capabilities)} callable skills covering the full e-commerce operating chain:
   - `ecom-listing` — Listing creation and optimization (Amazon, Shopify, TikTok Shop)
   - `ecom-advertising` — PPC campaign diagnosis and optimization
   - `ecom-inventory` — Demand forecasting and replenishment planning
   - `ecom-compliance` — Compliance checks, HS codes, IP risk screening
   - `ecom-pricing` — Competitive pricing and profitability analysis
   - `ecom-research` — Product research and market opportunity discovery
   - `ecom-applicability` — AI readiness assessment (should I use AI for X?)
   - `ecom-customer-service` — Review responses, appeals, refund/return support, FAQ, and CS KPIs

2. **Domain Ontology** — Machine-readable domain model (`ontology.json`):
   - {n_entities} entities with attributes (listing, campaign, inventory, compliance, etc.)
   - {n_relations} relationships between entities
   - {n_constraints} platform-specific constraints across {n_platforms} marketplaces
   - {n_processes} formal business processes (new product launch, replenishment, compliance review, etc.)

3. **Prompt Library** — `prompts.json` contains {prompt_count} production prompts across 3 languages.
   Each prompt includes self-check blocks with constraint references.

4. **Knowledge Base** — `knowledge/index.json` indexes all {n_chapters} chapters;
   `knowledge/chapters/` holds their full text ({n_body_chars:,} characters).

   The index carries a 300-character summary per chapter. That is a routing hint,
   not the content. **Never conclude the package lacks a topic from an index
   miss** — search or read the bodies first. A prior acceptance run reported
   "no EN 71 content" while the compliance chapter body did contain it.

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

## Answering Knowledge Questions

Before saying the package does not cover something:
1. `knowledge/index.json` — scan `title`, `key_entities`, `summary`
2. Grep `knowledge/chapters/` for the term — summaries cover under 1% of the text
3. Open the matching `body_path` and read it

Only after all three come up empty should you say the package lacks that content.

## Data Files

- `ontology.json` — Domain model (entities, relations, constraints, processes)
- `prompts.json` — {prompt_count} prompts, trilingual with constraint references
- `knowledge/index.json` — Chapter index with entity and constraint cross-references
- `knowledge/chapters/` — Full text of all {n_chapters} chapters
- `references/glossary.md` — Trilingual term definitions

## Integration

See `integration/` for framework-specific setup guides.
"""
    (DIST / "SKILL.md").write_text(root_skill)

    # 6. README.md — human quickstart
    readme = f"""# OPC E-Commerce AI Infrastructure

> Plug-and-play e-commerce operations capability for AI agents.

## Quick Start (30 seconds)

1. **Point your agent at this directory.** The entry point is `SKILL.md`.
2. Your agent now has {len(capabilities)} domain skills (listing, advertising, inventory, compliance, pricing, research, applicability, customer-service).
3. Ask: *"Help me write an Amazon listing"* — agent routes to `ecom-listing`, loads platform constraints, executes.

## What's Inside

| Component | Contains |
|-----------|----------|
| `SKILL.md` | Agent system prompt with routing rules |
| `ontology.json` | {n_entities} entities, {n_relations} relations, {n_constraints} constraints, {n_processes} processes |
| `prompts.json` | {len(prompts)} production prompts (zh/en/ja) |
| `knowledge/index.json` | {n_chapters}-chapter index with entity references |
| `knowledge/chapters/` | Full chapter text ({n_body_chars:,} chars) |
| `skills/` | {len(capabilities)} domain skills with manifests, playbooks, constraints |
| `integration/` | Framework-specific setup guides |

## How It Works

```
User: "Help me write a listing"
  → SKILL.md routing: "listing" → ecom-listing
  → load skills/ecom-listing/manifest.yaml (input schema)
  → load skills/ecom-listing/references/constraints.md (platform rules)
  → select prompt from skills/ecom-listing/references/playbook.md
  → execute, verify with self-check, deliver
```

## For Agent Developers

See `integration/mcp.md` for MCP server setup.
See each skill's manifest (skills/<skill>/manifest.yaml) for input/output schemas.
See `knowledge/query_guide.md` for retrieval patterns.
"""
    (DIST / "README.md").write_text(readme)

    # 7. INTEGRATION.md — framework guide index
    integration_md = """# Integration Guides

This package is framework-agnostic. Choose your integration path:

| Framework | Guide | Why |
|-----------|-------|-----|
| MCP (Model Context Protocol) | [integration/mcp.md](integration/mcp.md) | Natural fit: resources + prompts + tools |
| Direct file loading | [integration/mcp-system-prompt.md](integration/mcp-system-prompt.md) | No server needed — load files directly |

## Which Framework?

- **MCP** — Best for Claude Desktop, Cursor, and any MCP-compatible client
- **Direct loading** — Works with any agent that can read files and follow instructions

## Adding a New Framework

1. Create `integration/<framework>.md` with setup instructions
2. Add a system-prompt file with the adapted system prompt
3. Document any framework-specific routing or tool call format differences
"""
    (DIST / "INTEGRATION.md").write_text(integration_md)

    print(f"dist/ built: {len(prompts)} prompts, {len(ontology)} ontology files, {len(capabilities)} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
