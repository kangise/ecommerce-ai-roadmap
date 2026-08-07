# converge loop 执行指令（每轮读这一份）

你是 **converge loop** 的迭代执行者。本指令自包含——不依赖任何之前的对话。每轮恰好执行一个动作，跑完停下。

## 目标状态

- backlog（见 `scripts/loop/progress.md`）16 项全部 `done`；
- `python3 scripts/verify_content.py --list` 十项检查全为 0（迭代 2 后为 11 项，含 M7）。

## 本轮步骤（严格按序）

1. **探测**：`git status --short`。若有未提交改动 → **停下**，报告改动内容并请用户决定，不自动处理。
   `python3 scripts/verify_content.py --list` 记录当前失败项（基线）。
2. **取动作**：读 `scripts/loop/progress.md`，选第一个 `pending` 项（跳过 `blocked`）。若没有 pending → 输出收敛报告，终止。
3. **执行**：只改该动作需要的文件，最小改动。涉及脚本/CI 的按仓库既有风格（参考 `scripts/verify_content.py`）。
4. **验证**：
   - 重跑 `python3 scripts/verify_content.py --list`：该动作目标归零；
   - 回归：基线中原本为 0 的检查不得变非零；
   - 失败则修复；同一动作累计失败 2 次 → 在 progress.md 标 `blocked` 并写明原因，跳到步骤 5（提交可保留的中间态或不提交，按情况）。
5. **提交**：`git commit -m "loop(converge): <迭代号> <动作名>"`，一个动作一个提交。
6. **记录**：更新 `scripts/loop/progress.md`：状态列、最近验证结果、阻塞项。
7. **完成标志**：输出本轮摘要——diff 涉及文件、验证结果（失败 X 项）、剩余 pending n/16。然后停止，等用户说"继续"。

## 硬性规则

- 验证器是唯一真源：以 `verify_content.py` 退出码和输出为准，不编造"应该能过"。
- 不引入新失败：某改动让现有检查变非零 = 该动作失败，先修回归。
- 一个动作一个提交；不把多项改动揉进一个提交。
- blocked 不硬闯：失败 2 次就记录原因跳过，留给人工，不让循环空转。
- 涉及三语的内容改动：`src/` 改了必须同步 `i18n/en/src`、`i18n/ja/src`（结构一致，用 `scripts/gen_i18n_stubs.py --status` 验证）。
- 涉及外链/文件的改动跑不过 M4 时：先 `python3 scripts/verify_content.py --probe-links` 刷新缓存（仅当确需新增链接）。

## 每轮产出格式

```
本轮: 迭代 N — <动作名>
diff: <文件列表>
验证: verify_content.py — 失败 <X> 项（基线 <Y>）
剩余: pending n/16 · blocked <k> · done <d>
下一步: <建议>
```
