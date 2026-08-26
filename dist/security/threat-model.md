# Runtime threat model

## Assets

### Pilot readiness and bootstrap (L11)

### Assurance, audit integrity, and recovery (L12)

Audit events form a per-tenant append-only hash chain (`previous_hash` and
`event_hash`). Database triggers reject inconsistent inserts and mutation/deletion;
security assurance recomputes the chain so direct tampering is detectable. The
hash chain provides tamper evidence, not confidentiality or an external
timestamp/notary service.

Assurance reads remain tenant-scoped; only admins can create eval/security runs.
Restore assurance is CLI-only and is created in a verified newly restored
database, so an API caller cannot forge recovery evidence. No-data evals remain
blocked rather than being passed from empty evidence. Running Assurance work has
a bounded lease: only an expired lease may be resumed, with a visible incremented
attempt count; a live lease and terminal result cannot be overwritten.

Recovery validates SHA-256 manifests, SQLite integrity/schema, all referenced
evidence objects, safe relative paths, and absence of symlinks before restoring
only to a new destination. Backup includes sensitive business data and this
tool does not encrypt it; encrypted storage, access control, retention, and key
management are external production requirements.
Verify-only restore validates only the backup and deliberately does not inspect
or overwrite the requested target. CLI failure output carries a bounded error
code/type, not filesystem paths or sensitive business contents.

`GET /v1/pilot-status` keeps the existing bearer/viewer tenant boundary. Its
closed schemas expose only current-tenant readiness, local worker heartbeat
status, and actionable blockers. Credential reporting is presence/count metadata
only: API keys, secrets, refresh tokens, OpenAI keys, Authorization
headers, and provider responses cannot enter the payload or blocker message.

A new database's one-command bootstrap prints a one-time API key once. Treat terminal
output as sensitive until captured by an approved secret manager; never place it
in a URL or browser storage. Existing databases must not silently create another
tenant/key. Configured credentials do not prove live Amazon/OpenAI authorization;
missing dependencies remain blockers, never synthetic success.

Loopback is the default bind. Public exposure requires explicit opt-in and a
TLS/authenticated proxy. SIGTERM/SIGINT must preserve durable SQLite state and
leases; an occupied port, preflight/start failure, or worker shutdown timeout
returns structured non-zero CLI output rather than a false successful launch.
This is deliberately single-process SQLite: worker heartbeats are not
distributed consensus and do not imply multiprocess coordination or availability.

### Live Mission Control stream (L10)

`GET /v1/mission-control/events` adds an authenticated SSE boundary. The API
key remains an Authorization header on a `fetch()` stream; it is never an SSE
query parameter, cursor, event field, URL, browser-storage value, referrer, or
loggable client-side token. The resumption cursor is a non-sensitive,
tenant-local monotonic integer; the internal global sequence is never exposed,
so cursor gaps cannot disclose another tenant's activity. `Last-Event-ID` takes
precedence over `after` so a client cannot accidentally resume from an
untrusted query fallback.

Event data is deliberately a closed `MissionEvent` schema: tenant cursor,
domain event type, resource id/type, current/previous status, timestamp, and
bounded safe relationship metadata only. It excludes API keys, credentials, Authorization
headers, evidence rows, action/proposal payloads, and tenant identifiers. Each
connection is authenticated and tenant-scoped before it is admitted; viewers may
read their own tenant stream, and unauthorized/forbidden requests fail with
`401`/`403`. Global and per-tenant connection caps fail closed with `429` and
`Retry-After`, mitigating connection-exhaustion attacks without silently
downgrading authorization.

Replay/backlog and stream lifetime are bounded. A retention gap yields
`mission.reset` rather than an unsafe or unbounded replay; clients refetch the
normal tenant-scoped snapshot. `mission.reconnect` carries only a bounded retry
delay, and comment-only heartbeats carry no business data. Reverse proxies must disable SSE
buffering, preserve Authorization and Last-Event-ID, terminate TLS, and avoid
request/URL logging of credentials. The current SQLite/ThreadingHTTPServer
runtime is single-process only: it has no distributed connection limiter or
cross-instance event ordering guarantee.

- Tenant identity, API keys, tenant-owned `MarketplaceAccount` records
  (provider details, credential-reference presence, and persisted health
  outcome), tenant-owned L2 report recipe configuration, synced product
  records, tenant-owned L4 metric materializations/observations, multi-agent
  evidence/artifacts, and approval/audit history.
- External platform access tokens, which must remain in a deployment secret
  manager and outside SQLite, request payloads, logs, and audit metadata.

## Trust boundaries

1. The caller crosses the HTTP boundary with a bearer API key.
2. The runtime crosses the SQLite boundary with parameterized, tenant-scoped
   queries.
3. The connector crosses the platform boundary with an environment-resolved
   token and a constrained HTTPS host.
4. The catalog and account endpoints cross the authenticated API boundary;
   account IDs must remain scoped to the caller's tenant.
5. Metric materialization crosses from immutable normalized Evidence into a
   derived metric store; source ownership, numeric bounds, currency, period,
   provenance, and quality must be revalidated at that boundary.
6. Daily Ops crosses from a schedule-local business date and selected
   tenant-owned evidence into a persisted Agent Run/brief. Timezone conversion,
   DST resolution, local-date uniqueness, source freshness, and Reviewer
   eligibility are security-relevant control inputs rather than presentation
   details.

## Controls implemented

- PBKDF2-HMAC-SHA256 API-key hashes and constant-time verification.
- Tenant foreign keys plus explicit tenant predicates on every application
  read/write.
- Daily Ops schedules, occurrences, selected Evidence/Metric Observation IDs,
  source gaps, and briefs are tenant-owned. Reader paths are tenant scoped;
  schedule writes, manual triggers, execution, and retries require an
  operator-or-higher principal. A unique schedule/local-date occurrence and
  durable worker claims prevent duplicate business-day execution on restarts or
  repeated ticks.
- Daily Ops accepts an IANA timezone plus local time. DST fall-back selects the
  first occurrence and creates one local-date run; a spring-forward gap creates
  an explicit blocked immutable occurrence requiring a new corrected schedule. UTC timestamps
  do not replace the local-date idempotency key.
- Evidence selection is bounded by the frozen UTC scheduled instant, preventing
  look-ahead from later same-day observations. A canonical hashed schedule
  snapshot prevents mutable objectives, marketplaces, selectors, or graph
  bindings from changing an existing occurrence. Per-attempt lease tokens fence
  stale workers, and a durable local-date cursor performs bounded catch-up after
  downtime.
- Daily-created Agent Runs persist parent occurrence, attempt, and internal lease
  lineage. Downstream Briefing eligibility requires the parent to be completed
  and to point to that exact final child, preventing an approved orphan from a
  stale worker from influencing operations.
- The schedule creator is the explicit background execution principal. Role
  demotion below operator is blocked while enabled or nonterminal Daily Ops work
  remains; defensive worker handling persists an inactive-principal block rather
  than crashing or bypassing authorization. Re-enabling a paused schedule
  revalidates the creator's current operator role in a database trigger, closing
  enable/demotion races; safe disable does not depend on Graph liveness.
- A completed Daily Ops operational brief is persisted only after the bound
  Domain Agent Graph ends with a final `approved` Reviewer verdict. Empty
  source selection can retain a distinct no-report empty-state brief; stale
  source selections, Reviewer revision/rejection, and execution failures remain
  explicit run states and cannot be represented as a successful brief.
- The L8 scheduler and worker commands have no model tools and no external
  marketplace, catalog, ads, or financial write operation. They are not a
  distributed worker; multi-replica deployments must operate a single
  scheduler/worker leader or equivalent external lease-aware orchestrator.
- Marketplace account list/get/create/update/health operations enforce the
  viewer/admin/operator role gates, and cross-tenant account IDs resolve to
  the same 404 as unknown IDs.
- Connector configuration is validated against the provider schema and stores
  only environment-variable references. Safe account responses replace every
  credential reference with `present`; provider details exclude credential
  values and names.
- Connector health outcomes are persisted with `health_status`,
  `health_checked_at`, `health_error_code`, and `health_error_message`.
  Amazon SP-API health calls Sellers marketplace participation, Amazon Ads
  health calls only the fixed regional Profiles endpoint and verifies the
  configured Profile ID, and Shopify health calls the configured shop
  endpoint. Failures remain visible as durable `misconfigured` or `unhealthy`
  state.
- Report recipes enforce viewer read and operator create/update gates, require
  an Amazon SP-API connector account in the same tenant, and require every
  recipe marketplace ID to be a subset of the account's configured IDs. The
  four recipe keys and their derived Amazon/evidence report types are an
  explicit allowlist; recipe writes persist configuration only and make no
  Amazon request.
- Report synchronizations are tenant-owned durable records. Enqueue requires an
  operator-or-higher caller, an idempotency key, an enabled recipe, and a
  currently healthy linked Amazon account. Workers claim work with bounded
  leases and attempts, persist every provider state, honor bounded
  `Retry-After`, and never convert an exhausted or fatal attempt into success.
- Amazon report documents are accepted only after the allowlisted report flow
  reaches `DONE`. Sales/traffic JSON and TSV documents are normalized under
  byte, row, column, depth, and finite-number bounds before creating a
  tenant-owned Evidence import. `CANCELLED`, `FATAL`, malformed, or oversized
  documents remain visible durable failures.
- L3 report syncs require operator/owner authorization and an idempotency key;
  they require a healthy linked account, persist bounded attempts and status,
  honor provider `429`/`Retry-After`, and keep Amazon report IDs, processing
  states, Evidence import IDs, and terminal errors tenant-scoped.
- L4 observations and materializations are durable tenant-owned rows. Every
  get/list/materialize/backfill query includes the authenticated `tenant_id`;
  cross-tenant observation and import IDs fail as `404`. Viewer roles may read,
  operator-or-higher roles may materialize one import with an idempotency key,
  and only admin/owner roles may run bounded cursor backfills.
- Metric values use bounded exact Decimal strings (38 significant digits,
  scale 9). Non-finite, exponent-form, overflow, and excessive-scale inputs fail
  validation rather than becoming platform floats or silently rounded values.
- Accepted observations retain period start/end, grain, source import/SHA,
  source row/field, mapping version, bounded dimensions, and quality flags.
  These fields make derived values traceable without copying raw Evidence into
  API responses.
- Monetary observations require an explicit ISO 4217 source currency. Missing
  currency rows are quarantined without an observation, and currency remains a
  storage/query partition. Tenant locale, marketplace region, and neighboring
  rows are not trusted currency sources; L4 performs no FX conversion or cross-
  currency aggregation.
- L3 Evidence and L4 materialization use separate durable commit boundaries.
  A failed or quarantined materialization cannot roll back, delete, or relabel
  an already successful report sync or Evidence import. The failure remains
  explicit in `MetricMaterialization` and recovery uses an authorized retry or
  bounded backfill.
- Backfill is never implicit: an admin supplies a tenant-scoped cursor and a
  limit of 1–100. Startup, reads, UI refresh, and scheduler activity do not scan
  old imports. Production paths consume persisted Evidence only and contain no
  runtime mock-data fallback.
- Report documents are bounded before ingestion: sales/traffic JSON is
  flattened with depth/row/byte limits and other supported formats use bounded
  TSV parsing. `DONE` is the only state that can produce an Evidence import;
  `CANCELLED` and `FATAL` remain failed.
- Explicit SQLite schema versioning; unsupported newer schemas fail closed.
- Viewer/operator/admin/owner role checks; approval requires a second actor.
- Tenant-scoped user provisioning is exposed through authenticated admin APIs;
  role assignment is capped at the caller's role, owner changes require an
  owner, self-role changes fail, and the last owner cannot be demoted.
- Idempotency uniqueness per tenant and compare-and-set action transitions.
- Bounded execution leases, attempt counters, and explicit retry transitions;
  expired work is not silently treated as successful.
- HTTPS-only `*.myshopify.com` endpoint validation, bounded page size, and a
  30-second network timeout.
- JSON request IDs and append-only audit events for action/connector outcomes.
- Structured JSON logs and process counters for request/error monitoring.
- Loopback-only default bind plus explicit opt-in for non-loopback exposure;
  in-process per-client rate limiting returns 429 with `Retry-After`.
- Package SHA-256 manifest validation before MCP capabilities are exposed.
- Multi-agent evidence rejects secret-shaped fields, carries explicit source IDs,
  ontology platform IDs, and observation timestamps, and remains tenant scoped across runs, tasks,
  artifacts, and events.
- Specialist and manager outputs are structured and fail when they cite unknown
  evidence or assign one marketplace's evidence to another marketplace. Model
  credentials remain environment-only, and reports cannot call
  marketplace write tools directly.
- CSV/XLSX evidence is parsed locally, archive/size/row/column bounded, SHA-256
  identified, and stored as tenant-owned normalized rows plus content-addressed
  original bytes. Common buyer PII and secret-shaped columns fail closed;
  formulas remain inert strings and are counted. XLSX macros, encrypted archives,
  unsafe ZIP paths, and oversized decompressed content fail closed.
- Amazon SP-API credentials remain environment references. The connector uses a
  short-lived LWA access token in memory, validates region endpoints and report
  identifiers, restricts pre-signed downloads to HTTPS Amazon/S3/CloudFront
  hosts on the standard HTTPS port, and bounds both compressed and decompressed
  bytes.
- Background jobs and schedules are tenant-owned and created by an authorized
  user. Workers reconstruct that user's current role, claim work with a bounded
  lease, use idempotency keys per occurrence, and persist retry/failure state.
- The Mission Control shell has a restrictive CSP, no inline scripts/styles, no
  runtime third-party requests, no browser persistence for API keys, and
  authenticated same-origin data calls. The static shell contains no tenant
  data. Phosphor and Simple Icons assets are vendored with their licenses, and
  the generated Commerce Agent OS mark is packaged locally.
- The operating brief is a tenant-scoped read model over persisted Metric
  Observations. It never reparses Evidence rows, keeps currency/dimension/grain
  series isolated, caps history, and does not infer or hardcode production
  business metrics.
- Synthetic product-tour data is reachable only through the explicit
  `demo-seed` CLI, which requires a nonexistent database path and creates a
  tenant marked `demo`. The UI keeps the warning visible and normal onboarding
  always creates `production` tenants.
- The separate `demo` server accepts only one Demo tenant, has no public-bind
  option, exposes its temporary Reviewer key only on loopback with `no-store`,
  and revokes that key at shutdown. Normal `api` processes return 404 for the
  bootstrap route and keep bearer authentication mandatory.

## L5 Ads gate controls

Amazon Ads gates are tenant-scoped and read-only. Persist only redacted request
IDs and opaque attestation references; never persist LWA secrets, access tokens,
or profile payloads. `passed` requires live probe evidence plus external
approval and is the hard authorization boundary for L6.

## Residual risks and required deployment controls

- The reference API is HTTP-only and loopback by default: use TLS termination,
  a WAF/rate limiter, and an identity provider for internet-facing deployments.
- SQLite is not a high-availability store: schedule encrypted backups and use
  the Postgres adapter before multi-process scale-out.
- Environment references are safer than plaintext tokens but are not a KMS:
  inject them from a managed secret store and rotate them outside the app.
- Connector actions are intentionally read-only. Any future write action must
  add a separate operation allowlist, risk classification, approval policy,
  dry-run response, and rollback/reconciliation design.
- L1 connector accounts intentionally have no OAuth connect flow, delete
  operation, or background health scheduler. Health is an explicit synchronous
  caller action; adding automation requires a separate lease, authorization,
  retry, and audit design.
- L2 report recipes intentionally have no delete endpoint, OAuth flow, Amazon
  report creation/download, or background execution. `next_run_at` is stored
  configuration until a separately authorized scheduler contract exists.
- L3 report syncs remain read-only against Amazon and are triggered explicitly.
  L8 selects already persisted eligible Evidence and does not implicitly create
  an Amazon report; report-sync cadence remains an explicit operator concern. Live end-to-end assurance
  still depends on seller-authorized Amazon credentials and marketplace access,
  so CI validates the network boundary with injected transports rather than
  fabricated accounts.
- L3 syncs intentionally do not write to Amazon or automatically schedule
  recipes; the report worker is explicit and bounded. Live smoke validation
  remains dependent on real credentials and seller marketplace participation.
- L4 intentionally performs no FX conversion, cross-currency aggregation,
  inferred currency repair, automatic historical scan, or mutation of source
  Evidence. Adding any of these requires a separately reviewed policy, data
  lineage, authorization, and reconciliation design.
- L5 cannot independently verify the truth of an administrator-supplied
  attestation reference. Deployments must reconcile that opaque reference with
  Amazon approval records or their governance system before relying on a
  `passed` gate; API read success alone is insufficient.
- Agent prompts receive user evidence as untrusted data. Operators must still
  avoid placing personal data or secrets in evidence values; the first slice
  detects secret-shaped field names but is not a general DLP system.
- CSV header screening is also not a complete PII classifier. Sellers remain
  responsible for exporting the minimum necessary fields and for applicable
  marketplace, privacy, and retention obligations.
- The embedded content-addressed store is filesystem encryption dependent. Cloud
  deployment still requires encrypted object storage, per-tenant authorization,
  retention/deletion policy, malware scanning, and KMS-managed keys.
- Restricted Amazon reports and RDT/PII access are intentionally absent. Adding
  them requires approved Amazon roles, a dedicated data-classification contract,
  stronger DLP, retention controls, and a separate threat-model review.
- Bearer-key entry is acceptable only for the loopback embedded UI. Hosted UI
  authentication still requires TLS, external identity, secure HttpOnly session
  cookies, CSRF protection, and session revocation.

## L6 negative boundary

The conditional Ads adapter status is fail-closed: only `blocked` and
`eligible_not_installed` are representable, `adapter_registered` is fixed to
false, and the write-operation list is empty. A maximum 24-hour gate age plus
tenant-owned account, required-capability, account-update, Profile, and region
checks prevents stale or cross-tenant L5 evidence from becoming write
authorization. No Ads write
adapter, route, or action is registered. Future writes require a proposal,
explicit approval, audit/idempotency controls, and rollback review.
# L7 threat model

- Tenant isolation: every graph, version, verdict, run, and observation reference is tenant-scoped and authorization checked.
- Prompt/tool safety: graph tool policy is structurally empty and capped at zero; connector writes cannot be reached through model tools.
- Supply-chain safety: published DAGs are immutable and their definition hash
  is bound to an execution-contract fingerprint over orchestration code,
  ontology, and Skill manifests. Package drift fails closed until an admin
  publishes a newly reviewed version.
- Evidence integrity: specialists consume a persisted Evidence/Metric Observation snapshot; the manager cannot silently substitute live values.
- Separation of duties: Manager synthesis and the independent AI Reviewer are
  separate calls/tasks; non-approved runs, rather than graph versions, are
  rejected by the current Briefing read model and must remain rejected by future
  L8/L9 consumers. This Reviewer does not replace the
  human approval required for any external write.
- Deterministic review guards require structured Manager action type and Metric
  claims, enforce human approval on every L7 priority, reject multi-source
  `observe` claims plus incompatible or
  overlapping Metric aggregation, and require an approved Reviewer to cover
  every Manager Evidence reference and verbatim limitation. Briefing rechecks
  the final run-attempt report plus current Reviewer task-attempt, graph, and
  verdict lineage rather than trusting one status field; pre-L7 runs migrate as
  pending and retry history remains auditable.
- The default Reviewer uses the same configured provider, model, and credential
  trust domain as the Manager. It is an independent execution stage, not an
  independent vendor or security boundary; higher-assurance deployments need a
  separately configured Reviewer provider plus human approval for writes.
- L7 accepts only the reviewed canonical topology. Its executor is not a
  general-purpose arbitrary-DAG engine; adding nodes or edges requires a new
  execution, validation, migration, and threat-model review.

# L9 proposal threat model

- Lineage integrity: proposal creation derives Daily Ops, approved Agent Run,
  graph/hash, source priority, Evidence, Metric Observation, and payload hash
  inside the tenant boundary. Client-provided IDs cannot point to another
  tenant or an unreviewed run.
- Decision integrity: local `human.review` decisions are append-only and use
  optimistic proposal versions. The requester cannot self-approve; stale
  revision or decision attempts conflict instead of overwriting a reviewed
  payload.
- Execution integrity: each execution snapshots the approved proposal version
  and payload hash, is idempotent, lease-fenced, audited, and delegates only to
  existing safe read ActionService operations. A changed, expired, rejected,
  revision-required, or insufficiently approved proposal fails closed.
- Capability safety: expiry is included in every immutable version content hash.
  Execution rechecks same-tenant connector health and produces a durable
  `CONNECTOR_CAPABILITY_UNAVAILABLE` block before a connector call. The
  representable Amazon Ads campaign operation always returns
  `AMAZON_ADS_CAPABILITY_UNAVAILABLE` with `connector_calls=0`.
- Boundary: `human.review` is a local application control, not a substitute
  for real identity assurance, change-management, marketplace permission, or
  external Ads approval. L9 registers no generic marketplace write and no
  Amazon Ads write adapter, route, or operation; Amazon Ads remains blocked
  with zero write calls.
