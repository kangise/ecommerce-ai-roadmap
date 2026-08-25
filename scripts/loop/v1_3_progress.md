# v1.3.0 Amazon Operator Pilot — Loop 进度账本

更新日期：2026-08-26
规则：每轮仅在全部验证器通过后标记 `done`；同一根因两次失败即标记 `blocked`。每轮保留 evidence、commit、notes，且 commit 必须为一个动作一提交。

| Loop | 名称 | 状态 | Evidence | Commit | Notes |
|---|---|---|---|---|---|
| L0 | 基线合同 | done | `verify_all` 14 groups=0；pytest 63 passed；dist 153 fresh；MCP 69/878/9；wheel cold install + Schema v10 + CLI smoke | `loop(v1.3): L0 establish verified product baseline` | `main`/`origin/main` 原 HEAD `a6a6204`；敏感扫描与 `git diff --check` 通过；当前产品化成果固化为可恢复基线 |
| L1 | Accounts Center | done | Schema v11；Accounts API/UI；Amazon Sellers + Shopify shop health；pytest 77；14 groups=0；browser refresh persistence；wheel smoke | `loop(v1.3): L1 ship marketplace accounts center` | viewer read/admin manage/operator health；refs redacted；Demo 账户保持 unchecked/misconfigured 而非假成功 |
| L2 | Report Recipes | done | Schema v12；4 recipe allowlist；API/UI/RBAC；pytest 95；14 groups=0；browser Demo 4 recipes；wheel smoke | `loop(v1.3): L2 persist amazon report recipes` | 仅保存可复现配置，不调用Amazon；marketplaces强制为account subset；无删除/执行按钮 |
| L3 | SP-API Sync | pending |  |  |  |
| L4 | Metric Observations | pending |  |  |  |
| L5 | Ads Contract Gate | pending |  |  |  |
| L6 | Ads Adapter 条件实现 | pending |  |  |  |
| L7 | Domain Agent Graph | pending |  |  |  |
| L8 | Daily Ops | pending |  |  |  |
| L9 | Proposals | pending |  |  |  |
| L10 | Live Mission Control/SSE | pending |  |  |  |
| L11 | one-command Pilot | pending |  |  |  |
| L12 | eval/security/restore | pending |  |  |  |
| L13 | RC | pending |  |  |  |

## 每轮记录模板

### L0 — 基线合同

- Date: 2026-08-26
- Status: done
- Evidence: `roadmap/v1.3-amazon-operator-pilot.md`; `verify_all` 14 groups=0; `python3 -m pytest` 63 passed; `dist/` 153 files fresh; MCP package 69 chapters/878 prompts/9 skills; wheel cold install; installed Schema v10 and CLI smoke.
- Commit: `loop(v1.3): L0 establish verified product baseline`（本记录所在提交）
- Notes: 从 `a6a6204` 盘点 58 个 tracked 修改和产品化新增目录；敏感扫描未发现真实 API key、私钥或 `.env`；`dist/` 按仓库规则版本化，UI QA evidence 与报告共同保留。
- Validator results: all passed.
- Failure 1: none.
- Failure 2 / blocked reason: none.
- Restore point and result: 原始远端基线 `a6a6204`; 新 L0 提交成为 v1.3 Loop 恢复点。

### L1 — Accounts Center

- Date: 2026-08-26
- Status: done
- Evidence: `tests/test_accounts.py` 13 acceptance cases；全套 pytest 77 passed；`verify_all` 14 groups=0；MCP 69/878/9；`dist/` 153 fresh；wheel cold install Schema v11/account persistence/redaction smoke；`artifacts/design-qa/l1-accounts-center-final.jpg`。
- Commit: `loop(v1.3): L1 ship marketplace accounts center`（本记录所在提交）
- Notes: tenant-scoped list/get/create/update/health；Amazon marketplace directory/region validation；真实 Sellers marketplaceParticipations 和 Shopify shop health 边界；UI loading/empty/success/failure/RBAC；OAuth/delete/background checks 明确不在 L1。
- Validator results: all passed; browser health failure persisted as `misconfigured` across reload; console 0 errors.
- Failure 1: OpenAPI test wording与 contract gate 对 shop.json 代码样式产生误判；已修正文档字面并重建 dist。
- Failure 2 / blocked reason: none.
- Restore point and result: L0 `7f483b4`; L1 迁移和 UI 可由本轮单一提交回退。

### L2 — Report Recipes

- Date: 2026-08-26
- Status: done
- Evidence: `tests/test_report_recipes.py` 17 acceptance cases；全套 pytest 95 passed；`verify_all` 14 groups=0；MCP 69/878/9；`dist/` 153 fresh；wheel cold install Schema v12 + 4 tenant-owned recipes；`artifacts/design-qa/l2-report-recipes-final.jpg`。
- Commit: `loop(v1.3): L2 persist amazon report recipes`（本记录所在提交）
- Notes: 四种 allowlist 配方、严格 account/marketplace subset、viewer read/operator manage、完整更新与持久化；UI 明确 L2 不调用 Amazon，远程同步留给 L3。
- Validator results: all passed; Demo shows 4 persisted recipes and real catalog-derived form; browser console 0 errors.
- Failure 1: none.
- Failure 2 / blocked reason: none.
- Restore point and result: L1 `997cb18`; L2 Schema v12/Recipe UI 可由本轮提交单独回退。

### Lx — 名称

- Date:
- Status: pending | in_progress | blocked | done
- Evidence:
- Commit:
- Notes:
- Validator results:
- Failure 1:
- Failure 2 / blocked reason:
- Restore point and result:
