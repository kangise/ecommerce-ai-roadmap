# v1.0.0 — OPC E-Commerce AI Infrastructure

首版正式发布。**不仅是一本书——是 agent 即插即用的跨境电商运营基础设施。**

---

## 规模

| 指标 | 数值 |
|------|------|
| 知识章节 | 69 章，三语（中/英/日） |
| 领域实体 | 94 个，含属性和来源追踪 |
| 平台约束 | 184 条，覆盖 Amazon/Shopify/TikTok Shop 等 15 个平台 |
| 实体关系 | 78 条 |
| 业务流程 | 8 个（选品→上架→广告→库存→合规→财务→品牌→Agent 化） |
| 可执行 Prompt | 292 条（中文）/ 868 条（三语合计） |
| Domain Skills | 9 个（listing/advertising/inventory/compliance/pricing/research/social/applicability/customer） |
| CI 门禁 | 9 组 24 项，全 0 |

## 三层结构

### 1. 知识库（给人读 + agent 检索）
69 个章节覆盖跨境电商全操作链，从选品到自动化。三语同步。

### 2. Ontology（agent 之间的共享契约）
94 个实体、78 条关系、184 条平台约束、8 个业务流程。机器可读，`source:` 可追溯。

### 3. Skills + Prompts（agent 直接调用）
9 个 domain skill，每个含 manifest（I/O schema）、playbook（可执行 prompt）、constraints（平台规则）、boundaries（什么时候不该用）。

## 即插即用

```bash
# 1. 下载
git clone https://github.com/kangise/ecommerce-ai-roadmap.git
cd ecommerce-ai-roadmap

# 2. 构建
python3 scripts/build_dist.py

# 3. 接入你的 agent（MCP 示例）
# dist/SKILL.md 就是 agent 的系统 prompt
```

MCP 配置：
```json
{
  "mcpServers": {
    "opc-ecommerce": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dist"]
    }
  }
}
```

## 变更

本次 Release 包含从规划到执行的完整积累：
- **Phase 0**: N1 三语标签对齐 + Amazon 平台索引 + ontology 骨架
- **Phase A**: 4 域并行 ontology 抽取（94E/78R/184C）
- **Phase B**: 812 条 Prompt 补自检+输出格式+三语对齐
- **Phase C**: 9 个 domain skill + S1-S5 门禁
- **Phase D**: `dist/` 可安装包 + N7 门禁 + CI
- **Phase E**: M7 抗腐化 + 脚手架 + CONTRIBUTING
- **Loop 1**: N6 三语 Prompt 结构对齐（46 文件 → 0）
- **Loop 2**: ecom-social 新建 + S5 覆盖完善
- **Loop 3**: R1 路由测试 0/60 错误

---

`dist/` 目录是一个**自包含的 agent 能力包**。连上就知道。
