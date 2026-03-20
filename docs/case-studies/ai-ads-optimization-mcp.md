# 案例研究：用 MCP + Claude 自动化 Amazon 广告管理

> **场景**: Amazon PPC 广告优化
> **工具**: Claude + Amazon Ads MCP Server
> **难度**: 中级
> **预计节省**: 每周 10+ 小时，ACOS 降低 30-50%

[Hub 首页](../../README.md) · [案例列表](README.md)

---

## 背景

一个 Amazon 卖家管理 15 个 SP Campaign，每周花 8-10 小时手动分析搜索词报告、调整出价、添加否定词。ACOS 在 28-35% 之间波动，目标是降到 20% 以下。

## 传统方式（Before）

| 步骤 | 操作 | 时间 |
|------|------|------|
| 1 | 登录 Amazon Ads 后台，下载搜索词报告 | 15 分钟 |
| 2 | 在 Excel 中筛选高花费低转化的词 | 45 分钟 |
| 3 | 逐个 Campaign 添加否定词 | 30 分钟 |
| 4 | 筛选高转化词，移到 Manual Campaign | 45 分钟 |
| 5 | 调整出价（逐个关键词） | 60 分钟 |
| 6 | 检查预算消耗情况 | 15 分钟 |
| 7 | 生成周报给团队 | 30 分钟 |
| **总计** | | **4-5 小时/周** |

## MCP 方式（After）

```
对话 1（5 分钟）：
"分析过去 7 天所有 SP Campaign 的搜索词报告。
找出花费 > $10 但 0 转化的搜索词，添加为否定精确匹配。"
→ Claude 自动处理 23 个浪费词

对话 2（5 分钟）：
"找出转化率 > 15% 且至少 3 次转化的搜索词。
如果不在 Manual Campaign 中，添加为 Exact Match，
出价设为该词平均 CPC 的 120%。"
→ Claude 自动迁移 8 个高转化词

对话 3（3 分钟）：
"哪些 Campaign 的日预算在下午 3 点前耗尽？
建议重新分配预算。"
→ Claude 识别 3 个预算不足的 Campaign

对话 4（2 分钟）：
"生成本周广告优化报告，Markdown 格式。"
→ Claude 生成完整报告
```

| 步骤 | 操作 | 时间 |
|------|------|------|
| 1 | 对话式搜索词分析+否定词添加 | 5 分钟 |
| 2 | 高转化词迁移 | 5 分钟 |
| 3 | 预算重新分配 | 3 分钟 |
| 4 | 生成周报 | 2 分钟 |
| **总计** | | **15 分钟/周** |

## 结果

| 指标 | Before | After | 变化 |
|------|--------|-------|------|
| 每周时间 | 4-5 小时 | 15 分钟 | -95% |
| ACOS | 28-35% | 18-22% | -35% |
| 浪费性支出 | ~$800/月 | ~$200/月 | -75% |
| 高转化词覆盖 | 手动发现，遗漏多 | 自动全覆盖 | 显著提升 |

> **真实数据参考**：PPC 管理自动化可以每周节省 10+ 小时（[Maxmerce](https://www.maxmerce.com/blog/how-to-improve-amazon-ppc-performance-campaign-opt/)）。Amazon PPC ACOS 优化可以降低广告成本 30-50%（[Maxmerce](https://www.maxmerce.com/blog/amazon-ppc-acos-optimization-reduce-costs-boost-ro/)）。

Content rephrased for compliance with licensing restrictions.

## 关键学习

1. MCP 不是替代人工判断，而是替代重复性操作
2. 写操作（调整出价、添加否定词）建议先在测试 Campaign 验证
3. 每周 15 分钟的对话式管理 > 每周 5 小时的手动操作
4. 关键是建立标准化的对话流程（每周固定执行）

## 相关模块

- [B6 MCP 集成与 Agentic 工作流](../../paths/b-developers/b6-mcp-agentic-workflow.md)
- [A3 广告优化](../../paths/a-operators/a3-advertising.md)
- [A13 AI Growth Hack](../../paths/a-operators/a13-ai-growth-hack.md)
