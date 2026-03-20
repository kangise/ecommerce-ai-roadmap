# Customer Service & After-Sales Prompt Templates

> Last updated: 2026-03-10 | Templates: 2 | Status: Verified

---

## Template 1: Negative Review Batch Analysis

**Scenario**: Batch analyze product negative reviews, categorize issues, and develop improvement plans
**Recommended tools**: ChatGPT / Claude
**Status**: Verified
**Contributor**: [@kangise](https://github.com/kangise)

### Prompt

```
You are an e-commerce product quality analyst. Below are all 1-3 star reviews for my product from the past 60 days.

Please complete:
1. Categorize by issue type (Quality / Functionality / Shipping / Difficulty of Use / Unmet Expectations / Other)
2. Frequency and percentage for each type (in a table)
3. The 3 most representative review quotes for each type
4. For each issue:
- Short-term response (Listing adjustments, customer service scripts)
- Long-term improvement (product improvements, supplier communication points)
5. Priority ranking: Which issue to address first (considering frequency × severity)

[Paste negative reviews here]
```

### Expected Output

> AI will output a structured negative review analysis report including an issue categorization table (with frequency and percentages), representative reviews, short-term and long-term response plans, and a prioritized action plan.

### Tips

- Just paste the raw review text AI will automatically categorize and tally
- Follow up with "For the #1 ranked issue, help me draft an improvement request email to the supplier"

---

**Share this template**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/en/prompts/customer-service.md#template-1-negative-review-batch-analysis`
**Source**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × Cross-Border E-Commerce Knowledge Hub

---

## Template 2: Account Appeal (Plan of Action)

**Scenario**: Write a professional Plan of Action appeal letter when your account is suspended
**Recommended tools**: ChatGPT / Claude
**Status**: Verified
**Contributor**: [@kangise](https://github.com/kangise)

### Prompt

```
You are an Amazon account appeal expert. My account was suspended for the following reason:
[Paste violation notice]

Please write a Plan of Action that includes:
1. Root Cause acknowledge the issue, no deflecting
2. Immediate Actions specific emergency measures already taken (be specific)
3. Preventive Measures long-term measures to prevent recurrence (must be actionable)

Requirements: Tone should be sincere and professional, each section with numbered action items, no vague statements.
```

### Expected Output

> AI will output a clearly structured Plan of Action with root cause analysis, immediate actions taken, and preventive measures each section with specific numbered action items in a sincere, professional tone.

### Tips

- Paste the complete violation notice email, including the specific violation type and ASIN
- Follow up with "Translate this letter to English while maintaining a professional tone"

---

**Share this template**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/en/prompts/customer-service.md#template-2-account-appeal-plan-of-action`
**Source**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × Cross-Border E-Commerce Knowledge Hub
