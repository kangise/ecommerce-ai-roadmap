# Awesome AI Skills & Rules | Skill Files and Rule Sets for AI IDEs

> **Where this stops working**: this is a list, not a review. Inclusion means someone uses it in a cross-border e-commerce context, not that each was tested. AI IDEs iterate fast and entries go stale — check the vendor's own docs before relying on one.

> Skills, steering files, and rules for AI IDEs (Kiro/Cursor/Windsurf/Claude Code).
> Make AI work to your standards instead of re-explaining them every session.
> Last updated: 2026-03-15


---

## Contents

- [What are AI Skills / Rules](#what-are-ai-skills--rules)
- [External awesome lists and resources](#external-awesome-lists-and-resources)
- [Kiro Skills & Steering Files](#kiro-skills--steering-files)
- [Cursor Rules](#cursor-rules)
- [Claude Code SKILL.md](#claude-code-skillmd)
- [Recommended skills for e-commerce development](#recommended-skills-for-e-commerce-development)

---

## What are AI Skills / Rules

AI skills are persistent instructions for an AI assistant. Written once, followed automatically — no repeating yourself in every chat.

| Platform | File | Location | Notes |
|----------|------|----------|-------|
| Kiro | `*.md` | `.kiro/skills/` or `.kiro/steering/` | Steering files persist project conventions |
| Cursor | `.cursorrules` or `.mdc` | project root | Custom AI code-generation rules |
| Claude Code | `SKILL.md` | project root | Reusable AI coding instructions |
| Windsurf | `.windsurfrules` | project root | Similar to Cursor Rules |

---

## External Awesome Lists and Resources

### Cursor Rules collections

| Name | Stars | Description | Link |
|------|-------|-------------|------|
| awesome-cursorrules (PatrickJS) | 23.6K | The largest Cursor Rules collection, by language/framework | [GitHub](https://github.com/PatrickJS/awesome-cursorrules) |
| awesome-cursor-rules (blefnk) | popular | Frontend-optimized (Next.js/React/TypeScript/Tailwind) | [GitHub](https://github.com/blefnk/awesome-cursor-rules) |
| awesome-cursor-rules-mdc (sanjeed5) | curated | Cursor Rules in .mdc format | [GitHub](https://github.com/sanjeed5/awesome-cursor-rules-mdc) |
| Cursor-Rules (UltraInstinct0x) | practical | Focused on rules that produce runnable code | [GitHub](https://github.com/UltraInstinct0x/Cursor-Rules) |

### Directory sites

| Site | Description | Link |
|------|-------------|------|
| ExtMC | Searchable Cursor Rules directory, filter by framework/stack | [extmc.com](https://extmc.com/) |
| PromptGenius | Cross-IDE AI rules guide (Cursor/Windsurf/Copilot) | [promptgenius.net](https://promptgenius.net/cursorrules) |
| GitHub Topics: cursorrules | Every cursorrules project on GitHub | [GitHub Topics](https://github.com/topics/cursorrules) |

### In-depth guides

| Article | Source | Notes |
|---------|--------|-------|
| How To Write Rules for AI Coding Tools | VirtusLab | Best practices for writing AI rules |
| How to Develop SKILL.md for AI Coding Agents | MTechZilla | Production-grade SKILL.md guide |
| How to Guide AI With Rules and Tests | freeCodeCamp | Steering AI with rules and tests |
| Beyond the Vibes: A Rigorous Guide | tedivm | A rigorous guide to AI coding assistants |

Sources: [VirtusLab](https://virtuslab.com/blog/ai/how-to-write-rules-for-ai/), [MTechZilla](https://www.mtechzilla.com/blogs/how-to-develop-skill-md-production-guide-engineering-teams), [freeCodeCamp](https://www.freecodecamp.org/news/how-to-guide-ai-with-rules-and-tests/), [tedivm](https://blog.tedivm.com/guides/2026/03/beyond-the-vibes-coding-assistants-and-agents/).

Content rephrased for compliance with licensing restrictions.

---

## Kiro Skills & Steering Files

Kiro uses steering files to provide persistent project knowledge ([Kiro Docs](https://aws.amazon.com/documentation-overview/kiro/)).

| Type | Location | Trigger | Use |
|------|----------|---------|-----|
| Always-on | `.kiro/steering/*.md` | loaded on every conversation | Project conventions, coding standards |
| File-match | `.kiro/steering/*.md` + frontmatter | loaded when matching files are read | Rules for specific file types |
| Manual | `.kiro/steering/*.md` + `inclusion: manual` | referenced manually with `#` | On-demand reference docs |
| Skills | `.kiro/skills/*.md` | activated on demand | Reusable task instructions |

### E-commerce steering example

Steering files used by this project (CBEC-AI-Hub):

| File | Purpose |
|------|---------|
| `product.md` | Project context (Amazon account management, cross-border e-commerce) |
| `structure.md` | Project structure (file organization, naming conventions) |
| `tech.md` | Tech stack (Python/TypeScript/Chart.js) |

---

## Cursor Rules

Cursor Rules define custom rules for AI code generation ([PatrickJS](https://github.com/PatrickJS/awesome-cursorrules)).

### Recommended rules for e-commerce development

| Rule | Fits | Source |
|------|------|--------|
| Python Projects Guide | Python e-commerce scripting | [PatrickJS](https://github.com/PatrickJS/awesome-cursorrules) |
| Python Flask JSON | Flask API development | [PatrickJS](https://github.com/PatrickJS/awesome-cursorrules) |
| React TypeScript shadcn/ui | Shopify frontend / dashboards | [PatrickJS](https://github.com/PatrickJS/awesome-cursorrules) |
| Security Rules | Secure AI coding | [GitHub Topics](https://github.com/topics/cursorrules) |

---

## Claude Code SKILL.md

SKILL.md is a structured instruction file for AI coding agents such as Claude Code, Roo Code, OpenAI Codex, and Cursor. Write it once; the agent reads and applies it automatically ([MTechZilla](https://www.mtechzilla.com/blogs/how-to-develop-skill-md-production-guide-engineering-teams)).

Content rephrased for compliance with licensing restrictions.

### SKILL.md structure

```markdown
# Skill Name

## Context
Project background and tech stack

## Instructions
Concrete coding rules and constraints

## Examples
Good code examples vs. bad ones

## Constraints
Hard limits (security/performance/style)
```

---

## Recommended Skills for E-Commerce Development

### By role

| Role | Recommended tools | Recommended skills/rules |
|------|-------------------|--------------------------|
| Python developer | Kiro + Claude Code | Steering files (tech.md) + SKILL.md (Python conventions) |
| Frontend developer | Cursor | React/TypeScript rules + Shopify Liquid rules |
| Full-stack | Kiro | Steering + MCP config + skills |

### Quick start

```bash
# Kiro: create steering files
mkdir -p .kiro/steering
echo "# Project conventions\nYour coding rules..." > .kiro/steering/rules.md

# Cursor: create rules
echo "You are a Python e-commerce development expert..." > .cursorrules
```

---
