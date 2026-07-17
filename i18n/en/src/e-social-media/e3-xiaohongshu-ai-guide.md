# E3. Xiaohongshu (RedNote) AI Operations Guide

> **Track**: Path E: Social Media · **Module**: E3
> **Last updated**: 2026-03-14
> **Difficulty**: Intermediate
> **Estimated time**: 2-3 hours
> **Prerequisites**: [Path 0 Foundations](../0-foundations/)


---

## Chapter Navigation

1. [Xiaohongshu Platform Mechanism and Algorithm](#1-xiaohongshu-platform-mechanism-and-algorithm)
2. [AI Seeding-Note Creation Methodology](#2-ai-seeding-note-creation-methodology)
3. [Xiaohongshu SEO](#3-xiaohongshu-seo)
4. [KOL/KOC Collaboration AI Methodology](#4-kolkoc-collaboration-ai-methodology)
5. [Xiaohongshu E-Commerce Loop](#5-xiaohongshu-e-commerce-loop)
6. [Cross-Border Brands Onboarding Xiaohongshu](#6-cross-border-brands-onboarding-xiaohongshu)
7. [Prompt Templates](#7-prompt-templates)
8. [Common Pitfalls](#8-common-pitfalls)
9. [Completion Checklist](#9-completion-checklist)

---

## What You Will Produce in This Module

- An AI-driven Xiaohongshu seeding-note batch-production process
- A KOL/KOC screening and collaboration methodology
- A Xiaohongshu SEO optimization strategy
- A Xiaohongshu-specific prompt-template library

> **Core idea**: Xiaohongshu is a "seeding-decision platform." Users come to Xiaohongshu not for entertainment, but to make purchase decisions. Conversion rate 21.4% (far exceeding other platforms' 6-8%), 300-350 million MAU, 79% female users, search penetration 70%. AI's core value on Xiaohongshu is helping you produce "authentic-feeling" seeding content — not like an ad, like a friend's recommendation.

---

## 1. Xiaohongshu Platform Mechanism and Algorithm

### 1.1 The CES Scoring Mechanism

Xiaohongshu's content distribution is based on CES (Community Engagement Score):

| Interaction behavior | Weight | Description |
|----------------------|--------|-------------|
| Like | 1 point | Basic interaction |
| Save | 1 point | Indicates the content is valuable (similar to Instagram Save) |
| Comment | 4 points | Deep interaction, what the algorithm values most |
| Share | 4 points | Content's spreading power |
| Follow | 8 points | Highest weight, indicates the content makes users want to keep following |

> **Key insight**: The comment weight is 4x that of a like. So the core of Xiaohongshu operations isn't pursuing likes, but guiding comments. AI can help you design copy strategies that guide comments.

### 1.2 Traffic-Distribution Logic

```
Xiaohongshu's three major traffic entrances:
Explore-page recommendation (60-70% of traffic)
Recommended based on the user's interest tags
A new note has an initial exposure pool of 200-500
After meeting the CES threshold, it enters a larger traffic pool
AI application: optimize cover + title to boost click rate

Search (20-25% of traffic)
Users actively search keywords
Search penetration 70% (far exceeding other platforms)
Ranking factors: keyword match + CES + account weight
AI application: keyword research + note SEO

Following page (10-15% of traffic)
Content from already-followed users
Fan-stickiness maintenance
```

### 1.3 The Essential Difference from Instagram/TikTok

| Dimension | Xiaohongshu | Instagram | TikTok |
|-----------|-------------|-----------|--------|
| User intent | Seeding + decision ("buy or not") | Inspiration + lifestyle | Entertainment + pastime |
| Content style | Authentic, colloquial, like a friend sharing | Refined, aesthetic, aspirational | Entertaining, fast-paced, Hook |
| Core content | Image-text notes (70%) + short video | Reels + Carousel | Short video |
| Search behavior | Extremely strong (70% of users search) | Weak | Medium |
| Conversion path | Note → search → purchase | Reels → Shop → purchase | Video → yellow cart → purchase |
| Trust mechanism | Ordinary-person authentic sharing > creator recommendation | Creator recommendation > brand content | Content quality > follower count |

---

## 2. AI Seeding-Note Creation Methodology

### 2.1 Note-Type Matrix

| Type | Structure | Best scenario | Conversion effect |
|------|-----------|---------------|-------------------|
| Good-product sharing | Cover + usage experience + pros/cons + recommendation | New-product promotion | ⭐⭐⭐ |
| Tutorial/guide | Cover + steps + tips + product placement | Build a professional image | ⭐⭐ |
| Review/comparison | Cover + multi-product comparison + recommendation | Differentiated competition | ⭐⭐⭐ |
| Compilation/list | Cover + "X must-buy items" + introduce one by one | Category coverage | ⭐⭐⭐ |
| Warning/pitfall | Cover + problem description + solution | Spark resonance | ⭐⭐ |
| Unboxing | Cover + unpacking process + first impression | New-product launch | ⭐⭐ |

### 2.2 AI-Generate Seeding-Note Prompt

```
You are a Xiaohongshu viral-note creation expert. Your writing style is authentic, colloquial, like a close friend sharing a good product.

Product info:
- Product name: [name]
- Category: [X]
- Price: [X] yuan
- Core selling points: [3]
- Target audience: [age, scenario, pain points]

Please generate 3 different-angle seeding notes, each including:

1. Cover title (no more than 20 characters, including a number or pain point)
- Formula reference: "number + pain point + solution" or "identity + scenario + good product"

2. Body (300-500 characters)
- Opening: introduce with a pain point or scenario (don't state the product directly)
- Middle: usage experience (first person, colloquial, with emoji)
- Ending: summary recommendation + guide comments ("What do you think?")

3. Tag strategy (15-20)
- 5 trending tags
- 5 category tags
- 5-10 long-tail tags

4. Cover-image suggestion
- Image style (real shot/comparison/list)
- Text-overlay content

The 3 angles:
- Angle 1: pain-point solution ("Finally found...")
- Angle 2: scenario seeding ("[scenario] must-have item")
- Angle 3: comparison review ("Tried X products, recommend this one most")

Requirements:
- Authentic and natural tone, not like an ad
- Appropriate emoji use (2-3 per paragraph)
- Don't use absolute terms like "best," "first," "absolutely" (violates advertising law)
- Include interactive design that guides comments
```

### 2.3 Cover-Design Strategy

The Xiaohongshu cover determines 80% of the click rate:

| Cover type | Applicable scenario | Design points |
|------------|---------------------|---------------|
| Product real shot | Good-product sharing | Clean background + product close-up + text title |
| Comparison image | Review/comparison | Left-right split + Before/After |
| List image | Compilation recommendation | Multi-product collage + numbering |
| Text image | Guide/tutorial | Large-font title + concise background |
| Use scenario | Scenario seeding | Real use scenario + natural light |

> **AI assistance**: Use Canva AI or Meitu to generate cover templates, use ChatGPT to generate cover text.

---

## 3. Xiaohongshu SEO

### 3.1 Keyword-Placement Strategy

```
Xiaohongshu SEO keyword placement:
Title: the core keyword must appear (highest weight)
First 200 characters of the body: include 2-3 keywords (naturally integrated)
In the body: long-tail keywords distributed throughout
Tags: trending words + long-tail words combination
Comment section: supplement keywords in your own comments
```

### 3.2 AI Keyword Research

```
You are a Xiaohongshu SEO expert.

My product category is: [category]
Target audience: [describe]

Please help me do Xiaohongshu keyword research:

1. Core keywords (3-5): large search volume, fierce competition
2. Long-tail keywords (10-15): medium search volume, less competition
3. Scenario keywords (5-10): use scenarios users search for
4. Pain-point keywords (5-10): problems/pain points users search for
5. Competitor keywords (3-5): competitor brand name + category word

Label each keyword with:
- Estimated search popularity (high/medium/low)
- Recommended note type
- Title-usage suggestion
```

---

## 4. KOL/KOC Collaboration AI Methodology

> **Related reading**: [E1 Instagram](e1-instagram-facebook-ai-guide.md) — the Instagram creator-collaboration methodology is referenced in E1; the creator-screening scoring model and Creative Brief template can inform each other.

### 4.1 Xiaohongshu Creator Tiers

| Tier | Follower count | Characteristics | Collaboration model | Budget |
|------|----------------|-----------------|---------------------|--------|
| KOC (ordinary person) | <10K | Strong authenticity, high value | Product exchange/small payment | 0-500 yuan/note |
| Mid-tier creator | 10K-100K | Some influence, high engagement rate | Paid collaboration | 500-5000 yuan/note |
| Top KOL | 100K-1M | Large influence, brand endorsement | Paid collaboration + commission | 5000-50000 yuan/note |
| Super KOL | >1M | Celebrity effect | Brand-ambassador level | 50000+ yuan/note |

> **Xiaohongshu specialty**: Unlike TikTok, on Xiaohongshu the seeding effect of KOCs (ordinary people) is often better than big KOLs, because users trust "real users'" sharing more. Suggested budget allocation: 60% KOC + 30% mid-tier + 10% top.

### 4.2 AI Creator Screening

```
You are a Xiaohongshu creator-collaboration expert.

My product: [name], category [X], price [X] yuan
Target audience: [describe]
Budget: [X] yuan/month

Please help me design a creator-collaboration plan:

1. Creator-screening criteria (scoring model)
- Content relevance (weight 30%)
- Engagement rate (weight 25%): comments/likes ratio
- Follower-persona match (weight 20%)
- Note quality (weight 15%)
- Value for money (weight 10%)

2. Recommended creator combination (based on budget)
- KOC quantity and budget allocation
- Mid-tier creator quantity and budget allocation
- Top KOL quantity and budget allocation

3. Creator-outreach script template (Chinese, Xiaohongshu DM style)

4. Brief template (creation guide for creators)
- Product selling points (must be mentioned)
- Content-direction suggestions (don't restrict creative freedom)
- Prohibited items (banned words, competitor mentions)
- Publishing-time suggestion
```

---

## 5. Xiaohongshu E-Commerce Loop

### 5.1 Xiaohongshu Store vs Driving Traffic Externally

| Method | Advantages | Disadvantages | Best for |
|--------|------------|---------------|----------|
| Xiaohongshu store | On-site loop, short conversion path | Higher commission, limited traffic | Brand direct sales |
| Drive to Tmall/JD | Large traffic, high trust | Redirect loss | Domestic brands |
| Drive to an independent site | High profit, own data | High trust barrier | Cross-border brands |

### 5.2 Conversion Optimization for Notes with Links

- Naturally mention the product in the note, don't hard-sell
- Pin the purchase link in the comment section
- Compilation notes attach multiple product links
- Attach links in the livestream room (Xiaohongshu livestream leans toward a "slow livestream" style)

---

## 6. Cross-Border Brands Onboarding Xiaohongshu

### 6.1 Brand-Account Certification

- Enterprise certification requires a business license (overseas enterprises can use theirs)
- After certification, you get the brand badge, data analysis, and ad-placement permissions
- Cost: 600 yuan/year

### 6.2 Content-Localization Strategy

> **Related reading**: [A2 Listing Optimization](../a-operators/a2-listing-optimization.md) — the multilingual-localization methodology is referenced in A2; the content-localization framework for cross-border brands is reusable.

> **Core principle**: It's not translation, it's re-creation.

| Dimension | Wrong approach | Correct approach |
|-----------|----------------|------------------|
| Language | Directly translate English copy | Rewrite in Chinese, colloquial, down-to-earth |
| Images | Use Western model photos | Use Asian faces or real product shots |
| Selling points | Emphasize technical parameters | Emphasize use scenarios and emotional value |
| Price | Directly mark in USD | Convert to RMB, compare with similar domestic products |
| Trust | Emphasize brand history | Emphasize real user reviews and usage experience |

### 6.3 Compliance Notes

- Advertising law: can't use absolute terms like "best," "first," "absolutely"
- Cosmetics: need a filing number to sell on Xiaohongshu
- Food: needs a Chinese label and import permit
- Medical devices: strictly restricted promotion

---

## 7. Prompt Templates

### 7.1 Xiaohongshu Account Positioning

```
You are a Xiaohongshu brand-operations expert.

Brand info:
- Brand name: [name]
- Category: [X]
- Target audience: [describe]
- Brand tone: [describe]

Please help me design the Xiaohongshu account positioning:
1. Account-name suggestions (3 options)
2. Account bio (no more than 100 characters)
3. Content positioning (mainly what type of notes to post)
4. Content ratio (good-product sharing:tutorial:review:daily = ?:?:?:?)
5. Posting-frequency suggestion
6. The first month's 8 note topics
```

### 7.2 Comment-Section Interaction Scripts

```
Please generate comment-section interaction scripts for the following Xiaohongshu note:

Note topic: [describe]
Product: [name]

Generate:
1. Pinned comment (guide discussion + supplement info)
2. 5 reply templates (for common questions/praise/doubts)
3. 3 follow-up questions to guide interaction (boost comment count)
```

---

## 8. Common Pitfalls

### Pitfall 1: Notes Too Much Like Ads
Xiaohongshu users are extremely sensitive to ads. AI-generated content must go through "de-advertising" processing — add personal experience, real feelings, minor flaws.

### Pitfall 2: Ignoring Comment-Section Operations
The comment weight is 4x that of a like. After posting a note, you must actively reply to comments and guide discussion.

### Pitfall 3: Using Banned Words
Absolute terms like "best," "first," "absolutely effective" violate advertising law, and the note will be traffic-restricted or even deleted.

### Pitfall 4: Only Investing in Top KOLs
On Xiaohongshu, the seeding effect of KOCs is often better. The effect of 100 KOCs may exceed 1 top KOL.

---

## 8.5 Xiaohongshu Algorithm In-Depth Analysis

### Note Lifecycle and Traffic-Pool Mechanism

```
Xiaohongshu note traffic-distribution mechanism:

Phase 1: initial exposure pool (0-2 hours after posting)
The system allocates 200-500 exposures
Based on account weight and content-quality prediction
Key metric: click rate (the cover + title's appeal)
If the click rate is >5%, it enters the next traffic pool

Phase 2: expanded exposure pool (2-24 hours)
Exposure expands to 1000-5000
Key metric: engagement rate (CES score)
Comment weight 4 points > save 1 point > like 1 point
If CES meets the threshold, it keeps expanding
If CES doesn't meet the threshold, recommendation stops

Phase 3: large traffic pool (24 hours-7 days)
Exposure can reach 10K-100K+
Enters the Explore-page popular recommendations
Search ranking rises
Continuously gains long-tail traffic

Phase 4: long-tail traffic (7 days-several months)
Mainly search traffic
A quality note can continuously gain traffic for months
After the keyword ranking stabilizes, it becomes "evergreen content"
This is the biggest difference between Xiaohongshu and TikTok (TikTok content has a short lifespan)
```

### Hands-on Techniques to Improve the CES Score

| Interaction type | Weight | Improvement strategy |
|------------------|--------|----------------------|
| Comment (4 pts) | Highest | Ask a question at the end of the body ("What do you think?" "Have you used it?"); comment first yourself in the comment section to guide discussion; reply to every comment |
| Share (4 pts) | Highest | Create "worth-sharing-with-friends" content (lists/guides/warnings); guide "share with friends who need it" in the body |
| Follow (8 pts) | Highest per action | Series content ("Follow me to see the next one"); highlight the value proposition in the bio |
| Save (1 pt) | Basic | Create "worth-saving" content (tutorials/lists/comparison tables); guide "save first, then read" |
| Like (1 pt) | Basic | The basic metric of content quality |

### AI-Optimize CES Score Prompt

```
You are a Xiaohongshu algorithm-optimization expert.

Here is the data for my most recent 5 notes:
| Note title | Exposure | Click rate | Likes | Saves | Comments | Shares | CES |
[paste data]

Please analyze:
1. Which note has the highest CES? Why?
2. Which note has the highest click rate? What are the cover/title characteristics?
3. What do the notes with the most comments have in common?
4. How to boost the comment count? (specific copy-guidance strategy)
5. How to boost the save count? (what type of content is most likely to be saved)
6. Topic suggestions for the next 5 notes (based on data trends)
```

---

## 8.6 Xiaohongshu Content Creation Advanced

### Viral-Note Title Formula Library

| Formula | Example | Applicable scenario | Estimated click rate |
|---------|---------|---------------------|----------------------|
| Number + pain point + solution | "5 habits to improve your skin, the 3rd is so important" | Tutorial/guide | ⭐⭐⭐ |
| Identity + scenario + good product | "3 must-have gadgets for commuters" | Good-product recommendation | ⭐⭐⭐ |
| Comparison + conclusion | "Tried 10 neck fans, only recommend these 2" | Review/comparison | ⭐⭐⭐ |
| Counterintuitive + truth | "Stop buying XX! 90% of people chose wrong" | Warning/education | ⭐⭐⭐ |
| Time + effect | "Stuck with it for 30 days, the change is huge" | Before/After | ⭐⭐ |
| Price + surprise | "Got a ¥500 effect for ¥99" | Value-for-money recommendation | ⭐⭐⭐ |
| Regret + recommendation | "Regret not buying earlier! Can't go back after using it" | Good-product seeding | ⭐⭐⭐ |

### Xiaohongshu Body-Writing Framework

```
Viral-note body structure (300-500 characters):

Paragraph 1: scene introduction (50-80 characters)
Start with a pain point or scenario, don't state the product directly
Example: "Every time I go out, I'm sweating within 5 minutes, summer is really hard"
Use first person, colloquial
Include 1-2 emoji

Paragraph 2: product introduction (50-80 characters)
Naturally transition to the product
Example: "Until a friend recommended this neck fan, my summer was finally saved!"
Don't use words like "ad" or "recommend"
As natural as a friend sharing

Paragraph 3: usage experience (100-150 characters)
Describe the usage feeling in detail
Include specific details ("the airflow has 3 levels, the max is really cool")
Mention 1-2 minor flaws (adds authenticity)
Use-scenario description ("usable for commuting/exercise/shopping")
Use lots of emoji and colloquial expressions

Paragraph 4: summary recommendation (50-80 characters)
Summarize the core recommendation reason
Price info ("you can get it for ¥XX")
Suitable audience
Guide interaction ("How do you cool down in summer? Tell me in the comments!")

Tag section (15-20 tags):
5 trending tags (#good product recommendation #summer essentials)
5 category tags (#neck fan #portable fan)
5 scenario tags (#commuting item #outdoor gear)
5 long-tail tags (#summer going-out gadget #under-100 good product)
```

### Xiaohongshu Video Notes vs Image-Text Notes

| Dimension | Image-text note | Video note |
|-----------|-----------------|------------|
| Share | ~70% | ~30% (growing) |
| Production cost | Low (phone photo + text) | Medium (needs shooting + editing) |
| Engagement rate | Medium | Higher (video more easily sparks comments) |
| Search weight | High (text content is indexed) | Medium (subtitles are indexed but lower weight) |
| Suitable content | List/guide/comparison/review | Unboxing/tutorial/usage demo/Vlog |
| AI assistance | AI generates copy + cover text | AI generates script + subtitles |

> **Suggestion**: A 7:3 ratio of image-text notes to video notes. Image-text notes for SEO and search traffic, video notes for recommendation traffic and interaction.

---

## 8.7 Xiaohongshu Data Analysis and Optimization

### Key Metric System

```
Xiaohongshu operations key metrics:

1. Note metrics
Exposure (Impressions)
Click rate (CTR) = clicks/exposure → measures cover + title appeal
Engagement rate = (likes + saves + comments + shares)/exposure → measures content quality
CES score = likes×1 + saves×1 + comments×4 + shares×4 + follows×8
Save rate = saves/exposure → measures how "worth-saving" the content is
Comment rate = comments/exposure → measures how "discussion-sparking" the content is

2. Account metrics
Follower growth (daily/weekly/monthly)
Follower persona (age/gender/region/interests)
Account weight (affects the initial exposure-pool size)
Content verticality (whether continuously posting the same category)

3. Conversion metrics (if you have a store)
Note → store click rate
Store browse → add-to-cart rate
Add-to-cart → purchase rate
Order value and ROI
```

### AI Monthly Retrospective Prompt

```
You are a Xiaohongshu data-analysis expert.

Here is my Xiaohongshu account's data for this month:

Account data:
- Follower count: [X] (this month +[X])
- Notes published: [X]
- Total exposure: [X]
- Average engagement rate: [X]%

This month's Top 5 notes:
| Title | Type | Exposure | Likes | Saves | Comments | CES |
[paste data]

This month's Bottom 5 notes:
| Title | Type | Exposure | Likes | Saves | Comments | CES |
[paste data]

Please analyze:
1. This month's overall performance assessment (compared with last month)
2. Common characteristics of viral notes (title/cover/content type/posting time)
3. Problem diagnosis of low-efficiency notes
4. Content-strategy adjustment suggestions
5. Next month's 8 note topics (based on data trends and seasonality)
6. KOL/KOC collaboration-effect assessment (if any)
7. Risks to watch (like engagement rate dropping, follower growth slowing)
```

---

## 9. Completion Checklist

- [ ] Complete Xiaohongshu account positioning and setup
- [ ] Use AI to batch-generate 10+ seeding notes
- [ ] Build a keyword library and SEO optimization process
- [ ] Create and execute a KOL/KOC collaboration plan
- [ ] Use AI to analyze note data and optimize the strategy
