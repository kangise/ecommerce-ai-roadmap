# A14. Agentifying Operations

> **Track**: Path A: Operators · **Module**: A14
> **Last updated**: 2026-07-31
> **Level**: Intermediate
> **Time**: 1 hour/day, 1–2 weeks
> **Prerequisite**: [F2 Prompt Engineering](../0-foundations/f2-prompt-engineering.md) (especially §5, From Prompt to Skill)

---

## Chapter Navigation

1. [What agentifying actually saves](#1-what-agentifying-actually-saves) · 2. [Data-source audit](#2-data-source-audit-the-precondition) · 3. [Task triage](#3-task-triage-what-to-hand-over-what-to-keep) · 4. [Converting existing prompts into skills](#4-converting-existing-prompts-into-skills) · 5. [Three operations agents you can copy](#5-three-operations-agents-you-can-copy) · 6. [Common traps](#6-common-traps) · 7. [Completion checklist](#7-completion-checklist)

---

## What You'll Learn

The previous 13 chapters of Path A teach you to write prompts so AI does the work. This one covers the next step: **making that work stop requiring you to trigger it by hand each time**.

After this module you'll be able to:
- Judge which of your operational steps are worth agentifying and which would be a waste right now
- Audit where each step's data comes from — the precondition that decides whether agentifying is even possible
- Draw the human-confirmation boundary and know which actions an agent must never take alone
- Convert Path A's existing prompts into reusable skill files
- Stand up three concrete operations agents: daily report, restock alert, negative-review response

> **In one line**: agentifying isn't "moving the prompt somewhere else" — it's **removing the step where you shuttle data in the middle**. If the data can't move, agentifying is a false premise.

---

## 1. What agentifying actually saves

Take the most typical workflow in this book. Here's what "weekly ad optimization" actually costs you today:

```
1. Log into Seller Central                     ← human, 2 min
2. Download the search-term report             ← human, 3 min
3. Open ChatGPT, paste data, paste prompt      ← human, 2 min
4. Wait for the analysis                       ← AI, 1 min
5. Read it, decide which advice to accept      ← human, 10 min
6. Go back to the console, apply each change   ← human, 15 min
```

**The AI did step 4 only.** The other 32 minutes are human, and steps 1, 2, 3, and 6 are pure shuttling — no judgment, just moving data from one place to another.

That's where the value is. Step 5 — deciding what to accept — **should not be automated**. That's your job.

| Step | Nature | After agentifying |
|------|--------|-------------------|
| 1-2 fetch | Pure shuttling | Agent reads it directly via API/MCP |
| 3 assemble prompt | Pure shuttling | Already written into the skill file |
| 4 analyze | AI judgment | Unchanged |
| **5 decide what to accept** | **Your judgment** | **Stays human — this is the gate** |
| 6 apply changes | Pure shuttling | Agent executes after you confirm |

**So the right goal isn't "let the agent run ads autonomously" — it's "compress 32 minutes of shuttling into 10 minutes of judgment."** People who automate step 5 too usually hit an incident needing manual cleanup within the first month.

---

## 2. Data-source audit: the precondition

Whether steps 1–2 can be automated depends entirely on **whether the data is reachable**. This is the most practical section in the chapter. Do this table before anything else.

### 2.1 Sort your data sources into three classes

| Class | Traits | Agentifiable? | Typical examples |
|-------|--------|--------------|------------------|
| **Class A: has an API** | Official, stable interface | Yes — do these first | Amazon SP-API, Amazon Ads API, Shopify Admin API |
| **Class B: export but no API** | Downloadable file, but you click for it | Semi-auto: human exports, agent processes | Certain platform back-office reports |
| **Class C: UI only** | No API, no export | Postpone, or use computer use (slow and costly) | Regional platform consoles, some supplier portals |

**The conclusion is blunt: agentify Class A steps first, settle for semi-automation on Class B, leave Class C alone for now.** See the trade-off discussion in [B6 §9 Computer Use](../b-developers/b6-mcp-agentic-workflow.md).

### 2.2 Audit table template

Fill one row per operational step. Once it's complete, what to do and in what order answers itself.

| Operational step | Data needed | Source class | How to fetch | Minutes/week spent shuttling |
|-----------------|-------------|--------------|--------------|------------------------------|
| Ad optimization | Search-term report | A (Ads API) | API | 20 |
| Restocking | Inventory + sales | A (SP-API) | API | 15 |
| Review response | New reviews | A/B (platform-dependent) | API or export | 30 |
| Competitor monitoring | Competitor price/BSR | C (mostly no API) | Postpone | 40 |

> **Priority is the last column divided by fetch difficulty.** Long shuttling time on Class A data goes first.

### 2.3 An honest judgment

If your audit comes back mostly Class C, **what you should be doing right now isn't agentifying — it's fixing data availability**: switch to a tool that exports, apply for API access, or accept that some steps stay manual.

Forcing computer use onto Class C is usually slower and more expensive than doing it by hand, and one platform redesign breaks all of it.

---

## 3. Task triage: what to hand over, what to keep

There's exactly one test: **can a mistake be taken back?**

### 3.1 Three tiers

**Green — the agent may complete it autonomously**

Shared traits: read-only, or output circulates internally only, and errors are fixable.

- Pulling data, aggregating, generating the daily report
- Labeling and classifying reviews
- Generating listing/copy **drafts**
- Anomaly detection and alerting (notify only, no action)

**Yellow — the agent does it, but your nod makes it real**

Output goes outside, or changes state on the platform.

- Adjusting ad bids and budgets
- Editing listing content
- Replying to customers
- Submitting restock proposals

The pattern: the agent **prepares but does not submit**, presenting a checklist you tick before it executes.

**Red — never hand these to an agent**

- Delisting products, deleting listings
- Any refund, compensation, or movement of funds
- Accepting platform agreements, changing account settings
- Large purchase orders

This tier isn't "not yet, maybe later" — it's **structurally wrong to automate**, because the payoff is asymmetric: you save minutes and risk a shipment or an account.

### 3.2 The yellow item people miss

**Plenty of people treat "reply to customers" as green. It isn't.** A support reply can't be recalled once sent, and the model is happy to promise refund amounts, replacement timelines, and policy exceptions on your behalf — none of which you authorized.

Every customer-service prompt in this book carries that rule in its `<copy_discipline>` block. Carry it over verbatim when you agentify, and add a human gate on top.

---

## 4. Converting existing prompts into skills

[F2 §5](../0-foundations/f2-prompt-engineering.md) covers the three forms and the migration checklist. This section is the Path A specifics.

### 4.1 Five steps to migrate one prompt

Using [A3's negative-keyword prompt](a3-advertising.md):

**Step 1: confirm the data source.** It needs the search-term report → available via Amazon Ads API → Class A → proceed.

**Step 2: replace "paste data" with "read from."** The original `[paste data: search term, match type…]` becomes a declared source and field list.

**Step 3: make the output machine-readable.** "Negative list + reasoning" as prose was written for a human; now it feeds an API call.

**Step 4: add a preflight check and failure behavior.** Don't run on too few rows or missing fields.

**Step 5: mark the yellow action and gate it.** Adding negatives affects traffic — that's yellow.

### 4.2 What it looks like afterward

```markdown
---
name: negative-keyword-harvester
description: Weekly analysis of the Amazon search-term report, producing a
  negative-keyword list for confirmation. Requires the past 30 days of the
  search-term report (with cost, clicks, orders, sales fields).
---

<data_source>
Amazon Ads API: search-term report, past 30 days, fields must include
searchTerm / matchType / impressions / clicks / cost / orders / sales
</data_source>

<preflight_check>
- Stop if the report has fewer than 200 rows; report "insufficient sample, skipping this week"
- Stop and list missing fields if any required field is absent
</preflight_check>

<role>Amazon PPC negative-keyword expert</role>

<task>
Classify into four quadrants; produce exact-negative / phrase-negative / watch lists
</task>

<data_discipline>
- Use only numbers present in the report; do not estimate; do not draw on industry averages from memory
- Every negative recommendation must trace to a specific search-term row
</data_discipline>

<on_failure>
On insufficient data or failed validation, stop and report. Do not continue with assumed values
</on_failure>

<output_format>
JSON: [{term, matchType, action: "negative_exact"|"negative_phrase"|"watch",
        reason, cost_30d, orders_30d}]
</output_format>

<human_confirmation>
This skill only produces a list for confirmation. It does not call the API to
write negatives. The caller executes the write after the user selects.
</human_confirmation>

<self_check>
(1) Every requested deliverable (Classify into four quadrants; produce exact-nega…) is actually delivered; none omitted. <!-- ref: amazon.negative_keyword.exact.behavior --> <!-- ref: amazon.search_term.classification.observe_word -->
(2) Every figure comes from the pasted data; anything absent is written "missing" — no estimates from memory.
(3) Every conclusion is tagged with its source: [input data] or [model inference].
</self_check>
```

Compare: **the task description and data discipline are unchanged, word for word.** Everything new is about where to read, when not to run, who consumes the output, and who nods.

---

## 5. Three operations agents you can copy

Ordered by implementation difficulty. All three follow the same pattern: **agent fetches, analyzes, and produces a list for confirmation; you nod before anything executes.**

### 5.1 Daily operations report (green — easiest start)

**Why start here**: read-only throughout, no writes at all, error cost near zero. Ideal for observing the agent's judgment quality.

```
Trigger: daily 08:00
Sources: SP-API (sales, inventory) + Ads API (ad spend)
Actions:
  1. Pull yesterday's data
  2. Compare against the trailing 7-day average, flag deviations past threshold
  3. Generate the report, push to Slack/email
Human confirmation: not needed (read-only)
```

**Key design point**: every number in the report must carry its fetch time and source, and the agent must make no "estimates." Its job is to present and flag anomalies, not explain them — you judge the cause once you see the anomaly.

### 5.2 Restock alert (yellow)

```
Trigger: weekly, Monday
Sources: SP-API (inventory, sales history, in-transit)
Actions:
  1. Compute days-of-cover per SKU
  2. For those under the safety line, compute a proposed quantity using lead time
  3. Produce the restock proposal list
Human confirmation: required — restocking is a financial commitment
```

**Key design point**: the restock quantity calculation belongs in code, not the model. The model's job is "which SKUs need attention" and "is there an unusual pattern"; **the actual numbers come from a formula.** Letting the model compute restock quantity is the easiest trap in this chapter — it will give you a plausible number with nothing behind it.

### 5.3 Negative-review response (yellow — highest value, needs the tightest gate)

```
Trigger: a new 1–3 star review is detected
Sources: Review API or platform notification
Actions:
  1. Classify: logistics / quality / expectation mismatch / malicious
  2. Generate a reply draft
  3. Decide whether to escalate to a human
Human confirmation: required — a sent reply can't be recalled
```

**Key design point**: the draft must **never contain a specific refund amount, compensation promise, or timeline guarantee**. You fill those in. The agent's value is compressing 30 minutes of triage and drafting into 3 minutes of review — not making commitments for you.

> Technical implementation of all three is in [B4 Agent Workflow](../b-developers/b4-agent-workflow.md); MCP wiring is in [B6 MCP Integration](../b-developers/b6-mcp-agentic-workflow.md). This chapter covers only where the operational boundaries go.

---

## 6. Common Traps

### 6.1 Building the agent before solving the data source

The most common and most wasteful. If data still has to be exported by hand, the agent has only replaced "paste into ChatGPT" with "paste into the agent." You saved nothing. **Do the §2 audit first.**

### 6.2 Letting the model compute what a formula should

Restock quantity, margin, break-even, ACOS — all have exact formulas. Hand them to a model and you get a plausible number that can't be reproduced or traced. **The rule: if a formula can compute it, use the formula; the model judges and classifies.**

### 6.3 Treating yellow as green

Especially customer replies and listing edits. These are the most tempting to automate (repetitive, time-consuming) and the most likely to cause something irreversible. **The test isn't "is the AI good at this" — it's "can a mistake be undone."**

### 6.4 No audit trail

What the agent changed, when, and on what data — without a record you can neither reconstruct an incident nor appeal to the platform. Every write needs a log. That's the floor for agentifying, not an optional extra.

### 6.5 Doing everything at once

Agentify five steps simultaneously and you can't tell which one caused the problem. **One at a time, two stable weeks before the next.**

---

## When this doesn't work

- **The data source is class C.** The data-source grading at the start of this chapter is not a formality. Agentify something with no API and no reliable export and you will spend most of your time maintaining scrapers rather than operating. For class C, the order is: solve data access first, then talk about automation.
- **The task is in the red zone.** Irreversible actions — moving money, changing prices, promising something to a customer, deleting data — should not run unattended regardless of how accurate the agent is. The right shape for red-zone tasks is agent proposes, human confirms. This is not conservatism: the cost of an error is independent of its probability.
- **The time saved is less than the maintenance.** An agent needs data connections, tools, error handling, and periodic work to keep up with platform API changes. If the action it replaces costs you twenty minutes a week, the arithmetic does not work. Use the task triage table in this chapter to measure what each action actually costs before picking one.
- **Nobody on the team reads agent traces yet.** Agents fail silently — they carry wrong data confidently through to the end. With no one reading the trace and no anomaly alerting, agentifying only swaps human error for automation error you cannot see. Build the "how would we know it went wrong" mechanism before you go live.

---

## 7. Completion Checklist

- [ ] Completed the §2 data-source audit, with each step classified A/B/C
- [ ] Sorted your operational actions into green/yellow/red per §3, written down as a list
- [ ] Migrated at least one existing prompt into a skill file using the five steps in §4
- [ ] Stood up the daily-report agent (green) and ran it stably for a week
- [ ] Configured human confirmation for every yellow action
- [ ] Every write operation produces an audit log
- [ ] Can state plainly: which shuttling steps your agentification removed, and which judgment step you deliberately kept
