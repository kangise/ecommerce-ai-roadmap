# D0. Amazon 運用索引 | Amazon オペレーションインデックス

> **パス**: Path D: マルチプラットフォーム · **モジュール**: D0
> **最終更新**: 2026-08-08

---

## Amazon 専用章がない理由

Amazon は本書で 1,600 回以上登場します——次点の Shopify（767 回）の 2 倍以上です。それでも `d0-amazon-ai-guide.md` はありません：**Path A オペレーションラインがすなわち Amazon ラインだからです。**

a-operators の 14 章（a1 選品 → a14 エージェント化）はすべて Amazon をデフォルトの舞台として構築されています。Listing 最適化、PPC 広告、在庫管理、コンプライアンス——どのモジュールも Amazon の事例・制約・プロンプトを基準にしています。これは意図的な設計です：一人会社のコア運営現場は Amazon であり、運用手法をプラットフォーム中立層に抽象化すると実践密度が下がってしまいます。

> **このページは案内であり、本文の章ではありません。** Amazon の内容を a-operators からここに複製すると、二つの矛盾する情報源が生まれます——本ライブラリの CI ゲートが防ごうとしている腐敗そのものです。Amazon 固有の知識が必要なときは、該当する a-operators の章に直接ジャンプしてください。

---

## Amazon 運用クイックリファレンス

| 章 | 内容 | Amazon 関連度 |
|----|------|:--:|
| [A1 商品リサーチ](../a-operators/a1-product-research.md) | 選品手法、データソース、AI 支援スクリーニング | 高 |
| [A2 Listing 最適化](../a-operators/a2-listing-optimization.md) | タイトル、箇条書き、説明、Search Terms、画像コピー | 主戦場 |
| [A3 広告運用](../a-operators/a3-advertising.md) | PPC 戦略、入札最適化、ACOS 診断 | 主戦場 |
| [A4 カスタマーサービス](../a-operators/a4-customer-service.md) | レビュー返信、バイヤーメッセージ、紛争対応 | 高 |
| [A5 在庫管理](../a-operators/a5-inventory.md) | FBA 在庫予測、補充判断 | 高 |
| [A6 コンプライアンス](../a-operators/a6-compliance.md) | カテゴリ承認、IP リスク、FDA/FCC | 高 |
| [A7 画像](../a-operators/a7-visual-content.md) | メイン画像、A+ コンテンツ、ブランドストーリー | 高 |
| [A8 価格戦略](../a-operators/a8-pricing-strategy.md) | Buy Box 価格設定、動的再価格設定 | 中 |
| [A9 SEO/GEO](../a-operators/a9-seo-geo.md) | Amazon 検索順位、AI 検索エンジン最適化 | 高 |
| [A10 ブランド](../a-operators/a10-brand-building.md) | ブランド登録、Brand Analytics、ブランドストーリー | 中 |
| [A11 財務](../a-operators/a11-financial-analysis.md) | 利益試算、FBA 手数料、返品コスト | 中 |
| [A12 IP 保護](../a-operators/a12-ip-protection.md) | 商標、特許、乗っ取り監視 | 高 |
| [A13 成長](../a-operators/a13-ai-growth-hack.md) | 市場拡大、カテゴリ拡張 | 低 |
| [A14 エージェント化](../a-operators/a14-operations-agent.md) | Amazon 運用のエージェントモデル | 高 |

## Amazon 固有の制約一覧

これらの制約は Phase A で a-operators 本文から抽出されたものです。完全な定義は `ontology/constraints.yaml` を参照。

| 制約 | 値 | 出典 |
|------|-----|------|
| タイトル最大長 | 200 文字 | a2 §3.1 |
| 先頭 80 文字に最高検索ボリューム語を含める | 必須 | a2 §3.1 |
| 箇条書き最大長 | 200 文字/行 | a2 §3.1 |
| Search Terms 1 行あたり | ≤250 バイト、5 行 | a2 §3.1 |
| メイン画像要件 | 純白背景、占有率 ≥85%、最短辺 ≥1600px | a7 |

## 他プラットフォームとの違い

Amazon は最も「検索駆動型」のプラットフォームです：トラフィックはサイト内検索が中心で、Listing の質が露出とコンバージョンを直接左右します。これは Shopify（サイト外集客）や TikTok Shop（アルゴリズムフィード）とは根本的に異なる運営ロジックです。

| 次元 | Amazon | 比較対象 |
|------|--------|----------|
| トラフィック源 | サイト内検索 | Shopify: サイト外集客 |
| Listing 構造 | タイトル+箇条書き+説明+Search Terms | Shopify: 商品ページ SEO |
| 広告タイプ | PPC Sponsored Products/Brands/Display | Shopify: Google/Facebook/Instagram |
| フルフィルメント | FBA または FBM | Shopify: 自社または 3PL |
| AI 効果が高い領域 | Listing SEO + PPC 最適化 | Shopify: 広告 + メール |

詳細比較 → [プラットフォーム比較](platform-comparison.md)

---

## この方法が効かないとき

Amazon 運用の AI 手法は以下のシナリオでは機能しません：

- **審査が厳しいカテゴリ**：医療機器、食品接触材料などは AI コピーライティングではなく専門知識が必要
- **Supplier Central / Vendor Central**：B2B 供給モデルのルールは Seller Central と完全に異なる
- **自社配送（FBM）**：物流変数が多く、AI 在庫予測の精度は FBA シナリオより低下
- **新規サイトのコールドスタート**：日本、オーストラリアなど、AI 翻訳 ≠ ローカライゼーション、文化適応には人手が必要
