# Energy Price Forecasting System - User Guide

**Version**: 1.0  
**Last Updated**: December 15, 2025  
**Target Audience**: End users, developers, and system administrators

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Using the API](#using-the-api)
4. [Using the Frontend Dashboard](#using-the-frontend-dashboard)
5. [Running Model Training](#running-model-training)
6. [Backtesting Models](#backtesting-models)
7. [Advanced Analytics](#advanced-analytics)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [FAQ](#faq)

---

## Introduction

The Energy Price Forecasting System provides accurate predictions for energy commodity prices (WTI crude oil, Brent crude, and natural gas) through a REST API and interactive web dashboard. This guide will help you use the system effectively.

### What This System Does

- **Forecasts Prices**: Predicts energy commodity prices for 1-day, 7-day, and 30-day horizons
- **Historical Analysis**: Provides access to historical price data
- **Backtesting**: Evaluates model performance using historical data
- **Advanced Analytics**: Offers correlation analysis, seasonality detection, and anomaly detection
- **Model Comparison**: Compares multiple forecasting models side-by-side

### Key Features

- **Multi-Model Support**: ARIMA, Prophet, and LSTM models
- **REST API**: Programmatic access to all features
- **Web Dashboard**: Interactive visualization and analysis
- **Real-time Updates**: Daily data refresh and model retraining
- **Production-Ready**: Docker deployment, CI/CD, monitoring

---

## Getting Started

### Prerequisites

Before using the system, ensure you have:

1. **API Access**: An API key (contact administrator)
2. **Network Access**: Ability to reach the API endpoint
3. **Web Browser**: For dashboard access (Chrome, Firefox, Safari, Edge)

### Obtaining an API Key

1. Contact your system administrator to request an API key
2. API keys are required for all API endpoints
3. Keep your API key secure and do not share it

### API Base URL

The API base URL depends on your deployment:
- **Development**: `http://localhost:8000`
- **Staging**: `https://staging-api.example.com`
- **Production**: `https://api.example.com`

### Dashboard URL

The web dashboard is available at:
- **Development**: `http://localhost:3000`
- **Staging**: `https://staging-dashboard.example.com`
- **Production**: `https://dashboard.example.com`

---

## Using the API

### Authentication

All API requests require an API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your_api_key_here" \
     https://api.example.com/api/v1/health
```

### Rate Limits

- **Default**: 100 requests per minute per API key
- **Rate limit headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- **Exceeding limits**: Returns `429 Too Many Requests` with `Retry-After` header

### Getting Forecasts

#### Request Forecast

```bash
curl -X POST "https://api.example.com/api/v1/forecast" \
     -H "X-API-Key: your_api_key_here" \
     -H "Content-Type: application/json" \
     -d '{
       "commodity": "WTI",
       "horizon": 7,
       "start_date": "2024-12-15"
     }'
```

**Request Parameters**:
- `commodity` (required): `"WTI"`, `"BRENT"`, or `"NATURAL_GAS"`
- `horizon` (required): `1`, `7`, or `30` (days)
- `start_date` (optional): Start date for forecast (ISO format, default: today)
- `model_id` (optional): Specific model to use (default: best available)

**Response**:
```json
{
  "commodity": "WTI",
  "horizon": 7,
  "start_date": "2024-12-15",
  "predictions": [
    {"date": "2024-12-16", "price": 75.50, "confidence_lower": 73.20, "confidence_upper": 77.80},
    {"date": "2024-12-17", "price": 75.80, "confidence_lower": 73.50, "confidence_upper": 78.10},
    ...
  ],
  "model_id": "WTI_LSTM_v2",
  "metrics": {
    "rmse": 1.25,
    "mae": 0.95,
    "mape": 1.2
  }
}
```

### Getting Historical Data

```bash
curl -X GET "https://api.example.com/api/v1/historical/WTI?start_date=2024-01-01&end_date=2024-12-31" \
     -H "X-API-Key: your_api_key_here"
```

**Query Parameters**:
- `start_date` (required): Start date (ISO format)
- `end_date` (required): End date (ISO format)
- `limit` (optional): Maximum number of records (default: 1000)

**Response**:
```json
{
  "commodity": "WTI",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "data": [
    {"timestamp": "2024-01-01T00:00:00Z", "price": 70.25},
    {"timestamp": "2024-01-02T00:00:00Z", "price": 70.50},
    ...
  ],
  "count": 365
}
```

### Running Backtests

```bash
curl -X POST "https://api.example.com/api/v1/backtest" \
     -H "X-API-Key: your_api_key_here" \
     -H "Content-Type: application/json" \
     -d '{
       "commodity": "WTI",
       "model_id": "WTI_LSTM",
       "start_date": "2024-01-01",
       "end_date": "2024-12-31",
       "initial_capital": 10000,
       "strategy": "threshold"
     }'
```

**Request Parameters**:
- `commodity` (required): Commodity symbol
- `model_id` (required): Model identifier
- `start_date` (required): Backtest start date
- `end_date` (required): Backtest end date
- `initial_capital` (optional): Starting capital (default: 10000)
- `strategy` (optional): Trading strategy (default: "threshold")

**Response**:
```json
{
  "commodity": "WTI",
  "model_id": "WTI_LSTM",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 10000,
  "final_capital": 12500,
  "metrics": {
    "total_return": 0.25,
    "sharpe_ratio": 1.85,
    "sortino_ratio": 2.10,
    "max_drawdown": 0.08,
    "win_rate": 0.65,
    "total_trades": 120
  },
  "trades": [...]
}
```

### Getting Model Information

```bash
curl -X GET "https://api.example.com/api/v1/models/WTI" \
     -H "X-API-Key: your_api_key_here"
```

**Response**:
```json
{
  "commodity": "WTI",
  "models": [
    {
      "model_id": "WTI_LSTM_v2",
      "model_type": "LSTM",
      "version": "2.0",
      "training_date": "2024-12-10",
      "performance": {
        "rmse": 1.25,
        "mae": 0.95,
        "mape": 1.2
      },
      "status": "production"
    },
    ...
  ]
}
```

### Health Checks

```bash
curl https://api.example.com/health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-12-15T10:30:00Z",
  "version": "1.0.0"
}
```

---

## Using the Frontend Dashboard

### Accessing the Dashboard

1. Navigate to the dashboard URL in your web browser
2. No login required (authentication handled via API key in backend)

### Forecast Page

**Features**:
- Select commodity (WTI, Brent, Natural Gas)
- Choose forecast horizon (1-day, 7-day, 30-day)
- View interactive price forecast chart
- See confidence intervals
- Export forecast as PNG or CSV

**Steps**:
1. Select commodity from dropdown
2. Choose forecast horizon
3. Click "Generate Forecast"
4. View chart and metrics
5. Export if needed

### Historical Data Page

**Features**:
- View historical price data
- Filter by date range
- Interactive time-series chart
- Zoom and pan functionality
- Export data as CSV

**Steps**:
1. Select commodity
2. Choose date range
3. Click "Load Data"
4. View chart
5. Export if needed

### Backtest Page

**Features**:
- Configure backtest parameters
- View backtest results (P&L, metrics, trades)
- Compare multiple models
- Export results

**Steps**:
1. Select commodity and model
2. Choose date range
3. Set initial capital and strategy
4. Click "Run Backtest"
5. Review metrics and charts
6. Export results

### Model Comparison Page

**Features**:
- Compare multiple models side-by-side
- View statistical and risk metrics
- Interactive comparison charts
- Export comparison report

**Steps**:
1. Select commodity
2. Choose models to compare
3. Click "Compare Models"
4. Review metrics table and charts
5. Export report

---

## Running Model Training

### Automated Training

Models are automatically retrained on a schedule (typically weekly). Manual training can be triggered via:

```bash
# Train all models for all commodities
python train_all_models.py

# Train specific commodity
python train_all_models.py --commodity WTI

# Train specific model type
python train_all_models.py --model-type LSTM
```

### Training Process

1. **Data Preparation**: Fetches latest data from database
2. **Feature Engineering**: Creates technical indicators and time features
3. **Model Training**: Trains ARIMA, Prophet, and LSTM models
4. **Evaluation**: Evaluates models on validation set
5. **MLflow Logging**: Logs metrics and artifacts to MLflow
6. **Model Registration**: Registers best models to MLflow registry
7. **Validation Gates**: Validates models meet performance thresholds

### Monitoring Training

Training progress is logged to:
- **Console**: Real-time progress output
- **MLflow UI**: Experiment tracking and metrics
- **Log Files**: Detailed training logs

---

## Backtesting Models

### Using the API

See [Running Backtests](#running-backtests) section above.

### Using the Dashboard

See [Backtest Page](#backtest-page) section above.

### Understanding Results

**Key Metrics**:
- **Total Return**: Percentage return over backtest period
- **Sharpe Ratio**: Risk-adjusted return (higher is better, >1 is good)
- **Sortino Ratio**: Downside risk-adjusted return
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Total Trades**: Number of trades executed

**Interpreting Results**:
- **Sharpe Ratio > 1**: Good risk-adjusted returns
- **Win Rate > 50%**: More winning than losing trades
- **Max Drawdown < 20%**: Acceptable risk level
- **Total Return > 10%**: Positive performance

---

## Advanced Analytics

### Correlation Analysis

Analyze correlations between commodities:

```python
from analytics.correlation_analysis import CorrelationAnalyzer

analyzer = CorrelationAnalyzer()
results = analyzer.analyze_commodity_correlations(price_data)
```

### Seasonality Detection

Detect seasonal patterns:

```python
from analytics.seasonality_analysis import SeasonalityAnalyzer

analyzer = SeasonalityAnalyzer()
results = analyzer.detect_seasonality(price_data)
```

### Anomaly Detection

Identify anomalous price movements:

```python
from analytics.anomaly_detection import AnomalyDetector

detector = AnomalyDetector()
anomalies = detector.detect_anomalies(price_data, method='isolation_forest')
```

### Volatility Forecasting

Forecast price volatility:

```python
from analytics.volatility_forecasting import VolatilityForecaster

forecaster = VolatilityForecaster()
volatility = forecaster.forecast_volatility(returns_data, horizon=7)
```

---

## Troubleshooting

### Common Issues

#### API Returns 401 Unauthorized

**Problem**: Invalid or missing API key

**Solution**:
1. Verify API key is correct
2. Check `X-API-Key` header is included
3. Contact administrator if key is revoked

#### API Returns 429 Too Many Requests

**Problem**: Rate limit exceeded

**Solution**:
1. Wait for rate limit window to reset (check `Retry-After` header)
2. Reduce request frequency
3. Contact administrator for higher rate limits

#### Forecast Returns 404 Not Found

**Problem**: Model not available for commodity/horizon

**Solution**:
1. Check available models via `/api/v1/models/{commodity}`
2. Verify model is trained and registered
3. Wait for model training to complete

#### Database Connection Errors

**Problem**: Cannot connect to database

**Solution**:
1. Verify database is running (`docker ps`)
2. Check database credentials in `.env`
3. Verify network connectivity
4. Check database logs for errors

#### Model Training Fails

**Problem**: Training process errors

**Solution**:
1. Check training logs for error messages
2. Verify sufficient data is available
3. Check MLflow server is running
4. Verify dependencies are installed

---

## Best Practices

### API Usage

1. **Cache Responses**: Use cached responses when possible (TTL: 5 minutes)
2. **Batch Requests**: Combine multiple requests when possible
3. **Handle Errors**: Implement proper error handling and retries
4. **Monitor Rate Limits**: Track rate limit headers to avoid throttling
5. **Use Appropriate Horizons**: Choose forecast horizon based on use case

### Model Selection

1. **Short-term (1-day)**: Use LSTM for non-linear patterns
2. **Medium-term (7-day)**: Use Prophet for seasonality
3. **Long-term (30-day)**: Use ARIMA for trend following
4. **Compare Models**: Always compare multiple models before deployment

### Data Quality

1. **Verify Data Freshness**: Check last update timestamp
2. **Monitor Data Quality**: Review quality scores (target: 98%+)
3. **Handle Missing Data**: System handles missing data, but verify completeness

### Performance

1. **Use Caching**: Leverage API response caching
2. **Optimize Queries**: Use appropriate date ranges
3. **Monitor Latency**: Track API response times
4. **Scale Horizontally**: System supports horizontal scaling

---

## FAQ

### Q: How often are models retrained?

**A**: Models are automatically retrained weekly, or can be manually triggered. Training schedules can be configured by administrators.

### Q: What is the forecast accuracy?

**A**: Forecast accuracy varies by model and horizon:
- **1-day**: RMSE ~1-2 USD/barrel, Directional Accuracy ~60-70%
- **7-day**: RMSE ~2-4 USD/barrel, Directional Accuracy ~55-65%
- **30-day**: RMSE ~5-10 USD/barrel, Directional Accuracy ~50-60%

### Q: Can I use this for live trading?

**A**: This system is designed for analysis and research. Use at your own risk for live trading. Always validate predictions and implement proper risk management.

### Q: How do I get an API key?

**A**: Contact your system administrator to request an API key. API keys are required for all API endpoints.

### Q: What data sources are used?

**A**: The system uses three data sources:
- **EIA**: U.S. Energy Information Administration
- **FRED**: Federal Reserve Economic Data
- **Yahoo Finance**: Market data

### Q: How do I report bugs or issues?

**A**: Contact your system administrator or submit issues through the project repository.

### Q: Can I add custom models?

**A**: Yes, the system is extensible. Contact your system administrator for guidance on adding custom models.

---

## Additional Resources

- **API Documentation**: [Swagger UI](https://api.example.com/docs) (when deployed)
- **Architecture Documentation**: [System Architecture](architecture/SYSTEM_ARCHITECTURE.md)
- **Model Methodology**: [Model Methodology](architecture/MODEL_METHODOLOGY.md)
- **Deployment Guide**: [Deployment Guide](DEPLOYMENT_GUIDE.md)
- **Table of Contents**: [Documentation Index](TABLE-OF-CONTENTS.md)

---

**Document Version**: 1.0  
**Last Updated**: December 15, 2025  
**Maintained By**: Development Team

