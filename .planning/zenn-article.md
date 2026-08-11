# 一人会社のための AI E コマース基盤 —— Agent にプラグインするだけで越境 EC ができる

## これは何か

「AI で越境 EC を自動化したい」と言うと、たいてい Chat GPT にプロンプトを投げる話になる。**このリポジトリは違う。** Agent に差し込むだけで、越境 EC の運営に必要な知識・制約・実行能力をまるごと提供する基盤だ。

## 数字で見る

- **69 章**（日本語完訳、全ページ和訳済み）
- **94 の実体** + **78 の関係** + **184 のプラットフォーム制約**
- **292 のプロンプト**（すべて日本語訳付き、自検ブロック + 制約参照付き）
- **9 つのドメイン Skill**（listing、広告、在庫、コンプラ、価格、リサーチ、SNS、AI 適用判断、カスタマーサービス）

すべてのプロンプトには **<セルフチェック> ブロック**がついており、モデルが数字を捏造しないように制約が組み込まれている。

## なぜ日本語なのか

日本の「一人会社」文化は世界でも突出している。個人事業主が Amazon や Shopify で輸出するケースは年々増加。しかし日本語の AI E コマース資料は圧倒的に不足している。本リポジトリは **全 69 章すべて日本語完訳済み**であり、日本の一人会社経営者にそのまま使える。

## Agent に差し込む方法

```bash
git clone https://github.com/kangise/ecommerce-ai-skills.git
cd ecommerce-ai-skills
python3 scripts/build_dist.py
```

`dist/` ディレクトリを Agent に読み込ませるだけ。`dist/SKILL.md` が Agent のシステムプロンプトとして機能し、ルーティングルールに従って 9 つの Skill を自動選択する。

MCP 設定例：

```json
{
  "mcpServers": {
    "opc-ecommerce": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dist"]
    }
  }
}
```

## 他のプロンプト集との違い

ふつうのプロンプト集は「こう言えば AI が答えてくれる」という例文集だ。**この基盤は Agent が自律的に判断し、実行し、自己検証するための完全なシステムである。**

- プロンプトにはすべて出典制約（`source:`）と数値制約（`<!-- ref: constraint_id -->`）がついている
- CI ゲートが常時 24 項目をチェックし、古い数字や矛盾を検出する
- Ontology（94 実体・184 制約）は Agent 間で共有される「契約」として機能する

## まとめ

日本の一人会社経営者へ。あなたの Agent にこの基盤を差し込めば、越境 EC のための知識・制約・実行力が手に入る。**プロンプトを探す時間を、ビジネスに使おう。**

---

GitHub: [kangise/ecommerce-ai-skills](https://github.com/kangise/ecommerce-ai-skills)
