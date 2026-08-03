# B2. 予測モデルとインテリジェント意思決定

> **トラック**: Path B: 技術 · **モジュール**: B2
> **最終更新**: 2026-07-31
> **難易度**: 中級 → 上級
> **前提**: B1 データパイプラインの基礎(pandas、データクレンジング)、Python の基礎
> **所要時間**: 1 日 1 時間、2〜3 週間
---


```mermaid
flowchart LR
B1["B1 データパイプライン"]
B1 --> B2
B2[" B2 予測モデル<br/>(現在地)"]:::current
B2 --> B3
B3["B3 RAG 知識ベース"]
B3 --> B4
B4["B4 Agent ワークフロー"]
B4 --> B5
B5["B5 ローカルモデル配備"]
classDef current fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
```

---

## 章ナビゲーション

1. [予測方法論](#1-予測方法論) · 2. [ツール全景](#2-ツール全景) · 3. [コード実践](#3-コード実践) · 4. [モデル評価](#4-モデル評価) · 5. [実践プロジェクト](#5-実践プロジェクト-sku-販売予測システムの構築) · 6. [よくある罠](#6-よくある罠) · 7. [学習リソース](#7-学習リソース)


## このモジュールで構築するもの

販売予測モデル + Review 主題分析システム。

修了後には:
- Prophet で SKU の 30/60/90 日販売予測を行い、予測値と信頼区間を出力できる
- 時系列予測の核心原理(トレンド + 季節性 + ノイズの分解)を理解できる
- EC 予測の特殊な課題に対処できる: 大型セールのスパイク、新商品コールドスタート、競合の影響
- AutoGluon でゼロ設定モデリングを行い、最適なアルゴリズムを自動選択できる
- BERTopic で Review テキストから主題と感情トレンドを自動発見できる
- 予測結果を補充判断に変換できる([A5 在庫モジュール](../a-operators/a5-inventory.md) に接続)
- MAPE/MAE/RMSE でモデル品質を評価し、バックテストで予測の信頼性を検証できる

---

## 1. 予測方法論

> **関連**: [A5 在庫とサプライチェーン](../a-operators/a5-inventory.md) 販売予測の在庫補充判断への応用は A5 へ · [D3 クロスプラットフォーム AI 協同戦略](../d-platforms/cross-platform-strategy.md) クロスプラットフォーム需要予測は D3 へ。

### 1.1 時系列予測の第一原理

いかなる時系列データも 3 つの成分に分解できる:

```
観測値 = トレンド(Trend) + 季節性(Seasonality) + ノイズ(Residual)
```

| 成分 | 意味 | EC シーンの例 |
|------|------|---------------|
| トレンド | 長期的な上昇か下降の方向 | 新商品発売後に販売量が月ごとに増加;老舗商品が衰退期に入る |
| 季節性 | 固定周期の繰り返しパターン | 毎週月曜が最高販売(週末に注文、月曜に着荷);Q4 繁忙期 |
| ノイズ | 説明できないランダムな変動 | ある日突然インフルエンサーに推薦され、販売が急増し 1 日後に回復 |

**加法モデル vs 乗法モデル:**

- **加法モデル**: `y = trend + seasonality + noise` 季節変動の振幅が固定(例: 毎年 Q4 に 1000 件多く売れる)
- **乗法モデル**: `y = trend × seasonality × noise` 季節変動の振幅がトレンドに応じて変化(例: 毎年 Q4 に 30% 多く売れる)

EC シーンは通常、**乗法モデル**のほうが正確、販売の基数が大きいほど季節変動の絶対値も大きくなるため。

**分解の可視化:**

```python
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti TC", "Arial"]
matplotlib.rcParams["axes.unicode_minus"] = False

def decompose_sales(df: pd.DataFrame, date_col: str = "date", value_col: str = "units"):
    """
    販売時系列をトレンド、季節性、ノイズの 3 成分に分解する。

    Args:
        df: 日付と販売量を含む DataFrame
        date_col: 日付列名
        value_col: 販売量列名
    """
    ts = df.set_index(date_col)[value_col]
    ts = ts.asfreq("D").fillna(method="ffill") # 欠損日を補完

    # 乗法分解、周期=7(週季節性)
    result = seasonal_decompose(ts, model="multiplicative", period=7)

    fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
    result.observed.plot(ax=axes[0], title="元データ (Observed)")
    result.trend.plot(ax=axes[1], title="トレンド (Trend)")
    result.seasonal.plot(ax=axes[2], title="季節性 (Seasonality)")
    result.resid.plot(ax=axes[3], title="ノイズ (Residual)")

    plt.tight_layout()
    plt.savefig("output/decomposition.png", dpi=150)
    plt.show()

    return result

# 使用例
# df = pd.read_csv("data/daily_sales.csv")
# result = decompose_sales(df, date_col="date", value_col="units")
```

> **重要な洞察**: 分解後の「ノイズ」成分にまだ明確なパターンがある(例: 大型セールのたびに巨大な残差)なら、モデルに大型セールイベントのモデリングが欠けている。これはまさに Prophet の `holidays` パラメータが解決する問題。

### 1.2 EC 予測の特殊な課題

EC の販売予測は従来の小売より難しい、いくつかの独特な撹乱要因があるため:

| 課題 | 症状 | 影響 | 対応戦略 |
|------|------|------|----------|
| 大型セールのスパイク | Prime Day/BFCM で販売が 5-20 倍に急増 | モデルが極端値に引きずられる | 大型セールを特殊イベントとしてモデリング(Prophet holidays) |
| 新商品コールドスタート | 新 ASIN に履歴データなし | 時系列で予測できない | 類似品の販売曲線で類推予測 |
| 競合の影響 | 競合の値下げ/欠品で自分の販売が急変 | 外部要因は自分のデータから学べない | 外部回帰変数を追加(競合価格、BSR) |
| 広告依存 | 広告停止後に販売が崖崩れ | 自然販売と広告販売が混ざる | 自然流入と広告流入を分離してそれぞれ予測 |
| 在庫制約 | 欠品中は販売が 0(真の需要でない) | 履歴の 0 は「需要なし」を意味しない | 欠品期のデータは特殊処理か除外が必要 |
| 季節性の重畳 | 週季節性 + 月季節性 + 年季節性が同時に存在 | 単一周期のモデルでは不十分 | Prophet は複数季節性の自動モデリングに対応 |

**欠品データの処理(重要!):**

```python
def handle_stockout(df: pd.DataFrame, units_col: str = "units") -> pd.DataFrame:
    """
    欠品期間のゼロ販売データを処理する。

    欠品期間の販売 0 は需要 0 を意味しない。
    戦略: 欠品前後の平均販売で埋め、モデルが「特定の日は需要 0」と学ぶのを避ける。
    """
    df = df.copy()

    # 連続ゼロ販売をフラグ(欠品の可能性)
    df["is_zero"] = df[units_col] == 0
    df["zero_streak"] = (
        df["is_zero"]
        .groupby((~df["is_zero"]).cumsum())
        .cumsum()
    )

    # 連続 3 日以上のゼロ販売は欠品とみなす(真のゼロ需要でなく)
    stockout_mask = df["zero_streak"] >= 3

    if stockout_mask.any():
        # 前後各 7 日の非ゼロ平均で埋める
        rolling_mean = (
            df[~stockout_mask][units_col]
            .rolling(window=7, min_periods=1)
            .mean()
        )
        df.loc[stockout_mask, units_col] = rolling_mean.reindex(
            df.index
        ).ffill().bfill()

        stockout_days = stockout_mask.sum()
        print(f"{stockout_days} 日の欠品疑いを検出、ローリング平均で補完済み")

    df = df.drop(columns=["is_zero", "zero_streak"])
    return df
```

### 1.3 いつ簡単なルール vs いつ ML モデルを使うか

すべての予測に機械学習が必要なわけではない。適切な方法を選ぶことは、最も複雑な方法を選ぶことより重要:

| シーン | 推奨方法 | 理由 |
|--------|----------|------|
| 安定した老舗商品、履歴 >1 年 | Prophet / 指数平滑 | データ十分、時系列モデルの効果が良い |
| 新商品発売 <3 か月 | 類推法 + 人手調整 | データ不足、ML モデルは過学習する |
| 大型セール備蓄 | 昨年同期 × 成長係数 + 人手調整 | 大型セールは非常規イベント、履歴サンプルが少なすぎる |
| 複数 SKU の一括予測 | AutoGluon / LightGBM | 自動化度が高い、一括処理に向く |
| 説明性が必要 | Prophet | トレンド+季節性に分解でき、業務担当が理解できる |
| 精度を追求 | アンサンブル手法(複数モデル加重) | 単一モデルは偏る、アンサンブルで補完 |

**決定フレーム:**

```
履歴データ > 1 年?
はい → 販売が安定?
はい → Prophet(シンプルで高効率)
いいえ → Prophet + 外部変数 / AutoGluon
いいえ → 履歴データ > 3 か月?
はい → Prophet(短周期)/ 移動平均
いいえ → 類推法(類似品の履歴データを探す)
```

---

## 2. ツール全景

| ツール | 種類 | 難度 | 最適シーン | インストール |
|--------|------|------|------------|--------------|
| [Prophet](https://facebook.github.io/prophet/) | 時系列 | 入門 | 単 SKU 販売予測、最も始めやすい | `pip install prophet` |
| [Darts](https://unit8co.github.io/darts/) | 時系列 | 中級 | 複数モデルを比較したい | `pip install darts` |
| [AutoGluon](https://auto.gluon.ai/) | 自動化 ML | 入門 | ML 知識ゼロで一括モデリング | `pip install autogluon.timeseries` |
| [BERTopic](https://maartengr.github.io/BERTopic/) | NLP 主題モデリング | 中級 | Review テキストの主題発見 | `pip install bertopic` |
| [OR-Tools](https://developers.google.com/optimization) | 数理最適化 | 上級 | 補充戦略の最適化 | `pip install ortools` |
| [scikit-learn](https://scikit-learn.org/) | 汎用 ML | 中級 | 特徴量エンジニアリング、回帰、分類 | `pip install scikit-learn` |

**選択のアドバイス:**
- 始めたばかり → Prophet から、午後 1 回で結果が出る
- 自動化したい → AutoGluon、ゼロ設定で最適モデルを自動選択
- Review 分析が必要 → BERTopic、レビュー主題を自動発見
- 補充量の最適化が必要 → OR-Tools、数理計画で最適解を求める

---

## 3. コード実践

### 3.1 Prophet 販売予測(完全フロー)

Prophet は Meta がオープンソース化した時系列予測ライブラリで、業務予測用に設計されている。核心的な強み:
- 欠損値と異常値を自動処理
- 祝日効果を内蔵
- 説明可能な分解結果(トレンド + 季節性 + 祝日)
- 非専門家に優しい

**完全コード: データ準備 → 訓練 → 予測 → 評価 → 可視化**

```python
import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti TC", "Arial"]
matplotlib.rcParams["axes.unicode_minus"] = False

# ============================================================
# Step 1: データ準備
# ============================================================

def prepare_prophet_data(
df: pd.DataFrame,
date_col: str = "date",
value_col: str = "units"
) -> pd.DataFrame:
"""
業務データを Prophet が要求する形式に変換する。

Prophet は 2 列を要求:
- ds: 日付列(datetime 型)
- y: 目標値列(数値型)

Args:
df: 元データ
date_col: 日付列名
value_col: 目標値列名

Returns:
Prophet 形式の DataFrame
"""
prophet_df = df[[date_col, value_col]].copy()
prophet_df.columns = ["ds", "y"]

# 日付形式が正しいことを確保
prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])
prophet_df["y"] = pd.to_numeric(prophet_df["y"], errors="coerce")

# 日付でソートし重複除去(同日複数レコードは合計)
prophet_df = prophet_df.groupby("ds")["y"].sum().reset_index()
prophet_df = prophet_df.sort_values("ds").reset_index(drop=True)

# 欠損日を補完(0 で埋め、後で欠品処理ロジックで置換可)
date_range = pd.date_range(
start=prophet_df["ds"].min(),
end=prophet_df["ds"].max(),
freq="D"
)
prophet_df = (
prophet_df
.set_index("ds")
.reindex(date_range)
.fillna(0)
.reset_index()
.rename(columns={"index": "ds"})
)

print(f"データ準備完了: {len(prophet_df)} 日")
print(f"日付範囲: {prophet_df['ds'].min().date()} → {prophet_df['ds'].max().date()}")
print(f"日均販売: {prophet_df['y'].mean():.1f}")

return prophet_df

# ============================================================
# Step 2: モデルを訓練
# ============================================================

def train_prophet(
df: pd.DataFrame,
yearly: bool = True,
weekly: bool = True,
daily: bool = False,
changepoint_prior: float = 0.05
) -> Prophet:
"""
Prophet モデルを訓練する。

Args:
df: Prophet 形式データ(ds, y の 2 列)
yearly: 年季節性を有効化するか
weekly: 週季節性を有効化するか
daily: 日季節性を有効化するか(通常は不要)
changepoint_prior: トレンド変化点の感度
- 値が大きいほど、トレンド変化を捉えやすい(が過学習しうる)
- 値が小さいほど、トレンドが滑らか(が過小学習しうる)
- デフォルト 0.05、EC シーンは 0.1-0.3 推奨(変化が速い)

Returns:
訓練済みの Prophet モデル
"""
model = Prophet(
yearly_seasonality=yearly,
weekly_seasonality=weekly,
daily_seasonality=daily,
changepoint_prior_scale=changepoint_prior,
interval_width=0.8, # 80% 信頼区間
)

model.fit(df)
print("モデル訓練完了")

return model

# ============================================================
# Step 3: 予測を生成
# ============================================================

def make_forecast(
model: Prophet,
periods: int = 90,
freq: str = "D"
) -> pd.DataFrame:
"""
今後 N 日の予測を生成する。

Args:
model: 訓練済みの Prophet モデル
periods: 予測日数
freq: 頻度(D=日, W=週, M=月)

Returns:
予測結果 DataFrame、以下を含む:
- ds: 日付
- yhat: 予測値
- yhat_lower: 予測下界
- yhat_upper: 予測上界
- trend: トレンド成分
- weekly: 週季節性成分
- yearly: 年季節性成分
"""
future = model.make_future_dataframe(periods=periods, freq=freq)
forecast = model.predict(future)

# 予測値は負にできない(販売の最小は 0)
forecast["yhat"] = forecast["yhat"].clip(lower=0)
forecast["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)

print(f"予測完了: 今後 {periods} 日")
print(f"予測平均: {forecast['yhat'].tail(periods).mean():.1f}")
print(f"予測区間: [{forecast['yhat_lower'].tail(periods).mean():.1f}, "
f"{forecast['yhat_upper'].tail(periods).mean():.1f}]")

return forecast

# ============================================================
# Step 4: 可視化
# ============================================================

def plot_forecast(
model: Prophet,
forecast: pd.DataFrame,
actual_df: pd.DataFrame = None,
title: str = "SKU 販売予測"
):
"""
予測結果図を描画する。

Args:
model: Prophet モデル
forecast: 予測結果
actual_df: 実データ(比較用)
title: グラフタイトル
"""
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# 図 1: 予測 vs 実績
ax1 = axes[0]
ax1.plot(forecast["ds"], forecast["yhat"], color="#1a73e8", label="予測値")
ax1.fill_between(
forecast["ds"],
forecast["yhat_lower"],
forecast["yhat_upper"],
alpha=0.2, color="#1a73e8", label="80% 信頼区間"
)

if actual_df is not None:
ax1.scatter(
actual_df["ds"], actual_df["y"],
color="#333", s=10, alpha=0.5, label="実績値"
)

ax1.set_title(title, fontsize=14, fontweight="bold")
ax1.set_ylabel("販売量 (Units)")
ax1.legend()
ax1.grid(True, alpha=0.3)

# 図 2: 成分分解
ax2 = axes[1]
ax2.plot(forecast["ds"], forecast["trend"], label="トレンド", color="#e8710a")
if "weekly" in forecast.columns:
ax2_twin = ax2.twinx()
weekly_data = forecast.drop_duplicates(subset=["ds"]).tail(90)
ax2_twin.plot(
weekly_data["ds"], weekly_data["weekly"],
label="週季節性", color="#0d652d", alpha=0.7
)
ax2_twin.set_ylabel("週季節性")

ax2.set_title("トレンド分解", fontsize=14, fontweight="bold")
ax2.set_ylabel("トレンド")
ax2.legend(loc="upper left")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("output/forecast.png", dpi=150, bbox_inches="tight")
plt.show()
print("グラフを保存しました: output/forecast.png")

# ============================================================
# 完全な使用例
# ============================================================

# # 1. データをロード
# raw_df = pd.read_csv("data/daily_sales.csv")
# prophet_df = prepare_prophet_data(raw_df, date_col="date", value_col="units")
#
# # 2. 欠品データを処理
# prophet_df = handle_stockout(prophet_df, units_col="y")
#
# # 3. モデルを訓練
# model = train_prophet(prophet_df, changepoint_prior=0.1)
#
# # 4. 今後 90 日を予測
# forecast = make_forecast(model, periods=90)
#
# # 5. 可視化
# plot_forecast(model, forecast, actual_df=prophet_df, title="ASIN-B0XXXXX 販売予測")
```

> **changepoint_prior_scale 調整ガイド**: これは Prophet の最重要ハイパーパラメータ。EC データは変化が速いので、0.1 から試すことを推奨。予測曲線が滑らかすぎる(トレンド変化に追いつけない)なら 0.2-0.3 に上げる;予測曲線が変動しすぎる(ノイズを過学習)なら 0.01-0.05 に下げる。

### 3.2 Prophet 上級: 祝日効果と外部変数

基本の Prophet モデルは EC で最も重要な要因を無視している: 大型セールイベント。祝日効果の追加は予測精度を大きく高められる。

**EC 大型セールイベントを追加:**

```python
def create_ecommerce_holidays(years: list[int]) -> pd.DataFrame:
"""
EC 大型セールカレンダーを作成する。

Prophet の holidays パラメータは以下を含む DataFrame を受け取る:
- holiday: イベント名
- ds: イベント日付
- lower_window: イベント前の影響日数(負数)
- upper_window: イベント後の影響日数
"""
holidays = []

for year in years:
# Prime Day(通常 7 月中旬、2 日間持続)
holidays.append({
"holiday": "prime_day",
"ds": f"{year}-07-12",
"lower_window": -3, # 3 日前から影響開始(予熱期)
"upper_window": 2, # 終了後 2 日も余波あり
})

# Black Friday(11 月第 4 金曜)
# 簡略化: 11-24 付近に固定
holidays.append({
"holiday": "black_friday",
"ds": f"{year}-11-24",
"lower_window": -7, # BFCM 週は 1 週間前から開始
"upper_window": 3, # Cyber Monday 後の数日
})

# Cyber Monday
holidays.append({
"holiday": "cyber_monday",
"ds": f"{year}-11-27",
"lower_window": 0,
"upper_window": 1,
})

# 独身の日(中国セラーに影響)
holidays.append({
"holiday": "singles_day",
"ds": f"{year}-11-11",
"lower_window": -3,
"upper_window": 1,
})

# クリスマス前の買い物シーズン
holidays.append({
"holiday": "christmas_shopping",
"ds": f"{year}-12-15",
"lower_window": -5,
"upper_window": 10,
})

# 新年後の低迷期
holidays.append({
"holiday": "post_newyear_dip",
"ds": f"{year}-01-05",
"lower_window": -5,
"upper_window": 10,
})

return pd.DataFrame(holidays)

def train_prophet_with_holidays(
df: pd.DataFrame,
holidays: pd.DataFrame = None,
changepoint_prior: float = 0.1
) -> Prophet:
"""
祝日効果付きの Prophet モデルを訓練する。
"""
if holidays is None:
years = list(range(
df["ds"].dt.year.min(),
df["ds"].dt.year.max() + 2 # 予測年を含む
))
holidays = create_ecommerce_holidays(years)

model = Prophet(
yearly_seasonality=True,
weekly_seasonality=True,
daily_seasonality=False,
changepoint_prior_scale=changepoint_prior,
holidays=holidays,
holidays_prior_scale=10.0, # 祝日効果の感度
interval_width=0.8,
)

model.fit(df)
print(f"モデル訓練完了({len(holidays)} 個の祝日イベント含む)")

return model
```

**外部回帰変数を追加(広告費用、競合価格):**

```python
def train_prophet_with_regressors(
df: pd.DataFrame,
regressor_cols: list[str] = None
) -> Prophet:
"""
外部回帰変数付きの Prophet モデルを訓練する。

外部変数は以下がありうる:
- ad_spend: 広告費用(投入が多いほど販売が高い)
- competitor_price: 競合価格(競合が値上げ、自分の販売が上がりうる)
- bsr_rank: BSR 順位(順位が高いほど露出が多い)
- coupon_active: クーポンの有無(0/1)

注意: 予測時にも未来の外部変数値を提供する必要がある!
"""
years = list(range(
df["ds"].dt.year.min(),
df["ds"].dt.year.max() + 2
))
holidays = create_ecommerce_holidays(years)

model = Prophet(
yearly_seasonality=True,
weekly_seasonality=True,
changepoint_prior_scale=0.1,
holidays=holidays,
interval_width=0.8,
)

# 外部回帰変数を追加
regressor_cols = regressor_cols or []
for col in regressor_cols:
if col in df.columns:
model.add_regressor(col, standardize=True)
print(f"回帰変数を追加: {col}")

model.fit(df)
print("モデル訓練完了(外部変数含む)")

return model

def forecast_with_regressors(
model: Prophet,
periods: int = 90,
future_regressors: pd.DataFrame = None
) -> pd.DataFrame:
"""
外部変数付きの予測。

Args:
model: 訓練済みモデル
periods: 予測日数
future_regressors: 未来の外部変数値
提供しない場合は履歴平均で埋める(非推奨、精度が下がる)
"""
future = model.make_future_dataframe(periods=periods)

# 未来の外部変数をマージ
if future_regressors is not None:
future = future.merge(future_regressors, on="ds", how="left")

# 欠損の外部変数を履歴平均で埋める
for col in future.columns:
if col not in ["ds"] and future[col].isna().any():
fill_value = future[col].dropna().mean()
future[col] = future[col].fillna(fill_value)
print(f"{col} に欠損値、平均 {fill_value:.2f} で補完")

forecast = model.predict(future)
forecast["yhat"] = forecast["yhat"].clip(lower=0)
forecast["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)

return forecast

# 使用例
# df = prepare_prophet_data(raw_df)
# df["ad_spend"] = ad_data["spend"] # 広告費用データをマージ
# df["competitor_price"] = competitor_data["price"] # 競合価格をマージ
#
# model = train_prophet_with_regressors(df, regressor_cols=["ad_spend", "competitor_price"])
#
# # 予測時に未来の広告予算と競合価格の見積もりを提供する必要
# future_regs = pd.DataFrame({
# "ds": pd.date_range("2025-04-01", periods=90, freq="D"),
# "ad_spend": [500] * 90, # 未来の毎日広告予算 $500 と仮定
# "competitor_price": [29.99] * 90, # 競合価格は不変と仮定
# })
# forecast = forecast_with_regressors(model, periods=90, future_regressors=future_regs)
```

> **外部変数の罠**: 予測時に未来の外部変数値を提供する必要がある。未来の広告予算がわからないなら、`ad_spend` を回帰変数として追加すると逆に予測精度が下がる。未来の値を合理的に見積もれる変数だけを追加する。

### 3.3 AutoGluon 自動化予測(ゼロ設定モデリング)

AutoGluon は Amazon がオープンソース化した自動化機械学習フレームワーク。その時系列モジュールは複数モデル(Prophet、ETS、DeepAR、Theta など)を自動で試し、最適な 1 つを選ぶ。手動チューニングをしたくないシーンに向く。

```python
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

def autogluon_forecast(
df: pd.DataFrame,
date_col: str = "date",
value_col: str = "units",
item_col: str = "asin",
prediction_length: int = 30,
time_limit: int = 300
) -> pd.DataFrame:
"""
AutoGluon で複数 SKU の販売を自動予測する。

AutoGluon の強み:
- ゼロ設定: モデル選択やパラメータ調整が不要
- 複数 SKU: 一度の訓練で全 SKU を同時予測
- 自動アンサンブル: 複数モデルを自動で試し最適結果をアンサンブル

Args:
df: 日付、販売量、SKU ID を含む DataFrame
date_col: 日付列名
value_col: 目標値列名
item_col: SKU ID 列名
prediction_length: 予測日数
time_limit: 訓練時間の制限(秒)

Returns:
予測結果 DataFrame
"""
# 1. AutoGluon 形式に変換
ag_df = df.rename(columns={
date_col: "timestamp",
value_col: "target",
item_col: "item_id"
})
ag_df["timestamp"] = pd.to_datetime(ag_df["timestamp"])

ts_df = TimeSeriesDataFrame.from_data_frame(
ag_df,
id_column="item_id",
timestamp_column="timestamp"
)

print(f"データ: {ts_df.num_items} 個の SKU, "
f"{len(ts_df)} レコード")

# 2. 訓練(AutoGluon が最適モデルを自動選択)
predictor = TimeSeriesPredictor(
prediction_length=prediction_length,
target="target",
eval_metric="MAPE", # MAPE を評価指標に
)

predictor.fit(
train_data=ts_df,
time_limit=time_limit, # 訓練時間を制限
presets="medium_quality", # fast / medium / high / best
)

# 3. モデルランキングを確認
leaderboard = predictor.leaderboard(ts_df)
print("\nモデルランキング:")
print(leaderboard[["model", "score_val"]].to_string(index=False))

# 4. 予測を生成
predictions = predictor.predict(ts_df)

print(f"\n予測完了: {ts_df.num_items} 個の SKU × {prediction_length} 日")

return predictions

# 使用例
# df = pd.read_csv("data/daily_sales_all_skus.csv")
# predictions = autogluon_forecast(
# df,
# date_col="date",
# value_col="units",
# item_col="asin",
# prediction_length=30,
# time_limit=600 # 10 分
# )
#
# # ある SKU の予測を確認
# sku_pred = predictions.loc["B0XXXXX"]
# print(sku_pred)
```

> **AutoGluon vs Prophet どう選ぶ?**
> - 単一 SKU の深掘り分析 → Prophet(説明性が強い、祝日と外部変数を追加できる)
> - 100+ SKU の一括予測 → AutoGluon(自動化度が高い、一度で完了)
> - 何を使うか不確実 → まず AutoGluon でベースラインを走らせ、重点 SKU を Prophet で精調
>
> 参考: [AutoGluon 時系列ドキュメント](https://auto.gluon.ai/stable/tutorials/timeseries/index.html)

### 3.4 BERTopic Review 主題分析

BERTopic は大量の Review テキストから主題を自動発見し、顧客が何を言っているかの理解を助ける。手動で Review を読むより 100 倍効率的。

```python
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import pandas as pd

def analyze_review_topics(
reviews: list[str],
language: str = "english",
nr_topics: int = "auto",
min_topic_size: int = 10
) -> tuple:
"""
BERTopic で Review テキストから主題を自動発見する。

動作原理:
1. Sentence-BERT で各 Review をベクトルに変換
2. UMAP で次元削減
3. HDBSCAN でクラスタリング
4. c-TF-IDF で各主題のキーワードを抽出

Args:
reviews: Review テキストのリスト
language: 言語 ("english" か "chinese")
nr_topics: 主題数("auto" で自動決定)
min_topic_size: 最小主題サイズ(Review 数がこれ未満の主題は統合される)

Returns:
(topic_model, topics, probs)
- topic_model: 訓練済みの BERTopic モデル
- topics: 各 Review の主題番号
- probs: 各 Review が各主題に属する確率
"""
# 埋め込みモデルを選択
if language == "chinese":
embedding_model = SentenceTransformer(
"paraphrase-multilingual-MiniLM-L12-v2"
)
else:
embedding_model = SentenceTransformer(
"all-MiniLM-L6-v2"
)

# BERTopic モデルを作成
topic_model = BERTopic(
embedding_model=embedding_model,
nr_topics=nr_topics,
min_topic_size=min_topic_size,
language=language,
verbose=True
)

# 訓練
topics, probs = topic_model.fit_transform(reviews)

# 主題概要を出力
topic_info = topic_model.get_topic_info()
print("\n発見された主題:")
for _, row in topic_info.head(10).iterrows():
if row["Topic"] != -1: # -1 は外れ値
print(f"主題 {row['Topic']}: {row['Name']} "
f"({row['Count']} 件の Review)")

return topic_model, topics, probs

def get_topic_summary(
topic_model: BERTopic,
reviews: list[str],
topics: list[int],
ratings: list[int] = None
) -> pd.DataFrame:
"""
主題サマリレポートを生成する。

Args:
topic_model: 訓練済みモデル
reviews: Review テキスト
topics: 主題番号
ratings: 評価(1-5)、各主題の感情傾向の分析用

Returns:
主題サマリ DataFrame
"""
summary_data = []
topic_info = topic_model.get_topic_info()

for _, row in topic_info.iterrows():
topic_id = row["Topic"]
if topic_id == -1:
continue

# その主題のキーワードを取得
keywords = topic_model.get_topic(topic_id)
keyword_str = ", ".join([w for w, _ in keywords[:5]])

# その主題の Review インデックスを取得
topic_mask = [t == topic_id for t in topics]
topic_reviews = [r for r, m in zip(reviews, topic_mask) if m]

entry = {
"topic_id": topic_id,
"keywords": keyword_str,
"review_count": len(topic_reviews),
"sample_review": topic_reviews[0][:200] if topic_reviews else "",
}

# 評価データがあれば、その主題の平均評価を計算
if ratings:
topic_ratings = [r for r, m in zip(ratings, topic_mask) if m]
entry["avg_rating"] = round(sum(topic_ratings) / len(topic_ratings), 2) if topic_ratings else None
entry["negative_pct"] = round(
sum(1 for r in topic_ratings if r <= 2) / len(topic_ratings) * 100, 1
) if topic_ratings else None

summary_data.append(entry)

summary = pd.DataFrame(summary_data)

if "avg_rating" in summary.columns:
summary = summary.sort_values("avg_rating", ascending=True)

return summary

# 使用例
# reviews_df = pd.read_csv("data/reviews.csv")
# reviews = reviews_df["review_text"].tolist()
# ratings = reviews_df["rating"].tolist()
#
# topic_model, topics, probs = analyze_review_topics(reviews, language="english")
#
# # 主題サマリを生成
# summary = get_topic_summary(topic_model, reviews, topics, ratings)
# print(summary.to_string(index=False))
#
# # 主題分布を可視化
# fig = topic_model.visualize_topics()
# fig.write_html("output/review_topics.html")
#
# # 主題の時系列変化を確認(日付データが必要)
# timestamps = reviews_df["date"].tolist()
# topics_over_time = topic_model.topics_over_time(reviews, topics, timestamps)
# fig = topic_model.visualize_topics_over_time(topics_over_time)
# fig.write_html("output/topics_over_time.html")
```

> **BERTopic の実際の価値**: 競合 Review が 5000 件あるとすると、手動で読み終えるのに数日かかる。BERTopic は 5 分で教えてくれる: 主題 1 は「電池持ちが悪い」(平均評価 2.1)、主題 2 は「画質が良い」(平均評価 4.5)、主題 3 は「アプリが使いにくい」(平均評価 1.8)。これが製品改善の方向を直接示す。
>
> 参考: [BERTopic 公式ドキュメント](https://maartengr.github.io/BERTopic/) | [BERTopic ベストプラクティス](https://maartengr.github.io/BERTopic/getting_started/best_practices/best_practices.html)

### 3.5 予測結果を補充判断に変換

予測自体は目的でなく、補充判断が目的。この節は予測結果を [A5 在庫モジュール](../a-operators/a5-inventory.md) の補充ロジックに接続する。

```python
def forecast_to_reorder(
forecast: pd.DataFrame,
current_stock: int,
lead_time_days: int = 30,
safety_stock_days: int = 14,
moq: int = 100
) -> dict:
"""
予測結果を補充提案に変換する。

Args:
forecast: Prophet 予測結果
current_stock: 現在の在庫数
lead_time_days: サプライヤーの納期(日)
safety_stock_days: 安全在庫日数
moq: 最小発注量

Returns:
補充提案の辞書
"""
# 未来の予測データを取得
future_data = forecast[forecast["ds"] > pd.Timestamp.now()]

if future_data.empty:
return {"error": "未来の予測データなし"}

# 日均予測販売を計算(上界で保守的に見積もり)
daily_forecast = future_data["yhat"].mean()
daily_upper = future_data["yhat_upper"].mean()

# 安全在庫 = 安全日数 × 日均販売上界
safety_stock = int(safety_stock_days * daily_upper)

# Lead Time 期間の予想消費
lt_consumption = int(lead_time_days * daily_forecast)

# 再発注点 = Lead Time 消費 + 安全在庫
reorder_point = lt_consumption + safety_stock

# 現在在庫が支えられる日数
days_of_stock = int(current_stock / daily_forecast) if daily_forecast > 0 else 999

# 提案発注量 = 90 日予測需要 - 現在在庫 + 安全在庫
forecast_90d = int(future_data["yhat"].head(90).sum())
suggested_qty = max(forecast_90d - current_stock + safety_stock, 0)

# MOQ の倍数に切り上げ
if suggested_qty > 0:
suggested_qty = max(
((suggested_qty + moq - 1) // moq) * moq,
moq
)

# 緊急度の判断
if current_stock <= reorder_point * 0.5:
urgency = "緊急補充"
elif current_stock <= reorder_point:
urgency = "補充推奨"
else:
urgency = "在庫十分"

result = {
"urgency": urgency,
"current_stock": current_stock,
"days_of_stock": days_of_stock,
"daily_forecast": round(daily_forecast, 1),
"safety_stock": safety_stock,
"reorder_point": reorder_point,
"suggested_qty": suggested_qty,
"forecast_90d": forecast_90d,
"lead_time_days": lead_time_days,
}

print(f"\n補充提案:")
print(f"状態: {urgency}")
print(f"現在在庫: {current_stock} 件(あと {days_of_stock} 日支えられる)")
print(f"日均予測: {daily_forecast:.1f} 件/日")
print(f"安全在庫: {safety_stock} 件")
print(f"再発注点: {reorder_point} 件")
print(f"提案発注: {suggested_qty} 件(MOQ={moq})")

return result

# 使用例
# reorder = forecast_to_reorder(
# forecast=forecast,
# current_stock=500,
# lead_time_days=30,
# safety_stock_days=14,
# moq=200
# )
```

---

## 4. モデル評価

### 4.1 評価指標

| 指標 | 公式 | 意味 | 向くシーン |
|------|------|------|------------|
| MAE | `mean(abs(actual - predicted))` | 平均絶対誤差 | 汎用、異常値に鈍感 |
| RMSE | `sqrt(mean((actual - predicted)²))` | 二乗平均平方根誤差 | 大誤差を罰する、大偏差を許容しないシーンに向く |
| MAPE | `mean(abs((actual - predicted) / actual)) × 100%` | 平均絶対百分率誤差 | SKU 横断比較(販売基数に影響されない) |
| WAPE | `sum(abs(actual - predicted)) / sum(actual) × 100%` | 加重絶対百分率誤差 | 低販売時に MAPE が爆発するのを回避 |

**EC シーンは WAPE を推奨**: MAPE は実販売が 0 に近いとき無限大に近づく(0 に近い数で割る)が、WAPE は総販売を分母にするのでより安定。

```python
def evaluate_forecast(
    actual: pd.Series,
    predicted: pd.Series
) -> dict:
    """
    予測評価指標を計算する。

    Args:
        actual: 実績値
        predicted: 予測値

    Returns:
        評価指標の辞書
    """
    actual = actual.values
    predicted = predicted.values

    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))

    # MAPE(実績値が 0 の日を除外)
    nonzero_mask = actual > 0
    if nonzero_mask.any():
        mape = np.mean(
            np.abs((actual[nonzero_mask] - predicted[nonzero_mask])
                   / actual[nonzero_mask])
        ) * 100
    else:
        mape = float("inf")

    # WAPE(より頑健)
    wape = np.sum(np.abs(actual - predicted)) / np.sum(actual) * 100 if np.sum(actual) > 0 else float("inf")

    metrics = {
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "MAPE": round(mape, 2),
        "WAPE": round(wape, 2),
    }

    print("評価結果:")
    for k, v in metrics.items():
        unit = "%" if k in ("MAPE", "WAPE") else "units"
        print(f"{k}: {v} {unit}")

    return metrics
```

**MAPE 参考ベンチマーク(EC シーン):**

| MAPE | 評価 | 説明 |
|------|------|------|
| < 15% | 優秀 | 安定した老舗商品、データ十分 |
| 15-25% | 良好 | 大半の SKU の合理的な水準 |
| 25-40% | 許容 | 新商品や変動の大きいカテゴリ |
| > 40% | 要改善 | データ品質かモデル設定を確認 |

### 4.2 バックテスト(Backtesting)

バックテストは予測モデルを検証する最も信頼できる方法: 履歴データで「当時このモデルで予測していたらどうだったか」をシミュレートする。

```python
def backtest_prophet(
df: pd.DataFrame,
initial_days: int = 180,
horizon_days: int = 30,
period_days: int = 30
) -> pd.DataFrame:
"""
Prophet バックテスト: ローリングウィンドウ検証。

原理:
1. 最初の initial_days 日のデータで訓練
2. 今後 horizon_days 日を予測
3. 実績値と比較
4. ウィンドウを前へ period_days 日スライド、繰り返し

Args:
df: Prophet 形式データ
initial_days: 初期訓練データの日数
horizon_days: 毎回予測する日数
period_days: ウィンドウのスライド歩幅

Returns:
バックテスト結果 DataFrame
"""
from prophet.diagnostics import cross_validation, performance_metrics

model = Prophet(
yearly_seasonality=True,
weekly_seasonality=True,
changepoint_prior_scale=0.1,
interval_width=0.8,
)
model.fit(df)

# クロスバリデーション
cv_results = cross_validation(
model,
initial=f"{initial_days} days",
period=f"{period_days} days",
horizon=f"{horizon_days} days"
)

# 性能指標を計算
perf = performance_metrics(cv_results)

print("バックテスト結果:")
print(f"MAE: {perf['mae'].mean():.2f}")
print(f"RMSE: {perf['rmse'].mean():.2f}")
print(f"MAPE: {perf['mape'].mean() * 100:.2f}%")

return cv_results, perf

# 使用例
# cv_results, perf = backtest_prophet(prophet_df, initial_days=180, horizon_days=30)
#
# # バックテスト結果を可視化
# from prophet.plot import plot_cross_validation_metric
# fig = plot_cross_validation_metric(cv_results, metric="mape")
# plt.savefig("output/backtest_mape.png", dpi=150)
```

### 4.3 予測区間の使い方

予測値は点推定だが、業務判断は不確実性を考慮する必要がある。Prophet の予測区間は「真の値が高確率でこの範囲に入る」と教えてくれる。

| 判断シーン | どの値を使うか | 理由 |
|------------|----------------|------|
| 補充量の計算 | `yhat_upper`(上界) | 多めに備えるほうがよい、欠品損失 > 在庫コスト |
| 販売目標の設定 | `yhat`(中央値) | 目標は最も可能性の高い結果であるべき |
| 悲観シナリオ分析 | `yhat_lower`(下界) | 最悪ケースのキャッシュフローを評価 |
| 倉庫スペース計画 | `yhat_upper`(上界) | 十分な保管スペースを確保 |

---

## 5. 実践プロジェクト: SKU 販売予測システムの構築

### 5.1 プロジェクトアーキテクチャ

```
sales-forecaster/
config.py # 設定(データパス、モデルパラメータ)
requirements.txt # 依存関係

data/ # データディレクトリ
raw/ # 生の販売データ
processed/ # クレンジング後のデータ

models/ # モデル保存
prophet/ # Prophet モデルファイル

src/
data_prep.py # データ準備(クレンジング、欠品処理)
prophet_model.py # Prophet 訓練と予測
autogluon_model.py # AutoGluon 一括予測
review_analysis.py # BERTopic Review 分析
evaluator.py # モデル評価とバックテスト
reorder.py # 補充判断

output/ # 出力
forecasts/ # 予測結果 CSV
reports/ # HTML レポート
plots/ # グラフ

run_forecast.py # メインエントリ: 単 SKU 予測
run_batch_forecast.py # 一括予測エントリ
README.md
```

### 5.2 メインエントリスクリプト

```python
# run_forecast.py 単 SKU 販売予測
import argparse
import pandas as pd
from pathlib import Path

from src.data_prep import prepare_prophet_data, handle_stockout
from src.prophet_model import (
train_prophet_with_holidays,
make_forecast,
plot_forecast
)
from src.evaluator import evaluate_forecast, backtest_prophet
from src.reorder import forecast_to_reorder

def run(
data_path: str,
asin: str = None,
forecast_days: int = 90,
current_stock: int = None,
lead_time: int = 30
):
"""
完全な予測フロー: データ準備 → 訓練 → 予測 → 評価 → 補充提案
"""
print(f"予測フローを開始")

# 1. データをロード
df = pd.read_csv(data_path)
if asin and "asin" in df.columns:
df = df[df["asin"] == asin]
print(f"SKU: {asin}")

# 2. データ準備
prophet_df = prepare_prophet_data(df, date_col="date", value_col="units")
prophet_df = handle_stockout(prophet_df, units_col="y")

# 3. 訓練(祝日効果付き)
model = train_prophet_with_holidays(prophet_df, changepoint_prior=0.1)

# 4. 予測
forecast = make_forecast(model, periods=forecast_days)

# 5. 評価(最後の 30 日で検証)
if len(prophet_df) > 30:
train_df = prophet_df.iloc[:-30]
test_df = prophet_df.iloc[-30:]

eval_model = train_prophet_with_holidays(train_df)
eval_forecast = make_forecast(eval_model, periods=30)

eval_pred = eval_forecast.tail(30)["yhat"].values
eval_actual = test_df["y"].values
metrics = evaluate_forecast(
pd.Series(eval_actual), pd.Series(eval_pred)
)

# 6. 可視化
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

plot_forecast(
model, forecast, actual_df=prophet_df,
title=f"{'ASIN ' + asin if asin else 'SKU'} 販売予測 ({forecast_days}日)"
)

# 7. 予測結果を保存
forecast_output = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(forecast_days)
forecast_output.to_csv(
output_dir / f"forecast_{asin or 'sku'}_{forecast_days}d.csv",
index=False
)

# 8. 補充提案
if current_stock is not None:
reorder = forecast_to_reorder(
forecast,
current_stock=current_stock,
lead_time_days=lead_time
)

print(f"\n予測完了!結果は output/ に保存済み")

if __name__ == "__main__":
parser = argparse.ArgumentParser(description="SKU 販売予測")
parser.add_argument("--data", required=True, help="販売データ CSV パス")
parser.add_argument("--asin", help="ASIN")
parser.add_argument("--days", type=int, default=90, help="予測日数")
parser.add_argument("--stock", type=int, help="現在在庫")
parser.add_argument("--lead-time", type=int, default=30, help="納期(日)")
args = parser.parse_args()

run(
data_path=args.data,
asin=args.asin,
forecast_days=args.days,
current_stock=args.stock,
lead_time=args.lead_time
)
```

```bash
# 実行例
python3 run_forecast.py --data data/daily_sales.csv --asin B0XXXXX --days 90
python3 run_forecast.py --data data/daily_sales.csv --asin B0XXXXX --stock 500 --lead-time 30
```

---

## 6. よくある罠

| 罠 | 症状 | 解決策 |
|----|------|--------|
| 過学習 | 訓練セット MAPE が非常に低く、テストセット MAPE が非常に高い | `changepoint_prior_scale` を下げる、バックテストで検証 |
| データリーク | 未来データでモデルを訓練(通年データで Q3 を予測など) | 訓練/テストセットを時間で厳格に分割、`cross_validation` を使う |
| 欠品を無視 | 欠品期間の 0 を真の需要として扱う | `handle_stockout` 関数で処理 |
| 外部要因を無視 | 競合の値下げで販売急増、モデルが説明できない | 外部回帰変数を追加(競合価格、広告費用) |
| 予測値が負 | Prophet が負の予測を出しうる | `.clip(lower=0)` で切り捨て |
| 季節性の不整合 | 週データで訓練したのに日次予測を期待 | 訓練データと予測頻度を一致させる |
| 大型セールの過学習 | モデルが大型セールを常規パターンとして扱う | `holidays` パラメータで大型セールイベントを明示的にモデリング |
| 新商品データなし | 新 ASIN に販売履歴がない | 類似品の販売曲線で類推、または AutoGluon の転移学習を使う |

---

## 7. 学習リソース

### 7.1 無料講座とドキュメント

| リソース | プラットフォーム | 長さ | 向く相手 | リンク |
|----------|------------------|------|----------|--------|
| Prophet 公式チュートリアル | Meta | 2h | 時系列入門 | [facebook.github.io/prophet](https://facebook.github.io/prophet/) |
| Kaggle: Time Series | Kaggle | 5h | 時系列基礎 | [kaggle.com/learn/time-series](https://www.kaggle.com/learn/time-series) |
| Kaggle: Intro to ML | Kaggle | 4h | ML ゼロ基礎 | [kaggle.com/learn/intro-to-machine-learning](https://www.kaggle.com/learn/intro-to-machine-learning) |
| Google ML Crash Course | Google | 15h | ML を体系的に学ぶ | [developers.google.com/machine-learning/crash-course](https://developers.google.com/machine-learning/crash-course) |
| AutoGluon 時系列チュートリアル | Amazon | 2h | 自動化予測 | [auto.gluon.ai](https://auto.gluon.ai/) |
| BERTopic ドキュメント | GitHub | 3h | Review 主題分析 | [maartengr.github.io/BERTopic](https://maartengr.github.io/BERTopic/) |
| Darts ドキュメント | Unit8 | 3h | 複数モデル比較 | [unit8co.github.io/darts](https://unit8co.github.io/darts/) |

### 7.2 おすすめ GitHub リポジトリ

| リポジトリ | Star | 用途 |
|------------|------|------|
| [Prophet](https://github.com/facebook/prophet) | 18k+ | 時系列予測の中核ライブラリ |
| [AutoGluon](https://github.com/autogluon/autogluon) | 8k+ | 自動化 ML フレームワーク |
| [BERTopic](https://github.com/MaartenGr/BERTopic) | 6k+ | 主題モデリング |
| [Darts](https://github.com/unit8co/darts) | 8k+ | 時系列ツールボックス |
| [OR-Tools](https://github.com/google/or-tools) | 11k+ | 数理最適化 |

Content rephrased for compliance with licensing restrictions. Sources cited inline.

## 9. 完了チェック

- [ ] Prophet で実際の SKU の 90 日販売予測を行い、予測値と信頼区間を出力
- [ ] EC 大型セールの祝日効果(Prime Day、BFCM)を追加、祝日ありなしの予測精度差を比較
- [ ] バックテスト(backtesting)でモデルを検証、MAPE < 30%
- [ ] AutoGluon で 10+ SKU の一括予測を行い、モデルランキングを確認
- [ ] BERTopic で一組の Review テキストを分析、最低 3 つの意味ある主題を発見
- [ ] 予測結果を補充提案に変換(再発注点と提案発注量を計算)

以上をすべて完了すれば、EC 予測モデリングの中核スキルを習得しています。次は [B3 RAG 知識ベース](b3-rag-knowledge-base.md)へ。RAG ベースのインテリジェント Q&A システムの構築方法を学びます。

---

## 付録

### 付録 A: モデル選択の決定木

```
あなたの予測ニーズは何?

単一 SKU の深掘り予測
1 年以上の履歴データがある?
はい → Prophet + 祝日 + 外部変数
いいえ → Prophet 基本版 / 移動平均
なぜこう予測するか説明が必要?
はい → Prophet(トレンド+季節性に分解可能)
いいえ → AutoGluon(最適モデルを自動選択)

100+ SKU の一括予測
GPU がある?
はい → AutoGluon (high_quality preset)
いいえ → AutoGluon (medium_quality preset)
素早く結果を出す必要?
はい → AutoGluon (fast_training preset)

Review テキスト分析
主題発見 → BERTopic
感情分類 → scikit-learn + TF-IDF / BERT
キーワード抽出 → BERTopic の c-TF-IDF

補充最適化
簡単なルール → 予測値 + 安全在庫公式
多制約最適化 → OR-Tools(MOQ、倉容、資金を考慮)
```

### 付録 B: コード早見表

```python
# === Prophet 基礎 ===
from prophet import Prophet

df = pd.DataFrame({"ds": dates, "y": values}) # 必ず ds と y
model = Prophet()
model.fit(df)
future = model.make_future_dataframe(periods=90)
forecast = model.predict(future)
model.plot(forecast) # 予測図
model.plot_components(forecast) # 成分分解図

# === Prophet 祝日 ===
holidays = pd.DataFrame({
"holiday": ["prime_day"], "ds": ["2025-07-12"],
"lower_window": [-3], "upper_window": [2]
})
model = Prophet(holidays=holidays)

# === Prophet 外部変数 ===
model = Prophet()
model.add_regressor("ad_spend")
model.fit(df) # df に ad_spend 列が必要
future["ad_spend"] = 500 # 予測時にも提供

# === Prophet バックテスト ===
from prophet.diagnostics import cross_validation, performance_metrics
cv = cross_validation(model, initial="180 days", period="30 days", horizon="30 days")
perf = performance_metrics(cv)

# === AutoGluon ===
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
ts = TimeSeriesDataFrame.from_data_frame(df, id_column="item_id", timestamp_column="timestamp")
predictor = TimeSeriesPredictor(prediction_length=30, target="target")
predictor.fit(ts, time_limit=300)
predictions = predictor.predict(ts)

# === BERTopic ===
from bertopic import BERTopic
model = BERTopic(language="english", min_topic_size=10)
topics, probs = model.fit_transform(documents)
model.get_topic_info() # 主題概要
model.visualize_topics() # 主題可視化

# === 評価指標 ===
mae = np.mean(np.abs(actual - predicted))
rmse = np.sqrt(np.mean((actual - predicted) ** 2))
mape = np.mean(np.abs((actual - predicted) / actual)) * 100
wape = np.sum(np.abs(actual - predicted)) / np.sum(actual) * 100
```

### 付録 C: 依存関係のインストール

```bash
# 基礎予測
pip install prophet pandas numpy matplotlib

# AutoGluon(大きい、個別インストール推奨)
pip install autogluon.timeseries

# Review 分析
pip install bertopic sentence-transformers

# 数理最適化
pip install ortools

# 全部インストール
pip install prophet pandas numpy matplotlib \
autogluon.timeseries \
bertopic sentence-transformers \
ortools scikit-learn \
statsmodels
```

> Prophet は一部のシステムでインストール問題に遭遇しうる(pystan/cmdstanpy に依存)。インストール失敗時は [Prophet インストールガイド](https://facebook.github.io/prophet/docs/installation.html) を参照するか Google Colab(大半の依存関係がプリインストール済み)を使う。
---

[< B1 データパイプライン](b1-data-pipeline.md) | [Path 総覧](../README.md) | [B3 RAG >](b3-rag-knowledge-base.md)
