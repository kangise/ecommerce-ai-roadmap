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

## Known Limitations

### N6: Trilingual Prompt Structure Drift

The `N6` gate reports ~46 files where the three language trees have different numbers of prompt structure blocks. This is caused by translations evolving at different speeds (zh leads, en/ja follow). The gate correctly reports this drift. **Closing N6 requires a dedicated translation alignment loop** — adding missing prompt blocks to en/ja trees where zh has prompts the others lack.

Status: **documented, not closed** (N6 ≈ 46 as of 2026-08-08).

### R1: Routing Test Measures Documentation Diversity, Not Routing Accuracy

The `tests/routing-cases.yaml` test suite verifies that each skill's keyword triggers in `manifest.yaml` are diverse enough for an LLM agent to route correctly. **Keyword-matching against fixed test cases is NOT the real router** — a human or LLM reads the `routing:` table in `dist/SKILL.md` to make actual routing decisions.

The anti-degeneration check exists because this suite has degenerated twice. Both times it looked healthy:

- The first suite was 39 cases, **all 39 of which literally contained a trigger keyword** from their expected skill. A substring matcher matching strings that contain the substring proves nothing; `R1 = 0` carried no information.
- The fix added a `natural: true` field to cases and counted how many carried it. That is a **self-declared flag**, not a measurement — all 27 cases marked `natural` still contained literal triggers. A check that reads a hand-typed boolean cannot detect the property it was created to detect.

The check now **computes** the literal hit ratio, and the threshold is **50%** — at least half the suite must be phrased without the domain keyword in it, the way a real seller writes. A 95% threshold (the previous value) permits a suite that is almost entirely tautological, which is exactly the failure being guarded against.

There is a second way to defeat this, also tried: instead of writing cases containing the keywords, copy phrases out of the cases *into* the manifest triggers. Ten such fragments were found and removed (`这个类目`, `还能不能进`, `机器判断`, `花了钱`, `写到页面上`, `三个市场`, …). They are not domain vocabulary — no other e-commerce document would contain them. **A trigger keyword must be a word the domain uses, not a phrase lifted from a test case.**

### Why R1 does not reach 0

`R1` currently reports **11 errors out of 60**. This is expected and is not a defect to be closed by adding more keywords.

The matcher in `verify_all.py` does substring matching. Roughly a third of the suite is phrased the way sellers actually speak — "这个月花了三千块钱一单没出", "现在入场是不是已经太晚了" — where the intent is clear to a reader but no domain noun appears in the text. Closing that gap requires semantic matching, which this gate deliberately does not attempt.

Chasing these cases by adding keywords is the back-copying failure above wearing a different hat: it would raise the literal ratio, shrink the informative part of the suite, and still not generalize to the next phrasing.

**What R1 is for**: catching trigger lists that are too thin or too narrowly aligned with the tests. The residual error count is the honest distance between substring matching and understanding — it is a reported number, not a target.

**Real routing verification** — confirming an LLM routes correctly reading `dist/SKILL.md` — is a manual acceptance item, because the real router is the consuming model, not this script.

Status: **documented, not closed** (`R1 ≈ 11/60`). Anti-degeneration threshold: literal hit ratio must be ≤ 50% (currently 35%).

### ecom-social Skill Gap

The 7 social-media chapters (e1-e7) have ~50 prompts with no dedicated skill. They are currently exempt from S5 coverage checks. A combined `ecom-social` skill should be created covering Instagram, YouTube, Pinterest, Reddit, WhatsApp, Xiaohongshu, and cross-channel strategy.

Status: **documented, not started**.

## Scaffolding Scripts

- `scripts/new_chapter.py <path> <title>` — trilingual skeleton + SUMMARY + boundary section
- `scripts/new_platform.py <id> <name>` — above + platforms.yaml entry + skill index
- `scripts/new_prompt.py <chapter> <purpose>` — 6-block skeleton, trilingual, with self-check placeholder
- `scripts/new_constraint.py` — interactive constraint writer with ref location hints
