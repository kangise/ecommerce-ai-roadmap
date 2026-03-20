# B1. 数据采集与处理自动化 | Data Collection & Processing Automation

> **路径**: Path B: 技术人 · **模块**: B1
> **最后更新**: 2026-03-12
> **难度**: 中级
> **前提**: Python 基础（变量、函数、列表、字典）
> **预计时间**: 每天 1 小时，1-2 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kangise/ecommerce-ai-roadmap/blob/main/notebooks/b1-data-pipeline.ipynb) 直接在 Colab 运行配套 Notebook
---

[Hub 首页](../../README.md) · [Path B 总览](README.md)

```mermaid
flowchart LR
B1[" B1 数据管道<br/>（当前）"]:::current
B1 --> B2
B2["B2 预测模型"]
B2 --> B3
B3["B3 RAG 知识库"]
B3 --> B4
B4["B4 Agent 工作流"]
B4 --> B5
B5["B5 本地模型部署"]
classDef current fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
```

---

## 本模块章节导航

1. [数据工程方法论](#1-数据工程方法论) · 2. [pandas 数据处理](#2-核心技能pandas-数据处理) · 3. [SP-API 数据采集](#3-sp-api-数据采集) · 4. [浏览器自动化](#4-浏览器自动化selenium--playwright) · 5. [数据存储与查询](#5-数据存储与查询) · 6. [数据可视化](#6-数据可视化与报告) · 7. [实战项目](#7-实战项目构建完整的数据管道) · 8. [学习资源](#8-学习资源) · 9. [ OpenClaw 自动化](#9-用-openclaw-自动化数据管道) · 10. [完成标志](#10-完成标志)


## 本模块你将构建

一个自动化数据管道：从 Amazon 报告到清洗后的分析数据集。

完成本模块后，你将能够：
- 用 pandas 批量读取和清洗 Amazon 各类报告（Business Report、Advertising Report、FBA Report）
- 处理真实数据中的编码问题、日期格式不一致、多 marketplace 列名差异
- 正确计算复合指标（ASP、CR 等必须从基础指标重算，不能直接 sum）
- 用 SP-API 自动采集订单、库存、广告数据
- 用 Playwright 自动下载 Seller Central 中无法通过 API 获取的报告
- 用 DuckDB 对中等规模数据做高性能本地查询
- 搭建一个从数据采集到报告生成的完整 pipeline，并用 cron 定时运行

---

## 1. 数据工程方法论

> **相关阅读**: [A3 广告优化](../a-operators/a3-advertising.md) 広告報告分析応用详见 A3 · [F4 自動化与 Agent](../0-foundations/f4-agent-automation.md) 数据处理自动化的 Agent 基础理论详见 F4。

### 1.1 电商数据管道的第一性原理

数据管道的本质是把"散落在各处的原始数据"变成"可以直接用于决策的信息"。

对于跨境电商场景，数据管道有几个特殊性：
- **数据量不大但变化快**：一个中型卖家每天的数据量可能只有几 MB，但报告格式、列名、编码会随 Amazon 后台更新而变化
- **数据源碎片化**：销量在 Business Report，广告在 Advertising Console，库存在 FBA Report，Review 在前台页面
- **指标计算有陷阱**：ASP（平均售价）不能直接对多行求平均，必须用 GMS ÷ Units 重算；CR（转化率）同理

**ETL vs ELT 的选择：**

| 模式 | 含义 | 适合场景 |
|------|------|----------|
| ETL | 先清洗转换，再存储 | 数据量大、schema 固定的传统数仓 |
| ELT | 先存储原始数据，再按需转换 | 数据量小但格式多变的电商场景 |

对于跨境电商，推荐 ELT 模式：先把原始报告存下来（保留原始数据），再写脚本按需清洗和计算。原因：
1. Amazon 报告格式可能变化，保留原始数据方便回溯
2. 不同分析需求对同一份数据的清洗逻辑不同
3. 数据量小（通常 <100MB），存储成本可忽略

### 1.2 Amazon 数据源全景

| 数据源 | 获取方式 | 数据内容 | 更新频率 | 适合场景 |
|--------|----------|----------|----------|----------|
| Business Reports | Seller Central 下载 / SP-API | 销量、流量、转化率、Buy Box % | 每日 | 日常运营监控、周报月报 |
| Advertising Reports | Advertising Console / SP-API | 广告花费、点击、ACOS、关键词表现 | 每日 | 广告优化、ROI 分析 |
| Inventory Reports | Seller Central / SP-API | FBA 库存数量、可售/不可售、库龄 | 每日 | 库存预警、补货决策 |
| FBA Reports | Seller Central 下载 | 物流费用、退货明细、仓储费 | 每月 | 成本分析、退货率监控 |
| Brand Analytics | Seller Central（品牌卖家） | 搜索词排名、市场篮子、重复购买 | 每周 | 关键词策略、竞品分析 |
| SP-API | REST API 调用 | 订单、产品目录、定价、库存 | 实时 | 自动化系统、实时监控 |
| Review 数据 | 前台页面抓取 / 第三方工具 | 评分、评论文本、图片 | 不定期 | 产品改进、竞品分析 |

> **关键洞察**：Business Report 和 Advertising Report 是最常用的两个数据源，覆盖了 80% 的日常分析需求。SP-API 适合需要实时数据或自动化的场景。Brand Analytics 数据价值极高但只有品牌卖家才能访问。

### 1.3 技术栈选择

| 工具 | 用途 | 为什么选它 | 安装 |
|------|------|-----------|------|
| [pandas](https://pandas.pydata.org/) | 数据处理核心 | 电商数据量级（<1GB）pandas 完全够用，生态最成熟 | `pip install pandas` |
| [openpyxl](https://openpyxl.readthedocs.io/) | Excel 读写 | pandas 读写 .xlsx 的默认引擎 | `pip install openpyxl` |
| [python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api) | SP-API 封装 | 最活跃的 Python SP-API 库，star 1k+ | `pip install python-amazon-sp-api` |
| [DuckDB](https://duckdb.org/) | 本地高性能查询 | 直接查询 CSV/Parquet，无需导入，比 SQLite 快 10-100x | `pip install duckdb` |
| [Playwright](https://playwright.dev/python/) | 浏览器自动化 | 比 Selenium 更现代，自动等待、更稳定 | `pip install playwright` |
| [schedule](https://github.com/dbader/schedule) | 定时任务 | 纯 Python，比 cron 更易读 | `pip install schedule` |
| [Streamlit](https://streamlit.io/) | 快速仪表盘 | 几十行代码搭建交互式数据看板 | `pip install streamlit` |

**为什么不用 Spark/Airflow？**

跨境电商的数据量级（通常 <1GB）不需要分布式计算。Spark 和 Airflow 的运维成本远大于收益。pandas + DuckDB + cron 就是最佳组合：
- pandas 处理 <100MB 的数据毫无压力
- DuckDB 处理 100MB-10GB 的数据比 pandas 快 10 倍以上
- cron（或 schedule 库）足够做定时任务，不需要 Airflow 的 DAG 编排

---

## 2. 核心技能：pandas 数据处理

### 2.1 Amazon 报告的常见数据问题

在写代码之前，先了解你会遇到的"坑"。这些问题在真实业务中反复出现：

| 问题 | 表现 | 解决方案 |
|------|------|----------|
| 编码问题 | 中文乱码、日文乱码 | US/EU 报告用 `utf-8-sig`（处理 BOM），JP 报告用 `shift_jis` 或 `cp932` |
| 日期格式不一致 | US: `01/15/2025`，DE: `15.01.2025`，JP: `2025/01/15` | 用 `pd.to_datetime()` 的 `dayfirst` 参数，或统一转换 |
| 数值列含逗号 | `"1,234.56"` 被读成字符串 | `df['col'].str.replace(',', '').astype(float)` |
| 货币符号 | `"$29.99"` 或 `"€24,99"` | `str.replace('[$€¥£]', '', regex=True)` |
| 多 marketplace 列名差异 | US: `Units Ordered`，DE: `Bestellte Einheiten` | 建立列名映射字典 |
| 比率指标不能直接 sum | 把多行的 CR 直接求平均 → 错误 | 必须从基础指标重算：CR = Total Units ÷ Total Sessions |
| 空行和汇总行 | 报告末尾有 "Total" 汇总行 | 读取后过滤掉非数据行 |

### 2.2 代码示例：读取和清洗 Amazon Business Report

这是你最常用的代码。一个健壮的读取函数需要处理上面列出的所有问题：

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
"JP": "cp932", # 日本站用 Shift-JIS 变体
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

> **重要**：这个函数处理了 80% 的常见问题。但真实业务中你可能还会遇到 Amazon 更新报告格式的情况，建议加上 try-except 和日志记录。

### 2.3 代码示例：多报告合并与指标计算

跨境电商运营通常需要合并多个市场、多个时间段的报告。这里有一个关键陷阱：**比率指标不能直接求和或求平均**。

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

> **为什么 ASP 不能直接求平均？** 假设产品 A 售价 $10 卖了 100 件，产品 B 售价 $100 卖了 1 件。直接平均 ASP = ($10 + $100) / 2 = $55。但真实 ASP = ($10×100 + $100×1) / 101 = $10.89。差了 5 倍。这是电商数据分析中最常见的错误。

### 2.4 代码示例：自动化周报生成

把上面的代码串起来，生成一份完整的 HTML 周报：

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
<h1> 业务周报 | Weekly Report</h1>
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

print(f" 周报已生成: {output_path}")
return output_path

# 使用示例
# generate_weekly_report(
# report_files={"US": "us_report.csv", "DE": "de_report.csv"},
# output_path="output/weekly_report_2025_01_20.html"
# )
```

> **为什么用 HTML 而不是 Excel？** HTML 报告可以直接在浏览器打开、通过邮件分享、嵌入到内部系统。不需要安装任何软件。而且 HTML 支持更丰富的样式和交互（如 Chart.js 图表）。

---

## 3. SP-API 数据采集

### 3.1 SP-API 入门

Amazon Selling Partner API (SP-API) 是获取实时数据的官方渠道。相比手动下载报告，SP-API 的优势：
- **自动化**：脚本定时调用，无需人工操作
- **实时性**：订单数据几乎实时，库存数据每小时更新
- **结构化**：返回 JSON 格式，直接可用

**准备工作（一次性设置）：**

1. 在 [Seller Central](https://sellercentral.amazon.com/) 注册开发者账号
2. 创建 SP-API 应用，获取 `client_id` 和 `client_secret`
3. 获取 `refresh_token`（通过 OAuth 授权流程）
4. 安装 Python 库：`pip install python-amazon-sp-api`

**凭证管理（重要！不要硬编码）：**

```python
# config.json 不要提交到 Git！加入 .gitignore
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

load_dotenv() # 从 .env 文件加载

credentials = {
"refresh_token": os.getenv("SP_API_REFRESH_TOKEN"),
"lwa_app_id": os.getenv("SP_API_CLIENT_ID"),
"lwa_client_secret": os.getenv("SP_API_CLIENT_SECRET"),
}
```

> **安全提醒**：SP-API 凭证泄露可能导致店铺数据被盗。务必使用环境变量或加密配置文件，永远不要把凭证提交到 Git。

### 3.2 代码示例：获取订单数据

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

参考文档：[SP-API Orders API](https://developer-docs.amazon.com/sp-api/docs/orders-api-v0-reference) | [python-amazon-sp-api 文档](https://python-amazon-sp-api.readthedocs.io/)

### 3.3 代码示例：获取库存数据

库存监控是跨境电商的生命线。断货 = 丢排名 = 丢钱。

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
lambda x: " 断货" if x == 0
else " 低库存" if x < 50
else " 正常"
)

return df

# 使用示例
# inventory = fetch_inventory(credentials, Marketplaces.US)
# low_stock = inventory[inventory["stock_status"] != " 正常"]
# print(f" 需要关注的 SKU: {len(low_stock)}")
```

### 3.4 代码示例：获取广告报告

广告数据是优化 ACOS 的基础。SP-API 的广告报告是异步的：先请求生成报告，等报告生成完成后再下载。

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
print(f" 报告请求已创建: {report_id}")

# Step 2: 轮询状态（最多等 5 分钟）
max_wait = 300 # 秒
elapsed = 0
poll_interval = 15

while elapsed < max_wait:
status_response = reports_api.get_report(report_id)
status = status_response.payload["processingStatus"]

if status == "DONE":
doc_id = status_response.payload["reportDocumentId"]
print(f" 报告生成完成: {doc_id}")
break
elif status in ("CANCELLED", "FATAL"):
raise RuntimeError(f"报告生成失败: {status}")

print(f" 等待中... ({elapsed}s, 状态: {status})")
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

print(f" 获取到 {len(df)} 行数据")
return df

# 使用示例
# ad_report = request_advertising_report(
# credentials, Marketplaces.US,
# report_type="GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
# days_back=30
# )
```

> **常用报告类型**：
> - `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` 订单报告
> - `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA` FBA 库存报告
> - `GET_MERCHANT_LISTINGS_ALL_DATA` 商品列表报告
>
> 完整列表参考 [SP-API Report Type Values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

### 3.5 代码示例：定时数据采集脚本

把上面的采集逻辑串起来，用 `schedule` 库做定时任务：

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
inventory.get("stock_status", "") != " 正常"
] if "stock_status" in inventory.columns else pd.DataFrame()

if len(low_stock) > 0:
logger.warning(f" {len(low_stock)} 个 SKU 库存异常！")
# 可以在这里加邮件/Slack 通知

logger.info(f" 每日采集完成: {output_dir}")

except Exception as e:
logger.error(f" 采集失败: {e}", exc_info=True)

def weekly_report_generation():
"""每周报告生成任务"""
logger.info("开始生成周报...")
try:
# 合并本周的每日数据
# ... 调用 generate_weekly_report()
logger.info(" 周报生成完成")
except Exception as e:
logger.error(f" 周报生成失败: {e}", exc_info=True)

# 设置定时任务
schedule.every().day.at("08:00").do(daily_data_collection)
schedule.every().monday.at("09:00").do(weekly_report_generation)

if __name__ == "__main__":
logger.info(" 数据管道启动")
logger.info(f"定时任务: 每日 08:00 采集, 每周一 09:00 生成周报")

# 启动时先执行一次
daily_data_collection()

while True:
schedule.run_pending()
time.sleep(60)
```

> **生产环境建议**：`schedule` 库适合开发和小规模使用。生产环境推荐用系统级 cron（macOS/Linux）或 Windows Task Scheduler，更稳定且不依赖 Python 进程持续运行。
>
> ```bash
> # macOS/Linux cron 示例（每天早上 8 点执行）
> # 编辑 crontab: crontab -e
> 0 8 * * * /usr/bin/python3 /path/to/daily_collection.py >> /path/to/cron.log 2>&1
> ```

---

## 4. 浏览器自动化（Selenium / Playwright）

### 4.1 什么时候需要浏览器自动化

SP-API 覆盖了大部分数据需求，但有些数据只能通过 Seller Central 网页下载：

| 数据 | SP-API 可获取？ | 需要浏览器自动化？ |
|------|----------------|-------------------|
| 订单数据 | | 否 |
| 库存数据 | | 否 |
| Business Report | （部分） | 完整版需要下载 |
| Brand Analytics | | 必须登录下载 |
| QuickSight 报表 | | 必须登录下载 |
| 广告详细报告 | （Advertising API） | 否 |
| A+ Content 数据 | | |

### 4.2 Playwright vs Selenium 对比

| 维度 | Playwright | Selenium |
|------|-----------|----------|
| 安装 | `pip install playwright && playwright install` | `pip install selenium webdriver-manager` |
| 自动等待 | 内置智能等待 | 需要手动 `WebDriverWait` |
| 浏览器支持 | Chromium, Firefox, WebKit | Chrome, Firefox, Edge, Safari |
| 速度 | 更快（直接通过 CDP 通信） | 较慢（通过 WebDriver 协议） |
| 调试 | `PWDEBUG=1` 可视化调试 | 需要额外配置 |
| 社区 | 较新但增长快 | 成熟，文档和教程多 |
| 推荐 | 新项目首选 | 已有项目可继续用 |

**结论**：新项目用 Playwright，已有 Selenium 代码不需要迁移。

### 4.3 代码示例：用 Playwright 自动下载 Business Report

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
headless=False, # 设为 True 可无头运行，但更容易被检测
slow_mo=500 # 每步操作间隔 500ms，模拟人类操作
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

print(f" 报告已下载: {dest}")
return dest

finally:
browser.close()

# 使用示例
# filepath = download_business_report(
# email="your_email@example.com",
# password="your_password",
# download_dir="data/raw/business_reports"
# )
```

> **重要提醒**：
> 1. 浏览器自动化登录 Seller Central 可能违反 Amazon 的服务条款，请谨慎使用
> 2. 频繁自动登录可能触发账号安全验证
> 3. 优先使用 SP-API 获取数据，浏览器自动化只作为最后手段
> 4. 密码不要硬编码，使用环境变量或密钥管理工具

---

## 5. 数据存储与查询

### 5.1 文件存储 vs 数据库

| 方案 | 数据量 | 查询速度 | 适合场景 | 学习成本 |
|------|--------|----------|----------|----------|
| CSV/Excel | <100MB | 慢（全量加载） | 小规模、临时分析 | 零 |
| Parquet | <1GB | 快（列式存储） | 中规模、重复查询 | 低 |
| DuckDB | 100MB-10GB | 很快（OLAP 引擎） | 中规模、复杂查询 | 低 |
| SQLite | <1GB | 中等 | 需要事务的场景 | 低 |
| PostgreSQL | >1GB | 快 | 大规模、多用户 | 中 |

**推荐路径**：
- 刚开始：CSV/Excel（你已经在用了）
- 数据量增长到 50MB+：切换到 Parquet 格式（读写快 5-10 倍）
- 需要复杂查询（JOIN、窗口函数）：引入 DuckDB
- 多人协作或需要 Web 应用：PostgreSQL

### 5.2 DuckDB 快速入门

DuckDB 是近年来最受关注的嵌入式分析数据库。它的杀手级特性：**直接查询 CSV/Parquet 文件，无需导入**。

```python
import duckdb

# 直接查询 CSV 文件 不需要先用 pandas 读取！
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

print(result.fetchdf()) # 返回 pandas DataFrame
```

**DuckDB 的优势场景：**

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

# 场景 2: 窗口函数 计算每个 ASIN 的销量排名
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
print(" 库存不足 30 天的 ASIN:")
print(result.fetchdf())
```

> **DuckDB vs pandas 性能对比**：对于 100MB+ 的 CSV 文件，DuckDB 的查询速度通常是 pandas 的 10-100 倍。原因：DuckDB 使用列式存储和向量化执行，而 pandas 需要把整个文件加载到内存。
>
> 参考：[DuckDB 官方文档](https://duckdb.org/) | [DuckDB vs pandas 基准测试](https://duckdb.org/2021/05/14/sql-on-pandas.html)

---

## 6. 数据可视化与报告

### 6.1 matplotlib/seaborn 基础图表

对于快速的数据探索和分析，matplotlib 和 seaborn 是最直接的选择：

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

### 6.2 Streamlit 快速仪表盘

Streamlit 可以用几十行代码搭建一个交互式数据看板。非常适合内部团队使用：

```python
# dashboard.py 运行: streamlit run dashboard.py
import streamlit as st
import pandas as pd
import duckdb

st.set_page_config(page_title=" 电商数据看板", layout="wide")
st.title(" 电商数据看板 | E-Commerce Dashboard")

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

st.sidebar.success(f" 已加载 {len(df)} 行数据")

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
st.subheader(" 数据明细")
st.dataframe(df, use_container_width=True)

# DuckDB 自定义查询
st.subheader(" 自定义 SQL 查询")
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
st.info(" 请在左侧上传 Business Report 文件")
```

> **Streamlit 的优势**：零前端代码、自动刷新、内置图表组件、一键部署到 [Streamlit Cloud](https://streamlit.io/cloud)（免费）。非常适合给团队做内部数据看板。

### 6.3 HTML 报告生成（自包含，可直接分享）

对于需要通过邮件或 IM 分享的报告，自包含 HTML 是最佳格式。使用 Chart.js 从 CDN 加载，无需任何构建步骤：

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
<h1> {title}</h1>

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

print(f" HTML 报告已生成: {output_path}")
return output_path
```

> **为什么用自包含 HTML？** 一个 .html 文件就是完整的报告，可以通过邮件、Slack、微信直接发送。接收者双击打开即可查看，不需要安装任何软件。Chart.js 从 CDN 加载，文件本身只有几 KB。
---
---

## 7. 实战项目：构建完整的数据管道

### 7.1 项目架构

把前面学到的所有技能整合成一个完整的项目：

```
data-pipeline/
config.json # 配置文件（API 凭证路径、报告目录）
.env # 环境变量（API 密钥，不提交 Git）
.gitignore # 忽略 .env、data/raw/、*.log
requirements.txt # Python 依赖

extract/ # 数据采集层
__init__.py
sp_api_client.py # SP-API 数据采集（订单、库存）
report_downloader.py # 浏览器自动化下载报告
file_watcher.py # 监控文件夹，自动处理新报告

transform/ # 数据清洗和转换层
__init__.py
cleaners.py # 通用清洗函数（编码、数值、日期）
business_report.py # Business Report 专用清洗
advertising.py # 广告报告专用清洗
metrics.py # 指标计算（GMS、ASP、CR）

load/ # 数据存储层
__init__.py
file_store.py # CSV/Parquet 文件存储
duckdb_store.py # DuckDB 查询接口

report/ # 报告生成层
__init__.py
html_report.py # HTML 报告生成
excel_report.py # Excel 报告生成
templates/ # HTML 模板
weekly.html

data/ # 数据目录（不提交 Git）
raw/ # 原始数据（按日期组织）
20250120/
processed/ # 清洗后的数据

output/ # 输出报告
weekly/

schedule.py # 定时任务入口
run_pipeline.py # 手动执行入口
README.md # 项目说明
```

### 7.2 从零搭建的步骤

**Step 1: 初始化项目**

```bash
mkdir data-pipeline && cd data-pipeline
python3 -m venv venv
source venv/bin/activate # macOS/Linux

# 创建目录结构
mkdir -p extract transform load report/templates data/raw data/processed output

# 安装依赖
pip install pandas openpyxl duckdb python-amazon-sp-api \
python-dotenv schedule playwright requests
pip freeze > requirements.txt

# 初始化 Playwright 浏览器
playwright install chromium
```

**Step 2: 配置文件**

```python
# config.py 统一配置管理
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

**Step 3: 主 pipeline 脚本**

```python
# run_pipeline.py 手动执行完整 pipeline
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

print(f" Pipeline 启动: {date_str}, 市场: {markets}")

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
print(f" 找到 {market} 报告: {found[0].name}")

if not report_files:
print(" 未找到报告文件，尝试通过 SP-API 获取...")
# 这里可以调用 SP-API 采集逻辑
return

# === Transform ===
merged = merge_reports(report_files)
print(f" 合并完成: {len(merged)} 行")

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

print(f"\n Pipeline 完成!")
print(f" 处理数据: {processed_dir / 'merged.parquet'}")
print(f" 输出报告: {output_path}")

if __name__ == "__main__":
parser = argparse.ArgumentParser(description="数据管道")
parser.add_argument("--date", help="数据日期 YYYYMMDD")
parser.add_argument("--markets", nargs="+", help="市场列表")
args = parser.parse_args()

run(date_str=args.date, markets=args.markets)
```

```bash
# 运行示例
python3 run_pipeline.py # 处理今天的数据
python3 run_pipeline.py --date 20250120 # 处理指定日期
python3 run_pipeline.py --markets US DE # 只处理 US 和 DE
```

### 7.3 常见问题和调试技巧

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| 编码错误 | `UnicodeDecodeError` | 检查 market 参数是否正确，JP 用 `cp932` |
| SP-API 认证失败 | `401 Unauthorized` | 检查 refresh_token 是否过期，重新授权 |
| SP-API 限流 | `429 Too Many Requests` | 加 `time.sleep(1)` 或用指数退避 |
| 报告格式变化 | `KeyError: 'Units Ordered'` | 打印 `df.columns` 检查列名，更新映射 |
| Playwright 超时 | `TimeoutError` | 增加 `timeout` 参数，检查网络连接 |
| DuckDB 类型错误 | `Conversion Error` | 用 `TRY_CAST` 替代 `CAST`，或先清洗数据 |
| 内存不足 | `MemoryError` | 用 DuckDB 替代 pandas，或分批处理 |
| cron 不执行 | 日志无输出 | 检查 Python 路径（用绝对路径），检查权限 |

**调试技巧：**

```python
# 1. 快速检查 DataFrame 结构
def inspect(df: pd.DataFrame, name: str = "df"):
"""快速检查 DataFrame 的结构和数据质量"""
print(f"\n{'='*50}")
print(f" {name}: {df.shape[0]} 行 × {df.shape[1]} 列")
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

## 8. 学习资源

### 8.1 免费课程与教程

| 资源 | 平台 | 时长 | 适合谁 | 链接 |
|------|------|------|--------|------|
| Kaggle: Pandas Course | Kaggle | 4h | pandas 零基础 | [kaggle.com/learn/pandas](https://www.kaggle.com/learn/pandas) |
| Automate the Boring Stuff | 在线书 | 自学 | Python 自动化入门 | [automatetheboringstuff.com](https://automatetheboringstuff.com/) |
| SP-API 官方文档 | Amazon | 自学 | 需要用 SP-API 的开发者 | [developer-docs.amazon.com/sp-api](https://developer-docs.amazon.com/sp-api) |
| DuckDB 官方文档 | DuckDB | 自学 | 想用 SQL 查询本地文件 | [duckdb.org](https://duckdb.org/) |
| Playwright Python 文档 | Microsoft | 自学 | 浏览器自动化 | [playwright.dev/python](https://playwright.dev/python/) |
| pandas 官方文档 | pandas | 自学 | 进阶用法参考 | [pandas.pydata.org](https://pandas.pydata.org/) |

### 8.2 YouTube 频道推荐

| 频道 | 内容方向 | 为什么推荐 |
|------|----------|-----------|
| Corey Schafer | Python 基础 + pandas | 讲解清晰，适合入门，pandas 系列是经典 |
| sentdex | Python 数据分析 | 实战项目多，从数据采集到可视化全覆盖 |
| Rob Mulla | pandas + 数据科学 | 专注 pandas 技巧，短视频高效学习 |
| ArjanCodes | Python 工程实践 | 代码架构、设计模式，适合写出更好的 pipeline |

Content rephrased for compliance with licensing restrictions. Sources cited inline.

### 8.3 推荐 GitHub 仓库

| 仓库 | Star | 用途 |
|------|------|------|
| [python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api) | 1k+ | SP-API Python 封装，本模块核心依赖 |
| [awesome-pandas](https://github.com/tommyod/awesome-pandas) | 500+ | pandas 学习资源汇总 |
| [DuckDB](https://github.com/duckdb/duckdb) | 20k+ | 嵌入式分析数据库源码 |
| [Playwright Python](https://github.com/microsoft/playwright-python) | 10k+ | 浏览器自动化框架 |

---

## 9. 用 OpenClaw 自动化数据管道

### 9.1 场景：AI Agent 自动采集和处理 Amazon 报告

```
你对 OpenClaw 说：
"每天早上 8 点，从 Seller Central 下载昨天的 Business Report 和 Advertising Report，
合并到 Google Sheet 'Daily Dashboard'，如果有异常指标（销量下降 >20%、ACOS 上升 >10%），
发 Slack 告警到 #daily-ops"

OpenClaw 自动执行：
1. [Heartbeat] 每天 8:00 触发
2. [Skill: web-search / fetch MCP] 获取报告数据
3. [LLM + pandas] 数据清洗和合并
4. [Skill: google-sheets] 写入 Dashboard
5. [LLM] 检测异常指标
6. [Skill: slack] 异常时发送告警
```

### 9.2 需要的 Skills 和 MCP Server

| 组件 | 用途 | 链接 |
|------|------|------|
| **google-sheets** Skill | 读写数据报表 | [ClawHub](https://clawhub.ai/) |
| **slack** Skill | 异常告警通知 | [ClawHub](https://clawhub.ai/) |
| **memory** Skill | 存储历史基线数据 | [OpenClaw Docs](https://docs.openclaw.com/) |
| **filesystem MCP** | 读写本地 CSV/Excel | [MCP Filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) |
| **fetch MCP** | 调用 SP-API 等外部接口 | [MCP Fetch](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) |
| **sqlite MCP** | 本地数据库存储 | [MCP SQLite](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite) |

### 9.3 相关资源

| 资源 | 说明 | 链接 |
|------|------|------|
| OpenClaw 官方文档 | 安装和配置指南 | [docs.openclaw.com](https://docs.openclaw.com/) |
| ClawHub Skills 市场 | 搜索和安装 Agent Skills | [clawhub.ai](https://clawhub.ai/) |
| OpenClaw MCP 集成 | 连接 MCP Server | [Build Skill with MCP](https://rebeccamdeprey.com/blog/build-openclaw-skill-with-mcp) |
| F4 自动化与 Agent | Agent 基础模块 | [F4 模块](../0-foundations/f4-agent-automation.md) |

Content rephrased for compliance with licensing restrictions. Sources cited inline.

---

## 10. 完成标志

- [ ] 写一个脚本自动读取和清洗 Amazon Business Report（处理编码、数值、日期问题）
- [ ] 写一个脚本自动合并多个市场的报告并正确计算 ASP 和 CR（从基础指标重算）
- [ ] 用 SP-API 获取至少一种数据（订单或库存）
- [ ] 用 DuckDB 对 CSV 文件执行至少一次 SQL 查询
- [ ] 生成一份自包含的 HTML 周报（含 Chart.js 图表）
- [ ] 搭建一个完整的 pipeline 项目结构（extract → transform → load → report）

完成以上所有项目后，你已经掌握了电商数据管道的核心技能。接下来进入 [B2 预测模型](b2-prediction-models.md)，学习如何用 Prophet 做销量预测。

---

## 附录：代码速查表

### pandas 常用操作

```python
# 读取
df = pd.read_csv("file.csv", encoding="utf-8-sig")
df = pd.read_excel("file.xlsx", engine="openpyxl")

# 清洗
df["col"] = df["col"].str.replace(",", "").astype(float) # 去逗号转数值
df["date"] = pd.to_datetime(df["date"]) # 转日期
df = df.dropna(subset=["ASIN"]) # 删除空行
df = df[df["Units"] >= 0] # 过滤负数

# 聚合（正确计算比率指标）
summary = df.groupby("Market").agg(
units=("Units Ordered", "sum"),
gms=("GMS", "sum"),
sessions=("Sessions", "sum")
).reset_index()
summary["ASP"] = summary["gms"] / summary["units"] # 重算 ASP
summary["CR"] = summary["units"] / summary["sessions"] # 重算 CR

# 导出
df.to_csv("output.csv", index=False)
df.to_excel("output.xlsx", index=False)
df.to_parquet("output.parquet", index=False) # 推荐！
```

### SP-API 常用端点

| 端点 | 用途 | python-amazon-sp-api 类 |
|------|------|------------------------|
| Orders API | 获取订单列表和详情 | `sp_api.api.Orders` |
| Catalog Items API | 获取产品信息 | `sp_api.api.CatalogItems` |
| FBA Inventory API | 获取 FBA 库存 | `sp_api.api.Inventories` |
| Reports API | 请求和下载报告 | `sp_api.api.Reports` |
| Product Pricing API | 获取产品定价 | `sp_api.api.ProductPricing` |
| Notifications API | 订阅事件通知 | `sp_api.api.Notifications` |

完整 API 参考：[SP-API 文档](https://developer-docs.amazon.com/sp-api) | [python-amazon-sp-api 文档](https://python-amazon-sp-api.readthedocs.io/)

### DuckDB 常用查询

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

### 数据清洗 Checklist

在处理任何 Amazon 报告之前，检查以下项目：

- [ ] 文件编码正确（US/EU: utf-8-sig, JP: cp932）
- [ ] 列名已统一（处理多语言列名差异）
- [ ] 数值列已去除逗号和货币符号
- [ ] 日期列已转换为 datetime 类型
- [ ] 已过滤汇总行（Total/合計）和空行
- [ ] 负数和零值已处理（过滤或标记）
- [ ] 比率指标从基础指标重算（不直接 sum/avg）
- [ ] 已添加市场标识列（Market）
- [ ] 数据质量检查通过（缺失值、重复行、异常值）

---
> [Hub 首页](../../README.md) · [Path B 总览](README.md)
>
> **Path B**: [B1 数据](b1-data-pipeline.md) · [B2 预测](b2-prediction-models.md) · [B3 RAG](b3-rag-knowledge-base.md) · [B4 Agent](b4-agent-workflow.md) · [B5 部署](b5-local-model-deploy.md)
>
> **快速跳转**: [Path 0 基础](../0-foundations/) · [Path A 运营](../a-operators/) · [Path C 管理](../c-managers/) · [Path D 多平台](../d-platforms/) · [Path E 社交媒体](../e-social-media/)

<!-- nav:prev-next -->

---

[Path 总览](README.md) | [B2 预测 >](b2-prediction-models.md)
