# A5. Inventory & Supply Chain

> **Track**: Path A: Operators · **Module**: A5
> **Last updated**: 2026-03-12
> **Level**: Advanced
> **Time**: 30 minutes a day, 1–2 weeks
---


```mermaid
flowchart LR
A1["A1 Product Research"]
A1 --> A2
A2["A2 Listing Creation"]
A2 --> A3
A3["A3 Advertising"]
A3 --> A4
A4["A4 Customer Service"]
A4 --> A5
A5[" A5 Inventory & Supply Chain<br/>(you are here)"]:::current
A5 --> A6
A6["A6 Compliance"]
classDef current fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
```

---

## Chapter Navigation

1. [Inventory methodology](#1-inventory-methodology-the-basics-before-ai) · 2. [AI tool landscape](#2-ai-tool-landscape-what-to-use-for-inventory) · 3. [Prompt template library](#3-prompt-template-library-for-inventory) · 4. [Inventory workflow](#4-the-inventory-workflow) · 5. [Common traps](#5-common-inventory-traps) · 6. [Advanced techniques](#6-advanced-techniques) · 7. [Learning resources](#7-learning-resources)


## What You'll Learn

Use AI to turn inventory management from "restocking by gut feel" into "data-driven decisions." From safety-stock calculation to promo stocking, build a reusable AI-assisted inventory workflow.

After this module you'll be able to:
- Build a restock decision model with ChatGPT/Claude — compute the optimal restock time and quantity from historical sales and Lead Time
- Compute the safety-stock level with AI, balancing stockout risk and capital tie-up, avoiding the "either out of stock or overstocked" dilemma
- Build a promo-stocking strategy with AI (Prime Day / BFCM), starting systematic prep 8 weeks out
- Analyze IPI Score improvement plans with AI, avoiding storage limits and overage fees
- Assess supplier lead-time risk with AI, building supply-chain resilience
- Optimize multi-marketplace inventory allocation with AI across US/EU/JP

---

## 1. Inventory Methodology: the Basics Before AI

> **Related**: [D4 Walmart AI Guide](../d-platforms/d4-walmart-ai-guide.md) for WFS vs FBA logistics-cost comparison and inventory-allocation strategy · [D3 Cross-Platform AI Strategy](../d-platforms/cross-platform-strategy.md) for cross-platform inventory coordination.

### 1.1 The first principle of inventory management

Inventory management is fundamentally a balancing problem: **stockout cost vs overstock cost**.

```
Stockout cost = out-of-stock days × daily sales × AOV × margin + rank-recovery cost
```
- 1 day out of stock may lose only that day's sales
- 7+ days out of stock, keyword rank slides, and recovery may need 2–4 weeks of ad spend
- During the stockout, competitors grab your market share, and some customers may be lost permanently

```
Overstock cost = inventory quantity × unit storage fee × slow-moving days + long-term storage fee + capital-tie-up cost
```
- FBA monthly storage fee: standard size $0.87/cu ft (Jan–Sep), $2.40/cu ft (Oct–Dec)
- Age over 181 days starts incurring an Aged Inventory Surcharge
- Age over 365 days costs even more, severely eroding profit
- Capital tied up in inventory can't fund new-product development or advertising

> **Key insight**: for most cross-border sellers, the hidden cost of a stockout far exceeds overstocking. One stockout can drop BSR from Top 50 to Top 500, and recovery needs thousands in ad spend. But overstock cost is predictable and controllable. So your inventory strategy should lean toward "better to stock a bit more," but set a clear age-alert line.

**Safety-stock formula:**

```
Safety stock = Z × σ_d × √L

where:
Z = service-level factor (95% service level → Z = 1.65, 99% → Z = 2.33)
σ_d = standard deviation of daily sales (measures sales volatility)
L = Lead Time (days from order to warehouse-in)
```

**Reorder Point formula:**

```
Reorder Point = daily sales × Lead Time + safety stock
```

When inventory drops to the reorder point, you should place a restock order.

**The composition of Lead Time:**

| Stage | Typical time | Variability |
|-------|--------------|-------------|
| Supplier production | 15–30 days | ±7 days |
| Domestic transport to port | 3–5 days | ±2 days |
| Ocean freight (China → US West Coast) | 15–20 days | ±5 days |
| Customs + domestic transport | 5–10 days | ±3 days |
| FBA warehouse-in processing | 5–14 days | ±7 days (longer in peak season) |
| **Total** | **43–79 days** | **highly variable** |

> **Lead Time is the biggest source of uncertainty in inventory management.** FBA warehouse-in time can jump from 5 days to 21 in peak season (Q4). Your safety-stock calculation must account for Lead Time variability, not just the average.

### 1.2 Key Amazon FBA inventory metrics

| Metric | Definition | Target | Impact |
|--------|------------|--------|--------|
| **IPI Score** | Inventory Performance Index, a composite inventory-health score | ≥ 400 (avoid storage limits) | below the threshold, FBA warehouse-in quantity is capped |
| **Sell-through Rate** | past-90-day sales ÷ average inventory | > 3 (i.e., inventory turns 3× in 90 days) | the core component of IPI |
| **Excess Inventory** | inventory beyond the next 90 days of projected sales | the less the better | takes storage space, incurs extra fees |
| **Stranded Inventory** | ASINs with stock but not sellable (a Listing issue) | 0 | pure cost waste |
| **In-stock Rate** | days in stock ÷ total days | > 95% | affects BSR rank and ad performance |
| **Aged Inventory** | inventory aged over 90/180/270/365 days | minimize | incurs the Aged Inventory Surcharge |

**The composition of IPI Score (Amazon doesn't publish exact weights, but industry consensus):**

```
IPI Score ≈ f(Sell-through Rate, Excess Inventory %, Stranded Inventory %, In-stock Rate)
```

- **Sell-through Rate** has the highest weight — fast-selling inventory is good inventory
- **Excess Inventory %** — the lower the excess-inventory share, the better
- **Stranded Inventory** must be 0 — this is the easiest to fix
- **In-stock Rate** — keep a high in-stock rate, but don't over-stock

Content rephrased for compliance with licensing restrictions. Sources: [goaura.com IPI score guide](https://goaura.com/blog/improving-your-amazon-ipi-score), [goaura.com inventory management](https://goaura.com/blog/amazon-inventory-management)

### 1.3 AI's role in inventory management

What AI is good at:
- **Demand forecasting**: predict future demand from historical sales, seasonality, trends — far more accurate than "gut feel"
- **Restock calculation**: weigh Lead Time, safety stock, in-transit inventory, storage limits, and more to give an optimal restock suggestion
- **Anomaly detection**: spot sudden sales changes (spikes or crashes), pre-warning stockout or overstock risk
- **Scenario simulation**: simulate the outcomes of different stocking strategies (optimistic/base/pessimistic) to aid decisions
- **Multivariable optimization**: with limited capital, optimize inventory allocation across multiple SKUs

What AI is weak at:
- **Black-swan prediction**: pandemics, port strikes, policy changes — unpredictable events
- **Supplier-relationship management**: negotiating lead times and priority production needs human relationships
- **Quality judgment**: whether inventory has quality issues (expired, damaged) needs a physical check
- **Cash-flow decisions**: how much to stock ultimately depends on your cash position and risk appetite; AI can only advise

> **Core principle**: AI is your inventory analyst, not your inventory decision-maker. Use AI for data analysis and plan generation, humans for final decisions. Especially for large purchasing decisions (like promo stocking), AI's advice is a reference — the final call combines your cash position, supplier relationships, and risk appetite.

---

## 2. AI Tool Landscape: What to Use for Inventory

### 2.1 Paid tools reviewed

| Tool | Price | Core capability | For whom | AI features |
|------|-------|-----------------|----------|-------------|
| [SoStocked](https://www.sostocked.com/) | $49–199/mo | restock forecasting, seasonality adjustment, multi-warehouse management, purchase-order management | mid-to-large sellers (50+ SKUs) | AI demand forecasting, auto restock suggestions, seasonal-factor adjustment |
| [RestockPro](https://goaura.com/blog/restockpro) | $59–249/mo | restock suggestions, profit analysis, supplier management, FBA shipment planning | sellers serious about inventory management | AI restock algorithm, profit forecasting, age alerts |
| [Forecastly](https://www.forecastly.com/) | $49–149/mo | demand forecasting, stockout alerts, restock suggestions | sellers needing precise forecasts | ML demand forecasting, stockout-risk scoring |
| [Inventory Lab](https://www.inventorylab.com/) | $69/mo | profit tracking, inventory management, accounting integration | sellers needing profit analysis | profit forecasting, inventory-turnover analysis |
| Helium 10 Inventory Management | $79/mo (incl. in Platinum) | restock suggestions, inventory alerts, profit dashboard | Helium 10 users | AI restock suggestions, sales forecasting |

**Tool selection advice:**

**Tight budget (<$50/mo)**: ChatGPT/Claude + Excel + Amazon's official tools
- Do restock calculations and scenario analysis with ChatGPT
- Build a simple inventory-tracking sheet in Excel
- View official restock suggestions with Amazon Restock Inventory
- Good for sellers with under 20 SKUs

**Serious (\$50–150/mo)**: SoStocked or RestockPro + ChatGPT
- SoStocked/RestockPro for daily restock management and alerts
- ChatGPT for promo-stocking strategy and anomaly analysis
- Good for 20–100 SKUs

**Large sellers (\$150+/mo)**: RestockPro + SoStocked + a custom system
- Paid tools for daily management
- Custom Python scripts for tailored analysis (see Path B)
- Good for 100+ SKUs or multi-marketplace operations

Content rephrased for compliance with licensing restrictions. Sources: [goaura.com RestockPro review](https://goaura.com/blog/restockpro), [selectedfirms.co AI inventory management](https://selectedfirms.co/blog/ai-in-ecommerce-inventory-management)

### 2.2 Free tool stack

| Tool | Use | Link |
|------|-----|------|
| ChatGPT / Claude | restock calculation, safety-stock analysis, promo-stocking strategy, IPI improvement plans | [chat.openai.com](https://chat.openai.com/) / [claude.ai](https://claude.ai/) |
| Amazon Restock Inventory | official restock-suggestion tool, gives restock quantity and timing from sales trends | Seller Central → Inventory → Restock Inventory |
| Amazon FBA Revenue Calculator | compute FBA fees and margins to aid inventory decisions | [sellercentral.amazon.com/hz/fba/profitabilitycalculator](https://sellercentral.amazon.com/hz/fba/profitabilitycalculator/index) |
| Amazon Inventory Dashboard | inventory-health dashboard, IPI Score, age distribution, Stranded Inventory | Seller Central → Inventory → Inventory Dashboard |
| Google Sheets | build inventory-tracking sheets and restock-calculation models | [sheets.google.com](https://sheets.google.com/) |

**How to use the free tools:**

1. **Amazon Restock Inventory is the starting point**: it suggests restocks from your historical sales, but it doesn't account for promos, seasonality, or a new-product ramp. Use its suggestion as a baseline and adjust with AI.
2. **FBA Revenue Calculator for profit validation**: before deciding a stocking quantity, confirm per-unit profit with the Revenue Calculator. If the margin is too low, overstocking is a risk.
3. **ChatGPT for scenario analysis**: feed sales data, Lead Time, and budget to ChatGPT to simulate optimistic/base/pessimistic stocking plans.
4. **Google Sheets for ongoing tracking**: build a simple inventory-tracking sheet, update inventory, in-transit quantity, and ETA weekly, and let AI help design formulas and alert rules.

### 2.3 Open-source tools & APIs

| Tool/API | Use | GitHub/link |
|----------|-----|-------------|
| [Facebook Prophet](https://facebook.github.io/prophet/) | time-series forecasting, good for seasonal sales | [github.com/facebook/prophet](https://github.com/facebook/prophet) |
| pandas + numpy | data processing and analysis, the base tools for inventory calculation | [pandas.pydata.org](https://pandas.pydata.org/) |
| python-amazon-sp-api | SP-API Python wrapper, incl. Inventory API (inventory data) and Reports API (sales reports) | [github.com/saleweaver/python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api) |
| statsmodels | statistical modeling, incl. classic time-series models like ARIMA | [github.com/statsmodels/statsmodels](https://github.com/statsmodels/statsmodels) |
| scikit-learn | ML library, usable for demand forecasting and anomaly detection | [github.com/scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn) |

**When to use open-source tools?**

If you manage 50+ SKUs or need precise seasonal forecasts, open-source tools can:
- **Automate forecasting**: use Prophet for time-series forecasts per SKU, auto-accounting for seasonality, trend, and holiday effects
- **Batch calculation**: use pandas to compute safety stock, reorder point, and restock quantity for all SKUs at once
- **Auto alerts**: use a Python script to check inventory levels daily and auto-send stockout-alert emails

> For technical implementation, see the relevant modules in [Path B: Developers](../b-developers/).

---

## 3. Prompt Template Library (for Inventory)

> This section gives a deep breakdown of each template, common mistakes, and advanced variants.

### 3.1 Restock Decision Analysis

**Why this prompt works:** it asks the AI to weigh five key variables — daily sales, variability, current inventory, in-transit inventory, and Lead Time — and output restock suggestions for three scenarios. Key design points:
- "variability min–max" makes the AI understand sales uncertainty, not just the average
- "optimistic/base/pessimistic scenarios" forces risk analysis over a single forecast
- "capital-tie-up estimate" ties the inventory decision to the capital decision

**Common mistakes:**
- Providing only average sales → daily 10 units but a 3–25 range means totally different safety-stock needs. Provide the variability range
- Ignoring in-transit inventory → if 500 units are in transit, actual available inventory = current + in-transit
- Using average Lead Time → Lead Time variability matters more than sales variability. Use the last 3 actual Lead Times and take the max as the safe value
- Ignoring storage limits → when IPI Score is below the threshold, FBA warehouse-in quantity is capped. Restock can't exceed the limit

```
My product data:
- Past-90-day daily sales: [X] units (range [min]–[max])
- Current FBA inventory: [X] units
- In-transit inventory: [X] units (arriving in [X] days)
- Lead Time from order to warehouse-in: [X] days (last 3 actuals: [X], [X], [X] days)
- Safety-stock days target: [X] days
- Per-unit purchase cost: $[X]
- Per-unit FBA storage fee (monthly): $[X]
- Current IPI Score: [X]
- FBA storage limit: [X] units (if any)

Compute:
1. Days the current inventory can cover (incl. in-transit)
2. Safety-stock quantity (show the calculation with the formula)
3. Reorder Point
4. Suggested purchase quantity (optimistic/base/pessimistic scenarios)
5. Latest order date
6. If there's a promo (e.g., Prime Day), how much extra to stock
7. Capital-tie-up estimate (purchase cost + projected storage fee)
8. Risk note (advice on balancing stockout risk vs overstock risk)
```


**Advanced variants:**

**Variant A — multi-SKU batch restock priority:**

```
I have the following SKUs needing restock decisions, but limited capital (total budget $[X]):

SKU 1: [product name]
- Daily sales: [X] units, current inventory: [X] units, Lead Time: [X] days
- Per-unit cost: $[X], per-unit profit: $[X]

SKU 2: [product name]
- Daily sales: [X] units, current inventory: [X] units, Lead Time: [X] days
- Per-unit cost: $[X], per-unit profit: $[X]

[more SKUs...]

Please:
1. Stockout-urgency score per SKU (based on days-of-cover vs Lead Time)
2. Profit-contribution ranking per SKU
3. Optimal restock allocation under the budget limit
4. How the allocation changes if the budget increases 20%/50%
5. Which SKUs can defer restock? What's the risk of deferring?
```

> **Why use it**: with limited capital, not all SKUs can restock at once. Prioritize high-profit, high-stockout-risk SKUs; defer low-profit, well-stocked ones. AI can do this multivariable optimization.

**Variant B — first-batch stocking for a new product:**

```
I'm about to launch a new product and need to estimate the first FBA batch:

Product info:
- Category: [category]
- Price: $[X]
- Competitor daily-sales range: [X]–[X] units (from Helium 10/Jungle Scout)
- My target market share: [X]%
- Planned ad budget: $[X]/day
- Lead Time (order to warehouse-in): [X] days

Analyze:
1. Based on competitor data, estimate my daily-sales range (conservative/medium/optimistic)
2. First-batch stocking suggestion (cover [X] days of sales + safety stock)
3. Capital needed for the first batch
4. If the first batch sells faster/slower than expected, the second-batch restock strategy
5. New-product inventory risk notes (what if it doesn't sell? what if it sells too fast?)
```

> **Why use it**: a new product has no historical data, so estimate from competitor data and market analysis. The first-batch principle is "better too little than too much" — test the market with a small batch, and restock heavily only after confirming it sells.

---

### 3.2 Safety-Stock Calculation

**Why this prompt works:** safety stock isn't a gut-feel "stock 30 extra days" — it's a mathematical calculation based on sales and Lead Time variability. This prompt asks the AI to compute with formulas and explain each parameter, helping you understand "why this number."

**Common mistakes:**
- Using fixed days instead of the formula → "safety stock = 30 days of sales" is too crude. High-variability products need more; low-variability need less
- Ignoring Lead Time variability → if Lead Time goes from 45 to 60 days, safety stock must rise accordingly
- Same safety-stock standard for all SKUs → high-profit products can stock more (high stockout cost), low-profit stock less (relatively higher overstock cost)

```
Help me compute the safety stock for the following product:

Product data:
- Monthly sales over the past 180 days: [Jan X, Feb X, Mar X, Apr X, May X, Jun X]
- Standard deviation of daily sales: [X] (if unknown, compute from the monthly data)
- Lead Time data (last 5): [X days, X days, X days, X days, X days]
- Target service level: [95% / 99%] (95% means allowing a 5% stockout probability)
- Per-unit cost: $[X]
- Per-unit price: $[X]
- Monthly storage fee: $[X]/unit

Compute:
1. Daily sales and its standard deviation
2. Lead Time mean and standard deviation
3. Safety-stock quantity (with the formula Z × σ_d × √L, show the work)
4. Reorder Point (= daily sales × Lead Time + safety stock)
5. Capital-tie-up cost of the safety stock
6. If raising the service level from 95% to 99%, how much does safety stock increase? Is it worth it?
7. Advice: should this product use a 95% or 99% service level? Why?
```

---

### 3.3 Seasonal Demand Forecasting

**Why this prompt matters:** many cross-border products have clear seasonality — outdoor products sell well in summer, heating products in winter, gifts peak in Q4. Ignore seasonality and you'll run out in peak season and overstock in the off-season.

**Common mistakes:**
- Forecasting each month with the annual average → if Q4 sales are 3× Q1, using the average causes a severe Q4 stockout
- Only looking at last year's same period → this year's growth trend, market changes, and competitor landscape may differ
- Not distinguishing seasonality from trend → a sales rise could be seasonal (will fall back) or a trend (will persist); the responses differ

```
Help me analyze my product's seasonal demand and forecast the next 6 months of sales:

Historical sales (monthly):
- Last year: [Jan X, Feb X, Mar X, ..., Dec X]
- This year so far: [Jan X, Feb X, ...]

Product info:
- Category: [category]
- Main market: Amazon [US/DE/JP]
- Clear seasonality: [yes/no/unsure]
- Overall growth rate this year vs last: [X]%

Analyze:
1. Seasonal-pattern identification:
- Which months are peak? Which are off-season?
- How many times higher is peak vs off-season?
- Seasonal-factor table (each month's seasonal coefficient)

2. Next-6-months sales forecast:
- Base forecast (seasonality + growth trend)
- Optimistic (+20%)
- Pessimistic (-20%)

3. Stocking advice:
- Suggested inventory level per month
- Key restock timing (accounting for Lead Time)
- How far in advance to start stocking before peak season?

4. Risk notes:
- If seasonality is weaker/stronger than expected, how to adjust?
- What external factors could affect the seasonal pattern?
```

---

### 3.4 Promo-Stocking Strategy (Prime Day / BFCM)

**Why this prompt matters:** Prime Day and BFCM are Amazon's two biggest promos of the year. Promo-period sales can be 3–10× normal, but over-stocking turns into slow-moving inventory after. This prompt helps you build a systematic promo-stocking plan.

**Common mistakes:**
- Only looking at last year's promo data → this year's discount depth, ad budget, and competitor strategy may all differ
- Ignoring the sales change before and after the promo → sales dip 1–2 weeks before (shoppers wait for the discount) and 1–2 weeks after (demand pulled forward)
- Stocking too late → FBA warehouse-in slows 2–4 weeks before the promo; ship 6–8 weeks early
- No stop-loss line → if the promo underperforms, how do you handle the excess inventory? Plan ahead

```
Help me build a [Prime Day / BFCM] stocking strategy:

Product info:
- Product name: [name]
- Daily sales (last 30 days): [X] units
- Last year's same-promo data:
- Promo-period daily sales: [X] units ([X]× normal)
- Promo duration: [X] days
- Daily-sales change 2 weeks before the promo: [X]%
- Daily-sales change 2 weeks after the promo: [X]%
- Current FBA inventory: [X] units
- Lead Time: [X] days
- Planned discount depth: [X]% off
- Planned ad-budget increase: [X]%
- Promo date: [date]

Build:
1. Promo sales forecast:
- Based on last year's data + this year's growth + discount-depth adjustment
- Optimistic/base/pessimistic scenarios

2. Stocking-quantity calculation:
- Promo-period demand
- Buffer stock before/after the promo
- Safety stock
- Total stocking quantity

3. Timeline planning:
- Latest order date (back-calculated from Lead Time)
- Latest ship date
- FBA warehouse-in deadline
- Key checkpoints

4. Capital needs:
- Purchase cost
- First-leg logistics cost
- Projected storage fee
- Total capital need

5. Contingency plan:
- If promo sales are only 50% of expected, how to handle the excess?
- If promo sales exceed 150% of expected, how to emergency-restock?
- Stop-loss line: within how many days after the promo must inventory drop to what level?
```

> **The core principle of promo stocking**: better to under-stock than heavily over-stock. Post-promo slow-moving inventory racks up huge fees during the Q4 high-storage-fee period. Suggested stocking = base-scenario demand × 1.2 (a 20% buffer), not stocking to the optimistic scenario.

---

### 3.5 Multi-Marketplace Inventory Allocation

**Why this prompt matters:** if you run US, EU (DE/FR/IT/ES/UK), and JP marketplaces, inventory allocation is a complex optimization. Each marketplace's sales, storage fees, and Lead Time differ, and you must optimally allocate limited total inventory.

**Common mistakes:**
- Simple pro-rata by sales → ignores Lead Time and storage-fee differences per marketplace
- Ignoring the EU's Pan-EU vs EFN choice → Pan-EU auto-distributes across EU-country warehouses; EFN ships from one country only
- Ignoring exchange-rate and margin differences → the same product's margin can vary a lot by marketplace

```
My product sells on multiple Amazon marketplaces. Help me optimize inventory allocation:

Total available inventory: [X] units (or total purchase budget: $[X])

Per-marketplace data:
US:
- Daily sales: [X] units, Lead Time: [X] days
- Current inventory: [X] units, monthly storage fee: $[X]/unit
- Per-unit profit: $[X]

EU (DE main warehouse):
- Daily sales: [X] units, Lead Time: [X] days
- Current inventory: [X] units, monthly storage fee: €[X]/unit
- Per-unit profit: €[X]
- Logistics mode: [Pan-EU / EFN]

JP:
- Daily sales: [X] units, Lead Time: [X] days
- Current inventory: [X] units, monthly storage fee: ¥[X]/unit
- Per-unit profit: ¥[X]

Optimize:
1. Target inventory level (days) per marketplace
2. This restock's allocation plan
3. Stockout-risk assessment per marketplace
4. If total inventory can't satisfy all marketplaces, which to prioritize? Why?
5. Inventory-turnover comparison across marketplaces and improvement advice
```

---

### 3.6 Slow-Moving Inventory Handling Strategy

**Why this prompt matters:** slow-moving inventory is a hidden profit killer. Inventory aged over 180 days not only takes storage space but incurs the Aged Inventory Surcharge and drags down IPI Score. Handling it promptly is a key part of inventory management.

**Common mistakes:**
- Waiting until you get a long-term storage-fee notice → start watching at 90 days of age, act at 120
- Only thinking of markdown clearance → there's also creating a Removal Order, moving to other channels, bundle sales, and more
- Not computing the handling cost → sometimes destruction is cheaper than shipping back (return freight may exceed the product's value)

```
Here is my slow-moving inventory list:

SKU 1: [product name]
- Inventory quantity: [X] units
- Age: [X] days
- Original price: $[X], current price: $[X]
- Per-unit cost: $[X]
- Past-30-day sales: [X] units
- FBA monthly storage fee: $[X]/unit
- Projected Aged Inventory Surcharge: $[X]/unit

[more SKUs...]

Build a handling strategy per SKU:
1. Strategy-option assessment (cost and benefit of each):
- Markdown promotion (to what price? how long to clear?)
- Create a Lightning Deal or Coupon
- Create a Removal Order (ship-back vs destroy cost comparison)
- Move to another channel (eBay, own site, offline clearance)
- Bundle sales (pair with a bestseller)
- Donation (FBA Donations program)

2. Recommended strategy and execution timeline
3. Estimated recovery amount vs the cost of continued holding
4. How to avoid similar slow-movers in the future?
```

---

### 3.7 Supplier Lead-Time Risk Assessment

**Why this prompt matters:** supplier lead-time delays are one of the most common causes of stockouts. Assessing supplier lead-time risk in advance and building backups can greatly cut stockout probability.

**Common mistakes:**
- Only one supplier → single-supplier risk is extremely high; one problem means a stockout
- Not tracking historical lead-time data → no data, no risk assessment
- Ignoring seasonal factors → supplier capacity drops sharply around Chinese New Year and National Day

```
Help me assess supplier lead-time risk and build a response plan:

Supplier info:
Supplier A (primary):
- Partnership length: [X] years
- Lead-time record over the past 12 months: [X days, X days, X days, ...] (days from order to ship)
- Reason for the most recent delay: [reason]
- Capacity: [X] units/month
- Minimum order quantity (MOQ): [X] units

Supplier B (backup, if any):
- [similar info]

My needs:
- Average monthly purchase: [X] units
- Next large purchase date: [date]
- Any promo-stocking need: [yes/no]

Analyze:
1. Supplier A's lead-time reliability score (based on historical data)
2. Delay probability and expected delay days
3. If Supplier A is [X] days late, the impact on inventory
4. Backup plan:
- Do I need to develop a second supplier?
- Do I need more safety stock to buffer lead-time risk?
- Should I order early for key periods (before promos, before Chinese New Year)?
5. Supplier-management advice:
- How to communicate with the supplier to reduce delays?
- What lead-time guarantee clauses should the contract include?
```

---

### 3.8 IPI Score Improvement Plan

**Why this prompt matters:** an IPI Score below the threshold (currently 400) causes FBA storage limits, directly affecting your restock capacity. Improving IPI Score means optimizing Sell-through Rate, Excess Inventory, and Stranded Inventory simultaneously.

**Common mistakes:**
- Only watching the IPI number without analyzing causes → you need to know which dimension is dragging it down
- Raising Sell-through Rate by cutting inventory → this raises stockout risk, not worth it
- Ignoring Stranded Inventory → it's the easiest dimension to fix, but many sellers don't check it

```
My IPI Score needs improving. Help me build an improvement plan:

Current data:
- IPI Score: [X] (target: ≥ 400)
- Sell-through Rate: [X] (past-90-day sales ÷ average inventory)
- Excess Inventory: [X] ASINs, [X] units
- Stranded Inventory: [X] ASINs, [X] units
- In-stock Rate: [X]%
- Current storage limit: [X] cu ft (if any)

Excess Inventory details:
[list ASINs aged over 90 days, quantity, age]

Stranded Inventory details:
[list the stranded ASINs and reasons]

Build an improvement plan:
1. Diagnosis: what's the main reason for the low IPI Score?
2. Quick fixes (within 1 week):
- Stranded Inventory handling
- Most-urgent Excess Inventory handling
3. Mid-term improvement (1–3 months):
- Sell-through Rate improvement strategy
- Systematic Excess Inventory clearance plan
4. Long-term prevention:
- Restock-strategy adjustment (avoid over-stocking)
- Inventory-monitoring frequency and alerting mechanism
5. Estimated improvement timeline and target IPI Score
```

Content rephrased for compliance with licensing restrictions. Sources: [goaura.com IPI score improvement](https://goaura.com/blog/improving-your-amazon-ipi-score), [impakter.com FBA AI forecasting](https://impakter.com/the-2026-playbook-fba-prep-services-ai-forecasting-and-greener-3pl-operations/)

---

## 4. The Inventory Workflow

### 4.1 Monthly Restock SOP

A systematic restock flow run once a month to keep all SKUs at healthy inventory levels.

```

Step 1: data collection (30 min)
Action: export the following data
- Seller Central → Inventory → Manage Inventory (inventory)
- Business Reports → Sales (past 90 days)
- Inventory Dashboard → IPI Score and age distribution
- In-transit inventory list (purchase-order tracker)
AI: organize the data into a standard format, paste to ChatGPT

Step 2: inventory-health check (20 min)
Check: is IPI Score ≥ 400?
Check: any Stranded Inventory? → fix immediately
Check: any inventory aged > 90 days? → flag for handling
Check: any SKU about to stock out? (inventory < 14 days of sales)
AI: diagnose with the IPI improvement prompt (3.8)

Step 3: restock calculation (30 min)
AI: compute per SKU with the restock decision prompt (3.1)
Or: batch-process with the multi-SKU restock variant (3.1 Variant A)
Output: suggested restock quantity and latest order date per SKU
Review: a human checks the AI advice, adjusts for cash position

Step 4: place purchase orders (20 min)
Action: issue purchase orders to suppliers
Record: update the purchase-order tracker (supplier, quantity, ETA)
Confirm: confirm lead time and quality requirements with the supplier

Step 5: slow-moving inventory handling (20 min)
Action: handle the slow-movers flagged in Step 2
AI: build a plan with the slow-moving handling prompt (3.6)
Execute: create a promotion / Removal Order / channel transfer

```

### 4.2 Promo-Stocking SOP (8-week plan before Prime Day / BFCM)

Promo stocking is an 8-week systematic process, not something to start 2 weeks before.

```

Week 8 (8 weeks out): demand forecasting
Action: collect last year's promo data + this year's growth trend
AI: forecast promo sales with the promo-stocking prompt (3.4)
Output: stocking quantity for optimistic/base/pessimistic scenarios
Decision: set the stocking quantity (suggest base × 1.2)

Week 7: supplier communication
Action: issue the promo purchase order to the supplier
Confirm: lead-time commitment, quality standard, feasibility of a rush add-on order
AI: assess risk with the supplier lead-time prompt (3.7)
Backup: if the primary supplier lacks capacity, contact the backup

Week 6: first-leg logistics arrangement
Action: book ocean/air freight space
Note: logistics resources are tight before promos, book early
Decision: ocean vs air (see Advanced 6.3)
Track: update the logistics tracker, confirm the ETA at port

Week 5: QC and shipping
Action: factory QC → packing → shipping
Check: product quality, packaging integrity, label correctness
Ship: prepare the shipment plan per FBA requirements

Week 4: warehouse-in tracking
Action: track the shipment status
Alert: if logistics is delayed, trigger the backup (air-freight restock)
Prepare: start preparing the promo Listing optimization and ad plan

Week 3: FBA warehouse-in
Action: goods arrive at the FBA warehouse, awaiting processing
Note: warehouse-in may slow before promos, leave buffer time
Check: is the warehouse-in quantity correct? any Stranded Inventory?

Week 2: final confirmation
Check: is all inventory warehoused-in and sellable?
Check: is the promo Deal submitted and approved?
Check: are the ad budget and bids adjusted?
Prepare: CS templates for the promo period (see the A4 module)

Week 1: promo execution
Monitor: check the inventory-burn rate daily
Adjust: if burning faster than expected, consider raising the price or cutting ads
Record: log daily sales data for the next promo's reference

```

> **The core lesson of promo stocking**: most sellers' promo failures aren't "can't sell," they're "under-stocked" or "stocked too late." The 8-week prep looks long, but given supplier production + ocean freight + FBA warehouse-in time, it's just right.

### 4.3 New-Product First-Batch Stocking SOP

A new product has no historical data, so the first batch needs special care.

```

Step 1: market research (see the A1 product-research module)
Action: research competitor sales with Helium 10/Jungle Scout
Data: competitor daily-sales range, market size, seasonality
AI: estimate sales with the new-product first-batch prompt (3.1 Variant B)

Step 2: first-batch stocking decision
Principle: first batch = 30–45 days of projected sales (conservative)
Reason: new products are highly uncertain, test the market with a small batch
Calculation: projected daily sales × 45 days × 0.7 (conservative factor)
Capital: confirm purchase capital and first-leg logistics are within budget

Step 3: prep the second batch in parallel
Action: while shipping the first batch, confirm the second batch's lead time with the supplier
Trigger: if daily sales after listing hit 80% of expected, order immediately
Quantity: second batch = 60–90 days of projected sales (adjusted on actual data)

Step 4: post-listing monitoring
Frequency: check sales and inventory daily
Alert: if sales far exceed expected, emergency air-freight restock
Adjust: if sales far below expected, pause the second-batch purchase
AI: analyze the sales trend weekly with AI, adjust the restock plan

```

> **The core principle of new-product stocking**: better too little than too much for the first batch. New-product failure rates are high; if you stock 3000 but sell only 300, the remaining 2700 is pure loss. Test the market with 500–1000 units, then restock heavily once it sells.

---

## 5. Common Inventory Traps

### 5.1 Stockout-related traps

| Trap | Symptom | How to avoid |
|------|---------|--------------|
| **Overly optimistic Lead Time** | planning with the shortest-ever Lead Time, then a delay causes a stockout | use the max (not average) of the last 3–5 Lead Times for safety. Add a 7–14 day buffer in peak season. |
| **Ignoring FBA warehouse-in time** | goods at the US warehouse ≠ sellable. Processing takes 5–14 days, longer in peak | list FBA warehouse-in time separately in Lead Time, count it as 21 days in peak. |
| **Not monitoring in-transit inventory** | not knowing how much is in transit or when it arrives, causing duplicate or missed orders | build a purchase-order tracker, update the logistics status weekly. |
| **Under-stocking before a promo** | underestimating the promo sales multiple, stocking out on day 1 | use last year's promo data × 1.2 as the baseline. Better to over-stock 20% than run out. |
| **Under-stocking a new product's first batch** | a new product sells well then runs out fast, missing the best promotion window | prep the second batch while stocking the first, set a trigger to auto-order. |

### 5.2 Slow-moving-related traps

| Trap | Symptom | How to avoid |
|------|---------|--------------|
| **Over-stocking** | "stock a bit more" by gut feel, then age over 180 days incurs high storage fees | compute with the safety-stock formula, not gut feel. Set a 90-day age-alert line. |
| **Not handling slow-movers promptly** | waiting for a long-term storage-fee notice, by which point fees have piled up | check the age distribution monthly (Monthly SOP Step 2), build a handling plan at 90 days. |
| **Marking down too late** | starting markdowns at 300 days of age, after fees have accumulated | start markdown promotion at 120 days, consider a Removal Order at 180. |
| **Not clearing seasonal products** | summer products still in the warehouse in autumn, waiting for next summer | start clearing seasonal products 1 month before peak-season ends, don't wait for the off-season. |
| **Not cutting losses on a failed new product** | a new product doesn't sell after 3 months, but you keep holding | evaluate at 60 days post-listing; if daily sales < 30% of expected, start clearance. |

### 5.3 Capital-related traps

| Trap | Symptom | How to avoid |
|------|---------|--------------|
| **Too much capital tied up in inventory** | 80% of capital in inventory, no money for ads or new products | set an inventory-capital cap (suggest < 60%); over it, cut stocking. |
| **Not computing inventory holding cost** | only looking at purchase cost, ignoring storage, capital cost, slow-moving risk | total inventory cost = purchase + first-leg logistics + storage + capital-tie-up cost (8–12% annualized). |
| **Promo stocking overdraws cash flow** | heavy purchasing before the promo, but payout takes 2–4 weeks after, breaking cash flow | keep promo-stocking budget under 50% of available capital, reserve a cash buffer. |
| **Spreading capital across marketplaces** | stocking a bit in each marketplace, but not enough in any | concentrate resources in 1–2 main marketplaces, maintain others with minimal inventory. |

### 5.4 Logistics-related traps

| Trap | Symptom | How to avoid |
|------|---------|--------------|
| **Ocean freight only** | ocean is cheap but slow (30–45 days), too slow for emergency restocks | ocean for routine restocks, air for emergencies. Keep a 10–20% air-freight budget. |
| **Not booking freight space** | Q4 ocean space is tight, last-minute unavailable or doubled in price | book Q4 ocean space in Aug–Sep. |
| **Customs issues cause delays** | incomplete product documents, held by customs | prepare all customs documents in advance (invoice, packing list, compliance certificates). |
| **FBA shipment-plan errors** | wrong labels, quantity mismatch, non-compliant packaging, rejected by FBA | prepare strictly per FBA shipment requirements, do a final check before shipping. |

---

## 6. Advanced Techniques

### 6.1 AI Demand Forecasting: Prophet Intro

When your SKU count exceeds 20, forecasting each by hand with ChatGPT is unrealistic. Facebook Prophet is an open-source time-series forecasting tool, especially good for seasonal sales.

**When to use Prophet vs simple rules?**

| Scenario | Recommended method | Reason |
|----------|--------------------|--------|
| SKU < 20, no clear seasonality | ChatGPT + Excel | simple rules suffice, no complex model needed |
| SKU < 20, seasonal | ChatGPT + seasonal prompt (3.3) | AI can understand the seasonal pattern |
| SKU 20–100, seasonal | Prophet | batch forecasting is efficient, auto-handles seasonality |
| SKU 100+, multi-marketplace | Prophet + custom system | needs an automated pipeline |
| New product (no history) | ChatGPT + competitor data | Prophet needs history, unusable for new products |

**Prophet quick start (pseudocode):**

```python
# 1. Prepare data: date + sales
# Format: ds (date), y (sales)
import pandas as pd
from prophet import Prophet

df = pd.DataFrame({
'ds': ['2025-01-01', '2025-01-02', ...], # date
'y': [10, 12, 8, ...] # daily sales
})

# 2. Train the model
model = Prophet(
yearly_seasonality=True, # yearly seasonality
weekly_seasonality=True, # weekly seasonality (weekend sales may differ)
changepoint_prior_scale=0.05 # trend-change sensitivity
)
model.fit(df)

# 3. Forecast the next 90 days
future = model.make_future_dataframe(periods=90)
forecast = model.predict(future)

# 4. Output: forecast + confidence interval
# forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
# yhat = forecast, yhat_lower/upper = 80% confidence interval
```

> **Prophet's core strength**: it auto-handles seasonality, trend changes, and holiday effects, without manual parameter tuning. For products with 1+ years of history, Prophet's forecast accuracy usually beats human judgment. For detailed implementation, see the relevant modules in [Path B: Developers](../b-developers/).

Content rephrased for compliance with licensing restrictions. Source: [Facebook Prophet documentation](https://facebook.github.io/prophet/)

### 6.2 Multi-Channel Inventory Sync (Amazon + Shopify + own site)

If you sell on Amazon, Shopify, and your own site at once, inventory sync is a key challenge. The same inventory sold across channels can oversell (sold out but still selling on another channel) if not synced.

**Multi-channel inventory-management framework:**

```

Amazon Shopify own site
FBA warehouse self-fulfilled self-fulfilled


inventory-hub system
(total inventory pool)

```

**Strategy choices:**

| Strategy | For whom | Pros | Cons |
|----------|----------|------|------|
| **FBA-primary + MCF** | Amazon-primary sellers | fulfill other channels' orders from FBA inventory (Multi-Channel Fulfillment) | MCF fees are higher than FBA, timing may be slower |
| **Separate-warehouse management** | sellers with balanced channel sales | each channel has independent inventory, no cross-impact | needs more total inventory, higher capital tie-up |
| **3PL unified storage** | multi-channel large sellers | one warehouse serves all channels, highest inventory utilization | needs a 3PL partner, higher management complexity |

**AI-assisted multi-channel inventory allocation:**

```
I sell on the following channels at once. Help me optimize inventory allocation:

Total available inventory: [X] units

Channel data:
Amazon FBA: [X] orders/day, [X]% margin, Lead Time [X] days
Shopify: [X] orders/day, [X]% margin, self-fulfilled
Own site: [X] orders/day, [X]% margin, self-fulfilled

Advise:
1. Inventory-allocation ratio per channel
2. Should I use FBA MCF to fulfill other channels' orders?
3. Inventory-sync strategy (how to avoid overselling?)
4. If total inventory is insufficient, which channel to prioritize?
```

### 6.3 First-Leg Logistics Optimization: Ocean vs Air vs Rail

First-leg logistics usually is 10–20% of total product cost, and the right mode can meaningfully affect profit.

**Logistics-mode comparison:**

| Dimension | Ocean | Air | Rail (China-Europe) |
|-----------|-------|-----|---------------------|
| **Speed** | 30–45 days | 7–12 days | 18–25 days |
| **Cost** | $3–6/kg | $8–15/kg | $5–8/kg |
| **Best for** | large volume, non-urgent | small volume, emergency restock | EU marketplace, medium volume |
| **Minimum quantity** | 1 CBM or full container | no minimum | 1 CBM |
| **Risk** | port congestion, weather delays | flight cancellation, peak-season price hikes | route instability |
| **Applicable routes** | global | global | China → Europe |

**Decision framework:**

```
need to restock
inventory covers > 45 days?
yes → ocean (lowest cost)
inventory covers 15–45 days?
destination is Europe? → consider rail (value)
other → ocean + a little air (hybrid)
inventory covers < 15 days?
air (emergency restock, avoid stockout)
already out of stock?
air for the fastest batch + ocean for the large batch (both at once)
```

**AI-assisted logistics decision:**

```
Help me choose the optimal first-leg logistics mode:

Cargo info:
- Product weight: [X] kg/unit, volume: [X] CBM/unit
- This shipment quantity: [X] units
- Total weight: [X] kg, total volume: [X] CBM
- Origin: [city]
- Destination: Amazon [US/DE/JP] FBA warehouse

Time requirements:
- Current inventory covers: [X] days
- Desired arrival date: [date]

Logistics quotes (if any):
- Ocean: $[X]/kg or $[X]/CBM, [X] days
- Air: $[X]/kg, [X] days
- Rail: $[X]/kg (if applicable), [X] days

Analyze:
1. Total-cost comparison of each mode
2. Arrival time and stockout risk of each
3. Recommended plan (balancing cost and speed)
4. Recommend a hybrid (e.g., 70% ocean + 30% air)?
5. If logistics is [X] days late, the impact on inventory and the response
```

> **The core principle of first-leg logistics**: ocean for routine restocks to control cost, air for emergencies to avoid stockouts. Reserve a 10–20% air-freight budget as contingency for each ocean shipment.
---
Content rephrased for compliance with licensing restrictions. Source: [impakter.com FBA prep and 3PL operations](https://impakter.com/the-2026-playbook-fba-prep-services-ai-forecasting-and-greener-3pl-operations/)

---

## 7. Learning Resources

### 7.1 Free courses

| Resource | Platform | Length | For whom | Link |
|----------|----------|--------|----------|------|
| Amazon Seller University — Inventory Management | Amazon | self-paced | all sellers (official free courses on FBA inventory management, IPI Score, restock tools) | [sellercentral.amazon.com/learn](https://sellercentral.amazon.com/learn) |
| Supply Chain Management Specialization | Coursera (Rutgers) | 16 weeks | sellers wanting to learn supply chain systematically (inventory theory, demand forecasting, supplier management) | [coursera.org](https://www.coursera.org/specializations/supply-chain-management) |
| ChatGPT Prompt Engineering for Developers | DeepLearning.AI | 1.5h | everyone (writing good prompts is the basis of AI inventory analysis) | [deeplearning.ai](https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/) |
| Prophet Quick Start Guide | Facebook/Meta | 1h | sellers with a Python basis (time-series forecasting intro) | [facebook.github.io/prophet](https://facebook.github.io/prophet/docs/quick_start.html) |

### 7.2 Recommended YouTube channels

| Channel | Focus | Why |
|---------|-------|-----|
| My Amazon Guy | full Amazon-operations workflow, incl. inventory management and IPI Score optimization | comprehensive, many real cases and data |
| Seller Sessions | deep Amazon-seller interviews, incl. supply-chain and inventory strategy | real seller experience, hands-on |
| Jungle Scout | product-research and inventory-management tool tutorials, incl. demand-forecasting features | best source for tool tutorials |
| Travis Marziani | Amazon FBA operations, incl. inventory management and cash-flow optimization | good for SMB sellers, clear explanations |

### 7.3 Recommended reading

| Article/resource | Source | Core idea |
|------------------|--------|-----------|
| [Improving Your Amazon IPI Score](https://goaura.com/blog/improving-your-amazon-ipi-score) | GoAura | full IPI-Score improvement guide, incl. concrete strategies for the four dimensions and common pitfalls |
| [Amazon Inventory Management Guide](https://goaura.com/blog/amazon-inventory-management) | GoAura | systematic Amazon inventory-management method, from base metrics to advanced strategy |
| [RestockPro Review](https://goaura.com/blog/restockpro) | GoAura | deep RestockPro review, incl. feature comparison and use-case analysis |
| [AI in E-Commerce Inventory Management](https://selectedfirms.co/blog/ai-in-ecommerce-inventory-management) | SelectedFirms | full landscape of AI in e-commerce inventory management, incl. demand forecasting and auto-restock |
| [FBA Prep Services, AI Forecasting and Greener 3PL](https://impakter.com/the-2026-playbook-fba-prep-services-ai-forecasting-and-greener-3pl-operations/) | Impakter | 2026 FBA operations trends, incl. AI forecasting and green logistics |
| [How to Use AI to Grow Your Amazon Sales](https://us.entrepreneur.com/growing-a-business/how-to-use-ai-to-grow-your-amazon-sales-rankings-and/499421) | Entrepreneur | hands-on AI applications in Amazon operations, incl. inventory optimization and sales forecasting |
| [Prophet Documentation](https://facebook.github.io/prophet/) | Meta | Facebook Prophet official docs, the best intro to time-series forecasting |

Content rephrased for compliance with licensing restrictions. Sources cited inline.

### 7.4 Communities & forums

| Community | Platform | Notes |
|-----------|----------|-------|
| r/AmazonSeller | Reddit | general Amazon-seller community, active on inventory and supply chain |
| r/FulfillmentByAmazon | Reddit | FBA-seller community, lots of inventory and IPI-Score discussion |
| Amazon Seller Forums | Amazon | official forums, first-hand FBA policy updates and storage limits |
| WeAreSellers (知无不言) | Zhihu | Chinese cross-border community, rich supply-chain and logistics experience |
| Chuanglan Forum | independent | Chinese seller community, many first-leg logistics and supplier-management cases |
| eComCrew | Podcast + community | English e-commerce community, inventory best practices and tool recommendations |

## 9. Completion Checklist

- [ ] Built a complete restock decision model for one product with AI (with safety-stock calc, reorder point, three-scenario analysis)
- [ ] Analyzed your IPI Score with AI, built a concrete improvement plan and ran it at least 1 month
- [ ] Built one promo-stocking plan with AI (Prime Day or BFCM) with an 8-week timeline
- [ ] Built a monthly restock SOP and ran it at least 2 months, recording restock accuracy
- [ ] Handled at least one batch of slow-moving inventory with AI, comparing storage fees before and after
- [ ] Assessed supplier lead-time risk with AI, built at least one backup-supplier plan

Complete all of the above and you've mastered AI-assisted inventory management. Next: [A6 Compliance & Risk Control](a6-compliance.md) — using AI to handle Amazon compliance challenges.

---

## Appendix: Quick-Reference Cards

### Prompt cheat sheet

| Scenario | Prompt template | Section |
|----------|-----------------|---------|
| Restock decision analysis | Restock decision analysis | [3.1](#31-restock-decision-analysis) |
| Multi-SKU batch restock | Multi-SKU restock priority (Variant A) | [3.1](#31-restock-decision-analysis) |
| New-product first-batch | New-product first-batch estimate (Variant B) | [3.1](#31-restock-decision-analysis) |
| Safety-stock calculation | Safety-stock calculation | [3.2](#32-safety-stock-calculation) |
| Seasonal demand forecast | Seasonal demand forecasting | [3.3](#33-seasonal-demand-forecasting) |
| Promo-stocking strategy | Promo-stocking strategy (Prime Day/BFCM) | [3.4](#34-promo-stocking-strategy-prime-day--bfcm) |
| Multi-marketplace allocation | Multi-marketplace inventory allocation | [3.5](#35-multi-marketplace-inventory-allocation) |
| Slow-moving handling | Slow-moving inventory handling strategy | [3.6](#36-slow-moving-inventory-handling-strategy) |
| Supplier lead-time assessment | Supplier lead-time risk assessment | [3.7](#37-supplier-lead-time-risk-assessment) |
| IPI Score improvement | IPI Score improvement plan | [3.8](#38-ipi-score-improvement-plan) |
| Multi-channel allocation | Multi-channel inventory allocation | [6.2](#62-multi-channel-inventory-sync-amazon--shopify--own-site) |
| First-leg logistics decision | First-leg logistics-mode choice | [6.3](#63-first-leg-logistics-optimization-ocean-vs-air-vs-rail) |

### Tool cheat sheet

| Need | Recommended tool | Free alternative |
|------|------------------|------------------|
| Restock calculation | SoStocked / RestockPro | ChatGPT + Excel |
| Demand forecasting | SoStocked / Forecastly | ChatGPT + seasonal prompt |
| IPI monitoring | Amazon Inventory Dashboard | Amazon's official tools (free) |
| Age management | RestockPro | Amazon Inventory Age report |
| Profit tracking | Inventory Lab | Excel + FBA Revenue Calculator |
| Time-series forecasting | Prophet (open-source) | ChatGPT manual analysis |
| Inventory-data API | python-amazon-sp-api (open-source) | Seller Central manual export |
| Multi-channel sync | SoStocked / SellerCloud | manual management + Google Sheets |
| Supplier management | RestockPro | Excel + ChatGPT |
| Logistics tracking | Flexport / Freightos | Excel tracker |

### Safety-stock & restock formula quick reference

| Formula | Expression | Notes |
|---------|------------|-------|
| **Safety stock** | Z × σ_d × √L | Z=service-level factor, σ_d=daily-sales std dev, L=Lead Time days |
| **Reorder Point** | daily sales × Lead Time + safety stock | order when inventory drops to this level |
| **Economic Order Quantity (EOQ)** | √(2DS/H) | D=annual demand, S=per-order cost, H=unit annual holding cost |
| **Inventory turnover** | annual sales ÷ average inventory value | higher is better, means fast inventory flow |
| **Days of cover** | (current inventory + in-transit) ÷ daily sales | restock when below Lead Time + safety days |
| **Stockout cost** | out-of-stock days × daily sales × per-unit profit + rank-recovery cost | to assess the true loss of a stockout |
| **Overstock cost** | inventory quantity × monthly storage fee × slow-moving months + capital-tie-up cost | to assess the true cost of holding slow-movers |

### Service-level factor (Z) quick reference

| Service level | Z value | Meaning | Use case |
|---------------|---------|---------|----------|
| 90% | 1.28 | allow a 10% stockout probability | low-profit, easily substitutable products |
| 95% | 1.65 | allow a 5% stockout probability | the recommended value for most products |
| 97.5% | 1.96 | allow a 2.5% stockout probability | high-profit, high-stockout-cost products |
| 99% | 2.33 | allow a 1% stockout probability | core bestsellers that can't run out |

### Inventory-health checklist

```
Weekly check:
Is IPI Score ≥ 400?
Any Stranded Inventory? → fix immediately
Any SKU with inventory < 14 days of sales? → emergency restock
Is the in-transit inventory status normal? → track logistics

Monthly check:
List of SKUs aged > 90 days → build a handling plan
SKUs aged > 180 days → urgent clearance
Each SKU's Sell-through Rate → below 3 needs attention
Restock-plan execution → ordered and arrived on time?
Supplier lead-time record → update the lead-time data

Quarterly check:
Do safety-stock parameters need adjusting? (sales change, Lead Time change)
Supplier assessment → need to develop a backup supplier?
Inventory-capital share → over 60%?
Next promo's stocking plan → start 8 weeks out
```

### Inventory decision tree

```
need a restock decision
days of cover < Lead Time + safety days?
yes → emergency restock (consider air)
no ↓
days of cover < Lead Time + safety days + 30 days?
yes → routine restock (ocean)
no ↓
a promo in the next 3 months?
yes → start the promo-stocking SOP
no ↓
share of inventory aged > 90 days > 20%?
yes → handle slow-movers first, then consider restocking
no ↓
inventory level healthy → check again next month
```

[< A4 Customer Service](a4-customer-service.md) | [Path overview](../README.md) | [A6 Compliance >](a6-compliance.md)
