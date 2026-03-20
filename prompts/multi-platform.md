# 多平台运营 Prompt 模板

> 来源: [Path D 多平台](../paths/d-platforms/)

---

## 1. Amazon → Walmart Listing 转换

> 来源: [D4 Walmart](../paths/d-platforms/d4-walmart-ai-guide.md)

```
你是一个 Walmart Marketplace Listing 优化专家。

以下是我的 Amazon Listing：
- 标题：[Amazon 标题]
- Bullet Points：[5 点]
- 描述：[描述]
- 价格：$[X]

请转换为 Walmart 格式：
1. Walmart 标题（50-75 字符，Title Case，品牌+产品+核心属性）
2. Key Features（3-10 条，每条 ≤80 字符）
3. 描述（300-500 字，结构化，支持 HTML）
4. 需要填写的产品属性清单
5. Listing Quality Score 优化建议
6. 定价建议（Walmart 用户更价格敏感）
```

---

## 2. Walmart Connect 搜索词报告分析

> 来源: [D4 Walmart](../paths/d-platforms/d4-walmart-ai-guide.md)

```
你是一个 Walmart Connect 广告优化专家。

以下是我的 Walmart 搜索词报告数据（过去 14 天）：
Campaign: [名称]
总花费: $[X]，总点击: [X]，总订单: [X]，ROAS: [X]

搜索词数据（按花费排序 Top 20）：
| 搜索词 | 展示 | 点击 | 花费 | 订单 | 销售额 | ROAS |
[粘贴数据]

请分析（注意 Walmart 第一价格竞价特殊性）：
1. 高 ROAS 词（>4x）：应该提高出价多少？
2. 低 ROAS 词（<2x）：降低出价还是否定？
3. 高展示低点击词：出价问题还是 Listing 问题？
4. 零转化高花费词：立即否定的候选词
5. 新发现的长尾机会词
6. 预算重新分配建议
```

---

## 3. Temu 入驻决策评估

> 来源: [D5 Temu](../paths/d-platforms/d5-temu-seller-guide.md)

```
你是一个跨境电商多平台策略专家。

我的产品详细信息：
- 品类：[X]
- 工厂成本（FOB）：$[X]
- Amazon 售价：$[X]
- Amazon 月销量：[X] 单
- Amazon 利润率：[X]%
- 品牌定位：[高端/中端/性价比]
- 是否有海外仓：[是/否]

请做全面的 Temu 入驻评估：
1. 品类适配度评分（1-10）及理由
2. 全托管 vs 半托管推荐
3. 预估利润率（两种模式分别计算）
4. 对现有 Amazon 业务的影响分析
5. 风险评估（知识产权/价格战/政策变化）
6. 最终建议：入驻/不入驻/观望
```

---

## 4. 东南亚多语言 Listing 本地化

> 来源: [D6 东南亚](../paths/d-platforms/d6-southeast-asia-ai-guide.md)

```
你是一个东南亚电商本地化专家。

以下是我的英文产品 Listing：
- 标题：[英文标题]
- 描述：[英文描述]
- 卖点：[5 个]
- 价格：$[X]

请翻译并本地化为：
1. 印尼语（Bahasa Indonesia）
2. 泰语
3. 越南语

每个版本提供：产品标题、描述（300-500 字）、5 个卖点、10 个搜索关键词。
注意：不是直译，是本地化。货币转换、文化适配、当地搜索习惯。
```

---

## 5. 多平台品类机会分析

> 来源: [平台全景对比](../paths/d-platforms/platform-comparison.md)

```
你是一个跨境电商多平台策略专家。

我的情况：
- 当前平台：Amazon [US/EU/JP]
- 品类：[X]
- 月销量：[X] 单
- 月收入：$[X]
- 品牌注册：[是/否]
- 海外仓：[有/无]
- 团队规模：[X] 人
- 月预算（可用于新平台）：$[X]

请推荐我应该优先进入的 3 个平台，每个给出：
1. 推荐理由
2. 预估投入（时间+资金）
3. 预估回报（3/6/12 个月）
4. 主要风险
5. 第一步行动
```

---

[返回 Hub 首页](../README.md) · [Prompt 模板库](README.md)