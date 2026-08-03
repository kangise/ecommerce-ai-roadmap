# B8. EC データ可視化とリアルタイムダッシュボード

> **トラック**: Path B: 技術 · **モジュール**: B8
> **最終更新**: 2026-07-31
> **難易度**: 中級
> **所要時間**: 1 日 1 時間、1〜2 週間
> **前提モジュール**: [B1 データ収集と処理](b1-data-pipeline.md)


---

## 章ナビゲーション

1. [なぜ自作ダッシュボードが必要か](#1-なぜ自作ダッシュボードが必要か) · 2. [技術スタックの選択](#2-技術スタックの選択) · 3. [Streamlit クイックスタート](#3-streamlit-クイックスタート) · 4. [EC 核心ダッシュボードモジュール](#4-ec-核心ダッシュボードモジュール) · 5. [マルチプラットフォームデータ統合](#5-マルチプラットフォームデータ統合) · 6. [AI 強化ダッシュボード](#6-ai-強化ダッシュボード) · 7. [配備と共有](#7-配備と共有) · 8. [よくある罠](#8-よくある罠) · 9. [完了チェック](#9-完了チェック)

---

## このモジュールで構築するもの

- Streamlit EC 運営ダッシュボード(販売/広告/在庫/利益)
- マルチプラットフォームデータ統合ビュー(Amazon + Shopify + 広告プラットフォーム)
- AI 強化の異常検知と自動洞察
- クラウドに配備可能なリアルタイム監視システム

> **核心理念**: Amazon Seller Central と Shopify 後台のデータは異なるレポートに散らばり、一目で全体を見られない。自作ダッシュボードはすべてのデータを 1 つのビューに集約し、AI 異常検知を加え、「受動的にデータを見る」から「能動的に問題を発見」へ変える。

---

## 1. なぜ自作ダッシュボードが必要か

### 1.1 プラットフォーム後台の限界

| 限界 | 説明 | 自作ダッシュボードの解決 |
|------|------|--------------------------|
| データの分散 | 販売、広告、在庫が異なるページ | 1 ページで全体を見る |
| クロスプラットフォーム不可 | Amazon と Shopify のデータを結合できない | 統一データビュー |
| AI 洞察なし | 生データだけ、インテリジェント分析なし | AI 異常検知+提案 |
| カスタマイズ不可 | 固定のレポート形式 | 完全カスタムの指標とビュー |
| 共有不可 | 後台にログインしないと見られない | リンクを生成してチームに共有 |

---

## 2. 技術スタックの選択

### 2.1 方案の比較

| 方案 | 利点 | 欠点 | 向く |
|------|------|------|------|
| Streamlit | Python ネイティブ、開発が最速、無料 | 性能に限界、スタイルに制限 | 社内ツール、素早いプロトタイプ |
| Gradio | ML モデルの展示が良い、シンプル | 機能が少なめ | AI モデルの Demo |
| Dash (Plotly) | グラフが豊富、企業級 | 学習曲線が急 | 複雑なインタラクティブダッシュボード |
| 単一ファイル HTML | ゼロ依存、直接開ける | バックエンドなし、リアルタイムなし | 静的レポート |
| Retool/Metabase | ドラッグ&ドロップ、コーディング不要 | 有料、柔軟性が低い | 非技術チーム |

### 2.2 推奨: Streamlit + Plotly

```bash
pip3 install streamlit plotly pandas openpyxl
```

---

## 3. Streamlit クイックスタート

### 3.1 最小実行可能ダッシュボード(10 分)

```python
# dashboard.py EC 運営ダッシュボード
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="EC 運営ダッシュボード", layout="wide")
st.title("EC 運営ダッシュボード")

# サイドバー: 日付選択
with st.sidebar:
    st.header("フィルタ条件")
    date_range = st.date_input(
        "日付範囲",
        value=(datetime.now() - timedelta(days=30), datetime.now())
    )
    marketplace = st.selectbox("市場", ["All", "US", "EU", "JP"])

# データロード
@st.cache_data
def load_data():
    # あなたのデータ源に置換(CSV/API/データベース)
    df = pd.read_csv("sales_data.csv", parse_dates=["date"])
    return df

df = load_data()

# KPI カード
col1, col2, col3, col4 = st.columns(4)
col1.metric("総収入", f"${df['revenue'].sum():,.0f}",
            f"{(df['revenue'].sum() / df['revenue_prev'].sum() - 1)*100:+.1f}%")
col2.metric("総注文", f"{df['orders'].sum():,}")
col3.metric("平均客単価", f"${df['revenue'].sum() / df['orders'].sum():.2f}")
col4.metric("広告 ROAS", f"{df['ad_revenue'].sum() / df['ad_spend'].sum():.1f}x")

# 販売トレンドグラフ
st.subheader("販売トレンド")
daily = df.groupby("date").agg({"revenue": "sum", "orders": "sum"}).reset_index()
fig = px.line(daily, x="date", y="revenue", title="日次収入トレンド")
st.plotly_chart(fig, use_container_width=True)

# カテゴリ分布
col1, col2 = st.columns(2)
with col1:
    st.subheader("カテゴリ収入分布")
    cat_data = df.groupby("category")["revenue"].sum().reset_index()
    fig2 = px.pie(cat_data, values="revenue", names="category")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("在庫健全度")
    inv_data = df.groupby("sku")[["inventory_days", "daily_sales"]].mean().reset_index()
    inv_data["status"] = inv_data["inventory_days"].apply(
        lambda x: "緊急" if x < 7 else ("注意" if x < 14 else "正常")
    )
    st.dataframe(inv_data, use_container_width=True)
```

実行: `streamlit run dashboard.py`

---

## 4. EC 核心ダッシュボードモジュール

### 4.1 モジュールアーキテクチャ

```
EC ダッシュボードモジュール:

Overview(総覧)
KPI カード(収入/注文/利益/ROAS)
日/週/月トレンドグラフ
前年比/前月比の変化

Sales(販売分析)
SKU レベルの販売ランキング
カテゴリ/市場分布
新商品 vs 老舗商品のパフォーマンス
返品率分析

Advertising(広告分析)
Campaign パフォーマンスランキング
ACOS/ROAS/TACOS トレンド
キーワードパフォーマンス Top/Bottom
検索語発見
予算消費進捗

Inventory(在庫管理)
在庫健全度(赤黄緑信号)
販売可能日数の警告
補充提案
長期倉庫料の警告

Profitability(利益分析)
SKU レベルの真の利益
コスト構造の分解
利益トレンド
損益分岐分析

AI Insights(AI 洞察)
異常検知(販売急減/ACOS 急騰)
トレンド予測(今後 7 日の予測)
自動最適化提案
競合変化のリマインド
```

### 4.2 広告分析モジュールのコード

```python
def render_advertising_tab(df_ads: pd.DataFrame):
    """広告分析 Tab"""
    st.header("広告分析")

    # KPI
    col1, col2, col3, col4 = st.columns(4)
    total_spend = df_ads['spend'].sum()
    total_sales = df_ads['attributed_sales'].sum()
    col1.metric("総費用", f"${total_spend:,.0f}")
    col2.metric("広告売上", f"${total_sales:,.0f}")
    col3.metric("ACOS", f"{total_spend/total_sales*100:.1f}%")
    col4.metric("ROAS", f"{total_sales/total_spend:.1f}x")

    # Campaign ランキング
    st.subheader("Campaign パフォーマンスランキング")
    campaign_data = df_ads.groupby("campaign_name").agg({
        "spend": "sum",
        "attributed_sales": "sum",
        "clicks": "sum",
        "impressions": "sum"
    }).reset_index()
    campaign_data["acos"] = campaign_data["spend"] / campaign_data["attributed_sales"] * 100
    campaign_data["roas"] = campaign_data["attributed_sales"] / campaign_data["spend"]
    campaign_data["ctr"] = campaign_data["clicks"] / campaign_data["impressions"] * 100

    # ACOS をカラーコーディング
    st.dataframe(
        campaign_data.sort_values("spend", ascending=False),
        use_container_width=True,
        column_config={
            "acos": st.column_config.ProgressColumn(
                "ACOS %", min_value=0, max_value=100, format="%.1f%%"
            )
        }
    )

    # キーワード散布図(費用 vs 転換)
    st.subheader("キーワードパフォーマンス散布図")
    fig = px.scatter(
        df_ads.groupby("keyword").agg({"spend": "sum", "attributed_sales": "sum", "clicks": "sum"}).reset_index(),
        x="spend", y="attributed_sales", size="clicks",
        hover_name="keyword",
        title="費用 vs 売上(バブルサイズ=クリック数)"
    )
    fig.add_shape(type="line", x0=0, y0=0, x1=df_ads["spend"].max(),
                  y1=df_ads["spend"].max()/0.25, line=dict(dash="dash", color="red"))
    st.plotly_chart(fig, use_container_width=True)
```

---

## 5. マルチプラットフォームデータ統合

> **実事例: AWS EC トラフィック異常検知アーキテクチャ**
> AWS 公式ブログが EC トラフィックパターンの異常検知を自動化する方法を示した。ウェブサイトのページ訪問や注文完了などの指標の微小な異常を早期発見し、組織が是正措置を取るのを助け、業務 KPI への負の影響を減らす([AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/automating-anomaly-detection-in-ecommerce-traffic-patterns/))。

Content rephrased for compliance with licensing restrictions.

> **実事例: Streamlit BI ダッシュボードが GA4 + EC データを統合**
> Squadbase は Google Analytics 4(GA4)分析と EC インテリジェンスの 2 つの重要な業務領域を統合した総合的な Streamlit BI ダッシュボードを示し、ウェブサイトのトラフィック、ユーザー行動、転換パターンの深掘り分析を提供した([Squadbase](https://www.squadbase.dev/blog/showcase-streamlit-bi-dashboard-with-google-analytics-and-e-commerce))。

Content rephrased for compliance with licensing restrictions.

> **実事例: Amazon SP-API Python データ取得**
> Andrew Kushnerov のチュートリアルシリーズが、Python で Amazon SP-API から注文データと在庫/価格データを取得する方法を示した。重要な洞察: 注文は作成後も継続的に更新される(ステータス変化、金額変化)、高品質な分析を構築するには注文の完全なライフサイクルを追跡する必要がある([Medium - Orders](https://andrewkushnerov.medium.com/amazon-sp-api-get-orders-with-python-7b7e913d87ea)、[Medium - Inventory](https://andrewkushnerov.medium.com/amazon-sp-api-get-inventory-and-prices-with-python-3226b980bd79))。

Content rephrased for compliance with licensing restrictions.

### 5.1 Amazon SP-API データ取得

```python
# Amazon SP-API 注文データ取得の例
from sp_api.api import Orders, Reports
from sp_api.base import Marketplaces
from datetime import datetime, timedelta

def get_amazon_orders(days_back: int = 30) -> pd.DataFrame:
    """Amazon SP-API から注文データを取得"""
    orders_api = Orders(marketplace=Marketplaces.US)

    created_after = (datetime.now() - timedelta(days=days_back)).isoformat()

    all_orders = []
    response = orders_api.get_orders(
        CreatedAfter=created_after,
        OrderStatuses=["Shipped", "Unshipped"]
    )

    all_orders.extend(response.payload.get("Orders", []))

    # ページネーションを処理
    while response.payload.get("NextToken"):
        response = orders_api.get_orders(
            CreatedAfter=created_after,
            NextToken=response.payload["NextToken"]
        )
        all_orders.extend(response.payload.get("Orders", []))

    # DataFrame に変換
    df = pd.DataFrame(all_orders)
    df["OrderDate"] = pd.to_datetime(df["PurchaseDate"])
    df["Revenue"] = df["OrderTotal"].apply(
        lambda x: float(x["Amount"]) if isinstance(x, dict) else 0
    )

    return df

def get_amazon_inventory() -> pd.DataFrame:
    """FBA 在庫データを取得"""
    reports_api = Reports(marketplace=Marketplaces.US)

    # FBA 在庫レポートをリクエスト
    report = reports_api.create_report(
        reportType="GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA"
    )

    # レポート生成を待ってダウンロード
    # ... (report status をポーリング)

    return pd.read_csv(report_file, sep="\t")
```

### 5.2 統一データモデル

```python
# 統一されたクロスプラットフォーム販売データモデル
unified_schema = {
    "date": "datetime",
    "platform": "str", # amazon_us / shopify / walmart
    "sku": "str",
    "product_name": "str",
    "revenue": "float",
    "orders": "int",
    "units": "int",
    "refunds": "float",
    "ad_spend": "float",
    "ad_revenue": "float",
    "cogs": "float", # 製品コスト
    "fba_fees": "float", # プラットフォーム費用
    "net_profit": "float" # 純利益
}

def merge_platforms(amazon_df, shopify_df, walmart_df=None):
    """マルチプラットフォームデータを統一形式に結合"""
    dfs = []

    # Amazon
    amazon_df["platform"] = "amazon_us"
    amazon_df = amazon_df.rename(columns={...}) # 列名をマッピング
    dfs.append(amazon_df)

    # Shopify
    shopify_df["platform"] = "shopify"
    shopify_df = shopify_df.rename(columns={...})
    dfs.append(shopify_df)

    if walmart_df is not None:
        walmart_df["platform"] = "walmart"
        dfs.append(walmart_df)

    return pd.concat(dfs, ignore_index=True)
```

---

## 6. AI 強化ダッシュボード

### 6.1 EC 核心 KPI 体系

業界のベストプラクティス([ThoughtSpot](https://www.thoughtspot.com/data-trends/ecommerce-kpis-metrics)、[Feedcast](https://web.archive.org/web/20260307053526/https://feedcast.ai/en/blog/ultimate-guide-to-e-commerce-kpi-dashboards))によると、EC ダッシュボードは以下の KPI を追跡すべき:

| カテゴリ | KPI | 公式 | 健全な範囲 | 異常閾値 |
|----------|-----|------|------------|----------|
| 販売 | 日次収入 | 総売上 | カテゴリによる | ±30% vs 7 日平均 |
| 販売 | 転換率 | 注文/セッション | 8-15% (Amazon) | <5% か >25% |
| 販売 | 客単価 | 収入/注文 | カテゴリによる | ±20% vs 平均 |
| 広告 | ACOS | 広告費用/広告売上 | 15-25% | >40% |
| 広告 | TACOS | 広告費用/総売上 | 8-15% | >20% |
| 広告 | ROAS | 広告売上/広告費用 | 3-5x | <2x |
| 在庫 | 販売可能日数 | 在庫/日商 | 30-60 日 | <14 日か >90 日 |
| 在庫 | 在庫回転率 | COGS/平均在庫 | 6-12 回/年 | <4 回 |
| 利益 | 粗利率 | (収入-COGS)/収入 | 50-70% | <40% |
| 利益 | 純利率 | 純利益/収入 | 15-30% | <10% |
| 顧客 | 返品率 | 返品/注文 | 5-15% | >20% |
| 顧客 | Review 評価 | 平均星評価 | 4.0-4.5 | <3.8 |

Content rephrased for compliance with licensing restrictions.

### 6.2 異常検知(複数の方法)

```python
def detect_anomalies(df: pd.DataFrame, metric: str, threshold: float = 2.0):
    """Z-Score ベースの異常検知"""
    mean = df[metric].rolling(window=7).mean()
    std = df[metric].rolling(window=7).std()
    z_score = (df[metric] - mean) / std

    anomalies = df[abs(z_score) > threshold].copy()
    anomalies["direction"] = z_score.apply(lambda x: "異常に高い" if x > 0 else "異常に低い")

    return anomalies

# ダッシュボードで表示
anomalies = detect_anomalies(daily_data, "revenue")
if len(anomalies) > 0:
    st.warning(f"{len(anomalies)} 個の異常データ点を発見")
    st.dataframe(anomalies[["date", "revenue", "direction"]])
```

### 6.2 異常検知(複数の方法)

```python
import numpy as np

# 方法 1: Z-Score 異常検知(シンプルで有効)
def detect_zscore_anomalies(df: pd.DataFrame, metric: str,
                            window: int = 7, threshold: float = 2.0):
    """ローリング Z-Score ベースの異常検知"""
    mean = df[metric].rolling(window=window).mean()
    std = df[metric].rolling(window=window).std()
    z_score = (df[metric] - mean) / std

    anomalies = df[abs(z_score) > threshold].copy()
    anomalies["z_score"] = z_score[abs(z_score) > threshold]
    anomalies["direction"] = anomalies["z_score"].apply(
        lambda x: "異常に高い" if x > 0 else "異常に低い"
    )
    return anomalies

# 方法 2: IQR 異常検知(非正規分布により頑健)
def detect_iqr_anomalies(df: pd.DataFrame, metric: str, multiplier: float = 1.5):
    """四分位範囲ベースの異常検知"""
    Q1 = df[metric].quantile(0.25)
    Q3 = df[metric].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - multiplier * IQR
    upper = Q3 + multiplier * IQR

    anomalies = df[(df[metric] < lower) | (df[metric] > upper)].copy()
    anomalies["direction"] = anomalies[metric].apply(
        lambda x: "異常に高い" if x > upper else "異常に低い"
    )
    return anomalies

# 方法 3: 前年比/前月比 異常検知(EC で最も実用的)
def detect_period_anomalies(df: pd.DataFrame, metric: str,
                            threshold_pct: float = 0.3):
    """前年比/前月比の変化ベースの異常検知"""
    df = df.copy()
    df['wow_change'] = df[metric].pct_change(periods=7) # 前週比
    df['mom_change'] = df[metric].pct_change(periods=30) # 前月比

    anomalies = df[
        (abs(df['wow_change']) > threshold_pct) |
        (abs(df['mom_change']) > threshold_pct)
    ].copy()

    return anomalies

# ダッシュボードに統合
def render_anomaly_alerts(df: pd.DataFrame):
    """ダッシュボードで異常警告を表示"""
    metrics_to_check = {
        "revenue": {"threshold": 2.0, "label": "収入"},
        "orders": {"threshold": 2.0, "label": "注文"},
        "acos": {"threshold": 1.5, "label": "ACOS"},
        "conversion_rate": {"threshold": 2.0, "label": "転換率"}
    }

    all_anomalies = []
    for metric, config in metrics_to_check.items():
        if metric in df.columns:
            anomalies = detect_zscore_anomalies(df, metric, threshold=config["threshold"])
            for _, row in anomalies.iterrows():
                all_anomalies.append({
                    "日付": row["date"],
                    "指標": config["label"],
                    "方向": row["direction"],
                    "値": row[metric],
                    "Z-Score": f"{row['z_score']:.1f}"
                })

    if all_anomalies:
        st.warning(f"{len(all_anomalies)} 個の異常データ点を発見")
        st.dataframe(pd.DataFrame(all_anomalies), use_container_width=True)
    else:
        st.success("すべての指標が正常")
```

### 6.3 利益分析モジュール

```python
def render_profitability_tab(df: pd.DataFrame):
    """利益分析 Tab"""
    st.header("利益分析")

    # SKU レベルの利益計算
    df['gross_profit'] = df['revenue'] - df['cogs'] - df['fba_fees'] - df['ad_spend']
    df['gross_margin'] = df['gross_profit'] / df['revenue'] * 100
    df['net_profit'] = df['gross_profit'] - df['other_costs']
    df['net_margin'] = df['net_profit'] / df['revenue'] * 100

    # 利益ウォーターフォール図
    st.subheader("利益ウォーターフォール図(ユニットエコノミクス)")
    avg_price = df['revenue'].sum() / df['units'].sum()
    avg_cogs = df['cogs'].sum() / df['units'].sum()
    avg_fba = df['fba_fees'].sum() / df['units'].sum()
    avg_ad = df['ad_spend'].sum() / df['units'].sum()
    avg_other = df['other_costs'].sum() / df['units'].sum()
    avg_profit = avg_price - avg_cogs - avg_fba - avg_ad - avg_other

    waterfall_data = pd.DataFrame({
        'item': ['売価', 'COGS', 'FBA 費用', '広告費', 'その他コスト', '純利益'],
        'amount': [avg_price, -avg_cogs, -avg_fba, -avg_ad, -avg_other, avg_profit]
    })

    fig = px.bar(waterfall_data, x='item', y='amount',
                 color='amount', color_continuous_scale=['red', 'green'],
                 title=f"1 件あたり利益の分解(平均純利益: ${avg_profit:.2f})")
    st.plotly_chart(fig, use_container_width=True)

    # SKU 利益ランキング
    st.subheader("SKU 利益ランキング")
    sku_profit = df.groupby('sku').agg({
        'revenue': 'sum',
        'gross_profit': 'sum',
        'net_profit': 'sum',
        'units': 'sum'
    }).reset_index()
    sku_profit['margin'] = sku_profit['net_profit'] / sku_profit['revenue'] * 100
    sku_profit = sku_profit.sort_values('net_profit', ascending=False)

    # 赤字 SKU をマーク
    st.dataframe(
        sku_profit.style.applymap(
            lambda x: 'color: red' if isinstance(x, (int, float)) and x < 0 else '',
            subset=['net_profit', 'margin']
        ),
        use_container_width=True
    )
```

### 6.4 在庫健全度モジュール

```python
def render_inventory_tab(df_inv: pd.DataFrame):
    """在庫健全度 Tab"""
    st.header("在庫健全度")

    # 販売可能日数を計算
    df_inv['days_of_supply'] = df_inv['quantity'] / df_inv['daily_sales'].replace(0, 0.1)

    # 在庫状態の分類
    def classify_inventory(days):
        if days < 7:
            return "緊急補充"
        elif days < 14:
            return "まもなく欠品"
        elif days < 30:
            return "要注意"
        elif days < 90:
            return "健全"
        else:
            return "在庫過多"

    df_inv['status'] = df_inv['days_of_supply'].apply(classify_inventory)

    # 状態分布
    col1, col2 = st.columns(2)
    with col1:
        status_counts = df_inv['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index,
                     title="在庫状態分布")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # 緊急補充リスト
        urgent = df_inv[df_inv['days_of_supply'] < 14].sort_values('days_of_supply')
        st.subheader(f"補充が必要な SKU ({len(urgent)} 個)")
        st.dataframe(urgent[['sku', 'product_name', 'quantity',
                             'daily_sales', 'days_of_supply', 'status']],
                     use_container_width=True)

    # 長期倉庫料の警告
    st.subheader("長期倉庫料の警告")
    long_storage = df_inv[df_inv['days_in_warehouse'] > 180]
    if len(long_storage) > 0:
        estimated_fee = long_storage['quantity'].sum() * 6.90 # $6.90/立方フィート/月
        st.warning(f"{len(long_storage)} 個の SKU が倉庫内 180 日超、推定月倉庫料: ${estimated_fee:,.0f}")
        st.dataframe(long_storage[['sku', 'quantity', 'days_in_warehouse']])
```

### 6.5 AI 自動洞察

```python
def generate_ai_insights(data_summary: dict) -> str:
    """LLM でデータ洞察を生成"""
    prompt = f"""
あなたは EC データ分析の専門家です。以下は過去 7 日の運営データのサマリです:

{data_summary}

3-5 個のキーな洞察を生成、各々に含む:
1. 何を発見したか(データの事実)
2. なぜ重要か(業務への影響)
3. 推奨するアクション(具体的で実行可能)

日本語で簡潔に回答、各項目は 2 文を超えない。
"""
    # LLM API を呼ぶ
    return llm_call(prompt)
```

---

## 7. 配備と共有

### 7.1 配備オプション

| 方案 | コスト | 向く | 説明 |
|------|--------|------|------|
| Streamlit Cloud | 無料 | 個人/小チーム | GitHub から直接配備 |
| Hugging Face Spaces | 無料 | オープンソースプロジェクト | Streamlit 対応 |
| AWS EC2 / Lightsail | $5-20/月 | 企業内部 | 完全制御 |
| Docker + 任意のクラウド | オンデマンド | 柔軟な配備 | コンテナ化 |

### 7.2 Streamlit Cloud ワンクリック配備

```bash
# 1. プロジェクトに requirements.txt があることを確認
echo "streamlit\nplotly\npandas\nopenpyxl" > requirements.txt

# 2. GitHub にプッシュ
git add -A && git commit -m "add dashboard" && git push

# 3. share.streamlit.io で GitHub リポジトリを接続
# dashboard.py をエントリファイルに選択
# Deploy をクリック
```

---

## 8. よくある罠

### 8.1 全指標を載せる

グラフ 40 個は優先順位がないのと同じだ。有用なダッシュボードが答えるのは「今日何かすべきか」であって「どれだけデータがあるか」ではない。

### 8.2 基準線がない

数字が単独で置かれていても意味を持たない。前年同期比、前期比、目標線、業界ベンチマーク — 最低 1 つの参照がなければ、見た人は緊張すべきか判断できない。

### 8.3 データの遅延を明示しない

その数字がリアルタイムか前日分かは判断を左右する。明示がないと、誰かが T-1 のデータでその日の価格変更を決めてしまう。

### 8.4 自分にしか読めないものを作る

ダッシュボードはチームのものだ。項目名、指標の定義、警告色の意味は、頭の中ではなくグラフの隣に書くこと。

---

## 9. 完了チェック

- [ ] 4+ モジュールを含む Streamlit ダッシュボードを構築
- [ ] 最低 2 つのプラットフォームのデータを統合(Amazon + Shopify)
- [ ] 異常検知機能を実装(異常データ点を自動注記)
- [ ] AI 洞察生成を統合(LLM が自動でデータを分析)
- [ ] Streamlit Cloud か他のプラットフォームに配備

[< B7 Review NLP システム](b7-review-nlp-system.md) | [Path 総覧](../README.md) | [B9 AI 画像 Pipeline >](b9-ai-image-pipeline.md)
