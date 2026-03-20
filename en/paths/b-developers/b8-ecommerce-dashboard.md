[🇨🇳 中文](../../paths/b-developers/b8-ecommerce-dashboard.md) | 🇺🇸 English

# B8. E-commerce Data Visualization & Real-Time Dashboards

> **Path**: Path B: Developers · **Module**: B8
> **Last Updated**: 2026-03-15
> **Difficulty**: Intermediate
> **Estimated Time**: 1 hour/day, 1-2 weeks
> **Prerequisites**: [B1 Data Collection & Processing](b1-data-pipeline.md)

[Hub Home](../../README.md) · [Path B Overview](README.md)

---

## Chapter Navigation

1. [Why Build Your Own Dashboard](#1-why-build-your-own-dashboard) · 2. [Tech Stack Selection](#2-tech-stack-selection) · 3. [Streamlit Quick Start](#3-streamlit-quick-start) · 4. [Core E-commerce Dashboard Modules](#4-core-e-commerce-dashboard-modules) · 5. [Multi-Platform Data Integration](#5-multi-platform-data-integration) · 6. [AI-Enhanced Dashboard](#6-ai-enhanced-dashboard) · 7. [Deployment & Sharing](#7-deployment--sharing) · 8. [Completion Checklist](#8-completion-checklist)

---

## What You'll Build in This Module

- A Streamlit e-commerce operations dashboard (sales/ads/inventory/profitability)
- Multi-platform data integration views (Amazon + Shopify + ad platforms)
- AI-enhanced anomaly detection and automated insights
- A real-time monitoring system deployable to the cloud

> **Core Concept**: Data in Amazon Seller Central and Shopify admin is scattered across different reports you can't see the full picture at a glance. A custom dashboard aggregates all data into a single view, adds AI anomaly detection, and shifts you from "passively viewing data" to "proactively discovering issues."

---

## 1. Why Build Your Own Dashboard

### 1.1 Limitations of Platform Dashboards

| Limitation | Description | Custom Dashboard Solution |
|-----------|-------------|--------------------------|
| Scattered data | Sales, ads, inventory on different pages | See everything on one page |
| No cross-platform view | Amazon and Shopify data can't be merged | Unified data view |
| No AI insights | Only raw data, no intelligent analysis | AI anomaly detection + recommendations |
| No customization | Fixed report formats | Fully customizable metrics and views |
| Hard to share | Must log into the admin panel to view | Generate shareable links for the team |

---

## 2. Tech Stack Selection

### 2.1 Solution Comparison

| Solution | Pros | Cons | Best For |
|----------|------|------|----------|
| Streamlit | Python-native, fastest to develop, free | Limited performance, styling constraints | Internal tools, rapid prototyping |
| Gradio | Great for ML model demos, simple | Fewer features | AI model demos |
| Dash (Plotly) | Rich charts, enterprise-grade | Steep learning curve | Complex interactive dashboards |
| Single-file HTML | Zero dependencies, open directly | No backend, no real-time | Static reports |
| Retool/Metabase | Drag-and-drop, no coding needed | Paid, less flexible | Non-technical teams |

### 2.2 Recommended: Streamlit + Plotly

```bash
pip3 install streamlit plotly pandas openpyxl
```

---

## 3. Streamlit Quick Start

### 3.1 Minimum Viable Dashboard (10 Minutes)

```python
# dashboard.py 电商运营 Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="电商运营 Dashboard", layout="wide")
st.title(" 电商运营 Dashboard")

# 侧边栏：日期选择
with st.sidebar:
st.header("筛选条件")
date_range = st.date_input(
"日期范围",
value=(datetime.now() - timedelta(days=30), datetime.now())
)
marketplace = st.selectbox("市场", ["All", "US", "EU", "JP"])

# 数据加载
@st.cache_data
def load_data():
# 替换为你的数据源（CSV/API/数据库）
df = pd.read_csv("sales_data.csv", parse_dates=["date"])
return df

df = load_data()

# KPI 卡片
col1, col2, col3, col4 = st.columns(4)
col1.metric("总收入", f"${df['revenue'].sum():,.0f}",
f"{(df['revenue'].sum() / df['revenue_prev'].sum() - 1)*100:+.1f}%")
col2.metric("总订单", f"{df['orders'].sum():,}")
col3.metric("平均客单价", f"${df['revenue'].sum() / df['orders'].sum():.2f}")
col4.metric("广告 ROAS", f"{df['ad_revenue'].sum() / df['ad_spend'].sum():.1f}x")

# 销售趋势图
st.subheader(" 销售趋势")
daily = df.groupby("date").agg({"revenue": "sum", "orders": "sum"}).reset_index()
fig = px.line(daily, x="date", y="revenue", title="日收入趋势")
st.plotly_chart(fig, use_container_width=True)

# 品类分布
col1, col2 = st.columns(2)
with col1:
st.subheader(" 品类收入分布")
cat_data = df.groupby("category")["revenue"].sum().reset_index()
fig2 = px.pie(cat_data, values="revenue", names="category")
st.plotly_chart(fig2, use_container_width=True)

with col2:
st.subheader(" 库存健康度")
inv_data = df.groupby("sku")[["inventory_days", "daily_sales"]].mean().reset_index()
inv_data["status"] = inv_data["inventory_days"].apply(
lambda x: " 紧急" if x < 7 else (" 注意" if x < 14 else " 正常")
)
st.dataframe(inv_data, use_container_width=True)
```

Run with: `streamlit run dashboard.py`

---

## 4. Core E-commerce Dashboard Modules

### 4.1 Module Architecture

```
E-commerce Dashboard Modules:

Overview
KPI cards (revenue/orders/profit/ROAS)
Daily/weekly/monthly trend charts
YoY/WoW changes

Sales Analysis
SKU-level sales ranking
Category/marketplace distribution
New vs existing product performance
Return rate analysis

Advertising Analysis
Campaign performance ranking
ACOS/ROAS/TACOS trends
Top/bottom keyword performance
Search term discovery
Budget consumption progress

Inventory Management
Inventory health (red/yellow/green indicators)
Days of supply alerts
Restock recommendations
Long-term storage fee warnings

Profitability Analysis
SKU-level true profit
Cost structure breakdown
Profit trends
Break-even analysis

AI Insights
Anomaly detection (sales drops/ACOS spikes)
Trend forecasting (next 7 days)
Automated optimization recommendations
Competitor change alerts
```

### 4.2 Advertising Analysis Module Code

```python
def render_advertising_tab(df_ads: pd.DataFrame):
"""广告分析 Tab"""
st.header(" 广告分析")

# KPI
col1, col2, col3, col4 = st.columns(4)
total_spend = df_ads['spend'].sum()
total_sales = df_ads['attributed_sales'].sum()
col1.metric("总花费", f"${total_spend:,.0f}")
col2.metric("广告销售", f"${total_sales:,.0f}")
col3.metric("ACOS", f"{total_spend/total_sales*100:.1f}%")
col4.metric("ROAS", f"{total_sales/total_spend:.1f}x")

# Campaign 排名
st.subheader("Campaign 表现排名")
campaign_data = df_ads.groupby("campaign_name").agg({
"spend": "sum",
"attributed_sales": "sum",
"clicks": "sum",
"impressions": "sum"
}).reset_index()
campaign_data["acos"] = campaign_data["spend"] / campaign_data["attributed_sales"] * 100
campaign_data["roas"] = campaign_data["attributed_sales"] / campaign_data["spend"]
campaign_data["ctr"] = campaign_data["clicks"] / campaign_data["impressions"] * 100

# 颜色编码 ACOS
st.dataframe(
campaign_data.sort_values("spend", ascending=False),
use_container_width=True,
column_config={
"acos": st.column_config.ProgressColumn(
"ACOS %", min_value=0, max_value=100, format="%.1f%%"
)
}
)

# 关键词散点图（花费 vs 转化）
st.subheader("关键词表现散点图")
fig = px.scatter(
df_ads.groupby("keyword").agg({"spend": "sum", "attributed_sales": "sum", "clicks": "sum"}).reset_index(),
x="spend", y="attributed_sales", size="clicks",
hover_name="keyword",
title="花费 vs 销售（气泡大小=点击量）"
)
fig.add_shape(type="line", x0=0, y0=0, x1=df_ads["spend"].max(),
y1=df_ads["spend"].max()/0.25, line=dict(dash="dash", color="red"))
st.plotly_chart(fig, use_container_width=True)
```

---

## 5. Multi-Platform Data Integration

> **Real Case: AWS E-commerce Traffic Anomaly Detection Architecture**
> The official AWS blog demonstrated how to automate anomaly detection in e-commerce traffic patterns. Early detection of subtle anomalies in metrics like website page visits and order completions helps organizations take corrective action and reduce negative impact on business KPIs ([AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/automating-anomaly-detection-in-ecommerce-traffic-patterns/)).

Content rephrased for compliance with licensing restrictions.

> **Real Case: Streamlit BI Dashboard Integrating GA4 + E-commerce Data**
> Squadbase showcased a comprehensive Streamlit BI Dashboard integrating Google Analytics 4 (GA4) analytics and e-commerce intelligence across two key business areas, providing deep analysis of website traffic, user behavior, and conversion patterns ([Squadbase](https://www.squadbase.dev/blog/showcase-streamlit-bi-dashboard-with-google-analytics-and-e-commerce)).

Content rephrased for compliance with licensing restrictions.

> **Real Case: Amazon SP-API Python Data Retrieval**
> Andrew Kushnerov's tutorial series demonstrated how to retrieve order data and inventory/pricing data from the Amazon SP-API using Python. Key insight: orders continue to update after creation (status changes, amount changes), so building high-quality analytics requires tracking the complete order lifecycle ([Medium - Orders](https://andrewkushnerov.medium.com/amazon-sp-api-get-orders-with-python-7b7e913d87ea), [Medium - Inventory](https://andrewkushnerov.medium.com/amazon-sp-api-get-inventory-and-prices-with-python-3226b980bd79)).

Content rephrased for compliance with licensing restrictions.

### 5.1 Amazon SP-API Data Retrieval

```python
# Amazon SP-API 订单数据获取示例
from sp_api.api import Orders, Reports
from sp_api.base import Marketplaces
from datetime import datetime, timedelta

def get_amazon_orders(days_back: int = 30) -> pd.DataFrame:
"""从 Amazon SP-API 获取订单数据"""
orders_api = Orders(marketplace=Marketplaces.US)

created_after = (datetime.now() - timedelta(days=days_back)).isoformat()

all_orders = []
response = orders_api.get_orders(
CreatedAfter=created_after,
OrderStatuses=["Shipped", "Unshipped"]
)

all_orders.extend(response.payload.get("Orders", []))

# 处理分页
while response.payload.get("NextToken"):
response = orders_api.get_orders(
CreatedAfter=created_after,
NextToken=response.payload["NextToken"]
)
all_orders.extend(response.payload.get("Orders", []))

# 转换为 DataFrame
df = pd.DataFrame(all_orders)
df["OrderDate"] = pd.to_datetime(df["PurchaseDate"])
df["Revenue"] = df["OrderTotal"].apply(
lambda x: float(x["Amount"]) if isinstance(x, dict) else 0
)

return df

def get_amazon_inventory() -> pd.DataFrame:
"""获取 FBA 库存数据"""
reports_api = Reports(marketplace=Marketplaces.US)

# 请求 FBA 库存报告
report = reports_api.create_report(
reportType="GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA"
)

# 等待报告生成并下载
# ... (轮询 report status)

return pd.read_csv(report_file, sep="\t")
```

### 5.2 Unified Data Model

```python
# 统一的跨平台销售数据模型
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
"cogs": "float", # 产品成本
"fba_fees": "float", # 平台费用
"net_profit": "float" # 净利润
}

def merge_platforms(amazon_df, shopify_df, walmart_df=None):
"""合并多平台数据到统一格式"""
dfs = []

# Amazon
amazon_df["platform"] = "amazon_us"
amazon_df = amazon_df.rename(columns={...}) # 映射列名
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

### 6.1 Core E-commerce KPI Framework

Based on industry best practices ([ThoughtSpot](https://www.thoughtspot.com/data-trends/ecommerce-kpis-metrics), [Feedcast](https://feedcast.ai/en/blog/ultimate-guide-to-e-commerce-kpi-dashboards)), an e-commerce dashboard should track the following KPIs:

| Category | KPI | Formula | Healthy Range | Anomaly Threshold |
|----------|-----|---------|--------------|-------------------|
| Sales | Daily Revenue | Total sales | Varies by category | ±30% vs 7-day average |
| Sales | Conversion Rate | Orders/Sessions | 8-15% (Amazon) | <5% or >25% |
| Sales | Average Order Value | Revenue/Orders | Varies by category | ±20% vs average |
| Ads | ACOS | Ad Spend/Ad Sales | 15-25% | >40% |
| Ads | TACOS | Ad Spend/Total Sales | 8-15% | >20% |
| Ads | ROAS | Ad Sales/Ad Spend | 3-5x | <2x |
| Inventory | Days of Supply | Inventory/Daily Avg Sales | 30-60 days | <14 days or >90 days |
| Inventory | Inventory Turnover | COGS/Avg Inventory | 6-12x/year | <4x |
| Profit | Gross Margin | (Revenue-COGS)/Revenue | 50-70% | <40% |
| Profit | Net Margin | Net Profit/Revenue | 15-30% | <10% |
| Customer | Return Rate | Returns/Orders | 5-15% | >20% |
| Customer | Review Rating | Average stars | 4.0-4.5 | <3.8 |

Content rephrased for compliance with licensing restrictions.

### 6.2 Anomaly Detection (Multiple Methods)

```python
import numpy as np

# 方法 1：Z-Score 异常检测（简单有效）
def detect_zscore_anomalies(df: pd.DataFrame, metric: str,
window: int = 7, threshold: float = 2.0):
"""基于滚动 Z-Score 的异常检测"""
mean = df[metric].rolling(window=window).mean()
std = df[metric].rolling(window=window).std()
z_score = (df[metric] - mean) / std

anomalies = df[abs(z_score) > threshold].copy()
anomalies["z_score"] = z_score[abs(z_score) > threshold]
anomalies["direction"] = anomalies["z_score"].apply(
lambda x: " 异常高" if x > 0 else " 异常低"
)
return anomalies

# 方法 2：IQR 异常检测（对非正态分布更稳健）
def detect_iqr_anomalies(df: pd.DataFrame, metric: str, multiplier: float = 1.5):
"""基于四分位距的异常检测"""
Q1 = df[metric].quantile(0.25)
Q3 = df[metric].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - multiplier * IQR
upper = Q3 + multiplier * IQR

anomalies = df[(df[metric] < lower) | (df[metric] > upper)].copy()
anomalies["direction"] = anomalies[metric].apply(
lambda x: " 异常高" if x > upper else " 异常低"
)
return anomalies

# 方法 3：同比/环比异常检测（电商最实用）
def detect_period_anomalies(df: pd.DataFrame, metric: str,
threshold_pct: float = 0.3):
"""基于同比/环比变化的异常检测"""
df = df.copy()
df['wow_change'] = df[metric].pct_change(periods=7) # 周环比
df['mom_change'] = df[metric].pct_change(periods=30) # 月环比

anomalies = df[
(abs(df['wow_change']) > threshold_pct) |
(abs(df['mom_change']) > threshold_pct)
].copy()

return anomalies

# 在 Dashboard 中整合
def render_anomaly_alerts(df: pd.DataFrame):
"""在 Dashboard 中显示异常告警"""
metrics_to_check = {
"revenue": {"threshold": 2.0, "label": "收入"},
"orders": {"threshold": 2.0, "label": "订单"},
"acos": {"threshold": 1.5, "label": "ACOS"},
"conversion_rate": {"threshold": 2.0, "label": "转化率"}
}

all_anomalies = []
for metric, config in metrics_to_check.items():
if metric in df.columns:
anomalies = detect_zscore_anomalies(df, metric, threshold=config["threshold"])
for _, row in anomalies.iterrows():
all_anomalies.append({
"日期": row["date"],
"指标": config["label"],
"方向": row["direction"],
"值": row[metric],
"Z-Score": f"{row['z_score']:.1f}"
})

if all_anomalies:
st.warning(f" 发现 {len(all_anomalies)} 个异常数据点")
st.dataframe(pd.DataFrame(all_anomalies), use_container_width=True)
else:
st.success(" 所有指标正常")
```

### 6.3 Profitability Analysis Module

```python
def render_profitability_tab(df: pd.DataFrame):
"""利润分析 Tab"""
st.header(" 利润分析")

# SKU 级别利润计算
df['gross_profit'] = df['revenue'] - df['cogs'] - df['fba_fees'] - df['ad_spend']
df['gross_margin'] = df['gross_profit'] / df['revenue'] * 100
df['net_profit'] = df['gross_profit'] - df['other_costs']
df['net_margin'] = df['net_profit'] / df['revenue'] * 100

# 利润瀑布图
st.subheader("利润瀑布图（单位经济模型）")
avg_price = df['revenue'].sum() / df['units'].sum()
avg_cogs = df['cogs'].sum() / df['units'].sum()
avg_fba = df['fba_fees'].sum() / df['units'].sum()
avg_ad = df['ad_spend'].sum() / df['units'].sum()
avg_other = df['other_costs'].sum() / df['units'].sum()
avg_profit = avg_price - avg_cogs - avg_fba - avg_ad - avg_other

waterfall_data = pd.DataFrame({
'item': ['售价', 'COGS', 'FBA 费用', '广告费', '其他成本', '净利润'],
'amount': [avg_price, -avg_cogs, -avg_fba, -avg_ad, -avg_other, avg_profit]
})

fig = px.bar(waterfall_data, x='item', y='amount',
color='amount', color_continuous_scale=['red', 'green'],
title=f"单件利润分解（平均净利润: ${avg_profit:.2f}）")
st.plotly_chart(fig, use_container_width=True)

# SKU 利润排名
st.subheader("SKU 利润排名")
sku_profit = df.groupby('sku').agg({
'revenue': 'sum',
'gross_profit': 'sum',
'net_profit': 'sum',
'units': 'sum'
}).reset_index()
sku_profit['margin'] = sku_profit['net_profit'] / sku_profit['revenue'] * 100
sku_profit = sku_profit.sort_values('net_profit', ascending=False)

# 标记亏损 SKU
st.dataframe(
sku_profit.style.applymap(
lambda x: 'color: red' if isinstance(x, (int, float)) and x < 0 else '',
subset=['net_profit', 'margin']
),
use_container_width=True
)
```

### 6.4 Inventory Health Module

```python
def render_inventory_tab(df_inv: pd.DataFrame):
"""库存健康度 Tab"""
st.header(" 库存健康度")

# 计算可售天数
df_inv['days_of_supply'] = df_inv['quantity'] / df_inv['daily_sales'].replace(0, 0.1)

# 库存状态分类
def classify_inventory(days):
if days < 7:
return " 紧急补货"
elif days < 14:
return " 即将缺货"
elif days < 30:
return " 需要关注"
elif days < 90:
return " 健康"
else:
return " 库存过多"

df_inv['status'] = df_inv['days_of_supply'].apply(classify_inventory)

# 状态分布
col1, col2 = st.columns(2)
with col1:
status_counts = df_inv['status'].value_counts()
fig = px.pie(values=status_counts.values, names=status_counts.index,
title="库存状态分布")
st.plotly_chart(fig, use_container_width=True)

with col2:
# 紧急补货列表
urgent = df_inv[df_inv['days_of_supply'] < 14].sort_values('days_of_supply')
st.subheader(f" 需要补货的 SKU ({len(urgent)} 个)")
st.dataframe(urgent[['sku', 'product_name', 'quantity',
'daily_sales', 'days_of_supply', 'status']],
use_container_width=True)

# 长期仓储费预警
st.subheader(" 长期仓储费预警")
long_storage = df_inv[df_inv['days_in_warehouse'] > 180]
if len(long_storage) > 0:
estimated_fee = long_storage['quantity'].sum() * 6.90 # $6.90/cubic foot/month
st.warning(f" {len(long_storage)} 个 SKU 在仓超过 180 天，预估月仓储费: ${estimated_fee:,.0f}")
st.dataframe(long_storage[['sku', 'quantity', 'days_in_warehouse']])
```

### 6.5 AI Automated Insights

```python
def generate_ai_insights(data_summary: dict) -> str:
"""用 LLM 生成数据洞察"""
prompt = f"""
你是一个电商数据分析专家。以下是过去 7 天的运营数据摘要：

{data_summary}

请生成 3-5 条关键洞察，每条包含：
1. 发现了什么（数据事实）
2. 为什么重要（业务影响）
3. 建议的行动（具体可执行）

用简洁的中文回答，每条不超过 2 句话。
"""
# 调用 LLM API
return llm_call(prompt)
```

---

## 7. Deployment & Sharing

### 7.1 Deployment Options

| Solution | Cost | Best For | Notes |
|----------|------|----------|-------|
| Streamlit Cloud | Free | Personal/small teams | Deploy directly from GitHub |
| Hugging Face Spaces | Free | Open source projects | Supports Streamlit |
| AWS EC2 / Lightsail | $5-20/month | Internal enterprise use | Full control |
| Docker + any cloud | On-demand | Flexible deployment | Containerized |

### 7.2 One-Click Deployment to Streamlit Cloud

```bash
# 1. 确保项目有 requirements.txt
echo "streamlit\nplotly\npandas\nopenpyxl" > requirements.txt

# 2. 推送到 GitHub
git add -A && git commit -m "add dashboard" && git push

# 3. 在 share.streamlit.io 连接 GitHub 仓库
# 选择 dashboard.py 作为入口文件
# 点击 Deploy
```

---

## 8. Completion Checklist

- [ ] Built a Streamlit Dashboard with 4+ modules
- [ ] Integrated data from at least 2 platforms (Amazon + Shopify)
- [ ] Implemented anomaly detection (auto-flagging anomalous data points)
- [ ] Integrated AI insight generation (LLM auto-analyzing data)
- [ ] Deployed to Streamlit Cloud or another platform

---
> [Hub Home](../../README.md) · [Path B Overview](README.md)
>
> **Path B**: [B1 Data Pipeline](b1-data-pipeline.md) · [B2 Prediction Models](b2-prediction-models.md) · [B3 RAG Knowledge Base](b3-rag-knowledge-base.md) · [B4 AI Agent](b4-agent-workflow.md) · [B5 Local Models](b5-local-model-deploy.md) · [B6 MCP Integration](b6-mcp-agentic-workflow.md) · [B7 Review NLP](b7-review-nlp-system.md) · [B8 Dashboard](b8-ecommerce-dashboard.md) · [B9 AI Image Pipeline](b9-ai-image-pipeline.md)
>
> **Quick Links**: [Path 0 Foundations](../0-foundations/) · [Path A Operators](../a-operators/) · [Path C Managers](../c-managers/) · [Path D Multi-Platform](../d-platforms/) · [Path E Social Media](../e-social-media/)