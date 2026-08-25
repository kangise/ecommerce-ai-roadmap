# Runtime threat model

## Assets

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

## Controls implemented

- PBKDF2-HMAC-SHA256 API-key hashes and constant-time verification.
- Tenant foreign keys plus explicit tenant predicates on every application
  read/write.
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
- L3 report syncs remain read-only against Amazon and are triggered explicitly;
  automatic recipe scheduling is deferred to L8. Live end-to-end assurance
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
