# B1. データ収集と処理の自動化

> **トラック**: Path B: 技術 · **モジュール**: B1
> **最終更新**: 2026-07-31
> **難易度**: 中級
> **前提**: Python の基礎(変数、関数、リスト、辞書)
> **所要時間**: 1 日 1 時間、1〜2 週間

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kangise/ecommerce-ai-roadmap/blob/main/notebooks/b1-data-pipeline.ipynb) 付属 Notebook を Colab で直接実行
---


```mermaid
flowchart LR
B1[" B1 データパイプライン<br/>(現在地)"]:::current
B1 --> B2
B2["B2 予測モデル"]
B2 --> B3
B3["B3 RAG 知識ベース"]
B3 --> B4
B4["B4 Agent ワークフロー"]
B4 --> B5
B5["B5 ローカルモデル配備"]
classDef current fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
```

---

## 章ナビゲーション

1. [データエンジニアリング方法論](#1-データエンジニアリング方法論) · 2. [中核スキル](#2-中核スキル-pandas-データ処理) · 3. [SP-API データ収集](#3-sp-api-データ収集) · 4. [ブラウザ自動化(Selenium / Playwright)](#4-ブラウザ自動化selenium--playwright) · 5. [データ保存とクエリ](#5-データ保存とクエリ) · 6. [データ可視化とレポート](#6-データ可視化とレポート) · 7. [実践プロジェクト](#7-実践プロジェクト-完全なデータパイプラインの構築) · 8. [学習リソース](#8-学習リソース) · 9. [よくある罠](#9-よくある罠) · 10. [完了チェック](#10-完了チェック)


## このモジュールで構築するもの

自動化されたデータパイプライン: Amazon レポートからクレンジング済みの分析データセットまで。

修了後には:
- pandas で各種 Amazon レポート(Business Report、Advertising Report、FBA Report)を一括読み込み・クレンジングできる
- 実データのエンコーディング問題、日付形式の不一致、複数マーケットプレイスの列名差異に対処できる
- 複合指標(ASP、CR など)を正しく計算できる(基礎指標から再計算する必要があり、直接 sum できない)
- SP-API で注文、在庫、広告データを自動収集できる
- Playwright で API から取得できない Seller Central のレポートを自動ダウンロードできる
- DuckDB で中規模データに高性能なローカルクエリを実行できる
- データ収集からレポート生成までの完全なパイプラインを構築し、cron で定時実行できる

---

## 1. データエンジニアリング方法論

> **関連**: [A3 広告最適化](../a-operators/a3-advertising.md) 広告レポート分析の応用は A3 へ · [F4 自動化と Agent](../0-foundations/f4-agent-automation.md) データ処理自動化の Agent 基礎理論は F4 へ。

### 1.1 EC データパイプラインの第一原理

データパイプラインの本質は「あちこちに散らばった生データ」を「意思決定に直接使える情報」に変えること。

越境EC のシーンでは、データパイプラインにいくつかの特殊性がある:
- **データ量は少ないが変化が速い**: 中型セラーの 1 日のデータ量は数 MB でも、レポート形式・列名・エンコーディングは Amazon 後台の更新に伴って変わる
- **データ源の断片化**: 販売量は Business Report、広告は Advertising Console、在庫は FBA Report、レビューは前台ページ
- **指標計算に罠**: ASP(平均売価)は複数行を直接平均できず、GMS ÷ Units で再計算する必要がある。CR(転換率)も同様

**ETL vs ELT の選択:**

| モード | 意味 | 向くシーン |
|--------|------|------------|
| ETL | 先にクレンジング・変換し、その後保存 | データ量が大きく schema が固定の従来型データウェアハウス |
| ELT | 先に生データを保存し、その後必要に応じて変換 | データ量が少ないが形式が変わりやすい EC のシーン |

越境EC には ELT モードを推奨: まず生レポートを保存(生データを保持)し、その後スクリプトで必要に応じてクレンジング・計算。理由:
1. Amazon のレポート形式は変わりうる、生データの保持で遡及が容易
2. 分析ニーズが異なれば同じデータへのクレンジングロジックも異なる
3. データ量が小さい(通常 <100MB)、保存コストは無視できる

### 1.2 Amazon データ源の全景

| データ源 | 取得方法 | データ内容 | 更新頻度 | 向くシーン |
|----------|----------|------------|----------|------------|
| Business Reports | Seller Central ダウンロード / SP-API | 販売量、流入、転換率、Buy Box % | 毎日 | 日常運営監視、週報・月報 |
| Advertising Reports | Advertising Console / SP-API | 広告費用、クリック、ACOS、キーワードパフォーマンス | 毎日 | 広告最適化、ROI 分析 |
| Inventory Reports | Seller Central / SP-API | FBA 在庫数、販売可/不可、在庫日数 | 毎日 | 在庫警告、補充判断 |
| FBA Reports | Seller Central ダウンロード | 物流費用、返品明細、倉庫料 | 毎月 | コスト分析、返品率監視 |
| Brand Analytics | Seller Central(ブランドセラー) | 検索語順位、マーケットバスケット、リピート購入 | 毎週 | キーワード戦略、競合分析 |
| SP-API | REST API 呼び出し | 注文、商品カタログ、価格、在庫 | リアルタイム | 自動化システム、リアルタイム監視 |
| Review データ | 前台ページのスクレイピング / 第三者ツール | 評価、レビュー本文、画像 | 不定期 | 製品改善、競合分析 |

> **重要な洞察**: Business Report と Advertising Report は最もよく使う 2 つのデータ源で、日常分析ニーズの 80% をカバー。SP-API はリアルタイムデータや自動化が必要なシーンに向く。Brand Analytics のデータは価値が極めて高いがブランドセラーのみアクセス可能。

### 1.3 技術スタックの選択

| ツール | 用途 | なぜこれを選ぶか | インストール |
|--------|------|------------------|--------------|
| [pandas](https://pandas.pydata.org/) | データ処理の中核 | EC のデータ規模(<1GB)には pandas で十分、エコシステムが最も成熟 | `pip install pandas` |
| [openpyxl](https://openpyxl.readthedocs.io/) | Excel 読み書き | pandas が .xlsx を読み書きするデフォルトエンジン | `pip install openpyxl` |
| [python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api) | SP-API ラッパー | 最も活発な Python SP-API ライブラリ、star 1k+ | `pip install python-amazon-sp-api` |
| [DuckDB](https://duckdb.org/) | ローカル高性能クエリ | CSV/Parquet を直接クエリ、インポート不要、SQLite より 10-100 倍速い | `pip install duckdb` |
| [Playwright](https://playwright.dev/python/) | ブラウザ自動化 | Selenium より現代的、自動待機、より安定 | `pip install playwright` |
| [schedule](https://github.com/dbader/schedule) | 定時タスク | 純 Python、cron より読みやすい | `pip install schedule` |
| [Streamlit](https://streamlit.io/) | 高速ダッシュボード | 数十行のコードでインタラクティブなデータダッシュボードを構築 | `pip install streamlit` |

**なぜ Spark/Airflow を使わないか?**

越境EC のデータ規模(通常 <1GB)には分散計算は不要。Spark と Airflow の運用コストは効果をはるかに上回る。pandas + DuckDB + cron が最良の組み合わせ:
- pandas は <100MB のデータを難なく処理
- DuckDB は 100MB-10GB のデータを pandas より 10 倍以上速く処理
- cron(または schedule ライブラリ)で定時タスクは十分、Airflow の DAG 編成は不要

---

## 2. 中核スキル: pandas データ処理

### 2.1 Amazon レポートのよくあるデータ問題

コードを書く前に、遭遇する「罠」を理解しよう。これらの問題は実業務で繰り返し現れる:

| 問題 | 症状 | 解決策 |
|------|------|--------|
| エンコーディング問題 | 中国語文字化け、日本語文字化け | US/EU レポートは `utf-8-sig`(BOM 処理)、JP レポートは `shift_jis` か `cp932` |
| 日付形式の不一致 | US: `01/15/2025`、DE: `15.01.2025`、JP: `2025/01/15` | `pd.to_datetime()` の `dayfirst` パラメータを使う、または統一変換 |
| 数値列にカンマ | `"1,234.56"` が文字列として読まれる | `df['col'].str.replace(',', '').astype(float)` |
| 通貨記号 | `"$29.99"` か `"€24,99"` | `str.replace('[$€¥£]', '', regex=True)` |
| 複数マーケットプレイスの列名差異 | US: `Units Ordered`、DE: `Bestellte Einheiten` | 列名マッピング辞書を作る |
| 比率指標を直接 sum できない | 複数行の CR を直接平均 → 誤り | 基礎指標から再計算必須: CR = Total Units ÷ Total Sessions |
| 空行と集計行 | レポート末尾に "Total" 集計行 | 読み込み後に非データ行を除外 |

### 2.2 コード例: Amazon Business Report の読み込みとクレンジング

これが最もよく使うコード。堅牢な読み込み関数は上記のすべての問題に対処する必要がある:

```python
import pandas as pd
import numpy as np
from pathlib import Path

def load_business_report(filepath: str, market: str = "US") -> pd.DataFrame:
    """
    Amazon Business Report の CSV/Excel を読み込み、よくあるデータ問題に対処する。

    Args:
        filepath: レポートファイルのパス(.csv と .xlsx 対応)
        market: 市場ID (US, DE, FR, IT, ES, UK, JP)

    Returns:
        クレンジング済みの DataFrame
    """
    path = Path(filepath)

    # 1. 市場に応じてエンコーディングを選択
    encoding_map = {
        "US": "utf-8-sig",
        "UK": "utf-8-sig",
        "DE": "utf-8-sig",
        "FR": "utf-8-sig",
        "IT": "utf-8-sig",
        "ES": "utf-8-sig",
        "JP": "cp932", # JP サイトは Shift-JIS の変種を使う
    }
    encoding = encoding_map.get(market, "utf-8-sig")

    # 2. ファイルを読み込み
    if path.suffix == ".csv":
        df = pd.read_csv(filepath, encoding=encoding)
    elif path.suffix in (".xlsx", ".xls"):
        df = pd.read_excel(filepath, engine="openpyxl")
    else:
        raise ValueError(f"非対応のファイル形式: {path.suffix}")

    # 3. 列名を統一(多言語の列名差異に対処)
    column_mapping = {
        # ドイツ語列名のマッピング
        "Bestellte Einheiten": "Units Ordered",
        "Sitzungen": "Sessions",
        "Seitenaufrufe": "Page Views",
        # 日本語列名のマッピング
        "注文された商品の売上": "Ordered Product Sales",
        "セッション": "Sessions",
        # 汎用クリーンアップ
        "(Child) ASIN": "ASIN",
        "Child ASIN": "ASIN",
    }
    df = df.rename(columns=column_mapping)

    # 4. 数値列をクレンジング(カンマ、通貨記号を除去)
    numeric_cols = ["Units Ordered", "Ordered Product Sales",
                    "Sessions", "Page Views"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace(r"[$€¥£]", "", regex=True)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 5. 無効な行を除外(集計行、空行)
    if "ASIN" in df.columns:
        df = df[df["ASIN"].notna() & (df["ASIN"] != "")]
        df = df[~df["ASIN"].str.contains("Total|合計", na=False)]

    # 6. 市場IDを追加
    df["Market"] = market

    return df

# 使用例
# df_us = load_business_report("reports/us_business_report.csv", market="US")
# df_jp = load_business_report("reports/jp_business_report.csv", market="JP")
```

> **重要**: この関数はよくある問題の 80% に対処する。しかし実業務では Amazon がレポート形式を更新することもあり、try-except とログ記録の追加を推奨。

### 2.3 コード例: 複数レポートの結合と指標計算

越境EC 運営はよく複数市場・複数期間のレポートを結合する必要がある。ここに重要な罠がある: **比率指標は直接 sum や平均できない**。

```python
def merge_reports(report_files: dict[str, str]) -> pd.DataFrame:
    """
    複数市場の Business Report を結合する。

    Args:
        report_files: {market: filepath} 辞書
            例 {"US": "us_report.csv", "DE": "de_report.csv"}

    Returns:
        結合後の DataFrame
    """
    frames = []
    for market, filepath in report_files.items():
        df = load_business_report(filepath, market=market)
        frames.append(df)

    merged = pd.concat(frames, ignore_index=True)
    return merged

def calculate_metrics(df: pd.DataFrame, group_by: list[str]) -> pd.DataFrame:
    """
    指定した次元で核心指標を計算する。

    重要原則: 比率指標は基礎指標から再計算必須!
    - ASP = GMS / Units(ASP 列を平均してはいけない)
    - CR = Units / Sessions(CR 列を平均してはいけない)
    - Buy Box % = 加重平均(Sessions で加重)

    Args:
        df: 基礎指標を含む DataFrame
        group_by: グルーピング次元のリスト、例 ["Market", "Category"]

    Returns:
        集計後の DataFrame
    """
    # まず行レベルの GMS を計算
    if "GMS" not in df.columns:
        if "Ordered Product Sales" in df.columns:
            df["GMS"] = df["Ordered Product Sales"]
        elif "Units Ordered" in df.columns and "Unit Price" in df.columns:
            df["GMS"] = df["Units Ordered"] * df["Unit Price"]

    # 次元別に基礎指標を集計
    agg_dict = {
        "Units Ordered": "sum",
        "GMS": "sum",
        "Sessions": "sum",
        "Page Views": "sum",
    }
    # 存在する列だけ集計
    agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}

    summary = df.groupby(group_by).agg(agg_dict).reset_index()

    # 基礎指標から比率指標を再計算
    if "GMS" in summary.columns and "Units Ordered" in summary.columns:
        summary["ASP"] = np.where(
            summary["Units Ordered"] > 0,
            summary["GMS"] / summary["Units Ordered"],
            0
        )

    if "Units Ordered" in summary.columns and "Sessions" in summary.columns:
        summary["CR"] = np.where(
            summary["Sessions"] > 0,
            summary["Units Ordered"] / summary["Sessions"],
            0
        )

    return summary.round(2)

# 使用例
# reports = {"US": "us_report.csv", "DE": "de_report.csv", "JP": "jp_report.csv"}
# merged = merge_reports(reports)
#
# # 市場別に集計
# by_market = calculate_metrics(merged, group_by=["Market"])
#
# # 市場+カテゴリで集計
# by_market_cat = calculate_metrics(merged, group_by=["Market", "Category"])
```

> **なぜ ASP を直接平均できないか?** 製品 A が売価 $10 で 100 件、製品 B が売価 $100 で 1 件売れたとする。直接平均の ASP = ($10 + $100) / 2 = $55。しかし真の ASP = ($10×100 + $100×1) / 101 = $10.89。5 倍もずれる。これは EC データ分析で最もよくある誤り。

### 2.4 コード例: 週報の自動生成

上記のコードを繋げて、完全な HTML 週報を生成する:

```python
from datetime import datetime

def generate_weekly_report(
    report_files: dict[str, str],
    output_path: str = "weekly_report.html"
) -> str:
    """
    生レポートから HTML 週報を生成する。

    完全パイプライン: 読み込み → 結合 → クレンジング → 計算 → 出力
    """
    # 1. 読み込みと結合
    merged = merge_reports(report_files)

    # 2. 市場別に集計
    market_summary = calculate_metrics(merged, group_by=["Market"])

    # 3. カテゴリ別に集計(Category 列があれば)
    category_summary = None
    if "Category" in merged.columns:
        category_summary = calculate_metrics(
            merged, group_by=["Category"]
        ).sort_values("GMS", ascending=False)

    # 4. 全体指標を計算
    total_gms = merged["GMS"].sum() if "GMS" in merged.columns else 0
    total_units = merged["Units Ordered"].sum()
    overall_asp = total_gms / total_units if total_units > 0 else 0

    # 5. HTML を生成
    report_date = datetime.now().strftime("%Y-%m-%d")
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>週報 {report_date}</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: right; }}
th {{ background: #f5f5f5; text-align: left; }}
.metric {{ font-size: 24px; font-weight: bold; color: #1a73e8; }}
.card {{ display: inline-block; padding: 16px 24px; margin: 8px; border: 1px solid #e0e0e0; border-radius: 8px; }}
</style>
</head>
<body>
<h1>業務週報 | Weekly Report</h1>
<p>生成時刻: {report_date}</p>

<div>
<div class="card">
<div>Total GMS</div>
<div class="metric">${total_gms:,.2f}</div>
</div>
<div class="card">
<div>Total Units</div>
<div class="metric">{total_units:,}</div>
</div>
<div class="card">
<div>ASP</div>
<div class="metric">${overall_asp:.2f}</div>
</div>
</div>

<h2>市場別 | By Market</h2>
{market_summary.to_html(index=False)}
"""
    if category_summary is not None:
        html += f"""
<h2>カテゴリ別 | By Category</h2>
{category_summary.to_html(index=False)}
"""
    html += """
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"週報を生成しました: {output_path}")
    return output_path

# 使用例
# generate_weekly_report(
# report_files={"US": "us_report.csv", "DE": "de_report.csv"},
# output_path="output/weekly_report_2025_01_20.html"
# )
```

> **なぜ Excel でなく HTML か?** HTML レポートはブラウザで直接開け、メールで共有でき、社内システムに埋め込める。ソフトのインストール不要。さらに HTML はより豊かなスタイルとインタラクティブ性(Chart.js グラフなど)をサポート。

---

## 3. SP-API データ収集

### 3.1 SP-API 入門

Amazon Selling Partner API (SP-API) はリアルタイムデータを取得する公式チャネル。手動のレポートダウンロードと比べて、SP-API の利点:
- **自動化**: スクリプトが定時に呼び出し、人手不要
- **リアルタイム性**: 注文データはほぼリアルタイム、在庫データは毎時更新
- **構造化**: JSON 形式で返り、そのまま使える

**準備(一度きりの設定):**

1. [Seller Central](https://sellercentral.amazon.com/) で開発者アカウントを登録
2. SP-API アプリを作成、`client_id` と `client_secret` を取得
3. `refresh_token` を取得(OAuth 認可フローで)
4. Python ライブラリをインストール: `pip install python-amazon-sp-api`

**認証情報の管理(重要!ハードコードしない):**

```python
# config.json は Git にコミットしない! .gitignore に追加
{
"refresh_token": "your_refresh_token",
"lwa_app_id": "your_client_id",
"lwa_client_secret": "your_client_secret",
"aws_access_key": "your_aws_key",
"aws_secret_key": "your_aws_secret",
"role_arn": "your_role_arn"
}
```

```python
# または環境変数を使う(推奨)
import os
from dotenv import load_dotenv

load_dotenv() # .env ファイルから読み込み

credentials = {
"refresh_token": os.getenv("SP_API_REFRESH_TOKEN"),
"lwa_app_id": os.getenv("SP_API_CLIENT_ID"),
"lwa_client_secret": os.getenv("SP_API_CLIENT_SECRET"),
}
```

> **セキュリティ注意**: SP-API 認証情報の漏洩は店舗データの盗難につながりうる。必ず環境変数か暗号化した設定ファイルを使い、認証情報を Git にコミットしない。

### 3.2 コード例: 注文データの取得

```python
from sp_api.api import Orders
from sp_api.base import Marketplaces
from datetime import datetime, timedelta
import pandas as pd

def fetch_orders(
    credentials: dict,
    marketplace: Marketplaces = Marketplaces.US,
    days_back: int = 7
) -> pd.DataFrame:
    """
    直近 N 日の注文データを取得する。

    Args:
        credentials: SP-API 認証情報の辞書
        marketplace: 対象市場
        days_back: 遡る日数

    Returns:
        注文 DataFrame
    """
    orders_api = Orders(credentials=credentials, marketplace=marketplace)

    created_after = (
        datetime.utcnow() - timedelta(days=days_back)
    ).isoformat()

    all_orders = []
    next_token = None

    while True:
        if next_token:
            response = orders_api.get_orders(
                NextToken=next_token
            )
        else:
            response = orders_api.get_orders(
                CreatedAfter=created_after,
                OrderStatuses=["Shipped", "Unshipped"],
                MaxResultsPerPage=100
            )

        orders = response.payload.get("Orders", [])
        all_orders.extend(orders)

        next_token = response.payload.get("NextToken")
        if not next_token:
            break

    # DataFrame に変換
    if not all_orders:
        return pd.DataFrame()

    df = pd.json_normalize(all_orders)

    # キーフィールドをクレンジング
    if "OrderTotal.Amount" in df.columns:
        df["OrderTotal.Amount"] = pd.to_numeric(
            df["OrderTotal.Amount"], errors="coerce"
        )

    if "PurchaseDate" in df.columns:
        df["PurchaseDate"] = pd.to_datetime(df["PurchaseDate"])

    return df

# 使用例
# from sp_api.base import Marketplaces
# orders = fetch_orders(credentials, Marketplaces.US, days_back=30)
# print(f"{len(orders)} 件の注文を取得")
```

参考ドキュメント: [SP-API Orders API](https://developer-docs.amazon.com/sp-api/docs/orders-api-v0-reference) | [python-amazon-sp-api ドキュメント](https://python-amazon-sp-api.readthedocs.io/)

### 3.3 コード例: 在庫データの取得

在庫監視は越境EC の生命線。欠品 = 順位喪失 = 金の喪失。

```python
from sp_api.api import Inventories
from sp_api.base import Marketplaces
import pandas as pd

def fetch_inventory(
    credentials: dict,
    marketplace: Marketplaces = Marketplaces.US,
    granularity: str = "Marketplace"
) -> pd.DataFrame:
    """
    FBA 在庫サマリデータを取得する。

    Args:
        credentials: SP-API 認証情報
        marketplace: 対象市場
        granularity: 粒度 ("Marketplace" か "Country")

    Returns:
        在庫 DataFrame、販売可能数・不可能数などを含む
    """
    inv_api = Inventories(
        credentials=credentials, marketplace=marketplace
    )

    all_items = []
    next_token = None

    while True:
        kwargs = {
            "granularityType": granularity,
            "granularityId": marketplace.marketplace_id,
            "marketplaceIds": [marketplace.marketplace_id],
        }
        if next_token:
            kwargs["nextToken"] = next_token

        response = inv_api.get_inventory_summary_marketplace(**kwargs)

        summaries = response.payload.get("inventorySummaries", [])
        all_items.extend(summaries)

        next_token = response.payload.get("nextToken")
        if not next_token:
            break

    if not all_items:
        return pd.DataFrame()

    df = pd.json_normalize(all_items)

    # 在庫健全性フラグを追加
    if "totalQuantity" in df.columns:
        df["stock_status"] = df["totalQuantity"].apply(
            lambda x: "欠品" if x == 0
            else "低在庫" if x < 50
            else "正常"
        )

    return df

# 使用例
# inventory = fetch_inventory(credentials, Marketplaces.US)
# low_stock = inventory[inventory["stock_status"] != "正常"]
# print(f"注目が必要な SKU: {len(low_stock)}")
```

### 3.4 コード例: 広告レポートの取得

広告データは ACOS 最適化の基礎。SP-API の広告レポートは非同期: 先にレポート生成をリクエストし、生成完了後にダウンロードする。

```python
from sp_api.api import Reports
from sp_api.base import Marketplaces
import time
import json
import gzip
import pandas as pd

def request_advertising_report(
    credentials: dict,
    marketplace: Marketplaces = Marketplaces.US,
    report_type: str = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
    days_back: int = 7
) -> pd.DataFrame:
    """
    SP-API レポートをリクエストしてダウンロードする(非同期フロー)。

    SP-API レポートフロー:
    1. レポートリクエストを作成 → reportId を取得
    2. レポート状態をポーリング → DONE を待つ
    3. レポートドキュメントを取得 → 内容をダウンロード

    Args:
        credentials: SP-API 認証情報
        marketplace: 対象市場
        report_type: レポートタイプ(SP-API ドキュメント参照)
        days_back: 遡る日数
    """
    reports_api = Reports(
        credentials=credentials, marketplace=marketplace
    )

    from datetime import datetime, timedelta
    start_date = (
        datetime.utcnow() - timedelta(days=days_back)
    ).strftime("%Y-%m-%dT00:00:00Z")
    end_date = datetime.utcnow().strftime("%Y-%m-%dT23:59:59Z")

    # Step 1: レポートリクエストを作成
    create_response = reports_api.create_report(
        reportType=report_type,
        dataStartTime=start_date,
        dataEndTime=end_date,
        marketplaceIds=[marketplace.marketplace_id]
    )
    report_id = create_response.payload["reportId"]
    print(f"レポートリクエストを作成: {report_id}")

    # Step 2: 状態をポーリング(最大 5 分待機)
    max_wait = 300 # 秒
    elapsed = 0
    poll_interval = 15

    while elapsed < max_wait:
        status_response = reports_api.get_report(report_id)
        status = status_response.payload["processingStatus"]

        if status == "DONE":
            doc_id = status_response.payload["reportDocumentId"]
            print(f"レポート生成完了: {doc_id}")
            break
        elif status in ("CANCELLED", "FATAL"):
            raise RuntimeError(f"レポート生成失敗: {status}")

        print(f"待機中... ({elapsed}s, 状態: {status})")
        time.sleep(poll_interval)
        elapsed += poll_interval
    else:
        raise TimeoutError("レポート生成タイムアウト(5分)")

    # Step 3: レポートドキュメントをダウンロード
    doc_response = reports_api.get_report_document(
        doc_id, download=True
    )

    # 内容を解析(通常 TSV 形式)
    content = doc_response.payload.get("document", "")
    if isinstance(content, bytes):
        content = content.decode("utf-8")

    from io import StringIO
    df = pd.read_csv(StringIO(content), sep="\t")

    print(f"{len(df)} 行のデータを取得")
    return df

# 使用例
# ad_report = request_advertising_report(
# credentials, Marketplaces.US,
# report_type="GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
# days_back=30
# )
```

> **よく使うレポートタイプ**:
> - `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` 注文レポート
> - `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA` FBA 在庫レポート
> - `GET_MERCHANT_LISTINGS_ALL_DATA` 商品リストレポート
>
> 完全なリストは [SP-API Report Type Values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 参照

### 3.5 コード例: 定時データ収集スクリプト

上記の収集ロジックを繋げ、`schedule` ライブラリで定時タスクを作る:

```python
import schedule
import time
import logging
from datetime import datetime
from pathlib import Path

# ログを設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def daily_data_collection():
    """毎日のデータ収集タスク"""
    today = datetime.now().strftime("%Y%m%d")
    output_dir = Path(f"data/raw/{today}")
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"毎日のデータ収集を開始: {today}")

    try:
        # 1. 注文データを取得
        orders = fetch_orders(credentials, days_back=1)
        orders.to_csv(output_dir / "orders.csv", index=False)
        logger.info(f"注文データ: {len(orders)} 行")

        # 2. 在庫データを取得
        inventory = fetch_inventory(credentials)
        inventory.to_csv(output_dir / "inventory.csv", index=False)
        logger.info(f"在庫データ: {len(inventory)} 行")

        # 3. 低在庫警告をチェック
        low_stock = inventory[
            inventory.get("stock_status", "") != "正常"
        ] if "stock_status" in inventory.columns else pd.DataFrame()

        if len(low_stock) > 0:
            logger.warning(f"{len(low_stock)} 個の SKU の在庫が異常!")
            # ここにメール/Slack 通知を追加できる

        logger.info(f"毎日の収集完了: {output_dir}")

    except Exception as e:
        logger.error(f"収集失敗: {e}", exc_info=True)

def weekly_report_generation():
    """毎週のレポート生成タスク"""
    logger.info("週報の生成を開始...")
    try:
        # 今週の毎日データを結合
        # ... generate_weekly_report() を呼ぶ
        logger.info("週報の生成完了")
    except Exception as e:
        logger.error(f"週報の生成失敗: {e}", exc_info=True)

# 定時タスクを設定
schedule.every().day.at("08:00").do(daily_data_collection)
schedule.every().monday.at("09:00").do(weekly_report_generation)

if __name__ == "__main__":
    logger.info("データパイプライン起動")
    logger.info(f"定時タスク: 毎日 08:00 収集, 毎週月曜 09:00 週報生成")

    # 起動時にまず一度実行
    daily_data_collection()

    while True:
        schedule.run_pending()
        time.sleep(60)
```

> **本番環境の推奨**: `schedule` ライブラリは開発と小規模利用に向く。本番環境ではシステムレベルの cron(macOS/Linux)か Windows Task Scheduler を推奨、より安定で Python プロセスの継続実行に依存しない。
>
> ```bash
> # macOS/Linux cron の例(毎朝 8 時に実行)
> # crontab を編集: crontab -e
> 0 8 * * * /usr/bin/python3 /path/to/daily_collection.py >> /path/to/cron.log 2>&1
> ```

---

## 4. ブラウザ自動化(Selenium / Playwright)

### 4.1 いつブラウザ自動化が必要か

SP-API は大半のデータニーズをカバーするが、一部のデータは Seller Central のウェブページからしかダウンロードできない:

| データ | SP-API で取得可能? | ブラウザ自動化が必要? |
|--------|--------------------|------------------------|
| 注文データ | 可 | 否 |
| 在庫データ | 可 | 否 |
| Business Report | 一部 | 完全版はダウンロードが必要 |
| Brand Analytics | 不可 | ログインしてダウンロード必須 |
| QuickSight レポート | 不可 | ログインしてダウンロード必須 |
| 広告詳細レポート | 可(Advertising API) | 否 |
| A+ Content データ | 不可 | 可 |

### 4.2 Playwright vs Selenium の比較

| 次元 | Playwright | Selenium |
|------|-----------|----------|
| インストール | `pip install playwright && playwright install` | `pip install selenium webdriver-manager` |
| 自動待機 | 組み込みのスマート待機 | 手動の `WebDriverWait` が必要 |
| ブラウザ対応 | Chromium, Firefox, WebKit | Chrome, Firefox, Edge, Safari |
| 速度 | より速い(CDP で直接通信) | 遅め(WebDriver プロトコル経由) |
| デバッグ | `PWDEBUG=1` で可視化デバッグ | 追加設定が必要 |
| コミュニティ | 新しめだが急成長 | 成熟、ドキュメントとチュートリアルが多い |
| 推奨 | 新規プロジェクトの第一選択 | 既存プロジェクトは継続利用可 |

**結論**: 新規プロジェクトは Playwright、既存の Selenium コードは移行不要。

### 4.3 コード例: Playwright で Business Report を自動ダウンロード

```python
from playwright.sync_api import sync_playwright
from pathlib import Path
import time

def download_business_report(
    email: str,
    password: str,
    marketplace_url: str = "https://sellercentral.amazon.com",
    download_dir: str = "downloads",
    otp_callback=None
) -> str:
    """
    Seller Central に自動ログインし Business Report をダウンロードする。

    Args:
        email: Seller Central ログインメール
        password: ログインパスワード
        marketplace_url: Seller Central の URL
        download_dir: ダウンロードディレクトリ
        otp_callback: OTP コードのコールバック関数(二段階認証用)

    Returns:
        ダウンロードしたファイルのパス

    注意:
    - Amazon にはアンチボット機構があり、頻繁なログインは検証をトリガーしうる
    - headful モード(非 headless)の使用を推奨、検知確率を下げる
    - 二段階認証は手動入力か OTP コールバックで処理が必要
    """
    download_path = Path(download_dir).resolve()
    download_path.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        # headful モードを使用(可視のブラウザウィンドウ)
        browser = p.chromium.launch(
            headless=False, # True で無頭実行だが検知されやすい
            slow_mo=500 # 各操作の間隔 500ms、人間の操作を模倣
        )

        context = browser.new_context(
            accept_downloads=True,
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        try:
            # 1. ログインページへ遷移
            page.goto(marketplace_url)
            page.wait_for_load_state("networkidle")

            # 2. ログイン
            page.fill("#ap_email", email)
            page.click("#continue")
            page.fill("#ap_password", password)
            page.click("#signInSubmit")

            # 3. 二段階認証を処理(必要な場合)
            if page.locator("#auth-mfa-otpcode").is_visible(timeout=5000):
                if otp_callback:
                    otp = otp_callback()
                else:
                    otp = input("二段階認証コードを入力: ")
                page.fill("#auth-mfa-otpcode", otp)
                page.click("#auth-signin-button")

            page.wait_for_load_state("networkidle")

            # 4. Business Report ページへ遷移
            report_url = (
                f"{marketplace_url}/business-reports"
                "/ref=xx_sitemetric_dnav_xx"
            )
            page.goto(report_url)
            page.wait_for_load_state("networkidle")

            # 5. ダウンロードボタンをクリック
            with page.expect_download() as download_info:
                # "Detail Page Sales and Traffic" を選択
                page.click("text=Download")

            download = download_info.value
            dest = str(download_path / download.suggested_filename)
            download.save_as(dest)

            print(f"レポートをダウンロード: {dest}")
            return dest

        finally:
            browser.close()

# 使用例
# filepath = download_business_report(
# email="your_email@example.com",
# password="your_password",
# download_dir="data/raw/business_reports"
# )
```

> **重要な注意**:
> 1. ブラウザ自動化での Seller Central ログインは Amazon の利用規約に違反しうる、慎重に使用
> 2. 頻繁な自動ログインはアカウントセキュリティ検証をトリガーしうる
> 3. データ取得は SP-API を優先、ブラウザ自動化は最後の手段のみ
> 4. パスワードをハードコードせず、環境変数か秘密管理ツールを使う

---

## 5. データ保存とクエリ

### 5.1 ファイル保存 vs データベース

| 方案 | データ量 | クエリ速度 | 向くシーン | 学習コスト |
|------|----------|------------|------------|------------|
| CSV/Excel | <100MB | 遅い(全量ロード) | 小規模、一時的な分析 | ゼロ |
| Parquet | <1GB | 速い(列指向保存) | 中規模、繰り返しクエリ | 低 |
| DuckDB | 100MB-10GB | 非常に速い(OLAP エンジン) | 中規模、複雑なクエリ | 低 |
| SQLite | <1GB | 中程度 | トランザクションが必要なシーン | 低 |
| PostgreSQL | >1GB | 速い | 大規模、マルチユーザー | 中 |

**推奨パス**:
- 始めたばかり: CSV/Excel(既に使っている)
- データ量が 50MB+ に増えたら: Parquet 形式に切り替え(読み書きが明らかに速く、圧縮後のサイズも小さい)
- 複雑なクエリ(JOIN、ウィンドウ関数)が必要: DuckDB を導入
- 複数人協業や Web アプリが必要: PostgreSQL

### 5.2 DuckDB クイックスタート

DuckDB は近年最も注目される組み込み分析データベース。そのキラー機能: **CSV/Parquet ファイルを直接クエリ、インポート不要**。

```python
import duckdb

# CSV ファイルを直接クエリ pandas で先に読む必要なし!
result = duckdb.sql("""
SELECT
Market,
COUNT(*) as order_count,
SUM("Units Ordered") as total_units,
SUM("Ordered Product Sales") as total_gms,
SUM("Ordered Product Sales") / NULLIF(SUM("Units Ordered"), 0) as asp
FROM read_csv_auto('data/raw/20250120/orders.csv')
GROUP BY Market
ORDER BY total_gms DESC
""")

print(result.fetchdf()) # pandas DataFrame を返す
```

**DuckDB が優位なシーン:**

```python
# シーン 1: 複数の CSV ファイルを横断クエリ(ワイルドカード)
# 一行の SQL で data/raw/ 下の全日付フォルダの orders.csv をクエリ
result = duckdb.sql("""
SELECT
*,
filename as source_file
FROM read_csv_auto('data/raw/*/orders.csv', filename=true)
WHERE "Units Ordered" > 10
ORDER BY "Ordered Product Sales" DESC
LIMIT 100
""")

# シーン 2: ウィンドウ関数 各 ASIN の販売量順位を計算
result = duckdb.sql("""
SELECT
ASIN,
Market,
"Units Ordered",
RANK() OVER (
PARTITION BY Market
ORDER BY "Units Ordered" DESC
) as rank_in_market
FROM read_csv_auto('data/raw/20250120/orders.csv')
""")

# シーン 3: クエリ結果を直接 Parquet にエクスポート(CSV より 10 倍速い)
duckdb.sql("""
COPY (
SELECT * FROM read_csv_auto('data/raw/*/orders.csv')
) TO 'data/processed/all_orders.parquet' (FORMAT PARQUET)
""")

# シーン 4: pandas DataFrame と混合利用
import pandas as pd

df_inventory = pd.read_csv("data/raw/inventory.csv")

# DuckDB は pandas DataFrame を直接クエリできる!
result = duckdb.sql("""
SELECT
o.ASIN,
o."Units Ordered",
i.totalQuantity as current_stock,
i.totalQuantity / NULLIF(o."Units Ordered", 0) as days_of_stock
FROM read_csv_auto('data/raw/20250120/orders.csv') o
JOIN df_inventory i ON o.ASIN = i.asin
WHERE i.totalQuantity < 100
ORDER BY days_of_stock ASC
""")
print("在庫 30 日未満の ASIN:")
print(result.fetchdf())
```

> **DuckDB vs pandas 性能比較**: 100MB+ の CSV ファイルでは、DuckDB のクエリ速度は通常 pandas の 10-100 倍。理由: DuckDB は列指向保存とベクトル化実行を使い、pandas はファイル全体をメモリにロードする必要がある。
>
> 参考: [DuckDB 公式ドキュメント](https://duckdb.org/) | [DuckDB vs pandas ベンチマーク](https://duckdb.org/2021/05/14/sql-on-pandas.html)

---

## 6. データ可視化とレポート

### 6.1 matplotlib/seaborn の基本グラフ

素早いデータ探索と分析には、matplotlib と seaborn が最も直接的な選択:

```python
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd

# CJK フォントを設定(macOS)
matplotlib.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti TC", "Arial"]
matplotlib.rcParams["axes.unicode_minus"] = False

def plot_market_comparison(df: pd.DataFrame, metric: str = "GMS"):
    """
    複数市場の指標比較の棒グラフを描画する。

    Args:
        df: Market 列と指標列を含む DataFrame
        metric: 比較する指標名
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {"US": "#FF9900", "DE": "#003399", "JP": "#BC002D"}

    bars = ax.bar(
        df["Market"],
        df[metric],
        color=[colors.get(m, "#666") for m in df["Market"]]
    )

    # 棒の上に数値を表示
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2., height,
            f"${height:,.0f}" if metric == "GMS" else f"{height:,.0f}",
            ha="center", va="bottom", fontweight="bold"
        )

    ax.set_title(f"市場別 {metric} 比較", fontsize=14, fontweight="bold")
    ax.set_ylabel(metric)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"output/{metric}_by_market.png", dpi=150)
    plt.show()

# 使用例
# market_data = calculate_metrics(merged, group_by=["Market"])
# plot_market_comparison(market_data, "GMS")
# plot_market_comparison(market_data, "Units Ordered")
```

### 6.2 Streamlit 高速ダッシュボード

Streamlit は数十行のコードでインタラクティブなデータダッシュボードを構築できる。社内チーム利用に非常に向く:

```python
# dashboard.py 実行: streamlit run dashboard.py
import streamlit as st
import pandas as pd
import duckdb

st.set_page_config(page_title="EC データダッシュボード", layout="wide")
st.title("EC データダッシュボード | E-Commerce Dashboard")

# サイドバー: ファイルアップロード
uploaded_file = st.sidebar.file_uploader(
    "Business Report をアップロード", type=["csv", "xlsx"]
)

if uploaded_file:
    # データを読み込み
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl")

    st.sidebar.success(f"{len(df)} 行のデータを読み込みました")

    # 核心指標カード
    col1, col2, col3, col4 = st.columns(4)

    total_units = df["Units Ordered"].sum() if "Units Ordered" in df.columns else 0
    total_gms = df["GMS"].sum() if "GMS" in df.columns else 0
    asp = total_gms / total_units if total_units > 0 else 0

    col1.metric("Total Units", f"{total_units:,}")
    col2.metric("Total GMS", f"${total_gms:,.2f}")
    col3.metric("ASP", f"${asp:.2f}")
    col4.metric("SKU Count", f"{df['ASIN'].nunique() if 'ASIN' in df.columns else 0}")

    # 次元で絞り込み
    if "Market" in df.columns:
        selected_market = st.sidebar.multiselect(
            "市場を選択", df["Market"].unique(), default=df["Market"].unique()
        )
        df = df[df["Market"].isin(selected_market)]

    # データテーブル
    st.subheader("データ明細")
    st.dataframe(df, use_container_width=True)

    # DuckDB カスタムクエリ
    st.subheader("カスタム SQL クエリ")
    query = st.text_area(
        "SQL を入力(テーブル名は df)",
        value='SELECT Market, SUM("Units Ordered") as units FROM df GROUP BY Market'
    )
    if st.button("クエリを実行"):
        try:
            result = duckdb.sql(query).fetchdf()
            st.dataframe(result)
        except Exception as e:
            st.error(f"クエリエラー: {e}")

else:
    st.info("左側で Business Report ファイルをアップロードしてください")
```

> **Streamlit の利点**: フロントエンドコード不要、自動リフレッシュ、組み込みグラフコンポーネント、[Streamlit Cloud](https://streamlit.io/cloud)(無料)へワンクリックデプロイ。チームの社内データダッシュボードに最適。

### 6.3 HTML レポート生成(自己完結、直接共有可能)

メールや IM で共有するレポートには、自己完結の HTML が最良の形式。Chart.js を CDN からロードし、ビルドステップ不要:

```python
def generate_html_dashboard(
    df: pd.DataFrame,
    title: str = "業務レポート",
    output_path: str = "report.html"
):
    """
    Chart.js インタラクティブグラフ付きの自己完結 HTML レポートを生成する。
    ブラウザで直接開け、依存関係不要。
    """
    # グラフデータを準備
    if "Market" in df.columns and "GMS" in df.columns:
        market_data = df.groupby("Market")["GMS"].sum().reset_index()
        labels = market_data["Market"].tolist()
        values = market_data["GMS"].tolist()
    else:
        labels, values = [], []

    import json

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif;
max-width: 1200px; margin: 0 auto; padding: 24px;
background: #f8f9fa; color: #333; }}
h1 {{ margin-bottom: 24px; }}
.cards {{ display: flex; gap: 16px; margin-bottom: 24px; }}
.card {{ flex: 1; background: white; padding: 20px;
border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.card-value {{ font-size: 28px; font-weight: 700; color: #1a73e8; }}
.card-label {{ font-size: 14px; color: #666; margin-top: 4px; }}
.chart-container {{ background: white; padding: 24px;
border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
margin-bottom: 24px; }}
canvas {{ max-height: 400px; }}
</style>
</head>
<body>
<h1>{title}</h1>

<div class="cards">
<div class="card">
<div class="card-value">{df["GMS"].sum() if "GMS" in df.columns else 0:,.0f}</div>
<div class="card-label">Total GMS ($)</div>
</div>
<div class="card">
<div class="card-value">{df["Units Ordered"].sum() if "Units Ordered" in df.columns else 0:,}</div>
<div class="card-label">Total Units</div>
</div>
</div>

<div class="chart-container">
<canvas id="marketChart"></canvas>
</div>

<script>
new Chart(document.getElementById('marketChart'), {{
type: 'bar',
data: {{
labels: {json.dumps(labels)},
datasets: [{{
label: 'GMS ($)',
data: {json.dumps(values)},
backgroundColor: ['#FF9900', '#003399', '#BC002D', '#009639', '#0055A4']
}}]
}},
options: {{
responsive: true,
plugins: {{ legend: {{ display: false }} }}
}}
}});
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML レポートを生成: {output_path}")
    return output_path
```

> **なぜ自己完結 HTML か?** 1 つの .html ファイルが完全なレポートで、メール、Slack、微信で直接送れる。受信者はダブルクリックで閲覧でき、ソフトのインストール不要。Chart.js は CDN からロードされ、ファイル自体は数 KB だけ。
---
---

## 7. 実践プロジェクト: 完全なデータパイプラインの構築

### 7.1 プロジェクトアーキテクチャ

これまで学んだすべてのスキルを 1 つの完全なプロジェクトに統合する:

```
data-pipeline/
config.json # 設定ファイル(API 認証情報のパス、レポートディレクトリ)
.env # 環境変数(API キー、Git にコミットしない)
.gitignore # .env、data/raw/、*.log を無視
requirements.txt # Python 依存関係

extract/ # データ収集層
__init__.py
sp_api_client.py # SP-API データ収集(注文、在庫)
report_downloader.py # ブラウザ自動化でレポートをダウンロード
file_watcher.py # フォルダを監視、新レポートを自動処理

transform/ # データクレンジングと変換層
__init__.py
cleaners.py # 汎用クレンジング関数(エンコーディング、数値、日付)
business_report.py # Business Report 専用クレンジング
advertising.py # 広告レポート専用クレンジング
metrics.py # 指標計算(GMS、ASP、CR)

load/ # データ保存層
__init__.py
file_store.py # CSV/Parquet ファイル保存
duckdb_store.py # DuckDB クエリインターフェース

report/ # レポート生成層
__init__.py
html_report.py # HTML レポート生成
excel_report.py # Excel レポート生成
templates/ # HTML テンプレート
weekly.html

data/ # データディレクトリ(Git にコミットしない)
raw/ # 生データ(日付別に整理)
20250120/
processed/ # クレンジング後のデータ

output/ # 出力レポート
weekly/

schedule.py # 定時タスクのエントリ
run_pipeline.py # 手動実行のエントリ
README.md # プロジェクト説明
```

### 7.2 ゼロから構築する手順

**Step 1: プロジェクトを初期化**

```bash
mkdir data-pipeline && cd data-pipeline
python3 -m venv venv
source venv/bin/activate # macOS/Linux

# ディレクトリ構造を作成
mkdir -p extract transform load report/templates data/raw data/processed output

# 依存関係をインストール
pip install pandas openpyxl duckdb python-amazon-sp-api \
python-dotenv schedule playwright requests
pip freeze > requirements.txt

# Playwright ブラウザを初期化
playwright install chromium
```

**Step 2: 設定ファイル**

```python
# config.py 統一設定管理
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# プロジェクトルート
ROOT_DIR = Path(__file__).parent

# データディレクトリ
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_DIR = ROOT_DIR / "output"

# SP-API 認証情報(環境変数から読み込み)
SP_API_CREDENTIALS = {
    "refresh_token": os.getenv("SP_API_REFRESH_TOKEN", ""),
    "lwa_app_id": os.getenv("SP_API_CLIENT_ID", ""),
    "lwa_client_secret": os.getenv("SP_API_CLIENT_SECRET", ""),
    "aws_access_key": os.getenv("AWS_ACCESS_KEY", ""),
    "aws_secret_key": os.getenv("AWS_SECRET_KEY", ""),
    "role_arn": os.getenv("SP_API_ROLE_ARN", ""),
}

# 市場設定
MARKETS = {
    "US": {"encoding": "utf-8-sig", "currency": "USD"},
    "DE": {"encoding": "utf-8-sig", "currency": "EUR"},
    "JP": {"encoding": "cp932", "currency": "JPY"},
}

# ディレクトリの存在を確保
for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)
```

**Step 3: メイン pipeline スクリプト**

```python
# run_pipeline.py 完全な pipeline を手動実行
import argparse
from datetime import datetime
from pathlib import Path

from config import RAW_DATA_DIR, OUTPUT_DIR, MARKETS
from extract.sp_api_client import fetch_orders, fetch_inventory
from transform.business_report import load_business_report
from transform.metrics import calculate_metrics, merge_reports
from report.html_report import generate_html_dashboard

def run(date_str: str = None, markets: list = None):
    """
    完全なデータパイプラインを実行する。

    Args:
        date_str: データ日付 (YYYYMMDD)、デフォルトは今日
        markets: 処理する市場のリスト、デフォルトは全部
    """
    date_str = date_str or datetime.now().strftime("%Y%m%d")
    markets = markets or list(MARKETS.keys())

    print(f"Pipeline 起動: {date_str}, 市場: {markets}")

    # === Extract ===
    raw_dir = RAW_DATA_DIR / date_str
    raw_dir.mkdir(parents=True, exist_ok=True)

    # 手動ダウンロードしたレポートファイルをチェック
    report_files = {}
    for market in markets:
        pattern = f"*{market.lower()}*business*report*"
        found = list(raw_dir.glob(pattern))
        if found:
            report_files[market] = str(found[0])
            print(f"{market} レポートを発見: {found[0].name}")

    if not report_files:
        print("レポートファイルが見つからず、SP-API での取得を試行...")
        # ここで SP-API 収集ロジックを呼べる
        return

    # === Transform ===
    merged = merge_reports(report_files)
    print(f"結合完了: {len(merged)} 行")

    # 市場別に集計
    market_summary = calculate_metrics(merged, group_by=["Market"])

    # 処理後のデータを保存
    from config import PROCESSED_DATA_DIR
    processed_dir = PROCESSED_DATA_DIR / date_str
    processed_dir.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(processed_dir / "merged.parquet", index=False)

    # === Load & Report ===
    output_path = OUTPUT_DIR / f"report_{date_str}.html"
    generate_html_dashboard(
        merged,
        title=f"業務レポート {date_str}",
        output_path=str(output_path)
    )

    print(f"\nPipeline 完了!")
    print(f"処理データ: {processed_dir / 'merged.parquet'}")
    print(f"出力レポート: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="データパイプライン")
    parser.add_argument("--date", help="データ日付 YYYYMMDD")
    parser.add_argument("--markets", nargs="+", help="市場リスト")
    args = parser.parse_args()

    run(date_str=args.date, markets=args.markets)
```

```bash
# 実行例
python3 run_pipeline.py # 今日のデータを処理
python3 run_pipeline.py --date 20250120 # 指定日付を処理
python3 run_pipeline.py --markets US DE # US と DE のみ処理
```

### 7.3 よくある問題とデバッグのコツ

| 問題 | 症状 | 解決策 |
|------|------|--------|
| エンコーディングエラー | `UnicodeDecodeError` | market パラメータが正しいか確認、JP は `cp932` |
| SP-API 認証失敗 | `401 Unauthorized` | refresh_token が期限切れか確認、再認可 |
| SP-API レート制限 | `429 Too Many Requests` | `time.sleep(1)` を追加か指数バックオフを使用 |
| レポート形式変化 | `KeyError: 'Units Ordered'` | `df.columns` を print して列名を確認、マッピングを更新 |
| Playwright タイムアウト | `TimeoutError` | `timeout` パラメータを増やす、ネットワーク接続を確認 |
| DuckDB 型エラー | `Conversion Error` | `CAST` の代わりに `TRY_CAST` を使う、または先にデータをクレンジング |
| メモリ不足 | `MemoryError` | pandas の代わりに DuckDB を使う、またはバッチ処理 |
| cron が実行されない | ログに出力なし | Python パスを確認(絶対パスを使う)、権限を確認 |

**デバッグのコツ:**

```python
# 1. DataFrame の構造を素早く確認
def inspect(df: pd.DataFrame, name: str = "df"):
    """DataFrame の構造とデータ品質を素早く確認"""
    print(f"\n{'='*50}")
    print(f"{name}: {df.shape[0]} 行 × {df.shape[1]} 列")
    print(f"列名: {list(df.columns)}")
    print(f"データ型:\n{df.dtypes}")
    print(f"欠損値:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    print(f"最初の 3 行:\n{df.head(3)}")
    print(f"{'='*50}\n")

# 2. 安全な数値変換
def safe_numeric(series: pd.Series) -> pd.Series:
    """列を安全に数値へ変換、変換できないものは NaN に"""
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "")
        .str.replace(r"[$€¥£%]", "", regex=True)
        .str.strip(),
        errors="coerce"
    )

# 3. データ品質チェック
def quality_check(df: pd.DataFrame) -> dict:
    """データ品質レポートを返す"""
    return {
        "total_rows": len(df),
        "null_pct": (df.isnull().sum() / len(df) * 100).to_dict(),
        "duplicate_rows": df.duplicated().sum(),
        "negative_values": {
            col: (df[col] < 0).sum()
            for col in df.select_dtypes(include="number").columns
        }
    }
```

---

## 8. 学習リソース

### 8.1 無料講座とチュートリアル

| リソース | プラットフォーム | 長さ | 向く相手 | リンク |
|----------|------------------|------|----------|--------|
| Kaggle: Pandas Course | Kaggle | 4h | pandas ゼロ基礎 | [kaggle.com/learn/pandas](https://www.kaggle.com/learn/pandas) |
| Automate the Boring Stuff | オンライン書籍 | 自習 | Python 自動化入門 | [automatetheboringstuff.com](https://automatetheboringstuff.com/) |
| SP-API 公式ドキュメント | Amazon | 自習 | SP-API を使う開発者 | [developer-docs.amazon.com/sp-api](https://developer-docs.amazon.com/sp-api) |
| DuckDB 公式ドキュメント | DuckDB | 自習 | SQL でローカルファイルをクエリしたい | [duckdb.org](https://duckdb.org/) |
| Playwright Python ドキュメント | Microsoft | 自習 | ブラウザ自動化 | [playwright.dev/python](https://playwright.dev/python/) |
| pandas 公式ドキュメント | pandas | 自習 | 上級用法の参照 | [pandas.pydata.org](https://pandas.pydata.org/) |

### 8.2 おすすめ YouTube チャンネル

| チャンネル | 内容の方向 | おすすめ理由 |
|------------|------------|--------------|
| Corey Schafer | Python 基礎 + pandas | 解説が明快、入門に向く、pandas シリーズは定番 |
| sentdex | Python データ分析 | 実践プロジェクトが多い、データ収集から可視化まで網羅 |
| Rob Mulla | pandas + データサイエンス | pandas のテクニックに特化、短い動画で効率的に学習 |
| ArjanCodes | Python エンジニアリング実践 | コードアーキテクチャ、デザインパターン、より良い pipeline を書くのに向く |

Content rephrased for compliance with licensing restrictions. Sources cited inline.

### 8.3 おすすめ GitHub リポジトリ

| リポジトリ | Star | 用途 |
|------------|------|------|
| [python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api) | 1k+ | SP-API Python ラッパー、本モジュールの中核依存 |
| [awesome-pandas](https://github.com/tommyod/awesome-pandas) | 500+ | pandas 学習リソースまとめ |
| [DuckDB](https://github.com/duckdb/duckdb) | 20k+ | 組み込み分析データベースのソース |
| [Playwright Python](https://github.com/microsoft/playwright-python) | 10k+ | ブラウザ自動化フレームワーク |

## 9. よくある罠

### 9.1 レポート形式が変わらない前提で作る

プラットフォームは列名を変え、言語を変え、エンコーディングを変える。スキーマ検証がなければ、ある日から静かに誤ったデータが下流へ書き込まれる。**読み込みのたびに列名と行数を検証し、合わなければ止める。** 誤った結論を計算するよりましだ。

### 9.2 集計行をデータ行として扱う

Amazon のレポートは末尾に Total/合計 行を持つことが多く、除外しないと全統計が倍になる。最も多い静かな誤りだ。

### 9.3 タイムゾーンと通貨を揃えずに結合する

日付は各サイトのローカル時間、金額は各サイトの通貨のまま複数マーケットのデータを合算しても、出てくる数字に意味はない。取り込み前に基準へ正規化すること。

### 9.4 冪等でないパイプライン

再実行すると二重に書き込む。同じ入力なら何度実行しても同じ結果になるよう設計すること。でなければ障害後に再試行できなくなる。

---

## 10. 完了チェック

- [ ] Amazon Business Report を自動読み込み・クレンジングするスクリプトを書く(エンコーディング、数値、日付問題に対処)
- [ ] 複数市場のレポートを自動結合し ASP と CR を正しく計算するスクリプトを書く(基礎指標から再計算)
- [ ] SP-API で最低 1 種のデータ(注文か在庫)を取得
- [ ] DuckDB で CSV ファイルに最低 1 回 SQL クエリを実行
- [ ] 自己完結の HTML 週報を生成(Chart.js グラフ付き)
- [ ] 完全な pipeline プロジェクト構造を構築(extract → transform → load → report)

以上をすべて完了すれば、EC データパイプラインの中核スキルを習得しています。次は [B2 予測モデル](b2-prediction-models.md)へ。Prophet で販売予測を行う方法を学びます。

---

## 付録: コード早見表

### pandas 常用操作

```python
# 読み込み
df = pd.read_csv("file.csv", encoding="utf-8-sig")
df = pd.read_excel("file.xlsx", engine="openpyxl")

# クレンジング
df["col"] = df["col"].str.replace(",", "").astype(float) # カンマ除去、数値化
df["date"] = pd.to_datetime(df["date"]) # 日付に変換
df = df.dropna(subset=["ASIN"]) # 空行を削除
df = df[df["Units"] >= 0] # 負数を除外

# 集計(比率指標を正しく計算)
summary = df.groupby("Market").agg(
units=("Units Ordered", "sum"),
gms=("GMS", "sum"),
sessions=("Sessions", "sum")
).reset_index()
summary["ASP"] = summary["gms"] / summary["units"] # ASP を再計算
summary["CR"] = summary["units"] / summary["sessions"] # CR を再計算

# エクスポート
df.to_csv("output.csv", index=False)
df.to_excel("output.xlsx", index=False)
df.to_parquet("output.parquet", index=False) # 推奨!
```

### SP-API 常用エンドポイント

| エンドポイント | 用途 | python-amazon-sp-api クラス |
|----------------|------|-----------------------------|
| Orders API | 注文リストと詳細を取得 | `sp_api.api.Orders` |
| Catalog Items API | 商品情報を取得 | `sp_api.api.CatalogItems` |
| FBA Inventory API | FBA 在庫を取得 | `sp_api.api.Inventories` |
| Reports API | レポートをリクエスト・ダウンロード | `sp_api.api.Reports` |
| Product Pricing API | 商品価格を取得 | `sp_api.api.ProductPricing` |
| Notifications API | イベント通知を購読 | `sp_api.api.Notifications` |

完全な API 参照: [SP-API ドキュメント](https://developer-docs.amazon.com/sp-api) | [python-amazon-sp-api ドキュメント](https://python-amazon-sp-api.readthedocs.io/)

### DuckDB 常用クエリ

```sql
-- CSV を直接クエリ
SELECT * FROM read_csv_auto('data.csv') LIMIT 10;

-- 複数ファイルをクエリ(ワイルドカード)
SELECT * FROM read_csv_auto('data/raw/*/orders.csv');

-- 集計クエリ
SELECT Market, SUM("Units Ordered") as units, SUM(GMS) as gms
FROM read_csv_auto('data.csv')
GROUP BY Market;

-- ウィンドウ関数(順位)
SELECT *, RANK() OVER (PARTITION BY Market ORDER BY GMS DESC) as rank
FROM read_csv_auto('data.csv');

-- Parquet にエクスポート
COPY (SELECT * FROM read_csv_auto('data.csv'))
TO 'output.parquet' (FORMAT PARQUET);

-- pandas DataFrame をクエリ(Python 内で)
-- duckdb.sql("SELECT * FROM df WHERE units > 100")
```

### データクレンジング Checklist

Amazon レポートを処理する前に、以下の項目を確認:

- [ ] ファイルエンコーディングが正しい(US/EU: utf-8-sig, JP: cp932)
- [ ] 列名を統一済み(多言語の列名差異に対処)
- [ ] 数値列のカンマと通貨記号を除去済み
- [ ] 日付列を datetime 型に変換済み
- [ ] 集計行(Total/合計)と空行を除外済み
- [ ] 負数とゼロ値を処理済み(除外かフラグ)
- [ ] 比率指標を基礎指標から再計算済み(直接 sum/avg しない)
- [ ] 市場ID列(Market)を追加済み
- [ ] データ品質チェックに合格(欠損値、重複行、異常値)

[< Path B 総覧](../README.md) | [B2 予測モデル >](b2-prediction-models.md)
