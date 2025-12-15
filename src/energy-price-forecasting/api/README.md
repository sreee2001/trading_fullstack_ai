# API Service Layer

FastAPI REST API for the Energy Price Forecasting System.

## Overview

This package provides REST API endpoints for:
- Price forecasts (`/api/v1/forecast`)
- Historical data retrieval (`/api/v1/historical`)
- Model information (`/api/v1/models`)
- Backtesting results (`/api/v1/backtest`)
- System health monitoring (`/health`)

## Quick Start

### Run the API Server

```bash
# From the project root
cd src/energy-price-forecasting

# Run with uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python -m api.main
```

### Access API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

### Test the API

```bash
# Run unit tests
pytest tests/test_api_main.py -v

# Test root endpoint
curl http://localhost:8000/

# Test health check
curl http://localhost:8000/health
```

## Project Structure

```
api/
├── __init__.py          # Package initialization
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management (Story 4.1.2)
├── logging_config.py    # Logging setup (Story 4.1.3)
├── models/              # Pydantic request/response models
├── routes/               # API route handlers
│   ├── forecast.py      # Forecast endpoint (Feature 4.2)
│   ├── historical.py    # Historical data endpoint (Feature 4.3)
│   ├── models.py        # Model info endpoint (Feature 4.4)
│   └── backtest.py      # Backtesting endpoint (Feature 4.5)
├── services/            # Business logic services
├── middleware/          # Custom middleware (auth, rate limiting)
└── README.md            # This file
```

## Features

### ✅ Feature 4.1: FastAPI Application Setup (COMPLETE)

- ✅ Story 4.1.1: FastAPI application initialized
- ✅ Root endpoint (`/`) returns API information
- ✅ Health check endpoint (`/health`)
- ✅ CORS middleware configured
- ✅ OpenAPI documentation (Swagger UI & ReDoc)
- ✅ Unit tests (7 tests, all passing)

### 📋 Feature 4.2: Forecast Endpoint (PLANNED)

- 📋 Request/Response models (Pydantic)
- 📋 `/api/v1/forecast` endpoint
- 📋 Model loading and prediction
- 📋 Error handling

### 📋 Feature 4.3: Historical Data Endpoint (PLANNED)

- 📋 `/api/v1/historical` endpoint
- 📋 Database query integration
- 📋 Pagination and filtering

### 📋 Feature 4.4: Model Info Endpoint (PLANNED)

- 📋 `/api/v1/models` endpoint
- 📋 Model registry integration
- 📋 Performance metrics

### 📋 Feature 4.5: Backtesting Endpoint (PLANNED)

- 📋 `/api/v1/backtest` endpoint
- 📋 Backtesting engine integration
- 📋 Results formatting

## Configuration

### Environment Variables

Create a `.env` file (see `.env.example`):

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/energy_forecasting

# API Keys
EIA_API_KEY=your_eia_api_key
FRED_API_KEY=your_fred_api_key

# Security
SECRET_KEY=your_secret_key_here

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/api.log
```

## Testing

### Unit Tests

```bash
# Run all API tests
pytest tests/test_api_*.py -v

# Run with coverage
pytest tests/test_api_*.py --cov=api --cov-report=html
```

### Manual Testing

```bash
# Start the server
uvicorn api.main:app --reload

# Test root endpoint
curl http://localhost:8000/

# Test health check
curl http://localhost:8000/health

# View API docs
# Open http://localhost:8000/api/docs in browser
```

## Development

### Adding New Endpoints

1. Create route handler in `api/routes/`
2. Define Pydantic models in `api/models/`
3. Implement business logic in `api/services/`
4. Add route to `api/main.py`
5. Write unit tests in `tests/test_api_*.py`

### Code Style

- Follow PEP 8
- Use type hints
- Document all functions with docstrings
- Write unit tests for all endpoints

## Dependencies

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `pydantic`: Data validation
- `httpx`: HTTP client (for testing)

See `requirements.txt` for full list.

## Status

**Current Status**: Feature 4.1.1 Complete ✅

**Next Steps**:
- Story 4.1.2: Configure Environment Variables
- Story 4.1.3: Setup Logging Infrastructure
- Story 4.1.4: Implement Startup/Shutdown Events

## Documentation

- [User Stories](../../docs/energy-price-forecasting/user-stories/01-user-stories-epics-4-8.md)
- [Epic Breakdown](../../docs/energy-price-forecasting/project-plan/02-epic-breakdown.md)
- [Test Cases](../../docs/energy-price-forecasting/test-cases/EPIC-3-EPIC-4-MANUAL-TEST-CASES.md)

