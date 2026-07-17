# D4. Walmart Marketplace AI ガイド

> **トラック**: Path D: マルチプラットフォーム · **モジュール**: D4
> **最終更新**: 2026-03-14
> **難易度**: 中級
> **所要時間**: 2〜3 時間
> **前提モジュール**: [Path A 運営](../a-operators/)(Amazon の経験を 70% 直接再利用可能)


---

## 章ナビゲーション

1. [Walmart vs Amazon 核心的違い](#1-walmart-vs-amazon-核心的違い)
2. [Walmart SEO と Listing 最適化](#2-walmart-seo-と-listing-最適化)
3. [Walmart Connect 広告](#3-walmart-connect-広告)
4. [WFS 物流の意思決定](#4-wfs-物流の意思決定)
5. [Amazon → Walmart 移行方法論](#5-amazon--walmart-移行方法論)
6. [Prompt テンプレート](#6-prompt-テンプレート)
7. [完了チェック](#7-完了チェック)

---

## このモジュールで産出するもの

- Walmart Listing 最適化方案(Amazon の経験を基に適応)
- Walmart Connect 広告戦略
- Amazon → Walmart 移行チェックリスト

> **核心理念**: Walmart Marketplace は Amazon セラーにとって最も自然な第二プラットフォーム。250K+ のアクティブセラー、GMV $10B+、広告収入 $64 億(+46% YoY)。Path A の 70% の AI 方法論を直接再利用でき、本ガイドは差別化部分だけに焦点を当てる。

---

## 1. Walmart vs Amazon 核心的違い

| 次元 | Amazon | Walmart |
|------|--------|---------|
| セラー数 | 200 万+ | 25 万+ |
| 競争程度 | 極めて高い | 中程度(機会ウィンドウ) |
| Buy Box アルゴリズム | Review 数+価格+FBA | 価格の重みがより高い+WFS |
| Listing 品質スコア | 統一スコアなし | Listing Quality Score(可視) |
| 広告システム | Amazon PPC(成熟) | Walmart Connect(急成長) |
| 物流 | FBA | WFS(Walmart Fulfillment Services) |
| 手数料 | 8-15%(品目による) | 6-15%(通常やや低い) |
| 全チャネル | 純オンライン | オンライン+4700 店舗+Walmart+ |
| ユーザー像 | 全年齢、中高収入寄り | 家庭寄り、価格敏感 |

### 1.1 Walmart の独自の強み

- **競争が低め**: セラー数は Amazon の 1/8、同品目の競争プレッシャーが小さい
- **全チャネル**: オンライン注文が店舗受取可能、Amazon が到達できないユーザーをカバー
- **広告成長が速い**: Walmart Connect 広告収入 +46% YoY、早期の紅利
- **Walmart+**: 成長中の会員体系、Prime に似るが浸透率がより低い

---

## 2. Walmart SEO と Listing 最適化

> **関連リーディング**: [A2 Listing 最適化](../a-operators/a2-listing-optimization.md) Amazon Listing の汎用最適化方法論は A2 を参照でき、70% を Walmart に直接再利用可能。

### 2.1 Listing Quality Score

Walmart には可視の Listing Quality Score がある(Amazon にはない)、検索ランキングに直接影響する:

```
Listing Quality Score の構成:
コンテンツ品質(Content) — 重みが最高
タイトル: 50-75 文字が最適、形式「ブランド + 製品名 + 核心属性(サイズ/色/数量)」
必ず Title Case(各主要語の頭文字を大文字)
禁止: 全大文字、特殊文字、プロモ情報(「Sale」「Free Shipping」)
禁止: タイトルに価格を含む
Amazon との違い: Amazon は 200 文字の長いタイトルにキーワードを詰められる、Walmart は簡潔さを要求

Key Features(Bullet Points): 3-10 個、各 80 文字以内
前 3 個が最重要(折りたたみ前に可視)
動詞かベネフィットで始める(「Provides...」「Features...」)
Amazon との違い: Amazon は 500 文字/条を許す、Walmart はより精練を要求

説明: 最低 150 字、推奨 300-500 字
Rich Media 対応(A+ Content に類似)
HTML 形式を含められる(太字、リスト、表)
推奨構造: 利用シーン → 核心機能 → 仕様パラメータ → ブランドストーリー

属性(Attributes): 可能な限りすべての任意属性を記入
色、サイズ、材質、重量、産地など
属性の完全度が検索フィルタのマッチに直接影響
多くのセラーがこのステップを飛ばす、完全に記入するのは低コストのランキング向上

画像品質(Images)
メイン画像: 純白背景(RGB 255,255,255)、≥1000x1000px
補助画像: 最低 4 枚(推奨 6-8 枚)
シーン画像(使用中の製品)
サイズ対比画像(よくある物品との対比)
ディテールクローズアップ画像
パッケージ内容画像(What's in the box)
インフォグラフィック(セールスポイントの文字オーバーレイ)
動画: 強く推奨(Walmart は動画のある Listing に追加の重みを与える)
360° ビュー: 加点項目
Amazon との違い: Walmart の画像はより「素朴」を要求、過度な PS をせず、Walmart ユーザーに「本物で信頼できる」と感じさせる

価格競争力(Price)
Walmart は Amazon、Target、eBay などのプラットフォームと価格比較する
価格が高すぎると Score が下がり Buy Box を失う可能性
推奨: Walmart 価格 = Amazon 価格 かやや低く 5-10%
心理的価格設定: .88 か .97 で終わる(Walmart ユーザーの習慣)

在庫と履行(Fulfillment)
WFS 使用(顕著に加点、FBA の Amazon ランキングへの影響に類似)
配送速度: 2 日配送がベースライン、翌日達が加点
在庫充足度: 頻繁な欠品が Score を下げる
返品率: 高返品率は降格される
```

### 2.2 Walmart タイトル最適化公式

| 品目 | Amazon タイトルスタイル | Walmart タイトルスタイル(正しい) |
|------|-------------------------|-----------------------------------|
| 電子製品 | "UGREEN USB C Hub 8-in-1 Multiport Adapter with 4K HDMI, 100W PD, 3 USB 3.0, SD/TF Card Reader for MacBook Pro Air" | "UGREEN USB C Hub 8-in-1 with 4K HDMI, 100W PD Charging" |
| ホーム | "Portable Neck Fan, Hands Free Bladeless Fan, 360° Cooling, 3 Speeds, USB Rechargeable, Lightweight for Outdoor Sports Travel" | "Portable Neck Fan, Bladeless 360° Cooling, 3 Speeds, USB Rechargeable" |
| 美容 | "Vitamin C Serum for Face with Hyaluronic Acid, Retinol, Amino Acids - Anti Aging Skin Brightening Serum for Dark Spots, Fine Lines, Wrinkles - 1 fl oz" | "Vitamin C Face Serum with Hyaluronic Acid, Anti-Aging, 1 fl oz" |

**AI タイトル変換 Prompt:**

```
あなたは Walmart Listing タイトル最適化の専門家です。

以下は私の Amazon タイトルです:
[Amazon タイトルを貼り付け]

Walmart 形式に変換してください、要件:
1. 50-75 文字(Amazon は 200 を許す、Walmart は簡潔に)
2. 形式: ブランド + 製品名 + 1-2 個の核心属性
3. Title Case(各主要語の頭文字を大文字)
4. プロモ情報、価格、「Best」「#1」などの語を含まない
5. 最も重要な検索キーワードを保持
6. 3 つのバリエーションを提示
```

### 2.3 Walmart Rich Media(A+ Content に類似)

Walmart の Rich Media 機能は説明エリアに拡張コンテンツを追加できる:

| 機能 | Amazon A+ Content | Walmart Rich Media |
|------|-------------------|--------------------|
| ブランドストーリー | ✅ | ✅ |
| 対比表 | ✅ | ✅ |
| 図文モジュール | ✅ | ✅ |
| 動画埋め込み | ✅(Premium A+) | ✅(全セラー) |
| 360° ビュー | ❌ | ✅ |
| 技術要件 | Amazon バックエンドエディタ | HTML/CSS 対応 |
| 障壁 | ブランド登録が必要 | 全セラー利用可 |

> **重要な違い**: Walmart Rich Media は全セラーに開放(Amazon A+ はブランド登録が必要)、かつ HTML/CSS カスタマイズに対応し柔軟度がより高い。

**AI 生成 Walmart Rich Media コンテンツ Prompt:**

```
あなたは Walmart Rich Media コンテンツの専門家です。

製品: [名称]
セールスポイント: [5 個]
ターゲットオーディエンス: Walmart ユーザー(家庭寄り、価格敏感、実用性重視)

Rich Media コンテンツ方案を生成してください:
1. ブランドストーリーモジュール(100 字、品質と価値を強調)
2. 製品特性モジュール(3 つの図文ブロック、各: タイトル+50 字説明+画像提案)
3. 対比表(私の製品 vs 2 つの競合、5 つの次元)
4. 利用シーンモジュール(3 つのシーン、各: シーン名+30 字説明+画像提案)
5. FAQ モジュール(5 つのよくある質問+回答)

注意: Walmart ユーザーは「実用性」と「コスパ」をより重視、「高級ブランド感」を出しすぎない。
```

---

## 3. Walmart Connect 広告

> **関連リーディング**: [A3 広告最適化](../a-operators/a3-advertising.md) 検索語レポート分析の汎用方法論を Walmart Connect に直接再利用可能。

### 3.1 広告タイプ詳解

| 広告タイプ | 枠 | 課金 | 最低入札 | 向く |
|------------|-----|------|----------|------|
| Sponsored Products - Automatic | 検索結果+製品ページ | CPC | $0.20 | 新製品テスト、キーワード発見 |
| Sponsored Products - Manual | 検索結果+製品ページ | CPC | $0.20 | 精確なキーワード投下 |
| Sponsored Brands | 検索結果トップバナー | CPC | $1.00 | ブランド認知、品目占位 |
| Sponsored Videos | 検索結果の動画枠 | CPC | $0.20 | 製品演示、差別化展示 |
| Display Ads | サイト内+サイト外 | CPM/CPC | Campaign による | リマーケティング、ブランド露出 |

### 3.2 第一価格入札 vs 第二価格入札

これが Walmart と Amazon 広告の最大の違い:

```
Amazon(第二価格入札):
あなたが $1.50 入札、第二高入札が $1.00
→ あなたが実際に支払うのは $1.01(第二高+$0.01)
→ 戦略: 高価を入札でき、実際はそこまで払わない

Walmart(第一価格入札):
あなたが $1.50 入札
→ あなたが実際に支払うのは $1.50(入札した分だけ払う)
→ 戦略: 精確に入札する必要、高く入札すればお金の無駄
```

**Walmart 入札戦略のベストプラクティス:**

| 戦略 | 説明 | 適用シーン |
|------|------|------------|
| 保守的入札 | 品目推奨入札の 70% から始める | 新製品テスト期 |
| ラダーテスト | 3 日ごとに 10% 上げ、ROAS の変化を観察 | 最適入札を見つける |
| 時間帯調整 | 高転換時間帯(週末/夜)に入札を上げる | 成熟期の最適化 |
| キーワード階層化 | 高転換語に高入札、ロングテール語に低入札 | 予算が限られるとき |
| 自動+手動組み合わせ | 自動 Campaign で語を発見、手動 Campaign で精確に投下 | すべての段階 |

### 3.3 Walmart 検索語レポート分析

Walmart の検索語レポート形式は Amazon と異なり、AI 分析 Prompt を適応する必要がある:

```
あなたは Walmart Connect 広告最適化の専門家です。

以下は私の Walmart 検索語レポートデータ(過去 14 日):

Campaign: [名称]
総費用: $[X]
総クリック: [X]
総注文: [X]
ROAS: [X]

検索語データ(費用順 Top 20):
| 検索語 | 表示 | クリック | 費用 | 注文 | 売上 | ROAS |
[データを貼り付け]

分析してください:
1. 高 ROAS 語(>4x): これらの語の入札をどれだけ上げるべきか?
2. 低 ROAS 語(<2x): どれの入札を下げ、どれを否定すべきか?
3. 高表示低クリック語: 入札の問題か Listing の問題か?
4. 零転換高費用語: 即座に否定する候補語
5. 新たに発見したロングテール機会語
6. 予算再配分の提案

Walmart の特殊性に注意:
- 第一価格入札、入札調整はより精確に(Amazon のように高価入札できない)
- Walmart ユーザーはより価格敏感、低価製品の転換率が通常より高い
- 週末と夜の転換率は通常、平日昼間より高い
```

### 3.4 Walmart 広告 30 日起動計画

```
Week 1: データ収集期
1 つの Automatic Campaign を起動(予算 $20/日)
1 つの Manual Campaign を起動(5-10 個の核心キーワード、予算 $15/日)
入札: 品目推奨入札の 80%
目標: 検索語データを収集、ROAS を追わない

Week 2: 最適化期
検索語レポートを分析
Automatic から高転換語を抽出 → Manual に加える
低効率語を否定
入札を調整(高転換語 +15%、低転換語 -20%)
目標: ROAS > 2x

Week 3: 拡張期
Sponsored Brands Campaign を追加(ブランド登録があれば)
Sponsored Videos をテスト(動画素材があれば)
キーワードリストを拡張(ロングテール語を加える)
高転換 Campaign の予算を上げる
目標: ROAS > 3x

Week 4: スケール化
安定した Campaign の予算を 30-50% 上げる
Display Ads を起動(リマーケティング)
毎週の最適化 SOP を確立
目標: ROAS > 4x、広告売上シェア 20-30%
```

---

## 4. WFS 物流の意思決定

> **関連リーディング**: [A5 在庫管理](../a-operators/a5-inventory.md) 在庫管理と補充の意思決定の汎用方法論は A5 を参照。

### 4.1 WFS vs FBA 詳細対比

| 次元 | WFS | FBA |
|------|-----|-----|
| 保管料(標準) | $0.75/立方フィート/月 | $0.87/立方フィート/月(1-9月) |
| 保管料(繁忙期) | 繁忙期加算なし | $2.40/立方フィート/月(10-12月) |
| 配送費(小件) | $3.45〜 | $3.22〜 |
| 配送費(大件) | 通常 FBA より 10-15% 低い | やや高い |
| 長期保管料 | なし(2026 年政策) | あり(365 日後に徴収) |
| 返品処理 | Walmart が処理、費用が低め | Amazon が処理、費用が高め |
| マルチチャネル配送 | MCS(新機能、初回ユーザー -30%) | MCF |
| Buy Box 加成 | 顕著(FBA に類似) | 顕著 |
| 配送速度 | 2-3 日(Walmart+ 翌日達) | 1-2 日(Prime) |
| 入庫要件 | やや緩い | 厳格(ラベル/梱包要件が多い) |

### 4.2 WFS コスト計算 AI Prompt

```
あなたは EC 物流コスト分析の専門家です。

私の製品情報:
- 製品サイズ: [長x幅x高] インチ
- 製品重量: [X] ポンド
- 月販売量: Amazon [X] 件、Walmart [X] 件
- 現在の FBA 費用/件: $[X]

計算し対比してください:
1. FBA 月間総コスト(配送費+保管料+長期保管リスク)
2. WFS 月間総コスト(配送費+保管料)
3. 自己発送コスト見積もり(USPS/UPS/FedEx)
4. 最適物流方案の提案
5. 在庫配分比率の提案(FBA:WFS:自己発送)
```

### 4.3 Walmart Multichannel Solutions (MCS)

MCS は Walmart のマルチチャネル配送サービス(Amazon MCF に類似)、2026 年新登場:
- WFS 在庫で他チャネル(Shopify、eBay、自社サイト)の注文を配送
- 初回ユーザーは 30% 配送費割引
- Shopify、BigCommerce、WooCommerce と統合
- 配送速度: 2-3 日

> **戦略提案**: Amazon と Walmart の両方で販売するなら、WFS+MCS で FBA+MCF の一部を代替でき、物流コストを下げられる(特に繁忙期、WFS には繁忙期保管加算がない)。

---

## 5. Amazon → Walmart 移行方法論

### 5.1 移行前評価

```
あなたはマルチプラットフォーム EC 戦略の専門家です。

私の現在の Amazon の業務データ:
- 品目: [X]
- 月販売量: [X] 件
- 月収入: $[X]
- 平均販売価: $[X]
- 利益率: [X]%
- 主要競合数: [X]

Walmart 移行の可行性を評価してください:
1. この品目の Walmart での競争程度(その品目キーワードを検索、結果数と Review 数を見る)
2. 価格帯が Walmart ユーザーにマッチするか(Walmart ユーザーの平均客単価は Amazon より低い)
3. 推定 Walmart 月販売量(通常 Amazon の 10-30%、品目による)
4. 推定利益率の変化(手数料差+物流差+広告差)
5. 移行優先度の提案(即座/様子見/非推奨)
```

### 5.2 詳細な移行チェックリスト

```
Phase 1: 準備期(1-2 週間)
[ ] Walmart Marketplace セラーアカウントを登録
必要: 米国会社実体(または EIN)
必要: W-9 税表
審査時間: 2-4 週間
注意: Walmart の審査は Amazon より厳格、すべての申請が通るわけではない
[ ] UPC/GTIN を準備(Walmart は各製品に固有 UPC を要求)
[ ] 製品画像を準備(Walmart スタイルに適応、より「素朴」に)
[ ] Walmart 品目手数料率を調査

Phase 2: Listing 出品(1 週間)
[ ] タイトル形式を変換(50-75 文字、Title Case)
[ ] Key Features を書き直し(各 ≤80 文字、より精練)
[ ] Rich Media コンテンツを作成
[ ] すべての製品属性を記入(Listing Quality Score を高める)
[ ] 価格を設定(推奨 = Amazon 価格 か -5~10%)
[ ] 画像をアップロード(Walmart スタイルに適応)

Phase 3: 物流設定(1 週間)
[ ] WFS を登録
[ ] 入庫計画を作成
[ ] 初回在庫を送る(推奨 30 日販売量)
[ ] 自己発送の代替案を設定

Phase 4: 広告起動(2-4 週間)
[ ] Automatic Campaign を起動
[ ] Manual Campaign を起動(核心キーワード)
[ ] 毎週検索語レポートを分析
[ ] 入札とキーワードを段階的に最適化

Phase 5: 継続的最適化
[ ] 毎週 Listing Quality Score をチェック
[ ] 毎週広告を最適化
[ ] Buy Box 状態を監視
[ ] Walmart プロモに参加(Rollbacks、Flash Deals)
[ ] Walmart 専用データ追跡を確立
```

### 5.3 Walmart 特有のプロモ機構

| プロモタイプ | 説明 | Amazon との対比 |
|--------------|------|-----------------|
| Rollbacks | 一時的な値下げ、Walmart が「Rollback」タグを付ける | Lightning Deal に類似 |
| Flash Deals | 期間限定特価 | Lightning Deal に類似 |
| Clearance | 在庫処分価 | Outlet Deal に類似 |
| Walmart+ Weekend | Walmart+ 会員専属プロモ | Prime Day に類似 |
| 祝日プロモ | BFCM、Back to School など | 類似 |

### 5.4 よくある移行の誤り

| 誤り | 結果 | 正しいやり方 |
|------|------|--------------|
| Amazon タイトルをそのままコピー | Listing Quality Score が低い、ランキングが悪い | 50-75 文字の Walmart 形式に書き直し |
| Amazon 価格を使う | Buy Box を失う可能性(Walmart は価格比較がより厳格) | 価格 = Amazon 価格かやや低く |
| 属性記入を無視 | 検索フィルタにマッチしない | すべての任意属性を記入 |
| Amazon PPC 入札戦略を使う | 予算の無駄(第一価格入札) | 推奨入札 70% から始め、段階的に調整 |
| WFS を使わない | Buy Box の優位を失う | WFS を優先使用 |
| Walmart ユーザー像を無視 | コンテンツが不一致 | 実用性とコスパを強調、「高級」すぎない |

---

## 6. Prompt テンプレート

### 6.1 Walmart 品目機会分析

```
あなたは Walmart Marketplace 品目分析の専門家です。

私は現在 Amazon で [品目] を販売、月販 [X] 件。

この品目の Walmart での機会を分析してください:
1. Walmart 上のこの品目の競争程度(セラー数、Review 数)
2. 価格帯の対比(Walmart vs Amazon)
3. 推定月販売量ポテンシャル
4. 参入戦略の提案
5. 注意すべき Walmart 特有のコンプライアンス要件
```

---

## 6.2 Walmart Buy Box 深度解析

### Buy Box アルゴリズム因子の重み

Walmart Buy Box と Amazon Buy Box の核心的違いは価格の重みがより高いこと:

```
Walmart Buy Box アルゴリズム因子(重み順):

1. 価格(重みが最高)
製品価格 + 送料の総価
Amazon/Target/eBay などのプラットフォームとの価格比較
価格が高すぎると直接 Buy Box を失う
推奨: 総価(製品+送料)≤ Amazon の同製品価格
心理的価格設定: .88 か .97 で終わる

2. 配送速度と方式
WFS(Walmart Fulfillment Services)→ 最高優先度
2 日配送 → 高優先度
3-5 日配送 → 中優先度
5+ 日配送 → 低優先度
Walmart+ 翌日達 → 追加加点

3. セラーパフォーマンス指標
On-Time Delivery Rate(定時発送率)> 95%
Valid Tracking Rate(有効追跡率)> 99%
Cancellation Rate(キャンセル率)< 2%
Return Rate(返品率)は低いほど良い
Customer Satisfaction(顧客満足度スコア)

4. 在庫の深さ
在庫充足 → 加点
頻繁な欠品 → 降格
予約販売/欠品状態 → Buy Box を失う

5. セラーアカウント健全度
アカウント年齢
過去の販売量
ブランド登録状態
違反記録
```

> **関連リーディング**: [D1 Shopify](shopify-ai-guide.md) 独立サイトも運営するなら、Shopify のブランド構築と DTC 戦略は D1 を参照。

### Buy Box 監視と最適化 AI Prompt

```
あなたは Walmart Buy Box 最適化の専門家です。

私の製品データ:
- ASIN/Item ID: [X]
- 私の販売価: $[X]
- 競合最低価: $[X]
- 私の配送方式: [WFS/自己発送/2日配送]
- 私の Buy Box 占有率: [X]%
- 私のセラー評価: [X]
- 競合数: [X] のセラー

分析してください:
1. なぜ私は 100% Buy Box を占有していないか?
2. 価格をいくらに調整すれば Buy Box 占有率を上げられるか?
3. 配送方式はアップグレードが必要か?
4. セラーパフォーマンスのどの指標を改善する必要があるか?
5. 複数の競合セラーがいる場合、私の競争戦略は?
6. 自動調価ツールの使用を推奨するか?そうならどれを推奨?
```

### Walmart 自動調価戦略

| 戦略 | 説明 | 適用シーン | リスク |
|------|------|------------|--------|
| 最低価に追随 | 常に最低価にマッチ | 標準品、複数セラー競争 | 利益が圧縮される |
| 価格区間 | 最低/最高価を設定、区間内で調整 | ブランドプレミアムのある製品 | たまに Buy Box を失うかも |
| ROAS ベース調価 | 広告 ROAS が高いとき値上げ、低いとき値下げ | 広告駆動の製品 | データ蓄積が必要 |
| 時間帯調価 | 週末/夜に値上げ、平日に値下げ | 転換率に時間帯差のある製品 | テスト検証が必要 |
| 競合連動 | 競合価格変化を監視、自動応答 | 競争激しい品目 | 価格戦争を招くかも |

---

## 6.3 Walmart 品目手数料率詳細表

| 品目 | 手数料率 | Amazon との対比 |
|------|----------|-----------------|
| 消費電子 | 8% | Amazon 8-15% |
| ホーム・家具 | 10% | Amazon 15% |
| アパレル | 5-15% | Amazon 17% |
| 美容・パーソナルケア | 8% | Amazon 8-15% |
| おもちゃ | 8% | Amazon 15% |
| スポーツ・アウトドア | 8% | Amazon 15% |
| ペット用品 | 8% | Amazon 15% |
| 食品・食料品 | 8% | Amazon 8% |
| ジュエリー・時計 | 15% | Amazon 20% |
| 自動車部品 | 12% | Amazon 12% |

> **重要な発見**: Walmart はホーム(10% vs 15%)、アパレル(5-15% vs 17%)、おもちゃ(8% vs 15%)、ジュエリー(15% vs 20%)などの品目で手数料率が Amazon より著しく低い。これらの品目は Walmart での利益余地がより大きい。

---

## 6.4 Walmart Seller Center データ分析

### 主要レポートと指標

```
Walmart Seller Center 核心レポート:

一、販売レポート
Item Performance(単品パフォーマンス)
Page Views(ページ閲覧数)
Units Sold(販売量)
Revenue(収入)
Buy Box %(Buy Box 占有率)
Conversion Rate(転換率)

Sales Trend(販売トレンド)
日/週/月の販売トレンド
前年比/前月比の変化
品目対比

Returns Report(返品レポート)
返品率
返品理由の分類
返品コスト

二、広告レポート(Walmart Connect)
Campaign Performance
Search Term Report
Keyword Performance
Placement Report

三、在庫レポート
Inventory Health
WFS Inventory
Stranded Inventory
Restock Recommendations

四、セラーパフォーマンス
On-Time Delivery Rate
Valid Tracking Rate
Cancellation Rate
Customer Satisfaction Score
Policy Compliance
```

### AI 週報分析 Prompt

```
あなたは Walmart Marketplace データ分析の専門家です。

以下は私の Walmart 店舗の過去 7 日のデータです:

販売データ:
- 総収入: $[X]（先週 $[X]、変化 [X]%）
- 総注文: [X]（先週 [X]）
- 平均客単価: $[X]
- 転換率: [X]%
- Buy Box 平均占有率: [X]%

Top 5 製品パフォーマンス:
| 製品 | ページ閲覧 | 販売量 | 収入 | 転換率 | Buy Box% |
[データを貼り付け]

広告データ:
- 総広告費用: $[X]
- 広告収入: $[X]
- ROAS: [X]
- ACOS: [X]%

セラーパフォーマンス:
- 定時発送率: [X]%
- 有効追跡率: [X]%
- キャンセル率: [X]%
- 返品率: [X]%

提供してください:
1. 今週のパフォーマンス総括(3 文、先週と対比)
2. 最も好調な製品と原因分析
3. 不調の製品と改善提案
4. Buy Box 占有率の変化分析(下がった場合、原因は何か)
5. 広告最適化提案(ROAS と検索語データに基づく)
6. セラーパフォーマンス改善提案(基準を下回る指標があれば)
7. 来週の重点アクション項目(最大 3 個)
```

---

## 6.5 Walmart 全チャネル戦略

### オンライン+オフラインの協働(Walmart 独自の強み)

Walmart は 4700+ の実体店舗を持ち、これは Amazon にはない:

| 全チャネル機能 | 説明 | セラーへの影響 |
|----------------|------|----------------|
| Store Pickup | オンライン注文、店舗受取 | 転換率を高める(ユーザーがより便利と感じる) |
| Ship from Store | 最寄り店舗から発送 | より速い配送速度 |
| Returns to Store | オンライン購入、店舗返品 | 返品の摩擦を下げる(だが返品率を上げるかも) |
| Walmart+ | 会員無料配送+店舗優待 | 会員ユーザーの転換率がより高い |
| Local Delivery | ローカル 2 時間配送 | 特定品目(食品/日用品)の優位 |

### Walmart+ 会員戦略

Walmart+ は Walmart の会員計画(Amazon Prime に類似):
- 月額 $12.95 か年額 $98
- 無料配送(最低消費なし)
- 店舗スキャン決済
- Paramount+ ストリーミング
- 給油割引

**セラーへの影響**:
- Walmart+ 会員の転換率は非会員より 30-50% 高い
- WFS 製品は自動で Walmart+ 無料配送を享受
- 推奨: WFS を優先使用、製品が Walmart+ 会員に魅力的なことを確保

---

## 6.6 Walmart よくある落とし穴の深度解析

### 落とし穴 1: Amazon Listing をそのままコピー

**問題**: Amazon タイトルは 200 文字にキーワードを詰め込む、Walmart タイトルは 50-75 文字の簡潔明瞭を要求。そのままコピーすると Listing Quality Score が極めて低くなる。

**事例**:
```
Amazon タイトル(誤った例):
"UGREEN USB C Hub 8-in-1 Multiport Adapter with 4K HDMI 60Hz, 100W Power Delivery, 3 USB 3.0 Ports, SD/TF Card Reader, Gigabit Ethernet for MacBook Pro Air iPad Pro Dell XPS Surface Pro"

Walmart タイトル(正しい):
"UGREEN USB C Hub 8-in-1 with 4K HDMI, 100W PD Charging"
```

**AI 修復 Prompt**:
```
以下は私が Amazon から Walmart にコピーした Listing です、Walmart 形式に適応させてください:

Amazon タイトル: [貼り付け]
Amazon Bullet Points: [貼り付け]
Amazon 説明: [貼り付け]

出力してください:
1. Walmart タイトル(50-75 文字、Title Case)
2. Walmart Key Features(3-10 条、各 ≤80 文字)
3. Walmart 説明(300-500 字、構造化、HTML 対応)
4. 記入が必要な製品属性リスト
5. Listing Quality Score の見積もりと最適化提案
```

### 落とし穴 2: Walmart ユーザー像の違いを無視

**問題**: Walmart ユーザーと Amazon ユーザーの像が異なり、コンテンツ戦略の調整が必要。

| 次元 | Amazon ユーザー | Walmart ユーザー |
|------|-----------------|------------------|
| 収入水準 | 中高収入 | 中低収入、家庭が主 |
| 購買動機 | 便利+選択が多い | 価格+実用性 |
| 決定要因 | Review 数+ブランド | 価格+配送速度 |
| コンテンツ嗜好 | 詳細なパラメータ+ブランドストーリー | 簡潔で実用的+コスパを強調 |
| 画像嗜好 | 精緻+ライフスタイル | 本物+実用+明瞭 |

**AI コンテンツ適応 Prompt**:
```
以下は私の Amazon 製品説明です、Walmart ユーザーに適したスタイルに書き直してください:

Amazon 説明: [貼り付け]

Walmart ユーザーの特徴:
- より価格敏感、コスパを強調
- 実用性をより重視、ブランドストーリーを減らす
- 簡潔で直接的な表現を好む
- 家庭ユーザーが主、家庭使用シーンを強調

書き直してください、核心情報を保ちつつトーンと重点を調整。
```

### 落とし穴 3: 広告入札が高すぎる(第一価格入札)

**問題**: Amazon から来た多くのセラーは高価入札に慣れている(Amazon は第二価格入札で実際はそこまで払わないから)。Walmart で高価入札すると実際に高く払う。

**解決策**:
```
Walmart 入札最適化ステップ:

1. 品目推奨入札を確認(Walmart バックエンドが提供)
2. 初期入札 = 推奨入札 × 70%
3. 3 日実行、表示量とクリック量を観察
4. 表示量が不足なら → 10% 上げる
5. 表示量は十分だが ROAS が低いなら → 10% 下げる
6. 3 日ごとに調整、最適入札を見つけるまで
7. 各キーワードの最適入札を記録、入札データベースを構築

重要な原則:
- 一度に大幅な入札調整をしない(±10% が適切)
- 高転換語は推奨入札より高く入札できる
- ロングテール語の入札は推奨入札より 30-50% 低く
- 週末/夜は入札を適度に上げられる(転換率がより高い)
```

### 落とし穴 4: Walmart プロモに参加しない

**問題**: Walmart のプロモ(Rollbacks、Flash Deals)はランキングとトラフィックに顕著な影響があるが、多くの新規セラーは参加方法を知らない。

**Walmart プロモ参加ガイド**:

| 活動タイプ | 参加方法 | 割引要件 | トラフィック向上 |
|------------|----------|----------|------------------|
| Rollback | Seller Center バックエンドで申請 | 通常 10-25% off | ✅ |
| Flash Deal | 招待か申請が必要 | 通常 20-40% off | ✅✅ |
| Clearance | 手動で在庫処分価を設定 | 大幅割引 | ✅ |
| Walmart+ Weekend | 自動参加(WFS 製品) | 追加割引要件なし | ✅✅ |
| 祝日プロモ | 4-6 週間前に申請 | 活動による | ✅✅✅ |

### 落とし穴 5: Walmart Review 戦略を無視

**問題**: Walmart の Review システムは Amazon と異なる。Walmart は Spark Reviewer Program(Vine に類似)を許すが、多くのセラーは知らない。

**Walmart Review 獲得戦略**:
- Spark Reviewer Program: Walmart の公式レビュー計画、Amazon Vine に類似
- Review Accelerator: 有料レビュー獲得(Walmart 公式プログラム)
- 自然 Review: 優質な製品とサービスで蓄積
- 注意: Walmart はレビュー操作を禁止、違反はアカウント停止

---

## 6.7 Walmart AI ツール生態系

| ツール | 用途 | 価格 | 推奨度 |
|--------|------|------|--------|
| **Walmart Seller Center** | 公式バックエンド、Listing/注文/広告管理 | 無料 | ✅✅✅ |
| **Aura** | 自動調価+Buy Box 監視 | $97/月〜 | ✅✅ |
| **Helium 10 (Walmart)** | キーワードリサーチ+Listing 最適化 | $79/月〜 | ✅✅ |
| **Teikametrics** | AI 広告最適化 | 広告費用の割合による | ✅✅ |
| **SellerApp** | データ分析+広告最適化 | $49/月〜 | ✅ |
| **ChatGPT/Claude** | Listing コピー+データ分析+戦略計画 | $20/月 | ✅✅✅ |
| **Canva** | 製品画像デザイン | 無料/Pro $13/月 | ✅✅ |

---

## 7. 完了チェック

- [ ] Walmart セラー登録を完了
- [ ] 最低 10 個の Listing を適応しアップロード
- [ ] WFS を設定し初回発送を完了
- [ ] Walmart Connect 広告を起動
- [ ] Walmart データ分析フローを確立
