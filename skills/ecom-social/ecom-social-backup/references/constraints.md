<!-- intentionally-empty: no platform-level social media constraints in the ontology; platform best practices live in each chapter's prompt templates (see playbook.md) -->

# Constraints: ecom-social

Generated from `ontology/constraints.yaml`.

No platform-level social media constraints in ontology. This skill relies on platform-specific best practices documented in each chapter's prompt templates.

The playbook carries the operative rules per platform, embedded as `<数据纪律>` / `<文案纪律>` / `<输出格式>` / `<自检>` blocks inside each prompt (e.g. Reels 15-30 秒, 文字叠加每屏 ≤8 词, 小红书封面标题 ≤20 字, YouTube 描述前 150 字符含核心关键词, Reddit 社区规范遵守). Those chapter-derived rules are the constraint set for this skill; the ontology constraint file contains no `social.*` or per-platform numeric entries for these six platforms yet.

Cross-cutting content rules that do apply regardless of platform come from the shared ontology constraint `content.ai_generated.commercial_license`: when AI-generated content is used commercially, prefer tools with explicit commercial licenses and keep prompt + generation records as provenance.
