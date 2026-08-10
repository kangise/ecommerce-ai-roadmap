# v1.1.0 — 从"能装上"到"装上能用"

v1.0.0 交付了三层结构本身。v1.1.0 修的是三层之间的**接缝**：约束覆盖不全、MCP 只是一个文件系统指针、门禁能变绿但不能证伪。

---

## 规模变化

| 指标 | v1.0.0 | v1.1.0 | 说明 |
|------|--------|--------|------|
| 平台约束 | 184 | **318** | +134，15 个平台全部有约束 |
| 领域实体 | 94 | 94 | 空属性 10 → **0** |
| 无约束实体 | 32 | **0** | 每个实体都有可执行判据 |
| 实体关系 | 78 | 78 | — |
| 业务流程 | 8 | 8 | — |
| 可执行 Prompt | 868 | **878** | zh 292 / en 294 / ja 292 |
| Domain Skills | 9 | 9 | playbook 内容加厚 |
| 知识章节 | 69 | 69 | 三语 |
| 路由测试用例 | 60 | **90** | R1 0 错 |
| CI 门禁 | 9 组 24 项 | **10 组 30 项** | 全 0 |

---

## 主要变更

### 1. 约束覆盖补全（184 → 318）

v1.0.0 的 184 条约束里，Amazon 与 Shopify 占了大头，另外 12 个平台是空的——agent 路由到 Temu 或 Coupang 时拿不到任何平台规则，只能凭模型自身的记忆编。

- **+94 条平台约束**，覆盖此前无约束的 12 个平台：walmart、temu、shopee、lazada、rakuten、ebay、coupang、faire、aliexpress、mercado_libre、otto、zalando
- **+40 条实体约束**，覆盖 32 个此前无判据的实体：buy_box、bsr、prime、ltv、ipi、cac、wfs、bfcm、cpm、cod 等
- **10 个空属性实体全部填充**，`attributes` 不再是占位符

### 2. 专用 MCP Server 替换文件系统指针

v1.0.0 的 MCP 配置指向 `@modelcontextprotocol/server-filesystem`——本质上是把 `dist/` 当一堆文件暴露出去，agent 需要自己猜哪个文件该读。

`integration/mcp-server.py` 现在提供**类型化的三类接口**：
- **7 个 Resource**：ontology、prompts、knowledge index、skills 路由表等，各有明确 URI 与 MIME type
- **4 个 Tool**：按域检索约束、按场景匹配 skill、查平台差异、取 prompt 模板
- **9 个 Prompt**：每个 domain skill 一个入口，带参数 schema
- 内置 CLI 测试模式，不接 client 也能验证

### 3. 门禁从"能变绿"改成"能证伪"

这一轮修掉的是门禁自身的可信度问题——一套永远返回 0 的检查等于没有检查。

- **`verify_all.py` 此前无法失败**：不检查子脚本 returncode、传子脚本拒绝的逗号分隔 `--only`、`--sustain` 分支不打印总计行。三处全修，并做了故障注入验证
- **`verify_ontology.py` / `verify_skills.py` 只在 0 时打印 total**，导致失败对父脚本不可见。已修
- **R1 抗腐化改为实测**：此前统计的是自声明的 `natural: true` 字段，现在实算字面命中率，阈值与 CONTRIBUTING.md 统一到 95%
- **新增 R1b 门禁**：禁止把测试用例切碎回填进 manifest triggers。允许清单显式列出，每个例外可审查
- **D2 扩展到 prose 扫描**：`src/README.md` 的"56 篇指南"在整轮改造中一直没被发现，因为 D2 只扫 markdown 表格单元格
- **S5 幽灵文件名自检**：6 个豁免文件在 `src/` 里根本不存在；现在任一豁免文件名缺失即报错

### 4. 三语 Prompt 结构真实对齐

v1.0.0 的 N6 归零里混进了 93 个填充标签——批量脚本插的是英文通用模板（"Only use numbers from input_boundary…"），不是真实翻译。

- **93 个填充标签全部替换为真实翻译**
- **N6 豁免从 10 个收到 2 个**（仅 f1/f2，f2 因为它本身在讲解 prompt 结构，存在有意变体）
- **22 个错位的 constraint ref 标记移除**——批量脚本把约束引用贴到了含无关数字的行上

### 5. 路由测试扩容

- 用例 60 → **90**，R1 0 错
- ecom-applicability 需 ≥2 关键词命中才能压过 domain skill：单个"朋友说"不该压过"包装不好看"+"重新设计"
- ecom-applicability playbook 5 → 10 条 prompt

---

## 升级方式

```bash
git pull
python3 scripts/build_dist.py
```

MCP 配置改为专用 server：

```json
{
  "mcpServers": {
    "opc-ecommerce": {
      "command": "python3",
      "args": ["/path/to/ecommerce-ai-roadmap/integration/mcp-server.py"]
    }
  }
}
```

旧的 filesystem 配置仍可用，但拿不到 Tool 与 Prompt 两类能力。

---

## 已知边界

- **未做真机验证**：6 个场景 + 10 条 scope 查询 + 3 条拒答边界的测试计划在 `.planning/live-verification-plan.md`，需要真实 MCP client 环境执行
- **en 294 / zh 292**：英文侧多 2 条 prompt，来自两章的补充示例，不影响 N6 结构对齐

---

`dist/` 是自包含的 agent 能力包。v1.1.0 的差别是：接上之后，它不再需要你告诉它去读哪个文件。
