# Awesome AI Skills & Rules | AI IDE のスキルファイルとルール集

> AI IDE(Kiro/Cursor/Windsurf/Claude Code)の Skills、Steering Files、Rules のコレクション。
> AI にあなたの規約どおりに働かせる。毎回同じ説明を繰り返す必要はもうありません。
> 最終更新: 2026-03-15


---

## 目次

- [AI Skills / Rules とは](#ai-skills--rules-とは)
- [外部の Awesome Lists とリソース](#外部の-awesome-lists-とリソース)
- [Kiro Skills & Steering Files](#kiro-skills--steering-files)
- [Cursor Rules](#cursor-rules)
- [Claude Code SKILL.md](#claude-code-skillmd)
- [EC 開発におすすめの Skills](#ec-開発におすすめの-skills)

---

## AI Skills / Rules とは

AI Skills(スキルファイル)は AI アシスタントへの永続的な指示です。一度書けば AI が自動で従い、チャットのたびに繰り返す必要がありません。

| プラットフォーム | ファイル名 | 置き場所 | 説明 |
|------------------|-----------|----------|------|
| Kiro | `*.md` | `.kiro/skills/` または `.kiro/steering/` | Steering files がプロジェクト規約を永続化 |
| Cursor | `.cursorrules` または `.mdc` | プロジェクトルート | AI コード生成のカスタムルール |
| Claude Code | `SKILL.md` | プロジェクトルート | 再利用可能な AI コーディング指示 |
| Windsurf | `.windsurfrules` | プロジェクトルート | Cursor Rules に類似 |

---

## 外部の Awesome Lists とリソース

### Cursor Rules コレクション

| 名前 | Stars | 説明 | リンク |
|------|-------|------|--------|
| awesome-cursorrules (PatrickJS) | 23.6K | 最大の Cursor Rules 集、言語/フレームワーク別 | [GitHub](https://github.com/PatrickJS/awesome-cursorrules) |
| awesome-cursor-rules (blefnk) | 人気 | フロントエンド最適化(Next.js/React/TypeScript/Tailwind) | [GitHub](https://github.com/blefnk/awesome-cursor-rules) |
| awesome-cursor-rules-mdc (sanjeed5) | 精選 | .mdc 形式の Cursor Rules 集 | [GitHub](https://github.com/sanjeed5/awesome-cursor-rules-mdc) |
| Cursor-Rules (UltraInstinct0x) | 実用 | 実行可能なコード生成に特化したルール | [GitHub](https://github.com/UltraInstinct0x/Cursor-Rules) |

### ディレクトリサイト

| サイト | 説明 | リンク |
|--------|------|--------|
| ExtMC | 検索可能な Cursor Rules ディレクトリ、フレームワーク/技術スタックで絞り込み | [extmc.com](https://extmc.com/) |
| PromptGenius | IDE 横断の AI Rules ガイド(Cursor/Windsurf/Copilot) | [promptgenius.net](https://promptgenius.net/cursorrules) |
| GitHub Topics: cursorrules | GitHub 上のすべての cursorrules 関連プロジェクト | [GitHub Topics](https://github.com/topics/cursorrules) |

### 深掘りガイド

| 記事 | ソース | 説明 |
|------|--------|------|
| How To Write Rules for AI Coding Tools | VirtusLab | AI ルール作成のベストプラクティス |
| How to Develop SKILL.md for AI Coding Agents | MTechZilla | SKILL.md の本番運用ガイド |
| How to Guide AI With Rules and Tests | freeCodeCamp | ルールとテストで AI を導く |
| Beyond the Vibes: A Rigorous Guide | tedivm | AI コーディングアシスタントの厳密な使い方 |

Sources: [VirtusLab](https://virtuslab.com/blog/ai/how-to-write-rules-for-ai/), [MTechZilla](https://www.mtechzilla.com/guides/how-to-develop-skill-md-production-guide-engineering-teams), [freeCodeCamp](https://www.freecodecamp.org/news/how-to-guide-ai-with-rules-and-tests/), [tedivm](https://blog.tedivm.com/guides/2026/03/beyond-the-vibes-coding-assistants-and-agents/).

Content rephrased for compliance with licensing restrictions.

---

## Kiro Skills & Steering Files

Kiro は Steering Files で永続的なプロジェクト知識を提供します([Kiro Docs](https://aws.amazon.com/documentation-overview/kiro/))。

| 種類 | 置き場所 | トリガー | 用途 |
|------|----------|----------|------|
| Always-on | `.kiro/steering/*.md` | 会話のたびに自動ロード | プロジェクト規約、コーディング標準 |
| File-match | `.kiro/steering/*.md` + frontmatter | 一致するファイルを読むときにロード | 特定ファイルタイプのルール |
| Manual | `.kiro/steering/*.md` + `inclusion: manual` | `#` で手動参照 | 必要時に読むリファレンス |
| Skills | `.kiro/skills/*.md` | オンデマンドで有効化 | 再利用可能なタスク指示 |

### EC プロジェクトの Steering 例

本プロジェクト(CBEC-AI-Hub)で使っている Steering Files:

| ファイル | 用途 |
|----------|------|
| `product.md` | プロジェクト背景(Amazon アカウント運用、越境EC) |
| `structure.md` | プロジェクト構造(ファイル構成、命名規約) |
| `tech.md` | 技術スタック(Python/TypeScript/Chart.js) |

---

## Cursor Rules

Cursor Rules は AI コード生成のカスタムルールを定義します([PatrickJS](https://github.com/PatrickJS/awesome-cursorrules))。

### EC 開発におすすめの Rules

| Rule | 向き | ソース |
|------|------|--------|
| Python Projects Guide | Python の EC スクリプト開発 | [PatrickJS](https://github.com/PatrickJS/awesome-cursorrules/blob/main/rules/python-projects-guide-cursorrules-prompt-file/.cursorrules) |
| Python Flask JSON | Flask API 開発 | [PatrickJS](https://github.com/PatrickJS/awesome-cursorrules/blob/main/rules/python-flask-json-guide-cursorrules-prompt-file/.cursorrules) |
| React TypeScript shadcn/ui | Shopify フロントエンド / ダッシュボード | [PatrickJS](https://github.com/PatrickJS/awesome-cursorrules/blob/main/rules/cursor-ai-react-typescript-shadcn-ui-cursorrules-p/.cursorrules) |
| Security Rules | AI セキュアコーディング | [GitHub Topics](https://github.com/topics/cursorrules) |

---

## Claude Code SKILL.md

SKILL.md は Claude Code、Roo Code、OpenAI Codex、Cursor などの AI コーディング Agent 向けの構造化指示ファイルです。一度書けば Agent が自動で読み込み適用します([MTechZilla](https://www.mtechzilla.com/guides/how-to-develop-skill-md-production-guide-engineering-teams))。

Content rephrased for compliance with licensing restrictions.

### SKILL.md の構造

```markdown
# Skill Name

## Context
プロジェクト背景と技術スタック

## Instructions
具体的なコーディングルールと制約

## Examples
良いコード例 vs 悪いコード例

## Constraints
必ず守るべき制限(セキュリティ/性能/スタイル)
```

---

## EC 開発におすすめの Skills

### ロール別のおすすめ

| ロール | おすすめツール | おすすめ Skills/Rules |
|--------|---------------|----------------------|
| Python 開発 | Kiro + Claude Code | Steering Files(tech.md)+ SKILL.md(Python 規約) |
| フロントエンド開発 | Cursor | React/TypeScript Rules + Shopify Liquid Rules |
| フルスタック | Kiro | Steering + MCP 設定 + Skills |

### クイックスタート

```bash
# Kiro: Steering Files を作成
mkdir -p .kiro/steering
echo "# プロジェクト規約\nあなたのコーディングルール..." > .kiro/steering/rules.md

# Cursor: Rules を作成
echo "あなたは Python の EC 開発専門家です..." > .cursorrules

<コピー規律>
- 商品が実際には持たない機能・素材・認証・効果を書かないこと。上で私が挙げていない属性は本文に出さない — Listing の削除と虚偽広告の申立ての最大の原因がこれだ
- 良い文面のためにある訴求点が必要で、それを私が渡していない場合は、何を補ってほしいかを列挙し、勝手に補わないこと
- 効能・安全・環境・特許に関わる表現は別途印を付け、私が人手で確認できるようにすること
</コピー規律>
```

---
