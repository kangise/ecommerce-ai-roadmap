#!/usr/bin/env python3
"""Generate translation stubs + status table for the i18n trees.

- For every chapter in src/SUMMARY.md, ensure i18n/{en,ja}/src/<path> exists.
  Missing files get a stub: translated title + "translation in progress" note
  linking to the Chinese original on the live site.
- Files WITHOUT the `<!-- i18n-stub -->` marker are real translations and are
  never touched.
- `--status` rewrites i18n/STATUS.md from the current tree state.

Usage:
    python3 scripts/gen_i18n_stubs.py           # create missing stubs
    python3 scripts/gen_i18n_stubs.py --status  # also refresh i18n/STATUS.md
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
SITE = "https://kangise.github.io/ecommerce-ai-skills"
STUB_MARK = "<!-- i18n-stub -->"

# path (relative to src/) -> (English title, Japanese title)
TITLES = {
    "README.md": ("Preface", "はじめに"),
    "0-foundations/ai-landscape.md": ("AI Landscape Assessment", "AI 活用成熟度マップ"),
    "0-foundations/f1-ai-evolution.md": ("The Evolution of AI", "AI 技術の変遷"),
    "0-foundations/f2-prompt-engineering.md": ("Prompt Engineering", "プロンプトエンジニアリング"),
    "0-foundations/f3-rag-knowledge.md": ("RAG & Knowledge Retrieval", "RAG と知識検索"),
    "0-foundations/f4-agent-automation.md": ("Agent Automation", "Agent 自動化"),
    "0-foundations/f5-rpa-automation.md": ("RPA Automation", "RPA 自動化"),
    "0-foundations/f6-ai-tools-comparison.md": ("AI Tool Comparison", "AI ツール比較"),
    "a-operators/a1-product-research.md": ("Product Research & Market Insights", "商品リサーチと市場インサイト"),
    "a-operators/a2-listing-optimization.md": ("Listing Optimization", "商品ページ最適化"),
    "a-operators/a3-advertising.md": ("Advertising Optimization", "広告最適化"),
    "a-operators/a4-customer-service.md": ("Customer Service & After-Sales", "カスタマーサービスとアフターケア"),
    "a-operators/a5-inventory.md": ("Inventory & Supply Chain", "在庫とサプライチェーン"),
    "a-operators/a6-compliance.md": ("Compliance & Risk Management", "コンプライアンスとリスク管理"),
    "a-operators/a7-visual-content.md": ("Visual Content", "ビジュアルコンテンツ"),
    "a-operators/a8-pricing-strategy.md": ("Pricing Strategy", "価格戦略"),
    "a-operators/a9-seo-geo.md": ("SEO / GEO", "SEO / GEO"),
    "a-operators/a10-brand-building.md": ("Brand Building", "ブランド構築"),
    "a-operators/a11-financial-analysis.md": ("Financial Analysis", "財務分析"),
    "a-operators/a12-ip-protection.md": ("IP Protection", "知的財産保護"),
    "a-operators/a13-ai-growth-hack.md": ("AI Growth Hacking", "AI グロースハック"),
    "a-operators/a14-operations-agent.md": ("Agentifying Operations", "運用の Agent 化"),
    "b-developers/b1-data-pipeline.md": ("Data Pipeline", "データパイプライン"),
    "b-developers/b2-prediction-models.md": ("Prediction Models", "予測モデル"),
    "b-developers/b3-rag-knowledge-base.md": ("RAG Knowledge Base", "RAG ナレッジベース"),
    "b-developers/b4-agent-workflow.md": ("Agent Workflow", "Agent ワークフロー"),
    "b-developers/b5-local-model-deploy.md": ("Local Model Deployment", "ローカルモデルのデプロイ"),
    "b-developers/b6-mcp-agentic-workflow.md": ("MCP Integration", "MCP 連携"),
    "b-developers/b7-review-nlp-system.md": ("Review NLP System", "レビュー NLP システム"),
    "b-developers/b8-ecommerce-dashboard.md": ("E-Commerce Dashboard", "EC ダッシュボード"),
    "b-developers/b9-ai-image-pipeline.md": ("AI Image Pipeline", "AI 画像パイプライン"),
    "c-managers/c1-ai-assessment.md": ("AI Capability Assessment", "AI 能力アセスメント"),
    "c-managers/c2-team-building.md": ("Team Building", "チームビルディング"),
    "c-managers/c3-roi-evaluation.md": ("ROI Evaluation", "ROI 評価"),
    "c-managers/c4-ai-risk-governance.md": ("AI Risk Governance", "AI リスクガバナンス"),
    "c-managers/c5-competitive-intelligence.md": ("Competitive Intelligence", "競合インテリジェンス"),
    "d-platforms/d4-walmart-ai-guide.md": ("Walmart", "Walmart"),
    "d-platforms/d5-temu-seller-guide.md": ("Temu", "Temu"),
    "d-platforms/d6-southeast-asia-ai-guide.md": ("Southeast Asia (Shopee + Lazada)", "東南アジア (Shopee + Lazada)"),
    "d-platforms/d7-mercado-libre-ai-guide.md": ("Mercado Libre", "Mercado Libre"),
    "d-platforms/d8-rakuten-japan-ai-guide.md": ("Japan — Rakuten", "日本 — 楽天市場"),
    "d-platforms/d9-ebay-ai-guide.md": ("eBay", "eBay"),
    "d-platforms/d10-aliexpress-ai-guide.md": ("AliExpress", "AliExpress"),
    "d-platforms/d11-coupang-korea-ai-guide.md": ("Korea — Coupang", "韓国 — Coupang"),
    "d-platforms/d12-faire-wholesale-ai-guide.md": ("Faire Wholesale", "Faire 卸売"),
    "d-platforms/d13-europe-marketplaces-guide.md": ("Europe (Otto + Zalando)", "ヨーロッパ (Otto + Zalando)"),
    "d-platforms/shopify-ai-guide.md": ("Shopify", "Shopify"),
    "d-platforms/tiktok-shop-ai-guide.md": ("TikTok Shop", "TikTok Shop"),
    "d-platforms/cross-platform-strategy.md": ("Cross-Platform Synergy", "クロスプラットフォーム連携"),
    "d-platforms/platform-comparison.md": ("Platform Comparison", "プラットフォーム比較"),
    "e-social-media/e1-instagram-facebook-ai-guide.md": ("Instagram / Facebook", "Instagram / Facebook"),
    "e-social-media/e2-youtube-ai-guide.md": ("YouTube", "YouTube"),
    "e-social-media/e3-xiaohongshu-ai-guide.md": ("Xiaohongshu (RED)", "小紅書 (RED)"),
    "e-social-media/e4-pinterest-ai-guide.md": ("Pinterest", "Pinterest"),
    "e-social-media/e5-whatsapp-business-ai-guide.md": ("WhatsApp Business", "WhatsApp Business"),
    "e-social-media/e6-reddit-ai-guide.md": ("Reddit", "Reddit"),
    "e-social-media/e7-social-media-cross-channel.md": ("Cross-Channel Strategy", "クロスチャネル戦略"),
    "case-studies/ai-listing-optimization.md": ("Case Study: AI Listing Optimization", "事例: AI Listing 最適化"),
    "case-studies/ai-ppc-optimization.md": ("Case Study: AI PPC Optimization", "事例: AI 広告最適化"),
    "case-studies/ai-review-to-product.md": ("Case Study: Review-Driven Product Development", "事例: レビュー起点の商品開発"),
    "case-studies/hs-code-classification.md": ("Case Study: HS Code Classification", "事例: HS コード分類"),
    "case-studies/multilingual-recommendation.md": ("Case Study: Multilingual Recommendation", "事例: 多言語レコメンド"),
    "resources/model-matrix.md": ("Model Matrix", "モデルマトリクス"),
    "resources/awesome-ai-skills.md": ("Awesome AI Skills & Rules", "AI Skills・Rules コレクション"),
    "resources/awesome-mcp-agents.md": ("Awesome MCP & Agent Tools", "MCP・Agent ツール集"),
    "resources/skills-library.md": ("Skills Library", "Skills Library"),
    "resources/competitive-analysis.md": ("Competitive Analysis", "競合分析"),
    "resources/technical-guidelines.md": ("Technical Guidelines", "技術ガイドライン"),
}

STUB_TMPL = {
    "en": (
        "# {title}\n\n"
        "> 🚧 **Translation in progress.** This chapter is not yet available in English — "
        "in the meantime, read the [Chinese original]({zh_url}).\n\n"
        + STUB_MARK + "\n"
    ),
    "ja": (
        "# {title}\n\n"
        "> 🚧 **翻訳準備中です。** この章はまだ日本語に翻訳されていません。"
        "それまでは[中国語の原文]({zh_url})をご覧ください。\n\n"
        + STUB_MARK + "\n"
    ),
}


def summary_paths():
    text = open(os.path.join(SRC, "SUMMARY.md"), encoding="utf-8").read()
    return re.findall(r"\]\(([^)]+\.md)\)", text)


def is_stub(path):
    try:
        return STUB_MARK in open(path, encoding="utf-8").read()
    except FileNotFoundError:
        return None  # missing


def main():
    paths = summary_paths()
    created = {"en": 0, "ja": 0}
    for lang in ("en", "ja"):
        for rel in paths:
            if rel not in TITLES:
                print(f"WARN: no title mapping for {rel}; skipping")
                continue
            dst = os.path.join(ROOT, "i18n", lang, "src", rel)
            if os.path.exists(dst):
                continue  # real translation or existing stub: leave alone
            title = TITLES[rel][0 if lang == "en" else 1]
            zh_url = f"{SITE}/{rel[:-3]}.html"
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "w", encoding="utf-8") as f:
                f.write(STUB_TMPL[lang].format(title=title, zh_url=zh_url))
            created[lang] += 1
    print(f"stubs created: en={created['en']} ja={created['ja']}")

    if "--status" in sys.argv:
        lines = [
            "# Translation Status",
            "",
            "zh is the source of truth (`src/`). Regenerate this table with",
            "`python3 scripts/gen_i18n_stubs.py --status`.",
            "",
            "| Chapter | EN | JA |",
            "|---------|----|----|",
        ]
        done = {"en": 0, "ja": 0}
        for rel in paths:
            row = [f"`{rel}`"]
            for lang in ("en", "ja"):
                st = is_stub(os.path.join(ROOT, "i18n", lang, "src", rel))
                mark = "✅" if st is False else "🚧"
                if st is False:
                    done[lang] += 1
                row.append(mark)
            lines.append("| " + " | ".join(row) + " |")
        total = len(paths)
        lines.insert(4, f"\n**EN: {done['en']}/{total} · JA: {done['ja']}/{total}**")
        out = os.path.join(ROOT, "i18n", "STATUS.md")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"status: EN {done['en']}/{total}, JA {done['ja']}/{total} -> i18n/STATUS.md")


if __name__ == "__main__":
    main()
