# Outreach Log

记录本项目对外推广动作。

## 2026-08-09

| 动作 | 状态 | 链接/备注 |
|------|------|-----------|
| GitHub v1.0.0 Release | ✅ 完成 | tag v1.0.0, notes in .planning/release-notes-v1.0.0.md |
| MCP Server 目录提交 | ⚠️ 待仓库主人操作 | 下文提供 PR 草稿 |
| Skill/agent 工具目录 | ⚠️ 待仓库主人操作 | 下文提供 PR 草稿 |
| awesome-chatgpt-prompts PR | ⚠️ 待仓库主人操作 | 下文提供 PR 草稿 |
| Zenn/Qiita 日语文章 | ✅ 完成 | 文稿 in .planning/zenn-article.md |

## 2026-08-10

| 动作 | 状态 | 链接/备注 |
|------|------|-----------|
| v1.1.0 tag | ✅ 完成 | notes in .planning/release-notes-v1.1.0.md |
| 专用 MCP server | ✅ 完成 | integration/mcp-server.py（7 resource / 4 tool / 9 prompt） |
| 目录 PR 草稿更新 | ✅ 完成 | 数字同步到 318 约束 |
| GitHub Release 发布 | ⚠️ 待仓库主人操作 | 需要 web UI |
| 真机验证 | ⚠️ 阻塞 | 需要真实 MCP client 环境 |

## 目录 PR 草稿

### 1. MCP Server 目录
PR to: https://github.com/modelcontextprotocol/servers
Content: OPC E-Commerce Infrastructure — plug-and-play agent capability package for cross-border e-commerce operations. 69 chapters, 94 entities, 318 constraints, 9 domain skills. Dedicated MCP server exposing 7 resources, 4 tools, 9 prompts.
Entry: Add `kangise/ecommerce-ai-roadmap` under Community Servers → E-Commerce

### 2. Skill/agent 工具目录  
PR to: any agent-tool directory aggregator
Entry: 9 installable e-commerce domain skills (listing, advertising, inventory, compliance, pricing, research, social, applicability, customer). Each has I/O manifest, constraints, playbook.

### 3. awesome-chatgpt-prompts
PR to: https://github.com/f/awesome-chatgpt-prompts
Entry: E-Commerce AI Infrastructure — 292 guarded prompts with ontology constraints and auto-verification. Trilingual (zh/en/ja).

## 待提交
- [ ] 仓库主人: 发布 GitHub Release（v1.0.0 + v1.1.0）
- [ ] 仓库主人: 提交 3 个目录 PR
- [ ] 仓库主人: 更新 GitHub About/Topics/social preview
- [ ] 仓库主人: 在真实 MCP client 跑 .planning/live-verification-plan.md
