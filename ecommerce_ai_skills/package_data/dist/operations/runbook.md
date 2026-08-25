# Runtime operations runbook

## Health and startup

```bash
opc-ecommerce api --db /var/lib/ecommerce-ai/runtime.sqlite --host 127.0.0.1 --port 8787
curl -fsS http://127.0.0.1:8787/healthz
curl -fsS http://127.0.0.1:8787/readyz
```

The process must fail to start only for an invalid database path or schema
error. Connector failures are returned per action and recorded as `failed`.

Mission Control is served at `/app`. For the embedded loopback deployment, open
the connection dialog and paste a tenant API key; it stays in page memory only.
The daily brief is platform-filtered and derives every visible metric from
recognized fields in persisted Evidence. If a chart or Agent Brief is empty,
import the named report type or complete a Weekly Ops run—do not seed dashboard
values to make the screen appear populated. For a hosted deployment, replace
this bootstrap flow with the selected external identity provider and secure
sessions behind TLS.

For product tours, run `opc-ecommerce demo --db <demo.sqlite> --port 8788`.
It seeds a missing path, accepts only a single Demo tenant in an existing path,
binds only to loopback, and automatically opens a temporary Reviewer session in
the UI. The temporary key is revoked when the process stops. Keep the `DEMO
DATA` banner in screenshots, and remove the whole Demo database plus its
`.evidence_objects` directory when the tour environment is retired.

## Tenant onboarding

1. Run `opc-ecommerce init` once and put the returned owner key in a secret manager.
2. Use `POST /v1/users` to create a separate administrator or operator.
3. Use `POST /v1/api-keys` to issue that user a one-time key and deliver it through the secret manager.
4. Confirm `GET /v1/users` shows the intended role before registering a connector.
5. Keep at least two authorized people when second-actor approval is required; never share one key to simulate two actors.

Role changes use `PATCH /v1/users/{user_id}`. A caller cannot assign a role
higher than their own, cannot change their own role, and cannot demote the last
owner. User creation and role changes are audit events.

## Marketplace connector accounts (L1)

Connector accounts are durable and tenant-scoped. Use the catalog before
onboarding to discover the supported providers and Amazon marketplace
directory:

```bash
curl -fsS http://127.0.0.1:8787/v1/catalog \
  -H 'Authorization: Bearer <VIEWER_API_KEY>'
```

The catalog's `connector_providers` entries contain `id`, `name`,
`detail_fields`, and `credential_fields`; `amazon_marketplaces` entries contain
`id`, `name`, `country_code`, and `region`. The current providers are
`amazon_spapi` and `shopify`.

Role gates are explicit: `viewer` can list/read accounts, `admin` (and owner)
can create/update them, and `operator` (plus admin/owner) can run a health
check. The response is a safe `MarketplaceAccount`: provider details are
non-secret, and `credential_refs` maps each configured credential field to
`present`; no credential value or environment-variable name is returned.

Create with a full provider configuration. Every credential field must be an
environment-variable reference, and the referenced variable must be supplied
by the deployment secret manager—not in JSON or SQLite as a secret:

```bash
curl -fsS -X POST http://127.0.0.1:8787/v1/connectors \
  -H 'Authorization: Bearer <ADMIN_API_KEY>' \
  -H 'Content-Type: application/json' \
  -d '{
    "provider": "shopify",
    "external_account_id": "primary",
    "config": {
      "shop_domain": "shop-name.myshopify.com",
      "api_version": "2025-10",
      "credential_ref": "SHOPIFY_ADMIN_TOKEN"
    }
  }'
```

`PATCH /v1/connectors/<ACCOUNT_ID>` requires `config`; it accepts an optional
`external_account_id` and otherwise keeps the existing identifier. Updating
the account resets `health_status` to `unchecked` and clears the previous
health timestamp and error fields. There is no connector delete endpoint in
L1.

Run health checks explicitly; they are synchronous and do not run in the
background. Amazon checks LWA credentials and the real Sellers API
`/sellers/v1/marketplaceParticipations` response for configured marketplace
participation. Shopify reads the configured shop's shop.json endpoint. A
failed check is still a durable result: `misconfigured` is used for
`missing_credential` or `invalid_configuration`, and `unhealthy` is used for
`external_service_error`. Inspect `health_checked_at`, `health_error_code`,
and `health_error_message` after the call and after a restart.

```bash
curl -fsS -X POST \
  http://127.0.0.1:8787/v1/connectors/<ACCOUNT_ID>/health-check \
  -H 'Authorization: Bearer <OPERATOR_API_KEY>' \
  -H 'Content-Type: application/json' \
  -d '{}'
```

An account ID from another tenant returns `404`; do not infer whether it
exists from a different status or attempt to bypass that boundary. OAuth
connect flows, connector deletion, and scheduled/background health checks are
outside L1.

## Multi-agent runs

- Set `OPENAI_API_KEY` only in the deployment secret manager and set
  `EAI_OPENAI_MODEL` explicitly. Neither value is persisted in SQLite.
- Create a `weekly_ops` run with a unique idempotency key, then call its
  `/execute` endpoint. Creation itself does not call a model.
- A completed run is idempotent: another execute call returns the persisted
  bundle. A failed run is retried only by another explicit execute call.
- Inspect `GET /v1/agent-runs/{id}` for task failures and use
  `/v1/agent-runs/{id}/events?after=<cursor>` for incremental event polling.
  Missing credentials leave a requested run untouched; provider or invalid
  evidence-reference failures persist the run as `failed`.
- Reports are advisory artifacts. Any later marketplace write must become a
  separate Action and pass the existing approval boundary.

## Worker and scheduler

Run `opc-ecommerce worker --db <path>` and `opc-ecommerce scheduler --db <path>`
as separate supervised processes. Use `--once` in cron, Kubernetes Jobs, or
health automation. Jobs use leases and bounded retries; expired leases can be
claimed again. Schedules also use leases so multiple scheduler processes do not
materialize the same occurrence twice.

Inspect `/v1/jobs`, `/v1/schedules`, and `/v1/mission-control` during incidents.
A failed job remains durable after its final attempt. A schedule selector that
has no matching Evidence Import fails visibly and remains due for a later retry.

Evaluate representative completed runs after prompt, model, Skill, routing, or
policy changes. A failed evaluation is not retried into success; inspect its
individual checks, correct the workflow, rerun with the same evidence, and keep
the earlier failure as regression history.

## Evidence imports

- Upload CSV/TSV/XLSX through `POST /v1/evidence-imports` with platform, report type,
  filename, observation timestamp, and a unique idempotency key in headers.
- Use typed Amazon report types whenever possible; use `platform_generic` only
  when the data genuinely lacks a typed parser.
- The service stores normalized rows plus the original file in a tenant-scoped,
  content-addressed directory beside SQLite. Back up that directory together
  with the database; a database-only restore leaves import object keys unresolved.
- `GET /v1/evidence-imports` and `/{id}` return metadata without row bodies.
- Reusing an idempotency key with changed bytes or metadata returns `409`.
- Rejected PII/secret columns must be removed at the source or through a reviewed
  preprocessing step; do not rename them merely to evade the gate.
- XLSX requires the `xlsx` package extra, rejects macros/encrypted workbooks, and
  preserves formulas as inert strings rather than calculating them.

## Credential rotation

1. Create a new Shopify Admin API token in Shopify.
2. Update the secret-manager value referenced by `credential_ref`.
3. Execute a small read-only sync and inspect `/v1/audit`.
4. Revoke the old Shopify token in Shopify. No database migration is needed.

For Amazon SP-API, rotate the LWA client secret or refresh token in Amazon's
developer portal, update the secret-manager values referenced by the connector,
run one approved completed-report import, inspect `/v1/audit`, and only then
retire the previous secret. Access tokens are short-lived and never persisted.

## Incident checks

- `401`: verify the caller still has the full `eai_...<key-id>` value and that
  the key has not been revoked.
- `403`: verify the tenant role; do not work around authorization in the API.
- `409`: inspect action status and idempotency key; never retry with a new key
  until you know whether the original external call ran.
- A failed or lease-expired action can be re-queued with
  `POST /v1/actions/{id}/retry`; it still requires the original approval and a
  separate execution call.
- `502`: inspect the audit event's `error_type`, platform status, and token
  availability. The runtime will not convert this into success.
- Agent-run `502`: verify `OPENAI_API_KEY`, `EAI_OPENAI_MODEL`, model access,
  structured-output compatibility, and the run's persisted task errors. Do not
  replace a failed specialist result with a generated placeholder.
- Amazon report action `502`: verify all three LWA references, region,
  marketplace authorization, report role, `processingStatus=DONE`, document
  expiry, compression, and report size. Restricted/PII reports are unsupported;
  do not bypass this with a manually copied RDT.

## Backup and recovery

Stop the service or use a filesystem-consistent snapshot of the SQLite file and
its `-wal`/`-shm` companions plus `<database>.evidence_objects/`. Restore into a staging path, run the full test
and package validation gates, then promote. Production deployments still need
an encrypted backup schedule and a measured restore drill.
