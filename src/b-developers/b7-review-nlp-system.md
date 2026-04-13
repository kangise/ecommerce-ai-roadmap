# B7. Review 智能分析系统：NLP + 主题建模 + 情感分析

> **路径**: Path B: 技术人 · **模块**: B7
> **最后更新**: 2026-03-15
> **难度**: 中级
> **预计时间**: 每天 1 小时，2 周
> **前置模块**: [B1 数据采集与处理](b1-data-pipeline.md)


---

## 章节导航

1. [为什么需要 Review NLP 系统](#1-为什么需要-review-nlp-系统) · 2. [技术栈选择](#2-技术栈选择) · 3. [数据采集与预处理](#3-数据采集与预处理) · 4. [情感分析实战](#4-情感分析实战) · 5. [BERTopic 主题建模](#5-bertopic-主题建模) · 6. [LLM 增强分析](#6-llm-增强分析) · 7. [构建完整 Pipeline](#7-构建完整-pipeline) · 8. [完成标志](#8-完成标志)

---

## 本模块你将构建

- 一个 Amazon Review 自动采集和清洗 Pipeline
- 一个基于 BERT 的情感分析模型（正面/负面/中性）
- 一个 BERTopic 主题建模系统（自动发现 Review 中的核心话题）
- 一个 LLM 增强的 Review 洞察生成器（从数据到可执行建议）
- 一个完整的 Review 分析 Dashboard

> **核心理念**：Review 是电商最有价值的非结构化数据。传统方法是人工阅读，AI 方法是自动提取主题、情感和可执行洞察。一个好的 Review NLP 系统可以指导选品、改进产品、优化 Listing、预防差评。

---

## 1. 为什么需要 Review NLP 系统

### 1.1 Review 数据的价值

| 应用场景 | 输入 | 输出 | 业务价值 |
|----------|------|------|----------|
| 选品验证 | 竞品 Review | 用户痛点排名 | 找到差异化方向 |
| 产品改进 | 自己的差评 | 问题分类+频率 | 优先修复最高频问题 |
| Listing 优化 | 好评关键词 | 用户最看重的卖点 | 标题/Bullet 优化 |
| 广告优化 | Review 高频词 | 用户搜索意图 | 广告关键词扩展 |
| 客服预防 | 差评趋势 | 早期预警 | 在差评爆发前介入 |
| 竞品监控 | 竞品 Review 变化 | 竞品问题/优势变化 | 竞争策略调整 |

### 1.2 人工 vs AI 分析对比

| 维度 | 人工阅读 | AI NLP 分析 |
|------|---------|------------|
| 速度 | 100 条/小时 | 10,000 条/分钟 |
| 一致性 | 主观判断，不同人结果不同 | 客观一致 |
| 覆盖度 | 通常只看最近/最差的 | 全量分析 |
| 深度 | 表面理解 | 主题聚类+情感量化+趋势分析 |
| 成本 | 高（人力时间） | 低（一次开发，持续使用） |

---

## 2. 技术栈选择

### 2.1 推荐技术栈

```
Review NLP 系统技术栈：

数据层：
pandas 数据处理
SP-API / 爬虫 Review 采集
SQLite / PostgreSQL 数据存储

NLP 层：
transformers (HuggingFace) BERT 模型
BERTopic 主题建模
sentence-transformers 文本向量化
TextBlob / VADER 快速情感分析（轻量）
spaCy 文本预处理

LLM 增强层：
OpenAI API / Claude API 深度分析
本地 LLM (Ollama) 隐私敏感场景

可视化层：
Streamlit 交互式 Dashboard
matplotlib / plotly 图表
wordcloud 词云
```

### 2.2 依赖安装

```bash
# 核心依赖
pip3 install pandas numpy
pip3 install transformers torch sentence-transformers
pip3 install bertopic
pip3 install textblob vaderSentiment
pip3 install spacy
python3 -m spacy download en_core_web_sm

# 可视化
pip3 install streamlit plotly wordcloud matplotlib

# LLM（可选）
pip3 install openai anthropic
```

---

## 3. 数据采集与预处理

### 3.1 Review 数据获取方式

| 方式 | 优点 | 缺点 | 适合 |
|------|------|------|------|
| Amazon SP-API | 官方 API，稳定合规 | 只能获取自己产品的 Review | 自有产品分析 |
| 网页抓取 | 可获取竞品 Review | 需要处理反爬、合规风险 | 竞品分析 |
| 第三方工具导出 | 简单快速 | 数据格式不统一 | 快速分析 |
| 公开数据集 | 免费、大量 | 数据可能过时 | 学习和测试 |

> **真实资源**：多个教程展示了如何用 Python 抓取 Amazon Review 数据，包括使用 BeautifulSoup、Scrapy 和专业 API 服务（[ScrapingBee](https://www.scrapingbee.com/blog/how-to-scrape-amazon-reviews/)，[Oxylabs](https://oxylabs.io/blog/how-to-scrape-amazon-reviews)）。抓取的数据通常包含评分、标题、正文、日期、验证购买状态和有用投票数。

Content rephrased for compliance with licensing restrictions.

> **真实案例：跨产品 Review 分析**
> 学术研究展示了使用上下文主题建模（Contextual Topic Modeling）和关联规则挖掘对耳机品类的 Amazon Review 进行跨产品分析，发现不同产品之间共享的用户关注点和差异化特征（[MDPI](https://www.mdpi.com/0718-1876/19/4/170)）。

Content rephrased for compliance with licensing restrictions.

### 3.2 Review 数据结构

```python
import pandas as pd

# Review 数据标准格式
review_schema = {
"asin": str, # 产品 ASIN
"rating": int, # 1-5 星
"title": str, # Review 标题
"body": str, # Review 正文
"date": str, # 日期
"verified": bool, # 是否验证购买
"helpful_votes": int, # 有用投票数
"marketplace": str # 市场（US/UK/DE/JP）
}
```

### 3.2 数据清洗 Pipeline

```python
import re
import spacy

nlp = spacy.load("en_core_web_sm")

def clean_review(text: str) -> str:
"""清洗 Review 文本"""
if not text or not isinstance(text, str):
return ""

# 移除 HTML 标签
text = re.sub(r'<[^>]+>', '', text)
# 移除 URL
text = re.sub(r'http\S+', '', text)
# 移除多余空白
text = re.sub(r'\s+', ' ', text).strip()

return text

def preprocess_reviews(df: pd.DataFrame) -> pd.DataFrame:
"""预处理 Review DataFrame"""
# 清洗文本
df['clean_body'] = df['body'].apply(clean_review)
df['clean_title'] = df['title'].apply(clean_review)

# 合并标题和正文
df['full_text'] = df['clean_title'] + '. ' + df['clean_body']

# 过滤空文本
df = df[df['full_text'].str.len() > 10]

# 标记情感标签（基于星级的粗略分类）
df['sentiment_label'] = df['rating'].map({
1: 'negative', 2: 'negative',
3: 'neutral',
4: 'positive', 5: 'positive'
})

return df
```

---

## 4. 情感分析实战

### 4.1 方法对比

| 方法 | 准确度 | 速度 | 成本 | 适合 |
|------|--------|------|------|------|
| VADER | 中等（70-75%） | 极快 | 免费 | 快速筛选、大量数据 |
| TextBlob | 中等（70-75%） | 极快 | 免费 | 简单场景 |
| DistilBERT | 高（85-90%） | 中等 | 免费（本地） | 精确分析 |
| GPT/Claude API | 最高（90%+） | 慢 | 付费 | 小量高价值分析 |

### 4.2 VADER 快速情感分析

```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def vader_sentiment(text: str) -> dict:
"""VADER 情感分析（适合英文 Review）"""
scores = analyzer.polarity_scores(text)

# 判断情感
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

# 批量分析
df['vader'] = df['full_text'].apply(vader_sentiment)
df['vader_label'] = df['vader'].apply(lambda x: x['label'])
df['vader_score'] = df['vader'].apply(lambda x: x['score'])
```

### 4.3 DistilBERT 深度情感分析

```python
from transformers import pipeline

# 加载预训练情感分析模型
sentiment_pipeline = pipeline(
"sentiment-analysis",
model="distilbert-base-uncased-finetuned-sst-2-english",
device=0 # GPU，如果没有 GPU 用 -1
)

def bert_sentiment(texts: list, batch_size: int = 32) -> list:
"""批量 BERT 情感分析"""
results = sentiment_pipeline(texts, batch_size=batch_size, truncation=True)
return [
{
'label': r['label'].lower(),
'score': r['score'] if r['label'] == 'POSITIVE' else -r['score']
}
for r in results
]

# 批量处理（比逐条快 10x）
texts = df['full_text'].tolist()
sentiments = bert_sentiment(texts)
df['bert_label'] = [s['label'] for s in sentiments]
df['bert_score'] = [s['score'] for s in sentiments]
```

> **真实案例**：学术研究表明，基于 BERT 的情感分析在 Amazon Review 数据集上可以达到 90%+ 的准确率，显著优于传统机器学习方法（[MDPI](https://www.mdpi.com/1999-5903/18/3/138)）。BERTopic 结合 Amazon Review 数据可以自动发现产品的核心话题和用户关注点（[Amalytix](https://www.amalytix.com/en/blog/analyze-reviews-bertopic/)）。

Content rephrased for compliance with licensing restrictions.

---

## 5. BERTopic 主题建模

### 5.1 BERTopic 核心概念

BERTopic 使用 BERT 嵌入 + UMAP 降维 + HDBSCAN 聚类来自动发现文本中的主题。

```python
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

# 使用轻量级嵌入模型
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 创建 BERTopic 模型
topic_model = BERTopic(
embedding_model=embedding_model,
nr_topics="auto", # 自动确定主题数
min_topic_size=10, # 最小主题大小
language="english",
verbose=True
)

# 训练模型
topics, probs = topic_model.fit_transform(df['full_text'].tolist())

# 查看主题
topic_info = topic_model.get_topic_info()
print(topic_info.head(20))

# 查看每个主题的关键词
for topic_id in range(min(10, len(topic_info))):
print(f"\nTopic {topic_id}:")
print(topic_model.get_topic(topic_id))
```

### 5.2 差评专项主题分析

```python
# 只分析差评（1-2 星）的主题
negative_reviews = df[df['rating'] <= 2]['full_text'].tolist()

negative_topic_model = BERTopic(
embedding_model=embedding_model,
nr_topics=10, # 限制主题数
min_topic_size=5,
language="english"
)

neg_topics, neg_probs = negative_topic_model.fit_transform(negative_reviews)

# 差评主题排名（按频率）
neg_topic_info = negative_topic_model.get_topic_info()
print("=== 差评核心问题 TOP 10 ===")
for _, row in neg_topic_info.head(10).iterrows():
print(f"Topic {row['Topic']}: {row['Name']} ({row['Count']} reviews)")
```

### 5.3 主题趋势分析

```python
# 分析主题随时间的变化
topics_over_time = topic_model.topics_over_time(
df['full_text'].tolist(),
df['date'].tolist()
)

# 可视化
fig = topic_model.visualize_topics_over_time(topics_over_time)
fig.show()

# 发现：某个质量问题的差评是否在增加？
# 这可以作为产品改进的早期预警信号
```

### 5.4 高级 BERTopic 技巧

> **真实案例：Amalytix 的 Amazon Review BERTopic 分析**
> Amalytix 展示了如何用 BERTopic 分析 Amazon Review，自动发现产品的核心话题。BERTopic 使用基于 BERT 的方法和修改后的 TF-IDF 分析，能够从非结构化的 Review 文本中提取有意义的主题聚类（[Amalytix](https://www.amalytix.com/en/blog/analyze-reviews-bertopic/)）。

Content rephrased for compliance with licensing restrictions.

```python
# 高级技巧 1：按品类分组的主题分析
def analyze_by_category(df: pd.DataFrame, categories: list):
"""按品类分别做主题分析，发现品类特有的问题"""
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

# 高级技巧 2：多语言 Review 分析
from sentence_transformers import SentenceTransformer

# 使用多语言嵌入模型（支持 100+ 语言）
multilingual_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

multilingual_topic_model = BERTopic(
embedding_model=multilingual_model,
language="multilingual"
)

# 可以同时分析英语、德语、日语的 Review
all_reviews = pd.concat([us_reviews, de_reviews, jp_reviews])
topics, _ = multilingual_topic_model.fit_transform(all_reviews['full_text'].tolist())

# 高级技巧 3：主题标签自动生成（用 LLM）
def auto_label_topics(topic_model, top_n_topics=20):
"""用 LLM 为 BERTopic 发现的主题生成人类可读的标签"""
labels = {}
for topic_id in range(top_n_topics):
keywords = topic_model.get_topic(topic_id)
if not keywords:
continue

keyword_str = ", ".join([w for w, _ in keywords[:10]])

prompt = f"""
以下是从产品 Review 中提取的一个主题的关键词：
{keyword_str}

请用一个简短的中文标签（3-6 个字）描述这个主题。
只返回标签，不要解释。
"""
label = llm_call(prompt).strip()
labels[topic_id] = label

return labels

# 高级技巧 4：Review 质量评分
def score_review_quality(df: pd.DataFrame) -> pd.DataFrame:
"""评估 Review 的信息质量（用于筛选高价值 Review）"""
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

## 6. LLM 增强分析

### 6.1 用 LLM 生成可执行洞察

BERTopic 发现主题，LLM 解读主题并生成建议：

```python
import anthropic # 或 openai

client = anthropic.Anthropic()

def generate_review_insights(topic_info: dict, sample_reviews: list) -> str:
"""用 LLM 从 Review 主题生成可执行洞察"""
prompt = f"""
你是一个电商产品分析专家。以下是 Amazon Review 的 NLP 分析结果。

产品：[产品名]
分析的 Review 总数：{topic_info['total_reviews']}
时间范围：{topic_info['date_range']}

差评主题排名（按频率）：
{topic_info['negative_topics']}

好评主题排名：
{topic_info['positive_topics']}

差评样本（每个主题 3 条）：
{sample_reviews}

请生成：
1. 产品核心问题排名（按严重程度和频率）
2. 每个问题的具体改进建议
3. 用户最看重的 3 个卖点（用于 Listing 优化）
4. 竞品差异化机会（基于用户未满足的需求）
5. 预警信号（哪些问题在恶化？）
6. 优先级行动清单（ROI 最高的改进先做）
"""

response = client.messages.create(
model="claude-sonnet-4-20250514",
max_tokens=2000,
messages=[{"role": "user", "content": prompt}]
)

return response.content[0].text
```

### 6.2 竞品 Review 对比分析

```python
def competitive_review_analysis(my_reviews: pd.DataFrame,
competitor_reviews: pd.DataFrame) -> str:
"""对比自己和竞品的 Review 主题"""

# 分别做主题建模
my_topics = run_bertopic(my_reviews)
comp_topics = run_bertopic(competitor_reviews)

# 用 LLM 对比分析
prompt = f"""
对比两个产品的 Review 分析结果：

我的产品：
- 平均评分：{my_reviews['rating'].mean():.1f}
- 差评主题：{my_topics['negative']}
- 好评主题：{my_topics['positive']}

竞品：
- 平均评分：{competitor_reviews['rating'].mean():.1f}
- 差评主题：{comp_topics['negative']}
- 好评主题：{comp_topics['positive']}

请分析：
1. 我的产品 vs 竞品的优势和劣势
2. 竞品的差评中有哪些是我可以利用的机会
3. 我的差评中哪些问题竞品已经解决了
4. 差异化定位建议
"""
return llm_call(prompt)
```

---

## 7. 构建完整 Pipeline

### 7.1 端到端 Review 分析 Pipeline

```python
class ReviewAnalysisPipeline:
"""完整的 Review 分析 Pipeline"""

def __init__(self, embedding_model="all-MiniLM-L6-v2"):
self.embedding_model = SentenceTransformer(embedding_model)
self.sentiment_pipeline = pipeline(
"sentiment-analysis",
model="distilbert-base-uncased-finetuned-sst-2-english"
)
self.topic_model = None

def run(self, reviews_df: pd.DataFrame) -> dict:
"""运行完整分析"""
# Step 1: 预处理
df = preprocess_reviews(reviews_df)

# Step 2: 情感分析
sentiments = self.sentiment_pipeline(
df['full_text'].tolist(),
batch_size=32, truncation=True
)
df['sentiment'] = [s['label'].lower() for s in sentiments]

# Step 3: 主题建模
self.topic_model = BERTopic(
embedding_model=self.embedding_model,
nr_topics="auto",
min_topic_size=5
)
topics, _ = self.topic_model.fit_transform(df['full_text'].tolist())
df['topic'] = topics

# Step 4: 汇总
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

# Step 5: LLM 洞察
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

### 7.2 Streamlit Dashboard（完整实现）

```python
# review_dashboard.py Review 智能分析 Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

st.set_page_config(page_title="Review 智能分析", layout="wide")
st.title(" Review 智能分析系统")

# === 侧边栏 ===
with st.sidebar:
st.header(" 数据上传")
uploaded_file = st.file_uploader("上传 Review CSV", type="csv")

if uploaded_file:
st.header(" 分析设置")
min_rating = st.slider("最低评分筛选", 1, 5, 1)
max_rating = st.slider("最高评分筛选", 1, 5, 5)
num_topics = st.slider("主题数量", 5, 30, 10)
analysis_type = st.selectbox(
"分析类型",
["全部 Review", "仅差评 (1-2星)", "仅好评 (4-5星)", "中评 (3星)"]
)

if uploaded_file:
df = pd.read_csv(uploaded_file)
df = preprocess_reviews(df)

# 筛选
df_filtered = df[(df['rating'] >= min_rating) & (df['rating'] <= max_rating)]

# === Tab 1: 概览 ===
tab1, tab2, tab3, tab4, tab5 = st.tabs([
" 概览", " 情感分析", " 主题建模", " 趋势", " AI 洞察"
])

with tab1:
# KPI 卡片
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("总 Review", f"{len(df_filtered):,}")
col2.metric("平均评分", f"{df_filtered['rating'].mean():.2f} ")
col3.metric("差评率", f"{(df_filtered['rating'] <= 2).mean()*100:.1f}%")
col4.metric("好评率", f"{(df_filtered['rating'] >= 4).mean()*100:.1f}%")
col5.metric("验证购买", f"{df_filtered['verified'].mean()*100:.0f}%")

# 评分分布
col1, col2 = st.columns(2)
with col1:
rating_dist = df_filtered['rating'].value_counts().sort_index()
fig = px.bar(x=rating_dist.index, y=rating_dist.values,
labels={'x': '评分', 'y': '数量'},
title="评分分布",
color=rating_dist.index,
color_continuous_scale=['red', 'orange', 'yellow', 'lightgreen', 'green'])
st.plotly_chart(fig, use_container_width=True)

with col2:
# 词云
all_text = ' '.join(df_filtered['full_text'].tolist())
wc = WordCloud(width=800, height=400, background_color='white',
max_words=100, colormap='viridis').generate(all_text)
fig_wc, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wc, interpolation='bilinear')
ax.axis('off')
st.pyplot(fig_wc)

with tab2:
st.subheader(" 情感分析")

# 运行情感分析
with st.spinner("正在分析情感..."):
sentiments = bert_sentiment(df_filtered['full_text'].tolist())
df_filtered['sentiment'] = [s['label'] for s in sentiments]
df_filtered['sentiment_score'] = [s['score'] for s in sentiments]

# 情感分布
col1, col2 = st.columns(2)
with col1:
sent_dist = df_filtered['sentiment'].value_counts()
fig = px.pie(values=sent_dist.values, names=sent_dist.index,
title="情感分布",
color_discrete_map={'positive': 'green', 'negative': 'red', 'neutral': 'gray'})
st.plotly_chart(fig, use_container_width=True)

with col2:
# 情感 vs 评分的关系
fig = px.box(df_filtered, x='rating', y='sentiment_score',
title="情感得分 vs 评分",
labels={'rating': '评分', 'sentiment_score': '情感得分'})
st.plotly_chart(fig, use_container_width=True)

# 情感最极端的 Review
st.subheader("最正面的 Review")
top_positive = df_filtered.nlargest(3, 'sentiment_score')
for _, row in top_positive.iterrows():
st.success(f"{row['rating']} | {row['full_text'][:200]}...")

st.subheader("最负面的 Review")
top_negative = df_filtered.nsmallest(3, 'sentiment_score')
for _, row in top_negative.iterrows():
st.error(f"{row['rating']} | {row['full_text'][:200]}...")

with tab3:
st.subheader(" 主题建模 (BERTopic)")

with st.spinner("正在提取主题..."):
topic_model = BERTopic(
embedding_model=embedding_model,
nr_topics=num_topics,
min_topic_size=5
)
topics, probs = topic_model.fit_transform(df_filtered['full_text'].tolist())
df_filtered['topic'] = topics

# 主题概览
topic_info = topic_model.get_topic_info()
st.dataframe(topic_info[['Topic', 'Count', 'Name']].head(20),
use_container_width=True)

# 主题可视化
try:
fig = topic_model.visualize_barchart(top_n_topics=10)
st.plotly_chart(fig, use_container_width=True)
except:
pass

# 差评专项主题
st.subheader(" 差评核心问题")
neg_df = df_filtered[df_filtered['rating'] <= 2]
if len(neg_df) > 10:
neg_topic_counts = neg_df.groupby('topic').size().sort_values(ascending=False)
for topic_id in neg_topic_counts.head(5).index:
if topic_id == -1:
continue
keywords = topic_model.get_topic(topic_id)
keyword_str = ", ".join([w for w, _ in keywords[:5]])
count = neg_topic_counts[topic_id]
st.warning(f"**Topic {topic_id}** ({count} 条差评): {keyword_str}")

# 显示该主题的示例 Review
examples = neg_df[neg_df['topic'] == topic_id]['full_text'].head(2)
for ex in examples:
st.caption(f" → {ex[:150]}...")

with tab4:
st.subheader(" 趋势分析")

df_filtered['month'] = pd.to_datetime(df_filtered['date']).dt.to_period('M').astype(str)

# 月度评分趋势
monthly = df_filtered.groupby('month').agg({
'rating': 'mean',
'full_text': 'count'
}).reset_index()
monthly.columns = ['月份', '平均评分', 'Review 数量']

fig = go.Figure()
fig.add_trace(go.Bar(x=monthly['月份'], y=monthly['Review 数量'], name='Review 数量'))
fig.add_trace(go.Scatter(x=monthly['月份'], y=monthly['平均评分'],
name='平均评分', yaxis='y2', mode='lines+markers'))
fig.update_layout(
title="月度 Review 趋势",
yaxis=dict(title='Review 数量'),
yaxis2=dict(title='平均评分', overlaying='y', side='right', range=[1, 5])
)
st.plotly_chart(fig, use_container_width=True)

with tab5:
st.subheader(" AI 洞察")

if st.button("生成 AI 分析报告"):
with st.spinner("AI 正在分析..."):
insights = generate_review_insights({
'total_reviews': len(df_filtered),
'avg_rating': df_filtered['rating'].mean(),
'negative_topics': str(neg_topic_counts.head(5).to_dict()) if 'neg_topic_counts' in dir() else "N/A",
'positive_topics': "N/A",
'date_range': f"{df_filtered['date'].min()} to {df_filtered['date'].max()}"
}, df_filtered[df_filtered['rating'] <= 2].head(10).to_dict())

st.markdown(insights)

# 下载报告
st.download_button(
" 下载分析报告",
insights,
file_name=f"review_analysis_{datetime.now().strftime('%Y%m%d')}.md",
mime="text/markdown"
)

else:
st.info(" 请在左侧上传 Review CSV 文件开始分析")
st.markdown("""
**CSV 文件格式要求：**
- `rating`: 评分 (1-5)
- `title`: Review 标题
- `body`: Review 正文
- `date`: 日期
- `verified`: 是否验证购买 (True/False)
- `helpful_votes`: 有用投票数（可选）
""")
```

运行：`streamlit run review_dashboard.py`

### 7.3 导出分析结果

```python
def export_analysis_results(df: pd.DataFrame, topic_model, output_dir: str = "output"):
"""导出完整的分析结果"""
from pathlib import Path
Path(output_dir).mkdir(exist_ok=True)

# 1. 导出带标注的 Review 数据
df.to_csv(f"{output_dir}/reviews_analyzed.csv", index=False)

# 2. 导出主题摘要
topic_info = topic_model.get_topic_info()
topic_info.to_csv(f"{output_dir}/topics_summary.csv", index=False)

# 3. 导出差评主题详情
neg_df = df[df['rating'] <= 2]
neg_topics = neg_df.groupby('topic').agg({
'full_text': 'count',
'rating': 'mean'
}).sort_values('full_text', ascending=False)
neg_topics.to_csv(f"{output_dir}/negative_topics.csv")

# 4. 生成 HTML 报告
html_report = topic_model.visualize_topics()
html_report.write_html(f"{output_dir}/topic_visualization.html")

print(f"分析结果已导出到 {output_dir}/")
```

---

## 8. 完成标志

- [ ] 构建 Review 数据采集和清洗 Pipeline
- [ ] 实现 VADER + BERT 双层情感分析
- [ ] 用 BERTopic 对至少 1000 条 Review 做主题建模
- [ ] 用 LLM 生成可执行的 Review 洞察报告
- [ ] 构建 Streamlit Dashboard 展示分析结果
- [ ] 完成一次竞品 Review 对比分析

(b6-mcp-agentic-workflow.md) | [Path 总览](README.md) | [B8 Dashboard >](b8-ecommerce-dashboard.md)
