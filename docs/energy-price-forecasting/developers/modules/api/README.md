# API Module

**Purpose**: FastAPI REST API service for energy price forecasting

---

## Overview

The API module provides a production-ready REST API with:
- Forecast endpoints
- Historical data endpoints
- Model information endpoints
- Backtesting endpoints
- WebSocket support
- Authentication and rate limiting

---

## File Structure

```
api/
├── __init__.py
├── main.py                    # FastAPI application
├── config.py                  # Configuration
├── logging_config.py          # Logging setup
├── lifecycle.py               # Application lifecycle
├── Dockerfile                 # Container definition
├── routes/
│   ├── __init__.py
│   ├── forecast.py            # Forecast endpoint
│   ├── historical.py          # Historical data endpoint
│   ├── models.py              # Model info endpoint
│   ├── backtest.py            # Backtest endpoint
│   ├── admin.py               # Admin endpoints
│   ├── health.py              # Health checks
│   └── websocket.py           # WebSocket endpoint
├── services/
│   ├── __init__.py
│   ├── model_service.py       # Model loading service
│   ├── forecast_service.py    # Forecast generation
│   ├── backtest_service.py    # Backtest execution
│   └── historical_service.py # Historical data retrieval
├── auth/
│   ├── __init__.py
│   ├── api_key_manager.py     # API key management
│   └── middleware.py          # Auth middleware
├── cache/
│   ├── __init__.py
│   ├── redis_client.py        # Redis client
│   ├── cache_manager.py       # Cache management
│   └── rate_limit_middleware.py # Rate limiting
└── models/
    ├── __init__.py
    ├── forecast.py            # Forecast request/response
    ├── historical.py          # Historical request/response
    ├── backtest.py            # Backtest request/response
    └── models.py              # Model info response
```

---

## Main Application

### main.py

**Purpose**: FastAPI application entry point

**Key Components**:
- FastAPI app initialization
- Route registration
- Middleware setup
- CORS configuration
- Exception handlers

**Usage**:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Routes

### Forecast Route (`routes/forecast.py`)

**Endpoint**: `POST /api/v1/forecast`

**Purpose**: Generate price forecasts

**Request**:
```json
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
  "predictions": [...],
  "model_name": "LSTM",
  "model_version": "1.0.0"
}
```

**Key Functions**:
- `generate_forecast_response(request)`: Core forecast generation
- `@router.post("/forecast")`: Forecast endpoint handler

---

### Historical Route (`routes/historical.py`)

**Endpoint**: `GET /api/v1/historical`

**Purpose**: Retrieve historical price data

**Query Parameters**:
- `commodity`: WTI, BRENT, or NG
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

**Response**:
```json
{
  "commodity": "WTI",
  "data": [...],
  "total_count": 365
}
```

---

### Models Route (`routes/models.py`)

**Endpoint**: `GET /api/v1/models`

**Purpose**: List available models

**Query Parameters**:
- `commodity`: Optional filter by commodity

**Response**:
```json
{
  "models": [...],
  "total_count": 3
}
```

---

### Backtest Route (`routes/backtest.py`)

**Endpoint**: `POST /api/v1/backtest`

**Purpose**: Run backtests

**Request**:
```json
{
  "model_id": "lstm_wti_v1",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000,
  "commission": 0.001,
  "slippage": 0.0005,
  "strategy": "threshold",
  "strategy_params": {"threshold": 0.02}
}
```

**Response**:
```json
{
  "metrics": {...},
  "equity_curve": {...},
  "trades": [...]
}
```

---

### WebSocket Route (`routes/websocket.py`)

**Endpoint**: `WS /api/v1/ws/forecast/{commodity}/{horizon}`

**Purpose**: Real-time forecast streaming

**Usage**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/forecast/WTI/7?api_key=...');
ws.onmessage = (event) => {
  const forecast = JSON.parse(event.data);
  // Handle forecast update
};
```

---

## Services

### ModelService (`services/model_service.py`)

**Purpose**: Load and manage ML models

**Key Methods**:
- `load_model(commodity, model_type)`: Load model from registry
- `get_available_models(commodity)`: List available models
- `get_model_info(model_id)`: Get model metadata

---

### ForecastService (`services/forecast_service.py`)

**Purpose**: Generate forecasts

**Key Methods**:
- `generate_forecast(commodity, horizon, start_date)`: Generate forecast
- `prepare_features(data)`: Prepare input features
- `format_response(forecast, model)`: Format API response

---

### BacktestService (`services/backtest_service.py`)

**Purpose**: Execute backtests

**Key Methods**:
- `run_backtest(request)`: Execute backtest
- `calculate_metrics(trades, equity_curve)`: Calculate performance metrics
- `generate_equity_curve(trades)`: Generate equity curve

---

## Authentication

### API Key Management (`auth/api_key_manager.py`)

**Purpose**: Manage API keys

**Key Methods**:
- `create_api_key(name)`: Create new API key
- `validate_api_key(api_key)`: Validate API key
- `revoke_api_key(api_key)`: Revoke API key
- `get_api_key_from_request(request)`: Extract API key from request

**Usage**:
```python
from api.auth.api_key_manager import get_api_key_manager

manager = get_api_key_manager()
api_key = manager.create_api_key("my_app")
is_valid = manager.validate_api_key(api_key)
```

---

## Caching

### Cache Manager (`cache/cache_manager.py`)

**Purpose**: Manage Redis caching

**Key Methods**:
- `get(key)`: Get cached value
- `set(key, value, ttl)`: Set cached value
- `delete(key)`: Delete cached value
- `exists(key)`: Check if key exists

---

## Rate Limiting

### Rate Limit Middleware (`cache/rate_limit_middleware.py`)

**Purpose**: Enforce rate limits

**Configuration**:
- Default: 100 requests per minute
- Configurable per API key
- Redis-backed

---

## Testing

**Test Files**:
- `tests/test_api_main.py`
- `tests/test_api_forecast.py`
- `tests/test_api_websocket.py`

**Run Tests**:
```bash
pytest tests/test_api_*.py -v
```

---

## Configuration

**Environment Variables**:
- `DB_HOST`: Database host
- `DB_PORT`: Database port
- `DB_NAME`: Database name
- `REDIS_HOST`: Redis host
- `REDIS_PORT`: Redis port
- `API_ENV`: Environment (development/production)
- `API_DEBUG`: Debug mode

---

## Deployment

**Docker**:
```bash
docker build -t energy-forecasting-api -f api/Dockerfile .
docker run -p 8000:8000 energy-forecasting-api
```

**Docker Compose**:
```bash
docker compose up api
```

---

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

---

**Last Updated**: December 15, 2025

