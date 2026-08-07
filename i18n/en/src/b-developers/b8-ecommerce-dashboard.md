# B8. E-Commerce Data Visualization & Real-Time Dashboard

> **Track**: Path B: Developers · **Module**: B8
> **Last updated**: 2026-07-31
> **Level**: Intermediate
> **Time**: 1 hour a day, 1–2 weeks
> **Prerequisite**: [B1 Data Collection & Processing](b1-data-pipeline.md)


---

## Chapter Navigation

1. [Why build your own dashboard](#1-why-build-your-own-dashboard) · 2. [Tech-stack choice](#2-tech-stack-choice) · 3. [Streamlit quick start](#3-streamlit-quick-start) · 4. [Core e-commerce dashboard modules](#4-core-e-commerce-dashboard-modules) · 5. [Multi-platform data integration](#5-multi-platform-data-integration) · 6. [AI-enhanced dashboard](#6-ai-enhanced-dashboard) · 7. [Deploy and share](#7-deploy-and-share) · 8. [Common Traps](#8-common-traps) · 9. [Completion checklist](#9-completion-checklist)

---

## What You'll Build

- A Streamlit e-commerce operations dashboard (sales/ads/inventory/profit)
- A multi-platform data-integration view (Amazon + Shopify + ad platforms)
- AI-enhanced anomaly detection and auto-insights
- A cloud-deployable real-time monitoring system

> **Core idea**: data in Amazon Seller Central and the Shopify admin is scattered across different reports, so you can't see the big picture at a glance. A custom dashboard aggregates all data into one view, plus AI anomaly detection, turning you from "passively watching data" into "proactively finding problems."

---

## 1. Why Build Your Own Dashboard

### 1.1 The limits of platform back ends

| Limit | Notes | How a custom dashboard solves it |
|-------|-------|----------------------------------|
| Scattered data | sales, ads, inventory on different pages | see the big picture on one page |
| No cross-platform | Amazon and Shopify data can't merge | a unified data view |
| No AI insight | only raw data, no intelligent analysis | AI anomaly detection + advice |
| No customization | fixed report format | fully custom metrics and views |
| No sharing | must log into the back end to view | generate a link to share with the team |

---

## 2. Tech-Stack Choice

### 2.1 Option comparison

| Option | Pros | Cons | Best for |
|--------|------|------|----------|
| Streamlit | Python-native, fastest to build, free | limited performance, limited styling | internal tools, quick prototypes |
| Gradio | good for showcasing ML models, simple | fewer features | AI-model demos |
| Dash (Plotly) | rich charts, enterprise-grade | steep learning curve | complex interactive dashboards |
| Single-file HTML | zero dependencies, open directly | no back end, no real-time | static reports |
| Retool/Metabase | drag-and-drop, no coding | paid, low flexibility | non-technical teams |

### 2.2 Recommended: Streamlit + Plotly

```bash
pip3 install streamlit plotly pandas numpy openpyxl python-amazon-sp-api
```

---

## 3. Streamlit Quick Start

### 3.1 Minimal viable dashboard (10 minutes)

```python
# dashboard.py — e-commerce operations dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="E-Commerce Operations Dashboard", layout="wide")
st.title("E-Commerce Operations Dashboard")

# Sidebar: date selection
with st.sidebar:
    st.header("Filters")
    date_range = st.date_input(
        "Date range",
        value=(datetime.now() - timedelta(days=30), datetime.now())
    )
    marketplace = st.selectbox("Marketplace", ["All", "US", "EU", "JP"])

# Data loading
@st.cache_data
def load_data():
    # Replace with your data source (CSV/API/database)
    df = pd.read_csv("sales_data.csv", parse_dates=["date"])
    return df

df = load_data()

# KPI cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total revenue", f"${df['revenue'].sum():,.0f}",
            f"{(df['revenue'].sum() / df['revenue_prev'].sum() - 1)*100:+.1f}%")
col2.metric("Total orders", f"{df['orders'].sum():,}")
col3.metric("Average order value", f"${df['revenue'].sum() / df['orders'].sum():.2f}")
col4.metric("Ad ROAS", f"{df['ad_revenue'].sum() / df['ad_spend'].sum():.1f}x")

# Sales-trend chart
st.subheader("Sales trend")
daily = df.groupby("date").agg({"revenue": "sum", "orders": "sum"}).reset_index()
fig = px.line(daily, x="date", y="revenue", title="Daily revenue trend")
st.plotly_chart(fig, use_container_width=True)

# Category distribution
col1, col2 = st.columns(2)
with col1:
    st.subheader("Category revenue distribution")
    cat_data = df.groupby("category")["revenue"].sum().reset_index()
    fig2 = px.pie(cat_data, values="revenue", names="category")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Inventory health")
    inv_data = df.groupby("sku")[["inventory_days", "daily_sales"]].mean().reset_index()
    inv_data["status"] = inv_data["inventory_days"].apply(
        lambda x: "urgent" if x < 7 else ("watch" if x < 14 else "normal")
    )
    st.dataframe(inv_data, use_container_width=True)
```

Run: `streamlit run dashboard.py`

---

## 4. Core E-Commerce Dashboard Modules

### 4.1 Module architecture

```
E-commerce dashboard modules:

Overview
KPI cards (revenue/orders/profit/ROAS)
daily/weekly/monthly trend charts
YoY/MoM change

Sales (sales analysis)
SKU-level sales ranking
category/marketplace distribution
new vs old product performance
return-rate analysis

Advertising (ad analysis)
campaign-performance ranking
ACOS/ROAS/TACOS trends
keyword performance Top/Bottom
search-term discovery
budget-consumption progress

Inventory (inventory management)
inventory health (red-yellow-green)
days-of-cover alerts
restock suggestions
long-term storage-fee alerts

Profitability (profit analysis)
SKU-level true profit
cost-structure breakdown
profit trend
break-even analysis

AI Insights
anomaly detection (sales drop/ACOS spike)
trend forecast (next 7 days)
auto-optimization advice
competitor-change alerts
```

### 4.2 Advertising-analysis module code

```python
def render_advertising_tab(df_ads: pd.DataFrame):
    """Advertising-analysis tab"""
    st.header("Advertising analysis")

    # KPI
    col1, col2, col3, col4 = st.columns(4)
    total_spend = df_ads['spend'].sum()
    total_sales = df_ads['attributed_sales'].sum()
    col1.metric("Total spend", f"${total_spend:,.0f}")
    col2.metric("Ad sales", f"${total_sales:,.0f}")
    col3.metric("ACOS", f"{total_spend/total_sales*100:.1f}%")
    col4.metric("ROAS", f"{total_sales/total_spend:.1f}x")

    # Campaign ranking
    st.subheader("Campaign-performance ranking")
    campaign_data = df_ads.groupby("campaign_name").agg({
        "spend": "sum",
        "attributed_sales": "sum",
        "clicks": "sum",
        "impressions": "sum"
    }).reset_index()
    campaign_data["acos"] = campaign_data["spend"] / campaign_data["attributed_sales"] * 100
    campaign_data["roas"] = campaign_data["attributed_sales"] / campaign_data["spend"]
    campaign_data["ctr"] = campaign_data["clicks"] / campaign_data["impressions"] * 100

    # Color-code ACOS
    st.dataframe(
        campaign_data.sort_values("spend", ascending=False),
        use_container_width=True,
        column_config={
            "acos": st.column_config.ProgressColumn(
                "ACOS %", min_value=0, max_value=100, format="%.1f%%"
            )
        }
    )

    # Keyword scatter plot (spend vs conversion)
    st.subheader("Keyword-performance scatter plot")
    fig = px.scatter(
        df_ads.groupby("keyword").agg({"spend": "sum", "attributed_sales": "sum", "clicks": "sum"}).reset_index(),
        x="spend", y="attributed_sales", size="clicks",
        hover_name="keyword",
        title="Spend vs sales (bubble size = clicks)"
    )
    fig.add_shape(type="line", x0=0, y0=0, x1=df_ads["spend"].max(),
                  y1=df_ads["spend"].max()/0.25, line=dict(dash="dash", color="red"))
    st.plotly_chart(fig, use_container_width=True)
```

---

## 5. Multi-Platform Data Integration

> **Real case: AWS e-commerce traffic anomaly-detection architecture**
> AWS's official blog shows how to automate anomaly detection of e-commerce traffic patterns. Early detection of small anomalies in metrics like website page visits and order completions helps organizations take corrective action, reducing the negative impact on business KPIs ([AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/automating-anomaly-detection-in-ecommerce-traffic-patterns/)).

Content rephrased for compliance with licensing restrictions.

> **Real case: Streamlit BI dashboard integrating GA4 + e-commerce data**
> Squadbase showed a comprehensive Streamlit BI dashboard integrating two key business domains — Google Analytics 4 (GA4) analytics and e-commerce intelligence — providing deep analysis of website traffic, user behavior, and conversion patterns ([Squadbase](https://www.squadbase.dev/blog/showcase-streamlit-bi-dashboard-with-google-analytics-and-e-commerce)).

Content rephrased for compliance with licensing restrictions.

> **Real case: Amazon SP-API Python data fetching**
> Andrew Kushnerov's tutorial series shows how to fetch order data and inventory/price data from the Amazon SP-API with Python. Key insight: orders keep updating after creation (status changes, amount changes), so building high-quality analysis requires tracking the order's full lifecycle ([Medium - Orders](https://andrewkushnerov.medium.com/amazon-sp-api-get-orders-with-python-7b7e913d87ea), [Medium - Inventory](https://andrewkushnerov.medium.com/amazon-sp-api-get-inventory-and-prices-with-python-3226b980bd79)).

Content rephrased for compliance with licensing restrictions.

### 5.1 Amazon SP-API data fetching

```python
# Amazon SP-API order-data fetching example
from sp_api.api import Orders, Reports
from sp_api.base import Marketplaces
from datetime import datetime, timedelta

def get_amazon_orders(days_back: int = 30) -> pd.DataFrame:
    """Fetch order data from the Amazon SP-API"""
    orders_api = Orders(marketplace=Marketplaces.US)

    created_after = (datetime.now() - timedelta(days=days_back)).isoformat()

    all_orders = []
    response = orders_api.get_orders(
        CreatedAfter=created_after,
        OrderStatuses=["Shipped", "Unshipped"]
    )

    all_orders.extend(response.payload.get("Orders", []))

    # Handle pagination
    while response.payload.get("NextToken"):
        response = orders_api.get_orders(
            CreatedAfter=created_after,
            NextToken=response.payload["NextToken"]
        )
        all_orders.extend(response.payload.get("Orders", []))

    # Convert to DataFrame
    df = pd.DataFrame(all_orders)
    df["OrderDate"] = pd.to_datetime(df["PurchaseDate"])
    df["Revenue"] = df["OrderTotal"].apply(
        lambda x: float(x["Amount"]) if isinstance(x, dict) else 0
    )

    return df

def get_amazon_inventory() -> pd.DataFrame:
    """Fetch FBA inventory data"""
    reports_api = Reports(marketplace=Marketplaces.US)

    # Request the FBA inventory report
    report = reports_api.create_report(
        reportType="GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA"
    )

    # Wait for the report to generate and download
    # ... (poll report status)

    return pd.read_csv(report_file, sep="\t")
```

### 5.2 Unified data model

```python
# Unified cross-platform sales-data model
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
    "cogs": "float", # product cost
    "fba_fees": "float", # platform fees
    "net_profit": "float" # net profit
}

def merge_platforms(amazon_df, shopify_df, walmart_df=None):
    """Merge multi-platform data into a unified format"""
    dfs = []

    # Amazon
    amazon_df["platform"] = "amazon_us"
    amazon_df = amazon_df.rename(columns={...}) # map column names
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

## 6. AI-Enhanced Dashboard

### 6.1 The core e-commerce KPI system

Per industry best practices ([ThoughtSpot](https://www.thoughtspot.com/data-trends/ecommerce-kpis-metrics), [Feedcast](https://web.archive.org/web/20260307053526/https://feedcast.ai/en/blog/ultimate-guide-to-e-commerce-kpi-dashboards)), an e-commerce dashboard should track these KPIs:

| Category | KPI | Formula | Healthy range | Anomaly threshold |
|----------|-----|---------|---------------|-------------------|
| Sales | Daily revenue | total sales | varies by category | ±30% vs 7-day average |
| Sales | Conversion rate | orders/sessions | 8–15% (Amazon) | <5% or >25% |
| Sales | Average order value | revenue/orders | varies by category | ±20% vs average |
| Advertising | ACOS | ad spend/ad sales | 15–25% | >40% |
| Advertising | TACOS | ad spend/total sales | 8–15% | >20% |
| Advertising | ROAS | ad sales/ad spend | 3–5x | <2x |
| Inventory | Days of cover | inventory/daily sales | 30–60 days | <14 days or >90 days |
| Inventory | Inventory turnover | COGS/average inventory | 6–12×/year | <4× |
| Profit | Gross margin | (revenue-COGS)/revenue | 50–70% | <40% |
| Profit | Net margin | net profit/revenue | 15–30% | <10% |
| Customer | Return rate | returns/orders | 5–15% | >20% |
| Customer | Review rating | average stars | 4.0–4.5 | <3.8 |

Content rephrased for compliance with licensing restrictions.

### 6.2 Anomaly detection (multiple methods)

```python
def detect_anomalies(df: pd.DataFrame, metric: str, threshold: float = 2.0):
    """Z-Score-based anomaly detection"""
    mean = df[metric].rolling(window=7).mean()
    std = df[metric].rolling(window=7).std()
    z_score = (df[metric] - mean) / std

    anomalies = df[abs(z_score) > threshold].copy()
    anomalies["direction"] = z_score.apply(lambda x: "abnormally high" if x > 0 else "abnormally low")

    return anomalies

# Display in the dashboard
anomalies = detect_anomalies(daily_data, "revenue")
if len(anomalies) > 0:
    st.warning(f"Found {len(anomalies)} anomalous data points")
    st.dataframe(anomalies[["date", "revenue", "direction"]])
```

### 6.2 Anomaly detection (multiple methods)

```python
import numpy as np

# Method 1: Z-Score anomaly detection (simple and effective)
def detect_zscore_anomalies(df: pd.DataFrame, metric: str,
                            window: int = 7, threshold: float = 2.0):
    """Rolling Z-Score-based anomaly detection"""
    mean = df[metric].rolling(window=window).mean()
    std = df[metric].rolling(window=window).std()
    z_score = (df[metric] - mean) / std

    anomalies = df[abs(z_score) > threshold].copy()
    anomalies["z_score"] = z_score[abs(z_score) > threshold]
    anomalies["direction"] = anomalies["z_score"].apply(
        lambda x: "abnormally high" if x > 0 else "abnormally low"
    )
    return anomalies

# Method 2: IQR anomaly detection (more robust for non-normal distributions)
def detect_iqr_anomalies(df: pd.DataFrame, metric: str, multiplier: float = 1.5):
    """Interquartile-range-based anomaly detection"""
    Q1 = df[metric].quantile(0.25)
    Q3 = df[metric].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - multiplier * IQR
    upper = Q3 + multiplier * IQR

    anomalies = df[(df[metric] < lower) | (df[metric] > upper)].copy()
    anomalies["direction"] = anomalies[metric].apply(
        lambda x: "abnormally high" if x > upper else "abnormally low"
    )
    return anomalies

# Method 3: YoY/MoM anomaly detection (most practical for e-commerce)
def detect_period_anomalies(df: pd.DataFrame, metric: str,
                            threshold_pct: float = 0.3):
    """Anomaly detection based on YoY/MoM change"""
    df = df.copy()
    df['wow_change'] = df[metric].pct_change(periods=7) # week over week
    df['mom_change'] = df[metric].pct_change(periods=30) # month over month

    anomalies = df[
        (abs(df['wow_change']) > threshold_pct) |
        (abs(df['mom_change']) > threshold_pct)
    ].copy()

    return anomalies

# Integrate in the dashboard
def render_anomaly_alerts(df: pd.DataFrame):
    """Display anomaly alerts in the dashboard"""
    metrics_to_check = {
        "revenue": {"threshold": 2.0, "label": "Revenue"},
        "orders": {"threshold": 2.0, "label": "Orders"},
        "acos": {"threshold": 1.5, "label": "ACOS"},
        "conversion_rate": {"threshold": 2.0, "label": "Conversion rate"}
    }

    all_anomalies = []
    for metric, config in metrics_to_check.items():
        if metric in df.columns:
            anomalies = detect_zscore_anomalies(df, metric, threshold=config["threshold"])
            for _, row in anomalies.iterrows():
                all_anomalies.append({
                    "Date": row["date"],
                    "Metric": config["label"],
                    "Direction": row["direction"],
                    "Value": row[metric],
                    "Z-Score": f"{row['z_score']:.1f}"
                })

    if all_anomalies:
        st.warning(f"Found {len(all_anomalies)} anomalous data points")
        st.dataframe(pd.DataFrame(all_anomalies), use_container_width=True)
    else:
        st.success("All metrics normal")
```

### 6.3 Profit-analysis module

```python
def render_profitability_tab(df: pd.DataFrame):
    """Profit-analysis tab"""
    st.header("Profit analysis")

    # SKU-level profit calculation
    df['gross_profit'] = df['revenue'] - df['cogs'] - df['fba_fees'] - df['ad_spend']
    df['gross_margin'] = df['gross_profit'] / df['revenue'] * 100
    df['net_profit'] = df['gross_profit'] - df['other_costs']
    df['net_margin'] = df['net_profit'] / df['revenue'] * 100

    # Profit waterfall chart
    st.subheader("Profit waterfall (unit economics)")
    avg_price = df['revenue'].sum() / df['units'].sum()
    avg_cogs = df['cogs'].sum() / df['units'].sum()
    avg_fba = df['fba_fees'].sum() / df['units'].sum()
    avg_ad = df['ad_spend'].sum() / df['units'].sum()
    avg_other = df['other_costs'].sum() / df['units'].sum()
    avg_profit = avg_price - avg_cogs - avg_fba - avg_ad - avg_other

    waterfall_data = pd.DataFrame({
        'item': ['Price', 'COGS', 'FBA fees', 'Ad cost', 'Other costs', 'Net profit'],
        'amount': [avg_price, -avg_cogs, -avg_fba, -avg_ad, -avg_other, avg_profit]
    })

    fig = px.bar(waterfall_data, x='item', y='amount',
                 color='amount', color_continuous_scale=['red', 'green'],
                 title=f"Per-unit profit breakdown (average net profit: ${avg_profit:.2f})")
    st.plotly_chart(fig, use_container_width=True)

    # SKU profit ranking
    st.subheader("SKU profit ranking")
    sku_profit = df.groupby('sku').agg({
        'revenue': 'sum',
        'gross_profit': 'sum',
        'net_profit': 'sum',
        'units': 'sum'
    }).reset_index()
    sku_profit['margin'] = sku_profit['net_profit'] / sku_profit['revenue'] * 100
    sku_profit = sku_profit.sort_values('net_profit', ascending=False)

    # Flag loss-making SKUs
    st.dataframe(
        sku_profit.style.applymap(
            lambda x: 'color: red' if isinstance(x, (int, float)) and x < 0 else '',
            subset=['net_profit', 'margin']
        ),
        use_container_width=True
    )
```

### 6.4 Inventory-health module

```python
def render_inventory_tab(df_inv: pd.DataFrame):
    """Inventory-health tab"""
    st.header("Inventory health")

    # Compute days of cover
    df_inv['days_of_supply'] = df_inv['quantity'] / df_inv['daily_sales'].replace(0, 0.1)

    # Inventory-status classification
    def classify_inventory(days):
        if days < 7:
            return "urgent restock"
        elif days < 14:
            return "about to stock out"
        elif days < 30:
            return "needs attention"
        elif days < 90:
            return "healthy"
        else:
            return "overstocked"

    df_inv['status'] = df_inv['days_of_supply'].apply(classify_inventory)

    # Status distribution
    col1, col2 = st.columns(2)
    with col1:
        status_counts = df_inv['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index,
                     title="Inventory-status distribution")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Urgent-restock list
        urgent = df_inv[df_inv['days_of_supply'] < 14].sort_values('days_of_supply')
        st.subheader(f"SKUs needing restock ({len(urgent)})")
        st.dataframe(urgent[['sku', 'product_name', 'quantity',
                             'daily_sales', 'days_of_supply', 'status']],
                     use_container_width=True)

    # Long-term storage-fee alert
    st.subheader("Long-term storage-fee alert")
    long_storage = df_inv[df_inv['days_in_warehouse'] > 180]
    if len(long_storage) > 0:
        estimated_fee = long_storage['quantity'].sum() * 6.90 # $6.90/cubic foot/month
        st.warning(f"{len(long_storage)} SKUs in the warehouse over 180 days, estimated monthly storage fee: ${estimated_fee:,.0f}")
        st.dataframe(long_storage[['sku', 'quantity', 'days_in_warehouse']])
```

### 6.5 AI auto-insights

```python
def generate_ai_insights(data_summary: dict) -> str:
    """Generate data insights with an LLM"""
    prompt = f"""
You are an e-commerce data-analysis expert. Below is a summary of the past 7 days of operations data:

{data_summary}

Generate 3-5 key insights, each with:
1. What was found (data fact)
2. Why it matters (business impact)
3. Suggested action (concrete and executable)

Answer concisely in English, each no more than 2 sentences.
"""
    # Call the LLM API
    return llm_call(prompt)
```

---

## 7. Deploy and Share

### 7.1 Deployment options

| Option | Cost | Best for | Notes |
|--------|------|----------|-------|
| Streamlit Cloud | free | personal/small team | deploy directly from GitHub |
| Hugging Face Spaces | free | open-source projects | supports Streamlit |
| AWS EC2 / Lightsail | $5–20/mo | enterprise internal | full control |
| Docker + any cloud | on demand | flexible deployment | containerized |

### 7.2 Streamlit Cloud one-click deploy

```bash
# 1. Make sure the project has requirements.txt
echo "streamlit\nplotly\npandas\nopenpyxl" > requirements.txt

# 2. Push to GitHub
git add -A && git commit -m "add dashboard" && git push

# 3. Connect the GitHub repo at share.streamlit.io
# Select dashboard.py as the entry file
# Click Deploy
```

---

## 8. Common Traps

### 8.1 Putting every metric on it

Forty charts is the same as no priority. A useful dashboard answers "do I need to do something today," not "how much data do I have."

### 8.2 No baseline

A number alone means nothing. Year-over-year, period-over-period, a target line, an industry benchmark — you need at least one reference or the viewer can't tell whether to worry.

### 8.3 Not labeling data latency

Whether the number is live or from yesterday changes the decision. Unlabeled, someone will make a same-day repricing call on T-1 data.

### 8.4 Building something only you can read

The dashboard is for the team. Field naming, metric definitions, and what the alert colors mean all belong next to the chart, not in your head.

---

## When this doesn't work

- **You are the only one looking at it.** The cost of a self-built dashboard is maintenance: data sources change, platforms add fields, things break. For one person, a notebook that runs or a Google Sheet on a refresh schedule is usually enough, and the time saved outweighs what a nicer chart buys you.
- **Metric definitions are not agreed yet.** When three people compute "margin" three ways, the dashboard becomes the arena for that argument rather than the record of a consensus. Write the definitions down and fix them first — what is in the numerator and denominator, and on which time basis — then visualise. Skip this and every reading of the numbers restarts the alignment.
- **The data is too stale for the dashboard to drive a decision.** A dashboard refreshed each morning is no use where you need to react hourly — stock on a peak-sale day, an ad budget running out. Before building, check three frequencies: how often the data changes, how often you look, and how quickly you can act. If they do not line up, the dashboard is decoration.
- **Off-the-shelf BI already covers it.** Platform-native reports, Shopify analytics, or a cheap BI SaaS handle most routine metrics. Build your own because only you can join the cross-platform data, or because no tool computes the metric you need — not because you want a dashboard of your own.

---

## 9. Completion Checklist

- [ ] Built a Streamlit dashboard with 4+ modules
- [ ] Integrated data from at least 2 platforms (Amazon + Shopify)
- [ ] Implemented anomaly detection (auto-flagging anomalous data points)
- [ ] Integrated AI-insight generation (LLM auto-analyzes the data)
- [ ] Deployed to Streamlit Cloud or another platform

[< B7 Review NLP System](b7-review-nlp-system.md) | [Path overview](../README.md) | [B9 AI Image Pipeline >](b9-ai-image-pipeline.md)
