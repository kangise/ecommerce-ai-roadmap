# Listing & Content Creation Prompt Templates

> Last updated: 2026-03-10 | Templates: 3 | Status: Verified

---

## Template 1: Full Listing Generation

**Scenario**: Generate a complete Amazon Listing from scratch (title, bullet points, description, Search Terms)
**Recommended tools**: ChatGPT / Claude
**Status**: Verified
**Contributor**: [@kangise](https://github.com/kangise)

### Prompt

```
You are an Amazon Listing optimization expert with deep knowledge of [target market] search behavior.

Product information:
- Product name: [Name]
- Core selling points: [Selling point 1], [Selling point 2], [Selling point 3]
- Target customer: [Customer profile]
- Core keywords: [Keyword list]

Please generate:
1. Title (max 200 characters, first 80 characters include the most important keywords)
2. 5 Bullet Points (each starting with a capitalized selling point, incorporating keywords, highlighting differentiation)
3. Product description (under 200 words, telling the brand story and use scenarios)
4. Backend Search Terms (5 lines, each under 250 bytes, no repetition of words already in the title)

Requirements:
- Keywords naturally integrated, no keyword stuffing
- Language matches [target market] consumer search and reading habits
- Highlight differentiation from competitors
```

### Expected Output

> AI will output a complete Listing copy set including title, 5 Bullet Points, product description, and 5 lines of Search Terms, with keywords naturally integrated and matching the target market's language habits.

### Tips

- Provide competitor ASINs or Listing links so AI can reference them for differentiation
- After generation, follow up with "Check my keyword coverage" to optimize further

---

**Share this template**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/en/prompts/listing-optimization.md#template-1-full-listing-generation`
**Source**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × Cross-Border E-Commerce Knowledge Hub

---

## Template 2: Multi-Language Localization

**Scenario**: Localize an English Listing for other languages not direct translation, but market adaptation
**Recommended tools**: ChatGPT / Claude / DeepL
**Status**: Verified
**Contributor**: [@kangise](https://github.com/kangise)

### Prompt

```
You are an Amazon Listing localization expert fluent in [target language].

Here is the English Listing:
[Paste English Listing]

Please translate to [target language]. Note:
1. This is not word-for-word translation it should match [target market] consumer search habits and expressions
2. Replace with locally popular search keywords
3. Reorder selling points, putting what [target market] consumers care about most first
4. Note what localization adjustments you made and why
```

### Expected Output

> AI will output the localized Listing copy and note all localization adjustments at the end (such as keyword replacements, selling point reordering), helping you understand the reasoning behind each change.

### Tips

- Specify a specific market (e.g., "Germany" rather than "Europe") for better localization results
- Follow up with "What do German consumers care about most in products?" to optimize further

---

**Share this template**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/en/prompts/listing-optimization.md#template-2-multi-language-localization`
**Source**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × Cross-Border E-Commerce Knowledge Hub

---

## Template 3: Competitor Listing Strategy Breakdown

**Scenario**: Compare and analyze multiple competitor Listings to find differentiation positioning opportunities
**Recommended tools**: ChatGPT / Claude
**Status**: Verified
**Contributor**: [@kangise](https://github.com/kangise)

### Prompt

```
Analyze the following 3 competitors' Amazon Listings and compare their strategy differences:

[Competitor A title and bullet points]
[Competitor B title and bullet points]
[Competitor C title and bullet points]

Please output:
1. Each competitor's core positioning (summarized in one sentence)
2. Selling points they all emphasize (category "must-haves")
3. Unique selling points for each (differentiation opportunities)
4. Keyword coverage comparison table
5. How my Listing should differentiate its positioning
```

### Expected Output

> AI will output a competitor strategy comparison analysis including positioning summaries, common selling points, differentiation opportunities, keyword comparison table, and differentiation positioning recommendations for your product.

### Tips

- Paste complete titles and bullet point descriptions the more information, the more accurate the analysis
- Follow up with "If my product has an advantage in [specific area], how should I highlight it?"

---

**Share this template**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/en/prompts/listing-optimization.md#template-3-competitor-listing-strategy-breakdown`
**Source**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × Cross-Border E-Commerce Knowledge Hub
