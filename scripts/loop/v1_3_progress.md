# v1.3.0 Amazon Operator Pilot — Loop 进度账本

更新日期：2026-08-26
规则：每轮仅在全部验证器通过后标记 `done`；同一根因两次失败即标记 `blocked`。每轮保留 evidence、commit、notes，且 commit 必须为一个动作一提交。

| Loop | 名称 | 状态 | Evidence | Commit | Notes |
|---|---|---|---|---|---|
| L0 | 基线合同 | done | `verify_all` 14 groups=0；pytest 63 passed；dist 153 fresh；MCP 69/878/9；wheel cold install + Schema v10 + CLI smoke | `loop(v1.3): L0 establish verified product baseline` | `main`/`origin/main` 原 HEAD `a6a6204`；敏感扫描与 `git diff --check` 通过；当前产品化成果固化为可恢复基线 |
| L1 | Accounts Center | done | Schema v11；Accounts API/UI；Amazon Sellers + Shopify shop health；pytest 77；14 groups=0；browser refresh persistence；wheel smoke | `loop(v1.3): L1 ship marketplace accounts center` | viewer read/admin manage/operator health；refs redacted；Demo 账户保持 unchecked/misconfigured 而非假成功 |
| L2 | Report Recipes | done | Schema v12；4 recipe allowlist；API/UI/RBAC；pytest 95；14 groups=0；browser Demo 4 recipes；wheel smoke | `loop(v1.3): L2 persist amazon report recipes` | 仅保存可复现配置，不调用Amazon；marketplaces强制为account subset；无删除/执行按钮 |
| L3 | SP-API Sync | done | Schema v13；durable create/poll/download/Evidence；pytest 107；14 groups=0；wheel + worker smoke；browser QA | `loop(v1.3): L3 ship durable amazon report sync` | operator enqueue/viewer inspect；healthy account gate；bounded retry/JSON/TSV；无自动调度与 Amazon 写入；live credential smoke 不可用 |
| L4 | Metric Observations | done | Schema v14；durable materialization/observations；pytest 120；14 groups=0；wheel persistence smoke；browser QA | `loop(v1.3): L4 persist provenance-safe metric observations` | Decimal v2；ISO currency isolation；period/grain/series/quality；bounded backfill；Briefing 不再解析 Evidence rows |
| L5 | Ads Contract Gate | blocked | Schema v15；real LWA/profiles/SP v3 read gate；pytest 139；14 groups=0；wheel blocked-state smoke；browser QA | `loop(v1.3): L5 enforce amazon ads capability gate` | 实现与门禁全部通过；当前环境无 Ads credentials/外部批准，真实结果持久 blocked，L6 不得接入 |
| L6 | Ads Adapter 条件实现 | done | Schema v15 unchanged；negative adapter status；pytest 148；14 groups=0；wheel/API smoke；browser QA | `loop(v1.3): L6 lock conditional amazon ads adapter` | L5 条件为假；adapter_registered=false、writes=[]、无 Ads route/action/button；freshness/config/capability guard 可审计 |
| L7 | Domain Agent Graph | done | Schema v16；163 tests；14 groups=0；wheel graph/Reviewer persistence smoke；browser metric-only run + refresh QA | `loop(v1.3): L7 ship tenant-safe domain agent graph` | canonical immutable DAG；dynamic Amazon/Shopify/ontology specialists；Manager + independent Reviewer；zero tools；non-approved downstream lock |
| L8 | Daily Ops | done | Schema v17；184 tests；14 groups=0；wheel daily persistence + CLI smoke；browser Brief/toggle/refresh QA | `loop(v1.3): L8 ship fenced daily operations` | local-date cursor；scheduled cutoff；immutable config hash；fenced leases；approved parent-linked Brief；no external writes |
| L9 | Proposals | done | Schema v18；204 tests；14 groups=0；Python 3.12 wheel cold install；Demo executed/blocked/submitted refresh persistence；browser console 0 | `loop(v1.3): L9 ship proposal approval control plane` | immutable source/version/hash；1/2-person quorum；atomic audit；fenced recovery worker；safe Action reuse；Ads zero-call block |
| L10 | Live Mission Control/SSE | done | Schema v19；213 tests；14 groups=0；installed HTTP SSE smoke；browser event/resume/reconnect console 0 | `loop(v1.3): L10 stream tenant-safe mission control` | per-tenant cursor；1,000-event retention/reset；20 global/4 tenant connections；single-process boundary |
| L11 | one-command Pilot | done | Schema v20；225 tests；14 groups=0；wheel installed Pilot HTTP/SIGTERM smoke；browser six-heartbeat QA | `loop(v1.3): L11 run one-command pilot` | one process API+6 workers；boot lease fencing；readiness blockers；graceful persisted stop |
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

### L3 — SP-API Sync

- Date: 2026-08-26
- Status: done
- Evidence: `tests/test_report_syncs.py` 11 acceptance cases；全套 pytest 107 passed；`verify_all` 14 groups=0；MCP 69/878/9；`dist/` fresh；Python 3.12 wheel cold install + Schema v13 + `report-worker --once` smoke；`artifacts/design-qa/l3-report-sync-final.jpg`。
- Commit: `loop(v1.3): L3 ship durable amazon report sync`（本记录所在提交）
- Notes: tenant-owned durable sync；operator + Idempotency-Key + enabled recipe + healthy Amazon account gate；真实 `createReport`/`getReport`/document 边界；`IN_QUEUE`/`IN_PROGRESS` polling、`Retry-After`、bounded attempts、terminal failures；bounded JSON/TSV → Evidence；复合租户外键、意外 Worker 异常主动释放 lease；Mission Control 的运行/详情/禁用原因均接真实 API。L3 不自动调度配方、不写 Amazon；因缺 seller-authorized Amazon 凭证与 marketplace access，未宣称 live credential smoke 成功。
- Validator results: all repository and install gates passed; browser Demo shows four persisted recipes, disabled real-sync reason, empty Sync Activity, and zero console errors.
- Failure 1: 审计发现初始化异常可悬挂 lease 与报告下载 URL 可使用非标准 HTTPS 端口；已加入主动 reschedule+re-raise、443 限制及回归测试后全量复验通过。
- Failure 2 / blocked reason: 系统 Python 3.9 / pip 21 将 PEP 517 项目误构建为 `UNKNOWN-0.0.0`；改用工作区 Python 3.12 / pip 26 执行受支持的冷安装，依赖安装、CLI、Schema v13 与 worker smoke 均通过，不构成产品阻塞。
- Restore point and result: L2 `83fd583`; L3 Schema v13/Report Worker/UI 可由本轮提交单独回退。

### L4 — Metric Observations

- Date: 2026-08-26
- Status: done
- Evidence: `tests/test_metric_observations.py` 11 acceptance cases；全套 pytest 120 passed；`verify_all` 14 groups=0；MCP 69/878/9；`dist/` 153 fresh；Python 3.12 wheel cold install + Schema v14 + 4 persisted observations smoke；`artifacts/design-qa/l4-metric-observations-final.jpg`。
- Commit: `loop(v1.3): L4 persist provenance-safe metric observations`（本记录所在提交）
- Notes: tenant-owned materialization/observation two-table model；operator idempotent materialize、admin bounded cursor backfill、viewer list/detail；bounded lease + stale reclaim；Decimal calculation version `amazon-metrics-v2` stores conversion as ratio；explicit supported ISO currency allowlist、no inference/FX/cross-currency aggregation；period/grain/dimensions/series/provenance/quality retained；L3 Evidence commit stays successful if L4 fails；Briefing reads observations only and isolates currency/dimension/grain；UI exposes real materialize/source/retry actions and disables unsupported report types from runtime catalog.
- Validator results: all repository/install gates passed; browser Demo shows persisted USD/count/ratio observations, materialization states, eight-result bounded view, Evidence + Report Sync source detail, supported/unsupported action states, refresh persistence, and zero console errors.
- Failure 1: independent audit found a silently ignored `platform` filter and arbitrary three-letter currencies being accepted as ISO; API/OpenAPI/tests now pass the filter and enforce the supported Amazon marketplace currency allowlist.
- Failure 2 / blocked reason: first wheel smoke payload contained escaped newline bytes and was correctly rejected as empty CSV; rerunning with the intended bytes proved Schema v14 and observation persistence. This was a smoke-harness input error, not a runtime blocker.
- Restore point and result: L3 `1916af7`; L4 Schema v14/Metric Observation/Briefing/UI can be rolled back as one commit while leaving L3 Evidence intact.

### L5 — Amazon Ads Contract Gate

- Date: 2026-08-26
- Status: blocked（外部依赖；门禁实现与验证已完成）
- Evidence: `tests/test_ads_gates.py` 18 executed acceptance cases；全套 pytest 139 passed；`verify_all` 14 groups=0；MCP 69/878/9；`dist/` 153 fresh；Python 3.12 wheel cold install + Schema v15 + persisted `missing_credential` gate smoke；`artifacts/design-qa/l5-amazon-ads-gate-final.jpg`。
- Commit: `loop(v1.3): L5 enforce amazon ads capability gate`（本记录所在提交）
- Notes: `amazon_ads` account provider with redacted environment refs；fixed regional Profiles health；single-token LWA → `GET /v2/profiles` → configured Profile → read-only Sponsored Products v3 `POST /sp/campaigns/list`；campaign payload discarded；tenant-owned checking/passed/blocked/failed gate with idempotency/lease/recovery/request IDs；admin attestation kept separate from live capability evidence；only all four required capabilities can pass. Demo explicitly uses empty Ads env and persists two truthful blockers without network or fake success.
- Validator results: all repository/install gates passed; browser shows blocked LWA, skipped Profiles/Profile/Campaign checks, blocked external attestation, safe error, real modal/detail actions, and zero console errors. Official behavior was checked against Amazon Ads Advanced Tools and the `amzn/ads-advanced-tools-docs` Postman collection.
- Failure 1: integration review found incomplete Amazon Ads account OpenAPI oneOf/provider schemas, unsafe DTO drift, wrong docs repository link, and a Demo attestation that could look successful; schemas/DTO/docs were aligned and Demo now leaves attestation absent/blocked.
- Failure 2 / blocked reason: no Amazon Ads LWA credential variables, approved application evidence, authorized numeric Profile, or externally reconciled attestation exist in this environment. A real success smoke is therefore unavailable by design. Required unblock input: an approved tenant Ads account, three secret-manager variables, matching region/Profile ID, and a verified approval reference.
- Restore point and result: L4 `04a0947`; Schema v15/Ads connector/gate/UI can be rolled back as one commit without affecting SP-API reports or Metric Observations.

### L6 — Conditional Amazon Ads Adapter

- Date: 2026-08-26
- Status: done（L5 条件为假，按合同保持 Adapter 未安装）
- Evidence: `tests/test_ads_adapter_status.py` 8 acceptance cases；全套 pytest 148 passed；`verify_all` 14 groups=0；MCP 69/878/9；`dist/` 153 fresh；Python 3.12 wheel + authenticated status API smoke；`artifacts/design-qa/l6-ads-adapter-lock-final.jpg`。
- Commit: `loop(v1.3): L6 lock conditional amazon ads adapter`（本记录所在提交）
- Notes: viewer-readable tenant status；latest Gate queried directly per account；24-hour freshness、future timestamp、account update、region/Profile、exact required capabilities checks；status only `blocked|eligible_not_installed`；`adapter_registered=false` and `write_operations=[]` are invariant；ActionService/OpenAPI/UI contain no Amazon Ads write operation, route, execution, unlock, or registration button. A fixture-passed Gate can prove only future eligibility, never an installed adapter.
- Validator results: all repository/install gates passed; Demo shows L5 Gate blocked, required capabilities incomplete, Adapter not installed, write surface disabled, no write actions, and zero console errors.
- Failure 1: the delegated backend could not run pytest; its helper reused an L5 idempotency key and initially failed under the real runner. The helper, DTO/envelope, reason allowlist, time checks, and API coverage were repaired; targeted and full tests then passed.
- Failure 2 / blocked reason: independent audit found a 200-row tenant Gate scan could miss an account's latest Gate. Storage now queries latest by `(tenant_id, connector_account_id)` directly with a regression test. No remaining L6 blocker; L5's external block intentionally keeps the adapter absent.
- Restore point and result: L5 `05bc561`; L6 adds only a read-only status/negative boundary and can be reverted without changing Schema v15 or Ads gate history.

### L7 — Domain Agent Graph

- Date: 2026-08-26
- Status: done
- Evidence: `tests/test_agent_graphs.py` 13 acceptance cases；全套 pytest 163 passed；`verify_all` 14 groups=0；`dist/` fresh；Python 3.12 wheel cold install + Schema v16 + published graph + metric-only run + Reviewer/persistence smoke；`artifacts/design-qa/l7-domain-agent-graph-final.jpg`。
- Commit: `loop(v1.3): L7 ship tenant-safe domain agent graph`（本记录所在提交）
- Notes: tenant-owned graph/version model；published/retired definitions immutable；definition hash binds orchestration code + ontology + Skill manifests；run binds published ID/hash and exact Evidence/Metric Observation snapshot；canonical Evidence Analyst + dynamic marketplace specialists parallel stage → optional cross-platform Controller → Manager → separate Reviewer；all node tool policies fixed to `allowed_tools=[]`/`max_tool_calls=0`；every priority requires approval；Manager action/Metric claims and complete Reviewer reference/limitation coverage are deterministic gates；Briefing/evaluator verify final run-report + current Reviewer task-attempt lineage and reject legacy/non-approved outputs while retaining retry history；graph, run, task, artifact, event, evaluation tenant integrity is enforced at the database layer. Canonical-only execution and the default same-provider Reviewer trust domain are explicit limitations, not hidden general-DAG or external-review claims.
- Validator results: all repository, migration, installed-wheel, and browser gates passed；browser created and executed a metric-only run, displayed `operations_reviewer · completed · approved`, persisted it across reload, and reported zero console errors.
- Failure 1: independent audit found agent child tables relied on globally unique IDs rather than database-enforced tenant-parent ownership, and pre-L7 runs were initially migrated as approved；v16 now installs cross-tenant insert/update guards for runs, tasks, artifacts, events, and evaluations, migrates legacy review state as pending, and verifies full Reviewer lineage with a true old-v15-schema migration test.
- Failure 2 / blocked reason: final high-level audit found graph hashes did not bind installed execution inputs and a trivial partial Reviewer could approve only one Manager citation；re-audit then caught multi-source `observe`, free-text action classification, and retry-history selection gaps. Hashes now bind code/ontology/Skill manifests, stale runs fail closed, every priority requires approval, Metric operations are structurally bounded, Reviewer covers every Manager citation/limitation, and only final-attempt artifacts qualify downstream. Browser QA also fixed the Demo provider's metric-only input assumption. All paths have regression tests；no remaining L7 blocker.
- Restore point and result: L6 `bca4dc1`; L7 Schema v16/Graph service/API/UI can be reverted as one commit while preserving L0–L6 data. Published-version rollback inside v16 is done by publishing a new reviewed version, never mutating history.

### L8 — Daily Ops

- Date: 2026-08-26
- Status: done
- Evidence: `tests/test_daily_ops.py` 20 acceptance cases；全套 pytest 184 passed；`verify_all` 14 groups=0；`dist/` fresh；Python 3.12 wheel cold install + Schema v17 + hashed schedule snapshot + completed Reviewer-approved persisted Brief + installed `daily-scheduler`/`daily-worker --once` smoke；`artifacts/design-qa/l8-daily-ops-final.jpg`。
- Commit: `loop(v1.3): L8 ship fenced daily operations`（本记录所在提交）
- Notes: tenant-owned calendar schedule/occurrence model；IANA timezone, fold=0 and explicit nonexistent-time block；UTC `scheduled_for` is the Evidence cutoff；one occurrence per tenant/schedule/local date；immutable `schedule_config` hash；Metric Observation-first/raw fallback input selection；empty/blocked/failed/completed states；final Reviewer-gated persisted Brief；Daily child Agent Run parent lineage；per-attempt lease-token fencing and exhausted-attempt terminal failure；durable `next_local_date` bounded catch-up；execution-owner demotion/re-enable guards；real API/UI/CLI paths；zero marketplace writes. L8 consumes existing Evidence and does not silently create Amazon reports.
- Validator results: all repository/install gates passed；browser showed persisted Demo schedule + completed Brief, real stop/start actions, refresh persistence, and zero console errors；four independent high-level review rounds ended with no P0/P1.
- Failure 1: adversarial review found look-ahead to local-day end, mutable Schedule reads, stale Worker overwrite, downgraded execution owner, and missed dates across midnight. Selection now ends at the frozen scheduled instant, occurrences hash a closed config snapshot, all attempt writes are fenced, role transitions/re-enable are atomically guarded, and a durable cursor catches up one date per tick.
- Failure 2 / blocked reason: re-review found approved orphan Agent Runs could leak into the global Briefing and retired Graphs could prevent safe HTTP disable. Agent Runs now carry parent run/attempt/internal lease lineage and are downstream-eligible only when the completed parent points to that exact final child；Graph validation is skipped only for a no-change safe disable, with a real full-PATCH regression test. No remaining L8 blocker；live OpenAI success still depends on deployment credentials as documented in L7.
- Restore point and result: L7 `451ff1e`; L8 Schema v17/Daily Ops/API/UI/CLI can be reverted as one commit while preserving L0–L7 records. Existing Daily Ops history is immutable; operational recovery uses retry with the frozen snapshot or a new corrected schedule.

### L9 — Proposals

- Date: 2026-08-26
- Status: done
- Evidence: `tests/test_proposals.py` 18 acceptance/adversarial cases；全套 pytest 204 passed；`verify_all` 14 groups=0；OpenAPI closed operation payload contracts；Python 3.12 wheel cold install + Schema v18 + Demo `human.review → executed` / `Amazon Ads → blocked` + installed `proposal-worker --once` smoke；browser create→submit→reload persistence、自批按钮禁用、seeded executed/blocked histories、console 0 errors；`artifacts/design-qa/l9-proposals-final.jpg`。
- Commit: `loop(v1.3): L9 ship proposal approval control plane`（本记录所在提交）
- Notes: Proposal 只能从完成且 Reviewer-approved 的 Daily Ops 最终 Manager priority 派生；不可变 source/graph/evidence/metric/payload/content hashes 与版本历史；low/medium 需另一位 admin/owner，high/critical 需两位 distinct approvers；creator 不可自批；显式 expiry；execute/retry 永久幂等绑定；lease-token fencing 与 `proposal-worker` 恢复；状态与审计同事务；安全 Shopify/SP-API 动作复用既有 ActionService，账户不健康时零调用；Amazon Ads adapter 未安装时永久 blocked 且 `connector_calls=0`。
- Validator results: all repository/contract/install/browser gates passed；独立 high-level review 的全部 PoC 均 fail-closed，最终无可复现 P0/P1。
- Failure 1: adversarial review found pending/stale expiry races, reusable retry keys, execute-key aliases, non-atomic audit, role-demotion liveness, worker crash/hot-loop/FIFO, idempotent create replay, and UI run/priority mismatch. These were fixed with transaction-bound audit, immutable retry ledger, expiry-aware claims, active-role guards, bounded worker recovery, strict API/UI contracts, and regression tests.
- Failure 2 / blocked reason: DB raw-write review found mutable idempotency/execution bindings, expired decision/execution insertion, Action misbinding, forged or reused retry ledgers, and deletable execution history. Schema v18 triggers now reject each PoC. Amazon Ads live write remains intentionally blocked by the unresolved L5 external capability gate; L9 makes no live Ads write claim.
- Restore point and result: L8 `28ab04b`; L9 Schema v18/Proposal service/API/UI/worker can be reverted as one commit while preserving L0–L8 records. Proposal versions, decisions, retry requests, and execution history are immutable; operational recovery uses the same approved execution binding, never a new unapproved payload.

### L10 — Live Mission Control / SSE

- Date: 2026-08-26
- Status: done
- Evidence: `tests/test_live_mission_control.py` 6 persistence/isolation/wire/resource-boundary cases；全套 pytest 213 passed；`verify_all` 14 groups=0；OpenAPI numeric cursor + closed MissionEvent/Reset/Reconnect contracts；Python 3.12 wheel cold install + Schema v19 + installed authenticated HTTP SSE smoke；browser initial backlog、real `proposal.created` update、normal lifetime reconnect、reload cursor resume/no replay、console 0 errors；`artifacts/design-qa/l10-live-mission-control-final.jpg`。
- Commit: `loop(v1.3): L10 stream tenant-safe mission control`（本记录所在提交）
- Notes: immutable tenant-owned Mission Events are written by database triggers for Agent Run/Task, Report Sync, Job, Daily Ops, Proposal, and Proposal Execution insert/status transitions；only bounded status/relationship metadata is projected；internal global sequence and tenant id never leave storage；SSE uses bearer-header `fetch` streaming, tenant-local numeric `Last-Event-ID`, comment heartbeat, explicit retention reset and bounded reconnect；1,000 retained events/tenant；20 global and 4 per-tenant single-process connections；UI stores only the cursor in tenant-scoped sessionStorage and keeps API keys in memory.
- Validator results: all repository/contract/install/browser gates passed；real transition reached the UI without polling, reload resumed from the saved cursor without replaying old events, and a subsequent Proposal event arrived live.
- Failure 1: independent integration review found that a global AUTOINCREMENT cursor exposed other-tenant activity through sequence gaps, event/resource bindings were forgeable by raw SQL, query secrets could enter access logs, and the initial OpenAPI event envelope did not match the wire. Schema v19 now uses contiguous per-tenant cursors with a hidden internal sequence, real same-tenant resource/status binding, closed JSON metadata, query-free access logs, and exact `mission.update/reset/reconnect` contracts.
- Failure 2 / blocked reason: the first browser stress pass deliberately ran multiple one-second streams and reached the real 120 requests/minute client limiter; the UI surfaced reconnect/429 rather than bypassing it. The final isolated one-tab smoke used the normal authenticated flow, verified cursor resume and zero console errors. No L10 blocker remains；the explicit limitation is single-process SQLite/ThreadingHTTPServer polling with no HA, broker, or multi-process fan-out claim.
- Restore point and result: L9 `f52b72e`; L10 Schema v19/event projection/API/UI can be reverted as one commit while preserving L0–L9 state. Mission events are a bounded projection, not the audit source of truth；after retention or restore, clients refetch the durable Mission Control snapshot.

### L11 — one-command Pilot

- Date: 2026-08-26
- Status: done
- Evidence: `tests/test_pilot.py` 10 model/readiness/supervisor/CLI/HTTP/shutdown cases；全套 pytest 225 passed；`verify_all` 14 groups=0；OpenAPI closed Pilot status/runtime/worker/readiness contracts；Python 3.12 wheel cold install + installed `opc-ecommerce pilot` real HTTP + six healthy Worker heartbeats + SIGTERM exit 0 + reopened `stopped` persistence + read-only `--check` smoke；browser one-time-key connect、six heartbeat ticks、真实 refresh action、honest dependency blockers、Live SSE、console 0 errors；`artifacts/design-qa/l11-one-command-pilot-final.jpg`。
- Commit: `loop(v1.3): L11 run one-command pilot`（本记录所在提交）
- Notes: `opc-ecommerce pilot` pre-binds the loopback HTTP port, optionally bootstraps exactly one new tenant only when name/email are explicit, prints the new API key once, then runs API + Schedule/Job/Report/Daily Scheduler/Daily Worker/Proposal Worker in one supervised process；runtime-scoped Schema v20 boot generation/lease and per-worker heartbeats persist without tenant payloads or secrets；fresh duplicate supervisors fail, stale takeover fences the old boot；single-worker errors persist a safe type and do not stop peers；SIGINT/SIGTERM use an interruptible stop and only report clean success after all workers stop.
- Validator results: all repository/contract/install/browser gates passed；the installed wheel process reported six healthy workers while the tenant honestly remained blocked on absent Amazon/OpenAI/Daily dependencies, then persisted all workers as stopped after SIGTERM.
- Failure 1: integration review found potential port-bind orphan bootstrap, lease-expired-but-not-yet-stale status, ignored shutdown timeout, and unstructured bootstrap/preflight/server failures. Pilot now validates and pre-binds before tenant creation, evaluates lease expiry at read time, fences generations, returns structured nonzero failures, and persists `stopping`/`ShutdownTimeout` instead of claiming a clean exit.
- Failure 2 / blocked reason: initial readiness based only on historical account health could outlive revoked credentials. The final gate requires an Amazon health result no older than 24 hours plus current credential-environment presence, a published graph, enabled Daily Ops, and OpenAI key/model presence；only boolean/count information is exposed. L5 Amazon Ads remains an explicit optional blocked component. No L11 implementation blocker remains；HA/multi-process coordination is deliberately not claimed.
- Restore point and result: L10 `c36e622`; L11 Schema v20/Pilot supervisor/API/UI/CLI can be reverted as one commit while preserving L0–L10 tenant data. A stopped or stale boot remains diagnostic history；restart creates a higher fenced generation rather than mutating the old boot.

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
