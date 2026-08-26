# Changelog

All notable changes to ecommerce-ai-skills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Added a tenant-owned Provider Smoke control plane for OpenAI Responses,
  Amazon SP-API, and Shopify: operator-gated live probes, viewer-readable
  persisted results, 30-second per-target cooldowns, idempotent lease-fenced
  recovery, terminal audit-chain evidence, bounded request IDs/response reads,
  and explicit blocked/failed states. OpenAI probes use the deployment-shared
  `OPENAI_API_KEY` and `EAI_OPENAI_MODEL`, `store:false`, a small output limit,
  and never persist or display generated output or raw provider bodies.

### Changed
- Added an explicit, refresh-persistent Light/Dark control and corrected Dark
  foreground treatment for Primary commands, Amazon/TikTok brands, Agent and
  upload glyphs, navigation icons and the account identity anchor. Hover and
  active surfaces now retain visible icon contrast in both themes.
- Rebuilt the embedded Commerce Agent OS workbench around the NovoChoice L7
  decision-workspace principles: self-hosted IBM Plex/Source Han typography,
  a governed cool-gray token system, compact 4/6/8px geometry, neutral
  selection, surface-first boundaries, one dominant Canvas, contextual detail,
  honest semantic states, responsive task preservation, and accessible motion,
  contrast and dark-mode variants. Existing APIs, tenant/RBAC checks, actions,
  persisted Demo state and SSE behavior remain unchanged.

## [1.3.0] - 2026-08-26

### Fixed
- Track the generated `dist/` package and external-link cache so clean clones are complete.
- Make the full 42-gate suite cold-clone reproducible and regression-blocking.
- Fail the MCP server closed on missing, corrupt, or tampered packages.
- Add package integrity metadata, automated tests, and PR quality checks.

### Added
- L13 release-candidate contract: uniform `1.3.0` package/API/client versioning,
  deterministic source/UI/test/dist manifest, clean-clone generated JSON gate,
  dependency-isolated wheel smoke outside the checkout, installed Demo plus
  actual absent-target restore verification, tag/version enforcement, and
  SHA-256 checksums for every published release asset.
- L12 audit hash-chain, durable Assurance run, and verified recovery contract:
  admin-only eval/security checks, CLI-only restore evidence, blocked no-data
  evaluations, online SQLite plus evidence-object atomic backup, SHA-256
  manifests, and fail-closed restore verification. Backups contain sensitive
  data and remain unencrypted by this tool; production encryption/access control
  is external.
- L11 one-command Pilot operations contract: viewer-safe tenant readiness and
  local worker heartbeat status, explicit stale/degraded/stopped states,
  credential-presence-only blockers, loopback/public-bind and one-time-key
  boundaries, graceful shutdown guidance, and single-process SQLite limits.
  Amazon/OpenAI external dependencies remain explicit blocked/unknown states.
  Hardened readiness distinguishes attention from blocked, stale Amazon health
  from missing credentials, and graceful shutdown from worker-timeout stopping.
- L10 Mission Control streaming contract: viewer-authenticated tenant SSE with
  header-first tenant-local cursors, closed safe event metadata, heartbeat/reset/
  reconnect semantics, bounded replay/lifetime, global and tenant connection
  limits, proxy guidance, and contract gates. This is a single-process
  SQLite/ThreadingHTTPServer boundary; no distributed event broker is claimed.
- L9 durable tenant-owned proposals derived from approved Daily Ops / Agent
  Graph priorities, with immutable source/graph/evidence/metric/payload hash
  lineage, optimistic revisions, auditable local human decisions, risk-based
  approval thresholds, expiry, idempotent lease-fenced executions, and reuse
  of existing safe read actions only. Immutable version history includes
  expiry in the content hash; the proposal worker persists expiry and recovers
  linked executions without creating duplicate actions. No generic marketplace
  or Amazon Ads write capability is registered.
- L8 tenant-owned Daily Ops schedules and schedule-local occurrences with IANA
  timezone/DST handling, one durable local-date run, source-age validation,
  operator-triggered execution/retry, persisted eligible Daily Briefs, final
  Reviewer gating, scheduled-instant evidence cutoffs, immutable hashed schedule
  snapshots, fenced worker attempts, bounded missed-date catch-up, execution-
  principal lifecycle guards, parent-linked Agent Run eligibility, and an
  embedded no-external-write worker boundary.
- L7 tenant-owned, versioned Domain Agent Graphs with immutable published
  definitions, dynamic Amazon/Shopify/ontology marketplace specialists,
  Evidence and Metric Observation snapshots, application-level parallelism,
  Manager/Reviewer separation, zero model-tool policy, run graph/hash lineage,
  execution-contract fingerprinting, structured action/Metric claims, complete
  Reviewer coverage, and downstream blocking for legacy or non-approved runs.
- L6 conditional Amazon Ads adapter-status contract: fail-closed status,
  24-hour gate freshness, tenant/account/profile/region checks, and no Ads
  write adapter, route, action, or write operation in this build.
- L5 tenant-scoped Amazon Ads accounts and capability gate with environment-
  referenced LWA credentials, regional Profiles-only account health, a
  read-only Sponsored Products v3 campaign-list probe, bounded lease recovery,
  safe request IDs, explicit external-attestation evidence, and a hard L6
  boundary. Missing credentials or approval remain durable `blocked` state;
  no Ads resource is created or mutated.
- L4 tenant-owned metric observation and materialization contracts with exact
  bounded Decimal values, period/grain/provenance/quality metadata, strict
  currency isolation and missing-currency quarantine, operator idempotent
  per-import materialization, admin bounded cursor backfill, and an explicit
  L3 Evidence/L4 failure boundary without runtime mock fallbacks.
- L1 marketplace connector account contract for Amazon SP-API and Shopify:
  tenant-scoped list/get/create/update, role-gated synchronous health checks,
  redacted credential-reference presence, provider/marketplace catalogs, and
  persisted health outcomes.
- L2 Amazon report recipe contract with tenant-scoped list/get/create/update,
  operator write authorization, four explicit report-type mappings, linked
  Amazon marketplace-subset validation, and configuration-only persistence
  without Amazon calls or background execution.
- L3 durable Amazon Reports synchronization with operator/idempotency/healthy-
  account gates, `createReport` and bounded status polling, `Retry-After`
  handling, terminal failure persistence, bounded JSON/TSV normalization,
  tenant-owned Evidence imports, viewer inspection APIs, worker CLI, and real
  Mission Control sync actions and states. Automatic scheduling and Amazon
  write operations remain outside this slice.
- L3 idempotent Amazon report sync contract with durable worker states,
  bounded createReport/getReport polling, Retry-After handling, document-to-
  Evidence import semantics, and explicit no-auto-scheduling/no-write scope.
- Six ontology-backed AI systems terms, bringing the generated trilingual glossary and entity model to 100 entries.
- Four official Amazon Sponsored Brands Video constraints, bringing the ontology to 322 sourced constraints.
- A real installable Python package and `opc-ecommerce` entry point; wheels now include the generated knowledge artifact instead of metadata only.
- Tenant-scoped SQLite runtime with hashed API keys, RBAC, two-person approval, idempotency, audit events, and a Shopify credential-reference connector.
- Authenticated runtime API contract, threat model, and operations runbook.
- Public-bind guard, per-client request limiter, API-key rotation/revocation lifecycle, and optional MCP dependency extra.
- Tenant-scoped user list/create/role APIs that make second-actor approval usable without direct database access.
- Durable, platform-aware `weekly_ops` runs with an evidence analyst, dynamically generated marketplace specialists, Amazon's full installed Skill set, cross-platform review, manager synthesis, evidence/platform validation, persisted tasks/artifacts/events, explicit retry, and a real OpenAI Responses API boundary.
- Tenant-scoped CSV/TSV evidence imports with five typed Amazon report validators, generic support for all ontology marketplaces, SHA-256/idempotency, PII/secret-column rejection, and direct `evidence_import_ids` reuse in agent runs.
- Optional XLSX ingestion, explicit original-to-normalized field mapping, tenant-scoped content-addressed originals, ZIP/decompression/macro safeguards, worksheet selection, and Schema v6 migration.
- Approved read-only Amazon SP-API report imports using environment-referenced LWA credentials, regional endpoints, completed-report/document retrieval, Amazon-host allowlisting, bounded GZIP handling, and Evidence Import output.
- Durable agent jobs, leases, bounded retry/backoff, interval schedules with latest-Evidence selectors, worker/scheduler CLI processes, Schema v8 migration, Mission Control, and admin-only approval inbox APIs.
- Persisted deterministic Weekly Ops evaluations for task completion, priority shape, evidence references, platform isolation, owner assignment, approval policy, API history, and Mission Control failure counts; Schema v9 migration.
- Packaged responsive Mission Control Web UI with in-memory API-key session, live runtime catalog, real Evidence/Run/Job/Schedule/Approval/Eval/Audit actions, CSP security headers, loading/empty/error states, and UI/package tests.
- Redesigned Mission Control as an Amazon-first cross-platform operating brief with dedicated workflow navigation, licensed local icons, a real Evidence-derived trend service, persisted Agent Brief priorities, role-aware approval controls, and responsive desktop/mobile layouts.
- Added an explicit isolated `demo-seed` command, Demo tenant mode and Schema v10 migration, visible Demo warnings, seven-day Amazon/cross-platform sample Evidence, a completed Agent Run/Eval/Job, Schedule, and second-actor approval fixtures without adding runtime mock fallbacks.
- Added a loopback-only `demo` server that seeds a missing Demo database, auto-connects the browser through a temporary no-store Demo session, rejects production/multi-tenant databases, and revokes the temporary key at shutdown; normal API authentication is unchanged.

## [v1.1.0] - 2026-08-10

### Added
- Dedicated MCP server with typed resources, tools, and prompts.
- 318 sourced constraints across 15 platforms.
- Full chapter bodies in the distributable knowledge package.
- Independent live acceptance: 8/9 new cases and 3/3 regressions passed.

### Changed
- Routing probes now measure literal test degeneration and natural-language coverage.
- Domain Skills expanded to 9 with 878 trilingual prompts.

## [v1.0.0] - 2026-08-09

### Added
- Installable agent package generated from the trilingual book, ontology, and Skills.
- Initial ontology with 94 entities, 78 relations, and formal operating processes.

## [content-2026-03] - 2026-03-14

### Added
- **Path E: 社交媒体 AI 运营** (7 new guides)
- E1: Instagram + Facebook (Meta ecosystem) Reels, Advantage+ ads, Shopping
- E2: YouTube long-form reviews, Shorts, Shopping, Affiliate
- E3: 小红书 (Xiaohongshu/RedNote) seeding notes, KOL/KOC, China market
- E4: Pinterest visual search engine, Shopping Ads
- E5: WhatsApp Business AI Chatbot, conversational commerce
- E6: Reddit community marketing, product discovery
- E7: Cross-channel strategy content repurposing, attribution, budget allocation
- **Path D expanded to 13 platforms** (10 new guides)
- D4: Walmart Marketplace Listing Quality Score, Walmart Connect, WFS, migration guide
- D5: Temu fully/semi-managed models, competition analysis, entry decision framework
- D6: Southeast Asia (Shopee + Lazada) multilingual, livestream, COD
- D7: Mercado Libre (Latin America) Spanish/Portuguese localization, CBT
- D8: Rakuten (Japan) store customization, Points, R-Mail, YouTube Shopping partnership
- D9: eBay Magical Listing AI, Promoted Listings 2026 attribution changes
- D10: AliExpress Choice program, Southern Europe market
- D11: Coupang (Korea) Rocket Delivery, KC certification, Korean listing
- D12: Faire (wholesale) algorithm optimization, Faire Direct, retailer relationships
- D13: Europe (Otto + Zalando) German market, EU compliance (CE/EPR/VAT/GPSR)
- **Platform comparison summary page** 14 platforms + 7 social channels compared
- **Multi-language README translations** en/ja/es with shield.io language navigation badges
- **Path A backfill** video script generation (A2), ad creative workflow (A3), chatbot/social CS (A4), platform ad compliance (A6)
- **Unified navigation system** 3-layer navigation across all 40 content files
- **101 semantic cross-links** contextual links connecting related content across all Paths
- **Translation architecture** .translation/ARCHITECTURE.md with glossary, style guide, status tracker

### Changed
- README.md updated with Path D expansion (13 platforms) and Path E entry
- Path D README.md redesigned with full platform navigation
- Path selection table now includes Path D and Path E

## [content-2025-06-20] - 2025-06-20

### Added
- `notebooks/` directory with first Notebook: b1-data-pipeline.ipynb (Amazon 报告数据处理)
- `README_EN.md` complete English version of README
- "Top 10 Prompts" viral entry section in README.md
- "What's New" section at top of README.md
- New Issue templates: broken link report, prompt submission, notebook submission
- `CODEOWNERS` file for automated review assignment
- `CHANGELOG.md` (this file)
- Case studies: AI-Powered Listing Generation, Automated Review Analysis
- Contributors section in README.md
- Updated PR template with quality checklist
- SEO configuration in `_config.yml`

### Changed
- README.md first screen redesigned with bilingual tagline, badges, Mermaid diagram, and "Try This Now" section
- Updated link-checker workflow to scan all Markdown directories
- Updated `CONTRIBUTING.md` with Prompt template submission guide
- Updated `paths/b-developers/b1-data-pipeline.md` with Open in Colab badge

## [content-2025-06-15] - 2025-06-15

### Added
- Modularized content: `paths/` directory with A1-A6, B1-B5, C1-C3 modules
- `prompts/` directory with 5 standardized Prompt template files
- `roadmap/` directory with public roadmap and coverage map
- Competitive landscape analysis in `docs/competitive-analysis.md`
- Content quality test infrastructure (`tests/test_repo_properties.py`)
- Fixed `_config.yml` metadata to match README content
- Jekyll SEO plugins (jekyll-seo-tag, jekyll-sitemap)

### Changed
- README.md slimmed down to navigation hub (< 500 lines)
- All broken internal links fixed or removed

### Fixed
- Removed all "即将发布" placeholders without tracking Issues
- Fixed _config.yml title and description mismatch
