# B6. MCP 集成与 Agentic 电商工作流

> **路径**: Path B: 技术人 · **模块**: B6
> **最后更新**: 2026-03-15
> **难度**: 高级
> **预计时间**: 每天 1 小时，2-3 周
> **前置模块**: [B4 AI Agent 与自动化](b4-agent-workflow.md)

[Hub 首页](../../README.md) · [Path B 总览](README.md)

---

## 章节导航

1. [MCP 是什么](#1-mcp-是什么) · 2. [电商 MCP 生态](#2-电商-mcp-生态) · 3. [Amazon Ads MCP Server](#3-amazon-ads-mcp-server) · 4. [Shopify MCP 集成](#4-shopify-mcp-集成) · 5. [构建自定义 MCP Server](#5-构建自定义-mcp-server) · 6. [Agentic 工作流实战](#6-agentic-工作流实战) · 7. [安全与权限](#7-安全与权限) · 8. [完成标志](#8-完成标志)

---

## 本模块你将构建

- 一个连接 Amazon Ads 的 MCP 工作流（用 Claude 对话管理广告）
- 一个连接 Shopify 的 MCP 工作流（用 AI 管理产品和订单）
- 一个自定义 MCP Server（连接你自己的数据源）
- 理解 Agentic Commerce 的技术架构

> **核心理念**：MCP（Model Context Protocol）是 AI 的"USB-C 接口"一个通用标准，让 AI 模型安全地连接到外部工具和数据。2026 年 2 月 Amazon 正式发布了 Ads MCP Server，Shopify 也推出了官方 MCP 支持。这意味着你可以用自然语言对话来管理广告、产品、订单。

---

## 1. MCP 是什么

### 1.1 MCP 核心概念

MCP（Model Context Protocol）是 Anthropic 开发的开放标准，定义了 AI 模型如何连接外部工具和数据（[Badger Blue](https://badger.blue/blogs/ecommerce-unpacked/model-context-protocol-mcp-ecommerce)）。

Content rephrased for compliance with licensing restrictions.

```
MCP 架构：

AI 模型（Claude/ChatGPT/Gemini）
MCP 协议（标准化接口）
MCP Server（数据/工具提供者）
API
外部系统（Amazon Ads / Shopify / 数据库 / 文件系统）

类比：
USB-C 是硬件的通用接口
MCP 是 AI 的通用接口
不需要为每个 AI 模型写不同的集成代码
一个 MCP Server 可以被所有支持 MCP 的 AI 客户端使用
```

### 1.2 MCP vs 传统 API 集成

| 维度 | 传统 API 集成 | MCP |
|------|-------------|-----|
| 开发方式 | 为每个 AI 模型写定制代码 | 一次开发，所有 AI 模型通用 |
| 交互方式 | 代码调用 API | 自然语言对话 |
| 上下文 | 需要手动传递 | AI 自动理解上下文 |
| 安全性 | 各自实现 | 标准化权限模型 |
| 适合谁 | 开发者 | 开发者 + 高级运营 |

### 1.3 2026 年 MCP 生态现状

> **真实数据**：Amazon 于 2026 年 2 月 2 日正式发布 Ads MCP Server 开放测试版（[Canopy Management](https://canopymanagement.com/amazon-ads-mcp-server-ai/)）。Google 也开源了自己的 MCP 实现。已有生产级 MCP Server 每月处理超过 $4500 万的广告支出，覆盖 10,000+ 企业（[HyperFX](https://www.hyperfx.ai/blog/meta-ads-mcp-guide-ai-advertising-agents)）。74% 的中小企业已在积极测试或部署 AI 广告工具（[Stormy.ai](https://stormy.ai/blog/automating-amazon-ads-claude-mcp)）。

Content rephrased for compliance with licensing restrictions.

---

## 2. 电商 MCP 生态

> **完整工具集**: [ Awesome MCP & Agent 工具集](../../docs/awesome-mcp-agents.md) 电商 MCP Server、Agent 框架、外部资源的完整列表

### 2.1 已有的电商 MCP Server

| MCP Server | 平台 | 功能 | 状态 |
|-----------|------|------|------|
| Amazon Ads MCP | Amazon Advertising | SP/SB/SD 广告管理、报告、优化 | 官方开放测试（2026.2） |
| Shopify Storefront MCP | Shopify | 产品、购物车、客户、订单 | 官方支持（[shopify.dev](https://shopify.dev/docs/apps/build/storefront-mcp)） |
| Shopify Dev MCP | Shopify 开发 | 搜索文档、API Schema、构建 Functions | 官方支持（[shopify.dev](https://shopify.dev/docs/apps/build/devmcp)） |
| Meta Ads MCP | Meta/Facebook/Instagram | 广告管理、受众、报告 | 第三方（HyperFX 等） |
| Google Ads MCP | Google Ads | Campaign 管理、关键词、报告 | 第三方 |
| shopify-mcp（开源） | Shopify | 产品/订单/客户管理 | 社区开源（[GitHub](https://github.com/GeLi2001/shopify-mcp)） |

### 2.2 MCP 在电商中的应用场景

| 场景 | 传统方式 | MCP 方式 |
|------|---------|---------|
| 查看广告表现 | 登录 Amazon Ads 后台，导出报告 | "显示过去 7 天 ACOS 最高的 5 个 Campaign" |
| 调整出价 | 手动逐个修改 | "把 ACOS > 40% 的关键词出价降低 20%" |
| 上架新品 | 手动填写 Shopify 后台 | "用这个产品信息在 Shopify 创建新产品" |
| 库存预警 | 定期检查后台 | "哪些产品库存低于 7 天可售量？" |
| 竞品监控 | 手动查看竞品页面 | "对比我的产品和 ASIN B0xxx 的价格和评分" |

---

## 3. Amazon Ads MCP Server

### 3.1 设置 Amazon Ads MCP

```json
// mcp.json 配置示例
{
"mcpServers": {
"amazon-ads": {
"command": "npx",
"args": ["-y", "@anthropic/amazon-ads-mcp-server"],
"env": {
"AMAZON_ADS_CLIENT_ID": "your-client-id",
"AMAZON_ADS_CLIENT_SECRET": "your-client-secret",
"AMAZON_ADS_REFRESH_TOKEN": "your-refresh-token",
"AMAZON_ADS_PROFILE_ID": "your-profile-id"
}
}
}
}
```

> **注意**：需要先在 Amazon Advertising API 注册应用并获取凭证。详见 [Amazon Ads API 文档](https://advertising.amazon.com/API/docs/en-us)。

### 3.2 Amazon Ads MCP 可用工具

Amazon Ads MCP Server 提供了完整的广告管理能力。根据 MarketplaceAdPros 的实现（[Playbooks.com](https://playbooks.com/mcp/marketplaceadpros-amazon-ads)），可用工具包括：

| 工具类别 | 工具名 | 功能 | 示例对话 |
|----------|--------|------|---------|
| Campaign 管理 | list_campaigns | 获取 Campaign 列表 | "列出所有活跃的 SP Campaign" |
| | create_campaign | 创建新 Campaign | "创建一个新的 SP Auto Campaign，日预算 $50" |
| | update_campaign | 更新 Campaign 设置 | "把 Campaign X 的日预算从 $50 调到 $80" |
| 广告组 | list_ad_groups | 获取广告组 | "显示 Campaign X 下的所有广告组" |
| | create_ad_group | 创建广告组 | "在 Campaign X 下创建一个新广告组" |
| 关键词 | list_keywords | 获取关键词列表 | "哪些关键词的 ACOS > 30%？" |
| | update_bid | 调整出价 | "把关键词 X 的出价从 $1.5 调到 $1.2" |
| | create_negative | 添加否定词 | "把 'free' 添加为 Campaign 级否定词" |
| 搜索词 | get_search_terms | 搜索词报告 | "过去 30 天转化率最高的搜索词" |
| 报告 | generate_report | 生成报告 | "生成过去 7 天的 SP Campaign 报告" |
| | get_performance | 获取表现数据 | "过去 7 天的总花费和 ROAS" |
| Profile | list_profiles | 获取广告账户 | "列出所有可用的广告 Profile" |
| | get_regions | 获取区域信息 | "显示可用的市场区域" |

Content rephrased for compliance with licensing restrictions. Source: [Playbooks.com](https://playbooks.com/mcp/marketplaceadpros-amazon-ads).

> **真实案例：Amazon Ads MCP 2026.2 正式发布**
> 2026 年 2 月 2 日，Amazon 宣布 Ads MCP Server 开放测试版。拥有 API 凭证的卖家可以通过 Claude、ChatGPT 或 Gemini 等工具，用简单的命令创建 Campaign、优化出价、拉取报告、跨市场扩展（[ClearAds Agency](https://clearadsagency.com/what-is-amazons-mcp-server-and-how-does-it-change-advertising-for-sellers/)）。

Content rephrased for compliance with licensing restrictions.

### 3.3 5 大 MCP 广告自动化策略

根据 Stormy.ai 的实战指南（[Stormy.ai](https://stormy.ai/blog/automating-amazon-ads-claude-mcp)），以下是用 Claude MCP 管理 Amazon 广告的 5 个核心策略：

**策略 1：自动搜索词收割（Search Term Harvesting）**

传统方式：手动扫描 Auto Campaign 的搜索词报告，找到高转化词，手动移到 Exact Match Campaign，再手动在原 Campaign 中否定。

MCP 方式：
```
You: "分析过去 14 天 Auto Campaign 的搜索词报告。
找出满足以下条件的搜索词：
- 转化率 > 10%
- 至少 3 次转化
- 当前不在任何 Manual Campaign 中

对于每个符合条件的词：
1. 添加到 Manual Exact Match Campaign
2. 在原 Auto Campaign 中添加为否定精确匹配
3. 设置初始出价为该词在 Auto Campaign 中的平均 CPC 的 120%"

Claude: [调用 get_search_terms → 分析 → create_keyword → create_negative]
→ "已处理 12 个高转化搜索词，添加到 Manual Campaign，并在 Auto 中否定。"
```

**策略 2：浪费性支出自动清理**

```
You: "找出过去 30 天满足以下条件的关键词：
- 花费 > $20
- 0 转化
- 或 ACOS > 100%

列出这些词，并建议：暂停、降低出价 50%、或添加为否定词。"

Claude: [分析数据] → 返回分类建议
You: "执行所有建议"
Claude: [批量执行] → "已暂停 8 个词，降低 15 个词的出价，添加 23 个否定词。预计每月节省 $340。"
```

**策略 3：竞品关键词发现**

```
You: "分析竞品 ASIN B0XXXXXXXX 的广告关键词。
对比我的 Campaign 中已有的关键词。
找出竞品在投但我没有覆盖的关键词。
按预估搜索量排序。"

Claude: [调用多个工具] → 返回关键词差距列表
```

**策略 4：日预算智能分配**

```
You: "分析所有 Campaign 的日预算消耗情况。
哪些 Campaign 在下午 3 点前就花完了预算？（错过了晚间高转化时段）
哪些 Campaign 预算利用率 < 50%？（预算浪费）
建议重新分配预算。"

Claude: [分析] → "Campaign A 每天 2PM 预算耗尽，建议增加 30%。
Campaign B 利用率仅 35%，建议减少 20% 并转移到 Campaign A。"
```

**策略 5：周度自动化报告**

```
You: "生成本周广告优化报告，包含：
1. 总花费/销售/ACOS/ROAS 及 vs 上周变化
2. Top 5 表现最好的关键词
3. Top 5 浪费最多的关键词
4. 本周执行的优化操作汇总
5. 下周建议的优化行动
格式：Markdown，可以直接发给团队"

Claude: [汇总所有数据] → 生成完整报告
```

> **真实数据**：PPC 管理平台的自动化可以每周节省 10+ 小时的手动工作（[Maxmerce](https://www.maxmerce.com/blog/how-to-improve-amazon-ppc-performance-campaign-opt/)）。Amazon PPC ACOS 优化可以在保持或增加销售的同时降低广告成本 30-50%（[Maxmerce](https://www.maxmerce.com/blog/amazon-ppc-acos-optimization-reduce-costs-boost-ro/)）。

Content rephrased for compliance with licensing restrictions.

### 3.3 实战：用 Claude 对话管理 Amazon 广告

```
实战场景：周度广告优化

Step 1: 获取概览
You: "显示过去 7 天所有 SP Campaign 的表现，按 ACOS 从高到低排序"
Claude: [调用 get_campaigns + get_performance] → 返回表格

Step 2: 识别问题
You: "哪些 Campaign 的 ACOS > 目标 ACOS 25%？"
Claude: [分析数据] → 标注问题 Campaign

Step 3: 深入分析
You: "Campaign X 中哪些关键词在浪费预算？（花费 > $10 但 0 转化）"
Claude: [调用 get_keywords + get_search_terms] → 返回浪费词列表

Step 4: 执行优化
You: "把这些浪费词添加为否定词，并把 ACOS < 15% 的词出价提高 10%"
Claude: [调用 create_negative + update_bid] → 执行并确认

Step 5: 生成报告
You: "生成本周广告优化报告，包含执行的操作和预期影响"
Claude: [汇总] → 生成 Markdown 报告
```

> **真实案例**：Stormy.ai 展示了使用 Claude MCP 管理 Amazon 广告的 5 个策略，可以降低 ACOS 并每年节省 30 天工作时间（[Stormy.ai](https://stormy.ai/blog/automating-amazon-ads-claude-mcp)）。

Content rephrased for compliance with licensing restrictions.

---

## 4. Shopify MCP 集成

### 4.1 Shopify MCP 生态全景

Shopify 的 MCP 生态在 2026 年已经非常成熟，包含官方和社区两个层面：

**官方 MCP Server**（[Shopify Dev](https://shopify.dev/docs/apps/build/storefront-mcp)）：

| Server | 用途 | 能力 |
|--------|------|------|
| Storefront MCP | 面向买家的购物体验 | 产品浏览、购物车、结账、客户信息 |
| Dev MCP | 面向开发者 | 搜索文档、API Schema、构建 Functions |

**社区 MCP Server**：

| Server | 作者 | 功能 | 来源 |
|--------|------|------|------|
| shopify-mcp | GeLi2001 | 产品/客户/订单管理（GraphQL） | [GitHub](https://github.com/GeLi2001/shopify-mcp) |
| @cloud9-labs/mcp-shopify | Cloud9 Labs | 产品/订单/客户/库存/集合管理 | [LobeHub](https://lobehub.com/mcp/cloud9-labs-mcp-shopify) |
| shopify-mcp-server | Ajackus | Claude Desktop 集成 | [LobeHub](https://lobehub.com/mcp/ajackus-shopify-mcp-server) |
| shopify-storefront-mcp | QuentinCody | Storefront API 非官方实现 | [Hexmos](https://hexmos.com/freedevtools/mcp/other-tools-and-integrations/QuentinCody--shopify-storefront-mcp-server/) |

Content rephrased for compliance with licensing restrictions.

> **真实案例：Shopify MCP 成为 Agentic Commerce 的基础设施**
> Shopify 的 MCP 生态被描述为"Agentic Commerce 的技术连接组织"它允许 LLM（如 ChatGPT、Perplexity 或自定义 Agent）以机器和平台都能理解的语言"询问"你的店铺关于产品、库存和客户偏好的问题（[WeArePresta](https://wearepresta.com/shopify-mcp-server-the-standardized-interface-for-agentic-commerce-2026/)）。Shopify 官方 Storefront MCP Server 帮助客户通过 AI 代理浏览和购买商品（[Shopify Dev](https://www.shopify.dev/docs/apps/build/storefront-mcp/servers/storefront)）。

Content rephrased for compliance with licensing restrictions.

```
Shopify MCP 架构：

AI 助手（Claude/ChatGPT/自定义 Agent）
MCP 协议
Shopify MCP Server
Shopify Admin API / Storefront API
Shopify 店铺数据
产品（Products）
订单（Orders）
客户（Customers）
库存（Inventory）
购物车（Cart）
折扣（Discounts）
```

### 4.2 Shopify MCP 实战场景

```python
# 示例：用 Python 连接 Shopify MCP Server
# 需要安装：pip install mcp shopify-api

from mcp import ClientSession, StdioServerParameters
import asyncio

async def shopify_mcp_demo():
"""连接 Shopify MCP Server 并查询产品"""
server_params = StdioServerParameters(
command="npx",
args=["-y", "@shopify/storefront-mcp-server"],
env={
"SHOPIFY_STORE_URL": "your-store.myshopify.com",
"SHOPIFY_ACCESS_TOKEN": "your-access-token"
}
)

async with ClientSession(server_params) as session:
# 列出可用工具
tools = await session.list_tools()
print(f"可用工具: {[t.name for t in tools]}")

# 查询低库存产品
result = await session.call_tool(
"get_products",
{"query": "inventory_quantity:<10"}
)
print(f"低库存产品: {result}")

asyncio.run(shopify_mcp_demo())
```

### 4.3 Shopify Agentic Commerce 工作流

```
Shopify Agentic Commerce 完整工作流：

1. AI 购物助手（面向买家）
用户在 ChatGPT 中说 "我想买一个降噪耳机"
ChatGPT 通过 UCP 协议查询 Shopify 产品
返回产品推荐（价格、评分、库存）
用户确认购买
在 ChatGPT 内完成结账（Instant Checkout）

2. AI 运营助手（面向卖家）
卖家对 Claude 说 "今天有哪些订单需要处理？"
Claude 通过 MCP 查询 Shopify 订单
返回待处理订单列表
卖家说 "把这 5 个订单标记为已发货"
Claude 通过 MCP 更新订单状态

3. AI 库存管理（自动化）
Agent 每天自动检查库存水平
低于安全库存时自动发送预警
生成补货建议（基于销售趋势）
卖家确认后自动创建采购订单
```

---

## 5. 构建自定义 MCP Server

### 5.1 MCP Server 开发框架

```python
# 最小可行 MCP Server 示例
# 连接你自己的电商数据源

from mcp.server import Server
from mcp.types import Tool, TextContent
import json

# 创建 MCP Server
server = Server("ecommerce-data")

@server.list_tools()
async def list_tools():
"""定义可用工具"""
return [
Tool(
name="get_daily_sales",
description="获取指定日期范围的销售数据",
inputSchema={
"type": "object",
"properties": {
"start_date": {"type": "string", "description": "开始日期 YYYY-MM-DD"},
"end_date": {"type": "string", "description": "结束日期 YYYY-MM-DD"},
"marketplace": {"type": "string", "description": "市场 US/EU/JP"}
},
"required": ["start_date", "end_date"]
}
),
Tool(
name="get_acos_alerts",
description="获取 ACOS 超标的广告 Campaign",
inputSchema={
"type": "object",
"properties": {
"threshold": {"type": "number", "description": "ACOS 阈值（%）"}
},
"required": ["threshold"]
}
),
Tool(
name="get_inventory_alerts",
description="获取库存预警（低于安全库存的 SKU）",
inputSchema={
"type": "object",
"properties": {
"days_threshold": {"type": "integer", "description": "可售天数阈值"}
}
}
)
]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
"""处理工具调用"""
if name == "get_daily_sales":
# 连接你的数据源（CSV/数据库/API）
sales_data = query_sales_data(
arguments["start_date"],
arguments["end_date"],
arguments.get("marketplace", "US")
)
return [TextContent(type="text", text=json.dumps(sales_data))]

elif name == "get_acos_alerts":
alerts = query_acos_alerts(arguments["threshold"])
return [TextContent(type="text", text=json.dumps(alerts))]

elif name == "get_inventory_alerts":
alerts = query_inventory_alerts(arguments.get("days_threshold", 14))
return [TextContent(type="text", text=json.dumps(alerts))]

# 启动 Server
if __name__ == "__main__":
import asyncio
from mcp.server.stdio import stdio_server
asyncio.run(stdio_server(server))
```

### 5.2 注册到 Claude/Kiro

```json
// .kiro/settings/mcp.json 或 claude_desktop_config.json
{
"mcpServers": {
"my-ecommerce": {
"command": "python3",
"args": ["path/to/my_mcp_server.py"],
"env": {
"DB_CONNECTION": "your-database-url"
}
}
}
}
```

---

## 6. Agentic 工作流实战

### 6.1 多 Agent 协作架构

```
电商 Multi-Agent 系统：


Orchestrator Agent
（协调所有子 Agent，分配任务）



广告 库存 客服
Agent Agent Agent

MCP: MCP: MCP:
Amazon Shopify WhatsApp
Ads Inventory Business


每个 Agent 有自己的 MCP 连接和专业知识
Orchestrator 根据任务类型分配给对应 Agent
```

### 6.2 每日自动化运营 Agent（完整实现）

```python
# daily_ops_agent.py 完整的每日运营自动化 Agent
# 使用 LangGraph + MCP

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Literal
import operator
import json
from datetime import datetime, timedelta

class DailyOpsState(TypedDict):
"""Agent 状态定义"""
sales_data: dict
ad_alerts: list
inventory_alerts: list
review_alerts: list
daily_report: str
actions_taken: Annotated[list, operator.add]
errors: Annotated[list, operator.add]

# === Step 1: 销售数据检查 ===
async def check_sales(state: DailyOpsState) -> DailyOpsState:
"""通过 MCP 获取昨日销售数据"""
try:
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
today = datetime.now().strftime("%Y-%m-%d")

# 调用自定义 MCP Server
sales = await mcp_call("my-ecommerce", "get_daily_sales", {
"start_date": yesterday,
"end_date": today,
"marketplace": "US"
})

# 计算关键指标
prev_week = await mcp_call("my-ecommerce", "get_daily_sales", {
"start_date": (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d"),
"end_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
})

sales_data = {
"date": yesterday,
"revenue": sales["total_revenue"],
"orders": sales["total_orders"],
"units": sales["total_units"],
"wow_change": (sales["total_revenue"] - prev_week["total_revenue"])
/ prev_week["total_revenue"] * 100,
"top_products": sales.get("top_products", [])[:5],
"anomalies": []
}

# 异常检测
if abs(sales_data["wow_change"]) > 30:
sales_data["anomalies"].append(
f"收入周环比变化 {sales_data['wow_change']:+.1f}%（阈值 ±30%）"
)

state["sales_data"] = sales_data
state["actions_taken"] = [f" 获取销售数据: ${sales_data['revenue']:,.0f}"]

except Exception as e:
state["errors"] = [f" 销售数据获取失败: {str(e)}"]

return state

# === Step 2: 广告检查 ===
async def check_ads(state: DailyOpsState) -> DailyOpsState:
"""通过 Amazon Ads MCP 检查广告表现"""
try:
# 获取 ACOS 超标的 Campaign
campaigns = await mcp_call("amazon-ads", "list_campaigns", {
"status": "ENABLED"
})

alerts = []
for campaign in campaigns:
perf = await mcp_call("amazon-ads", "get_performance", {
"campaign_id": campaign["id"],
"days": 7
})

acos = perf["spend"] / max(perf["sales"], 0.01) * 100

if acos > 40:
alerts.append({
"campaign": campaign["name"],
"acos": acos,
"spend": perf["spend"],
"sales": perf["sales"],
"severity": "high" if acos > 60 else "medium"
})

# 检查预算耗尽
if perf.get("budget_utilization", 0) > 95:
alerts.append({
"campaign": campaign["name"],
"issue": "预算在下午前耗尽",
"utilization": perf["budget_utilization"],
"severity": "medium"
})

state["ad_alerts"] = alerts
state["actions_taken"] = [
f" 检查广告: {len(campaigns)} 个 Campaign, {len(alerts)} 个告警"
]

except Exception as e:
state["errors"] = [f" 广告检查失败: {str(e)}"]

return state

# === Step 3: 库存检查 ===
async def check_inventory(state: DailyOpsState) -> DailyOpsState:
"""通过 Shopify/Amazon MCP 检查库存"""
try:
inventory = await mcp_call("shopify", "get_inventory_levels", {})

alerts = []
for item in inventory:
days_of_supply = item["quantity"] / max(item["daily_sales"], 0.1)

if days_of_supply < 14:
alerts.append({
"sku": item["sku"],
"product": item["title"],
"quantity": item["quantity"],
"days_of_supply": round(days_of_supply, 1),
"daily_sales": item["daily_sales"],
"severity": "high" if days_of_supply < 7 else "medium",
"reorder_qty": int(item["daily_sales"] * 45) # 45 天补货量
})

state["inventory_alerts"] = alerts
state["actions_taken"] = [
f" 检查库存: {len(alerts)} 个 SKU 需要补货"
]

except Exception as e:
state["errors"] = [f" 库存检查失败: {str(e)}"]

return state

# === Step 4: Review 检查 ===
async def check_reviews(state: DailyOpsState) -> DailyOpsState:
"""检查新的差评"""
try:
new_reviews = await mcp_call("my-ecommerce", "get_recent_reviews", {
"days": 1,
"max_rating": 3
})

alerts = []
for review in new_reviews:
alerts.append({
"asin": review["asin"],
"rating": review["rating"],
"title": review["title"][:50],
"severity": "high" if review["rating"] <= 2 else "low"
})

state["review_alerts"] = alerts
state["actions_taken"] = [
f" 检查 Review: {len(alerts)} 条新差评"
]

except Exception as e:
state["errors"] = [f" Review 检查失败: {str(e)}"]

return state

# === Step 5: 生成报告 ===
async def generate_report(state: DailyOpsState) -> DailyOpsState:
"""用 LLM 生成每日运营报告"""

report_data = {
"date": state.get("sales_data", {}).get("date", "N/A"),
"sales": state.get("sales_data", {}),
"ad_alerts": state.get("ad_alerts", []),
"inventory_alerts": state.get("inventory_alerts", []),
"review_alerts": state.get("review_alerts", []),
"actions": state.get("actions_taken", []),
"errors": state.get("errors", [])
}

prompt = f"""
你是一个电商运营 AI 助手。请基于以下数据生成简洁的每日运营报告。

数据：
{json.dumps(report_data, ensure_ascii=False, indent=2)}

报告格式：
# 每日运营报告 - {{date}}

## 销售概览
（收入、订单、环比变化、异常）

## 需要行动的事项（按优先级排序）
（广告告警、库存告警、差评告警）

## 今日建议行动清单
（具体的、可执行的行动，标注优先级 P0/P1/P2）

## 系统状态
（执行的检查、遇到的错误）
"""

report = await llm_call(prompt)
state["daily_report"] = report

return state

# === 决策路由 ===
def should_auto_fix(state: DailyOpsState) -> Literal["auto_fix", "report"]:
"""决定是否自动修复问题"""
high_severity = sum(
1 for a in state.get("ad_alerts", []) if a.get("severity") == "high"
)
if high_severity > 0:
return "auto_fix"
return "report"

# === 自动修复 ===
async def auto_fix_ads(state: DailyOpsState) -> DailyOpsState:
"""自动修复高严重度的广告问题"""
for alert in state.get("ad_alerts", []):
if alert.get("severity") == "high" and alert.get("acos", 0) > 60:
# 自动降低出价 20%（需要人工确认）
state["actions_taken"] = [
f" 建议: Campaign '{alert['campaign']}' ACOS={alert['acos']:.0f}%，"
f"建议降低出价 20%（需要人工确认）"
]
return state

# === 构建工作流 ===
workflow = StateGraph(DailyOpsState)

# 添加节点
workflow.add_node("sales", check_sales)
workflow.add_node("ads", check_ads)
workflow.add_node("inventory", check_inventory)
workflow.add_node("reviews", check_reviews)
workflow.add_node("auto_fix", auto_fix_ads)
workflow.add_node("report", generate_report)

# 定义流程
workflow.set_entry_point("sales")
workflow.add_edge("sales", "ads")
workflow.add_edge("ads", "inventory")
workflow.add_edge("inventory", "reviews")
workflow.add_conditional_edges("reviews", should_auto_fix)
workflow.add_edge("auto_fix", "report")
workflow.add_edge("report", END)

# 编译
app = workflow.compile()

# === 运行 ===
async def run_daily_ops():
"""每天早上 8 点运行"""
initial_state = {
"sales_data": {},
"ad_alerts": [],
"inventory_alerts": [],
"review_alerts": [],
"daily_report": "",
"actions_taken": [],
"errors": []
}

result = await app.ainvoke(initial_state)

# 输出报告
print(result["daily_report"])

# 发送到 Slack/邮件
# await send_to_slack(result["daily_report"])

return result

if __name__ == "__main__":
import asyncio
asyncio.run(run_daily_ops())
```

### 6.3 定时调度

```python
# 使用 APScheduler 定时运行
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# 每天早上 8:00 运行每日报告
scheduler.add_job(run_daily_ops, 'cron', hour=8, minute=0)

# 每 4 小时检查一次广告异常
scheduler.add_job(check_ads_only, 'interval', hours=4)

# 每小时检查库存
scheduler.add_job(check_inventory_only, 'interval', hours=1)

scheduler.start()
```

---

## 7. 安全与权限

### 7.1 MCP 安全最佳实践

| 原则 | 说明 | 实现 |
|------|------|------|
| 最小权限 | 只授予 MCP Server 必要的 API 权限 | 使用只读 Token（除非需要写入） |
| 人工确认 | 写操作（修改出价/创建订单）需要人工确认 | 在 Agent 中设置确认节点 |
| 审计日志 | 记录所有 MCP 调用 | 日志文件 + 定期审查 |
| Token 轮换 | 定期更换 API Token | 每 90 天轮换 |
| 环境隔离 | 测试环境和生产环境分离 | 不同的 MCP 配置文件 |

### 7.2 实现审计日志

```python
import logging
from datetime import datetime
from functools import wraps

# 配置审计日志
audit_logger = logging.getLogger("mcp_audit")
audit_logger.setLevel(logging.INFO)
handler = logging.FileHandler("mcp_audit.log")
handler.setFormatter(logging.Formatter(
"%(asctime)s | %(levelname)s | %(message)s"
))
audit_logger.addHandler(handler)

def audit_mcp_call(func):
"""MCP 调用审计装饰器"""
@wraps(func)
async def wrapper(name: str, arguments: dict, *args, **kwargs):
# 记录调用
audit_logger.info(f"CALL | tool={name} | args={arguments}")

try:
result = await func(name, arguments, *args, **kwargs)
audit_logger.info(f"SUCCESS | tool={name} | result_size={len(str(result))}")
return result
except Exception as e:
audit_logger.error(f"ERROR | tool={name} | error={str(e)}")
raise

return wrapper

# 使用
@audit_mcp_call
async def call_tool(name: str, arguments: dict):
# ... MCP 调用逻辑
pass
```

### 7.3 人工确认机制

```python
class HumanInTheLoop:
"""写操作的人工确认机制"""

WRITE_OPERATIONS = {
"update_bid", "create_campaign", "create_negative",
"update_campaign", "delete_keyword",
"create_product", "update_order", "update_inventory"
}

@staticmethod
async def confirm(tool_name: str, arguments: dict) -> bool:
"""检查是否需要人工确认"""
if tool_name not in HumanInTheLoop.WRITE_OPERATIONS:
return True # 读操作自动通过

print(f"\n 写操作确认请求:")
print(f" 工具: {tool_name}")
print(f" 参数: {arguments}")

response = input(" 确认执行？(y/n): ").strip().lower()

if response == 'y':
audit_logger.info(f"CONFIRMED | tool={tool_name}")
return True
else:
audit_logger.info(f"REJECTED | tool={tool_name}")
return False
```

### 7.4 常见风险与防范

| 风险 | 说明 | 防范 | 严重度 |
|------|------|------|--------|
| AI 误操作 | AI 错误理解指令，执行了错误操作 | 写操作必须人工确认 | 高 |
| Token 泄露 | API Token 被暴露在代码或日志中 | 使用环境变量，日志脱敏 | 高 |
| 过度授权 | MCP Server 权限过大 | 最小权限原则，定期审查 | 中 |
| 数据泄露 | 敏感数据通过 AI 模型传输 | 使用本地模型处理敏感数据 | 中 |
| 速率限制 | API 调用超过限制 | 实现速率限制和重试逻辑 | 中 |
| 成本失控 | AI 自动执行导致广告预算超支 | 设置预算上限和告警 | 高 |

```python
# 预算安全阀示例
class BudgetSafetyValve:
"""防止 AI 自动操作导致预算超支"""

def __init__(self, max_daily_spend_change: float = 100.0,
max_single_bid_change: float = 2.0):
self.max_daily_spend_change = max_daily_spend_change
self.max_single_bid_change = max_single_bid_change
self.daily_changes = 0.0

def check_bid_change(self, current_bid: float, new_bid: float) -> bool:
"""检查出价变更是否在安全范围内"""
change = abs(new_bid - current_bid)

if change > self.max_single_bid_change:
audit_logger.warning(
f"BID_BLOCKED | change=${change:.2f} > max=${self.max_single_bid_change}"
)
return False

self.daily_changes += change
if self.daily_changes > self.max_daily_spend_change:
audit_logger.warning(
f"DAILY_LIMIT | total_changes=${self.daily_changes:.2f}"
)
return False

return True
```

---

## 8. Meta Ads MCP 与多平台扩展

### 8.1 Meta Ads MCP

> **真实数据**：已有生产级 MCP Server 每月处理超过 $4500 万的广告支出，覆盖 10,000+ 企业。Google 也开源了自己的 MCP 实现（[HyperFX](https://www.hyperfx.ai/blog/meta-ads-mcp-guide-ai-advertising-agents)）。

Content rephrased for compliance with licensing restrictions.

| 平台 MCP | 状态 | 核心能力 |
|----------|------|---------|
| Amazon Ads MCP | 官方开放测试 | SP/SB/SD Campaign 管理 |
| Meta Ads MCP | 第三方成熟 | Campaign/AdSet/Ad 管理、受众、报告 |
| Google Ads MCP | 第三方/官方 | Campaign/关键词/报告 |
| TikTok Ads MCP | 社区开发中 | Campaign 管理 |
| Shopify MCP | 官方支持 | 产品/订单/客户/库存 |

### 8.2 多平台 MCP 统一管理

```python
# 概念代码：多平台广告统一管理
class MultiPlatformAdManager:
"""通过 MCP 统一管理多平台广告"""

def __init__(self):
self.platforms = {
"amazon": AmazonAdsMCP(),
"meta": MetaAdsMCP(),
"google": GoogleAdsMCP()
}

async def get_cross_platform_report(self, days: int = 7) -> dict:
"""跨平台广告报告"""
reports = {}
for name, mcp in self.platforms.items():
reports[name] = await mcp.get_performance(days=days)

# 统一格式
unified = {
"total_spend": sum(r["spend"] for r in reports.values()),
"total_revenue": sum(r["revenue"] for r in reports.values()),
"by_platform": reports,
"overall_roas": sum(r["revenue"] for r in reports.values()) /
sum(r["spend"] for r in reports.values())
}
return unified

async def rebalance_budget(self, total_budget: float):
"""基于 ROAS 自动重新分配跨平台预算"""
report = await self.get_cross_platform_report()

# 按 ROAS 加权分配
total_roas = sum(
r["revenue"] / r["spend"] for r in report["by_platform"].values()
)

for name, r in report["by_platform"].items():
platform_roas = r["revenue"] / r["spend"]
new_budget = total_budget * (platform_roas / total_roas)
await self.platforms[name].update_daily_budget(new_budget)
```

---

## 8. 完成标志

- [ ] 成功配置 Amazon Ads MCP Server 并用 Claude 查询广告数据
- [ ] 成功配置 Shopify MCP Server 并用 AI 管理产品
- [ ] 构建一个自定义 MCP Server（连接你自己的数据源）
- [ ] 实现一个每日自动化运营 Agent（至少包含 2 个 MCP 连接）
- [ ] 建立 MCP 安全最佳实践（权限控制 + 审计日志）

---
> [Hub 首页](../../README.md) · [Path B 总览](README.md)
>
> **Path B**: [B1 数据管道](b1-data-pipeline.md) · [B2 预测模型](b2-prediction-models.md) · [B3 RAG 知识库](b3-rag-knowledge-base.md) · [B4 AI Agent](b4-agent-workflow.md) · [B5 本地模型](b5-local-model-deploy.md) · [B6 MCP 集成](b6-mcp-agentic-workflow.md) · [B7 Review NLP](b7-review-nlp-system.md)
>
> **快速跳转**: [Path 0 基础](../0-foundations/) · [Path A 运营](../a-operators/) · [Path C 管理](../c-managers/) · [Path D 多平台](../d-platforms/) · [Path E 社交媒体](../e-social-media/)
