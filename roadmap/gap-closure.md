# Gap closure matrix

This matrix is the acceptance boundary for the current repository. A gap is
closed only when code, persistence, authorization, tests, and a runnable check
exist together. External-provider decisions are recorded as blockers rather
than replaced with mocks.

| Gap | Status | Evidence |
|---|---|---|
| Generated artifact can be installed | **Closed** | `pyproject.toml`, `opc-ecommerce`, wheel smoke test, package-data freshness gate |
| MCP package integrity and deterministic routing | **Closed** | SHA-256 manifest, fail-closed loader, R1/R1b/R2 = 0 |
| Tenant ownership and durable state | **Closed for embedded runtime** | SQLite foreign keys, tenant predicates, schema version, refresh-safe record tests |
| Authentication and authorization | **Closed for API-key runtime** | Hashed `eai_` keys, tenant-scoped public user provisioning, viewer/operator/admin/owner roles, cross-tenant and role-escalation checks |
| API key lifecycle and basic abuse protection | **Closed for embedded runtime** | Rotation/revocation endpoints, last-key guard, loopback default, explicit public-bind flag, 120/minute in-process limiter |
| Human approval and replay safety | **Closed for read-only sync action** | Public second-user onboarding, separate one-time keys, two-actor approval, compare-and-set transitions, per-tenant idempotency |
| Execution recovery and pagination | **Closed for embedded Shopify sync** | Bounded action leases, attempt counters, explicit retry, persisted per-account page cursor, `/readyz` schema check |
| External connector boundary | **Closed for Shopify read-only products** | HTTPS host validation, environment credential reference, timeout/error tests |
| Audit and basic observability | **Closed for embedded runtime** | Append-only audit rows, request IDs, JSON logs, disposable process counters |
| Multi-agent Weekly Ops Council | **Closed for synchronous analysis slice** | Durable tenant-scoped runs/tasks/artifacts/events, ontology-driven Amazon and other marketplace specialists, cross-platform review, manager synthesis, structured evidence/platform references, explicit retry, real Responses API boundary |
| Marketplace evidence ingestion | **Closed for bounded file slice** | Tenant-scoped CSV/TSV/XLSX imports, five typed Amazon report shapes, generic imports for all ontology marketplaces, field mapping, content-addressed originals, SHA-256/idempotency, PII/secret rejection, durable import references in agent runs |
| Amazon SP-API Reports | **Closed for approved read-only report import** | Environment-referenced LWA credentials, regional endpoints, completed-report/document retrieval, Amazon-host validation, bounded GZIP download, second-actor approval, Evidence Import output |
| Background execution and schedules | **Closed for embedded single-database runtime** | Durable jobs, leases, bounded retry/backoff, interval schedules, latest-Evidence selectors, idempotent occurrences, worker/scheduler CLI, polling APIs |
| Mission Control backend | **Closed for API slice** | Real persisted counts, recent/failed runs and jobs, schedules, and admin-only approval inbox; no hardcoded business metrics |
| Mission Control embedded UI | **Closed for designed local product slice** | Amazon-first cross-platform operating brief, Evidence-derived trends, persisted Agent Brief priorities, role-aware approvals, dedicated workflow navigation, licensed local assets, responsive desktop/mobile UI, in-memory bearer session, CSP, wired actions and UI/API tests |
| Product-tour Demo data | **Closed for isolated local slice** | Explicit new-database-only seed command, Demo tenant mode, visible warnings, seven-day Amazon/cross-platform Evidence, completed Run/Eval/Job, Schedule and approval fixtures; no production fallback data |
| Agent workflow evals | **Closed for deterministic contract slice** | Persisted graders for task completion, priority structure, evidence, platform isolation, owner assignment, and approval policy; Mission Control failure count |
| Distributed execution and hosted UI | **Partial by design** | Embedded workers/schedules, Mission Control UI/polling, and incremental event cursors are real; distributed queues, WebSocket events, external identity/session auth, and cloud deployment remain product increments. |
| Remote HTTP MCP transport | **Partial by design** | Read-only stdio MCP remains; authenticated REST API is provided separately. Implementing streamable HTTP MCP requires selecting and pinning an MCP SDK/server deployment contract. |
| HA database, KMS, TLS, distributed rate limiting, external identity | **Blocked by deployment choice** | Threat model and runbook define the required controls; invitation, recovery, SSO, and user deletion remain external-identity responsibilities; SQLite/loopback defaults fail closed instead of implying internet readiness. |
| Billing/subscription workflow | **Blocked by product choice** | No payment provider, plan model, tax region, or entitlement policy was supplied; no fake checkout was added. |
| Additional live marketplace connectors and Amazon Ads | **Explicit next connector** | Platform-aware agents accept real evidence for all 15 ontology marketplaces and Amazon SP-API Reports now has a read-only slice. Ads, broader SP-API resources, and other platforms still need an owner, OAuth scope, API version, rate-limit policy, and real test account. |

## Exit rule

The repository is green when all rows marked “Closed” stay green under the
full gate, installation, cold-clone, and tamper checks. Rows marked Partial or
Blocked require the named external decision; they must not be silently marked
complete by adding fixtures or hardcoded production data.
