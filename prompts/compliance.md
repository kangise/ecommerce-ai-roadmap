# 合规风控与库存管理 Prompt 模板 | Compliance & Inventory Prompts

> 最后更新: 2026-03-10 | 模板数量: 2 | 验证状态: 已验证

---

## 模板 1: 多市场合规对比

**场景**: 快速查询不同国家/品类的合规要求，生成合规清单
**推荐工具**: ChatGPT / Claude / Gemini
**验证状态**: 已验证
**贡献者**: [@kangise](https://github.com/kangise)

### Prompt

```
我要在 Amazon [US/DE/JP] 销售 [产品类型]。

请生成合规要求对比表：
1. 每个市场需要的产品认证
2. 包装和标签的特殊要求
3. 特殊品类的额外要求（如电池、儿童用品、食品接触）
4. 预估认证费用范围和周期
5. 常见合规陷阱

注意：法规可能已更新，请标注信息时效性，建议向认证机构确认。
```

### 预期输出示例

> AI 会输出一个多市场合规对比表，按市场列出所需认证、包装标签要求、特殊品类要求、费用预估和常见陷阱，并标注信息时效性提醒。

### 使用技巧

- 指定具体产品类型（如"锂电池充电宝"而非"电子产品"），结果更精准
- 可以追问"如果我已有 FCC 认证，还需要额外做什么才能进入德国市场"

---

**分享此模板**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/prompts/compliance.md#模板-1-多市场合规对比`
**来源**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × 跨境电商实战知识库

---

## 模板 2: 补货决策分析

**场景**: 基于历史销量数据计算最优补货时间和采购量
**推荐工具**: ChatGPT / Claude
**验证状态**: 已验证
**贡献者**: [@kangise](https://github.com/kangise)

### Prompt

```
我的产品数据：
- 过去90天日均销量：[X] 件（波动范围 [min]-[max]）
- 当前 FBA 库存：[X] 件
- 在途库存：[X] 件
- 从下单到入仓的 Lead Time：[X] 天
- 安全库存天数目标：[X] 天

请计算：
1. 当前库存可支撑天数
2. 最晚采购下单日期
3. 建议采购量（乐观/基准/悲观三种场景）
4. 如果有大促（如 Prime Day），需要额外备多少
5. 资金占用估算
```

### 预期输出示例

> AI 会输出库存可支撑天数、最晚下单日期、三种场景的采购量建议、大促额外备货量和资金占用估算，帮助你做出数据驱动的补货决策。

### 使用技巧

- 提供真实的销量波动范围，AI 会给出更合理的安全库存建议
- 可以追问"如果 Lead Time 延长到 [X] 天，计划怎么调整"来做风险预案

---

**分享此模板**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/prompts/compliance.md#模板-2-补货决策分析`
**来源**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × 跨境电商实战知识库
