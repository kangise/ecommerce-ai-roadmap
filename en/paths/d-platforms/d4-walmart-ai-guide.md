[🇨🇳 中文](../../paths/d-platforms/d4-walmart-ai-guide.md) | 🇺🇸 English

# D4. Walmart Marketplace AI Guide

> **Path**: Path D: Multi-Platform · **Module**: D4
> **Last Updated**: 2026-03-14
> **Difficulty**: ⭐⭐ Intermediate
> **Estimated Time**: 2-3 hours
> **Prerequisites**: [Path A Operations](../a-operators/) (70% of Amazon experience directly transferable)

🏠 [Hub Home](../../README.md) · 📋 [Path D Overview](README.md)

---

## 📖 Chapter Navigation

1. [Walmart vs Amazon Core Differences](#1-walmart-vs-amazon-core-differences)
2. [Walmart SEO & Listing Optimization](#2-walmart-seo--listing-optimization)
3. [Walmart Connect Advertising](#3-walmart-connect-advertising)
4. [WFS Logistics Decisions](#4-wfs-logistics-decisions)
5. [Amazon → Walmart Migration Methodology](#5-amazon--walmart-migration-methodology)
6. [Prompt Templates](#6-prompt-templates)
7. [Completion Checklist](#7-completion-checklist)

---

## What You'll Produce in This Module

- A Walmart Listing optimization plan (adapted from Amazon experience)
- A Walmart Connect advertising strategy
- An Amazon → Walmart migration checklist

> 💡 **Core Concept**: Walmart Marketplace is the most natural second platform for Amazon sellers. 250K+ active sellers, GMV $10B+, ad revenue $6.4B (+46% YoY). 70% of AI methodologies from Path A can be directly reused — this guide focuses only on the differences.

---

## 1. Walmart vs Amazon Core Differences

| Dimension | Amazon | Walmart |
|-----------|--------|---------|
| Seller Count | 2M+ | 250K+ |
| Competition Level | Extremely High | Moderate (window of opportunity) |
| Buy Box Algorithm | Review count + price + FBA | Price weighted more heavily + WFS |
| Listing Quality Score | No unified score | Listing Quality Score (visible) |
| Ad System | Amazon PPC (mature) | Walmart Connect (fast-growing) |
| Fulfillment | FBA | WFS (Walmart Fulfillment Services) |
| Commission | 8-15% (varies by category) | 6-15% (generally slightly lower) |
| Omnichannel | Online only | Online + 4,700 stores + Walmart+ |
| Customer Profile | All ages, skews mid-to-high income | Family-oriented, price-sensitive |

### 1.1 Walmart's Unique Advantages

- **Lower competition**: 1/8 the seller count of Amazon, less competitive pressure in the same categories
- **Omnichannel**: Online orders can be picked up in-store, reaching customers Amazon can't
- **Fast ad growth**: Walmart Connect ad revenue +46% YoY, early-mover advantage
- **Walmart+**: Growing membership program, similar to Prime but with lower penetration

---

## 2. Walmart SEO & Listing Optimization

> 📎 **Related Reading**: [A2 Listing Optimization](../a-operators/a2-listing-optimization.md#1-listing-methodology-the-fundamentals-before-ai) — General Amazon Listing optimization methodology from A2 can be referenced, with 70% directly transferable to Walmart.

### 2.1 Listing Quality Score

Walmart has a visible Listing Quality Score (Amazon doesn't), which directly impacts search rankings:

```
Listing Quality Score Components:
├── Content Quality — Highest weight
│   ├── Title: 50-75 characters optimal, format "Brand + Product Name + Key Attributes (Size/Color/Quantity)"
│   │   ├── Must be Title Case (capitalize first letter of each major word)
│   │   ├── No all caps, special characters, or promotional info ("Sale""Free Shipping")
│   │   ├── No prices in the title
│   │   └── Difference from Amazon: Amazon allows 200-char keyword-stuffed titles; Walmart requires concise
│   │
│   ├── Key Features (Bullet Points): 3-10, each no more than 80 characters
│   │   ├── First 3 are most important (visible before fold)
│   │   ├── Start with verbs or benefit points ("Provides...", "Features...")
│   │   └── Difference from Amazon: Amazon allows 500 chars/bullet; Walmart requires more concise
│   │
│   ├── Description: At least 150 words, recommended 300-500 words
│   │   ├── Supports Rich Media (similar to A+ Content)
│   │   ├── Can include HTML formatting (bold, lists, tables)
│   │   └── Recommended structure: Use cases → Core features → Specifications → Brand story
│   │
│   └── Attributes: Fill in all optional attributes
│       ├── Color, size, material, weight, origin, etc.
│       ├── Attribute completeness directly affects search filter matching
│       └── Many sellers overlook this — completing all attributes is a low-cost ranking boost
│
├── Image Quality
│   ├── Main image: Pure white background (RGB 255,255,255), ≥1000x1000px
│   ├── Secondary images: At least 4 (recommended 6-8)
│   │   ├── Lifestyle images (product in use)
│   │   ├── Size comparison images (compared to common objects)
│   │   ├── Detail close-ups
│   │   ├── What's in the box
│   │   └── Infographics (selling points overlaid with text)
│   ├── Video: Strongly recommended (Walmart gives extra weight to listings with video)
│   ├── 360° view: Bonus
│   └── Difference from Amazon: Walmart images should be more "authentic" — less heavy editing, making Walmart users feel "real and trustworthy"
│
├── Price Competitiveness
│   ├── Walmart compares prices with Amazon, Target, eBay, etc.
│   ├── Overpricing lowers Score and may lose Buy Box
│   ├── Recommendation: Walmart pricing = Amazon price or slightly lower by 5-10%
│   └── Psychological pricing: End in .88 or .97 (Walmart customer habit)
│
└── Inventory & Fulfillment
    ├── WFS usage (significant boost, similar to FBA's impact on Amazon rankings)
    ├── Delivery speed: 2-day shipping is baseline, next-day is a bonus
    ├── Stock availability: Frequent stockouts lower Score
    └── Return rate: High return rates lead to ranking suppression
```

### 2.2 Walmart Title Optimization Formula

| Category | Amazon Title Style | Walmart Title Style (Correct) |
|----------|-------------------|-------------------------------|
| Electronics | "UGREEN USB C Hub 8-in-1 Multiport Adapter with 4K HDMI, 100W PD, 3 USB 3.0, SD/TF Card Reader for MacBook Pro Air" | "UGREEN USB C Hub 8-in-1 with 4K HDMI, 100W PD Charging" |
| Home | "Portable Neck Fan, Hands Free Bladeless Fan, 360° Cooling, 3 Speeds, USB Rechargeable, Lightweight for Outdoor Sports Travel" | "Portable Neck Fan, Bladeless 360° Cooling, 3 Speeds, USB Rechargeable" |
| Beauty | "Vitamin C Serum for Face with Hyaluronic Acid, Retinol, Amino Acids - Anti Aging Skin Brightening Serum for Dark Spots, Fine Lines, Wrinkles - 1 fl oz" | "Vitamin C Face Serum with Hyaluronic Acid, Anti-Aging, 1 fl oz" |

**AI Title Conversion Prompt:**

```
你是一个 Walmart Listing 标题优化专家。

以下是我的 Amazon 标题：
[粘贴 Amazon 标题]

请转换为 Walmart 格式，要求：
1. 50-75 字符（Amazon 允许 200，Walmart 要简洁）
2. 格式：品牌 + 产品名 + 1-2 个核心属性
3. Title Case（每个主要词首字母大写）
4. 不包含促销信息、价格、"Best""#1"等词
5. 保留最重要的搜索关键词
6. 给出 3 个变体供选择
```

### 2.3 Walmart Rich Media (Similar to A+ Content)

Walmart's Rich Media feature allows enhanced content in the description area:

| Feature | Amazon A+ Content | Walmart Rich Media |
|---------|-------------------|-------------------|
| Brand Story | ✅ | ✅ |
| Comparison Table | ✅ | ✅ |
| Image-Text Modules | ✅ | ✅ |
| Video Embed | ✅ (Premium A+) | ✅ (All sellers) |
| 360° View | ❌ | ✅ |
| Technical Requirements | Amazon backend editor | Supports HTML/CSS |
| Threshold | Requires Brand Registry | Available to all sellers |

> **Key Difference**: Walmart Rich Media is open to all sellers (Amazon A+ requires Brand Registry), and supports HTML/CSS customization for greater flexibility.

**AI-Generated Walmart Rich Media Content Prompt:**

```
你是一个 Walmart Rich Media 内容专家。

产品：[名称]
卖点：[5 个]
目标受众：Walmart 用户（偏家庭、价格敏感、重视实用性）

请生成 Rich Media 内容方案：
1. 品牌故事模块（100 字，强调品质和价值）
2. 产品特性模块（3 个图文块，每块：标题+50 字描述+图片建议）
3. 对比表格（我的产品 vs 2 个竞品，5 个维度）
4. 使用场景模块（3 个场景，每个：场景名+30 字描述+图片建议）
5. FAQ 模块（5 个常见问题+回答）

注意：Walmart 用户更看重"实用性"和"性价比"，不要太"高端品牌感"。
```

---

## 3. Walmart Connect Advertising

> 📎 **Related Reading**: [A3 Advertising Optimization](../a-operators/a3-advertising.md#31-search-term-report-analysis) — The general search term report analysis methodology can be directly reused for Walmart Connect.

### 3.1 Ad Types Explained

| Ad Type | Placement | Billing | Min Bid | Best For |
|---------|-----------|---------|---------|----------|
| Sponsored Products - Automatic | Search results + product pages | CPC | $0.20 | New product testing, keyword discovery |
| Sponsored Products - Manual | Search results + product pages | CPC | $0.20 | Precise keyword targeting |
| Sponsored Brands | Top banner on search results | CPC | $1.00 | Brand awareness, category positioning |
| Sponsored Videos | Video placement in search results | CPC | $0.20 | Product demos, differentiation |
| Display Ads | On-site + off-site | CPM/CPC | Per Campaign | Retargeting, brand exposure |

### 3.2 First-Price vs Second-Price Bidding

This is the biggest difference between Walmart and Amazon advertising:

```
Amazon (Second-Price Bidding):
You bid $1.50, second-highest bid is $1.00
→ You actually pay $1.01 (second-highest + $0.01)
→ Strategy: You can bid high; you won't actually pay that much

Walmart (First-Price Bidding):
You bid $1.50
→ You actually pay $1.50 (you pay what you bid)
→ Strategy: You must bid precisely; overbidding is wasting money
```

**Walmart Bidding Strategy Best Practices:**

| Strategy | Description | Use Case |
|----------|-------------|----------|
| Conservative Bidding | Start at 70% of category suggested bid | New product testing phase |
| Staircase Testing | Increase by 10% every 3 days, observe ROAS changes | Finding optimal bid |
| Time-of-Day Adjustment | Increase bids during high-conversion periods (weekends/evenings) | Mature optimization |
| Keyword Tiering | High-conversion keywords get higher bids, long-tail gets lower | Limited budget |
| Auto + Manual Combo | Auto campaigns discover keywords, Manual campaigns target precisely | All stages |

### 3.3 Walmart Search Term Report Analysis

Walmart's search term report format differs from Amazon's. The AI analysis prompt needs to be adapted:

```
你是一个 Walmart Connect 广告优化专家。

以下是我的 Walmart 搜索词报告数据（过去 14 天）：

Campaign: [名称]
总花费: $[X]
总点击: [X]
总订单: [X]
ROAS: [X]

搜索词数据（按花费排序 Top 20）：
| 搜索词 | 展示 | 点击 | 花费 | 订单 | 销售额 | ROAS |
[粘贴数据]

请分析：
1. 高 ROAS 词（>4x）：这些词应该提高出价多少？
2. 低 ROAS 词（<2x）：哪些应该降低出价，哪些应该否定？
3. 高展示低点击词：是出价问题还是 Listing 问题？
4. 零转化高花费词：立即否定的候选词
5. 新发现的长尾机会词
6. 预算重新分配建议

注意 Walmart 特殊性：
- 第一价格竞价，出价调整要更精确（不像 Amazon 可以出高价）
- Walmart 用户更价格敏感，低价产品的转化率通常更高
- 周末和晚上的转化率通常高于工作日白天
```

### 3.4 Walmart Advertising 30-Day Launch Plan

```
Week 1: Data Collection Phase
├── Launch 1 Automatic Campaign (budget $20/day)
├── Launch 1 Manual Campaign (5-10 core keywords, budget $15/day)
├── Bids: 80% of category suggested bid
└── Goal: Collect search term data, don't chase ROAS

Week 2: Optimization Phase
├── Analyze search term reports
├── Extract high-converting terms from Automatic → add to Manual
├── Negate low-performing terms
├── Adjust bids (high-converting +15%, low-converting -20%)
└── Goal: ROAS > 2x

Week 3: Expansion Phase
├── Add Sponsored Brands Campaign (if brand registered)
├── Test Sponsored Videos (if video assets available)
├── Expand keyword list (add long-tail keywords)
├── Increase budget for high-converting campaigns
└── Goal: ROAS > 3x

Week 4: Scaling
├── Increase budget 30-50% for stable campaigns
├── Launch Display Ads (retargeting)
├── Establish weekly optimization SOP
└── Goal: ROAS > 4x, ad sales ratio 20-30%
```

---

## 4. WFS Logistics Decisions

> 📎 **Related Reading**: [A5 Inventory Management](../a-operators/a5-inventory.md#1-inventory-methodology-the-fundamentals-before-ai) — General inventory management and restocking methodology from A5.

### 4.1 WFS vs FBA Detailed Comparison

| Dimension | WFS | FBA |
|-----------|-----|-----|
| Storage Fee (Standard) | $0.75/cu ft/month | $0.87/cu ft/month (Jan-Sep) |
| Storage Fee (Peak) | No peak surcharge | $2.40/cu ft/month (Oct-Dec) |
| Fulfillment Fee (Small) | Starting at $3.45 | Starting at $3.22 |
| Fulfillment Fee (Large) | Typically 10-15% lower than FBA | Higher |
| Long-Term Storage Fee | None (2026 policy) | Yes (charged after 365 days) |
| Return Handling | Walmart handles, lower cost | Amazon handles, higher cost |
| Multi-Channel Fulfillment | MCS (new feature, -30% for first-time users) | MCF |
| Buy Box Boost | Significant (similar to FBA) | Significant |
| Delivery Speed | 2-3 days (Walmart+ next-day) | 1-2 days (Prime) |
| Inbound Requirements | More lenient | Strict (many labeling/packaging requirements) |

### 4.2 WFS Cost Calculation AI Prompt

```
你是一个电商物流成本分析专家。

我的产品信息：
- 产品尺寸：[长x宽x高] 英寸
- 产品重量：[X] 磅
- 月销量：Amazon [X] 单，Walmart [X] 单
- 当前 FBA 费用/单：$[X]

请计算并对比：
1. FBA 月度总成本（配送费+仓储费+长期仓储风险）
2. WFS 月度总成本（配送费+仓储费）
3. 自发货成本估算（USPS/UPS/FedEx）
4. 最优物流方案建议
5. 库存分配比例建议（FBA:WFS:自发货）
```

### 4.3 Walmart Multichannel Solutions (MCS)

MCS is Walmart's multi-channel fulfillment service (similar to Amazon MCF), newly launched in 2026:
- Use WFS inventory to fulfill orders from other channels (Shopify, eBay, own website)
- First-time users get 30% fulfillment fee discount
- Integrates with Shopify, BigCommerce, WooCommerce
- Delivery speed: 2-3 days

> **Strategy Tip**: If you sell on both Amazon and Walmart, you can use WFS+MCS to replace some FBA+MCF, reducing logistics costs (especially during peak season, since WFS has no peak storage surcharge).

---

## 5. Amazon → Walmart Migration Methodology

### 5.1 Pre-Migration Assessment

```
你是一个多平台电商策略专家。

我目前在 Amazon 的业务数据：
- 品类：[X]
- 月销量：[X] 单
- 月收入：$[X]
- 平均售价：$[X]
- 利润率：[X]%
- 主要竞品数量：[X]

请评估 Walmart 迁移可行性：
1. 这个品类在 Walmart 的竞争程度（搜索该品类关键词，看结果数量和 Review 数量）
2. 价格带是否匹配 Walmart 用户（Walmart 用户平均客单价低于 Amazon）
3. 预估 Walmart 月销量（通常是 Amazon 的 10-30%，取决于品类）
4. 预估利润率变化（佣金差异+物流差异+广告差异）
5. 迁移优先级建议（立即/观望/不建议）
```

### 5.2 Detailed Migration Checklist

```
Phase 1: Preparation (1-2 weeks)
├── [ ] Register Walmart Marketplace seller account
│   ├── Required: US business entity (or EIN)
│   ├── Required: W-9 tax form
│   ├── Review time: 2-4 weeks
│   └── Note: Walmart's review is stricter than Amazon; not all applications are approved
├── [ ] Prepare UPC/GTIN (Walmart requires a unique UPC for each product)
├── [ ] Prepare product images (adapted to Walmart style, more "authentic")
└── [ ] Research Walmart category commission rates

Phase 2: Listing Upload (1 week)
├── [ ] Convert title format (50-75 characters, Title Case)
├── [ ] Rewrite Key Features (each ≤80 characters, more concise)
├── [ ] Create Rich Media content
├── [ ] Fill in all product attributes (boost Listing Quality Score)
├── [ ] Set pricing (recommended = Amazon price or -5~10%)
└── [ ] Upload images (adapted to Walmart style)

Phase 3: Logistics Setup (1 week)
├── [ ] Register for WFS
├── [ ] Create inbound shipment plan
├── [ ] Send initial inventory (recommended 30-day supply)
└── [ ] Set up self-fulfillment backup option

Phase 4: Advertising Launch (2-4 weeks)
├── [ ] Launch Automatic Campaign
├── [ ] Launch Manual Campaign (core keywords)
├── [ ] Analyze search term reports weekly
└── [ ] Gradually optimize bids and keywords

Phase 5: Ongoing Optimization
├── [ ] Check Listing Quality Score weekly
├── [ ] Optimize ads weekly
├── [ ] Monitor Buy Box status
├── [ ] Participate in Walmart promotions (Rollbacks, Flash Deals)
└── [ ] Establish Walmart-specific data tracking
```

### 5.3 Walmart-Specific Promotion Mechanisms

| Promotion Type | Description | Amazon Comparison |
|----------------|-------------|-------------------|
| Rollbacks | Temporary price reduction, Walmart marks with "Rollback" label | Similar to Lightning Deal |
| Flash Deals | Limited-time special pricing | Similar to Lightning Deal |
| Clearance | Clearance pricing | Similar to Outlet Deal |
| Walmart+ Weekend | Walmart+ member-exclusive promotions | Similar to Prime Day |
| Holiday Promotions | BFCM, Back to School, etc. | Similar |

### 5.4 Common Migration Mistakes

| Mistake | Consequence | Correct Approach |
|---------|-------------|------------------|
| Directly copying Amazon titles | Low Listing Quality Score, poor rankings | Rewrite to 50-75 character Walmart format |
| Using Amazon pricing | May lose Buy Box (Walmart price-matches more aggressively) | Price = Amazon price or slightly lower |
| Ignoring attribute fields | Won't match search filters | Fill in all optional attributes |
| Using Amazon PPC bidding strategy | Wasted budget (first-price bidding) | Start at 70% of suggested bid, adjust gradually |
| Not using WFS | Lose Buy Box advantage | Prioritize WFS |
| Ignoring Walmart customer profile | Content mismatch | Emphasize practicality and value, don't go too "premium" |

---

## 6. Prompt Templates

### 6.1 Walmart Category Opportunity Analysis

```
你是一个 Walmart Marketplace 品类分析专家。

我目前在 Amazon 销售 [品类]，月销 [X] 单。

请分析这个品类在 Walmart 的机会：
1. Walmart 上该品类的竞争程度（卖家数量、Review 数量）
2. 价格带对比（Walmart vs Amazon）
3. 预估月销量潜力
4. 进入策略建议
5. 需要注意的 Walmart 特有合规要求
```

---

## 6.2 Walmart Buy Box Deep Dive

### Buy Box Algorithm Factor Weights

The core difference between Walmart Buy Box and Amazon Buy Box is that price carries more weight:

```
Walmart Buy Box Algorithm Factors (ranked by weight):

1. Price (Highest Weight)
├── Product price + shipping total
├── Price comparison with Amazon/Target/eBay and other platforms
├── Overpricing directly loses Buy Box
├── Recommendation: Total price (product + shipping) ≤ Amazon same-product price
└── Psychological pricing: End in .88 or .97

2. Delivery Speed and Method
├── WFS (Walmart Fulfillment Services) → Highest priority
├── 2-day shipping → High priority
├── 3-5 day shipping → Medium priority
├── 5+ day shipping → Low priority
└── Walmart+ next-day → Extra bonus

3. Seller Performance Metrics
├── On-Time Delivery Rate > 95%
├── Valid Tracking Rate > 99%
├── Cancellation Rate < 2%
├── Return Rate — the lower the better
└── Customer Satisfaction Score

4. Inventory Depth
├── Sufficient inventory → Bonus
├── Frequent stockouts → Ranking suppression
└── Pre-order/out-of-stock status → Lose Buy Box

5. Seller Account Health
├── Account age
├── Historical sales volume
├── Brand registration status
└── Violation history
```

> 📎 **Related Reading**: [D1 Shopify](shopify-ai-guide.md#13-case-studies-shopify-store-ai-implementation) — If you also run a DTC store, refer to D1 for Shopify brand building and DTC strategies.

### Buy Box Monitoring & Optimization AI Prompt

```
你是一个 Walmart Buy Box 优化专家。

我的产品数据：
- ASIN/Item ID: [X]
- 我的售价: $[X]
- 竞品最低价: $[X]
- 我的配送方式: [WFS/自发货/2天配送]
- 我的 Buy Box 占有率: [X]%
- 我的卖家评分: [X]
- 竞品数量: [X] 个卖家

请分析：
1. 我为什么没有 100% 占有 Buy Box？
2. 价格需要调整到多少才能提高 Buy Box 占有率？
3. 配送方式是否需要升级？
4. 卖家绩效中哪些指标需要改善？
5. 如果有多个竞品卖家，我的竞争策略是什么？
6. 是否建议使用自动调价工具？如果是，推荐哪些？
```

### Walmart Automated Repricing Strategies

| Strategy | Description | Use Case | Risk |
|----------|-------------|----------|------|
| Match Lowest Price | Always match the lowest price | Commodity products, multi-seller competition | Margin compression |
| Price Range | Set min/max price, adjust within range | Products with brand premium | May occasionally lose Buy Box |
| ROAS-Based Repricing | Raise price when ad ROAS is high, lower when low | Ad-driven products | Requires data accumulation |
| Time-Based Repricing | Raise on weekends/evenings, lower on weekdays | Products with time-based conversion differences | Requires testing |
| Competitor-Linked | Monitor competitor price changes, auto-respond | Highly competitive categories | May trigger price wars |

---

## 6.3 Walmart Category Commission Rate Table

| Category | Commission Rate | Amazon Comparison |
|----------|----------------|-------------------|
| Consumer Electronics | 8% | Amazon 8-15% |
| Home & Furniture | 10% | Amazon 15% |
| Apparel | 5-15% | Amazon 17% |
| Beauty & Personal Care | 8% | Amazon 8-15% |
| Toys | 8% | Amazon 15% |
| Sports & Outdoors | 8% | Amazon 15% |
| Pet Supplies | 8% | Amazon 15% |
| Grocery | 8% | Amazon 8% |
| Jewelry & Watches | 15% | Amazon 20% |
| Auto Parts | 12% | Amazon 12% |

> **Key Finding**: Walmart has significantly lower commission rates than Amazon in Home (10% vs 15%), Apparel (5-15% vs 17%), Toys (8% vs 15%), and Jewelry (15% vs 20%). These categories offer greater profit margins on Walmart.

---

## 6.4 Walmart Seller Center Data Analysis

### Key Reports & Metrics

```
Walmart Seller Center Core Reports:

I. Sales Reports
├── Item Performance
│   ├── Page Views
│   ├── Units Sold
│   ├── Revenue
│   ├── Buy Box %
│   └── Conversion Rate
│
├── Sales Trend
│   ├── Daily/Weekly/Monthly sales trends
│   ├── YoY/MoM changes
│   └── Category comparison
│
└── Returns Report
    ├── Return rate
    ├── Return reason breakdown
    └── Return cost

II. Advertising Reports (Walmart Connect)
├── Campaign Performance
├── Search Term Report
├── Keyword Performance
└── Placement Report

III. Inventory Reports
├── Inventory Health
├── WFS Inventory
├── Stranded Inventory
└── Restock Recommendations

IV. Seller Performance
├── On-Time Delivery Rate
├── Valid Tracking Rate
├── Cancellation Rate
├── Customer Satisfaction Score
└── Policy Compliance
```

### AI Weekly Report Analysis Prompt

```
你是一个 Walmart Marketplace 数据分析专家。

以下是我的 Walmart 店铺过去 7 天的数据：

销售数据：
- 总收入: $[X]（上周 $[X]，变化 [X]%）
- 总订单: [X]（上周 [X]）
- 平均客单价: $[X]
- 转化率: [X]%
- Buy Box 平均占有率: [X]%

Top 5 产品表现：
| 产品 | 页面浏览 | 销量 | 收入 | 转化率 | Buy Box% |
[粘贴数据]

广告数据：
- 总广告花费: $[X]
- 广告收入: $[X]
- ROAS: [X]
- ACOS: [X]%

卖家绩效：
- 准时发货率: [X]%
- 有效追踪率: [X]%
- 取消率: [X]%
- 退货率: [X]%

请提供：
1. 本周表现总结（3 句话，与上周对比）
2. 表现最好的产品及原因分析
3. 表现下滑的产品及改善建议
4. Buy Box 占有率变化分析（如果下降，原因是什么）
5. 广告优化建议（基于 ROAS 和搜索词数据）
6. 卖家绩效改善建议（如果有指标低于标准）
7. 下周重点行动项（最多 3 个）
```

---

## 6.5 Walmart Omnichannel Strategy

### Online + Offline Synergy (Walmart's Unique Advantage)

Walmart has 4,700+ physical stores — something Amazon doesn't have:

| Omnichannel Feature | Description | Impact on Sellers |
|---------------------|-------------|-------------------|
| Store Pickup | Order online, pick up in-store | Increases conversion (users find it more convenient) |
| Ship from Store | Ship from nearest store | Faster delivery speed |
| Returns to Store | Buy online, return in-store | Reduces return friction (but may increase return rate) |
| Walmart+ | Free delivery for members + in-store benefits | Member users have higher conversion rates |
| Local Delivery | 2-hour local delivery | Advantage for specific categories (food/daily essentials) |

### Walmart+ Membership Strategy

Walmart+ is Walmart's membership program (similar to Amazon Prime):
- Monthly $12.95 or annual $98
- Free delivery (no minimum purchase)
- In-store scan & go checkout
- Paramount+ streaming
- Gas discounts

**Impact on Sellers**:
- Walmart+ members have 30-50% higher conversion rates than non-members
- WFS products automatically qualify for Walmart+ free delivery
- Recommendation: Prioritize WFS to ensure products appeal to Walmart+ members

---

## 6.6 Common Walmart Pitfalls Deep Dive

### ❌ Pitfall 1: Directly Copying Amazon Listings

**Problem**: Amazon titles allow 200 characters of keyword stuffing; Walmart titles require 50-75 concise characters. Direct copying results in extremely low Listing Quality Scores.

**Example**:
```
Amazon Title (Wrong for Walmart):
"UGREEN USB C Hub 8-in-1 Multiport Adapter with 4K HDMI 60Hz, 100W Power Delivery, 3 USB 3.0 Ports, SD/TF Card Reader, Gigabit Ethernet for MacBook Pro Air iPad Pro Dell XPS Surface Pro"

Walmart Title (Correct):
"UGREEN USB C Hub 8-in-1 with 4K HDMI, 100W PD Charging"
```

**AI Fix Prompt**:
```
以下是我从 Amazon 复制到 Walmart 的 Listing，请帮我适配为 Walmart 格式：

Amazon 标题：[粘贴]
Amazon Bullet Points：[粘贴]
Amazon 描述：[粘贴]

请输出：
1. Walmart 标题（50-75 字符，Title Case）
2. Walmart Key Features（3-10 条，每条 ≤80 字符）
3. Walmart 描述（300-500 字，结构化，支持 HTML）
4. 需要填写的产品属性清单
5. Listing Quality Score 预估和优化建议
```

### ❌ Pitfall 2: Ignoring Walmart Customer Profile Differences

**Problem**: Walmart and Amazon customers have different profiles; content strategy needs adjustment.

| Dimension | Amazon Customers | Walmart Customers |
|-----------|-----------------|-------------------|
| Income Level | Mid-to-high income | Mid-to-low income, family-oriented |
| Purchase Motivation | Convenience + wide selection | Price + practicality |
| Decision Factors | Review count + brand | Price + delivery speed |
| Content Preference | Detailed specs + brand story | Concise, practical + value-focused |
| Image Preference | Polished + lifestyle | Authentic + practical + clear |

**AI Content Adaptation Prompt**:
```
以下是我的 Amazon 产品描述，请改写为适合 Walmart 用户的风格：

Amazon 描述：[粘贴]

Walmart 用户特征：
- 更价格敏感，强调性价比
- 更注重实用性，减少品牌故事
- 更喜欢简洁直接的表达
- 家庭用户为主，强调家庭使用场景

请改写，保持核心信息但调整语气和重点。
```

### ❌ Pitfall 3: Overbidding on Ads (First-Price Bidding)

**Problem**: Many sellers transitioning from Amazon are used to bidding high (because Amazon uses second-price bidding, so you don't actually pay that much). On Walmart, bidding high means actually paying high.

**Solution**:
```
Walmart Bid Optimization Steps:

1. Check category suggested bid (provided in Walmart backend)
2. Initial bid = Suggested bid × 70%
3. Run for 3 days, observe impressions and clicks
4. If impressions are insufficient → Increase by 10%
5. If impressions are sufficient but ROAS is low → Decrease by 10%
6. Adjust every 3 days until optimal bid is found
7. Record optimal bid for each keyword, build a bid database

Key Principles:
- Never make large bid adjustments at once (±10% is ideal)
- High-converting keywords can bid above suggested bid
- Long-tail keyword bids should be 30-50% below suggested bid
- Weekends/evenings can have slightly higher bids (higher conversion rates)
```

### ❌ Pitfall 4: Not Participating in Walmart Promotions

**Problem**: Walmart promotions (Rollbacks, Flash Deals) significantly impact rankings and traffic, but many new sellers don't know how to participate.

**Walmart Promotion Participation Guide**:

| Event Type | How to Participate | Discount Required | Traffic Boost |
|------------|-------------------|-------------------|---------------|
| Rollback | Apply via Seller Center backend | Typically 10-25% off | ⭐⭐⭐⭐ |
| Flash Deal | Requires invitation or application | Typically 20-40% off | ⭐⭐⭐⭐⭐ |
| Clearance | Manually set clearance price | Deep discount | ⭐⭐⭐ |
| Walmart+ Weekend | Auto-enrolled (WFS products) | No additional discount required | ⭐⭐⭐ |
| Holiday Promotions | Apply 4-6 weeks in advance | Depends on event | ⭐⭐⭐⭐⭐ |

### ❌ Pitfall 5: Ignoring Walmart Review Strategy

**Problem**: Walmart's review system differs from Amazon — Walmart allows the Spark Reviewer Program (similar to Vine), but many sellers don't know about it.

**Walmart Review Acquisition Strategies**:
- Spark Reviewer Program: Walmart's official review program, similar to Amazon Vine
- Review Accelerator: Paid review acquisition (official Walmart program)
- Organic Reviews: Accumulate through quality products and service
- Note: Walmart prohibits fake reviews; violations result in account suspension

---

## 6.7 Walmart AI Tool Ecosystem

| Tool | Purpose | Price | Rating |
|------|---------|-------|--------|
| **Walmart Seller Center** | Official backend: Listing/order/ad management | Free | ⭐⭐⭐⭐⭐ |
| **Aura** | Automated repricing + Buy Box monitoring | From $97/mo | ⭐⭐⭐⭐ |
| **Helium 10 (Walmart)** | Keyword research + Listing optimization | From $79/mo | ⭐⭐⭐⭐ |
| **Teikametrics** | AI ad optimization | % of ad spend | ⭐⭐⭐⭐ |
| **SellerApp** | Data analytics + ad optimization | From $49/mo | ⭐⭐⭐ |
| **ChatGPT/Claude** | Listing copy + data analysis + strategy planning | $20/mo | ⭐⭐⭐⭐⭐ |
| **Canva** | Product image design | Free/Pro $13/mo | ⭐⭐⭐⭐ |

---

## 7. Completion Checklist

- [ ] Complete Walmart seller registration
- [ ] Adapt and upload at least 10 Listings
- [ ] Set up WFS and complete first shipment
- [ ] Launch Walmart Connect advertising
- [ ] Establish Walmart data analysis workflow

---
> 🏠 [Hub Home](../../README.md) · 📋 [Path D Overview](README.md) · 📊 [Platform Comparison](platform-comparison.md)
> 
> **Path D**: [D1 Shopify](shopify-ai-guide.md) · [D2 TikTok](tiktok-shop-ai-guide.md) · [D3 Cross-Platform](cross-platform-strategy.md) · [D4 Walmart](d4-walmart-ai-guide.md) · [D5 Temu](d5-temu-seller-guide.md) · [D6 Southeast Asia](d6-southeast-asia-ai-guide.md) · [D7 Latin America](d7-mercado-libre-ai-guide.md) · [D8 Japan](d8-rakuten-japan-ai-guide.md) · [D9 eBay](d9-ebay-ai-guide.md) · [D10 AliExpress](d10-aliexpress-ai-guide.md) · [D11 Korea](d11-coupang-korea-ai-guide.md) · [D12 Faire](d12-faire-wholesale-ai-guide.md) · [D13 Europe](d13-europe-marketplaces-guide.md)
> 
> **Quick Jump**: [Path 0 Foundations](../0-foundations/) · [Path A Operations](../a-operators/) · [Path B Technical](../b-developers/) · [Path C Management](../c-managers/) · [Path E Social Media](../e-social-media/)