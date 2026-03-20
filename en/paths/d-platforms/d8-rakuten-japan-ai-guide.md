[🇨🇳 中文](../../paths/d-platforms/d8-rakuten-japan-ai-guide.md) | 🇺🇸 English

# D8. Rakuten Japan E-Commerce AI Guide

> **Path**: Path D: Multi-Platform · **Module**: D8
> **Last Updated**: 2026-03-14
> **Difficulty**: Intermediate
> **Estimated Time**: 1.5 hours

[Hub Home](../../README.md) · [Path D Overview](README.md)

---

> Rakuten GMV ~$31B, Japan e-commerce market $258B (2025). Japan's second-largest e-commerce platform (behind Amazon JP). Partnered with YouTube Shopping in 2026. Completely different operational logic from Amazon JP Rakuten is more like an "online department store" where sellers have high customization control.

## 1. Rakuten vs Amazon JP Core Differences

| Dimension | Amazon JP | Rakuten |
|-----------|-----------|---------|
| Store Page | Standardized (no customization) | Highly customizable (HTML pages) |
| Brand Display | Limited (A+ Content) | Extensive (custom store design) |
| Points System | Amazon Points (weak) | Rakuten Points (extremely strong, closed-loop ecosystem) |
| Email Marketing | Prohibited from contacting buyers | Encouraged (R-Mail) |
| Campaign Mechanism | Prime Day / BFCM | Super Sale / Marathon / 5th & 0th Day |
| Customer Profile | All ages | Skews female, 30-50 years old, household spending |
| Monthly Fee | None (commission-based) | ¥19,500-100,000/month (plan-based) |
| Commission | 8-15% | 2-7% (but with monthly fee) |

## 2. Rakuten-Specific Operational Differences

### 2.1 Store Page Customization

Rakuten's biggest differentiator is fully customizable store pages (HTML/CSS), similar to a mini independent website:

- Brand story pages
- Product category navigation
- Campaign landing pages
- Custom banners and visual design

AI Application: Use AI to generate Japanese store copy, campaign page content, and banner text.

### 2.2 Rakuten Points Ecosystem

Rakuten Points is one of Japan's largest points ecosystems:
- Users earn points shopping on Rakuten, paying with Rakuten Card, booking on Rakuten Travel
- Points can be used across the entire Rakuten ecosystem
- Sellers can set bonus point multipliers to attract users (similar to discounts but in points form)
- During Super Point Back events, point multipliers stack, driving massive traffic surges

### 2.3 R-Mail Email Marketing

> **Related Reading**: [D1 Shopify](shopify-ai-guide.md#23-shopify-email-marketing-deep-methodology-from-klaviyo-to-ai-personalization) Shopify's Klaviyo email marketing methodology from D1 can be referenced; email automation and personalization strategies can be reused for R-Mail.

Amazon prohibits sellers from directly contacting buyers, but Rakuten encourages it:
- R-Mail: Sellers can email users who have purchased
- Email content: New product announcements, promotions, points events, usage tutorials
- AI Application: AI-generated Japanese marketing emails, personalized recommendations, send time optimization

**R-Mail AI Generation Prompt:**

```
你是一个 Rakuten 邮件营销专家，精通日语商务邮件。

店铺信息：
- 店铺名：[名称]
- 品类：[X]
- 本次邮件目的：[新品通知/促销/复购提醒/感谢]

请生成 R-Mail 邮件：
1. 邮件标题（≤50 字符，吸引打开）
2. 邮件正文（日语，です/ます体）
- 开头：感谢+问候
- 中间：核心信息（新品/促销/推荐）
- 结尾：CTA + 积分提醒
3. 推荐发送时间（日本用户习惯）
4. 个性化变量建议（用户名、上次购买产品等）

注意：
- 日本消费者重视礼貌和细节
- 邮件不要太长（日本用户偏好简洁）
- 必须包含退订链接（日本法律要求）
- 积分相关信息是打开率最高的内容
```

### 2.4 Campaign Mechanism

> **Real Case: Rakuten × YouTube Shopping Japan Launch**
> On February 20, 2026, Google and Rakuten announced the launch of YouTube Shopping in Japan. Users watching YouTube videos can press a button to see product names and prices on screen, then navigate to Rakuten's e-commerce platform for details ([Japan Today](https://japantoday.com/category/tech/google-rakuten-to-provide-new-shopping-service-in-japan-on-youtube)). This is Japan's first e-commerce platform to partner with YouTube Shopping, and creators can earn commissions by promoting Rakuten products.

Content rephrased for compliance with licensing restrictions.

| Campaign | Frequency | Characteristics | Seller Strategy |
|----------|-----------|-----------------|-----------------|
| Super Sale | Quarterly | Site-wide mega sale, highest traffic | Prepare inventory and campaign pages 4 weeks ahead |
| Marathon | Monthly | Buy more, earn more points (cross-store accumulation) | Set tiered point multipliers to attract bundle purchases |
| 5th & 0th Day | Monthly 5/10/15/20/25/30 | 5x points day | Conversion rates significantly higher on these dates |
| Shopping Marathon | Irregular | Cross-store shopping points stacking | Participation earns extra exposure |

### 2.5 YouTube Shopping × Rakuten (2026 New Feature)

> **Related Reading**: [E2 YouTube AI Operations](../e-social-media/e2-youtube-ai-guide.md#e2-youtube-ai-operations-guide-youtube-ai-playbook) YouTube operations methodology from E2; influencer collaboration and video content strategies can be directly reused.

In February 2026, Rakuten partnered with Google to launch YouTube Shopping in Japan the first e-commerce platform in Japan to do so.

Per multiple reports ([Japan Today](https://japantoday.com/category/tech/google-rakuten-to-provide-new-shopping-service-in-japan-on-youtube), [Marketech APAC](https://marketech-apac.com/rakuten-ichiba-taps-google-to-roll-out-youtube-shopping-affiliate-programme-in-japan/), [Krows Digital](https://krows-digital.com/rakuten-youtube-shopping-japan-2026/)):

| Feature | Description |
|---------|-------------|
| In-Video Shopping | Users click "View Products" button in YouTube videos |
| Product Info Display | Product name and price shown on screen |
| Seamless Navigation | Users can navigate to Rakuten product page while continuing to watch |
| Creator Commission | YouTube creators earn commissions promoting Rakuten products |
| Affiliate Program | Based on YouTube Shopping Affiliate Programme |

Content rephrased for compliance with licensing restrictions.

**Impact on Sellers**:
- YouTube influencer collaborations become a new traffic source for Rakuten
- Need to prepare product assets suitable for video showcase
- Product pages need optimization to handle YouTube traffic
- Collaborations with Japanese YouTube creators become more valuable

### 2.6 Rakuten Initial Setup Fees

Per industry sources ([NextLevel Global](https://nextlevel.global/blog/2025/10/22/japan-ecommerce-marketplace-comparison/)), Rakuten onboarding requires an initial setup fee of ¥60,000, plus monthly subscription of ¥19,500-¥100,000 (depending on plan).

Content rephrased for compliance with licensing restrictions.

| Fee Item | Amount | Notes |
|----------|--------|-------|
| Initial Setup Fee | ¥60,000 | One-time |
| Ganbare! Plan Monthly | ¥19,500/mo | For new sellers |
| Standard Plan Monthly | ¥50,000/mo | For medium-scale |
| Mega Shop Plan Monthly | ¥100,000/mo | For large-scale |
| Commission | 2-7% (by category and plan) | Higher monthly fee = lower commission |
| System Usage Fee | 0.1% of monthly sales | Additional fee |

## 3. Japanese Listing AI Optimization

> **Related Reading**: [A2 Listing Optimization](../a-operators/a2-listing-optimization.md#42-listing-optimization-sop-improving-existing-listings) General Listing optimization methodology from A2; core optimization framework can be adapted for Japanese Listings.

### 3.1 Japanese Consumer Copy Preferences

| Dimension | Western Style | Japanese Style |
|-----------|--------------|----------------|
| Information Density | Concise, highlight key points | Detailed, comprehensive |
| Tone | Direct, confident | Polite, humble (です/ます form) |
| Trust Elements | Review count | Quality assurance, safety, Made in Japan |
| Image Style | Lifestyle | Detailed spec images, usage instruction images |
| After-Sales Promise | Simple return policy | Detailed warranty, customer service contact info |

### 3.2 AI-Generated Japanese Listing (Enhanced)

```
你是一个 Rakuten 日本市场的 Listing 优化专家，精通日语电商文案。

以下是我的英文产品信息：
- 产品名：[名称]
- 品类：[X]
- 卖点：[5 个]
- 价格：$[X]（约 ¥[X]）
- 目标用户：[描述]

请生成完整的 Rakuten 日语 Listing：

1. 商品名（日语，80-120 字符）
- 格式：【品牌名】产品名 核心属性 | 関連キーワード
- Rakuten 标题可以包含【】和 | 分隔符
- 包含搜索热词

2. キャッチコピー（宣传语，20-30 字符）
- 简短有力，突出核心价值

3. 商品説明（500-1000 字，です/ます体）
- 开头：产品概述+核心价值
- 中间：详细功能说明+使用场景
- 结尾：品質保証+售后承诺
- 包含 HTML 格式（Rakuten 支持自定义 HTML）

4. 商品スペック（规格表，所有技术参数）

5. 推荐キーワード（10-15 个日语搜索词）

6. 店铺页面文案建议
- ブランドストーリー（品牌故事）
- 選ばれる理由（为什么选择我们）
- お客様の声（客户评价精选）

注意：
- 使用です/ます体，强调品質、安心、保証
- 日本消费者喜欢详细的使用说明和注意事项
- 包含"送料無料"标识（如果适用）
- 提及积分倍率（ポイント倍）
```

### 3.3 Rakuten Store Page Design

Rakuten's biggest differentiator is fully customizable store pages (HTML/CSS):

```
Recommended Rakuten Store Page Structure:

Top Page (Homepage)
Header: Brand logo + navigation + search
Main Banner: Current promotions/new arrivals
Categories: Organized by product line
Rankings: Store's Top 5 bestsellers
New Arrivals: Recently listed products
Reviews: Curated positive review screenshots
Footer: Store info + contact + return policy
```

### 3.4 Rakuten Advertising System

| Ad Type | Description | Billing |
|---------|-------------|---------|
| RPP (Rakuten Promotion Platform) | Search results ads | CPC (from ¥25) |
| CPA Ads | Pay per conversion | 20% of transaction amount |
| Coupon Advance | Coupon ads | Per distribution volume |
| Targeting Display | Display ads | CPM |

**RPP Ad Optimization Prompt:**

```
你是一个 Rakuten RPP 广告优化专家。

我的产品：[名称]
品类：[X]
日预算：¥[X]
当前 ROAS：[X]

请优化：
1. 日语关键词策略（核心词+长尾词）
2. 出价策略（Rakuten RPP 最低 ¥25/click）
3. 与 Super Sale/Marathon 活动的配合
4. 积分倍率设置建议（提高积分倍率 vs 降价的 ROI 对比）
```

## 4. Cross-Border Onboarding Operations

### 4.1 Onboarding Paths

| Path | Description | Best For |
|------|-------------|----------|
| Direct Onboarding | Requires Japanese legal entity or local representative | Sellers with a Japanese company |
| Through Agency | Japanese local agency handles onboarding and operations | Cross-border sellers without a Japanese company |
| Rakuten Global Market | Rakuten's cross-border channel | Testing the Japanese market |

### 4.2 Onboarding Fees

| Plan | Monthly Fee | Commission | Best For |
|------|-----------|------------|----------|
| Ganbare! Plan | ¥19,500/mo | 3.5-7% | New sellers / small scale |
| Standard Plan | ¥50,000/mo | 2-4.5% | Medium scale |
| Mega Shop Plan | ¥100,000/mo | 2-4.5% | Large scale / many SKUs |

## 5. Completion Checklist

- [ ] Complete Rakuten onboarding application
- [ ] Design custom store page
- [ ] Complete Japanese Listing optimization
- [ ] Set up Rakuten Points strategy
- [ ] Establish R-Mail email marketing workflow
- [ ] Launch RPP advertising
- [ ] Participate in first Super Sale event
- [ ] Explore YouTube Shopping × Rakuten collaboration opportunities

---
> [Hub Home](../../README.md) · [Path D Overview](README.md) · [Platform Comparison](platform-comparison.md)
>
> **Path D**: [D1 Shopify](shopify-ai-guide.md) · [D2 TikTok](tiktok-shop-ai-guide.md) · [D3 Cross-Platform](cross-platform-strategy.md) · [D4 Walmart](d4-walmart-ai-guide.md) · [D5 Temu](d5-temu-seller-guide.md) · [D6 Southeast Asia](d6-southeast-asia-ai-guide.md) · [D7 Latin America](d7-mercado-libre-ai-guide.md) · [D8 Japan](d8-rakuten-japan-ai-guide.md) · [D9 eBay](d9-ebay-ai-guide.md) · [D10 AliExpress](d10-aliexpress-ai-guide.md) · [D11 Korea](d11-coupang-korea-ai-guide.md) · [D12 Faire](d12-faire-wholesale-ai-guide.md) · [D13 Europe](d13-europe-marketplaces-guide.md)
>
> **Quick Jump**: [Path 0 Foundations](../0-foundations/) · [Path A Operations](../a-operators/) · [Path B Technical](../b-developers/) · [Path C Management](../c-managers/) · [Path E Social Media](../e-social-media/)