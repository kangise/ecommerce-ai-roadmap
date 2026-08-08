# Contributing to E-Commerce AI Roadmap

## Quick Start

```bash
python3 scripts/verify_all.py    # Run all 24 gates — must be 0
```

## Extension Paths

| I want to… | Command | Then |
|------------|---------|------|
| Add a chapter | `python3 scripts/new_chapter.py <path> <title>` | Fill content → add boundary section → run `verify_all.py` |
| Add a platform | `python3 scripts/new_platform.py <id> <name>` | Fill content → add constraints to `ontology/constraints.yaml` → run `verify_all.py` |
| Add a prompt | `python3 scripts/new_prompt.py <chapter> <purpose>` | Fill 6 blocks → self-check references constraints with `<!-- ref: id -->` → run `verify_all.py` |
| Change a constraint | Edit `ontology/constraints.yaml` | `O5` gate lists all files needing updates → fix them → run `verify_all.py` |
| Add a skill domain | Follow Phase C structure in `skills/` | `S1/S2/S3` gates will verify |

**Every path ends the same way: `python3 scripts/verify_all.py` must return 0.**

## Gate Reference (24 gates)

| Group | Gates | Script |
|-------|-------|--------|
| Structure | anchors, xanchors, links, python, parity | verify_content.py |
| Content | M1, M2, M4, M5, M6, M7, N1, N2, N3, N4, N5, N6 | verify_content.py |
| Ontology | P0, O1, O2, O3, O4, O5 | verify_ontology.py |
| Skills | S1, S2, S3 | verify_skills.py |
| Dist | N7 | build_dist.py (via verify_all.py) |

## Fact Freshness (M7)

All `verified: YYYY-MM` facts have an 18-month shelf life. The M7 gate turns red when facts expire.

**Note:** 63 facts were verified in 2026-08 and will all expire simultaneously in 2028-02. Plan a re-verification cycle before then, or accept the cliff and run a dedicated verification loop in 2028-02.

## Trilingual Rules

- All content must exist in `src/`, `i18n/en/src/`, and `i18n/ja/src/`
- Parity gate checks file existence and structure fingerprint
- Prompt tags: zh `<自检>`/`<输出格式>`, en `<self_check>`/`<output_format>`, ja `<セルフチェック>`/`<出力形式>`
- Constraint refs (`<!-- ref: id -->`) must be included in all three languages

## Commit Checklist

1. Run `python3 scripts/verify_all.py` — must be 0
2. Run `python3 scripts/build_dist.py` and commit the updated `dist/`
3. New external links require `python3 scripts/verify_content.py --probe-links`

## Scaffolding Scripts

- `scripts/new_chapter.py <path> <title>` — trilingual skeleton + SUMMARY + boundary section
- `scripts/new_platform.py <id> <name>` — above + platforms.yaml entry + skill index
- `scripts/new_prompt.py <chapter> <purpose>` — 6-block skeleton, trilingual, with self-check placeholder
- `scripts/new_constraint.py` — interactive constraint writer with ref location hints
