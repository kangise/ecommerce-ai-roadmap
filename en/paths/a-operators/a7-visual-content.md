[🇨🇳 中文](../../../paths/a-operators/a7-visual-content.md) | 🇺🇸 English

# A7. AI Visual Content Creation

> **Path**: Path A: Operators · **Module**: A7
> **Last Updated**: 2026-03-14
> **Difficulty**: Intermediate
> **Estimated Time**: 30 minutes per day, 12 weeks
> **Prerequisite**: [A2 Listing & Content Creation](a2-listing-optimization.md)

[Hub Home](../../README.md) · [Path A Overview](README.md)

---

## Chapter Navigation

1. [Why AI Visual Content Is Essential in 2026](#1-why-ai-visual-content-is-essential-in-2026)
2. [AI Product Image Generation](#2-ai-product-image-generation)
3. [AI Product Video Generation](#3-ai-product-video-generation)
4. [Image/Video Specs by Platform](#4-imagevideo-specs-by-platform)
5. [AI Visual Content Workflow](#5-ai-visual-content-workflow)
6. [Prompt Templates](#6-prompt-templates)
7. [Tool Comparison & Recommendations](#7-tool-comparison--recommendations)
8. [Common Pitfalls](#8-common-pitfalls)
9. [Completion Checklist](#9-completion-checklist)

---

## What You'll Learn in This Module

- Generate professional-grade product images with AI (white background, lifestyle, and scene images)
- Create product videos with AI (showcase videos, ad creatives, social media videos)
- Understand image/video spec requirements across platforms
- Build a scalable AI visual content production workflow

> **Core Insight**: In 2026, AI product photography can reduce shooting costs by 80%, and lifestyle images convert 2230% better than plain white-background images ([Entrepreneur](https://apac.entrepreneur.com/news-and-trends/how-smart-entrepreneurs-are-cutting-product-photography/501040)). The AI video generation market reached $7.168 billion in 2025, growing 20% year-over-year ([Fortune Business Insights](https://framepack.cc/articles/ai-video-tools-comparison-framepack)). Sellers who aren't using AI for visual content are falling behind.

Content rephrased for compliance with licensing restrictions.

---

## 1. Why AI Visual Content Is Essential in 2026

### 1.1 The Numbers

| Metric | Data | Source |
|--------|------|--------|
| AI product photography cost reduction | 80% | Entrepreneur 2026 |
| Lifestyle image vs. white-background conversion lift | 2230% | A/B testing studies |
| AI video generation market size (2025) | $7.168B | Fortune Business Insights |
| AI video market projection (2032) | $25.6B | Fortune Business Insights |
| Amazon product video impact on conversion | +9.7% | Amazon internal data |
| Listing dwell time with video | +2x | Industry benchmark |

### 1.2 Three Levels of AI Visual Content

```
Level 1: AI-Assisted Editing (Easiest)
Background removal/replacement (PhotoRoom, Remove.bg)
Image enhancement (upscaling, denoising, color correction)
Batch cropping and resizing
Best for: Existing product photos that need quick optimization

Level 2: AI-Generated Scene Images (Intermediate)
Real product photo + AI-generated background/scene
Tools: Midjourney, DALL-E, Ideogram, PhotoRoom AI Staging
No studio needed, no models needed
Best for: Lifestyle images on a limited budget

Level 3: Fully AI-Generated (Advanced)
Generate product images from text descriptions
Generate videos from product images
AI virtual models (apparel categories)
Best for: Pre-launch concept validation, bulk social media content
```

---

## 2. AI Product Image Generation

### 2.1 Tool Landscape

| Tool | Core Feature | Price | Best For |
|------|-------------|-------|----------|
| **Midjourney** | High-quality AI image generation | From $10/mo | Creative scene & lifestyle images |
| **DALL-E 3** (ChatGPT) | Text → image | $20/mo (ChatGPT Plus) | Quick concept validation |
| **Ideogram** | Accurate text rendering | Free/Paid | Images with text (labels, packaging) |
| **PhotoRoom** | Background removal + AI scenes | Free/Pro $10/mo | White-background → scene images |
| **Canva AI** | Image editing + AI generation | Free/Pro $13/mo | All-in-one tool for non-designers |
| **Adobe Firefly** | Professional AI editing | From $5/mo | Teams already using Adobe |
| **ZMO AI** | E-commerce AI models | Paid | Virtual models for apparel |
| **Nano Banana AI** | Amazon product images | Paid | Amazon listing images |

### 2.2 Amazon Product Image AI Generation in Practice

**White-Background Main Image**

Amazon main image requirements: pure white background (RGB 255,255,255), product fills 85%+ of the frame, ≥1000x1000px.

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

**Scene / Lifestyle Images**

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
```

**Midjourney Product Scene Image Prompt Template:**

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
```

### 2.3 Infographic / Feature Highlight Image Generation

Among Amazon secondary images, infographics are one of the highest-converting image types:

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

## 3. AI Product Video Generation

### 3.1 Video Tool Landscape

| Tool | Core Feature | Price | Best For |
|------|-------------|-------|----------|
| **CapCut** | Video editing + AI features | Free/Pro $8/mo | TikTok/Reels short videos |
| **Runway Gen-3** | Text/image → video | From $12/mo | High-quality product showcase videos |
| **Pika** | Image → animated video | Free/Pro $8/mo | Product motion displays |
| **Magic Hour** | Product image → ad video | Paid | Bulk ad creative generation |
| **Canva Video** | Template-based video creation | Free/Pro $13/mo | Non-professionals |
| **InVideo AI** | AI auto-generated video | From $25/mo | Complete product videos |
| **HeyGen** | AI virtual presenter | From $24/mo | Product intro/tutorial videos |
| **Synthesia** | AI avatar video | From $22/mo | Multi-language product intros |

### 3.2 Amazon Product Video AI Production

Amazon allows product videos in listings. Listings with video see an average 9.7% conversion lift:

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

### 3.3 Bulk Social Media Video Production with AI

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

> **Related Reading**: [E1 Instagram Reels](../e-social-media/e1-instagram-facebook-ai-guide.md#2-instagram-vs-tiktok-vs-youtube-content-strategy-differences) Reels video creation methodology · [E2 YouTube](../e-social-media/e2-youtube-ai-guide.md#2-youtube-seo-methodology) YouTube video scripts and thumbnails · [D2 TikTok Shop](../d-platforms/tiktok-shop-ai-guide.md#15-short-video-content-creation-advanced-methodology) TikTok short video bulk production

---

## 4. Image/Video Specs by Platform

| Platform | Image Size | Video Size | Video Duration | Special Requirements |
|----------|-----------|-----------|---------------|---------------------|
| Amazon Main Image | 2000x2000 (1:1) | 16:9 | 30120s | White background, product fills 85%+ |
| Amazon Secondary | 2000x2000 (1:1) | | | Scene/infographic/comparison images |
| Shopify | Custom | Custom | Custom | Recommended 2048x2048 |
| Instagram Feed | 1080x1080 (1:1) | 9:16 | 1590s | Polished aesthetic style |
| Instagram Stories | 1080x1920 (9:16) | 9:16 | ≤60s | Full-screen vertical |
| TikTok | | 1080x1920 (9:16) | 1560s | Vertical, first 3 seconds are key |
| YouTube Thumbnail | 1280x720 (16:9) | 16:9 | Unlimited | High contrast, large text |
| YouTube Shorts | | 1080x1920 (9:16) | ≤60s | Vertical |
| Pinterest | 1000x1500 (2:3) | 9:16 | 1560s | Vertical, text overlay |
| Walmart | 2000x2000 (1:1) | 16:9 | 30120s | White-background main image |
| eBay | 1600x1600 (1:1) | | | White background recommended |

---

## 5. AI Visual Content Workflow

### 5.1 New Product Launch Visual Content SOP

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

## 6. Prompt Templates

### 6.1 Midjourney E-commerce Product Image Prompt Library

**White-Background Product Image:**
```
[产品描述], product photography, pure white background, studio lighting,
high resolution, commercial photography, centered composition,
sharp focus, no shadows --ar 1:1 --v 6.1 --s 100
```

**Lifestyle Scene Image:**
```
[产品描述] in use, [场景描述], lifestyle photography, natural lighting,
warm tones, shallow depth of field, editorial style,
photorealistic --ar 1:1 --v 6.1 --s 250
```

**Infographic Background:**
```
clean minimal background for product infographic, [品牌色] accent color,
geometric shapes, modern design, negative space,
professional layout --ar 1:1 --v 6.1 --s 150
```

### 6.2 AI Video Script Generation

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
```

---

## 7. Tool Comparison & Recommendations

### 7.1 Recommendations by Budget

| Budget | Image Tools | Video Tools | Monthly Cost |
|--------|------------|-------------|-------------|
| Free | PhotoRoom Free + Canva Free | CapCut Free | $0 |
| $2050/mo | Midjourney + PhotoRoom | CapCut Pro + Pika | $2636 |
| $50100/mo | Midjourney + Adobe Firefly | Runway + CapCut + HeyGen | $5480 |
| $100+/mo | Full tool suite | Full tool suite | $100+ |

### 7.2 Recommendations by Category

| Category | Key Image Types Needed | Recommended Tools |
|----------|----------------------|-------------------|
| Electronics | White-background + feature infographics + size comparison | PhotoRoom + Canva |
| Home & Living | Scene images (room settings) | Midjourney + PhotoRoom AI Staging |
| Apparel | Virtual model images | ZMO AI + Lalaland.ai |
| Beauty | Usage effect images + Before/After | Midjourney + Canva |
| Food | Food photography style | Midjourney (food prompts) |
| Outdoor & Sports | Outdoor scene images | Midjourney (outdoor scenes) |

---

## 8. Common Pitfalls

### Pitfall 1: Using AI-generated images directly as Amazon main images
Amazon requires the main image to be a real photograph of the product. AI-generated scene images can be used as secondary images, but the main image should be a real photo with AI background removal.

### Pitfall 2: Ignoring platform image policies
Amazon prohibits text, logos, and watermarks on main images. AI-generated infographics can only be used as secondary images.

### Pitfall 3: Inaccurate product details in AI-generated images
AI may alter the product's color, shape, button placement, and other details. Always manually verify product accuracy after generation.

### Pitfall 4: Over-relying on AI generation, neglecting real photography
AI scene images are great, but buyers also need to see real product photos. Recommended ratio: 50% real photos + 50% AI-generated.

### Pitfall 5: Copyright risks
Copyright ownership of images generated by tools like Midjourney remains debated. For commercial use, choose tools that explicitly grant commercial licenses (Midjourney paid plans, Adobe Firefly, Canva Pro).

---

## 9. Completion Checklist

- [ ] Generate a complete image set for one product using AI (white-background + scene + infographic)
- [ ] Create at least 1 product video using AI (3060 seconds)
- [ ] Build a Midjourney e-commerce prompt template library
- [ ] Master at least 2 AI image tools and 1 AI video tool
- [ ] Complete a cost comparison between AI images and traditional photography

---
> [Hub Home](../../README.md) · [Path A Overview](README.md)
>
> **Path A**: [A1 Product Research](a1-product-research.md) · [A2 Listing](a2-listing-optimization.md) · [A3 Advertising](a3-advertising.md) · [A4 Customer Service](a4-customer-service.md) · [A5 Inventory](a5-inventory.md) · [A6 Compliance](a6-compliance.md) · [A7 Visual Content](a7-visual-content.md)
>
> **Quick Jump**: [Path 0 Foundations](../0-foundations/) · [Path B Developers](../b-developers/) · [Path C Managers](../c-managers/) · [Path D Multi-Platform](../d-platforms/) · [Path E Social Media](../e-social-media/)
