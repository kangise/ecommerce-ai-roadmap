[🇨🇳 中文](../../paths/0-foundations/f5-rpa-automation.md) | 🇺🇸 English

# F5. RPA & No-Code Automation in Practice

> **Path**: Path 0: AI Foundations · **Module**: F5
> **Last Updated**: 2026-03-14
> **Difficulty**: Intermediate
> **Estimated Time**: 23 hours
> **Prerequisites**: [F4 Automation & Agents](f4-agent-automation.md)

[Hub Home](../../README.md) · [Path 0 Overview](README.md)

---

## Chapter Navigation

1. [RPA vs Workflow Automation vs AI Agent](#1-rpa-vs-workflow-automation-vs-ai-agent)
2. [No-Code Automation Tool Landscape](#2-no-code-automation-tool-landscape)
3. [n8n Deep Dive](#3-n8n-deep-dive)
4. [Zapier / Make in Practice](#4-zapier--make-in-practice)
5. [Top 10 Cross-Border E-Commerce Automation Workflows](#5-top-10-cross-border-e-commerce-automation-workflows)
6. [RPA Tools & Browser Automation](#6-rpa-tools--browser-automation)
7. [AI + Automation Integration](#7-ai--automation-integration)
8. [Tool Selection Decision Framework](#8-tool-selection-decision-framework)
9. [Completion Checklist](#9-completion-checklist)

---

## What You'll Learn in This Module

F4 covered automation concepts and Agent theory. This module focuses on hands-on practice building real automation workflows with specific tools.

After completing this module, you'll be able to:
- Distinguish the right use cases for RPA, workflow automation, and AI Agents
- Build cross-border e-commerce automation workflows with n8n (free, self-hosted)
- Quickly set up simple automations with Zapier/Make (paid, zero-code)
- Understand browser RPA tools like Defy, Bardeen, and Browse AI
- Build 10 core cross-border e-commerce automation scenarios
- Integrate AI (ChatGPT/Claude API) into automation workflows

> **How this differs from F4**: F4 covered "what AI Agents can do" (conceptual level). This module covers "which tools to use and how to build" (hands-on level). F4 is theory-focused; F5 is practice-focused.

---

## 1. RPA vs Workflow Automation vs AI Agent

### 1.1 Fundamental Differences Between Three Types of Automation

| Dimension | RPA (Robotic Process Automation) | Workflow Automation | AI Agent |
|-----------|--------------------------------|-------------------|----------|
| Core Logic | Simulates human actions (clicking, typing, copying) | Connects systems via APIs | AI makes autonomous decisions + executes |
| Typical Tools | UiPath, Automation Anywhere, Defy, Bardeen | n8n, Zapier, Make | LangGraph, CrewAI, OpenClaw |
| Code Required? | No (record actions) | No (drag-and-drop) | Yes (Python) |
| Flexibility | Low (fixed processes) | Medium (conditional branching) | High (autonomous decisions) |
| Stability | Low (breaks when UI changes) | High (APIs are stable) | Medium (AI can make mistakes) |
| Cost | LowMedium | LowHigh (usage-based pricing) | High (API call costs) |
| Best For | Systems without APIs (Seller Central backend operations) | Connecting systems that have APIs | Complex tasks requiring judgment and decisions |

### 1.2 How Cross-Border E-Commerce Sellers Should Choose

```
你的自动化需求是什么？

需要操作没有 API 的网页后台？（Seller Central、QuickSight）
→ RPA（Defy、Bardeen、Browse AI）

需要连接多个有 API 的系统？（Shopify→Google Sheets→Slack）
→ 工作流自动化（n8n、Zapier、Make）

需要 AI 判断和决策？（分析数据后自动调整策略）
→ AI Agent（LangGraph + 工作流工具）

预算有限，想免费？
→ n8n（自托管免费）+ Defy（免费版）

不想折腾，愿意付费？
→ Zapier（最简单）或 Make（性价比高）
```

---

## 2. No-Code Automation Tool Landscape

### 2.1 Tool Comparison

| Tool | Type | Price | Integrations | Self-Hosted | AI Integration | Best For |
|------|------|-------|-------------|-------------|---------------|----------|
| **n8n** | Workflow | Free (self-hosted) / $20/mo (cloud) | 400+ | | (AI Agent nodes) | Technical sellers who need full control |
| **Zapier** | Workflow | Free (100 tasks/mo) / from $20/mo | 7000+ | | (AI steps) | Non-technical sellers, quick setup |
| **Make** | Workflow | Free (1000 ops/mo) / from $9/mo | 1500+ | | | Best value, complex workflows |
| **Defy** | Browser RPA | Free tier available | Browser actions | | | Web backend automation |
| **Bardeen** | Browser RPA | Free tier / $10/mo | Browser + API | | | Data scraping + automation |
| **Browse AI** | Web Scraping | Free (50 runs/mo) / $49/mo | Web scraping | | | Competitor monitoring, price scraping |
| **Power Automate** | Workflow + RPA | From $15/mo | Microsoft ecosystem | | (Copilot) | Teams already using Microsoft 365 |

### 2.2 Cross-Border E-Commerce Scenario Mapping

| Scenario | Best Tool | Reason |
|----------|----------|--------|
| Seller Central report downloads | Defy / Bardeen | No API available, requires browser simulation |
| Multi-platform inventory sync | n8n / Make | Needs to connect multiple APIs |
| New negative review alerts | Zapier | Simplest option, set up in 5 minutes |
| Competitor price monitoring | Browse AI + n8n | Scrape + process + notify |
| Ad report auto-analysis | n8n + OpenAI API | Download → AI analysis → generate report |
| Social media content scheduling | Zapier / Make | Connect Meta/YouTube APIs |
| Order → Shipping → Notification | n8n / Zapier | Standard workflow |
| Multi-language Listing batch generation | n8n + OpenAI API | Batch AI translation calls |
| Review monitoring + sentiment analysis | n8n + OpenAI API | Scrape → AI analysis → classify → notify |
| Monthly operations report generation | n8n + Google Sheets | Aggregate data → generate charts → send email |

---

## 3. n8n Deep Dive

### 3.1 Why We Recommend n8n

n8n is the most worthwhile automation tool for cross-border e-commerce sellers to learn:

- **Free self-hosting**: One-click Docker deployment, data stays entirely in your hands
- **Native AI integration**: Built-in AI Agent nodes that directly call OpenAI/Claude APIs
- **400+ integrations**: Shopify, Google Sheets, Slack, Telegram, HTTP Request, and more
- **Visual editor**: Drag-and-drop, no coding required
- **Active community**: Tons of ready-made workflow templates you can import directly

### 3.2 Installing n8n (5 Minutes)

```bash
# Docker 一键安装（推荐）
docker run -it --rm \
--name n8n \
-p 5678:5678 \
-v n8n_data:/home/node/.n8n \
docker.n8n.io/n8nio/n8n

# 打开浏览器访问 http://localhost:5678
```

Or use n8n Cloud (free 14-day trial): https://n8n.io

### 3.3 E-Commerce Workflow: Review Monitoring + AI Analysis

```
工作流结构：

[Schedule Trigger] 每小时执行一次
↓
[HTTP Request] 抓取 Amazon 产品页面的最新 Review
↓
[IF] Review 评分 ≤ 3 星？
是 →
[OpenAI] 分析差评内容，提取痛点和情感
↓
[Google Sheets] 记录到差评追踪表
↓
[Slack/Telegram] 通知运营团队
↓
[OpenAI] 生成回复草稿

否 →
[Google Sheets] 记录到好评统计表
```

### 3.4 E-Commerce Workflow: Multi-Platform Inventory Sync

```
工作流结构（基于 n8n）：

[Webhook] Shopify 订单创建触发
↓
[Shopify] 获取订单详情（SKU、数量）
↓
[Code] 计算新库存数量
↓
[并行执行]
[Amazon SP-API] 更新 Amazon 库存
[Walmart API] 更新 Walmart 库存
[Google Sheets] 更新库存追踪表
[Slack] 通知团队库存变化
```

### 3.5 E-Commerce Workflow: Ad Report AI Analysis

```
工作流结构：

[Schedule Trigger] 每周一早上 9 点
↓
[Amazon SP-API] 下载过去 7 天的搜索词报告
↓
[Code] 数据清洗和格式化
↓
[OpenAI] 分析报告，生成优化建议
↓
[Google Docs] 生成周报文档
↓
[Gmail] 发送给团队
```

> **Related Reading**: [A3 Advertising Optimization](../a-operators/a3-advertising.md#31-search-term-report-analysis) Methodology for search term report analysis, which can serve as a Prompt template for AI analysis.

---

## 4. Zapier / Make in Practice

### 4.1 Zapier: The Simplest Automation

Zapier is perfect for sellers who don't want to tinker set up an automation in 5 minutes:

**Example: New Negative Review Slack Notification**

```
触发器（Trigger）：Amazon Seller Central → New Review（需要第三方集成）
↓
过滤器（Filter）：评分 ≤ 3 星
↓
动作（Action）：Slack → 发送消息到 #reviews 频道
↓
动作（Action）：Google Sheets → 添加一行到差评追踪表
```

**Popular Zapier Zaps for E-Commerce:**

| Zap | Trigger | Action | Purpose |
|-----|---------|--------|---------|
| New order notification | Shopify new order | Slack message | Real-time order monitoring |
| Inventory alert | Google Sheets inventory < threshold | Email notification | Prevent stockouts |
| New review logging | Third-party review tool | Google Sheets entry | Review tracking |
| Social media scheduling | Google Sheets content calendar | Buffer/Later publish | Auto-publish content |
| Customer feedback collection | Typeform submission | Notion database | Customer insights |

### 4.2 Make (formerly Integromat): Best Value

Make is cheaper than Zapier and supports more complex workflows (branching, loops, error handling):

**Make vs Zapier Comparison:**

| Dimension | Zapier | Make |
|-----------|--------|------|
| Free tier | 100 tasks/mo | 1000 ops/mo |
| Paid starting at | $20/mo | $9/mo |
| Complex workflows | Mostly linear | Supports branching/loops/parallel |
| Visualization | Simple list | Canvas-style drag-and-drop (more intuitive) |
| Learning curve | Very low | Low |
| Integrations | 7000+ | 1500+ |
| Best for | Simple automations | Complex workflows |

---

## 5. Top 10 Cross-Border E-Commerce Automation Workflows

### Automation Priority Ranked by ROI

| Priority | Workflow | Time Saved | Recommended Tool | Difficulty |
|----------|----------|-----------|-----------------|------------|
| 1 | Real-time negative review alerts | 2 hrs/week | Zapier | |
| 2 | Low inventory warnings | 3 hrs/week | Zapier / n8n | |
| 3 | Competitor price monitoring | 5 hrs/week | Browse AI + n8n | |
| 4 | Ad report auto-download + analysis | 4 hrs/week | n8n + OpenAI | |
| 5 | Multi-platform inventory sync | 3 hrs/week | n8n | |
| 6 | Social media content auto-scheduling | 5 hrs/week | Zapier / Make | |
| 7 | Customer service auto-reply (FAQs) | 10 hrs/week | n8n + OpenAI | |
| 8 | Monthly operations report generation | 8 hrs/month | n8n + Google Sheets | |
| 9 | Multi-language Listing batch generation | 10 hrs/batch | n8n + OpenAI | |
| 10 | Review sentiment analysis + trend tracking | 5 hrs/week | n8n + OpenAI | |

> **Total**: If fully implemented, you can save 40+ hours per week. Start with priorities 13 for the smallest investment and fastest returns.

---

## 6. RPA Tools & Browser Automation

### 6.1 Why You Need RPA

Many e-commerce backends don't have APIs (or have limited API functionality):
- Many Amazon Seller Central features have no corresponding SP-API
- QuickSight reports can only be downloaded manually
- Platform backend operations (bulk price changes, image uploads, etc.)

This is where RPA comes in simulating human actions in the browser.

### 6.2 Defy

Defy is a browser RPA tool that records and replays browser actions:

| Feature | Description |
|---------|-------------|
| Record actions | Record your browser actions like screen recording |
| Replay execution | Automatically repeat recorded actions |
| Data extraction | Extract data from web pages into spreadsheets |
| Scheduled execution | Set up scheduled tasks to run automatically |
| AI-assisted | Uses AI to understand page structure for better stability |

**E-Commerce Use Cases:**
- Bulk download Seller Central reports
- Bulk modify product prices
- Bulk upload product images
- Competitor page data scraping

### 6.3 Bardeen

Bardeen is another browser automation tool, more focused on data scraping and workflows:

| Feature | Description |
|---------|-------------|
| Web scraping | Extract structured data from any web page |
| Workflows | Connect browser actions with APIs |
| AI integration | Built-in AI to process scraped data |
| Template library | Large collection of ready-made automation templates |

**E-Commerce Use Cases:**
- Scrape competitor review data
- Scrape competitor prices and inventory status
- Auto-fill product information across platforms
- LinkedIn influencer data scraping (for influencer partnerships)

### 6.4 Browse AI

Browse AI specializes in web data scraping and monitoring:

| Feature | Description |
|---------|-------------|
| No-code scraping | Click to select the data you want to scrape |
| Scheduled monitoring | Periodically scrape and compare changes |
| Change notifications | Automatic alerts when data changes |
| API output | Scraping results available via API |

**E-Commerce Use Cases:**
- Competitor price monitoring (daily scraping, alerts on price changes)
- Competitor new product monitoring (detect newly listed products)
- BSR ranking tracking
- Review count and rating tracking

---

## 7. AI + Automation Integration

### 7.1 The Role of AI in Automation Workflows

```
传统自动化：触发 → 固定流程 → 输出
AI 增强自动化：触发 → AI 分析/判断 → 动态流程 → 输出

示例：Review 监控工作流

传统版：
新 Review → 评分 ≤ 3？→ 通知团队

AI 增强版：
新 Review → AI 分析情感和主题 →
产品质量问题 → 通知产品团队 + 生成改进建议
物流问题 → 通知物流团队 + 检查 FBA 库存
使用方法问题 → 生成 FAQ 更新建议
恶意差评 → 标记 + 生成申诉草稿
```

### 7.2 n8n AI Agent Nodes Explained

n8n has a complete built-in AI node system that lets you call AI directly within workflows:

```
n8n AI 节点类型：

1. OpenAI Chat Model 调用 GPT-4/GPT-4o
用途：文本生成、分析、翻译
配置：API Key + Model + Temperature
电商用法：Listing 生成、Review 分析、客服回复

2. AI Agent 让 AI 自主决策下一步操作
用途：复杂任务的自主执行
配置：System Prompt + Tools + Memory
电商用法：自动分析数据并决定优化方向

3. AI Chain 多步 AI 处理链
用途：需要多步 AI 处理的任务
配置：多个 AI 节点串联
电商用法：Review → 翻译 → 分析 → 生成报告

4. AI Memory 给 AI 添加记忆
用途：跨次调用保持上下文
配置：Buffer Memory / Vector Store Memory
电商用法：客服 Chatbot 记住之前的对话

5. AI Tool 让 AI 调用外部工具
用途：AI 决定何时调用什么工具
配置：定义可用工具列表
电商用法：AI 决定是否需要查询库存、发送通知等
```

### 7.3 Hands-On: Building a Smart Review Analysis System with n8n + OpenAI

This is a complete, deployment-ready workflow:

```
工作流详细设计：

节点 1: Schedule Trigger
频率：每 2 小时执行一次
配置：Cron Expression: 0 */2 * * *

节点 2: HTTP Request（获取 Review 数据）
方法：GET
URL：你的 Review 数据源（SP-API 或第三方工具 API）
认证：Bearer Token
输出：JSON 格式的 Review 列表

节点 3: IF（过滤新 Review）
条件：Review 日期 > 上次检查时间
输出：只保留新 Review

节点 4: Loop Over Items（逐条处理）

节点 5: OpenAI Chat Model（AI 分析）
Model：gpt-4o-mini（成本低，速度快）
System Prompt：
"你是一个电商 Review 分析专家。分析以下 Review 并输出 JSON：
{
"sentiment": "positive/neutral/negative",
"category": "product_quality/shipping/usage/price/other",
"key_issue": "一句话总结核心问题",
"severity": 1-5,
"suggested_reply": "建议的回复草稿",
"action_needed": "none/monitor/respond/escalate"
}"
User Message：{{$json.review_text}}
Temperature：0.3（低温度，输出更稳定）

节点 6: Switch（根据 AI 分析结果分流）
action_needed == "escalate" → 节点 7a
action_needed == "respond" → 节点 7b
action_needed == "monitor" → 节点 7c
action_needed == "none" → 节点 7d

节点 7a: Slack（紧急通知）
Channel：#urgent-reviews
Message： 紧急差评需要处理
产品：{{product_name}}
评分：{{rating}} 星
问题：{{key_issue}}
建议回复：{{suggested_reply}}
Mention：@运营负责人

节点 7b: Google Sheets（记录+生成回复）
添加到"待回复"Sheet
包含 AI 生成的回复草稿

节点 7c: Google Sheets（记录到监控表）

节点 7d: Google Sheets（记录到好评统计表）

节点 8: 汇总统计
本次新增 Review 数量
正面/中性/负面比例
需要处理的数量
发送日报到 Slack/Email
```

**Cost Estimate**:
- n8n self-hosted: $0 (Docker)
- OpenAI API: ~$0.01/review (gpt-4o-mini)
- 50 reviews/day: ~$0.50/day = ~$15/month
- Time saved: ~10 hrs/week × $25/hr = $250/week

### 7.4 Hands-On: Multi-Language Listing Batch Generation Workflow

```
工作流设计：

节点 1: Google Sheets Trigger
监控"待翻译"Sheet
新行添加时触发

节点 2: 获取产品信息
从 Sheet 读取：英文标题、Bullet Points、描述、关键词
目标语言列表：[日语, 德语, 西班牙语, 法语, 意大利语]

节点 3: Loop Over Languages

节点 4: OpenAI Chat Model（翻译+本地化）
System Prompt：
"你是一个 Amazon Listing 本地化专家。
不是直译，是本地化：
- 使用目标市场消费者的搜索习惯
- 适配当地的度量单位
- 调整文化表达方式
- 保持 SEO 关键词密度
目标语言：{{target_language}}"
User Message：{{product_info}}
Temperature：0.5

节点 5: Google Sheets（写入翻译结果）
每种语言一列
标注翻译状态

节点 6: Slack 通知
"产品 {{product_name}} 的 5 种语言 Listing 已生成，请人工审核"
```

### 7.5 Amazon BSA AI Agent Compliance Requirements (March 2026 Update)

> **Important**: Starting March 4, 2026, Amazon updated its BSA (Business Solutions Agreement) with formal requirements for AI Agents and automation tools ([PPC Land](https://ppc.land/amazons-new-ai-agent-rules-shake-up-sellers-before-march-4-deadline/)).

**New Requirements**:
- AI Agents must clearly identify themselves as automated systems at all times
- Must continuously comply with Amazon's Agent Policy
- Must immediately stop access when Amazon requests it
- Third-party tool developers are also subject to these rules

**Impact on Automation Workflows**:
- Using RPA tools to operate Seller Central requires extra caution
- Automation via SP-API is unaffected (the API itself is authorized)
- Browser automation (Defy/Bardeen) operating Seller Central may violate the policy
- Recommendation: Prioritize SP-API; avoid directly simulating browser actions on Seller Central

Content rephrased for compliance with licensing restrictions.

---

### 7.6 Detailed Implementation Plans for 10 E-Commerce Automation Workflows

#### Workflow 1: Real-Time Negative Review Alerts (5-Minute Setup)

```
工具：Zapier（最简单）
触发：第三方 Review 监控工具（如 FeedbackWhiz）→ 新 Review
过滤：评分 ≤ 3 星
动作 1：Slack 发送消息（含 Review 内容+产品链接）
动作 2：Google Sheets 添加一行
预估节省：2 小时/周
```

#### Workflow 2: Low Inventory Warnings (10-Minute Setup)

```
工具：n8n 或 Zapier
触发：Schedule（每天早上 9 点）
步骤 1：SP-API 获取库存数据
步骤 2：Code 节点计算：当前库存 / 日均销量 = 可售天数
步骤 3：IF 可售天数 < 14 天
步骤 4：Slack/Email 通知 + Google Sheets 记录
预估节省：3 小时/周
```

#### Workflow 3: Competitor Price Monitoring (30-Minute Setup)

```
工具：Browse AI + n8n
步骤 1：Browse AI 每天抓取 5 个竞品的价格
步骤 2：n8n Webhook 接收 Browse AI 数据
步骤 3：Code 节点对比昨天的价格
步骤 4：IF 价格变化 > 5%
步骤 5：Slack 通知 + Google Sheets 记录价格历史
步骤 6：（可选）OpenAI 分析价格趋势并建议调价策略
预估节省：5 小时/周
```

#### Workflow 4: Ad Report Auto-Download + AI Analysis (1-Hour Setup)

```
工具：n8n + OpenAI API
触发：Schedule（每周一早上 9 点）
步骤 1：SP-API 下载过去 7 天的搜索词报告
步骤 2：Code 节点数据清洗（去重、格式化、计算 ROAS/ACOS）
步骤 3：OpenAI 分析报告
Prompt："分析以下搜索词数据，找出：
1. 高 ROAS 词（应提高出价）
2. 浪费词（应否定）
3. 新发现的长尾机会
4. 预算重新分配建议"
步骤 4：Google Docs 生成周报
步骤 5：Gmail 发送给团队
预估节省：4 小时/周
```

#### Workflow 5: Social Media Content Auto-Scheduling (20-Minute Setup)

```
工具：Zapier 或 Make
触发：Google Sheets 新行（内容日历）
步骤 1：读取内容（文案+图片链接+发布时间+平台）
步骤 2：Switch 按平台分流
Instagram → Later/Buffer API
Facebook → Meta API
TikTok → 手动（API 限制）
Pinterest → Pinterest API
步骤 3：确认发布成功 → 更新 Sheet 状态
预估节省：5 小时/周
```

#### Workflows 610: Summary

| # | Workflow | Tool | Core Logic | Time Saved |
|---|---------|------|-----------|-----------|
| 6 | Multi-platform inventory sync | n8n | Shopify Webhook → Update Amazon/Walmart inventory | 3 hrs/week |
| 7 | Customer service auto-reply | n8n + OpenAI | New message → AI classify → auto-reply/escalate to human | 10 hrs/week |
| 8 | Monthly report generation | n8n + Google Sheets | Aggregate platform data → AI analysis → PDF report | 8 hrs/month |
| 9 | Multi-language Listing generation | n8n + OpenAI | English Listing → AI translate to 5 languages → human review | 10 hrs/batch |
| 10 | Review sentiment trends | n8n + OpenAI | Daily reviews → AI analysis → trend charts → weekly report | 5 hrs/week |

---

## 8. Tool Selection Decision Framework

```
你是一个跨境电商自动化顾问。

我的情况：
- 团队规模：[X] 人
- 技术能力：[无代码/会用 Excel/会写 Python]
- 月预算（自动化工具）：$[X]
- 主要平台：[Amazon/Shopify/Walmart/...]
- 最想自动化的 3 个任务：[列出]

请推荐：
1. 最适合我的自动化工具组合
2. 每个工具的具体用途
3. 实施优先级（先做什么）
4. 预估每周节省的时间
5. 第一个月的行动计划
```

---

## 9. Completion Checklist

- [ ] Understand the differences and use cases for RPA, workflow automation, and AI Agents
- [ ] Install and run n8n (Docker or Cloud)
- [ ] Build at least 1 automation workflow (recommended: negative review alerts)
- [ ] Try integrating AI into a workflow (OpenAI API)
- [ ] Create your automation priority list

> **Next Steps**: If you want to dive deeper into building AI Agent systems, head to [Path B: B4 AI Agent & Automation](../b-developers/b4-agent-workflow.md). If you'd rather master existing tools first, go back to [Path A](../a-operators/) to apply AI to specific operations scenarios.

---
> [Hub Home](../../README.md) · [Path 0 Overview](README.md) · [AI Landscape Assessment](ai-landscape.md)
>
> **Path 0**: [F1 AI Evolution](f1-ai-evolution.md) · [F2 Prompt Engineering](f2-prompt-engineering.md) · [F3 RAG Knowledge Base](f3-rag-knowledge.md) · [F4 Agent Automation](f4-agent-automation.md) · [F5 RPA Automation](f5-rpa-automation.md) · [AI Landscape](ai-landscape.md)
>
> **Quick Jump**: [Path A Operations](../a-operators/) · [Path B Technical](../b-developers/) · [Path C Management](../c-managers/) · [Path D Multi-Platform](../d-platforms/) · [Path E Social Media](../e-social-media/)
