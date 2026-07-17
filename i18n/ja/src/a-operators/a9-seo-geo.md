# A9. AI SEO と GEO 最適化

> **トラック**: Path A: 運営 · **モジュール**: A9
> **最終更新**: 2026-03-15
> **難易度**: 上級
> **所要時間**: 1 日 30 分、2〜3 週間
> **前提モジュール**: [A2 Listing 最適化](a2-listing-optimization.md)


---

## 章ナビゲーション

1. [SEO から GEO へ](#1-seo-から-geo-へ) · 2. [Amazon SEO](#2-amazon-seo) · 3. [Google SEO](#3-google-seo-for-shopify) · 4. [GEO 最適化](#4-geo-最適化の実操) · 5. [ソーシャルプラットフォーム SEO](#5-ソーシャルプラットフォーム-seo) · 6. [ツール](#6-ai-seo-ツール比較) · 7. [プロンプト](#7-プロンプトテンプレート) · 8. [完了チェック](#8-完了チェック)

---

## このモジュールで学べること

- SEO → GEO のパラダイムシフトを理解(Google 順位から AI 推薦へ)
- Amazon SEO の最新アルゴリズム(COSMO + Rufus)を習得
- Shopify Google SEO の方法論を習得
- GEO 最適化を学び、ChatGPT/Perplexity/Gemini にあなたの製品を推薦させる
- 各ソーシャルプラットフォームのサイト内 SEO を理解

> 2026 年、消費者の 1/3 が既に AI Agent で製品発見を行っている。GEO は 2026 年の最も重要な新スキル。

---

## 1. SEO から GEO へ

### 1.1 検索行動の 3 回の変革

| 変革 | 時間 | 核心ロジック | EC への影響 |
|------|------|--------------|-------------|
| Google 検索 | 2000s-現在 | キーワード+リンク+コンテンツ | Shopify Google SEO |
| プラットフォーム内検索 | 2010s-現在 | プラットフォームルール+販売量+転換率 | Amazon A9/COSMO |
| AI 検索/GEO | 2024-現在 | 構造化データ+ブランド権威+レビュー | ChatGPT/Perplexity に推薦される |

### 1.2 GEO vs 従来の SEO

| 次元 | 従来の SEO | GEO |
|------|------------|-----|
| 目標 | Google 順位 | AI 推薦/引用 |
| ユーザー行動 | 検索結果ページを閲覧 | AI の答えを直接取得 |
| 順位要因 | キーワード+リンク+コンテンツ | 構造化データ+ブランド権威+レビュー+被引用頻度 |
| コンテンツ形式 | 長い記事、ブログ | FAQ+Schema+構造化データ |
| 測定指標 | 順位/流入/CTR | AI 推薦頻度/ブランド言及率 |

### 1.3 なぜ越境セラーは GEO に注目すべきか

- Shopify Agentic Storefronts(UCP プロトコル)が AI Agent に ChatGPT 内で直接購入させる
- Perplexity Comet ブラウザがユーザーの代わりに Amazon で買い物できる
- Google AI Overviews が検索結果の上部に AI の答えを表示
- AI に推薦されない = ますます多くの流入を失う

> **関連**: [D1 Shopify](../d-platforms/shopify-ai-guide.md) GEO と Agentic Storefronts は D1 へ。

---

## 2. Amazon SEO

> **関連**: [A2 Listing 最適化](a2-listing-optimization.md) A9→COSMO→Rufus の完全な進化は A2 へ。

### 2.1 2026 Amazon SEO の核心チェックリスト

```
タイトル: コア語を最初の 80 文字に、自然言語、COSMO フレンドリー(「誰が必要」「なぜ必要」に答える)
Bullet Points: 利益点で始める、Rufus フレンドリー(ユーザーの質問に答える)、最初の 3 つが最重要
Backend: タイトルの語を繰り返さない、スペル変体/同義語を含む、250 バイト、スペース区切り
Q&A 事前埋め込み: 20+ の高頻度質問、Rufus が読んでユーザーに答える、答えにキーワードを含む
A+ Content: COSMO が読んで製品を理解、使用シーンを含む、画像 Alt Text にキーワードを含む
```

### 2.2 Amazon SEO 監査プロンプト

```
あなたは COSMO と Rufus アルゴリズムに精通した Amazon SEO の専門家です。

私の Listing:
- タイトル: [貼り付け]
- Bullet Points: [貼り付け]
- Backend Search Terms: [貼り付け]
- 競合 ASIN: [3 個]

SEO 監査をしてください:
1. COSMO フレンドリー度スコア(1-10)
2. Rufus フレンドリー度スコア(1-10)
3. Backend 最適化の提案
4. Q&A 事前埋め込みの提案(10 個の質問)
5. キーワードカバレッジのギャップ
6. 優先度アクションリスト
```

---

## 3. Google SEO for Shopify

### 3.1 技術 SEO チェックリスト

| 項目 | 要件 | ツール |
|------|------|--------|
| SSL | HTTPS(Shopify 自動) | |
| Sitemap | GSC に提出 | Google Search Console |
| Core Web Vitals | LCP<2.5s, FID<100ms, CLS<0.1 | PageSpeed Insights |
| Schema | Product/FAQ/Breadcrumb/Review | JSON-LD |
| 画像 | WebP、Alt Text にキーワードを含む | Shopify 画像最適化 App |
| URL | 簡潔、キーワードを含む | Shopify 後台 |

### 3.2 コンテンツ SEO 戦略

| コンテンツタイプ | 例 | 購入意図 | 頻度 |
|------------------|-----|----------|------|
| 製品ガイド | "How to Choose Best [カテゴリ]" | 高 | 月 2 本 |
| 比較記事 | "[A] vs [B]: Which Better?" | 高 | 月 2 本 |
| チュートリアル | "How to Use [製品]" | 中 | 月 2 本 |
| リスト記事 | "Top 10 [カテゴリ] 2026" | 高 | 四半期ごと |

### 3.3 Schema 構造化データ(GEO の基礎)

```json
{
"@context": "https://schema.org",
"@type": "Product",
"name": "製品名",
"brand": {"@type": "Brand", "name": "ブランド名"},
"description": "製品説明",
"offers": {
"@type": "Offer",
"price": "29.99",
"priceCurrency": "USD",
"availability": "https://schema.org/InStock"
},
"aggregateRating": {
"@type": "AggregateRating",
"ratingValue": "4.7",
"reviewCount": "1250"
}
}
```

---

## 4. GEO 最適化の実操

### 4.1 AI にあなたの製品を推薦させる 5 つの戦略

| 戦略 | 説明 | 難度 | 影響 |
|------|------|------|------|
| 構造化データ | Product/FAQ Schema | | |
| FAQ 最適化 | 自然言語 Q&A + Schema | | |
| ブランド言及 | 第三者サイトで言及される | | |
| レビューカバレッジ | Amazon/Trustpilot で高評価 | | |
| Agentic Storefronts | Shopify UCP プロトコル | | |

### 4.2 GEO 核心データ(2026 研究)

業界研究([Onely](https://www.onely.com/blog/geo-for-ecommerce-how-to-boost-product-visibility-in-ai-search/))によると、GEO 最適化の核心戦略と効果:

| 戦略 | 効果 | 説明 |
|------|------|------|
| 完全な Product Schema | AI 引用率 +40-60% | 構造化データは AI が製品を理解する基礎 |
| 50+ の顧客レビュー | AI 推薦確率 +2.5 倍 | レビューの数量と質が AI 推薦に直接影響 |
| 競合比較コンテンツ | AI 引用率 +45-70% | 買い物シーンでは比較コンテンツが最も引用される |

Content rephrased for compliance with licensing restrictions.

### 4.3 GEO の 5 大支柱(EC 版)

2026 年の GEO 実践ガイド([TheCommerceShop](https://thecommerceshop.com/manufacturers/blog/5-pillars-of-geo-for-ecommerce/)、[Prefixbox](https://www.prefixbox.com/blog/guide-to-generative-engine-optimization/))によると、EC の GEO 最適化には 5 大支柱がある:

| 支柱 | 説明 | 実操 |
|------|------|------|
| エンティティの明確さ | AI はあなたのブランドと製品を明確に理解する必要 | Schema、ブランドページ、Wikipedia/Wikidata を充実 |
| 構造化コンテンツ | AI は構造化され解析可能なコンテンツを好む | FAQ、比較表、スペック表、構造化された説明 |
| 意図駆動 | コンテンツはユーザーの購入意図に答える必要 | "best X for Y" 系コンテンツ、使用シーンの説明 |
| 購入可能性 | AI の答えは直接購入に導ける必要 | 製品ページに在庫あり、価格が正確、ディープリンクが有効 |
| 権威シグナル | AI は権威ある情報源を信頼 | 第三者レビュー、メディア報道、専門認証 |

Content rephrased for compliance with licensing restrictions.

### 4.4 Agentic Commerce(AI 代理の買い物)

2026 年で最も重要な GEO トレンドは Agentic Commerce — AI エージェントがユーザーの代わりに買い物を完了する([Charle Agency](https://www.charleagency.com/articles/agentic-commerce/)):

| プラットフォーム | AI 買い物機能 | 状態 |
|------------------|---------------|------|
| ChatGPT | Instant Checkout(サイト内で直接購入) | 提供中 |
| Shopify | Agentic Storefronts(UCP プロトコル) | 提供中 |
| Google | AI Mode + Gemini 買い物 | 提供中 |
| Microsoft | Copilot Checkout | 提供中 |
| Perplexity | Comet ブラウザ代理購入 | テスト中 |
| Reddit | AI 買い物検索カルーセル | テスト中 |

> Shopify と Google は UCP(Universal Commerce Protocol)を共同開発した、AI 買い物のオープン標準([Shopify Enterprise](https://www.shopify.com/enterprise/blog/generative-engine-optimization))。Shopify ブランドは ChatGPT、Copilot、Gemini などの AI チャネル内で直接販売できる最初の存在。

Content rephrased for compliance with licensing restrictions.

```
あなたは Agentic Commerce 戦略の専門家です。

私のブランド: [名前]
販売チャネル: [Amazon / Shopify / 両方]
カテゴリ: [X]

私の Agentic Commerce 準備度を評価してください:
1. 構造化データの完全度(Product/FAQ/Breadcrumb/Review Schema)
2. AI 発見可能性(ChatGPT/Perplexity/Google AI Overviews で言及されているか)
3. 購入可能性(価格が正確/在庫/ディープリンク/UCP プロトコル)
4. アクション計画(短期 1 週/中期 1 月/長期 3 月)
```

### 4.5 GEO 効果測定(強化版)

```
毎月 GEO 監査を実行:

1. AI 検索テスト(5 プラットフォーム)
- ChatGPT: "best [カテゴリ] 2026" → 言及されるか記録
- Perplexity: "recommend [カテゴリ] for [シーン]" → 記録
- Gemini: "[カテゴリ] buying guide" → 記録
- Claude: "compare [ブランド] vs [競合]" → 記録
- Google AI Overviews: "[カテゴリ] review" → 記録

2. 競合比較: 誰が AI にもっと推薦されるか?ギャップ分析

3. 構造化データの検証: Google Rich Results Test + Schema.org Validator

4. コンテンツ監査: FAQ カバレッジ、比較コンテンツ、第三者引用

5. トレンド追跡: AI 推薦頻度の変化、新しい AI 買い物チャネル
```

### 4.6 AI 検索可視度ツール

| ツール | 機能 | 価格 |
|--------|------|------|
| AEO Engine | AI 検索可視度モニタリング([AEO Engine](https://aeoengine.ai/blog/most-recommended-ai-search-visibility-solutions)) | 有料 |
| Nudge Now | GEO 最適化プラットフォーム | 有料 |
| Otterly.ai | AI 検索順位追跡 | 有料 |
| ChatGPT/Perplexity | AI 推薦を手動でテスト | 無料/$20/月 |
| Google Search Console | AI Overviews データ | 無料 |

Content rephrased for compliance with licensing restrictions.

---

## 5. ソーシャルプラットフォーム SEO

| プラットフォーム | 検索メカニズム | キーワードの配置 | 詳細ガイド |
|------------------|----------------|------------------|------------|
| TikTok | サイト内検索+レコメンド | タイトル+説明+字幕+Hashtag | [D2](../d-platforms/tiktok-shop-ai-guide.md) |
| YouTube | 検索+レコメンド | タイトル+説明+タグ+字幕 | [E2](../e-social-media/e2-youtube-ai-guide.md) |
| Pinterest | ビジュアル検索 | Pin タイトル+説明+Board | [E4](../e-social-media/e4-pinterest-ai-guide.md) |
| 小紅書 | サイト内検索(70% 浸透率) | タイトル+本文の最初 200 字+タグ | [E3](../e-social-media/e3-xiaohongshu-ai-guide.md) |

---

## 6. AI SEO ツール比較

| ツール | 機能 | 価格 | 向く |
|--------|------|------|------|
| Ahrefs | キーワード+競合+リンク | $99/月〜 | 総合 SEO |
| Semrush | キーワード+広告+コンテンツ | $130/月〜 | 企業級 |
| Surfer SEO | AI コンテンツ最適化 | $89/月〜 | コンテンツ SEO |
| Helium 10 | Amazon キーワード+Listing | $79/月〜 | Amazon SEO |
| vidIQ | YouTube SEO | 無料/$4.5/月 | YouTube |
| ChatGPT/Claude | 汎用 AI 補助 | $20/月 | すべてのシーン |

---

## 7. プロンプトテンプレート

### 7.1 GEO 監査

```
あなたは GEO の専門家です。ブランド [X]、製品 [X]、サイト [URL]。
評価: 構造化データの完全度、FAQ 最適化の提案(10 個)、ブランド言及分析、レビューカバレッジ、競合ギャップ、優先アクションリスト。
```

### 7.2 マルチプラットフォームキーワードリサーチ

```
製品 [X]、カテゴリ [X]、市場 [US]。
Amazon/Google/TikTok/YouTube/Pinterest それぞれに 10 個のキーワードを提供、検索ボリューム帯、競争度、推奨コンテンツタイプを注記。
```

---

## 8. 完了チェック

- [ ] Amazon Listing SEO 監査を完了
- [ ] Shopify に Schema 構造化データを追加
- [ ] FAQ Schema を追加(10+ の質問)
- [ ] ChatGPT/Perplexity/Gemini で製品推薦をテスト
- [ ] クロスプラットフォーム SEO キーワード集を構築
- [ ] Agentic Commerce 準備度を評価
- [ ] 月次 GEO 監査フローを構築

[< A8 価格戦略](a8-pricing-strategy.md) | [Path 総覧](../README.md) | [A10 ブランド >](a10-brand-building.md)
