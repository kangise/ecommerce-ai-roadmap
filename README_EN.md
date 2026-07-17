# ecommerce-ai-roadmap: AI × Cross-Border E-Commerce Knowledge Hub

> Practical AI playbooks for cross-border e-commerce — an AAAI China Chapter open-source initiative

<div align="center">

### 📖 [Read Online](https://kangise.github.io/ecommerce-ai-roadmap/) (Chinese)

</div>

[![AAAI China Chapter](https://img.shields.io/badge/AAAI_China_Chapter-Initiative-blue)](https://github.com/kangise/ecommerce-ai-roadmap)
[![Stars](https://img.shields.io/github/stars/kangise/ecommerce-ai-roadmap?style=social)](https://github.com/kangise/ecommerce-ai-roadmap)
[![License: CC0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

**56 hands-on guides · 6 tracks · 18 runnable Colab notebooks · copy-paste prompts in every guide.**
Original content, not a link aggregator. Guides are written in Chinese — the prompts inside are bilingual-friendly and work in any LLM.

🇺🇸 English | 🇨🇳 [中文](README.md)

<p align="center">
  <img src="assets/content-map.svg" alt="Content map — 56 guides across 6 tracks" width="100%">
</p>

---

## Try It in 30 Seconds

Copy the prompt below into [ChatGPT](https://chat.openai.com/) or [Claude](https://claude.ai/) and get an instant market analysis:

```
You are a senior cross-border e-commerce expert with deep knowledge of the Amazon marketplace.
I want to sell a portable neck fan on Amazon US.
Please provide a quick market feasibility analysis including:
1. Category characteristics (seasonality, competition level, price range)
2. Top 3 competitors' key selling points and main pain points from negative reviews
3. 3 potential differentiation angles
4. Risk alerts (compliance, patents, seasonal inventory risks)
Present key data comparisons in table format.
```

Every one of the 56 guides ships prompts like this. Ten of the most-used ones are [right below](#top-10-prompts-ready-to-use).

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

[Product Research](notebooks/a1-product-research.ipynb) · [Multilingual Listing](notebooks/a2-multilingual-listing.ipynb) · [Advertising](notebooks/a3-advertising.ipynb) · [Negative Reviews](notebooks/a4-negative-review-analysis.ipynb) · [Inventory Reorder](notebooks/a5-inventory-reorder.ipynb) · [Compliance Checker](notebooks/a6-compliance-checker.ipynb) · [Price Tracker](notebooks/a8-price-tracker.ipynb) · [GEO Audit](notebooks/a9-geo-audit.ipynb) · [Brand Audit](notebooks/a10-brand-audit.ipynb) · [Profit Calculator](notebooks/a11-profit-calculator.ipynb) · [Patent Search](notebooks/a12-ip-patent-search.ipynb) · [Data Pipeline](notebooks/b1-data-pipeline.ipynb) · [Sales Forecast](notebooks/b2-sales-forecast.ipynb) · [Review NLP](notebooks/b7-review-analysis.ipynb) · [Dashboard](notebooks/b8-dashboard-demo.ipynb) · [ROI Evaluation](notebooks/c3-roi-evaluation.ipynb) · [Cross-Platform Content](notebooks/d3-cross-platform-content.ipynb) · [Social Calendar](notebooks/e1-social-content-calendar.ipynb)

## Case Studies

[AI Listing Optimization](src/case-studies/ai-listing-optimization.md) — 4 hours → 45 minutes per SKU

[AI PPC Optimization](src/case-studies/ai-ppc-optimization.md) — ACOS 35% → 18%

[Review-Driven Product Development](src/case-studies/ai-review-to-product.md) — 4.6★ vs. competitor's 4.2★

[All case studies →](src/case-studies/)

---

## Community

ecommerce-ai-roadmap is an open-source project under the **AAAI China Chapter**, dedicated to the practical application of AI in cross-border e-commerce.

- **Star** this repo to stay updated
- [Submit an issue](https://github.com/kangise/ecommerce-ai-roadmap/issues) to report problems or suggest improvements
- [Submit a PR](https://github.com/kangise/ecommerce-ai-roadmap/pulls) to contribute prompts, notebooks, or case studies

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
