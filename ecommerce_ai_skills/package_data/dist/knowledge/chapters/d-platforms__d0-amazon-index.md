# D0. Amazon 运营索引 | Amazon Operations Index

> **路径**: Path D: 多平台 · **模块**: D0
> **最后更新**: 2026-08-08

---

## 为什么没有 Amazon 专章

Amazon 在本库中出现 1600 余次——是第二高频平台（Shopify）的两倍多。但你没有看到 `d0-amazon-ai-guide.md`：**因为 Path A 运营线本身就是 Amazon 线。**

a-operators 的 14 个章节（a1 选品 → a14 Agent 化）以 Amazon 为默认场景构建。Listing 优化、PPC 广告、库存管理、合规风控——每个模块的示例、约束和 Prompt 都以 Amazon 为基准。这不是疏忽，是有意设计：一人公司运营的核心场景就是 Amazon，把运营方法论放在平台无关层反而会稀释它的实操密度。

> **本页是指南，不是正文。** 把 Amazon 内容从 a-operators 抄过来会产生两份不一致的事实源——这正是本库用门禁防止的问题。需要 Amazon 具体知识时，直接跳到对应的 a-operators 章节。

---

## Amazon 运营章节速查

以下是 a-operators 中与 Amazon 运营直接相关的章节：

| 章节 | 内容 | Amazon 相关度 |
|------|------|:--:|
| [A1 选品](../a-operators/a1-product-research.md) | 选品方法论、数据源、AI 辅助筛选 | 高 |
| [A2 Listing 优化](../a-operators/a2-listing-optimization.md) | 标题、五点、描述、Search Terms、图片文案 | 主战场 |
| [A3 广告投放](../a-operators/a3-advertising.md) | PPC 策略、竞价优化、ACOS 诊断 | 主战场 |
| [A4 客服](../a-operators/a4-customer-service.md) | Review 响应、买家消息、纠纷处理 | 高 |
| [A5 库存管理](../a-operators/a5-inventory.md) | FBA 库存预测、补货决策 | 高 |
| [A6 合规](../a-operators/a6-compliance.md) | 类目审核、IP 风险、FDA/FCC | 高 |
| [A7 图片](../a-operators/a7-visual-content.md) | 主图、A+ 内容、品牌故事 | 高 |
| [A8 定价](../a-operators/a8-pricing-strategy.md) | Buy Box 定价、动态调价 | 中 |
| [A9 SEO/GEO](../a-operators/a9-seo-geo.md) | Amazon 搜索排名、AI 搜索引擎优化 | 高 |
| [A10 品牌](../a-operators/a10-brand-building.md) | 品牌注册、Brand Analytics、品牌故事 | 中 |
| [A11 财务](../a-operators/a11-financial-analysis.md) | 利润测算、FBA 费用、退货成本 | 中 |
| [A12 IP 保护](../a-operators/a12-ip-protection.md) | 商标、专利、跟卖监控 | 高 |
| [A13 增长](../a-operators/a13-ai-growth-hack.md) | 市场拓展、类目扩张 | 低 |
| [A14 Agent 化](../a-operators/a14-operations-agent.md) | Amazon 运营的 Agent 模式 | 高 |

## Amazon 特有约束速览

以下约束是 Phase A 从 a-operators 正文中抽取的，这里给出预览。完整约束定义见 `ontology/constraints.yaml`。

| 约束 | 值 | 来源 |
|------|-----|------|
| 标题最大长度 | 200 字符 | a2 §3.1 |
| 前 80 字符含最高搜索量词 | 必须 | a2 §3.1 |
| Bullet Point 最大长度 | 200 字符/条 | a2 §3.1 |
| Search Terms 每行 | ≤250 字节，5 行 | a2 §3.1 |
| 主图要求 | 纯白底、占画面 ≥85%、最短边 ≥1600px | a7 |

## 与其他平台的差异

Amazon 是最「搜索驱动」的平台：流量来源以站内搜索为主，Listing 质量直接决定曝光和转化。这和 Shopify（站外获客）、TikTok Shop（算法推荐）有根本性的运营差异。

| 维度 | Amazon | 对比平台 |
|------|--------|----------|
| 流量来源 | 站内搜索为主 | Shopify: 站外获客 |
| Listing 结构 | 标题+五点+描述+Search Terms | Shopify: 产品页 SEO |
| 广告类型 | PPC Sponsored Products/Brands/Display | Shopify: Google/Facebook/Ins |
| 履约 | FBA 或 FBM | Shopify: 自行履约或 3PL |
| AI 价值高点 | Listing SEO + PPC 优化 | Shopify: 广告 + 邮件 |

详细对比见 → [平台全景对比](platform-comparison.md)

---

## 什么时候这套不管用

Amazon 运营的 AI 方法论在以下场景会失效：

- **品类审核严格**：医疗器械、食品接触材料等需要专业知识而不是 AI 文案技巧
- **Supplier Central / Vendor Central**：B2B 供货模式的规则和 Seller Central 完全不同
- **自配送（FBM）**：物流体验变量多，AI 预测库存的精度低于 FBA 场景
- **新站点冷启动**：日本站、澳洲站等，AI 翻译 ≠ 本地化，文化适配需要人工
