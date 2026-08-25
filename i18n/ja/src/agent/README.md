# Agent 接入

本仓库不仅是一本书。`dist/` 目录是即插即用的 agent 能力包。

> `dist/SKILL.md` — Agent 系统 prompt（含路由规则）
> `dist/README.md` — 快速开始
> `dist/integration/mcp.md` — MCP Server 接入

三层结构：

| 层 | 内容 | 给谁 |
|---|---|---|
| 知识库 (src/) | 69 章，三语 | 人读 · agent 检索 |
| Ontology (ontology/) | 100 实体 · 322 约束 | agent 之间的共享契約 |
| Skills (skills/) | 9 个可安装 skill · 878 条 Prompt | agent 直接调用 |

---

## 验证

```bash
python3 scripts/verify_all.py   # 所有门禁
python3 scripts/build_dist.py   # 构建 dist/
```
