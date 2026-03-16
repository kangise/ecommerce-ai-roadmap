# 🧠 Awesome AI Skills & Rules | AI IDE Skills and Rule Collections

> Collections of Skills, Steering Files, and Rules for AI IDEs (Kiro/Cursor/Windsurf/Claude Code) and AI Agents (OpenClaw).
> Let AI work according to your standards — no more repeating yourself every time.
> Last updated: 2026-03-15

🏠 [Hub Home](../README.md) · 🔌 [Awesome MCP & Agent](awesome-mcp-agents.md) · 🔧 [B6 MCP Integration](../paths/b-developers/b6-mcp-agentic-workflow.md) · ⚡ [F4 Agent Automation](../paths/0-foundations/f4-agent-automation.md)

---

## 📋 Table of Contents

- [What Are AI Skills / Rules](#-what-are-ai-skills--rules)
- [External Awesome Lists and Resources](#-external-awesome-lists-and-resources)
- [OpenClaw Skills & Plugins](#-openclaw-skills--plugins)
- [Kiro Skills & Steering Files](#-kiro-skills--steering-files)
- [Cursor Rules](#-cursor-rules)
- [Claude Code SKILL.md](#-claude-code-skillmd)
- [Recommended Skills for E-Commerce Development](#-recommended-skills-for-e-commerce-development)

---

## 💡 What Are AI Skills / Rules

AI Skills (skill files) are persistent instructions for AI assistants. Write once, and the AI follows them automatically — no need to repeat yourself in every conversation.

| Platform | File Name | Location | Description |
|----------|-----------|----------|-------------|
| Kiro | `*.md` | `.kiro/skills/` or `.kiro/steering/` | Steering files for persistent project standards |
| Cursor | `.cursorrules` or `.mdc` | Project root | Custom AI code generation rules |
| Claude Code | `SKILL.md` | Project root | Reusable AI coding instructions |
| OpenClaw | Skills (JS/TS modules) | `skills/` directory | Executable skills for AI Agents |
| Windsurf | `.windsurfrules` | Project root | Similar to Cursor Rules |

---

## 🌐 External Awesome Lists and Resources

### Cursor Rules Collections

| Name | Stars | Description | Link |
|------|-------|-------------|------|
| awesome-cursorrules (PatrickJS) | 23.6K ⭐ | Largest Cursor Rules collection, categorized by language/framework | [GitHub](https://github.com/PatrickJS/awesome-cursorrules) |
| awesome-cursor-rules (blefnk) | Popular | Frontend development optimization (Next.js/React/TypeScript/Tailwind) | [GitHub](https://github.com/blefnk/awesome-cursor-rules) |
| awesome-cursor-rules-mdc (sanjeed5) | Curated | .mdc format Cursor Rules collection | [GitHub](https://github.com/sanjeed5/awesome-cursor-rules-mdc) |
| Cursor-Rules (UltraInstinct0x) | Practical | Focused on generating executable code | [GitHub](https://github.com/UltraInstinct0x/Cursor-Rules) |

### Directory Websites

| Website | Description | Link |
|---------|-------------|------|
| ExtMC | Searchable Cursor Rules directory, filterable by framework/tech stack | [extmc.com](https://extmc.com/) |
| PromptGenius | AI Rules cross-IDE guide (Cursor/Windsurf/Copilot) | [promptgenius.net](https://promptgenius.net/cursorrules) |
| GitHub Topics: cursorrules | All cursorrules-related projects on GitHub | [GitHub Topics](https://github.com/topics/cursorrules) |

### In-Depth Guides

| Article | Source | Description |
|---------|--------|-------------|
| How To Write Rules for AI Coding Tools | VirtusLab | Best practices for writing AI rules |
| How to Develop SKILL.md for AI Coding Agents | MTechZilla | Production-grade SKILL.md guide |
| How to Guide AI With Rules and Tests | freeCodeCamp | Guiding AI with rules and tests |
| Beyond the Vibes: A Rigorous Guide | tedivm | Rigorous guide for AI coding assistants |

Sources: [VirtusLab](https://virtuslab.com/blog/ai/how-to-write-rules-for-ai/), [MTechZilla](https://www.mtechzilla.com/guides/how-to-develop-skill-md-production-guide-engineering-teams), [freeCodeCamp](https://www.freecodecamp.org/news/how-to-guide-ai-with-rules-and-tests/), [tedivm](https://blog.tedivm.com/guides/2026/03/beyond-the-vibes-coding-assistants-and-agents/).

Content rephrased for compliance with licensing restrictions.

---

## 🐾 OpenClaw Skills & Plugins

OpenClaw is the hottest open-source AI Agent framework of 2026 (180K+ GitHub Stars), and its Skills system is a core competitive advantage. Skills are like npm packages — install and use, no need to build from scratch ([Tencent Cloud](https://www.tencentcloud.com/techpedia/140807)).

Content rephrased for compliance with licensing restrictions.

### OpenClaw Core Concepts

| Concept | Description |
|---------|-------------|
| Gateway | Locally running AI gateway connecting messaging platforms and AI models |
| Skills | Executable skill modules (similar to npm packages) defining what an Agent can do |
| Plugins | Extension plugins connecting external services (messaging platforms/APIs/tools) |
| Channels | Messaging channels (WhatsApp/Telegram/Discord/Slack/iMessage) |

### OpenClaw Official Skills Ecosystem

> OpenClaw has 50+ official integrations, which is one of its core competitive advantages ([ApiYi](https://help.apiyi.com/en/openclaw-extensions-ecosystem-guide-en.html)).

Content rephrased for compliance with licensing restrictions.

| Category | Skills | Description |
|----------|--------|-------------|
| Messaging Channels | WhatsApp, Telegram, Discord, Slack, Signal, iMessage, Google Chat, Teams | Multi-platform messaging |
| Browser | Browser Relay, Screen Capture | Web browsing, screenshots, automation |
| File System | File Manager, Code Executor | File read/write, code execution |
| Calendar/Email | Google Calendar, Gmail, Outlook | Schedule management, email handling |
| Dev Tools | GitHub, Git, Terminal | Code management, command execution |
| Data Analysis | CSV/Excel Parser, Web Scraper | Data processing and scraping |
| AI Models | Claude, GPT-4, DeepSeek, Gemini, Ollama | Multi-model support |

### OpenClaw E-Commerce Use Cases

```
OpenClaw E-Commerce Automation Examples:

1. WhatsApp Customer Service Agent
   ├── Install WhatsApp Channel Plugin
   ├── Configure customer service Skill (Product FAQ/Returns/Shipping tracking)
   ├── Connect Shopify MCP (query order status)
   └── 24/7 auto-reply, escalate complex issues to humans

2. Multi-Platform Price Monitoring
   ├── Install Web Scraper Skill
   ├── Scheduled competitor price scraping
   ├── AI analyzes price changes
   └── Push alerts via Telegram

3. Daily Operations Report
   ├── Install CSV Parser + Gmail Skill
   ├── Auto-download Amazon reports
   ├── AI analyzes key metrics
   └── Send daily report via Slack
```

### OpenClaw Resources

| Resource | Description | Link |
|----------|-------------|------|
| OpenClaw GitHub | Main repository (180K+ Stars) | [GitHub](https://github.com/nicepkg/openclaw) |
| Official Docs | Installation and configuration guide | [openclaw.dev](https://openclaw.dev/) |
| Skills Marketplace | Browse pre-built Skills | Built into OpenClaw CLI |
| Installation Guide | One-click install: `npm install -g openclaw@latest` | [AIFreeAPI](https://www.aifreeapi.com/en/posts/openclaw-installation-guide) |
| Full Tutorial | From zero to personal AI assistant | [DigitalApplied](https://www.digitalapplied.com/blog/openclaw-ai-complete-guide-setup-skills-automation) |

---

## ⚡ Kiro Skills & Steering Files

Kiro uses Steering Files to provide persistent project knowledge ([Kiro Docs](https://aws.amazon.com/documentation-overview/kiro/)).

| Type | Location | Trigger | Purpose |
|------|----------|---------|---------|
| Always-on | `.kiro/steering/*.md` | Auto-loaded on every conversation | Project standards, coding conventions |
| File-match | `.kiro/steering/*.md` + frontmatter | Loaded when matching files are read | Rules for specific file types |
| Manual | `.kiro/steering/*.md` + `inclusion: manual` | Referenced manually with `#` | On-demand reference docs |
| Skills | `.kiro/skills/*.md` | Activated on demand | Reusable task instructions |

### E-Commerce Project Steering Examples

Steering Files used in this project (CBEC-AI-Hub):

| File | Purpose |
|------|---------|
| `product.md` | Project background (Amazon Account Manager, cross-border e-commerce) |
| `structure.md` | Project structure (file organization, naming conventions) |
| `tech.md` | Tech stack (Python/TypeScript/Chart.js) |

---

## 📐 Cursor Rules

Cursor Rules define custom rules for AI code generation ([PatrickJS](https://github.com/PatrickJS/awesome-cursorrules)).

### Recommended Rules for E-Commerce Development

| Rule | Best For | Source |
|------|----------|--------|
| Python Projects Guide | Python e-commerce script development | [PatrickJS](https://github.com/PatrickJS/awesome-cursorrules/blob/main/rules/python-projects-guide-cursorrules-prompt-file/.cursorrules) |
| Python Flask JSON | Flask API development | [PatrickJS](https://github.com/PatrickJS/awesome-cursorrules/blob/main/rules/python-flask-json-guide-cursorrules-prompt-file/.cursorrules) |
| React TypeScript shadcn/ui | Shopify frontend/Dashboard | [PatrickJS](https://github.com/PatrickJS/awesome-cursorrules/blob/main/rules/cursor-ai-react-typescript-shadcn-ui-cursorrules-p/.cursorrules) |
| Security Rules | AI secure coding | [GitHub Topics](https://github.com/topics/cursorrules) |

---

## 📝 Claude Code SKILL.md

SKILL.md is a structured instruction file for AI coding agents like Claude Code, Roo Code, OpenAI Codex, and Cursor. Write once, and the Agent automatically reads and applies it ([MTechZilla](https://www.mtechzilla.com/guides/how-to-develop-skill-md-production-guide-engineering-teams)).

Content rephrased for compliance with licensing restrictions.

### SKILL.md Structure

```markdown
# Skill Name

## Context
Project background and tech stack

## Instructions
Specific coding rules and constraints

## Examples
Good code examples vs. bad code examples

## Constraints
Mandatory restrictions (security/performance/style)
```

---

## 🛒 Recommended Skills for E-Commerce Development

### Recommendations by Role

| Role | Recommended Tools | Recommended Skills/Rules |
|------|-------------------|--------------------------|
| Operations (Non-technical) | OpenClaw | WhatsApp Customer Service Skill + Web Scraper + Report Generation |
| Python Developer | Kiro + Claude Code | Steering Files (tech.md) + SKILL.md (Python standards) |
| Frontend Developer | Cursor | React/TypeScript Rules + Shopify Liquid Rules |
| Full-Stack | Kiro | Steering + MCP Configuration + Skills |
| Automation | OpenClaw + n8n | OpenClaw Skills + n8n MCP |

### Quick Start

```bash
# OpenClaw: One-click install AI assistant
npm install -g openclaw@latest
openclaw onboard

# Kiro: Create Steering Files
mkdir -p .kiro/steering
echo "# Project Standards\nYour coding rules..." > .kiro/steering/rules.md

# Cursor: Create Rules
echo "You are a Python e-commerce development expert..." > .cursorrules
```

---

> 🏠 [Hub Home](../README.md) · 🔌 [Awesome MCP & Agent](awesome-mcp-agents.md) · 🔧 [B6 MCP Integration](../paths/b-developers/b6-mcp-agentic-workflow.md) · ⚡ [F4 Agent Automation](../paths/0-foundations/f4-agent-automation.md)
