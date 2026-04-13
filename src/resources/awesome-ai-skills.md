# Awesome AI Skills & Rules | AI IDE 技能文件与规则集合

> AI IDE（Kiro/Cursor/Windsurf/Claude Code）和 AI Agent（OpenClaw）的 Skills、Steering Files、Rules 集合。
> 让 AI 按照你的规范工作，不再每次重复解释。
> 最后更新: 2026-03-15


---

## 目录

- [什么是 AI Skills / Rules](#什么是-ai-skills--rules)
- [外部 Awesome Lists 和资源](#外部-awesome-lists-和资源)
- [OpenClaw Skills & Plugins](#openclaw-skills--plugins)
- [Kiro Skills & Steering Files](#kiro-skills--steering-files)
- [Cursor Rules](#cursor-rules)
- [Claude Code SKILL.md](#claude-code-skillmd)
- [电商开发推荐 Skills](#电商开发推荐-skills)

---

## 什么是 AI Skills / Rules

AI Skills（技能文件）是给 AI 助手的持久化指令。写一次，AI 自动遵循，不用每次聊天都重复。

| 平台 | 文件名 | 位置 | 说明 |
|------|--------|------|------|
| Kiro | `*.md` | `.kiro/skills/` 或 `.kiro/steering/` | Steering files 持久化项目规范 |
| Cursor | `.cursorrules` 或 `.mdc` | 项目根目录 | 自定义 AI 代码生成规则 |
| Claude Code | `SKILL.md` | 项目根目录 | 可复用的 AI 编码指令 |
| OpenClaw | Skills（JS/TS 模块） | `skills/` 目录 | AI Agent 的可执行技能 |
| Windsurf | `.windsurfrules` | 项目根目录 | 类似 Cursor Rules |

---

## 外部 Awesome Lists 和资源

### Cursor Rules 集合

| 名称 | Stars | 说明 | 链接 |
|------|-------|------|------|
| awesome-cursorrules (PatrickJS) | 23.6K | 最大的 Cursor Rules 集合，按语言/框架分类 | [GitHub](https://github.com/PatrickJS/awesome-cursorrules) |
| awesome-cursor-rules (blefnk) | 热门 | 前端开发优化（Next.js/React/TypeScript/Tailwind） | [GitHub](https://github.com/blefnk/awesome-cursor-rules) |
| awesome-cursor-rules-mdc (sanjeed5) | 精选 | .mdc 格式的 Cursor Rules 集合 | [GitHub](https://github.com/sanjeed5/awesome-cursor-rules-mdc) |
| Cursor-Rules (UltraInstinct0x) | 实用 | 专注于生成可执行代码的规则 | [GitHub](https://github.com/UltraInstinct0x/Cursor-Rules) |

### 目录网站

| 网站 | 说明 | 链接 |
|------|------|------|
| ExtMC | 可搜索的 Cursor Rules 目录，按框架/技术栈筛选 | [extmc.com](https://extmc.com/) |
| PromptGenius | AI Rules 跨 IDE 指南（Cursor/Windsurf/Copilot） | [promptgenius.net](https://promptgenius.net/cursorrules) |
| GitHub Topics: cursorrules | GitHub 上所有 cursorrules 相关项目 | [GitHub Topics](https://github.com/topics/cursorrules) |

### 深度指南

| 文章 | 来源 | 说明 |
|------|------|------|
| How To Write Rules for AI Coding Tools | VirtusLab | AI 规则编写最佳实践 |
| How to Develop SKILL.md for AI Coding Agents | MTechZilla | SKILL.md 生产级指南 |
| How to Guide AI With Rules and Tests | freeCodeCamp | 用规则和测试引导 AI |
| Beyond the Vibes: A Rigorous Guide | tedivm | AI 编码助手严谨使用指南 |

Sources: [VirtusLab](https://virtuslab.com/blog/ai/how-to-write-rules-for-ai/), [MTechZilla](https://www.mtechzilla.com/guides/how-to-develop-skill-md-production-guide-engineering-teams), [freeCodeCamp](https://www.freecodecamp.org/news/how-to-guide-ai-with-rules-and-tests/), [tedivm](https://blog.tedivm.com/guides/2026/03/beyond-the-vibes-coding-assistants-and-agents/).

Content rephrased for compliance with licensing restrictions.

---

## OpenClaw Skills & Plugins

OpenClaw 是 2026 年最热门的开源 AI Agent 框架（180K+ GitHub Stars），其 Skills 系统是核心竞争力。Skills 就像 npm 包安装即用，不需要从零编写（[Tencent Cloud](https://www.tencentcloud.com/techpedia/140807)）。

Content rephrased for compliance with licensing restrictions.

### OpenClaw 核心概念

| 概念 | 说明 |
|------|------|
| Gateway | 本地运行的 AI 网关，连接消息平台和 AI 模型 |
| Skills | 可执行的技能模块（类似 npm 包），定义 Agent 能做什么 |
| Plugins | 扩展插件，连接外部服务（消息平台/API/工具） |
| Channels | 消息渠道（WhatsApp/Telegram/Discord/Slack/iMessage） |

### OpenClaw 官方 Skills 生态

> OpenClaw 拥有 50+ 官方集成，是其核心竞争优势之一（[ApiYi](https://help.apiyi.com/en/openclaw-extensions-ecosystem-guide-en.html)）。

Content rephrased for compliance with licensing restrictions.

| 类别 | Skills | 说明 |
|------|--------|------|
| 消息渠道 | WhatsApp, Telegram, Discord, Slack, Signal, iMessage, Google Chat, Teams | 多平台消息收发 |
| 浏览器 | Browser Relay, Screen Capture | 网页浏览、截图、自动化 |
| 文件系统 | File Manager, Code Executor | 文件读写、代码执行 |
| 日历/邮件 | Google Calendar, Gmail, Outlook | 日程管理、邮件处理 |
| 开发工具 | GitHub, Git, Terminal | 代码管理、命令执行 |
| 数据分析 | CSV/Excel Parser, Web Scraper | 数据处理和抓取 |
| AI 模型 | Claude, GPT-4, DeepSeek, Gemini, Ollama | 多模型支持 |

### OpenClaw 电商应用场景

```
OpenClaw 电商自动化示例：

1. WhatsApp 客服 Agent
安装 WhatsApp Channel Plugin
配置客服 Skill（产品FAQ/退换货/物流查询）
连接 Shopify MCP（查询订单状态）
7×24 自动回复，复杂问题转人工

2. 多平台价格监控
安装 Web Scraper Skill
定时抓取竞品价格
AI 分析价格变化
通过 Telegram 推送告警

3. 每日运营报告
安装 CSV Parser + Gmail Skill
自动下载 Amazon 报告
AI 分析关键指标
通过 Slack 发送日报
```

### OpenClaw 资源

| 资源 | 说明 | 链接 |
|------|------|------|
| OpenClaw GitHub | 主仓库（180K+ Stars） | [GitHub](https://github.com/nicepkg/openclaw) |
| 官方文档 | 安装和配置指南 | [openclaw.dev](https://openclaw.dev/) |
| Skills 市场 | 预构建 Skills 浏览 | 内置于 OpenClaw CLI |
| 安装指南 | 一键安装：`npm install -g openclaw@latest` | [AIFreeAPI](https://www.aifreeapi.com/en/posts/openclaw-installation-guide) |
| 完整教程 | 从零到个人 AI 助手 | [DigitalApplied](https://www.digitalapplied.com/blog/openclaw-ai-complete-guide-setup-skills-automation) |

---

## Kiro Skills & Steering Files

Kiro 使用 Steering Files 提供持久化的项目知识（[Kiro Docs](https://aws.amazon.com/documentation-overview/kiro/)）。

| 类型 | 位置 | 触发方式 | 用途 |
|------|------|---------|------|
| Always-on | `.kiro/steering/*.md` | 每次对话自动加载 | 项目规范、编码标准 |
| File-match | `.kiro/steering/*.md` + frontmatter | 读取匹配文件时加载 | 特定文件类型的规则 |
| Manual | `.kiro/steering/*.md` + `inclusion: manual` | 用 `#` 手动引用 | 按需加载的参考文档 |
| Skills | `.kiro/skills/*.md` | 按需激活 | 可复用的任务指令 |

### 电商项目 Steering 示例

本项目（CBEC-AI-Hub）使用的 Steering Files：

| 文件 | 用途 |
|------|------|
| `product.md` | 项目背景（Amazon Account Manager、跨境电商） |
| `structure.md` | 项目结构（文件组织、命名规范） |
| `tech.md` | 技术栈（Python/TypeScript/Chart.js） |

---

## Cursor Rules

Cursor Rules 定义 AI 代码生成的自定义规则（[PatrickJS](https://github.com/PatrickJS/awesome-cursorrules)）。

### 电商开发推荐 Rules

| Rule | 适合 | 来源 |
|------|------|------|
| Python Projects Guide | Python 电商脚本开发 | [PatrickJS](https://github.com/PatrickJS/awesome-cursorrules/blob/main/rules/python-projects-guide-cursorrules-prompt-file/.cursorrules) |
| Python Flask JSON | Flask API 开发 | [PatrickJS](https://github.com/PatrickJS/awesome-cursorrules/blob/main/rules/python-flask-json-guide-cursorrules-prompt-file/.cursorrules) |
| React TypeScript shadcn/ui | Shopify 前端/Dashboard | [PatrickJS](https://github.com/PatrickJS/awesome-cursorrules/blob/main/rules/cursor-ai-react-typescript-shadcn-ui-cursorrules-p/.cursorrules) |
| Security Rules | AI 安全编码 | [GitHub Topics](https://github.com/topics/cursorrules) |

---

## Claude Code SKILL.md

SKILL.md 是给 Claude Code、Roo Code、OpenAI Codex、Cursor 等 AI 编码 Agent 的结构化指令文件。写一次，Agent 自动读取并应用（[MTechZilla](https://www.mtechzilla.com/guides/how-to-develop-skill-md-production-guide-engineering-teams)）。

Content rephrased for compliance with licensing restrictions.

### SKILL.md 结构

```markdown
# Skill Name

## Context
项目背景和技术栈

## Instructions
具体的编码规则和约束

## Examples
好的代码示例 vs 不好的代码示例

## Constraints
必须遵守的限制（安全/性能/风格）
```

---

## 电商开发推荐 Skills

### 按角色推荐

| 角色 | 推荐工具 | 推荐 Skills/Rules |
|------|---------|-------------------|
| 运营（非技术） | OpenClaw | WhatsApp 客服 Skill + Web Scraper + 报告生成 |
| Python 开发 | Kiro + Claude Code | Steering Files（tech.md）+ SKILL.md（Python 规范） |
| 前端开发 | Cursor | React/TypeScript Rules + Shopify Liquid Rules |
| 全栈 | Kiro | Steering + MCP 配置 + Skills |
| 自动化 | OpenClaw + n8n | OpenClaw Skills + n8n MCP |

### 快速开始

```bash
# OpenClaw：一键安装 AI 助手
npm install -g openclaw@latest
openclaw onboard

# Kiro：创建 Steering Files
mkdir -p .kiro/steering
echo "# 项目规范\n你的编码规则..." > .kiro/steering/rules.md

# Cursor：创建 Rules
echo "你是一个 Python 电商开发专家..." > .cursorrules
```

---

