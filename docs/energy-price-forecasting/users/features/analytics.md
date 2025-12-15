# Analytics Features

**Time to Read**: 2 minutes

---

## Overview

Advanced analytics provide deeper market insights beyond basic forecasting. Analyze correlations, detect seasonality, forecast volatility, and identify anomalies.

---

## Available Analytics

### 1. Correlation Analysis

Analyze relationships between different energy commodities.

**What it shows**:
- Correlation coefficients (Pearson, Spearman)
- Rolling correlations over time
- Correlation heatmaps

**Use cases**:
- Understand commodity relationships
- Diversification strategies
- Market regime identification

---

### 2. Seasonality Detection

Identify seasonal patterns in price movements.

**What it shows**:
- Seasonal strength indicators
- Seasonal decomposition (trend, seasonal, residual)
- Seasonal patterns visualization

**Use cases**:
- Plan for seasonal price changes
- Understand cyclical patterns
- Optimize trading timing

---

### 3. Volatility Forecasting

Predict future price volatility using GARCH models.

**What it shows**:
- Volatility forecasts
- Volatility clustering patterns
- Risk estimates

**Use cases**:
- Risk management
- Option pricing
- Position sizing

---

### 4. Anomaly Detection

Identify unusual price movements or data quality issues.

**What it shows**:
- Anomaly flags
- Outlier detection
- Change point detection

**Use cases**:
- Data quality monitoring
- Market event detection
- Risk alerts

---

### 5. Market Regime Detection

Identify different market conditions (bull, bear, volatile, stable).

**What it shows**:
- Regime classifications
- Regime transitions
- Regime characteristics

**Use cases**:
- Strategy adaptation
- Risk adjustment
- Market timing

---

### 6. Feature Importance

Understand which factors most influence price predictions.

**What it shows**:
- SHAP values
- Permutation importance
- Feature rankings

**Use cases**:
- Model interpretability
- Feature selection
- Understanding drivers

---

## Using Analytics

### Via API

```bash
# Correlation Analysis
GET /api/v1/analytics/correlation?commodity1=WTI&commodity2=BRENT

# Seasonality
GET /api/v1/analytics/seasonality?commodity=WTI

# Volatility Forecast
GET /api/v1/analytics/volatility?commodity=WTI&horizon=7

# Anomaly Detection
GET /api/v1/analytics/anomalies?commodity=WTI&start_date=2024-01-01
```

### Via Dashboard

Analytics are integrated into the dashboard:
- View correlations in model comparison
- See seasonality in forecast charts
- Monitor anomalies in data quality reports

---

## Understanding Results

### Correlation Values

- **+1.0**: Perfect positive correlation
- **0.0**: No correlation
- **-1.0**: Perfect negative correlation
- **>0.7**: Strong positive relationship
- **<-0.7**: Strong negative relationship

### Seasonal Strength

- **0.0-0.3**: Weak seasonality
- **0.3-0.7**: Moderate seasonality
- **0.7-1.0**: Strong seasonality

### Volatility

- **Low (<10%)**: Stable prices
- **Medium (10-20%)**: Normal volatility
- **High (>20%)**: Volatile market

---

## Best Practices

1. **Use Multiple Analytics**: Combine insights from different analyses
2. **Consider Context**: Market conditions affect all analytics
3. **Regular Updates**: Re-run analytics as new data arrives
4. **Validate Findings**: Cross-check with external market data

---

## Next Steps

- **Forecasting**: Use insights to improve forecasts
- **Backtesting**: Incorporate analytics into strategies
- **Risk Management**: Use volatility for position sizing

---

**Last Updated**: December 15, 2025

