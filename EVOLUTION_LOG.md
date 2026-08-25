# Evolution Log

> Evidence snapshot for the repository's convergence loop. Updated 2026-08-22.
> Counts are not hand-maintained: run `python3 scripts/verify_content.py --metrics`
> and `python3 scripts/verify_all.py` to reproduce them.

## Current verified state

| Dimension | Evidence | Status |
|---|---|---|
| Knowledge | 69 source chapters; zh/en/ja books build successfully | verified |
| Glossary | 100 trilingual domain terms | verified |
| Agent package | 9 skills, 878 prompts, 69 complete chapter bodies | verified |
| Ontology | 100 entities, 322 constraints, 78 relations, 8 processes, 15 platforms | verified |
| Integration | MCP package validates checksums and exposes 8 resources, 5 tools, 9 prompts | verified |
| Multi-agent runtime | Ontology-driven Amazon and 14 other marketplace agents, cross-platform review, durable state, evidence/platform validation, retry, and tenant isolation | verified with injected provider transport |
| Evidence ingestion | Five typed Amazon CSV/XLSX reports plus generic files for all ontology marketplaces; field mapping, content-addressed originals, durable IDs, PII/secret rejection, and run integration | verified with test fixtures only |
| Routing | 0/117 known misroutes; runtime MCP passes the same acceptance cases | verified |
| Examples | 18 structurally valid notebooks; no notebook generates runtime mock data | verified |
| Content quality | All content checks and repository gates return zero gaps | verified |
| Fact maintenance | 322 dated constraints and verified source files map to owned review batches | verified |
| Release | Generated `dist/`, package manifest, tests, PR gate, Pages gate, weekly health, tag release | verified |

## 2026-08-13 convergence closeout

- Made `dist/` and the external-link cache versionable so a clean checkout can
  pass before any mutating build step.
- Added deterministic distribution freshness checks, file checksums, package
  count validation, and fail-closed MCP startup behavior.
- Replaced the 19-error routing budget with a zero-error gate and generalized
  intent patterns; added runtime MCP parity tests.
- Removed all default generated/mock business data from notebooks. Core
  lightweight notebooks execute in tests using fixtures that live only in test
  code; heavyweight notebooks require explicit real input files.
- Resolved the Amazon Sponsored Brands Video caption gap from current Amazon Ads
  sources without inventing a caption character limit.
- Added staggered, owned fact-review batches and made coverage part of M7.
- Added reproducible convergence metrics and brought the glossary floor to 100.

## Remaining product decision

The shipped artifact is a production-oriented knowledge/skill/MCP package with
an embedded multi-tenant runtime, not a complete internet-facing SaaS product.
The embedded slice now includes durable users, tenant ownership, API-key RBAC,
public user provisioning, second-actor approval, audit, and a read-only Shopify
sync. It also includes a synchronous Weekly Ops Council backed by a real
Responses API boundary; live provider verification still requires operator-owned
credentials and model access. Product decisions still required for SaaS are the user-facing application,
external identity, billing/entitlements, deployment topology, and additional
systems of record. Acceptance conditions remain in `roadmap/README.md`.

## Verification commands

```bash
python3 scripts/build_dist.py --check
python3 scripts/verify_content.py --metrics
python3 scripts/verify_all.py
python3 -m pytest
python3 integration/mcp-server.py --validate --dist dist
```
