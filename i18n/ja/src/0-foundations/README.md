# Path 0: AI の基礎から | AI Foundations

> **推奨される先修パス** 運用担当でも技術者でも管理者でも、まずこのパスで AI の基礎認識を作ることを勧める
> **最終更新**: 2026-08-04
> **難易度**: 入門
> **想定時間**: 1 日 30 分、1 週間で全モジュール
> **前提**: なし。ゼロから学べる

---


## なぜ Path 0 が必要か

Path A/B/C は基本概念を理解している前提で書かれている。次の問いに自信がなければ、先に Path 0 を終えてほしい:

- LLM は結局どう動いているのか。なぜときどき「でっちあげる」のか
- Prompt の良し悪しで結果はどれだけ変わるのか。体系的な方法はあるのか
- RAG とは何か。なぜ AI は自社商品を知らないのか。どうすれば知らせられるのか
- Agent と普通の ChatGPT の会話は何が違うのか。自動化はどこまでできるのか

## パスナビゲーション

```mermaid
flowchart LR
F1["F1 AI のこれまで"]
F1 --> F2
F2["F2 Prompt エンジニアリング"]
F2 --> F3
F3["F3 ナレッジベースと RAG"]
F3 --> F4
F4["F4 自動化と Agent"]
F4 --> F5
F5["F5 RPA とローコード"]
style F1 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
style F2 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
style F3 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
style F4 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
style F5 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
```

## モジュール概要

| モジュール | テーマ | 理解できること | 想定時間 |
|-----------|--------|---------------|----------|
| [F1. AI のこれまで](f1-ai-evolution.md) | 機械学習から Agent までの流れ | LLM の本質は何か、なぜこれができるのか | 2 時間 |
| [F2. Prompt エンジニアリング](f2-prompt-engineering.md) | CRISP フレームワーク + 上級テクニック + 本書の 6 ブロック記法と規律ブロック | 高品質な Prompt を体系的に書く方法、そしてモデルにデータをでっちあげさせない方法 | 3 時間 |
| [F3. ナレッジベースと RAG](f3-rag-knowledge.md) | Embedding、ベクトル DB、RAG アーキテクチャ | 自社データを AI に理解させる方法 | 2 時間 |
| [F4. 自動化と Agent](f4-agent-automation.md) | スクリプトから Agent までの 3 層 | AI Agent に何ができるか、どう使うか | 2 時間 |
| [F5. RPA とローコード自動化](f5-rpa-automation.md) | n8n / Zapier / Make / Defy 実践 | 具体的なツールで自動化ワークフローを組む | 2〜3 時間 |
| [F6. AI ツール比較](f6-ai-tools-comparison.md) | ChatGPT / Claude / Gemini などの横断比較 | 各ツールの得意分野と選び方 | 1 時間(逐次参照) |

## 学習の進め方

- **運用担当**: F1(認識づくり)と F2(Prompt が中核スキル)を重点的に。F3/F4 は概念の把握で十分
- **技術者**: 5 モジュールすべて。F3/F4 は Path B の理論的土台
- **管理者**: F1(チームと話す土台)と F4(自動化の限界の理解)を重点的に。F2/F3 はざっと通す

## 完了の目安

- [ ] LLM の仕組みを自分の言葉で説明できる(技術的詳細は不要、本質を外さなければよい)
- [ ] CRISP フレームワークで構造化した Prompt を書け、よくある失敗を直せる
- [ ] Prompt にデータ規律ブロックを足すべき場面と、それが防ぐ誤りの種類がわかる
- [ ] RAG の基本構成を理解し、直接聞くのではなく RAG を使うべき場面がわかる
- [ ] Agent と通常の会話の違いを理解し、どの業務が Agent 向きか判断できる

Path 0 の後は [AI 活用の全体像](ai-landscape.md) で俯瞰してから、役割に応じて次へ:
- 運用担当 → [Path A: AI で運用を効率化](../a-operators/)
- 技術者 → [Path B: AI システム構築](../b-developers/)
- 管理者 → [Path C: AI 戦略の実行](../c-managers/)

---

[Hub トップへ](../README.md) · [学習パス一覧へ](../README.md)
