[🇨🇳 中文](../../paths/b-developers/b2-prediction-models.md) | 🇺🇸 English

# B2. Prediction Models & Intelligent Decision-Making

> **Path**: Path B: Developers · **Module**: B2
> **Last Updated**: 2026-03-12
> **Difficulty**: Intermediate → Advanced
> **Prerequisites**: B1 Data Pipeline Fundamentals (pandas, data cleaning), Python basics
> **Estimated Time**: 1 hour/day, 23 weeks
---

[Hub Home](../../README.md) · [Path B Overview](README.md)

```mermaid
flowchart LR
B1["B1 Data Pipeline"]
B1 --> B2
B2[" B2 Prediction Models<br/>(Current)"]:::current
B2 --> B3
B3["B3 RAG Knowledge Base"]
B3 --> B4
B4["B4 Agent Workflow"]
B4 --> B5
B5["B5 Local Model Deployment"]
classDef current fill:#ff9900,stroke:#333,color:#fff,font-weight:bold
```

---

## Module Navigation

1. [Prediction Methodology](#1-prediction-methodology) · 2. [Tool Landscape](#2-tool-landscape) · 3. [Hands-On Code](#3-hands-on-code) · 4. [Model Evaluation](#4-model-evaluation) · 5. [Practical Project](#5-practical-project-building-a-sku-sales-forecasting-system) · 6. [Common Pitfalls](#6-common-pitfalls) · 7. [Learning Resources](#7-learning-resources) · 8. [ OpenClaw Automation](#8-automating-forecasting-with-openclaw) · 9. [Completion Checklist](#9-completion-checklist)


## What You'll Build in This Module

A sales forecasting model + Review topic analysis system.

After completing this module, you'll be able to:
- Use Prophet to generate 30/60/90-day sales forecasts for SKUs, with predicted values and confidence intervals
- Understand the core principles of time series forecasting (trend + seasonality + noise decomposition)
- Handle e-commerce-specific forecasting challenges: promotional spikes, new product cold starts, competitor effects
- Use AutoGluon for zero-configuration modeling that automatically selects the best algorithm
- Use BERTopic to automatically discover topics and sentiment trends from Review text
- Convert forecast results into replenishment decisions (connecting to [A5 Inventory Module](../a-operators/a5-inventory.md))
- Evaluate model quality using MAPE/MAE/RMSE and validate forecast reliability with backtesting

---

## 1. Prediction Methodology

> **Related Reading**: [A5 Inventory & Supply Chain](../a-operators/a5-inventory.md#a5-inventory-supply-chain) See A5 for how sales forecasting applies to inventory replenishment decisions. · [D3 Cross-Platform AI Collaboration Strategy](../d-platforms/cross-platform-strategy.md#8-cross-platform-pricing-strategy) See D3 for cross-platform demand forecasting.

### 1.1 First Principles of Time Series Forecasting

Any time series data can be decomposed into three components:

```
Observed Value = Trend + Seasonality + Residual (Noise)
```

| Component | Meaning | E-commerce Example |
|-----------|---------|-------------------|
| Trend | Long-term upward or downward direction | Sales gradually increase month-over-month after a new product launch; legacy products enter decline |
| Seasonality | Repeating patterns at fixed intervals | Highest sales on Mondays (weekend orders arrive Monday); Q4 peak season |
| Noise | Unexplainable random fluctuations | An influencer suddenly features the product, sales spike for one day then return to normal |

**Additive vs. Multiplicative Models:**

- **Additive model**: `y = trend + seasonality + noise` Seasonal fluctuation amplitude is fixed (e.g., Q4 sells 1,000 more units every year)
- **Multiplicative model**: `y = trend × seasonality × noise` Seasonal fluctuation amplitude scales with the trend (e.g., Q4 sells 30% more every year)

E-commerce scenarios are typically more accurate with **multiplicative models**, because the larger the sales base, the larger the absolute seasonal fluctuation.

**Decomposition Visualization:**

```python
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti TC", "Arial"]
matplotlib.rcParams["axes.unicode_minus"] = False

def decompose_sales(df: pd.DataFrame, date_col: str = "date", value_col: str = "units"):
"""
将销量时间序列分解为趋势、季节性、噪声三个成分。

Args:
df: 包含日期和销量的 DataFrame
date_col: 日期列名
value_col: 销量列名
"""
ts = df.set_index(date_col)[value_col]
ts = ts.asfreq("D").fillna(method="ffill") # 补齐缺失日期

# 乘法分解，周期=7（周季节性）
result = seasonal_decompose(ts, model="multiplicative", period=7)

fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
result.observed.plot(ax=axes[0], title="原始数据 (Observed)")
result.trend.plot(ax=axes[1], title="趋势 (Trend)")
result.seasonal.plot(ax=axes[2], title="季节性 (Seasonality)")
result.resid.plot(ax=axes[3], title="噪声 (Residual)")

plt.tight_layout()
plt.savefig("output/decomposition.png", dpi=150)
plt.show()

return result

# 使用示例
# df = pd.read_csv("data/daily_sales.csv")
# result = decompose_sales(df, date_col="date", value_col="units")
```

> **Key Insight**: If the "noise" component after decomposition still shows obvious patterns (e.g., large residuals during every major promotion), it means your model is missing event modeling for promotions. This is exactly what Prophet's `holidays` parameter is designed to solve.

### 1.2 Unique Challenges of E-commerce Forecasting

E-commerce sales forecasting is harder than traditional retail due to several unique disrupting factors:

| Challenge | Symptom | Impact | Mitigation Strategy |
|-----------|---------|--------|---------------------|
| Promotional spikes | Sales surge 520x during Prime Day/BFCM | Model gets skewed by extreme values | Model promotions as special events (Prophet holidays) |
| New product cold start | New ASIN has no historical data | Time series forecasting is impossible | Use analogous products' sales curves for proxy forecasting |
| Competitor effects | Competitor price drops/stockouts cause sudden changes in your sales | External factors can't be learned from your own data | Add external regressors (competitor price, BSR) |
| Ad dependency | Sales cliff-drop after stopping ads | Organic and ad-driven sales are mixed together | Separate organic and ad traffic for independent forecasting |
| Inventory constraints | Sales are 0 during stockouts (not real demand) | Zeros in historical data don't mean "no demand" | Stockout periods need special handling or exclusion |
| Layered seasonality | Weekly + monthly + yearly seasonality coexist | A single-period model isn't enough | Prophet supports automatic multi-seasonality modeling |

**Stockout Data Handling (Critical!):**

```python
def handle_stockout(df: pd.DataFrame, units_col: str = "units") -> pd.DataFrame:
"""
处理断货期间的零销量数据。

断货期间销量为 0 不代表需求为 0。
策略：用断货前后的平均销量填充，避免模型学到"某些天需求为 0"。
"""
df = df.copy()

# 标记连续零销量（可能是断货）
df["is_zero"] = df[units_col] == 0
df["zero_streak"] = (
df["is_zero"]
.groupby((~df["is_zero"]).cumsum())
.cumsum()
)

# 连续 3 天以上零销量视为断货（而非真实零需求）
stockout_mask = df["zero_streak"] >= 3

if stockout_mask.any():
# 用前后各 7 天的非零均值填充
rolling_mean = (
df[~stockout_mask][units_col]
.rolling(window=7, min_periods=1)
.mean()
)
df.loc[stockout_mask, units_col] = rolling_mean.reindex(
df.index
).ffill().bfill()

stockout_days = stockout_mask.sum()
print(f" 检测到 {stockout_days} 天疑似断货，已用滚动均值填充")

df = df.drop(columns=["is_zero", "zero_streak"])
return df
```

### 1.3 When to Use Simple Rules vs. ML Models

Not every forecast needs machine learning. Choosing the right method matters more than choosing the most complex one:

| Scenario | Recommended Method | Rationale |
|----------|-------------------|-----------|
| Stable legacy product, >1 year history | Prophet / Exponential Smoothing | Sufficient data, time series models work well |
| New product launch, <3 months | Analogy method + manual adjustment | Insufficient data, ML models will overfit |
| Promotional stocking | Last year same period × growth factor + manual adjustment | Promotions are irregular events with too few historical samples |
| Multi-SKU batch forecasting | AutoGluon / LightGBM | High automation, suitable for batch processing |
| Explainability needed | Prophet | Decomposable into trend + seasonality, business users can understand |
| Accuracy-focused | Ensemble methods (multi-model weighted) | Single models have bias, ensembles can complement each other |

**Decision Framework:**

```
Historical data > 1 year?
Yes → Sales stable?
Yes → Prophet (simple and efficient)
No → Prophet + external variables / AutoGluon
No → Historical data > 3 months?
Yes → Prophet (short cycle) / Moving Average
No → Analogy method (find similar products' historical data)
```

---

## 2. Tool Landscape

| Tool | Type | Difficulty | Best For | Installation |
|------|------|------------|----------|-------------|
| [Prophet](https://facebook.github.io/prophet/) | Time Series | Beginner | Single-SKU sales forecasting, easiest to get started | `pip install prophet` |
| [Darts](https://unit8co.github.io/darts/) | Time Series | Intermediate | Comparing multiple models | `pip install darts` |
| [AutoGluon](https://auto.gluon.ai/) | Automated ML | Beginner | Zero ML knowledge batch modeling | `pip install autogluon.timeseries` |
| [BERTopic](https://maartengr.github.io/BERTopic/) | NLP Topic Modeling | Intermediate | Review text topic discovery | `pip install bertopic` |
| [OR-Tools](https://developers.google.com/optimization) | Operations Research | Advanced | Replenishment strategy optimization | `pip install ortools` |
| [scikit-learn](https://scikit-learn.org/) | General ML | Intermediate | Feature engineering, regression, classification | `pip install scikit-learn` |

**Recommendations:**
- Just starting out → Begin with Prophet you can get results in an afternoon
- Want automation → AutoGluon zero-config, automatically selects the best model
- Need Review analysis → BERTopic automatically discovers review topics
- Need to optimize reorder quantities → OR-Tools mathematical programming for optimal solutions

---

## 3. Hands-On Code

### 3.1 Prophet Sales Forecasting (Complete Workflow)

Prophet is Meta's open-source time series forecasting library, purpose-built for business forecasting. Its core strengths:
- Automatically handles missing values and outliers
- Built-in holiday effects
- Interpretable decomposition results (trend + seasonality + holidays)
- Friendly for non-specialists

**Complete Code: Data Preparation → Training → Forecasting → Evaluation → Visualization**

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
# Step 1: 数据准备
# ============================================================

def prepare_prophet_data(
df: pd.DataFrame,
date_col: str = "date",
value_col: str = "units"
) -> pd.DataFrame:
"""
将业务数据转换为 Prophet 要求的格式。

Prophet 要求两列：
- ds: 日期列（datetime 类型）
- y: 目标值列（数值类型）

Args:
df: 原始数据
date_col: 日期列名
value_col: 目标值列名

Returns:
Prophet 格式的 DataFrame
"""
prophet_df = df[[date_col, value_col]].copy()
prophet_df.columns = ["ds", "y"]

# 确保日期格式正确
prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])
prophet_df["y"] = pd.to_numeric(prophet_df["y"], errors="coerce")

# 按日期排序并去重（同一天多条记录则求和）
prophet_df = prophet_df.groupby("ds")["y"].sum().reset_index()
prophet_df = prophet_df.sort_values("ds").reset_index(drop=True)

# 补齐缺失日期（用 0 填充，后续可用断货处理逻辑替换）
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

print(f" 数据准备完成: {len(prophet_df)} 天")
print(f" 日期范围: {prophet_df['ds'].min().date()} → {prophet_df['ds'].max().date()}")
print(f" 日均销量: {prophet_df['y'].mean():.1f}")

return prophet_df

# ============================================================
# Step 2: 训练模型
# ============================================================

def train_prophet(
df: pd.DataFrame,
yearly: bool = True,
weekly: bool = True,
daily: bool = False,
changepoint_prior: float = 0.05
) -> Prophet:
"""
训练 Prophet 模型。

Args:
df: Prophet 格式数据（ds, y 两列）
yearly: 是否启用年季节性
weekly: 是否启用周季节性
daily: 是否启用日季节性（通常不需要）
changepoint_prior: 趋势变化点灵敏度
- 值越大，模型越容易捕捉趋势变化（但可能过拟合）
- 值越小，趋势越平滑（但可能欠拟合）
- 默认 0.05，电商场景建议 0.1-0.3（变化较快）

Returns:
训练好的 Prophet 模型
"""
model = Prophet(
yearly_seasonality=yearly,
weekly_seasonality=weekly,
daily_seasonality=daily,
changepoint_prior_scale=changepoint_prior,
interval_width=0.8, # 80% 置信区间
)

model.fit(df)
print(" 模型训练完成")

return model

# ============================================================
# Step 3: 生成预测
# ============================================================

def make_forecast(
model: Prophet,
periods: int = 90,
freq: str = "D"
) -> pd.DataFrame:
"""
生成未来 N 天的预测。

Args:
model: 训练好的 Prophet 模型
periods: 预测天数
freq: 频率（D=天, W=周, M=月）

Returns:
预测结果 DataFrame，包含：
- ds: 日期
- yhat: 预测值
- yhat_lower: 预测下界
- yhat_upper: 预测上界
- trend: 趋势成分
- weekly: 周季节性成分
- yearly: 年季节性成分
"""
future = model.make_future_dataframe(periods=periods, freq=freq)
forecast = model.predict(future)

# 预测值不能为负（销量最小为 0）
forecast["yhat"] = forecast["yhat"].clip(lower=0)
forecast["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)

print(f" 预测完成: 未来 {periods} 天")
print(f" 预测均值: {forecast['yhat'].tail(periods).mean():.1f}")
print(f" 预测区间: [{forecast['yhat_lower'].tail(periods).mean():.1f}, "
f"{forecast['yhat_upper'].tail(periods).mean():.1f}]")

return forecast

# ============================================================
# Step 4: 可视化
# ============================================================

def plot_forecast(
model: Prophet,
forecast: pd.DataFrame,
actual_df: pd.DataFrame = None,
title: str = "SKU 销量预测"
):
"""
绘制预测结果图。

Args:
model: Prophet 模型
forecast: 预测结果
actual_df: 实际数据（用于对比）
title: 图表标题
"""
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# 图 1: 预测 vs 实际
ax1 = axes[0]
ax1.plot(forecast["ds"], forecast["yhat"], color="#1a73e8", label="预测值")
ax1.fill_between(
forecast["ds"],
forecast["yhat_lower"],
forecast["yhat_upper"],
alpha=0.2, color="#1a73e8", label="80% 置信区间"
)

if actual_df is not None:
ax1.scatter(
actual_df["ds"], actual_df["y"],
color="#333", s=10, alpha=0.5, label="实际值"
)

ax1.set_title(title, fontsize=14, fontweight="bold")
ax1.set_ylabel("销量 (Units)")
ax1.legend()
ax1.grid(True, alpha=0.3)

# 图 2: 成分分解
ax2 = axes[1]
ax2.plot(forecast["ds"], forecast["trend"], label="趋势", color="#e8710a")
if "weekly" in forecast.columns:
ax2_twin = ax2.twinx()
weekly_data = forecast.drop_duplicates(subset=["ds"]).tail(90)
ax2_twin.plot(
weekly_data["ds"], weekly_data["weekly"],
label="周季节性", color="#0d652d", alpha=0.7
)
ax2_twin.set_ylabel("周季节性")

ax2.set_title("趋势分解", fontsize=14, fontweight="bold")
ax2.set_ylabel("趋势")
ax2.legend(loc="upper left")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("output/forecast.png", dpi=150, bbox_inches="tight")
plt.show()
print(" 图表已保存: output/forecast.png")

# ============================================================
# 完整使用示例
# ============================================================

# # 1. 加载数据
# raw_df = pd.read_csv("data/daily_sales.csv")
# prophet_df = prepare_prophet_data(raw_df, date_col="date", value_col="units")
#
# # 2. 处理断货数据
# prophet_df = handle_stockout(prophet_df, units_col="y")
#
# # 3. 训练模型
# model = train_prophet(prophet_df, changepoint_prior=0.1)
#
# # 4. 预测未来 90 天
# forecast = make_forecast(model, periods=90)
#
# # 5. 可视化
# plot_forecast(model, forecast, actual_df=prophet_df, title="ASIN-B0XXXXX 销量预测")
```

> **changepoint_prior_scale Tuning Guide**: This is Prophet's most important hyperparameter. E-commerce data changes quickly, so start with 0.1. If the forecast curve is too smooth (can't keep up with trend changes), increase to 0.20.3. If the forecast curve is too volatile (overfitting noise), decrease to 0.010.05.

### 3.2 Prophet Advanced: Holiday Effects & External Variables

The basic Prophet model ignores the most important factor in e-commerce: promotional events. Adding holiday effects can significantly improve forecast accuracy.

**Adding E-commerce Promotional Events:**

```python
def create_ecommerce_holidays(years: list[int]) -> pd.DataFrame:
"""
创建电商大促日历。

Prophet 的 holidays 参数接受一个 DataFrame，包含：
- holiday: 事件名称
- ds: 事件日期
- lower_window: 事件前影响天数（负数）
- upper_window: 事件后影响天数
"""
holidays = []

for year in years:
# Prime Day（通常 7 月中旬，持续 2 天）
holidays.append({
"holiday": "prime_day",
"ds": f"{year}-07-12",
"lower_window": -3, # 提前 3 天开始有影响（预热期）
"upper_window": 2, # 结束后 2 天仍有余波
})

# Black Friday（11 月第四个周五）
# 简化处理：固定 11-24 附近
holidays.append({
"holiday": "black_friday",
"ds": f"{year}-11-24",
"lower_window": -7, # BFCM 周提前一周开始
"upper_window": 3, # Cyber Monday 后几天
})

# Cyber Monday
holidays.append({
"holiday": "cyber_monday",
"ds": f"{year}-11-27",
"lower_window": 0,
"upper_window": 1,
})

# 双十一（对中国卖家有影响）
holidays.append({
"holiday": "singles_day",
"ds": f"{year}-11-11",
"lower_window": -3,
"upper_window": 1,
})

# 圣诞节前购物季
holidays.append({
"holiday": "christmas_shopping",
"ds": f"{year}-12-15",
"lower_window": -5,
"upper_window": 10,
})

# 新年后低谷期
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
训练带节假日效应的 Prophet 模型。
"""
if holidays is None:
years = list(range(
df["ds"].dt.year.min(),
df["ds"].dt.year.max() + 2 # 包含预测年份
))
holidays = create_ecommerce_holidays(years)

model = Prophet(
yearly_seasonality=True,
weekly_seasonality=True,
daily_seasonality=False,
changepoint_prior_scale=changepoint_prior,
holidays=holidays,
holidays_prior_scale=10.0, # 节假日效应的灵敏度
interval_width=0.8,
)

model.fit(df)
print(f" 模型训练完成（含 {len(holidays)} 个节假日事件）")

return model
```

**Adding External Regressors (Ad Spend, Competitor Price):**

```python
def train_prophet_with_regressors(
df: pd.DataFrame,
regressor_cols: list[str] = None
) -> Prophet:
"""
训练带外部回归变量的 Prophet 模型。

外部变量可以是：
- ad_spend: 广告花费（广告投入越多，销量越高）
- competitor_price: 竞品价格（竞品涨价，自己销量可能上升）
- bsr_rank: BSR 排名（排名越高，曝光越多）
- coupon_active: 是否有优惠券（0/1）

注意：预测时也需要提供未来的外部变量值！
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

# 添加外部回归变量
regressor_cols = regressor_cols or []
for col in regressor_cols:
if col in df.columns:
model.add_regressor(col, standardize=True)
print(f" 添加回归变量: {col}")

model.fit(df)
print(" 模型训练完成（含外部变量）")

return model

def forecast_with_regressors(
model: Prophet,
periods: int = 90,
future_regressors: pd.DataFrame = None
) -> pd.DataFrame:
"""
带外部变量的预测。

Args:
model: 训练好的模型
periods: 预测天数
future_regressors: 未来的外部变量值
如果不提供，用历史均值填充（不推荐，会降低精度）
"""
future = model.make_future_dataframe(periods=periods)

# 合并未来的外部变量
if future_regressors is not None:
future = future.merge(future_regressors, on="ds", how="left")

# 对缺失的外部变量用历史均值填充
for col in future.columns:
if col not in ["ds"] and future[col].isna().any():
fill_value = future[col].dropna().mean()
future[col] = future[col].fillna(fill_value)
print(f" {col} 有缺失值，用均值 {fill_value:.2f} 填充")

forecast = model.predict(future)
forecast["yhat"] = forecast["yhat"].clip(lower=0)
forecast["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)

return forecast

# 使用示例
# df = prepare_prophet_data(raw_df)
# df["ad_spend"] = ad_data["spend"] # 合并广告花费数据
# df["competitor_price"] = competitor_data["price"] # 合并竞品价格
#
# model = train_prophet_with_regressors(df, regressor_cols=["ad_spend", "competitor_price"])
#
# # 预测时需要提供未来的广告预算和竞品价格预估
# future_regs = pd.DataFrame({
# "ds": pd.date_range("2025-04-01", periods=90, freq="D"),
# "ad_spend": [500] * 90, # 假设未来每天广告预算 $500
# "competitor_price": [29.99] * 90, # 假设竞品价格不变
# })
# forecast = forecast_with_regressors(model, periods=90, future_regressors=future_regs)
```

> **The External Variable Trap**: When forecasting, you need to provide future values for external variables. If you don't know the future ad budget, then adding `ad_spend` as a regressor will actually reduce forecast accuracy. Only add variables whose future values you can reasonably estimate.

### 3.3 AutoGluon Automated Forecasting (Zero-Config Modeling)

AutoGluon is Amazon's open-source automated machine learning framework. Its time series module automatically tries multiple models (Prophet, ETS, DeepAR, Theta, etc.) and selects the best one. Ideal for scenarios where you don't want to manually tune parameters.

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
用 AutoGluon 自动化预测多个 SKU 的销量。

AutoGluon 的优势：
- 零配置：不需要选模型、调参数
- 多 SKU：一次训练，同时预测所有 SKU
- 自动集成：自动尝试多种模型并集成最优结果

Args:
df: 包含日期、销量、SKU 标识的 DataFrame
date_col: 日期列名
value_col: 目标值列名
item_col: SKU 标识列名
prediction_length: 预测天数
time_limit: 训练时间限制（秒）

Returns:
预测结果 DataFrame
"""
# 1. 转换为 AutoGluon 格式
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

print(f" 数据: {ts_df.num_items} 个 SKU, "
f"{len(ts_df)} 条记录")

# 2. 训练（AutoGluon 自动选择最优模型）
predictor = TimeSeriesPredictor(
prediction_length=prediction_length,
target="target",
eval_metric="MAPE", # 用 MAPE 作为评估指标
)

predictor.fit(
train_data=ts_df,
time_limit=time_limit, # 限制训练时间
presets="medium_quality", # fast / medium / high / best
)

# 3. 查看模型排行榜
leaderboard = predictor.leaderboard(ts_df)
print("\n 模型排行榜:")
print(leaderboard[["model", "score_val"]].to_string(index=False))

# 4. 生成预测
predictions = predictor.predict(ts_df)

print(f"\n 预测完成: {ts_df.num_items} 个 SKU × {prediction_length} 天")

return predictions

# 使用示例
# df = pd.read_csv("data/daily_sales_all_skus.csv")
# predictions = autogluon_forecast(
# df,
# date_col="date",
# value_col="units",
# item_col="asin",
# prediction_length=30,
# time_limit=600 # 10 分钟
# )
#
# # 查看某个 SKU 的预测
# sku_pred = predictions.loc["B0XXXXX"]
# print(sku_pred)
```

> **AutoGluon vs. Prophet How to Choose?**
> - Deep analysis of a single SKU → Prophet (strong interpretability, supports holidays and external variables)
> - Batch forecasting 100+ SKUs → AutoGluon (high automation, handles everything at once)
> - Not sure which to use → Run AutoGluon first for a baseline, then fine-tune key SKUs with Prophet
>
> Reference: [AutoGluon Time Series Documentation](https://auto.gluon.ai/stable/tutorials/timeseries/index.html)

### 3.4 BERTopic Review Topic Analysis

BERTopic can automatically discover topics from large volumes of Review text, helping you understand what customers are saying. This is 100x more efficient than reading Reviews manually.

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
用 BERTopic 从 Review 文本中自动发现主题。

工作原理：
1. 用 Sentence-BERT 将每条 Review 转换为向量
2. 用 UMAP 降维
3. 用 HDBSCAN 聚类
4. 用 c-TF-IDF 提取每个主题的关键词

Args:
reviews: Review 文本列表
language: 语言 ("english" 或 "chinese")
nr_topics: 主题数量（"auto" 自动确定）
min_topic_size: 最小主题大小（Review 数少于此值的主题会被合并）

Returns:
(topic_model, topics, probs)
- topic_model: 训练好的 BERTopic 模型
- topics: 每条 Review 的主题编号
- probs: 每条 Review 属于各主题的概率
"""
# 选择嵌入模型
if language == "chinese":
embedding_model = SentenceTransformer(
"paraphrase-multilingual-MiniLM-L12-v2"
)
else:
embedding_model = SentenceTransformer(
"all-MiniLM-L6-v2"
)

# 创建 BERTopic 模型
topic_model = BERTopic(
embedding_model=embedding_model,
nr_topics=nr_topics,
min_topic_size=min_topic_size,
language=language,
verbose=True
)

# 训练
topics, probs = topic_model.fit_transform(reviews)

# 输出主题概览
topic_info = topic_model.get_topic_info()
print("\n 发现的主题:")
for _, row in topic_info.head(10).iterrows():
if row["Topic"] != -1: # -1 是离群点
print(f" 主题 {row['Topic']}: {row['Name']} "
f"({row['Count']} 条 Review)")

return topic_model, topics, probs

def get_topic_summary(
topic_model: BERTopic,
reviews: list[str],
topics: list[int],
ratings: list[int] = None
) -> pd.DataFrame:
"""
生成主题摘要报告。

Args:
topic_model: 训练好的模型
reviews: Review 文本
topics: 主题编号
ratings: 评分（1-5），用于分析每个主题的情感倾向

Returns:
主题摘要 DataFrame
"""
summary_data = []
topic_info = topic_model.get_topic_info()

for _, row in topic_info.iterrows():
topic_id = row["Topic"]
if topic_id == -1:
continue

# 获取该主题的关键词
keywords = topic_model.get_topic(topic_id)
keyword_str = ", ".join([w for w, _ in keywords[:5]])

# 获取该主题的 Review 索引
topic_mask = [t == topic_id for t in topics]
topic_reviews = [r for r, m in zip(reviews, topic_mask) if m]

entry = {
"topic_id": topic_id,
"keywords": keyword_str,
"review_count": len(topic_reviews),
"sample_review": topic_reviews[0][:200] if topic_reviews else "",
}

# 如果有评分数据，计算该主题的平均评分
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

# 使用示例
# reviews_df = pd.read_csv("data/reviews.csv")
# reviews = reviews_df["review_text"].tolist()
# ratings = reviews_df["rating"].tolist()
#
# topic_model, topics, probs = analyze_review_topics(reviews, language="english")
#
# # 生成主题摘要
# summary = get_topic_summary(topic_model, reviews, topics, ratings)
# print(summary.to_string(index=False))
#
# # 可视化主题分布
# fig = topic_model.visualize_topics()
# fig.write_html("output/review_topics.html")
#
# # 查看主题随时间的变化（需要日期数据）
# timestamps = reviews_df["date"].tolist()
# topics_over_time = topic_model.topics_over_time(reviews, topics, timestamps)
# fig = topic_model.visualize_topics_over_time(topics_over_time)
# fig.write_html("output/topics_over_time.html")
```

> **The Real Value of BERTopic**: Say you have 5,000 competitor Reviews reading them all manually would take days. BERTopic can tell you in 5 minutes: Topic 1 is "poor battery life" (avg rating 2.1), Topic 2 is "great image quality" (avg rating 4.5), Topic 3 is "app is hard to use" (avg rating 1.8). This directly points you to product improvement priorities.
>
> Reference: [BERTopic Official Documentation](https://maartengr.github.io/BERTopic/) | [BERTopic Best Practices](https://maartengr.github.io/BERTopic/getting_started/best_practices/best_practices.html)

### 3.5 Converting Forecast Results into Replenishment Decisions

Forecasting itself isn't the goal replenishment decisions are. This section connects forecast results to the replenishment logic in [A5 Inventory Module](../a-operators/a5-inventory.md).

```python
def forecast_to_reorder(
forecast: pd.DataFrame,
current_stock: int,
lead_time_days: int = 30,
safety_stock_days: int = 14,
moq: int = 100
) -> dict:
"""
将预测结果转化为补货建议。

Args:
forecast: Prophet 预测结果
current_stock: 当前库存数量
lead_time_days: 供应商交货周期（天）
safety_stock_days: 安全库存天数
moq: 最小起订量

Returns:
补货建议字典
"""
# 取未来预测数据
future_data = forecast[forecast["ds"] > pd.Timestamp.now()]

if future_data.empty:
return {"error": "无未来预测数据"}

# 计算日均预测销量（用上界做保守估计）
daily_forecast = future_data["yhat"].mean()
daily_upper = future_data["yhat_upper"].mean()

# 安全库存 = 安全天数 × 日均销量上界
safety_stock = int(safety_stock_days * daily_upper)

# Lead Time 期间的预期消耗
lt_consumption = int(lead_time_days * daily_forecast)

# 再订货点 = Lead Time 消耗 + 安全库存
reorder_point = lt_consumption + safety_stock

# 当前库存可支撑天数
days_of_stock = int(current_stock / daily_forecast) if daily_forecast > 0 else 999

# 建议订货量 = 90 天预测需求 - 当前库存 + 安全库存
forecast_90d = int(future_data["yhat"].head(90).sum())
suggested_qty = max(forecast_90d - current_stock + safety_stock, 0)

# 向上取整到 MOQ 的倍数
if suggested_qty > 0:
suggested_qty = max(
((suggested_qty + moq - 1) // moq) * moq,
moq
)

# 紧急程度判断
if current_stock <= reorder_point * 0.5:
urgency = " 紧急补货"
elif current_stock <= reorder_point:
urgency = " 建议补货"
else:
urgency = " 库存充足"

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

print(f"\n 补货建议:")
print(f" 状态: {urgency}")
print(f" 当前库存: {current_stock} 件（可支撑 {days_of_stock} 天）")
print(f" 日均预测: {daily_forecast:.1f} 件/天")
print(f" 安全库存: {safety_stock} 件")
print(f" 再订货点: {reorder_point} 件")
print(f" 建议订货: {suggested_qty} 件（MOQ={moq}）")

return result

# 使用示例
# reorder = forecast_to_reorder(
# forecast=forecast,
# current_stock=500,
# lead_time_days=30,
# safety_stock_days=14,
# moq=200
# )
```

---

## 4. Model Evaluation

### 4.1 Evaluation Metrics

| Metric | Formula | Meaning | Best For |
|--------|---------|---------|----------|
| MAE | `mean(abs(actual - predicted))` | Mean Absolute Error | General purpose, robust to outliers |
| RMSE | `sqrt(mean((actual - predicted)²))` | Root Mean Square Error | Penalizes large errors, good when big deviations are unacceptable |
| MAPE | `mean(abs((actual - predicted) / actual)) × 100%` | Mean Absolute Percentage Error | Cross-SKU comparison (unaffected by sales volume base) |
| WAPE | `sum(abs(actual - predicted)) / sum(actual) × 100%` | Weighted Absolute Percentage Error | Avoids MAPE blowing up on low-volume days |

**WAPE is recommended for e-commerce**: MAPE approaches infinity when actual sales are near 0 (dividing by a near-zero number), while WAPE uses total sales as the denominator, making it more stable.

```python
def evaluate_forecast(
actual: pd.Series,
predicted: pd.Series
) -> dict:
"""
计算预测评估指标。

Args:
actual: 实际值
predicted: 预测值

Returns:
评估指标字典
"""
actual = actual.values
predicted = predicted.values

mae = np.mean(np.abs(actual - predicted))
rmse = np.sqrt(np.mean((actual - predicted) ** 2))

# MAPE（过滤掉实际值为 0 的天）
nonzero_mask = actual > 0
if nonzero_mask.any():
mape = np.mean(
np.abs((actual[nonzero_mask] - predicted[nonzero_mask])
/ actual[nonzero_mask])
) * 100
else:
mape = float("inf")

# WAPE（更稳健）
wape = np.sum(np.abs(actual - predicted)) / np.sum(actual) * 100 if np.sum(actual) > 0 else float("inf")

metrics = {
"MAE": round(mae, 2),
"RMSE": round(rmse, 2),
"MAPE": round(mape, 2),
"WAPE": round(wape, 2),
}

print(" 评估结果:")
for k, v in metrics.items():
unit = "%" if k in ("MAPE", "WAPE") else "units"
print(f" {k}: {v} {unit}")

return metrics
```

**MAPE Reference Benchmarks (E-commerce):**

| MAPE | Rating | Notes |
|------|--------|-------|
| < 15% | Excellent | Stable legacy products with sufficient data |
| 1525% | Good | Reasonable level for most SKUs |
| 2540% | Acceptable | New products or highly volatile categories |
| > 40% | Needs improvement | Check data quality or model configuration |

### 4.2 Backtesting

Backtesting is the most reliable way to validate a forecasting model: it uses historical data to simulate "what would have happened if we had used this model to forecast back then."

```python
def backtest_prophet(
df: pd.DataFrame,
initial_days: int = 180,
horizon_days: int = 30,
period_days: int = 30
) -> pd.DataFrame:
"""
Prophet 回测：滚动窗口验证。

原理：
1. 用前 initial_days 天数据训练
2. 预测未来 horizon_days 天
3. 与实际值对比
4. 窗口向前滑动 period_days 天，重复

Args:
df: Prophet 格式数据
initial_days: 初始训练数据天数
horizon_days: 每次预测的天数
period_days: 窗口滑动步长

Returns:
回测结果 DataFrame
"""
from prophet.diagnostics import cross_validation, performance_metrics

model = Prophet(
yearly_seasonality=True,
weekly_seasonality=True,
changepoint_prior_scale=0.1,
interval_width=0.8,
)
model.fit(df)

# 交叉验证
cv_results = cross_validation(
model,
initial=f"{initial_days} days",
period=f"{period_days} days",
horizon=f"{horizon_days} days"
)

# 计算性能指标
perf = performance_metrics(cv_results)

print(" 回测结果:")
print(f" MAE: {perf['mae'].mean():.2f}")
print(f" RMSE: {perf['rmse'].mean():.2f}")
print(f" MAPE: {perf['mape'].mean() * 100:.2f}%")

return cv_results, perf

# 使用示例
# cv_results, perf = backtest_prophet(prophet_df, initial_days=180, horizon_days=30)
#
# # 可视化回测结果
# from prophet.plot import plot_cross_validation_metric
# fig = plot_cross_validation_metric(cv_results, metric="mape")
# plt.savefig("output/backtest_mape.png", dpi=150)
```

### 4.3 Using Prediction Intervals

The predicted value is a point estimate, but business decisions need to account for uncertainty. Prophet's prediction intervals tell you "the true value will most likely fall within this range."

| Decision Scenario | Which Value to Use | Rationale |
|-------------------|-------------------|----------|
| Reorder quantity calculation | `yhat_upper` (upper bound) | Better to over-stock slightly stockout losses > inventory holding costs |
| Sales target setting | `yhat` (median) | Targets should reflect the most likely outcome |
| Pessimistic scenario analysis | `yhat_lower` (lower bound) | Evaluate worst-case cash flow |
| Warehouse space planning | `yhat_upper` (upper bound) | Ensure sufficient storage capacity |

---

## 5. Practical Project: Building a SKU Sales Forecasting System

### 5.1 Project Architecture

```
sales-forecaster/
config.py # Configuration (data paths, model parameters)
requirements.txt # Dependencies

data/ # Data directory
raw/ # Raw sales data
processed/ # Cleaned data

models/ # Model storage
prophet/ # Prophet model files

src/
data_prep.py # Data preparation (cleaning, stockout handling)
prophet_model.py # Prophet training and forecasting
autogluon_model.py # AutoGluon batch forecasting
review_analysis.py # BERTopic Review analysis
evaluator.py # Model evaluation and backtesting
reorder.py # Replenishment decisions

output/ # Output
forecasts/ # Forecast result CSVs
reports/ # HTML reports
plots/ # Charts

run_forecast.py # Main entry: single SKU forecast
run_batch_forecast.py # Batch forecast entry
README.md
```

### 5.2 Main Entry Script

```python
# run_forecast.py 单 SKU 销量预测
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
完整预测流程：数据准备 → 训练 → 预测 → 评估 → 补货建议
"""
print(f" 开始预测流程")

# 1. 加载数据
df = pd.read_csv(data_path)
if asin and "asin" in df.columns:
df = df[df["asin"] == asin]
print(f" SKU: {asin}")

# 2. 数据准备
prophet_df = prepare_prophet_data(df, date_col="date", value_col="units")
prophet_df = handle_stockout(prophet_df, units_col="y")

# 3. 训练（带节假日效应）
model = train_prophet_with_holidays(prophet_df, changepoint_prior=0.1)

# 4. 预测
forecast = make_forecast(model, periods=forecast_days)

# 5. 评估（用最后 30 天做验证）
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

# 6. 可视化
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

plot_forecast(
model, forecast, actual_df=prophet_df,
title=f"{'ASIN ' + asin if asin else 'SKU'} 销量预测 ({forecast_days}天)"
)

# 7. 保存预测结果
forecast_output = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(forecast_days)
forecast_output.to_csv(
output_dir / f"forecast_{asin or 'sku'}_{forecast_days}d.csv",
index=False
)

# 8. 补货建议
if current_stock is not None:
reorder = forecast_to_reorder(
forecast,
current_stock=current_stock,
lead_time_days=lead_time
)

print(f"\n 预测完成！结果已保存到 output/")

if __name__ == "__main__":
parser = argparse.ArgumentParser(description="SKU 销量预测")
parser.add_argument("--data", required=True, help="销量数据 CSV 路径")
parser.add_argument("--asin", help="ASIN 编号")
parser.add_argument("--days", type=int, default=90, help="预测天数")
parser.add_argument("--stock", type=int, help="当前库存")
parser.add_argument("--lead-time", type=int, default=30, help="交货周期(天)")
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
# 运行示例
python3 run_forecast.py --data data/daily_sales.csv --asin B0XXXXX --days 90
python3 run_forecast.py --data data/daily_sales.csv --asin B0XXXXX --stock 500 --lead-time 30
```

---

## 6. Common Pitfalls

| Pitfall | Symptom | Solution |
|---------|---------|----------|
| Overfitting | Training MAPE is very low, test MAPE is very high | Lower `changepoint_prior_scale`, validate with backtesting |
| Data leakage | Using future data to train the model (e.g., using full-year data to predict Q3) | Strictly split train/test by time, use `cross_validation` |
| Ignoring stockouts | Zeros during stockout periods treated as real demand | Use the `handle_stockout` function to handle them |
| Ignoring external factors | Competitor price drop causes sales surge the model can't explain | Add external regressors (competitor price, ad spend) |
| Negative predictions | Prophet may output negative forecast values | Use `.clip(lower=0)` to truncate |
| Seasonality mismatch | Training on weekly data but expecting daily-level predictions | Ensure training data and forecast frequency are consistent |
| Promotion overfitting | Model treats promotions as regular patterns | Use the `holidays` parameter to explicitly model promotional events |
| No data for new products | New ASIN has no sales history | Use analogous products' sales curves, or AutoGluon's transfer learning |

---

## 7. Learning Resources

### 7.1 Free Courses & Documentation

| Resource | Platform | Duration | Best For | Link |
|----------|----------|----------|----------|------|
| Prophet Official Tutorial | Meta | 2h | Time series intro | [facebook.github.io/prophet](https://facebook.github.io/prophet/) |
| Kaggle: Time Series | Kaggle | 5h | Time series fundamentals | [kaggle.com/learn/time-series](https://www.kaggle.com/learn/time-series) |
| Kaggle: Intro to ML | Kaggle | 4h | ML from zero | [kaggle.com/learn/intro-to-machine-learning](https://www.kaggle.com/learn/intro-to-machine-learning) |
| Google ML Crash Course | Google | 15h | Systematic ML learning | [developers.google.com/machine-learning/crash-course](https://developers.google.com/machine-learning/crash-course) |
| AutoGluon Time Series Tutorial | Amazon | 2h | Automated forecasting | [auto.gluon.ai](https://auto.gluon.ai/) |
| BERTopic Documentation | GitHub | 3h | Review topic analysis | [maartengr.github.io/BERTopic](https://maartengr.github.io/BERTopic/) |
| Darts Documentation | Unit8 | 3h | Multi-model comparison | [unit8co.github.io/darts](https://unit8co.github.io/darts/) |

### 7.2 Recommended GitHub Repositories

| Repository | Stars | Use Case |
|------------|-------|----------|
| [Prophet](https://github.com/facebook/prophet) | 18k+ | Core time series forecasting library |
| [AutoGluon](https://github.com/autogluon/autogluon) | 8k+ | Automated ML framework |
| [BERTopic](https://github.com/MaartenGr/BERTopic) | 6k+ | Topic modeling |
| [Darts](https://github.com/unit8co/darts) | 8k+ | Time series toolkit |
| [OR-Tools](https://github.com/google/or-tools) | 11k+ | Operations research optimization |

Content rephrased for compliance with licensing restrictions. Sources cited inline.

---

## 8. Automating Forecasting with OpenClaw

### 8.1 Scenario: AI Agent Runs Sales Forecasts on a Schedule and Generates Replenishment Recommendations

```
You tell OpenClaw:
"Every Monday, automatically run sales forecasts, generate replenishment
recommendations based on the results, update the forecast Dashboard,
and send a summary to Slack."

OpenClaw automatically executes:
1. [Heartbeat] Triggers every Monday
2. [filesystem MCP] Reads the latest sales data
3. [LLM + Prophet] Runs 90-day sales forecast
4. [LLM] Generates replenishment recommendations based on forecast results
5. [Skill: google-sheets] Updates the forecast Dashboard
6. [Skill: slack] Sends forecast summary
```

### 8.2 Required Skills and MCP Servers

| Component | Purpose | Link |
|-----------|---------|------|
| **filesystem MCP** | Read/write local sales data | [MCP Filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) |
| **google-sheets** Skill | Update forecast Dashboard | [ClawHub](https://clawhub.ai/) |
| **slack** Skill | Send forecast summary | [ClawHub](https://clawhub.ai/) |
| **memory** Skill | Store historical forecast baselines | [OpenClaw Docs](https://docs.openclaw.com/) |
| **sqlite MCP** | Local database storage | [MCP SQLite](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite) |

### 8.3 Related Resources

| Resource | Description | Link |
|----------|-------------|------|
| OpenClaw Official Docs | Installation and configuration guide | [docs.openclaw.com](https://docs.openclaw.com/) |
| ClawHub Skills Marketplace | Search and install Agent Skills | [clawhub.ai](https://clawhub.ai/) |
| OpenClaw MCP Integration | Connect MCP Servers | [Build Skill with MCP](https://rebeccamdeprey.com/blog/build-openclaw-skill-with-mcp) |
| F4 Automation & Agents | Agent fundamentals module | [F4 Module](../0-foundations/f4-agent-automation.md) |

Content rephrased for compliance with licensing restrictions. Sources cited inline.

---

## 9. Completion Checklist

- [ ] Use Prophet to generate a 90-day sales forecast for a real SKU, outputting predicted values and confidence intervals
- [ ] Add e-commerce promotional holiday effects (Prime Day, BFCM) and compare forecast accuracy with and without holidays
- [ ] Validate the model using backtesting, achieving MAPE < 30%
- [ ] Use AutoGluon to batch-forecast 10+ SKUs and review the model leaderboard
- [ ] Use BERTopic to analyze a set of Review texts and discover at least 3 meaningful topics
- [ ] Convert forecast results into replenishment recommendations (calculate reorder point and suggested order quantity)

After completing all items above, you've mastered the core skills of e-commerce predictive modeling. Next, move on to [B3 RAG Knowledge Base](b3-rag-knowledge-base.md) to learn how to build an intelligent Q&A system based on RAG.

---

## Appendix

### Appendix A: Model Selection Decision Tree

```
What's your forecasting need?

Deep forecast for a single SKU
Have 1+ year of historical data?
Yes → Prophet + holidays + external variables
No → Basic Prophet / Moving Average
Need to explain why the forecast looks this way?
Yes → Prophet (decomposable into trend + seasonality)
No → AutoGluon (auto-selects the best model)

Batch forecast 100+ SKUs
Have a GPU?
Yes → AutoGluon (high_quality preset)
No → AutoGluon (medium_quality preset)
Need quick results?
Yes → AutoGluon (fast_training preset)

Review text analysis
Topic discovery → BERTopic
Sentiment classification → scikit-learn + TF-IDF / BERT
Keyword extraction → BERTopic's c-TF-IDF

Replenishment optimization
Simple rules → Forecast value + safety stock formula
Multi-constraint optimization → OR-Tools (considering MOQ, warehouse capacity, capital)
```

### Appendix B: Code Cheat Sheet

```python
# === Prophet Basics ===
from prophet import Prophet

df = pd.DataFrame({"ds": dates, "y": values}) # 必须是 ds 和 y
model = Prophet()
model.fit(df)
future = model.make_future_dataframe(periods=90)
forecast = model.predict(future)
model.plot(forecast) # 预测图
model.plot_components(forecast) # 成分分解图

# === Prophet Holidays ===
holidays = pd.DataFrame({
"holiday": ["prime_day"], "ds": ["2025-07-12"],
"lower_window": [-3], "upper_window": [2]
})
model = Prophet(holidays=holidays)

# === Prophet External Variables ===
model = Prophet()
model.add_regressor("ad_spend")
model.fit(df) # df 必须包含 ad_spend 列
future["ad_spend"] = 500 # 预测时也要提供

# === Prophet Backtesting ===
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
model.get_topic_info() # 主题概览
model.visualize_topics() # 主题可视化

# === Evaluation Metrics ===
mae = np.mean(np.abs(actual - predicted))
rmse = np.sqrt(np.mean((actual - predicted) ** 2))
mape = np.mean(np.abs((actual - predicted) / actual)) * 100
wape = np.sum(np.abs(actual - predicted)) / np.sum(actual) * 100
```

### Appendix C: Dependency Installation

```bash
# Basic forecasting
pip install prophet pandas numpy matplotlib

# AutoGluon (large package, recommend installing separately)
pip install autogluon.timeseries

# Review analysis
pip install bertopic sentence-transformers

# Operations research optimization
pip install ortools

# Install everything
pip install prophet pandas numpy matplotlib \
autogluon.timeseries \
bertopic sentence-transformers \
ortools scikit-learn \
statsmodels
```

> Prophet may encounter installation issues on some systems (depends on pystan/cmdstanpy). If installation fails, refer to the [Prophet Installation Guide](https://facebook.github.io/prophet/docs/installation.html) or use Google Colab (most dependencies are pre-installed).
---

---
> [Hub Home](../../README.md) · [Path B Overview](README.md)
>
> **Path B**: [B1 Data](b1-data-pipeline.md) · [B2 Prediction](b2-prediction-models.md) · [B3 RAG](b3-rag-knowledge-base.md) · [B4 Agent](b4-agent-workflow.md) · [B5 Deployment](b5-local-model-deploy.md)
>
> **Quick Jump**: [Path 0 Foundations](../0-foundations/) · [Path A Operations](../a-operators/) · [Path C Management](../c-managers/) · [Path D Multi-Platform](../d-platforms/) · [Path E Social Media](../e-social-media/)
