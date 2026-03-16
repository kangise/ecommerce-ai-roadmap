# Inventory Management Prompt Templates

> Related module: [A5 Inventory Management](../paths/a-operators/a5-inventory.md)

---

## 1. Safety Stock Calculation

```
You are a cross-border e-commerce inventory management expert. Please help me calculate the safety stock level for the following product.

Product information:
- ASIN: [ASIN]
- Average daily sales: [X] units (past 30-day average)
- Sales volatility: daily standard deviation [X] units
- Supplier lead time: [X] days (from order to warehouse receipt)
- Lead time variability: ±[X] days
- Target service level: [95%/99%]

Please output:
1. Safety stock quantity (units) with calculation process
2. Reorder point (ROP)
3. Suggested order quantity (EOQ estimate)
4. Estimated stockout risk assessment
```

## 2. Restocking Decision Analysis

```
You are an Amazon FBA inventory planner. Please provide restocking recommendations based on the following data.

Current inventory status:
- FBA available inventory: [X] units
- FBA in-transit inventory: [X] units (estimated arrival in [X] days)
- Overseas warehouse inventory: [X] units
- Factory in production: [X] units (estimated completion in [X] days)

Sales trends:
- Past 7-day daily average: [X] units
- Past 30-day daily average: [X] units
- Upcoming major promotion: [Yes/No, date]
- Seasonal factors: [Off-season / Peak season / Stable]

Please output:
1. Current inventory days of supply
2. Whether immediate restocking is needed (Yes/No + reasoning)
3. Recommended restocking quantity and timeline
4. Promotional stocking recommendations (if applicable)
5. Risk alerts (stockout / overstock / storage fees)
```

## 3. Slow-Moving Inventory Disposal

```
You are an inventory optimization consultant. The following product is experiencing slow sales. Please provide a disposal plan.

Slow-moving product information:
- ASIN: [ASIN]
- Current inventory: [X] units
- Past 30-day sales: [X] units
- Inventory age distribution: 0-90 days [X] units / 91-180 days [X] units / 181-270 days [X] units / 271-365 days [X] units
- Product cost: $[X]/unit
- Current selling price: $[X]
- Monthly storage fee: $[X]

Please output:
1. Slow-moving severity assessment (Mild / Moderate / Severe)
2. Disposal options ranked by priority:
   - Price reduction promotion (suggested price and expected clearance timeline)
   - Outlet / Warehouse Deals
   - Transfer to overseas warehouse
   - Disposal (cost-benefit comparison)
3. Cost-benefit analysis for each option
4. Recommended option and execution timeline
```

---

⬅️ [Back to Prompt Template Library](README.md) | 📦 [A5 Inventory Management Module](../paths/a-operators/a5-inventory.md)
