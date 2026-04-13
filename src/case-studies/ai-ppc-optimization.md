# 案例：AI 广告优化 — ACOS 从 35% 降到 18%

> Domain: 流量与获客 · 关联模块: [A3 广告优化](../a-operators/a3-advertising.md)

---

## 背景

一个家居品类卖家，Amazon US 单站点，月广告预算 $15,000，20 个活跃 campaign。ACOS 长期在 30-35% 徘徊，TACOS 12%。团队每周花 3-4 小时手动调整出价和否定词，但效果不稳定。

核心问题：
- 搜索词报告每周 2000+ 行，人工分析只能看 Top 100
- 出价调整靠"感觉"，没有系统化的决策框架
- 浪费性支出（高点击零转化的词）占总支出 25%+
- 新品 launch 阶段 ACOS 经常飙到 60%+

## SOP：AI 广告优化周循环

### 每周一：搜索词报告 AI 分析（30 分钟）

从 Seller Central 下载过去 7 天的搜索词报告，喂给 AI：

```
你是 Amazon PPC 数据分析专家。以下是我的搜索词报告数据（过去 7 天）：
[粘贴 CSV 数据或关键列：搜索词、展示量、点击量、花费、销售额、订单数]

请按以下四象限分类：
1. 明星词（高转化 + 高销售）：ACOS < 20%，订单 >= 2
2. 潜力词（有转化但量小）：ACOS < 30%，订单 = 1
3. 观察词（高展示低转化）：点击 >= 10，订单 = 0
4. 浪费词（纯烧钱）：花费 > $10，订单 = 0

对每个分类给出具体操作建议：
- 明星词：建议出价范围和匹配类型
- 潜力词：是否值得提高出价测试
- 观察词：是否加为否定词或降低出价
- 浪费词：立即否定的词列表

输出为表格，按花费降序排列。
```

### 每周二：执行否定词和出价调整（20 分钟）

根据 AI 分析结果：
1. 把"浪费词"加入 campaign 级否定精确匹配
2. 把"明星词"从自动 campaign 提取到手动 campaign（精确匹配）
3. 调整"潜力词"出价（+15-20%，观察一周）
4. 对"观察词"降低出价（-20%）或暂停

### 每周五：竞品广告策略分析（15 分钟）

```
我在 Amazon US 卖 [品类]，以下是我的 Top 3 竞品 ASIN：
[ASIN 列表]

请分析：
1. 他们的 Sponsored Products 广告出现在哪些关键词下（我搜索时看到的）
2. 他们是否在用 Sponsored Brands 和 Sponsored Display
3. 他们的定价策略（是否在用 coupon/deal 配合广告）
4. 我应该在哪些关键词上与他们竞争，哪些应该避开

注意：我的产品售价 $[价格]，他们的售价分别是 $[价格列表]
```

### 每月一次：广告结构健康度诊断（30 分钟）

```
以下是我所有 campaign 的月度汇总数据：
[粘贴 campaign 名称、类型、预算、花费、销售额、ACOS、展示量]

请诊断：
1. 哪些 campaign 的 ACOS 异常高？可能原因是什么？
2. 预算分配是否合理？（高 ROAS campaign 是否预算不足）
3. 是否有 campaign 之间的关键词重叠（自我竞争）
4. 新品 campaign 和成熟品 campaign 的策略是否应该不同
5. 给出下个月的预算重新分配建议
```

## 结果（3 个月后）

| 指标 | Month 0 | Month 1 | Month 2 | Month 3 |
|------|---------|---------|---------|---------|
| ACOS | 35% | 28% | 22% | 18% |
| TACOS | 12% | 10% | 8.5% | 7% |
| 月广告花费 | $15,000 | $14,200 | $13,500 | $12,800 |
| 月广告销售额 | $42,857 | $50,714 | $61,364 | $71,111 |
| 浪费性支出占比 | 25% | 15% | 8% | 5% |
| 否定词数量 | 50 | 180 | 320 | 450 |
| 每周优化时间 | 3-4 小时 | 1.5 小时 | 1 小时 | 1 小时 |

关键变化：ACOS 降了 17 个百分点，但广告销售额反而增长了 66%。核心原因是把浪费性支出（$3,750/月）重新分配给了高转化关键词。

## Tips

1. 否定词是最被低估的优化手段 — 行业数据显示，管理 50+ 品牌的 PPC 专家认为大部分 ACOS 问题的根源是广告展示在不该展示的地方，而不是出价问题（[来源](https://gigabrands.ai/blog/lower-acos-negative-targeting)，content rephrased）
2. 不要只看 ACOS，要看 TACOS — ACOS 只衡量广告效率，TACOS（广告花费/总销售额）才能反映广告对整体业务的贡献
3. 新品前 30 天不要追求低 ACOS — 新品阶段的目标是数据积累和关键词排名，ACOS 60% 是正常的
4. AI 分析搜索词报告的核心价值是"发现人眼看不到的模式" — 2000 行数据里的长尾词组合，人工很难发现
5. 行业平均 ACOS 约 30%（[来源](https://keywords.am/blog/amazon-ppc-optimization/)，content rephrased），如果你的 ACOS 远高于此，先检查否定词和浪费性支出

## 参考来源

- Content was rephrased for compliance with licensing restrictions
- [DeepBI: Amazon PPC Success Stories](https://www.deepbi.com/case/) — AI-driven ACOS reduction from 14% to 3%
- [GigaBrands: Lower ACOS with Negative Targeting](https://gigabrands.ai/blog/lower-acos-negative-targeting) — Negative targeting methodology
- [Keywords.am: Best Amazon PPC Optimization Strategy](https://keywords.am/blog/amazon-ppc-optimization/) — Industry ACOS benchmarks
- [Influencer Marketing Hub: Amazon PPC Campaign Structure 2026](https://influencermarketinghub.com/amazon-ppc-campaign-structure/) — Campaign restructuring results
