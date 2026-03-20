# Advertising Optimization Prompt Templates

> Last updated: 2026-03-10 | Templates: 2 | Status: Verified

---

## Template 1: Search Term Report Analysis

**Scenario**: Analyze Amazon PPC search term reports to identify waste and optimization opportunities
**Recommended tools**: ChatGPT / Claude
**Status**: Verified
**Contributor**: [@kangise](https://github.com/kangise)

### Prompt

```
You are an Amazon PPC advertising optimization expert.

Here is my search term report data (past 30 days):
[Paste: Search term, Impressions, Clicks, Spend, Orders, Sales]

Please analyze and output:
1. Top 10 high-converting keywords (sorted by ROAS) recommend increasing bids
2. Top 10 high-spend low-converting keywords recommend lowering bids or negating
3. High-impression low-click keywords (CTR < 0.3%) analyze possible causes
4. Suggested negative keyword list (exact match vs. phrase match)
5. Budget reallocation recommendations

Present in tables, noting the recommended action and priority for each keyword.
```

### Expected Output

> AI will output categorized keyword analysis tables including high-converting terms, wasteful terms, and low-CTR terms with specific action recommendations, plus a negative keyword list and budget allocation plan.

### Tips

- Export CSV data directly from the ad console and paste it keeping column headers improves results
- Follow up with "If my budget is only $X/day, how should I allocate it?" for more specific recommendations

---

**Share this template**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/en/prompts/advertising.md#template-1-search-term-report-analysis`
**Source**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × Cross-Border E-Commerce Knowledge Hub

---

## Template 2: Ad Copy A/B Testing

**Scenario**: Generate multiple headline variations in different styles for Sponsored Brands ads
**Recommended tools**: ChatGPT / Claude / Gemini
**Status**: Verified
**Contributor**: [@kangise](https://github.com/kangise)

### Prompt

```
My product is [product description], and the core selling point is [selling point].

Please generate 5 different styles of Headlines for Sponsored Brands ads (each no more than 50 characters):
1. Feature-oriented
2. Scenario-oriented
3. Emotion-oriented
4. Data-oriented (e.g., "24-Hour Battery Life")
5. Problem-solving (e.g., "Say Goodbye to XX Hassles")

For each Headline, note the expected effect and suitable audience.
```

### Expected Output

> AI will output 5 different styles of ad Headlines, each with expected effect descriptions and target audience analysis, ready for direct use in A/B testing.

### Tips

- Provide competitor ad copy as reference so AI can help you differentiate
- After generation, follow up with "Which Headline is best suited for [specific audience]?" to narrow down further

---

**Share this template**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/en/prompts/advertising.md#template-2-ad-copy-ab-testing`
**Source**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × Cross-Border E-Commerce Knowledge Hub
