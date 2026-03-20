# Multi-Language Translation Architecture

## Overview

Source language: Chinese (zh) -- current content in `paths/` and `README.md`
Target languages: English (en), Japanese (ja), Spanish (es)
Translation engine: Kiro (manual trigger, not API-based)
SEO strategy: Subdirectory per language at repo root

## Directory Structure

```
/
README.md # Chinese homepage (source of truth)
en/
README.md # English homepage
paths/
0-foundations/
ai-landscape.md
a-operators/
a1-product-research.md
a2-listing-optimization.md
a3-advertising.md
a4-customer-service.md
a5-inventory.md
a6-compliance.md
d-platforms/
shopify-ai-guide.md
tiktok-shop-ai-guide.md
cross-platform-strategy.md
ja/
README.md # Japanese homepage
paths/ # Same structure as en/
es/
README.md # Spanish homepage
paths/ # Same structure as en/
paths/ # Chinese content (source)
.translation/
ARCHITECTURE.md # This file
GLOSSARY.md # Terminology glossary (all languages)
STYLE_GUIDE.md # Translation style guide per language
STATUS.md # Translation status tracker
```

## Translation Status Tracker (.translation/STATUS.md)

Tracks which files need translation or update.

Format:
```
| Source File (zh) | en Status | en Hash | ja Status | ja Hash | es Status | es Hash |
|------------------|-----------|---------|-----------|---------|-----------|---------|
| README.md | current | abc123 | pending | | pending | |
| paths/0-foundations/ai-landscape.md | outdated | def456 | pending | | pending | |
```

Status values:
- `current` -- translation matches source
- `outdated` -- source has been updated since last translation
- `pending` -- not yet translated
- `` -- not applicable

Hash = first 7 chars of the git commit hash when the translation was last synced.

## Workflow

### Initial Translation (one-time)
1. Prioritize files by traffic/importance:
- Tier 1: README.md, ai-landscape.md (translate first)
- Tier 2: a2-listing-optimization.md, a3-advertising.md, a6-compliance.md
- Tier 3: d-platforms/ files
- Tier 4: remaining a-operators/ files
2. Ken tells Kiro: "translate [file] to en/ja/es"
3. Kiro reads source, translates, writes to en/ja/es directories
4. Kiro updates STATUS.md with current hash
5. Commit and push

### Ongoing Sync
1. Ken updates Chinese content
2. Ken tells Kiro: "sync translations"
3. Kiro runs: git log to find changed .md files since last sync
4. Kiro checks STATUS.md to identify outdated translations
5. Kiro translates only the changed files
6. Kiro updates STATUS.md
7. Commit and push

## Glossary (.translation/GLOSSARY.md)

Key terms that must be translated consistently across all files:

| Chinese | English | Japanese | Spanish | Notes |
|---------|---------|----------|---------|-------|
| 跨境电商 | Cross-border e-commerce | 越境EC | Comercio electronico transfronterizo | |
| 选品 | Product research / Product selection | 商品リサーチ | Investigacion de productos | |
| Listing | Listing | リスティング | Listing | Keep English in all languages |
| 五点 | Bullet Points | バレットポイント | Bullet Points | Keep English in ja/es |
| 广告优化 | Advertising optimization | 広告最適化 | Optimizacion de publicidad | |
| 客服 | Customer service | カスタマーサービス | Servicio al cliente | |
| 合规 | Compliance | コンプライアンス | Cumplimiento normativo | |
| 独立站 | Independent store / DTC store | 独立サイト / 自社EC | Tienda independiente | |
| 达人 | Creator / Influencer | クリエイター | Creador / Influencer | |
| 直播 | Livestream | ライブコマース | Transmision en vivo | |
| 痛点 | Pain point | ペインポイント | Punto de dolor | |
| 卖点 | Selling point | セールスポイント | Punto de venta | |
| 复购 | Repeat purchase | リピート購入 | Compra repetida | |
| 种草 | Seeding / Product discovery | 種まき / 商品発見 | Descubrimiento de producto | |

## Style Guide (.translation/STYLE_GUIDE.md)

### English
- Tone: Professional but approachable, like talking to a fellow seller
- Use American English spelling
- Keep technical terms in English (ACOS, ROAS, PPC, FBA, etc.)
- Prompt templates: translate the instructions but keep placeholder brackets [X] as-is
- Code blocks: do not translate content inside code blocks
- Tables: translate cell content but keep markdown structure

### Japanese
- Tone: Polite (です/ます体), professional
- Use katakana for English loanwords (リスティング, マーケティング)
- Keep technical terms in English with katakana reading where helpful
- Amazon/Shopify/TikTok: keep in English
- Numbers: use Arabic numerals (not kanji)

### Spanish
- Tone: Professional, use usted (formal)
- Use Spain Spanish (castellano), not Latin American variants
- Keep technical terms in English (ACOS, ROAS, PPC, Listing)
- Currency: keep $ for USD, use EUR symbol where applicable

### All Languages
- Do NOT translate content inside ``` code blocks
- Do NOT translate URLs
- Do NOT translate file paths in links (keep relative paths working)
- Translate alt text for images
- Keep markdown formatting intact (headers, tables, lists, links)
- Each translated file must have a language switcher at the top:
`[中文](../../paths/...) | [English](../en/paths/...) | [日本語](../ja/paths/...) | [Espanol](../es/paths/...)`

## SEO Considerations

- Each language README.md has localized H1 title with target keywords:
- en: "AI Prompts & Strategies for Amazon Sellers, Shopify & TikTok Shop"
- ja: "越境EC AI 実践ガイド | Amazon セラー・Shopify・TikTok Shop"
- es: "Guia de IA para Vendedores de Amazon, Shopify y TikTok Shop"
- Language switcher links at top of every page (helps Google discover all versions)
- File names stay in English across all languages (URL consistency)
- Internal links within each language directory are self-contained
