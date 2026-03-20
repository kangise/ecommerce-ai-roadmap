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

想先了解 AI 能做什么？从 [AI 基础](paths/0-foundations/) 开始 — [AI 演进](paths/0-foundations/f1-ai-evolution.md)、[Prompt 工程](paths/0-foundations/f2-prompt-engineering.md)、[RAG](paths/0-foundations/f3-rag-knowledge.md)、[Agent](paths/0-foundations/f4-agent-automation.md)，以及一份 [AI 全景评估](paths/0-foundations/ai-landscape.md)帮你判断优先级。

---

## 选品

[选品与市场洞察](paths/a-operators/a1-product-research.md) — 用 AI 做 [竞品 Review 痛点分析](paths/a-operators/a1-product-research.md#31-竞品-review-痛点分析)、[市场可行性 5 维度评估](paths/a-operators/a1-product-research.md#32-市场可行性快速评估)、[关键词需求聚类](paths/a-operators/a1-product-research.md#33-关键词需求聚类)。内含完整的 [选品 SOP 工作流](paths/a-operators/a1-product-research.md#4-选品实战工作流)和 [常见选品陷阱](paths/a-operators/a1-product-research.md#5-常见选品陷阱)。

[定价策略](paths/a-operators/a8-pricing-strategy.md) — [Buy Box 定价策略](paths/a-operators/a8-pricing-strategy.md#21-amazon-buy-box-定价策略)、[价格弹性分析](paths/a-operators/a8-pricing-strategy.md#22-价格弹性分析)、[竞品价格带分析](paths/a-operators/a8-pricing-strategy.md#23-竞品价格带分析)、AI 竞品价格监控。

[知识产权保护](paths/a-operators/a12-ip-protection.md) — [选品阶段专利排查](paths/a-operators/a12-ip-protection.md#21-选品阶段的专利排查)、[AI 辅助专利分析](paths/a-operators/a12-ip-protection.md#22-ai-辅助专利分析)、[TRO 临时限制令防范](paths/a-operators/a12-ip-protection.md#23-tro临时限制令风险防范)、商标监控。

## 供应链

[库存与供应链](paths/a-operators/a5-inventory.md) — [FBA 库存关键指标](paths/a-operators/a5-inventory.md#12-amazon-fba-库存关键指标)、AI 补货预测、安全库存计算、供应商评估。

## 内容

[Listing 优化](paths/a-operators/a2-listing-optimization.md) — 从 [A9 到 COSMO/Rufus 的算法演进](paths/a-operators/a2-listing-optimization.md#11-amazon-搜索算法演进从-a9-到-cosmo--rufus)，到 [Listing 全套一键生成](paths/a-operators/a2-listing-optimization.md#31-listing-全套生成标题--五点--描述--search-terms)（标题+五点+描述+Search Terms），到 [多语言本地化](paths/a-operators/a2-listing-optimization.md#32-多语言本地化不是直译)（不是翻译，是文化适配+本地关键词+度量转换），到 [Q&A 预埋](paths/a-operators/a2-listing-optimization.md)让 Rufus 推荐你的产品。

[视觉内容](paths/a-operators/a7-visual-content.md) — [AI 产品图片生成](paths/a-operators/a7-visual-content.md#2-ai-产品图片生成)（Midjourney/DALL-E 实操）、[信息图/卖点图](paths/a-operators/a7-visual-content.md#23-信息图卖点图-ai-生成)、[AI 产品视频](paths/a-operators/a7-visual-content.md#3-ai-产品视频生成)。

[品牌建设](paths/a-operators/a10-brand-building.md) — [品牌故事框架](paths/a-operators/a10-brand-building.md#21-品牌故事框架)与 AI 生成、[品牌视觉一致性](paths/a-operators/a10-brand-building.md#3-ai-品牌视觉一致性)、[2026 DTC 品牌趋势](paths/a-operators/a10-brand-building.md#13-2026-年-dtc-品牌趋势)。

## 流量

[广告优化](paths/a-operators/a3-advertising.md) — [搜索词报告 AI 分析](paths/a-operators/a3-advertising.md#31-搜索词报告分析)（四象限分类：明星词/潜力词/观察词/浪费词）、[广告文案 A/B 测试](paths/a-operators/a3-advertising.md#32-广告文案-ab-测试)、[否定关键词策略](paths/a-operators/a3-advertising.md#33-否定关键词策略)、[新品 30 天广告启动计划](paths/a-operators/a3-advertising.md)。

[SEO/GEO](paths/a-operators/a9-seo-geo.md) — [Amazon SEO 2026 核心清单](paths/a-operators/a9-seo-geo.md#21-2026-amazon-seo-核心清单)、[Google SEO for Shopify](paths/a-operators/a9-seo-geo.md#3-google-seo-for-shopify)、[GEO 优化实操](paths/a-operators/a9-seo-geo.md#4-geo-优化实操)（让 ChatGPT/Perplexity/Gemini 推荐你的产品的 5 个策略）。

[AI Growth Hack](paths/a-operators/a13-ai-growth-hack.md) — 从选品验证到规模化的 5 阶段增长飞轮。

## 社交媒体

### 主流平台

[Instagram/Facebook](paths/e-social-media/e1-instagram-facebook-ai-guide.md) — Reels 脚本批量生成、Advantage+ 智能广告、Shopping 标签优化、[Instagram vs TikTok vs YouTube 内容策略差异](paths/e-social-media/e1-instagram-facebook-ai-guide.md#2-instagram-vs-tiktok-vs-youtube内容策略差异)。

[YouTube](paths/e-social-media/e2-youtube-ai-guide.md) — [YouTube SEO 双引擎](paths/e-social-media/e2-youtube-ai-guide.md#21-youtube-搜索算法的双引擎)、AI 关键词研究、长视频评测脚本、Shorts 创作、Shopping + Affiliate 变现。

[小红书](paths/e-social-media/e3-xiaohongshu-ai-guide.md) — [CES 评分机制](paths/e-social-media/e3-xiaohongshu-ai-guide.md#11-ces-评分机制)、[流量分发逻辑](paths/e-social-media/e3-xiaohongshu-ai-guide.md#12-流量分发逻辑)、AI 种草笔记创作、KOL/KOC 合作。

[Pinterest](paths/e-social-media/e4-pinterest-ai-guide.md) — [Pinterest 搜索排名因素](paths/e-social-media/e4-pinterest-ai-guide.md#21-pinterest-搜索排名因素)、Board 策略、视觉搜索引擎优化、Shopping Ads。

### 对话与社区

[WhatsApp](paths/e-social-media/e5-whatsapp-business-ai-guide.md) — [Business App vs API 选择](paths/e-social-media/e5-whatsapp-business-ai-guide.md#11-whatsapp-business-app-vs-api)、[AI Chatbot 工作流设计](paths/e-social-media/e5-whatsapp-business-ai-guide.md#21-电商-chatbot-工作流设计)、多语言自动回复。

[Reddit](paths/e-social-media/e6-reddit-ai-guide.md) — ["Reddit before buying" 趋势](paths/e-social-media/e6-reddit-ai-guide.md#11-reddit-before-buying-趋势)、[Reddit AI 购物搜索](paths/e-social-media/e6-reddit-ai-guide.md#12-reddit-ai-购物搜索2026-新功能)（2026 新功能）、Subreddit 选择策略。

### 跨渠道

[跨渠道策略](paths/e-social-media/e7-social-media-cross-channel.md) — 一个内容多平台适配、跨渠道归因、预算分配。

## 客服

[客服与售后](paths/a-operators/a4-customer-service.md) — [客服场景全景](paths/a-operators/a4-customer-service.md#12-客服场景全景)、差评批量分析（自动分类+频率统计+改善方案）、多语言客服回复生成、[账号申诉 Plan of Action](paths/a-operators/a6-compliance.md#36-amazon-政策违规应对)、A-to-Z Claim 应对。

## 合规与财务

[合规与风控](paths/a-operators/a6-compliance.md) — [主要市场合规框架对比](paths/a-operators/a6-compliance.md#12-主要市场的合规框架对比)、[多市场合规对比 Prompt](paths/a-operators/a6-compliance.md#31-多市场合规对比深化版)（CE/FCC/PSE/UKCA 一表对比）、[合规成本估算](paths/a-operators/a6-compliance.md#33-合规成本估算)、[BSA AI Agent 合规新规](paths/a-operators/a6-compliance.md#61-2026-新趋势amazon-ai-agent-合规要求bsa-更新)。

[财务分析](paths/a-operators/a11-financial-analysis.md) — [常见财务盲区](paths/a-operators/a11-financial-analysis.md#11-常见的财务盲区)、[Amazon 真实利润计算公式](paths/a-operators/a11-financial-analysis.md#21-amazon-真实利润计算公式)、[成本优化矩阵](paths/a-operators/a11-financial-analysis.md#31-成本优化矩阵)、6 个月现金流预测。

[AI 风险治理](paths/c-managers/c4-ai-risk-governance.md) — AI 幻觉风险、数据隐私、使用治理政策。

---

## 多平台

### 货架电商

[Walmart](paths/d-platforms/d4-walmart-ai-guide.md) · [eBay](paths/d-platforms/d9-ebay-ai-guide.md) · [AliExpress](paths/d-platforms/d10-aliexpress-ai-guide.md) · [Temu](paths/d-platforms/d5-temu-seller-guide.md) · [Faire](paths/d-platforms/d12-faire-wholesale-ai-guide.md)

### 独立站

[Shopify AI 指南](paths/d-platforms/shopify-ai-guide.md) — 全链路手册：选品、产品页优化、[GEO 优化](paths/d-platforms/shopify-ai-guide.md#213-geo-优化实操-让-ai-推荐你的产品)（让 AI 推荐你的产品）、[Agentic Storefronts](paths/d-platforms/shopify-ai-guide.md#212-agentic-storefronts-与-ucp-协议-在-ai-平台内直接卖货)（在 ChatGPT 内直接卖货）、[Klaviyo 邮件个性化](paths/d-platforms/shopify-ai-guide.md#23-shopify-邮件营销深度方法论-从-klaviyo-到-ai-个性化)、[Amazon 转 Shopify 迁移方法论](paths/d-platforms/shopify-ai-guide.md#28-从-amazon-迁移到-shopify-的完整方法论)。

### 短视频与直播

[TikTok Shop](paths/d-platforms/tiktok-shop-ai-guide.md) — [Hook 公式库](paths/d-platforms/tiktok-shop-ai-guide.md#152-hook-设计方法论-不是吸引注意力而是制造信息缺口)（信息缺口理论）、[3 幕视频脚本](paths/d-platforms/tiktok-shop-ai-guide.md#153-视频脚本的3-幕结构)（转化率 3-5x）、[达人量化评分模型](paths/d-platforms/tiktok-shop-ai-guide.md#162-ai-达人筛选的量化评分模型)（100 分制）、[直播分钟级脚本](paths/d-platforms/tiktok-shop-ai-guide.md#173-直播脚本的节奏设计)、[GMV Max 优化](paths/d-platforms/tiktok-shop-ai-guide.md#142-gmv-max-强制化-2025-年-9-月起的重大变化)。

### 亚太

[东南亚](paths/d-platforms/d6-southeast-asia-ai-guide.md) · [日本 Rakuten](paths/d-platforms/d8-rakuten-japan-ai-guide.md) · [韩国 Coupang](paths/d-platforms/d11-coupang-korea-ai-guide.md)

### 欧洲与拉美

[Mercado Libre](paths/d-platforms/d7-mercado-libre-ai-guide.md) · [Otto/Zalando](paths/d-platforms/d13-europe-marketplaces-guide.md)

### 跨平台策略

[跨平台协同](paths/d-platforms/cross-platform-strategy.md) · [平台全景对比](paths/d-platforms/platform-comparison.md)

---

## 技术

给开发者的 9 个模块。

### 数据与预测

[数据管道](paths/b-developers/b1-data-pipeline.md) — [Amazon 数据源全景](paths/b-developers/b1-data-pipeline.md#12-amazon-数据源全景)、SP-API 接入、pandas 自动化报告合并。

[预测模型](paths/b-developers/b2-prediction-models.md) — [时间序列预测原理](paths/b-developers/b2-prediction-models.md#11-时间序列预测的第一性原理)、Prophet/AutoGluon 实操、SKU 90 天销量预测。

### 知识库与 Agent

[RAG 知识库](paths/b-developers/b3-rag-knowledge-base.md) — [RAG vs Fine-tuning 选择](paths/b-developers/b3-rag-knowledge-base.md#12-rag-vs-fine-tuning-的选择)、LlamaIndex + Chroma 搭建产品 FAQ 问答系统。

[Agent 工作流](paths/b-developers/b4-agent-workflow.md) — [Agent vs Chain vs RAG 区别](paths/b-developers/b4-agent-workflow.md#12-agent-vs-chain-vs-rag三种模式的区别)、[ReAct 模式](paths/b-developers/b4-agent-workflow.md#13-react-模式agent-的核心思维框架)、LangGraph + CrewAI 构建运营监控 Agent。

[MCP 集成](paths/b-developers/b6-mcp-agentic-workflow.md) — [MCP 核心概念](paths/b-developers/b6-mcp-agentic-workflow.md#11-mcp-核心概念)、[MCP vs 传统 API](paths/b-developers/b6-mcp-agentic-workflow.md#12-mcp-vs-传统-api-集成)、用 Claude 对话管理广告和产品。

### 部署与应用

[本地部署](paths/b-developers/b5-local-model-deploy.md) — [云端 vs 本地决策框架](paths/b-developers/b5-local-model-deploy.md#12-云端-vs-本地决策框架)、[硬件要求速查](paths/b-developers/b5-local-model-deploy.md#13-硬件要求速查)、Ollama + LoRA 微调。

[Review NLP](paths/b-developers/b7-review-nlp-system.md) — BERTopic 主题建模、情感分析、自动洞察生成。

[Dashboard](paths/b-developers/b8-ecommerce-dashboard.md) — Streamlit + Plotly 多平台 KPI Dashboard、AI 异常检测。

[AI 图片生成](paths/b-developers/b9-ai-image-pipeline.md) — ComfyUI/Stable Diffusion 产品图批量生成 Pipeline。

## 管理

[AI 能力评估](paths/c-managers/c1-ai-assessment.md) — [AI 落地三阶段](paths/c-managers/c1-ai-assessment.md#12-ai-落地的三个阶段)、[AI 成熟度评估问卷](paths/c-managers/c1-ai-assessment.md#41-ai-成熟度评估问卷10-个问题)、[5/20/50 人团队落地案例](paths/c-managers/c1-ai-assessment.md#7-学习资源)。

[团队建设](paths/c-managers/c2-team-building.md) — 培训计划、习惯养成，目标：团队 80%+ 每天用 AI。

[ROI 评估](paths/c-managers/c3-roi-evaluation.md) — ROI 计算框架、效果衡量方法。

[竞争情报](paths/c-managers/c5-competitive-intelligence.md) — 竞品 AI 动态监控、竞争格局分析。

---

## Notebook

18 个 Colab Notebook，一键运行：[选品](notebooks/a1-product-research.ipynb) · [Listing](notebooks/a2-multilingual-listing.ipynb) · [广告](notebooks/a3-advertising.ipynb) · [差评](notebooks/a4-negative-review-analysis.ipynb) · [库存](notebooks/a5-inventory-reorder.ipynb) · [合规](notebooks/a6-compliance-checker.ipynb) · [定价](notebooks/a8-price-tracker.ipynb) · [GEO](notebooks/a9-geo-audit.ipynb) · [品牌](notebooks/a10-brand-audit.ipynb) · [利润](notebooks/a11-profit-calculator.ipynb) · [IP](notebooks/a12-ip-patent-search.ipynb) · [数据](notebooks/b1-data-pipeline.ipynb) · [预测](notebooks/b2-sales-forecast.ipynb) · [NLP](notebooks/b7-review-analysis.ipynb) · [Dashboard](notebooks/b8-dashboard-demo.ipynb) · [ROI](notebooks/c3-roi-evaluation.ipynb) · [跨平台](notebooks/d3-cross-platform-content.ipynb) · [社交](notebooks/e1-social-content-calendar.ipynb)

## 案例

[AI Listing 优化](docs/case-studies/ai-listing-optimization.md) — 4 小时 → 45 分钟/SKU

[AI 广告优化](docs/case-studies/ai-ppc-optimization.md) — ACOS 35% → 18%

[AI Review 驱动选品](docs/case-studies/ai-review-to-product.md) — 评分 4.6 vs 竞品 4.2

[全部案例 →](docs/case-studies/)

---

欢迎贡献。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) · [免责声明](DISCLAIMER.md) · *An AAAI China Chapter Initiative*
