# Case Study: AI PPC Optimization — ACOS from 35% down to 18%

> Domain: Traffic & Acquisition · Related module: [A3 Advertising Optimization](../a-operators/a3-advertising.md)

---

## Background

A home-goods seller on Amazon US (single marketplace), $15,000 monthly ad budget, 20 active campaigns. ACOS had been stuck at 30–35% for months, TACOS at 12%. The team spent 3–4 hours a week manually adjusting bids and negative keywords, with inconsistent results.

Core problems:
- The search term report ran 2,000+ rows a week; manual analysis only ever covered the top 100
- Bid adjustments ran on "gut feel" — no systematic decision framework
- Wasted spend (high-click, zero-conversion terms) accounted for 25%+ of total spend
- ACOS regularly spiked past 60% during new-product launches

## SOP: The Weekly AI Ad-Optimization Loop

### Monday: AI analysis of the search term report (30 min)

Download the past 7 days' search term report from Seller Central and feed it to AI:

```
You are an Amazon PPC data analyst. Here is my search term report (past 7 days):
[Paste CSV data or the key columns: search term, impressions, clicks, spend, sales, orders]

Classify every term into four quadrants:
1. Star terms (high conversion + high sales): ACOS < 20%, orders >= 2
2. Potential terms (converting but low volume): ACOS < 30%, orders = 1
3. Watch terms (high impressions, no conversion): clicks >= 10, orders = 0
4. Waste terms (pure money burn): spend > $10, orders = 0

Give concrete actions for each class:
- Star terms: recommended bid range and match type
- Potential terms: whether a bid-increase test is worth it
- Watch terms: negative-match them or lower the bid?
- Waste terms: the list to negative-match immediately

Output as a table, sorted by spend descending.
```

### Tuesday: apply negatives and bid changes (20 min)

Based on the AI analysis:
1. Add the "waste terms" as campaign-level negative exact match
2. Graduate the "star terms" from auto campaigns into manual campaigns (exact match)
3. Raise bids on "potential terms" (+15–20%, watch for a week)
4. Lower bids on "watch terms" (−20%) or pause them

### Friday: competitor ad-strategy analysis (15 min)

```
I sell [category] on Amazon US. Here are my top 3 competitor ASINs:
[ASIN list]

Please analyze:
1. Which keywords their Sponsored Products ads show up under (as seen when I search)
2. Whether they are running Sponsored Brands and Sponsored Display
3. Their pricing strategy (are they pairing coupons/deals with ads?)
4. Which keywords I should contest, and which I should avoid

Note: my product sells at $[price]; theirs sell at $[price list]
```

### Monthly: ad-account structure health check (30 min)

```
Here is the monthly summary for all my campaigns:
[Paste campaign name, type, budget, spend, sales, ACOS, impressions]

Please diagnose:
1. Which campaigns have abnormally high ACOS, and what are the likely causes?
2. Is budget allocated sensibly? (Are high-ROAS campaigns starved?)
3. Is there keyword overlap between campaigns (self-competition)?
4. Should new-product campaigns and mature-product campaigns run different strategies?
5. Recommend next month's budget reallocation
```

## Results (after 3 months)

| Metric | Month 0 | Month 1 | Month 2 | Month 3 |
|--------|---------|---------|---------|---------|
| ACOS | 35% | 28% | 22% | 18% |
| TACOS | 12% | 10% | 8.5% | 7% |
| Monthly ad spend | $15,000 | $14,200 | $13,500 | $12,800 |
| Monthly ad sales | $42,857 | $50,714 | $61,364 | $71,111 |
| Wasted-spend share | 25% | 15% | 8% | 5% |
| Negative keywords | 50 | 180 | 320 | 450 |
| Weekly optimization time | 3–4 h | 1.5 h | 1 h | 1 h |

The key shift: ACOS dropped 17 percentage points while ad sales grew 66%. The driver was reallocating wasted spend ($3,750/month) to high-converting keywords.

## Tips

1. Negative keywords are the most underrated lever — practitioners managing 50+ brands report that most ACOS problems trace back to ads showing where they shouldn't, not to bid levels ([source](https://gigabrands.ai/blog/lower-acos-negative-targeting), content rephrased)
2. Don't watch ACOS alone — watch TACOS. ACOS measures ad efficiency; TACOS (ad spend / total sales) reflects what ads contribute to the whole business
3. Don't chase low ACOS in a product's first 30 days — the launch phase is for data accumulation and keyword ranking; 60% ACOS is normal there
4. The core value of AI on search term reports is spotting patterns humans can't — long-tail combinations buried in 2,000 rows
5. The industry-average ACOS is roughly 30% ([source](https://keywords.am/blog/amazon-ppc-optimization/), content rephrased); if yours is far above that, check negatives and wasted spend first

## References

- Content was rephrased for compliance with licensing restrictions
- [DeepBI: Amazon PPC Success Stories](https://www.deepbi.com/case/) — AI-driven ACOS reduction from 14% to 3%
- [GigaBrands: Lower ACOS with Negative Targeting](https://gigabrands.ai/blog/lower-acos-negative-targeting) — Negative targeting methodology
- [Keywords.am: Best Amazon PPC Optimization Strategy](https://keywords.am/blog/amazon-ppc-optimization/) — Industry ACOS benchmarks
- [Influencer Marketing Hub: Amazon PPC Campaign Structure 2026](https://influencermarketinghub.com/amazon-ppc-campaign-structure/) — Campaign restructuring results
