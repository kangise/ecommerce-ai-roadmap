[🇨🇳 中文](../../paths/b-developers/b9-ai-image-pipeline.md) | 🇺🇸 English

# B9. AI Product Image & Video Generation Pipeline

> **Path**: Path B: Developers · **Module**: B9
> **Last Updated**: 2026-03-15
> **Difficulty**: ⭐⭐⭐ Advanced
> **Estimated Time**: 1 hour/day, 2-3 weeks
> **Prerequisites**: None (standalone module, but familiarity with [A7 Visual Content](../a-operators/a7-visual-content.md) is recommended)

🏠 [Hub Home](../../README.md) · 📋 [Path B Overview](README.md)

---

## 📖 Chapter Navigation

1. [Why You Need an AI Image Pipeline](#1-why-you-need-an-ai-image-pipeline) · 2. [Tech Stack Selection](#2-tech-stack-selection) · 3. [ComfyUI Product Image Workflow](#3-comfyui-product-image-workflow) · 4. [API Solutions](#4-api-solutionsmidjourneydall-eflux) · 5. [Batch Generation Pipeline](#5-batch-generation-pipeline) · 6. [AI Video Generation](#6-ai-video-generation) · 7. [Quality Control & Compliance](#7-quality-control--compliance) · 8. [Completion Checklist](#8-completion-checklist)

---

## What You'll Build in This Module

- A ComfyUI product image generation workflow (white background hero images + lifestyle shots + infographics)
- An API-driven batch image generation pipeline (Midjourney/DALL-E/Flux)
- An automated product video generation system
- Brand visual consistency safeguards

> 💡 **Core Concept**: Product images are the #1 factor in e-commerce conversion rates. The traditional approach is hiring photographers ($500-2,000/product); the AI approach uses ComfyUI/Midjourney ($0-50/product). But AI generation isn't "one-click magic" — you need to build a repeatable, controllable, brand-consistent pipeline.

> 📎 **Related Reading**: [A7 Visual Content](../a-operators/a7-visual-content.md#1-why-ai-visual-content-is-essential-in-2026) — Operator-focused AI visual content methodology

---

## 1. Why You Need an AI Image Pipeline

### 1.1 E-commerce Image Requirements Matrix

| Image Type | Purpose | Qty/Product | Traditional Cost | AI Cost |
|-----------|---------|-------------|-----------------|---------|
| White background hero | Amazon/Shopify main image | 1 | $100-300 | $0-5 |
| Lifestyle shots | Usage scenario showcase | 3-5 | $200-500 | $5-20 |
| Infographics | Dimensions/comparison/feature callouts | 2-3 | $100-200 | $5-10 |
| A+ Content | Brand story imagery | 5-7 | $300-500 | $10-30 |
| Social media | Instagram/TikTok assets | 10-20/month | $500-1,000/month | $20-50/month |
| Ad creatives | PPC/Meta/Google Ads | 5-10 variants | $200-500 | $10-30 |

### 1.2 Challenges of AI Image Generation

| Challenge | Description | Solution |
|-----------|-------------|---------|
| Product consistency | AI-generated product may look different from the real thing | Use actual product photos as reference (ControlNet/IP-Adapter) |
| Brand consistency | Inconsistent styles across images | Fixed prompt prefix + Style Reference |
| Platform compliance | Amazon main images require pure white background | Post-processing: background removal + white background compositing |
| Text rendering | AI-generated text is often garbled | Post-processing: overlay text with Pillow/Canva |
| Copyright risk | AI may generate content similar to existing works | Use commercially licensed tools + manual review |

---

## 2. Tech Stack Selection

### 2.1 Solution Comparison

| Solution | Pros | Cons | Cost | Best For |
|----------|------|------|------|----------|
| ComfyUI (local) | Full control, automatable, free | Requires GPU, steep learning curve | Hardware cost | High volume, technical teams |
| Midjourney | Highest quality, diverse styles | No API (requires Discord), less controllable | $10-30/month | Small batches of high-quality images |
| DALL-E 3 (API) | Has API, programmable | Medium quality, limited styles | Pay-per-use | Batch generation, automation |
| Flux (local/API) | Open source, high quality, fine-tunable | Requires GPU | Free/pay-per-use | Technical teams, customization |
| Adobe Firefly | Commercially safe, indemnification | Limited features | From $10/month | Commercial use, compliance-first |
| Canva AI | Easy to use, rich templates | Low flexibility | $13/month | Non-technical users |

### 2.2 Recommended Combination

```
Recommended AI Image Tech Stack:

Hero/Lifestyle Image Generation:
├── ComfyUI + Flux (local, full control)
├── or Midjourney (cloud, highest quality)
└── or DALL-E 3 API (programmable, batch generation)

Post-Processing:
├── rembg (Python background removal)
├── Pillow (image processing, text overlay)
└── OpenCV (advanced image processing)

Batch Management:
├── Python scripts (automated workflows)
└── Canva Brand Kit (template management)
```

---

## 3. ComfyUI Product Image Workflow

### 3.1 Installing ComfyUI

```bash
# 克隆 ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 安装依赖
pip3 install -r requirements.txt

# 下载模型（Flux 推荐）
# 将模型文件放到 models/checkpoints/ 目录

# 启动
python3 main.py
# 浏览器打开 http://127.0.0.1:8188
```

### 3.2 Product Image Generation Workflow

> **Real Case: ComfyUI Product Image Workflow in Practice**
> MyAIForce demonstrated a complete ComfyUI product image workflow: input a skincare product photo and a descriptive prompt, and the workflow automatically places the product seamlessly into a new background, adjusting lighting and shadows to match the new environment for a natural, harmonious look. The workflow includes 7 steps: upload image → set background → basic adjustments → product positioning → relighting → inpainting → restore details ([MyAIForce](https://myaiforce.com/comfyui-product-photography/)).

Content rephrased for compliance with licensing restrictions.

> **Real Case: Midjourney + ComfyUI Combined Workflow**
> Another advanced workflow combines Midjourney and ComfyUI: first generate a high-quality scene background with Midjourney, then use ComfyUI's ControlNet and IP-Adapter to precisely place the product into the scene while adjusting lighting and shadows to preserve key product details like text ([MyAIForce](https://myaiforce.com/product-photography-comfyui-midjourney/)).

Content rephrased for compliance with licensing restrictions.

> **Real Case: ComfyUI Background Replacement V4 Workflow**
> The latest V4 background replacement workflow uses SDXL checkpoints, requiring only 10 sampling steps and approximately 6GB VRAM for basic tasks. Using Flux models yields higher quality results but requires more VRAM ([MyAIForce](https://myaiforce.com/flux-replace-background-v4/)).

Content rephrased for compliance with licensing restrictions.

```
ComfyUI E-commerce Product Image Complete Workflow (7 Steps):

Step 1: Upload Image and Set Background
├── Load Image node: load product photo
├── Background selection: upload preset background or generate with prompt
└── Parameter settings: resolution, sampling steps

Step 2: Basic Adjustments
├── Product cutout (Florence2Run or rembg)
├── Size adjustment
└── Initial compositing

Step 3: Product Positioning
├── Adjust product position in frame
├── Scale ratio
└── Angle adjustment

Step 4: Relighting
├── IC-Light node: adjust product lighting based on background
├── Shadow direction matching
└── Highlight adjustment

Step 5: Generate Background
├── Flux Fill + Redux: generate background matching the product
├── or IP-Adapter: copy reference image style
└── KSampler: execute generation

Step 6: Inpainting
├── Fix seams between product and background
├── Add natural shadows
└── Detail blending

Step 7: Restore Details and Colors
├── Restore original product colors
├── Sharpen details
├── Final output
└── Save as PNG/JPEG
```

### 3.3 E-commerce Scene Prompt Templates (40+ Tested Templates)

> **Real Resource**: Apatero compiled 40+ tested AI product image prompt templates covering white background, lifestyle, flat lay, infographic, and all other e-commerce scenarios ([Apatero](https://www.apatero.com/blog/best-prompts-product-photography-ai-generation-2025)).

Content rephrased for compliance with licensing restrictions.

```python
# 电商产品图 Prompt 模板库（扩展版）
PROMPT_TEMPLATES = {
    # === 主图系列 ===
    "amazon_main": {
        "positive": "professional product photography, {product}, centered on pure white background #FFFFFF, product fills 85 percent of frame, studio lighting with soft shadows, high resolution 8k, sharp focus, no text no logos no watermarks, commercial catalog style",
        "negative": "blurry, low quality, text, watermark, logo, human, hand, colored background, shadow on background, props, accessories not part of product"
    },
    "shopify_hero": {
        "positive": "hero product shot, {product}, clean minimal background with subtle gradient, dramatic studio lighting, slight shadow underneath, premium feel, editorial quality, 4k",
        "negative": "cluttered, busy background, text, watermark, low quality"
    },
    
    # === 场景图系列 ===
    "lifestyle_home": {
        "positive": "lifestyle product photography, {product} in modern minimalist home, natural window lighting, warm tones, shallow depth of field, bokeh background, editorial style, authentic feel",
        "negative": "artificial, oversaturated, studio look, text, watermark"
    },
    "lifestyle_outdoor": {
        "positive": "outdoor lifestyle photography, {product} in natural setting, golden hour lighting, vibrant colors, adventure feel, authentic, editorial quality",
        "negative": "indoor, artificial lighting, text, watermark, studio"
    },
    "lifestyle_office": {
        "positive": "modern office setting, {product} on clean desk, natural lighting from window, minimalist decor, professional atmosphere, shallow depth of field",
        "negative": "cluttered, messy, dark, text, watermark"
    },
    "lifestyle_kitchen": {
        "positive": "modern kitchen setting, {product} on marble countertop, natural lighting, fresh ingredients nearby, clean and bright, food photography style",
        "negative": "dirty, cluttered, dark, text, watermark"
    },
    
    # === 平铺图系列 ===
    "flat_lay_minimal": {
        "positive": "flat lay photography, {product} with complementary items, top-down view, clean arrangement on {surface}, soft shadows, minimalist, {color_scheme}",
        "negative": "cluttered, messy, blurry, text, 3D perspective"
    },
    "flat_lay_seasonal": {
        "positive": "seasonal flat lay, {product} surrounded by {season} elements, top-down view, cohesive color palette, editorial styling, natural textures",
        "negative": "cluttered, artificial, text, watermark"
    },
    
    # === 信息图背景系列 ===
    "infographic_clean": {
        "positive": "clean infographic background for {product}, {color_scheme} gradient, modern design, ample negative space for text overlay, professional, soft lighting on product",
        "negative": "text, numbers, charts, cluttered, busy, distracting elements"
    },
    "infographic_comparison": {
        "positive": "split comparison layout background, {product} centered, left side and right side clearly divided, clean modern design, space for before/after or feature comparison text",
        "negative": "text, numbers, cluttered"
    },
    
    # === 社交媒体系列 ===
    "instagram_aesthetic": {
        "positive": "instagram aesthetic product shot, {product}, trendy styling, {color_scheme} color palette, natural lighting, lifestyle feel, square format, influencer style",
        "negative": "corporate, boring, text, watermark, low quality"
    },
    "tiktok_dynamic": {
        "positive": "dynamic product shot, {product}, vibrant colors, energetic composition, slight motion blur on background, youth-oriented, vertical format 9:16",
        "negative": "static, boring, corporate, text"
    },
    
    # === A+ Content 系列 ===
    "aplus_brand_story": {
        "positive": "brand story photography, {product} in aspirational setting, warm emotional lighting, lifestyle context, premium quality, cinematic feel",
        "negative": "cheap, low quality, text, watermark"
    },
    "aplus_feature_highlight": {
        "positive": "close-up detail shot, {product} {feature} highlighted, macro photography style, sharp focus on detail, soft background, studio lighting",
        "negative": "blurry, wide shot, text, watermark"
    }
}

def generate_prompt(template_name: str, product: str, **kwargs) -> dict:
    """生成产品图 Prompt"""
    template = PROMPT_TEMPLATES[template_name]
    # 填充默认值
    defaults = {
        "surface": "white marble",
        "color_scheme": "blue and white",
        "season": "autumn",
        "feature": "texture detail"
    }
    for k, v in defaults.items():
        kwargs.setdefault(k, v)
    
    return {
        "positive": template["positive"].format(product=product, **kwargs),
        "negative": template["negative"]
    }

# 使用示例
prompt = generate_prompt(
    "lifestyle_home",
    product="wireless bluetooth earbuds with charging case"
)
print(prompt["positive"])
```

---

## 4. API Solutions (Midjourney/DALL-E/Flux)

### 4.1 DALL-E 3 Batch Generation

```python
from openai import OpenAI
import requests
from pathlib import Path

client = OpenAI()

def generate_product_image(
    product_description: str,
    style: str = "white_background",
    size: str = "1024x1024",
    output_dir: str = "output"
) -> str:
    """用 DALL-E 3 生成产品图"""
    
    prompts = {
        "white_background": f"Professional product photography of {product_description}, centered on pure white background, studio lighting, high resolution, commercial quality",
        "lifestyle": f"Lifestyle product photography of {product_description} being used in a modern home setting, natural lighting, warm tones, editorial quality",
        "amazon_main": f"Amazon product listing main image: {product_description}, pure white background (#FFFFFF), product fills 85% of frame, no text or logos, professional studio photography"
    }
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompts[style],
        size=size,
        quality="hd",
        n=1
    )
    
    # 下载图片
    image_url = response.data[0].url
    Path(output_dir).mkdir(exist_ok=True)
    
    img_data = requests.get(image_url).content
    filepath = f"{output_dir}/{product_description[:30]}_{style}.png"
    with open(filepath, "wb") as f:
        f.write(img_data)
    
    return filepath

# 批量生成
products = [
    "wireless bluetooth earbuds with charging case",
    "stainless steel water bottle 32oz",
    "portable neck fan with LED display"
]

for product in products:
    for style in ["white_background", "lifestyle"]:
        path = generate_product_image(product, style)
        print(f"Generated: {path}")
```

### 4.2 Background Removal + White Background Compositing

```python
from rembg import remove
from PIL import Image
import io

def create_amazon_main_image(input_path: str, output_path: str):
    """创建 Amazon 合规的白底主图"""
    # 读取图片
    with open(input_path, "rb") as f:
        input_data = f.read()
    
    # 去背景
    output_data = remove(input_data)
    
    # 创建白底画布
    fg = Image.open(io.BytesIO(output_data)).convert("RGBA")
    
    # 计算产品占比（Amazon 要求 85%+）
    bbox = fg.getbbox()
    product_w = bbox[2] - bbox[0]
    product_h = bbox[3] - bbox[1]
    
    # 创建正方形白底（产品占 85%）
    canvas_size = int(max(product_w, product_h) / 0.85)
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 255))
    
    # 居中放置产品
    offset_x = (canvas_size - product_w) // 2 - bbox[0]
    offset_y = (canvas_size - product_h) // 2 - bbox[1]
    canvas.paste(fg, (offset_x, offset_y), fg)
    
    # 保存为 RGB（Amazon 不接受透明背景）
    canvas.convert("RGB").save(output_path, "JPEG", quality=95)
    print(f"Amazon main image saved: {output_path}")
```

---

## 5. Batch Generation Pipeline

### 5.1 Complete Product Image Generation Pipeline

```python
import os
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductImageRequest:
    """产品图生成请求"""
    product_name: str
    product_description: str
    source_image: Optional[str] = None  # 产品实拍图路径
    brand_color: str = "blue"
    target_platforms: list = None  # ["amazon", "shopify", "instagram"]
    
    def __post_init__(self):
        if self.target_platforms is None:
            self.target_platforms = ["amazon", "shopify"]

class ProductImagePipeline:
    """电商产品图批量生成 Pipeline"""
    
    def __init__(self, method: str = "dalle", output_dir: str = "output/images"):
        self.method = method
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self.log = []
    
    def generate_product_set(self, request: ProductImageRequest) -> dict:
        """为一个产品生成完整的图片集"""
        product_dir = os.path.join(
            self.output_dir, 
            request.product_name.replace(" ", "_")[:30]
        )
        Path(product_dir).mkdir(exist_ok=True)
        
        results = {"product": request.product_name, "images": {}}
        
        # 1. Amazon 白底主图
        if "amazon" in request.target_platforms:
            self._log(f"生成 Amazon 主图: {request.product_name}")
            main_img = self._generate_image(
                request, "amazon_main", 
                os.path.join(product_dir, "amazon_main.jpg")
            )
            # 后处理：去背景 + 白底合成
            amazon_img = self._post_process_amazon(main_img)
            results["images"]["amazon_main"] = amazon_img
            
            # 合规检查
            compliance = check_amazon_compliance(amazon_img)
            results["images"]["amazon_compliance"] = compliance
            if not compliance["compliant"]:
                self._log(f"⚠️ Amazon 合规问题: {compliance['issues']}")
        
        # 2. 场景图 x3
        scenes = [
            ("modern living room", "lifestyle_home"),
            ("outdoor natural setting", "lifestyle_outdoor"),
            ("clean office desk", "lifestyle_office")
        ]
        results["images"]["lifestyle"] = []
        for i, (scene, template) in enumerate(scenes):
            self._log(f"生成场景图 {i+1}/3: {scene}")
            img = self._generate_image(
                request, template,
                os.path.join(product_dir, f"lifestyle_{i+1}.jpg"),
                scene=scene
            )
            results["images"]["lifestyle"].append(img)
        
        # 3. 信息图背景 x2
        results["images"]["infographic"] = []
        for i, color in enumerate(["blue and white", "warm earth tones"]):
            self._log(f"生成信息图背景 {i+1}/2")
            img = self._generate_image(
                request, "infographic_clean",
                os.path.join(product_dir, f"infographic_{i+1}.jpg"),
                color_scheme=color
            )
            results["images"]["infographic"].append(img)
        
        # 4. 社交媒体素材
        if "instagram" in request.target_platforms:
            self._log("生成 Instagram 素材")
            img = self._generate_image(
                request, "instagram_aesthetic",
                os.path.join(product_dir, "instagram.jpg"),
                color_scheme=request.brand_color
            )
            results["images"]["instagram"] = img
        
        # 5. A+ Content 品牌故事图
        self._log("生成 A+ Content 图")
        img = self._generate_image(
            request, "aplus_brand_story",
            os.path.join(product_dir, "aplus_brand.jpg")
        )
        results["images"]["aplus"] = img
        
        # 保存元数据
        metadata = {
            "product": request.product_name,
            "generated_at": datetime.now().isoformat(),
            "method": self.method,
            "images": {k: str(v) for k, v in results["images"].items()},
            "log": self.log
        }
        with open(os.path.join(product_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        self._log(f"✅ 完成: {request.product_name} ({len(results['images'])} 张图片)")
        return results
    
    def batch_generate(self, requests: list[ProductImageRequest]) -> list:
        """批量生成多个产品的图片集"""
        all_results = []
        for i, request in enumerate(requests):
            print(f"\n{'='*50}")
            print(f"Processing {i+1}/{len(requests)}: {request.product_name}")
            print(f"{'='*50}")
            
            try:
                results = self.generate_product_set(request)
                all_results.append(results)
            except Exception as e:
                self._log(f"❌ 失败: {request.product_name} - {str(e)}")
                all_results.append({"product": request.product_name, "error": str(e)})
        
        # 生成批量报告
        self._generate_batch_report(all_results)
        return all_results
    
    def _generate_image(self, request, template, output_path, **kwargs):
        """生成单张图片（根据 method 选择不同的生成方式）"""
        prompt = generate_prompt(template, request.product_description, **kwargs)
        
        if self.method == "dalle":
            return self._dalle_generate(prompt, output_path)
        elif self.method == "comfyui":
            return self._comfyui_generate(prompt, request.source_image, output_path)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def _dalle_generate(self, prompt, output_path):
        """DALL-E 3 生成"""
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt["positive"],
            size="1024x1024",
            quality="hd",
            n=1
        )
        # 下载并保存
        import requests
        img_data = requests.get(response.data[0].url).content
        with open(output_path, "wb") as f:
            f.write(img_data)
        return output_path
    
    def _post_process_amazon(self, image_path):
        """Amazon 主图后处理"""
        output_path = image_path.replace(".jpg", "_amazon.jpg")
        create_amazon_main_image(image_path, output_path)
        return output_path
    
    def _log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.append(f"[{timestamp}] {message}")
        print(f"[{timestamp}] {message}")
    
    def _generate_batch_report(self, results):
        """生成批量处理报告"""
        report = f"# 产品图批量生成报告\n\n"
        report += f"生成时间: {datetime.now().isoformat()}\n"
        report += f"总产品数: {len(results)}\n"
        report += f"成功: {sum(1 for r in results if 'error' not in r)}\n"
        report += f"失败: {sum(1 for r in results if 'error' in r)}\n\n"
        
        for r in results:
            if "error" in r:
                report += f"❌ {r['product']}: {r['error']}\n"
            else:
                report += f"✅ {r['product']}: {len(r['images'])} 张图片\n"
        
        with open(os.path.join(self.output_dir, "batch_report.md"), "w") as f:
            f.write(report)
```

Usage example:

```python
# === 使用示例 ===
if __name__ == "__main__":
    pipeline = ProductImagePipeline(method="dalle")
    
    products = [
        ProductImageRequest(
            product_name="Wireless Bluetooth Earbuds",
            product_description="premium wireless bluetooth earbuds with active noise cancellation, charging case, white color",
            brand_color="blue",
            target_platforms=["amazon", "shopify", "instagram"]
        ),
        ProductImageRequest(
            product_name="Stainless Steel Water Bottle",
            product_description="32oz stainless steel insulated water bottle, matte black, with bamboo lid",
            brand_color="green",
            target_platforms=["amazon", "shopify"]
        ),
        ProductImageRequest(
            product_name="Portable Neck Fan",
            product_description="portable bladeless neck fan with LED display, 3 speed settings, white and gray",
            brand_color="blue",
            target_platforms=["amazon", "instagram"]
        )
    ]
    
    results = pipeline.batch_generate(products)
```

### 5.2 A/B Test Image Variants

```python
def generate_ab_test_variants(request: ProductImageRequest, 
                               num_variants: int = 3) -> list:
    """为 A/B 测试生成多个主图变体"""
    variants = []
    
    # 变体 1：不同角度
    angles = ["front view centered", "45 degree angle", "slight top-down angle"]
    
    # 变体 2：不同光照
    lightings = ["soft studio lighting", "dramatic side lighting", "bright even lighting"]
    
    # 变体 3：不同构图
    compositions = [
        "product fills 85% of frame",
        "product fills 70% with more white space",
        "product with subtle shadow underneath"
    ]
    
    for i in range(num_variants):
        variant_prompt = (
            f"professional product photography, {request.product_description}, "
            f"{angles[i % len(angles)]}, {lightings[i % len(lightings)]}, "
            f"{compositions[i % len(compositions)]}, "
            f"pure white background, high resolution 8k"
        )
        
        img = generate_with_dalle(variant_prompt, f"variant_{i+1}.jpg")
        variants.append({
            "variant": i + 1,
            "angle": angles[i % len(angles)],
            "lighting": lightings[i % len(lightings)],
            "composition": compositions[i % len(compositions)],
            "image": img
        })
    
    return variants
```

---

## 6. AI Video Generation

### 6.1 Product Video Types

| Type | Duration | Purpose | AI Tools |
|------|----------|---------|----------|
| Product showcase | 15-30s | Amazon video, Shopify | Runway Gen-3 / Pika |
| Tutorial | 30-60s | A+ Content, YouTube | Synthesia / HeyGen |
| Social short-form | 15-60s | TikTok/Reels/Shorts | CapCut AI / Runway |
| Ad video | 6-15s | PPC video ads | Runway / Sora |

### 6.2 Product Showcase Video Generation

```python
# 概念代码：用 Runway API 生成产品展示视频
import runway

def generate_product_video(
    product_image: str,
    motion_prompt: str = "slow 360 degree rotation, studio lighting",
    duration: int = 4  # 秒
) -> str:
    """从产品图生成展示视频"""
    
    task = runway.image_to_video.create(
        model="gen3a_turbo",
        prompt_image=product_image,
        prompt_text=motion_prompt,
        duration=duration
    )
    
    # 等待生成完成
    task = runway.tasks.retrieve(task.id)
    while task.status != "SUCCEEDED":
        import time
        time.sleep(5)
        task = runway.tasks.retrieve(task.id)
    
    return task.output[0]  # 视频 URL
```

---

## 7. Quality Control & Compliance

### 7.1 Amazon Image Compliance Check

```python
def check_amazon_compliance(image_path: str) -> dict:
    """检查图片是否符合 Amazon 要求"""
    img = Image.open(image_path)
    issues = []
    
    # 尺寸检查（最小 1000px）
    if min(img.size) < 1000:
        issues.append(f"尺寸不足: {img.size}，最小需要 1000x1000")
    
    # 白底检查（主图）
    pixels = list(img.getdata())
    corners = [pixels[0], pixels[img.width-1], 
               pixels[-img.width], pixels[-1]]
    for i, corner in enumerate(corners):
        if not all(c > 240 for c in corner[:3]):
            issues.append(f"角落 {i} 不是纯白: {corner}")
    
    # 产品占比检查
    # ... (检查产品是否占画面 85%+)
    
    return {
        "compliant": len(issues) == 0,
        "issues": issues,
        "size": img.size,
        "format": img.format
    }
```

### 7.2 Brand Consistency Checks

| Check Item | Method | Tool |
|-----------|--------|------|
| Color consistency | Extract dominant colors and compare against brand palette | Pillow + ColorThief |
| Style consistency | CLIP embedding similarity | sentence-transformers |
| Logo placement | Template verification | Pillow |
| Text font | OCR + font matching | Tesseract |

---

## 8. Completion Checklist

- [ ] Set up ComfyUI or chose an API solution
- [ ] Generated a complete image set for one product (hero + lifestyle + infographic)
- [ ] Implemented automated background removal + white background compositing
- [ ] Built a batch generation pipeline (processing 5+ products at once)
- [ ] Passed Amazon image compliance checks
- [ ] Generated at least 1 product showcase video

---
> 🏠 [Hub Home](../../README.md) · 📋 [Path B Overview](README.md)
> 
> **Path B**: [B1 Data Pipeline](b1-data-pipeline.md) · [B2 Prediction Models](b2-prediction-models.md) · [B3 RAG Knowledge Base](b3-rag-knowledge-base.md) · [B4 AI Agent](b4-agent-workflow.md) · [B5 Local Models](b5-local-model-deploy.md) · [B6 MCP Integration](b6-mcp-agentic-workflow.md) · [B7 Review NLP](b7-review-nlp-system.md) · [B8 Dashboard](b8-ecommerce-dashboard.md) · [B9 AI Image Pipeline](b9-ai-image-pipeline.md)
> 
> **Quick Links**: [Path 0 Foundations](../0-foundations/) · [Path A Operators](../a-operators/) · [Path C Managers](../c-managers/) · [Path D Multi-Platform](../d-platforms/) · [Path E Social Media](../e-social-media/)