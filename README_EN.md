<div align="center">

# Cross-Border E-Commerce AI Knowledge Base

### Read it as a book. Install it as agent capability.

**Every number CI-verified · Every prompt carries anti-hallucination guardrails · Every chapter states when the method breaks**

🇺🇸 English&nbsp;·&nbsp;[🇨🇳 中文](README.md)&nbsp;·&nbsp;[🇯🇵 日本語](README_JA.md)&nbsp;&nbsp;|&nbsp;&nbsp;📖 [Read Online](https://kangise.github.io/ecommerce-ai-skills/)&nbsp;&nbsp;|&nbsp;&nbsp;📦 [Install for Agent](dist/)

[![License: CC0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)
[![Stars](https://img.shields.io/github/stars/kangise/ecommerce-ai-skills?style=social)](https://github.com/kangise/ecommerce-ai-skills)
[![AAAI China Chapter](https://img.shields.io/badge/AAAI_China_Chapter-Initiative-blue)](https://github.com/kangise/ecommerce-ai-skills)

</div>

<br>
<p align="center">
  <img src="assets/hero-en.svg" alt="One source, two consumption paths: 69 chapters through CI gates — one path builds a trilingual site for readers, the other an installable agent package" width="100%">
</p>
<br>

## What This Is

An AI operations knowledge base for cross-border e-commerce. **One source, two uses:**

- **Read it** — 69 chapters, trilingual, [online site](https://kangise.github.io/ecommerce-ai-skills/) with language switching
- **Install it for your agent** — [`dist/`](dist/) is a plug-and-play capability package, one MCP config line to Claude / Cursor

Both paths are guarded by the same CI gates. **Gates fail, neither ships.**

<br>

## Who You Are → Where to Start

<p align="center">
  <img src="assets/paths-en.svg" alt="Four entry paths: a solo seller 3 min, finding AI knowledge for an agent 5 min, a team wanting one unified SOP same-day, learning the capability-packaging method" width="100%">
</p>

<br>

## Why Not Just Another Prompt Collection

<p align="center">
  <img src="assets/guardrail-en.svg" alt="The same question: an ordinary prompt invents plausible numbers, while this library's prompt stops and asks you for the data because of its three guardrails" width="100%">
</p>

Ask an AI "roughly how much does this category sell per month?" and it will almost always hand you a plausible-looking number — **one it does not actually know**.

Sourcing, restocking, and pricing have real money behind them. The agent era makes it worse: a model acts on numbers it doesn't know to adjust prices and place orders.

**The difference isn't fancier prompts — it's drawing the line where AI stops.**

<br>

## 30-Second Demo

Paste this into [ChatGPT](https://chatgpt.com/) or [Claude](https://claude.ai/):

```
<role>Cross-border sourcing consultant familiar with Amazon [US/DE/JP]</role>

<my_conditions>
- Startup capital: ¥[X]0K
- Experience level: [beginner/experienced/veteran]
- Preferred categories: [write your preference, or "no preference"]
- Risk appetite: [conservative/medium/aggressive]
</my_conditions>

<tool_data>
[Optional. Paste category data exported from Helium 10 / Jungle Scout. If empty, see data_discipline below]
</tool_data>

<task>
Recommend 5 category directions, each with:
1. Category name and brief description
2. Why this may be an opportunity now (state the basis for your judgment)
3. What data I need to verify to confirm it (name the specific metrics and the tool to pull them from)
4. Main risks and mitigations
5. Order-of-magnitude read on startup capital (can my stated budget cover it?)
6. Recommended entry strategy (differentiation direction)
</task>

<data_discipline>
- **Do not give specific monthly sales, price, or margin figures** unless they appear in <tool_data>. You do not have live market data, and an invented number leads me to stock the wrong product
- When <tool_data> is empty, item 3 matters most: tell me what to look up rather than guessing the answer for me
- Tag each conclusion: [tool data] or [category-level inference]
- If you lack the basis for a judgment, ask me for the data before concluding
</data_discipline>

<constraints>
- Don't recommend already-red-ocean categories (phone cases, cables)
- Prioritize categories with room for differentiation
- Respect my capital and experience limits
</constraints>

<output_format>
Recommend exactly 5 category directions, each following the fixed 6-item structure from <task> above:
1. Category name and brief description (1–2 sentences)
2. Why this may be an opportunity now (basis for the judgment)
3. Data to verify (specific metrics + the tool to pull them)
4. Main risks and mitigations
5. Order-of-magnitude read on startup capital (can my budget cover it?)
6. Recommended entry strategy (differentiation direction)
</output_format>

<self_check>
Before delivering, confirm: (1) no number appears that I didn't provide, (2) every category states what to verify next, (3) exactly 5 recommendations
</self_check>

Note:
- Don't recommend already-red-ocean categories (phone cases, cables)
- Prioritize categories with room for differentiation
- Account for my capital and experience limits

<copy_discipline>
- Never write a feature, material, certification, or result the product doesn't have. Any attribute I didn't state above must not appear in the copy
- For anything sent to a customer (replies, emails, templates), don't make commitments I haven't authorized: refund amounts, compensation, timelines, or exceptions to platform policy must be confirmed by me before they go in
- Flag any claim touching efficacy, safety, environmental, or patent language separately for manual review
</copy_discipline>
```

**Notice how it doesn't fabricate numbers** — it tells you exactly which figures to look up yourself. From [A1 Product Research · 3.7 Category Opportunity Discovery](src/a-operators/a1-product-research.md).

<br>

## Three Real Usage Scenarios

### 1 · Write an Amazon Listing for a new product (no coding required)

Open [A2 Listing Optimization](src/a-operators/a2-listing-optimization.md), copy the "full-listing generation" prompt, and fill in your product info.

You get a listing with **platform hard constraints** baked in: title ≤200 characters with the highest-search-volume keyword in the first 80, 5 bullets each ≤200 characters with no HTML, backend Search Terms ≤250 bytes per line.

> These aren't rules we made up — they're Amazon's actual limits, stored in [`ontology/constraints.yaml`](ontology/constraints.yaml), and the prompt's `<self_check>` block verifies each one. Change a constraint once, and gate `O5` makes every prompt referencing it change together.

### 2 · Turn Claude Desktop into an e-commerce consultant (5 minutes)

```json
{
  "mcpServers": {
    "opc-ecommerce": {
      "command": "npx",
      "args": ["-y", "mcp-server-filesystem", "/path/to/ecommerce-ai-skills/dist"]
    }
  }
}
```

After install:

| You ask | What it does |
|---|---|
| "ACOS is up to 40%, what do I do?" | Routes to `ecom-advertising` — a diagnostic path, not generic advice |
| "Should I use AI for demand forecasting?" | Routes to `ecom-applicability` — **answers "not with under a year of data"**, because it has every chapter's failure boundaries installed |
| "How do I reply to a complaint that the product doesn't match the photos?" | Routes to `ecom-customer-service` — reply templates with copy discipline |

See [dist/integration/mcp.md](dist/integration/mcp.md).

### 3 · Cross-platform launches for your team, no rules to memorize

The same "title" is a different thing on each of three platforms — look it up in [`ontology/constraints.yaml`](ontology/constraints.yaml):

```yaml
amazon.listing.title.max_length:       200  characters
shopify.product_page.title.max_length:  70  characters
tiktok_shop.product.title.max_length:   80  characters
```

When the team asks in the group chat again, just share the link. Or use the `ecom-listing` skill to generate compliant variants for all three platforms in one go.

<br>

## Not Just a Book — Three Layers

| Layer | Contents | Scale | For |
|---|---|---|---|
| **Knowledge Base** | 69 chapters, trilingual (zh/en/ja) | 69 chapters | Human reading · agent retrieval |
| **Ontology** | E-commerce domain model | 94 entities · 318 constraints · 78 relations · 8 processes | Shared contract between agents |
| **Skills + Prompts** | Guarded executable capabilities | 878 prompts · 9 installable skills | Agent direct invocation |

`dist/` directory structure:

```
dist/
  SKILL.md       ← Agent entry point — read it to know how to route requests
  ontology.json  ← E-commerce domain model (entities, relations, constraints)
  prompts.json   ← Guardrailed prompts, trilingual
  skills/        ← 9 domain skills, each with manifest + playbook + boundaries
  knowledge/     ← Structured index of the 69 chapters
  integration/   ← MCP server setup guide
```

<br>

## Why Trust This Content

Not because "we're careful" — because of **24 CI gates**. Every one must be 0; a non-zero fails the build:

| Gate | What it checks |
|---|---|
| `M1` | Every hard number in the text has a source, a verification date, a hedge word, or an explicit flag |
| `M2` | Every how-to chapter has a "when this doesn't work" section |
| `M4` | Every external link has been probed and isn't dead |
| `M7` | `verified` markers older than 18 months auto-expire with an error |
| `N3` `N4` | Every prompt has a self-check block and an output format |
| `O5` | Constraint values written in the text must match the ontology |
| `parity` | All three language files exist and have matching structure |

Run it yourself:

```bash
python3 scripts/verify_all.py
```

> The full gate list and design rationale are in [`scripts/README.md`](scripts/README.md). Known open items are written down in [`CONTRIBUTING.md`](CONTRIBUTING.md), not hidden.

<br>

## Where to Start

| You are | Start here |
|--------|---------|
| Wanting to know what AI can actually do | [AI Landscape Assessment](src/0-foundations/ai-landscape.md) — 30 minutes on maturity per step |
| An operator, ready to use it today | [A1 Product Research](src/a-operators/a1-product-research.md) · [A2 Listing](src/a-operators/a2-listing-optimization.md) · [A3 Advertising](src/a-operators/a3-advertising.md) |
| Already using AI, want automation | [A14 Agentified Operations](src/a-operators/a14-operations-agent.md) — decide which steps are worth it first |
| Technical, building your own | [B4 Agent Workflow](src/b-developers/b4-agent-workflow.md) · [B6 MCP Integration](src/b-developers/b6-mcp-agentic-workflow.md) |
| Facing compliance right now | [Tariffs & de minimis](src/a-operators/a11-financial-analysis.md) · [EU AI Act](src/a-operators/a6-compliance.md) |

<br>

## Other Things You Might Care About

- **Content that doesn't rot in three months** — chapters only describe capability tiers; model ids and prices live on one [model matrix](src/resources/model-matrix.md) page with verification dates, and `M7` errors when they expire
- **Built for the agent era** — not just prompts, but [how to migrate them into skill files](src/0-foundations/f2-prompt-engineering.md) and [which actions must never go to an agent](src/a-operators/a14-operations-agent.md)
- **CC0** — take it, no attribution required, no need to tell me

---

## Content Index

| Domain | Topics |
|--------|--------|
| AI Foundations | [AI Evolution](src/0-foundations/f1-ai-evolution.md) · [Prompt Engineering](src/0-foundations/f2-prompt-engineering.md) · [RAG](src/0-foundations/f3-rag-knowledge.md) · [Agents](src/0-foundations/f4-agent-automation.md) · [RPA](src/0-foundations/f5-rpa-automation.md) · [Tool Comparison](src/0-foundations/f6-ai-tools-comparison.md) · [AI Landscape](src/0-foundations/ai-landscape.md) |
| Product Research | [Product Research](src/a-operators/a1-product-research.md) · [Pricing Strategy](src/a-operators/a8-pricing-strategy.md) · [IP Protection](src/a-operators/a12-ip-protection.md) |
| Supply Chain | [Inventory & Supply Chain](src/a-operators/a5-inventory.md) |
| Content & Conversion | [Listing Optimization](src/a-operators/a2-listing-optimization.md) · [Visual Content](src/a-operators/a7-visual-content.md) · [Brand Building](src/a-operators/a10-brand-building.md) |
| Traffic & Acquisition | [Advertising](src/a-operators/a3-advertising.md) · [SEO / GEO](src/a-operators/a9-seo-geo.md) · [Growth Hacking](src/a-operators/a13-ai-growth-hack.md) |
| Social Media | [Instagram / Facebook](src/e-social-media/e1-instagram-facebook-ai-guide.md) · [YouTube](src/e-social-media/e2-youtube-ai-guide.md) · [Xiaohongshu (RED)](src/e-social-media/e3-xiaohongshu-ai-guide.md) · [Pinterest](src/e-social-media/e4-pinterest-ai-guide.md) · [WhatsApp](src/e-social-media/e5-whatsapp-business-ai-guide.md) · [Reddit](src/e-social-media/e6-reddit-ai-guide.md) · [Cross-Channel](src/e-social-media/e7-social-media-cross-channel.md) |
| Customer Operations | [Customer Service & After-Sales](src/a-operators/a4-customer-service.md) |
| Compliance & Finance | [Compliance & Risk](src/a-operators/a6-compliance.md) · [Financial Analysis](src/a-operators/a11-financial-analysis.md) · [AI Risk Governance](src/c-managers/c4-ai-risk-governance.md) |
| Marketplaces — Shelf | [Walmart](src/d-platforms/d4-walmart-ai-guide.md) · [eBay](src/d-platforms/d9-ebay-ai-guide.md) · [AliExpress](src/d-platforms/d10-aliexpress-ai-guide.md) · [Temu](src/d-platforms/d5-temu-seller-guide.md) · [Faire](src/d-platforms/d12-faire-wholesale-ai-guide.md) |
| Marketplaces — DTC | [Shopify](src/d-platforms/shopify-ai-guide.md) |
| Marketplaces — Short Video | [TikTok Shop](src/d-platforms/tiktok-shop-ai-guide.md) |
| Marketplaces — APAC | [Southeast Asia](src/d-platforms/d6-southeast-asia-ai-guide.md) · [Japan (Rakuten)](src/d-platforms/d8-rakuten-japan-ai-guide.md) · [Korea (Coupang)](src/d-platforms/d11-coupang-korea-ai-guide.md) |
| Marketplaces — EU & LatAm | [Mercado Libre](src/d-platforms/d7-mercado-libre-ai-guide.md) · [Otto / Zalando](src/d-platforms/d13-europe-marketplaces-guide.md) |
| Cross-Platform Strategy | [Cross-Platform Synergy](src/d-platforms/cross-platform-strategy.md) · [Platform Comparison](src/d-platforms/platform-comparison.md) |
| Building AI Systems | [Data Pipeline](src/b-developers/b1-data-pipeline.md) · [Prediction Models](src/b-developers/b2-prediction-models.md) · [RAG Knowledge Base](src/b-developers/b3-rag-knowledge-base.md) · [Agent Workflow](src/b-developers/b4-agent-workflow.md) · [Local Deployment](src/b-developers/b5-local-model-deploy.md) · [MCP](src/b-developers/b6-mcp-agentic-workflow.md) · [Review NLP](src/b-developers/b7-review-nlp-system.md) · [Dashboard](src/b-developers/b8-ecommerce-dashboard.md) · [Image Pipeline](src/b-developers/b9-ai-image-pipeline.md) |
| Team & Management | [AI Assessment](src/c-managers/c1-ai-assessment.md) · [Team Building](src/c-managers/c2-team-building.md) · [ROI Evaluation](src/c-managers/c3-roi-evaluation.md) · [Competitive Intelligence](src/c-managers/c5-competitive-intelligence.md) |

---

## Six Tracks

| Track | Who It's For | Coding? | What You Get |
|-------|-------------|---------|--------------|
| **[0 · AI Foundations](src/0-foundations/)** (7 guides) | Everyone | No | A working mental model of LLMs, prompts, RAG, agents |
| **[A · Operators](src/a-operators/)** (13 guides) | Product research / ops / ads / CS | No | A reusable AI workflow for every step from sourcing to growth, Amazon-first |
| **[B · Developers](src/b-developers/)** (9 guides) | Engineering / data / BI | Python | Deployable systems: pipelines, forecasts, RAG, agents, dashboards |
| **[C · Managers](src/c-managers/)** (5 guides) | Team leads / founders | No | An AI adoption roadmap: assessment, training, ROI, risk governance |
| **[D · Marketplaces](src/d-platforms/)** (14 guides) | Multi-platform sellers | No | Platform-specific playbooks: Shopify, TikTok Shop, Walmart, and 10 more |
| **[E · Social Media](src/e-social-media/)** (7 guides) | Content & growth | No | Channel strategies that map to the buyer journey, from discovery to decision |

---

## Top 10 Prompts (Ready to Use)

Hand-picked from the guides — copy into ChatGPT / Claude and get results instantly.

**1. Competitor Review Pain Point Analysis** — Extract product improvement ideas from negative reviews
```
You are a senior Amazon product manager. I'll give you a set of 1-3 star competitor reviews.
Analyze and output: Top 5 user pain points (by frequency), representative review quotes, improvement suggestions, and difficulty rating. Present in table format.
[Paste negative reviews here]
```
[Full guide →](src/a-operators/a1-product-research.md#31-竞品-review-痛点分析)

**2. Market Feasibility Quick Assessment** — 5-dimension scoring to decide if a product is worth pursuing
```
You are a cross-border e-commerce product research expert. Assess this product:
Product: [product name] Target market: Amazon [US/DE/JP]
Analyze across 5 dimensions (score 1-5 each): market demand, competition intensity, profit margin, supply chain difficulty, compliance risk.
Give a final recommendation: Enter / Proceed with caution / Pass.
```
[Full guide →](src/a-operators/a1-product-research.md#32-市场可行性快速评估)

**3. Full Listing Generation** — Title, bullet points, description, and search terms in one go
```
You are an Amazon Listing optimization expert for the [target market].
Product: [name] Selling points: [point 1/2/3] Keywords: [keyword list]
Generate: Title (≤200 chars), 5 Bullet Points, Product Description (≤200 words), Backend Search Terms (5 lines).
Integrate keywords naturally, highlight differentiation.
```
[Full guide →](src/a-operators/a2-listing-optimization.md#31-listing-全套生成标题--五点--描述--search-terms)

**4. Multilingual Localization** — Not translation, but market adaptation
```
You are an Amazon Listing localization expert fluent in [target language].
[Paste English listing]
Localize to [target language]: match local search habits, replace with local keywords, reorder selling points for local priorities, annotate all localization changes with reasons.
```
[Full guide →](src/a-operators/a2-listing-optimization.md#32-多语言本地化不是直译)

**5. Competitor Listing Strategy Breakdown** — Compare and find differentiation opportunities
```
Analyze these 3 competitor Amazon Listings and compare their strategies:
[Competitor A/B/C titles and bullet points]
Output: Each competitor's core positioning, shared selling points, differentiation opportunities, keyword coverage comparison table, and positioning recommendations for my listing.
```
[Full guide →](src/a-operators/a2-listing-optimization.md)

**6. Search Term Report Analysis** — Find ad spend waste and optimization opportunities
```
You are an Amazon PPC advertising expert. Here's my search term report (past 30 days):
[Paste data]
Output: High-converting keywords TOP 10, high-spend low-conversion TOP 10, low CTR analysis, negative keyword suggestions, budget reallocation plan.
```
[Full guide →](src/a-operators/a3-advertising.md#31-搜索词报告分析)

**7. Ad Copy A/B Testing** — 5 headline styles for Sponsored Brands
```
Product: [description] Key selling point: [main benefit]
Generate 5 Sponsored Brands Headlines (≤50 chars each): feature-driven, scenario-driven, emotion-driven, data-driven, problem-solving.
Annotate expected impact and target audience for each.
```
[Full guide →](src/a-operators/a3-advertising.md#32-广告文案-ab-测试)

**8. Bulk Negative Review Analysis** — Categorize issues and create action plans
```
You are an e-commerce product quality analyst. Here are all 1-3 star reviews from the past 60 days.
Categorize by type (quality/functionality/shipping/usability/expectation mismatch), calculate frequency %, list 3 representative reviews per category, provide short-term + long-term solutions, and prioritize.
[Paste reviews]
```
[Full guide →](src/a-operators/a4-customer-service.md)

**9. Account Appeal Letter (Plan of Action)** — Professional reinstatement appeal
```
You are an Amazon account appeal expert. My account was suspended for:
[Paste violation notice]
Write a Plan of Action: Root Cause (acknowledge the issue), Immediate Actions (steps already taken), Preventive Measures (long-term prevention). Professional and sincere tone, specific action items in each section.
```
[Full guide →](src/a-operators/a6-compliance.md#36-amazon-政策违规应对)

**10. Multi-Market Compliance Comparison** — Generate compliance checklists fast
```
I want to sell [product type] on Amazon [US/DE/JP].
Generate a compliance comparison table: required certifications per market, packaging & labeling requirements, special category requirements, estimated costs & timelines, common compliance pitfalls.
Note information currency and recommend confirming with certification bodies.
```
[Full guide →](src/a-operators/a6-compliance.md#31-多市场合规对比深化版)

---

## Notebook Lab

18 Jupyter notebooks that run directly on Google Colab — zero setup required:

[Product Research](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/a1-product-research.ipynb) · [Multilingual Listing](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/a2-multilingual-listing.ipynb) · [Advertising](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/a3-advertising.ipynb) · [Negative Reviews](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/a4-negative-review-analysis.ipynb) · [Inventory Reorder](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/a5-inventory-reorder.ipynb) · [Compliance Checker](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/a6-compliance-checker.ipynb) · [Price Tracker](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/a8-price-tracker.ipynb) · [GEO Audit](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/a9-geo-audit.ipynb) · [Brand Audit](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/a10-brand-audit.ipynb) · [Profit Calculator](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/a11-profit-calculator.ipynb) · [Patent Search](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/a12-ip-patent-search.ipynb) · [Data Pipeline](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/b1-data-pipeline.ipynb) · [Sales Forecast](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/b2-sales-forecast.ipynb) · [Review NLP](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/b7-review-analysis.ipynb) · [Dashboard](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/b8-dashboard-demo.ipynb) · [ROI Evaluation](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/c3-roi-evaluation.ipynb) · [Cross-Platform Content](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/d3-cross-platform-content.ipynb) · [Social Calendar](https://colab.research.google.com/github/kangise/ecommerce-ai-skills/blob/main/notebooks/e1-social-content-calendar.ipynb)

## Case Studies

[AI Listing Optimization](src/case-studies/ai-listing-optimization.md) — 4 hours → 45 minutes per SKU

[AI PPC Optimization](src/case-studies/ai-ppc-optimization.md) — ACOS 35% → 18%

[Review-Driven Product Development](src/case-studies/ai-review-to-product.md) — 4.6★ vs. competitor's 4.2★

[All case studies →](src/case-studies/)

---

## Community

ecommerce-ai-skills is an open-source project under the **AAAI China Chapter**, dedicated to the practical application of AI in cross-border e-commerce.

- **Star** this repo to stay updated
- [Submit an issue](https://github.com/kangise/ecommerce-ai-skills/issues) to report problems or suggest improvements
- [Submit a PR](https://github.com/kangise/ecommerce-ai-skills/pulls) to contribute prompts, notebooks, or case studies

## Contributing

We especially welcome:

1. **Prompt templates** — battle-tested prompts that work in real business scenarios (note which AI tools you tested with)
2. **Notebooks** — hands-on tutorials that run on Google Colab free tier
3. **Case studies** — how you solved an e-commerce problem with AI, and the results
4. **Tool reviews** — pros and cons of AI tools you've actually used
5. **Fixes** — broken links, outdated content

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) — free to use, no attribution required · [Disclaimer](DISCLAIMER.md) · *An AAAI China Chapter Initiative*
