# Contributing to ecommerce-ai-skills

## Quick Start

```bash
python3 scripts/verify_all.py    # Run all gates — must be 0 (except documented residuals)
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

## Gate Reference (42 gates, 14 groups)

| Group | Gates | Script |
|-------|-------|--------|
| Structure | anchors, xanchors, links, python, parity | verify_content.py |
| Content | M1, M2, M4, M5, M6, M7, N1, N2, N3, N4, N5, N6 | verify_content.py |
| Ontology | P0, O1, O2, O3, O4, O5 | verify_ontology.py |
| Skills | S1, S2, S3, S4, S5, M8 | verify_skills.py |
| Knowledge | K1 | verify_all.py --k1 |
| K2 Bodies | K2 | verify_all.py --k2 |
| Routing | R1 | verify_all.py --r1 |
| R1b Frags | R1b | verify_all.py --r1b |
| R2 Natural | R2 | verify_all.py --r2 |
| S6 Attrib | S6 | verify_all.py --s6 |
| Integration / Docs | I1, D1, D2 | verify_all.py --i1/--d1/--d2 |
| Sustain | E1, E2, E3 | verify_all.py --sustain |
| Dist | N7 | build_dist.py (via verify_all.py) |

Every gate here was added because something broke. When a live acceptance run
finds a failure the gates could not see, add a gate that catches it — do not
relax the acceptance standard.

### K2: the knowledge layer must ship bodies

`dist/knowledge/index.json` carries a 300-character summary per chapter. That
is under 1% of a chapter's text. For several releases `dist/` shipped the index
and no bodies, and the first live acceptance run concluded the package had no
EN 71 / EU toy-safety content — while `src/a-operators/a6-compliance.md` did
contain it. Every reported "content hole" had to be re-checked against `src/`
before anyone could tell which were real.

`K2` fails if any index entry lacks `body_path`, points at a missing file, or
carries a body no longer than its own summary or materially shorter than the
`src/` original.

## Fact Freshness (M7)

All `verified: YYYY-MM` facts have an 18-month shelf life. The M7 gate turns red when facts expire.

**Note:** all 386 `verified` facts (68 in prose + 318 in the ontology) carry 2026-08 and expire together in 2028-02. Plan a re-verification cycle before then, or accept the cliff and run a dedicated verification loop in 2028-02.

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

The `N6` gate catches files where the three language trees carry different
numbers of prompt structure blocks, caused by translations evolving at
different speeds (zh leads, en/ja follow).

Status: **closed** (N6 = 0). Two exemptions remain, `f1` and `f2`; `f2` teaches
the prompt structure itself, so it contains intentional variation. Do not add
exemptions to make this green — an exemption whose filename does not exist in
`src/` is itself a gate failure.

### R1: Routing Test Measures Documentation Diversity, Not Routing Accuracy

The `tests/routing-cases.yaml` test suite verifies that each skill's keyword triggers in `manifest.yaml` are diverse enough for an LLM agent to route correctly. **Keyword-matching against fixed test cases is NOT the real router** — a human or LLM reads the `routing:` table in `dist/SKILL.md` to make actual routing decisions.

The anti-degeneration check exists because this suite has degenerated twice. Both times it looked healthy:

- The first suite was 39 cases, **all 39 of which literally contained a trigger keyword** from their expected skill. A substring matcher matching strings that contain the substring proves nothing; `R1 = 0` carried no information.
- The fix added a `natural: true` field to cases and counted how many carried it. That is a **self-declared flag**, not a measurement — all 27 cases marked `natural` still contained literal triggers. A check that reads a hand-typed boolean cannot detect the property it was created to detect.

The check now **computes** the literal hit ratio, and the threshold is **50%** — at least half the suite must be phrased without the domain keyword in it, the way a real seller writes. A 95% threshold (the previous value) permits a suite that is almost entirely tautological, which is exactly the failure being guarded against.

There is a second way to defeat this, also tried: instead of writing cases containing the keywords, copy phrases out of the cases *into* the manifest triggers. Ten such fragments were found and removed (`这个类目`, `还能不能进`, `机器判断`, `花了钱`, `写到页面上`, `三个市场`, …). They are not domain vocabulary — no other e-commerce document would contain them. **A trigger keyword must be a word the domain uses, not a phrase lifted from a test case.**

### Why R1 does not reach 0

`R1` currently reports **19 errors out of 117**. This is expected and is not a defect to be closed by adding more keywords.

The matcher in `verify_all.py` does substring matching. Roughly a sixth of the suite is phrased the way sellers actually speak — "这个月花了三千块钱一单没出", "现在入场是不是已经太晚了" — where the intent is clear to a reader but no domain noun appears in the text. Closing that gap requires semantic matching, which this gate deliberately does not attempt.

Chasing these cases by adding keywords is the back-copying failure above wearing a different hat: it would raise the literal ratio, shrink the informative part of the suite, and still not generalize to the next phrasing.

**What R1 is for**: catching trigger lists that are too thin or too narrowly aligned with the tests. The residual error count is the honest distance between substring matching and understanding — it is a reported number, not a target.

**Real routing verification** — confirming an LLM routes correctly reading `dist/SKILL.md` — is a manual acceptance item, because the real router is the consuming model, not this script.

Status: **documented, not closed** (`R1 ≈ 19/117`). Anti-degeneration threshold: literal hit ratio must be ≤ 50% (currently 43%).

The residual rose from 10 to 19 in v4 Sprint 2, and that is the honest direction. 33 sentence-fragment triggers were removed (a batch of them had been hidden in `FRAG_ALLOWLIST` under the label "verified as real domain vocabulary" — 拍板, 能信吗, 靠谱吗, 清掉 …, which no e-commerce document contains). Removing them dropped the false matches those fragments were producing, so cases that had "passed" by matching a lifted phrase now correctly show as misroutes. Real domain vocabulary (备货, 断货, ACOS, 盈亏平衡, 类目审核 …) was added to recover what could be recovered honestly; the rest — 「这个月花了三千块钱一单没出」, 「旺季前要备多少货才不会断」 — carry no domain noun at all and are the substring-vs-semantics gap, not a fixable keyword miss.

**Do not close this residual by re-adding fragments.** R1b now blocks the manifest side and R2 blocks the test side (see below).

### R1 hard rules — never change these to make gates green

Two rules on `R1` exist because both were violated in the same commit that
declared "R1 = 0":

1. **The anti-degeneration threshold is 50%.** Do not raise it. A 95% threshold
   permits a suite that is 94% tautological, which is the failure the check
   exists to catch. If the literal ratio rises past 50%, the fix is to add
   non-literal test cases and to check whether recent triggers were lifted from
   test-case wording (see rule 2). It is **not** to raise the threshold.

2. **Manifest triggers must be domain vocabulary.** A trigger is a word that
   would appear in another e-commerce document — not a phrase chopped out of a
   test case to make the substring matcher hit. Gate `R1b` enforces this by
   flagging triggers containing pronouns, question tails, hedges, or specific
   residues actually observed in past back-copying (「怎么办」/「要不要」/「跑出来」/…).

   Legitimate question-form triggers exist (`AI能做吗`, `该不该用AI` — they carry
   the domain noun `AI`). They live in `FRAG_ALLOWLIST` in `verify_all.py`,
   listed explicitly one by one. Add entries there only after confirming the
   keyword is not lifted from a test case.

**When `R1` reports errors, the correct response is one of:**

- Add domain vocabulary to manifest triggers (real terms — `否定关键词`, `补货点`, `一星差评`, not `怎么办`).
- Add non-literal test cases so the suite exercises phrasings the router should catch.
- Accept the residual and report it. `R1` is documented as not-closed; the residual is a reported metric, not a target.

**Not permitted:** raising the threshold, adding fragments to triggers, adding fragments to `FRAG_ALLOWLIST` without a real domain noun, or gaming test cases to include literal keywords.

### R1b: sentence-fragment triggers

`R1b` counts manifest triggers that look like phrases lifted from a test case
rather than domain vocabulary. Target 0. See rule 2 above. Implementation in
`verify_all.py` (`FRAG_MARKERS`, `FRAG_ALLOWLIST`, `_is_fragment`).

### R2: natural-language routing probe

`routing-cases.yaml` (the fixed suite R1 runs) co-evolves with the triggers, so
its literal ratio is a floor, not a ceiling. `R2` runs a separate set,
`tests/routing-cases-natural.yaml`, written **query-first without looking at the
triggers**, and requires its literal-hit ratio to stay **< 40%** — stricter than
R1's 50%, because this set is the harder, phrasing-first probe. Target 0 (i.e.
ratio under threshold). Both R1 and R2 fold through the same `_normalize` the MCP
server uses, so a gate pass means the real router would match the same way.

## Scaffolding Scripts

- `scripts/new_chapter.py <path> <title>` — trilingual skeleton + SUMMARY + boundary section
- `scripts/new_platform.py <id> <name>` — above + platforms.yaml entry + skill index
- `scripts/new_prompt.py <chapter> <purpose>` — 6-block skeleton, trilingual, with self-check placeholder
- `scripts/new_constraint.py` — interactive constraint writer with ref location hints

### Chinese trigger coverage (documented, not closed)

The v4 Sprint 5 independent acceptance run found manifest `triggers.keywords`
lean on Chinese: several queries (「标题」, 「差评」, 「补货点」, 「视频广告」) route
correctly by the LLM reading `dist/SKILL.md` semantically, but a pure
keyword/substring router would miss them because the literal trigger is the
English term (title, negative review, reorder point, advertising).

The real router is the consuming model, so this is not a live failure — but the
manifests should carry the Chinese domain vocabulary too. Widening them is a
separate round, and every added trigger must still pass `R1b`: add domain words
(标题, 差评, 补货, 广告, 合规, 产品页), never sentence fragments.

Status: **documented, not closed**.
