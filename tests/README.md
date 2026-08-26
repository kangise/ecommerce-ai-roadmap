# 测试目录

# Test contract

The repository keeps tests at the top level of this directory. They cover the
generated distribution, routing acceptance cases, notebook execution with
explicit fixture inputs, the installable wheel, and the tenant-safe runtime,
including public user onboarding and the complete second-actor approval path.
The runtime suite also covers durable multi-agent runs, ontology-driven Amazon
and other marketplace agents, cross-platform execution, manager synthesis,
evidence/platform-reference failures, explicit retries,
tenant isolation, HTTP routes, and the real Responses request boundary through
an injected transport fixture.
CSV/XLSX coverage includes typed Amazon report validation, generic marketplace files,
idempotency, preserved string values, PII/secret rejection, formula-cell accounting,
field mapping, content-addressed originals, ZIP/XLSX limits, HTTP uploads, durable
import IDs, and cross-tenant access denial.
Amazon connector coverage includes LWA exchange, `x-amz-access-token`, regional
report/document requests, GZIP download, credential absence, approved action
execution, local Evidence creation, and absence of persisted secret values.
Worker coverage includes leases, retry/backoff, idempotent queueing, scheduler
occurrences, latest-Evidence selectors, CLI `--once`, Mission Control aggregation,
approval inbox authorization, and tenant isolation.
Evaluation coverage includes passing completed runs, persisted grader history,
tampered approval-policy regression detection, and Mission Control failure counts.
Daily Ops coverage verifies tenant-scoped schedule and occurrence persistence,
IANA timezone/local-date behavior including DST ambiguity and gaps, one run per
schedule-local day under concurrent triggers, source-selection freshness and
explicit empty states, operator/viewer authorization, retry and stale-lease
recovery with per-attempt fencing, immutable hashed schedule snapshots,
scheduled-instant look-ahead prevention, bounded missed-date catch-up, execution
principal demotion/re-enable guards, orphan Agent Run downstream exclusion,
scheduler/worker CLI entrypoints, persisted brief
retrieval, final Reviewer eligibility, cross-tenant 404 behavior, and the
explicit absence of external-write tools. One-shot scheduler/worker command
tests do not claim multi-replica scheduler coordination.
UI coverage validates JavaScript syntax, visible-button wiring, real endpoint
references, static serving, CSP/no-store headers, live catalog data, and wheel packaging.
Briefing coverage verifies real Amazon Evidence aggregation, trend provenance,
approval filtering, platform validation, HTTP authentication, and tenant isolation.
Demo coverage verifies new-path refusal, explicit tenant mode, generated
Evidence/Run/Eval/Action/Job/Schedule state, CLI output, production defaults, and
the persistent UI warning. It also proves the auto-session exists only on an
explicit single-tenant Demo app and remains 404 on normal Runtime processes.
Marketplace connector coverage verifies the OpenAPI L1 contract for the
tenant-scoped account list/get/create/update and synchronous health-check
routes, the `MarketplaceAccount` redacted response fields, provider and
Amazon-marketplace catalog entries, viewer/admin/operator role gates,
environment-reference-only configuration, cross-tenant 404 behavior, and
persistent `unchecked`/`healthy`/`misconfigured`/`unhealthy` health outcomes.
The contract intentionally does not cover OAuth connect flows, connector
deletion, or background health checks.
Report recipe coverage verifies the L2 list/get/create/update contract,
`ReportRecipe` field set, four-key Amazon/evidence allowlist, catalog mappings,
viewer read and operator write roles, same-tenant Amazon connector ownership,
marketplace-ID subset validation, full update payload requirements, durable
configuration-only behavior, and the explicit absence of delete, OAuth,
Amazon-call, and background-execution semantics.
Report sync coverage verifies the L3 idempotent `202` trigger, viewer sync
inspection routes, `ReportSync` fields and status allowlist, healthy-account
gate, bounded createReport/getReport polling and retry semantics, Retry-After
handling, DONE-to-Evidence import boundary, bounded JSON/TSV ingestion, and
the explicit no-write/no-auto-scheduling limitation.
Amazon report-sync coverage verifies the L3 enqueue/list/get contract,
operator and tenant boundaries, idempotency, enabled-recipe and healthy-account
gates, exact `createReport` payloads, `IN_QUEUE`/`IN_PROGRESS` polling,
`Retry-After` backoff, bounded attempts, terminal provider and credential
failures, `DONE` document retrieval, bounded sales/traffic JSON and TSV
normalization, finite-number rejection, Evidence persistence, recipe schedule
advancement, the one-shot worker CLI, and real UI action/state wiring. Network
calls use injected transport fixtures; the suite does not claim a live Amazon
credential smoke test.
Metric materialization coverage verifies the L4 source and generated OpenAPI
contracts for tenant-owned observation list/detail and materialization list,
operator/idempotency per-import materialization, admin-only bounded cursor
backfill, exact bounded Decimal strings, currency-isolated observations,
missing-currency quarantine, period/grain/provenance/quality fields, durable
failure visibility, and the rule that a failed L4 attempt cannot roll back an
already successful L3 Evidence import. Production materialization has no mock
data fallback; runtime behavior tests may use explicit fixtures only.

Run the complete suite with:

```bash
python3 -m pytest
```

Ads capability-gate contract coverage verifies tenant-scoped list/detail,
admin/owner Idempotency-Key protection, `amazon_ads` capabilities,
checking/passed/blocked/failed states, safe request IDs/errors, and the
LWA → regional profiles → target profile → campaigns-list read-only probe.
It does not claim live Ads smoke: this machine has no Ads credentials or
external attestation, so L5 remains blocked until both are supplied.

L6 negative-boundary coverage verifies the viewer-readable adapter-status
route, optional account filter, blocked/eligible_not_installed allowlist,
fixed `adapter_registered=false`, zero write operations, reason-code allowlist,
nullable freshness fields, and absence of Ads write routes/actions. Fixtures
may prove only `eligible_not_installed`; they must not claim an installed or
live-writing adapter. Future writes remain conditional on proposal, approval,
audit, and rollback.

L9 proposal coverage verifies tenant-scoped source-lineage derivation from an
approved Daily Ops / Agent Graph result, immutable evidence/metric/graph and
payload hashes, idempotent create/execute/retry, optimistic version conflicts,
self-approval rejection, risk-derived local approval thresholds, expiry,
execution leases, and delegation only to the two existing safe read Action
operations. It also asserts that L9 adds no Amazon Ads or generic marketplace
write surface. Fixtures remain test-only; `human.review` is a local audited
decision, not an external marketplace approval.

L10 contract coverage validates the viewer-authenticated Mission Control SSE
route, `text/event-stream` media type, bearer-header-only authentication,
header-first tenant-local integer cursor semantics, closed safe `MissionEvent`
metadata, reset/reconnect controls, comment-only heartbeats, and `401`/`403`/`422`/`429`
responses. It also checks the source and generated distribution retain the
single-process SQLite/ThreadingHTTPServer and reverse-proxy limitations. It
does not claim a distributed broker, multiprocess fan-out, or a live external
SSE smoke; connection and parser behavior are runtime/UI tests.

L11 contract coverage validates `GET /v1/pilot-status` as a viewer-authenticated
closed-schema tenant read model: explicit readiness blockers, credential
presence/counts only, runtime boot state, attention vs blocked, and the six worker heartbeat states
(`starting`/`healthy`/`stale`/`degraded`/`stopped`). It verifies the documented
one-command Pilot lifecycle, new vs existing database bootstrap, one-time key,
loopback/public-bind, `--check`, SIGTERM, structured port/preflight/start/shutdown-timeout
failure, and single-process SQLite boundaries.
It does not claim real Amazon authorization or OpenAI success without external
credentials and live evidence.

L12 coverage validates tenant audit `previous_hash`/`event_hash` tamper chains,
immutable Assurance list/detail runs, viewer reads and admin-only idempotent
eval/security creation, closed check/status contracts, 300-second lease/crash
resume attempts, and blocked no-data evals.
It also validates online SQLite/evidence-object backups, SHA-256 manifests,
owner-only modes, atomic new-directory publish, verify-only/no-overwrite restore,
path traversal/symlink/corruption rejection, and restore-generated Assurance
evidence. Backup encryption and production storage access controls are external
requirements, not claims made by the runtime.

The production gate is broader than pytest:

```bash
python3 scripts/build_dist.py --check
python3 scripts/verify_all.py
python3 integration/mcp-server.py --validate --dist dist
```

Tests must not create runtime mock data. Synthetic rows are allowed only in
test fixtures, and external connector tests must inject a transport rather
than call a platform with invented credentials.

# Contract tests

`test_distribution.py` keeps the generated OpenAPI contract aligned with the
source contract. `test_agent_graphs.py` covers graph/version RBAC and
immutability, canonical topology/prompt/tool rejection, dynamic Amazon,
Shopify, and other ontology specialists, Metric Observation snapshots,
idempotent graph lineage, installed execution-contract drift, structured
Manager action/Metric claims, complete Reviewer reference/limitation coverage,
legacy-run pending isolation and rerun binding, tenant-parent database guards,
Manager/Reviewer ordering, Reviewer rejection, and HTTP routes. Provider fixtures exercise the real
structured-output boundary without claiming a live OpenAI-key success; that
remains an explicit deployment smoke limitation.

## L13 release candidate contracts

`test_release_candidate.py` freezes the `1.3.0` version across project metadata,
the importable package, OpenAPI, HTTP server headers, and outbound User-Agent.
It also proves the RC manifest is deterministic, fresh, and tamper-evident;
checks the release workflow's tag, cold-wheel, installed Demo/recovery, checksum,
and asset gates; and refuses to close while the roadmap or L13 Loop ledger still
says pending. The workflow performs the dependency-isolated cold install on
Python 3.11; local wheel metadata coverage is skipped only when the host Python
is below the declared `>=3.10` support floor.

## L7-adapted UI visual contract

`test_ui.py::test_l7_decision_workspace_visual_contract_is_complete` keeps the
embedded workbench aligned with the NovoChoice L7 adaptation. It blocks missing
navigation/Canvas/detail regions, undefined visual tokens, unlicensed or
unpackaged fonts, weights above 500, oversized ordinary radii, `transition: all`,
missing dark/reduced-motion/reduced-transparency/forced-color behavior, stale
hardcoded Canvas chart colors, visible technical Proposal hashes, and a stretched
Proposal primary action. Static serving tests also fetch a real WOFF2 through
the production handler and verify its MIME type and bytes.
