---
name: ecom-applicability
description: Determine whether AI is appropriate for a specific e-commerce task. Use when evaluating if a problem has enough data, the right tools, or acceptable risk for AI automation. Answers 'should I use AI for X?' with boundary-aware reasoning.
---

# Applicability Skill

## When to Use

Determine whether AI is appropriate for a specific e-commerce task. Use when evaluating if a problem has enough data, the right tools, or acceptable risk for AI automation. Answers 'should I use AI for X?' with boundary-aware reasoning.

## Method

### 1. Load Domain Constraints

Read `references/constraints.md` for platform-specific rules (character limits, byte constraints, format requirements).

### 2. Review Boundaries

Read `references/boundaries.md` to understand when this skill should NOT be applied.

### 3. Select Prompt Template

Choose the appropriate template from `assets/templates/` or load the full playbook from `references/playbook.md`.

### 4. Apply and Verify

Execute the prompt. Use the `<自检>/<self_check>/<セルフチェック>` block in each prompt to verify output quality before delivering results.

## References

- [Constraints](references/constraints.md) — Platform rules and limits
- [Playbook](references/playbook.md) — Prompt collection
- [Boundaries](references/boundaries.md) — When not to use

## Templates

See `assets/templates/` for copy-ready prompt templates.
