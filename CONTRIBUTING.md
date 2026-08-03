---
layout: page
title: 贡献指南
permalink: /contributing/
---

# 贡献指南 | Contributing Guide

欢迎为 ecommerce-ai-roadmap 做贡献！以下是参与方式和提交标准。

Welcome to ecommerce-ai-roadmap! Here's how you can contribute.

---

## 你可以做什么 | Ways to Contribute

### 提交 Prompt 模板（最简单！）

**不需要会 Git/PR** 直接通过 Issue 提交即可：

1. 打开 [Prompt 提交模板](https://github.com/kangise/ecommerce-ai-roadmap/issues/new?template=prompt_submission.md)
2. 填写表单：模板名称、场景、Prompt 内容、使用效果
3. 提交 Issue，维护者会审核并转化为正式模板文件
4. 你会被标注为贡献者

Prompt 模板分布在各章节中，运营侧集中在 [运营路径](src/a-operators/)，通用模板见 [F2 §6](src/0-foundations/f2-prompt-engineering.md)。

### 多平台运营经验（ 新增方向）

我们刚扩展了 13 个电商平台和 7 个社交媒体渠道的指南，特别欢迎以下贡献：

| 贡献方向 | 说明 | 提交方式 |
|----------|------|----------|
| **平台实操经验** | 你在 Walmart/Shopee/Mercado Libre/Rakuten/Coupang 等平台的运营经验 | Issue 或 PR |
| **社交媒体案例** | Instagram/YouTube/小红书/Pinterest 的成功引流案例（含数据） | Issue |
| **多语言 Prompt** | 西语/葡语/日语/韩语/泰语等语言的电商 Prompt 模板 | Issue 或 PR |
| **平台数据更新** | 佣金率变化、新功能上线、政策更新等 | Issue |
| **合规信息更新** | 各国认证要求变化（KC/CE/EPR 等） | Issue |
| **Fact-check 修正** | 发现数据不准确？帮忙修正并提供来源 | Issue 或 PR |

### 社交媒体内容（ 新增方向）

Path E 社交媒体指南特别需要：
- 各平台的算法变化和最新最佳实践
- 达人合作的真实案例和 ROI 数据
- 各平台广告投放的实操经验和基准数据
- 跨平台内容复用的工作流分享

### 翻译贡献（ 新增方向）

中英日三语已全部完成（各 68 章，见 [i18n/STATUS.md](i18n/STATUS.md)）。欢迎：
- 英文翻译：paths/ 下的核心模块
- 日文翻译：特别是 Amazon JP 和 Rakuten 相关内容
- 西班牙语翻译：特别是 Mercado Libre 相关内容
- 翻译质量审核：检查现有翻译的准确性

### 提交 Notebook

通过 [Notebook 提交模板](https://github.com/kangise/ecommerce-ai-roadmap/issues/new?template=notebook_submission.md) 提交，要求：
- 可在 Google Colab 免费版运行
- 第一个代码单元格包含 `!pip install` 安装依赖
- 包含中英文注释

### 提交案例 | Case Study

通过 [案例提交模板](https://github.com/kangise/ecommerce-ai-roadmap/issues/new?template=case_study_submission.md) 提交，要求包含具体量化指标。

### 报告空链接

发现失效链接？通过 [空链接报告模板](https://github.com/kangise/ecommerce-ai-roadmap/issues/new?template=broken_link_report.md) 提交。

### 其他贡献

- **补充学习资源** 发现好的课程、视频、工具？提交 PR
- **修正内容** 信息过时或描述不准确？帮忙修正
- **翻译** 校对现有英日译文，或提议新语种（流程见 [scripts/gen_i18n_stubs.py](scripts/gen_i18n_stubs.py)）
- **数据验证** 帮忙验证平台费率、市场数据等数字的准确性

---

## Prompt 模板标准格式 | Prompt Template Format

如果你通过 PR 直接提交 Prompt 模板文件，请使用以下格式：

```markdown
## 模板 N: 模板名称

**场景**: 使用场景描述
**推荐工具**: ChatGPT / Claude / Gemini
**验证状态**: 已验证 / 社区贡献-待验证
**贡献者**: [@your-github-handle](https://github.com/your-github-handle)

### Prompt

```
你的 Prompt 内容...
```

### 预期输出示例

> 简要展示输出格式和质量

### 使用技巧

- Tip 1
- Tip 2

---

**分享此模板**: `直接链接 URL`
**来源**: [ecommerce-ai-roadmap](https://github.com/kangise/ecommerce-ai-roadmap)
```

---

---

## 写作约定 | Writing Conventions

新增或改写章节前请先读这一节。这些约定不是格式偏好，每一条对应一个真实踩过的坑。完整说明见 [F2 §4-5](src/0-foundations/f2-prompt-engineering.md)。

### 1. 正文不写模型型号

写**能力档位**（T1 前沿 / T2 主力 / T3 高速 / T4 本地），不写具体型号。型号、价格、上下文长度集中在 [模型矩阵](src/resources/model-matrix.md)，带校验日期。

> 换代时只改矩阵一个文件，不必翻 60 多章。唯一例外是 `f1-ai-evolution`——那章讲历史，型号是叙述对象。

### 2. Prompt 六块结构 + 护栏

```
<角色> <输入数据> <任务> <数据纪律> <输出格式> <自检>
```

**`<数据纪律>` 是必须的**，只要 Prompt 涉及数字、外部事实或对外文案。按场景选：

| 块 | 用在 | 防什么 |
|---|---|---|
| `<数据纪律>` | 问外部事实、要估算 | 模型编造销量/税率/搜索量，读者拿去做决策 |
| `<文案纪律>` | 生成对外文案 | 编造产品没有的功能认证；替卖家承诺退款时效 |
| `<输入数据边界>` | 需要粘贴数据 | 粘进去的竞品评论里一句"忽略以上要求"劫持分析 |
| `<计算纪律>` | 财务/库存计算 | 用假设的参数补齐，结果无法复核 |

可直接粘贴的块见 [F2 §4.3](src/0-foundations/f2-prompt-engineering.md)。

### 3. 章节骨架

指南章需要四件套：章节导航 · 本模块你将 · 常见陷阱 · 完成标志。案例页和资源页不套用这个模板。

### 4. 三语同步

`src/` 是中文源，`i18n/en/src` 和 `i18n/ja/src` 结构完全对应。**改中文就要同步改英日**，否则 `python3 scripts/gen_i18n_stubs.py --status` 会掉。

### 5. 动章节编号时

改 `## N.` 会连带影响三处：导航项、导航的序号标签、所有 `### N.x` 子节号。可靠做法是先构建，再从产物 HTML 的 `id="..."` 反向核对：

```bash
mdbook build && mdbook build i18n/en && mdbook build i18n/ja
```

注意标题里的冒号在锚点中会变成连字符。

### 6. 提交前自检

```bash
mdbook build . && mdbook build i18n/en && mdbook build i18n/ja   # 三本书都要 0 ERROR
python3 scripts/gen_i18n_stubs.py --status                        # 三语章节数须相等
```

---

## PR 提交流程 | PR Workflow

1. Fork 仓库
2. 创建分支 (`git checkout -b add-prompt-xxx`)
3. 修改内容
4. 确保通过质量检查清单（见 PR 模板）
5. 提交 PR，简要说明更改

### 资源提交标准

- 内容质量高，对电商从业者有实际帮助
- 优先推荐免费或有免费层级的资源
- 注明资源类型（课程 / 视频 / 书籍 / 工具 / 文章）
- 简要说明为什么推荐

### 格式参考

```markdown
- [课程名称](URL) 一句话说明为什么推荐
- [YouTube: 视频/频道名](URL) 一句话说明
- *书名* (作者) 一句话说明
- [工具名](URL) 一句话说明用途
```

---

## 问题反馈 | Feedback

- [提交 Issue](https://github.com/kangise/ecommerce-ai-roadmap/issues)
- [查看路线图](roadmap/README.md)
