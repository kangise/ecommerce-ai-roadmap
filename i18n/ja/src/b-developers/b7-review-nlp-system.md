# B7. Review インテリジェント分析システム: NLP + 主題モデリング + 感情分析

> **トラック**: Path B: 技術 · **モジュール**: B7
> **最終更新**: 2026-03-15
> **難易度**: 中級
> **所要時間**: 1 日 1 時間、2 週間
> **前提モジュール**: [B1 データ収集と処理](b1-data-pipeline.md)


---

## 章ナビゲーション

1. [なぜ Review NLP システムが必要か](#1-なぜ-review-nlp-システムが必要か) · 2. [技術スタックの選択](#2-技術スタックの選択) · 3. [データ収集と前処理](#3-データ収集と前処理) · 4. [感情分析の実践](#4-感情分析の実践) · 5. [BERTopic 主題モデリング](#5-bertopic-主題モデリング) · 6. [LLM 強化分析](#6-llm-強化分析) · 7. [完全な Pipeline の構築](#7-完全な-pipeline-の構築) · 8. [完了チェック](#8-完了チェック)

---

## このモジュールで構築するもの

- Amazon Review の自動収集とクレンジング Pipeline
- BERT ベースの感情分析モデル(正面/負面/中立)
- BERTopic 主題モデリングシステム(Review の核心話題を自動発見)
- LLM 強化の Review 洞察ジェネレーター(データから実行可能な提案へ)
- 完全な Review 分析ダッシュボード

> **核心理念**: Review は EC で最も価値のある非構造化データ。従来の方法は人手で読むこと、AI の方法は主題、感情、実行可能な洞察を自動抽出すること。良い Review NLP システムは商品リサーチの指導、製品改善、Listing 最適化、低評価の予防ができる。

---

## 1. なぜ Review NLP システムが必要か

### 1.1 Review データの価値

| 応用シーン | 入力 | 出力 | 業務価値 |
|------------|------|------|----------|
| 商品リサーチ検証 | 競合 Review | ユーザー痛点のランキング | 差別化の方向を見つける |
| 製品改善 | 自分の低評価 | 問題分類+頻度 | 最高頻度の問題を優先修正 |
| Listing 最適化 | 高評価のキーワード | ユーザーが最も重視する訴求点 | タイトル/Bullet の最適化 |
| 広告最適化 | Review の高頻度語 | ユーザーの検索意図 | 広告キーワードの拡張 |
| CS 予防 | 低評価のトレンド | 早期警告 | 低評価の爆発前に介入 |
| 競合監視 | 競合 Review の変化 | 競合の問題/優位の変化 | 競争戦略の調整 |

### 1.2 人手 vs AI 分析の比較

| 次元 | 人手で読む | AI NLP 分析 |
|------|------------|-------------|
| 速度 | 100 件/時 | 10,000 件/分 |
| 一貫性 | 主観判断、人により結果が異なる | 客観的で一貫 |
| カバレッジ | 通常は最新/最悪だけ見る | 全量分析 |
| 深さ | 表面的な理解 | 主題クラスタリング+感情の定量化+トレンド分析 |
| コスト | 高い(人力の時間) | 低い(一度開発、継続利用) |

---

## 2. 技術スタックの選択

### 2.1 推奨技術スタック

```
Review NLP システムの技術スタック:

データ層:
pandas データ処理
SP-API / スクレイパー Review 収集
SQLite / PostgreSQL データ保存

NLP 層:
transformers (HuggingFace) BERT モデル
BERTopic 主題モデリング
sentence-transformers テキストベクトル化
TextBlob / VADER 高速感情分析(軽量)
spaCy テキスト前処理

LLM 強化層:
OpenAI API / Claude API 深掘り分析
ローカル LLM (Ollama) プライバシー敏感シーン

可視化層:
Streamlit インタラクティブダッシュボード
matplotlib / plotly グラフ
wordcloud ワードクラウド
```

### 2.2 依存関係のインストール

```bash
# コア依存
pip3 install pandas numpy
pip3 install transformers torch sentence-transformers
pip3 install bertopic
pip3 install textblob vaderSentiment
pip3 install spacy
python3 -m spacy download en_core_web_sm

# 可視化
pip3 install streamlit plotly wordcloud matplotlib

# LLM(オプション)
pip3 install openai anthropic
```

---

## 3. データ収集と前処理

### 3.1 Review データの取得方法

| 方法 | 利点 | 欠点 | 向く |
|------|------|------|------|
| Amazon SP-API | 公式 API、安定・規約準拠 | 自分の製品の Review しか取れない | 自社製品分析 |
| ウェブスクレイピング | 競合 Review を取れる | アンチスクレイピング対応が必要、規約リスク | 競合分析 |
| 第三者ツールのエクスポート | シンプルで速い | データ形式が不統一 | 素早い分析 |
| 公開データセット | 無料、大量 | データが古い可能性 | 学習とテスト |

> **実リソース**: 複数のチュートリアルが Python で Amazon Review データをスクレイピングする方法を示している、BeautifulSoup、Scrapy、専門 API サービスの使用を含む([ScrapingBee](https://www.scrapingbee.com/blog/how-to-scrape-amazon-reviews/)、[Oxylabs](https://oxylabs.io/blog/how-to-scrape-amazon-reviews))。スクレイピングしたデータには通常、評価、タイトル、本文、日付、検証購入ステータス、有用投票数が含まれる。

Content rephrased for compliance with licensing restrictions.

> **実事例: 製品横断の Review 分析**
> 学術研究が、文脈的主題モデリング(Contextual Topic Modeling)と関連ルールマイニングを使ってヘッドホンカテゴリの Amazon Review を製品横断で分析し、異なる製品間で共有されるユーザーの関心事と差別化的特徴を発見する方法を示した([MDPI](https://www.mdpi.com/0718-1876/19/4/170))。

Content rephrased for compliance with licensing restrictions.

### 3.2 Review データ構造

```python
import pandas as pd

# Review データ標準形式
review_schema = {
"asin": str, # 製品 ASIN
"rating": int, # 1-5 星
"title": str, # Review タイトル
"body": str, # Review 本文
"date": str, # 日付
"verified": bool, # 検証購入か否か
"helpful_votes": int, # 有用投票数
"marketplace": str # 市場(US/UK/DE/JP)
}
```

### 3.2 データクレンジング Pipeline

```python
import re
import spacy

nlp = spacy.load("en_core_web_sm")

def clean_review(text: str) -> str:
"""Review テキストをクレンジング"""
if not text or not isinstance(text, str):
return ""

# HTML タグを除去
text = re.sub(r'<[^>]+>', '', text)
# URL を除去
text = re.sub(r'http\S+', '', text)
# 余分な空白を除去
text = re.sub(r'\s+', ' ', text).strip()

return text

def preprocess_reviews(df: pd.DataFrame) -> pd.DataFrame:
"""Review DataFrame を前処理"""
# テキストをクレンジング
df['clean_body'] = df['body'].apply(clean_review)
df['clean_title'] = df['title'].apply(clean_review)

# タイトルと本文を結合
df['full_text'] = df['clean_title'] + '. ' + df['clean_body']

# 空テキストを除外
df = df[df['full_text'].str.len() > 10]

# 感情ラベルをタグ付け(星評価に基づく粗い分類)
df['sentiment_label'] = df['rating'].map({
1: 'negative', 2: 'negative',
3: 'neutral',
4: 'positive', 5: 'positive'
})

return df
```

---

## 4. 感情分析の実践

### 4.1 方法の比較

| 方法 | 精度 | 速度 | コスト | 向く |
|------|------|------|--------|------|
| VADER | 中程度(70-75%) | 極速 | 無料 | 素早い選別、大量データ |
| TextBlob | 中程度(70-75%) | 極速 | 無料 | シンプルなシーン |
| DistilBERT | 高(85-90%) | 中程度 | 無料(ローカル) | 精密分析 |
| GPT/Claude API | 最高(90%+) | 遅い | 有料 | 少量・高価値の分析 |

### 4.2 VADER 高速感情分析

```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def vader_sentiment(text: str) -> dict:
"""VADER 感情分析(英語 Review に向く)"""
scores = analyzer.polarity_scores(text)

# 感情を判定
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

# 一括分析
df['vader'] = df['full_text'].apply(vader_sentiment)
df['vader_label'] = df['vader'].apply(lambda x: x['label'])
df['vader_score'] = df['vader'].apply(lambda x: x['score'])
```

### 4.3 DistilBERT 深掘り感情分析

```python
from transformers import pipeline

# 事前訓練済み感情分析モデルをロード
sentiment_pipeline = pipeline(
"sentiment-analysis",
model="distilbert-base-uncased-finetuned-sst-2-english",
device=0 # GPU、なければ -1
)

def bert_sentiment(texts: list, batch_size: int = 32) -> list:
"""一括 BERT 感情分析"""
results = sentiment_pipeline(texts, batch_size=batch_size, truncation=True)
return [
{
'label': r['label'].lower(),
'score': r['score'] if r['label'] == 'POSITIVE' else -r['score']
}
for r in results
]

# 一括処理(逐条より 10x 速い)
texts = df['full_text'].tolist()
sentiments = bert_sentiment(texts)
df['bert_label'] = [s['label'] for s in sentiments]
df['bert_score'] = [s['score'] for s in sentiments]
```

> **実事例**: 学術研究によると、BERT ベースの感情分析は Amazon Review データセットで 90%+ の精度に達し、従来の機械学習手法を大きく上回る([MDPI](https://www.mdpi.com/1999-5903/18/3/138))。BERTopic を Amazon Review データと組み合わせると製品の核心話題とユーザーの関心事を自動発見できる([Amalytix](https://www.amalytix.com/en/blog/analyze-reviews-bertopic/))。

Content rephrased for compliance with licensing restrictions.

---

## 5. BERTopic 主題モデリング

### 5.1 BERTopic の核心概念

BERTopic は BERT 埋め込み + UMAP 次元削減 + HDBSCAN クラスタリングでテキストの主題を自動発見する。

```python
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

# 軽量な埋め込みモデルを使用
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# BERTopic モデルを作成
topic_model = BERTopic(
embedding_model=embedding_model,
nr_topics="auto", # 主題数を自動決定
min_topic_size=10, # 最小主題サイズ
language="english",
verbose=True
)

# モデルを訓練
topics, probs = topic_model.fit_transform(df['full_text'].tolist())

# 主題を確認
topic_info = topic_model.get_topic_info()
print(topic_info.head(20))

# 各主題のキーワードを確認
for topic_id in range(min(10, len(topic_info))):
print(f"\nTopic {topic_id}:")
print(topic_model.get_topic(topic_id))
```

### 5.2 低評価専門の主題分析

```python
# 低評価(1-2 星)だけを分析
negative_reviews = df[df['rating'] <= 2]['full_text'].tolist()

negative_topic_model = BERTopic(
embedding_model=embedding_model,
nr_topics=10, # 主題数を制限
min_topic_size=5,
language="english"
)

neg_topics, neg_probs = negative_topic_model.fit_transform(negative_reviews)

# 低評価主題のランキング(頻度順)
neg_topic_info = negative_topic_model.get_topic_info()
print("=== 低評価の核心問題 TOP 10 ===")
for _, row in neg_topic_info.head(10).iterrows():
print(f"Topic {row['Topic']}: {row['Name']} ({row['Count']} reviews)")
```

### 5.3 主題トレンド分析

```python
# 主題の時系列変化を分析
topics_over_time = topic_model.topics_over_time(
df['full_text'].tolist(),
df['date'].tolist()
)

# 可視化
fig = topic_model.visualize_topics_over_time(topics_over_time)
fig.show()

# 発見: ある品質問題の低評価が増えているか?
# これは製品改善の早期警告シグナルになりうる
```

### 5.4 高度な BERTopic テクニック

> **実事例: Amalytix の Amazon Review BERTopic 分析**
> Amalytix は BERTopic で Amazon Review を分析し、製品の核心話題を自動発見する方法を示した。BERTopic は BERT ベースの手法と修正 TF-IDF 分析を使い、非構造化の Review テキストから意味ある主題クラスタを抽出できる([Amalytix](https://www.amalytix.com/en/blog/analyze-reviews-bertopic/))。

Content rephrased for compliance with licensing restrictions.

```python
# 高度テクニック 1: カテゴリ別にグループ化した主題分析
def analyze_by_category(df: pd.DataFrame, categories: list):
"""カテゴリごとに主題分析、カテゴリ固有の問題を発見"""
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

# 高度テクニック 2: 多言語 Review 分析
from sentence_transformers import SentenceTransformer

# 多言語埋め込みモデルを使用(100+ 言語対応)
multilingual_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

multilingual_topic_model = BERTopic(
embedding_model=multilingual_model,
language="multilingual"
)

# 英語、ドイツ語、日本語の Review を同時に分析できる
all_reviews = pd.concat([us_reviews, de_reviews, jp_reviews])
topics, _ = multilingual_topic_model.fit_transform(all_reviews['full_text'].tolist())

# 高度テクニック 3: 主題ラベルの自動生成(LLM で)
def auto_label_topics(topic_model, top_n_topics=20):
"""BERTopic が発見した主題に LLM で人間可読なラベルを生成"""
labels = {}
for topic_id in range(top_n_topics):
keywords = topic_model.get_topic(topic_id)
if not keywords:
continue

keyword_str = ", ".join([w for w, _ in keywords[:10]])

prompt = f"""
以下は製品 Review から抽出したある主題のキーワードです:
{keyword_str}

この主題を短いラベル(3-6 語)で記述してください。
ラベルのみ返す、説明は不要。
"""
label = llm_call(prompt).strip()
labels[topic_id] = label

return labels

# 高度テクニック 4: Review 品質スコアリング
def score_review_quality(df: pd.DataFrame) -> pd.DataFrame:
"""Review の情報品質を評価(高価値 Review の選別用)"""
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

## 6. LLM 強化分析

### 6.1 LLM で実行可能な洞察を生成

BERTopic が主題を発見し、LLM が主題を解読して提案を生成:

```python
import anthropic # または openai

client = anthropic.Anthropic()

def generate_review_insights(topic_info: dict, sample_reviews: list) -> str:
"""LLM で Review 主題から実行可能な洞察を生成"""
prompt = f"""
あなたは EC 製品分析の専門家です。以下は Amazon Review の NLP 分析結果です。

製品: [製品名]
分析した Review 総数: {topic_info['total_reviews']}
時間範囲: {topic_info['date_range']}

低評価主題のランキング(頻度順):
{topic_info['negative_topics']}

高評価主題のランキング:
{topic_info['positive_topics']}

低評価サンプル(各主題 3 件):
{sample_reviews}

生成してください:
1. 製品核心問題のランキング(深刻度と頻度順)
2. 各問題の具体的な改善提案
3. ユーザーが最も重視する 3 つの訴求点(Listing 最適化用)
4. 競合差別化の機会(ユーザーの未充足ニーズに基づく)
5. 警告シグナル(どの問題が悪化している?)
6. 優先度アクションリスト(ROI が最も高い改善を先に)
"""

response = client.messages.create(
model="claude-sonnet-4-20250514",
max_tokens=2000,
messages=[{"role": "user", "content": prompt}]
)

return response.content[0].text
```

### 6.2 競合 Review 比較分析

```python
def competitive_review_analysis(my_reviews: pd.DataFrame,
competitor_reviews: pd.DataFrame) -> str:
"""自分と競合の Review 主題を比較"""

# それぞれ主題モデリング
my_topics = run_bertopic(my_reviews)
comp_topics = run_bertopic(competitor_reviews)

# LLM で比較分析
prompt = f"""
2 つの製品の Review 分析結果を比較:

私の製品:
- 平均評価: {my_reviews['rating'].mean():.1f}
- 低評価主題: {my_topics['negative']}
- 高評価主題: {my_topics['positive']}

競合:
- 平均評価: {competitor_reviews['rating'].mean():.1f}
- 低評価主題: {comp_topics['negative']}
- 高評価主題: {comp_topics['positive']}

分析してください:
1. 私の製品 vs 競合の優位と劣位
2. 競合の低評価の中で私が利用できる機会はどれか
3. 私の低評価の中で競合が既に解決した問題はどれか
4. 差別化ポジションの提案
"""
return llm_call(prompt)
```

---

## 7. 完全な Pipeline の構築

### 7.1 エンドツーエンド Review 分析 Pipeline

```python
class ReviewAnalysisPipeline:
"""完全な Review 分析 Pipeline"""

def __init__(self, embedding_model="all-MiniLM-L6-v2"):
self.embedding_model = SentenceTransformer(embedding_model)
self.sentiment_pipeline = pipeline(
"sentiment-analysis",
model="distilbert-base-uncased-finetuned-sst-2-english"
)
self.topic_model = None

def run(self, reviews_df: pd.DataFrame) -> dict:
"""完全な分析を実行"""
# Step 1: 前処理
df = preprocess_reviews(reviews_df)

# Step 2: 感情分析
sentiments = self.sentiment_pipeline(
df['full_text'].tolist(),
batch_size=32, truncation=True
)
df['sentiment'] = [s['label'].lower() for s in sentiments]

# Step 3: 主題モデリング
self.topic_model = BERTopic(
embedding_model=self.embedding_model,
nr_topics="auto",
min_topic_size=5
)
topics, _ = self.topic_model.fit_transform(df['full_text'].tolist())
df['topic'] = topics

# Step 4: 集約
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

### 7.2 Streamlit ダッシュボード(完全実装)

```python
# review_dashboard.py Review インテリジェント分析ダッシュボード
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

st.set_page_config(page_title="Review インテリジェント分析", layout="wide")
st.title("Review インテリジェント分析システム")

# === サイドバー ===
with st.sidebar:
st.header("データアップロード")
uploaded_file = st.file_uploader("Review CSV をアップロード", type="csv")

if uploaded_file:
st.header("分析設定")
min_rating = st.slider("最低評価フィルタ", 1, 5, 1)
max_rating = st.slider("最高評価フィルタ", 1, 5, 5)
num_topics = st.slider("主題数", 5, 30, 10)
analysis_type = st.selectbox(
"分析タイプ",
["すべての Review", "低評価のみ (1-2星)", "高評価のみ (4-5星)", "中評価 (3星)"]
)

if uploaded_file:
df = pd.read_csv(uploaded_file)
df = preprocess_reviews(df)

# フィルタ
df_filtered = df[(df['rating'] >= min_rating) & (df['rating'] <= max_rating)]

# === Tab 1: 概要 ===
tab1, tab2, tab3, tab4, tab5 = st.tabs([
"概要", "感情分析", "主題モデリング", "トレンド", "AI 洞察"
])

with tab1:
# KPI カード
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("総 Review", f"{len(df_filtered):,}")
col2.metric("平均評価", f"{df_filtered['rating'].mean():.2f}")
col3.metric("低評価率", f"{(df_filtered['rating'] <= 2).mean()*100:.1f}%")
col4.metric("高評価率", f"{(df_filtered['rating'] >= 4).mean()*100:.1f}%")
col5.metric("検証購入", f"{df_filtered['verified'].mean()*100:.0f}%")

# 評価分布
col1, col2 = st.columns(2)
with col1:
rating_dist = df_filtered['rating'].value_counts().sort_index()
fig = px.bar(x=rating_dist.index, y=rating_dist.values,
labels={'x': '評価', 'y': '数量'},
title="評価分布",
color=rating_dist.index,
color_continuous_scale=['red', 'orange', 'yellow', 'lightgreen', 'green'])
st.plotly_chart(fig, use_container_width=True)

with col2:
# ワードクラウド
all_text = ' '.join(df_filtered['full_text'].tolist())
wc = WordCloud(width=800, height=400, background_color='white',
max_words=100, colormap='viridis').generate(all_text)
fig_wc, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wc, interpolation='bilinear')
ax.axis('off')
st.pyplot(fig_wc)

with tab2:
st.subheader("感情分析")

# 感情分析を実行
with st.spinner("感情を分析中..."):
sentiments = bert_sentiment(df_filtered['full_text'].tolist())
df_filtered['sentiment'] = [s['label'] for s in sentiments]
df_filtered['sentiment_score'] = [s['score'] for s in sentiments]

# 感情分布
col1, col2 = st.columns(2)
with col1:
sent_dist = df_filtered['sentiment'].value_counts()
fig = px.pie(values=sent_dist.values, names=sent_dist.index,
title="感情分布",
color_discrete_map={'positive': 'green', 'negative': 'red', 'neutral': 'gray'})
st.plotly_chart(fig, use_container_width=True)

with col2:
# 感情 vs 評価の関係
fig = px.box(df_filtered, x='rating', y='sentiment_score',
title="感情スコア vs 評価",
labels={'rating': '評価', 'sentiment_score': '感情スコア'})
st.plotly_chart(fig, use_container_width=True)

# 感情が最も極端な Review
st.subheader("最も正面の Review")
top_positive = df_filtered.nlargest(3, 'sentiment_score')
for _, row in top_positive.iterrows():
st.success(f"{row['rating']} | {row['full_text'][:200]}...")

st.subheader("最も負面の Review")
top_negative = df_filtered.nsmallest(3, 'sentiment_score')
for _, row in top_negative.iterrows():
st.error(f"{row['rating']} | {row['full_text'][:200]}...")

with tab3:
st.subheader("主題モデリング (BERTopic)")

with st.spinner("主題を抽出中..."):
topic_model = BERTopic(
embedding_model=embedding_model,
nr_topics=num_topics,
min_topic_size=5
)
topics, probs = topic_model.fit_transform(df_filtered['full_text'].tolist())
df_filtered['topic'] = topics

# 主題概要
topic_info = topic_model.get_topic_info()
st.dataframe(topic_info[['Topic', 'Count', 'Name']].head(20),
use_container_width=True)

# 主題可視化
try:
fig = topic_model.visualize_barchart(top_n_topics=10)
st.plotly_chart(fig, use_container_width=True)
except:
pass

# 低評価専門の主題
st.subheader("低評価の核心問題")
neg_df = df_filtered[df_filtered['rating'] <= 2]
if len(neg_df) > 10:
neg_topic_counts = neg_df.groupby('topic').size().sort_values(ascending=False)
for topic_id in neg_topic_counts.head(5).index:
if topic_id == -1:
continue
keywords = topic_model.get_topic(topic_id)
keyword_str = ", ".join([w for w, _ in keywords[:5]])
count = neg_topic_counts[topic_id]
st.warning(f"**Topic {topic_id}** ({count} 件の低評価): {keyword_str}")

# その主題の例 Review を表示
examples = neg_df[neg_df['topic'] == topic_id]['full_text'].head(2)
for ex in examples:
st.caption(f" → {ex[:150]}...")

with tab4:
st.subheader("トレンド分析")

df_filtered['month'] = pd.to_datetime(df_filtered['date']).dt.to_period('M').astype(str)

# 月次評価トレンド
monthly = df_filtered.groupby('month').agg({
'rating': 'mean',
'full_text': 'count'
}).reset_index()
monthly.columns = ['月', '平均評価', 'Review 数']

fig = go.Figure()
fig.add_trace(go.Bar(x=monthly['月'], y=monthly['Review 数'], name='Review 数'))
fig.add_trace(go.Scatter(x=monthly['月'], y=monthly['平均評価'],
name='平均評価', yaxis='y2', mode='lines+markers'))
fig.update_layout(
title="月次 Review トレンド",
yaxis=dict(title='Review 数'),
yaxis2=dict(title='平均評価', overlaying='y', side='right', range=[1, 5])
)
st.plotly_chart(fig, use_container_width=True)

with tab5:
st.subheader("AI 洞察")

if st.button("AI 分析レポートを生成"):
with st.spinner("AI が分析中..."):
insights = generate_review_insights({
'total_reviews': len(df_filtered),
'avg_rating': df_filtered['rating'].mean(),
'negative_topics': str(neg_topic_counts.head(5).to_dict()) if 'neg_topic_counts' in dir() else "N/A",
'positive_topics': "N/A",
'date_range': f"{df_filtered['date'].min()} to {df_filtered['date'].max()}"
}, df_filtered[df_filtered['rating'] <= 2].head(10).to_dict())

st.markdown(insights)

# レポートをダウンロード
st.download_button(
"分析レポートをダウンロード",
insights,
file_name=f"review_analysis_{datetime.now().strftime('%Y%m%d')}.md",
mime="text/markdown"
)

else:
st.info("左側で Review CSV ファイルをアップロードして分析を開始してください")
st.markdown("""
**CSV ファイル形式の要件:**
- `rating`: 評価 (1-5)
- `title`: Review タイトル
- `body`: Review 本文
- `date`: 日付
- `verified`: 検証購入か否か (True/False)
- `helpful_votes`: 有用投票数(オプション)
""")
```

実行: `streamlit run review_dashboard.py`

### 7.3 分析結果のエクスポート

```python
def export_analysis_results(df: pd.DataFrame, topic_model, output_dir: str = "output"):
"""完全な分析結果をエクスポート"""
from pathlib import Path
Path(output_dir).mkdir(exist_ok=True)

# 1. 注記付きの Review データをエクスポート
df.to_csv(f"{output_dir}/reviews_analyzed.csv", index=False)

# 2. 主題サマリをエクスポート
topic_info = topic_model.get_topic_info()
topic_info.to_csv(f"{output_dir}/topics_summary.csv", index=False)

# 3. 低評価主題の詳細をエクスポート
neg_df = df[df['rating'] <= 2]
neg_topics = neg_df.groupby('topic').agg({
'full_text': 'count',
'rating': 'mean'
}).sort_values('full_text', ascending=False)
neg_topics.to_csv(f"{output_dir}/negative_topics.csv")

# 4. HTML レポートを生成
html_report = topic_model.visualize_topics()
html_report.write_html(f"{output_dir}/topic_visualization.html")

print(f"分析結果を {output_dir}/ にエクスポートしました")
```

---

## 8. 完了チェック

- [ ] Review データ収集とクレンジング Pipeline を構築
- [ ] VADER + BERT の二層感情分析を実装
- [ ] BERTopic で最低 1000 件の Review に主題モデリング
- [ ] LLM で実行可能な Review 洞察レポートを生成
- [ ] Streamlit ダッシュボードを構築して分析結果を表示
- [ ] 競合 Review 比較分析を 1 回完了

[< B6 MCP 統合](b6-mcp-agentic-workflow.md) | [Path 総覧](../README.md) | [B8 Dashboard >](b8-ecommerce-dashboard.md)
