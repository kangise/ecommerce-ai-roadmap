# D4. Walmart Marketplace AI Guide

> **Track**: Path D: Multi-Platform · **Module**: D4
> **Last updated**: 2026-03-14
> **Difficulty**: Intermediate
> **Estimated time**: 2-3 hours
> **Prerequisites**: [Path A Operations](../a-operators/) (Amazon experience is 70% directly reusable)


---

## Chapter Navigation

1. [Walmart vs Amazon Core Differences](#1-walmart-vs-amazon-core-differences)
2. [Walmart SEO & Listing Optimization](#2-walmart-seo--listing-optimization)
3. [Walmart Connect Advertising](#3-walmart-connect-advertising)
4. [WFS Logistics Decision](#4-wfs-logistics-decision)
5. [Amazon → Walmart Migration Methodology](#5-amazon--walmart-migration-methodology)
6. [Prompt Templates](#6-prompt-templates)
7. [Completion Checklist](#7-completion-checklist)

---

## What You Will Produce in This Module

- A Walmart Listing optimization plan (adapted from Amazon experience)
- A Walmart Connect ad strategy
- An Amazon → Walmart migration checklist

> **Core idea**: Walmart Marketplace is the most natural second platform for Amazon sellers. 250K+ active sellers, GMV $10B+, ad revenue $6.4 billion (+46% YoY). 70% of the AI methodology in Path A is directly reusable, and this guide only focuses on the differentiating parts.

---

## 1. Walmart vs Amazon Core Differences

| Dimension | Amazon | Walmart |
|-----------|--------|---------|
| Number of sellers | 2 million+ | 250K+ |
| Competition level | Extremely high | Medium (window of opportunity) |
| Buy Box algorithm | Review count + price + FBA | Higher price weighting + WFS |
| Listing quality score | No unified score | Listing Quality Score (visible) |
| Ad system | Amazon PPC (mature) | Walmart Connect (fast-growing) |
| Logistics | FBA | WFS (Walmart Fulfillment Services) |
| Commission | 8-15% (varies by category) | 6-15% (usually slightly lower) |
| Omnichannel | Pure online | Online + 4,700 stores + Walmart+ |
| User persona | All ages, skews middle-high income | Skews family, price-sensitive |

### 1.1 Walmart's Unique Advantages

- **Lower competition**: the number of sellers is 1/8 of Amazon's, less competitive pressure in the same category
- **Omnichannel**: online orders can be picked up in-store, reaching users Amazon can't
- **Fast ad growth**: Walmart Connect ad revenue +46% YoY, an early-mover dividend
- **Walmart+**: a growing membership system, similar to Prime but with lower penetration

---

## 2. Walmart SEO & Listing Optimization

> **Related reading**: [A2 Listing Optimization](../a-operators/a2-listing-optimization.md) — the general optimization methodology for Amazon Listings can be referenced in A2, 70% directly reusable on Walmart.

### 2.1 Listing Quality Score

Walmart has a visible Listing Quality Score (Amazon doesn't), which directly affects search ranking:

```
Composition of the Listing Quality Score:
Content quality (Content) — highest weight
Title: 50-75 characters is best, format "brand + product name + core attribute (size/color/quantity)"
Must be Title Case (first letter of each major word capitalized)
Prohibited: all caps, special characters, promotional info ("Sale," "Free Shipping")
Prohibited: including the price in the title
Difference from Amazon: Amazon allows a 200-character long title stuffed with keywords, Walmart requires conciseness

Key Features (Bullet Points): 3-10, each no more than 80 characters
The first 3 are most important (visible before the fold)
Start with a verb or benefit ("Provides...", "Features...")
Difference from Amazon: Amazon allows 500 characters/bullet, Walmart requires more concision

Description: at least 150 words, recommended 300-500 words
Supports Rich Media (similar to A+ Content)
Can include HTML formatting (bold, lists, tables)
Recommended structure: use scenario → core features → spec parameters → brand story

Attributes: fill in all optional attributes as much as possible
Color, size, material, weight, origin, etc.
Attribute completeness directly affects search-filter matching
Many sellers skip this step; filling it in completely is a low-cost ranking boost

Image quality (Images)
Hero image: pure white background (RGB 255,255,255), ≥1000x1000px
Supporting images: at least 4 (recommended 6-8)
Scene image (product in use)
Size-comparison image (compared with common objects)
Detail close-up image
Package-contents image (What's in the box)
Infographic (selling-point text overlay)
Video: strongly recommended to upload (Walmart gives Listings with video extra weight)
360° view: a bonus
Difference from Amazon: Walmart images require more "plainness," don't over-Photoshop, make Walmart users feel "authentic and reliable"

Price competitiveness (Price)
Walmart compares prices with platforms like Amazon, Target, eBay
Too-high a price lowers the Score and may lose the Buy Box
Recommendation: Walmart pricing = Amazon price or slightly lower by 5-10%
Psychological pricing: end in .88 or .97 (Walmart users' habit)

Inventory and fulfillment (Fulfillment)
WFS usage (significant boost, similar to FBA's impact on Amazon ranking)
Delivery speed: 2-day delivery is the baseline, next-day is a bonus
Inventory sufficiency: frequent stockouts lower the Score
Return rate: a high return rate gets demoted
```

### 2.2 Walmart Title Optimization Formula

| Category | Amazon title style | Walmart title style (correct) |
|----------|--------------------|-------------------------------|
| Electronics | "UGREEN USB C Hub 8-in-1 Multiport Adapter with 4K HDMI, 100W PD, 3 USB 3.0, SD/TF Card Reader for MacBook Pro Air" | "UGREEN USB C Hub 8-in-1 with 4K HDMI, 100W PD Charging" |
| Home | "Portable Neck Fan, Hands Free Bladeless Fan, 360° Cooling, 3 Speeds, USB Rechargeable, Lightweight for Outdoor Sports Travel" | "Portable Neck Fan, Bladeless 360° Cooling, 3 Speeds, USB Rechargeable" |
| Beauty | "Vitamin C Serum for Face with Hyaluronic Acid, Retinol, Amino Acids - Anti Aging Skin Brightening Serum for Dark Spots, Fine Lines, Wrinkles - 1 fl oz" | "Vitamin C Face Serum with Hyaluronic Acid, Anti-Aging, 1 fl oz" |

**AI title conversion prompt:**

```
You are a Walmart Listing title optimization expert.

Here is my Amazon title:
[paste Amazon title]

Please convert it to Walmart format, requirements:
1. 50-75 characters (Amazon allows 200, Walmart needs conciseness)
2. Format: brand + product name + 1-2 core attributes
3. Title Case (first letter of each major word capitalized)
4. Don't include promotional info, price, "Best," "#1," etc.
5. Keep the most important search keywords
6. Give 3 variants to choose from
```

### 2.3 Walmart Rich Media (Similar to A+ Content)

Walmart's Rich Media feature allows adding enhanced content in the description area:

| Feature | Amazon A+ Content | Walmart Rich Media |
|---------|-------------------|--------------------|
| Brand story | ✅ | ✅ |
| Comparison table | ✅ | ✅ |
| Image-text module | ✅ | ✅ |
| Video embed | ✅ (Premium A+) | ✅ (all sellers) |
| 360° view | ❌ | ✅ |
| Technical requirement | Amazon backend editor | Supports HTML/CSS |
| Barrier | Requires brand registration | Available to all sellers |

> **Key difference**: Walmart Rich Media is open to all sellers (Amazon A+ requires brand registration), and it supports HTML/CSS customization for higher flexibility.

**AI-generate Walmart Rich Media content prompt:**

```
You are a Walmart Rich Media content expert.

Product: [name]
Selling points: [5]
Target audience: Walmart users (skew family, price-sensitive, value practicality)

Please generate a Rich Media content plan:
1. Brand-story module (100 words, emphasize quality and value)
2. Product-feature module (3 image-text blocks, each: title + 50-word description + image suggestion)
3. Comparison table (my product vs 2 competitors, 5 dimensions)
4. Use-scenario module (3 scenarios, each: scenario name + 30-word description + image suggestion)
5. FAQ module (5 common questions + answers)

Note: Walmart users value "practicality" and "value for money" more, don't be too "premium brand."
```

---

## 3. Walmart Connect Advertising

> **Related reading**: [A3 Advertising Optimization](../a-operators/a3-advertising.md) — the general methodology for search-term report analysis is directly reusable on Walmart Connect.

### 3.1 Ad Types Explained

| Ad type | Placement | Billing | Minimum bid | Best for |
|---------|-----------|---------|-------------|----------|
| Sponsored Products - Automatic | Search results + product page | CPC | $0.20 | New-product testing, keyword discovery |
| Sponsored Products - Manual | Search results + product page | CPC | $0.20 | Precise keyword placement |
| Sponsored Brands | Search-results top banner | CPC | $1.00 | Brand awareness, category positioning |
| Sponsored Videos | Search-results video slot | CPC | $0.20 | Product demonstration, differentiation display |
| Display Ads | On-site + off-site | CPM/CPC | Per Campaign | Remarketing, brand exposure |

### 3.2 First-Price Auction vs Second-Price Auction

This is the biggest difference between Walmart and Amazon ads:

```
Amazon (second-price auction):
You bid $1.50, the second-highest bid is $1.00
→ You actually pay $1.01 (second-highest + $0.01)
→ Strategy: you can bid high, you won't actually pay that much

Walmart (first-price auction):
You bid $1.50
→ You actually pay $1.50 (you pay what you bid)
→ Strategy: you must bid precisely, bidding high is wasting money
```

**Walmart bidding-strategy best practices:**

| Strategy | Description | Applicable scenario |
|----------|-------------|---------------------|
| Conservative bid | Start at 70% of the category-suggested bid | New-product testing period |
| Ladder testing | Raise 10% every 3 days, observe ROAS change | Finding the optimal bid |
| Time-of-day adjustment | Raise bids during high-conversion periods (weekends/evenings) | Maturity-period optimization |
| Keyword tiering | High bids for high-conversion words, low bids for long-tail words | When budget is limited |
| Auto + manual combination | Auto Campaign discovers words, Manual Campaign places precisely | All phases |

### 3.3 Walmart Search-Term Report Analysis

Walmart's search-term report format differs from Amazon's, and the AI-analysis prompt needs to be adapted:

```
You are a Walmart Connect ad optimization expert.

Here is my Walmart search-term report data (past 14 days):

Campaign: [name]
Total spend: $[X]
Total clicks: [X]
Total orders: [X]
ROAS: [X]

Search-term data (sorted by spend, Top 20):
| Search term | Impressions | Clicks | Spend | Orders | Sales | ROAS |
[paste data]

Please analyze:
1. High-ROAS words (>4x): how much should I raise the bid on these?
2. Low-ROAS words (<2x): which should I lower the bid on, which should I negate?
3. High-impression low-click words: is it a bid problem or a Listing problem?
4. Zero-conversion high-spend words: candidates for immediate negation
5. Newly discovered long-tail opportunity words
6. Budget-reallocation suggestions

Note Walmart's specifics:
- First-price auction, bid adjustments need to be more precise (unlike Amazon where you can bid high)
- Walmart users are more price-sensitive, low-price products usually have a higher conversion rate
- Weekend and evening conversion rates are usually higher than weekday daytime
```

### 3.4 Walmart Advertising 30-Day Launch Plan

```
Week 1: data-collection period
Launch 1 Automatic Campaign (budget $20/day)
Launch 1 Manual Campaign (5-10 core keywords, budget $15/day)
Bid: 80% of the category-suggested bid
Goal: collect search-term data, don't pursue ROAS

Week 2: optimization period
Analyze the search-term report
Extract high-conversion words from Automatic → add to Manual
Negate inefficient words
Adjust bids (high-conversion words +15%, low-conversion words -20%)
Goal: ROAS > 2x

Week 3: expansion period
Add a Sponsored Brands Campaign (if you have brand registration)
Test Sponsored Videos (if you have video material)
Expand the keyword list (add long-tail words)
Increase the budget of high-conversion Campaigns
Goal: ROAS > 3x

Week 4: scaling
Increase the budget of stable Campaigns by 30-50%
Launch Display Ads (remarketing)
Establish a weekly optimization SOP
Goal: ROAS > 4x, ad-sales share 20-30%
```

---

## 4. WFS Logistics Decision

> **Related reading**: [A5 Inventory Management](../a-operators/a5-inventory.md) — the general methodology for inventory management and replenishment decisions is referenced in A5.

### 4.1 Detailed WFS vs FBA Comparison

| Dimension | WFS | FBA |
|-----------|-----|-----|
| Storage fee (standard) | $0.75/cubic foot/month | $0.87/cubic foot/month (Jan-Sep) |
| Storage fee (peak season) | No peak-season surcharge | $2.40/cubic foot/month (Oct-Dec) |
| Fulfillment fee (small items) | From $3.45 | From $3.22 |
| Fulfillment fee (large items) | Usually 10-15% lower than FBA | Higher |
| Long-term storage fee | None (2026 policy) | Yes (charged after 365 days) |
| Return handling | Walmart handles, lower fee | Amazon handles, higher fee |
| Multi-channel fulfillment | MCS (new feature, -30% for first-time users) | MCF |
| Buy Box bonus | Significant (similar to FBA) | Significant |
| Delivery speed | 2-3 days (Walmart+ next-day) | 1-2 days (Prime) |
| Inbound requirements | Relatively lenient | Strict (many label/packaging requirements) |

### 4.2 WFS Cost-Calculation AI Prompt

```
You are an e-commerce logistics cost analysis expert.

My product info:
- Product dimensions: [L x W x H] inches
- Product weight: [X] pounds
- Monthly sales: Amazon [X] orders, Walmart [X] orders
- Current FBA fee/order: $[X]

Please calculate and compare:
1. FBA monthly total cost (fulfillment fee + storage fee + long-term storage risk)
2. WFS monthly total cost (fulfillment fee + storage fee)
3. Self-fulfillment cost estimate (USPS/UPS/FedEx)
4. Optimal logistics-plan suggestion
5. Inventory-allocation ratio suggestion (FBA:WFS:self-fulfillment)
```

### 4.3 Walmart Multichannel Solutions (MCS)

MCS is Walmart's multi-channel fulfillment service (similar to Amazon MCF), newly launched in 2026:
- Use WFS inventory to fulfill orders from other channels (Shopify, eBay, your own website)
- First-time users enjoy a 30% fulfillment-fee discount
- Integrates with Shopify, BigCommerce, WooCommerce
- Delivery speed: 2-3 days

> **Strategy suggestion**: If you sell on both Amazon and Walmart, you can use WFS+MCS to replace part of FBA+MCF, lowering logistics costs (especially in peak season, WFS has no peak-season storage surcharge).

---

## 5. Amazon → Walmart Migration Methodology

### 5.1 Pre-Migration Assessment

```
You are a multi-platform e-commerce strategy expert.

My current Amazon business data:
- Category: [X]
- Monthly sales: [X] orders
- Monthly revenue: $[X]
- Average selling price: $[X]
- Profit margin: [X]%
- Number of main competitors: [X]

Please assess the feasibility of migrating to Walmart:
1. The competition level of this category on Walmart (search the category keyword, look at the number of results and reviews)
2. Whether the price band matches Walmart users (Walmart users' average order value is lower than Amazon's)
3. Estimated Walmart monthly sales (usually 10-30% of Amazon's, depending on the category)
4. Estimated profit-margin change (commission difference + logistics difference + ad difference)
5. Migration-priority suggestion (immediate/wait and see/not recommended)
```

### 5.2 Detailed Migration Checklist

```
Phase 1: preparation period (1-2 weeks)
[ ] Register a Walmart Marketplace seller account
Need: a US company entity (or EIN)
Need: a W-9 tax form
Review time: 2-4 weeks
Note: Walmart's review is stricter than Amazon's, not all applications pass
[ ] Prepare UPC/GTIN (Walmart requires each product to have a unique UPC)
[ ] Prepare product images (adapt to Walmart style, more "plain")
[ ] Research Walmart category commission rates

Phase 2: Listing upload (1 week)
[ ] Convert the title format (50-75 characters, Title Case)
[ ] Rewrite Key Features (each ≤80 characters, more concise)
[ ] Create Rich Media content
[ ] Fill in all product attributes (boost Listing Quality Score)
[ ] Set pricing (recommended = Amazon price or -5~10%)
[ ] Upload images (adapt to Walmart style)

Phase 3: logistics setup (1 week)
[ ] Register for WFS
[ ] Create an inbound plan
[ ] Send the first batch of inventory (recommended 30 days of sales)
[ ] Set up a self-fulfillment fallback plan

Phase 4: ad launch (2-4 weeks)
[ ] Launch an Automatic Campaign
[ ] Launch a Manual Campaign (core keywords)
[ ] Analyze the search-term report weekly
[ ] Gradually optimize bids and keywords

Phase 5: continuous optimization
[ ] Check the Listing Quality Score weekly
[ ] Optimize ads weekly
[ ] Monitor Buy Box status
[ ] Participate in Walmart promotions (Rollbacks, Flash Deals)
[ ] Establish Walmart-specific data tracking
```

### 5.3 Walmart-Specific Promotion Mechanisms

| Promotion type | Description | Comparison with Amazon |
|----------------|-------------|------------------------|
| Rollbacks | Temporary price cut, Walmart marks a "Rollback" tag | Similar to Lightning Deal |
| Flash Deals | Limited-time special price | Similar to Lightning Deal |
| Clearance | Clearance price | Similar to Outlet Deal |
| Walmart+ Weekend | Walmart+ member-exclusive promotion | Similar to Prime Day |
| Holiday promotions | BFCM, Back to School, etc. | Similar |

### 5.4 Common Migration Mistakes

| Mistake | Consequence | Correct approach |
|---------|-------------|------------------|
| Directly copying the Amazon title | Low Listing Quality Score, poor ranking | Rewrite to 50-75 character Walmart format |
| Using Amazon pricing | May lose the Buy Box (Walmart price-compares more strictly) | Price = Amazon price or slightly lower |
| Ignoring attribute filling | Search filters can't match | Fill in all optional attributes |
| Using Amazon PPC bid strategy | Waste budget (first-price auction) | Start at 70% of the suggested bid, adjust gradually |
| Not using WFS | Lose the Buy Box advantage | Prioritize using WFS |
| Ignoring the Walmart user persona | Content mismatch | Emphasize practicality and value, don't be too "premium" |

---

## 6. Prompt Templates

### 6.1 Walmart Category Opportunity Analysis

```
You are a Walmart Marketplace category analysis expert.

I currently sell [category] on Amazon, [X] orders/month.

Please analyze the opportunity of this category on Walmart:
1. The competition level of this category on Walmart (number of sellers, number of reviews)
2. Price-band comparison (Walmart vs Amazon)
3. Estimated monthly sales potential
4. Entry-strategy suggestion
5. Walmart-specific compliance requirements to note
```

---

## 6.2 Walmart Buy Box In-Depth Analysis

### Buy Box Algorithm Factor Weights

The core difference between the Walmart Buy Box and the Amazon Buy Box is that price weighting is higher:

```
Walmart Buy Box algorithm factors (sorted by weight):

1. Price (highest weight)
Product price + shipping total price
Price comparison with platforms like Amazon/Target/eBay
Too-high a price directly loses the Buy Box
Recommendation: total price (product + shipping) ≤ Amazon's price for the same product
Psychological pricing: end in .88 or .97

2. Delivery speed and method
WFS (Walmart Fulfillment Services) → highest priority
2-day delivery → high priority
3-5 day delivery → medium priority
5+ day delivery → low priority
Walmart+ next-day → extra bonus

3. Seller performance metrics
On-Time Delivery Rate > 95%
Valid Tracking Rate > 99%
Cancellation Rate < 2%
Return Rate the lower the better
Customer Satisfaction (customer-satisfaction score)

4. Inventory depth
Sufficient inventory → bonus
Frequent stockouts → demotion
Pre-order/out-of-stock status → lose the Buy Box

5. Seller account health
Account age
Historical sales
Brand-registration status
Violation record
```

> **Related reading**: [D1 Shopify](shopify-ai-guide.md) — if you also run an independent site, Shopify's brand-building and DTC strategy are referenced in D1.

### Buy Box Monitoring and Optimization AI Prompt

```
You are a Walmart Buy Box optimization expert.

My product data:
- ASIN/Item ID: [X]
- My selling price: $[X]
- Competitor lowest price: $[X]
- My fulfillment method: [WFS/self-fulfillment/2-day delivery]
- My Buy Box share: [X]%
- My seller rating: [X]
- Number of competitors: [X] sellers

Please analyze:
1. Why don't I have 100% Buy Box ownership?
2. What price do I need to adjust to in order to increase Buy Box share?
3. Does the fulfillment method need an upgrade?
4. Which metrics in seller performance need improvement?
5. If there are multiple competitor sellers, what's my competitive strategy?
6. Is it recommended to use an auto-repricing tool? If so, which are recommended?
```

### Walmart Auto-Repricing Strategy

| Strategy | Description | Applicable scenario | Risk |
|----------|-------------|---------------------|------|
| Follow the lowest price | Always match the lowest price | Standard products, multi-seller competition | Profit gets squeezed |
| Price range | Set a min/max price, adjust within the range | Products with a brand premium | May occasionally lose the Buy Box |
| ROAS-based repricing | Raise the price when ad ROAS is high, lower it when low | Ad-driven products | Requires data accumulation |
| Time-of-day repricing | Raise on weekends/evenings, lower on weekdays | Products with time-of-day conversion differences | Requires testing to validate |
| Competitor linkage | Monitor competitor price changes, auto-respond | Fiercely competitive categories | May trigger a price war |

---

## 6.3 Walmart Category Commission Rate Table

| Category | Commission rate | Comparison with Amazon |
|----------|-----------------|------------------------|
| Consumer electronics | 8% | Amazon 8-15% |
| Home & furniture | 10% | Amazon 15% |
| Apparel | 5-15% | Amazon 17% |
| Beauty & personal care | 8% | Amazon 8-15% |
| Toys | 8% | Amazon 15% |
| Sports & outdoor | 8% | Amazon 15% |
| Pet supplies | 8% | Amazon 15% |
| Grocery | 8% | Amazon 8% |
| Jewelry & watches | 15% | Amazon 20% |
| Auto parts | 12% | Amazon 12% |

> **Key finding**: Walmart's commission rates are significantly lower than Amazon's in categories like home (10% vs 15%), apparel (5-15% vs 17%), toys (8% vs 15%), and jewelry (15% vs 20%). These categories have larger profit margins on Walmart.

---

## 6.4 Walmart Seller Center Data Analysis

### Key Reports and Metrics

```
Walmart Seller Center core reports:

1. Sales reports
Item Performance
Page Views
Units Sold
Revenue
Buy Box %
Conversion Rate

Sales Trend
Daily/weekly/monthly sales trends
YoY/QoQ changes
Category comparison

Returns Report
Return rate
Return-reason categorization
Return cost

2. Ad reports (Walmart Connect)
Campaign Performance
Search Term Report
Keyword Performance
Placement Report

3. Inventory reports
Inventory Health
WFS Inventory
Stranded Inventory
Restock Recommendations

4. Seller performance
On-Time Delivery Rate
Valid Tracking Rate
Cancellation Rate
Customer Satisfaction Score
Policy Compliance
```

### AI Weekly Report Analysis Prompt

```
You are a Walmart Marketplace data analysis expert.

Here is my Walmart store data for the past 7 days:

Sales data:
- Total revenue: $[X] (last week $[X], change [X]%)
- Total orders: [X] (last week [X])
- Average order value: $[X]
- Conversion rate: [X]%
- Average Buy Box share: [X]%

Top 5 product performance:
| Product | Page views | Units sold | Revenue | Conversion rate | Buy Box% |
[paste data]

Ad data:
- Total ad spend: $[X]
- Ad revenue: $[X]
- ROAS: [X]
- ACOS: [X]%

Seller performance:
- On-time delivery rate: [X]%
- Valid tracking rate: [X]%
- Cancellation rate: [X]%
- Return rate: [X]%

Please provide:
1. This week's performance summary (3 sentences, compared with last week)
2. The best-performing product and reason analysis
3. Declining products and improvement suggestions
4. Buy Box share change analysis (if it dropped, what's the reason)
5. Ad-optimization suggestions (based on ROAS and search-term data)
6. Seller-performance improvement suggestions (if any metric is below standard)
7. Next week's key action items (at most 3)
```

---

## 6.5 Walmart Omnichannel Strategy

### Online + Offline Coordination (Walmart's Unique Advantage)

Walmart has 4,700+ physical stores, which Amazon doesn't:

| Omnichannel feature | Description | Impact on sellers |
|---------------------|-------------|-------------------|
| Store Pickup | Order online, pick up in-store | Boosts conversion rate (users find it more convenient) |
| Ship from Store | Ship from the nearest store | Faster delivery speed |
| Returns to Store | Buy online, return in-store | Lowers return friction (but may raise the return rate) |
| Walmart+ | Member free delivery + in-store discounts | Members have a higher conversion rate |
| Local Delivery | Local 2-hour delivery | An advantage for specific categories (food/daily necessities) |

### Walmart+ Membership Strategy

Walmart+ is Walmart's membership program (similar to Amazon Prime):
- Monthly fee $12.95 or annual fee $98
- Free delivery (no minimum spend)
- In-store scan checkout
- Paramount+ streaming
- Fuel discounts

**Impact on sellers**:
- Walmart+ members have a 30-50% higher conversion rate than non-members
- WFS products automatically enjoy Walmart+ free delivery
- Recommendation: prioritize using WFS, ensure the product is attractive to Walmart+ members

---

## 6.6 Walmart Common Pitfalls In-Depth Analysis

### Pitfall 1: Directly Copying the Amazon Listing

**Problem**: Amazon titles stuff 200 characters with keywords, while Walmart titles require a concise 50-75 characters. Directly copying leads to an extremely low Listing Quality Score.

**Case**:
```
Amazon title (wrong example):
"UGREEN USB C Hub 8-in-1 Multiport Adapter with 4K HDMI 60Hz, 100W Power Delivery, 3 USB 3.0 Ports, SD/TF Card Reader, Gigabit Ethernet for MacBook Pro Air iPad Pro Dell XPS Surface Pro"

Walmart title (correct):
"UGREEN USB C Hub 8-in-1 with 4K HDMI, 100W PD Charging"
```

**AI fix prompt**:
```
Here is the Listing I copied from Amazon to Walmart, please help me adapt it to Walmart format:

Amazon title: [paste]
Amazon Bullet Points: [paste]
Amazon description: [paste]

Please output:
1. Walmart title (50-75 characters, Title Case)
2. Walmart Key Features (3-10 bullets, each ≤80 characters)
3. Walmart description (300-500 words, structured, supports HTML)
4. A list of product attributes to fill in
5. Listing Quality Score estimate and optimization suggestions
```

### Pitfall 2: Ignoring the Walmart User-Persona Difference

**Problem**: Walmart users and Amazon users have different personas, and the content strategy needs adjustment.

| Dimension | Amazon user | Walmart user |
|-----------|-------------|--------------|
| Income level | Middle-high income | Middle-low income, mainly family |
| Purchase motivation | Convenience + many choices | Price + practicality |
| Decision factors | Review count + brand | Price + delivery speed |
| Content preference | Detailed specs + brand story | Concise and practical + value highlighted |
| Image preference | Refined + lifestyle | Authentic + practical + clear |

**AI content-adaptation prompt**:
```
Here is my Amazon product description, please rewrite it in a style suitable for Walmart users:

Amazon description: [paste]

Walmart user characteristics:
- More price-sensitive, emphasize value for money
- Value practicality more, reduce the brand story
- Prefer concise and direct expression
- Mainly family users, emphasize family-use scenarios

Please rewrite, keeping the core information but adjusting the tone and focus.
```

### Pitfall 3: Ad Bids Too High (First-Price Auction)

**Problem**: Many sellers coming from Amazon are used to bidding high (because Amazon is a second-price auction and they won't actually pay that much). On Walmart, bidding high means actually paying high.

**Solution**:
```
Walmart bid-optimization steps:

1. Check the category-suggested bid (provided in the Walmart backend)
2. Initial bid = suggested bid × 70%
3. Run for 3 days, observe impressions and clicks
4. If impressions are insufficient → raise 10%
5. If impressions are sufficient but ROAS is low → lower 10%
6. Adjust every 3 days until you find the optimal bid
7. Record the optimal bid for each keyword, build a bid database

Key principles:
- Never adjust the bid drastically at once (±10% is appropriate)
- High-conversion words can bid above the suggested bid
- Long-tail words should bid 30-50% below the suggested bid
- Weekends/evenings can raise bids appropriately (higher conversion rate)
```

### Pitfall 4: Not Participating in Walmart Promotions

**Problem**: Walmart's promotions (Rollbacks, Flash Deals) have a significant impact on ranking and traffic, but many new sellers don't know how to participate.

**Walmart promotion-participation guide**:

| Promotion type | How to participate | Discount requirement | Traffic boost |
|----------------|--------------------|-----------------------|---------------|
| Rollback | Apply in the Seller Center backend | Usually 10-25% off | ✅ |
| Flash Deal | Requires invitation or application | Usually 20-40% off | ✅✅ |
| Clearance | Manually set a clearance price | Large discount | ✅ |
| Walmart+ Weekend | Auto-participate (WFS products) | No extra discount requirement | ✅✅ |
| Holiday promotions | Apply 4-6 weeks in advance | Depends on the event | ✅✅✅ |

### Pitfall 5: Ignoring Walmart Review Strategy

**Problem**: Walmart's review system differs from Amazon's. Walmart allows the Spark Reviewer Program (similar to Vine), but many sellers don't know it.

**Walmart review-acquisition strategy**:
- Spark Reviewer Program: Walmart's official review program, similar to Amazon Vine
- Review Accelerator: paid review acquisition (Walmart's official program)
- Organic reviews: accumulate through quality products and service
- Note: Walmart prohibits fake reviews, violations lead to account bans

---

## 6.7 Walmart AI Tool Ecosystem

| Tool | Use | Price | Recommendation |
|------|-----|-------|----------------|
| **Walmart Seller Center** | Official backend, Listing/order/ad management | Free | ✅✅✅ |
| **Aura** | Auto-repricing + Buy Box monitoring | From $97/month | ✅✅ |
| **Helium 10 (Walmart)** | Keyword research + Listing optimization | From $79/month | ✅✅ |
| **Teikametrics** | AI ad optimization | Based on ad-spend percentage | ✅✅ |
| **SellerApp** | Data analysis + ad optimization | From $49/month | ✅ |
| **ChatGPT/Claude** | Listing copy + data analysis + strategy planning | $20/month | ✅✅✅ |
| **Canva** | Product-image design | Free/Pro $13/month | ✅✅ |

---

## 7. Completion Checklist

- [ ] Complete Walmart seller registration
- [ ] Adapt and upload at least 10 Listings
- [ ] Set up WFS and complete the first shipment
- [ ] Launch Walmart Connect advertising
- [ ] Establish a Walmart data-analysis process
