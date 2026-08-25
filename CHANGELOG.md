# Changelog

All notable changes to ecommerce-ai-skills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed
- Track the generated `dist/` package and external-link cache so clean clones are complete.
- Make the full 42-gate suite cold-clone reproducible and regression-blocking.
- Fail the MCP server closed on missing, corrupt, or tampered packages.
- Add package integrity metadata, automated tests, and PR quality checks.

### Added
- L1 marketplace connector account contract for Amazon SP-API and Shopify:
  tenant-scoped list/get/create/update, role-gated synchronous health checks,
  redacted credential-reference presence, provider/marketplace catalogs, and
  persisted health outcomes.
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
