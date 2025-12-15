# Analytics Module

**Purpose**: Advanced market analysis including correlation, volatility, seasonality, and anomaly detection

---

## Overview

The analytics module provides sophisticated market analysis tools beyond basic forecasting. It includes correlation analysis, volatility forecasting, seasonality detection, anomaly detection, market regime detection, and feature importance analysis.

---

## File Structure

```
analytics/
├── __init__.py                    # Module exports
├── correlation_analysis.py       # Correlation analysis
├── volatility_forecasting.py     # Volatility forecasting
├── seasonality_analysis.py      # Seasonality detection
├── anomaly_detection.py          # Anomaly detection
├── market_regime_detection.py    # Market regime identification
├── feature_importance.py         # Feature importance analysis
└── insight_generation.py         # Insight generation
```

---

## Key Classes

### CorrelationAnalyzer (`correlation_analysis.py`)

**Purpose**: Analyze relationships between commodities

**Key Methods**:
- `calculate_correlation(commodity1, commodity2, method)`: Calculate correlation
- `rolling_correlation(commodity1, commodity2, window)`: Rolling correlation
- `correlation_matrix(commodities)`: Correlation matrix
- `plot_correlation_heatmap(matrix)`: Visualize correlations

**Usage**:
```python
from analytics.correlation_analysis import CorrelationAnalyzer

analyzer = CorrelationAnalyzer()
correlation = analyzer.calculate_correlation('WTI', 'BRENT', method='pearson')
rolling_corr = analyzer.rolling_correlation('WTI', 'BRENT', window=30)
matrix = analyzer.correlation_matrix(['WTI', 'BRENT', 'NG'])
```

---

### VolatilityForecaster (`volatility_forecasting.py`)

**Purpose**: Forecast price volatility using GARCH models

**Key Methods**:
- `fit_garch_model(data)`: Fit GARCH model
- `forecast_volatility(horizon)`: Forecast volatility
- `calculate_historical_volatility(data, window)`: Historical volatility
- `volatility_clustering(data)`: Detect volatility clustering

**Usage**:
```python
from analytics.volatility_forecasting import VolatilityForecaster

forecaster = VolatilityForecaster()
forecaster.fit_garch_model(data)
volatility_forecast = forecaster.forecast_volatility(horizon=7)
historical_vol = forecaster.calculate_historical_volatility(data, window=30)
```

---

### SeasonalityAnalyzer (`seasonality_analysis.py`)

**Purpose**: Detect seasonal patterns in price movements

**Key Methods**:
- `detect_seasonality(data, period)`: Detect seasonality
- `seasonal_strength(data)`: Calculate seasonal strength
- `seasonal_decomposition(data, period)`: Decompose into components
- `plot_seasonal_patterns(data)`: Visualize seasonality

**Usage**:
```python
from analytics.seasonality_analysis import SeasonalityAnalyzer

analyzer = SeasonalityAnalyzer()
seasonality = analyzer.detect_seasonality(data, period=12)
strength = analyzer.seasonal_strength(data)
decomposition = analyzer.seasonal_decomposition(data, period=12)
```

---

### AnomalyDetector (`anomaly_detection.py`)

**Purpose**: Identify unusual price movements

**Key Methods**:
- `detect_outliers(data, method)`: Detect outliers
- `detect_changepoints(data)`: Detect change points
- `detect_anomalies(data, threshold)`: Detect anomalies
- `plot_anomalies(data, anomalies)`: Visualize anomalies

**Usage**:
```python
from analytics.anomaly_detection import AnomalyDetector

detector = AnomalyDetector()
outliers = detector.detect_outliers(data, method='iqr')
changepoints = detector.detect_changepoints(data)
anomalies = detector.detect_anomalies(data, threshold=3.0)
```

---

### MarketRegimeDetector (`market_regime_detection.py`)

**Purpose**: Identify different market conditions

**Key Methods**:
- `detect_regimes(data)`: Detect market regimes
- `classify_regime(data)`: Classify current regime
- `regime_transitions(data)`: Identify regime transitions
- `regime_characteristics(regime)`: Get regime characteristics

**Usage**:
```python
from analytics.market_regime_detection import MarketRegimeDetector

detector = MarketRegimeDetector()
regimes = detector.detect_regimes(data)
current_regime = detector.classify_regime(data)
transitions = detector.regime_transitions(data)
```

---

### FeatureImportanceAnalyzer (`feature_importance.py`)

**Purpose**: Analyze feature importance for models

**Key Methods**:
- `calculate_shap_values(model, data)`: Calculate SHAP values
- `permutation_importance(model, data, target)`: Permutation importance
- `feature_rankings(importance_scores)`: Rank features
- `plot_importance(importance_scores)`: Visualize importance

**Usage**:
```python
from analytics.feature_importance import FeatureImportanceAnalyzer

analyzer = FeatureImportanceAnalyzer()
shap_values = analyzer.calculate_shap_values(model, data)
perm_importance = analyzer.permutation_importance(model, data, target)
rankings = analyzer.feature_rankings(perm_importance)
```

---

### InsightGenerator (`insight_generation.py`)

**Purpose**: Generate actionable insights from analysis

**Key Methods**:
- `generate_insights(data, analysis_results)`: Generate insights
- `summarize_findings(analyses)`: Summarize findings
- `recommend_actions(insights)`: Recommend actions

**Usage**:
```python
from analytics.insight_generation import InsightGenerator

generator = InsightGenerator()
insights = generator.generate_insights(data, analysis_results)
summary = generator.summarize_findings(analyses)
recommendations = generator.recommend_actions(insights)
```

---

## Analytics Types

### Correlation Analysis
- Pearson correlation
- Spearman correlation
- Rolling correlations
- Correlation heatmaps

### Volatility Analysis
- GARCH models
- Historical volatility
- Volatility clustering
- Risk estimation

### Seasonality Analysis
- Seasonal strength
- Seasonal decomposition
- Cyclical patterns
- Trend analysis

### Anomaly Detection
- Outlier detection (IQR, Z-score)
- Change point detection
- Anomaly scoring
- Alert generation

### Market Regime Detection
- Bull/Bear markets
- High/Low volatility
- Trending/Ranging markets
- Regime transitions

---

## Testing

**Test Files**:
- `tests/test_analytics.py`
- `tests/test_correlation_analysis.py`
- `tests/test_volatility_forecasting.py`

**Run Tests**:
```bash
pytest tests/test_analytics.py -v
```

---

## Dependencies

- `pandas`: Data manipulation
- `numpy`: Numerical operations
- `scipy`: Statistical functions
- `statsmodels`: Statistical models (GARCH)
- `scikit-learn`: Machine learning utilities
- `matplotlib`: Visualization

---

## Integration

The analytics module is used by:
- **API**: Analytics endpoints
- **Dashboard**: Analytics visualizations
- **Model Development**: Feature importance analysis
- **Risk Management**: Volatility and regime analysis

---

## Best Practices

1. **Multiple Methods**: Use multiple analysis methods for validation
2. **Context Awareness**: Consider market context in analysis
3. **Regular Updates**: Re-run analytics as new data arrives
4. **Visualization**: Visualize results for better understanding
5. **Actionable Insights**: Generate actionable recommendations

---

## Extending

To add new analytics:

1. Create analyzer class
2. Implement analysis methods
3. Add visualization
4. Add tests
5. Update documentation

---

**Last Updated**: December 15, 2025

