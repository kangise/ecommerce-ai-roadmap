# Unresolved / Ambiguous Candidates

Dumping ground for entities, constraints, or relations we are not sure about.
Each entry notes the ambiguity and the source passage. Do **not** guess —
move entries to the YAML files only when confirmed.

## Format

```
### <candidate name>
- Source: <chapter anchor>
- Ambiguity: <what makes us unsure>
- Candidates for: entities.yaml | relations.yaml | constraints.yaml
```

## Candidates from Inventory domain extraction (2026-08)

Full extraction lives in `inventory-domain.yaml`; entries marked `flagged: true` there are mirrored here.

### warehouse
- Source: src/a-operators/a5-inventory.md#62-多渠道库存同步amazon--shopify--独立站
- Ambiguity: 章节出现"FBA 仓库/库存中心系统/3PL 统一仓储"，但无统一"warehouse"实体定义；实体由多处归纳而来
- Candidates for: entities.yaml

### fbm_inventory
- Source: src/a-operators/a5-inventory.md#62-多渠道库存同步amazon--shopify--独立站
- Ambiguity: 原文仅"自发货"一词（FBA 仓库 vs 自发货），FBM 实体为归纳命名
- Candidates for: entities.yaml

### promo_sales_multiplier (大促销量倍数 3-10x)
- Source: src/a-operators/a5-inventory.md#34-大促备货策略prime-day--bfcm
- Ambiguity: 原文"可能是平时的 3-10 倍"，属经验性参考，非实测/平台数据
- Candidates for: constraints.yaml

### MAPE 基准（<15 优秀 / 15-25 良好 / 25-40 可接受 / >40 需改进）与回测目标 MAPE<30%
- Source: src/b-developers/b2-prediction-models.md#41-评估指标, #8-完成标志
- Ambiguity: 章节明确标注为参考线/基准（claims: benchmark），不是市场实测均值
- Candidates for: constraints.yaml

### forecast.reorder_urgency_rule（库存 ≤ 补货点×0.5 → 紧急）
- Source: src/b-developers/b2-prediction-models.md#35-预测结果转化为补货决策
- Ambiguity: 来自示例代码的阈值划分，属实现约定而非领域规则
- Candidates for: constraints.yaml

### forecast.stockout_data_handling（连续≥3天零销量 → 断货，7天窗口填充）
- Source: src/b-developers/b2-prediction-models.md#12-电商预测的特殊挑战
- Ambiguity: 3 天/7 天来自章节代码，属工程约定
- Candidates for: constraints.yaml

### forecast.changepoint_prior_range（默认 0.05，电商 0.1-0.3）
- Source: src/b-developers/b2-prediction-models.md#31-prophet-销量预测完整流程
- Ambiguity: 章节调参指南的工程建议，非硬性约束
- Candidates for: constraints.yaml

### inventory.eoq_formula（√(2DS/H)）
- Source: src/a-operators/a5-inventory.md#安全库存与补货公式速查
- Ambiguity: 仅以速查表形式出现，未展开推导与使用前提（H 的口径未定义）
- Candidates for: constraints.yaml

## Candidates from Compliance & Risk domain extraction (2026-08)

Full extraction lives in `compliance-risk.yaml`; entries marked `flagged: true` there are mirrored here.

### product_category_approval（品类准入审批）
- Source: src/a-operators/a6-compliance.md#41-新品上架前合规检查-sop
- Ambiguity: Amazon "类目审核/category approval" 未在章节中作为正式名词出现，由 SOP "在 Amazon Seller Central 确认品类的具体合规要求" 推断
- Candidates for: entities.yaml | relations.yaml | constraints.yaml

### hs_code 位数格式（WCO 6 位基础码 / HTS 8-10 位）
- Source: src/case-studies/hs-code-classification.md#相关资源
- Ambiguity: 位数规则派生自案例引用的 WCO/HTS 官方资源，案例正文未逐字写明
- Candidates for: constraints.yaml

### EU Digital Product Passport 时间线（2027-2030 分品类）
- Source: src/a-operators/a6-compliance.md#72-欧盟新法规digital-product-passport-与-gpsr
- Ambiguity: 章节原文为"预计"，法规尚未生效，日期不确定
- Candidates for: constraints.yaml

### EU AI Act 透明度义务生效日期（2026-08-02）
- Source: src/a-operators/a6-compliance.md#51-三条直接落到卖家头上的义务
- Ambiguity: 生效日期为章节 2026-07-31 核实结果；Digital Omnibus 对高风险档（附件 III）的推迟尚未在官方公报刊登，日期应以官方公报为准
- Candidates for: constraints.yaml

### 认证有效期（通常 1-5 年）与续期提前量（3 个月）
- Source: src/a-operators/a6-compliance.md#61-认证相关陷阱
- Ambiguity: "通常 1-5 年""提前 3 个月"为一般性表述，非统一规则，不同认证有效期不同
- Candidates for: constraints.yaml

### 扩展约束 kind（min_size / validity_period / max_duration / cost_range）
- Source: ontology/constraints.yaml（schema 注释）
- Ambiguity: 模板枚举仅列 max_length | min_length | max_bytes | count | format | forbidden | required；compliance-risk.yaml 使用了 4 个扩展 kind，合并前需先扩展 schema
- Candidates for: constraints.yaml

## G3: Amazon 视频广告字幕规格（v4 Sprint 4 复核）

真机验收 B3「Amazon 视频广告字幕」路由到 ecom-advertising 但零相关约束。

复核结论：**真内容缺口，但补不了**。
- src/a-operators/a3-advertising.md 有 Sponsored Brands Video 的 15 秒脚本 Prompt（L439-490），
  但**没有字幕/caption 的具体规格**（字数、时长、安全区）。
- ontology 里只有 tiktok_shop 的视频约束，无 Amazon 视频广告约束。
- 不能从「15 秒脚本」推出字幕字数上限——那是编造约束，违反 M1/O1 纪律。

处置：需要人去 Amazon Advertising 官方规格页核实 SBV 字幕/视频规格后补约束。
在此之前记为未解决，不瞎补。来源候选：
  https://advertising.amazon.com/help（Sponsored Brands Video 规格）
