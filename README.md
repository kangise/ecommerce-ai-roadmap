<div align="center">

### Language / 语言切换

[![中文](https://img.shields.io/badge/🇨🇳_中文-当前语言-orange?style=for-the-badge)](README.md) [![English](https://img.shields.io/badge/🇺🇸_English-Click_Here-blue?style=for-the-badge)](en/README.md) [![日本語](https://img.shields.io/badge/🇯🇵_日本語-ここをクリック-red?style=for-the-badge)](ja/README.md) [![Español](https://img.shields.io/badge/🇪🇸_Español-Haz_Clic-yellow?style=for-the-badge)](es/README.md)

</div>

# ecommerce-ai-roadmap

> 跨境电商 AI 实战知识库 — AAAI China Chapter 开源项目

[![AAAI China Chapter](https://img.shields.io/badge/AAAI_China_Chapter-Initiative-blue)](https://github.com/kangise/ecommerce-ai-roadmap)
[![Stars](https://img.shields.io/github/stars/kangise/ecommerce-ai-roadmap?style=social)](https://github.com/kangise/ecommerce-ai-roadmap)
[![License: CC0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

🇨🇳 中文（当前） | 🇺🇸 [English](en/README.md) | 🇯🇵 [日本語](ja/README.md)（概要のみ） | 🇪🇸 [Español](es/README.md)（resumen）

---


跨境电商 AI 实操手册 — 56 篇指南覆盖从选品到增长的完整链路，每个环节都有可直接复制的 Prompt 和 SOP。

<!-- 这里后续放一张内容体系全景图 -->

---

## 从哪里开始

如果你还没用过 AI 做电商，先花 30 秒试一下。把下面这段复制到 [ChatGPT](https://chat.openai.com/) 或 [Claude](https://claude.ai/)：

```
你是一个资深的跨境电商运营专家，精通 Amazon 平台。
我想在 Amazon US 销售一款便携式颈挂风扇（Neck Fan）。
请帮我做一个快速的市场可行性分析，包含：
1. 这个品类的市场特征（季节性、竞争程度、价格带）
2. TOP 3 竞品的核心卖点和差评中的主要痛点
3. 3个可能的差异化方向
4. 风险提示（合规、专利、季节性库存风险）
请用表格形式呈现关键数据对比。
```

这就是 AI 在跨境电商中最基础的用法。这个知识库里有 56 篇指南，每篇都有类似的 Prompt，覆盖你业务的每一个环节。

如果你想系统地了解 AI 能做什么，从 [AI 基础](paths/0-foundations/) 开始。这里有 [AI 技术演进](paths/0-foundations/f1-ai-evolution.md)的全景、[Prompt 工程](paths/0-foundations/f2-prompt-engineering.md)的方法论、[RAG](paths/0-foundations/f3-rag-knowledge.md) 和 [Agent](paths/0-foundations/f4-agent-automation.md) 的原理，以及一份 [AI 应用全景评估](paths/0-foundations/ai-landscape.md)，帮你判断每个环节 AI 的成熟度和优先级。

---

## 业务链路

跨境电商的业务链路是：选什么卖 → 怎么展示 → 怎么获客 → 怎么服务 → 怎么赚钱。每个环节都有 AI 的应用点。

**选品与市场** — 一切从选品开始。[选品与市场洞察](paths/a-operators/a1-product-research.md)教你用 AI 做竞品 Review 痛点分析、市场可行性评估和关键词聚类。选好品之后，[定价策略](paths/a-operators/a8-pricing-strategy.md)帮你建立动态定价模型，[知识产权保护](paths/a-operators/a12-ip-protection.md)帮你在选品阶段就排查专利和商标风险。

**供应链与库存** — 选好品，接下来是备货。[库存与供应链](paths/a-operators/a5-inventory.md)覆盖了 AI 驱动的补货预测、安全库存计算和供应商评估。

**内容与转化** — 产品到手，需要让它在平台上"被看见"和"被买走"。[Listing 优化](paths/a-operators/a2-listing-optimization.md)是最高频的场景 — 从 Rufus/COSMO 语义优化到多语言本地化，一个 Prompt 就能生成完整的标题+五点+描述。[视觉内容](paths/a-operators/a7-visual-content.md)教你用 AI 生成产品图和视频素材。[品牌建设](paths/a-operators/a10-brand-building.md)帮你构建品牌故事、视觉系统和跨平台一致性 — 这是长期转化资产，不是短期技巧。

**流量与获客** — 内容做好了，需要流量。[广告优化](paths/a-operators/a3-advertising.md)教你用 AI 分析搜索词报告、找到浪费性支出、优化出价策略。[SEO/GEO](paths/a-operators/a9-seo-geo.md)覆盖了传统搜索优化和 2026 年最热的趋势 — 让你的产品被 ChatGPT、Perplexity 和 Gemini 推荐。[AI Growth Hack](paths/a-operators/a13-ai-growth-hack.md)是增长的系统化方法论，从选品验证到规模化的 5 阶段飞轮。

**社交媒体营销** — 流量不只来自平台内部。[Instagram/Facebook](paths/e-social-media/e1-instagram-facebook-ai-guide.md) 的 Reels 创作和 Advantage+ 广告、[YouTube](paths/e-social-media/e2-youtube-ai-guide.md) 的长视频评测和 Shorts、[小红书](paths/e-social-media/e3-xiaohongshu-ai-guide.md)的种草笔记、[Pinterest](paths/e-social-media/e4-pinterest-ai-guide.md) 的视觉搜索、[WhatsApp](paths/e-social-media/e5-whatsapp-business-ai-guide.md) 的对话式商务、[Reddit](paths/e-social-media/e6-reddit-ai-guide.md) 的口碑营销 — 每个渠道都有 AI 的打法。[跨渠道策略](paths/e-social-media/e7-social-media-cross-channel.md)教你一个内容多平台适配。

**客户运营** — 流量转化成订单后，[客服与售后](paths/a-operators/a4-customer-service.md)帮你用 AI 批量分析差评、生成多语言客服回复、撰写账号申诉信。

**合规与财务** — 最后是确保你合法地赚钱。[合规与风控](paths/a-operators/a6-compliance.md)覆盖了 CE/FCC/PSE/UKCA 多市场合规对比和 BSA AI Agent 合规新规。[财务分析](paths/a-operators/a11-financial-analysis.md)帮你计算含所有隐藏成本的真实利润和现金流预测。[AI 风险治理](paths/c-managers/c4-ai-risk-governance.md)帮你建立 AI 使用的治理政策。

---

## 多平台扩展

以上内容以 Amazon 为主线，但 AI 的能力可以扩展到任何平台。

**货架电商** — [Walmart](paths/d-platforms/d4-walmart-ai-guide.md) 是 Amazon 卖家最自然的第二平台，[eBay](paths/d-platforms/d9-ebay-ai-guide.md) 适合二手和翻新品，[AliExpress](paths/d-platforms/d10-aliexpress-ai-guide.md) 的全托管模式正在改变南欧市场，[Temu](paths/d-platforms/d5-temu-seller-guide.md) 的竞争分析和入驻决策框架帮你判断是否值得进入，[Faire](paths/d-platforms/d12-faire-wholesale-ai-guide.md) 是 B2B 批发的新渠道。

**独立站** — [Shopify AI 指南](paths/d-platforms/shopify-ai-guide.md)是一篇 2200 行的完整手册，从选品到 GEO 优化到 Agentic Storefronts（在 ChatGPT 内直接卖货），覆盖了独立站的全链路。

**短视频与直播** — [TikTok Shop](paths/d-platforms/tiktok-shop-ai-guide.md) 的 1600 行指南覆盖了 Hook 公式、3 幕视频脚本、达人量化评分模型、直播分钟级脚本和 GMV Max 优化策略。

**亚太市场** — [东南亚 Shopee/Lazada](paths/d-platforms/d6-southeast-asia-ai-guide.md) 的多语言本地化和直播带货、[日本 Rakuten](paths/d-platforms/d8-rakuten-japan-ai-guide.md) 的店铺自定义和积分生态、[韩国 Coupang](paths/d-platforms/d11-coupang-korea-ai-guide.md) 的 Rocket Delivery 和韩语 Listing。

**欧洲与拉美** — [拉美 Mercado Libre](paths/d-platforms/d7-mercado-libre-ai-guide.md) 的西语/葡语本地化、[欧洲 Otto/Zalando](paths/d-platforms/d13-europe-marketplaces-guide.md) 的德国市场和 EU 合规（CE/EPR/VAT/GPSR）。

如果你在多个平台运营，[跨平台协同](paths/d-platforms/cross-platform-strategy.md)教你一个核心文档适配三个平台、跨平台归因和广告预算分配。[平台全景对比](paths/d-platforms/platform-comparison.md)把 13 个平台 + 7 个社交渠道放在一张表里对比。

---

## 技术构建

如果你是开发者，想构建自己的 AI 电商工具，这里有 9 个技术模块：从 [数据管道](paths/b-developers/b1-data-pipeline.md)（pandas + SP-API）到 [预测模型](paths/b-developers/b2-prediction-models.md)（Prophet + AutoGluon），从 [RAG 知识库](paths/b-developers/b3-rag-knowledge-base.md)（LlamaIndex + Chroma）到 [Agent 工作流](paths/b-developers/b4-agent-workflow.md)（LangGraph + CrewAI），从 [本地模型部署](paths/b-developers/b5-local-model-deploy.md)（Ollama + LoRA）到 [MCP 集成](paths/b-developers/b6-mcp-agentic-workflow.md)（用 Claude 对话管理广告和产品）。还有 [Review NLP 系统](paths/b-developers/b7-review-nlp-system.md)、[电商 Dashboard](paths/b-developers/b8-ecommerce-dashboard.md) 和 [AI 图片生成 Pipeline](paths/b-developers/b9-ai-image-pipeline.md)。

---

## 团队与管理

如果你是管理者，想推动团队 AI 转型：[AI 能力评估](paths/c-managers/c1-ai-assessment.md)帮你做优先级排序，[团队建设](paths/c-managers/c2-team-building.md)帮你让 80%+ 的人每天用 AI，[ROI 评估](paths/c-managers/c3-roi-evaluation.md)帮你量化 AI 投入的回报，[竞争情报](paths/c-managers/c5-competitive-intelligence.md)帮你监控竞品的 AI 动态。

---

## Notebook 实验室

18 个 Jupyter Notebook，可在 Google Colab 一键运行，不需要本地环境。覆盖选品（[a1](notebooks/a1-product-research.ipynb)）、Listing（[a2](notebooks/a2-multilingual-listing.ipynb)）、广告（[a3](notebooks/a3-advertising.ipynb)）、差评分析（[a4](notebooks/a4-negative-review-analysis.ipynb)）、库存（[a5](notebooks/a5-inventory-reorder.ipynb)）、合规（[a6](notebooks/a6-compliance-checker.ipynb)）、定价（[a8](notebooks/a8-price-tracker.ipynb)）、GEO 审计（[a9](notebooks/a9-geo-audit.ipynb)）、品牌审计（[a10](notebooks/a10-brand-audit.ipynb)）、利润计算（[a11](notebooks/a11-profit-calculator.ipynb)）、IP 排查（[a12](notebooks/a12-ip-patent-search.ipynb)）、数据管道（[b1](notebooks/b1-data-pipeline.ipynb)）、销量预测（[b2](notebooks/b2-sales-forecast.ipynb)）、Review NLP（[b7](notebooks/b7-review-analysis.ipynb)）、Dashboard（[b8](notebooks/b8-dashboard-demo.ipynb)）、ROI 计算（[c3](notebooks/c3-roi-evaluation.ipynb)）、跨平台内容（[d3](notebooks/d3-cross-platform-content.ipynb)）、社交内容日历（[e1](notebooks/e1-social-content-calendar.ipynb)）。[完整索引 →](notebooks/README.md)

---

## 案例研究

带 SOP、Prompt 和量化结果的实战案例：[AI Listing 优化](docs/case-studies/ai-listing-optimization.md)（单 SKU 创建时间从 4 小时降到 45 分钟）、[AI 广告优化](docs/case-studies/ai-ppc-optimization.md)（ACOS 从 35% 降到 18%）、[AI Review 分析驱动选品](docs/case-studies/ai-review-to-product.md)（产品评分 4.6 星 vs 竞品 4.2）。[查看全部案例 →](docs/case-studies/)

---

## 贡献

欢迎贡献内容、修正错误或分享你的实战经验。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) — 自由使用，无需署名。[免责声明](DISCLAIMER.md)

*An AAAI China Chapter Initiative*
