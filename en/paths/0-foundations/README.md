[🇨🇳 中文](../../paths/0-foundations/README.md) | 🇺🇸 English

# Path 0: AI Foundations

> **Recommended prerequisite path** Whether you're an operator, developer, or manager, we suggest completing this path first to build a solid AI foundation
> **Last updated**: 2026-03-11
> **Difficulty**: Beginner
> **Estimated time**: 30 minutes per day, 1 week to complete all modules
> **Prerequisites**: None completely beginner-friendly

---

[Hub Home](../../README.md) · [Learning Paths Overview](../README.md)

## Why You Need Path 0

Paths A/B/C assume you already understand basic AI concepts. If you're unsure about any of the following questions, we recommend completing Path 0 first:

- How do LLMs actually work? Why do they sometimes "hallucinate"?
- How big is the gap between a well-written and a poorly-written prompt? Is there a systematic methodology?
- What is RAG? Why doesn't AI know about my product information? How can I make it aware?
- What's the difference between an Agent and a regular ChatGPT conversation? How far can automation really go?

## Path Navigation

```mermaid
flowchart LR
F1["F1 The Evolution of AI"]
F1 --> F2
F2["F2 Prompt Engineering"]
F2 --> F3
F3["F3 Knowledge Bases & RAG"]
F3 --> F4
F4["F4 Automation & Agents"]
style F1 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
style F2 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
style F3 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
style F4 fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
```

## Module Overview

| Module | Topic | What You'll Understand | Estimated Time |
|--------|-------|----------------------|----------------|
| [F1. The Evolution of AI](f1-ai-evolution.md) | From machine learning to Agents the development timeline | What LLMs fundamentally are and why they can do what they do | 2 hours |
| [F2. Prompt Engineering](f2-prompt-engineering.md) | CRISP framework + advanced techniques + scenario templates | How to systematically write high-quality prompts | 3 hours |
| [F3. Knowledge Bases & RAG](f3-rag-knowledge.md) | Embeddings, vector databases, RAG architecture | How to make AI understand your private data | 2 hours |
| [F4. Automation & Agents](f4-agent-automation.md) | Three layers of automation from scripts to Agents | What AI Agents can do and how to use them | 2 hours |
| [F5. RPA & Low-Code Automation](f5-rpa-automation.md) | Hands-on with n8n/Zapier/Make/Defy | Building automation workflows with specific tools | 2-3 hours |

## Study Recommendations

- **Operators**: Focus on F1 (build understanding) + F2 (prompting is your core skill). For F3/F4, just grasp the concepts.
- **Developers**: Complete all four modules F3/F4 are the theoretical foundation for your Path B journey.
- **Managers**: Focus on F1 (essential for communicating with your team) + F4 (understand the boundaries of automation). Skim through F2/F3.

## Completion Checklist

- [ ] Can explain how LLMs work in your own words (no technical details needed, but understand the essence)
- [ ] Can write structured prompts using the CRISP framework and know how to fix common mistakes
- [ ] Understand the core RAG architecture and know when to use RAG instead of asking AI directly
- [ ] Understand the difference between Agents and regular conversations, and can identify which business scenarios are suitable for Agents

After completing Path 0, we recommend checking out the [ AI Application Landscape Assessment](ai-landscape.md) to build a big-picture view, then choose your next step based on your role:
- Operators → [Path A: AI-Powered Operations](../a-operators/)
- Developers → [Path B: Building AI Systems](../b-developers/)
- Managers → [Path C: AI Strategy Implementation](../c-managers/)

---

[Back to Hub Home](../../README.md) · [Back to Learning Paths Overview](../README.md)
