# Forecasting Features

**Time to Read**: 3 minutes

---

## Overview

The forecasting feature generates price predictions for energy commodities using advanced machine learning models. You can forecast prices for 1-day, 7-day, or 30-day horizons.

---

## What You Can Forecast

### Commodities Supported

- **WTI** (West Texas Intermediate Crude Oil)
- **BRENT** (Brent Crude Oil)
- **NG** (Natural Gas)

### Forecast Horizons

- **1-Day**: Short-term price movements
- **7-Day**: Weekly price trends
- **30-Day**: Monthly price outlook

---

## How It Works

1. **Select Commodity**: Choose WTI, BRENT, or NG
2. **Set Horizon**: Choose 1, 7, or 30 days
3. **Generate Forecast**: System uses trained ML models
4. **View Results**: See predictions with confidence intervals

---

## Using the Dashboard

### Step-by-Step

1. Navigate to **Forecast** page
2. Select commodity from dropdown
3. Adjust forecast horizon slider (1-30 days)
4. Choose start date
5. Click **Generate Forecast**
6. View:
   - Forecast chart with confidence intervals
   - Prediction table with dates and prices
   - Average price and price range metrics

### Understanding the Results

- **Price**: Predicted price for that date
- **Confidence Lower**: Lower bound of prediction range
- **Confidence Upper**: Upper bound of prediction range
- **Chart**: Visual representation with historical comparison

---

## Using the API

### Request Example

```bash
POST /api/v1/forecast
Content-Type: application/json

{
  "commodity": "WTI",
  "horizon": 7,
  "start_date": "2025-12-15"
}
```

### Response Example

```json
{
  "commodity": "WTI",
  "forecast_date": "2025-12-15",
  "horizon": 7,
  "predictions": [
    {
      "date": "2025-12-16",
      "price": 75.50,
      "confidence_lower": 71.73,
      "confidence_upper": 79.28
    },
    ...
  ],
  "model_name": "LSTM",
  "model_version": "1.0.0"
}
```

---

## Real-Time Updates (WebSocket)

For real-time forecast updates, use WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/forecast?commodity=WTI&horizon=7');

ws.onmessage = (event) => {
  const forecast = JSON.parse(event.data);
  console.log('New forecast:', forecast);
};
```

---

## Models Used

The system uses multiple ML models:

- **ARIMA**: Statistical time-series model
- **Prophet**: Facebook's forecasting tool
- **LSTM**: Deep learning neural network

The best-performing model is automatically selected for each commodity.

---

## Confidence Intervals

Each forecast includes confidence intervals showing the prediction range:
- **Lower Bound**: 95% confidence lower limit
- **Upper Bound**: 95% confidence upper limit
- **Interpretation**: Price is expected to be within this range 95% of the time

---

## Best Practices

1. **Use Appropriate Horizon**: 
   - 1-day for trading decisions
   - 7-day for weekly planning
   - 30-day for monthly outlook

2. **Consider Confidence Intervals**: 
   - Wider intervals = more uncertainty
   - Narrower intervals = higher confidence

3. **Compare with Historical Data**: 
   - View historical trends alongside forecasts
   - Understand market context

4. **Use Multiple Models**: 
   - Compare forecasts from different models
   - Use ensemble approach for better accuracy

---

## Limitations

- Forecasts are based on historical patterns
- Market shocks may cause deviations
- Confidence intervals are statistical estimates
- Models require regular retraining

---

## Next Steps

- **Backtesting**: Test forecast accuracy with [Backtesting Features](backtesting.md)
- **Analytics**: Analyze market trends with [Analytics Features](analytics.md)
- **API Integration**: See [API Usage Guide](../guides/api-usage.md)

---

**Last Updated**: December 15, 2025

