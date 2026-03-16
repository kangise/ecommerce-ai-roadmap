# Product Research & Market Analysis Prompt Templates

> Last updated: 2026-03-10 | Templates: 3 | Status: ✅ Verified

---

## Template 1: Competitor Review Pain Point Analysis

**Scenario**: Analyze competitor negative reviews to extract product improvement directions and differentiation opportunities
**Recommended tools**: ChatGPT / Claude
**Status**: ✅ Verified
**Contributor**: [@kangise](https://github.com/kangise)

### Prompt

```
You are a senior Amazon product manager. I will provide you with a set of 1-3 star reviews from competitors.
Please analyze these reviews and output:
1. Top 5 user pain points (ranked by mention frequency)
2. Specific description and representative review quotes for each pain point
3. Product improvement suggestions for each pain point
4. Which of these pain points are easiest to solve through product design

Output format: Present in a table with columns: Pain Point | Frequency | Representative Review | Improvement Suggestion | Difficulty

[Paste negative reviews here]
```

### Expected Output

> AI will output a structured table ranking 5 core pain points by frequency, each with original review quotes and actionable improvement suggestions, helping you quickly identify product optimization directions.

### Tips

- Pasting 50-100 negative reviews at once works best; too few means insufficient sample size
- Follow up with "Which pain point has the lowest improvement cost and highest impact?" to narrow your focus

---

📎 **Share this template**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/en/prompts/product-research.md#template-1-competitor-review-pain-point-analysis`
🏠 **Source**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) — AI × Cross-Border E-Commerce Knowledge Hub

---

## Template 2: Market Feasibility Assessment

**Scenario**: Quickly assess whether a product is worth entering a specific market
**Recommended tools**: ChatGPT / Claude / Gemini
**Status**: ✅ Verified
**Contributor**: [@kangise](https://github.com/kangise)

### Prompt

```
You are a cross-border e-commerce product selection expert. Please conduct a market feasibility assessment for the following product:

Product: [Product name]
Target market: Amazon [US/DE/JP]

Please analyze from the following dimensions, scoring each 1-5:
1. Market demand (search volume trends, category growth)
2. Competition intensity (top seller concentration, difficulty for new entrants)
3. Profit margin (typical selling price, estimated cost structure)
4. Supply chain difficulty (supplier availability, quality control requirements)
5. Compliance risk (certification requirements, patent risks)

Finally, provide an overall recommendation: Enter / Proceed with Caution / Pass, with reasoning.
```

### Expected Output

> AI will output a 5-dimension scoring table (1-5 per item) with analysis rationale for each dimension, concluding with an "Enter / Proceed with Caution / Pass" recommendation and reasoning.

### Tips

- The more specific the product information you provide (price range, target audience), the more accurate the assessment
- You can assess multiple products simultaneously for comparison — follow up with "Which of these three products should I prioritize?"

---

📎 **Share this template**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/en/prompts/product-research.md#template-2-market-feasibility-assessment`
🏠 **Source**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) — AI × Cross-Border E-Commerce Knowledge Hub

---

## Template 3: Keyword Demand Clustering

**Scenario**: Group a large set of search keywords by actual purchase intent to discover product opportunities
**Recommended tools**: ChatGPT / Claude
**Status**: ✅ Verified
**Contributor**: [@kangise](https://github.com/kangise)

### Prompt

```
Below is a list of search keywords for an Amazon category (from Helium 10 or Jungle Scout).
Please cluster these keywords by the user's actual purchase intent.

For each cluster:
1. Provide a cluster name (representing the user need)
2. List the included keywords
3. Estimate demand strength (High / Medium / Low)
4. Suggest corresponding product features

[Paste keyword list here]
```

### Expected Output

> AI will group keywords into 4-8 demand clusters, each with a clear name, keyword list, demand strength assessment, and corresponding product feature suggestions, helping you discover real market needs from keyword data.

### Tips

- 30-200 keywords works best
- Follow up with "Which cluster has the least competition but highest demand?" to find blue ocean opportunities

---

📎 **Share this template**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/en/prompts/product-research.md#template-3-keyword-demand-clustering`
🏠 **Source**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) — AI × Cross-Border E-Commerce Knowledge Hub
