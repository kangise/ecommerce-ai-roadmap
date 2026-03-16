# Multi-Platform Operations Prompt Templates

> Source: [Path D Multi-Platform](../paths/d-platforms/)

---

## 1. Amazon → Walmart Listing Conversion

> Source: [D4 Walmart](../paths/d-platforms/d4-walmart-ai-guide.md)

```
You are a Walmart Marketplace Listing optimization expert.

Here is my Amazon Listing:
- Title: [Amazon title]
- Bullet Points: [5 points]
- Description: [Description]
- Price: $[X]

Please convert to Walmart format:
1. Walmart title (50-75 characters, Title Case, Brand + Product + Core Attributes)
2. Key Features (3-10 items, each ≤80 characters)
3. Description (300-500 words, structured, supports HTML)
4. Required product attribute checklist
5. Listing Quality Score optimization tips
6. Pricing recommendations (Walmart shoppers are more price-sensitive)
```

---

## 2. Walmart Connect Search Term Report Analysis

> Source: [D4 Walmart](../paths/d-platforms/d4-walmart-ai-guide.md)

```
You are a Walmart Connect advertising optimization expert.

Here is my Walmart search term report data (past 14 days):
Campaign: [Name]
Total spend: $[X], Total clicks: [X], Total orders: [X], ROAS: [X]

Search term data (Top 20 by spend):
| Search Term | Impressions | Clicks | Spend | Orders | Sales | ROAS |
[Paste data]

Please analyze (note Walmart's first-price auction specifics):
1. High ROAS terms (>4x): How much should I increase bids?
2. Low ROAS terms (<2x): Lower bids or negate?
3. High-impression low-click terms: Bid issue or Listing issue?
4. Zero-conversion high-spend terms: Candidates for immediate negation
5. Newly discovered long-tail opportunity terms
6. Budget reallocation recommendations
```

---

## 3. Temu Entry Decision Assessment

> Source: [D5 Temu](../paths/d-platforms/d5-temu-seller-guide.md)

```
You are a cross-border e-commerce multi-platform strategy expert.

My product details:
- Category: [X]
- Factory cost (FOB): $[X]
- Amazon selling price: $[X]
- Amazon monthly sales: [X] units
- Amazon profit margin: [X]%
- Brand positioning: [Premium / Mid-range / Value]
- Overseas warehouse: [Yes / No]

Please conduct a comprehensive Temu entry assessment:
1. Category fit score (1-10) with reasoning
2. Full-service vs. semi-service model recommendation
3. Estimated profit margin (calculated for both models)
4. Impact analysis on existing Amazon business
5. Risk assessment (IP / price wars / policy changes)
6. Final recommendation: Enter / Don't enter / Wait and see
```

---

## 4. Southeast Asia Multi-Language Listing Localization

> Source: [D6 Southeast Asia](../paths/d-platforms/d6-southeast-asia-ai-guide.md)

```
You are a Southeast Asian e-commerce localization expert.

Here is my English product Listing:
- Title: [English title]
- Description: [English description]
- Selling points: [5 points]
- Price: $[X]

Please translate and localize into:
1. Indonesian (Bahasa Indonesia)
2. Thai
3. Vietnamese

For each version provide: Product title, Description (300-500 words), 5 selling points, 10 search keywords.
Note: This is not direct translation — it's localization. Include currency conversion, cultural adaptation, and local search habits.
```

---

## 5. Multi-Platform Category Opportunity Analysis

> Source: [Platform Overview Comparison](../paths/d-platforms/platform-comparison.md)

```
You are a cross-border e-commerce multi-platform strategy expert.

My situation:
- Current platform: Amazon [US/EU/JP]
- Category: [X]
- Monthly sales: [X] units
- Monthly revenue: $[X]
- Brand registered: [Yes / No]
- Overseas warehouse: [Yes / No]
- Team size: [X] people
- Monthly budget (available for new platforms): $[X]

Please recommend the top 3 platforms I should prioritize entering, with the following for each:
1. Recommendation rationale
2. Estimated investment (time + capital)
3. Estimated return (3 / 6 / 12 months)
4. Key risks
5. First action step
```

---

🏠 [Back to Hub Home](../README.md) · 📋 [Prompt Template Library](README.md)
