# 选品与市场分析 Prompt 模板 | Product Research Prompts

> 最后更新: 2026-03-10 | 模板数量: 3 | 验证状态: 已验证

---

## 模板 1: 竞品 Review 痛点分析

**场景**: 分析竞品差评，提取产品改进方向和差异化机会
**推荐工具**: ChatGPT / Claude
**验证状态**: 已验证
**贡献者**: [@kangise](https://github.com/kangise)

### Prompt

```
你是一个资深的 Amazon 产品经理。我会给你一组竞品的 1-3 星差评。
请分析这些差评，输出：
1. 排名前5的用户痛点（按提及频率排序）
2. 每个痛点的具体描述和代表性评论原文
3. 针对每个痛点的产品改进建议
4. 这些痛点中，哪些最容易通过产品设计解决

输出格式：用表格呈现，列为：痛点 | 频率 | 代表性评论 | 改进建议 | 难度

[在此粘贴差评内容]
```

### 预期输出示例

### 预期输出示例

> 以下是用 Claude 3.5 Sonnet 对某颈挂风扇竞品 50 条差评运行此 Prompt 的实际输出（节选）：

| 痛点 | 频率 | 代表性评论 | 改进建议 | 难度 |
|------|------|-----------|---------|------|
| 电池续航不足 | 18/50 | "Barely lasts 2 hours on high" | 升级到 4000mAh+ 电池，标注真实续航 | 中 |
| 风力太弱 | 12/50 | "Can barely feel it outdoors" | 优化叶片设计，增加 turbo 档位 | 中 |
| 佩戴不舒适 | 9/50 | "Too heavy, neck hurts after 30min" | 减重至 200g 以下，加硅胶垫 | 低 |
| 噪音大 | 7/50 | "Sounds like a drone in a meeting" | 无刷电机 + 降噪设计 | 高 |
| 充电口脆弱 | 4/50 | "USB-C port broke after 2 months" | 加固充电口，改用磁吸充电 | 高 |

### 使用技巧

- 一次粘贴 50-100 条差评效果最佳，太少则样本不足
- 可以追问"哪个痛点的改进成本最低、效果最明显"来进一步聚焦

---

**分享此模板**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/prompts/product-research.md#模板-1-竞品-review-痛点分析`
**来源**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × 跨境电商实战知识库

---

## 模板 2: 市场可行性快速评估

**场景**: 快速评估一个产品是否值得进入某个市场
**推荐工具**: ChatGPT / Claude / Gemini
**验证状态**: 已验证
**贡献者**: [@kangise](https://github.com/kangise)

### Prompt

```
你是一个跨境电商选品专家。请对以下产品做市场可行性评估：

产品：[产品名称]
目标市场：Amazon [US/DE/JP]

请从以下维度分析，每个维度给出 1-5 分评分：
1. 市场需求（搜索量趋势、品类增长性）
2. 竞争强度（头部卖家集中度、新品进入难度）
3. 利润空间（典型售价、预估成本结构）
4. 供应链难度（供应商可得性、品控要求）
5. 合规风险（认证要求、专利风险）

最后给出综合建议：进入 / 谨慎 / 放弃，并说明理由。
```

### 预期输出示例

> AI 会输出一个 5 维度评分表（每项 1-5 分），附带每个维度的分析依据，最后给出"进入/谨慎/放弃"的综合建议和理由。

### 使用技巧

- 提供越具体的产品信息（价格区间、目标客群），评估越准确
- 可以同时评估多个产品做横向对比，追问"这三个产品中优先做哪个"

---

**分享此模板**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/prompts/product-research.md#模板-2-市场可行性快速评估`
**来源**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × 跨境电商实战知识库

---

## 模板 3: 关键词需求聚类

**场景**: 将大量搜索关键词按用户真实购买意图分组，发现产品机会
**推荐工具**: ChatGPT / Claude
**验证状态**: 已验证
**贡献者**: [@kangise](https://github.com/kangise)

### Prompt

```
以下是一个 Amazon 品类的搜索关键词列表（来自 Helium 10 或 Jungle Scout）。
请将这些关键词按用户的真实购买意图进行聚类分组。

对每个聚类：
1. 给出聚类名称（代表的用户需求）
2. 包含的关键词列表
3. 预估的需求强度（高/中/低）
4. 对应的产品特性建议

[在此粘贴关键词列表]
```

### 预期输出示例

> AI 会将关键词分成 4-8 个需求聚类，每个聚类有明确的命名、关键词列表、需求强度评估和对应的产品特性建议，帮助你从关键词数据中发现真实的市场需求。

### 使用技巧

- 关键词数量在 30-200 个之间效果最好
- 可以追问"哪个聚类的竞争最小但需求最大"来找蓝海机会

---

**分享此模板**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/prompts/product-research.md#模板-3-关键词需求聚类`
**来源**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × 跨境电商实战知识库
