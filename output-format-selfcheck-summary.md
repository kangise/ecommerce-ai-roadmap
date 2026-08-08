# Output-Format & Self-Check Blocks — Completion Summary

**Task**: Add `<output_format>` + `<self_check>` blocks (zh: `<输出格式>` `<自检>` / ja: `<出力形式>` `<セルフチェック>`) to ALL prompt code blocks in 4 chapters × 3 languages (12 files). Only additions; no existing content changed.

**Result**: 102 prompt blocks updated (34 per language), 1,206 lines added, 0 lines removed/deleted (verified via `git diff --numstat`). Fence balance verified even in all 12 files.

## Per-file counts

| Chapter | File (en / zh / ja) | Prompts updated |
|---|---|---|
| YouTube | `i18n/en/src/e-social-media/e2-youtube-ai-guide.md` · `src/e-social-media/e2-youtube-ai-guide.md` · `i18n/ja/src/e-social-media/e2-youtube-ai-guide.md` | 12 |
| Walmart | `i18n/en/src/d-platforms/d4-walmart-ai-guide.md` · `src/d-platforms/d4-walmart-ai-guide.md` · `i18n/ja/src/d-platforms/d4-walmart-ai-guide.md` | 10 |
| Images (A7) | `i18n/en/src/a-operators/a7-visual-content.md` · `src/a-operators/a7-visual-content.md` · `i18n/ja/src/a-operators/a7-visual-content.md` | 5 |
| Temu | `i18n/en/src/d-platforms/d5-temu-seller-guide.md` · `src/d-platforms/d5-temu-seller-guide.md` · `i18n/ja/src/d-platforms/d5-temu-seller-guide.md` | 7 |

## What was added (per prompt block, at end of code block before closing ```)

- `<output_format>` — exact deliverable structure: ordered labeled sections ①②③…, tables (columns/rows), field lists, counts (e.g. "exactly 5 options", "8 labeled parts", "6 sections in order").
- `<self_check>` — 3–5 task-specific, countable verification items ("Before delivering, verify each item and report the result"), matching the established convention in `src/d-platforms/shopify-ai-guide.md`.
- `<!-- ref: constraint_id -->` appended on check items matching `ontology/constraints.yaml` constraints (all 7 referenced IDs validated to exist).

## Constraint refs used (validated against constraints.yaml)

- `eu.ai_act.transparency` — 12× (AI-generated video/voice/avatar → EU AI Act Art. 50 labeling; YouTube review script, Shorts, ad script, A7 video script)
- `content.ai_generated.commercial_license` — 24× (commercial-license tooling + prompt-record retention; YouTube thumbnails, all A7 image/video prompts, Temu image prompt)
- `amazon.product_image.main.no_text_overlay` — 6× (A7 main-image prompts)
- `amazon.product_image.secondary_text.max_words` — 3× (A7 lifestyle scene)
- `amazon.product_image.secondary_title.max_words` + `amazon.product_image.secondary_subtitle.max_words` — 3× each (A7 infographic background)
- `ip.tro.risk_prevention` — 3× (Temu onboarding decision, IP-risk screening item)

## Scope notes

- Only genuine AI prompts received blocks. Informational/workflow/checklist/SOP code blocks (e.g. key-metrics lists, migration checklists, 30-day plans, description SEO template, Midjourney workflow descriptions) were intentionally left untouched, matching the precedent in the already-completed Shopify guide.
- A7's 3 one-line Midjourney library templates were included (they are prompt templates) with compact output-format/self-check blocks.
- Non-prompt blocks in each file were not modified; fence count per file unchanged except the added blocks' own fences (all even).
