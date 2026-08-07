# converge loop 进度

> 每轮结束时更新本文件。`done` 跳过、`blocked` 说明原因、`pending` 继续。中断后从第一个 pending 恢复。

**状态**: paused
**当前迭代**: 0/17
**最近验证**: 未运行（loop 尚未启动）

**目标三层结构**（收敛判据，非 backlog 清空）：
- **结果目标**：内容指标达阈值——术语表 ≥ 100 条 · skills ≥ 5 个 · 失败案例 ≥ 2 篇 · Prompt 模板库可复算 · 无过期 verified 标记 · README 数字全部可复算（由 `verify_content.py --metrics` 度量，迭代 0 实现）
- **约束**：`verify_content.py --list` 十项检查全 0，任何动作不得引入新失败
- **前置**：M7 / 过期门禁 / CHANGELOG 门禁 / 外链 cron 等机制——为内容优化铺路，单独完成不算收敛

---

## Backlog

| 迭代 | 动作 | 角色 | 状态 | 备注 |
|------|------|------|------|------|
| 0 | R-0 `--metrics` 内容度量模式（收敛判据的前提） | 前置 | pending | |
| 1 | R-1a README 数字单一数据源（章节/Prompt/Notebook 自动统计） | 前置 | pending | |
| 2 | R-1b M7 顶层文档检查上线 + README 数字统一 | 前置 | pending | 依赖迭代 1 |
| 3 | R-2 修复或退役 tests/（迁移 mdBook 时代 + CI 跑 pytest） | 前置 | pending | |
| 4 | U-1 verified 过期门禁（> 6 个月报错） | 门禁 | pending | 依赖迭代 0 |
| 5 | R-5 M2 升级：失效小节须含具体失效条件 | 门禁 | pending | |
| 6 | R-6 无证据断言检查 | 门禁 | pending | |
| 7 | R-7 EVOLUTION_LOG 对齐（基于门禁实际指标） | 前置 | pending | 依赖迭代 4 |
| 8 | U-2 外链 cron workflow + 死链自动开 issue | 前置 | pending | |
| 9 | U-3 CHANGELOG 门禁 | 前置 | pending | |
| 10 | RICH-5 Prompt 模板库 + 自动计数 | 内容 | pending | 依赖迭代 1 |
| 11 | RICH-2 三语术语表初版（100 条） | 内容 | pending | |
| 12 | R-4 翻译 parity 术语一致性检查 | 门禁 | pending | 依赖迭代 11 |
| 13 | RICH-1 skills/ 资产（5 个技能包） | 内容 | pending | |
| 14 | RICH-3 失败案例 ×2 | 内容 | pending | |
| 15 | RICH-4 交互式导航 | 内容 | pending | 依赖迭代 13 |
| 16 | U-4/U-5 易腐事实清单 + 过期报告模板 | 前置 | pending | 依赖迭代 4 |

---

## 阻塞项

（无）
