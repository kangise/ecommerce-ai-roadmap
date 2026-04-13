# A9. AI SEO 与 GEO 优化 | AI SEO & Generative Engine Optimization

> **路径**: Path A: 运营人 · **模块**: A9
> **最后更新**: 2026-03-15
> **难度**: 高级
> **预计时间**: 每天 30 分钟，2-3 周
> **前置模块**: [A2 Listing 优化](a2-listing-optimization.md)


---

## 章节导航

1. [从 SEO 到 GEO](#1-从-seo-到-geo) · 2. [Amazon SEO](#2-amazon-seo) · 3. [Google SEO](#3-google-seo-for-shopify) · 4. [GEO 优化](#4-geo-优化实操) · 5. [社交平台 SEO](#5-社交平台-seo) · 6. [工具](#6-ai-seo-工具对比) · 7. [Prompt](#7-prompt-模板) · 8. [完成标志](#8-完成标志)

---

## 本模块你将学会

- 理解 SEO → GEO 的范式转变（从 Google 排名到 AI 推荐）
- 掌握 Amazon SEO 最新算法（COSMO + Rufus）
- 掌握 Shopify Google SEO 方法论
- 学会 GEO 优化让 ChatGPT/Perplexity/Gemini 推荐你的产品
- 了解各社交平台站内 SEO

> 2026 年，1/3 的消费者已使用 AI Agent 进行产品发现。GEO 是 2026 年最重要的新技能。

---

## 1. 从 SEO 到 GEO

### 1.1 搜索行为三次变革

| 变革 | 时间 | 核心逻辑 | 电商影响 |
|------|------|---------|---------|
| Google 搜索 | 2000s-现在 | 关键词+链接+内容 | Shopify Google SEO |
| 平台内搜索 | 2010s-现在 | 平台规则+销量+转化率 | Amazon A9/COSMO |
| AI 搜索/GEO | 2024-现在 | 结构化数据+品牌权威+评价 | 被 ChatGPT/Perplexity 推荐 |

### 1.2 GEO vs 传统 SEO

| 维度 | 传统 SEO | GEO |
|------|---------|-----|
| 目标 | Google 排名 | AI 推荐/引用 |
| 用户行为 | 浏览搜索结果页 | 直接获得 AI 答案 |
| 排名因素 | 关键词+链接+内容 | 结构化数据+品牌权威+评价+被引用频率 |
| 内容格式 | 长文章、博客 | FAQ+Schema+结构化数据 |
| 衡量指标 | 排名/流量/CTR | AI 推荐频率/品牌提及率 |

### 1.3 为什么跨境卖家必须关注 GEO

- Shopify Agentic Storefronts（UCP 协议）让 AI Agent 直接在 ChatGPT 内购买
- Perplexity Comet 浏览器可代替用户在 Amazon 购物
- Google AI Overviews 在搜索结果顶部显示 AI 答案
- 不被 AI 推荐 = 失去越来越多的流量

> **相关阅读**: [D1 Shopify](../d-platforms/shopify-ai-guide.md) GEO 和 Agentic Storefronts 详见 D1

---

## 2. Amazon SEO

> **相关阅读**: [A2 Listing 优化](a2-listing-optimization.md) A9→COSMO→Rufus 完整演进详见 A2

### 2.1 2026 Amazon SEO 核心清单

```
标题：核心词前 80 字符，自然语言，COSMO 友好（回答"谁需要""为什么需要"）
Bullet Points：利益点开头，Rufus 友好（回答用户问题），前 3 条最重要
Backend：不重复标题词，含拼写变体/同义词，250 字节，空格分隔
Q&A 预埋：20+ 高频问题，Rufus 读取回答用户，答案含关键词
A+ Content：COSMO 读取理解产品，含使用场景，图片 Alt Text 含关键词
```

### 2.2 Amazon SEO 审计 Prompt

```
你是 Amazon SEO 专家，精通 COSMO 和 Rufus 算法。

我的 Listing：
- 标题: [粘贴]
- Bullet Points: [粘贴]
- Backend Search Terms: [粘贴]
- 竞品 ASIN: [3 个]

请做 SEO 审计：
1. COSMO 友好度评分（1-10）
2. Rufus 友好度评分（1-10）
3. Backend 优化建议
4. Q&A 预埋建议（10 个问题）
5. 关键词覆盖差距
6. 优先级行动清单
```

---

## 3. Google SEO for Shopify

### 3.1 技术 SEO 检查清单

| 项目 | 要求 | 工具 |
|------|------|------|
| SSL | HTTPS（Shopify 自动） | |
| Sitemap | 提交到 GSC | Google Search Console |
| Core Web Vitals | LCP<2.5s, FID<100ms, CLS<0.1 | PageSpeed Insights |
| Schema | Product/FAQ/Breadcrumb/Review | JSON-LD |
| 图片 | WebP，Alt Text 含关键词 | Shopify 图片优化 App |
| URL | 简洁，含关键词 | Shopify 后台 |

### 3.2 内容 SEO 策略

| 内容类型 | 示例 | 购买意图 | 频率 |
|----------|------|---------|------|
| 产品指南 | "How to Choose Best [品类]" | 高 | 每月 2 篇 |
| 对比文章 | "[A] vs [B]: Which Better?" | 高 | 每月 2 篇 |
| 教程 | "How to Use [产品]" | 中 | 每月 2 篇 |
| 清单 | "Top 10 [品类] 2026" | 高 | 每季度 |

### 3.3 Schema 结构化数据（GEO 基础）

```json
{
"@context": "https://schema.org",
"@type": "Product",
"name": "产品名称",
"brand": {"@type": "Brand", "name": "品牌名"},
"description": "产品描述",
"offers": {
"@type": "Offer",
"price": "29.99",
"priceCurrency": "USD",
"availability": "https://schema.org/InStock"
},
"aggregateRating": {
"@type": "AggregateRating",
"ratingValue": "4.7",
"reviewCount": "1250"
}
}
```

---

## 4. GEO 优化实操

### 4.1 让 AI 推荐你的产品的 5 个策略

| 策略 | 说明 | 难度 | 影响 |
|------|------|------|------|
| 结构化数据 | Product/FAQ Schema | | |
| FAQ 优化 | 自然语言问答+Schema | | |
| 品牌提及 | 第三方网站被提及 | | |
| 评价覆盖 | Amazon/Trustpilot 高评分 | | |
| Agentic Storefronts | Shopify UCP 协议 | | |

### 4.2 GEO 核心数据（2026 研究）

根据行业研究（[Onely](https://www.onely.com/blog/geo-for-ecommerce-how-to-boost-product-visibility-in-ai-search/)），GEO 优化的核心策略和效果：

| 策略 | 效果 | 说明 |
|------|------|------|
| 完整 Product Schema | AI 引用率提升 40-60% | 结构化数据是 AI 理解产品的基础 |
| 50+ 客户评价 | AI 推荐概率提升 2.5 倍 | 评价数量和质量直接影响 AI 推荐 |
| 竞品对比内容 | AI 引用率提升 45-70% | 购物场景下对比内容被引用最多 |

Content rephrased for compliance with licensing restrictions.

### 4.3 GEO 五大支柱（电商版）

根据 2026 年 GEO 实践指南（[TheCommerceShop](https://thecommerceshop.com/manufacturers/blog/5-pillars-of-geo-for-ecommerce/)，[Prefixbox](https://www.prefixbox.com/blog/guide-to-generative-engine-optimization/)），电商 GEO 优化有五大支柱：

| 支柱 | 说明 | 实操 |
|------|------|------|
| 实体清晰度 | AI 需要明确理解你的品牌和产品 | 完善 Schema、品牌页面、Wikipedia/Wikidata |
| 结构化内容 | AI 偏好结构化、可解析的内容 | FAQ、对比表、规格表、结构化描述 |
| 意图驱动 | 内容需要回答用户的购买意图 | "best X for Y" 类内容、使用场景描述 |
| 可购物性 | AI 答案需要能直接导向购买 | 产品页面有库存、价格准确、深链接可用 |
| 权威信号 | AI 信任有权威性的来源 | 第三方评测、媒体报道、专业认证 |

Content rephrased for compliance with licensing restrictions.

### 4.4 Agentic Commerce（AI 代理购物）

2026 年最重要的 GEO 趋势是 Agentic CommerceAI 代理代替用户完成购物（[Charle Agency](https://www.charleagency.com/articles/agentic-commerce/)）：

| 平台 | AI 购物功能 | 状态 |
|------|-----------|------|
| ChatGPT | Instant Checkout（站内直接购买） | 已上线 |
| Shopify | Agentic Storefronts（UCP 协议） | 已上线 |
| Google | AI Mode + Gemini 购物 | 已上线 |
| Microsoft | Copilot Checkout | 已上线 |
| Perplexity | Comet 浏览器代购 | 测试中 |
| Reddit | AI 购物搜索轮播 | 测试中 |

> Shopify 与 Google 共同开发了 UCP（Universal Commerce Protocol），AI 购物的开放标准（[Shopify Enterprise](https://www.shopify.com/enterprise/blog/generative-engine-optimization)）。Shopify 品牌最先能在 ChatGPT、Copilot、Gemini 等 AI 渠道内直接销售。

Content rephrased for compliance with licensing restrictions.

```
你是一个 Agentic Commerce 策略专家。

我的品牌：[名称]
销售渠道：[Amazon / Shopify / 两者都有]
品类：[X]

请评估我的 Agentic Commerce 准备度：
1. 结构化数据完整度（Product/FAQ/Breadcrumb/Review Schema）
2. AI 可发现性（ChatGPT/Perplexity/Google AI Overviews 是否被提及）
3. 可购物性（价格准确/库存/深链接/UCP 协议）
4. 行动计划（短期 1 周/中期 1 月/长期 3 月）
```

### 4.5 GEO 效果检测（增强版）

```
每月执行 GEO 审计：

1. AI 搜索测试（5 个平台）
- ChatGPT: "best [品类] 2026" → 记录是否被提及
- Perplexity: "recommend [品类] for [场景]" → 记录
- Gemini: "[品类] buying guide" → 记录
- Claude: "compare [品牌] vs [竞品]" → 记录
- Google AI Overviews: "[品类] review" → 记录

2. 竞品对比：谁被 AI 推荐更多？差距分析

3. 结构化数据验证：Google Rich Results Test + Schema.org Validator

4. 内容审计：FAQ 覆盖度、对比内容、第三方引用

5. 趋势追踪：AI 推荐频率变化、新 AI 购物渠道
```

### 4.6 AI 搜索可见度工具

| 工具 | 功能 | 价格 |
|------|------|------|
| AEO Engine | AI 搜索可见度监控（[AEO Engine](https://aeoengine.ai/blog/most-recommended-ai-search-visibility-solutions)） | 付费 |
| Nudge Now | GEO 优化平台 | 付费 |
| Otterly.ai | AI 搜索排名追踪 | 付费 |
| ChatGPT/Perplexity | 手动测试 AI 推荐 | 免费/$20/月 |
| Google Search Console | AI Overviews 数据 | 免费 |

Content rephrased for compliance with licensing restrictions.

---

## 5. 社交平台 SEO

| 平台 | 搜索机制 | 关键词位置 | 详细指南 |
|------|---------|-----------|---------|
| TikTok | 站内搜索+推荐 | 标题+描述+字幕+Hashtag | [D2](../d-platforms/tiktok-shop-ai-guide.md) |
| YouTube | 搜索+推荐 | 标题+描述+标签+字幕 | [E2](../e-social-media/e2-youtube-ai-guide.md) |
| Pinterest | 视觉搜索 | Pin 标题+描述+Board | [E4](../e-social-media/e4-pinterest-ai-guide.md) |
| 小红书 | 站内搜索（70%渗透率） | 标题+正文前200字+标签 | [E3](../e-social-media/e3-xiaohongshu-ai-guide.md) |

---

## 6. AI SEO 工具对比

| 工具 | 功能 | 价格 | 适合 |
|------|------|------|------|
| Ahrefs | 关键词+竞品+链接 | $99/月起 | 全面 SEO |
| Semrush | 关键词+广告+内容 | $130/月起 | 企业级 |
| Surfer SEO | AI 内容优化 | $89/月起 | 内容 SEO |
| Helium 10 | Amazon 关键词+Listing | $79/月起 | Amazon SEO |
| vidIQ | YouTube SEO | 免费/$4.5/月 | YouTube |
| ChatGPT/Claude | 通用 AI 辅助 | $20/月 | 所有场景 |

---

## 7. Prompt 模板

### 7.1 GEO 审计

```
你是 GEO 专家。品牌 [X]，产品 [X]，网站 [URL]。
评估：结构化数据完整度、FAQ 优化建议（10个）、品牌提及分析、评价覆盖、竞品差距、优先行动清单。
```

### 7.2 多平台关键词研究

```
产品 [X]，品类 [X]，市场 [US]。
为 Amazon/Google/TikTok/YouTube/Pinterest 各提供 10 个关键词，标注搜索量级、竞争度、推荐内容类型。
```

---

## 8. 完成标志

- [ ] 完成 Amazon Listing SEO 审计
- [ ] 为 Shopify 添加 Schema 结构化数据
- [ ] 添加 FAQ Schema（10+ 问题）
- [ ] 在 ChatGPT/Perplexity/Gemini 测试产品推荐
- [ ] 建立跨平台 SEO 关键词库
- [ ] 评估 Agentic Commerce 准备度
- [ ] 建立月度 GEO 审计流程

(a8-pricing-strategy.md) | [Path 总览](README.md) | [A10 品牌 >](a10-brand-building.md)
