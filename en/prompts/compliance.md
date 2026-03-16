# Compliance & Inventory Management Prompt Templates

> Last updated: 2026-03-10 | Templates: 2 | Status: ✅ Verified

---

## Template 1: Multi-Market Compliance Comparison

**Scenario**: Quickly look up compliance requirements across different countries/categories and generate a compliance checklist
**Recommended tools**: ChatGPT / Claude / Gemini
**Status**: ✅ Verified
**Contributor**: [@kangise](https://github.com/kangise)

### Prompt

```
I want to sell [product type] on Amazon [US/DE/JP].

Please generate a compliance requirements comparison table:
1. Required product certifications for each market
2. Special packaging and labeling requirements
3. Additional requirements for special categories (e.g., batteries, children's products, food-contact items)
4. Estimated certification cost ranges and timelines
5. Common compliance pitfalls

Note: Regulations may have been updated. Please indicate information currency and recommend confirming with certification agencies.
```

### Expected Output

> AI will output a multi-market compliance comparison table listing required certifications, packaging/labeling requirements, special category requirements, cost estimates, and common pitfalls by market, with a reminder about information currency.

### Tips

- Specify the exact product type (e.g., "lithium battery power bank" rather than "electronics") for more precise results
- Follow up with "If I already have FCC certification, what else do I need to enter the German market?"

---

📎 **Share this template**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/en/prompts/compliance.md#template-1-multi-market-compliance-comparison`
🏠 **Source**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) — AI × Cross-Border E-Commerce Knowledge Hub

---

## Template 2: Restocking Decision Analysis

**Scenario**: Calculate optimal restocking timing and purchase quantity based on historical sales data
**Recommended tools**: ChatGPT / Claude
**Status**: ✅ Verified
**Contributor**: [@kangise](https://github.com/kangise)

### Prompt

```
My product data:
- Average daily sales over the past 90 days: [X] units (fluctuation range [min]-[max])
- Current FBA inventory: [X] units
- In-transit inventory: [X] units
- Lead time from order to warehouse receipt: [X] days
- Target safety stock days: [X] days

Please calculate:
1. How many days current inventory can sustain
2. Latest date to place a purchase order
3. Recommended purchase quantity (optimistic / baseline / pessimistic scenarios)
4. Additional stock needed for major promotions (e.g., Prime Day)
5. Capital tied up estimate
```

### Expected Output

> AI will output inventory sustainability days, latest order date, purchase quantity recommendations for three scenarios, additional promotional stock needs, and capital tied up estimates, helping you make data-driven restocking decisions.

### Tips

- Provide realistic sales fluctuation ranges for more reasonable safety stock recommendations
- Follow up with "If lead time extends to [X] days, how should the plan adjust?" for contingency planning

---

📎 **Share this template**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/en/prompts/compliance.md#template-2-restocking-decision-analysis`
🏠 **Source**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) — AI × Cross-Border E-Commerce Knowledge Hub
