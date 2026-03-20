# B9. AI 产品图片与视频生成 Pipeline

> **路径**: Path B: 技术人 · **模块**: B9
> **最后更新**: 2026-03-15
> **难度**: 高级
> **预计时间**: 每天 1 小时，2-3 周
> **前置模块**: 无（独立模块，但建议了解 [A7 视觉内容](../a-operators/a7-visual-content.md)）

[Hub 首页](../../README.md) · [Path B 总览](README.md)

---

## 章节导航

1. [为什么需要 AI 图片 Pipeline](#1-为什么需要-ai-图片-pipeline) · 2. [技术栈选择](#2-技术栈选择) · 3. [ComfyUI 产品图工作流](#3-comfyui-产品图工作流) · 4. [API 方案](#4-api-方案midjourneydall-eflux) · 5. [批量生成 Pipeline](#5-批量生成-pipeline) · 6. [视频生成](#6-ai-视频生成) · 7. [质量控制与合规](#7-质量控制与合规) · 8. [完成标志](#8-完成标志)

---

## 本模块你将构建

- 一个 ComfyUI 产品图生成工作流（白底主图 + 场景图 + 信息图）
- 一个 API 驱动的批量图片生成 Pipeline（Midjourney/DALL-E/Flux）
- 一个产品视频自动生成系统
- 品牌视觉一致性保障机制

> **核心理念**：电商产品图是转化率的第一要素。传统方式是请摄影师拍摄（$500-2000/产品），AI 方式是用 ComfyUI/Midjourney 生成（$0-50/产品）。但 AI 生成不是"一键出图"，需要构建可重复、可控制、品牌一致的 Pipeline。

> **相关阅读**: [A7 视觉内容](../a-operators/a7-visual-content.md) 运营视角的 AI 视觉内容方法论

---

## 1. 为什么需要 AI 图片 Pipeline

### 1.1 电商图片需求矩阵

| 图片类型 | 用途 | 数量/产品 | 传统成本 | AI 成本 |
|----------|------|----------|---------|---------|
| 白底主图 | Amazon/Shopify 主图 | 1 | $100-300 | $0-5 |
| 场景图 | 使用场景展示 | 3-5 | $200-500 | $5-20 |
| 信息图 | 尺寸/对比/功能说明 | 2-3 | $100-200 | $5-10 |
| A+ Content | 品牌故事图文 | 5-7 | $300-500 | $10-30 |
| 社交媒体 | Instagram/TikTok 素材 | 10-20/月 | $500-1000/月 | $20-50/月 |
| 广告素材 | PPC/Meta/Google Ads | 5-10 变体 | $200-500 | $10-30 |

### 1.2 AI 图片生成的挑战

| 挑战 | 说明 | 解决方案 |
|------|------|---------|
| 产品一致性 | AI 生成的产品外观可能与实物不同 | 使用产品实拍图作为参考（ControlNet/IP-Adapter） |
| 品牌一致性 | 不同图片风格不统一 | 固定 Prompt 前缀 + Style Reference |
| 平台合规 | Amazon 主图要求纯白底 | 后处理去背景 + 白底合成 |
| 文字渲染 | AI 生成的文字经常出错 | 后处理用 Pillow/Canva 叠加文字 |
| 版权风险 | AI 可能生成与已有作品相似的内容 | 使用商业许可工具 + 人工审核 |

---

## 2. 技术栈选择

### 2.1 方案对比

| 方案 | 优点 | 缺点 | 成本 | 适合 |
|------|------|------|------|------|
| ComfyUI（本地） | 完全控制、可自动化、免费 | 需要 GPU、学习曲线陡 | 硬件成本 | 大量图片、技术团队 |
| Midjourney | 质量最高、风格多样 | 无 API（需要 Discord）、不可控 | $10-30/月 | 少量高质量图片 |
| DALL-E 3（API） | 有 API、可编程 | 质量中等、风格有限 | 按量付费 | 批量生成、自动化 |
| Flux（本地/API） | 开源、质量高、可微调 | 需要 GPU | 免费/按量 | 技术团队、定制化 |
| Adobe Firefly | 商业安全、有赔偿保障 | 功能有限 | $10/月起 | 商业使用、合规优先 |
| Canva AI | 简单易用、模板丰富 | 灵活性低 | $13/月 | 非技术人员 |

### 2.2 推荐组合

```
推荐的 AI 图片技术栈：

主图/场景图生成：
ComfyUI + Flux（本地，完全控制）
或 Midjourney（云端，质量最高）
或 DALL-E 3 API（可编程，批量生成）

后处理：
rembg（Python 去背景）
Pillow（图片处理、文字叠加）
OpenCV（高级图片处理）

批量管理：
Python 脚本（自动化工作流）
Canva Brand Kit（模板管理）
```

---

## 3. ComfyUI 产品图工作流

### 3.1 安装 ComfyUI

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

### 3.2 产品图生成工作流

> **真实案例：ComfyUI 产品图工作流实战**
> MyAIForce 展示了一个完整的 ComfyUI 产品图工作流：输入一张护肤品图片和描述性 Prompt，工作流自动将产品无缝融入新背景，调整光照和阴影以匹配新环境，确保自然和谐的外观。工作流包含 7 个步骤：上传图片→设置背景→基础调整→产品定位→重新打光→重绘→恢复细节（[MyAIForce](https://myaiforce.com/comfyui-product-photography/)）。

Content rephrased for compliance with licensing restrictions.

> **真实案例：Midjourney + ComfyUI 组合工作流**
> 另一个高级工作流将 Midjourney 和 ComfyUI 结合：先用 Midjourney 生成高质量的场景背景，再用 ComfyUI 的 ControlNet 和 IP-Adapter 将产品精确放置到场景中，同时调整光照和阴影以保留产品文字等关键细节（[MyAIForce](https://myaiforce.com/product-photography-comfyui-midjourney/)）。

Content rephrased for compliance with licensing restrictions.

> **真实案例：ComfyUI 背景替换 V4 工作流**
> 最新的 V4 背景替换工作流使用 SDXL checkpoints，仅需 10 个采样步骤和约 6GB VRAM 即可完成基础任务。使用 Flux 模型可以获得更高质量的效果，但需要更多 VRAM（[MyAIForce](https://myaiforce.com/flux-replace-background-v4/)）。

Content rephrased for compliance with licensing restrictions.

```
ComfyUI 电商产品图完整工作流（7 步）：

Step 1: 上传图片和设置背景
Load Image 节点：加载产品实拍图
背景选择：上传预设背景 或 用 Prompt 生成
参数设置：分辨率、采样步数

Step 2: 基础调整
产品抠图（Florence2Run 或 rembg）
尺寸调整
初始合成

Step 3: 产品定位
调整产品在画面中的位置
缩放比例
角度调整

Step 4: 重新打光（Relighting）
IC-Light 节点：根据背景调整产品光照
阴影方向匹配
高光调整

Step 5: 生成背景
Flux Fill + Redux：生成与产品匹配的背景
或 IP-Adapter：复制参考图片的风格
KSampler：执行生成

Step 6: 重绘（Inpainting）
修复产品与背景的接缝
添加自然阴影
细节融合

Step 7: 恢复细节和颜色
恢复产品原始颜色
锐化细节
最终输出
保存为 PNG/JPEG
```

### 3.3 电商场景 Prompt 模板（40+ 测试过的模板）

> **真实资源**：Apatero 整理了 40+ 经过测试的 AI 产品图 Prompt 模板，覆盖白底、场景、平铺、信息图等所有电商场景（[Apatero](https://www.apatero.com/blog/best-prompts-product-photography-ai-generation-2025)）。

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

## 4. API 方案（Midjourney/DALL-E/Flux）

### 4.1 DALL-E 3 批量生成

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

### 4.2 去背景 + 白底合成

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

## 5. 批量生成 Pipeline

### 5.1 完整的产品图生成 Pipeline

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
source_image: Optional[str] = None # 产品实拍图路径
brand_color: str = "blue"
target_platforms: list = None # ["amazon", "shopify", "instagram"]

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
self._log(f" Amazon 合规问题: {compliance['issues']}")

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

self._log(f" 完成: {request.product_name} ({len(results['images'])} 张图片)")
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
self._log(f" 失败: {request.product_name} - {str(e)}")
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
report += f" {r['product']}: {r['error']}\n"
else:
report += f" {r['product']}: {len(r['images'])} 张图片\n"

with open(os.path.join(self.output_dir, "batch_report.md"), "w") as f:
f.write(report)

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

### 5.2 A/B 测试图片变体

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

## 6. AI 视频生成

### 6.1 产品视频类型

| 类型 | 时长 | 用途 | AI 工具 |
|------|------|------|---------|
| 产品展示 | 15-30s | Amazon 视频、Shopify | Runway Gen-3 / Pika |
| 使用教程 | 30-60s | A+ Content、YouTube | Synthesia / HeyGen |
| 社交短视频 | 15-60s | TikTok/Reels/Shorts | CapCut AI / Runway |
| 广告视频 | 6-15s | PPC 视频广告 | Runway / Sora |

### 6.2 产品展示视频生成

```python
# 概念代码：用 Runway API 生成产品展示视频
import runway

def generate_product_video(
product_image: str,
motion_prompt: str = "slow 360 degree rotation, studio lighting",
duration: int = 4 # 秒
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

return task.output[0] # 视频 URL
```

---

## 7. 质量控制与合规

### 7.1 Amazon 图片合规检查

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

### 7.2 品牌一致性检查

| 检查项 | 方法 | 工具 |
|--------|------|------|
| 配色一致 | 提取主色调对比品牌色 | Pillow + ColorThief |
| 风格一致 | CLIP 嵌入相似度 | sentence-transformers |
| Logo 位置 | 模板检查 | Pillow |
| 文字字体 | OCR + 字体匹配 | Tesseract |

---

## 8. 完成标志

- [ ] 搭建 ComfyUI 或选择 API 方案
- [ ] 为一个产品生成完整图片集（主图+场景图+信息图）
- [ ] 实现去背景+白底合成的自动化流程
- [ ] 构建批量生成 Pipeline（一次处理 5+ 产品）
- [ ] 通过 Amazon 图片合规检查
- [ ] 生成至少 1 个产品展示视频

---
> [Hub 首页](../../README.md) · [Path B 总览](README.md)
>
> **Path B**: [B1 数据管道](b1-data-pipeline.md) · [B2 预测模型](b2-prediction-models.md) · [B3 RAG 知识库](b3-rag-knowledge-base.md) · [B4 AI Agent](b4-agent-workflow.md) · [B5 本地模型](b5-local-model-deploy.md) · [B6 MCP 集成](b6-mcp-agentic-workflow.md) · [B7 Review NLP](b7-review-nlp-system.md) · [B8 Dashboard](b8-ecommerce-dashboard.md) · [B9 AI 图片生成](b9-ai-image-pipeline.md)
>
> **快速跳转**: [Path 0 基础](../0-foundations/) · [Path A 运营](../a-operators/) · [Path C 管理](../c-managers/) · [Path D 多平台](../d-platforms/) · [Path E 社交媒体](../e-social-media/)
