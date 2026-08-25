# Runtime API

The Python package includes a small authenticated JSON API for the production
vertical slice. It persists tenant-owned connector records and action state in
SQLite, and is intentionally separate from the read-only MCP adapter. It also
provides a durable, platform-aware `weekly_ops` workflow: an evidence analyst and
one specialist per marketplace run in parallel; multi-platform runs add a
cross-platform controller before the store manager synthesizes the final work.

## Start

```bash
python3 -m pip install .
opc-ecommerce init --db ./runtime.sqlite --name "Example shop" --email owner@example.com
# Save the one-time eai_... API key in a secret manager.
opc-ecommerce api --db ./runtime.sqlite --host 127.0.0.1 --port 8787
```

To execute agent runs, inject both variables through the deployment secret and
configuration system. The runtime has no default model and never stores the key:

```bash
export OPENAI_API_KEY='<REAL_OPENAI_API_KEY>'
export EAI_OPENAI_MODEL='<RESPONSES_API_MODEL_WITH_STRUCTURED_OUTPUTS>'
```

The MCP SDK is optional: install `ecommerce-ai-skills[mcp]` only when the
stdio MCP adapter is needed. The Runtime API itself does not require it.

The default bind address is loopback. Put a managed TLS/authenticated reverse
proxy in front of any non-local deployment; the server does not terminate TLS.
Non-loopback binding requires the explicit `--allow-public` flag so an
accidental startup cannot expose bearer keys on plain HTTP.
See `openapi/runtime-api.yaml` for the request contract.
Use `/healthz` for process liveness and `/readyz` for SQLite/schema readiness.

Open `http://127.0.0.1:8787/app` for the packaged Mission Control UI. The
Amazon-first daily brief keeps Amazon, Shopify, Walmart, and TikTok Shop in the
top platform switcher; Evidence, Agent Runs, Approvals, Automations, Jobs, and
Audit remain available through the left navigation. Its static shell is
unauthenticated, but every data request uses the supplied tenant API key. The
key remains only in page memory and is cleared on reload/disconnect; the app
never writes it to browser storage, cookies, or the DOM.

## Explicit Demo data

For the zero-setup product tour, run the dedicated loopback-only Demo server:

```bash
opc-ecommerce demo --db ./commerce-agent-demo.sqlite --port 8788
```

If the path does not exist, the command seeds it; an existing path must contain
exactly one Demo tenant. The command has no public-bind option. It creates a
temporary Reviewer key, exposes it only through the loopback
`/v1/demo-session` bootstrap, keeps it in page memory, and revokes it when the
Demo server stops. The browser therefore opens with data immediately without
weakening normal API authentication.

For seed-only/manual-key workflows, use `opc-ecommerce demo-seed --db
./commerce-agent-demo.sqlite`; it refuses every existing file and never adds
sample rows to a real tenant database. The seed creates a tenant with
`tenant_mode=demo`, seven Amazon
Business observations, Ads/FBA/Shopify Evidence, a completed cross-platform
Weekly Ops run, a passing Eval, two requested Actions, a completed Job, a future
Schedule, and Audit events. The one-time JSON output contains Owner and Reviewer
keys; connect the UI with the Reviewer key to exercise the real second-actor
approval flow. Mission Control displays a permanent `DEMO DATA` label and
warning whenever `/v1/me` reports a Demo tenant.

Demo values are synthetic seed fixtures and must never be used for business
decisions, model evaluation, benchmarks, or production screenshots without the
visible Demo warning.

## Security contract

- API keys are PBKDF2-HMAC-SHA256 hashes; the clear key is printed only by
  `init` and is never stored in SQLite.
- `POST /v1/api-keys/rotate` issues a replacement before revoking the current
  key; the service refuses to revoke a tenant's last active key.
- Admin/owner users can issue and revoke tenant keys; list responses contain
  prefixes and metadata only, never secret material.
- Admin/owner users can list and create tenant users through `/v1/users`.
  Callers cannot assign a role above their own; only owners can create another
  owner, self-role changes are rejected, and the last owner cannot be demoted.
- Every application row has a `tenant_id`; reads and writes require the
  authenticated principal's tenant.
- Tenants carry an explicit `production` or `demo` mode. Normal onboarding is
  always `production`; only the explicit seed command can create Demo mode.
- Roles are `viewer`, `operator`, `admin`, and `owner`.
- Connector configuration stores an environment-variable reference, never a
  Shopify token. The variable must be present when an action executes.
- Mutating work is requested with an `Idempotency-Key`, approved by a second
  admin/owner, then executed. A failed external call is recorded as failed and
  returned as an error; it is never reported as success.
- Each execution claims a bounded lease and increments `attempt_count`. A
  failed or expired execution can be explicitly re-queued through
  `POST /v1/actions/{id}/retry`; approval is never skipped.
- Audit events include tenant, actor, request id, action, resource, outcome,
  and metadata. They are append-only through the runtime service.
- `/v1/metrics` exposes disposable process counters (`http_requests_total` and
  `http_errors_total`) for smoke monitoring; it is not a source of business
  or marketplace metrics.
- The embedded API applies a per-client in-process request budget (120 requests
  per minute by default). It is a safety floor, not a distributed quota.
- Shopify pagination is persisted per tenant/account, so a restart resumes from
  the last cursor rather than silently dropping later pages.
- Multi-agent evidence is tenant-owned and rejects fields that look like tokens,
  passwords, secrets, credentials, or authorization material.
- Agent findings and final priorities must cite supplied `source_id` values.
  Unknown or missing evidence references fail the run instead of being accepted.
- Each specialist receives the installed manifests for its assigned domain Skills,
  so required inputs, outputs, platforms, entities, and constraint IDs come from
  the generated package rather than a second hardcoded capability catalog.

## Weekly Ops Council

Creating a run is durable and does not spend model tokens. Supply real exported
or connector-derived evidence; every source needs a stable ID, ontology platform
ID, type, timezone-aware observation time, and non-empty data. A run can cover up
to five marketplaces plus shared `cross_platform` evidence, but shared evidence
cannot replace at least one marketplace-specific source.

Supported marketplace IDs come from `ontology.json`: `amazon`, `shopify`,
`tiktok_shop`, `walmart`, `temu`, `shopee`, `lazada`, `mercado_libre`, `rakuten`,
`ebay`, `aliexpress`, `coupang`, `faire`, `otto`, and `zalando`. The OpenAPI enum
is checked against that ontology in CI.

For Amazon, use real exports such as Business Reports, Ads search-term or campaign
reports, FBA inventory, returns/feedback, and listing/catalog data. The Amazon
operator receives every installed Skill whose manifest supports Amazon. Other
platform operators are built through the same manifest-driven rule; unsupported
domains become explicit gaps rather than borrowed Amazon behavior.

### Import CSV or XLSX evidence

The preferred path is to upload a real export once, then reference its durable ID.
CSV/TSV support has no extra dependency. XLSX support is optional:

```bash
python3 -m pip install 'ecommerce-ai-skills[xlsx]'
```
The first typed Amazon importers are:

- `amazon_business_report`
- `amazon_ads_search_term`
- `amazon_fba_inventory`
- `amazon_returns`
- `amazon_listing`

All ontology marketplaces can use `platform_generic` when no typed parser exists.
Typed Amazon reports must contain their expected semantic columns. Values remain
strings exactly as exported; the importer never manufactures or silently coerces
business metrics. The first typed validators recognize normalized English report
headers; localized headers should use a reviewed preprocessing step or
`platform_generic` until a locale-specific alias set is implemented.

```bash
curl -fsS http://127.0.0.1:8787/v1/evidence-imports \
  -H 'Authorization: Bearer <OPERATOR_API_KEY>' \
  -H 'Idempotency-Key: amazon-business-<PERIOD>' \
  -H 'Content-Type: text/csv' \
  -H 'X-Evidence-Platform: amazon' \
  -H 'X-Evidence-Type: amazon_business_report' \
  -H 'X-Evidence-Filename: business-report.csv' \
  -H 'X-Evidence-Observed-At: <ISO_8601_TIMESTAMP_WITH_TIMEZONE>' \
  --data-binary '@<REAL_AMAZON_EXPORT.csv>'
```

CSV/TSV uploads are capped at 2 MB; XLSX at 5 MB and 50 MB uncompressed. Both are
limited to 5,000 rows, 200 columns, and 800 KB after normalization. UTF-8 is
required for delimited text. XLSX accepts `.xlsx` only—macros and encrypted
workbooks fail. Use `X-Evidence-Sheet` to select a worksheet.

Imports reject secret-shaped and common buyer PII columns. Formula-like cells
are counted and preserved as inert strings, never executed. Original bytes are
stored in a tenant-scoped, content-addressed directory beside the SQLite database
with SHA-256 integrity; the database stores only its relative object key.
`GET /v1/evidence-imports` returns metadata without parsed rows or file bytes.

Create a run from one or more imports:

```json
{
  "workflow": "weekly_ops",
  "objective": "Find the most important evidence-backed actions for this week.",
  "evidence_import_ids": ["<EVIDENCE_IMPORT_ID>"]
}
```

Inline `evidence` remains supported and may be combined with import IDs.

## Background jobs and schedules

Create an agent run, then enqueue it through `POST /v1/jobs`. A worker claims
jobs with a bounded lease, persists attempts, and retries failures with bounded
exponential backoff up to `max_attempts`:

```bash
opc-ecommerce worker --db ./runtime.sqlite
```

Interval schedules materialize durable runs and jobs. Use selectors to resolve
the newest matching Evidence Import at each occurrence instead of pinning a
stale file forever:

```json
{
  "name": "Amazon weekly review",
  "objective": "Review the latest Amazon operating evidence.",
  "evidence_selectors": [
    {"platform": "amazon", "report_type": "amazon_business_report"},
    {"platform": "amazon", "report_type": "amazon_ads_search_term"}
  ],
  "interval_minutes": 10080,
  "next_run_at": "<ISO_8601_TIMESTAMP_WITH_TIMEZONE>"
}
```

Run the scheduler as a separate process:

```bash
opc-ecommerce scheduler --db ./runtime.sqlite
```

Both commands support `--once` for supervisors and smoke checks. Schedule and
job state is tenant-owned, lease-safe, refresh-safe, and visible through
`/v1/schedules`, `/v1/jobs`, and `/v1/jobs/{id}`.

## Mission Control API

`GET /v1/mission-control` returns real persisted counts, recent runs, failed
runs/jobs, schedules, and the approval inbox. `GET /v1/approvals` is restricted
to admin/owner roles and returns requested Actions awaiting a second actor.

`GET /v1/briefing?platform=amazon` is the evidence-backed read model for the
designed daily brief. It calculates only metrics whose recognized fields exist
in tenant-owned imports: sales, units, sessions, unit/session conversion, ad
spend, zero-fulfillable inventory counts, returns, and listing rows. Amounts
retain the report's source currency because currency metadata is not invented.
Each metric links to its source import and includes at most seven real
observations. Agent priorities come from the latest completed persisted Weekly
Ops report; the roster comes from persisted tasks; the decision rail contains
real requested Actions. Missing compatible Evidence produces an explicit empty
state instead of synthetic dashboard values.

`GET /v1/catalog` supplies the UI's platform, Evidence report, workflow, and
Action registries from live runtime sources. The packaged application supports
real Evidence upload, Run creation/execution/queueing/evaluation, Schedule
creation/toggling, Action approval, Job/Audit inspection, and visible
loading/empty/error states. The home screen is a responsive operating brief,
not a feature inventory; setup forms remain in their dedicated navigation views.

## Workflow evaluations

`POST /v1/agent-runs/{id}/evaluate` runs deterministic graders against a
completed Weekly Ops artifact and persists the result. The current evaluator
checks completed tasks, priority shape, evidence references, platform isolation,
owner assignment, and approval policy. `GET /v1/agent-runs/{id}/evaluations`
returns its history; failed evaluation counts appear in Mission Control.

These checks evaluate enforceable workflow contracts, not whether a business
recommendation will increase revenue. Provider/model comparisons still require
representative real-store datasets and live runs.

```bash
curl -fsS http://127.0.0.1:8787/v1/agent-runs \
  -H 'Authorization: Bearer <OPERATOR_API_KEY>' \
  -H 'Idempotency-Key: weekly-<PERIOD>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workflow":"weekly_ops",
    "objective":"Find the most important evidence-backed actions for this week.",
    "evidence":[{
      "source_id":"amazon-business-report-<EXPORT_DATE>",
      "platform":"amazon",
      "source_type":"amazon_business_report",
      "observed_at":"<ISO_8601_TIMESTAMP_WITH_TIMEZONE>",
      "data":[{"asin":"<REAL_ASIN>","ordered_product_sales":"<REAL_EXPORTED_VALUE>"}]
    }]
  }'
```

Execute the returned run ID explicitly:

```bash
curl -fsS -X POST http://127.0.0.1:8787/v1/agent-runs/<RUN_ID>/execute \
  -H 'Authorization: Bearer <OPERATOR_API_KEY>'
```

`GET /v1/agent-runs` lists compact run metadata. `GET /v1/agent-runs/{id}`
returns the persisted tasks, evidence-bound artifacts, and event timeline.
Operations UIs can poll `GET /v1/agent-runs/{id}/events?after=<cursor>` for
incremental events without reloading the full bundle.
Execution is read-only: a report may describe a downstream action and mark it
`requires_approval`, but only the existing approved Action service can perform
an external side effect.

## Create the second actor

`init` creates the first owner. Create a separate administrator before using
the approval workflow; do not share the owner key between two people.

```bash
curl -fsS http://127.0.0.1:8787/v1/users \
  -H 'Authorization: Bearer <OWNER_API_KEY>' \
  -H 'Content-Type: application/json' \
  -d '{"email":"approver@example.com","role":"admin"}'

curl -fsS http://127.0.0.1:8787/v1/api-keys \
  -H 'Authorization: Bearer <OWNER_API_KEY>' \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"<USER_ID_FROM_PREVIOUS_RESPONSE>"}'
```

The second response contains the administrator's API key once. Deliver it
through a secret manager. `GET /v1/users` returns tenant user metadata without
keys, and `PATCH /v1/users/{user_id}` changes a role subject to the safeguards
above.

## Approval sequence

1. An operator or owner creates an action with a unique `Idempotency-Key`.
2. A different admin or owner calls `/v1/actions/{id}/approve` with their own key.
3. An operator or owner executes the approved action.
4. All four user/key/action events remain available through `/v1/audit`.

## Connector example

Register metadata (no secret in the payload):

```json
{
  "provider": "shopify",
  "external_account_id": "primary",
  "config": {
    "shop_domain": "shop-name.myshopify.com",
    "api_version": "2025-10",
    "credential_ref": "SHOPIFY_ADMIN_TOKEN"
  }
}
```

Then set `SHOPIFY_ADMIN_TOKEN` through the deployment secret manager. The only
currently implemented action is the read-only `shopify.sync_products`, which
stores the returned product records under the current tenant.

### Amazon SP-API Reports connector

Register only environment references and non-secret account metadata:

```json
{
  "provider": "amazon_spapi",
  "external_account_id": "primary-us",
  "config": {
    "region": "na",
    "marketplace_ids": ["<REAL_MARKETPLACE_ID>"],
    "lwa_client_id_ref": "AMAZON_LWA_CLIENT_ID",
    "lwa_client_secret_ref": "AMAZON_LWA_CLIENT_SECRET",
    "lwa_refresh_token_ref": "AMAZON_LWA_REFRESH_TOKEN"
  }
}
```

Set those variables through the deployment secret manager. The connector uses
the LWA refresh-token exchange and passes the short-lived token only in the
`x-amz-access-token` header. It supports the official `na`, `eu`, and `fe`
endpoints and never persists refresh, client-secret, or access-token values.

The first approved action retrieves an already completed, non-restricted,
delimited report and converts it into a durable Evidence Import:

```json
{
  "operation": "amazon_spapi.import_report",
  "payload": {
    "external_account_id": "primary-us",
    "report_id": "<REAL_COMPLETED_REPORT_ID>",
    "evidence_report_type": "amazon_listing"
  }
}
```

Submit this through `/v1/actions`, approve it with a second admin/owner, then
execute it. The connector checks `processingStatus=DONE`, follows the report
document flow, permits only HTTPS Amazon/S3/CloudFront hosts, bounds downloads
and GZIP expansion, and delegates semantic CSV validation to the Evidence layer.

This slice deliberately does not create reports, access Restricted Data Tokens
or PII reports, call Amazon Ads, or support XML/JSON report documents. Those
remain separate connector increments with their own permissions and contracts.

The SQLite schema carries an explicit schema version and fails closed if a
newer unsupported version is opened. Schema upgrades must be shipped as a
reviewed migration, never as an ad-hoc table edit.

## Known boundary

SQLite is the first deployable adapter, suitable for one process and a small
installation. A multi-process/high-availability deployment still needs a
Postgres adapter, managed secret/KMS integration, TLS termination, distributed
rate limiting, backup/restore drills, and an external identity provider. Those
are tracked as deployment decisions rather than hidden behind mock
implementations.

User provisioning is intentionally administrator-driven. The embedded runtime
does not send invitation email, recover accounts, implement SSO, or delete
users; revoke that user's keys when access must be removed. Those lifecycle
features belong to the external identity decision for an internet-facing SaaS.

Agent execution is synchronous in this embedded slice. It does not yet provide
a worker queue, schedules, WebSocket event streaming, browser upload UI, or a
visual operations board. Evidence must be supplied by the authenticated caller,
and live OpenAI verification requires the caller's real API key and selected
Responses-compatible model.
