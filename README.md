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

## 关于本知识库

这是一个面向跨境电商从业者的 AI 实战知识库。不是链接聚合，不是工具推荐列表 — 是可以直接拿来用的原创内容：Prompt 模板、Colab Notebook、方法论指南和实战案例。

覆盖范围：Amazon Listing 优化 / Rufus & COSMO 语义 SEO / GEO & Agentic Commerce / PPC 广告分析 / TikTok Shop 视频脚本 / Shopify 独立站 / 13 个电商平台 / 7 个社交媒体渠道。

当前规模：56 篇深度指南 · 30 个 Prompt 模板 · 18 个 Colab Notebook · 8 个实战案例 · 4 种语言。

## 如何使用

这个知识库按「角色」组织成 6 条学习路径，每条路径由若干独立模块组成。你不需要从头读到尾 — 根据你的角色选一条路径，按需挑选模块即可。

**使用流程**：

1. 先看下面的「选择你的路径」，找到适合你的路径
2. 进入路径后，每个模块都是独立的，可以跳着看
3. 每个模块包含：方法论 + Prompt 模板 + 实操步骤 + 完成标志
4. Prompt 模板可以直接复制到 ChatGPT / Claude 使用
5. Notebook 可以在 Google Colab 一键运行，不需要本地环境

**快速体验** — 复制下面的 Prompt 到 [ChatGPT](https://chat.openai.com/) 或 [Claude](https://claude.ai/)，30 秒得到一份市场分析：

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

更多 Prompt → [Prompt 模板库](prompts/)

---

## 目录

> 找特定内容？按 `T` 搜文件名，或按 `/` 全文搜索。

- [关于本知识库](#关于本知识库)
- [如何使用](#如何使用)
- [热门内容直通车](#热门内容直通车)
- [内容总览](#内容总览)
- [学习路径](#学习路径)
- [Prompt 模板库](#prompt-模板库)
- [Notebook 实验室](#notebook-实验室)
- [案例研究](#案例研究)
- [贡献指南](#贡献指南)

---

## 热门内容直通车

> 按使用频率精选 Top 10 场景。[查看全部 60 个场景 →](docs/popular-scenarios.md)

| # | 场景 | 一句话说明 | 直达 |
|---|------|----------|------|
| 1 | 竞品 Review 痛点提取 | 50 条差评 -> 痛点排名 + 改进方向 | [A1](paths/a-operators/a1-product-research.md) |
| 2 | Listing 全套一键生成 | 标题+五点+描述+Search Terms，45 分钟搞定 | [A2](paths/a-operators/a2-listing-optimization.md) |
| 3 | Rufus/COSMO 语义优化 | 从关键词匹配到意图匹配，2026 最重要的变化 | [A2](paths/a-operators/a2-listing-optimization.md#11-amazon-搜索算法演进从-a9-到-cosmo--rufus) |
| 4 | 搜索词报告 AI 分析 | 高 ROAS 词/浪费词/隐藏长尾机会 | [A3](paths/a-operators/a3-advertising.md) |
| 5 | 多市场合规对比表 | CE/FCC/PSE/UKCA 一表对比，30 分钟出清单 | [A6](paths/a-operators/a6-compliance.md) |
| 6 | GEO 优化 | 让产品被 ChatGPT/Perplexity 推荐 | [A9](paths/a-operators/a9-seo-geo.md) · [D1](paths/d-platforms/shopify-ai-guide.md) |
| 7 | TikTok Hook 公式 + 3 幕脚本 | 信息缺口理论 + 转化率 3-5x 的视频结构 | [D2](paths/d-platforms/tiktok-shop-ai-guide.md) |
| 8 | 一文档三平台适配 | 一个核心文档 -> Amazon+Shopify+TikTok | [D3](paths/d-platforms/cross-platform-strategy.md) |
| 9 | AI 利润计算器 | 含所有隐藏成本的真实利润计算 | [A11](paths/a-operators/a11-financial-analysis.md) |
| 10 | AI Growth Hack 飞轮 | 从选品到规模化的 5 阶段增长系统 | [A13](paths/a-operators/a13-ai-growth-hack.md) |

[回到目录](#目录)

---
## 内容总览

按主题域浏览所有内容，点击链接直接进入。

| Domain | Topics |
|--------|--------|
| **AI 基础** | [AI 演进](paths/0-foundations/f1-ai-evolution.md) · [Prompt 工程](paths/0-foundations/f2-prompt-engineering.md) · [RAG](paths/0-foundations/f3-rag-knowledge.md) · [Agent](paths/0-foundations/f4-agent-automation.md) · [RPA](paths/0-foundations/f5-rpa-automation.md) · [工具对比](paths/0-foundations/f6-ai-tools-comparison.md) · [AI 全景评估](paths/0-foundations/ai-landscape.md) |
| **选品与市场** | [选品与市场洞察](paths/a-operators/a1-product-research.md) · [定价策略](paths/a-operators/a8-pricing-strategy.md) · [知识产权保护](paths/a-operators/a12-ip-protection.md) |
| **供应链与库存** | [库存与供应链](paths/a-operators/a5-inventory.md) |
| **内容与转化** | [Listing 优化](paths/a-operators/a2-listing-optimization.md) · [视觉内容](paths/a-operators/a7-visual-content.md) · [品牌建设](paths/a-operators/a10-brand-building.md) |
| **流量与获客** | [广告优化](paths/a-operators/a3-advertising.md) · [SEO/GEO](paths/a-operators/a9-seo-geo.md) · [AI Growth Hack](paths/a-operators/a13-ai-growth-hack.md) |
| **社交媒体营销** | [Instagram/Facebook](paths/e-social-media/e1-instagram-facebook-ai-guide.md) · [YouTube](paths/e-social-media/e2-youtube-ai-guide.md) · [小红书](paths/e-social-media/e3-xiaohongshu-ai-guide.md) · [Pinterest](paths/e-social-media/e4-pinterest-ai-guide.md) · [WhatsApp](paths/e-social-media/e5-whatsapp-business-ai-guide.md) · [Reddit](paths/e-social-media/e6-reddit-ai-guide.md) · [跨渠道策略](paths/e-social-media/e7-social-media-cross-channel.md) |
| **客户运营** | [客服与售后](paths/a-operators/a4-customer-service.md) |
| **合规与财务** | [合规与风控](paths/a-operators/a6-compliance.md) · [财务分析](paths/a-operators/a11-financial-analysis.md) · [AI 风险治理](paths/c-managers/c4-ai-risk-governance.md) |
| **多平台 — 货架电商** | [Walmart](paths/d-platforms/d4-walmart-ai-guide.md) · [eBay](paths/d-platforms/d9-ebay-ai-guide.md) · [AliExpress](paths/d-platforms/d10-aliexpress-ai-guide.md) · [Temu](paths/d-platforms/d5-temu-seller-guide.md) · [Faire](paths/d-platforms/d12-faire-wholesale-ai-guide.md) |
| **多平台 — 独立站** | [Shopify AI 指南](paths/d-platforms/shopify-ai-guide.md) |
| **多平台 — 短视频与直播** | [TikTok Shop](paths/d-platforms/tiktok-shop-ai-guide.md) |
| **多平台 — 亚太** | [东南亚 Shopee/Lazada](paths/d-platforms/d6-southeast-asia-ai-guide.md) · [日本 Rakuten](paths/d-platforms/d8-rakuten-japan-ai-guide.md) · [韩国 Coupang](paths/d-platforms/d11-coupang-korea-ai-guide.md) |
| **多平台 — 欧洲与拉美** | [拉美 Mercado Libre](paths/d-platforms/d7-mercado-libre-ai-guide.md) · [欧洲 Otto/Zalando](paths/d-platforms/d13-europe-marketplaces-guide.md) |
| **跨平台策略** | [跨平台协同](paths/d-platforms/cross-platform-strategy.md) · [平台全景对比](paths/d-platforms/platform-comparison.md) |
| **AI 系统构建** | [数据管道](paths/b-developers/b1-data-pipeline.md) · [预测模型](paths/b-developers/b2-prediction-models.md) · [RAG 知识库](paths/b-developers/b3-rag-knowledge-base.md) · [Agent 工作流](paths/b-developers/b4-agent-workflow.md) · [本地模型部署](paths/b-developers/b5-local-model-deploy.md) · [MCP 集成](paths/b-developers/b6-mcp-agentic-workflow.md) · [Review NLP](paths/b-developers/b7-review-nlp-system.md) · [Dashboard](paths/b-developers/b8-ecommerce-dashboard.md) · [AI 图片生成](paths/b-developers/b9-ai-image-pipeline.md) |
| **团队与管理** | [AI 能力评估](paths/c-managers/c1-ai-assessment.md) · [团队建设](paths/c-managers/c2-team-building.md) · [ROI 评估](paths/c-managers/c3-roi-evaluation.md) · [竞争情报](paths/c-managers/c5-competitive-intelligence.md) |

[回到目录](#目录)

---

## 学习路径

不确定从哪里开始？按角色选一条路径。每条路径是对上面 domain 内容的推荐阅读顺序。

### Path A: 运营人 — 不写代码，用 AI 提效

适合：选品/运营/广告/客服岗 · 时间：每天 30 分钟，2-4 周 · [Path A 总览 →](paths/a-operators/)

| 阶段 | 模块 | 完成标志 |
|------|------|----------|
| 先修 | [AI 基础](paths/0-foundations/) · [AI 全景评估](paths/0-foundations/ai-landscape.md) | 理解 Prompt/RAG/Agent 的区别 |
| 核心 | [A1 选品](paths/a-operators/a1-product-research.md) → [A2 Listing](paths/a-operators/a2-listing-optimization.md) → [A3 广告](paths/a-operators/a3-advertising.md) → [A4 客服](paths/a-operators/a4-customer-service.md) → [A5 库存](paths/a-operators/a5-inventory.md) → [A6 合规](paths/a-operators/a6-compliance.md) | 每个环节有可复用的 AI 工作流 |
| 进阶 | [A7 视觉](paths/a-operators/a7-visual-content.md) · [A8 定价](paths/a-operators/a8-pricing-strategy.md) · [A9 SEO/GEO](paths/a-operators/a9-seo-geo.md) · [A10 品牌](paths/a-operators/a10-brand-building.md) · [A11 财务](paths/a-operators/a11-financial-analysis.md) · [A12 IP](paths/a-operators/a12-ip-protection.md) · [A13 增长](paths/a-operators/a13-ai-growth-hack.md) | 按需选学 |
| 扩展 | [多平台](paths/d-platforms/) · [社交媒体](paths/e-social-media/) | 拓展到 Amazon 以外 |

### Path B: 技术人 — 构建 AI 电商系统

适合：开发/数据/BI 岗 · 需要 Python · 时间：每天 1 小时，4-8 周 · [Path B 总览 →](paths/b-developers/)

| 阶段 | 模块 | 完成标志 |
|------|------|----------|
| 先修 | [AI 基础](paths/0-foundations/) | 理解 LLM/RAG/Agent 原理 |
| 核心 | [B1 数据管道](paths/b-developers/b1-data-pipeline.md) → [B2 预测模型](paths/b-developers/b2-prediction-models.md) → [B3 RAG](paths/b-developers/b3-rag-knowledge-base.md) → [B4 Agent](paths/b-developers/b4-agent-workflow.md) | 能独立构建 AI 电商工具 |
| 进阶 | [B5 本地部署](paths/b-developers/b5-local-model-deploy.md) · [B6 MCP](paths/b-developers/b6-mcp-agentic-workflow.md) · [B7 NLP](paths/b-developers/b7-review-nlp-system.md) · [B8 Dashboard](paths/b-developers/b8-ecommerce-dashboard.md) · [B9 图片](paths/b-developers/b9-ai-image-pipeline.md) | 按需选学 |

### Path C: 管理者 — AI 战略落地

适合：团队负责人/创始人 · 不需要技术背景 · 时间：集中 3-5 小时 · [Path C 总览 →](paths/c-managers/)

| 阶段 | 模块 | 完成标志 |
|------|------|----------|
| 先修 | [AI 全景评估](paths/0-foundations/ai-landscape.md) | 了解 AI 在电商各环节的成熟度 |
| 核心 | [C1 能力评估](paths/c-managers/c1-ai-assessment.md) → [C2 团队建设](paths/c-managers/c2-team-building.md) → [C3 ROI](paths/c-managers/c3-roi-evaluation.md) | 输出 AI 落地规划书 |
| 进阶 | [C4 风险治理](paths/c-managers/c4-ai-risk-governance.md) · [C5 竞争情报](paths/c-managers/c5-competitive-intelligence.md) | 风险管理和竞争战略 |

[回到目录](#目录)

---

## Prompt 模板库

30 个模板，按场景分类，可直接复制到 ChatGPT / Claude 使用。[查看完整模板库 →](prompts/README.md)

| 模板集 | 模板数 | 场景 |
|--------|--------|------|
| [选品与市场分析](prompts/product-research.md) | 3 | 竞品 Review 分析、市场评估、关键词聚类 |
| [Listing 生成与优化](prompts/listing-optimization.md) | 3 | Listing 全套生成、多语言本地化、竞品策略拆解 |
| [广告分析与优化](prompts/advertising.md) | 2 | 搜索词报告分析、广告文案 A/B 测试 |
| [客服与售后](prompts/customer-service.md) | 2 | 差评批量分析、账号申诉信 |
| [合规与风控](prompts/compliance.md) | 1 | 多市场合规对比 |
| [社交媒体运营](prompts/social-media.md) | 5 | Instagram Reels、YouTube、小红书、跨平台适配 |
| [多平台运营](prompts/multi-platform.md) | 5 | Walmart、Temu、东南亚、多平台品类分析 |
| [高级运营 A7-A13](prompts/advanced-operations.md) | 8 | AI 产品图、定价、GEO、品牌、利润、IP、增长 |

[回到目录](#目录)

---

## Notebook 实验室

18 个 Jupyter Notebook，可在 Google Colab 一键运行。[查看完整索引 →](notebooks/README.md)

| Domain | Notebook | 难度 |
|--------|----------|------|
| 选品与市场 | [a1-product-research](notebooks/a1-product-research.ipynb) · [a8-price-tracker](notebooks/a8-price-tracker.ipynb) · [a12-ip-patent-search](notebooks/a12-ip-patent-search.ipynb) | 入门-中级 |
| 内容与转化 | [a2-multilingual-listing](notebooks/a2-multilingual-listing.ipynb) · [a10-brand-audit](notebooks/a10-brand-audit.ipynb) | 中级 |
| 流量与获客 | [a3-advertising](notebooks/a3-advertising.ipynb) · [a9-geo-audit](notebooks/a9-geo-audit.ipynb) | 入门-中级 |
| 客户运营 | [a4-negative-review-analysis](notebooks/a4-negative-review-analysis.ipynb) | 入门 |
| 供应链与库存 | [a5-inventory-reorder](notebooks/a5-inventory-reorder.ipynb) | 入门 |
| 合规与财务 | [a6-compliance-checker](notebooks/a6-compliance-checker.ipynb) · [a11-profit-calculator](notebooks/a11-profit-calculator.ipynb) · [c3-roi-evaluation](notebooks/c3-roi-evaluation.ipynb) | 入门 |
| 社交媒体 | [e1-social-content-calendar](notebooks/e1-social-content-calendar.ipynb) | 入门 |
| 跨平台 | [d3-cross-platform-content](notebooks/d3-cross-platform-content.ipynb) | 中级 |
| AI 系统构建 | [b1-data-pipeline](notebooks/b1-data-pipeline.ipynb) · [b2-sales-forecast](notebooks/b2-sales-forecast.ipynb) · [b7-review-analysis](notebooks/b7-review-analysis.ipynb) · [b8-dashboard-demo](notebooks/b8-dashboard-demo.ipynb) | 入门-中级 |

[回到目录](#目录)

---

## 案例研究

带量化指标的实战案例。[查看全部案例 →](docs/case-studies/)

[回到目录](#目录)

---

## 贡献指南

欢迎贡献 Prompt 模板、Notebook、案例或修正内容。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

[回到目录](#目录)

---

## 许可证

[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) -- 自由使用，无需署名。

[免责声明](DISCLAIMER.md) -- 第三方商标、数据引用、AI 生成内容声明

---

*An AAAI China Chapter Initiative*
