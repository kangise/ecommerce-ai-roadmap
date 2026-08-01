# A7. AI Visual Content Creation

> **Track**: Path A: Operators · **Module**: A7
> **Last updated**: 2026-07-31
> **Level**: Intermediate
> **Time**: 30 minutes a day, 1–2 weeks
> **Prerequisite**: [A2 Listing & Content Creation](a2-listing-optimization.md)


---

## Chapter Navigation

1. [Why AI visual content is a 2026 must](#1-why-ai-visual-content-is-a-2026-must)
2. [AI product-image generation](#2-ai-product-image-generation)
3. [AI product-video generation](#3-ai-product-video-generation)
4. [Per-platform image/video specs](#4-per-platform-imagevideo-specs)
5. [AI visual-content workflow](#5-ai-visual-content-workflow)
6. [Prompt templates](#6-prompt-templates)
7. [Tool comparison and recommendations](#7-tool-comparison-and-recommendations)
8. [Common traps](#8-common-traps)
9. [Completion checklist](#9-completion-checklist)

---

## What You'll Learn

- Generate professional-grade product images with AI (white-background, scene, lifestyle)
- Produce product videos with AI (demo, ad, social-media videos)
- Master each platform's image/video spec requirements
- Build a batch AI visual-content production workflow

> **Core idea**: in 2026, AI product images can cut 80% of photography cost, and lifestyle images convert 22–30% higher than plain white-background images ([Entrepreneur](https://apac.entrepreneur.com/news-and-trends/how-smart-entrepreneurs-are-cutting-product-photography/501040)). The AI video-generation market reached $7.168B in 2025, growing 20% a year ([Fortune Business Insights](https://framepack.cc/articles/ai-video-tools-comparison-framepack)). Sellers who can't do AI visual content are losing competitiveness.

Content rephrased for compliance with licensing restrictions.

---

## 1. Why AI Visual Content Is a 2026 Must

### 1.1 Let the data speak

| Metric | Data | Source |
|--------|------|--------|
| AI product-image cost reduction | 80% | Entrepreneur 2026 |
| Lifestyle vs white-background conversion lift | 22–30% | A/B test studies |
| AI video-generation market size (2025) | $7.168B | Fortune Business Insights |
| AI video market projection (2032) | $25.6B | Fortune Business Insights |
| Amazon product video's effect on conversion | +9.7% | industry research |
| Time-on-Listing with video | +2× | industry benchmark |

### 1.2 The three levels of AI visual content

```
Level 1: AI-assisted editing (simplest)
Background removal/replacement (PhotoRoom, Remove.bg)
Image enhancement (upscale, denoise, color grade)
Batch crop and resize
Good for: existing product photos needing quick optimization

Level 2: AI-generated scene images (intermediate)
Real product photo + AI-generated background/scene
Tools: Midjourney, Nano Banana Pro, Ideogram, PhotoRoom AI Staging
No studio, no models needed
Good for: needing lifestyle images on a limited budget

Level 3: full AI generation (advanced)
Generate product images from text descriptions
Generate videos from product images
AI virtual models (apparel category)
Good for: pre-launch concept validation, batch social-media content production

<copy_discipline>
- Never write a feature, material, certification, or result the product doesn't actually have. Any attribute I didn't state above must not appear in the copy — this is the number-one cause of listing takedowns and false-advertising complaints
- If you need a selling point I didn't supply, list what you need from me rather than improvising
- Flag any claim touching efficacy, safety, environmental, or patent language separately so I can verify it by hand
</copy_discipline>
```

---

## 2. AI Product-Image Generation

### 2.1 Tool landscape

| Tool | Core function | Price | Best for |
|------|---------------|-------|----------|
| **Midjourney** | high-quality AI image generation | from $10/mo | creative scene and lifestyle images |
| **GPT Image 2** (ChatGPT) | text → image | $20/mo (ChatGPT Plus) | quick concept validation |
| **Ideogram** | accurate text rendering | free/paid | images containing text (labels, packaging) |
| **PhotoRoom** | background removal + AI scenes | free/Pro $10/mo | product white-background → scene image |
| **Canva AI** | image editing + AI generation | free/Pro $13/mo | an all-rounder for non-designers |
| **Adobe Firefly** | pro-grade AI editing | from $5/mo | teams already on Adobe |
| **ZMO AI** | e-commerce AI models | paid | virtual models for apparel |
| **Nano Banana AI** | dedicated to Amazon product images | paid | Amazon Listing images |

### 2.2 Amazon product-image AI generation in practice

**White-background main image (Main Image)**

Amazon main-image requirements: pure white background (RGB 255,255,255), product filling 85%+ of the frame, ≥1000×1000px.

```
AI workflow:
1. Shoot the product with your phone (any background)
2. PhotoRoom / Remove.bg one-click background removal
3. Auto-replace with a pure white background
4. Adjust product position and size (fill 85%+ of the frame)
5. Export at 2000×2000px (Amazon recommended)

Time: 2 min/image (vs 30 min/image traditional photography)
Cost: $0 (PhotoRoom free tier)
```

**Scene / lifestyle images**

```
Method 1: PhotoRoom AI Staging (simplest)
1. Upload the product white-background image
2. Choose a scene template (kitchen/living room/outdoor/desk)
3. AI auto-places the product into the scene
4. Adjust lighting and angle
Time: 1 min/image

Method 2: Midjourney (highest quality)
1. Upload a product reference image to Midjourney
2. Describe the desired scene with a prompt
3. Generate 4 variants, pick the best
4. Fine-tune in Photoshop/Canva
Time: 5–10 min/image

<copy_discipline>
- Never write a feature, material, certification, or result the product doesn't have. Any attribute I didn't state above must not appear in the copy
- For anything sent to a customer (replies, emails, templates), don't make commitments I haven't authorized: refund amounts, compensation, timelines, or exceptions to platform policy must be confirmed by me before they go in
- Flag any claim touching efficacy, safety, environmental, or patent language separately for manual review
</copy_discipline>
```

**Midjourney product-scene image prompt template:**

```
You are a Midjourney prompt expert focused on e-commerce product images.

Product: [name]
Product appearance: [color, material, size description]
Target scene: [use-case description]
Target platform: [Amazon/Shopify/Instagram]
Style: [minimal/warm/professional/outdoor/modern]

Generate 5 Midjourney prompts, each with:
1. The full English prompt (Midjourney only accepts English)
2. Recommended parameters (--ar ratio, --v version, --s stylization)
3. Expected-effect description

5 angles:
- Angle 1: product close-up (white/light background, highlight detail)
- Angle 2: use scene (a lifestyle image of a person using the product)
- Angle 3: environmental scene (product in a natural environment)
- Angle 4: comparison/size reference (product next to a common object)
- Angle 5: creative/concept image (a creative composition for social media)

Midjourney prompt format requirements:
- Open with the subject description
- Include lighting (soft lighting, studio lighting, natural light)
- Include style (photorealistic, commercial photography, lifestyle)
- Include technical parameters (--ar 1:1 --v 6.1 --s 250)

<copy_discipline>
- Never write a feature, material, certification, or result the product doesn't have. Any attribute I didn't state above must not appear in the copy
- For anything sent to a customer (replies, emails, templates), don't make commitments I haven't authorized: refund amounts, compensation, timelines, or exceptions to platform policy must be confirmed by me before they go in
- Flag any claim touching efficacy, safety, environmental, or patent language separately for manual review
</copy_discipline>
```

### 2.3 Infographic / selling-point image AI generation

Among Amazon's secondary images, the infographic is one of the highest-converting image types:

```
AI infographic workflow:
1. Generate selling-point copy with ChatGPT/Claude (≤8 words per point)
2. Choose an infographic template with Canva AI
3. Insert the product image + selling-point copy
4. AI auto-adjusts layout and color
5. Export multiple sizes (Amazon/Shopify/social media)

Canva AI prompt:
"Create a product infographic for [product name], highlighting these 5 features:
1. [selling point 1]
2. [selling point 2]
3. [selling point 3]
4. [selling point 4]
5. [selling point 5]
Style: clean, modern, white background with accent color [brand color]"

<copy_discipline>
- Never write a feature, material, certification, or result the product doesn't actually have. Any attribute I didn't state above must not appear in the copy — this is the number-one cause of listing takedowns and false-advertising complaints
- If you need a selling point I didn't supply, list what you need from me rather than improvising
- Flag any claim touching efficacy, safety, environmental, or patent language separately so I can verify it by hand
</copy_discipline>
```

---

## 3. AI Product-Video Generation

### 3.1 Video-tool landscape

| Tool | Core function | Price | Best for |
|------|---------------|-------|----------|
| **CapCut** | video editing + AI features | free/Pro $8/mo | TikTok/Reels short videos |
| **Runway Gen-4.5** | image/text → video, strong editing control | subscription | ads needing tight creative control |
| **Veo 3.1** (Google Flow) | text/image → video, generates audio | subscription | cinematic shots, finished clips with sound |
| **Kling 3** | image → video, strong motion realism | subscription | animated product showcases |
| **Seedance 2** | image → video, longer shot planning | subscription | ads, brand scenes, storyboard-driven work |
| **Magic Hour** | product image → ad video | paid | batch ad-creative generation |
| **Canva Video** | template-based video creation | free/Pro $13/mo | non-professionals |
| **InVideo AI** | AI auto-generates video | from $25/mo | complete product videos |
| **HeyGen** | AI virtual presenter | from $24/mo | product-intro/tutorial videos |
| **Synthesia** | AI avatar video | from $22/mo | multilingual product intros |

### 3.2 Amazon product video with AI

Amazon lets you upload a product video to the Listing, and Listings with video convert 9.7% higher on average:

```
Amazon product-video types:

1. Product-demo video (30–60s)
Multi-angle appearance
Core-feature demonstration
Size comparison
AI tools: Runway (image → video) + CapCut (editing)

2. Usage-tutorial video (60–120s)
Unboxing
Install/setup steps
Usage demo
AI tools: HeyGen (AI virtual presenter narration) + CapCut

3. Comparison video (30–60s)
Visual comparison with competitors
Before/After effect
AI tools: CapCut (split-screen comparison template)

4. Brand-story video (60–90s)
Brand philosophy
Manufacturing process
User stories
AI tools: InVideo AI (generate a full video from text)
```

### 3.3 Batch social-media video production with AI

```
Workflow to generate 10+ videos from one product's assets:

Step 1: asset prep
5 product white-background images
3 product use-scene images (AI-generated)
30s of real product-footage clips (a phone is enough)
Product selling-point copy (ChatGPT-generated)

Step 2: AI generates video variants
Runway: product image → 3s animated showcase × 5 angles
CapCut: template editing × 3 styles (demo/tutorial/comparison)
Pika: product image → animated background × 3 scenes
Total: 11 video assets

Step 3: platform adaptation
Amazon product video: landscape 16:9, 30–60s
TikTok/Reels: vertical 9:16, 15–30s
YouTube Shorts: vertical 9:16, 30–60s
Pinterest: vertical 2:3 or 9:16
Total: each asset × 4 platforms = 44 videos

Step 4: copy + subtitles
ChatGPT generates per-platform copy
CapCut AI auto-generates subtitles
Batch export
```

> **Related**: [E1 Instagram Reels](../e-social-media/e1-instagram-facebook-ai-guide.md) for Reels video methodology · [E2 YouTube](../e-social-media/e2-youtube-ai-guide.md) for YouTube scripts and thumbnails · [D2 TikTok Shop](../d-platforms/tiktok-shop-ai-guide.md) for TikTok short-video batch production.

---

## 4. Per-Platform Image/Video Specs

| Platform | Image size | Video size | Video length | Special requirements |
|----------|------------|------------|--------------|----------------------|
| Amazon main image | 2000×2000 (1:1) | 16:9 | 30–120s | white background, product fills 85%+ |
| Amazon secondary image | 2000×2000 (1:1) | | | scene/infographic/comparison |
| Shopify | custom | custom | custom | 2048×2048 recommended |
| Instagram Feed | 1080×1080 (1:1) | 9:16 | 15–90s | polished aesthetic |
| Instagram Stories | 1080×1920 (9:16) | 9:16 | ≤60s | full-screen vertical |
| TikTok | | 1080×1920 (9:16) | 15–60s | vertical, first 3s are key |
| YouTube thumbnail | 1280×720 (16:9) | 16:9 | unlimited | high contrast, large text |
| YouTube Shorts | | 1080×1920 (9:16) | ≤60s | vertical |
| Pinterest | 1000×1500 (2:3) | 9:16 | 15–60s | vertical, text overlay |
| Walmart | 2000×2000 (1:1) | 16:9 | 30–120s | white-background main image |
| eBay | 1600×1600 (1:1) | | | white background recommended |

---

## 5. AI Visual-Content Workflow

### 5.1 New-product launch visual-content SOP

```
Day 1: real product shots (a phone is enough)
5 white-background images (different angles)
3 handheld/in-use images
2 packaging/accessory images
30s usage-video clip

Day 2: AI image generation
PhotoRoom: white-background optimization (removal + adjustment)
Midjourney: 5 lifestyle scene images
Canva AI: 3 infographic/selling-point images
1 size-comparison image
Total: ~15 images

Day 3: AI video generation
Runway: 1 product-demo video (30s)
CapCut: 3 TikTok/Reels short videos
HeyGen: 1 product-intro video (60s, AI virtual presenter)
Total: ~5 videos

Day 4: platform adaptation + upload
Amazon: main image + 6 secondary images + 1 video
Shopify: product-page images + video
Social media: per-platform size adaptation
Ad creative: Meta Ads/Google Ads images + video

Traditional way: 2–3 weeks + $2000–5000
AI way: 4 days + $50–100 (tool subscriptions)
```

---

## 6. Prompt Templates

> **Prompt conventions used here**: the templates below work as-is, but for anything involving numbers, forecasts, or recommendations, paste in [the data-discipline block from F2 §4.3](../0-foundations/f2-prompt-engineering.md#43-the-data-discipline-block-ready-to-paste). It forbids the model from inventing data you didn't supply — the most common failure mode for this class of prompt.

### 6.1 Midjourney e-commerce product-image prompt library

**White-background product image:**
```
[product description], product photography, pure white background, studio lighting,
high resolution, commercial photography, centered composition,
sharp focus, no shadows --ar 1:1 --v 6.1 --s 100
```

**Lifestyle scene image:**
```
[product description] in use, [scene description], lifestyle photography, natural lighting,
warm tones, shallow depth of field, editorial style,
photorealistic --ar 1:1 --v 6.1 --s 250
```

**Infographic background:**
```
clean minimal background for product infographic, [brand color] accent color,
geometric shapes, modern design, negative space,
professional layout --ar 1:1 --v 6.1 --s 150
```

### 6.2 AI video-script generation

```
You are an e-commerce product-video script expert.

Product: [name]
Video type: [product demo / usage tutorial / comparison / brand story]
Target platform: [Amazon/TikTok/Instagram/YouTube]
Video length: [30/60/120s]

Generate a video script with:
1. A shot description for each shot (for the AI video-generation tool)
2. Subtitle/voiceover text
3. Duration marks
4. Recommended AI tools (which tool to generate each shot)
5. Background-music style advice

<copy_discipline>
- Never write a feature, material, certification, or result the product doesn't actually have. Any attribute I didn't state above must not appear in the copy — this is the number-one cause of listing takedowns and false-advertising complaints
- If you need a selling point I didn't supply, list what you need from me rather than improvising
- Flag any claim touching efficacy, safety, environmental, or patent language separately so I can verify it by hand
</copy_discipline>
```

---

## 7. Tool Comparison and Recommendations

### 7.1 By budget

| Budget | Image tools | Video tools | Monthly cost |
|--------|-------------|-------------|--------------|
| Free | PhotoRoom free + Canva free | CapCut free | $0 |
| $20–50/mo | Midjourney + PhotoRoom | CapCut Pro + Pika | $26–36 |
| $50–100/mo | Midjourney + Adobe Firefly | Runway + CapCut + HeyGen | $54–80 |
| $100+/mo | full tool suite | full tool suite | $100+ |

### 7.2 By category

| Category | Most-needed image type | Recommended tools |
|----------|------------------------|-------------------|
| Electronics | white-background + feature infographic + size comparison | PhotoRoom + Canva |
| Home | scene images (in-room effect) | Midjourney + PhotoRoom AI Staging |
| Apparel | virtual-model images | ZMO AI + Lalaland.ai |
| Beauty | usage-effect + Before/After | Midjourney + Canva |
| Food | food-photography style | Midjourney (food prompts) |
| Outdoor/sports | outdoor scene images | Midjourney (outdoor scenes) |

---

## 8. Common Traps

### Trap 1: using an AI-generated image directly as the Amazon main image
The Amazon main image must be a real photo of the product. AI-generated scene images can be used as secondary images, but for the main image use a real shot + AI background removal.

### Trap 2: ignoring each platform's image policy
Amazon bans text, logos, and watermarks on the main image. AI-generated infographics can only be secondary images.

### Trap 3: inaccurate product details in AI generation
AI may change the product's color, shape, button positions, and other details. After generating, you must manually check the accuracy of product details.

### Trap 4: over-relying on AI generation, ignoring real shots
AI scene images are great, but buyers also need to see real product photos. Suggested ratio: 50% real shots + 50% AI-generated.

### Trap 5: copyright risk
The copyright ownership of images generated by tools like Midjourney is still disputed. For commercial use, prefer tools that explicitly grant a commercial license (Midjourney paid, Adobe Firefly, Canva Pro).

---

## 9. Completion Checklist

- [ ] Generated a complete image set for one product with AI (white-background + scene + infographic)
- [ ] Made at least 1 product video with AI (30–60s)
- [ ] Built a Midjourney e-commerce prompt-template library
- [ ] Mastered at least 2 AI image tools and 1 AI video tool
- [ ] Completed a cost comparison of AI images vs traditional photography

[< A6 Compliance](a6-compliance.md) | [Path overview](../README.md) | [A8 Pricing >](a8-pricing-strategy.md)
