# Ontology: E-Commerce Domain Model

> Schema version: 1.0
> Last updated: 2026-08-08

## What this is

A machine-readable shared contract for the e-commerce domain. Every entity, constraint, platform difference, and process defined here is backed by a `source:` pointer to a specific section of the 67-chapter knowledge base. **Nothing here is invented — everything is extracted.**

## Why it exists

Without a formal domain model, multiple agents working with this knowledge base will independently reinterpret the same prose and produce inconsistent representations. One agent's "listing" won't match another's. Constraints like "Amazon title ≤ 200 characters" get hardcoded into prompts and drift apart when Amazon changes the rule.

The ontology is the contract between:
- **Knowledge** (the prose chapters) — what the domain looks like
- **Capabilities** (prompts and skills) — what agents do
- **State** (user data) — what a specific business has

## Files

| File | What it holds |
|------|--------------|
| `entities.yaml` | Entities: what things exist in the domain, their attributes, and type signatures |
| `relations.yaml` | Relations: how entities connect (belongs_to, targets, consumes, produces...) |
| `constraints.yaml` | Constraints: platform-specific rules (max length, format, forbidden values) |
| `platforms.yaml` | Platforms: every marketplace with its source chapters and first-class status |
| `processes.yaml` | Processes: formal workflows (new product launch → listing → campaign...) |
| `_unresolved.md` | Dumping ground: candidate entities/constraints we are not sure about |

## Schema rules

1. **Every entry must have `source:` pointing to a concrete chapter anchor.** Gate `O1` enforces this.
2. **Platform rates and thresholds must carry `verified: YYYY-MM`.** Gate `M7` checks expiry.
3. **Nothing is invented.** If you are unsure about an entity, put it in `_unresolved.md` instead of guessing.

## Editing workflow

1. Extract from chapters → add to the appropriate YAML file
2. Run `python3 scripts/verify_ontology.py` — O1/O3/O4 must be 0
3. For constraints that affect prompts: add `<!-- ref: constraint_id -->` markers in the prompt body (see Phase B in the plan)
4. Commit

## Adding a new entity

```yaml
- id: asin
  label: {zh: ASIN, en: ASIN, ja: ASIN}
  definition:
    zh: Amazon 标准识别编号，每个上架商品有唯一 ASIN
    en: Amazon Standard Identification Number
    ja: Amazon 標準識別番号
  attributes: []
  source:
    - src/a-operators/a2-listing-optimization.md#...
```

## Gate reference

| Gate | Script | What it checks |
|------|--------|---------------|
| P0 | verify_ontology.py | Phase 0 complete: N1 trilingual + amazon in platforms.yaml + ontology skeleton exists |
| O1 | verify_ontology.py | Every `source:` pointer resolves to a real anchor |
| O2 | verify_ontology.py | High-frequency nouns that might be entities are tracked |
| O3 | verify_ontology.py | Every platform with a chapter is in platforms.yaml |
| O4 | verify_ontology.py | glossary.md is in sync with ontology entries |
| O5 | verify_ontology.py | `<!-- ref: -->` markers in prompts match constraint values |
