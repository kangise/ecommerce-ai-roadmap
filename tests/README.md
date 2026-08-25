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

Run the complete suite with:

```bash
python3 -m pytest
```

The production gate is broader than pytest:

```bash
python3 scripts/build_dist.py --check
python3 scripts/verify_all.py
python3 integration/mcp-server.py --validate --dist dist
```

Tests must not create runtime mock data. Synthetic rows are allowed only in
test fixtures, and external connector tests must inject a transport rather
than call a platform with invented credentials.
