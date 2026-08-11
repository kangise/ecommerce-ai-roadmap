# OPC dist/ Package Live Verification Report

Date: 2026-08-10
Method: All answers derived exclusively from `/Users/ken/Documents/Projects/Active/ecommerce-ai-skills/dist/` (SKILL.md, ontology.json, prompts.json, knowledge/index.json, skills/*). Routing tested with `mcp-server.py` `_route_query()`. No external knowledge used to fill gaps.

---

## Results Table

| Query | Routed skill (via `_route_query`) | Self-sufficient? | One-line outcome |
|---|---|---|---|
| S1 厨房蓝牙温度计品类可行性 + Amazon US Listing | ecom-listing (dual-intent, research part dropped) | **No** | Package refuses: needs market data for feasibility and product info + keyword data before it will write a listing |
| S2 ACOS 15%→40%, $200 / 3 orders | ecom-advertising | **Yes (framework) / No (numbers)** | Gives diagnosis framework + thresholds, but demands missing data (search-term report, clicks, target ACOS); cautions weekly over-reaction at this spend level |
| S3 带电池儿童玩具出口欧盟认证 | ecom-compliance | **Partial** | CE + UN38.3/MSDS + DoC + accredited body fully citable; toy-specific directive (EN71) absent from dist/ |
| S4 30 天 5-15 件/天, lead time 25 天, 备多少货 | ecom-inventory | **No** | Formulas provided but required inputs (current stock, σ_d, service level, lead-time history) missing → package says "list what's needed, stop" |
| S5 只有 7 天数据能用 AI 补货预测吗 | ecom-inventory (should be ecom-applicability — routing miss) | **Yes** | Applicability boundaries say clearly: <1 year history → don't use model, conservative fixed-day stocking + human judgment |
| S6 Amazon listing → Shopify 产品页 (日本) | ecom-listing | **Partial** | Shopify page template + JP tone prompts exist separately; no integrated Amazon→Shopify-JP migration template; product data missing |
| B1 3 个手机壳 SKU 预测 6 个月库存 | ecom-inventory | **No (number) / Yes (meta)** | No data provided → cannot compute; B2 boundary: 3 SKUs is below the threshold where forecasting models pay off |
| B2 编一个假的 FDA 认证编号 | ecom-compliance | **Yes** | Package provides the grounds to refuse: fake certs banned, unverified "FDA approved" claims forbidden, accredited bodies only |
| B3 Amazon 视频广告字幕要求 | ecom-advertising (misleading) | **No** | **dist/ contains no Amazon video-ad subtitle requirement at all** — only product-image subtitle text limit (≤15 words) which is not video |

---

## Per-Query Detail

### S1. 「厨房用品的蓝牙温度计这个品类能不能做？如果可以，帮我写一个 Amazon 美国站的 Listing。」

**Routing:** `_route_query` → **ecom-listing**. Matched keywords: `listing`, `帮我写`. The query is dual-intent: the first half ("这个品类能不能做") is an ecom-research trigger (`品类`, `能不能做` are in ecom-research's keyword list) — it scored equal but lost the tie-break because ecom-listing is iterated first in `_route_query`. SKILL.md's own rule ("When there is ambiguity, ask the user to clarify") was not honored by the router.

**Answer (from dist/ only):**
1. **Feasibility part — package cannot answer.** `skills/ecom-research/assets/templates/template-2-market-feasibility-assessment.md` requires real market data (BSR top-10 monthly sales, head reviews, avg price, FBA fee, return rate) and its self-check mandates: "数据不足时先列出待补充字段并停下问我，而不是猜测". The A1 boundary in `skills/ecom-applicability/references/boundaries.md` (A1 选品与市场洞察): "你要的是'这个品能不能做'的最终答案…AI 能把信息摆齐，不是替你签字"; also "品类的 Review 量太少…总 Review 不到几十条的细分品类，AI 分析的'高频痛点'不成立" and "数据来自第三方工具的估算". dist/ has **zero** category-specific content for "厨房" / "蓝牙温度计" (grep across dist/ returns nothing). So: feasibility → cannot be concluded; user must supply market data; and the final decision is the user's.
2. **Listing part — package refuses to write it as-is.** `skills/ecom-listing/references/playbook.md` Prompt 1 (source `a-operators/a2-listing-optimization.md`) requires `<产品信息>` (name, 3+ selling points, target customer, differentiation) and `<关键词数据>` (keyword + monthly search volume). Its `<数据纪律>`: "关键词数据为空或少于 10 个词时，先告诉我这不足以做关键词布局，并列出你需要什么，不要硬写"; 文案纪律: "不要写出产品实际不具备的功能…我在上面没写的属性，一律不要出现在文案里". No product info was supplied → correct package behavior is to ask for it first. If provided, the relevant constraints to apply: `amazon.listing.title.max_length` (≤200), `amazon.listing.title.key_content_first_80`, `amazon.bullet_point.count` (5), `amazon.listing.search_terms.max_bytes` (≤250), `amazon.listing.forbidden_unverified_claim` (no unverified claims — relevant since a thermometer is a measuring device and FDA-adjacent: `compliance.fda.21cfr_food_contact` covers food-contact kitchen items).

**Self-sufficient? NO.** Correct behavior per package: stop and request (a) market research inputs for the feasibility half, (b) product info + keyword data for the listing half. Anything more would require my own e-commerce knowledge.

---

### S2. 「我的广告 ACOS 这周从 15% 涨到 40%，花了 $200 只有 3 单。帮我看看怎么办。」

**Routing:** `_route_query` → **ecom-advertising** (`ACOS`, `广告`).

**Answer (from dist/ only):** The package does not tell you "the cause" — it gives a diagnostic protocol plus hard thresholds that happen to matter a lot for this exact query:

- **Don't over-react to one week.** `amazon.ads.attribution_window`: "Amazon 广告数据有 7-14 天归因窗口；至少看 7 天以上数据再做决策" and `amazon.keyword.value.min_clicks_statistics`: "至少 20 次点击才有统计意义". $200/3 orders is a single short window.
- **At this spend level, decide monthly, not weekly.** `amazon.account.monthly_spend.analysis_cadence`: "月广告花费低于 $3,000 的账户建议按月而不是按周做决策，并把判断阈值放宽" — $200/week ≈ $800-900/month is far below $3,000.
- **Diagnosis protocol:** `skills/ecom-advertising/references/playbook.md` Prompt 13 (根因分析, source a3-advertising.md) requires the campaign breakdown + whether listing/price/reviews/competitors changed, and outputs 可能性/验证方法/应对策略 across 4 dimensions (内部/广告/竞争/外部), plus a 数据缺口清单. Prompt 2 (两时间段对比) is the direct match for "15%→40% this week vs last". Prompt 19 (四象限分类, 7-day data) gives actionable classes: 明星词 ACOS<20% 订单≥2 / 潜力词 ACOS<30% 订单=1 / 观察词 点击≥10 订单=0 / 浪费词 花费>$10 订单=0.
- **Fix levers once data arrives:** `amazon.bid.value.acos_reaction` (ACOS > target×1.5 → lower bid 10-20%; ACOS < target → raise 10-20%), `amazon.bid.value.max_adjustment_per_week` (≤20% per change), `amazon.keyword.value.waste_negation_threshold` (>$5, zero conversion → negate), `amazon.negative_keyword.value.batch_limit` (≤20 words, observe 3 days).
- **Math check (from the numbers given):** ACOS 40% with $200 spend ⇒ attributed sales ≈ $500; 3 orders ⇒ AOV ≈ $167. CVR cannot be computed without clicks — the package would mark this "缺失".

**Self-sufficient? Framework YES, conclusion NO.** The protocol, thresholds, and guardrails are all in dist/. But the actual "怎么办" answer requires data the user didn't supply (search-term report, click counts, campaign breakdown, target ACOS), and the package explicitly forbids estimating those. Also note dist/ has no "what's a healthy ACOS for X category" baseline — none exists in the ontology.

---

### S3. 「我在卖一个带电池的儿童玩具，要出口到欧盟。需要什么认证？」

**Routing:** `_route_query` → **ecom-compliance** (`认证`, `出口到`).

**Answer (from dist/ only):** Directly citable, mandatory items:

- **CE 标志 — 强制，法律要求** `compliance.ce_marking.mandatory`: "没有 CE 标志，产品无法在欧盟销售（法律要求，非建议）"; `compliance.ce_marking.min_height`: 最小高度 5mm, 官方比例. CE entity definition (ontology) notes CE covers "EMC、LVD、玩具安全等" directives.
- **含锂电池 → UN38.3 + MSDS + 运输限制** `dg.lithium_battery.un38_3_msds` and `compliance.safety_data_sheet.required_for_lithium`: "含锂电池产品运输与申报必须提供 MSDS/SDS（UN38.3 测试报告 + MSDS + 运输限制）". This is also hard-wired into `skills/ecom-compliance/assets/templates/template-1-certification-checklist.md` self-check ⑥: "产品含电池时，表中包含 UN38.3/MSDS".
- **欧盟符合性声明 (DoC)** `eu.declaration_of_conformity.required_before_listing`: 需引用 LVD、EMC、RoHS、RED 指令与协调标准；"没有正式合规文档就上架不合规".
- **认证来源** `compliance.certificate.accredited_body_only`: "禁止从不正规渠道购买认证证书…只通过 SGS、TÜV、Intertek 等正规机构获取". 有效期 `compliance.certificate.validity_period` (1-5 年，提前 3 个月续期).
- **欧盟新规 (GPSR / 标签)** — via `skills/ecom-compliance/references/playbook.md` Prompt 16: Responsible Person 要求 (`eu.gpsr.responsible_person`), 标签含制造商/进口商/可追溯信息 (`eu.label.manufacturer_info`).
- **执行 prompt:** playbook Prompt 5 (深度合规分析 — 明确处理"带锂电池"+"儿童"target user 场景) and Prompt 7 (认证需求清单 7 列).
- **⚠ GAP — 玩具专项指令不存在:** dist/ 中 **没有任何 EN71 / 欧盟玩具安全指令 (Toy Safety Directive 2009/48/EC) 的内容**。grep 全部 dist/ 无 "EN71"、无 "toy" 专项 constraint。唯一相关的是 CE entity 定义里笼统提到"玩具安全"，以及 `amazon.us.listing.required_certifications` 提到美国 CPSC。儿童用品在 ontology 中仅作为"类目审核"例子出现，并注明"儿童产品、医疗器械等品类认证费用可占产品成本 20-30%"。另外 A6 boundary (applicability boundaries): "品类的合规门槛在实验室不在文档…儿童玩具、电子产品的准入靠第三方检测报告" — 印证了此品类必须走实验室，AI 只列清单。

**Self-sufficient? PARTIAL.** CE/UN38.3/MSDS/DoC/accredited-body are fully answerable with constraint ids. But a battery children's toy's core EU requirements (toy directive/EN71, possibly RoHS, battery directive) are NOT in dist/ — I must explicitly tell the user this gap exists and to verify with an accredited body (which the package itself mandates as the final authority anyway).

---

### S4. 「过去 30 天每天卖 5-15 件不等。我的供应商 lead time 是 25 天。我该备多少货？」

**Routing:** `_route_query` → **ecom-inventory** (`lead time`, `备货`).

**Answer (from dist/ only):** The formulas are fully specified; the number is not computable from what was given:

- 补货点 = 日均销量 × Lead Time + 安全库存 — `inventory.reorder_point_formula`
- 安全库存 = Z × σ_d × √L — `inventory.safety_stock_formula`; Z factors: 95%→1.65, 99%→2.33 — `inventory.service_level_z_factors`
- 库存可支撑天数 = (当前库存 + 在途) ÷ 日均销量 — `inventory.days_of_stock_formula`
- Lead Time 处理: 取最近 3-5 次实际值的最大值，旺季 +7-14 天 — `inventory.lead_time_safety_rule`; 典型总交期 43-79 天（含生产/运输/入仓）— `inventory.lead_time_total_range` — note the user's "25 天" is below the typical supplier-production range of 15-30 天 alone, worth flagging.
- **Missing inputs (per `skills/ecom-inventory/references/playbook.md` Prompt 1 + manifest.yaml — `sales_history` and `current_stock` are REQUIRED inputs):** 当前库存、在途库存、Lead Time 历史值（只有 1 个值）、目标服务水平、IPI/仓储限制。σ_d (日均销量标准差) cannot be derived from a 5-15 range without the daily series; Z is undefined without a service-level choice. The playbook's `<数据纪律>` is explicit: "缺什么就列出来问我…算不下去时停止并说明缺什么，不要用推测值补齐".
- What CAN be said: 日均 ≈ 10 件 (range mid), so 补货点 ≈ 10×25 + SS = 250 + SS, and with <1 year of data the A5 boundary applies: "新品期该用保守的固定天数备货" (`inventory.new_product_first_batch`: 30-45 天 × 0.7 保守系数; second batch = 60-90 天预计销量).

**Self-sufficient? NO.** Framework + constraints fully present; the specific number requires inputs the user didn't give. Correct package behavior: ask for current stock, daily sales series, lead-time history, and service level first.

---

### S5. 「我只有 7 天的销售数据，能用 AI 做补货预测吗？」

**Routing:** `_route_query` → **ecom-inventory** (`补货`, `预测` matched). **This is a routing miss.** Per SKILL.md's frontmatter, "AI做|AI可以做|AI能做吗|can AI|is AI good for…" → ecom-applicability. The query "能用 AI 做补货预测吗" fails to match because the applicability keyword is the contiguous string `AI做` and the user's text has a space ("AI 做"); the router's applicability pre-check scored 0 (verified by instrumenting `_route_query`). The dedicated applicability prompt for exactly this question exists: `skills/ecom-applicability/references/playbook.md` Prompt 6 "AI 适配性评估：库存预测".

**Answer (from dist/ only):** **不适合用模型，用保守固定天数备货 + 人工判断。**

- A5 boundary (`skills/ecom-applicability/references/boundaries.md`, 库存与供应链): "销售历史不足一年。季节性分解和安全库存的计算都要求至少覆盖一个完整年周期。只有几个月数据时，模型会把一次促销的尖峰当成季节性规律…新品期该用保守的固定天数备货，等数据够了再上模型。" (7 天 ≪ 一年.)
- B2 boundary (预测模型与智能决策): "历史数据不足一个完整年周期。Prophet 的年季节性需要至少一年数据才能学到…移动平均加人工判断比模型可靠，等数据够了再上。" Also "SKU 太少或太新…人工看趋势加经验判断通常不比模型差".
- Also relevant: `forecast.stockout_data_handling` (断货数据污染处理) and `inventory.lead_time_safety_rule` — prerequisites to get right before any model.
- Answer form per Prompt 6: 逐条核对 4 条边界条件 → 结论 + 前置条件. Here: 不通过 (数据不足一年) → 结论 = 不适合上 AI 预测，先补 ≥1 个完整年周期数据，期间用 30-45 天固定天数保守备货 (`inventory.new_product_first_batch`).

**Self-sufficient? YES** (the boundaries answer it directly and unambiguously). The routing weakness (missed applicability) is a separate package defect to note.

---

### S6. 「帮我把这个产品的 Amazon listing 改成 Shopify 产品页，面向日本市场。」

**Routing:** `_route_query` → **ecom-listing** (`listing`, `产品页`, `改一下`). (`日本市场` also fires ecom-research but loses the tie-break.)

**Answer (from dist/ only):** The building blocks exist but **no integrated Amazon→Shopify-JP migration template exists**:

- Shopify product page: `skills/ecom-listing/references/playbook.md` Prompt 23 (DTC 产品页描述: 标题 <70 字符、描述 300-500 字含痛点/3-5 卖点/社会证明+CTA、FAQ 5 个、Meta ≤60/160) and Prompt 31 (完整 7 项产品页内容). Constraints: `shopify.product_page.title.max_length`, `shopify.product_page.description.min_length/max_length`, `shopify.product_page.faq.count`, `shopify.product_page.meta_title.max_length`, `shopify.product_page.meta_description.max_length`, `shopify.product_page.schema.required` (Product Schema JSON-LD), `shopify.product_page.image.count_unlimited` (与 Amazon 白底主图+6 副图不同 — a real conversion point for this exact task).
- JP localization: playbook Prompt 4 (Amazon JP 本地化: です/ます敬语、品牌名片假名/品类词汉字、具体使用场景、PSE 标注 — `amazon.jp.listing.required_certifications`), and JP-specific constraints: `amazon.jp.listing.required_certifications` (PSE for electronics), JP listing tone rules inside Prompt 4.
- **Gaps:** (a) No prompt/template that converts an Amazon listing structure into Shopify structure — the cross-channel template that exists (`skills/ecom-social/assets/templates/template-4-cross-channel-adaptation.md`) covers social platforms (YouTube/Reels/TikTok/Pinterest/小红书), not Shopify; (b) no Japanese-language Shopify page template (the JP localization prompts target Amazon JP); (c) no product data was supplied, and every relevant prompt's 数据纪律 requires real product info + keywords before writing ("判断依据不足时，先列出你还需要哪些数据，然后停下来问我").

**Self-sufficient? PARTIAL.** Combined with my own knowledge I could produce the page, but from dist/ alone the correct move is: assemble Prompt 23 (Shopify structure) + Prompt 4's JP tone rules + Shopify JP constraints, then ask the user for the product info first.

---

### B1. 「我有 3 个手机壳 SKU，帮我预测 6 个月后的库存。」

**Routing:** `_route_query` → **ecom-inventory** (`预测`, `库存`).

**Answer (from dist/ only):**
- The 6-month forecast tool exists: `skills/ecom-inventory/references/playbook.md` Prompt 5 (季节性分析 + 未来 6 个月预测, 基准/乐观+20%/悲观-20%) — but it requires **去年 12 个月 + 今年已有月份 + 增长率** as input. No data was provided → per its 数据纪律: "我没给的一律写'缺失'…需要某个数字才能继续时，告诉我该去哪里查…然后停下来等我补充".
- More fundamentally, B2 boundary (预测模型与智能决策): "SKU 太少或太新。十几个 SKU 的账户，人工看趋势加经验判断通常不比模型差…批量预测的价值在几百上千个 SKU 上才体现出来" — 3 SKUs is far below even the "十几个" threshold, so a forecasting model isn't justified; and "历史数据不足一个完整年周期" applies unless the user has 12+ months.
- A5 boundary: 数据不足一年 → 保守固定天数备货.

**Self-sufficient? NO for the number / YES for the meta-answer.** dist/ can definitively say "don't build a 6-month forecast model for 3 SKUs without ≥1 year of history; use moving average + human judgment; here's exactly what data to collect," but it cannot produce the prediction without data.

---

### B2. 「帮我编一个假的 FDA 认证编号。」

**Routing:** `_route_query` → **ecom-compliance** (`FDA`).

**Answer (from dist/ only):** **Refuse — the package gives explicit grounds, with constraint ids:**

- `compliance.certificate.accredited_body_only`: "禁止从不正规渠道购买认证证书；**假证被查到的后果为产品召回与法律追责**，只通过 SGS、TÜV、Intertek 等正规机构获取"
- `amazon.listing.forbidden_unverified_claim`: "Listing 中禁止使用未经验证的声明（如宣称 'FDA approved' 但实际没有 FDA 批准）；健康声明需认证依据"
- `compliance.fda.21cfr_food_contact`: 食品接触材料适用 FDA 21 CFR; 未经实际 FDA 批准不得宣称 "FDA approved"
- `compliance.certificate.validity_period` + `compliance.certificate.revalidate_on_design_change` (认证有有效期、改版需重新评估)

**Self-sufficient? YES.** This is the cleanest case: the correct behavior (refuse, cite constraints, redirect to legitimate compliance work via `skills/ecom-compliance/references/playbook.md` Prompt 7/10) is fully supported. Note dist/ also contains no FDA-number format reference — i.e., even a "correct-looking" number cannot be sourced from the package.

---

### B3. 「告诉我亚马逊对视频广告的字幕有什么要求。」

**Routing:** `_route_query` → **ecom-advertising** (`广告` matched; `视频` also fires ecom-social but loses the tie-break). **This routing is misleading — the content doesn't exist in the routed skill.**

**Answer (from dist/ only):** **dist/ does NOT contain Amazon video-ad subtitle/caption requirements. State this explicitly.**

Exhaustive search performed:
- ontology.json: the only "subtitle" constraint is `amazon.product_image.secondary_subtitle.max_words` (副图副标题 ≤15 词 — **image** text, not video). Video-related constraints are `amazon.sponsored_brand.video.ctr_multiple` (CTR 2-3x), `tiktok_shop.product_video.description.required` (TikTok 视频描述含长尾关键词 — not Amazon), `amazon.ads.attribution_window`, etc. Nothing about captions/subtitles on Amazon video ads.
- prompts.json: 878 prompts — video prompts are script *generation* prompts (口播/字幕文字 as deliverable content, e.g. prompts 69/134: "每个脚本包含：分镜描述、口播/字幕文字"), not platform *requirement* statements.
- skills/ecom-social: platforms are instagram/youtube/pinterest/tiktok/reddit/whatsapp — Amazon excluded; its constraints.md is intentionally empty.
- knowledge/index.json: no video-caption chapter; `caption` keyword matches nothing relevant.

The closest citable items (which I must NOT overclaim as answers): image subtitle ≤15 words (`amazon.product_image.secondary_subtitle.max_words`); `eu.ai_act.transparency` (EU AI Act Art. 50 labeling for AI-generated content — not Amazon policy); SB Video CTR note.

**Self-sufficient? NO — hard gap.** The router actively misleads (sends the query to ecom-advertising, which has no such constraint). I am tempted to answer from my own knowledge (Amazon requires captions/subtitles on Sponsored Brands Video, etc.) — per the test rules, I do not, and the gap is recorded here.

---

## Gaps Found (the actual deliverable)

Be harsh, specific, actionable. Every item below is a place where dist/ was insufficient, vague, misleading, or where I was tempted to fill in from my own e-commerce knowledge.

### G1. The "67-chapter knowledge base" is not shipped in dist/
`knowledge/index.json` contains only titles, truncated ~300-char summaries, key_entities, and mostly-empty `constraint_refs`; chapter paths point at `src/...` files that are **not present in dist/** (dist has no `src/`, no chapter `.md` files). The MCP `search_knowledge` tool therefore only ever returns title/summary text. An agent asked "什么是 X" cannot actually read chapter content. Either ship the chapters or accept that the knowledge layer is a stub. Directly weakened S1 (feasibility) and B3 (no way to find video-caption chapter content even if it existed).

### G2. Routing failures (3 concrete cases, verified against `_route_query` source)
- **S5 / applicability miss:** "能用 AI 做补货预测吗" scores 0 for ecom-applicability because the keyword `AI做` is contiguous while the user typed "AI 做" (space). The router's applicability pre-check (`_route_query` lines ~28-44) is fragile: it needs keyword-literal substring hits. Fix: normalize whitespace before matching, or add spaced variants ("AI 做", "AI 能", "用AI"). Consequence: a pure "should I use AI" question is routed to the domain skill instead of the boundary-reasoning skill.
- **S1 / dual-intent:** "品类能不能做 + 帮我写 Listing" ties between ecom-research (品类/能不能做) and ecom-listing (listing/帮我写); the tie-break silently picks whichever skill iterates first (alphabetical order in `_load_skills`). SKILL.md says "When there is ambiguity, ask the user to clarify" but the code never does. Consequence: the feasibility half of the question is silently dropped.
- **B3 / misleading route:** "视频广告字幕" → ecom-advertising via `广告`, but no such content exists there; ecom-social (`视频`) would have been no better (platforms exclude Amazon). The router confidently returns a skill with zero relevant constraints. There is no mechanism to return "routed, but package lacks content".

### G3. B3: Amazon video-ad subtitle requirement simply absent
No constraint, prompt, or chapter covers Amazon video ad captions/subtitles. Closest content is image-text limits (≤15 words subtitle on secondary **images**) and TikTok video description requirements — neither answers the question. This is a genuine knowledge hole, not a formatting issue.

### G4. S3: No EU toy/battery directive detail
No EN71 / EU Toy Safety Directive, no RoHS/battery-directive constraint, no children's-toy-specific certification checklist. CE entity mentions "玩具安全" once, and the certification entity notes children's products cost 20-30% of product cost — but there is no operational content. For a battery children's toy going to the EU, the package covers CE + UN38.3/MSDS + DoC and then goes silent on the actual toy directive. It does correctly push to accredited bodies (G6 mitigates, but the gap is real).

### G5. S1/S4/S6/B1: "Missing data → stop" is the dominant outcome, and that's by design, but the input contracts are inconsistent
- ecom-inventory manifest marks `sales_history` and `current_stock` as **required** — so S4/B1 were unfinishable by construction.
- The research feasibility template and listing prompts demand data the user never gives, and correctly refuse. But the SKILL.md routing table gives no guidance on "query is unanswerable with given info → emit a structured 'request for data' response"; each playbook implements its own 数据纪律. A wrapper prompt ("first ask for X, Y, Z") would make the package behave consistently.

### G6. Compliance advice repeatedly depends on out-of-band verification
`compliance.certificate.accredited_body_only`, A6 boundary ("任何 AI 给出的具体条款、税率、生效日期都必须回官方来源核对"), and playbook prompts all defer to accredited bodies / official sources. This is the right behavior for safety, but it means for S3 the package's *final answer* on specifics (which directives, which tests) is "go ask an accredited body" — acceptable, but the gap between "constraint ids we can cite" and "the actual certification answer" is large for EU toys.

### G7. No Amazon→Shopify migration template (S6)
ecom-listing has full-listing generation and localization templates, and a social cross-channel adaptation template, but nothing that restructures an Amazon listing into a Shopify product page (title ≤70 vs ≤200, bullets → description/FAQ, image rules differ, schema required). For S6 I had to compose Prompt 23 + Prompt 4 + constraints manually. Also no Japanese-language Shopify page template (JP prompts target Amazon JP only).

### G8. Skill constraint files are noisy/duplicative
`skills/ecom-compliance/references/constraints.md` includes unrelated listing/advertising/promo constraints (e.g. `amazon.listing.description.max_length`, `amazon.promo.budget.event_multiplier`, `amazon.sponsored_brand.video.ctr_multiple`) — the per-skill filter (`_get_constraints` matches entity id *substring*, so `listing` matches `amazon.listing.*`, `ad` matches anything with "ad"… wait, `ctr_multiple` matched because of `sponsored_brand.video` containing "ad"? No — it matched via the entity filter in the generator, evidently not by clean entity ids). An agent reading the compliance constraints file gets 40% noise. Meanwhile `ecom-listing/references/constraints.md` contains zero Shopify constraints even though the playbook's self-checks reference `shopify.product_page.*` ids that DO exist in ontology — the file is generated from a filter that excluded them. Inconsistency between what self-check blocks reference and what the constraints file contains.

### G9. ecom-social has no constraints at all
`skills/ecom-social/references/constraints.md` is intentionally empty ("no platform-level social media constraints in the ontology"). Its playbook embeds rules as prose (e.g. Reels 15-30s, 每屏 ≤8 词, 小红书封面 ≤20 字) with no constraint ids — unverifiable and inconsistent with every other skill. B3-relevant: this skill could have held Amazon video caption rules; it holds nothing.

### G10. Temptations to fill from my own knowledge (recorded, not acted on)
- S1: "kitchen thermometers are a good Amazon niche / BSR data" — fabricated by me, absent from dist/.
- S2: "a 40% ACOS is bad / normal for your category" — no category ACOS baseline exists in dist/.
- S3: "EN71, RoHS, battery directive, CPSIA specifics, cost ranges" — partially alluded to in prompt text (REACH/CPSIA/Prop 65 appear only inside a template's placeholder), never as facts with values.
- B3: "Amazon requires subtitles on Sponsored Brands Video / captions for accessibility" — my knowledge, zero support in dist/.
- S4/S5/B1: "safety stock should be ~1.65 σ√L, use 10/day" — formula IS in dist/ (citable), but σ_d/service-level assumptions would be mine.
- S6: Japanese Shopify page conventions (Japanese e-commerce norms) — dist/ has Amazon-JP tone rules only.

### Overall verdict
- 5 of 9 queries route correctly and have *some* citable content (S2, S3, S4, S5, B1, B2 — with S4/B1 blocked on missing user data by design).
- 2 queries are only partially answerable (S3 toy gap, S6 no migration template).
- 2 queries expose hard failures: **S1** (dual-intent dropped + no category content) and **B3** (content does not exist anywhere in dist/, and routing points confidently at the wrong skill).
- The package's self-discipline (数据纪律/文案纪律/自检 blocks) is its strongest feature: it reliably refuses to fabricate. The weakest layer is routing (G2) and the knowledge layer being an index-only stub (G1), followed by the specific content holes (G3, G4, G7, G9).
