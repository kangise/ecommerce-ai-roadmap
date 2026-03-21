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


跨境电商 AI 实操手册 — 56 篇指南，从选品到增长，每个环节都有可直接复制的 Prompt。

<!-- 这里后续放一张内容体系全景图 -->

---

## 先试一下

把这段复制到 [ChatGPT](https://chat.openai.com/) 或 [Claude](https://claude.ai/)，30 秒出结果：

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

这个知识库里有 56 篇指南，每篇都有类似的 Prompt。

这个知识库里有 56 篇指南，每篇都有类似的 Prompt。想先了解 AI 能做什么？从 [AI 基础](paths/0-foundations/)开始，里面有 [AI 技术演进](paths/0-foundations/f1-ai-evolution.md)的全景、[Prompt 工程](paths/0-foundations/f2-prompt-engineering.md)的方法论、[RAG](paths/0-foundations/f3-rag-knowledge.md) 和 [Agent](paths/0-foundations/f4-agent-automation.md) 的原理。如果你时间有限，直接看 [AI 全景评估](paths/0-foundations/ai-landscape.md)，30 分钟了解每个环节 AI 的成熟度。

---

## 选品

一切从选品开始。[选品与市场洞察](paths/a-operators/a1-product-research.md)教你用 AI 从 50 条竞品差评中[提取核心痛点](paths/a-operators/a1-product-research.md#31-竞品-review-痛点分析)，用 [5 个维度快速评估市场可行性](paths/a-operators/a1-product-research.md#32-市场可行性快速评估)（需求、竞争、利润、供应链、合规），再通过[关键词聚类](paths/a-operators/a1-product-research.md#33-关键词需求聚类)发现竞品没覆盖的蓝海需求。整个流程有一套完整的 [SOP](paths/a-operators/a1-product-research.md#4-选品实战工作流)，也列出了[常见的选品陷阱](paths/a-operators/a1-product-research.md#5-常见选品陷阱)帮你避坑。

选好品之后，你需要定价。[定价策略](paths/a-operators/a8-pricing-strategy.md)里讲了 [Buy Box 的定价逻辑](paths/a-operators/a8-pricing-strategy.md#21-amazon-buy-box-定价策略)、如何做[价格弹性分析](paths/a-operators/a8-pricing-strategy.md#22-价格弹性分析)来找到最优价格点，以及怎么用 AI 做[竞品价格带分析](paths/a-operators/a8-pricing-strategy.md#23-竞品价格带分析)。

还有一个很多人忽略的环节：[知识产权](paths/a-operators/a12-ip-protection.md)。在选品阶段就应该做[专利排查](paths/a-operators/a12-ip-protection.md#21-选品阶段的专利排查)，用 [AI 辅助分析专利风险](paths/a-operators/a12-ip-protection.md#22-ai-辅助专利分析)，了解 [TRO（临时限制令）](paths/a-operators/a12-ip-protection.md#23-tro临时限制令风险防范)的防范方法，避免产品上架后被投诉下架。

## 供应链

品选好了，接下来是备货。[库存与供应链](paths/a-operators/a5-inventory.md)从 [FBA 库存的关键指标](paths/a-operators/a5-inventory.md#12-amazon-fba-库存关键指标)讲起，教你用 AI 做补货预测、计算安全库存、评估供应商。

## 内容

产品到手，需要让它在平台上被看见、被买走。

[Listing 优化](paths/a-operators/a2-listing-optimization.md)是最高频的场景。Amazon 的搜索算法已经从 A9 演进到了 [COSMO + Rufus](paths/a-operators/a2-listing-optimization.md#11-amazon-搜索算法演进从-a9-到-cosmo--rufus)，这意味着 Listing 不能再堆关键词，而要覆盖用户意图。这篇指南教你用一个 Prompt [生成完整的标题+五点+描述+Search Terms](paths/a-operators/a2-listing-optimization.md#31-listing-全套生成标题--五点--描述--search-terms)，做[多语言本地化](paths/a-operators/a2-listing-optimization.md#32-多语言本地化不是直译)（不是翻译，是文化适配+本地关键词+度量转换），以及通过 [Q&A 预埋](paths/a-operators/a2-listing-optimization.md)让 Rufus 在回答用户问题时推荐你的产品。

Listing 文字做好了，还需要视觉。[视觉内容](paths/a-operators/a7-visual-content.md)教你用 Midjourney 和 DALL-E [生成产品主图](paths/a-operators/a7-visual-content.md#2-ai-产品图片生成)、[信息图和卖点图](paths/a-operators/a7-visual-content.md#23-信息图卖点图-ai-生成)，以及 [AI 产品视频](paths/a-operators/a7-visual-content.md#3-ai-产品视频生成)。

如果你想做品牌而不只是卖货，[品牌建设](paths/a-operators/a10-brand-building.md)讲了如何用 AI 构建[品牌故事](paths/a-operators/a10-brand-building.md#21-品牌故事框架)、保持[跨平台视觉一致性](paths/a-operators/a10-brand-building.md#3-ai-品牌视觉一致性)，以及 [2026 年 DTC 品牌的趋势](paths/a-operators/a10-brand-building.md#13-2026-年-dtc-品牌趋势)。

## 流量

内容做好了，需要流量。

付费流量看[广告优化](paths/a-operators/a3-advertising.md)。核心是用 AI [分析搜索词报告](paths/a-operators/a3-advertising.md#31-搜索词报告分析)，把关键词分成四象限（明星词、潜力词、观察词、浪费词），然后用[否定关键词策略](paths/a-operators/a3-advertising.md#33-否定关键词策略)砍掉浪费性支出，用 [A/B 测试](paths/a-operators/a3-advertising.md#32-广告文案-ab-测试)优化广告文案。新品卖家可以直接用[30 天广告启动计划](paths/a-operators/a3-advertising.md)。

自然流量看 [SEO/GEO](paths/a-operators/a9-seo-geo.md)。除了传统的 [Amazon SEO](paths/a-operators/a9-seo-geo.md#21-2026-amazon-seo-核心清单) 和 [Google SEO for Shopify](paths/a-operators/a9-seo-geo.md#3-google-seo-for-shopify)，2026 年最重要的变化是 [GEO（生成式引擎优化）](paths/a-operators/a9-seo-geo.md#4-geo-优化实操)— 让你的产品被 ChatGPT、Perplexity 和 Gemini 推荐给用户。

想要系统化的增长方法论？[AI Growth Hack](paths/a-operators/a13-ai-growth-hack.md) 把从选品验证到规模化拆成了 5 个阶段，每个阶段都有对应的 AI 工作流。

## 社交媒体

流量不只来自平台内部。

[Instagram 和 Facebook](paths/e-social-media/e1-instagram-facebook-ai-guide.md) 共享 Meta 生态，但[内容策略完全不同](paths/e-social-media/e1-instagram-facebook-ai-guide.md#2-instagram-vs-tiktok-vs-youtube内容策略差异)。这篇指南教你批量生成 Reels 脚本、用 Advantage+ 智能投放、优化 Shopping 标签。

[YouTube](paths/e-social-media/e2-youtube-ai-guide.md) 的价值在于长尾流量。理解 [YouTube 搜索算法的双引擎](paths/e-social-media/e2-youtube-ai-guide.md#21-youtube-搜索算法的双引擎)后，你可以用 AI 做关键词研究、写评测脚本、做 Shorts，通过 Shopping 和 Affiliate 变现。

[小红书](paths/e-social-media/e3-xiaohongshu-ai-guide.md)的算法和其他平台不一样，核心是 [CES 评分机制](paths/e-social-media/e3-xiaohongshu-ai-guide.md#11-ces-评分机制)和独特的[流量分发逻辑](paths/e-social-media/e3-xiaohongshu-ai-guide.md#12-流量分发逻辑)。这篇指南教你用 AI 写种草笔记、做 KOL/KOC 合作。

[Pinterest](paths/e-social-media/e4-pinterest-ai-guide.md) 本质上是一个视觉搜索引擎，理解它的[搜索排名因素](paths/e-social-media/e4-pinterest-ai-guide.md#21-pinterest-搜索排名因素)和 Board 策略后，可以用 Shopping Ads 直接转化。

[WhatsApp](paths/e-social-media/e5-whatsapp-business-ai-guide.md) 在拉美和东南亚是主要的客户触达渠道。先搞清楚 [Business App 和 API 的区别](paths/e-social-media/e5-whatsapp-business-ai-guide.md#11-whatsapp-business-app-vs-api)，然后按[电商 Chatbot 工作流](paths/e-social-media/e5-whatsapp-business-ai-guide.md#21-电商-chatbot-工作流设计)搭建多语言自动回复。

[Reddit](paths/e-social-media/e6-reddit-ai-guide.md) 正在成为产品发现的重要渠道 — 越来越多消费者在购买前会搜 ["Reddit before buying"](paths/e-social-media/e6-reddit-ai-guide.md#11-reddit-before-buying-趋势)，而 2026 年 Reddit 还上线了 [AI 购物搜索](paths/e-social-media/e6-reddit-ai-guide.md#12-reddit-ai-购物搜索2026-新功能)功能。

如果你同时运营多个社交渠道，[跨渠道策略](paths/e-social-media/e7-social-media-cross-channel.md)教你一个内容多平台适配、跨渠道归因和预算分配。

## 客服

订单来了之后，[客服与售后](paths/a-operators/a4-customer-service.md)帮你处理日常。先了解 Amazon [客服场景的全景](paths/a-operators/a4-customer-service.md#12-客服场景全景)，然后用 AI 批量分析差评（自动分类、频率统计、改善方案），生成多语言客服回复，写[账号申诉 Plan of Action](paths/a-operators/a6-compliance.md#36-amazon-政策违规应对)，应对 A-to-Z Claim。

## 合规与财务

最后是确保你合法地赚钱。

[合规与风控](paths/a-operators/a6-compliance.md)从[主要市场的合规框架对比](paths/a-operators/a6-compliance.md#12-主要市场的合规框架对比)讲起，教你用 AI 做 [CE/FCC/PSE/UKCA 多市场合规对比](paths/a-operators/a6-compliance.md#31-多市场合规对比深化版)、[估算合规成本](paths/a-operators/a6-compliance.md#33-合规成本估算)（认证费+测试费+标签费+年度维护），以及应对 [2026 年 BSA AI Agent 合规新规](paths/a-operators/a6-compliance.md#61-2026-新趋势amazon-ai-agent-合规要求bsa-更新)。

[财务分析](paths/a-operators/a11-financial-analysis.md)帮你看清[常见的财务盲区](paths/a-operators/a11-financial-analysis.md#11-常见的财务盲区)，用 [Amazon 真实利润计算公式](paths/a-operators/a11-financial-analysis.md#21-amazon-真实利润计算公式)算出含所有隐藏成本的真实利润，通过[成本优化矩阵](paths/a-operators/a11-financial-analysis.md#31-成本优化矩阵)找到降本空间，做 6 个月的现金流预测。

如果你的团队在用 AI 工具，[AI 风险治理](paths/c-managers/c4-ai-risk-governance.md)帮你建立治理政策，管控 AI 幻觉风险和数据隐私问题。

---

## 多平台

以上内容以 Amazon 为主线，但同样的 AI 能力可以扩展到其他平台。

### 货架电商

[Walmart](paths/d-platforms/d4-walmart-ai-guide.md) 是 Amazon 卖家最自然的第二平台。[eBay](paths/d-platforms/d9-ebay-ai-guide.md) 适合二手和翻新品。[AliExpress](paths/d-platforms/d10-aliexpress-ai-guide.md) 的全托管模式正在改变南欧市场。[Temu](paths/d-platforms/d5-temu-seller-guide.md) 的指南重点不是教你怎么运营（卖家自主空间有限），而是帮你做竞争分析和入驻决策。[Faire](paths/d-platforms/d12-faire-wholesale-ai-guide.md) 是 B2B 批发的新渠道。

### 独立站

[Shopify AI 指南](paths/d-platforms/shopify-ai-guide.md)是一篇 2200 行的完整手册。从选品和产品页优化开始，到 [GEO 优化](paths/d-platforms/shopify-ai-guide.md#213-geo-优化实操-让-ai-推荐你的产品)让 AI 推荐你的产品，到 [Agentic Storefronts](paths/d-platforms/shopify-ai-guide.md#212-agentic-storefronts-与-ucp-协议-在-ai-平台内直接卖货)在 ChatGPT 内直接卖货，到 [Klaviyo 邮件个性化](paths/d-platforms/shopify-ai-guide.md#23-shopify-邮件营销深度方法论-从-klaviyo-到-ai-个性化)做发送时间优化和 LTV 预测，再到 [Amazon 转 Shopify 的迁移方法论](paths/d-platforms/shopify-ai-guide.md#28-从-amazon-迁移到-shopify-的完整方法论)。

### 短视频与直播

[TikTok Shop](paths/d-platforms/tiktok-shop-ai-guide.md) 的 1600 行指南覆盖了短视频和直播的完整打法。用[信息缺口理论设计 Hook](paths/d-platforms/tiktok-shop-ai-guide.md#152-hook-设计方法论-不是吸引注意力而是制造信息缺口)，用 [3 幕结构写视频脚本](paths/d-platforms/tiktok-shop-ai-guide.md#153-视频脚本的3-幕结构)（转化率 3-5x），用 [100 分制模型量化评估达人](paths/d-platforms/tiktok-shop-ai-guide.md#162-ai-达人筛选的量化评分模型)，用[分钟级脚本设计直播节奏](paths/d-platforms/tiktok-shop-ai-guide.md#173-直播脚本的节奏设计)，以及应对 [GMV Max 强制化](paths/d-platforms/tiktok-shop-ai-guide.md#142-gmv-max-强制化-2025-年-9-月起的重大变化)后的广告策略调整。

### 亚太

[东南亚](paths/d-platforms/d6-southeast-asia-ai-guide.md)（Shopee + Lazada）的多语言本地化和直播带货。[日本 Rakuten](paths/d-platforms/d8-rakuten-japan-ai-guide.md) 的店铺自定义、积分生态和邮件营销。[韩国 Coupang](paths/d-platforms/d11-coupang-korea-ai-guide.md) 的 Rocket Delivery 和韩语 Listing。

### 欧洲与拉美

[Mercado Libre](paths/d-platforms/d7-mercado-libre-ai-guide.md) 的西语/葡语本地化和拉美市场特点。[Otto 和 Zalando](paths/d-platforms/d13-europe-marketplaces-guide.md) 的德国市场和 EU 合规（CE/EPR/VAT/GPSR）。

### 跨平台策略

如果你在多个平台运营，[跨平台协同](paths/d-platforms/cross-platform-strategy.md)教你一个核心文档适配三个平台、做跨平台归因和广告预算分配。[平台全景对比](paths/d-platforms/platform-comparison.md)把 13 个平台和 7 个社交渠道放在一起对比。

---

## 技术

如果你是开发者，想构建自己的 AI 电商工具。

从[数据管道](paths/b-developers/b1-data-pipeline.md)开始 — 了解 [Amazon 数据源全景](paths/b-developers/b1-data-pipeline.md#12-amazon-数据源全景)，用 SP-API 和 pandas 搭建自动化报告处理。然后用[预测模型](paths/b-developers/b2-prediction-models.md)做 SKU 销量预测，理解[时间序列预测的原理](paths/b-developers/b2-prediction-models.md#11-时间序列预测的第一性原理)和电商预测的特殊挑战。

想做智能问答？[RAG 知识库](paths/b-developers/b3-rag-knowledge-base.md)讲了 [RAG 和 Fine-tuning 怎么选](paths/b-developers/b3-rag-knowledge-base.md#12-rag-vs-fine-tuning-的选择)，用 LlamaIndex + Chroma 搭建产品 FAQ 系统。想做自动化？[Agent 工作流](paths/b-developers/b4-agent-workflow.md)讲了 [Agent、Chain 和 RAG 三种模式的区别](paths/b-developers/b4-agent-workflow.md#12-agent-vs-chain-vs-rag三种模式的区别)和 [ReAct 思维框架](paths/b-developers/b4-agent-workflow.md#13-react-模式agent-的核心思维框架)，用 LangGraph + CrewAI 构建运营监控 Agent。想用 Claude 直接管理广告和产品？[MCP 集成](paths/b-developers/b6-mcp-agentic-workflow.md)讲了 [MCP 协议和传统 API 的区别](paths/b-developers/b6-mcp-agentic-workflow.md#12-mcp-vs-传统-api-集成)。

还有[本地模型部署](paths/b-developers/b5-local-model-deploy.md)（[云端 vs 本地的决策框架](paths/b-developers/b5-local-model-deploy.md#12-云端-vs-本地决策框架)、Ollama + LoRA 微调）、[Review NLP 系统](paths/b-developers/b7-review-nlp-system.md)（BERTopic 主题建模 + 情感分析）、[电商 Dashboard](paths/b-developers/b8-ecommerce-dashboard.md)（Streamlit + Plotly + AI 异常检测）、[AI 图片生成 Pipeline](paths/b-developers/b9-ai-image-pipeline.md)（ComfyUI/Stable Diffusion 批量生成）。

---

## 管理

如果你是管理者，想推动团队 AI 转型。

先做 [AI 能力评估](paths/c-managers/c1-ai-assessment.md)，了解 [AI 落地的三个阶段](paths/c-managers/c1-ai-assessment.md#12-ai-落地的三个阶段)，用 [10 个问题的成熟度问卷](paths/c-managers/c1-ai-assessment.md#41-ai-成熟度评估问卷10-个问题)评估团队现状，参考 [5 人、20 人、50 人团队的落地案例](paths/c-managers/c1-ai-assessment.md#7-学习资源)。然后通过[团队建设](paths/c-managers/c2-team-building.md)让 80%+ 的人每天用 AI，用 [ROI 评估](paths/c-managers/c3-roi-evaluation.md)量化 AI 投入的回报，用[竞争情报](paths/c-managers/c5-competitive-intelligence.md)监控竞品的 AI 动态。

---

## Notebook

18 个 Colab Notebook，一键运行：[选品](notebooks/a1-product-research.ipynb) · [Listing](notebooks/a2-multilingual-listing.ipynb) · [广告](notebooks/a3-advertising.ipynb) · [差评](notebooks/a4-negative-review-analysis.ipynb) · [库存](notebooks/a5-inventory-reorder.ipynb) · [合规](notebooks/a6-compliance-checker.ipynb) · [定价](notebooks/a8-price-tracker.ipynb) · [GEO](notebooks/a9-geo-audit.ipynb) · [品牌](notebooks/a10-brand-audit.ipynb) · [利润](notebooks/a11-profit-calculator.ipynb) · [IP](notebooks/a12-ip-patent-search.ipynb) · [数据](notebooks/b1-data-pipeline.ipynb) · [预测](notebooks/b2-sales-forecast.ipynb) · [NLP](notebooks/b7-review-analysis.ipynb) · [Dashboard](notebooks/b8-dashboard-demo.ipynb) · [ROI](notebooks/c3-roi-evaluation.ipynb) · [跨平台](notebooks/d3-cross-platform-content.ipynb) · [社交](notebooks/e1-social-content-calendar.ipynb)

## 案例

[AI Listing 优化](docs/case-studies/ai-listing-optimization.md) — 4 小时 → 45 分钟/SKU

[AI 广告优化](docs/case-studies/ai-ppc-optimization.md) — ACOS 35% → 18%

[AI Review 驱动选品](docs/case-studies/ai-review-to-product.md) — 评分 4.6 vs 竞品 4.2

[全部案例 →](docs/case-studies/)

---

## 内容索引

### 按主题

| Domain | Topics |
|--------|--------|
| AI 基础 | [AI 演进](paths/0-foundations/f1-ai-evolution.md) · [Prompt 工程](paths/0-foundations/f2-prompt-engineering.md) · [RAG](paths/0-foundations/f3-rag-knowledge.md) · [Agent](paths/0-foundations/f4-agent-automation.md) · [RPA](paths/0-foundations/f5-rpa-automation.md) · [工具对比](paths/0-foundations/f6-ai-tools-comparison.md) · [AI 全景评估](paths/0-foundations/ai-landscape.md) |
| 选品与市场 | [选品洞察](paths/a-operators/a1-product-research.md) · [定价策略](paths/a-operators/a8-pricing-strategy.md) · [知识产权](paths/a-operators/a12-ip-protection.md) |
| 供应链 | [库存与供应链](paths/a-operators/a5-inventory.md) |
| 内容与转化 | [Listing 优化](paths/a-operators/a2-listing-optimization.md) · [视觉内容](paths/a-operators/a7-visual-content.md) · [品牌建设](paths/a-operators/a10-brand-building.md) |
| 流量与获客 | [广告优化](paths/a-operators/a3-advertising.md) · [SEO/GEO](paths/a-operators/a9-seo-geo.md) · [Growth Hack](paths/a-operators/a13-ai-growth-hack.md) |
| 社交媒体 | [Instagram/Facebook](paths/e-social-media/e1-instagram-facebook-ai-guide.md) · [YouTube](paths/e-social-media/e2-youtube-ai-guide.md) · [小红书](paths/e-social-media/e3-xiaohongshu-ai-guide.md) · [Pinterest](paths/e-social-media/e4-pinterest-ai-guide.md) · [WhatsApp](paths/e-social-media/e5-whatsapp-business-ai-guide.md) · [Reddit](paths/e-social-media/e6-reddit-ai-guide.md) · [跨渠道](paths/e-social-media/e7-social-media-cross-channel.md) |
| 客户运营 | [客服与售后](paths/a-operators/a4-customer-service.md) |
| 合规与财务 | [合规风控](paths/a-operators/a6-compliance.md) · [财务分析](paths/a-operators/a11-financial-analysis.md) · [AI 风险治理](paths/c-managers/c4-ai-risk-governance.md) |
| 多平台 — 货架 | [Walmart](paths/d-platforms/d4-walmart-ai-guide.md) · [eBay](paths/d-platforms/d9-ebay-ai-guide.md) · [AliExpress](paths/d-platforms/d10-aliexpress-ai-guide.md) · [Temu](paths/d-platforms/d5-temu-seller-guide.md) · [Faire](paths/d-platforms/d12-faire-wholesale-ai-guide.md) |
| 多平台 — 独立站 | [Shopify](paths/d-platforms/shopify-ai-guide.md) |
| 多平台 — 短视频 | [TikTok Shop](paths/d-platforms/tiktok-shop-ai-guide.md) |
| 多平台 — 亚太 | [东南亚](paths/d-platforms/d6-southeast-asia-ai-guide.md) · [日本](paths/d-platforms/d8-rakuten-japan-ai-guide.md) · [韩国](paths/d-platforms/d11-coupang-korea-ai-guide.md) |
| 多平台 — 欧洲拉美 | [Mercado Libre](paths/d-platforms/d7-mercado-libre-ai-guide.md) · [Otto/Zalando](paths/d-platforms/d13-europe-marketplaces-guide.md) |
| 跨平台策略 | [跨平台协同](paths/d-platforms/cross-platform-strategy.md) · [平台对比](paths/d-platforms/platform-comparison.md) |
| AI 系统构建 | [数据管道](paths/b-developers/b1-data-pipeline.md) · [预测模型](paths/b-developers/b2-prediction-models.md) · [RAG 知识库](paths/b-developers/b3-rag-knowledge-base.md) · [Agent](paths/b-developers/b4-agent-workflow.md) · [本地部署](paths/b-developers/b5-local-model-deploy.md) · [MCP](paths/b-developers/b6-mcp-agentic-workflow.md) · [Review NLP](paths/b-developers/b7-review-nlp-system.md) · [Dashboard](paths/b-developers/b8-ecommerce-dashboard.md) · [图片生成](paths/b-developers/b9-ai-image-pipeline.md) |
| 团队与管理 | [能力评估](paths/c-managers/c1-ai-assessment.md) · [团队建设](paths/c-managers/c2-team-building.md) · [ROI](paths/c-managers/c3-roi-evaluation.md) · [竞争情报](paths/c-managers/c5-competitive-intelligence.md) |

### 按角色

| 路径 | 适合谁 | 阶段 | 模块 |
|------|--------|------|------|
| Path A 运营 | 选品/运营/广告/客服 | 先修 | [AI 基础](paths/0-foundations/) · [AI 全景评估](paths/0-foundations/ai-landscape.md) |
| | | 核心 | [A1 选品](paths/a-operators/a1-product-research.md) → [A2 Listing](paths/a-operators/a2-listing-optimization.md) → [A3 广告](paths/a-operators/a3-advertising.md) → [A4 客服](paths/a-operators/a4-customer-service.md) → [A5 库存](paths/a-operators/a5-inventory.md) → [A6 合规](paths/a-operators/a6-compliance.md) |
| | | 进阶 | [A7 视觉](paths/a-operators/a7-visual-content.md) · [A8 定价](paths/a-operators/a8-pricing-strategy.md) · [A9 SEO/GEO](paths/a-operators/a9-seo-geo.md) · [A10 品牌](paths/a-operators/a10-brand-building.md) · [A11 财务](paths/a-operators/a11-financial-analysis.md) · [A12 IP](paths/a-operators/a12-ip-protection.md) · [A13 增长](paths/a-operators/a13-ai-growth-hack.md) |
| Path B 技术 | 开发/数据/BI | 核心 | [B1 数据](paths/b-developers/b1-data-pipeline.md) → [B2 预测](paths/b-developers/b2-prediction-models.md) → [B3 RAG](paths/b-developers/b3-rag-knowledge-base.md) → [B4 Agent](paths/b-developers/b4-agent-workflow.md) |
| | | 进阶 | [B5 部署](paths/b-developers/b5-local-model-deploy.md) · [B6 MCP](paths/b-developers/b6-mcp-agentic-workflow.md) · [B7 NLP](paths/b-developers/b7-review-nlp-system.md) · [B8 Dashboard](paths/b-developers/b8-ecommerce-dashboard.md) · [B9 图片](paths/b-developers/b9-ai-image-pipeline.md) |
| Path C 管理 | 团队负责人/创始人 | 核心 | [C1 评估](paths/c-managers/c1-ai-assessment.md) → [C2 团队](paths/c-managers/c2-team-building.md) → [C3 ROI](paths/c-managers/c3-roi-evaluation.md) |
| | | 进阶 | [C4 风险](paths/c-managers/c4-ai-risk-governance.md) · [C5 竞情](paths/c-managers/c5-competitive-intelligence.md) |

---

欢迎贡献。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) · [免责声明](DISCLAIMER.md) · *An AAAI China Chapter Initiative*
