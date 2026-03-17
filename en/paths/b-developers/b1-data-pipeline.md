[🇨🇳 中文](../../paths/b-developers/b1-data-pipeline.md) | 🇺🇸 English

# B1. Data Collection & Processing Automation

> **Path**: Path B: Developers · **Module**: B1  
> **Last Updated**: 2026-03-12  
> **Difficulty**: ⭐⭐ Intermediate  
> **Prerequisites**: Python basics (variables, functions, lists, dictionaries)  
> **Estimated Time**: 1 hour per day, 1–2 weeks

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kangise/ecommerce-ai-roadmap/blob/main/notebooks/b1-data-pipeline.ipynb) — Run the companion Notebook directly in Colab
---

🏠 [Hub Home](../../README.md) · 📋 [Path B Overview](README.md)

```mermaid
flowchart LR
    B1["✅ B1 Data Pipeline<br/>(Current)"]:::current
    B1 --> B2
    B2["B2 Prediction Models"]
    B2 --> B3
    B3["B3 RAG Knowledge Base"]
    B3 --> B4
    B4["B4 Agent Workflow"]
    B4 --> B5
    B5["B5 Local Model Deployment"]
    classDef current fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
```

---

## 📖 Module Navigation

1. [Data Engineering Methodology](#1-data-engineering-methodology) · 2. [pandas Data Processing](#2-core-skill-pandas-data-processing) · 3. [SP-API Data Collection](#3-sp-api-data-collection) · 4. [Browser Automation](#4-browser-automation-selenium--playwright) · 5. [Data Storage & Querying](#5-data-storage--querying) · 6. [Data Visualization](#6-data-visualization--reporting) · 7. [Hands-On Project](#7-hands-on-project-building-a-complete-data-pipeline) · 8. [Learning Resources](#8-learning-resources) · 9. [🦞 OpenClaw Automation](#9-automating-data-pipelines-with-openclaw) · 10. [Completion Checklist](#10-completion-checklist)


## What You'll Build in This Module

An automated data pipeline: from Amazon reports to clean, analysis-ready datasets.

After completing this module, you'll be able to:
- Use pandas to batch-read and clean various Amazon reports (Business Report, Advertising Report, FBA Report)
- Handle real-world data issues like encoding problems, inconsistent date formats, and column name differences across marketplaces
- Correctly calculate composite metrics (ASP, CR, etc. must be recalculated from base metrics — never directly summed)
- Use SP-API to automatically collect order, inventory, and advertising data
- Use Playwright to auto-download reports from Seller Central that aren't available via API
- Use DuckDB for high-performance local queries on medium-sized datasets
- Build a complete pipeline from data collection to report generation, scheduled with cron

---

## 1. Data Engineering Methodology

> 📎 **Related Reading**: [A3 Advertising Optimization](../a-operators/a3-advertising.md#8-automate-ad-optimization-with-openclaw) — See A3 for advertising report analysis applications · [F4 Automation & Agents](../0-foundations/f4-agent-automation.md#f4-automation-ai-agents) — See F4 for the theoretical foundations of data processing automation with Agents.

### 1.1 First Principles of E-Commerce Data Pipelines

The essence of a data pipeline is transforming "raw data scattered across various sources" into "information ready for decision-making."

For cross-border e-commerce, data pipelines have several unique characteristics:
- **Small volume but fast-changing**: A mid-sized seller's daily data might only be a few MB, but report formats, column names, and encodings can change with Amazon backend updates
- **Fragmented data sources**: Sales are in Business Reports, ads in Advertising Console, inventory in FBA Reports, reviews on the storefront
- **Metric calculation pitfalls**: ASP (Average Selling Price) can't be averaged across rows — it must be recalculated as GMS ÷ Units; CR (Conversion Rate) follows the same rule

**ETL vs ELT — Which to Choose:**

| Pattern | Meaning | Best For |
|---------|---------|----------|
| ETL | Clean and transform first, then store | Large datasets with fixed schemas in traditional data warehouses |
| ELT | Store raw data first, then transform on demand | Small datasets with variable formats — typical in e-commerce |

For cross-border e-commerce, ELT is recommended: store the raw reports first (preserving original data), then write scripts to clean and calculate as needed. Here's why:
1. Amazon report formats may change — keeping raw data allows you to trace back
2. Different analyses require different cleaning logic on the same data
3. Data volume is small (typically <100MB), so storage cost is negligible

### 1.2 Amazon Data Source Overview

| Data Source | How to Obtain | Content | Update Frequency | Best For |
|-------------|---------------|---------|------------------|----------|
| Business Reports | Seller Central download / SP-API | Sales, traffic, conversion rate, Buy Box % | Daily | Daily ops monitoring, weekly/monthly reports |
| Advertising Reports | Advertising Console / SP-API | Ad spend, clicks, ACOS, keyword performance | Daily | Ad optimization, ROI analysis |
| Inventory Reports | Seller Central / SP-API | FBA inventory quantities, sellable/unsellable, age | Daily | Inventory alerts, restocking decisions |
| FBA Reports | Seller Central download | Logistics fees, return details, storage fees | Monthly | Cost analysis, return rate monitoring |
| Brand Analytics | Seller Central (brand owners) | Search term rankings, market basket, repeat purchases | Weekly | Keyword strategy, competitor analysis |
| SP-API | REST API calls | Orders, product catalog, pricing, inventory | Real-time | Automated systems, real-time monitoring |
| Review Data | Storefront scraping / third-party tools | Ratings, review text, images | Irregular | Product improvement, competitor analysis |

> 💡 **Key Insight**: Business Reports and Advertising Reports are the two most commonly used data sources, covering 80% of daily analysis needs. SP-API is ideal for real-time data or automation scenarios. Brand Analytics data is extremely valuable but only accessible to brand-registered sellers.

### 1.3 Technology Stack

| Tool | Purpose | Why This One | Installation |
|------|---------|-------------|-------------|
| [pandas](https://pandas.pydata.org/) | Core data processing | E-commerce data volumes (<1GB) are well within pandas' capabilities; most mature ecosystem | `pip install pandas` |
| [openpyxl](https://openpyxl.readthedocs.io/) | Excel read/write | Default engine for pandas .xlsx operations | `pip install openpyxl` |
| [python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api) | SP-API wrapper | Most active Python SP-API library, 1k+ stars | `pip install python-amazon-sp-api` |
| [DuckDB](https://duckdb.org/) | High-performance local queries | Query CSV/Parquet directly without importing; 10–100x faster than SQLite | `pip install duckdb` |
| [Playwright](https://playwright.dev/python/) | Browser automation | More modern than Selenium with auto-wait and better stability | `pip install playwright` |
| [schedule](https://github.com/dbader/schedule) | Scheduled tasks | Pure Python, more readable than cron | `pip install schedule` |
| [Streamlit](https://streamlit.io/) | Quick dashboards | Build interactive data dashboards in just a few dozen lines of code | `pip install streamlit` |

**Why not Spark/Airflow?**

Cross-border e-commerce data volumes (typically <1GB) don't require distributed computing. The operational overhead of Spark and Airflow far outweighs the benefits. pandas + DuckDB + cron is the optimal combination:
- pandas handles <100MB data effortlessly
- DuckDB processes 100MB–10GB data 10x faster than pandas
- cron (or the schedule library) is sufficient for scheduled tasks — no need for Airflow's DAG orchestration

---

## 2. Core Skill: pandas Data Processing

### 2.1 Common Data Issues in Amazon Reports

Before writing code, familiarize yourself with the "gotchas" you'll encounter. These issues come up repeatedly in real business scenarios:

| Issue | Symptom | Solution |
|-------|---------|----------|
| Encoding problems | Garbled Chinese/Japanese characters | US/EU reports: use `utf-8-sig` (handles BOM); JP reports: use `shift_jis` or `cp932` |
| Inconsistent date formats | US: `01/15/2025`, DE: `15.01.2025`, JP: `2025/01/15` | Use `pd.to_datetime()` with the `dayfirst` parameter, or standardize conversion |
| Commas in numeric columns | `"1,234.56"` read as string | `df['col'].str.replace(',', '').astype(float)` |
| Currency symbols | `"$29.99"` or `"€24,99"` | `str.replace('[$€¥£]', '', regex=True)` |
| Column name differences across marketplaces | US: `Units Ordered`, DE: `Bestellte Einheiten` | Build a column name mapping dictionary |
| Ratio metrics can't be directly summed | Averaging CR across rows → incorrect | Must recalculate from base metrics: CR = Total Units ÷ Total Sessions |
| Blank rows and summary rows | "Total" summary row at end of report | Filter out non-data rows after reading |

### 2.2 Code Example: Reading and Cleaning an Amazon Business Report

This is the code you'll use most often. A robust reading function needs to handle all the issues listed above:

```python
import pandas as pd
import numpy as np
from pathlib import Path

def load_business_report(filepath: str, market: str = "US") -> pd.DataFrame:
    """
    读取 Amazon Business Report CSV/Excel，处理常见数据问题。
    
    Args:
        filepath: 报告文件路径（支持 .csv 和 .xlsx）
        market: 市场标识 (US, DE, FR, IT, ES, UK, JP)
    
    Returns:
        清洗后的 DataFrame
    """
    path = Path(filepath)
    
    # 1. 根据市场选择编码
    encoding_map = {
        "US": "utf-8-sig",
        "UK": "utf-8-sig",
        "DE": "utf-8-sig",
        "FR": "utf-8-sig",
        "IT": "utf-8-sig",
        "ES": "utf-8-sig",
        "JP": "cp932",  # 日本站用 Shift-JIS 变体
    }
    encoding = encoding_map.get(market, "utf-8-sig")
    
    # 2. 读取文件
    if path.suffix == ".csv":
        df = pd.read_csv(filepath, encoding=encoding)
    elif path.suffix in (".xlsx", ".xls"):
        df = pd.read_excel(filepath, engine="openpyxl")
    else:
        raise ValueError(f"不支持的文件格式: {path.suffix}")
    
    # 3. 统一列名（处理多语言列名差异）
    column_mapping = {
        # 德语列名映射
        "Bestellte Einheiten": "Units Ordered",
        "Sitzungen": "Sessions",
        "Seitenaufrufe": "Page Views",
        # 日语列名映射
        "注文された商品の売上": "Ordered Product Sales",
        "セッション": "Sessions",
        # 通用清理
        "(Child) ASIN": "ASIN",
        "Child ASIN": "ASIN",
    }
    df = df.rename(columns=column_mapping)
    
    # 4. 清洗数值列（去除逗号、货币符号）
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
    
    # 5. 过滤无效行（汇总行、空行）
    if "ASIN" in df.columns:
        df = df[df["ASIN"].notna() & (df["ASIN"] != "")]
        df = df[~df["ASIN"].str.contains("Total|合計", na=False)]
    
    # 6. 添加市场标识
    df["Market"] = market
    
    return df

# 使用示例
# df_us = load_business_report("reports/us_business_report.csv", market="US")
# df_jp = load_business_report("reports/jp_business_report.csv", market="JP")
```

> ⚠️ **Important**: This function handles 80% of common issues. However, in real business scenarios you may encounter Amazon updating report formats, so it's recommended to add try-except blocks and logging.

### 2.3 Code Example: Merging Multiple Reports & Calculating Metrics

Cross-border e-commerce operations typically require merging reports across multiple marketplaces and time periods. There's a critical pitfall here: **ratio metrics cannot be directly summed or averaged**.

```python
def merge_reports(report_files: dict[str, str]) -> pd.DataFrame:
    """
    合并多个市场的 Business Report。
    
    Args:
        report_files: {market: filepath} 字典
            例如 {"US": "us_report.csv", "DE": "de_report.csv"}
    
    Returns:
        合并后的 DataFrame
    """
    frames = []
    for market, filepath in report_files.items():
        df = load_business_report(filepath, market=market)
        frames.append(df)
    
    merged = pd.concat(frames, ignore_index=True)
    return merged

def calculate_metrics(df: pd.DataFrame, group_by: list[str]) -> pd.DataFrame:
    """
    按指定维度计算核心指标。
    
    关键原则：比率指标必须从基础指标重算！
    - ASP = GMS / Units（不能对 ASP 列求平均）
    - CR = Units / Sessions（不能对 CR 列求平均）
    - Buy Box % = 加权平均（按 Sessions 加权）
    
    Args:
        df: 包含基础指标的 DataFrame
        group_by: 分组维度列表，如 ["Market", "Category"]
    
    Returns:
        汇总后的 DataFrame
    """
    # 先计算行级 GMS
    if "GMS" not in df.columns:
        if "Ordered Product Sales" in df.columns:
            df["GMS"] = df["Ordered Product Sales"]
        elif "Units Ordered" in df.columns and "Unit Price" in df.columns:
            df["GMS"] = df["Units Ordered"] * df["Unit Price"]
    
    # 按维度汇总基础指标
    agg_dict = {
        "Units Ordered": "sum",
        "GMS": "sum",
        "Sessions": "sum",
        "Page Views": "sum",
    }
    # 只聚合存在的列
    agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
    
    summary = df.groupby(group_by).agg(agg_dict).reset_index()
    
    # 从基础指标重算比率指标
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

# 使用示例
# reports = {"US": "us_report.csv", "DE": "de_report.csv", "JP": "jp_report.csv"}
# merged = merge_reports(reports)
# 
# # 按市场汇总
# by_market = calculate_metrics(merged, group_by=["Market"])
# 
# # 按市场+品类汇总
# by_market_cat = calculate_metrics(merged, group_by=["Market", "Category"])
```

> 💡 **Why can't you just average ASP?** Suppose Product A is priced at $10 and sold 100 units, while Product B is priced at $100 and sold 1 unit. A simple average ASP = ($10 + $100) / 2 = $55. But the true ASP = ($10×100 + $100×1) / 101 = $10.89. That's off by a factor of 5. This is the most common mistake in e-commerce data analysis.

### 2.4 Code Example: Automated Weekly Report Generation

Let's chain together the code above to generate a complete HTML weekly report:

```python
from datetime import datetime

def generate_weekly_report(
    report_files: dict[str, str],
    output_path: str = "weekly_report.html"
) -> str:
    """
    从原始报告生成 HTML 周报。
    
    完整 pipeline: 读取 → 合并 → 清洗 → 计算 → 输出
    """
    # 1. 读取和合并
    merged = merge_reports(report_files)
    
    # 2. 按市场汇总
    market_summary = calculate_metrics(merged, group_by=["Market"])
    
    # 3. 按品类汇总（如果有品类列）
    category_summary = None
    if "Category" in merged.columns:
        category_summary = calculate_metrics(
            merged, group_by=["Category"]
        ).sort_values("GMS", ascending=False)
    
    # 4. 计算整体指标
    total_gms = merged["GMS"].sum() if "GMS" in merged.columns else 0
    total_units = merged["Units Ordered"].sum()
    overall_asp = total_gms / total_units if total_units > 0 else 0
    
    # 5. 生成 HTML
    report_date = datetime.now().strftime("%Y-%m-%d")
    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>周报 {report_date}</title>
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
    <h1>📊 业务周报 | Weekly Report</h1>
    <p>生成时间: {report_date}</p>
    
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
    
    <h2>按市场 | By Market</h2>
    {market_summary.to_html(index=False)}
"""
    if category_summary is not None:
        html += f"""
    <h2>按品类 | By Category</h2>
    {category_summary.to_html(index=False)}
"""
    html += """
</body>
</html>"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ 周报已生成: {output_path}")
    return output_path

# 使用示例
# generate_weekly_report(
#     report_files={"US": "us_report.csv", "DE": "de_report.csv"},
#     output_path="output/weekly_report_2025_01_20.html"
# )
```

> 💡 **Why HTML instead of Excel?** HTML reports can be opened directly in a browser, shared via email, or embedded in internal systems. No software installation required. Plus, HTML supports richer styling and interactivity (like Chart.js charts).

---

## 3. SP-API Data Collection

### 3.1 Getting Started with SP-API

Amazon Selling Partner API (SP-API) is the official channel for obtaining real-time data. Compared to manually downloading reports, SP-API offers:
- **Automation**: Scripts run on a schedule — no manual intervention needed
- **Real-time data**: Order data is near real-time; inventory data updates hourly
- **Structured output**: Returns JSON format, ready to use

**Setup (one-time configuration):**

1. Register a developer account on [Seller Central](https://sellercentral.amazon.com/)
2. Create an SP-API application and obtain your `client_id` and `client_secret`
3. Get a `refresh_token` (via the OAuth authorization flow)
4. Install the Python library: `pip install python-amazon-sp-api`

**Credential Management (Important! Never hardcode credentials):**

```python
# config.json — 不要提交到 Git！加入 .gitignore
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
# 或者用环境变量（推荐）
import os
from dotenv import load_dotenv

load_dotenv()  # 从 .env 文件加载

credentials = {
    "refresh_token": os.getenv("SP_API_REFRESH_TOKEN"),
    "lwa_app_id": os.getenv("SP_API_CLIENT_ID"),
    "lwa_client_secret": os.getenv("SP_API_CLIENT_SECRET"),
}
```

> ⚠️ **Security Reminder**: Leaked SP-API credentials could lead to store data theft. Always use environment variables or encrypted configuration files, and never commit credentials to Git.

### 3.2 Code Example: Fetching Order Data

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
    获取最近 N 天的订单数据。
    
    Args:
        credentials: SP-API 凭证字典
        marketplace: 目标市场
        days_back: 回溯天数
    
    Returns:
        订单 DataFrame
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
    
    # 转换为 DataFrame
    if not all_orders:
        return pd.DataFrame()
    
    df = pd.json_normalize(all_orders)
    
    # 清洗关键字段
    if "OrderTotal.Amount" in df.columns:
        df["OrderTotal.Amount"] = pd.to_numeric(
            df["OrderTotal.Amount"], errors="coerce"
        )
    
    if "PurchaseDate" in df.columns:
        df["PurchaseDate"] = pd.to_datetime(df["PurchaseDate"])
    
    return df

# 使用示例
# from sp_api.base import Marketplaces
# orders = fetch_orders(credentials, Marketplaces.US, days_back=30)
# print(f"获取到 {len(orders)} 个订单")
```

Reference docs: [SP-API Orders API](https://developer-docs.amazon.com/sp-api/docs/orders-api-v0-reference) | [python-amazon-sp-api docs](https://python-amazon-sp-api.readthedocs.io/)

### 3.3 Code Example: Fetching Inventory Data

Inventory monitoring is the lifeline of cross-border e-commerce. Stockout = lost rankings = lost revenue.

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
    获取 FBA 库存汇总数据。
    
    Args:
        credentials: SP-API 凭证
        marketplace: 目标市场
        granularity: 粒度 ("Marketplace" 或 "Country")
    
    Returns:
        库存 DataFrame，包含可售数量、不可售数量等
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
    
    # 添加库存健康标记
    if "totalQuantity" in df.columns:
        df["stock_status"] = df["totalQuantity"].apply(
            lambda x: "🔴 断货" if x == 0
            else "🟡 低库存" if x < 50
            else "🟢 正常"
        )
    
    return df

# 使用示例
# inventory = fetch_inventory(credentials, Marketplaces.US)
# low_stock = inventory[inventory["stock_status"] != "🟢 正常"]
# print(f"⚠️ 需要关注的 SKU: {len(low_stock)}")
```

### 3.4 Code Example: Fetching Advertising Reports

Advertising data is the foundation for optimizing ACOS. SP-API advertising reports are asynchronous: you first request report generation, wait for it to complete, then download.

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
    请求并下载 SP-API 报告（异步流程）。
    
    SP-API 报告流程：
    1. 创建报告请求 → 获取 reportId
    2. 轮询报告状态 → 等待 DONE
    3. 获取报告文档 → 下载内容
    
    Args:
        credentials: SP-API 凭证
        marketplace: 目标市场
        report_type: 报告类型（参考 SP-API 文档）
        days_back: 回溯天数
    """
    reports_api = Reports(
        credentials=credentials, marketplace=marketplace
    )
    
    from datetime import datetime, timedelta
    start_date = (
        datetime.utcnow() - timedelta(days=days_back)
    ).strftime("%Y-%m-%dT00:00:00Z")
    end_date = datetime.utcnow().strftime("%Y-%m-%dT23:59:59Z")
    
    # Step 1: 创建报告请求
    create_response = reports_api.create_report(
        reportType=report_type,
        dataStartTime=start_date,
        dataEndTime=end_date,
        marketplaceIds=[marketplace.marketplace_id]
    )
    report_id = create_response.payload["reportId"]
    print(f"📋 报告请求已创建: {report_id}")
    
    # Step 2: 轮询状态（最多等 5 分钟）
    max_wait = 300  # 秒
    elapsed = 0
    poll_interval = 15
    
    while elapsed < max_wait:
        status_response = reports_api.get_report(report_id)
        status = status_response.payload["processingStatus"]
        
        if status == "DONE":
            doc_id = status_response.payload["reportDocumentId"]
            print(f"✅ 报告生成完成: {doc_id}")
            break
        elif status in ("CANCELLED", "FATAL"):
            raise RuntimeError(f"报告生成失败: {status}")
        
        print(f"⏳ 等待中... ({elapsed}s, 状态: {status})")
        time.sleep(poll_interval)
        elapsed += poll_interval
    else:
        raise TimeoutError("报告生成超时（5分钟）")
    
    # Step 3: 下载报告文档
    doc_response = reports_api.get_report_document(
        doc_id, download=True
    )
    
    # 解析内容（通常是 TSV 格式）
    content = doc_response.payload.get("document", "")
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    
    from io import StringIO
    df = pd.read_csv(StringIO(content), sep="\t")
    
    print(f"📊 获取到 {len(df)} 行数据")
    return df

# 使用示例
# ad_report = request_advertising_report(
#     credentials, Marketplaces.US,
#     report_type="GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
#     days_back=30
# )
```

> 💡 **Common Report Types**:
> - `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` — Order report
> - `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA` — FBA inventory report
> - `GET_MERCHANT_LISTINGS_ALL_DATA` — Product listings report
> 
> For the full list, see [SP-API Report Type Values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

### 3.5 Code Example: Scheduled Data Collection Script

Let's chain together the collection logic above and use the `schedule` library for scheduled tasks:

```python
import schedule
import time
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
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
    """每日数据采集任务"""
    today = datetime.now().strftime("%Y%m%d")
    output_dir = Path(f"data/raw/{today}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"开始每日数据采集: {today}")
    
    try:
        # 1. 获取订单数据
        orders = fetch_orders(credentials, days_back=1)
        orders.to_csv(output_dir / "orders.csv", index=False)
        logger.info(f"订单数据: {len(orders)} 行")
        
        # 2. 获取库存数据
        inventory = fetch_inventory(credentials)
        inventory.to_csv(output_dir / "inventory.csv", index=False)
        logger.info(f"库存数据: {len(inventory)} 行")
        
        # 3. 检查低库存预警
        low_stock = inventory[
            inventory.get("stock_status", "") != "🟢 正常"
        ] if "stock_status" in inventory.columns else pd.DataFrame()
        
        if len(low_stock) > 0:
            logger.warning(f"⚠️ {len(low_stock)} 个 SKU 库存异常！")
            # 可以在这里加邮件/Slack 通知
        
        logger.info(f"✅ 每日采集完成: {output_dir}")
        
    except Exception as e:
        logger.error(f"❌ 采集失败: {e}", exc_info=True)

def weekly_report_generation():
    """每周报告生成任务"""
    logger.info("开始生成周报...")
    try:
        # 合并本周的每日数据
        # ... 调用 generate_weekly_report()
        logger.info("✅ 周报生成完成")
    except Exception as e:
        logger.error(f"❌ 周报生成失败: {e}", exc_info=True)

# 设置定时任务
schedule.every().day.at("08:00").do(daily_data_collection)
schedule.every().monday.at("09:00").do(weekly_report_generation)

if __name__ == "__main__":
    logger.info("🚀 数据管道启动")
    logger.info(f"定时任务: 每日 08:00 采集, 每周一 09:00 生成周报")
    
    # 启动时先执行一次
    daily_data_collection()
    
    while True:
        schedule.run_pending()
        time.sleep(60)
```

> 💡 **Production Recommendation**: The `schedule` library is suitable for development and small-scale use. For production environments, system-level cron (macOS/Linux) or Windows Task Scheduler is recommended — more stable and doesn't depend on a continuously running Python process.
>
> ```bash
> # macOS/Linux cron example (run daily at 8 AM)
> # Edit crontab: crontab -e
> 0 8 * * * /usr/bin/python3 /path/to/daily_collection.py >> /path/to/cron.log 2>&1
> ```

---

## 4. Browser Automation (Selenium / Playwright)

### 4.1 When Do You Need Browser Automation?

SP-API covers most data needs, but some data can only be downloaded through the Seller Central web interface:

| Data | Available via SP-API? | Needs Browser Automation? |
|------|----------------------|--------------------------|
| Order data | ✅ | No |
| Inventory data | ✅ | No |
| Business Report | ✅ (partial) | Full version requires download |
| Brand Analytics | ❌ | ✅ Must log in to download |
| QuickSight reports | ❌ | ✅ Must log in to download |
| Detailed ad reports | ✅ (Advertising API) | No |
| A+ Content data | ❌ | ✅ |

### 4.2 Playwright vs Selenium Comparison

| Dimension | Playwright | Selenium |
|-----------|-----------|----------|
| Installation | `pip install playwright && playwright install` | `pip install selenium webdriver-manager` |
| Auto-wait | ✅ Built-in smart waiting | ❌ Requires manual `WebDriverWait` |
| Browser support | Chromium, Firefox, WebKit | Chrome, Firefox, Edge, Safari |
| Speed | Faster (communicates directly via CDP) | Slower (via WebDriver protocol) |
| Debugging | `PWDEBUG=1` visual debugging | Requires extra configuration |
| Community | Newer but growing fast | Mature, extensive docs and tutorials |
| Recommendation | ✅ First choice for new projects | Fine to keep using in existing projects |

**Bottom line**: Use Playwright for new projects; no need to migrate existing Selenium code.

### 4.3 Code Example: Auto-Downloading Business Report with Playwright

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
    自动登录 Seller Central 并下载 Business Report。
    
    Args:
        email: Seller Central 登录邮箱
        password: 登录密码
        marketplace_url: Seller Central URL
        download_dir: 下载目录
        otp_callback: OTP 验证码回调函数（用于两步验证）
    
    Returns:
        下载文件的路径
    
    注意：
    - Amazon 有反爬机制，频繁登录可能触发验证
    - 建议使用 headful 模式（非 headless）减少被检测概率
    - 两步验证需要手动输入或通过 OTP 回调处理
    """
    download_path = Path(download_dir).resolve()
    download_path.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        # 使用 headful 模式（可见浏览器窗口）
        browser = p.chromium.launch(
            headless=False,  # 设为 True 可无头运行，但更容易被检测
            slow_mo=500      # 每步操作间隔 500ms，模拟人类操作
        )
        
        context = browser.new_context(
            accept_downloads=True,
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            # 1. 导航到登录页
            page.goto(marketplace_url)
            page.wait_for_load_state("networkidle")
            
            # 2. 登录
            page.fill("#ap_email", email)
            page.click("#continue")
            page.fill("#ap_password", password)
            page.click("#signInSubmit")
            
            # 3. 处理两步验证（如果需要）
            if page.locator("#auth-mfa-otpcode").is_visible(timeout=5000):
                if otp_callback:
                    otp = otp_callback()
                else:
                    otp = input("请输入两步验证码: ")
                page.fill("#auth-mfa-otpcode", otp)
                page.click("#auth-signin-button")
            
            page.wait_for_load_state("networkidle")
            
            # 4. 导航到 Business Report 页面
            report_url = (
                f"{marketplace_url}/business-reports"
                "/ref=xx_sitemetric_dnav_xx"
            )
            page.goto(report_url)
            page.wait_for_load_state("networkidle")
            
            # 5. 点击下载按钮
            with page.expect_download() as download_info:
                # 选择 "Detail Page Sales and Traffic"
                page.click("text=Download")
            
            download = download_info.value
            dest = str(download_path / download.suggested_filename)
            download.save_as(dest)
            
            print(f"✅ 报告已下载: {dest}")
            return dest
            
        finally:
            browser.close()

# 使用示例
# filepath = download_business_report(
#     email="your_email@example.com",
#     password="your_password",
#     download_dir="data/raw/business_reports"
# )
```

> ⚠️ **Important Reminders**:
> 1. Automating Seller Central logins via browser may violate Amazon's Terms of Service — use with caution
> 2. Frequent automated logins may trigger account security verification
> 3. Always prioritize SP-API for data retrieval; browser automation should be a last resort
> 4. Never hardcode passwords — use environment variables or a secrets management tool

---

## 5. Data Storage & Querying

### 5.1 File Storage vs Database

| Solution | Data Volume | Query Speed | Best For | Learning Curve |
|----------|-------------|-------------|----------|---------------|
| CSV/Excel | <100MB | Slow (full load) | Small-scale, ad-hoc analysis | None |
| Parquet | <1GB | Fast (columnar storage) | Medium-scale, repeated queries | Low |
| DuckDB | 100MB–10GB | Very fast (OLAP engine) | Medium-scale, complex queries | Low |
| SQLite | <1GB | Moderate | Scenarios requiring transactions | Low |
| PostgreSQL | >1GB | Fast | Large-scale, multi-user | Medium |

**Recommended progression**:
- Starting out: CSV/Excel (you're probably already using these)
- Data grows to 50MB+: Switch to Parquet format (5–10x faster read/write)
- Need complex queries (JOINs, window functions): Introduce DuckDB
- Multi-user collaboration or web applications: PostgreSQL

### 5.2 DuckDB Quick Start

DuckDB is one of the most talked-about embedded analytical databases in recent years. Its killer feature: **query CSV/Parquet files directly without importing**.

```python
import duckdb

# 直接查询 CSV 文件 — 不需要先用 pandas 读取！
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

print(result.fetchdf())  # 返回 pandas DataFrame
```

**Where DuckDB really shines:**

```python
# 场景 1: 跨多个 CSV 文件查询（通配符）
# 一行 SQL 查询 data/raw/ 下所有日期文件夹中的 orders.csv
result = duckdb.sql("""
    SELECT 
        *,
        filename as source_file
    FROM read_csv_auto('data/raw/*/orders.csv', filename=true)
    WHERE "Units Ordered" > 10
    ORDER BY "Ordered Product Sales" DESC
    LIMIT 100
""")

# 场景 2: 窗口函数 — 计算每个 ASIN 的销量排名
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

# 场景 3: 将查询结果直接导出为 Parquet（比 CSV 快 10 倍）
duckdb.sql("""
    COPY (
        SELECT * FROM read_csv_auto('data/raw/*/orders.csv')
    ) TO 'data/processed/all_orders.parquet' (FORMAT PARQUET)
""")

# 场景 4: 与 pandas DataFrame 混合使用
import pandas as pd

df_inventory = pd.read_csv("data/raw/inventory.csv")

# DuckDB 可以直接查询 pandas DataFrame！
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
print("⚠️ 库存不足 30 天的 ASIN:")
print(result.fetchdf())
```

> 💡 **DuckDB vs pandas Performance**: For CSV files over 100MB, DuckDB query speed is typically 10–100x faster than pandas. The reason: DuckDB uses columnar storage and vectorized execution, while pandas needs to load the entire file into memory.
>
> Reference: [DuckDB Official Docs](https://duckdb.org/) | [DuckDB vs pandas Benchmarks](https://duckdb.org/2021/05/14/sql-on-pandas.html)

---

## 6. Data Visualization & Reporting

### 6.1 matplotlib/seaborn Basic Charts

For quick data exploration and analysis, matplotlib and seaborn are the most straightforward choices:

```python
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd

# 设置中文字体（macOS）
matplotlib.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti TC", "Arial"]
matplotlib.rcParams["axes.unicode_minus"] = False

def plot_market_comparison(df: pd.DataFrame, metric: str = "GMS"):
    """
    绘制多市场指标对比柱状图。
    
    Args:
        df: 包含 Market 和指标列的 DataFrame
        metric: 要对比的指标名
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = {"US": "#FF9900", "DE": "#003399", "JP": "#BC002D"}
    
    bars = ax.bar(
        df["Market"],
        df[metric],
        color=[colors.get(m, "#666") for m in df["Market"]]
    )
    
    # 在柱子上方显示数值
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2., height,
            f"${height:,.0f}" if metric == "GMS" else f"{height:,.0f}",
            ha="center", va="bottom", fontweight="bold"
        )
    
    ax.set_title(f"各市场 {metric} 对比", fontsize=14, fontweight="bold")
    ax.set_ylabel(metric)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(f"output/{metric}_by_market.png", dpi=150)
    plt.show()

# 使用示例
# market_data = calculate_metrics(merged, group_by=["Market"])
# plot_market_comparison(market_data, "GMS")
# plot_market_comparison(market_data, "Units Ordered")
```

### 6.2 Streamlit Quick Dashboard

Streamlit lets you build an interactive data dashboard in just a few dozen lines of code. Perfect for internal team use:

```python
# dashboard.py — 运行: streamlit run dashboard.py
import streamlit as st
import pandas as pd
import duckdb

st.set_page_config(page_title="📊 电商数据看板", layout="wide")
st.title("📊 电商数据看板 | E-Commerce Dashboard")

# 侧边栏：文件上传
uploaded_file = st.sidebar.file_uploader(
    "上传 Business Report", type=["csv", "xlsx"]
)

if uploaded_file:
    # 读取数据
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    
    st.sidebar.success(f"✅ 已加载 {len(df)} 行数据")
    
    # 核心指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    total_units = df["Units Ordered"].sum() if "Units Ordered" in df.columns else 0
    total_gms = df["GMS"].sum() if "GMS" in df.columns else 0
    asp = total_gms / total_units if total_units > 0 else 0
    
    col1.metric("Total Units", f"{total_units:,}")
    col2.metric("Total GMS", f"${total_gms:,.2f}")
    col3.metric("ASP", f"${asp:.2f}")
    col4.metric("SKU Count", f"{df['ASIN'].nunique() if 'ASIN' in df.columns else 0}")
    
    # 按维度筛选
    if "Market" in df.columns:
        selected_market = st.sidebar.multiselect(
            "选择市场", df["Market"].unique(), default=df["Market"].unique()
        )
        df = df[df["Market"].isin(selected_market)]
    
    # 数据表格
    st.subheader("📋 数据明细")
    st.dataframe(df, use_container_width=True)
    
    # DuckDB 自定义查询
    st.subheader("🔍 自定义 SQL 查询")
    query = st.text_area(
        "输入 SQL（表名为 df）",
        value='SELECT Market, SUM("Units Ordered") as units FROM df GROUP BY Market'
    )
    if st.button("执行查询"):
        try:
            result = duckdb.sql(query).fetchdf()
            st.dataframe(result)
        except Exception as e:
            st.error(f"查询错误: {e}")

else:
    st.info("👈 请在左侧上传 Business Report 文件")
```

> 💡 **Streamlit's Advantages**: Zero frontend code, auto-refresh, built-in chart components, one-click deployment to [Streamlit Cloud](https://streamlit.io/cloud) (free). Ideal for building internal data dashboards for your team.

### 6.3 HTML Report Generation (Self-Contained, Ready to Share)

For reports that need to be shared via email or IM, self-contained HTML is the best format. Chart.js loads from CDN — no build step required:

```python
def generate_html_dashboard(
    df: pd.DataFrame,
    title: str = "业务报告",
    output_path: str = "report.html"
):
    """
    生成自包含的 HTML 报告，含 Chart.js 交互图表。
    直接在浏览器打开，无需任何依赖。
    """
    # 准备图表数据
    if "Market" in df.columns and "GMS" in df.columns:
        market_data = df.groupby("Market")["GMS"].sum().reset_index()
        labels = market_data["Market"].tolist()
        values = market_data["GMS"].tolist()
    else:
        labels, values = [], []
    
    import json
    
    html = f"""<!DOCTYPE html>
<html lang="zh">
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
    <h1>📊 {title}</h1>
    
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
    
    print(f"✅ HTML 报告已生成: {output_path}")
    return output_path
```

> 💡 **Why self-contained HTML?** A single .html file is a complete report that can be sent directly via email, Slack, or WeChat. Recipients just double-click to view — no software installation needed. Chart.js loads from CDN, so the file itself is only a few KB.
---
---

## 7. Hands-On Project: Building a Complete Data Pipeline

### 7.1 Project Architecture

Let's integrate all the skills you've learned into a complete project:

```
data-pipeline/
├── config.json              # Configuration (API credential paths, report directories)
├── .env                     # Environment variables (API keys, don't commit to Git)
├── .gitignore               # Ignore .env, data/raw/, *.log
├── requirements.txt         # Python dependencies
│
├── extract/                 # Data collection layer
│   ├── __init__.py
│   ├── sp_api_client.py     # SP-API data collection (orders, inventory)
│   ├── report_downloader.py # Browser automation for report downloads
│   └── file_watcher.py      # Monitor folders, auto-process new reports
│
├── transform/               # Data cleaning and transformation layer
│   ├── __init__.py
│   ├── cleaners.py          # Generic cleaning functions (encoding, numbers, dates)
│   ├── business_report.py   # Business Report-specific cleaning
│   ├── advertising.py       # Advertising report-specific cleaning
│   └── metrics.py           # Metric calculations (GMS, ASP, CR)
│
├── load/                    # Data storage layer
│   ├── __init__.py
│   ├── file_store.py        # CSV/Parquet file storage
│   └── duckdb_store.py      # DuckDB query interface
│
├── report/                  # Report generation layer
│   ├── __init__.py
│   ├── html_report.py       # HTML report generation
│   ├── excel_report.py      # Excel report generation
│   └── templates/           # HTML templates
│       └── weekly.html
│
├── data/                    # Data directory (don't commit to Git)
│   ├── raw/                 # Raw data (organized by date)
│   │   └── 20250120/
│   └── processed/           # Cleaned data
│
├── output/                  # Output reports
│   └── weekly/
│
├── schedule.py              # Scheduled task entry point
├── run_pipeline.py          # Manual execution entry point
└── README.md                # Project documentation
```

### 7.2 Step-by-Step Build Guide

**Step 1: Initialize the Project**

```bash
mkdir data-pipeline && cd data-pipeline
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# 创建目录结构
mkdir -p extract transform load report/templates data/raw data/processed output

# 安装依赖
pip install pandas openpyxl duckdb python-amazon-sp-api \
            python-dotenv schedule playwright requests
pip freeze > requirements.txt

# 初始化 Playwright 浏览器
playwright install chromium
```

**Step 2: Configuration File**

```python
# config.py — 统一配置管理
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 项目根目录
ROOT_DIR = Path(__file__).parent

# 数据目录
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_DIR = ROOT_DIR / "output"

# SP-API 凭证（从环境变量读取）
SP_API_CREDENTIALS = {
    "refresh_token": os.getenv("SP_API_REFRESH_TOKEN", ""),
    "lwa_app_id": os.getenv("SP_API_CLIENT_ID", ""),
    "lwa_client_secret": os.getenv("SP_API_CLIENT_SECRET", ""),
    "aws_access_key": os.getenv("AWS_ACCESS_KEY", ""),
    "aws_secret_key": os.getenv("AWS_SECRET_KEY", ""),
    "role_arn": os.getenv("SP_API_ROLE_ARN", ""),
}

# 市场配置
MARKETS = {
    "US": {"encoding": "utf-8-sig", "currency": "USD"},
    "DE": {"encoding": "utf-8-sig", "currency": "EUR"},
    "JP": {"encoding": "cp932", "currency": "JPY"},
}

# 确保目录存在
for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)
```

**Step 3: Main Pipeline Script**

```python
# run_pipeline.py — 手动执行完整 pipeline
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
    执行完整的数据管道。
    
    Args:
        date_str: 数据日期 (YYYYMMDD)，默认今天
        markets: 要处理的市场列表，默认全部
    """
    date_str = date_str or datetime.now().strftime("%Y%m%d")
    markets = markets or list(MARKETS.keys())
    
    print(f"🚀 Pipeline 启动: {date_str}, 市场: {markets}")
    
    # === Extract ===
    raw_dir = RAW_DATA_DIR / date_str
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查是否有手动下载的报告文件
    report_files = {}
    for market in markets:
        pattern = f"*{market.lower()}*business*report*"
        found = list(raw_dir.glob(pattern))
        if found:
            report_files[market] = str(found[0])
            print(f"  📄 找到 {market} 报告: {found[0].name}")
    
    if not report_files:
        print("  ⚠️ 未找到报告文件，尝试通过 SP-API 获取...")
        # 这里可以调用 SP-API 采集逻辑
        return
    
    # === Transform ===
    merged = merge_reports(report_files)
    print(f"  🔄 合并完成: {len(merged)} 行")
    
    # 按市场汇总
    market_summary = calculate_metrics(merged, group_by=["Market"])
    
    # 保存处理后的数据
    from config import PROCESSED_DATA_DIR
    processed_dir = PROCESSED_DATA_DIR / date_str
    processed_dir.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(processed_dir / "merged.parquet", index=False)
    
    # === Load & Report ===
    output_path = OUTPUT_DIR / f"report_{date_str}.html"
    generate_html_dashboard(
        merged,
        title=f"业务报告 {date_str}",
        output_path=str(output_path)
    )
    
    print(f"\n✅ Pipeline 完成!")
    print(f"   处理数据: {processed_dir / 'merged.parquet'}")
    print(f"   输出报告: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="数据管道")
    parser.add_argument("--date", help="数据日期 YYYYMMDD")
    parser.add_argument("--markets", nargs="+", help="市场列表")
    args = parser.parse_args()
    
    run(date_str=args.date, markets=args.markets)
```

```bash
# Usage examples
python3 run_pipeline.py                          # Process today's data
python3 run_pipeline.py --date 20250120          # Process a specific date
python3 run_pipeline.py --markets US DE          # Process only US and DE
```

### 7.3 Common Issues and Debugging Tips

| Issue | Symptom | Solution |
|-------|---------|----------|
| Encoding error | `UnicodeDecodeError` | Check if the market parameter is correct; JP uses `cp932` |
| SP-API auth failure | `401 Unauthorized` | Check if refresh_token has expired; re-authorize |
| SP-API rate limiting | `429 Too Many Requests` | Add `time.sleep(1)` or use exponential backoff |
| Report format change | `KeyError: 'Units Ordered'` | Print `df.columns` to check column names; update mapping |
| Playwright timeout | `TimeoutError` | Increase the `timeout` parameter; check network connection |
| DuckDB type error | `Conversion Error` | Use `TRY_CAST` instead of `CAST`, or clean data first |
| Out of memory | `MemoryError` | Use DuckDB instead of pandas, or process in batches |
| cron not executing | No log output | Check Python path (use absolute path); check permissions |

**Debugging Tips:**

```python
# 1. 快速检查 DataFrame 结构
def inspect(df: pd.DataFrame, name: str = "df"):
    """快速检查 DataFrame 的结构和数据质量"""
    print(f"\n{'='*50}")
    print(f"📊 {name}: {df.shape[0]} 行 × {df.shape[1]} 列")
    print(f"列名: {list(df.columns)}")
    print(f"数据类型:\n{df.dtypes}")
    print(f"缺失值:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    print(f"前 3 行:\n{df.head(3)}")
    print(f"{'='*50}\n")

# 2. 安全的数值转换
def safe_numeric(series: pd.Series) -> pd.Series:
    """安全地将列转换为数值，无法转换的变为 NaN"""
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "")
        .str.replace(r"[$€¥£%]", "", regex=True)
        .str.strip(),
        errors="coerce"
    )

# 3. 数据质量检查
def quality_check(df: pd.DataFrame) -> dict:
    """返回数据质量报告"""
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

## 8. Learning Resources

### 8.1 Free Courses & Tutorials

| Resource | Platform | Duration | Best For | Link |
|----------|----------|----------|----------|------|
| Kaggle: Pandas Course | Kaggle | 4h | pandas beginners | [kaggle.com/learn/pandas](https://www.kaggle.com/learn/pandas) |
| Automate the Boring Stuff | Online book | Self-paced | Python automation intro | [automatetheboringstuff.com](https://automatetheboringstuff.com/) |
| SP-API Official Docs | Amazon | Self-paced | Developers using SP-API | [developer-docs.amazon.com/sp-api](https://developer-docs.amazon.com/sp-api) |
| DuckDB Official Docs | DuckDB | Self-paced | SQL queries on local files | [duckdb.org](https://duckdb.org/) |
| Playwright Python Docs | Microsoft | Self-paced | Browser automation | [playwright.dev/python](https://playwright.dev/python/) |
| pandas Official Docs | pandas | Self-paced | Advanced usage reference | [pandas.pydata.org](https://pandas.pydata.org/) |

### 8.2 Recommended YouTube Channels

| Channel | Focus | Why Recommended |
|---------|-------|-----------------|
| Corey Schafer | Python basics + pandas | Clear explanations, great for beginners; pandas series is a classic |
| sentdex | Python data analysis | Lots of hands-on projects, covers data collection through visualization |
| Rob Mulla | pandas + data science | Focused on pandas tips, short videos for efficient learning |
| ArjanCodes | Python engineering practices | Code architecture, design patterns — helps you write better pipelines |

Content rephrased for compliance with licensing restrictions. Sources cited inline.

### 8.3 Recommended GitHub Repositories

| Repository | Stars | Purpose |
|------------|-------|---------|
| [python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api) | 1k+ | SP-API Python wrapper — core dependency for this module |
| [awesome-pandas](https://github.com/tommyod/awesome-pandas) | 500+ | Curated pandas learning resources |
| [DuckDB](https://github.com/duckdb/duckdb) | 20k+ | Embedded analytical database source code |
| [Playwright Python](https://github.com/microsoft/playwright-python) | 10k+ | Browser automation framework |

---

## 9. Automating Data Pipelines with OpenClaw

### 9.1 Scenario: AI Agent Auto-Collecting and Processing Amazon Reports

```
You tell OpenClaw:
"Every day at 8 AM, download yesterday's Business Report and Advertising Report from Seller Central,
merge them into the Google Sheet 'Daily Dashboard', and if any metrics are abnormal (sales drop >20%,
ACOS increase >10%), send a Slack alert to #daily-ops"

OpenClaw automatically executes:
1. [Heartbeat] Triggers at 8:00 AM daily
2. [Skill: web-search / fetch MCP] Fetches report data
3. [LLM + pandas] Data cleaning and merging
4. [Skill: google-sheets] Writes to Dashboard
5. [LLM] Detects abnormal metrics
6. [Skill: slack] Sends alert on anomalies
```

### 9.2 Required Skills and MCP Servers

| Component | Purpose | Link |
|-----------|---------|------|
| **google-sheets** Skill | Read/write data reports | [ClawHub](https://clawhub.ai/) |
| **slack** Skill | Anomaly alert notifications | [ClawHub](https://clawhub.ai/) |
| **memory** Skill | Store historical baseline data | [OpenClaw Docs](https://docs.openclaw.com/) |
| **filesystem MCP** | Read/write local CSV/Excel | [MCP Filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) |
| **fetch MCP** | Call external APIs like SP-API | [MCP Fetch](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) |
| **sqlite MCP** | Local database storage | [MCP SQLite](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite) |

### 9.3 Related Resources

| Resource | Description | Link |
|----------|-------------|------|
| OpenClaw Official Docs | Installation and configuration guide | [docs.openclaw.com](https://docs.openclaw.com/) |
| ClawHub Skills Marketplace | Search and install Agent Skills | [clawhub.ai](https://clawhub.ai/) |
| OpenClaw MCP Integration | Connecting MCP Servers | [Build Skill with MCP](https://rebeccamdeprey.com/blog/build-openclaw-skill-with-mcp) |
| F4 Automation & Agents | Agent foundations module | [F4 Module](../0-foundations/f4-agent-automation.md) |

Content rephrased for compliance with licensing restrictions. Sources cited inline.

---

## 10. Completion Checklist

- [ ] Write a script to automatically read and clean an Amazon Business Report (handling encoding, numeric, and date issues)
- [ ] Write a script to merge reports from multiple marketplaces and correctly calculate ASP and CR (recalculated from base metrics)
- [ ] Use SP-API to fetch at least one type of data (orders or inventory)
- [ ] Execute at least one SQL query on a CSV file using DuckDB
- [ ] Generate a self-contained HTML weekly report (with Chart.js charts)
- [ ] Build a complete pipeline project structure (extract → transform → load → report)

Once you've completed all the items above, you've mastered the core skills of e-commerce data pipelines. Next up: [B2 Prediction Models](b2-prediction-models.md), where you'll learn to forecast sales with Prophet.

---

## Appendix: Quick Reference

### pandas Common Operations

```python
# 读取
df = pd.read_csv("file.csv", encoding="utf-8-sig")
df = pd.read_excel("file.xlsx", engine="openpyxl")

# 清洗
df["col"] = df["col"].str.replace(",", "").astype(float)  # 去逗号转数值
df["date"] = pd.to_datetime(df["date"])                    # 转日期
df = df.dropna(subset=["ASIN"])                            # 删除空行
df = df[df["Units"] >= 0]                                  # 过滤负数

# 聚合（正确计算比率指标）
summary = df.groupby("Market").agg(
    units=("Units Ordered", "sum"),
    gms=("GMS", "sum"),
    sessions=("Sessions", "sum")
).reset_index()
summary["ASP"] = summary["gms"] / summary["units"]        # 重算 ASP
summary["CR"] = summary["units"] / summary["sessions"]    # 重算 CR

# 导出
df.to_csv("output.csv", index=False)
df.to_excel("output.xlsx", index=False)
df.to_parquet("output.parquet", index=False)               # 推荐！
```

### SP-API Common Endpoints

| Endpoint | Purpose | python-amazon-sp-api Class |
|----------|---------|---------------------------|
| Orders API | Fetch order lists and details | `sp_api.api.Orders` |
| Catalog Items API | Fetch product information | `sp_api.api.CatalogItems` |
| FBA Inventory API | Fetch FBA inventory | `sp_api.api.Inventories` |
| Reports API | Request and download reports | `sp_api.api.Reports` |
| Product Pricing API | Fetch product pricing | `sp_api.api.ProductPricing` |
| Notifications API | Subscribe to event notifications | `sp_api.api.Notifications` |

Full API reference: [SP-API Docs](https://developer-docs.amazon.com/sp-api) | [python-amazon-sp-api Docs](https://python-amazon-sp-api.readthedocs.io/)

### DuckDB Common Queries

```sql
-- 直接查询 CSV
SELECT * FROM read_csv_auto('data.csv') LIMIT 10;

-- 查询多个文件（通配符）
SELECT * FROM read_csv_auto('data/raw/*/orders.csv');

-- 聚合查询
SELECT Market, SUM("Units Ordered") as units, SUM(GMS) as gms
FROM read_csv_auto('data.csv')
GROUP BY Market;

-- 窗口函数（排名）
SELECT *, RANK() OVER (PARTITION BY Market ORDER BY GMS DESC) as rank
FROM read_csv_auto('data.csv');

-- 导出为 Parquet
COPY (SELECT * FROM read_csv_auto('data.csv')) 
TO 'output.parquet' (FORMAT PARQUET);

-- 查询 pandas DataFrame（在 Python 中）
-- duckdb.sql("SELECT * FROM df WHERE units > 100")
```

### Data Cleaning Checklist

Before processing any Amazon report, verify the following:

- [ ] File encoding is correct (US/EU: utf-8-sig, JP: cp932)
- [ ] Column names are standardized (handle multi-language column name differences)
- [ ] Numeric columns have commas and currency symbols removed
- [ ] Date columns are converted to datetime type
- [ ] Summary rows (Total) and blank rows are filtered out
- [ ] Negative values and zeros are handled (filtered or flagged)
- [ ] Ratio metrics are recalculated from base metrics (never directly sum/avg)
- [ ] Market identifier column (Market) is added
- [ ] Data quality checks pass (missing values, duplicate rows, outliers)

---
> 🏠 [Hub Home](../../README.md) · 📋 [Path B Overview](README.md)
> 
> **Path B**: [B1 Data](b1-data-pipeline.md) · [B2 Prediction](b2-prediction-models.md) · [B3 RAG](b3-rag-knowledge-base.md) · [B4 Agent](b4-agent-workflow.md) · [B5 Deployment](b5-local-model-deploy.md)
> 
> **Quick Jump**: [Path 0 Foundations](../0-foundations/) · [Path A Operations](../a-operators/) · [Path C Management](../c-managers/) · [Path D Multi-Platform](../d-platforms/) · [Path E Social Media](../e-social-media/)
