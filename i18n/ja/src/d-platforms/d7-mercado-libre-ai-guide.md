# D7. Mercado Libre 中南米 EC AI ガイド

> **トラック**: Path D: マルチプラットフォーム · **モジュール**: D7
> **最終更新**: 2026-07-31
> **難易度**: 中級
> **所要時間**: 1.5 時間


---

> GMV $65B(2025)、1.2 億の年間買い手、収入 +39% YoY。中南米最大の EC プラットフォーム、最も成長の速い地域市場。核心市場: ブラジル(最大)、メキシコ、アルゼンチン、コロンビア。

## 章ナビゲーション

1. [中南米市場概観](#1-中南米市場概観) · 2. [スペイン語/ポルトガル語 Listing AI 最適化](#2-スペイン語ポルトガル語-listing-ai-最適化) · 3. [Mercado Libre 特有の運営の違い](#3-mercado-libre-特有の運営の違い) · 4. [越境出店](#4-越境出店) · 5. [Mercado Libre Global Selling 深度ガイド](#5-mercado-libre-global-selling-深度ガイド) · 6. [よくある罠](#6-よくある罠) · 7. [完了チェック](#7-完了チェック)

---

## このモジュールで学べること

中南米は最も成長が速く、競争密度は北米よりはるかに低い。言語と決済が主な障壁だ。

このモジュールを終えると、次ができるようになる:
- 中南米各国の市場差を読み、どのサイトから始めるか判断できる
- 機械翻訳ではなく、現地の語感に合うスペイン語/ポルトガル語 Listing を AI で作れる
- Mercado Libre と Amazon のルール・運営リズムの決定的な違いを押さえる
- 越境出店の手続きを完了し、Global Selling で多国展開できる

---


## 1. 中南米市場概観

| 国 | 人口 | EC 規模 | 主要プラットフォーム | 言語 |
|----|------|---------|----------------------|------|
| ブラジル | 2.1 億 | 最大 | Mercado Libre > Amazon BR | ポルトガル語 |
| メキシコ | 1.3 億 | 第二 | Mercado Libre > Amazon MX | スペイン語 |
| アルゼンチン | 4600 万 | 第三 | Mercado Libre が主導 | スペイン語 |
| コロンビア | 5100 万 | 成長が速い | Mercado Libre > Falabella | スペイン語 |

### 1.1 Mercado Libre 生態系

- **Mercado Pago**: 決済システム(中南米版 Alipay)
- **Mercado Envios**: 物流ネットワーク(FBA に類似)
- **Mercado Ads**: 広告システム
- **Mercado Shops**: 独立サイトツール(Shopify に類似)

## 2. スペイン語/ポルトガル語 Listing AI 最適化

### 2.1 言語の違い詳解

| 次元 | ブラジルポルトガル語 vs ポルトガルのポルトガル語 | 中南米スペイン語 vs スペインのスペイン語 |
|------|--------------------------------------------------|--------------------------------------------|
| 差異の程度 | 大きい(語彙+文法+発音) | 中程度(語彙+用語習慣) |
| アナロジー | 米国英語 vs 英国英語に類似 | 米国英語 vs 英国英語に類似 |
| AI 翻訳の注意 | 必ず「ブラジルポルトガル語」を指定 | 必ず「中南米スペイン語」を指定 |
| よくある誤り | "telemóvel"(ポルトガル) vs "celular"(ブラジル) | "ordenador"(スペイン) vs "computadora"(中南米) |
| 呼称の違い | "você"(ブラジル) vs "tu"(ポルトガル) | "vosotros"(スペイン) vs "ustedes"(中南米) |

### 2.2 Mercado Libre タイトル最適化

> **関連リーディング**: [A2 Listing 最適化](../a-operators/a2-listing-optimization.md) 多言語ローカライズの汎用方法論は A2 を参照、Listing 最適化フレームワークをスペイン語/ポルトガル語に適応可能。

Mercado Libre のタイトル形式は Amazon と異なる:

| 次元 | Amazon | Mercado Libre |
|------|--------|---------------|
| 文字制限 | 200 文字 | 60 文字(より短い) |
| 形式 | ブランド+キーワード詰め込み | ブランド+製品+核心属性 |
| 言語 | 英語 | スペイン語/ポルトガル語(現地言語必須) |
| キーワード戦略 | タイトルにキーワードを詰める | タイトルは簡潔、キーワードは属性と説明に置く |

### 2.3 AI ローカライズ Prompt(強化版)

```
あなたは中南米 EC ローカライズの専門家で、ブラジルとメキシコ市場に精通しています。

以下は私の英語製品 Listing です:
- タイトル: [英語タイトル]
- 説明: [英語説明]
- セールスポイント: [5 個]
- 価格: $[X] USD

以下に翻訳してください:

1. ブラジルポルトガル語版
- タイトル(≤60 文字、ブラジルポルトガル語、ポルトガルのポルトガル語ではなく)
- 説明(300-500 字、口語的、"você" を使用)
- 5 つのセールスポイント
- 価格を R$ に変換(現在の為替レートで)
- 10 個のブラジルポルトガル語検索キーワード
- ブラジル消費者が特に気にする点(例 "frete grátis" 送料無料、"parcelamento" 分割払い)

2. 中南米スペイン語版(メキシコ)
- タイトル(≤60 文字、中南米スペイン語、スペインのスペイン語ではなく)
- 説明(300-500 字、品目により "usted" か "tú" を使用)
- 5 つのセールスポイント
- 価格を MXN に変換
- 10 個のメキシコスペイン語検索キーワード
- メキシコ消費者が特に気にする点(例 "envío gratis" 送料無料、"meses sin intereses" 無利息分割)

注意:
- Mercado Libre タイトル形式: ブランド+製品+核心属性(≤60 文字)
- 中南米消費者は分割払いオプションを極度に気にする
- 送料無料(frete grátis / envío gratis)が転換率の鍵となる要因
- 欧州のポルトガル語/スペイン語の表現を使わない
```

## 3. Mercado Libre 特有の運営の違い

### 3.1 ランキングアルゴリズム詳解

| 要因 | 重み | 説明 | AI 応用 |
|------|------|------|---------|
| 物流等級 | ⭐⭐⭐ | Mercado Envios Full(FBA に類似)がランキングを大幅に向上 | 物流方案の意思決定 |
| 価格競争力 | ⭐⭐⭐ | 中南米ユーザーは極度に価格敏感 | AI 競合価格監視 |
| セラー信用 | ⭐⭐ | MercadoLíder 等級が露出に影響 | 高評価率を維持 |
| 販売量 | ⭐⭐ | 過去の販売量がランキングに影響 | 初期はプロモで量を上げる必要があるかも |
| Listing 品質 | ⭐⭐ | 画像+説明の完全度 | AI で Listing を最適化 |
| 分割払い | ⭐⭐ | 無利息分割を提供する製品はランキングが高い | 分割オプションを設定 |

### 3.2 Mercado Libre セラー等級

| 等級 | 要件 | 権益 |
|------|------|------|
| 普通セラー | 新規登録 | 基礎機能 |
| MercadoLíder | 販売量+高評価率が基準達成 | より多くの露出+より低い手数料 |
| MercadoLíder Gold | より高い販売量+より高い高評価率 | 最多露出+最低手数料+専属 CS |

### 3.3 Mercado Ads 広告システム

> **関連リーディング**: [A3 広告最適化](../a-operators/a3-advertising.md) 広告最適化の汎用方法論は A3 を参照、CPC 広告最適化フレームワークを Mercado Ads に再利用可能。

| 広告タイプ | 説明 | 課金 |
|------------|------|------|
| Product Ads | 検索結果ページ広告 | CPC |
| Display Ads | サイト内ディスプレイ広告 | CPM |
| Brand Ads | ブランドバナー(ブランド認証が必要) | CPC |

```
あなたは Mercado Ads 最適化の専門家です。

私の製品: [名称]、品目 [X]
ターゲット国: [ブラジル/メキシコ]
日予算: [X] 現地通貨

広告最適化提案を出してください:
1. キーワード戦略(現地言語キーワード)
2. 入札戦略(中南米市場の競争程度を考慮)
3. 広告タイプの選択
4. Mercado Envios Full との連携戦略
5. 大型セール期間(Hot Sale、Buen Fin、Black Friday)の広告調整
```

### 3.4 中南米特有のプロモ機構

| プロモ | 国 | 時間 | 説明 |
|--------|----|------|------|
| Hot Sale | メキシコ | 5月 | メキシコ最大の EC プロモ |
| Buen Fin | メキシコ | 11月 | メキシコ版 Black Friday |
| Black Friday | ブラジル | 11月 | ブラジル最大のプロモ |
| Dia do Consumidor | ブラジル | 3月15日 | 消費者の日プロモ |
| CyberMonday | アルゼンチン | 11月 | アルゼンチンの EC プロモ |

## 4. 越境出店

### 4.1 CBT(Cross-Border Trade)モデル詳解

Mercado Libre の CBT は越境セラー専用に設計された出店モデル:

```
CBT 出店フロー:

Step 1: 登録
Mercado Libre CBT パートナー経由で申請
中国会社の直接登録に対応
提供が必要: 営業許可証、法人身分証、銀行口座
審査時間: 1-2 週間

Step 2: 製品出品
バッチアップロードに対応(API か Excel)
スペイン語/ポルトガル語 Listing が必須(英語は不可)
画像要件: 白背景メイン画像 + 最低 3 枚の補助画像
価格設定: 現地通貨(R$/MXN/ARS)

Step 3: 物流選択
Mercado Envios Full(推奨)
FBA に類似: Mercado Libre 倉庫に発送
配送速度: 1-3 日(ローカル倉発送)
ランキングが大幅向上
返品は Mercado Libre が処理
Mercado Envios(標準)
セラーが発送、Mercado Libre が物流ラベルを提供
配送速度: 3-7 日
CBT 越境直送
中国から買い手に直送
配送速度: 15-30 日
ランキング重みが最低
非推奨(テスト段階を除く)
```

### 4.2 Mercado Libre 2025 Q4 主要データ

> **実事例: Mercado Libre は「中南米の Amazon」と呼ばれるがそれをはるかに超える**
> 2026 年 2 月時点で、Mercado Libre は中南米に不可欠なデジタルインフラとしての地位を固く確立した。「中南米の Amazon」という比喩はますますその生態系の全範囲を捉えきれなくなっている — それは同時に決済プラットフォーム(Mercado Pago)、物流ネットワーク(Mercado Envios)、信用サービス(Mercado Credito)、広告プラットフォームである([Financial Content](https://www.financialcontent.com/article/finterra-2026-2-27-the-latin-american-flywheel-a-2026-deep-dive-research-feature-on-mercadolibre-meli))。

Content rephrased for compliance with licensing restrictions.

Mercado Libre の Q4 2025 決算レポート([Morningstar](https://www.morningstar.com/news/business-wire/20260224265595/))に基づく:

| 指標 | Q4 2025 データ | YoY 変化 |
|------|----------------|----------|
| 純収入 | $8.8B | +45% |
| GMV | $19.9B | +37% |
| 通年収入 | ~$29B | +39% |
| ブラジル items sold | - | +45% YoY |
| ブラジル FX-neutral GMV | - | +35% YoY |
| 営業利益率 | 10.1% | -340bps(戦略投資) |

主要な戦略投資の方向:
- 無料配送閾値の引き下げ(ブラジル)→ 販売量急増
- クレジットカード事業の拡張
- 1P(自社)事業
- CBT 越境貿易
- 物流ネットワークの拡張

> **セラーへの示唆**: Mercado Libre は無料配送と物流インフラに大きく投資している。Mercado Envios Full を使うセラーが最大のトラフィック紅利を得る。中南米の EC 浸透率はわずか 12-15%(vs 米国 27%、中国 35%+)、成長余地が巨大。

Content rephrased for compliance with licensing restrictions. Sources: [Morningstar](https://www.morningstar.com/news/business-wire/20260224265595/), [Finimize](https://finimize.com/content/meli-asset-snapshot).

### 4.3 中南米市場特有の課題

> **関連リーディング**: [A6 コンプライアンスとリスク管理](../a-operators/a6-compliance.md) マルチ市場コンプライアンス方法論は A6 を参照、中南米各国の税務と認証要件は汎用コンプライアンスフレームワークを参照可能。

| 課題 | 説明 | 対応戦略 |
|------|------|----------|
| 高返品率 | 中南米の物流インフラの制限、返品プロセスが複雑 | Mercado Envios Full を使う(返品はプラットフォームが処理) |
| 為替変動 | アルゼンチンペソ、ブラジルレアルの変動が大きい | 定期的に価格を調整、Mercado Pago 自動決済を使う |
| 分割払い文化 | 中南米消費者は分割に慣れている(12-18 回無利息) | 分割オプションを必ず有効化、さもないと転換率が極めて低い |
| 税務の複雑さ | 各国の税制が異なる、ブラジルの税務は特に複雑 | Mercado Libre の税務計算ツールを使う |
| 偽物/侵害 | プラットフォーム上の偽物問題が深刻 | ブランド保護を登録、Mercado Libre のブランド保護プログラムを使う |

## 5. Mercado Libre Global Selling 深度ガイド

### 5.1 Global Selling プラットフォーム概観

Mercado Libre Global Selling([global-selling.mercadolibre.com](https://global-selling.mercadolibre.com/landing/about))はワンストップの越境ソリューションを提供する:

| データ | 数値 |
|--------|------|
| カバー国 | 18 か国 |
| 買い手数 | 6500 万+ |
| セラー数 | 1200 万+ |
| 秒あたり訪問 | 538+ |
| 秒あたり注文 | 29 |
| GMV | $25.5B(過去 12 か月平均) |

Content rephrased for compliance with licensing restrictions. Source: [Mercado Libre Global Selling](https://global-selling.mercadolibre.com/landing/about).

### 5.2 Global Selling が対応する市場

単一アカウントで 5 つの中南米市場を管理できる([Mercado Libre](https://global-selling.mercadolibre.com/landing/how-it-works)):

| 市場 | URL | 通貨 | 特徴 |
|------|-----|------|------|
| メキシコ | mercadolibre.com.mx | MXN | 第二の市場、成長が速い |
| ブラジル | mercadolivre.com.br | BRL | 最大の市場、競争が激しい |
| チリ | mercadolibre.cl | CLP | 中規模 |
| コロンビア | mercadolibre.com.co | COP | 成長が速い |
| アルゼンチン | mercadolibre.com.ar | ARS | 為替変動が大きい |

### 5.3 Global Selling 物流方案

Mercado Envios は Mercado Libre の物流ソリューション([Mercado Libre Shipping](https://global-selling.mercadolibre.com/landing/shipping-solutions)):

```
Global Selling 物流フロー:

セラーが在庫準備
↓
指定運送業者に発送(DHL/UPS)
↓ 3 営業日以内に運送業者に引き渡し
運送業者が目的国へ輸送
↓ 標準輸送時間
ラストマイル配送で買い手へ
↓
買い手が受領

主要要件:
3 営業日以内に包裹を指定運送業者に引き渡す
Mercado Libre が提供する物流ラベルを使う
USD で受金、買い手は現地通貨で支払う
返品はプラットフォーム政策に従って処理
```

Content rephrased for compliance with licensing restrictions. Source: [Mercado Libre Learning Center](https://global-selling.mercadolibre.com/learning-center/news/how-to-ship-your-products-to-latin-america).

### 5.4 中南米市場選品 AI 戦略

```
あなたは中南米 EC 選品の専門家です。

私のサプライチェーン能力: [中国工場/米国倉庫]
予算: $[X]
ターゲット市場: [ブラジル/メキシコ/全中南米]

中南米市場の選品機会を分析してください:

1. 高需要低競争品目分析
- ブラジル人気品目(電子、ファッション、ホーム)
- メキシコ人気品目(電子、自動車部品、ホーム)
- 中国サプライチェーン優位の品目

2. 価格戦略
- 関税と物流コストを考慮した価格設定
- 分割払いの価格設定への影響
- 現地セラーとの価格競争力

3. 季節性分析
- 中南米の主要ショッピング祝日
- 南半球の季節差(ブラジル/アルゼンチン/チリ)
- 大型セールカレンダー(Hot Sale/Buen Fin/Black Friday)

4. コンプライアンス要件
- 各国の輸入制限品目
- 認証要件(INMETRO-ブラジル/NOM-メキシコ)
- 税務の考慮

5. 競争分析
- 中南米での中国セラーの競争構図
- Amazon MX/BR との差別化
- 現地ブランドの競争優位

<データ規律>
- 市場データ・検索量・競合の実績・法令条文・料率に関する具体的な数字や事実は、私が提供した情報にあるものだけを使う。**渡していない部分を記憶で埋めないこと** — この種の事実は変化が速く、記憶にある版は古い可能性がある
- 判断にある事実が必要なときは、どの公式ソースで確認すべきかを伝え、そこで止まって私に尋ねること
- 結論ごとに出典を付す: [私が提供した情報] または [モデル推測]
</データ規律>
```

### 5.5 Mercado Libre データ分析ツール

| ツール | 用途 | 価格 |
|--------|------|------|
| Mercado Libre Analytics | 公式データ分析 | 無料(セラーバックエンド) |
| Nubimetrics | 中南米 EC データ分析 | 有料 |
| GoTrendier | 中南米市場トレンド分析 | 有料 |
| ChatGPT/Claude | スペイン語/ポルトガル語 Listing 生成 | $20/月 |
| CrystalZoom | Mercado Libre データツール | 有料 |

## 6. よくある罠

### 6.1 スペイン語を 1 つの言語として扱う

メキシコ・アルゼンチン・チリでは語の選び方が転換率に響くほど違う。ある国では日常語でも、別の国では誰も検索しない語ということがある。そして**ブラジルはポルトガル語であってスペイン語ではない** — 新規セラーが最も犯しやすい誤りだ。AI でローカライズするときは国まで指定すること。「スペイン語」だけでは足りない。

### 6.2 分割払い(cuotas)を用意しない

中南米の買い手は欧米よりはるかに分割払いに依存している。単価がある程度以上の商品で分割に対応しないと、転換率はそのまま落ちる。販促手段ではなくインフラだ。

### 6.3 欧米の前提で配送を約束する

通関の不確実性は北米よりずっと高い。理想ケースで納期を書けば、低評価は物流に集中する。保守的に書くこと。

### 6.4 Mercado Envios が必須であることと費用構造を軽視する

任意項目として原価計算すると、最後に利益が合わなくなる。出店前に着地コストへ織り込むこと。

---

## 7. 完了チェック

- [ ] 中南米市場分析と国選択を完了
- [ ] Mercado Libre に出店(ブラジルおよび/またはメキシコ)
- [ ] スペイン語/ポルトガル語 Listing ローカライズを完了
- [ ] Mercado Ads を起動
- [ ] Mercado Envios Full を設定
