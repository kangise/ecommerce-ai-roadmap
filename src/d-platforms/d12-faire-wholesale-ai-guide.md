# D12. Faire 批发电商 AI 指南

> **路径**: Path D: 多平台 · **模块**: D12
> **最后更新**: 2026-03-14
> **难度**: 入门
> **预计时间**: 45 分钟


---

> GMV ~$3B（2025），收入 $500M+（+40% YoY），700K+ 零售商。B2B 批发平台，连接品牌与独立零售商。与 B2C 电商完全不同的商业模式。

## 1. Faire 商业模式

### 1.1 Faire vs B2C 平台

| 维度 | Faire（B2B 批发） | Amazon（B2C 零售） |
|------|-------------------|-------------------|
| 买家 | 独立零售商/精品店 | 终端消费者 |
| 订单量 | 批量（MOQ） | 单件 |
| 定价 | 批发价（零售价的 40-50%） | 零售价 |
| 关系 | 长期合作 | 一次性交易 |
| 佣金 | 15%（新客户）/ 0%（回头客） | 8-15% |
| 退货 | 60 天免费退货（Faire 承担） | 30 天 |

### 1.2 适合 Faire 的产品

- 有品牌故事的产品（独立零售商看重品牌）
- 设计感强的产品（家居、礼品、美妆、食品）
- 有一定利润空间的产品（批发价需要是零售价的 40-50%）
- 不适合：纯标品、低价产品、无品牌产品

## 2. AI 应用场景

### 2.1 Faire 算法与排名机制

Faire 的搜索算法决定哪些品牌被零售商看到。以下是基于实操经验的排名因素（[Smoothed.io](https://www.smoothed.io/blog/faire-account-settings-that-drive-sales)）：

```
Faire 搜索排名因素：

1. 账号设置（很多卖家忽略，但影响巨大）
MOQ（最低起订量）：设为 $0 可以出现在所有筛选结果中（3x 曝光）
Lead Time（发货时间）：1-3 天最佳，>14 天会被视为红旗
Collections（合集）：Faire 允许 20 个合集，大部分卖家只用 3-4 个
品牌标签：eco-friendly/women-owned/handmade 等标签是零售商的筛选条件
产品属性：每个字段都要填完整，空字段 = 搜索不到

2. 销售数据
历史订单量
复购率（回头客比例）
评价数量和评分
转化率（浏览→下单）

3. 内容质量
产品图片质量
品牌故事完整度
视频（极少品牌上传视频，上传的会获得额外曝光）
产品描述详细度
```

Content rephrased for compliance with licensing restrictions.

### 2.2 Faire 账号设置优化（高杠杆操作）

基于 [Smoothed.io](https://www.smoothed.io/blog/faire-account-settings-that-drive-sales) 的实操数据，以下设置调整可以显著提升曝光：

**MOQ 设为 $0（最高杠杆）**

Faire 零售商可以按 MOQ 筛选：$0、$100、$200。如果你的 MOQ 设为 $200，你只在零售商选择 $200 筛选时出现。设为 $0 则在所有三个筛选中出现一个设置改变带来 3 倍曝光。

小订单不是问题它们带来评价、训练算法、最终转化为大额复购。

**Lead Time 保持 1-3 天**

零售商被 Amazon 速度训练过了。14 天的 Lead Time 感觉像红旗。超过承诺的 Lead Time 更糟会降低算法排名并产生差评。

> **关键提醒**：永远不要使用 Holiday Mode / Pause Mode。算法会重置，回来后要花数月恢复排名。替代方案：把 Lead Time 延长到 40+ 天，订单会减少但排名不会丢失。

**使用全部 20 个 Collections**

Collections 是 Faire 站内搜索的 SEO。分两类创建：
- 产品导向：Bestsellers、New Arrivals、Summer Essentials、Holiday Gift Sets
- 零售商导向："For Gift Shops"、"For Boutiques"、"For Online Retailers"、"For Spa & Wellness"

每个没创建的 Collection = 一个搜不到你的搜索结果。

**阶梯促销（Always-On）**

| 层级 | 优惠 | 目的 |
|------|------|------|
| 达到平均订单金额 | 免运费 | 推动订单达到目标金额 |
| 更高金额 | 10% off + 免运费 | 推动更大订单 |
| $1000-2000+ | 20% off | 吸引大批量买家 |
| 预售产品 | 5% off | 提前收集订单 |

**运费策略**

把包装和处理费用计入产品价格，不要在结账时加"handling fee"。零售商被训练期望透明定价，结账时的额外费用会杀死转化率。

### 2.3 品牌故事 AI 生成（基于 Faire 最佳实践）

> **相关阅读**: [D1 Shopify](shopify-ai-guide.md) 品牌建设也可参考 D1 Shopify 独立站，DTC 品牌策略和品牌故事方法论可复用。

Faire 官方建议品牌故事聚焦 USP（独特卖点），而不是个人经历。零售商不需要你的创业故事他们需要知道你的产品为什么能在他们的店里卖得好。

```
你是一个 Faire 品牌页面优化专家，精通 B2B 批发电商。

品牌信息：
- 品牌名：[名称]
- 品类：[X]
- 核心 USP：[3 个独特卖点]
- 品牌标签（勾选所有适用的）：
Eco-friendly Women-owned Handmade
Gives back Small batch Made in [国家]
- 目标零售商类型：[精品店/礼品店/家居店/美妆店/在线零售商]

请生成完整的 Faire 品牌页面内容：

1. Brand Story（200-300 字）
- 聚焦 USP，不是个人故事
- 回答零售商最关心的问题："为什么我的顾客会买这个？"
- 包含具体数据（如果有）：复购率、平均评分、获奖信息
- 语气：专业但有温度，像在 Trade Show 上面对面介绍

2. 产品描述模板（面向零售商，不是消费者）
- 零售卖点："这个产品在店里好卖的 3 个理由"
- 建议零售价和利润空间（"Wholesale $X → Retail $X = XX% margin"）
- 陈列建议（"放在收银台旁边 / 与 XX 品类搭配展示"）
- 目标消费者画像（帮零售商理解谁会买）

3. 20 个 Collections 建议
- 10 个产品导向 Collections（名称+描述）
- 10 个零售商导向 Collections（名称+描述）

4. 视频脚本（30-60 秒，虚拟 Trade Show Pitch）
- 开头：品牌介绍（5 秒）
- 中间：产品展示+USP（20-40 秒）
- 结尾：为什么零售商应该进货（10 秒）
```

### 2.4 Faire Ads（Promoted Listings）

Faire 的广告系统是 CPC 模式。基于实操数据（[Smoothed.io](https://www.smoothed.io/blog/faire-account-settings-that-drive-sales)）：$570 广告花费产生 $1,979 首单销售额（3.5x ROAS），且不包含这些零售商的后续复购。

```
Faire Ads 最佳实践：

1. 预算设置
设置高于预期的月预算（Faire 广告库存有限，不会全花完）
从 $200-500/月 开始测试
3-4 个月内逐步增加
不要一开始就设 $20000先确认转化漏斗没问题

2. 优化顺序
先优化产品图片和描述（广告把流量带来，但转化靠内容）
再优化定价和 MOQ（确保零售商愿意下单）
最后增加广告预算
如果 ROAS < 2x，先修内容再加预算

3. 效果追踪
首单 ROAS（广告直接带来的销售）
复购 ROAS（首单客户的后续复购，0% 佣金）
混合 ROAS（首单+复购的综合回报）
目标：首单 ROAS > 3x，混合 ROAS > 5x
```

Content rephrased for compliance with licensing restrictions.

### 2.5 批发定价深度策略

> **相关阅读**: [A1 选品与市场调研](../a-operators/a1-product-research.md) 选品和定价方法论参考 A1，市场调研框架可帮助确定批发定价策略。

Faire 的费用结构（[B2Bridge](https://b2bridge.io/blog/faire-wholesale-pricing/)）：

| 费用项 | 金额 | 说明 |
|--------|------|------|
| 新客户佣金 | 15% | Faire 算法带来的新零售商 |
| 回头客佣金 | 0% | 零售商直接复购（通过 Faire 平台） |
| Faire Direct 佣金 | 0% | 你自己带来的零售商（通过你的专属链接） |
| 新客户一次性费用 | $10 | 每个新零售商首单 |
| 支付处理费 | 包含在佣金中 | 无额外费用 |

> **关键策略：Faire Direct**。如果你有自己的零售商客户（Trade Show 认识的、自己开发的），通过 Faire Direct 链接让他们在 Faire 上下单，佣金为 0%。这是 Faire 最被低估的功能。

```
你是一个 B2B 批发定价专家，精通 Faire 平台。

我的产品：
- 产品名：[名称]
- 单位成本（COGS）：$[X]
- 当前零售价（Amazon/Shopify）：$[X]
- 品类：[X]
- 预估月销量（Faire）：[X] 单

请设计完整的 Faire 定价方案：

1. 批发价计算
- 标准 Keystone：批发价 = 零售价 × 40-50%
- 考虑 Faire 15% 佣金后的实际利润
- 考虑 Faire Direct（0% 佣金）的混合利润

2. 阶梯定价
- Tier 1（1-11 件）：$[X]/件
- Tier 2（12-47 件）：$[X]/件（-5%）
- Tier 3（48+ 件）：$[X]/件（-10%）
- 每个 Tier 的利润率计算

3. 首单优惠策略
- 新零售商首单 10% off（降低试单门槛）
- 免运费门槛设置
- 预售折扣（5% off）

4. 利润模型
- 场景 A：100% 新客户（15% 佣金）
- 场景 B：50% 新客户 + 50% 回头客
- 场景 C：30% 新客户 + 50% 回头客 + 20% Faire Direct
- 每个场景的混合利润率

5. MAP（最低广告价格）策略
- 是否需要设置 MAP 保护零售商利润
- 如何在 Faire 上执行 MAP 政策
```

### 2.6 零售商关系管理（Faire 的核心竞争力）

Faire 的商业模式核心：新客户 15% 佣金，回头客 0% 佣金。这意味着你的长期利润取决于复购率。

```
你是一个 B2B 客户关系管理专家，精通 Faire 平台。

我在 Faire 上有 [X] 个零售商客户。
平均首单金额：$[X]
当前复购率：[X]%
目标复购率：[X]%

请设计零售商关系管理方案：

1. 新客户 Onboarding（首单后 7 天内）
- Day 1：感谢邮件（包含品牌故事+使用建议）
- Day 3：确认收货+满意度调查
- Day 7：陈列建议+销售 Tips

2. 复购激励（首单后 30-90 天）
- Day 30：新品预览（提前通知老客户）
- Day 60：独家折扣（回头客专属）
- Day 90：如果未复购，发送"我们想念你"邮件+特别优惠

3. 季节性沟通
- 每季度：季节性产品推荐
- Trade Show 前：Market Season 特别优惠
- 节日前 8 周：节日产品预售

4. VIP 客户管理（Top 20% 客户）
- 新品首发权
- 独家折扣
- 个性化推荐
- 定期 1:1 沟通

5. 流失预警
- 超过 [X] 天未复购 → 自动触发挽回邮件
- 连续 2 次未复购 → 人工跟进
- 提供"回归优惠"（15-20% off）
```

## 3. Faire 战略分析与 AI 应用

> **真实案例：Faire 的商业策略**
> Faire 的核心策略是"从极度狭窄开始，然后用数据扩展"。平台构建的是采购层（sourcing layer）而非销售层，嵌入式金融（Net 60 付款条件）是粘合剂而非产品本身（[Faster Than Normal](https://fasterthannormal.co/businesses/faire)）。这意味着在 Faire 上成功的关键是理解零售商的采购心理，而非消费者的购买心理。

Content rephrased for compliance with licensing restrictions.

### 3.1 Faire 上的 AI 应用场景

| 场景 | AI 应用 | 工具 |
|------|---------|------|
| 品牌故事 | AI 生成打动零售商的品牌叙事 | ChatGPT/Claude |
| 产品描述 | AI 生成 B2B 风格的产品描述（强调利润空间和陈列效果） | ChatGPT/Claude |
| 定价策略 | AI 计算批发价/建议零售价/利润空间 | ChatGPT + Excel |
| 零售商沟通 | AI 生成个性化的零售商邀约和跟进邮件 | ChatGPT/Claude |
| 产品图片 | AI 生成适合批发展示的产品图（含陈列效果图） | Midjourney/DALL-E |
| 市场分析 | AI 分析 Faire 上的品类趋势和竞品 | ChatGPT + Faire 数据 |

### 3.2 B2B vs B2C 文案差异

```
你是一个 B2B 批发文案专家。

以下是我的 B2C（Amazon）产品描述：
[粘贴 Amazon Listing]

请转化为 Faire B2B 批发描述，注意以下差异：

B2C 关注：消费者利益、使用场景、情感诉求
B2B 关注：零售商利润空间、陈列效果、复购率、品牌故事

请生成：
1. Faire 品牌页面描述（强调品牌故事和零售商价值）
2. 产品描述（强调利润空间、陈列建议、目标客群）
3. 给零售商的首次合作邮件模板
4. 批发定价建议（基于零售价的 40-50%）
```

> **真实数据**：2026 年 Marketplace 成功将取决于统一运营、加强产品数据、采用自动化，以及战略性而非机会性地选择平台（[ChannelEngine](https://www.channelengine.com/en/blog/marketplace-strategy-tips-webinar)）。

Content rephrased for compliance with licensing restrictions.

## 4. 完成标志

- [ ] 评估产品是否适合 Faire
- [ ] 完成品牌页面和产品上架
- [ ] 设置批发定价和 MOQ
- [ ] 建立零售商关系管理流程
