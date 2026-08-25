# ecommerce-ai-skills Roadmap

> Updated 2026-08-22. The repository is a trilingual knowledge base and an
> installable agent-capability package generated from one source of truth.

## Current baseline

| Layer | Shipped state |
|---|---|
| Knowledge | 69 chapters in zh/en/ja; all three mdBook sites build cleanly |
| Ontology | 100 entities · 322 constraints · 78 relations · 8 processes · 15 platforms |
| Agent package | 9 domain Skills · 878 prompts · complete chapter bodies |
| Integration | Dedicated read-only MCP server with 8 resources, 5 tools, and 9 prompts; installable `opc-ecommerce` entry point |
| Runtime vertical slice | SQLite persistence, user/RBAC/approval/audit, Shopify and Amazon ingestion, Weekly Ops, workers/schedules, packaged Mission Control UI, approval inbox, and Evals |
| Quality | 42 gates, automated tests, cold-clone dist verification, weekly link health |
| Release | Versioned package manifest and tag-driven GitHub Release workflow |

## Delivery principles

1. `src/`, `ontology/`, `skills/`, and `integration/` are the editable sources.
2. `dist/` is generated, versioned, integrity-checked, and must be fresh in every PR.
3. A clean clone must pass `python3 scripts/verify_all.py` and `python3 -m pytest`.
4. Facts with a shelf life carry a verification date and expire through M7.
5. Missing platform facts remain explicit unresolved items; they are never guessed.

## Next product increments

| Increment | Acceptance condition |
|---|---|
| Quarterly fact refresh | No verified fact approaches the 18-month deadline without an owner and review batch |
| Notebook smoke matrix | Representative lightweight notebooks execute in CI; heavy notebooks publish a recorded Colab verification date |
| Semantic routing evaluation | Independent query-first set measures LLM routing without weakening R1/R1b/R2 |
| Production deployment hardening | Add Postgres HA, managed KMS/secret rotation, TLS/rate limiting, external identity, backups/restore drills, and a chosen billing provider before internet-facing SaaS |
| Agent operations surface | Add distributed queues, WebSocket events, external identity/session auth, and hosted deployment around the embedded Mission Control product |

Coverage by domain and platform is maintained in [coverage-map.md](coverage-map.md).
The executable gap acceptance boundary is documented in [gap-closure.md](gap-closure.md).
