# Epic 2: Core ML Model Development - Kickoff

**Epic**: 2 - Core ML Model Development  
**Status**: 🚀 **STARTING**  
**Start Date**: December 14, 2025  
**Estimated Duration**: 4 weeks (28 days)  
**Dependencies**: Epic 1 Complete ✅

---

## 🎯 Epic Overview

Epic 2 focuses on building the machine learning core of the Energy Price Forecasting System. We'll implement feature engineering, train multiple models (statistical and neural network-based), set up training infrastructure, and establish experiment tracking with MLflow.

**Goal**: Create accurate, reliable forecasting models for WTI crude oil, Brent crude, and natural gas prices.

---

## 📋 Features in Epic 2

| Feature | Description | Effort | Stories | Priority |
|---------|-------------|--------|---------|----------|
| **2.1** | Feature Engineering Pipeline | 5 days | 6 | P0 |
| **2.2** | Baseline Statistical Models (ARIMA/SARIMA) | 4 days | 5 | P0 |
| **2.3** | LSTM Neural Network Model | 5 days | 7 | P0 |
| **2.4** | Model Training Infrastructure | 4 days | 5 | P0 |
| **2.5** | Hyperparameter Tuning Framework | 3 days | 4 | P1 |
| **2.6** | Model Versioning & Experiment Tracking (MLflow) | 3 days | 4 | P1 |
| **2.7** | Multi-Horizon Forecasting Implementation | 4 days | 5 | P1 |
| **TOTAL** | | **28 days** | **36 stories** | |

---

## 🎯 Feature 2.1: Feature Engineering Pipeline (STARTING)

**Effort**: 5 days  
**Priority**: P0 (Critical)  
**Status**: 🔄 **Starting Now**

### User Stories

**Story 2.1.1: Implement Technical Indicators (Moving Averages)** (4 hours)
- Simple Moving Average (SMA) for 5, 10, 20, 50, 200 days
- Exponential Moving Average (EMA) for same windows
- Returns DataFrame with MA columns
- Unit tests

**Story 2.1.2: Implement RSI, MACD, Bollinger Bands** (6 hours)
- RSI (Relative Strength Index) - 14-day period
- MACD (Moving Average Convergence Divergence) - 12, 26, 9 periods
- Bollinger Bands - 20-day MA, 2 std
- ATR (Average True Range)
- Unit tests

**Story 2.1.3: Implement Lag Features** (3 hours)
- Lags: 1, 7, 30 days
- Returns DataFrame with lag columns
- Handles NaN values appropriately
- Unit tests

**Story 2.1.4: Implement Rolling Window Statistics** (4 hours)
- Rolling mean, std, min, max
- Windows: 7, 30, 90 days
- Returns DataFrame with statistics
- Unit tests

**Story 2.1.5: Implement Seasonal Decomposition** (5 hours)
- Trend component extraction
- Seasonal component extraction
- Residual component
- Uses statsmodels seasonal_decompose
- Unit tests

**Story 2.1.6: Create Feature Engineering Pipeline Class** (6 hours)
- Class `FeatureEngineer` orchestrates all transformations
- Method `transform(df)` applies all features
- Configurable feature selection
- Handles missing values
- Unit tests

### Architecture Design

```
┌─────────────────────────────────────────────────────────┐
│          FEATURE ENGINEERING PIPELINE                   │
└─────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Raw Price  │  │  Technical   │  │   Time       │
│   Data       │  │  Indicators  │  │   Features   │
│              │  │              │  │              │
│ • timestamp  │  │ • SMA/EMA    │  │ • Lags       │
│ • price      │  │ • RSI        │  │ • Rolling    │
│ • volume     │  │ • MACD       │  │ • Seasonal   │
│ • OHLCV      │  │ • Bollinger  │  │ • Decompose  │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                ┌──────────────────┐
                │  FeatureEngineer │
                │     transform()  │
                └──────────────────┘
                         │
                         ▼
                ┌──────────────────┐
                │  Enriched        │
                │  DataFrame       │
                │  (50+ features)  │
                └──────────────────┘
```

### Expected Output

**Input DataFrame**:
```
date       | price  | volume
-----------|--------|----------
2024-01-01 | 71.65  | 1000000
2024-01-02 | 72.10  | 1100000
...
```

**Output DataFrame** (after feature engineering):
```
date       | price | volume | sma_5 | sma_20 | ema_10 | rsi_14 | macd | bb_upper | lag_1 | rolling_std_30 | trend | seasonal
-----------|-------|--------|-------|--------|--------|--------|------|----------|-------|----------------|-------|----------
2024-01-01 | 71.65 | 1M     | 71.20 | 70.50  | 71.30  | 55.2   | 0.15 | 73.20    | 71.40 | 1.25           | 71.5  | 0.15
...
```

**Feature Count**: 50+ features per row

---

## 🚀 Implementation Plan

### Phase 1: Setup (Day 1, Morning)
- [x] Create Epic 2 kickoff document
- [ ] Create `feature_engineering/` module structure
- [ ] Set up requirements (ta-lib or pandas-ta)
- [ ] Create base `FeatureEngineer` class skeleton

### Phase 2: Technical Indicators (Day 1-2)
- [ ] Implement Story 2.1.1 (Moving Averages)
- [ ] Implement Story 2.1.2 (RSI, MACD, Bollinger)
- [ ] Write unit tests for indicators
- [ ] Validate with real data

### Phase 3: Time Features (Day 2-3)
- [ ] Implement Story 2.1.3 (Lag Features)
- [ ] Implement Story 2.1.4 (Rolling Statistics)
- [ ] Implement Story 2.1.5 (Seasonal Decomposition)
- [ ] Write unit tests

### Phase 4: Pipeline Integration (Day 3-4)
- [ ] Implement Story 2.1.6 (Pipeline Class)
- [ ] Integration testing
- [ ] Performance optimization
- [ ] Documentation

### Phase 5: Testing & Documentation (Day 4-5)
- [ ] Comprehensive unit tests
- [ ] Integration with database data
- [ ] Feature importance analysis
- [ ] Documentation and examples

---

## 📊 Success Criteria

**Feature 2.1 Complete When**:
- [x] All 6 user stories implemented
- [ ] 50+ features generated per data row
- [ ] Unit tests with >80% coverage
- [ ] Integration test with real data passes
- [ ] Performance: <5 seconds for 1000 rows
- [ ] Documentation complete
- [ ] Example scripts created

---

## 🔧 Technical Stack

**Libraries**:
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `ta` or `pandas-ta` - Technical indicators
- `statsmodels` - Seasonal decomposition
- `scikit-learn` - StandardScaler, feature selection
- `pytest` - Unit testing

**Files to Create**:
```
src/energy-price-forecasting/
├── feature_engineering/
│   ├── __init__.py
│   ├── indicators.py          # Technical indicators
│   ├── time_features.py       # Lag, rolling, seasonal
│   ├── pipeline.py            # FeatureEngineer class
│   └── config.yaml            # Feature configuration
│
├── tests/
│   ├── test_indicators.py
│   ├── test_time_features.py
│   └── test_feature_pipeline.py
│
└── examples/
    └── feature_engineering_example.py
```

---

## 📚 Resources & References

**Technical Indicators**:
- [pandas-ta documentation](https://github.com/twopirllc/pandas-ta)
- [TA-Lib documentation](https://mrjbq7.github.io/ta-lib/)
- [Investopedia - Technical Indicators](https://www.investopedia.com/terms/t/technicalindicator.asp)

**Time Series Features**:
- [statsmodels - Seasonal Decomposition](https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.seasonal_decompose.html)
- [Feature Engineering for Time Series](https://towardsdatascience.com/feature-engineering-for-time-series-forecasting-e23f0e1e8e1e)

**Best Practices**:
- [scikit-learn - Feature Engineering](https://scikit-learn.org/stable/modules/preprocessing.html)
- [Time Series Feature Engineering in Python](https://machinelearningmastery.com/basic-feature-engineering-time-series-data-python/)

---

## 🎓 Expected Learnings

This feature will demonstrate:
- ✅ Advanced pandas data manipulation
- ✅ Technical analysis indicator implementation
- ✅ Time series feature engineering techniques
- ✅ Pipeline design patterns
- ✅ Performance optimization for large datasets
- ✅ Comprehensive testing strategies

---

## 🔮 Next Steps After Feature 2.1

**Feature 2.2: Baseline Statistical Models** (4 days)
- Implement ARIMA/SARIMA
- Implement Exponential Smoothing
- Implement Facebook Prophet
- Performance benchmarking
- Model comparison framework

**Feature 2.3: LSTM Neural Network** (5 days)
- Sequence-to-sequence modeling
- Multi-variate time series
- Attention mechanisms
- Hyperparameter tuning

---

## 📝 Development Checklist

**Before Starting**:
- [x] Epic 1 complete and verified
- [x] Documentation reviewed
- [x] TODO list created
- [ ] Development environment ready
- [ ] Dependencies installed
- [ ] Module structure created

**During Development**:
- [ ] Follow TDD approach (test-first)
- [ ] Write comprehensive docstrings
- [ ] Log key decisions
- [ ] Update TODO list regularly
- [ ] Commit frequently with clear messages

**Before Feature Complete**:
- [ ] All tests passing (>80% coverage)
- [ ] Real data validation successful
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] Example scripts working
- [ ] Code review completed

---

**Kickoff Date**: December 14, 2025  
**Target Completion**: December 19, 2025 (5 days)  
**Status**: 🚀 **READY TO START**

Let's build some amazing features! 🚀

