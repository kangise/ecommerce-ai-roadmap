# Changelog

All notable changes to ecommerce-ai-roadmap will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [v1.2.0] - 2026-03-14

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

## [v1.1.0] - 2025-06-20

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

## [v1.0.0] - 2025-06-15

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
