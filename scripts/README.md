# scripts/

维护脚本。这里列的每一个都真实存在——早先的版本描述了一批从没写过的目录和脚本，已删除。

| 文件 | 作用 |
|------|------|
| `verify_content.py` | 内容校验套件。CI 在构建之后跑，任何一项非零就让部署失败 |
| `apply_indent.py` | 把手工重建好的代码块缩进按行套用到三语树 |
| `gen_i18n_stubs.py` | 生成 EN/JA 章节骨架，并统计翻译覆盖率 |
| `link-status.json` | 外链探测结果缓存，由 `verify_content.py --probe-links` 写入 |
| `fact_review.py` | 事实复核队列：批次到期时间、余量、过期分布 |
| `watch_sources.py` | 上游 API 规范巡检：变更时指出受影响的约束、代码和章节 |
| `audit_content.py` | 内容审计报告：有效性、完整性、友好度三个维度 |
| `setup/setup_environment.sh` | 本地环境准备 |


## fact_review.py

`M7` 负责纪律：每条有时效的事实必须归属于一个评审批次，批次到期日须早于时效红线
（18 个月）减去 3 个月提前量。但 M7 只在失败状态下报错——批次已逾期，或事实已过期。
两者之间没有输出，维护者无法直接查询本季度应复核的内容，只能手动查阅 YAML 并计算日期。

本脚本提供该查询，并报告 M7 无法呈现的两项信息：

- **余量（slack）** — 批次到期日与该批次最早事实失效日之间的间隔月数。M7 使用 `>` 判定，
  余量为 0 仍然合法，但意味着任何延期都会直接导致门禁失败。
- **过期悬崖** — 同一月份标注的事实会在同一月份集中过期。一次批量复核会使下一次复核
  同样集中。

```bash
python3 scripts/fact_review.py                  # 完整队列
python3 scripts/fact_review.py --list           # 列出每条事实
python3 scripts/fact_review.py --batch <id>     # 查看单个批次
python3 scripts/fact_review.py --due-within 90  # 90 天内有批次到期则 exit 1
python3 scripts/fact_review.py --json           # 机器可读
```

只有 `--due-within` 返回非零——本脚本是报告，不是门禁。未到期的日期不应导致构建失败。
周检工作流以 `continue-on-error` 方式调用，将队列输出到日志。

> 当前状态：345 条事实均标注为 `2026-08`，将于 `2028-02` 集中过期；
> `evidence-and-social` 批次余量为 0。两者均为排期问题，与内容质量无关。



## watch_sources.py

`fact_review.py` 按时间表安排人工复核平台**规则**，这是处理政策变化的正确方式——
政策所在的页面无法抓取：Amazon Seller Central 帮助页跳转登录，Shopify 帮助中心对
自动请求返回 403，OpenAI 文档由客户端渲染。对这些 URL 做哈希监控只会得到一个永不
触发的监控器，并暗示了并不存在的覆盖范围。

本脚本覆盖另一半：runtime 所依赖的**机器可读 API 接口**，变更既可检测也可操作。
监控清单在 [`maintenance/source-watch.yaml`](../maintenance/source-watch.yaml)，
每个条目必须声明变更后应复核哪些约束、代码和章节。

```bash
python3 scripts/watch_sources.py            # 与已记录状态比对
python3 scripts/watch_sources.py --update   # 比对并记录新状态
python3 scripts/watch_sources.py --list     # 不联网，查看监控清单
```

默认返回 0。上游有提交不等于有问题，需要人判断是否触及所声明的范围，因此不作为门禁；
如需在 CI 中阻断，用 `--fail-on-change`。周检工作流以 `continue-on-error` 调用并写入状态。

未认证的 GitHub API 限速 60 次/小时，设置 `GITHUB_TOKEN` 可提高。


## audit_content.py

门禁套件回答"有没有坏掉"，应当长期为 0。本脚本回答另一个问题——"内容是否够好"，
**预期会有发现**。这些是判断题不是缺陷，因此不作为门禁，恒返回 0。

它要补的洞：`M1` 要求正文里的数字带来源、核验日期或对冲词，但
`prose_lines()` 会跳过所有以 `|` 开头的行——**表格豁免**。对规格表这是合理的
（"标题上限 200 字符"不需要引用），但市场规模数字也在表格里，而那些恰恰是易变、
高风险的：GMV、MAU、市场份额、增长率、效率提升百分比。`V1` 覆盖的正是这个盲区。

```bash
python3 scripts/audit_content.py             # 全部
python3 scripts/audit_content.py --axis V    # 只看有效性
python3 scripts/audit_content.py --only V1 --list
python3 scripts/audit_content.py --json
```

| 维度 | 检查 |
|------|------|
| 有效性 | `V1` 表格中无来源的市场规模数字 · `V2` 大量数字但全篇零外链的章节 · `V3` 上次探测未返回 200 的引用链接，按应采取的动作分组 |
| 完整性 | `C1` 参考类页面缺少局限性说明 · `C2` platforms.yaml 中无对应章节的平台 · `C3` 篇幅显著低于同路径中位数的章节 |
| 友好度 | `F1` 无可运行 Prompt 的指南章 · `F2` 长章节缺页内导航 · `F3` 长小节无三级标题 |

判断引用是否存在时必须**剔除代码围栏**：每个 Prompt 模板的数据纪律块都含有
"标注来源"字样，按关键词匹配会让一个零引用的章节通过——56 个无源数字正是这样
藏在绿色门禁背后的。

## verify_content.py

当前共十八项检查，各自返回一个计数，全为 0 才算通过。全仓库的
43 项门禁与 14 个分组见 [`CONTRIBUTING.md`](../CONTRIBUTING.md#gate-reference-42-gates-14-groups)。

```bash
python3 scripts/verify_content.py            # CI 跑的这个（全离线）
python3 scripts/verify_content.py --list     # 连具体条目一起打印
python3 scripts/verify_content.py --only M1  # 只跑一项
```

**结构类**——坏掉的东西，不是"不够好"的东西：

- `anchors` / `xanchors` / `links` — 页内锚点、跨文件锚点、跨文件链接
- `python` — 每个 ` ```python ` 块可编译
- `parity` — `src/` 下每个文件在 en/ja 都存在，且结构指纹（标题层级序列、代码块数、表格行数）一致

**门禁类**——本书对自己的内容纪律要求：

- `M1` 正文里的硬数字必须有来源、核验日期、对冲词，或小节标记
- `M2` 每个指南章都有"什么时候这套不管用"小节
- `M4` 每个外链都探测过且不是死链
- `M5` 没有零入链的正文页
- `M6` 章节编号连续，且导航里可见的序号与它指向的锚点编号一致
- `N1` Prompt 块里的六块标签开了就要闭
- `N2` 代码里 import 的第三方库，本章说过怎么装
- `N3` 每个 Prompt 都有自检块
- `N4` 每个 Prompt 都声明输出格式
- `N5` 自检内容不能机械重复
- `N6` 三语 Prompt 结构保持一致
- `M7` 有时效的事实在 18 个月后自动过期，并覆盖维护责任人
- `M8` 表格里的市场规模数字（GMV/MAU/份额/用户数）必须带来源、核验日期或 allowlist 条目

`N1` 的计数比看上去麻烦：`<角色>文字</角色>` 写在同一行，而纪律块正文会**提到**标签名（"只使用 <输入数据> 中出现的数字"）。规则是先消掉同行成对的，再只认行首——否则正确的写法会被大量误报。

`N2` 认 `pip/pip3/uv pip/python -m pip install`、`conda install`、`poetry add`，以及 `包名==版本` 形式的清单。开头标了 `# 概念代码` / `# Conceptual` 的块不计入——它没有声称自己能跑。

### 外链探测

`M4` **不做实时探测**，它读缓存。新加的链接如果没探测过就是失败——这样能强制在合并前验活，同时构建不依赖网络和各家的爬虫策略。

```bash
python3 scripts/verify_content.py --probe-links   # 探测新链接，刷新 scripts/link-status.json
```

判死之前一律回退 GET 复验：Kaggle Learn 和 shopify.com/magic 都对 HEAD 返回 404 但 GET 正常，把它们当死链会让你去改本来能用的链接。403/429 算软失败（很多站点单纯拒绝脚本请求）。

### 锚点规则的验证方式

`slugify()` 复刻的是 mdBook 的行为，而这个行为有几处反直觉的地方。它不是照文档写的，是对着构建产物逐个 heading 对拍出来的：

```bash
mdbook build
python3 scripts/verify_content.py --anchors-vs-build docs
```

改动 `slugify()` 之后、升级 mdBook 之后，都该重跑一次。当前 pin 的 0.5.4 上有三处需要注意：

1. **智能标点默认开着**——`--` 会变成 en dash、`---` 变成 em dash，随后作为标点被整个丢掉；单个 `-` 会保留。所以 `A -- B` 的锚点里那两个连字符是不存在的。
2. **heading 文本先 trim**——前导空格不会变成前导连字符。
3. **小写走 Unicode 全量**，不是 `to_ascii_lowercase`。

另外 setext 标题（正文行紧跟 `---`）**故意不建模**。mdBook 会把它渲染成 H2，但在本书里每一次出现都是意外（一行徽章、一段结尾正文被变成了标题）。让这个分歧暴露出来，比吸收它更有用——`--anchors-vs-build` 会把它报成"这一页对不上"。

## 内容写作约定

新增章节时要跟上的两件事，`verify_content.py` 会检查：

**失效边界小节**，不带编号（追加不触发重编号），插在该章**最后一个 H2 之前**——先知道边界，再去勾"完成标志"。标题固定为：

| 树 | 标题 |
|---|---|
| `src` | `## 什么时候这套不管用` |
| `i18n/en/src` | `## When this doesn't work` |
| `i18n/ja/src` | `## この方法が効かないとき` |

要点写具体失效条件（数据量、品类、团队规模、平台状态），格式是「**条件。** 后果和该怎么办」，不是免责声明。

**claims 标记**，HTML 注释形式，读者看不见。放在首个 H2 之前覆盖整章，否则覆盖到下一个 H2。每个标记都要配一句读者能看见的说明：

| 标记 | 含义 |
|---|---|
| `<!-- claims: illustrative -->` | 数字是为说明构造的，不是实测（走查案例、公式演算、执行轨迹） |
| `<!-- claims: verified YYYY-MM -->` | 可核实但有保质期的事实（工具定价、平台费率与阈值） |
| `<!-- claims: benchmark -->` | **本书建议的判断阈值**，不是别人的测量结果 |

`benchmark` 最容易用错：平台公布的统计、第三方调研数字都不是 benchmark。**含义错的标签比没有标签更糟**。

## apply_indent.py

```bash
python3 scripts/apply_indent.py b-developers/b1-data-pipeline.md 7 /tmp/fixed.py
python3 scripts/apply_indent.py <章节> <块序号> <修好的文件> --only i18n/en/src
```

代码块缩进只能手工重建，不能写启发式：`if x:` 后面跟一串非终止语句时，"块在哪结束"在语法上不可判定，猜出来的错答案看着像对的，而读者会照抄。

三语树在代码围栏内逐行对齐，所以中文侧算出的缩进可以直接套用。这个前提偶尔会破（翻译后的 docstring 可能多换一行）——**不要为了绕过去而放宽行数校验**，那道校验正是防止写坏的东西。用 `--only <tree>` 分树套用。
