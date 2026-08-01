# B9. AI 製品画像・動画生成 Pipeline

> **トラック**: Path B: 技術 · **モジュール**: B9
> **最終更新**: 2026-07-31
> **難易度**: 上級
> **所要時間**: 1 日 1 時間、2〜3 週間
> **前提モジュール**: なし(独立モジュール、ただし [A7 視覚コンテンツ](../a-operators/a7-visual-content.md) の理解を推奨)


---

## 章ナビゲーション

1. [なぜ AI 画像 Pipeline が必要か](#1-なぜ-ai-画像-pipeline-が必要か) · 2. [技術スタックの選択](#2-技術スタックの選択) · 3. [ComfyUI 製品画像ワークフロー](#3-comfyui-製品画像ワークフロー) · 4. [クラウド API 方式](#4-クラウド-api-方式) · 5. [バッチ生成 Pipeline](#5-バッチ生成-pipeline) · 6. [動画生成](#6-ai-動画生成) · 7. [品質管理とコンプライアンス](#7-品質管理とコンプライアンス) · 8. [よくある罠](#8-よくある罠) · 9. [完了チェック](#9-完了チェック)

---

## このモジュールで構築するもの

- ComfyUI 製品画像生成ワークフロー(白背景メイン画像 + シーン画像 + インフォグラフィック)
- API 駆動のバッチ画像生成 Pipeline(Midjourney/GPT Image 2/FLUX.2)
- 製品動画の自動生成システム
- ブランドビジュアルの一貫性保証メカニズム

> **核心理念**: EC の製品画像は転換率の第一要素。従来のやり方はカメラマンに撮影を依頼($500-2000/製品)、AI のやり方は ComfyUI/Midjourney で生成($0-50/製品)。しかし AI 生成は「ワンクリックで画像が出る」わけではなく、再現可能・制御可能・ブランド一貫の Pipeline を構築する必要がある。

> **関連リーディング**: [A7 視覚コンテンツ](../a-operators/a7-visual-content.md) 運営視点の AI ビジュアルコンテンツ方法論

---

## 1. なぜ AI 画像 Pipeline が必要か

### 1.1 EC 画像需要マトリクス

| 画像タイプ | 用途 | 数量/製品 | 従来コスト | AI コスト |
|------------|------|-----------|------------|-----------|
| 白背景メイン画像 | Amazon/Shopify メイン画像 | 1 | $100-300 | $0-5 |
| シーン画像 | 使用シーンの展示 | 3-5 | $200-500 | $5-20 |
| インフォグラフィック | サイズ/比較/機能説明 | 2-3 | $100-200 | $5-10 |
| A+ Content | ブランドストーリーの図文 | 5-7 | $300-500 | $10-30 |
| ソーシャルメディア | Instagram/TikTok 素材 | 10-20/月 | $500-1000/月 | $20-50/月 |
| 広告素材 | PPC/Meta/Google Ads | 5-10 バリエーション | $200-500 | $10-30 |

### 1.2 AI 画像生成の課題

| 課題 | 説明 | 解決策 |
|------|------|--------|
| 製品の一貫性 | AI 生成の製品外観が実物と異なる可能性 | 製品実写画像を参照に使用(ControlNet/IP-Adapter) |
| ブランドの一貫性 | 画像ごとにスタイルが不統一 | 固定 Prompt 接頭辞 + Style Reference |
| プラットフォームのコンプライアンス | Amazon メイン画像は純白背景が必須 | 後処理で背景除去 + 白背景合成 |
| 文字レンダリング | AI 生成の文字はしばしば誤る | 後処理で Pillow/Canva を使い文字を重ねる |
| 著作権リスク | AI が既存作品に似たコンテンツを生成する可能性 | 商用ライセンスツールを使用 + 人手審査 |

---

## 2. 技術スタックの選択

### 2.1 方案の比較

| 方案 | 利点 | 欠点 | コスト | 向く |
|------|------|------|--------|------|
| ComfyUI(ローカル) | 完全制御、自動化可能、無料 | GPU が必要、学習曲線が急 | ハードウェアコスト | 大量画像、技術チーム |
| Midjourney | 品質最高、スタイル多様 | API なし(Discord が必要)、制御不可 | $10-30/月 | 少量の高品質画像 |
| GPT Image 2(API) | API あり、プログラム可能 | 品質中程度、スタイルに制限 | 従量課金 | バッチ生成、自動化 |
| Flux(ローカル/API) | オープンソース、高品質、微調整可能 | GPU が必要 | 無料/従量 | 技術チーム、カスタマイズ |
| Adobe Firefly | 商用安全、賠償保証あり | 機能に制限 | $10/月〜 | 商用利用、コンプライアンス優先 |
| Canva AI | シンプルで使いやすい、テンプレート豊富 | 柔軟性が低い | $13/月 | 非技術者 |

### 2.2 推奨の組み合わせ

```
推奨の AI 画像技術スタック:

メイン画像/シーン画像の生成:
ComfyUI + Flux(ローカル、完全制御)
または Midjourney(クラウド、品質最高)
または GPT Image 2 API(プログラム可能、バッチ生成)

後処理:
rembg(Python 背景除去)
Pillow(画像処理、文字オーバーレイ)
OpenCV(高度な画像処理)

バッチ管理:
Python スクリプト(自動化ワークフロー)
Canva Brand Kit(テンプレート管理)
```

---

## 3. ComfyUI 製品画像ワークフロー

### 3.1 ComfyUI のインストール

```bash
# ComfyUI をクローン
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 依存関係をインストール
pip3 install -r requirements.txt

# モデルをダウンロード(Flux 推奨)
# モデルファイルを models/checkpoints/ ディレクトリに配置

# 起動
python3 main.py
# ブラウザで http://127.0.0.1:8188 を開く
```

### 3.2 製品画像生成ワークフロー

> **実事例: ComfyUI 製品画像ワークフローの実戦**
> MyAIForce は完全な ComfyUI 製品画像ワークフローを示した。スキンケア製品の画像と説明的な Prompt を入力すると、ワークフローが自動で製品を新しい背景にシームレスに融合し、光照と影を新環境に合わせて調整し、自然で調和のとれた見た目を確保する。ワークフローは 7 ステップ: 画像アップロード→背景設定→基礎調整→製品配置→再照明→インペイント→ディテール復元([MyAIForce](https://myaiforce.com/comfyui-product-photography/))。

Content rephrased for compliance with licensing restrictions.

> **実事例: Midjourney + ComfyUI 組み合わせワークフロー**
> もう 1 つの高度なワークフローは Midjourney と ComfyUI を組み合わせる: まず Midjourney で高品質なシーン背景を生成し、次に ComfyUI の ControlNet と IP-Adapter で製品をシーンに正確に配置しつつ、光照と影を調整して製品の文字など重要なディテールを保持する([MyAIForce](https://myaiforce.com/product-photography-comfyui-midjourney/))。

Content rephrased for compliance with licensing restrictions.

> **実事例: ComfyUI 背景置換 V4 ワークフロー**
> 最新の V4 背景置換ワークフローは SDXL checkpoints を使い、基礎タスクはわずか 10 サンプリングステップと約 6GB VRAM で完了できる。Flux モデルを使えばより高品質な効果が得られるが、より多くの VRAM が必要([MyAIForce](https://myaiforce.com/flux-replace-background-v4/))。

Content rephrased for compliance with licensing restrictions.

```
ComfyUI EC 製品画像の完全ワークフロー(7 ステップ):

Step 1: 画像アップロードと背景設定
Load Image ノード: 製品実写画像を読み込む
背景選択: プリセット背景をアップロード または Prompt で生成
パラメータ設定: 解像度、サンプリングステップ数

Step 2: 基礎調整
製品切り抜き(Florence2Run または rembg)
サイズ調整
初期合成

Step 3: 製品配置
画面内の製品位置を調整
拡大縮小比率
角度調整

Step 4: 再照明(Relighting)
IC-Light ノード: 背景に応じて製品の光照を調整
影の方向のマッチング
ハイライト調整

Step 5: 背景生成
Flux Fill + Redux: 製品にマッチする背景を生成
または IP-Adapter: 参照画像のスタイルを複製
KSampler: 生成を実行

Step 6: インペイント(Inpainting)
製品と背景の継ぎ目を修復
自然な影を追加
ディテールの融合

Step 7: ディテールと色の復元
製品の元の色を復元
ディテールをシャープ化
最終出力
PNG/JPEG として保存
```

### 3.3 EC シーン Prompt テンプレート(40+ のテスト済みテンプレート)

> **実リソース**: Apatero は 40+ のテスト済み AI 製品画像 Prompt テンプレートを整理し、白背景、シーン、平置き、インフォグラフィックなどすべての EC シーンをカバーした([Apatero](https://www.apatero.com/blog/best-prompts-product-photography-ai-generation-2025))。

Content rephrased for compliance with licensing restrictions.

```python
# EC 製品画像 Prompt テンプレートライブラリ(拡張版)
PROMPT_TEMPLATES = {
# === メイン画像シリーズ ===
"amazon_main": {
"positive": "professional product photography, {product}, centered on pure white background #FFFFFF, product fills 85 percent of frame, studio lighting with soft shadows, high resolution 8k, sharp focus, no text no logos no watermarks, commercial catalog style",
"negative": "blurry, low quality, text, watermark, logo, human, hand, colored background, shadow on background, props, accessories not part of product"
},
"shopify_hero": {
"positive": "hero product shot, {product}, clean minimal background with subtle gradient, dramatic studio lighting, slight shadow underneath, premium feel, editorial quality, 4k",
"negative": "cluttered, busy background, text, watermark, low quality"
},

# === シーン画像シリーズ ===
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

# === 平置き画像シリーズ ===
"flat_lay_minimal": {
"positive": "flat lay photography, {product} with complementary items, top-down view, clean arrangement on {surface}, soft shadows, minimalist, {color_scheme}",
"negative": "cluttered, messy, blurry, text, 3D perspective"
},
"flat_lay_seasonal": {
"positive": "seasonal flat lay, {product} surrounded by {season} elements, top-down view, cohesive color palette, editorial styling, natural textures",
"negative": "cluttered, artificial, text, watermark"
},

# === インフォグラフィック背景シリーズ ===
"infographic_clean": {
"positive": "clean infographic background for {product}, {color_scheme} gradient, modern design, ample negative space for text overlay, professional, soft lighting on product",
"negative": "text, numbers, charts, cluttered, busy, distracting elements"
},
"infographic_comparison": {
"positive": "split comparison layout background, {product} centered, left side and right side clearly divided, clean modern design, space for before/after or feature comparison text",
"negative": "text, numbers, cluttered"
},

# === ソーシャルメディアシリーズ ===
"instagram_aesthetic": {
"positive": "instagram aesthetic product shot, {product}, trendy styling, {color_scheme} color palette, natural lighting, lifestyle feel, square format, influencer style",
"negative": "corporate, boring, text, watermark, low quality"
},
"tiktok_dynamic": {
"positive": "dynamic product shot, {product}, vibrant colors, energetic composition, slight motion blur on background, youth-oriented, vertical format 9:16",
"negative": "static, boring, corporate, text"
},

# === A+ Content シリーズ ===
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
"""製品画像 Prompt を生成"""
template = PROMPT_TEMPLATES[template_name]
# デフォルト値を埋める
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

# 使用例
prompt = generate_prompt(
"lifestyle_home",
product="wireless bluetooth earbuds with charging case"
)
print(prompt["positive"])
```

---

## 4. クラウド API 方式

### 4.1 GPT Image 2 バッチ生成

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
"""GPT Image 2 で製品画像を生成"""

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

# 画像をダウンロード
image_url = response.data[0].url
Path(output_dir).mkdir(exist_ok=True)

img_data = requests.get(image_url).content
filepath = f"{output_dir}/{product_description[:30]}_{style}.png"
with open(filepath, "wb") as f:
f.write(img_data)

return filepath

# バッチ生成
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

### 4.2 背景除去 + 白背景合成

```python
from rembg import remove
from PIL import Image
import io

def create_amazon_main_image(input_path: str, output_path: str):
"""Amazon 準拠の白背景メイン画像を作成"""
# 画像を読み込む
with open(input_path, "rb") as f:
input_data = f.read()

# 背景を除去
output_data = remove(input_data)

# 白背景キャンバスを作成
fg = Image.open(io.BytesIO(output_data)).convert("RGBA")

# 製品の占有率を計算(Amazon は 85%+ を要求)
bbox = fg.getbbox()
product_w = bbox[2] - bbox[0]
product_h = bbox[3] - bbox[1]

# 正方形の白背景を作成(製品が 85% を占める)
canvas_size = int(max(product_w, product_h) / 0.85)
canvas = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 255))

# 製品を中央に配置
offset_x = (canvas_size - product_w) // 2 - bbox[0]
offset_y = (canvas_size - product_h) // 2 - bbox[1]
canvas.paste(fg, (offset_x, offset_y), fg)

# RGB として保存(Amazon は透明背景を受け付けない)
canvas.convert("RGB").save(output_path, "JPEG", quality=95)
print(f"Amazon main image saved: {output_path}")
```

---

## 5. バッチ生成 Pipeline

### 5.1 完全な製品画像生成 Pipeline

```python
import os
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductImageRequest:
"""製品画像生成リクエスト"""
product_name: str
product_description: str
source_image: Optional[str] = None # 製品実写画像のパス
brand_color: str = "blue"
target_platforms: list = None # ["amazon", "shopify", "instagram"]

def __post_init__(self):
if self.target_platforms is None:
self.target_platforms = ["amazon", "shopify"]

class ProductImagePipeline:
"""EC 製品画像バッチ生成 Pipeline"""

def __init__(self, method: str = "openai", output_dir: str = "output/images"):
self.method = method
self.output_dir = output_dir
Path(output_dir).mkdir(parents=True, exist_ok=True)
self.log = []

def generate_product_set(self, request: ProductImageRequest) -> dict:
"""1 つの製品向けに完全な画像セットを生成"""
product_dir = os.path.join(
self.output_dir,
request.product_name.replace(" ", "_")[:30]
)
Path(product_dir).mkdir(exist_ok=True)

results = {"product": request.product_name, "images": {}}

# 1. Amazon 白背景メイン画像
if "amazon" in request.target_platforms:
self._log(f"Amazon メイン画像を生成: {request.product_name}")
main_img = self._generate_image(
request, "amazon_main",
os.path.join(product_dir, "amazon_main.jpg")
)
# 後処理: 背景除去 + 白背景合成
amazon_img = self._post_process_amazon(main_img)
results["images"]["amazon_main"] = amazon_img

# コンプライアンスチェック
compliance = check_amazon_compliance(amazon_img)
results["images"]["amazon_compliance"] = compliance
if not compliance["compliant"]:
self._log(f" Amazon コンプライアンス問題: {compliance['issues']}")

# 2. シーン画像 x3
scenes = [
("modern living room", "lifestyle_home"),
("outdoor natural setting", "lifestyle_outdoor"),
("clean office desk", "lifestyle_office")
]
results["images"]["lifestyle"] = []
for i, (scene, template) in enumerate(scenes):
self._log(f"シーン画像を生成 {i+1}/3: {scene}")
img = self._generate_image(
request, template,
os.path.join(product_dir, f"lifestyle_{i+1}.jpg"),
scene=scene
)
results["images"]["lifestyle"].append(img)

# 3. インフォグラフィック背景 x2
results["images"]["infographic"] = []
for i, color in enumerate(["blue and white", "warm earth tones"]):
self._log(f"インフォグラフィック背景を生成 {i+1}/2")
img = self._generate_image(
request, "infographic_clean",
os.path.join(product_dir, f"infographic_{i+1}.jpg"),
color_scheme=color
)
results["images"]["infographic"].append(img)

# 4. ソーシャルメディア素材
if "instagram" in request.target_platforms:
self._log("Instagram 素材を生成")
img = self._generate_image(
request, "instagram_aesthetic",
os.path.join(product_dir, "instagram.jpg"),
color_scheme=request.brand_color
)
results["images"]["instagram"] = img

# 5. A+ Content ブランドストーリー画像
self._log("A+ Content 画像を生成")
img = self._generate_image(
request, "aplus_brand_story",
os.path.join(product_dir, "aplus_brand.jpg")
)
results["images"]["aplus"] = img

# メタデータを保存
metadata = {
"product": request.product_name,
"generated_at": datetime.now().isoformat(),
"method": self.method,
"images": {k: str(v) for k, v in results["images"].items()},
"log": self.log
}
with open(os.path.join(product_dir, "metadata.json"), "w") as f:
json.dump(metadata, f, indent=2, ensure_ascii=False)

self._log(f" 完了: {request.product_name} ({len(results['images'])} 枚の画像)")
return results

def batch_generate(self, requests: list[ProductImageRequest]) -> list:
"""複数製品の画像セットをバッチ生成"""
all_results = []
for i, request in enumerate(requests):
print(f"\n{'='*50}")
print(f"Processing {i+1}/{len(requests)}: {request.product_name}")
print(f"{'='*50}")

try:
results = self.generate_product_set(request)
all_results.append(results)
except Exception as e:
self._log(f" 失敗: {request.product_name} - {str(e)}")
all_results.append({"product": request.product_name, "error": str(e)})

# バッチレポートを生成
self._generate_batch_report(all_results)
return all_results

def _generate_image(self, request, template, output_path, **kwargs):
"""単一画像を生成(method に応じて生成方式を選択)"""
prompt = generate_prompt(template, request.product_description, **kwargs)

if self.method == "openai":
return self._openai_generate(prompt, output_path)
elif self.method == "comfyui":
return self._comfyui_generate(prompt, request.source_image, output_path)
else:
raise ValueError(f"Unknown method: {self.method}")

def _openai_generate(self, prompt, output_path):
"""GPT Image 2 生成"""
response = client.images.generate(
model="gpt-image-2",
prompt=prompt["positive"],
size="1024x1024",
quality="hd",
n=1
)
# ダウンロードして保存
import requests
img_data = requests.get(response.data[0].url).content
with open(output_path, "wb") as f:
f.write(img_data)
return output_path

def _post_process_amazon(self, image_path):
"""Amazon メイン画像の後処理"""
output_path = image_path.replace(".jpg", "_amazon.jpg")
create_amazon_main_image(image_path, output_path)
return output_path

def _log(self, message):
timestamp = datetime.now().strftime("%H:%M:%S")
self.log.append(f"[{timestamp}] {message}")
print(f"[{timestamp}] {message}")

def _generate_batch_report(self, results):
"""バッチ処理レポートを生成"""
report = f"# 製品画像バッチ生成レポート\n\n"
report += f"生成時刻: {datetime.now().isoformat()}\n"
report += f"総製品数: {len(results)}\n"
report += f"成功: {sum(1 for r in results if 'error' not in r)}\n"
report += f"失敗: {sum(1 for r in results if 'error' in r)}\n\n"

for r in results:
if "error" in r:
report += f" {r['product']}: {r['error']}\n"
else:
report += f" {r['product']}: {len(r['images'])} 枚の画像\n"

with open(os.path.join(self.output_dir, "batch_report.md"), "w") as f:
f.write(report)

# === 使用例 ===
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

### 5.2 A/B テスト画像バリエーション

```python
def generate_ab_test_variants(request: ProductImageRequest,
num_variants: int = 3) -> list:
"""A/B テスト向けに複数のメイン画像バリエーションを生成"""
variants = []

# バリエーション 1: 異なる角度
angles = ["front view centered", "45 degree angle", "slight top-down angle"]

# バリエーション 2: 異なる光照
lightings = ["soft studio lighting", "dramatic side lighting", "bright even lighting"]

# バリエーション 3: 異なる構図
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

## 6. AI 動画生成

### 6.1 製品動画のタイプ

| タイプ | 長さ | 用途 | AI ツール |
|--------|------|------|-----------|
| 製品展示 | 15-30s | Amazon 動画、Shopify | Runway Gen-3 / Pika |
| 使用チュートリアル | 30-60s | A+ Content、YouTube | Synthesia / HeyGen |
| ソーシャルショート動画 | 15-60s | TikTok/Reels/Shorts | CapCut AI / Runway |
| 広告動画 | 6-15s | PPC 動画広告 | Runway Gen-4.5 / Veo 3.1 |

### 6.2 製品展示動画の生成

```python
# コンセプトコード: Runway API で製品展示動画を生成
import runway

def generate_product_video(
product_image: str,
motion_prompt: str = "slow 360 degree rotation, studio lighting",
duration: int = 4 # 秒
) -> str:
"""製品画像から展示動画を生成"""

task = runway.image_to_video.create(
model="gen3a_turbo",
prompt_image=product_image,
prompt_text=motion_prompt,
duration=duration
)

# 生成完了を待つ
task = runway.tasks.retrieve(task.id)
while task.status != "SUCCEEDED":
import time
time.sleep(5)
task = runway.tasks.retrieve(task.id)

return task.output[0] # 動画 URL
```

---

## 7. 品質管理とコンプライアンス

### 7.1 Amazon 画像コンプライアンスチェック

```python
def check_amazon_compliance(image_path: str) -> dict:
"""画像が Amazon の要件を満たすかチェック"""
img = Image.open(image_path)
issues = []

# サイズチェック(最小 1000px)
if min(img.size) < 1000:
issues.append(f"サイズ不足: {img.size}、最小 1000x1000 が必要")

# 白背景チェック(メイン画像)
pixels = list(img.getdata())
corners = [pixels[0], pixels[img.width-1],
pixels[-img.width], pixels[-1]]
for i, corner in enumerate(corners):
if not all(c > 240 for c in corner[:3]):
issues.append(f"角 {i} が純白ではない: {corner}")

# 製品占有率チェック
# ... (製品が画面の 85%+ を占めるかチェック)

return {
"compliant": len(issues) == 0,
"issues": issues,
"size": img.size,
"format": img.format
}
```

### 7.2 ブランド一貫性チェック

| チェック項目 | 方法 | ツール |
|--------------|------|--------|
| 配色の一貫性 | 主色調を抽出しブランド色と比較 | Pillow + ColorThief |
| スタイルの一貫性 | CLIP 埋め込みの類似度 | sentence-transformers |
| Logo の位置 | テンプレートチェック | Pillow |
| 文字フォント | OCR + フォントマッチング | Tesseract |

---

## 8. よくある罠

### 8.1 メイン商品画像をテキストから生成する

テキストからの生成はあなたの商品を想像し直すため、細部・比率・ロゴがずれる。商品そのものは実物写真を起点に、画像から画像/画像から動画で作ること。品質だけでなくコンプライアンスの問題でもある。

### 8.2 生成画像のメタデータを残さない

どの画像が AI 生成か、どのツールで、いつ — EU AI 法の透明性義務の下では説明できる必要がある。[A6 §5](../a-operators/a6-compliance.md) を参照。

### 8.3 一括生成して人手の選別をしない

AI の出力歩留まりは思われているより低く、特に手・文字・反射・素材表現で顕著だ。パイプラインには人手の抜き取り確認の工程が要る。比率は低くてよいがゼロにはできない。

### 8.4 プラットフォームごとの画像規格を無視する

メイン画像の白背景、最小寸法、文字の占有率制限 — 規則はプラットフォームごとに違う。制約なしで生成すれば、却下されるか作り直しになる。

---

## 9. 完了チェック

- [ ] ComfyUI を構築するか API 方案を選択
- [ ] 1 つの製品向けに完全な画像セットを生成(メイン画像+シーン画像+インフォグラフィック)
- [ ] 背景除去+白背景合成の自動化フローを実装
- [ ] バッチ生成 Pipeline を構築(一度に 5+ 製品を処理)
- [ ] Amazon 画像コンプライアンスチェックに合格
- [ ] 最低 1 本の製品展示動画を生成

[< B8 EC データダッシュボード](b8-ecommerce-dashboard.md) | [Path 総覧](../README.md)
