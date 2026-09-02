# F3. Knowledge Bases & RAG

> **Track**: Path 0: AI Foundations · **Module**: F3
> **Last updated**: 2026-07-31
> **Level**: Intermediate
> **Time**: 2 hours
> **Prerequisites**: [F1 The Evolution of AI](f1-ai-evolution.md), [F2 Prompt Engineering](f2-prompt-engineering.md)

---


```mermaid
flowchart LR
F1["F1 The Evolution of AI"]
F1 --> F2
F2["F2 Prompt Engineering"]
F2 --> F3
F3[" F3 Knowledge & RAG<br/>(you are here)"]:::current
F3 --> F4
F4["F4 Automation & Agents"]
classDef current fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
```

---

## Chapter Navigation

1. [Why AI Doesn’t Know Your Product Information](#1-why-ai-doesnt-know-your-product-information) · 2. [Embeddings](#2-embeddings-teaching-ai-to-understand-meaning) · 3. [Vector Databases](#3-vector-databases-storing-and-retrieving-meaning) · 4. [RAG Architecture](#4-rag-architecture-the-full-workflow) · 5. [Hands-On Overview](#5-hands-on-overview-building-a-product-knowledge-base) · 6. [RAG Optimization Techniques](#6-rag-optimization-techniques) · 7. [FAQ](#7-faq) · 8. [Learning Resources](#8-learning-resources) · 9. [Common Traps](#9-common-traps) · 10. [Completion Checklist](#10-completion-checklist)


## What You'll Understand

Why doesn't ChatGPT know your product details? How do you get AI to answer from your private data? RAG is the core technology that solves this.

After this module you'll be able to:
- Explain why AI doesn't know your products, policies, or internal data
- Explain embeddings in plain language
- Know what a vector database is and why you need one
- Understand the full RAG architecture and workflow
- Judge when a scenario needs RAG and when it doesn't
- Follow the basic steps of building a product knowledge base (for code, see [B3 RAG Knowledge Base](../b-developers/b3-rag-knowledge-base.md))

> **This module's scope**: conceptual understanding — no code required. To actually build a RAG system, continue to [Path B: B3 RAG Knowledge Base](../b-developers/b3-rag-knowledge-base.md) afterward.

---

## 1. Why AI Doesn't Know Your Product Information

### 1.1 Where AI's knowledge comes from

Recall F1: an LLM's knowledge comes entirely from training data — public text from the internet: Wikipedia, news, forums, code repositories.

**What AI knows:**
- Amazon's general rules and policies (public information)
- General traits of common categories (public discussion)
- Generic e-commerce operations knowledge (blogs, tutorials)

**What AI doesn't know:**
- Your product's actual specs and selling points
- Your internal pricing strategy and profit data
- Your suppliers and sourcing costs
- Your sales history and trends
- Your customer-service SOPs and internal policies
- The latest platform policy changes (training data has a cutoff)

### 1.2 Three ways to make AI "know" your data

| Method | Mechanism | Pros | Cons | Fits |
|--------|-----------|------|------|------|
| **Paste it in** | put the data in the prompt | simplest, zero cost | bounded by the context window (128K–1M tokens) | small data (<50 pages) |
| **Fine-tuning** | retrain the model on your data | the model "remembers" your knowledge | expensive, slow to update, can forget | changing model style/format |
| **RAG** | retrieve relevant data at query time, inject into the prompt | live updates, cheap, explainable | you must build a retrieval system | large data, frequent updates |

### 1.3 The e-commerce analogy

**Pasting** = printing all your documents and spreading them on the desk for your assistant to consult.
- Fine when there's little material
- The desk runs out of space when there's a lot (context window limit)

**Fine-tuning** = making your assistant spend a month memorizing everything.
- Fast answers once memorized
- But updated material means re-memorizing (retraining)
- And they may mix things up (hallucination)

**RAG** = giving your assistant a filing cabinet and a retrieval system. For every question, they first pull the relevant folder, then answer from it.
- The cabinet updates any time
- Answers are traceable (back to specific documents)
- The cabinet can grow without limit

> **Bottom line**: for cross-border e-commerce teams, RAG is the practical choice. Large volumes, frequent updates, and traceability requirements — exactly RAG's strengths.

---

## 2. Embeddings: Teaching AI to "Understand" Meaning

### 2.1 What is an embedding

An embedding converts text into a list of numbers (a vector) that captures the text's *meaning*.

**The intuition:**

Imagine placing products on a map. The traditional way is keyword matching — "Bluetooth earbuds" only matches documents containing exactly those words.

The embedding way places each product in a "semantic space":
- "Bluetooth earbuds" and "wireless earbuds" sit close together (similar meaning)
- "Bluetooth earbuds" and "Bluetooth speaker" are a medium distance apart (related, different)
- "Bluetooth earbuds" and "kitchen knives" are far apart (unrelated)

```
Semantic space sketch (simplified to 2D):

audio devices
↑
Bluetooth speaker    wireless earbuds
Bluetooth earbuds
smartwatch    wired earbuds

← wearables    accessories →

phone case

kitchen knives (far away, not in this region)
```

Real embeddings aren't 2D but 768D or 1536D (hundreds to thousands of dimensions), but the principle is the same: semantically similar text → nearby vectors.

### 2.2 How embedding works

```
Input text → embedding model → vector (a list of numbers)

Example:
"This Bluetooth headset has great noise cancellation"
→ [0.12, -0.34, 0.56, 0.78, -0.23, ..., 0.45] (1536 numbers)

"The active noise cancelling on these wireless earbuds is excellent"
→ [0.11, -0.32, 0.55, 0.79, -0.21, ..., 0.44] (1536 numbers)

The two vectors are very close → similar meaning!
```

### 2.3 Common embedding models

| Model | Provider | Dimensions | Price | Fits |
|-------|----------|-----------|-------|------|
| text-embedding-3-small | OpenAI | 1536 | $0.02/M tokens | best value, default choice |
| text-embedding-3-large | OpenAI | 3072 | $0.13/M tokens | when you need more precision |
| Voyage-3 | Voyage AI | 1024 | $0.06/M tokens | code and technical docs |
| BGE-M3 | BAAI | 1024 | free (open source) | multilingual, self-hosted |
| Cohere Embed v3 | Cohere | 1024 | $0.10/M tokens | multilingual search |

**Recommendations for cross-border e-commerce:**
- Tight budget: OpenAI text-embedding-3-small (cheap and good)
- Multilingual needs: BGE-M3 (free, open source; supports Chinese/English/Japanese/German/French)
- Data privacy: BGE-M3 self-hosted (data never leaves your servers)

### 2.4 Keyword search vs semantic search

| Dimension | Keyword search | Semantic search (embeddings) |
|-----------|----------------|------------------------------|
| Mechanism | exact keyword match | semantic similarity match |
| Does "wireless earbuds" find "Bluetooth earbuds"? | no (different keywords) | yes (similar meaning) |
| Does "earphone noise cancel" find Chinese documents? | no (different language) | yes (cross-lingual semantic match) |
| Speed | extremely fast | fast (milliseconds) |
| Fits | precise lookup of known content | fuzzy lookup, cross-language lookup |

> **In practice the best answer is hybrid search**: keyword search to narrow the field, then semantic search to match precisely. That's the mainstream RAG design in 2026.

---

## 3. Vector Databases: Storing and Retrieving Meaning

<!-- claims: illustrative -->

> The numbers in this section are constructed to illustrate the point, not measured.


### 3.1 Why you need one

Ordinary databases (MySQL, PostgreSQL) excel at exact queries: "find products where price = $25.99."

They're poor at semantic queries: "find reviews semantically similar to 'noise cancellation is weak'."

Vector databases are purpose-built to store and retrieve vectors — finding the most similar few among millions in milliseconds.

### 3.2 The main vector databases

| Database | Type | Price | Fits | Trait |
|----------|------|-------|------|-------|
| [Chroma](https://www.trychroma.com/) | embedded | free, open source | prototyping, small scale | Python-native, simplest |
| [FAISS](https://github.com/facebookresearch/faiss) | library | free, open source | large scale, high performance | by Meta, extremely fast |
| [Pinecone](https://www.pinecone.io/) | cloud | free tier + paid | production, zero ops | fully managed, works out of the box |
| [Weaviate](https://weaviate.io/) | self-hosted/cloud | free, open source | hybrid search | keyword + semantic hybrid |
| [Qdrant](https://qdrant.tech/) | self-hosted/cloud | free, open source | high-performance production | written in Rust, excellent performance |
| [pgvector](https://github.com/pgvector/pgvector) | PostgreSQL extension | free | teams already on PostgreSQL | no extra database needed |

**Recommendations:**
- Just starting: Chroma (simplest — 10 lines of code)
- Production: Pinecone (no ops) or Qdrant (self-hosted)
- Already on PostgreSQL: pgvector (no extra infrastructure)

Content rephrased for compliance with licensing restrictions. Sources: [Vector Databases 2026 Guide](https://iterathon.tech/blog/vector-databases-ai-applications-guide), [Embeddings and Vector Databases Guide](https://tutorialq.com/ai/machine-learning/embeddings-and-vector-databases)

### 3.3 How a vector database is used

```
Write phase (one-time):
documents → chunking → embedding model → vectors → stored in the vector DB

Query phase (every question):
user question → embedding model → query vector → vector DB search → most similar chunks returned
```

**Chunking is the crux:**

You can't store a 50-page manual as one vector — too big; the meaning gets diluted. Split documents into chunks:

| Chunking strategy | Chunk size | Fits |
|-------------------|-----------|------|
| By paragraph | 100–300 words | structured documents (FAQ, policies) |
| Fixed length | 500–1,000 words | long documents (product manuals) |
| Semantic | auto-detected | mixed content (reviews, email) |
| By heading level | split at H1/H2/H3 | Markdown/HTML documents |

> **The golden rule of chunking**: each chunk should hold one complete unit of information. Too small loses context; too big adds noise. 500–1,000 words is usually a good starting point.

---

## 4. RAG Architecture: the Full Workflow

### 4.1 RAG's three stages

```
Stage 1: Indexing — one-time preparation

collect documents → chunk them → generate embeddings
↓ ↓ ↓
product manuals 500 words/chunk vectorize
FAQ documents
review data → store in the vector database
policy files


Stage 2: Retrieval — every question

user question → query vector → vector DB search
↓ ↓
"Is this product waterproof?" top 5 relevant chunks returned


Stage 3: Generation — every question

system prompt + retrieved chunks + user question
↓
sent to the LLM
↓
the LLM answers based on the retrieved content
"According to the product manual, this product is IPX5 water-resistant..."

```

### 4.2 RAG vs asking the AI directly

**Scenario: a customer asks "which Bluetooth version do your earbuds support?"**

**Direct question (no RAG):**
```
AI: "Generally, earbuds from 2024–2025 support Bluetooth 5.0 or 5.3..."
→ generic — not your product's actual answer
```

**With RAG:**
```
Retrieved chunk:
"Model XB-500, Bluetooth 5.3, supports AAC/SBC/LDAC codecs,
15 m range, connects to 2 devices simultaneously."

AI answers from the retrieved content:
"Our XB-500 earbuds support Bluetooth 5.3 with AAC, SBC, and LDAC
codecs, a 15-meter range, and simultaneous connection to 2 devices."
→ precise, specific, grounded in your product data
```

### 4.3 RAG applications in cross-border e-commerce

> **Related**: [B3 RAG Knowledge Base](../b-developers/b3-rag-knowledge-base.md) for the build; [A4 Customer Service](../a-operators/a4-customer-service.md) for RAG-driven FAQ answering.

| Scenario | Knowledge base contents | Example question | Value |
|----------|------------------------|------------------|-------|
| **Product FAQ system** | manuals, specs, usage guides | "How long does it last?" "Fast charging?" | support efficiency +80% |
| **Internal policy lookup** | returns policy, pricing rules, approval flows | "What's the EU returns policy?" | fast onboarding |
| **Compliance knowledge base** | per-market certification rules, regulations | "What certification does Bluetooth need in Japan?" | lower compliance risk |
| **Competitor intelligence** | competitor reviews, listings, price history | "What are competitor A's recent complaints?" | automated monitoring |
| **Operations SOP library** | handbooks, best practices, precedents | "What's the standard launch flow?" | knowledge retention |
| **Supplier records** | supplier profiles, quotes, correspondence | "What price did we agree with factory B?" | sourcing decisions |

### 4.4 Prompt design for RAG

A RAG prompt typically has three parts:

```
System prompt (fixed):
"You are a product support assistant. Answer using the reference
material below. If the material doesn't cover it, tell the user you
are not sure — do not invent an answer. Cite your sources."

Retrieved chunks (dynamic):
---reference start---
[Chunk 1]: Model XB-500, Bluetooth 5.3...
[Chunk 2]: Water resistance IPX5, usable in rain...
[Chunk 3]: Battery: 30 h with ANC on, 50 h off...
---reference end---

User question (dynamic):
"Can I swim with these earbuds?"
```

**Key design principles:**

| Principle | How | Why it matters |
|-----------|-----|----------------|
| Instruct answering from the material | "answer using the reference material" | reduces fabrication |
| Allow "I don't know" | "if it's not in the material, say so" | avoids forced wrong answers |
| Require citations | "cite your sources" | enables verification |
| Bound the scope | "only answer product-related questions" | keeps the AI on-topic |

### 4.5 Evaluating a RAG system

How do you know your RAG system is good? Evaluate two dimensions:

**Retrieval quality:**

| Metric | Meaning | How to measure |
|--------|---------|----------------|
| Recall | were the relevant documents retrieved? | prepare test questions, check the results contain the right documents |
| Precision | are the retrieved documents all relevant? | check how many of the top 5 are truly relevant |
| MRR (Mean Reciprocal Rank) | where does the right document rank? | higher rank for the correct document is better |

**Generation quality:**

| Metric | Meaning | How to measure |
|--------|---------|----------------|
| Faithfulness | is the answer grounded in the retrieved content? | verify every claim exists in the retrieved chunks |
| Relevancy | does the answer address the question? | human review for topicality |
| Completeness | does it cover all the relevant information? | check for missing key facts |

**A simple evaluation method:**

Prepare 20–30 test questions with reference answers, run them regularly, and track quality over time.

```
Test set example:
| Question | Expected answer | Expected source |
|----------|-----------------|-----------------|
| "Which Bluetooth version?" | "5.3" | product_spec.md |
| "Can it go in water?" | "IPX5 — splash-proof, not submersible" | product_spec.md |
| "How long is the warranty?" | "12 months" | warranty_policy.md |
```

### 4.6 RAG cost analysis

| Cost item | One-time | Recurring | Notes |
|-----------|----------|-----------|-------|
| Embedding generation | $0.01–0.10 | | depends on volume (~$0.05 per 1,000 pages) |
| Vector database | $0 | $0–50/mo | Chroma free; Pinecone has a free tier |
| LLM API calls | | $0.01–0.10/query | per-query LLM cost |
| Development time | 8–40 h | 2–4 h/mo | build + maintenance |

**Example estimate (small product knowledge base):**

```
Volume: 50 product manuals + 500 FAQs ≈ 200 pages
Embedding cost: $0.02 (one-time)
Vector DB: $0 (local Chroma)
Monthly queries: 1,000
LLM cost: $5–10/mo (T3 fast tier)
Total monthly cost: $5–10

Against labor:
Support answers 30 product questions/day × 5 min each = 2.5 h/day
Monthly labor: 2.5 h × 22 days × $15/h = $825

ROI: ($825 − $10) / $10 = 8,150%
```

---

## 5. Hands-On Overview: Building a Product Knowledge Base

> This section is conceptual. For the full code walkthrough, see [B3 RAG Knowledge Base](../b-developers/b3-rag-knowledge-base.md).

### 5.1 The minimal RAG system (10 lines of code)

With LlamaIndex + Chroma, 10 lines of Python get you a working RAG system:

```python
# Conceptual code (full version in module B3)
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# 1. Load documents (manuals, FAQs, ...)
documents = SimpleDirectoryReader("product_docs/").load_data()

# 2. Build the index (auto chunking + embedding + storage)
index = VectorStoreIndex.from_documents(documents)

# 3. Create a query engine
query_engine = index.as_query_engine()

# 4. Ask
response = query_engine.query("Which Bluetooth version does this product support?")
print(response)
# → "According to the manual, the XB-500 supports Bluetooth 5.3..."
```

### 5.2 Build steps at a glance

```
Step 1: collect documents (1–2 h)
product manuals (PDF/Word)
FAQ documents
common support questions and answers
spec sheets
internal policy documents

Step 2: preprocess (30 min)
convert to one format (text/Markdown)
clean formatting issues (mojibake, stray blank lines)
verify completeness

Step 3: build the RAG system (1–2 h)
install dependencies (pip install llama-index chromadb)
configure the embedding model and LLM
load documents and build the index
test queries

Step 4: optimize and operate (ongoing)
tune the chunking strategy
tune retrieval parameters
add new documents
monitor answer quality
```

### 5.3 No-code RAG options

If you don't want to write code, these tools ship RAG out of the box:

| Tool | Price | Trait | For whom |
|------|-------|-------|----------|
| ChatGPT + file upload | $20/mo (Plus) | upload PDFs/docs, ask directly | individuals, small volumes |
| Claude + Projects | $20/mo (Pro) | create a project, upload documents as its knowledge base | individuals needing a persistent knowledge base |
| Notion AI | $10/mo | AI Q&A over your Notion pages | teams already on Notion |
| Dify | free, open source | visual RAG app builder | customization without much code |
| Coze | free | by ByteDance, Chinese-friendly | Chinese-language scenarios, fast setup |

---

## 6. RAG Optimization Techniques

### 6.1 What drives RAG quality

| Factor | Effect | Direction |
|--------|--------|-----------|
| **Chunking strategy** | too big → noise; too small → lost context | test sizes; start at 500–1,000 words |
| **Embedding model** | model quality bounds semantic accuracy | use OpenAI or BGE-M3, not older models |
| **Retrieval count (Top-K)** | too few → missed info; too many → noise | start at Top-5, tune from results |
| **Document quality** | garbage in, garbage out | ensure accuracy and clean formatting |
| **Query rewriting** | user questions may be imprecise | rewrite the question with an LLM before retrieving |

### 6.2 Advanced RAG patterns (2026)

```
Naive RAG:
question → retrieve → generate
Simple and effective — fine for most scenarios

Advanced RAG:
question → query rewriting → hybrid retrieval → reranking → generate
Query rewriting: optimize the user's question with an LLM
Hybrid retrieval: keyword + semantic together
Reranking: reorder results with a cross-encoder
For quality-critical scenarios

Modular RAG:
question → routing → best retrieval strategy → multi-source retrieval → fusion → generate
Routing: classify the question, choose the strategy
Multi-source: query several knowledge bases at once
Fusion: merge multi-source results
For complex enterprise applications
```

Content rephrased for compliance with licensing restrictions. Sources: [RAG Architecture Guide 2026](https://ztabs.co/blog/rag-architecture-guide), [RAG Systems Production Guide 2026](https://iterathon.tech/blog/rag-systems-production-guide-2025)

---

## 7. FAQ

### 7.1 RAG FAQ

| Question | Answer |
|----------|--------|
| "How is RAG different from uploading files to ChatGPT?" | ChatGPT's file upload is itself a form of RAG — but you can't control chunking, retrieval parameters, etc. Self-built RAG is fully customizable. |
| "My data is tiny (<10 documents) — do I need RAG?" | No. Uploading to ChatGPT/Claude is enough. RAG's value shows at larger volumes (50+ documents). |
| "Does RAG guarantee 100% accuracy?" | No. RAG reduces hallucination but can't eliminate it. Retrieval can miss key information, and the LLM can misread retrieved content. Human-review critical answers. |
| "Can multilingual documents share one knowledge base?" | Yes — use a multilingual embedding model (e.g., BGE-M3), or index per language. |
| "How much does a RAG system cost?" | Minimum: Chroma (free) + OpenAI embeddings ($0.02/M tokens) + a T3 fast-tier LLM. ~$1–2 per 1,000 queries. |
| "What about data security?" | Local embedding model (BGE-M3) + local LLM (Ollama) + local vector DB (Chroma) — data never leaves your servers. |

### 7.2 When you don't need RAG

| Scenario | Why not | Alternative |
|----------|---------|-------------|
| Very small data (<10 pages) | fits straight into the prompt | ChatGPT/Claude file upload |
| No live updates needed | the data never changes | fine-tuning may fit better |
| Only changing output style | RAG solves "knowledge," not "style" | fine-tuning or prompt adjustments |
| General-knowledge questions | the AI already knows | just ask directly |

---

## 8. Learning Resources

### 8.1 Getting started

| Resource | Source | Why |
|----------|--------|-----|
| [Building RAG from Scratch](https://www.deeplearning.ai/courses/building-evaluating-advanced-rag) | DeepLearning.AI | free course, RAG from zero |
| [LlamaIndex starter tutorial](https://docs.llamaindex.ai/en/stable/getting_started/starter_example/) | LlamaIndex | the simplest RAG intro — 10 lines |
| [RAG Architecture Guide 2026](https://ztabs.co/blog/rag-architecture-guide) | ZTabs | the current RAG architecture landscape |
| [Embeddings Guide](https://tutorialq.com/ai/machine-learning/embeddings-and-vector-databases) | TutorialQ | plain-language embeddings and vector DBs |

### 8.2 Going deeper

| Resource | Source | Why |
|----------|--------|-----|
| [B3 RAG Knowledge Base module](../b-developers/b3-rag-knowledge-base.md) | ecommerce-ai-skills | this hub's hands-on module, complete code |
| [Vector Databases 2026 Guide](https://iterathon.tech/blog/vector-databases-ai-applications-guide) | Iterathon | selection and production deployment |
| [Retrieval-Augmented Generation (RAG) paper](https://arxiv.org/abs/2005.11401) | Meta AI | the original RAG paper (2020) — theoretical grounding |

## 9. Common Traps

### 9.1 Assuming RAG eliminates hallucination

RAG reduces invention from nothing. It does not eliminate "retrieved it but misread it" or "found nothing and answered anyway." The real defense is requiring source attribution in the prompt and permitting the model to answer "not in the material."

### 9.2 Copying default chunking settings

Fixed-length chunking cuts a spec table or a compliance clause in half, and the retrieved fragment naturally can't answer the question. For e-commerce, chunking by semantic unit (one SKU, one policy, one FAQ) usually beats chunking by character count.

### 9.3 Building the knowledge base and never maintaining it

Product specs, platform policies, and shipping rules all change. The most common RAG failure isn't technical — it's that nobody updated the material for six months, which makes it more dangerous than not having it.

### 9.4 Using RAG for what belongs in a database

"Which SKU sold best last month" is a SQL query, not a semantic retrieval problem. Forcing structured queries through RAG is both slower and less accurate.

---

## When this doesn't work

- **You have fewer than a few dozen documents.** RAG earns its keep by finding the relevant few passages in a large body of text. With a dozen product manuals, putting all of them in the context window is simpler and more accurate — today's context windows hold hundreds of thousands of characters, and the retrieval layer only adds a new place to fail.
- **The answer needs an aggregate, not a location.** "Which three of our products have the highest return rate" is not a question retrieval can answer — it returns a few similar passages, not a total. Query a database for that. Retrieval-based QA is good at "where did we say X", not at "how much X is there in total".
- **The documents themselves are wrong or stale.** RAG faithfully surfaces whatever you gave it. Leave a two-year-old fee schedule in the knowledge base and it will confidently quote two-year-old fees to a customer. Auditing the documents before you launch matters far more than tuning chunk_size.
- **You are liable when the answer is wrong.** A support bot replying to customers directly, compliance answers feeding a declaration — in those settings RAG's habit of inventing when retrieval comes up empty is a real risk. Either add human review, or instruct the prompt to say it does not know and then actually test that it does (the support prompt in §7 exists for this).

---

## 10. Completion Checklist

- [ ] Can explain why AI doesn't know your product information
- [ ] Understand embeddings (text → vector → semantic similarity)
- [ ] Know what vector databases do and the main options
- [ ] Can sketch RAG's three-stage architecture (index → retrieve → generate)
- [ ] Can judge whether a scenario needs RAG
- [ ] Know at least one no-code RAG option (ChatGPT file upload / Claude Projects)

Complete all of the above and you understand the core technology for grounding AI in private data. Next: [F4 Automation & Agents](f4-agent-automation.md) — making AI execute tasks, not just answer questions.
