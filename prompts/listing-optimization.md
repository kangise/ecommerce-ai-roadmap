# Listing 与内容创作 Prompt 模板 | Listing Optimization Prompts

> 最后更新: 2026-03-10 | 模板数量: 3 | 验证状态: 已验证

---

## 模板 1: Listing 全套生成

**场景**: 从零生成完整的 Amazon Listing（标题、五点、描述、Search Terms）
**推荐工具**: ChatGPT / Claude
**验证状态**: 已验证
**贡献者**: [@kangise](https://github.com/kangise)

### Prompt

```
你是一个 Amazon Listing 优化专家，精通 [目标市场] 市场的搜索习惯。

产品信息：
- 产品名称：[名称]
- 核心卖点：[卖点1]、[卖点2]、[卖点3]
- 目标客户：[客户画像]
- 核心关键词：[关键词列表]

请生成：
1. 标题（不超过200字符，前80字符包含最重要的关键词）
2. 5个 Bullet Points（每条以大写卖点开头，融入关键词，突出差异化）
3. 产品描述（200字以内，讲品牌故事和使用场景）
4. 后台 Search Terms（5行，每行不超过250字节，不重复标题中的词）

要求：
- 关键词自然融入，不堆砌
- 语言符合 [目标市场] 消费者的搜索和阅读习惯
- 突出与竞品的差异化
```

### 预期输出示例

> AI 会输出一套完整的 Listing 文案，包含标题、5 条 Bullet Points、产品描述和 5 行 Search Terms，关键词自然融入且符合目标市场的语言习惯。

### 使用技巧

- 提供竞品 ASIN 或 Listing 链接，让 AI 参考竞品做差异化
- 生成后可追问"帮我检查关键词覆盖率"来优化

---

**分享此模板**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/prompts/listing-optimization.md#模板-1-listing-全套生成`
**来源**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × 跨境电商实战知识库

---

## 模板 2: 多语言本地化

**场景**: 将英文 Listing 本地化为其他语言，不是直译而是适配当地市场
**推荐工具**: ChatGPT / Claude / DeepL
**验证状态**: 已验证
**贡献者**: [@kangise](https://github.com/kangise)

### Prompt

```
你是一个精通 [目标语言] 的 Amazon Listing 本地化专家。

以下是英文版 Listing：
[粘贴英文 Listing]

请翻译为 [目标语言] 版本。注意：
1. 不是逐字翻译，要符合 [目标市场] 消费者的搜索习惯和表达方式
2. 替换为当地市场常用的搜索关键词
3. 调整卖点顺序，把 [目标市场] 消费者最关心的放前面
4. 标注你做了哪些本地化调整及原因
```

### 预期输出示例

> AI 会输出本地化后的 Listing 文案，并在末尾标注所有本地化调整（如关键词替换、卖点顺序调整），帮助你理解为什么这样改。

### 使用技巧

- 指定具体市场（如"德国"而非"欧洲"），本地化效果更好
- 可以追问"德国消费者最关心产品的哪些方面"来进一步优化

---

**分享此模板**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/prompts/listing-optimization.md#模板-2-多语言本地化`
**来源**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × 跨境电商实战知识库

---

## 模板 3: 竞品 Listing 策略拆解

**场景**: 对比分析多个竞品 Listing，找到差异化定位机会
**推荐工具**: ChatGPT / Claude
**验证状态**: 已验证
**贡献者**: [@kangise](https://github.com/kangise)

### Prompt

```
分析以下 3 个竞品的 Amazon Listing，对比它们的策略差异：

[竞品A标题和五点]
[竞品B标题和五点]
[竞品C标题和五点]

请输出：
1. 三个竞品各自的核心定位（用一句话概括）
2. 它们共同强调的卖点（品类"必备项"）
3. 各自独有的卖点（差异化机会）
4. 关键词覆盖对比表
5. 我的 Listing 应该如何差异化定位
```

### 预期输出示例

> AI 会输出一份竞品策略对比分析，包含定位总结、共性卖点、差异化机会、关键词对比表，以及针对你的产品的差异化定位建议。

### 使用技巧

- 粘贴完整的标题和五点描述，信息越全分析越准
- 可以追问"如果我的产品在 [某方面] 有优势，应该怎么突出"

---

**分享此模板**: `https://github.com/kangise/ecommerce-ai-roadmap/blob/main/prompts/listing-optimization.md#模板-3-竞品-listing-策略拆解`
**来源**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap) AI × 跨境电商实战知识库
