# API Usage Guide

**Time to Read**: 3 minutes

---

## Overview

The REST API provides programmatic access to all system features. Use it to integrate forecasts, backtests, and analytics into your applications.

---

## Base URL

```
http://localhost:8000/api/v1
```

Production: Replace with your production API URL

---

## Authentication

Most endpoints require an API key. Include it in the `X-API-Key` header:

```bash
curl -H "X-API-Key: epf_your_api_key_here" \
  http://localhost:8000/api/v1/models
```

**Get API Key**: Use admin endpoints or contact administrator

---

## Key Endpoints

### Forecast Endpoint

Generate price forecasts:

```bash
POST /api/v1/forecast
Content-Type: application/json

{
  "commodity": "WTI",
  "horizon": 7,
  "start_date": "2025-12-15"
}
```

**Response**:
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
    }
  ]
}
```

---

### Historical Data Endpoint

Retrieve historical prices:

```bash
GET /api/v1/historical?commodity=WTI&start_date=2024-01-01&end_date=2024-12-31
```

**Response**:
```json
{
  "commodity": "WTI",
  "data": [
    {
      "date": "2024-01-01",
      "price": 72.50,
      "source": "EIA"
    }
  ],
  "total_count": 365
}
```

---

### Models Endpoint

List available models:

```bash
GET /api/v1/models?commodity=WTI
```

**Response**:
```json
{
  "models": [
    {
      "model_id": "lstm_wti_v1",
      "commodity": "WTI",
      "model_type": "LSTM",
      "version": "1.0.0",
      "stage": "Production"
    }
  ],
  "total_count": 1
}
```

---

### Backtest Endpoint

Run backtests:

```bash
POST /api/v1/backtest
Content-Type: application/json

{
  "model_id": "lstm_wti_v1",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000,
  "commission": 0.001,
  "slippage": 0.0005,
  "strategy": "threshold",
  "strategy_params": {
    "threshold": 0.02
  }
}
```

---

## Rate Limiting

- **Limit**: 100 requests per minute per API key
- **Response**: 429 Too Many Requests when exceeded
- **Header**: `X-RateLimit-Remaining` shows remaining requests

---

## Error Handling

### Common Errors

**401 Unauthorized**: Invalid or missing API key
```json
{
  "detail": "Invalid API key"
}
```

**404 Not Found**: Resource doesn't exist
```json
{
  "detail": "Model not found for commodity WTI"
}
```

**429 Too Many Requests**: Rate limit exceeded
```json
{
  "detail": "Rate limit exceeded. Retry after 60 seconds"
}
```

**500 Internal Server Error**: Server issue
```json
{
  "detail": "Internal server error"
}
```

---

## WebSocket API

For real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/forecast?commodity=WTI&horizon=7');

ws.onmessage = (event) => {
  const forecast = JSON.parse(event.data);
  console.log('Forecast update:', forecast);
};

// Subscribe to updates
ws.send(JSON.stringify({
  action: 'subscribe',
  commodity: 'WTI',
  horizon: 7
}));
```

---

## Code Examples

### Python

```python
import requests

API_BASE = "http://localhost:8000/api/v1"
API_KEY = "epf_your_api_key"

headers = {"X-API-Key": API_KEY}

# Get forecast
response = requests.post(
    f"{API_BASE}/forecast",
    json={"commodity": "WTI", "horizon": 7, "start_date": "2025-12-15"},
    headers=headers
)
forecast = response.json()
```

### JavaScript

```javascript
const API_BASE = 'http://localhost:8000/api/v1';
const API_KEY = 'epf_your_api_key';

async function getForecast() {
  const response = await fetch(`${API_BASE}/forecast`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({
      commodity: 'WTI',
      horizon: 7,
      start_date: '2025-12-15'
    })
  });
  return await response.json();
}
```

---

## Best Practices

1. **Cache Responses**: Forecasts are cached - reuse when possible
2. **Handle Errors**: Always check response status codes
3. **Respect Rate Limits**: Implement exponential backoff
4. **Use WebSocket**: For real-time updates instead of polling
5. **Validate Input**: Check commodity and date formats

---

## API Documentation

Full interactive documentation available at:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

---

## Next Steps

- **Dashboard Usage**: See [Dashboard Guide](dashboard-usage.md)
- **Troubleshooting**: See [Troubleshooting Guide](troubleshooting.md)
- **Developer Docs**: See [Developer Documentation](../../developers/index.md)

---

**Last Updated**: December 15, 2025

