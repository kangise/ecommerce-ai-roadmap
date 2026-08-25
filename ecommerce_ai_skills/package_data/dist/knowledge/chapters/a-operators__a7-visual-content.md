# A7. AI 图片与视频生成 | AI Visual Content Creation

> **路径**: Path A: 运营人 · **模块**: A7
> **最后更新**: 2026-07-31
> **难度**: 中级
> **预计时间**: 每天 30 分钟，1-2 周
> **前置模块**: [A2 Listing 与内容创作](a2-listing-optimization.md)


---

## 章节导航

1. [为什么 AI 视觉内容是 2026 年的必修课](#1-为什么-ai-视觉内容是-2026-年的必修课)
2. [AI 产品图片生成](#2-ai-产品图片生成)
3. [AI 产品视频生成](#3-ai-产品视频生成)
4. [各平台图片/视频规格](#4-各平台图片视频规格)
5. [AI 视觉内容工作流](#5-ai-视觉内容工作流)
6. [Prompt 模板](#6-prompt-模板)
7. [工具对比与推荐](#7-工具对比与推荐)
8. [常见陷阱](#8-常见陷阱)
9. [完成标志](#9-完成标志)

---

## 本模块你将学会

- 用 AI 生成专业级产品图片（白底图、场景图、生活方式图）
- 用 AI 制作产品视频（展示视频、广告视频、社交媒体视频）
- 掌握各平台的图片/视频规格要求
- 建立一套 AI 视觉内容批量生产工作流

> **核心理念**：2026 年，AI 产品图片可以降低 80% 的摄影成本，生活方式图片的转化率比纯白底图高 22-30%（[Entrepreneur](https://apac.entrepreneur.com/news-and-trends/how-smart-entrepreneurs-are-cutting-product-photography/501040)）。AI 视频生成市场 2025 年达 $71.68 亿，年增长 20%（[Fortune Business Insights](https://framepack.cc/articles/ai-video-tools-comparison-framepack)）。不会用 AI 做视觉内容的卖家，正在失去竞争力。

Content rephrased for compliance with licensing restrictions.

---

## 1. 为什么 AI 视觉内容是 2026 年的必修课

### 1.1 数据说话

| 指标 | 数据 | 来源 |
|------|------|------|
| AI 产品图片成本降低 | 80% | Entrepreneur 2026 |
| 生活方式图 vs 白底图转化率提升 | 22-30% | A/B 测试研究 |
| AI 视频生成市场规模（2025） | $71.68 亿 | Fortune Business Insights |
| AI 视频市场预计（2032） | $256 亿 | Fortune Business Insights |
| Amazon 产品视频对转化率的影响 | 通常为正，幅度按品类差异大 | 需自行 A/B |
| 有视频的 Listing 停留时间 | +2x | 行业基准 |

### 1.2 AI 视觉内容的三个层次

```
Level 1：AI 辅助编辑（最简单）
背景移除/替换（PhotoRoom、Remove.bg）
图片增强（放大、去噪、调色）
批量裁剪和调整尺寸
适合：已有产品实拍图，需要快速优化

Level 2：AI 生成场景图（中级）
产品实拍图 + AI 生成背景/场景
工具：Midjourney、Nano Banana Pro、Ideogram、PhotoRoom AI Staging
不需要摄影棚，不需要模特
适合：需要生活方式图但预算有限

Level 3：AI 完全生成（高级）
从文字描述生成产品图片
从产品图片生成视频
AI 虚拟模特（服装品类）
适合：新品上市前的概念验证、社交媒体内容批量生产
```

---

## 2. AI 产品图片生成

<!-- claims: verified 2026-08 -->

> 本节引用的平台指标要求与费率核验日期: 2026-08。平台随时会调，以各自后台的官方说明为准。


### 2.1 工具全景

| 工具 | 核心功能 | 价格 | 最适合 |
|------|---------|------|--------|
| **Midjourney** | 高质量 AI 图片生成 | $10/月起 | 创意场景图、生活方式图 |
| **GPT Image 2**（ChatGPT） | 文字→图片 | $20/月（ChatGPT Plus） | 快速概念验证 |
| **Ideogram** | 文字渲染准确 | 免费/付费 | 包含文字的图片（标签、包装） |
| **PhotoRoom** | 背景移除+AI 场景 | 免费/Pro $10/月 | 产品白底图→场景图 |
| **Canva AI** | 图片编辑+AI 生成 | 免费/Pro $13/月 | 非设计师的全能工具 |
| **Adobe Firefly** | 专业级 AI 编辑 | $5/月起 | 已用 Adobe 的团队 |
| **ZMO AI** | 电商专用 AI 模特 | 付费 | 服装品类虚拟模特 |
| **Nano Banana AI** | Amazon 产品图专用 | 付费 | Amazon Listing 图片 |

### 2.2 Amazon 产品图片 AI 生成实操

**白底主图（Main Image）**

Amazon 主图要求：纯白背景（RGB 255,255,255），产品占画面 85%+，≥1000x1000px。

```
AI 工作流：
1. 手机拍摄产品照片（任何背景）
2. PhotoRoom / Remove.bg 一键去背景
3. 自动替换为纯白背景
4. 调整产品位置和大小（占画面 85%+）
5. 导出 2000x2000px（Amazon 推荐）

时间：2 分钟/张（vs 传统摄影 30 分钟/张）
成本：$0（PhotoRoom 免费版）
```

**场景图/生活方式图（Lifestyle Images）**

```
方法 1：PhotoRoom AI Staging（最简单）
1. 上传产品白底图
2. 选择场景模板（厨房/客厅/户外/办公桌）
3. AI 自动将产品放入场景
4. 调整光影和角度
时间：1 分钟/张

方法 2：Midjourney（最高质量）
1. 上传产品参考图到 Midjourney
2. 使用 Prompt 描述想要的场景
3. 生成 4 张变体，选择最佳
4. 用 Photoshop/Canva 微调
时间：5-10 分钟/张

<文案纪律>
- 不要写出产品实际不具备的功能、材质、认证或效果。我在上面没写的属性，一律不要出现在文案里——这是 Listing 被下架和被投诉虚假宣传的头号原因
- 需要某个卖点才能写好但我没提供时，先列出你需要我补充什么，不要自行发挥
- 涉及疗效、安全、环保、专利的表述，单独标出来提示我人工核对
</文案纪律>
```

**Midjourney 产品场景图 Prompt 模板：**

```
你是一个 Midjourney Prompt 专家，专注于电商产品图片。

产品：[名称]
产品外观：[颜色、材质、尺寸描述]
目标场景：[使用场景描述]
目标平台：[Amazon/Shopify/Instagram]
风格：[简约/温馨/专业/户外/现代]

请生成 5 个 Midjourney Prompt，每个包含：
1. 完整的英文 Prompt（Midjourney 只接受英文）
2. 推荐的参数（--ar 比例、--v 版本、--s 风格化程度）
3. 预期效果描述

5 个角度：
- 角度 1：产品特写（白色/浅色背景，突出细节）
- 角度 2：使用场景（人物使用产品的生活方式图）
- 角度 3：环境场景（产品在自然环境中）
- 角度 4：对比/尺寸参考（产品与常见物品对比）
- 角度 5：创意/概念图（适合社交媒体的创意构图）

Midjourney Prompt 格式要求：
- 以主体描述开头
- 包含光线描述（soft lighting, studio lighting, natural light）
- 包含风格描述（photorealistic, commercial photography, lifestyle）
- 包含技术参数（--ar 1:1 --v 6.1 --s 250）

<数据纪律>
- 涉及市场数据、搜索量、竞品表现、法规条款、费率的具体数字或事实，只能来自我提供的信息。**我没给的不要凭记忆补**——这类事实变化快，你记忆里的版本可能已经过期
- 需要某个事实才能判断时，告诉我该去哪个官方来源核实，然后停下来问我
- 每个结论标注来源：[我提供的信息] 或 [模型推测]
</数据纪律>
<输出格式>
交付 5 个 Midjourney Prompt，编号列表，对应 5 个角度各 1 个（特写/使用场景/环境场景/尺寸参考/创意），每个含 3 个标注项：① 完整英文 Prompt ② 推荐参数（--ar、--v、--s）③ 预期效果描述。
</输出格式>

<自检>
交付前逐条核对并报告结果：
① 恰好 5 个 Prompt，5 个角度各 1 个，顺序正确
② 每个 Prompt 以主体描述开头，包含光线 + 风格 + 技术参数
③ 产品属性（颜色/材质/尺寸）与提供的产品信息完全一致——无虚构属性
④ 用于 Amazon 主图的 Prompt 不得添加文字/logo/水印；文字叠加只允许出现在副图类 Prompt <!-- ref: amazon.product_image.main.no_text_overlay -->
⑤ 商业用途优先选择有明确商业许可的工具，并保留 Prompt 与生成记录 <!-- ref: content.ai_generated.commercial_license -->
</自检>
```

### 2.3 信息图/卖点图 AI 生成

Amazon 的辅图中，信息图（Infographic）是转化率最高的图片类型之一：

```
AI 信息图工作流：
1. 用 ChatGPT/Claude 生成卖点文案（每个卖点 ≤8 个词）
2. 用 Canva AI 选择信息图模板
3. 放入产品图片 + 卖点文案
4. AI 自动调整布局和配色
5. 导出多个尺寸（Amazon/Shopify/社交媒体）

Canva AI Prompt：
"Create a product infographic for [产品名], highlighting these 5 features:
1. [卖点 1]
2. [卖点 2]
3. [卖点 3]
4. [卖点 4]
5. [卖点 5]
Style: clean, modern, white background with accent color [品牌色]"
```

---

## 3. AI 产品视频生成

### 3.1 视频工具全景

| 工具 | 核心功能 | 价格 | 最适合 |
|------|---------|------|--------|
| **CapCut** | 视频剪辑+AI 功能 | 免费/Pro $8/月 | TikTok/Reels 短视频 |
| **Runway Gen-4.5** | 图片/文字→视频，剪辑控制强 | 订阅制 | 需要精细创意控制的广告片 |
| **Veo 3.1**（Google Flow） | 文字/图片→视频，自带音频生成 | 订阅制 | 电影感镜头、带声音的成片 |
| **Kling 3** | 图片→视频，运动真实感强 | 订阅制 | 产品动态展示 |
| **Seedance 2** | 图片→视频，长镜头规划 | 订阅制 | 广告、品牌场景、分镜驱动的制作 |
| **Magic Hour** | 产品图→广告视频 | 付费 | 广告素材批量生成 |
| **Canva Video** | 模板化视频制作 | 免费/Pro $13/月 | 非专业人士 |
| **InVideo AI** | AI 自动生成视频 | $25/月起 | 完整的产品视频 |
| **HeyGen** | AI 虚拟主播 | $24/月起 | 产品介绍/教程视频 |
| **Synthesia** | AI 虚拟人视频 | $22/月起 | 多语言产品介绍 |

### 3.2 Amazon 产品视频 AI 制作

Amazon 允许在 Listing 中上传产品视频，有视频的 Listing 转化率通常更高——具体幅度按品类和视频质量差很多，用 A/B 或上线前后对比测：

```
Amazon 产品视频类型：

1. 产品展示视频（30-60 秒）
多角度展示产品外观
核心功能演示
尺寸对比
AI 工具：Runway（图片→视频）+ CapCut（剪辑）

2. 使用教程视频（60-120 秒）
开箱过程
安装/设置步骤
使用演示
AI 工具：HeyGen（AI 虚拟主播讲解）+ CapCut

3. 对比视频（30-60 秒）
与竞品的视觉对比
Before/After 效果
AI 工具：CapCut（分屏对比模板）

4. 品牌故事视频（60-90 秒）
品牌理念
制造过程
用户故事
AI 工具：InVideo AI（从文字生成完整视频）
```

### 3.3 社交媒体视频 AI 批量生产

```
从 1 个产品素材生成 10+ 个视频的工作流：

Step 1: 素材准备
产品白底图 5 张
产品使用场景图 3 张（AI 生成）
产品实拍视频片段 30 秒（手机拍摄即可）
产品卖点文案（ChatGPT 生成）

Step 2: AI 生成视频变体
Runway：产品图→3 秒动态展示 × 5 个角度
CapCut：模板化剪辑 × 3 种风格（产品展示/教程/对比）
Pika：产品图→动态背景 × 3 种场景
总计：11 个视频素材

Step 3: 平台适配
Amazon 产品视频：横版 16:9，30-60 秒
TikTok/Reels：竖版 9:16，15-30 秒
YouTube Shorts：竖版 9:16，30-60 秒
Pinterest：竖版 2:3 或 9:16
总计：每个素材 × 4 个平台 = 44 个视频

Step 4: 文案+字幕
ChatGPT 生成各平台文案
CapCut AI 自动生成字幕
批量导出
```

> **相关阅读**: [E1 Instagram Reels](../e-social-media/e1-instagram-facebook-ai-guide.md) Reels 视频创作方法论 · [E2 YouTube](../e-social-media/e2-youtube-ai-guide.md) YouTube 视频脚本和缩略图 · [D2 TikTok Shop](../d-platforms/tiktok-shop-ai-guide.md) TikTok 短视频批量生产

---

## 4. 各平台图片/视频规格

| 平台 | 图片尺寸 | 视频尺寸 | 视频时长 | 特殊要求 |
|------|---------|---------|---------|---------|
| Amazon 主图 | 2000x2000（1:1） | 16:9 | 30-120 秒 | 白底，产品占 85%+ |
| Amazon 辅图 | 2000x2000（1:1） | | | 场景图/信息图/对比图 |
| Shopify | 自定义 | 自定义 | 自定义 | 建议 2048x2048 |
| Instagram Feed | 1080x1080（1:1） | 9:16 | 15-90 秒 | 精致美学风格 |
| Instagram Stories | 1080x1920（9:16） | 9:16 | ≤60 秒 | 全屏竖版 |
| TikTok | | 1080x1920（9:16） | 15-60 秒 | 竖版，前 3 秒是关键 |
| YouTube 缩略图 | 1280x720（16:9） | 16:9 | 不限 | 高对比度，大文字 |
| YouTube Shorts | | 1080x1920（9:16） | ≤60 秒 | 竖版 |
| Pinterest | 1000x1500（2:3） | 9:16 | 15-60 秒 | 竖版，文字叠加 |
| Walmart | 2000x2000（1:1） | 16:9 | 30-120 秒 | 白底主图 |
| eBay | 1600x1600（1:1） | | | 白底推荐 |

---

## 5. AI 视觉内容工作流

### 5.1 新品上市视觉内容 SOP

```
Day 1: 产品实拍（手机即可）
白底图 5 张（不同角度）
手持/使用图 3 张
包装/配件图 2 张
30 秒使用视频片段

Day 2: AI 图片生成
PhotoRoom：白底图优化（去背景+调整）
Midjourney：生活方式场景图 5 张
Canva AI：信息图/卖点图 3 张
尺寸对比图 1 张
总计：~15 张图片

Day 3: AI 视频生成
Runway：产品展示视频 1 个（30 秒）
CapCut：TikTok/Reels 短视频 3 个
HeyGen：产品介绍视频 1 个（60 秒，AI 虚拟主播）
总计：~5 个视频

Day 4: 平台适配+上传
Amazon：主图+6 张辅图+1 个视频
Shopify：产品页图片+视频
社交媒体：各平台尺寸适配
广告素材：Meta Ads/Google Ads 图片+视频

传统方式：2-3 周 + $2000-5000
AI 方式：4 天 + $50-100（工具订阅费）
```

---

## 6. Prompt 模板

> **本库 Prompt 写法约定**：下面的模板可直接用，但涉及数字、预测、推荐的场景，建议把 [F2 §4.3 的数据纪律块](../0-foundations/f2-prompt-engineering.md#43-可以直接粘的数据纪律块)粘进去——它禁止模型编造你没提供的数据，是这类 Prompt 最容易出事的地方。

### 6.1 Midjourney 电商产品图 Prompt 库

**白底产品图：**
```
[产品描述], product photography, pure white background, studio lighting,
high resolution, commercial photography, centered composition,
sharp focus, no shadows --ar 1:1 --v 6.1 --s 100
<输出格式>
生成 4 张变体图（Midjourney 默认网格）：纯白背景上的产品图，影棚灯光、无阴影、无文字。
</输出格式>

<自检>
交付前逐条核对并报告结果：
① 背景为纯白（RGB 255,255,255）且无阴影
② 图中无文字、logo、水印或道具 <!-- ref: amazon.product_image.main.no_text_overlay -->
③ 产品颜色/形状/细节与真实产品图完全一致
④ 记录生成 Prompt 与日期，作为商业用途的创作证据 <!-- ref: content.ai_generated.commercial_license -->
</自检>
```

**生活方式场景图：**
```
[产品描述] in use, [场景描述], lifestyle photography, natural lighting,
warm tones, shallow depth of field, editorial style,
photorealistic --ar 1:1 --v 6.1 --s 250
<输出格式>
生成 4 张变体图：产品处于描述的生活场景中，自然光、暖色调、写实风格。
</输出格式>

<自检>
交付前逐条核对并报告结果：
① 产品清晰可见，颜色/形状/细节与真实产品一致
② 场景与光线符合要求的场景描述
③ 若用作 Amazon 副图，图内叠加文字不超过 20 个词 <!-- ref: amazon.product_image.secondary_text.max_words -->
④ 记录生成 Prompt 与日期，作为商业用途的创作证据 <!-- ref: content.ai_generated.commercial_license -->
</自检>
```

**信息图背景：**
```
clean minimal background for product infographic, [品牌色] accent color,
geometric shapes, modern design, negative space,
professional layout --ar 1:1 --v 6.1 --s 150
<输出格式>
生成 4 张变体图：产品信息图用的干净极简背景，品牌色点缀、几何风格、现代设计、为文字留白。
</输出格式>

<自检>
交付前逐条核对并报告结果：
① 背景使用指定品牌点缀色，几何-现代风格
② 预留卖点文字叠加的留白（图内不烧录文字）
③ 拟叠加文字：标题 ≤5 个词，副标题 ≤15 个词 <!-- ref: amazon.product_image.secondary_title.max_words --> <!-- ref: amazon.product_image.secondary_subtitle.max_words -->
④ 记录生成 Prompt 与日期，作为商业用途的创作证据 <!-- ref: content.ai_generated.commercial_license -->
</自检>
```

### 6.2 AI 视频脚本生成

```
你是一个电商产品视频脚本专家。

产品：[名称]
视频类型：[产品展示/使用教程/对比/品牌故事]
目标平台：[Amazon/TikTok/Instagram/YouTube]
视频时长：[30/60/120 秒]

请生成视频脚本，包含：
1. 每个镜头的画面描述（用于 AI 视频生成工具）
2. 字幕/旁白文字
3. 时长标注
4. 推荐的 AI 工具（每个镜头用什么工具生成）
5. 背景音乐风格建议

<数据纪律>
- 涉及市场数据、搜索量、竞品表现、法规条款、费率的具体数字或事实，只能来自我提供的信息。**我没给的不要凭记忆补**——这类事实变化快，你记忆里的版本可能已经过期
- 需要某个事实才能判断时，告诉我该去哪个官方来源核实，然后停下来问我
- 每个结论标注来源：[我提供的信息] 或 [模型推测]
</数据纪律>

<文案纪律>
- 不要写出产品实际不具备的功能、材质、认证或效果。我在上面没写的属性，一律不要出现在文案里——这是 Listing 被下架和被投诉虚假宣传的头号原因
- 需要某个卖点才能写好但我没提供时，先列出你需要我补充什么，不要自行发挥
- 涉及疗效、安全、环保、专利的表述，单独标出来提示我人工核对
</文案纪律>
<输出格式>
交付分镜表格：镜头号 | 时长标记 | 镜头描述（供 AI 视频工具）| 字幕/口播文字 | 推荐 AI 工具 | 背景音乐风格。
</输出格式>

<自检>
交付前逐条核对并报告结果：
① 每个镜头 6 列齐全（镜头号、时长、描述、字幕/口播、工具、音乐）
② 各镜头时长合计与要求的视频长度（30/60/120 秒）一致
③ 未出现产品信息之外的功能/材质/认证/效果；相关表述单独标出待人工核对
④ 若使用 AI 配音/虚拟形象/生成画面，需注明 EU AI 法案第 50 条透明度标注义务 <!-- ref: eu.ai_act.transparency -->
⑤ 推荐的 AI 工具须有明确的商业许可 <!-- ref: content.ai_generated.commercial_license -->
</自检>
```

---

## 7. 工具对比与推荐

### 7.1 按预算推荐

| 预算 | 图片工具 | 视频工具 | 月成本 |
|------|---------|---------|--------|
| 免费 | PhotoRoom 免费版 + Canva 免费版 | CapCut 免费版 | $0 |
| $20-50/月 | Midjourney + PhotoRoom | CapCut Pro + Pika | $26-36 |
| $50-100/月 | Midjourney + Adobe Firefly | Runway + CapCut + HeyGen | $54-80 |
| $100+/月 | 全套工具 | 全套工具 | $100+ |

### 7.2 按品类推荐

| 品类 | 最需要的图片类型 | 推荐工具 |
|------|----------------|---------|
| 电子产品 | 白底图+功能信息图+尺寸对比 | PhotoRoom + Canva |
| 家居 | 场景图（房间内效果） | Midjourney + PhotoRoom AI Staging |
| 服装 | 虚拟模特图 | ZMO AI + Lalaland.ai |
| 美妆 | 使用效果图+Before/After | Midjourney + Canva |
| 食品 | 美食摄影风格 | Midjourney（美食 Prompt） |
| 户外运动 | 户外场景图 | Midjourney（户外场景） |

---

## 8. 常见陷阱

<!-- claims: benchmark -->

> 这里的数值是判断自己数据用的参考线，不是市场实测均值。跑过一轮后用你自己的中位数替换。


### 陷阱 1：AI 生成的图片直接用作 Amazon 主图
Amazon 主图要求是产品的真实照片。AI 生成的场景图可以用作辅图，但主图建议用实拍+AI 去背景。

### 陷阱 2：忽略各平台的图片政策
Amazon 禁止在主图上添加文字、logo、水印。AI 生成的信息图只能用作辅图。

### 陷阱 3：AI 生成的产品细节不准确
AI 可能改变产品的颜色、形状、按钮位置等细节。生成后必须人工检查产品细节的准确性。

### 陷阱 4：过度依赖 AI 生成，忽略实拍
AI 场景图很好，但买家也需要看到真实的产品照片。建议比例：实拍 50% + AI 生成 50%。

### 陷阱 5：版权风险
Midjourney 等工具生成的图片版权归属仍有争议。商业使用建议选择明确授予商业许可的工具（Midjourney 付费版、Adobe Firefly、Canva Pro）。

---

## 什么时候这套不管用

- **产品的实物细节必须真实。** AI 生成图能做场景、能做氛围，做不了"这个扣子的实际质感"。买家收到货和图不符会直接触发退货和差评，某些平台还会判定为误导性图片。材质、颜色、尺寸相关的展示必须用实拍，AI 图只做场景和氛围补充。
- **平台把 AI 生成内容单列了。** 主图规则、AI 内容标注要求、素材审核标准这几年一直在动（EU AI Act 的透明度条款就直接管到这里，见 [A6](a6-compliance.md)）。上批量之前先确认目标平台当前对 AI 图的政策，别拿去年的理解做今年的量。
- **需要的是一致性而不是单张好图。** 同一产品的一组图（主图 + 场景 + 细节 + A+）要看起来是同一个品牌同一个产品。生成模型每次输出都有随机性，光影、色温、产品朝向都会飘。要一致性就得固定种子、用同一参考图做 img2img，或者干脆实拍打底再做后期。
- **品类靠图片建立信任。** 珠宝、手表、二手、高客单价的东西，买家会放大看细节找瑕疵。这些品类用 AI 生成图的收益远小于风险——一旦被发现是生成的，信任成本比省下的拍摄费高得多。

---

## 9. 完成标志

- [ ] 用 AI 为一个产品生成完整的图片套装（白底图+场景图+信息图）
- [ ] 用 AI 制作至少 1 个产品视频（30-60 秒）
- [ ] 建立 Midjourney 电商 Prompt 模板库
- [ ] 掌握至少 2 个 AI 图片工具和 1 个 AI 视频工具
- [ ] 完成一次 AI 图片 vs 传统摄影的成本对比

(a6-compliance.md) | [Path 总览](README.md) | [A8 定价 >](a8-pricing-strategy.md)
