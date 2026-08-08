# Constraints: ecom-pricing

Generated from `ontology/constraints.yaml`.

- **amazon.cpc.value.actual_price_formula**: Amazon PPC 采用第二价格拍卖，实际支付的 CPC = 第二高出价 + $0.01，不需要出最高价 (verified 2026-08)
- **amazon.roas.value.profitable_threshold**: ROAS > 3.0 视为盈利 (verified 2026-08)

## Pricing Methodology (not platform rules)

The following are domain-specific financial constraints used in pricing analysis:
- **Breakeven price**: Unit cost + (Fixed costs / Expected units). Must exceed this to be profitable.
- **Minimum advertised price (MAP)**: Brand-enforced minimum. Violating MAP risks losing the brand relationship.
- **Competitive price range**: Lowest to highest among top 5 competitors. Pricing outside this range requires justification.
- **Profit margin**: (Price - Total Per-Unit Cost) / Price. Industry target varies by category (15-30% for electronics, 40-60% for private label).
- **Buy Box rotation**: Amazon rotates Buy Box among sellers within ~2% of the lowest price. Winning requires being within that band.
