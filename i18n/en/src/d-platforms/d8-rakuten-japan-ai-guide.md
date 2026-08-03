# D8. Rakuten Japan E-Commerce AI Guide

> **Track**: Path D: Multi-Platform · **Module**: D8
> **Last updated**: 2026-07-31
> **Difficulty**: Intermediate
> **Estimated time**: 1.5 hours


---

> Rakuten GMV ~$31B, the Japanese e-commerce market is $258B (2025). Japan's second-largest e-commerce platform (after Amazon JP). Partnering with YouTube Shopping in 2026. The operating logic is completely different from Amazon JP — Rakuten is more like an "online mall," and sellers have a high degree of customization.

## Chapter Navigation

1. [Rakuten vs Amazon JP Core Differences](#1-rakuten-vs-amazon-jp-core-differences) · 2. [Rakuten-Specific Operational Differences](#2-rakuten-specific-operational-differences) · 3. [Japanese Listing AI Optimization](#3-japanese-listing-ai-optimization) · 4. [Cross-Border Onboarding in Practice](#4-cross-border-onboarding-in-practice) · 5. [Common Traps](#5-common-traps) · 6. [Completion Checklist](#6-completion-checklist)

---

## What You'll Learn

Japan has high AOV and stable repeat purchase, but Rakuten plays by rules that are nothing like Amazon JP's.

After this module you'll be able to:
- State the core differences between Rakuten and Amazon JP in traffic logic and store weighting
- Write listings with AI that match Japanese business writing conventions (keigo, structure, information density)
- Work Rakuten's store-specific mechanics (Super SALE, points, store design)
- Complete the cross-border onboarding process

---


## 1. Rakuten vs Amazon JP Core Differences

| Dimension | Amazon JP | Rakuten |
|-----------|-----------|---------|
| Store page | Standardized (can't customize) | Highly customizable (HTML page) |
| Brand display | Limited (A+ Content) | Extremely strong (custom store design) |
| Points system | Amazon Points (weak) | Rakuten Points (extremely strong, closed ecosystem) |
| Email marketing | Prohibited from contacting buyers | Encourages sellers to send emails (R-Mail) |
| Event mechanism | Prime Day / BFCM | Super Sale / Marathon / days with 5 and 0 |
| User persona | All ages | Skews female, 30-50, family consumption |
| Monthly rent | None (by commission) | ¥19,500-100,000/month (by plan) |
| Commission | 8-15% | 2-7% (but with monthly rent) |

## 2. Rakuten-Specific Operational Differences

### 2.1 Store-Page Customization

Rakuten's biggest difference is that the store page can be fully customized (HTML/CSS), like a mini independent site:

- Brand-story page
- Product-category navigation
- Event-topic page
- Custom banner and visual design

AI application: use AI to generate Japanese store copy, event-page content, banner copy.

### 2.2 The Rakuten Points Ecosystem

Rakuten Points is one of Japan's largest points ecosystems:
- Users earn points shopping on Rakuten, paying with a Rakuten Card, and booking hotels on Rakuten Travel
- Points can be used across the entire Rakuten ecosystem
- Sellers can set an extra points multiplier to attract users (like a discount but in points form)
- During Super Point Back events the points multiplier stacks, and traffic surges

### 2.3 R-Mail Email Marketing

> **Related reading**: [D1 Shopify](shopify-ai-guide.md) — Shopify's Klaviyo email-marketing methodology can be referenced in D1; the email-automation and personalization strategies are reusable for R-Mail.

Amazon prohibits sellers from directly contacting buyers, but Rakuten encourages it:
- R-Mail: sellers can email users who have purchased
- Email content: new-product notifications, promotions, points events, usage tutorials
- AI application: AI generates Japanese marketing emails, personalized recommendations, send-time optimization

**R-Mail AI generation prompt:**

```
You are a Rakuten email-marketing expert, proficient in Japanese business emails.

Store info:
- Store name: [name]
- Category: [X]
- The purpose of this email: [new-product notification/promotion/repurchase reminder/thanks]

Please generate an R-Mail email:
1. Email subject (≤50 characters, attract opens)
2. Email body (Japanese, desu/masu form)
- Opening: thanks + greeting
- Middle: core info (new product/promotion/recommendation)
- Ending: CTA + points reminder
3. Recommended send time (Japanese users' habits)
4. Personalization-variable suggestions (username, last-purchased product, etc.)

Note:
- Japanese consumers value politeness and detail
- The email shouldn't be too long (Japanese users prefer conciseness)
- Must include an unsubscribe link (required by Japanese law)
- Points-related info has the highest open rate

<copy_discipline>
- Never write a feature, material, certification, or result the product doesn't have. Any attribute I didn't state above must not appear in the copy
- For anything sent to a customer (replies, emails, templates), don't make commitments I haven't authorized: refund amounts, compensation, timelines, or exceptions to platform policy must be confirmed by me before they go in
- Flag any claim touching efficacy, safety, environmental, or patent language separately for manual review
</copy_discipline>
```

### 2.4 Event Mechanism

> **Real case: Rakuten × YouTube Shopping Japan launch**
> On February 20, 2026, Google and Rakuten announced the launch of the YouTube Shopping service in Japan. While watching a YouTube video, users can press a button to show the product name and price on the screen, then jump to the Rakuten e-commerce platform for details ([Japan Today](https://japantoday.com/category/tech/google-rakuten-to-provide-new-shopping-service-in-japan-on-youtube)). This is Japan's first e-commerce platform to partner with YouTube Shopping, and creators can earn commissions by promoting Rakuten products.

Content rephrased for compliance with licensing restrictions.

| Event | Frequency | Characteristics | Seller strategy |
|-------|-----------|-----------------|-----------------|
| Super Sale | Quarterly | Site-wide big sale, the most traffic | Prepare inventory and event pages 4 weeks in advance |
| Marathon | Monthly | The more you buy, the more points (accumulated across stores) | Set tiered points multipliers to encourage users to bundle |
| Days with 5 and 0 | Monthly on the 5th/10th/15th/20th/25th/30th | 5x points days | These dates' conversion rates are significantly higher than usual |
| Shopping Marathon (お買い物マラソン) | Irregular | Cross-store shopping points stack | Participating gets extra exposure |

### 2.5 YouTube Shopping × Rakuten (2026 New Feature)

> **Related reading**: [E2 YouTube AI Operations](../e-social-media/e2-youtube-ai-guide.md) — the YouTube operations methodology is referenced in E2; the creator-collaboration and video-content strategies are directly reusable.

In February 2026, Rakuten partnered with Google to launch the YouTube Shopping feature in Japan. This is Japan's first e-commerce platform to partner with YouTube Shopping.

According to multiple reports ([Japan Today](https://japantoday.com/category/tech/google-rakuten-to-provide-new-shopping-service-in-japan-on-youtube), [Marketech APAC](https://marketech-apac.com/rakuten-ichiba-taps-google-to-roll-out-youtube-shopping-affiliate-programme-in-japan/), [Krows Digital](https://krows-digital.com/rakuten-youtube-shopping-japan-2026/)):

| Feature | Description |
|---------|-------------|
| In-video shopping | Users click the "View Products" button in a YouTube video |
| Product-info display | The product name and price are shown on the screen |
| Seamless jump | Users can navigate to the Rakuten product page while continuing to watch the video |
| Creator commission | YouTube creators earn commissions by promoting Rakuten products |
| Affiliate program | Based on the YouTube Shopping Affiliate Programme |

Content rephrased for compliance with licensing restrictions.

**Impact on sellers**:
- YouTube creator collaboration becomes a new traffic entry point for Rakuten
- You need to prepare product material suitable for video display
- The product page needs optimization to catch YouTube traffic
- Collaboration with Japanese YouTube creators becomes more valuable

**AI application**:
- AI generates product-introduction scripts suitable for YouTube creators (Japanese)
- AI screens suitable Japanese YouTube creators for collaboration
- AI analyzes YouTube traffic conversion data
- Combine with the methodology of [E2 YouTube AI Operations](../e-social-media/e2-youtube-ai-guide.md)

```
You are a Rakuten × YouTube Shopping strategy expert.

My Rakuten store: [name]
Category: [X]
Monthly sales: ¥[X]

Please create a YouTube Shopping strategy:

1. Product selection suitable for YouTube promotion
- Products with strong visual appeal
- Products needing demonstration/tutorials
- Moderate price (¥3,000-30,000)

2. Japanese YouTube creator collaboration plan
- Target creator types (review-focused/lifestyle/beauty)
- Collaboration model (product provision/payment/affiliate)
- Budget allocation

3. Product-page optimization (to catch YouTube traffic)
- Landing-page design
- Video-viewer exclusive offer
- Points-multiplier setting

4. Effect tracking
- YouTube → Rakuten conversion tracking
- Creator ROI analysis
- Comparison with other traffic channels

<calculation_discipline>
- Use only the numbers I supplied above. Do not assume any parameter I didn't give you (interest rates, industry averages, platform fee rates, exchange rates) — list what's missing and ask
- **Write out the formula before substituting numbers** so I can check each step. Don't give only the final result
- For conclusions involving money or inventory, note which input they're most sensitive to — which number, if I change it, flips the conclusion
- If you can't complete the calculation, stop and say what's missing. Do not fill gaps with assumed values
</calculation_discipline>
```

### 2.6 Rakuten Initial Setup Fee

According to industry material ([NextLevel Global](https://nextlevel.global/blog/2025/10/22/japan-ecommerce-marketplace-comparison/)), Rakuten onboarding requires an initial setup fee of ¥60,000, plus a monthly subscription fee of ¥19,500-¥100,000 (depending on the plan).

Content rephrased for compliance with licensing restrictions.

| Fee item | Amount | Description |
|----------|--------|-------------|
| Initial setup fee | ¥60,000 | One-time |
| Ganbare! Plan monthly rent | ¥19,500/month | For new sellers |
| Standard Plan monthly rent | ¥50,000/month | For medium scale |
| Mega Shop Plan monthly rent | ¥100,000/month | For large scale |
| Commission | 2-7% (by category and plan) | The higher the rent, the lower the commission |
| System usage fee | 0.1% of monthly sales | Extra fee |

### 2.7 Rakuten vs Amazon JP Selection Decision Framework

```
You are a Japanese e-commerce platform strategy expert.

My product: [name]
Category: [X]
Brand positioning: [premium/mid-range/value]
Monthly budget: ¥[X]
Have a Japanese legal entity: [yes/no]

Please help me decide between Rakuten vs Amazon JP:

1. Category-suitability analysis
- Rakuten's advantage categories: food, beauty, fashion, home
- Amazon JP's advantage categories: electronics, books, daily necessities
- On which platform does my category have more advantage?

2. Cost comparison
- Rakuten: monthly rent + commission + initial setup fee
- Amazon JP: commission + FBA fees
- Which platform has lower total cost?

3. Operational complexity
- Rakuten: needs a custom store page (HTML/CSS)
- Amazon JP: standardized Listing
- Does my team's capability match?

4. Traffic acquisition
- Rakuten: points ecosystem + email marketing + events
- Amazon JP: search + ads + Prime
- Which traffic-acquisition method suits me better?

5. Brand building
- Rakuten: highly customizable, large brand-display space
- Amazon JP: standardized, limited brand display
- How important is brand building to me?

6. Recommendation
- Which platform to onboard first?
- Should I onboard both platforms at the same time?
- Resource-allocation suggestions

<copy_discipline>
- Never write a feature, material, certification, or result the product doesn't have. Any attribute I didn't state above must not appear in the copy
- For anything sent to a customer (replies, emails, templates), don't make commitments I haven't authorized: refund amounts, compensation, timelines, or exceptions to platform policy must be confirmed by me before they go in
- Flag any claim touching efficacy, safety, environmental, or patent language separately for manual review
</copy_discipline>
```

## 3. Japanese Listing AI Optimization

> **Related reading**: [A2 Listing Optimization](../a-operators/a2-listing-optimization.md) — the general Listing-optimization methodology is referenced in A2, the core optimization framework is adaptable to Japanese Listings.

### 3.1 Japanese Consumer Copy Preferences

| Dimension | Western style | Japanese style |
|-----------|---------------|----------------|
| Information volume | Concise, highlight key points | Detailed, comprehensive |
| Tone | Direct, confident | Polite, humble (desu/masu form) |
| Trust elements | Review count | Quality assurance, safety/security, made in Japan |
| Image style | Lifestyle | Detailed spec images, usage-instruction images |
| After-sales promise | Simple return policy | Detailed warranty, customer-service contact |

### 3.2 AI-Generate Japanese Listing (Enhanced Version)

```
You are a Rakuten Japan-market Listing optimization expert, proficient in Japanese e-commerce copy.

Here is my English product info:
- Product name: [name]
- Category: [X]
- Selling points: [5]
- Price: $[X] (about ¥[X])
- Target users: [describe]

Please generate a complete Rakuten Japanese Listing:

1. Product name (Japanese, 80-120 characters)
- Format: 【brand name】product name core attribute | related keywords
- The Rakuten title can include 【】 and | separators
- Include search hot words

2. Catchphrase (キャッチコピー, 20-30 characters)
- Short and powerful, highlight the core value

3. Product description (商品説明, 500-1000 characters, desu/masu form)
- Opening: product overview + core value
- Middle: detailed feature explanation + use scenarios
- Ending: quality assurance + after-sales promise
- Include HTML formatting (Rakuten supports custom HTML)

4. Product spec (商品スペック, all technical parameters)

5. Recommended keywords (10-15 Japanese search terms)

6. Store-page copy suggestions
- Brand story (ブランドストーリー)
- Reasons to choose us (選ばれる理由)
- Customer reviews (お客様の声, selected)

Note:
- Use desu/masu form, emphasize quality, security, warranty
- Japanese consumers like detailed usage instructions and precautions
- Include the "free shipping" (送料無料) mark (if applicable)
- Mention the points multiplier (ポイント倍)

<copy_discipline>
- Never write a feature, material, certification, or result the product doesn't actually have. Any attribute I didn't state above must not appear in the copy — this is the number-one cause of listing takedowns and false-advertising complaints
- If you need a selling point I didn't supply, list what you need from me rather than improvising
- Flag any claim touching efficacy, safety, environmental, or patent language separately so I can verify it by hand
</copy_discipline>
```

### 3.3 Rakuten Store-Page Design

Rakuten's biggest difference is that the store page can be fully customized (HTML/CSS):

```
Rakuten store-page structure suggestion:

Top page (トップページ)
Header (ヘッダー): brand logo + navigation + search
Main banner (メインバナー): current promotion/new products
Category (カテゴリー): classified by product line
Ranking (ランキング): store best-sellers Top 5
New arrivals (新着商品): recently listed products
Reviews (レビュー): selected positive-review screenshots
Footer (フッター): store info + contact + return policy
```

### 3.4 Rakuten Ad System

| Ad type | Description | Billing |
|---------|-------------|---------|
| RPP (Rakuten Promotion Platform) | Search-results ads | CPC (from ¥25) |
| CPA ads | Pay per sale | 20% of the sale amount |
| Coupon Advance (クーポンアドバンス) | Coupon ads | By distribution volume |
| Targeting Display (ターゲティングディスプレイ) | Display ads | CPM |

**RPP ad optimization prompt:**

```
You are a Rakuten RPP ad optimization expert.

My product: [name]
Category: [X]
Daily budget: ¥[X]
Current ROAS: [X]

Please optimize:
1. Japanese keyword strategy (core words + long-tail words)
2. Bidding strategy (Rakuten RPP minimum ¥25/click)
3. Coordination with Super Sale/Marathon events
4. Points-multiplier setting suggestions (ROI comparison of raising the points multiplier vs a price cut)

<calculation_discipline>
- Use only the numbers I supplied above. Do not assume any parameter I didn't give you (interest rates, industry averages, platform fee rates, exchange rates) — list what's missing and ask
- **Write out the formula before substituting numbers** so I can check each step. Don't give only the final result
- For conclusions involving money or inventory, note which input they're most sensitive to — which number, if I change it, flips the conclusion
- If you can't complete the calculation, stop and say what's missing. Do not fill gaps with assumed values
</calculation_discipline>
```

## 4. Cross-Border Onboarding in Practice

### 4.1 Onboarding Paths

| Path | Description | Best for |
|------|-------------|----------|
| Direct onboarding | Needs a Japanese legal entity or a representative in Japan | Sellers with a Japanese company |
| Through an agency | A local Japanese agency onboards and operates on your behalf | Cross-border sellers without a Japanese company |
| Rakuten Global Market | Rakuten's cross-border channel | Testing the Japanese market |

### 4.2 Onboarding Fees

| Plan | Monthly rent | Commission | Best for |
|------|--------------|------------|----------|
| Ganbare! Plan | ¥19,500/month | 3.5-7% | New sellers/small scale |
| Standard Plan | ¥50,000/month | 2-4.5% | Medium scale |
| Mega Shop Plan | ¥100,000/month | 2-4.5% | Large scale/many SKUs |

## 5. Common Traps

### 5.1 Running Rakuten with an Amazon mindset

Rakuten is **store-centric**, not product-centric. Traffic goes to the store, not the individual item. Operating each SKU as a standalone listing forfeits the platform's main traffic mechanism.

### 5.2 Machine-translating Japanese

Get the keigo level or the business register wrong and Japanese shoppers will simply read you as an untrustworthy merchant. This is where Japan differs most from other markets — "unnatural" copy is a hard failure here, not a minor blemish.

### 5.3 Skipping the points (ポイント) campaigns

Sitting out the points-multiplier campaigns during major sales means voluntarily exiting the sale traffic. Price the points cost in up front rather than deciding when the campaign arrives.

### 5.4 Under-investing in store design

The Rakuten store page carries most of the brand-trust weight. Ship with a default template and your conversion will sit visibly below comparable sellers.

---

## When this doesn't work

- **Your Japanese is merely correct.** This market is sensitive to honorific level, sentence rhythm and the handling of loanwords, and traces of machine translation cost you trust directly. It shows most in support replies — a wrong politeness level reads worse than no reply. A native speaker has to pass over the final text.
- **You transplant Amazon's shop and operating model.** Shops here are merchant-operated: page structure, promotional mechanics and the points system follow a different logic from Amazon's. Carrying an Amazon listing mindset across usually does not take, and the shop needs rebuilding on the platform's own model.
- **You apply standard cross-border aftersales.** Japanese buyers generally expect more of packaging integrity, dispatch speed, documentation and response, and falling short shows up in reviews and is hard to recover. Confirm your fulfilment chain can reach that level consistently before entering, rather than listing first and finding out.
- **Your volume does not support local operations.** Local support, local returns and maintaining Japanese content are ongoing costs. At low volume, testing through Amazon JP first is usually safer than opening a second Japanese channel at the same time.

---

## 6. Completion Checklist

- [ ] Complete Rakuten onboarding application
- [ ] Design a custom store page
- [ ] Complete Japanese Listing optimization
- [ ] Set up a Rakuten Points strategy
- [ ] Establish an R-Mail email-marketing process
- [ ] Launch RPP advertising
- [ ] Participate in the first Super Sale event
- [ ] Explore YouTube Shopping × Rakuten collaboration opportunities
