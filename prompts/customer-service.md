# 客服与售后 Prompt 模板 | Customer Service Prompts

> 最后更新: 2026-03-10 | 模板数量: 2 | 验证状态: 已验证

---

## 模板 1: 差评批量分析

**场景**: 批量分析产品差评，分类问题并制定改善方案
**推荐工具**: ChatGPT / Claude
**验证状态**: 已验证
**贡献者**: [@kangise](https://github.com/kangise)

### Prompt

```
你是一个电商产品质量分析师。以下是我的产品最近60天的所有1-3星评论。

请完成：
1. 按问题类型分类（质量/功能/物流/使用困难/预期不符/其他）
2. 每个类型的频率和占比（用表格）
3. 每个类型中最有代表性的3条评论原文
4. 针对每个问题：
- 短期应对（Listing 调整、客服话术）
- 长期改善（产品改进、供应商沟通要点）
5. 优先级排序：先解决哪个问题（考虑频率 x 严重程度）

[粘贴差评内容]
```

### 预期输出示例

> AI 会输出一份结构化的差评分析报告，包含问题分类表格（含频率和占比）、代表性评论、短期和长期应对方案，以及按优先级排序的行动计划。

### 使用技巧

- 粘贴原始评论文本即可，AI 会自动分类和统计
- 可以追问"针对排名第一的问题，帮我写一封给供应商的改进要求邮件"

---

**分享此模板**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/prompts/customer-service.md#模板-1-差评批量分析`
**来源**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × 跨境电商实战知识库

---

## 模板 2: 账号申诉信 (Plan of Action)

**场景**: 账号被暂停时，撰写专业的 Plan of Action 申诉信
**推荐工具**: ChatGPT / Claude
**验证状态**: 已验证
**贡献者**: [@kangise](https://github.com/kangise)

### Prompt

```
你是一个 Amazon 账号申诉专家。我的账号因为以下原因被暂停：
[粘贴违规通知]

请撰写 Plan of Action，包含：
1. Root Cause -- 承认问题，不推卸
2. Immediate Actions -- 已采取的紧急措施（要具体）
3. Preventive Measures -- 防止再次发生的长期措施（要可执行）

要求：语气诚恳专业，每个部分用编号列出具体行动项，不要空话。
```

### 预期输出示例

> AI 会输出一封结构清晰的 Plan of Action，包含根因分析、已采取措施和预防措施三个部分，每部分有具体的编号行动项，语气诚恳专业。

### 使用技巧

- 粘贴完整的违规通知邮件，包含具体的违规类型和 ASIN
- 可以追问"帮我把这封信翻译成英文，保持专业语气"

---

**分享此模板**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/prompts/customer-service.md#模板-2-账号申诉信-plan-of-action`
**来源**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × 跨境电商实战知识库
