# B9. AI Product Image & Video Generation Pipeline

> **Track**: Path B: Technical · **Module**: B9
> **Last updated**: 2026-07-31
> **Difficulty**: Advanced
> **Estimated time**: 1 hour/day, 2-3 weeks
> **Prerequisites**: None (standalone module, but understanding [A7 Visual Content](../a-operators/a7-visual-content.md) is recommended)


---

## Chapter Navigation

1. [Why You Need an AI Image Pipeline](#1-why-you-need-an-ai-image-pipeline) · 2. [Tech Stack Selection](#2-tech-stack-selection) · 3. [ComfyUI Product Image Workflow](#3-comfyui-product-image-workflow) · 4. [Cloud API Approaches](#4-cloud-api-approaches) · 5. [Batch Generation Pipeline](#5-batch-generation-pipeline) · 6. [Video Generation](#6-ai-video-generation) · 7. [Quality Control & Compliance](#7-quality-control--compliance) · 8. [Common Traps](#8-common-traps) · 9. [Completion Checklist](#9-completion-checklist)

---

## What You Will Build in This Module

- A ComfyUI product image generation workflow (white-background hero + scene shots + infographics)
- An API-driven batch image generation pipeline (Midjourney/GPT Image 2/FLUX.2)
- An automated product video generation system
- A brand visual consistency assurance mechanism

> **Core idea**: E-commerce product images are the number-one factor in conversion rate. The traditional approach is to hire a photographer ($500-2000/product); the AI approach is to generate with ComfyUI/Midjourney ($0-50/product). But AI generation isn't "one-click image creation" — you need to build a repeatable, controllable, brand-consistent pipeline.

> **Related reading**: [A7 Visual Content](../a-operators/a7-visual-content.md) — AI visual content methodology from the operator's perspective

---

## 1. Why You Need an AI Image Pipeline

### 1.1 E-commerce Image Demand Matrix

| Image type | Purpose | Quantity/product | Traditional cost | AI cost |
|------------|---------|------------------|------------------|---------|
| White-background hero | Amazon/Shopify main image | 1 | $100-300 | $0-5 |
| Scene shot | Use-case display | 3-5 | $200-500 | $5-20 |
| Infographic | Size/comparison/feature explanation | 2-3 | $100-200 | $5-10 |
| A+ Content | Brand story visuals | 5-7 | $300-500 | $10-30 |
| Social media | Instagram/TikTok assets | 10-20/month | $500-1000/month | $20-50/month |
| Ad creative | PPC/Meta/Google Ads | 5-10 variants | $200-500 | $10-30 |

### 1.2 Challenges of AI Image Generation

| Challenge | Description | Solution |
|-----------|-------------|----------|
| Product consistency | The AI-generated product appearance may differ from the real item | Use real product photos as reference (ControlNet/IP-Adapter) |
| Brand consistency | Different images have inconsistent styles | Fixed prompt prefix + Style Reference |
| Platform compliance | Amazon main images require pure white backgrounds | Post-process background removal + white-background compositing |
| Text rendering | AI-generated text is frequently wrong | Overlay text in post with Pillow/Canva |
| Copyright risk | AI may generate content similar to existing works | Use commercially licensed tools + human review |

---

## 2. Tech Stack Selection

### 2.1 Option Comparison

| Option | Pros | Cons | Cost | Best for |
|--------|------|------|------|----------|
| ComfyUI (local) | Full control, automatable, free | Requires GPU, steep learning curve | Hardware cost | High volume, technical teams |
| Midjourney | Highest quality, diverse styles | No API (needs Discord), less controllable | $10-30/month | Small volume of high-quality images |
| GPT Image 2 (API) | Has API, programmable | Medium quality, limited styles | Pay-as-you-go | Batch generation, automation |
| Flux (local/API) | Open source, high quality, fine-tunable | Requires GPU | Free/pay-as-you-go | Technical teams, customization |
| Adobe Firefly | Commercially safe, indemnity guarantee | Limited features | From $10/month | Commercial use, compliance-first |
| Canva AI | Simple and easy, rich templates | Low flexibility | $13/month | Non-technical users |

### 2.2 Recommended Combination

```
Recommended AI image tech stack:

Hero / scene image generation:
ComfyUI + Flux (local, full control)
or Midjourney (cloud, highest quality)
or GPT Image 2 API (programmable, batch generation)

Post-processing:
rembg (Python background removal)
Pillow (image processing, text overlay)
OpenCV (advanced image processing)

Batch management:
Python scripts (automated workflows)
Canva Brand Kit (template management)
```

---

## 3. ComfyUI Product Image Workflow

### 3.1 Installing ComfyUI

```bash
# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
pip3 install -r requirements.txt

# Download models (Flux recommended)
# Place model files in the models/checkpoints/ directory

# Launch
python3 main.py
# Open http://127.0.0.1:8188 in your browser
```

### 3.2 Product Image Generation Workflow

> **Real case: ComfyUI product photography workflow in practice**
> MyAIForce demonstrated a complete ComfyUI product image workflow: input a skincare product image and a descriptive prompt, and the workflow automatically blends the product seamlessly into a new background, adjusting lighting and shadows to match the new environment for a natural, harmonious look. The workflow has 7 steps: upload image → set background → basic adjustment → product positioning → relighting → inpainting → detail restoration ([MyAIForce](https://myaiforce.com/comfyui-product-photography/)).

Content rephrased for compliance with licensing restrictions.

> **Real case: Midjourney + ComfyUI combined workflow**
> Another advanced workflow combines Midjourney and ComfyUI: first use Midjourney to generate a high-quality scene background, then use ComfyUI's ControlNet and IP-Adapter to precisely place the product into the scene while adjusting lighting and shadows to preserve key details such as product text ([MyAIForce](https://myaiforce.com/product-photography-comfyui-midjourney/)).

Content rephrased for compliance with licensing restrictions.

> **Real case: ComfyUI background replacement V4 workflow**
> The latest V4 background-replacement workflow uses SDXL checkpoints, requiring only 10 sampling steps and about 6GB VRAM for basic tasks. Using Flux models yields higher-quality results but requires more VRAM ([MyAIForce](https://myaiforce.com/flux-replace-background-v4/)).

Content rephrased for compliance with licensing restrictions.

```
Complete ComfyUI e-commerce product image workflow (7 steps):

Step 1: Upload image and set background
Load Image node: load the real product photo
Background choice: upload a preset background or generate with a prompt
Parameter settings: resolution, sampling steps

Step 2: Basic adjustment
Product cutout (Florence2Run or rembg)
Size adjustment
Initial compositing

Step 3: Product positioning
Adjust the product's position in the frame
Scale ratio
Angle adjustment

Step 4: Relighting
IC-Light node: adjust product lighting to match the background
Shadow direction matching
Highlight adjustment

Step 5: Generate background
Flux Fill + Redux: generate a background matching the product
or IP-Adapter: replicate the style of a reference image
KSampler: execute generation

Step 6: Inpainting
Repair the seam between product and background
Add natural shadows
Detail blending

Step 7: Restore detail and color
Restore the product's original colors
Sharpen details
Final output
Save as PNG/JPEG
```

### 3.3 E-commerce Scene Prompt Templates (40+ tested templates)

> **Real resource**: Apatero compiled 40+ tested AI product image prompt templates covering all e-commerce scenarios — white background, scene, flat lay, infographic, and more ([Apatero](https://www.apatero.com/blog/best-prompts-product-photography-ai-generation-2025)).

Content rephrased for compliance with licensing restrictions.

```python
# E-commerce product image prompt template library (extended version)
PROMPT_TEMPLATES = {
# === Hero image series ===
"amazon_main": {
"positive": "professional product photography, {product}, centered on pure white background #FFFFFF, product fills 85 percent of frame, studio lighting with soft shadows, high resolution 8k, sharp focus, no text no logos no watermarks, commercial catalog style",
"negative": "blurry, low quality, text, watermark, logo, human, hand, colored background, shadow on background, props, accessories not part of product"
},
"shopify_hero": {
"positive": "hero product shot, {product}, clean minimal background with subtle gradient, dramatic studio lighting, slight shadow underneath, premium feel, editorial quality, 4k",
"negative": "cluttered, busy background, text, watermark, low quality"
},

# === Scene image series ===
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

# === Flat lay series ===
"flat_lay_minimal": {
"positive": "flat lay photography, {product} with complementary items, top-down view, clean arrangement on {surface}, soft shadows, minimalist, {color_scheme}",
"negative": "cluttered, messy, blurry, text, 3D perspective"
},
"flat_lay_seasonal": {
"positive": "seasonal flat lay, {product} surrounded by {season} elements, top-down view, cohesive color palette, editorial styling, natural textures",
"negative": "cluttered, artificial, text, watermark"
},

# === Infographic background series ===
"infographic_clean": {
"positive": "clean infographic background for {product}, {color_scheme} gradient, modern design, ample negative space for text overlay, professional, soft lighting on product",
"negative": "text, numbers, charts, cluttered, busy, distracting elements"
},
"infographic_comparison": {
"positive": "split comparison layout background, {product} centered, left side and right side clearly divided, clean modern design, space for before/after or feature comparison text",
"negative": "text, numbers, cluttered"
},

# === Social media series ===
"instagram_aesthetic": {
"positive": "instagram aesthetic product shot, {product}, trendy styling, {color_scheme} color palette, natural lighting, lifestyle feel, square format, influencer style",
"negative": "corporate, boring, text, watermark, low quality"
},
"tiktok_dynamic": {
"positive": "dynamic product shot, {product}, vibrant colors, energetic composition, slight motion blur on background, youth-oriented, vertical format 9:16",
"negative": "static, boring, corporate, text"
},

# === A+ Content series ===
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
"""Generate a product image prompt"""
template = PROMPT_TEMPLATES[template_name]
# Fill in default values
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

# Usage example
prompt = generate_prompt(
"lifestyle_home",
product="wireless bluetooth earbuds with charging case"
)
print(prompt["positive"])
```

---

## 4. Cloud API Approaches

### 4.1 GPT Image 2 Batch Generation

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
"""Generate a product image with GPT Image 2"""

prompts = {
"white_background": f"Professional product photography of {product_description}, centered on pure white background, studio lighting, high resolution, commercial quality",
"lifestyle": f"Lifestyle product photography of {product_description} being used in a modern home setting, natural lighting, warm tones, editorial quality",
"amazon_main": f"Amazon product listing main image: {product_description}, pure white background (#FFFFFF), product fills 85% of frame, no text or logos, professional studio photography"
}

response = client.images.generate(
model="gpt-image-2",
prompt=prompts[style],
size=size,
quality="hd",
n=1
)

# Download the image
image_url = response.data[0].url
Path(output_dir).mkdir(exist_ok=True)

img_data = requests.get(image_url).content
filepath = f"{output_dir}/{product_description[:30]}_{style}.png"
with open(filepath, "wb") as f:
f.write(img_data)

return filepath

# Batch generation
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

### 4.2 Background Removal + White-Background Compositing

```python
from rembg import remove
from PIL import Image
import io

def create_amazon_main_image(input_path: str, output_path: str):
    """Create an Amazon-compliant white-background hero image"""
    # Read the image
    with open(input_path, "rb") as f:
        input_data = f.read()

    # Remove the background
    output_data = remove(input_data)

    # Create a white-background canvas
    fg = Image.open(io.BytesIO(output_data)).convert("RGBA")

    # Compute the product's proportion (Amazon requires 85%+)
    bbox = fg.getbbox()
    product_w = bbox[2] - bbox[0]
    product_h = bbox[3] - bbox[1]

    # Create a square white background (product occupies 85%)
    canvas_size = int(max(product_w, product_h) / 0.85)
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 255))

    # Center the product
    offset_x = (canvas_size - product_w) // 2 - bbox[0]
    offset_y = (canvas_size - product_h) // 2 - bbox[1]
    canvas.paste(fg, (offset_x, offset_y), fg)

    # Save as RGB (Amazon does not accept transparent backgrounds)
    canvas.convert("RGB").save(output_path, "JPEG", quality=95)
    print(f"Amazon main image saved: {output_path}")
```

---

## 5. Batch Generation Pipeline

### 5.1 A Complete Product Image Generation Pipeline

```python
import os
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductImageRequest:
"""Product image generation request"""
product_name: str
product_description: str
source_image: Optional[str] = None # Path to the real product photo
brand_color: str = "blue"
target_platforms: list = None # ["amazon", "shopify", "instagram"]

def __post_init__(self):
if self.target_platforms is None:
self.target_platforms = ["amazon", "shopify"]

class ProductImagePipeline:
"""E-commerce product image batch generation pipeline"""

def __init__(self, method: str = "openai", output_dir: str = "output/images"):
self.method = method
self.output_dir = output_dir
Path(output_dir).mkdir(parents=True, exist_ok=True)
self.log = []

def generate_product_set(self, request: ProductImageRequest) -> dict:
"""Generate a complete image set for one product"""
product_dir = os.path.join(
self.output_dir,
request.product_name.replace(" ", "_")[:30]
)
Path(product_dir).mkdir(exist_ok=True)

results = {"product": request.product_name, "images": {}}

# 1. Amazon white-background hero image
if "amazon" in request.target_platforms:
self._log(f"Generating Amazon hero image: {request.product_name}")
main_img = self._generate_image(
request, "amazon_main",
os.path.join(product_dir, "amazon_main.jpg")
)
# Post-processing: background removal + white-background compositing
amazon_img = self._post_process_amazon(main_img)
results["images"]["amazon_main"] = amazon_img

# Compliance check
compliance = check_amazon_compliance(amazon_img)
results["images"]["amazon_compliance"] = compliance
if not compliance["compliant"]:
self._log(f" Amazon compliance issue: {compliance['issues']}")

# 2. Scene shots x3
scenes = [
("modern living room", "lifestyle_home"),
("outdoor natural setting", "lifestyle_outdoor"),
("clean office desk", "lifestyle_office")
]
results["images"]["lifestyle"] = []
for i, (scene, template) in enumerate(scenes):
self._log(f"Generating scene shot {i+1}/3: {scene}")
img = self._generate_image(
request, template,
os.path.join(product_dir, f"lifestyle_{i+1}.jpg"),
scene=scene
)
results["images"]["lifestyle"].append(img)

# 3. Infographic backgrounds x2
results["images"]["infographic"] = []
for i, color in enumerate(["blue and white", "warm earth tones"]):
self._log(f"Generating infographic background {i+1}/2")
img = self._generate_image(
request, "infographic_clean",
os.path.join(product_dir, f"infographic_{i+1}.jpg"),
color_scheme=color
)
results["images"]["infographic"].append(img)

# 4. Social media assets
if "instagram" in request.target_platforms:
self._log("Generating Instagram asset")
img = self._generate_image(
request, "instagram_aesthetic",
os.path.join(product_dir, "instagram.jpg"),
color_scheme=request.brand_color
)
results["images"]["instagram"] = img

# 5. A+ Content brand story image
self._log("Generating A+ Content image")
img = self._generate_image(
request, "aplus_brand_story",
os.path.join(product_dir, "aplus_brand.jpg")
)
results["images"]["aplus"] = img

# Save metadata
metadata = {
"product": request.product_name,
"generated_at": datetime.now().isoformat(),
"method": self.method,
"images": {k: str(v) for k, v in results["images"].items()},
"log": self.log
}
with open(os.path.join(product_dir, "metadata.json"), "w") as f:
json.dump(metadata, f, indent=2, ensure_ascii=False)

self._log(f" Done: {request.product_name} ({len(results['images'])} images)")
return results

def batch_generate(self, requests: list[ProductImageRequest]) -> list:
"""Batch-generate image sets for multiple products"""
all_results = []
for i, request in enumerate(requests):
print(f"\n{'='*50}")
print(f"Processing {i+1}/{len(requests)}: {request.product_name}")
print(f"{'='*50}")

try:
results = self.generate_product_set(request)
all_results.append(results)
except Exception as e:
self._log(f" Failed: {request.product_name} - {str(e)}")
all_results.append({"product": request.product_name, "error": str(e)})

# Generate the batch report
self._generate_batch_report(all_results)
return all_results

def _generate_image(self, request, template, output_path, **kwargs):
"""Generate a single image (chooses the generation method based on self.method)"""
prompt = generate_prompt(template, request.product_description, **kwargs)

if self.method == "openai":
return self._openai_generate(prompt, output_path)
elif self.method == "comfyui":
return self._comfyui_generate(prompt, request.source_image, output_path)
else:
raise ValueError(f"Unknown method: {self.method}")

def _openai_generate(self, prompt, output_path):
"""GPT Image 2 generation"""
response = client.images.generate(
model="gpt-image-2",
prompt=prompt["positive"],
size="1024x1024",
quality="hd",
n=1
)
# Download and save
import requests
img_data = requests.get(response.data[0].url).content
with open(output_path, "wb") as f:
f.write(img_data)
return output_path

def _post_process_amazon(self, image_path):
"""Amazon hero image post-processing"""
output_path = image_path.replace(".jpg", "_amazon.jpg")
create_amazon_main_image(image_path, output_path)
return output_path

def _log(self, message):
timestamp = datetime.now().strftime("%H:%M:%S")
self.log.append(f"[{timestamp}] {message}")
print(f"[{timestamp}] {message}")

def _generate_batch_report(self, results):
"""Generate the batch-processing report"""
report = f"# Product Image Batch Generation Report\n\n"
report += f"Generated at: {datetime.now().isoformat()}\n"
report += f"Total products: {len(results)}\n"
report += f"Succeeded: {sum(1 for r in results if 'error' not in r)}\n"
report += f"Failed: {sum(1 for r in results if 'error' in r)}\n\n"

for r in results:
if "error" in r:
report += f" {r['product']}: {r['error']}\n"
else:
report += f" {r['product']}: {len(r['images'])} images\n"

with open(os.path.join(self.output_dir, "batch_report.md"), "w") as f:
f.write(report)

# === Usage example ===
if __name__ == "__main__":
pipeline = ProductImagePipeline(method="openai")

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

### 5.2 A/B Testing Image Variants

```python
def generate_ab_test_variants(request: ProductImageRequest,
                              num_variants: int = 3) -> list:
    """Generate multiple hero-image variants for A/B testing"""
    variants = []

    # Variant 1: different angles
    angles = ["front view centered", "45 degree angle", "slight top-down angle"]

    # Variant 2: different lighting
    lightings = ["soft studio lighting", "dramatic side lighting", "bright even lighting"]

    # Variant 3: different composition
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

        img = generate_with_gpt_image(variant_prompt, f"variant_{i+1}.jpg")
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

| Type | Duration | Purpose | AI tool |
|------|----------|---------|---------|
| Product showcase | 15-30s | Amazon video, Shopify | Kling 3 / Seedance 2 |
| Usage tutorial | 30-60s | A+ Content, YouTube | Synthesia / HeyGen |
| Social short video | 15-60s | TikTok/Reels/Shorts | CapCut AI / Runway Gen-4.5 |
| Ad video | 6-15s | PPC video ads | Runway Gen-4.5 / Veo 3.1 |

### 6.2 Product Showcase Video Generation

```python
# Conceptual code: generate a product showcase video with the Runway API
import runway

def generate_product_video(
    product_image: str,
    motion_prompt: str = "slow 360 degree rotation, studio lighting",
    duration: int = 4 # seconds
) -> str:
    """Generate a showcase video from a product image"""

    task = runway.image_to_video.create(
        model="gen3a_turbo",
        prompt_image=product_image,
        prompt_text=motion_prompt,
        duration=duration
    )

    # Wait for generation to complete
    task = runway.tasks.retrieve(task.id)
    while task.status != "SUCCEEDED":
        import time
        time.sleep(5)
        task = runway.tasks.retrieve(task.id)

    return task.output[0] # Video URL
```

---

## 7. Quality Control & Compliance

### 7.1 Amazon Image Compliance Check

```python
def check_amazon_compliance(image_path: str) -> dict:
    """Check whether an image meets Amazon requirements"""
    img = Image.open(image_path)
    issues = []

    # Size check (minimum 1000px)
    if min(img.size) < 1000:
        issues.append(f"Insufficient size: {img.size}, minimum 1000x1000 required")

    # White-background check (hero image)
    pixels = list(img.getdata())
    corners = [pixels[0], pixels[img.width-1],
               pixels[-img.width], pixels[-1]]
    for i, corner in enumerate(corners):
        if not all(c > 240 for c in corner[:3]):
            issues.append(f"Corner {i} is not pure white: {corner}")

    # Product proportion check
    # ... (check whether the product occupies 85%+ of the frame)

    return {
        "compliant": len(issues) == 0,
        "issues": issues,
        "size": img.size,
        "format": img.format
    }
```

### 7.2 Brand Consistency Check

| Check item | Method | Tool |
|------------|--------|------|
| Color consistency | Extract the dominant color and compare with the brand color | Pillow + ColorThief |
| Style consistency | CLIP embedding similarity | sentence-transformers |
| Logo position | Template check | Pillow |
| Text font | OCR + font matching | Tesseract |

---

## 8. Common Traps

### 8.1 Using text-to-image for the main product shot

Text-to-image re-imagines your product; details, proportions, and logo drift. The product itself must go image-to-image or image-to-video from a real photo. This is a compliance issue as much as a quality one.

### 8.2 Not keeping metadata on generated images

Which image is AI-generated, with what tool, when — under the EU AI Act's transparency duties you need to be able to answer this. See [A6 §5](../a-operators/a6-compliance.md).

### 8.3 Batch generating with no human screening

AI image yield is lower than people assume, especially on hands, text, reflections, and material rendering. The pipeline needs a human spot-check stage; the rate can be low but not zero.

### 8.4 Ignoring per-platform image specs

White background for the main image, minimum dimensions, text-coverage limits — rules differ by platform. Generate without those constraints and you'll either be rejected or redo the work.

---

## 9. Completion Checklist

- [ ] Set up ComfyUI or choose an API approach
- [ ] Generate a complete image set for one product (hero + scene + infographic)
- [ ] Implement an automated background-removal + white-background-compositing flow
- [ ] Build a batch generation pipeline (process 5+ products at once)
- [ ] Pass the Amazon image compliance check
- [ ] Generate at least 1 product showcase video

[< B8 E-Commerce Dashboard](b8-ecommerce-dashboard.md) | [Path overview](../README.md)
