# F2. Prompt Engineering

> **Track**: Path 0: AI Foundations · **Module**: F2
> **Last updated**: 2026-03-12
> **Level**: Beginner → Intermediate
> **Time**: 3 hours
> **Prerequisite**: [F1 The Evolution of AI](f1-ai-evolution.md)

---


```mermaid
flowchart LR
F1["F1 The Evolution of AI"]
F1 --> F2
F2[" F2 Prompt Engineering<br/>(you are here)"]:::current
F2 --> F3
F3["F3 Knowledge & RAG"]
F3 --> F4
F4["F4 Automation & Agents"]
classDef current fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
```

---

## Chapter Navigation

1. [Why prompts matter](#1-why-prompts-matter) · 2. [The CRISP framework](#2-the-crisp-framework-a-method-for-structured-prompts) · 3. [Six advanced techniques](#3-six-advanced-prompt-techniques) · 4. [Template library](#4-cross-border-e-commerce-prompt-template-library-20) · 5. [Common mistakes & fixes](#5-common-mistakes--fixes) · 6. [Advanced: context engineering](#6-advanced-from-prompt-engineering-to-context-engineering) · 7. [Learning resources](#7-learning-resources)


## What You'll Master

The prompt is your only interface to the AI. With the same model, a well-written prompt and a poorly written one can differ 10× in output quality.

After this module you'll be able to:
- Write structured, high-quality prompts with the CRISP framework
- Use 6 advanced techniques (Chain-of-Thought, few-shot, and more)
- Draw on 20+ ready-to-use prompt templates for cross-border e-commerce
- Recognize and fix common prompt mistakes
- Understand the shift from prompt engineering to context engineering

> **Core idea**: prompt engineering isn't "writing one good instruction" — it's "designing a complete communication protocol." You're giving the AI not just a question, but a full definition of role, background, constraints, format, and expectations.

---

## 1. Why Prompts Matter

### 1.1 Same question, different prompts

**Scenario: analyzing competitor reviews**

**Bad prompt:**
```
Analyze these reviews for me
```

**AI output:** a vague summary — no structure, no actionable advice.

**Good prompt:**
```
You are a senior Amazon product manager specializing in consumer electronics.
I'll give you a set of 1–3 star reviews for competitor Bluetooth earbuds (50 total).

Analyze them and output:
1. The top 5 user pain points (ranked by mention frequency)
2. 1–2 representative review quotes per pain point
3. An improvement suggestion per pain point
4. Which pain points are easiest to solve through product design

Output format: table
Language: English

[Paste the reviews here]
```

**AI output:** a structured table — pain points ranked by frequency, each with quotes and actionable improvements.

**Where's the difference?**

| Dimension | Bad prompt | Good prompt |
|-----------|-----------|-------------|
| Role | none | "senior Amazon product manager" |
| Background | none | "consumer electronics," "Bluetooth earbuds," "1–3 star reviews" |
| Concrete asks | "analyze" | 4 explicit output requirements |
| Output format | none | "table" |
| Language | none | "English" |

### 1.2 The essence of a prompt: shrinking the AI's "guess space"

Recall F1: an LLM is a next-word predictor. When your prompt is vague, the AI has too many possible directions and picks the "most common" one — usually generic filler.

When your prompt is precise, you shrink its guess space down to the direction you want.

```
Vague prompt → huge output space → most likely a mediocre result
Precise prompt → small output space → most likely the result you wanted
```

It's exactly like assigning work to a new hire:
- "Make me a report" → they don't know what report, for whom, in what format, due when
- "Make a Q1 sales analysis for the boss, as slides, with YoY growth and the top 10 products, by Friday" → they know what to do

### 1.3 The ROI of prompt engineering

| Investment | Return |
|-----------|--------|
| 2 extra minutes writing the prompt | 20 minutes saved editing the output |
| Building a prompt template library (one-time 2 h) | 30 minutes/day saved per teammate |
| Learning the CRISP framework (this module, 3 h) | 50%+ quality lift on every AI interaction |

---

## 2. The CRISP Framework: a Method for Structured Prompts

### 2.1 What is CRISP

CRISP is a framework for writing high-quality prompts — five letters, five elements:

```
C Context: give the AI enough background
R Role: define what role the AI should play
I Instructions: state exactly what to do
S Specifications: define output format, length, language, ...
P Proof: ask the AI for evidence or its reasoning
```

### 2.2 Each element in detail

**C — Context**

Tell the AI "the situation in which you're asking." The richer the background, the more precise the answer.

| No context | With context |
|-----------|--------------|
| "Write me a product title" | "I sell a portable neck fan on Amazon US, target customers are outdoor-sports enthusiasts, price $25, main competitors are JISULIFE and TORRAS" |

**Context checklist (cross-border e-commerce):**
- What's the product? Category, traits, selling points
- Target market? US/EU/JP
- Target customer? Age, scenario, needs
- Who are the competitors? Price band, strengths/weaknesses
- Your constraints? Budget, time, resources

**R — Role**

Give the AI a professional role and it will answer with that role's knowledge and lens.

| Scenario | Suggested role |
|----------|----------------|
| Writing listings | "You are an Amazon listing optimization expert with 5 years' experience" |
| Review analysis | "You are a senior product manager focused on consumer electronics" |
| Ad optimization | "You are an Amazon PPC expert" |
| Compliance questions | "You are a cross-border compliance consultant fluent in EU/US/JP regulation" |
| Supplier negotiation | "You are a procurement manager with 10 years' experience" |
| Market analysis | "You are an e-commerce industry analyst" |

> **Why do roles work?** Because the training data contains text from different roles. Specify "Amazon PPC expert" and the AI leans toward PPC terminology and analytical frames.

**I — Instructions**

State exactly what to do. Good instructions are specific, executable, and prioritized.

| Vague | Specific |
|-------|----------|
| "Analyze this data" | "From these search terms, find terms with ACOS > 50% and clicks > 100, sorted by spend descending" |
| "Write a title" | "Write 3 Amazon title variants, each ≤ 200 characters, containing keywords [X], [Y], [Z]" |
| "Give me advice" | "Give 3 concrete improvements, each with: problem, fix, expected impact" |

**S — Specifications**

Define what the output should look like.

| Spec type | Examples |
|-----------|----------|
| Format | "output as a table," "use Markdown," "numbered list" |
| Length | "each point ≤ 50 words," "500–800 words total" |
| Language | "answer in Chinese," "listing in English, analysis in Chinese" |
| Tone | "professional but accessible," "readable by Amazon shoppers" |
| Structure | "conclusion first, then analysis," "highest priority first" |

**P — Proof**

Ask the AI to explain its reasoning or cite evidence — it reduces hallucination.

```
Example proof requirements:
- "Explain your reasoning"
- "Annotate the basis for each suggestion"
- "If you're unsure about something, say so explicitly"
- "Separate 'data-based conclusions' from 'experience-based conjecture'"
```

### 2.3 A complete CRISP example

**Scenario: deciding whether to enter a new category**

```
[C - Context]
I'm an Amazon US seller focused on consumer electronics,
annual revenue ~$500K, team of 5.
I'm considering entering the portable projector category.
Current leaders on Amazon US: XGIMI, Anker Nebula, YABER.
My startup budget is about ¥300K.

[R - Role]
You are a cross-border product-sourcing consultant with 10 years'
experience, deeply familiar with consumer electronics on Amazon US.

[I - Instructions]
Run a full market feasibility assessment for portable projectors:
1. Market size and growth trend
2. Competitive landscape (leaders' strengths and weaknesses)
3. Profit-margin estimate
4. Entry barriers (capital, technology, certification)
5. Key risks
6. Go/No-Go recommendation

[S - Specifications]
- Format: a table per dimension + brief analysis
- Language: Chinese
- Scoring: 1–5 per dimension
- End with an overall score and an explicit recommendation (enter / caution / pass)

[P - Proof]
- Mark which points come from public data and which are conjecture
- If a dimension is uncertain, say so
- Explain how the overall score is computed
```

> **You don't label [C][R][I][S][P] in real use** — that's just for teaching. Once fluent, you'll fold the five elements in naturally.


---

## 3. Six Advanced Prompt Techniques

### 3.1 Chain-of-Thought

Make the AI "think step by step" instead of jumping to an answer. Best for problems requiring reasoning.

**Without CoT:**
```
What's this product's margin on Amazon US?
Sourcing cost ¥80, price $29.99, FBA fee $5.50, referral fee 15%
```
The AI may spit out a number with an opaque, error-prone calculation.

**With CoT:**
```
Calculate this product's Amazon US margin step by step:
1. Convert the sourcing cost from CNY to USD (rate 7.2)
2. Compute the Amazon referral fee
3. Sum all costs
4. Compute profit and margin

Data: sourcing cost ¥80, price $29.99, FBA fee $5.50, referral 15%
```

**Why it works:** forcing intermediate steps makes every step checkable. If one step is wrong, you see it immediately.

**Where to use it:**
- Profit and cost analysis
- Multi-step market assessments
- Decisions requiring logic
- Any analysis where you need to "see the work"

### 3.2 Few-shot learning

Give the AI a few examples so it learns your desired format and style.

```
Analyze each competitor's title strategy in this format:

Example:
Title: Anker Soundcore Life Q20 Hybrid Active Noise Cancelling Headphones
Analysis:
- Brand first (Anker Soundcore) → high brand recognition, so lead with it
- Core selling point (Hybrid Active Noise Cancelling) → technical differentiation
- Category word (Headphones) → guarantees search match
- Strategy: brand + technical selling point + category word

Now analyze these 3 titles the same way:
1. [Competitor A title]
2. [Competitor B title]
3. [Competitor C title]
```

**Why it works:** an example is more precise than a description. Rather than 100 words describing the format you want, show one.

**Best practices:**
- 1–3 examples are usually enough
- Cover different cases (positive/negative, simple/complex)
- The examples' format *is* your expected output format

### 3.3 Role-playing

Have the AI adopt specific personas and analyze from their viewpoints.

```
Evaluate this product from each of these 3 perspectives:

Persona 1 — the picky consumer:
"I shop on Amazon often, demand high quality, and read the negative
reviews carefully. Does this listing convince me to buy?"

Persona 2 — the competitor's ops manager:
"I run operations at a competitor and see this new product entering.
Is it a threat? How should I respond?"

Persona 3 — the Amazon category manager:
"I'm the Amazon category manager reviewing products in this category.
Does this listing carry any compliance risk? How's its quality score?"
```

**Why it works:** multi-persona analysis surfaces problems a single lens misses.

### 3.4 Structured output

Require a specific output structure — easier to process and compare downstream.

```
Output the analysis in this JSON format:

{
"product_name": "...",
"market_score": 1-5,
"competition_score": 1-5,
"profit_score": 1-5,
"risk_factors": ["risk 1", "risk 2"],
"recommendation": "enter/caution/pass",
"reasoning": "why"
}
```

**Where to use it:**
- Batch-evaluating many products
- Data destined for Excel or a database
- Standardizing analysis format across a team

### 3.5 Iterative refinement

Don't expect perfection from one prompt. Treat the AI as a collaborator and refine over multiple turns.

```
Round 1:
"Write an Amazon title for Bluetooth earbuds"

Round 2:
"Good, but add the keyword 'noise cancelling' and keep it under 150 characters"

Round 3:
"Great. Now give me 3 variants emphasizing:
A. Technical specs (noise reduction dB, battery life)
B. Usage scenarios (commuting, sports, office)
C. Emotional appeal (enjoy music, focus at work)"

Round 4:
"I'll take direction B. Refine it further and add '2026 new model' and 'Type-C fast charging'"
```

**Why it works:** complex tasks are hard to specify in one shot. Iteration lets you steer after seeing output.

### 3.6 Constraint setting

Telling the AI what *not* to do matters as much as what to do.

```
Write 5 bullet points for an Amazon listing.

Constraints:
- No hype words ("best," "perfect," "revolutionary")
- No competitor brand names
- No HTML tags
- Each bullet ≤ 200 characters
- No repeated keywords
- No all-caps (except the brand name)
```

**Common constraints (cross-border e-commerce):**

| Constraint type | Examples |
|-----------------|----------|
| Content | "don't fabricate data," "no unverified claims" |
| Format | "under X words," "table, not paragraphs" |
| Compliance | "no medical claims," "no competitor brands" |
| Style | "no academic tone," "no Chinglish" |
| Safety | "if unsure, say so instead of guessing" |

---

## 4. Cross-Border E-Commerce Prompt Template Library (20+)

> **Related**: [A2 Listing Optimization](../a-operators/a2-listing-optimization.md) for listing prompt templates in depth


### 4.1 Product research & market analysis (5)

**Template 1: competitor review pain-point extraction**
```
Role: senior Amazon product manager
Input: [paste 50+ one-to-three-star reviews]
Task: extract the top 5 pain points, ranked by frequency
Output: table (pain point | frequency | representative quote | improvement | difficulty)
```

**Template 2: 5-dimension market feasibility**
```
Role: cross-border sourcing consultant
Input: product name, target market, competitor info
Task: score demand/competition/profit/supply chain/compliance (1–5 each)
Output: score table + overall recommendation (enter/caution/pass)
```

**Template 3: keyword demand clustering**
```
Role: Amazon SEO expert
Input: [paste 100+ keywords]
Task: cluster by purchase intent, spot underserved demand
Output: cluster table (cluster | keywords | volume | competition | product opportunity)
```

**Template 4: trend judgment**
```
Role: e-commerce trend analyst
Input: category name + Google Trends data + BSR data
Task: judge whether the category is rising / plateaued / declining
Output: judgment + evidence + entry-timing advice
```

**Template 5: supplier comparison**
```
Role: procurement manager
Input: 3 suppliers' quotes, MOQs, lead times, credentials
Task: multi-dimension comparison
Output: comparison table + ranked recommendation + negotiation strategy
```

### 4.2 Listings & content (5)

**Template 6: full listing generation**
```
Role: Amazon listing optimization expert
Input: product info, selling points, keyword list
Task: generate title + 5 bullets + description + Search Terms
Constraints: title ≤ 200 characters, keywords woven in naturally
```

**Template 7: multilingual localization**
```
Role: [target language] localization expert
Input: English listing
Task: translate + localize (swap keywords, reorder selling points)
Output: localized listing + notes on every adaptation
```

**Template 8: A+ content planning**
```
Role: Amazon A+ Content designer
Input: product info, brand story, competitor A+ screenshots
Task: plan A+ module layout and copy
Output: module order + title/copy/image suggestion per module
```

**Template 9: competitor listing breakdown**
```
Role: competitive analyst
Input: 3 competitors' complete listings
Task: contrast strategies, find differentiation openings
Output: strategy comparison + keyword coverage comparison + differentiation advice
```

**Template 10: selling-point distillation**
```
Role: brand marketing expert
Input: product specs, positive reviews, competitor weaknesses
Task: distill 3 core selling points + a one-line USP
Output: selling points + supporting evidence + usage scenarios
```

### 4.3 Advertising & marketing (4)

> **Related**: [A3 Advertising Optimization](../a-operators/a3-advertising.md) for ad-analysis templates in depth

**Template 11: search term report analysis**
```
Role: Amazon PPC expert
Input: search term report (past 30 days)
Task: find high-converting terms, waste terms, negative suggestions
Output: top 10 converters + top 10 waste + negatives list + budget advice
```

**Template 12: ad copy A/B variants**
```
Role: ad copywriter
Input: product description, core selling point
Task: generate headlines in 5 styles (feature/scenario/emotion/data/problem-solving)
Output: 5 headlines + expected impact + audience fit
```

**Template 13: promotion planning**
```
Role: e-commerce promotion strategist
Input: product info, sales history, promo budget
Task: build a BFCM/Prime Day promotion plan
Output: promo calendar + discount strategy + ad support plan + expected ROI
```

**Template 14: brand story writing**
```
Role: brand storyteller
Input: brand background, founding story, core values
Task: write the Amazon Brand Story content
Output: brand story copy (200–300 words) + image suggestions
```

### 4.4 Customer service & after-sales (3)

**Template 15: bulk negative-review analysis**
```
Role: product quality analyst
Input: last 60 days of 1–3 star reviews
Task: classify by type, compute frequencies, propose fixes
Output: classification table + frequency share + short-term response + long-term fix + priority
```

**Template 16: reply template generation**
```
Role: Amazon customer-service expert
Input: common question types
Task: generate multilingual reply templates
Output: 3 variants per question (formal/friendly/brief) × languages
```

**Template 17: appeal letter (Plan of Action)**
```
Role: Amazon account appeal expert
Input: the violation notice
Task: write the Plan of Action
Output: Root Cause + Immediate Actions + Preventive Measures
```

### 4.5 Operations management (4)

**Template 18: restock decision analysis**
```
Role: inventory management expert
Input: 90 days of sales, current stock, supplier lead time
Task: compute safety stock and restock advice
Output: safety stock + reorder timing + order quantity + risk notes
```

**Template 19: competitor monitoring weekly**
```
Role: competitive intelligence analyst
Input: competitors' price/review/BSR changes
Task: analyze their strategic moves and how to respond
Output: change summary + strategy analysis + response advice
```

**Template 20: daily/weekly ops report**
```
Role: operations data analyst
Input: the day's/week's sales, ads, inventory data
Task: generate a structured ops report
Output: KPI summary + anomaly flags + action suggestions
```

**Template 21: multi-market compliance comparison**
```
Role: cross-border compliance consultant
Input: product type, target market list
Task: generate a compliance-requirement comparison per market
Output: comparison table + certification cost estimate + common pitfalls
```


---

## 5. Common Mistakes & Fixes

### 5.1 The ten prompt mistakes

| # | Mistake | Example | Fix | Fixed version |
|---|---------|---------|-----|---------------|
| 1 | **Too vague** | "Analyze the market" | add product, market, dimensions | "Analyze the competitive landscape for Bluetooth earbuds on Amazon US" |
| 2 | **No role** | "Write a title" | add a role | "You are an Amazon listing expert; write a title" |
| 3 | **No format spec** | "Give me advice" | specify format | "Give 5 suggestions as a numbered list, ≤50 words each" |
| 4 | **Too much at once** | "Analyze the market, write the listing, plan the ads" | split into prompts | analyze first, then write the listing from the analysis |
| 5 | **Analysis without data** | "What's this category's monthly volume?" | provide data to analyze | "Here's the Helium 10 export — analyze..." |
| 6 | **Expecting live info** | "What's the BSR right now?" | acknowledge the limits | "Assume BSR is 50–100; analyze..." |
| 7 | **No constraints** | "Write a product description" | add length/style/taboo constraints | "≤200 words, no hype, emphasize practicality" |
| 8 | **Sloppy language mixing** | Chinese prompt wanting English output | state language explicitly | "Listing in English; analysis in Chinese" |
| 9 | **Not iterating** | give up after one bad output | give feedback | "Title's too long — cut to under 150 characters" |
| 10 | **Not saving good prompts** | rewrite from scratch each time | build a template library | store proven prompts in a shared team doc |

### 5.2 A repair walkthrough: from bad to good

**Original prompt (bad):**
```
Take a look at this product for me
```

**Diagnosis:**
- No role
- No context (which product? which market?)
- "Take a look" is vague (evaluate on which dimensions?)
- No output format
- No proof requirement

**First improvement:**
```
You are a cross-border sourcing consultant.
Assess the market outlook for a "portable neck fan" on Amazon US.
Analyze demand, competition, and profit.
```

**Second improvement (full CRISP):**
```
[Role] You are a sourcing consultant with 10 years' experience,
deeply familiar with consumer electronics on Amazon US.

[Context] I'm an Amazon seller doing $200K/year with a team of 3
and a launch budget of ¥150K. I'm considering the portable neck-fan
category. Current leaders: JISULIFE (BSR #1, 4.3 stars, 12,000+
reviews) and TORRAS (BSR #3, 4.4 stars, 8,000+ reviews).

[Task] Run a full market feasibility assessment:
1. Demand (search trends, seasonality, growth potential)
2. Competition (leaders' moats, difficulty for new entrants)
3. Profit (estimate cost structure and margin)
4. Risk (seasonality, patents, compliance)
5. Overall recommendation (Go/No-Go + entry strategy if Go)

[Format] Table per dimension + 1–5 score + brief analysis.
End with an overall score and an explicit recommendation.

[Proof] Mark what's based on public information vs. your conjecture.
If a dimension is uncertain, say so.
```

### 5.3 Prompt differences across models

| Model | Prompt preference | Notes |
|-------|-------------------|-------|
| ChatGPT (GPT-4o) | accepts any format; responds well to natural language | long prompts work well; give plenty of context |
| Claude (Sonnet/Opus) | prefers structure; XML tags work great | organize with `<context>` `<instructions>` etc. |
| Gemini | responds well to concise prompts | the huge context window is the edge — load in lots of reference material |
| DeepSeek | strong with Chinese prompts | great value for high-volume calls |

**Claude-specific technique — XML tags:**
```
<context>
I'm an Amazon US seller focused on consumer electronics.
</context>

<task>
Analyze the pain points in the competitor reviews below.
</task>

<format>
Table with: pain point, frequency, representative quote, improvement.
</format>

<reviews>
[Paste the reviews here]
</reviews>
```

---

## 6. Advanced: From Prompt Engineering to Context Engineering

> **Related**: [D6 Southeast Asia AI Guide](../d-platforms/d6-southeast-asia-ai-guide.md) for multilingual prompt applications

### 6.1 The 2026 shift: context engineering

In mid-2025, Andrej Karpathy (formerly OpenAI) framed it memorably: the LLM is like a CPU, the context window is like RAM, and you are the operating system responsible for loading the right information.

Prompt engineering is evolving into **context engineering** — not just writing one good prompt, but architecting the entire information input.

Content rephrased for compliance with licensing restrictions. Source: [Context Engineering Guide 2026](https://open.substack.com/pub/theaicorner1/p/context-engineering-guide-2026)

```
Prompt engineering (2023–2024):
Focus: how to write a good instruction
Core skills: CRISP, CoT, few-shot
Fits: single conversations, simple tasks

Context engineering (2025–2026):
Focus: how to architect the whole information input
Core skills: information curation, context management, tool orchestration
New questions:
Which information goes into context? (more isn't better)
How is it prioritized and organized?
How do tools fetch information dynamically?
How is multi-turn context managed?
Fits: complex workflows, agents, long-running projects
```

### 6.2 Context engineering in practice

**Principle 1: layer the information**

```
Layer 1 — system instructions (always present):
role definition, output specs, constraints

Layer 2 — task context (loaded as needed):
the current task's background and data

Layer 3 — reference material (retrieved dynamically):
relevant document snippets via RAG

Layer 4 — conversation history (managed automatically):
prior turns (may need summarization/compression)
```

**Principle 2: manage the context budget**

Every model's window is finite. Manage context like an ad budget:

| Content type | Priority | Budget share |
|--------------|----------|--------------|
| System instructions & role | highest | 5–10% |
| Core data for the current task | high | 40–50% |
| Reference material & examples | medium | 20–30% |
| Conversation history | low | 10–20% |

**Principle 3: output contracts**

The 2026 best practice is to design the prompt as a "contract":

```
Output contract = {
format: table/JSON/Markdown
length: max X words
tone: professional/friendly/brief
required sections: [list]
behavior when unsure: explicitly mark "uncertain"
error handling: if input data is insufficient, ask rather than guess
}
```

Content rephrased for compliance with licensing restrictions. Source: [Prompt Engineering Best Practices 2026](https://promptbuilder.cc/blog/prompt-engineering-best-practices-2026)

---

## 7. Learning Resources

### 7.1 Essential reading

| Resource | Source | Why |
|----------|--------|-----|
| [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering) | OpenAI | the official best practices — most authoritative |
| [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) | Anthropic | Claude-specific techniques, XML tag usage |
| [ChatGPT Prompt Engineering for Developers](https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/) | DeepLearning.AI | free 1.5 h hands-on course |
| [12 Advanced Prompt Engineering Techniques](https://www.aipromptlibrary.app/blog/advanced-prompt-engineering-techniques) | AI Prompt Library | a current roundup of advanced techniques |

### 7.2 Practice plan

| Stage | Do | Time |
|-------|----|------|
| Week 1 | rewrite your existing prompts with CRISP | 15 min/day |
| Week 2 | try the 6 advanced techniques, keep what fits | 20 min/day |
| Week 3 | build a personal template library (10+ prompts) | one 2 h block |
| Ongoing | after each AI session, reflect on how the prompt could improve | 2 min each |

## 9. Completion Checklist

- [ ] Can write structured prompts with the CRISP framework
- [ ] Have used at least 3 advanced techniques (CoT, few-shot, role-playing, ...)
- [ ] Built a personal library of 10+ go-to prompts
- [ ] Can spot and fix the common prompt mistakes
- [ ] Understand context engineering's concepts and principles

Complete all of the above and you've mastered the core skill of communicating with AI. Next: [F3 Knowledge & RAG](f3-rag-knowledge.md) — teaching AI to understand your private data.
