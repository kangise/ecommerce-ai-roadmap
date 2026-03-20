# 广告优化 Prompt 模板 | Advertising Prompts

> 最后更新: 2026-03-10 | 模板数量: 2 | 验证状态: 已验证

---

## 模板 1: 搜索词报告分析

**场景**: 分析 Amazon PPC 搜索词报告，找出浪费和优化机会
**推荐工具**: ChatGPT / Claude
**验证状态**: 已验证
**贡献者**: [@kangise](https://github.com/kangise)

### Prompt

```
你是一个 Amazon PPC 广告优化专家。

以下是我的搜索词报告数据（过去30天）：
[粘贴：搜索词、展示量、点击量、花费、订单数、销售额]

请分析并输出：
1. 高转化关键词 TOP 10（按 ROAS 排序）-- 建议提高竞价
2. 高花费低转化关键词 TOP 10 -- 建议降低竞价或否定
3. 高展示低点击关键词（CTR < 0.3%）-- 分析可能原因
4. 建议添加的否定关键词列表（精确否定 vs 短语否定）
5. 预算重新分配建议

用表格呈现，标注每个关键词的建议操作和优先级。
```

### 预期输出示例

> AI 会输出分类整理的关键词分析表格，包含高转化词、浪费词、低 CTR 词的具体操作建议，以及否定关键词列表和预算分配方案。

### 使用技巧

- 直接从广告后台导出 CSV 数据粘贴，保留列名效果更好
- 可以追问"如果预算只有 $X/天，应该怎么分配"来获得更具体的建议

---

**分享此模板**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/prompts/advertising.md#模板-1-搜索词报告分析`
**来源**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × 跨境电商实战知识库

---

## 模板 2: 广告文案 A/B 测试

**场景**: 为 Sponsored Brands 广告生成多种风格的 Headline 变体
**推荐工具**: ChatGPT / Claude / Gemini
**验证状态**: 已验证
**贡献者**: [@kangise](https://github.com/kangise)

### Prompt

```
我的产品是 [产品描述]，核心卖点是 [卖点]。

请为 Sponsored Brands 广告生成 5 个不同风格的 Headline（每个不超过50字符）：
1. 功能导向型
2. 场景导向型
3. 情感导向型
4. 数据导向型（如"24小时续航"）
5. 问题解决型（如"告别XX烦恼"）

每个 Headline 标注预期效果和适合的受众。
```

### 预期输出示例

> AI 会输出 5 个不同风格的广告 Headline，每个附带预期效果说明和目标受众分析，方便你直接用于 A/B 测试。

### 使用技巧

- 提供竞品的广告文案作为参考，AI 可以帮你做差异化
- 生成后可追问"哪个 Headline 最适合 [特定受众]"来进一步筛选

---

**分享此模板**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/prompts/advertising.md#模板-2-广告文案-ab-测试`
**来源**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × 跨境电商实战知识库
