# Path 0: AI Foundations First | AI Foundations

> **Recommended prerequisite path** Whether you are an operator, an engineer, or a manager, finish this path first to build a working mental model of AI
> **Last updated**: 2026-08-04
> **Difficulty**: Beginner
> **Estimated time**: 30 minutes a day, all modules done in a week
> **Prerequisites**: None — no prior background needed

---


## Why Path 0 exists

Paths A/B/C assume you already understand the basic concepts. If any of these questions still feel fuzzy, start here:

- How does an LLM actually work? Why does it sometimes make things up?
- How much difference does a well-written prompt make versus a bad one? Is there a method, or is it guesswork?
- What is RAG? Why doesn't the AI know anything about my products, and how do I fix that?
- How is an Agent different from a normal ChatGPT conversation? How far does automation actually go?

## Path navigation

```mermaid
flowchart LR
F1["F1 How AI Got Here"]
F1 --> F2
F2["F2 Prompt Engineering"]
F2 --> F3
F3["F3 Knowledge Bases & RAG"]
F3 --> F4
F4["F4 Automation & Agents"]
F4 --> F5
F5["F5 RPA & Low-Code"]
style F1 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
style F2 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
style F3 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
style F4 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
style F5 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
```

## Module overview

| Module | Topic | What you will understand | Time |
|--------|-------|--------------------------|------|
| [F1. How AI Got Here](f1-ai-evolution.md) | From machine learning to agents | What an LLM really is, and why it can do these things | 2 hours |
| [F2. Prompt Engineering](f2-prompt-engineering.md) | CRISP framework + advanced techniques + this library's six-block form and discipline blocks | How to write high-quality prompts systematically, and how to stop the model from inventing data | 3 hours |
| [F3. Knowledge Bases & RAG](f3-rag-knowledge.md) | Embeddings, vector databases, RAG architecture | How to make AI understand your private data | 2 hours |
| [F4. Automation & Agents](f4-agent-automation.md) | The three layers from script to agent | What an AI agent can do, and how to use one | 2 hours |
| [F5. RPA & Low-Code Automation](f5-rpa-automation.md) | n8n / Zapier / Make / Defy in practice | Building automation workflows with concrete tools | 2–3 hours |
| [F6. AI Tool Comparison](f6-ai-tools-comparison.md) | ChatGPT / Claude / Gemini and others, side by side | What each tool is actually good at, and which to reach for | 1 hour (reference) |

## How to study this

- **Operators**: focus on F1 (mental model) + F2 (prompting is your core skill); skim F3/F4 for concepts
- **Engineers**: do all five modules — F3/F4 are the theory behind Path B
- **Managers**: focus on F1 (the basis for talking to your team) + F4 (understanding where automation stops); skim F2/F3

## Done when

- [ ] You can explain in your own words how an LLM works — no technical detail required, but the essence has to be right
- [ ] You can write a structured prompt with the CRISP framework and fix the common mistakes
- [ ] You know when to add a data-discipline block to a prompt, and which class of error it catches
- [ ] You understand the RAG architecture and when to reach for RAG instead of just asking the AI
- [ ] You understand how an agent differs from a plain conversation, and can judge which business cases suit one

After Path 0, read [AI Application Landscape](ai-landscape.md) for the wide view, then pick your next step by role:
- Operators → [Path A: AI in Daily Operations](../a-operators/)
- Engineers → [Path B: Building AI Systems](../b-developers/)
- Managers → [Path C: AI Strategy in Practice](../c-managers/)

---

[Back to Hub](../README.md) · [Back to Learning Paths](../README.md)
