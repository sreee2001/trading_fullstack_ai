# Feature Engineering Module

**Purpose**: Create technical indicators, lag features, and time-based features for ML models

---

## Overview

The feature engineering module transforms raw price data into features suitable for machine learning models. It includes technical indicators, lag features, seasonal decomposition, and time-based features.

---

## File Structure

```
feature_engineering/
├── __init__.py              # Module exports
├── indicators.py            # Technical indicators (327+ lines)
├── time_features.py         # Time-based features (293+ lines)
├── pipeline.py             # Feature engineering pipeline
└── config.yaml             # Configuration
```

---

## Key Classes & Functions

### Technical Indicators (`indicators.py`)

**Functions**:
- `calculate_sma(df, column, windows)`: Simple Moving Average
- `calculate_ema(df, column, windows)`: Exponential Moving Average
- `calculate_rsi(df, column, period)`: Relative Strength Index
- `calculate_macd(df, column)`: MACD indicator
- `calculate_bollinger_bands(df, column, period, std_dev)`: Bollinger Bands
- `calculate_atr(df, high, low, close, period)`: Average True Range
- `add_all_technical_indicators(df)`: Add all indicators at once

**Usage**:
```python
from feature_engineering.indicators import add_all_technical_indicators
import pandas as pd

df = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=100),
    'price': [70 + i*0.1 for i in range(100)]
})

# Add all technical indicators
df = add_all_technical_indicators(df)

# Or add specific indicators
from feature_engineering.indicators import calculate_sma, calculate_rsi
df = calculate_sma(df, column='price', windows=[5, 10, 20])
df = calculate_rsi(df, column='price', period=14)
```

---

### Time Features (`time_features.py`)

**Functions**:
- `create_lag_features(df, column, lags)`: Create lagged price features
- `calculate_rolling_statistics(df, column, windows)`: Rolling statistics
- `seasonal_decompose_features(df, column, period)`: Seasonal decomposition
- `create_date_features(df, date_column)`: Date-based features
- `add_all_time_features(df)`: Add all time features

**Usage**:
```python
from feature_engineering.time_features import add_all_time_features

# Add lag features
from feature_engineering.time_features import create_lag_features
df = create_lag_features(df, column='price', lags=[1, 2, 3, 7, 14, 30])

# Add rolling statistics
from feature_engineering.time_features import calculate_rolling_statistics
df = calculate_rolling_statistics(df, column='price', windows=[7, 14, 30])

# Add date features
df = create_date_features(df, date_column='date')
```

---

### Feature Engineering Pipeline (`pipeline.py`)

**FeatureEngineer Class**:
- Orchestrates feature creation
- Handles missing data
- Validates feature quality

**Key Methods**:
- `fit(data)`: Learn feature parameters from data
- `transform(data)`: Create features for data
- `fit_transform(data)`: Fit and transform in one step

**Usage**:
```python
from feature_engineering.pipeline import FeatureEngineer

engineer = FeatureEngineer()
engineer.fit(train_data)
features = engineer.transform(test_data)

# Or in one step
features = engineer.fit_transform(data)
```

---

## Feature Types

### Technical Indicators

- **Moving Averages**: SMA, EMA (multiple windows)
- **Momentum**: RSI, MACD
- **Volatility**: Bollinger Bands, ATR
- **Trend**: Moving average crossovers

### Time Features

- **Lag Features**: Previous price values (1, 2, 3, 7, 14, 30 days)
- **Rolling Statistics**: Mean, std, min, max over windows
- **Seasonal Decomposition**: Trend, seasonal, residual components
- **Date Features**: Day of week, month, quarter, year

### Feature Combinations

- **Price Ratios**: Current price / moving average
- **Volatility Ratios**: Current volatility / historical volatility
- **Momentum Signals**: RSI-based signals

---

## Configuration

**config.yaml**:
```yaml
indicators:
  sma_windows: [5, 10, 20, 50]
  ema_windows: [12, 26]
  rsi_period: 14
  macd_fast: 12
  macd_slow: 26
  macd_signal: 9

time_features:
  lag_periods: [1, 2, 3, 7, 14, 30]
  rolling_windows: [7, 14, 30, 60]
  seasonal_period: 12
```

---

## Feature Selection

Features are selected based on:
- **Correlation**: Remove highly correlated features
- **Importance**: Use feature importance from models
- **Performance**: Test feature combinations

---

## Testing

**Test Files**:
- `tests/test_feature_engineering.py`

**Run Tests**:
```bash
pytest tests/test_feature_engineering.py -v
```

---

## Dependencies

- `pandas`: Data manipulation
- `numpy`: Numerical operations
- `scipy`: Statistical functions
- `statsmodels`: Seasonal decomposition

---

## Integration

The feature engineering module is used by:
- **Training Pipeline**: Prepare features for model training
- **Forecast Generation**: Create features for predictions
- **Model Evaluation**: Feature importance analysis

---

## Best Practices

1. **Fit on Training Data**: Always fit feature engineering on training data only
2. **Handle Missing Data**: Fill or drop missing values appropriately
3. **Feature Scaling**: Scale features for neural networks
4. **Feature Selection**: Remove redundant features
5. **Validation**: Validate feature quality before training

---

## Extending

To add new features:

1. Create function in `indicators.py` or `time_features.py`
2. Add to `add_all_technical_indicators()` or `add_all_time_features()`
3. Update configuration
4. Add tests
5. Update documentation

---

**Last Updated**: December 15, 2025

