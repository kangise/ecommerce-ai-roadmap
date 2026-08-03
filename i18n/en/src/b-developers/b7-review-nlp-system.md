# B7. Review Intelligence System: NLP + Topic Modeling + Sentiment Analysis

> **Track**: Path B: Developers · **Module**: B7
> **Last updated**: 2026-07-31
> **Level**: Intermediate
> **Time**: 1 hour a day, 2 weeks
> **Prerequisite**: [B1 Data Collection & Processing](b1-data-pipeline.md)


---

## Chapter Navigation

1. [Why you need a Review NLP system](#1-why-you-need-a-review-nlp-system) · 2. [Tech-stack choice](#2-tech-stack-choice) · 3. [Data collection & preprocessing](#3-data-collection--preprocessing) · 4. [Sentiment analysis in practice](#4-sentiment-analysis-in-practice) · 5. [BERTopic topic modeling](#5-bertopic-topic-modeling) · 6. [LLM-enhanced analysis](#6-llm-enhanced-analysis) · 7. [Build a complete pipeline](#7-build-a-complete-pipeline) · 8. [Common Traps](#8-common-traps) · 9. [Completion checklist](#9-completion-checklist)

---

## What You'll Build

- An Amazon Review auto-collection and cleaning pipeline
- A BERT-based sentiment-analysis model (positive/negative/neutral)
- A BERTopic topic-modeling system (auto-discover core topics in Reviews)
- An LLM-enhanced Review-insight generator (from data to executable advice)
- A complete Review-analysis dashboard

> **Core idea**: Reviews are e-commerce's most valuable unstructured data. The traditional method is reading by hand; the AI method is auto-extracting topics, sentiment, and executable insights. A good Review NLP system can guide product research, improve products, optimize Listings, and prevent negatives.

---

## 1. Why You Need a Review NLP System

### 1.1 The value of Review data

| Application scenario | Input | Output | Business value |
|----------------------|-------|--------|----------------|
| Product-research validation | competitor Reviews | user-pain-point ranking | find a differentiation direction |
| Product improvement | your own negatives | problem categories + frequency | prioritize the highest-frequency problem |
| Listing optimization | positive-review keywords | the selling points users value most | title/Bullet optimization |
| Ad optimization | high-frequency Review words | user search intent | ad-keyword expansion |
| CS prevention | negative-review trends | early warning | intervene before negatives explode |
| Competitor monitoring | competitor-Review changes | competitor problem/advantage changes | competitive-strategy adjustment |

### 1.2 Human vs AI analysis comparison

| Dimension | Reading by hand | AI NLP analysis |
|-----------|-----------------|-----------------|
| Speed | 100/hour | 10,000/minute |
| Consistency | subjective, differs by person | objective and consistent |
| Coverage | usually only the latest/worst | full analysis |
| Depth | surface understanding | topic clustering + sentiment quantification + trend analysis |
| Cost | high (labor time) | low (develop once, use continuously) |

---

## 2. Tech-Stack Choice

### 2.1 Recommended tech stack

```
Review NLP system tech stack:

Data layer:
pandas data processing
SP-API / scraper Review collection
SQLite / PostgreSQL data storage

NLP layer:
transformers (HuggingFace) BERT models
BERTopic topic modeling
sentence-transformers text embedding
TextBlob / VADER quick sentiment analysis (lightweight)
spaCy text preprocessing

LLM-enhancement layer:
OpenAI API / Claude API deep analysis
local LLM (Ollama) privacy-sensitive scenarios

Visualization layer:
Streamlit interactive dashboard
matplotlib / plotly charts
wordcloud word clouds
```

### 2.2 Dependency installation

```bash
# Core dependencies
pip3 install pandas numpy
pip3 install transformers torch sentence-transformers
pip3 install bertopic
pip3 install textblob vaderSentiment
pip3 install spacy
python3 -m spacy download en_core_web_sm

# Visualization
pip3 install streamlit plotly wordcloud matplotlib

# LLM (optional)
pip3 install openai anthropic
```

---

## 3. Data Collection & Preprocessing

### 3.1 Ways to get Review data

| Method | Pros | Cons | Best for |
|--------|------|------|----------|
| Amazon SP-API | official API, stable and compliant | can only get your own products' Reviews | own-product analysis |
| Web scraping | can get competitor Reviews | needs anti-scraping handling, compliance risk | competitor analysis |
| Third-party tool export | simple and fast | inconsistent data format | quick analysis |
| Public dataset | free, plentiful | data may be outdated | learning and testing |

> **Real resources**: several tutorials show how to scrape Amazon Review data with Python, using BeautifulSoup, Scrapy, and professional API services ([ScrapingBee](https://www.scrapingbee.com/blog/how-to-scrape-amazon-reviews/), [Oxylabs](https://oxylabs.io/blog/how-to-scrape-amazon-reviews)). Scraped data usually includes rating, title, body, date, verified-purchase status, and helpful-vote count.

Content rephrased for compliance with licensing restrictions.

> **Real case: cross-product Review analysis**
> Academic research shows using Contextual Topic Modeling and association-rule mining to do cross-product analysis of Amazon Reviews in the headphone category, discovering shared user concerns and differentiating features across products ([MDPI](https://www.mdpi.com/0718-1876/19/4/170)).

Content rephrased for compliance with licensing restrictions.

### 3.2 Review data structure

```python
import pandas as pd

# Review data standard format
review_schema = {
"asin": str, # product ASIN
"rating": int, # 1-5 stars
"title": str, # Review title
"body": str, # Review body
"date": str, # date
"verified": bool, # verified purchase or not
"helpful_votes": int, # helpful-vote count
"marketplace": str # marketplace (US/UK/DE/JP)
}
```

### 3.2 Data-cleaning pipeline

```python
import re
import spacy

nlp = spacy.load("en_core_web_sm")

def clean_review(text: str) -> str:
"""Clean the Review text"""
if not text or not isinstance(text, str):
return ""

# Remove HTML tags
text = re.sub(r'<[^>]+>', '', text)
# Remove URLs
text = re.sub(r'http\S+', '', text)
# Remove extra whitespace
text = re.sub(r'\s+', ' ', text).strip()

return text

def preprocess_reviews(df: pd.DataFrame) -> pd.DataFrame:
"""Preprocess the Review DataFrame"""
# Clean text
df['clean_body'] = df['body'].apply(clean_review)
df['clean_title'] = df['title'].apply(clean_review)

# Merge title and body
df['full_text'] = df['clean_title'] + '. ' + df['clean_body']

# Filter empty text
df = df[df['full_text'].str.len() > 10]

# Tag sentiment labels (rough classification based on star rating)
df['sentiment_label'] = df['rating'].map({
1: 'negative', 2: 'negative',
3: 'neutral',
4: 'positive', 5: 'positive'
})

return df
```

---

## 4. Sentiment Analysis in Practice

### 4.1 Method comparison

| Method | Accuracy | Speed | Cost | Best for |
|--------|----------|-------|------|----------|
| VADER | medium (70–75%) | extremely fast | free | quick screening, large data |
| TextBlob | medium (70–75%) | extremely fast | free | simple scenarios |
| DistilBERT | high (85–90%) | medium | free (local) | precise analysis |
| GPT/Claude API | highest (90%+) | slow | paid | small-volume high-value analysis |

### 4.2 VADER quick sentiment analysis

```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def vader_sentiment(text: str) -> dict:
"""VADER sentiment analysis (good for English Reviews)"""
scores = analyzer.polarity_scores(text)

# Judge the sentiment
if scores['compound'] >= 0.05:
label = 'positive'
elif scores['compound'] <= -0.05:
label = 'negative'
else:
label = 'neutral'

return {
'label': label,
'score': scores['compound'],
'positive': scores['pos'],
'negative': scores['neg'],
'neutral': scores['neu']
}

# Batch analysis
df['vader'] = df['full_text'].apply(vader_sentiment)
df['vader_label'] = df['vader'].apply(lambda x: x['label'])
df['vader_score'] = df['vader'].apply(lambda x: x['score'])
```

### 4.3 DistilBERT deep sentiment analysis

```python
from transformers import pipeline

# Load a pre-trained sentiment-analysis model
sentiment_pipeline = pipeline(
"sentiment-analysis",
model="distilbert-base-uncased-finetuned-sst-2-english",
device=0 # GPU; use -1 if no GPU
)

def bert_sentiment(texts: list, batch_size: int = 32) -> list:
"""Batch BERT sentiment analysis"""
results = sentiment_pipeline(texts, batch_size=batch_size, truncation=True)
return [
{
'label': r['label'].lower(),
'score': r['score'] if r['label'] == 'POSITIVE' else -r['score']
}
for r in results
]

# Batch processing (10x faster than one by one)
texts = df['full_text'].tolist()
sentiments = bert_sentiment(texts)
df['bert_label'] = [s['label'] for s in sentiments]
df['bert_score'] = [s['score'] for s in sentiments]
```

> **Real case**: academic research shows BERT-based sentiment analysis can reach 90%+ accuracy on Amazon Review datasets, significantly outperforming traditional machine-learning methods ([MDPI](https://www.mdpi.com/1999-5903/18/3/138)). BERTopic combined with Amazon Review data can auto-discover a product's core topics and user concerns ([Amalytix](https://www.amalytix.com/en/blog/analyze-reviews-bertopic/)).

Content rephrased for compliance with licensing restrictions.

---

## 5. BERTopic Topic Modeling

### 5.1 BERTopic core concepts

BERTopic uses BERT embeddings + UMAP dimensionality reduction + HDBSCAN clustering to auto-discover topics in text.

```python
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

# Use a lightweight embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Create the BERTopic model
topic_model = BERTopic(
embedding_model=embedding_model,
nr_topics="auto", # auto-determine the number of topics
min_topic_size=10, # minimum topic size
language="english",
verbose=True
)

# Train the model
topics, probs = topic_model.fit_transform(df['full_text'].tolist())

# View topics
topic_info = topic_model.get_topic_info()
print(topic_info.head(20))

# View each topic's keywords
for topic_id in range(min(10, len(topic_info))):
print(f"\nTopic {topic_id}:")
print(topic_model.get_topic(topic_id))
```

### 5.2 Negative-review dedicated topic analysis

```python
# Analyze only negatives (1-2 stars)
negative_reviews = df[df['rating'] <= 2]['full_text'].tolist()

negative_topic_model = BERTopic(
embedding_model=embedding_model,
nr_topics=10, # limit the number of topics
min_topic_size=5,
language="english"
)

neg_topics, neg_probs = negative_topic_model.fit_transform(negative_reviews)

# Negative-topic ranking (by frequency)
neg_topic_info = negative_topic_model.get_topic_info()
print("=== Top 10 core negative-review problems ===")
for _, row in neg_topic_info.head(10).iterrows():
print(f"Topic {row['Topic']}: {row['Name']} ({row['Count']} reviews)")
```

### 5.3 Topic-trend analysis

```python
# Analyze topics over time
topics_over_time = topic_model.topics_over_time(
df['full_text'].tolist(),
df['date'].tolist()
)

# Visualize
fig = topic_model.visualize_topics_over_time(topics_over_time)
fig.show()

# Discover: are negatives about a certain quality issue increasing?
# This can be an early-warning signal for product improvement
```

### 5.4 Advanced BERTopic techniques

> **Real case: Amalytix's Amazon Review BERTopic analysis**
> Amalytix showed how to analyze Amazon Reviews with BERTopic, auto-discovering a product's core topics. BERTopic uses a BERT-based approach and a modified TF-IDF analysis to extract meaningful topic clusters from unstructured Review text ([Amalytix](https://www.amalytix.com/en/blog/analyze-reviews-bertopic/)).

Content rephrased for compliance with licensing restrictions.

```python
# Advanced technique 1: topic analysis grouped by category
def analyze_by_category(df: pd.DataFrame, categories: list):
"""Do topic analysis per category, discovering category-specific problems"""
results = {}
for cat in categories:
cat_df = df[df['category'] == cat]
if len(cat_df) < 50:
continue

model = BERTopic(
embedding_model=embedding_model,
nr_topics=8,
min_topic_size=5
)
topics, _ = model.fit_transform(cat_df['full_text'].tolist())
results[cat] = {
'model': model,
'topics': model.get_topic_info(),
'negative_topics': cat_df[cat_df['rating'] <= 2].groupby(
pd.Series(topics)[cat_df['rating'] <= 2].values
).size().sort_values(ascending=False)
}
return results

# Advanced technique 2: multilingual Review analysis
from sentence_transformers import SentenceTransformer

# Use a multilingual embedding model (supports 100+ languages)
multilingual_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

multilingual_topic_model = BERTopic(
embedding_model=multilingual_model,
language="multilingual"
)

# Can analyze English, German, and Japanese Reviews at once
all_reviews = pd.concat([us_reviews, de_reviews, jp_reviews])
topics, _ = multilingual_topic_model.fit_transform(all_reviews['full_text'].tolist())

# Advanced technique 3: auto-generate topic labels (with an LLM)
def auto_label_topics(topic_model, top_n_topics=20):
"""Use an LLM to generate human-readable labels for BERTopic-discovered topics"""
labels = {}
for topic_id in range(top_n_topics):
keywords = topic_model.get_topic(topic_id)
if not keywords:
continue

keyword_str = ", ".join([w for w, _ in keywords[:10]])

prompt = f"""
Here are the keywords of a topic extracted from product Reviews:
{keyword_str}

Describe this topic with a short label (3-6 words).
Return only the label, no explanation.
"""
label = llm_call(prompt).strip()
labels[topic_id] = label

return labels

# Advanced technique 4: Review quality scoring
def score_review_quality(df: pd.DataFrame) -> pd.DataFrame:
"""Assess a Review's information quality (to filter high-value Reviews)"""
df['word_count'] = df['full_text'].str.split().str.len()
df['has_specific_detail'] = df['full_text'].str.contains(
r'\d+\s*(day|week|month|hour|minute|inch|cm|kg|lb|oz)',
case=False, regex=True
)
df['has_comparison'] = df['full_text'].str.contains(
r'(better than|worse than|compared to|vs|versus|unlike)',
case=False, regex=True
)
df['quality_score'] = (
(df['word_count'] > 30).astype(int) * 2 +
df['has_specific_detail'].astype(int) * 3 +
df['has_comparison'].astype(int) * 3 +
(df['helpful_votes'] > 0).astype(int) * 2
)
return df
```

---

## 6. LLM-Enhanced Analysis

### 6.1 Generate executable insights with an LLM

BERTopic discovers topics, and the LLM interprets them and generates advice:

```python
import anthropic # or openai

client = anthropic.Anthropic()

def generate_review_insights(topic_info: dict, sample_reviews: list) -> str:
"""Use an LLM to generate executable insights from Review topics"""
prompt = f"""
You are an e-commerce product-analysis expert. Below is the NLP-analysis result of Amazon Reviews.

Product: [product name]
Total Reviews analyzed: {topic_info['total_reviews']}
Time range: {topic_info['date_range']}

Negative-topic ranking (by frequency):
{topic_info['negative_topics']}

Positive-topic ranking:
{topic_info['positive_topics']}

Negative-review samples (3 per topic):
{sample_reviews}

Generate:
1. Core-problem ranking (by severity and frequency)
2. Concrete improvement advice per problem
3. The 3 selling points users value most (for Listing optimization)
4. Competitor-differentiation opportunities (based on unmet user needs)
5. Warning signals (which problems are worsening?)
6. Prioritized action list (do the highest-ROI improvements first)
"""

response = client.messages.create(
model="claude-sonnet-4-20250514",
max_tokens=2000,
messages=[{"role": "user", "content": prompt}]
)

return response.content[0].text
```

### 6.2 Competitor-Review comparison analysis

```python
def competitive_review_analysis(my_reviews: pd.DataFrame,
competitor_reviews: pd.DataFrame) -> str:
"""Compare your own and competitor Review topics"""

# Do topic modeling separately
my_topics = run_bertopic(my_reviews)
comp_topics = run_bertopic(competitor_reviews)

# Comparative analysis with an LLM
prompt = f"""
Compare the Review-analysis results of two products:

My product:
- Average rating: {my_reviews['rating'].mean():.1f}
- Negative topics: {my_topics['negative']}
- Positive topics: {my_topics['positive']}

Competitor:
- Average rating: {competitor_reviews['rating'].mean():.1f}
- Negative topics: {comp_topics['negative']}
- Positive topics: {comp_topics['positive']}

Analyze:
1. My product's advantages and disadvantages vs the competitor
2. Which of the competitor's negatives are opportunities I can leverage
3. Which of my negatives has the competitor already solved
4. Differentiation-positioning advice
"""
return llm_call(prompt)
```

---

## 7. Build a Complete Pipeline

### 7.1 End-to-end Review-analysis pipeline

```python
class ReviewAnalysisPipeline:
"""A complete Review-analysis pipeline"""

def __init__(self, embedding_model="all-MiniLM-L6-v2"):
self.embedding_model = SentenceTransformer(embedding_model)
self.sentiment_pipeline = pipeline(
"sentiment-analysis",
model="distilbert-base-uncased-finetuned-sst-2-english"
)
self.topic_model = None

def run(self, reviews_df: pd.DataFrame) -> dict:
"""Run the full analysis"""
# Step 1: preprocess
df = preprocess_reviews(reviews_df)

# Step 2: sentiment analysis
sentiments = self.sentiment_pipeline(
df['full_text'].tolist(),
batch_size=32, truncation=True
)
df['sentiment'] = [s['label'].lower() for s in sentiments]

# Step 3: topic modeling
self.topic_model = BERTopic(
embedding_model=self.embedding_model,
nr_topics="auto",
min_topic_size=5
)
topics, _ = self.topic_model.fit_transform(df['full_text'].tolist())
df['topic'] = topics

# Step 4: aggregate
results = {
'total_reviews': len(df),
'avg_rating': df['rating'].mean(),
'sentiment_dist': df['sentiment'].value_counts().to_dict(),
'rating_dist': df['rating'].value_counts().to_dict(),
'topics': self.topic_model.get_topic_info().to_dict(),
'negative_topics': self._get_negative_topics(df),
'positive_topics': self._get_positive_topics(df),
'trends': self._get_trends(df)
}

# Step 5: LLM insights
results['insights'] = generate_review_insights(results,
df[df['rating'] <= 2].sample(min(15, len(df[df['rating'] <= 2])))
)

return results

def _get_negative_topics(self, df):
neg = df[df['rating'] <= 2]
return neg.groupby('topic').size().sort_values(ascending=False).head(10)

def _get_positive_topics(self, df):
pos = df[df['rating'] >= 4]
return pos.groupby('topic').size().sort_values(ascending=False).head(10)

def _get_trends(self, df):
df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
return df.groupby('month')['rating'].mean()
```

### 7.2 Streamlit dashboard (full implementation)

```python
# review_dashboard.py — Review Intelligence dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

st.set_page_config(page_title="Review Intelligence", layout="wide")
st.title("Review Intelligence System")

# === Sidebar ===
with st.sidebar:
st.header("Data upload")
uploaded_file = st.file_uploader("Upload a Review CSV", type="csv")

if uploaded_file:
st.header("Analysis settings")
min_rating = st.slider("Min rating filter", 1, 5, 1)
max_rating = st.slider("Max rating filter", 1, 5, 5)
num_topics = st.slider("Number of topics", 5, 30, 10)
analysis_type = st.selectbox(
"Analysis type",
["All Reviews", "Negatives only (1-2 stars)", "Positives only (4-5 stars)", "Neutral (3 stars)"]
)

if uploaded_file:
df = pd.read_csv(uploaded_file)
df = preprocess_reviews(df)

# Filter
df_filtered = df[(df['rating'] >= min_rating) & (df['rating'] <= max_rating)]

# === Tab 1: overview ===
tab1, tab2, tab3, tab4, tab5 = st.tabs([
"Overview", "Sentiment analysis", "Topic modeling", "Trends", "AI insights"
])

with tab1:
# KPI cards
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Reviews", f"{len(df_filtered):,}")
col2.metric("Average rating", f"{df_filtered['rating'].mean():.2f}")
col3.metric("Negative rate", f"{(df_filtered['rating'] <= 2).mean()*100:.1f}%")
col4.metric("Positive rate", f"{(df_filtered['rating'] >= 4).mean()*100:.1f}%")
col5.metric("Verified purchase", f"{df_filtered['verified'].mean()*100:.0f}%")

# Rating distribution
col1, col2 = st.columns(2)
with col1:
rating_dist = df_filtered['rating'].value_counts().sort_index()
fig = px.bar(x=rating_dist.index, y=rating_dist.values,
labels={'x': 'Rating', 'y': 'Count'},
title="Rating distribution",
color=rating_dist.index,
color_continuous_scale=['red', 'orange', 'yellow', 'lightgreen', 'green'])
st.plotly_chart(fig, use_container_width=True)

with col2:
# Word cloud
all_text = ' '.join(df_filtered['full_text'].tolist())
wc = WordCloud(width=800, height=400, background_color='white',
max_words=100, colormap='viridis').generate(all_text)
fig_wc, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wc, interpolation='bilinear')
ax.axis('off')
st.pyplot(fig_wc)

with tab2:
st.subheader("Sentiment analysis")

# Run sentiment analysis
with st.spinner("Analyzing sentiment..."):
sentiments = bert_sentiment(df_filtered['full_text'].tolist())
df_filtered['sentiment'] = [s['label'] for s in sentiments]
df_filtered['sentiment_score'] = [s['score'] for s in sentiments]

# Sentiment distribution
col1, col2 = st.columns(2)
with col1:
sent_dist = df_filtered['sentiment'].value_counts()
fig = px.pie(values=sent_dist.values, names=sent_dist.index,
title="Sentiment distribution",
color_discrete_map={'positive': 'green', 'negative': 'red', 'neutral': 'gray'})
st.plotly_chart(fig, use_container_width=True)

with col2:
# Sentiment vs rating relationship
fig = px.box(df_filtered, x='rating', y='sentiment_score',
title="Sentiment score vs rating",
labels={'rating': 'Rating', 'sentiment_score': 'Sentiment score'})
st.plotly_chart(fig, use_container_width=True)

# The most extreme Reviews by sentiment
st.subheader("Most positive Reviews")
top_positive = df_filtered.nlargest(3, 'sentiment_score')
for _, row in top_positive.iterrows():
st.success(f"{row['rating']} | {row['full_text'][:200]}...")

st.subheader("Most negative Reviews")
top_negative = df_filtered.nsmallest(3, 'sentiment_score')
for _, row in top_negative.iterrows():
st.error(f"{row['rating']} | {row['full_text'][:200]}...")

with tab3:
st.subheader("Topic modeling (BERTopic)")

with st.spinner("Extracting topics..."):
topic_model = BERTopic(
embedding_model=embedding_model,
nr_topics=num_topics,
min_topic_size=5
)
topics, probs = topic_model.fit_transform(df_filtered['full_text'].tolist())
df_filtered['topic'] = topics

# Topic overview
topic_info = topic_model.get_topic_info()
st.dataframe(topic_info[['Topic', 'Count', 'Name']].head(20),
use_container_width=True)

# Topic visualization
try:
fig = topic_model.visualize_barchart(top_n_topics=10)
st.plotly_chart(fig, use_container_width=True)
except:
pass

# Negative-review dedicated topics
st.subheader("Core negative-review problems")
neg_df = df_filtered[df_filtered['rating'] <= 2]
if len(neg_df) > 10:
neg_topic_counts = neg_df.groupby('topic').size().sort_values(ascending=False)
for topic_id in neg_topic_counts.head(5).index:
if topic_id == -1:
continue
keywords = topic_model.get_topic(topic_id)
keyword_str = ", ".join([w for w, _ in keywords[:5]])
count = neg_topic_counts[topic_id]
st.warning(f"**Topic {topic_id}** ({count} negatives): {keyword_str}")

# Show example Reviews for this topic
examples = neg_df[neg_df['topic'] == topic_id]['full_text'].head(2)
for ex in examples:
st.caption(f" → {ex[:150]}...")

with tab4:
st.subheader("Trend analysis")

df_filtered['month'] = pd.to_datetime(df_filtered['date']).dt.to_period('M').astype(str)

# Monthly rating trend
monthly = df_filtered.groupby('month').agg({
'rating': 'mean',
'full_text': 'count'
}).reset_index()
monthly.columns = ['Month', 'Average rating', 'Review count']

fig = go.Figure()
fig.add_trace(go.Bar(x=monthly['Month'], y=monthly['Review count'], name='Review count'))
fig.add_trace(go.Scatter(x=monthly['Month'], y=monthly['Average rating'],
name='Average rating', yaxis='y2', mode='lines+markers'))
fig.update_layout(
title="Monthly Review trend",
yaxis=dict(title='Review count'),
yaxis2=dict(title='Average rating', overlaying='y', side='right', range=[1, 5])
)
st.plotly_chart(fig, use_container_width=True)

with tab5:
st.subheader("AI insights")

if st.button("Generate AI analysis report"):
with st.spinner("AI is analyzing..."):
insights = generate_review_insights({
'total_reviews': len(df_filtered),
'avg_rating': df_filtered['rating'].mean(),
'negative_topics': str(neg_topic_counts.head(5).to_dict()) if 'neg_topic_counts' in dir() else "N/A",
'positive_topics': "N/A",
'date_range': f"{df_filtered['date'].min()} to {df_filtered['date'].max()}"
}, df_filtered[df_filtered['rating'] <= 2].head(10).to_dict())

st.markdown(insights)

# Download the report
st.download_button(
"Download the analysis report",
insights,
file_name=f"review_analysis_{datetime.now().strftime('%Y%m%d')}.md",
mime="text/markdown"
)

else:
st.info("Please upload a Review CSV file on the left to start analysis")
st.markdown("""
**CSV file format requirements:**
- `rating`: rating (1-5)
- `title`: Review title
- `body`: Review body
- `date`: date
- `verified`: verified purchase (True/False)
- `helpful_votes`: helpful-vote count (optional)
""")
```

Run: `streamlit run review_dashboard.py`

### 7.3 Export analysis results

```python
def export_analysis_results(df: pd.DataFrame, topic_model, output_dir: str = "output"):
"""Export the complete analysis results"""
from pathlib import Path
Path(output_dir).mkdir(exist_ok=True)

# 1. Export the annotated Review data
df.to_csv(f"{output_dir}/reviews_analyzed.csv", index=False)

# 2. Export the topic summary
topic_info = topic_model.get_topic_info()
topic_info.to_csv(f"{output_dir}/topics_summary.csv", index=False)

# 3. Export negative-topic details
neg_df = df[df['rating'] <= 2]
neg_topics = neg_df.groupby('topic').agg({
'full_text': 'count',
'rating': 'mean'
}).sort_values('full_text', ascending=False)
neg_topics.to_csv(f"{output_dir}/negative_topics.csv")

# 4. Generate an HTML report
html_report = topic_model.visualize_topics()
html_report.write_html(f"{output_dir}/topic_visualization.html")

print(f"Analysis results exported to {output_dir}/")
```

---

## 8. Common Traps

### 8.1 Substituting sentiment polarity for problem localization

Knowing 30% is negative carries no action. What's useful is "of the negatives, how much is shipping, how much is quality, how much is expectation mismatch" — the taxonomy has to map to actions you can take.

### 8.2 Ignoring language and market differences

The distribution of complaints for the same product varies widely by market; mixing them dilutes both. Run per marketplace.

### 8.3 Concluding on too small a sample

Three mentions of a complaint across 20 reviews could be noise or signal. Set a minimum sample threshold so anecdotes don't drive product decisions.

### 8.4 Analyzing only the negatives

Five-star reviews contain what customers actually value — which is what your listing copy should say. Reading only the negatives keeps you patching weaknesses without knowing your strengths.

---

## 9. Completion Checklist

- [ ] Built a Review-collection and cleaning pipeline
- [ ] Implemented a two-layer VADER + BERT sentiment analysis
- [ ] Did topic modeling on at least 1000 Reviews with BERTopic
- [ ] Generated an executable Review-insight report with an LLM
- [ ] Built a Streamlit dashboard to display the analysis results
- [ ] Completed one competitor-Review comparison analysis

[< B6 MCP Integration](b6-mcp-agentic-workflow.md) | [Path overview](../README.md) | [B8 Dashboard >](b8-ecommerce-dashboard.md)
