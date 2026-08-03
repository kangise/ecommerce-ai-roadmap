# Model Matrix

> **Verified**: 2026-07-31
> **This page is the single source of truth for model ids across the whole book.** Every other chapter describes *capability tiers* and links back here for the actual model names.

---


<!-- claims: verified 2026-08 -->

> Tool prices in this section were checked in 2026-08. SaaS pricing moves often — verify on the vendor's own site before you commit.

## Why chapters don't name specific models

The methodology in this knowledge base has a half-life measured in years. Model ids have a half-life measured in months. Two examples from the same week this page was verified: OpenAI cut the Luna tier by 80% and the Terra tier by 20% on 2026-07-30; Google shipped three new Flash models on 2026-07-21. Any chapter that hard-codes a model id becomes wrong within a quarter.

So the convention here is:

- Chapters say **"use a frontier-tier model to cluster competitor complaints"**, not "use model X to cluster competitor complaints"
- Model ids, prices, and context limits — the perishable facts — live only on this page, with a verification date
- On a new generation you edit one file, once per language, instead of touching 60+ chapters

The one exception is [The Evolution of AI](../0-foundations/f1-ai-evolution.md). That chapter is about history; GPT-3 and Claude 2 are its subject matter, not a recommendation, so those names stay.

---

## The four capability tiers

Tier definitions are stable. You can build a tech-selection process on them without revisiting it every time a vendor ships.

| Tier | When to reach for it | Typical e-commerce tasks | Relative cost |
|------|---------------------|-------------------------|---------------|
| **T1 Frontier** | Being wrong is expensive, or the task needs multi-step reasoning | Compliance risk assessment, patent-workaround analysis, annual sourcing strategy, complex attribution modeling | baseline ×10 |
| **T2 Workhorse** | The default for everyday production work | Bulk listing generation, ad copy, review clustering, support drafts | baseline ×3 |
| **T3 Fast** | Simple task, very high volume, latency-sensitive | Review sentiment labeling, category assignment, field extraction, first-pass translation | baseline ×1 |
| **T4 Local** | Data cannot leave your infrastructure, or sustained high volume needs to be cheap | Order data containing customer info, internal knowledge-base Q&A, offline batch jobs | electricity + one-time hardware |

**Rule of thumb**: prove the workflow on T1 and generate a batch of "gold answers," then move the volume to T2/T3 and use those gold answers as your acceptance test. Most e-commerce tasks settle on T2. Starting your prompt iteration on T3 is a common waste of time — you can't tell whether a bad result means a bad prompt or an underpowered model.

---

## Current models by tier

> Models and prices below are current as of **2026-07-31**. Prices are API dollars per million tokens (input/output) and are here for order-of-magnitude comparison only — the vendor page is authoritative.

### Cloud APIs

| Vendor | T1 Frontier | T2 Workhorse | T3 Fast |
|--------|------------|--------------|---------|
| **Anthropic** | Claude Opus 5<br/>`claude-opus-5` · $5/$25 · 1M context | Claude Sonnet 5<br/>`claude-sonnet-5` · $2/$10 (launch price through 2026-08-31, then $3/$15) | Claude Haiku 4.5<br/>`claude-haiku-4-5` |
| **OpenAI** | GPT-5.6 Sol<br/>`gpt-5.6-sol` (alias `gpt-5.6`) · $5/$30 | GPT-5.6 Terra<br/>`gpt-5.6-terra` · $2.50/$15 | GPT-5.6 Luna<br/>`gpt-5.6-luna` |
| **Google** | Gemini 3.1 Pro (Preview)<br/>Gemini 2.5 Pro (Stable) | Gemini 3.6 Flash<br/>(Google's own "workhorse" positioning) | Gemini 3.5 Flash-Lite |

Worth knowing:

- All three GPT-5.6 tiers share roughly a 1.05M-token context window, 128K max output, and a 2026-02-16 knowledge cutoff. "Feed every competitor listing in the category at once" no longer requires chunking.
- OpenAI cut Luna (−80%) and Terra (−20%) on 2026-07-30. If your cost model is a few months old, rerun it.
- Google's version numbers don't line up across tiers — Flash is on 3.6 while Pro's 3.1 is still Preview, and 3.5 Pro is in partner testing. Pick by tier, not by which number is bigger.
- The ChatGPT web/app model names are not the API names (the app currently mixes GPT-5.3 Instant as default, GPT-5.4 Thinking/Pro, GPT-5.5, and GPT-5.6). Keep the distinction when writing SOPs — your operations team is on the app.

### T4 Local (open weights)

| Model | Sizes | Good for | License |
|-------|-------|---------|---------|
| **Qwen3** | 8B / 14B (normal GPU) · 30B-A3B MoE (~24GB VRAM) | Default pick for Chinese-language e-commerce; strong multilingual | Apache 2.0 |
| **Qwen3-235B-A22B** | 235B MoE | Currently the strongest open-weight model across broad benchmarks | Apache 2.0 |
| **Qwen3-Coder-480B** | 480B MoE | Writing data pipelines and automation scripts (69.6% SWE-bench Verified) | Apache 2.0 |
| **Gemma 3 27B** | 27B | Runs on a single high-memory GPU; solid generalist | Gemma license |
| **DeepSeek R1** | — | Tasks that need a visible reasoning chain (97.3% MATH-500) | MIT |

To run: install [Ollama](https://ollama.com) or LM Studio, then `ollama run qwen3:8b` pulls a quantized GGUF and exposes an OpenAI-compatible local endpoint — meaning every OpenAI-SDK example in this book works locally by changing one `base_url`. Use vLLM for high-concurrency production, llama.cpp for CPU/edge. Short on VRAM? Drop the quantization (Q4 and below), at some cost to quality.

Full deployment walkthrough in [B5 Local Model Deployment](../b-developers/b5-local-model-deploy.md).

### Video generation

| Model | Strength | E-commerce use |
|-------|---------|----------------|
| **Veo 3.1** (Google Flow) | Cinematic quality + native audio generation | Finished-feeling ad spots with sound |
| **Runway Gen-4.5** | Strong editing control, team-friendly | Deliverables needing tight creative control |
| **Kling 3** | Best motion realism | Animated product showcases |
| **Seedance 2** | Image-to-video + longer shot planning | Ads, brand scenes, storyboard-driven work |

**The single most important rule for e-commerce**: for the product itself, **always go image-to-video** (start from a real product photo). Never text-to-video. Text-to-video re-imagines your product — details, proportions, and logo will drift, and using that as ad creative is a compliance risk.

> OpenAI's Sora 2 is no longer a recommendation — the consumer experience ended in April 2026 and the API is scheduled to shut down on 2026-09-24. If your pipeline still depends on it, plan a migration.

### Image generation

| Model | Strength | E-commerce use |
|-------|---------|----------------|
| **Nano Banana Pro** (Google) | Photorealism + text rendering + multilingual | Product shots, marketing images with copy, localized creative per market |
| **FLUX.2 Pro** | Photoreal product images at API volume | High-frequency automated pipelines |
| **GPT Image 2** | Best complex-instruction adherence | Scenes where you need many constraints honored at once |
| **Midjourney V8.1** | Highest aesthetic ceiling | Brand-tone imagery, lifestyle scenes |
| **Ideogram 4** | Typography and in-image text | Banners needing precise text |
| **Recraft V4.1** | Design systems / vector | Icons, brand visual specs |

There is no longer a single "best" image model. The working combination is: volume through the FLUX.2 Pro or Nano Banana Pro API, hero images curated by hand out of Midjourney, precise-text work in Ideogram. See [A7 Visual Content](../a-operators/a7-visual-content.md) and [B9 AI Image Pipeline](../b-developers/b9-ai-image-pipeline.md).

---

## How to re-verify this page

This table will go stale. Refresh it quarterly — it takes about ten minutes:

1. **Official pricing pages** (the only trustworthy source; third-party comparison sites lag badly)
   - Anthropic: <https://www.anthropic.com/pricing>
   - OpenAI: <https://openai.com/api/pricing/>
   - Google: <https://ai.google.dev/gemini-api/docs/pricing>
2. **Official model lists** — check for new tiers and for anything marked deprecated
   - <https://docs.claude.com/en/docs/about-claude/models>
   - <https://developers.openai.com/api/docs/changelog>
   - <https://ai.google.dev/gemini-api/docs/models>
3. **Open-weight leaderboards** for T4 turnover: the Hugging Face open LLM leaderboard, LMArena
4. Update the **verification date** at the top of this page and add a row to the changelog below

The test for "does the prose need to change too" is simple: **if the tier boundaries still hold, no chapter needs a single edit.** Only a genuinely new shape that the four tiers can't hold — say, a vendor shipping a commerce-specific vertical model — justifies revisiting the chapter text.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-31 | Page created. Chapter prose converted to capability-tier language; all model-id references now link here |
| 2026-07-31 | Added the video-generation tier; flagged Sora 2 as deprecated (consumer ended 2026-04, API shuts down 2026-09-24) |
