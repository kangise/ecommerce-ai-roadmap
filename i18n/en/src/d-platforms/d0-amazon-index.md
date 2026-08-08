# D0. Amazon Operations Index

> **Path**: Path D: Multi-Platform · **Module**: D0
> **Last updated**: 2026-08-08

---

## Why there is no Amazon chapter

Amazon appears over 1,600 times in this book—more than twice as often as the next platform (Shopify). But you won't find `d0-amazon-ai-guide.md`: that is because **Path A Operations IS the Amazon path.**

All 14 a-operators chapters (a1 Product Research → a14 Agentization) are built with Amazon as the default setting. Listing optimization, PPC advertising, inventory management, compliance — every module uses Amazon examples, constraints and prompts as its baseline. This is deliberate: for a one-person company the core operating theatre is Amazon. Abstracting operations methodology into a platform-agnostic layer would water down its executional density.

> **This page is a signpost, not a body chapter.** Duplicating Amazon content from a-operators here would create two competing sources of truth — exactly the kind of rot this book's CI gates are designed to prevent. When you need Amazon-specific knowledge, go directly to the relevant a-operators chapter.

---

## Amazon operations quick reference

| Chapter | What it covers | Amazon relevance |
|---------|---------------|:--:|
| [A1 Product Research](../a-operators/a1-product-research.md) | Sourcing methodology, data sources, AI-assisted screening | High |
| [A2 Listing Optimization](../a-operators/a2-listing-optimization.md) | Titles, bullets, descriptions, Search Terms, image copy | Home turf |
| [A3 Advertising](../a-operators/a3-advertising.md) | PPC strategy, bid optimization, ACOS diagnostics | Home turf |
| [A4 Customer Service](../a-operators/a4-customer-service.md) | Review responses, buyer messages, dispute handling | High |
| [A5 Inventory](../a-operators/a5-inventory.md) | FBA inventory forecasting, replenishment decisions | High |
| [A6 Compliance](../a-operators/a6-compliance.md) | Category approval, IP risk, FDA/FCC | High |
| [A7 Images](../a-operators/a7-visual-content.md) | Main images, A+ Content, brand story | High |
| [A8 Pricing](../a-operators/a8-pricing-strategy.md) | Buy Box pricing, dynamic repricing | Medium |
| [A9 SEO/GEO](../a-operators/a9-seo-geo.md) | Amazon search ranking, AI-engine optimization | High |
| [A10 Brand](../a-operators/a10-brand-building.md) | Brand Registry, Brand Analytics, brand story | Medium |
| [A11 Finance](../a-operators/a11-financial-analysis.md) | Profit calculation, FBA fees, return costs | Medium |
| [A12 IP Protection](../a-operators/a12-ip-protection.md) | Trademarks, patents, hijacker monitoring | High |
| [A13 Growth](../a-operators/a13-ai-growth-hack.md) | Market expansion, category diversification | Low |
| [A14 Agentization](../a-operators/a14-operations-agent.md) | Agent model for Amazon operations | High |

## Amazon-specific constraints at a glance

These constraints are extracted from a-operators during Phase A. The full set lives in `ontology/constraints.yaml`.

| Constraint | Value | Source |
|------------|-------|--------|
| Title max length | 200 characters | a2 §3.1 |
| First 80 chars must include highest-volume keyword | Required | a2 §3.1 |
| Bullet Point max length | 200 characters each | a2 §3.1 |
| Search Terms per line | ≤250 bytes, 5 lines | a2 §3.1 |
| Main image requirements | Pure white background, ≥85% fill, shortest side ≥1600px | a7 |

## How Amazon differs from other platforms

Amazon is the most "search-driven" platform: traffic comes from on-site search, and listing quality directly determines impressions and conversion. This is fundamentally different from Shopify (off-site acquisition) and TikTok Shop (algorithmic feed discovery).

| Dimension | Amazon | Compare to |
|-----------|--------|-------------|
| Traffic source | On-site search | Shopify: off-site acquisition |
| Listing structure | Title + bullets + description + Search Terms | Shopify: product page SEO |
| Ad types | PPC Sponsored Products/Brands/Display | Shopify: Google/Facebook/Instagram |
| Fulfillment | FBA or FBM | Shopify: self-fulfill or 3PL |
| Where AI matters most | Listing SEO + PPC optimization | Shopify: ads + email |

Detailed comparison → [Platform Comparison](platform-comparison.md)

---

## When this doesn't work

Amazon operations AI methodology breaks down in these scenarios:

- **Heavily gated categories**: Medical devices, food-contact materials require domain expertise beyond AI copywriting
- **Supplier Central / Vendor Central**: B2B supply rules differ completely from Seller Central
- **FBM (Fulfilled by Merchant)**: More logistics variables, AI inventory forecasting precision drops vs FBA
- **New marketplace cold start**: Japan, Australia — AI translation ≠ localization, cultural adaptation needs human judgment
