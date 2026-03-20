# Advanced Operations Prompt Templates (A7-A13)

> Prompt templates covering visual content, pricing, SEO/GEO, branding, finance, IP, and Growth Hacking.
> Corresponds to Path A modules A7-A13.

[Hub Home](../README.md) · [Prompt Template Library](README.md)

---

## Template List

1. [AI Product Image Generation (A7)](#1-ai-product-image-generation-a7)
2. [Competitor Price Monitoring & Dynamic Pricing (A8)](#2-competitor-price-monitoring--dynamic-pricing-a8)
3. [GEO Audit & AI Search Optimization (A9)](#3-geo-audit--ai-search-optimization-a9)
4. [Brand Story & Visual System Generation (A10)](#4-brand-story--visual-system-generation-a10)
5. [SKU True Profit Calculation (A11)](#5-sku-true-profit-calculation-a11)
6. [Comprehensive IP Risk Assessment (A12)](#6-comprehensive-ip-risk-assessment-a12)
7. [AI Growth Hack Product Validation (A13)](#7-ai-growth-hack-product-validation-a13)
8. [Daily AI Operations Brief (A13)](#8-daily-ai-operations-brief-a13)

---

## 1. AI Product Image Generation (A7)

> Detailed methodology: [A7 Visual Content](../paths/a-operators/a7-visual-content.md)

```
You are an e-commerce product image planning expert.

My product: [Name]
Category: [X]
Target platform: [Amazon/Shopify/Instagram]
Brand colors: [X]

Please plan a complete image suite for this product:

1. Amazon main image (white background, product fills 85%+)
- Shooting angle recommendations
- Lighting plan
- AI generation prompt (Midjourney/DALL-E format)

2. Lifestyle images x3
- Descriptions of 3 different usage scenarios
- AI generation prompt for each scenario

3. Infographic images x2
- Size comparison chart layout suggestions
- Feature highlight chart layout suggestions

4. A+ Content images x3
- Brand story image
- Product comparison image
- Usage tutorial image

5. Social media assets
- Instagram square image prompt
- TikTok vertical image prompt

Each prompt should include positive descriptions and negative exclusion terms.
```

**Tips**: After generation, use rembg (Python) to remove backgrounds, then use Pillow to composite onto white. See [B9 AI Image Pipeline](../paths/b-developers/b9-ai-image-pipeline.md) for details.

---

## 2. Competitor Price Monitoring & Dynamic Pricing (A8)

> Detailed methodology: [A8 Pricing Strategy](../paths/a-operators/a8-pricing-strategy.md)

```
You are an e-commerce pricing strategy expert.

My product: [Name]
Current price: $[X]
Cost (including FBA): $[X]
Current profit margin: [X]%

Competitor pricing data (past 30 days):
- Competitor A: $[X] → $[X] (change [X]%)
- Competitor B: $[X] (stable)
- Competitor C: $[X] → $[X] (change [X]%)

Please analyze:
1. Possible reasons for competitor price changes
2. Should I adjust my price or hold steady?
3. If adjusting, what is the optimal price point? (considering profit margin and sales elasticity)
4. Pricing strategy for major promotions (Prime Day/BFCM)
5. Long-term pricing roadmap (3-6 months)
```

---

## 3. GEO Audit & AI Search Optimization (A9)

> Detailed methodology: [A9 SEO/GEO](../paths/a-operators/a9-seo-geo.md)

```
You are a GEO (Generative Engine Optimization) expert.

My brand: [Name]
Product: [X]
Website: [URL] (if Shopify)
Amazon ASIN: [X]

Please conduct a GEO audit:

1. Structured data check
- Is Product Schema complete?
- Does FAQ Schema exist?
- Does Review Schema exist?

2. AI search visibility test
- Search "best [category] 2026" in ChatGPT is my brand mentioned?
- Search in Perplexity is it recommended?
- Are competitors [A/B/C] recommended more often?

3. Optimization recommendations
- Schema to add/fix
- FAQ content to create (10 questions)
- Third-party citations/reviews to obtain
- Agentic Commerce readiness assessment

4. Priority action list (1 week / 1 month / 3 months)
```

---

## 4. Brand Story & Visual System Generation (A10)

> Detailed methodology: [A10 Brand Building](../paths/a-operators/a10-brand-building.md)

```
You are a brand strategy expert specializing in creating brand systems for cross-border e-commerce brands.

Brand information:
- Brand name: [Name]
- Category: [X]
- Target market: [US/EU/JP]
- Target customer: [Age / Gender / Lifestyle]
- Differentiation from competitors: [Your unique qualities]
- Founder background: [Brief description]

Please generate a complete brand system in one go:

1. Brand story (200-300 words, suitable for Amazon Brand Store / Shopify About page)
2. Brand mission (1 sentence, ≤30 words)
3. Brand tagline (3 options, each ≤8 words)
4. Brand values (3-5)
5. Brand voice guidelines (tone standards for each platform)
- Amazon Listing tone
- Shopify product page tone
- Instagram tone
- TikTok tone
6. Color palette recommendations (primary + secondary + accent colors, with hex codes)
7. Amazon A+ Content brand story module copy
```

---

## 5. SKU True Profit Calculation (A11)

> Detailed methodology: [A11 Financial Analysis](../paths/a-operators/a11-financial-analysis.md)

```
You are a cross-border e-commerce financial analysis expert.

Product data (past 30 days):
- Product: [Name]
- Selling price: $[X], Monthly sales: [X] units
- Purchase cost (FOB): $[X]/unit
- International shipping: $[X]/unit
- Customs duty: [X]%
- Amazon referral fee: [X]%
- FBA fulfillment fee: $[X]/unit
- FBA monthly storage fee: $[X]/unit
- Advertising spend: $[X]/month
- Return rate: [X]%
- Tool subscriptions: $[X]/month

Please calculate:
1. True profit per unit (deducting all costs, including hidden costs)
2. Per-unit profit margin
3. Monthly total profit
4. Break-even point (units needed to cover fixed costs)
5. Cost structure breakdown (which item has the highest share)
6. 3 specific suggestions to reduce costs
7. Profit sensitivity analysis at ±10% price change
```

---

## 6. Comprehensive IP Risk Assessment (A12)

> Detailed methodology: [A12 Intellectual Property](../paths/a-operators/a12-ip-protection.md)

```
You are an intellectual property risk assessment expert.

Product I plan to sell:
- Category: [X]
- Core features: [List 3-5]
- Appearance characteristics: [Description]
- Target market: [US/EU/JP]

Please conduct a comprehensive IP risk assessment:

1. Patent risk (High / Medium / Low)
- Common patent types in this category
- Key patent databases to search
- High-risk features/design elements

2. Trademark risk (High / Medium / Low)
- Whether the brand name may conflict with existing trademarks
- Recommended trademark search steps

3. Copyright risk (High / Medium / Low)
- Copyright considerations for product images/copy
- Copyright policies for AI-generated content

4. TRO risk (High / Medium / Low)
- Whether this category has frequent TRO cases
- Preventive measures

5. Overall risk rating and recommendations
- Go / Caution / No-Go decision
- If Go: compliance steps to complete first
```

---

## 7. AI Growth Hack Product Validation (A13)

> Detailed methodology: [A13 AI Growth Hack](../paths/a-operators/a13-ai-growth-hack.md)

```
You are a cross-border e-commerce product selection expert with deep expertise in AI data analysis.

My conditions:
- Starting capital: $[X]
- Target market: [US/EU/JP]
- Supply chain: [China factory / 1688 / Trading company]
- Operations experience: [Beginner / 1-2 years / 3+ years]

Please use the AI Growth Hack framework to help me select products:

1. Recommend 5 categories (noting market size / competition level / profit margin / entry barrier)
2. Review pain point analysis for each category (what users complain about most = differentiation opportunity)
3. Final recommendation of 1 category + complete reasoning
4. Differentiation strategy
5. Estimated first order quantity and startup costs
6. 6-month ROI projection
7. AI-accelerated timeline from product selection to listing launch
```

---

## 8. Daily AI Operations Brief (A13)

> Detailed methodology: [A13 AI Growth Hack](../paths/a-operators/a13-ai-growth-hack.md#7-ai-agent-工作流实战)

```
You are my e-commerce operations AI assistant. Please generate today's operations brief based on the following data.

Yesterday's data:
- Total revenue: $[X] (vs. day before $[X])
- Total orders: [X] units
- Ad spend: $[X], Ad sales: $[X]
- ACOS: [X]%
- Returns: [X] units
- New negative reviews: [X]

Please generate:
1. Key metrics summary (revenue / orders / ACOS day-over-day and week-over-week)
2. Anomaly alerts (which metrics deviate from normal range)
3. Today's priority action list (ranked by P0 / P1 / P2)
4. One optimization suggestion (based on data trends)

Keep it concise designed to be read in under 5 minutes.
```

---

> [Hub Home](../README.md) · [Prompt Template Library](README.md) · [Path A Operations](../paths/a-operators/)
