# Runtime threat model

## Assets

- Tenant identity, API keys, tenant-owned `MarketplaceAccount` records
  (provider details, credential-reference presence, and persisted health
  outcome), tenant-owned L2 report recipe configuration, synced product
  records, multi-agent evidence/artifacts, and approval/audit history.
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
  Amazon health calls the real Sellers marketplace-participation endpoint for
  configured IDs; Shopify health calls the configured shop endpoint. Failures
  remain visible as durable `misconfigured` or `unhealthy` state.
- Report recipes enforce viewer read and operator create/update gates, require
  an Amazon SP-API connector account in the same tenant, and require every
  recipe marketplace ID to be a subset of the account's configured IDs. The
  four recipe keys and their derived Amazon/evidence report types are an
  explicit allowlist; recipe writes persist configuration only and make no
  Amazon request.
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
  hosts, and bounds both compressed and decompressed bytes.
- Background jobs and schedules are tenant-owned and created by an authorized
  user. Workers reconstruct that user's current role, claim work with a bounded
  lease, use idempotency keys per occurrence, and persist retry/failure state.
- The Mission Control shell has a restrictive CSP, no inline scripts/styles, no
  runtime third-party requests, no browser persistence for API keys, and
  authenticated same-origin data calls. The static shell contains no tenant
  data. Phosphor and Simple Icons assets are vendored with their licenses, and
  the generated Commerce Agent OS mark is packaged locally.
- The operating brief is a tenant-scoped read model. It parses only recognized
  numeric Evidence columns, preserves source-currency ambiguity, caps history,
  and does not infer or hardcode production business metrics.
- Synthetic product-tour data is reachable only through the explicit
  `demo-seed` CLI, which requires a nonexistent database path and creates a
  tenant marked `demo`. The UI keeps the warning visible and normal onboarding
  always creates `production` tenants.
- The separate `demo` server accepts only one Demo tenant, has no public-bind
  option, exposes its temporary Reviewer key only on loopback with `no-store`,
  and revokes that key at shutdown. Normal `api` processes return 404 for the
  bootstrap route and keep bearer authentication mandatory.

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
