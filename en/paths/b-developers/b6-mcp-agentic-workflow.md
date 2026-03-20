[🇨🇳 中文](../../paths/b-developers/b6-mcp-agentic-workflow.md) | 🇺🇸 English

# B6. MCP Integration & Agentic E-commerce Workflows

> **Path**: Path B: Developers · **Module**: B6
> **Last Updated**: 2026-03-15
> **Difficulty**: Advanced
> **Estimated Time**: 1 hour/day, 2-3 weeks
> **Prerequisites**: [B4 AI Agent & Automation](b4-agent-workflow.md)

[Hub Home](../../README.md) · [Path B Overview](README.md)

---

## Chapter Navigation

1. [What Is MCP](#1-what-is-mcp) · 2. [E-commerce MCP Ecosystem](#2-e-commerce-mcp-ecosystem) · 3. [Amazon Ads MCP Server](#3-amazon-ads-mcp-server) · 4. [Shopify MCP Integration](#4-shopify-mcp-integration) · 5. [Building Custom MCP Servers](#5-building-custom-mcp-servers) · 6. [Agentic Workflow in Practice](#6-agentic-workflow-in-practice) · 7. [Security & Permissions](#7-security--permissions) · 8. [Completion Checklist](#8-completion-checklist)

---

## What You'll Build in This Module

- An MCP workflow connected to Amazon Ads (manage ads through Claude conversations)
- An MCP workflow connected to Shopify (manage products and orders with AI)
- A custom MCP Server (connected to your own data sources)
- Understanding of the Agentic Commerce technical architecture

> **Core Concept**: MCP (Model Context Protocol) is the "USB-C port" for AI a universal standard that lets AI models securely connect to external tools and data. In February 2026, Amazon officially released the Ads MCP Server, and Shopify also launched official MCP support. This means you can manage ads, products, and orders through natural language conversations.

---

## 1. What Is MCP

### 1.1 MCP Core Concepts

MCP (Model Context Protocol) is an open standard developed by Anthropic that defines how AI models connect to external tools and data ([Badger Blue](https://badger.blue/blogs/ecommerce-unpacked/model-context-protocol-mcp-ecommerce)).

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

### 1.2 MCP vs Traditional API Integration

| Dimension | Traditional API Integration | MCP |
|-----------|---------------------------|-----|
| Development | Write custom code for each AI model | Build once, works with all AI models |
| Interaction | Code-based API calls | Natural language conversations |
| Context | Must be passed manually | AI understands context automatically |
| Security | Each implementation is different | Standardized permission model |
| Target Users | Developers | Developers + advanced operators |

### 1.3 MCP Ecosystem in 2026

> **Real Data**: Amazon officially released the Ads MCP Server open beta on February 2, 2026 ([Canopy Management](https://canopymanagement.com/amazon-ads-mcp-server-ai/)). Google also open-sourced its own MCP implementation. Production-grade MCP Servers already process over $45 million in monthly ad spend, covering 10,000+ businesses ([HyperFX](https://www.hyperfx.ai/blog/meta-ads-mcp-guide-ai-advertising-agents)). 74% of SMBs are actively testing or deploying AI advertising tools ([Stormy.ai](https://stormy.ai/blog/automating-amazon-ads-claude-mcp)).

Content rephrased for compliance with licensing restrictions.

---

## 2. E-commerce MCP Ecosystem

> **Full Toolkit**: [ Awesome MCP & Agent Toolkit](../../docs/awesome-mcp-agents.md#awesome-mcp-servers-ai-agent-tools-awesome-mcp-agent-tools-for-e-commerce) Complete list of e-commerce MCP Servers, Agent frameworks, and external resources

### 2.1 Existing E-commerce MCP Servers

| MCP Server | Platform | Features | Status |
|-----------|----------|----------|--------|
| Amazon Ads MCP | Amazon Advertising | SP/SB/SD ad management, reporting, optimization | Official open beta (2026.2) |
| Shopify Storefront MCP | Shopify | Products, cart, customers, orders | Official support ([shopify.dev](https://shopify.dev/docs/apps/build/storefront-mcp)) |
| Shopify Dev MCP | Shopify Development | Search docs, API Schema, build Functions | Official support ([shopify.dev](https://shopify.dev/docs/apps/build/devmcp)) |
| Meta Ads MCP | Meta/Facebook/Instagram | Ad management, audiences, reporting | Third-party (HyperFX, etc.) |
| Google Ads MCP | Google Ads | Campaign management, keywords, reporting | Third-party |
| shopify-mcp (open source) | Shopify | Product/order/customer management | Community open source ([GitHub](https://github.com/GeLi2001/shopify-mcp)) |

### 2.2 MCP Use Cases in E-commerce

| Scenario | Traditional Approach | MCP Approach |
|----------|---------------------|-------------|
| Check ad performance | Log into Amazon Ads console, export reports | "Show the 5 campaigns with the highest ACOS over the past 7 days" |
| Adjust bids | Manually modify one by one | "Lower bids by 20% for keywords with ACOS > 40%" |
| List a new product | Manually fill in Shopify admin | "Create a new product on Shopify with this product info" |
| Inventory alerts | Periodically check the dashboard | "Which products have less than 7 days of sellable inventory?" |
| Competitor monitoring | Manually check competitor pages | "Compare my product's price and rating with ASIN B0xxx" |

---

## 3. Amazon Ads MCP Server

### 3.1 Setting Up Amazon Ads MCP

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

> **Note**: You need to register an application with the Amazon Advertising API and obtain credentials first. See the [Amazon Ads API Documentation](https://advertising.amazon.com/API/docs/en-us).

### 3.2 Amazon Ads MCP Available Tools

The Amazon Ads MCP Server provides comprehensive ad management capabilities. Based on the MarketplaceAdPros implementation ([Playbooks.com](https://playbooks.com/mcp/marketplaceadpros-amazon-ads)), available tools include:

| Tool Category | Tool Name | Function | Example Conversation |
|--------------|-----------|----------|---------------------|
| Campaign Management | list_campaigns | Get campaign list | "List all active SP Campaigns" |
| | create_campaign | Create new campaign | "Create a new SP Auto Campaign with $50 daily budget" |
| | update_campaign | Update campaign settings | "Change Campaign X's daily budget from $50 to $80" |
| Ad Groups | list_ad_groups | Get ad groups | "Show all ad groups under Campaign X" |
| | create_ad_group | Create ad group | "Create a new ad group under Campaign X" |
| Keywords | list_keywords | Get keyword list | "Which keywords have ACOS > 30%?" |
| | update_bid | Adjust bids | "Change keyword X's bid from $1.5 to $1.2" |
| | create_negative | Add negative keywords | "Add 'free' as a campaign-level negative keyword" |
| Search Terms | get_search_terms | Search term report | "Top converting search terms over the past 30 days" |
| Reports | generate_report | Generate reports | "Generate an SP Campaign report for the past 7 days" |
| | get_performance | Get performance data | "Total spend and ROAS for the past 7 days" |
| Profile | list_profiles | Get ad accounts | "List all available ad Profiles" |
| | get_regions | Get region info | "Show available market regions" |

Content rephrased for compliance with licensing restrictions. Source: [Playbooks.com](https://playbooks.com/mcp/marketplaceadpros-amazon-ads).

> **Real Case: Amazon Ads MCP Official Release in 2026.2**
> On February 2, 2026, Amazon announced the Ads MCP Server open beta. Sellers with API credentials can create campaigns, optimize bids, pull reports, and expand across marketplaces through tools like Claude, ChatGPT, or Gemini using simple commands ([ClearAds Agency](https://clearadsagency.com/what-is-amazons-mcp-server-and-how-does-it-change-advertising-for-sellers/)).

Content rephrased for compliance with licensing restrictions.

### 3.3 5 Key MCP Ad Automation Strategies

Based on Stormy.ai's practical guide ([Stormy.ai](https://stormy.ai/blog/automating-amazon-ads-claude-mcp)), here are 5 core strategies for managing Amazon ads with Claude MCP:

**Strategy 1: Automated Search Term Harvesting**

Traditional approach: Manually scan Auto Campaign search term reports, find high-converting terms, manually move them to Exact Match Campaigns, then manually negate them in the original campaign.

MCP approach:
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

**Strategy 2: Wasteful Spend Auto-Cleanup**

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

**Strategy 3: Competitor Keyword Discovery**

```
You: "分析竞品 ASIN B0XXXXXXXX 的广告关键词。
对比我的 Campaign 中已有的关键词。
找出竞品在投但我没有覆盖的关键词。
按预估搜索量排序。"

Claude: [调用多个工具] → 返回关键词差距列表
```

**Strategy 4: Smart Daily Budget Allocation**

```
You: "分析所有 Campaign 的日预算消耗情况。
哪些 Campaign 在下午 3 点前就花完了预算？（错过了晚间高转化时段）
哪些 Campaign 预算利用率 < 50%？（预算浪费）
建议重新分配预算。"

Claude: [分析] → "Campaign A 每天 2PM 预算耗尽，建议增加 30%。
Campaign B 利用率仅 35%，建议减少 20% 并转移到 Campaign A。"
```

**Strategy 5: Weekly Automated Reports**

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

> **Real Data**: PPC management platform automation can save 10+ hours of manual work per week ([Maxmerce](https://www.maxmerce.com/blog/how-to-improve-amazon-ppc-performance-campaign-opt/)). Amazon PPC ACOS optimization can reduce ad costs by 30-50% while maintaining or increasing sales ([Maxmerce](https://www.maxmerce.com/blog/amazon-ppc-acos-optimization-reduce-costs-boost-ro/)).

Content rephrased for compliance with licensing restrictions.

### 3.3 Hands-On: Managing Amazon Ads Through Claude Conversations

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

> **Real Case**: Stormy.ai demonstrated 5 strategies for managing Amazon ads using Claude MCP, which can lower ACOS and save 30 days of work per year ([Stormy.ai](https://stormy.ai/blog/automating-amazon-ads-claude-mcp)).

Content rephrased for compliance with licensing restrictions.

---

## 4. Shopify MCP Integration

### 4.1 Shopify MCP Ecosystem Overview

Shopify's MCP ecosystem is already quite mature in 2026, spanning both official and community levels:

**Official MCP Servers** ([Shopify Dev](https://shopify.dev/docs/apps/build/storefront-mcp)):

| Server | Purpose | Capabilities |
|--------|---------|-------------|
| Storefront MCP | Buyer-facing shopping experience | Product browsing, cart, checkout, customer info |
| Dev MCP | Developer-facing | Search docs, API Schema, build Functions |

**Community MCP Servers**:

| Server | Author | Features | Source |
|--------|--------|----------|--------|
| shopify-mcp | GeLi2001 | Product/customer/order management (GraphQL) | [GitHub](https://github.com/GeLi2001/shopify-mcp) |
| @cloud9-labs/mcp-shopify | Cloud9 Labs | Product/order/customer/inventory/collection management | [LobeHub](https://lobehub.com/mcp/cloud9-labs-mcp-shopify) |
| shopify-mcp-server | Ajackus | Claude Desktop integration | [LobeHub](https://lobehub.com/mcp/ajackus-shopify-mcp-server) |
| shopify-storefront-mcp | QuentinCody | Unofficial Storefront API implementation | [Hexmos](https://hexmos.com/freedevtools/mcp/other-tools-and-integrations/QuentinCody--shopify-storefront-mcp-server/) |

Content rephrased for compliance with licensing restrictions.

> **Real Case: Shopify MCP as the Foundation for Agentic Commerce**
> Shopify's MCP ecosystem has been described as "the connective tissue for Agentic Commerce" it allows LLMs (like ChatGPT, Perplexity, or custom Agents) to "ask" your store about products, inventory, and customer preferences in a language both machines and platforms understand ([WeArePresta](https://wearepresta.com/shopify-mcp-server-the-standardized-interface-for-agentic-commerce-2026/)). The official Shopify Storefront MCP Server helps customers browse and purchase products through AI agents ([Shopify Dev](https://www.shopify.dev/docs/apps/build/storefront-mcp/servers/storefront)).

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

### 4.2 Shopify MCP Hands-On Scenarios

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

### 4.3 Shopify Agentic Commerce Workflow

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

## 5. Building Custom MCP Servers

### 5.1 MCP Server Development Framework

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

### 5.2 Registering with Claude/Kiro

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

## 6. Agentic Workflow in Practice

### 6.1 Multi-Agent Collaboration Architecture

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

### 6.2 Daily Automated Operations Agent (Full Implementation)

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

### 6.3 Scheduled Execution

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

## 7. Security & Permissions

### 7.1 MCP Security Best Practices

| Principle | Description | Implementation |
|-----------|-------------|---------------|
| Least Privilege | Only grant MCP Servers the minimum required API permissions | Use read-only tokens (unless writes are needed) |
| Human Confirmation | Write operations (modifying bids/creating orders) require human approval | Set up confirmation nodes in the Agent |
| Audit Logging | Log all MCP calls | Log files + periodic review |
| Token Rotation | Regularly rotate API tokens | Rotate every 90 days |
| Environment Isolation | Separate test and production environments | Different MCP config files |

### 7.2 Implementing Audit Logging

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

### 7.3 Human-in-the-Loop Confirmation

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

### 7.4 Common Risks & Mitigation

| Risk | Description | Mitigation | Severity |
|------|-------------|-----------|----------|
| AI Misoperation | AI misinterprets instructions and executes wrong actions | Require human confirmation for write operations | High |
| Token Leakage | API tokens exposed in code or logs | Use environment variables, sanitize logs | High |
| Over-Permissioning | MCP Server has excessive permissions | Least privilege principle, periodic audits | Medium |
| Data Leakage | Sensitive data transmitted through AI models | Use local models for sensitive data | Medium |
| Rate Limiting | API calls exceed limits | Implement rate limiting and retry logic | Medium |
| Cost Overrun | AI automation causes ad budget overspend | Set budget caps and alerts | High |

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

## 8. Meta Ads MCP & Multi-Platform Expansion

### 8.1 Meta Ads MCP

> **Real Data**: Production-grade MCP Servers already process over $45 million in monthly ad spend, covering 10,000+ businesses. Google also open-sourced its own MCP implementation ([HyperFX](https://www.hyperfx.ai/blog/meta-ads-mcp-guide-ai-advertising-agents)).

Content rephrased for compliance with licensing restrictions.

| Platform MCP | Status | Core Capabilities |
|-------------|--------|-------------------|
| Amazon Ads MCP | Official open beta | SP/SB/SD Campaign management |
| Meta Ads MCP | Mature third-party | Campaign/AdSet/Ad management, audiences, reporting |
| Google Ads MCP | Third-party/Official | Campaign/keyword/reporting |
| TikTok Ads MCP | Community development | Campaign management |
| Shopify MCP | Official support | Products/orders/customers/inventory |

### 8.2 Unified Multi-Platform MCP Management

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

## 8. Completion Checklist

- [ ] Successfully configured Amazon Ads MCP Server and queried ad data with Claude
- [ ] Successfully configured Shopify MCP Server and managed products with AI
- [ ] Built a custom MCP Server (connected to your own data source)
- [ ] Implemented a daily automated operations Agent (with at least 2 MCP connections)
- [ ] Established MCP security best practices (permission control + audit logging)

---
> [Hub Home](../../README.md) · [Path B Overview](README.md)
>
> **Path B**: [B1 Data Pipeline](b1-data-pipeline.md) · [B2 Prediction Models](b2-prediction-models.md) · [B3 RAG Knowledge Base](b3-rag-knowledge-base.md) · [B4 AI Agent](b4-agent-workflow.md) · [B5 Local Models](b5-local-model-deploy.md) · [B6 MCP Integration](b6-mcp-agentic-workflow.md) · [B7 Review NLP](b7-review-nlp-system.md)
>
> **Quick Links**: [Path 0 Foundations](../0-foundations/) · [Path A Operators](../a-operators/) · [Path C Managers](../c-managers/) · [Path D Multi-Platform](../d-platforms/) · [Path E Social Media](../e-social-media/)