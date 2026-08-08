<!-- Generated from ontology/entities.yaml — do not edit by hand -->
<!-- claims: verified 2026-08 -->

# Glossary / 术语表 / 用語集

## Listing / Listing
> リスティング

- **ZH**: Amazon 商品上架信息的统称，包含标题、五点、产品描述、A+ Content、Search Terms 与图片等组成部分，是"被搜索到"与"被点击购买"的载体
- **EN**: The full set of product content fields on an Amazon listing (title, bullet points, description, A+ Content, Search Terms, images) that bridges search visibility and purchase conversion

## 五点 / Bullet Point
> 箇条書き

- **ZH**: Amazon Listing 中的卖点条目，通常 5 条，每条以大写卖点短语开头，先讲用户利益再讲产品特性
- **EN**: One of the selling-point lines in an Amazon listing (typically five), each starting with an all-caps benefit phrase, benefit before feature

## Search Term / Search Term
> サーチターム

- **ZH**: Amazon 后台的隐藏关键词字段，用户不可见但参与索引，共 250 字节，用于覆盖标题和五点放不下的长尾词
- **EN**: The hidden backend keyword field on Amazon that is indexed but not visible to shoppers; 250 bytes total, used to cover long-tail keywords not in the title or bullets

## ASIN / ASIN

- **ZH**: Amazon 标准识别编号，每个上架商品有唯一 ASIN；放入 Search Terms 没有索引价值
- **EN**: Amazon Standard Identification Number, unique per listed product; carries no indexing value inside Search Terms

## 产品图片 / Product Image
> 商品画像

- **ZH**: Amazon Listing 中的图片，含 1 张白底主图和 6 张副图；主图禁止文字/logo/水印，副图可承载文字信息图
- **EN**: Images of an Amazon listing: one white-background main image plus six secondary images; text/logo/watermark are forbidden on the main image

## A+ Content / A+ Content
> A+コンテンツ

- **ZH**: Amazon 品牌卖家可用的模块化增强内容（品牌故事、图文模块、对比图、使用场景、FAQ），无字符限制，是 Rufus 与 COSMO 读取的信息源之一
- **EN**: Modular enhanced content for Amazon brand sellers (brand story, image-text modules, comparison charts, use cases, FAQ); no character limit and readable by Rufus/COSMO

## 品牌故事 / Brand Story
> ブランドストーリー

- **ZH**: A+ Content 中的品牌故事模块（Brand Story），出现在 Review 上方，是免费的品牌曝光位
- **EN**: The Brand Story module of A+ Content, displayed above the reviews as free brand exposure

## Review / Review
> レビュー

- **ZH**: 买家评价，Rufus 回答用户问题时引用的信息源之一，好的 Review 比好的 Listing 文案更重要
- **EN**: Customer ratings and reviews; one of the sources Amazon Rufus cites when answering shopper questions

## Q&A / Q&A

- **ZH**: 产品问答/FAQ，Q&A 区域内容会被 Rufus 直接引用；GEO 场景下每个产品页也应配备 FAQ
- **EN**: Product Q&A / FAQ; the Q&A section is directly cited by Rufus, and FAQ coverage also drives AI search engines (GEO)

## 关键词 / Keyword
> キーワード

- **ZH**: 用户搜索的词，按权重布局在标题、五点、Search Terms 等组成部分中；关键词堆砌会被 A10/COSMO 算法惩罚
- **EN**: A term shoppers search; laid out by weight across title, bullets and Search Terms; keyword stuffing is penalized by the A10/COSMO algorithm

## 产品页 / Product Page
> 商品ページ

- **ZH**: Shopify 独立站的产品页面，自由格式（Liquid 模板），可嵌入视频/动画，是 Google SEO 与品牌故事的载体
- **EN**: A Shopify store product page; free-form (Liquid templates), can embed video/animation, carries Google SEO and brand storytelling

## Schema 标记 / Schema Markup
> スキーママークアップ

- **ZH**: 结构化数据标记（JSON-LD，Schema.org 的 Product/Offer/AggregateRating），AI 引擎偏好结构化产品信息，是 GEO 优化的核心
- **EN**: Structured data markup (JSON-LD; Schema.org Product/Offer/AggregateRating); AI engines prefer structured product data — the core of GEO

## TikTok 商品 / TikTok Product
> TikTok 商品

- **ZH**: TikTok Shop 的商品（及其商品卡/商品页），作用是"确认购买决策"而非说服购买；标题简短、主图为生活场景图、视频必须
- **EN**: A TikTok Shop product (and its product card/page), whose job is to confirm — not create — a purchase decision; short title, lifestyle main image, mandatory video

## 带货短视频 / Product Video
> 商品動画

- **ZH**: TikTok Shop 商品页/内容流中的带货短视频，是 TikTok 的核心转化元素；表现最好的视频应放在商品页上
- **EN**: Short commerce video used on TikTok product pages and feeds — the core conversion element; the best-performing video belongs on the product page

## 话题标签 / Hashtag
> ハッシュタグ

- **ZH**: TikTok 商品页和视频上的话题标签，按品类/场景/趋势或高流量/精准分类，参与站内搜索
- **EN**: Topic hashtags on TikTok product pages and videos, categorized as category/scene/trend or high-traffic/precise; they participate in on-site search

## 产品数据 Feed / Product Feed
> 商品フィード

- **ZH**: 提供给广告/购物引擎的结构化产品数据（标题、图片、价格、描述），如 Google Shopping Feed 与 TikTok GMV Max 产品目录
- **EN**: Structured product data (title, image, price, description) supplied to ad/shopping engines — e.g. the Google Shopping feed and the TikTok GMV Max catalog

## 广告活动 / Campaign
> 広告キャンペーン

- **ZH**: Amazon PPC 广告结构的顶级容器，包含广告组、关键词和预算设置；案例中的 20 个活跃 campaign 即指此层级
- **EN**: Top-level container in the Amazon PPC hierarchy holding ad groups, keywords and budget settings

## 广告组 / Ad Group
> 広告グループ

- **ZH**: Campaign 内的关键词分组单元，用于按匹配类型或关键词主题分组，实现针对性优化
- **EN**: Grouping unit inside a campaign that holds keywords; split by match type or theme for targeted optimization

## 匹配类型 / Match Type
> マッチタイプ

- **ZH**: 关键词与搜索词的匹配规则：Broad（广泛，探索性）、Phrase（词组，中间）、Exact（精确，精准流量）；匹配类型不同应分层分析
- **EN**: Rule linking a keyword to search terms: broad (exploratory), phrase (intermediate), exact (precise); performance must be analyzed separately per match type

## 出价 / Bid
> 入札額

- **ZH**: 广告主愿意为每次点击支付的最高金额；广告排名 = 出价 × 相关性 × 转化率
- **EN**: Maximum amount an advertiser is willing to pay per click; ad rank = bid × relevance × conversion rate

## 预算 / Budget
> 予算

- **ZH**: 广告活动（Campaign）的日预算或月预算；预算跟着 ROAS 走，但需考虑广告战略目标
- **EN**: Daily or monthly budget of a campaign; allocation should follow ROAS while respecting strategic goals

## 展示量 / Impression
> インプレッション

- **ZH**: 广告被展示的次数；高展示零点击说明主图或价格可能有问题
- **EN**: Number of times an ad is displayed; high impressions with zero clicks suggests a listing image or price problem

## 点击量 / Click
> クリック数

- **ZH**: 广告被点击的次数；CPC = 广告花费 ÷ 点击数
- **EN**: Number of times an ad is clicked; CPC = ad spend / clicks

## 转化 / Conversion
> コンバージョン

- **ZH**: 广告点击后产生的订单；CVR = 订单数 ÷ 点击数 × 100%
- **EN**: Orders generated from ad clicks; CVR = orders / clicks × 100%

## 点击率 / CTR

- **ZH**: CTR = 点击数 ÷ 展示量 × 100%；快速参考健康值 >0.3%
- **EN**: CTR = clicks / impressions × 100%; healthy reference threshold >0.3%

## 每次点击成本 / CPC

- **ZH**: 每次点击实际支付的费用；Amazon 采用第二价格拍卖，实际 CPC = 第二高出价 + $0.01
- **EN**: Actual cost per click; Amazon uses a second-price auction, so actual CPC = second-highest bid + $0.01

## 广告销售成本率 / ACOS

- **ZH**: ACOS = 广告花费 ÷ 广告销售额 × 100%；目标 ACOS < 产品利润率，盈亏平衡 ACOS = 利润率
- **EN**: ACOS = ad spend / ad sales × 100%; target ACOS below product margin; break-even ACOS equals margin

## 总广告销售成本率 / TACOS

- **ZH**: TACOS = 广告花费 ÷ 总销售额（广告+自然）× 100%；TACOS 持续下降 = 飞轮效应在运转，广告依赖减少
- **EN**: TACOS = ad spend / total sales (ads + organic) × 100%; a falling TACOS means the organic-rank flywheel is working

## 广告支出回报率 / ROAS

- **ZH**: ROAS = 广告销售额 ÷ 广告花费；ROAS = 1 / ACOS
- **EN**: ROAS = ad sales / ad spend; ROAS = 1 / ACOS

## 转化率 / CVR

- **ZH**: CVR = 订单数 ÷ 点击数 × 100%；快速参考健康值 >8%
- **EN**: CVR = orders / clicks × 100%; healthy reference threshold >8%

## 商品推广 / Sponsored Products (SP)
> スポンサープロダクト

- **ZH**: 展示在搜索结果页和产品详情页的 CPC 广告，无最低预算，适合所有阶段（必备），核心目标是直接转化和关键词排名
- **EN**: CPC ads shown on search results and product detail pages; no minimum budget; suitable for all stages; goal is direct conversion and keyword ranking

## 品牌推广 / Sponsored Brands (SB)
> スポンサーブランド

- **ZH**: 展示在搜索结果顶部横幅的 CPC 广告，需要品牌注册，最低预算 $1/天，核心目标是品牌曝光和品类占位；Headline 限 50 字符
- **EN**: CPC ads shown as a banner at the top of search results; requires brand registry, $1/day minimum budget; goal is brand exposure; headline limited to 50 characters

## 展示型推广 / Sponsored Display (SD)
> スポンサーディスプレイ

- **ZH**: 展示在产品详情页和站外的 CPC/vCPM 广告，需要品牌注册，最低预算 $1/天，核心目标是再营销和竞品拦截
- **EN**: CPC/vCPM ads shown on product detail pages and off-Amazon; requires brand registry, $1/day minimum; goals are retargeting and competitor interception

## Amazon DSP / Amazon DSP

- **ZH**: 按 CPM（展示）计价的站内外全渠道展示广告，通常最低 $10,000+/月，适合大卖家和品牌
- **EN**: CPM-based full-funnel display advertising across on- and off-Amazon; typically $10,000+/month minimum; for big sellers and brands

## 搜索词报告 / Search Term Report
> 検索語レポート

- **ZH**: 从 Advertising Console 导出的报告（Advertising → Reports → Search Term Report），每行含搜索词、匹配类型、展示量、点击量、花费、订单数、销售额；是广告优化最重要的数据源
- **EN**: Report exported from the Advertising Console (Advertising → Reports → Search Term Report) with search term, match type, impressions, clicks, spend, orders, sales per row; the most important data source for ad optimization

## 否定关键词 / Negative Keyword
> 否定キーワード

- **ZH**: 屏蔽不相关搜索词的设置，分精确否定（Negative Exact，仅屏蔽完全匹配搜索词）和短语否定（Negative Phrase，屏蔽包含该短语的所有搜索词）；可设在 campaign 级
- **EN**: Setting that blocks irrelevant search terms; two types — negative exact (blocks only the exact search term) and negative phrase (blocks every search term containing the phrase); applied at campaign level

## 广告创意 / Ad Creative
> 広告クリエイティブ

- **ZH**: 广告文案与素材，如 Sponsored Brands Headline（限 50 字符）和 SB Video 15 秒脚本；用于 A/B 测试的变体
- **EN**: Ad copy and assets such as Sponsored Brands headlines (max 50 characters) and 15-second SB Video scripts; variants are A/B tested

## ASIN 定向 / ASIN Targeting (Product Targeting)
> ASIN ターゲティング

- **ZH**: 把广告投放到指定竞品 ASIN 的产品详情页（Product Targeting）；需分析目标 ASIN 的展示量、点击量、花费、订单数
- **EN**: Targeting competitor ASINs so your ad appears on their product detail pages (Product Targeting); performance is analyzed by target ASIN impressions, clicks, spend, orders

## 库存 / Inventory
> 在庫

- **ZH**: 电商卖家的商品存量，管理的本质是平衡缺货成本与滞销成本
- **EN**: Stock of goods held by an e-commerce seller; management balances stockout cost vs. stagnation cost

## 仓库 / Warehouse
> 倉庫

- **ZH**: 库存存放地点，含 FBA 仓库、自建仓、3PL 仓；多渠道场景下由库存中心系统(总库存池)统一协调
- **EN**: Physical location holding inventory (FBA warehouse, own warehouse, 3PL); multi-channel setups use a central inventory pool

## FBA 库存 / FBA Inventory
> FBA在庫

- **ZH**: 存放在 Amazon 履约中心、由 FBA 发货的库存，受 IPI 评分与仓储限制约束
- **EN**: Inventory stored in Amazon fulfillment centers and fulfilled by FBA; subject to IPI score and storage limits

## 自发货库存 / FBM Inventory
> 自己発送在庫

- **ZH**: 卖家自行履约（自发货）的库存，如 Shopify / 独立站渠道库存
- **EN**: Inventory fulfilled by the seller (self-fulfillment), e.g. Shopify / DTC store stock

## 库存水位 / Stock Level
> 在庫水準

- **ZH**: 某一时刻的库存数量，补货决策的输入变量之一（当前库存 / 在途库存 / 目标水位）
- **EN**: Quantity of stock at a point in time; an input to replenishment decisions (current / in-transit / target)

## 安全库存 / Safety Stock
> 安全在庫

- **ZH**: 为吸收销量波动与 Lead Time 波动而额外持有的库存，按 Z × σ_d × √L 计算
- **EN**: Extra stock held to absorb demand and lead-time variability, computed as Z × σ_d × √L

## 补货点 / Reorder Point
> 発注点

- **ZH**: 库存降到该水位时应下单补货；= 日均销量 × Lead Time + 安全库存
- **EN**: Stock level at which a replenishment order should be placed; = daily sales × lead time + safety stock

## 交期 / Lead Time
> リードタイム

- **ZH**: 从下单到入仓可售的天数，含供应商生产、国内运输、海运、清关、FBA 入仓；是库存管理最大的不确定性来源
- **EN**: Days from order placement to sellable stock, covering production, domestic transport, sea freight, customs, FBA inbound; the largest uncertainty in inventory management

## 供应商 / Supplier
> サプライヤー

- **ZH**: 商品生产/供货方，需评估交期可靠性、产能、MOQ，并建立备选供应商
- **EN**: Party producing/supplying goods; assessed on delivery reliability, capacity, MOQ; backup suppliers recommended

## 采购订单 / Purchase Order
> 発注書

- **ZH**: 向供应商下达的采购单据，记录供应商、数量、预计交期，并纳入在途库存追踪
- **EN**: Order issued to a supplier recording vendor, quantity and expected delivery; tracked as in-transit inventory

## 履约中心 / Fulfillment Center
> フルフィルメントセンター

- **ZH**: Amazon FBA 仓库，货物到港后需经 5-14 天（旺季可达 21 天）入仓处理方可销售
- **EN**: Amazon FBA warehouse; inbound processing takes 5-14 days (up to 21 in peak season) before units become sellable

## 头程物流 / Shipment
> 貨物輸送

- **ZH**: 从供应商到 FBA 仓库的头程货运，可选海运(30-45天)、空运(7-12天)、铁路(18-25天)
- **EN**: First-leg freight from supplier to FBA warehouse: sea (30-45d), air (7-12d), rail (18-25d)

## 补货建议 / Restock Recommendation
> 補充推奨

- **ZH**: AI 或工具基于销量、Lead Time、安全库存、仓储限制等输出的补货数量/时间建议，需人工复核后转采购订单
- **EN**: Suggested replenishment quantity/timing produced by AI or tools from sales, lead time, safety stock and storage limits; requires human review before ordering

## 需求预测 / Demand Forecast
> 需要予測

- **ZH**: 基于历史销量、季节性、趋势与节假日事件对未来的销量预测，输出点估计与置信区间
- **EN**: Future sales prediction from historical sales, seasonality, trend and holiday events, with point estimate and confidence intervals

## IPI 评分 / IPI Score
> IPIスコア

- **ZH**: Inventory Performance Index，综合库存健康评分，低于 400 会被限制 FBA 入仓数量
- **EN**: Inventory Performance Index; scores below 400 trigger FBA inbound quantity limits

## 售出率 / Sell-through Rate
> 消化率

- **ZH**: 过去 90 天销量 ÷ 平均库存，目标 > 3（90 天内周转 3 次），IPI 核心组成部分
- **EN**: 90-day sales ÷ average inventory; target > 3 (3 turns in 90 days); core IPI component

## 超量库存 / Excess Inventory
> 過剰在庫

- **ZH**: 超过 90 天预计销量的库存，占用仓储空间并产生额外费用，拉低 IPI
- **EN**: Inventory exceeding 90 days of forecast sales; consumes storage, adds fees, lowers IPI

## 滞留库存 / Stranded Inventory
> 滞留在庫

- **ZH**: 有库存但因 Listing 问题无法销售的 ASIN，目标为 0，是最易修复的 IPI 维度
- **EN**: ASINs with stock that cannot be sold due to listing issues; target 0; the easiest IPI fix

## 有货率 / In-stock Rate
> 在庫充足率

- **ZH**: 有库存的天数 ÷ 总天数，目标 > 95%，影响 BSR 排名与广告效果
- **EN**: Days in stock ÷ total days; target > 95%; affects BSR ranking and ad performance

## 库龄库存 / Aged Inventory
> 長期滞留在庫

- **ZH**: 库龄超过 90/180/270/365 天的库存，超 181 天开始产生 Aged Inventory Surcharge
- **EN**: Inventory aged over 90/180/270/365 days; aged-inventory surcharge starts after 181 days

## 在途库存 / In-transit Inventory
> 輸送中在庫

- **ZH**: 已下单/已发货但未入仓的库存，实际可用库存 = 当前库存 + 在途库存
- **EN**: Ordered/shipped but not yet received stock; available stock = current stock + in-transit

## 库存可支撑天数 / Days of Stock
> 在庫持続日数

- **ZH**: (当前库存 + 在途库存) ÷ 日均销量，低于 Lead Time + 安全天数时需要补货
- **EN**: (current stock + in-transit) ÷ daily sales; below lead time + safety days, replenish

## 最小起订量 / MOQ
> 最小発注数量

- **ZH**: 供应商要求的最小起订量，补货量需向上取整到 MOQ 的倍数
- **EN**: Supplier's minimum order quantity; order quantity is rounded up to a multiple of MOQ

## 库存周转率 / Inventory Turnover
> 在庫回転率

- **ZH**: 年销售额 ÷ 平均库存价值，越高说明库存流转越快
- **EN**: Annual sales ÷ average inventory value; higher means faster stock turnover

## 合规检查 / Compliance Check
> コンプライアンス確認

- **ZH**: 新品上架前及运营中按清单逐项核对认证、标签、包装、化学物质、税务等合规项的检查流程，产出合规需求清单与通过/未通过结论
- **EN**: Pre-launch and ongoing verification of certifications, labels, packaging, chemicals and tax obligations against a checklist; gates listing publication

## 认证证书 / Certification
> 認証

- **ZH**: 由认证机构（SGS、TÜV、Intertek 等）颁发的合规证书，具有有效期（通常 1-5 年），过期或产品改版后失效
- **EN**: Compliance certificate issued by accredited bodies (SGS, TÜV, Intertek); has validity period, invalidated by expiry or design change

## 知识产权 / IP Right
> 知的財産権

- **ZH**: 知识产权总称，含专利、商标、版权等；属地主权（美国注册在欧盟不生效），是跨境卖家最大的法律风险来源之一
- **EN**: Umbrella term for patents, trademarks, copyrights; territorial rights, major legal risk for cross-border sellers

## 商标 / Trademark
> 商標

- **ZH**: 按国家/地区注册的商标权，是 Amazon Brand Registry 的前提；抢注是跨境电商常见陷阱
- **EN**: Jurisdiction-registered trademark; prerequisite for Amazon Brand Registry; squatting is a common trap

## 专利 / Patent
> 特許

- **ZH**: 专利（发明专利/实用新型/外观设计）；侵权判断看功能与外观而非名称，外观设计专利侵权门槛低
- **EN**: Patent (utility/design); infringement judged by function and appearance, not product name; design patents have a low infringement bar

## 版权 / Copyright
> 著作権

- **ZH**: 版权，覆盖产品图片、Listing 文案、品牌设计、视频等内容作品；侵权后果为 DMCA 投诉与 Listing 下架
- **EN**: Copyright over product images, listing copy, brand design, videos; infringement leads to DMCA takedowns

## 海关编码 / HS Code
> HSコード

- **ZH**: 海关协调制度编码，跨境清关的商品分类代码；错误分类可能导致海关罚款和延误，是少数值得自动化的合规环节
- **EN**: Harmonized System customs classification code; misclassification risks fines and delays

## 品类准入审批 / Product Category Approval
> カテゴリー承認

- **ZH**: 平台/市场对特定品类的准入控制；Amazon 要求上架前在 Seller Central 确认品类具体合规要求（如儿童产品、医疗器械、锂电池）
- **EN**: Marketplace gating for a product category; Amazon requires confirming category-specific compliance in Seller Central before listing

## FDA 要求 / FDA Requirement
> FDA要件

- **ZH**: 美国 FDA 要求，如食品接触材料适用 FDA 21 CFR；未经实际 FDA 批准不得在 Listing 宣称 "FDA approved"
- **EN**: US FDA requirements (e.g., FDA 21 CFR for food-contact materials); unapproved "FDA approved" claims are forbidden in listings

## FCC 要求 / FCC Requirement
> FCC要件

- **ZH**: 美国 FCC 认证（Part 15），所有发射无线电频率的电子设备强制要求；无认证海关可直接扣货
- **EN**: US FCC certification (Part 15), mandatory for all RF-emitting electronics; customs may seize uncertified goods

## CE 标志 / CE Marking
> CEマーク

- **ZH**: 进入欧盟市场的强制标志，覆盖安全、健康、环保等多指令（EMC、LVD、玩具安全等）；有最小尺寸与比例要求
- **EN**: Mandatory EU market access mark covering multiple directives (EMC, LVD, Toy Safety); has minimum size and proportion rules

## 危险品 / Dangerous Goods
> 危険物

- **ZH**: 危险品（如含锂电池产品），需满足 UN38.3 测试、MSDS 与运输限制等特殊要求
- **EN**: Dangerous goods (e.g., lithium-battery products) subject to UN38.3 testing, MSDS and transport restrictions

## 受限产品 / Restricted Product
> 販売制限品

- **ZH**: 缺少对应市场强制认证（CE/FCC/PSE/UKCA）即无法合法销售的产品；儿童产品、医疗器械等品类认证费用可占产品成本 20-30%
- **EN**: Product that cannot be legally sold without mandatory certification for the target market; certain categories have high certification cost share

## 标签要求 / Label Requirement
> ラベル要件

- **ZH**: 目标市场对产品标签的要求：当地官方语言、制造商/进口商信息、原产地标注、CE 标志尺寸、Prop 65 警告、回收标志等
- **EN**: Market-specific labeling rules: local language, manufacturer/importer info, country of origin, CE mark size, Prop 65 warning, recycling marks

## 安全数据表 / Safety Data Sheet
> 安全データシート

- **ZH**: 危险品（含锂电池产品）运输与申报所需的 MSDS/SDS，是锂电池特殊要求（UN38.3、MSDS、运输限制）之一
- **EN**: MSDS/SDS required for dangerous-goods shipping and declaration (UN38.3, MSDS, transport restrictions)

## 欧盟责任主体 / EU Responsible Person
> EU責任者

- **ZH**: 欧盟境内经济运营者（进口商、授权代表或履行服务提供商），GPSR 强制要求；中国卖家必须指定，Amazon 可能要求提供后才能上架
- **EN**: EU economic operator (importer, authorized representative or fulfillment provider) mandated by GPSR; required for Chinese sellers

## 符合性声明 / Declaration of Conformity
> 適合宣言書

- **ZH**: 欧盟符合性声明，需引用适用指令（LVD、EMC、RoHS、RED）与协调标准；属法律文件，签署人对准确性负法律责任
- **EN**: EU Declaration of Conformity citing applicable directives (LVD, EMC, RoHS, RED) and harmonized standards; legally binding for signatory

## 亚马逊品牌注册 / Amazon Brand Registry
> Amazonブランドレジストリ

- **ZH**: Amazon 品牌保护体系，需已注册商标；配套 Transparency、Project Zero（AI 自动移除仿冒）、Report a Violation 等工具
- **EN**: Amazon brand protection program requiring a registered trademark; unlocks Transparency, Project Zero and Report a Violation

## Buy Box / Buy Box

- **ZH**: 亚马逊购物车，每个 ASIN 只有一个卖家获得。赢得 Buy Box 是成交的前提。
- **EN**: The Amazon Buy Box — the add-to-cart box on a product detail page. Only one seller wins it per ASIN.

## 评分 / Rating
> 評価

- **ZH**: 产品星级评分（1-5星），直接影响搜索排名和转化率。
- **EN**: Product star rating (1-5), directly affects search ranking and conversion.

## BSR（畅销排名） / Best Sellers Rank
> ベストセラーランク

- **ZH**: Amazon 畅销排名，每小时更新，数字越小销量越高。
- **EN**: Amazon Best Sellers Rank, updated hourly. Lower number = higher sales.

## Amazon Prime / Amazon Prime

- **ZH**: Amazon 会员体系，Prime 商品有 Prime 标识，影响 Buy Box 权重和转化率。
- **EN**: Amazon Prime membership. Prime-eligible products get a Prime badge, affecting Buy Box weight and conversion.

## LTV（客户生命周期价值） / LTV (Lifetime Value)
> LTV（顧客生涯価値）

- **ZH**: 一个客户从第一次购买到最后一次购买的总价值。LTV/CAC 比是核心盈利指标。
- **EN**: Total value of a customer from first to last purchase. LTV/CAC ratio is a core profitability metric.

## 促销活动 / Deal/Promotion
> プロモーション

- **ZH**: Amazon 限时促销活动（Lightning Deal、7-Day Deal、Coupon），影响曝光和转化。
- **EN**: Amazon time-limited promotions (Lightning Deal, 7-Day Deal, Coupon). Affects visibility and conversion.

## 品牌旗舰店 / Storefront
> ストアフロント

- **ZH**: Amazon 品牌旗舰店页面（Amazon Store），品牌注册后可用。
- **EN**: Amazon Store / Storefront page, available after Brand Registry.

## Seller Central / Seller Central
> セラーセントラル

- **ZH**: Amazon 卖家后台管理系统，所有运营操作和数据分析的入口。
- **EN**: Amazon seller backend management system — entry point for all operations and data analysis.

## IPI（库存绩效指数） / IPI (Inventory Performance Index)
> IPI（在庫パフォーマンス指数）

- **ZH**: Amazon FBA 库存绩效指数（0-1000），低于阈值（通常 400-500）会限制仓储容量。
- **EN**: Amazon FBA Inventory Performance Index (0-1000). Below threshold (typically 400-500) restricts storage capacity.

## CAC（客户获取成本） / CAC (Customer Acquisition Cost)
> CAC（顧客獲得コスト）

- **ZH**: 获取一个新客户的平均营销费用。CAC = 总营销支出 / 新客户数。
- **EN**: Average marketing spend to acquire a new customer. CAC = Total Marketing Spend / New Customers.

## WFS（Walmart 仓储配送） / WFS (Walmart Fulfillment Services)
> WFS

- **ZH**: Walmart 的仓储配送服务，类似 Amazon FBA。使用 WFS 的商品有 Buy Box 优势。
- **EN**: Walmart fulfillment service, similar to Amazon FBA. WFS products have Buy Box advantage.

## 黑五网一 / Black Friday / Cyber Monday
> ブラックフライデー / サイバーマンデー

- **ZH**: 黑色星期五 + 网络星期一，全年最大促销期。
- **EN**: Black Friday + Cyber Monday — the year's biggest promotional period.

## CPM（千次展示成本） / CPM (Cost Per Mille)
> CPM（1000インプレッション単価）

- **ZH**: 每千次展示的广告成本，品牌广告和 DSP 广告的核心指标。
- **EN**: Advertising cost per thousand impressions. Core metric for brand ads and DSP.

## 货到付款 / Cash on Delivery
> 代金引換

- **ZH**: 配送后当面付款，东南亚和中东市场的主要支付方式。
- **EN**: Payment on delivery. Primary payment method in Southeast Asia and Middle East markets.

