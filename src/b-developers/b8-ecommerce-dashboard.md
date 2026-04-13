# B8. 电商数据可视化与实时 Dashboard

> **路径**: Path B: 技术人 · **模块**: B8
> **最后更新**: 2026-03-15
> **难度**: 中级
> **预计时间**: 每天 1 小时，1-2 周
> **前置模块**: [B1 数据采集与处理](b1-data-pipeline.md)


---

## 章节导航

1. [为什么需要自建 Dashboard](#1-为什么需要自建-dashboard) · 2. [技术栈选择](#2-技术栈选择) · 3. [Streamlit 快速上手](#3-streamlit-快速上手) · 4. [电商核心 Dashboard 模块](#4-电商核心-dashboard-模块) · 5. [多平台数据整合](#5-多平台数据整合) · 6. [AI 增强 Dashboard](#6-ai-增强-dashboard) · 7. [部署与分享](#7-部署与分享) · 8. [完成标志](#8-完成标志)

---

## 本模块你将构建

- 一个 Streamlit 电商运营 Dashboard（销售/广告/库存/利润）
- 多平台数据整合视图（Amazon + Shopify + 广告平台）
- AI 增强的异常检测和自动洞察
- 可部署到云端的实时监控系统

> **核心理念**：Amazon Seller Central 和 Shopify 后台的数据分散在不同报告中，无法一眼看到全局。自建 Dashboard 把所有数据汇聚到一个视图，加上 AI 异常检测，让你从"被动看数据"变成"主动发现问题"。

---

## 1. 为什么需要自建 Dashboard

### 1.1 平台后台的局限

| 局限 | 说明 | 自建 Dashboard 解决 |
|------|------|-------------------|
| 数据分散 | 销售、广告、库存在不同页面 | 一个页面看全局 |
| 无法跨平台 | Amazon 和 Shopify 数据无法合并 | 统一数据视图 |
| 无 AI 洞察 | 只有原始数据，没有智能分析 | AI 异常检测+建议 |
| 无法自定义 | 固定的报告格式 | 完全自定义指标和视图 |
| 无法分享 | 需要登录后台才能看 | 生成链接分享给团队 |

---

## 2. 技术栈选择

### 2.1 方案对比

| 方案 | 优点 | 缺点 | 适合 |
|------|------|------|------|
| Streamlit | Python 原生、开发最快、免费 | 性能有限、样式受限 | 内部工具、快速原型 |
| Gradio | ML 模型展示好、简单 | 功能较少 | AI 模型 Demo |
| Dash (Plotly) | 图表丰富、企业级 | 学习曲线陡 | 复杂交互 Dashboard |
| 单文件 HTML | 零依赖、可直接打开 | 无后端、无实时 | 静态报告 |
| Retool/Metabase | 拖拽式、无需编码 | 付费、灵活性低 | 非技术团队 |

### 2.2 推荐：Streamlit + Plotly

```bash
pip3 install streamlit plotly pandas openpyxl
```

---

## 3. Streamlit 快速上手

### 3.1 最小可行 Dashboard（10 分钟）

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

运行：`streamlit run dashboard.py`

---

## 4. 电商核心 Dashboard 模块

### 4.1 模块架构

```
电商 Dashboard 模块：

Overview（总览）
KPI 卡片（收入/订单/利润/ROAS）
日/周/月趋势图
同比/环比变化

Sales（销售分析）
SKU 级别销售排名
品类/市场分布
新品 vs 老品表现
退货率分析

Advertising（广告分析）
Campaign 表现排名
ACOS/ROAS/TACOS 趋势
关键词表现 Top/Bottom
搜索词发现
预算消耗进度

Inventory（库存管理）
库存健康度（红黄绿灯）
可售天数预警
补货建议
长期仓储费预警

Profitability（利润分析）
SKU 级别真实利润
成本结构分解
利润趋势
盈亏平衡分析

AI Insights（AI 洞察）
异常检测（销量骤降/ACOS 飙升）
趋势预测（未来 7 天预测）
自动优化建议
竞品变化提醒
```

### 4.2 广告分析模块代码

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

## 5. 多平台数据整合

> **真实案例：AWS 电商流量异常检测架构**
> AWS 官方博客展示了如何自动化电商流量模式的异常检测。早期发现网站页面访问和订单完成等指标的微小异常，帮助组织采取纠正措施，减少对业务 KPI 的负面影响（[AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/automating-anomaly-detection-in-ecommerce-traffic-patterns/)）。

Content rephrased for compliance with licensing restrictions.

> **真实案例：Streamlit BI Dashboard 整合 GA4 + 电商数据**
> Squadbase 展示了一个综合性的 Streamlit BI Dashboard，整合了 Google Analytics 4（GA4）分析和电商智能两个关键业务领域，提供网站流量、用户行为和转化模式的深度分析（[Squadbase](https://www.squadbase.dev/blog/showcase-streamlit-bi-dashboard-with-google-analytics-and-e-commerce)）。

Content rephrased for compliance with licensing restrictions.

> **真实案例：Amazon SP-API Python 数据获取**
> Andrew Kushnerov 的系列教程展示了如何用 Python 从 Amazon SP-API 获取订单数据和库存/价格数据。关键洞察：订单在创建后会持续更新（状态变化、金额变化），要构建高质量分析需要追踪订单的完整生命周期（[Medium - Orders](https://andrewkushnerov.medium.com/amazon-sp-api-get-orders-with-python-7b7e913d87ea)，[Medium - Inventory](https://andrewkushnerov.medium.com/amazon-sp-api-get-inventory-and-prices-with-python-3226b980bd79)）。

Content rephrased for compliance with licensing restrictions.

### 5.1 Amazon SP-API 数据获取

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

### 5.2 统一数据模型

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

## 6. AI 增强 Dashboard

### 6.1 电商核心 KPI 体系

根据行业最佳实践（[ThoughtSpot](https://www.thoughtspot.com/data-trends/ecommerce-kpis-metrics)，[Feedcast](https://feedcast.ai/en/blog/ultimate-guide-to-e-commerce-kpi-dashboards)），电商 Dashboard 应该追踪以下 KPI：

| 类别 | KPI | 公式 | 健康范围 | 异常阈值 |
|------|-----|------|---------|---------|
| 销售 | 日收入 | 总销售额 | 因品类而异 | ±30% vs 7 日均值 |
| 销售 | 转化率 | 订单/会话 | 8-15% (Amazon) | <5% 或 >25% |
| 销售 | 客单价 | 收入/订单 | 因品类而异 | ±20% vs 均值 |
| 广告 | ACOS | 广告花费/广告销售 | 15-25% | >40% |
| 广告 | TACOS | 广告花费/总销售 | 8-15% | >20% |
| 广告 | ROAS | 广告销售/广告花费 | 3-5x | <2x |
| 库存 | 可售天数 | 库存/日均销量 | 30-60 天 | <14 天或 >90 天 |
| 库存 | 库存周转率 | COGS/平均库存 | 6-12 次/年 | <4 次 |
| 利润 | 毛利率 | (收入-COGS)/收入 | 50-70% | <40% |
| 利润 | 净利率 | 净利润/收入 | 15-30% | <10% |
| 客户 | 退货率 | 退货/订单 | 5-15% | >20% |
| 客户 | Review 评分 | 平均星级 | 4.0-4.5 | <3.8 |

Content rephrased for compliance with licensing restrictions.

### 6.2 异常检测（多种方法）

```python
def detect_anomalies(df: pd.DataFrame, metric: str, threshold: float = 2.0):
"""基于 Z-Score 的异常检测"""
mean = df[metric].rolling(window=7).mean()
std = df[metric].rolling(window=7).std()
z_score = (df[metric] - mean) / std

anomalies = df[abs(z_score) > threshold].copy()
anomalies["direction"] = z_score.apply(lambda x: " 异常高" if x > 0 else " 异常低")

return anomalies

# 在 Dashboard 中显示
anomalies = detect_anomalies(daily_data, "revenue")
if len(anomalies) > 0:
st.warning(f" 发现 {len(anomalies)} 个异常数据点")
st.dataframe(anomalies[["date", "revenue", "direction"]])
```

### 6.2 异常检测（多种方法）

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

### 6.3 利润分析模块

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

### 6.4 库存健康度模块

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

### 6.5 AI 自动洞察

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

## 7. 部署与分享

### 7.1 部署选项

| 方案 | 成本 | 适合 | 说明 |
|------|------|------|------|
| Streamlit Cloud | 免费 | 个人/小团队 | 直接从 GitHub 部署 |
| Hugging Face Spaces | 免费 | 开源项目 | 支持 Streamlit |
| AWS EC2 / Lightsail | $5-20/月 | 企业内部 | 完全控制 |
| Docker + 任意云 | 按需 | 灵活部署 | 容器化 |

### 7.2 Streamlit Cloud 一键部署

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

## 8. 完成标志

- [ ] 构建一个包含 4+ 模块的 Streamlit Dashboard
- [ ] 整合至少 2 个平台的数据（Amazon + Shopify）
- [ ] 实现异常检测功能（自动标注异常数据点）
- [ ] 集成 AI 洞察生成（LLM 自动分析数据）
- [ ] 部署到 Streamlit Cloud 或其他平台

(b7-review-nlp-system.md) | [Path 总览](README.md) | [B9 图片 >](b9-ai-image-pipeline.md)
