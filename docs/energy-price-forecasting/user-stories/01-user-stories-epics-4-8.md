# Energy Price Forecasting System - User Stories (Epics 4-8)

**Project**: Energy Price Forecasting System  
**Version**: 1.0  
**Date**: December 14, 2025  
**Status**: ✅ Approved - Complete User Stories

---

## Overview

This document continues the user stories from Epics 1-3, covering the remaining Epics 4-8:
- Epic 4: API Service Layer (9 features)
- Epic 5: Visualization & User Interface (8 features)
- Epic 6: MLOps & Deployment Pipeline (8 features)
- Epic 7: Advanced Analytics & Insights (7 features)
- Epic 8: Quality Assurance & Documentation (12 features)

---

# EPIC 4: API Service Layer 🌐

## Feature 4.1: FastAPI Application Setup

### Story 4.1.1: Initialize FastAPI Application
**As a** backend developer  
**I want** a FastAPI application initialized  
**So that** I can build REST API endpoints

**Acceptance Criteria**:
- [ ] FastAPI app created in `main.py`
- [ ] App runs successfully with `uvicorn`
- [ ] Root endpoint `/` returns welcome message
- [ ] CORS middleware configured
- [ ] Application structure documented
- [ ] Unit tests for app initialization

**Technical Notes**:
```python
from fastapi import FastAPI
app = FastAPI(title="Energy Price Forecasting API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Energy Price Forecasting API", "version": "1.0.0"}
```

**Effort**: 3 hours  
**Dependencies**: None

---

### Story 4.1.2: Configure Environment Variables and Settings
**As a** backend developer  
**I want** configuration managed via environment variables  
**So that** deployment is flexible

**Acceptance Criteria**:
- [ ] `.env.example` file created
- [ ] Pydantic Settings class implemented
- [ ] Environment variables loaded (DB_URL, API_KEYS, etc.)
- [ ] Validation of required settings
- [ ] Settings accessible throughout app
- [ ] Unit tests

**Technical Notes**:
- Use `pydantic-settings`
- Settings: DATABASE_URL, EIA_API_KEY, FRED_API_KEY, SECRET_KEY

**Effort**: 3 hours  
**Dependencies**: Story 4.1.1

---

### Story 4.1.3: Setup Logging Infrastructure
**As a** backend developer  
**I want** comprehensive logging  
**So that** I can debug and monitor the API

**Acceptance Criteria**:
- [ ] Python logging configured
- [ ] Log levels configurable (DEBUG, INFO, WARNING, ERROR)
- [ ] Request/response logging middleware
- [ ] Log to file and console
- [ ] Structured logging format (JSON optional)
- [ ] Unit tests

**Technical Notes**:
- Use Python `logging` module
- Middleware logs all requests with timestamps, status codes

**Effort**: 3 hours  
**Dependencies**: Story 4.1.1

---

### Story 4.1.4: Implement Startup and Shutdown Events
**As a** backend developer  
**I want** startup/shutdown event handlers  
**So that** I can initialize/cleanup resources

**Acceptance Criteria**:
- [ ] `@app.on_event("startup")` handler implemented
- [ ] Initialize database connection pool
- [ ] Load ML models into memory (optional)
- [ ] `@app.on_event("shutdown")` handler implemented
- [ ] Close database connections
- [ ] Unit tests

**Technical Notes**:
```python
@app.on_event("startup")
async def startup_event():
    # Initialize resources
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup resources
    pass
```

**Effort**: 3 hours  
**Dependencies**: Story 4.1.2

---

## Feature 4.2: Forecast Endpoint (`/forecast`)

### Story 4.2.1: Define Request/Response Models (Pydantic)
**As a** backend developer  
**I want** Pydantic models for forecast requests/responses  
**So that** data validation is automatic

**Acceptance Criteria**:
- [ ] `ForecastRequest` model defined
- [ ] Fields: commodity, horizon, start_date
- [ ] Validation rules (commodity in allowed list, horizon > 0)
- [ ] `ForecastResponse` model defined
- [ ] Fields: commodity, forecast_date, horizon, predictions
- [ ] Unit tests

**Technical Notes**:
```python
from pydantic import BaseModel, Field
from typing import List

class ForecastRequest(BaseModel):
    commodity: str = Field(..., pattern="^(WTI|BRENT|NG)$")
    horizon: int = Field(..., ge=1, le=30)
    start_date: str = Field(..., pattern="^\d{4}-\d{2}-\d{2}$")

class Prediction(BaseModel):
    date: str
    price: float
    confidence_lower: float
    confidence_upper: float

class ForecastResponse(BaseModel):
    commodity: str
    forecast_date: str
    horizon: int
    predictions: List[Prediction]
```

**Effort**: 3 hours  
**Dependencies**: Feature 4.1 complete

---

### Story 4.2.2: Implement Forecast Endpoint Handler
**As a** backend developer  
**I want** the `/forecast` endpoint implemented  
**So that** users can request price forecasts

**Acceptance Criteria**:
- [ ] `POST /api/v1/forecast` endpoint created
- [ ] Request validation using Pydantic model
- [ ] Load appropriate model from disk/registry
- [ ] Generate forecast using model
- [ ] Return ForecastResponse
- [ ] Error handling (404 if model not found, 500 on errors)
- [ ] Integration tests

**Technical Notes**:
```python
@app.post("/api/v1/forecast", response_model=ForecastResponse)
async def forecast(request: ForecastRequest):
    # Load model
    # Generate forecast
    # Return response
    pass
```

**Effort**: 6 hours  
**Dependencies**: Story 4.2.1, Epic 2 complete

---

### Story 4.2.3: Integrate Model Loading Service
**As a** backend developer  
**I want** models loaded efficiently  
**So that** API responds quickly

**Acceptance Criteria**:
- [ ] Model loading service class created
- [ ] Models loaded once at startup (cached in memory)
- [ ] Lazy loading support (load on first request)
- [ ] Model registry integration (MLflow)
- [ ] Unit tests

**Technical Notes**:
- Cache models in memory to avoid reloading
- Use singleton pattern or dependency injection

**Effort**: 5 hours  
**Dependencies**: Story 4.2.2, Epic 2 Feature 2.6

---

### Story 4.2.4: Implement Response Caching (Optional)
**As a** backend developer  
**I want** forecast responses cached  
**So that** repeated requests are fast

**Acceptance Criteria**:
- [ ] Cache key based on request parameters
- [ ] Cache TTL: 5 minutes
- [ ] Redis integration
- [ ] Cache hit/miss logging
- [ ] Unit tests

**Technical Notes**:
- Use Redis or in-memory cache (cachetools)
- Cache key: f"{commodity}_{horizon}_{start_date}"

**Effort**: 4 hours (Optional)  
**Dependencies**: Story 4.2.2

---

## Feature 4.3: Historical Data Endpoint (`/historical`)

### Story 4.3.1: Define Request/Response Models for Historical Data
**As a** backend developer  
**I want** Pydantic models for historical data requests  
**So that** validation is automatic

**Acceptance Criteria**:
- [ ] `HistoricalDataRequest` query parameters model
- [ ] Fields: commodity, start_date, end_date, limit, offset
- [ ] `HistoricalDataResponse` model
- [ ] Fields: commodity, data (list of price points), total_count
- [ ] Unit tests

**Technical Notes**:
```python
class HistoricalDataRequest(BaseModel):
    commodity: str
    start_date: str
    end_date: str
    limit: int = 1000
    offset: int = 0
```

**Effort**: 2 hours  
**Dependencies**: Feature 4.1 complete

---

### Story 4.3.2: Implement Historical Data Endpoint Handler
**As a** backend developer  
**I want** the `/historical` endpoint implemented  
**So that** users can retrieve historical prices

**Acceptance Criteria**:
- [ ] `GET /api/v1/historical` endpoint created
- [ ] Query parameters validated
- [ ] Fetch data from database
- [ ] Support pagination (limit, offset)
- [ ] Return HistoricalDataResponse
- [ ] Error handling
- [ ] Integration tests

**Technical Notes**:
- Query database with date range filter
- Apply limit and offset for pagination

**Effort**: 5 hours  
**Dependencies**: Story 4.3.1, Epic 1 complete

---

### Story 4.3.3: Optimize Database Queries for Performance
**As a** backend developer  
**I want** optimized database queries  
**So that** historical data retrieval is fast

**Acceptance Criteria**:
- [ ] Use indexes on timestamp and commodity_id
- [ ] Query optimization (select only needed columns)
- [ ] Connection pooling configured
- [ ] Query execution time <100ms
- [ ] Performance tests

**Technical Notes**:
- Ensure indexes exist on (timestamp, commodity_id)
- Use TimescaleDB time-bucketing if aggregating

**Effort**: 3 hours  
**Dependencies**: Story 4.3.2

---

## Feature 4.4: Model Info Endpoint (`/models`)

### Story 4.4.1: Define Models Metadata Response Schema
**As a** backend developer  
**I want** a schema for model metadata  
**So that** users understand available models

**Acceptance Criteria**:
- [ ] `ModelInfo` Pydantic model
- [ ] Fields: model_id, commodity, model_type, version, training_date, metrics
- [ ] `ModelsListResponse` model (list of ModelInfo)
- [ ] Unit tests

**Technical Notes**:
```python
class ModelMetrics(BaseModel):
    rmse: float
    mae: float
    directional_accuracy: float
    sharpe_ratio: float

class ModelInfo(BaseModel):
    model_id: str
    commodity: str
    model_type: str
    version: str
    training_date: str
    metrics: ModelMetrics
```

**Effort**: 2 hours  
**Dependencies**: Feature 4.1 complete

---

### Story 4.4.2: Implement Models List Endpoint
**As a** backend developer  
**I want** the `/models` endpoint implemented  
**So that** users can discover available models

**Acceptance Criteria**:
- [ ] `GET /api/v1/models` endpoint created
- [ ] Query MLflow registry for models
- [ ] Filter by commodity (optional query param)
- [ ] Return ModelsListResponse
- [ ] Error handling
- [ ] Integration tests

**Technical Notes**:
- Query MLflow Model Registry
- Return all registered models with metadata

**Effort**: 5 hours  
**Dependencies**: Story 4.4.1, Epic 2 Feature 2.6

---

## Feature 4.5: Backtesting Endpoint (`/backtest`)

### Story 4.5.1: Define Backtest Request/Response Models
**As a** backend developer  
**I want** Pydantic models for backtest requests  
**So that** validation is automatic

**Acceptance Criteria**:
- [ ] `BacktestRequest` model
- [ ] Fields: model_id, start_date, end_date, initial_capital, strategy_params
- [ ] `BacktestResponse` model
- [ ] Fields: model_id, metrics (RMSE, Sharpe, etc.), trades, cumulative_pnl
- [ ] Unit tests

**Technical Notes**:
```python
class BacktestRequest(BaseModel):
    model_id: str
    start_date: str
    end_date: str
    initial_capital: float = 100000
    strategy_params: dict = {"threshold": 0.02}

class BacktestResponse(BaseModel):
    model_id: str
    start_date: str
    end_date: str
    metrics: dict
    num_trades: int
    cumulative_pnl: float
```

**Effort**: 3 hours  
**Dependencies**: Feature 4.1 complete

---

### Story 4.5.2: Implement Backtesting Endpoint Handler
**As a** backend developer  
**I want** the `/backtest` endpoint implemented  
**So that** users can run backtests

**Acceptance Criteria**:
- [ ] `POST /api/v1/backtest` endpoint created
- [ ] Request validation
- [ ] Load model
- [ ] Run backtesting (call Epic 3 backtesting module)
- [ ] Return BacktestResponse
- [ ] Error handling
- [ ] Integration tests

**Technical Notes**:
- This may be a long-running operation
- Consider async processing or timeout warnings

**Effort**: 6 hours  
**Dependencies**: Story 4.5.1, Epic 3 complete

---

### Story 4.5.3: Implement Async Backtesting with Job Queue (Optional)
**As a** backend developer  
**I want** backtesting run asynchronously  
**So that** API doesn't block on long operations

**Acceptance Criteria**:
- [ ] Job queue setup (Celery or background tasks)
- [ ] Submit backtest as background job
- [ ] Return job_id immediately
- [ ] Endpoint to check job status: `GET /api/v1/backtest/{job_id}`
- [ ] Endpoint to retrieve results when complete
- [ ] Unit tests

**Technical Notes**:
- Use FastAPI BackgroundTasks or Celery
- Store job status in Redis or database

**Effort**: 8 hours (Optional)  
**Dependencies**: Story 4.5.2

---

## Feature 4.6: Authentication & API Key Management

### Story 4.6.1: Design API Key Schema
**As a** backend developer  
**I want** an API key schema defined  
**So that** keys can be stored securely

**Acceptance Criteria**:
- [ ] Database table `api_keys` created
- [ ] Fields: id, key_hash, user_id, created_at, expires_at, is_active
- [ ] Migration script
- [ ] Schema documented

**Technical Notes**:
- Store hashed keys only (bcrypt or similar)
- Never store plain-text keys

**Effort**: 2 hours  
**Dependencies**: Epic 1 Feature 1.4 complete

---

### Story 4.6.2: Implement API Key Generation
**As a** backend developer  
**I want** to generate API keys  
**So that** users can authenticate

**Acceptance Criteria**:
- [ ] Function `generate_api_key()` creates unique key
- [ ] Function `store_api_key(key, user_id)` hashes and stores
- [ ] Key format: `epf_` + random string (e.g., `epf_a1b2c3d4...`)
- [ ] Returns plain-text key once (not stored)
- [ ] Unit tests

**Technical Notes**:
- Use `secrets` module for secure random generation
- Hash with bcrypt before storing

**Effort**: 4 hours  
**Dependencies**: Story 4.6.1

---

### Story 4.6.3: Implement API Key Validation Middleware
**As a** backend developer  
**I want** API key validation on all protected endpoints  
**So that** only authenticated users can access

**Acceptance Criteria**:
- [ ] Middleware checks `X-API-Key` header
- [ ] Validates key against database (check hash)
- [ ] Returns 401 if missing or invalid
- [ ] Returns 403 if key expired or inactive
- [ ] Attaches user context to request
- [ ] Unit tests

**Technical Notes**:
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    # Validate key
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return user
```

**Effort**: 5 hours  
**Dependencies**: Story 4.6.2

---

### Story 4.6.4: Implement API Key Revocation
**As a** backend developer  
**I want** to revoke API keys  
**So that** compromised keys can be disabled

**Acceptance Criteria**:
- [ ] Function `revoke_api_key(key_id)` sets is_active=False
- [ ] Admin endpoint `DELETE /api/v1/admin/keys/{key_id}`
- [ ] Revoked keys rejected by middleware
- [ ] Unit tests

**Technical Notes**:
- Update `is_active` field in database

**Effort**: 3 hours  
**Dependencies**: Story 4.6.3

---

## Feature 4.7: Rate Limiting & Caching (Redis)

### Story 4.7.1: Setup Redis Connection
**As a** backend developer  
**I want** Redis connected  
**So that** I can use it for caching and rate limiting

**Acceptance Criteria**:
- [ ] Redis client initialized at startup
- [ ] Connection configuration from environment
- [ ] Connection health check
- [ ] Graceful fallback if Redis unavailable
- [ ] Unit tests

**Technical Notes**:
- Library: `redis-py` or `aioredis`
- Environment: REDIS_URL

**Effort**: 3 hours  
**Dependencies**: Feature 4.1 complete

---

### Story 4.7.2: Implement Rate Limiting Middleware
**As a** backend developer  
**I want** rate limiting per API key  
**So that** abuse is prevented

**Acceptance Criteria**:
- [ ] Middleware tracks requests per API key
- [ ] Limit: 100 requests per minute per key
- [ ] Returns 429 (Too Many Requests) if exceeded
- [ ] `Retry-After` header included
- [ ] Counter stored in Redis
- [ ] Unit tests

**Technical Notes**:
- Use sliding window or token bucket algorithm
- Redis key: `rate_limit:{api_key}`

**Effort**: 5 hours  
**Dependencies**: Story 4.7.1, Feature 4.6 complete

---

### Story 4.7.3: Implement Response Caching
**As a** backend developer  
**I want** GET responses cached  
**So that** repeated requests are fast

**Acceptance Criteria**:
- [ ] Cache GET `/historical` responses (TTL: 5 min)
- [ ] Cache GET `/models` responses (TTL: 10 min)
- [ ] Cache key based on endpoint + query params
- [ ] Cache hit/miss logged
- [ ] Unit tests

**Technical Notes**:
- Redis key: `cache:{endpoint}:{params_hash}`
- TTL configurable per endpoint

**Effort**: 4 hours  
**Dependencies**: Story 4.7.1

---

### Story 4.7.4: Implement Cache Invalidation Strategy
**As a** backend developer  
**I want** cache invalidated appropriately  
**So that** stale data isn't served

**Acceptance Criteria**:
- [ ] Invalidate `/models` cache when new model registered
- [ ] Invalidate `/historical` cache when new data ingested
- [ ] Manual cache clear endpoint (admin): `DELETE /api/v1/admin/cache`
- [ ] Unit tests

**Technical Notes**:
- Clear cache keys matching pattern

**Effort**: 3 hours  
**Dependencies**: Story 4.7.3

---

## Feature 4.8: API Documentation (Swagger UI)

### Story 4.8.1: Configure OpenAPI Metadata
**As a** backend developer  
**I want** comprehensive OpenAPI metadata  
**So that** API documentation is clear

**Acceptance Criteria**:
- [ ] API title, description, version configured
- [ ] Contact information added
- [ ] License information added
- [ ] Tags for endpoint grouping
- [ ] Documentation visible at `/docs`

**Technical Notes**:
```python
app = FastAPI(
    title="Energy Price Forecasting API",
    description="API for energy commodity price forecasting",
    version="1.0.0",
    contact={"name": "Your Name", "email": "email@example.com"},
    license_info={"name": "MIT"}
)
```

**Effort**: 2 hours  
**Dependencies**: Feature 4.1 complete

---

### Story 4.8.2: Add Detailed Endpoint Descriptions and Examples
**As a** backend developer  
**I want** detailed descriptions for all endpoints  
**So that** users understand how to use them

**Acceptance Criteria**:
- [ ] Docstrings for all endpoint functions
- [ ] Request examples in Pydantic models
- [ ] Response examples in Pydantic models
- [ ] Error response documentation
- [ ] Visible in Swagger UI

**Technical Notes**:
```python
@app.post("/api/v1/forecast", 
    response_model=ForecastResponse,
    summary="Generate price forecast",
    description="Generate energy commodity price forecast for specified horizon")
async def forecast(request: ForecastRequest):
    """
    Generate forecast for energy commodity.
    
    - **commodity**: WTI, BRENT, or NG
    - **horizon**: Number of days ahead (1-30)
    - **start_date**: Forecast start date
    """
    pass
```

**Effort**: 4 hours  
**Dependencies**: All endpoint features

---

### Story 4.8.3: Document Authentication in Swagger
**As a** backend developer  
**I want** authentication documented in Swagger  
**So that** users know how to authenticate

**Acceptance Criteria**:
- [ ] Security scheme defined (API Key)
- [ ] "Authorize" button in Swagger UI
- [ ] Test authentication directly in Swagger
- [ ] Documentation on obtaining API key

**Technical Notes**:
```python
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# FastAPI automatically adds to OpenAPI schema
```

**Effort**: 2 hours  
**Dependencies**: Feature 4.6 complete

---

## Feature 4.9: Health Check & Monitoring Endpoints

### Story 4.9.1: Implement Basic Health Check Endpoint
**As a** DevOps engineer  
**I want** a health check endpoint  
**So that** I can monitor API availability

**Acceptance Criteria**:
- [ ] `GET /health` endpoint created
- [ ] Returns 200 if API is running
- [ ] Response: `{"status": "healthy"}`
- [ ] No authentication required
- [ ] Unit tests

**Technical Notes**:
- Simple liveness check

**Effort**: 1 hour  
**Dependencies**: Feature 4.1 complete

---

### Story 4.9.2: Implement Readiness Check Endpoint
**As a** DevOps engineer  
**I want** a readiness check  
**So that** I know when API is ready to serve

**Acceptance Criteria**:
- [ ] `GET /ready` endpoint created
- [ ] Checks database connectivity
- [ ] Checks Redis connectivity (if configured)
- [ ] Checks model availability
- [ ] Returns 200 if ready, 503 if not
- [ ] Response includes component status
- [ ] Unit tests

**Technical Notes**:
```python
@app.get("/ready")
async def readiness():
    db_ok = check_database()
    redis_ok = check_redis()
    models_ok = check_models_loaded()
    
    if all([db_ok, redis_ok, models_ok]):
        return {"status": "ready", "components": {...}}
    else:
        raise HTTPException(status_code=503, detail="Not ready")
```

**Effort**: 4 hours  
**Dependencies**: Feature 4.1, Epic 1 complete

---

### Story 4.9.3: Implement Prometheus Metrics Endpoint (Optional)
**As a** DevOps engineer  
**I want** Prometheus metrics exposed  
**So that** I can monitor API performance

**Acceptance Criteria**:
- [ ] `GET /metrics` endpoint
- [ ] Exposes request count, latency, error rate
- [ ] Counter for each endpoint
- [ ] Histogram for request duration
- [ ] Prometheus format
- [ ] Unit tests

**Technical Notes**:
- Library: `prometheus-fastapi-instrumentator`

**Effort**: 3 hours (Optional)  
**Dependencies**: Feature 4.1 complete

---

# EPIC 5: Visualization & User Interface 📈

## Feature 5.1: React Application Setup (TypeScript)

### Story 5.1.1: Initialize React Application with TypeScript
**As a** frontend developer  
**I want** a React app with TypeScript  
**So that** I have type safety

**Acceptance Criteria**:
- [ ] React app created (Vite recommended)
- [ ] TypeScript configured
- [ ] App runs successfully (`npm run dev`)
- [ ] Basic folder structure created
- [ ] README with setup instructions

**Technical Notes**:
- Command: `npm create vite@latest dashboard -- --template react-ts`
- Or: `npx create-react-app dashboard --template typescript`

**Effort**: 2 hours  
**Dependencies**: None

---

### Story 5.1.2: Setup Routing with React Router
**As a** frontend developer  
**I want** routing configured  
**So that** I can have multiple pages

**Acceptance Criteria**:
- [ ] `react-router-dom` installed
- [ ] Router configured in App.tsx
- [ ] Routes: `/`, `/forecast`, `/models`, `/backtest`
- [ ] Navigation working
- [ ] Unit tests

**Technical Notes**:
```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/forecast" element={<Forecast />} />
      </Routes>
    </BrowserRouter>
  );
}
```

**Effort**: 3 hours  
**Dependencies**: Story 5.1.1

---

### Story 5.1.3: Setup State Management (Context API or Redux)
**As a** frontend developer  
**I want** state management configured  
**So that** I can share state across components

**Acceptance Criteria**:
- [ ] State management library chosen (Context API or Redux Toolkit)
- [ ] Store/Context configured
- [ ] Initial state defined
- [ ] Example usage in component
- [ ] Unit tests

**Technical Notes**:
- Recommendation: Start with Context API, use Redux if state becomes complex

**Effort**: 4 hours  
**Dependencies**: Story 5.1.1

---

### Story 5.1.4: Setup API Client with Axios
**As a** frontend developer  
**I want** an API client configured  
**So that** I can communicate with backend

**Acceptance Criteria**:
- [ ] `axios` installed
- [ ] API client class/module created
- [ ] Base URL configured
- [ ] Default headers (API key, content-type)
- [ ] Error handling interceptor
- [ ] Retry logic (optional)
- [ ] Unit tests

**Technical Notes**:
```tsx
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': process.env.REACT_APP_API_KEY
  }
});

export default apiClient;
```

**Effort**: 3 hours  
**Dependencies**: Story 5.1.1

---

### Story 5.1.5: Setup Styling Framework (Tailwind CSS or Material-UI)
**As a** frontend developer  
**I want** a styling framework  
**So that** UI development is efficient

**Acceptance Criteria**:
- [ ] Styling framework installed (Tailwind CSS or Material-UI)
- [ ] Configuration complete
- [ ] Theme customization (colors, fonts)
- [ ] Example styled components
- [ ] Documentation

**Technical Notes**:
- Option 1: Tailwind CSS (utility-first, lightweight)
- Option 2: Material-UI (component library, faster development)
- Recommendation: Tailwind for flexibility, MUI for speed

**Effort**: 3 hours  
**Dependencies**: Story 5.1.1

---

## Feature 5.2: Price Chart Component (Historical & Forecast)

### Story 5.2.1: Choose and Setup Charting Library
**As a** frontend developer  
**I want** a charting library integrated  
**So that** I can display price charts

**Acceptance Criteria**:
- [ ] Library chosen (Chart.js, Recharts, or Plotly.js)
- [ ] Library installed
- [ ] Basic chart example working
- [ ] Documentation reviewed

**Technical Notes**:
- Chart.js: Simple, lightweight
- Recharts: React-native, composable
- Plotly.js: Feature-rich, interactive
- Recommendation: Recharts for React integration

**Effort**: 2 hours  
**Dependencies**: Feature 5.1 complete

---

### Story 5.2.2: Create PriceChart Component
**As a** frontend developer  
**I want** a reusable price chart component  
**So that** I can display historical prices

**Acceptance Criteria**:
- [ ] Component `PriceChart.tsx` created
- [ ] Props: data (array of {date, price})
- [ ] Line chart rendered
- [ ] X-axis: Date, Y-axis: Price
- [ ] Responsive
- [ ] Unit tests

**Technical Notes**:
```tsx
interface PriceChartProps {
  data: Array<{date: string, price: number}>;
}

export const PriceChart: React.FC<PriceChartProps> = ({ data }) => {
  // Render chart
};
```

**Effort**: 5 hours  
**Dependencies**: Story 5.2.1

---

### Story 5.2.3: Add Forecast Data Overlay
**As a** frontend developer  
**I want** forecasted prices overlaid on chart  
**So that** users see predictions

**Acceptance Criteria**:
- [ ] Forecast data displayed as separate series
- [ ] Different color/style (e.g., dashed line)
- [ ] Legend distinguishes historical vs forecast
- [ ] Props updated: historicalData, forecastData
- [ ] Unit tests

**Technical Notes**:
- Two series: one for historical, one for forecast

**Effort**: 4 hours  
**Dependencies**: Story 5.2.2

---

### Story 5.2.4: Add Confidence Intervals (Shaded Area)
**As a** frontend developer  
**I want** confidence intervals visualized  
**So that** users understand uncertainty

**Acceptance Criteria**:
- [ ] Shaded area between upper and lower bounds
- [ ] Semi-transparent fill
- [ ] Props include: confidence_lower, confidence_upper
- [ ] Toggle on/off (optional)
- [ ] Unit tests

**Technical Notes**:
- Use area chart or filled region
- Opacity: 0.2-0.3

**Effort**: 4 hours  
**Dependencies**: Story 5.2.3

---

### Story 5.2.5: Add Interactivity (Zoom, Pan, Tooltip)
**As a** frontend developer  
**I want** interactive chart features  
**So that** users can explore data

**Acceptance Criteria**:
- [ ] Tooltip on hover showing date and price
- [ ] Zoom in/out functionality
- [ ] Pan to scroll through time
- [ ] Reset zoom button
- [ ] Unit tests

**Technical Notes**:
- Most charting libraries support these features
- Configure via library options

**Effort**: 4 hours  
**Dependencies**: Story 5.2.2

---

## Feature 5.3: Model Performance Dashboard

### Story 5.3.1: Create MetricCard Component
**As a** frontend developer  
**I want** reusable metric cards  
**So that** I can display model metrics

**Acceptance Criteria**:
- [ ] Component `MetricCard.tsx` created
- [ ] Props: title, value, unit, color
- [ ] Card displays title and value prominently
- [ ] Responsive layout
- [ ] Unit tests

**Technical Notes**:
```tsx
interface MetricCardProps {
  title: string;
  value: number | string;
  unit?: string;
  color?: string;
}
```

**Effort**: 3 hours  
**Dependencies**: Feature 5.1 complete

---

### Story 5.3.2: Fetch and Display Model Metrics
**As a** frontend developer  
**I want** model metrics fetched from API  
**So that** performance is displayed

**Acceptance Criteria**:
- [ ] Fetch from `GET /api/v1/models`
- [ ] Display metrics: RMSE, MAE, Directional Accuracy, Sharpe Ratio
- [ ] Use MetricCard for each metric
- [ ] Grid layout (2x2 or 4x1)
- [ ] Loading state
- [ ] Error handling
- [ ] Unit tests

**Technical Notes**:
- Use `useEffect` to fetch on mount
- Store in state

**Effort**: 5 hours  
**Dependencies**: Story 5.3.1, Epic 4 Feature 4.4

---

### Story 5.3.3: Create Model Comparison Table
**As a** frontend developer  
**I want** models compared in a table  
**So that** users can see relative performance

**Acceptance Criteria**:
- [ ] Table component with columns: Model Name, RMSE, MAE, Sharpe Ratio
- [ ] Sortable columns
- [ ] Highlight best model (row)
- [ ] Responsive (horizontal scroll on mobile)
- [ ] Unit tests

**Technical Notes**:
- Use HTML table or library like `react-table`

**Effort**: 5 hours  
**Dependencies**: Story 5.3.2

---

## Feature 5.4: Forecast vs Actual Comparison View

### Story 5.4.1: Create ComparisonChart Component
**As a** frontend developer  
**I want** a chart comparing forecast vs actual  
**So that** users see accuracy

**Acceptance Criteria**:
- [ ] Component `ComparisonChart.tsx` created
- [ ] Two line series: Predicted, Actual
- [ ] Different colors
- [ ] Legend
- [ ] Responsive
- [ ] Unit tests

**Technical Notes**:
- Similar to PriceChart but with two series

**Effort**: 5 hours  
**Dependencies**: Feature 5.2 complete

---

### Story 5.4.2: Display Accuracy Metrics Below Chart
**As a** frontend developer  
**I want** accuracy metrics displayed  
**So that** users quantify performance

**Acceptance Criteria**:
- [ ] Calculate or fetch: RMSE, MAE, Directional Accuracy
- [ ] Display below chart
- [ ] Use MetricCard or simple text
- [ ] Unit tests

**Technical Notes**:
- Fetch from backend or calculate client-side

**Effort**: 3 hours  
**Dependencies**: Story 5.4.1

---

## Feature 5.5: Trading Signal Indicators

### Story 5.5.1: Add Signal Markers to Price Chart
**As a** frontend developer  
**I want** trading signals visualized on chart  
**So that** users see buy/sell points

**Acceptance Criteria**:
- [ ] Buy signal: Green arrow up
- [ ] Sell signal: Red arrow down
- [ ] Markers positioned at signal dates
- [ ] Tooltip shows signal details
- [ ] Unit tests

**Technical Notes**:
- Add markers/annotations to chart
- Chart.js: Use point style
- Recharts: Use scatter plot overlay

**Effort**: 5 hours  
**Dependencies**: Feature 5.2 complete, Epic 3 Feature 3.3

---

### Story 5.5.2: Implement Toggle for Signals
**As a** frontend developer  
**I want** signals toggled on/off  
**So that** chart isn't cluttered

**Acceptance Criteria**:
- [ ] Checkbox "Show Signals"
- [ ] State tracks toggle
- [ ] Signals shown/hidden based on state
- [ ] Unit tests

**Technical Notes**:
- Use React state: `const [showSignals, setShowSignals] = useState(true);`

**Effort**: 2 hours  
**Dependencies**: Story 5.5.1

---

## Feature 5.6: Interactive Filters (Commodity, Time Range)

### Story 5.6.1: Create Commodity Selector Dropdown
**As a** frontend developer  
**I want** a commodity dropdown  
**So that** users can select which commodity to view

**Acceptance Criteria**:
- [ ] Dropdown with options: WTI, Brent, Natural Gas
- [ ] State tracks selected commodity
- [ ] Charts update on selection
- [ ] Unit tests

**Technical Notes**:
```tsx
<select value={commodity} onChange={(e) => setCommodity(e.target.value)}>
  <option value="WTI">WTI Crude Oil</option>
  <option value="BRENT">Brent Crude Oil</option>
  <option value="NG">Natural Gas</option>
</select>
```

**Effort**: 3 hours  
**Dependencies**: Feature 5.1 complete

---

### Story 5.6.2: Create Date Range Picker
**As a** frontend developer  
**I want** a date range picker  
**So that** users can select time periods

**Acceptance Criteria**:
- [ ] Date picker component (use library like `react-datepicker`)
- [ ] Start and end date selection
- [ ] State tracks selected range
- [ ] Charts/data update on change
- [ ] Unit tests

**Technical Notes**:
- Library: `react-datepicker`

**Effort**: 4 hours  
**Dependencies**: Feature 5.1 complete

---

### Story 5.6.3: Create Forecast Horizon Selector
**As a** frontend developer  
**I want** a horizon selector  
**So that** users can choose forecast length

**Acceptance Criteria**:
- [ ] Selector with options: 1 day, 7 days, 30 days
- [ ] State tracks selected horizon
- [ ] Forecast request uses selected horizon
- [ ] Unit tests

**Technical Notes**:
- Radio buttons or dropdown

**Effort**: 2 hours  
**Dependencies**: Feature 5.1 complete

---

### Story 5.6.4: Implement Apply Filters Button
**As a** frontend developer  
**I want** filters applied on button click  
**So that** users control when data refreshes

**Acceptance Criteria**:
- [ ] "Apply Filters" button
- [ ] Button triggers data fetch with selected filters
- [ ] Loading indicator while fetching
- [ ] Error handling
- [ ] Unit tests

**Technical Notes**:
- Collect commodity, date range, horizon
- Call API with parameters

**Effort**: 3 hours  
**Dependencies**: Stories 5.6.1-5.6.3

---

## Feature 5.7: Export Functionality (CSV, PNG)

### Story 5.7.1: Implement Export Chart as PNG
**As a** frontend developer  
**I want** to export charts as images  
**So that** users can save visualizations

**Acceptance Criteria**:
- [ ] "Export Chart" button
- [ ] Generates PNG of current chart
- [ ] Downloads with timestamp filename
- [ ] Works across browsers
- [ ] Unit tests

**Technical Notes**:
- Library: `html2canvas` or chart library's built-in export
- Chart.js: Use `chart.toBase64Image()`

**Effort**: 4 hours  
**Dependencies**: Feature 5.2 complete

---

### Story 5.7.2: Implement Export Data as CSV
**As a** frontend developer  
**I want** to export data as CSV  
**So that** users can analyze in Excel

**Acceptance Criteria**:
- [ ] "Export CSV" button
- [ ] Converts chart data to CSV format
- [ ] Downloads with timestamp filename
- [ ] Includes headers
- [ ] Unit tests

**Technical Notes**:
```tsx
const exportCSV = (data: any[]) => {
  const csv = convertToCSV(data);
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  // Trigger download
};
```

**Effort**: 3 hours  
**Dependencies**: Feature 5.2 complete

---

## Feature 5.8: Responsive Design (Mobile/Desktop)

### Story 5.8.1: Implement Responsive Layout with Breakpoints
**As a** frontend developer  
**I want** responsive layouts  
**So that** app works on all devices

**Acceptance Criteria**:
- [ ] CSS media queries or Tailwind breakpoints
- [ ] Layout adjusts: mobile (<768px), tablet (768-1024px), desktop (>1024px)
- [ ] Charts resize appropriately
- [ ] Navigation adapts (hamburger menu on mobile)
- [ ] Unit tests (visual regression optional)

**Technical Notes**:
- Breakpoints: 768px, 1024px
- Use CSS Grid or Flexbox

**Effort**: 6 hours  
**Dependencies**: All Feature 5 components

---

### Story 5.8.2: Implement Mobile Navigation (Hamburger Menu)
**As a** frontend developer  
**I want** hamburger menu on mobile  
**So that** navigation is accessible

**Acceptance Criteria**:
- [ ] Hamburger icon on mobile (<768px)
- [ ] Menu slides in on click
- [ ] Navigation links in menu
- [ ] Closes on link click or outside click
- [ ] Unit tests

**Technical Notes**:
- Use state to track menu open/closed

**Effort**: 4 hours  
**Dependencies**: Story 5.1.2

---

### Story 5.8.3: Test Cross-Browser Compatibility
**As a** QA engineer  
**I want** app tested on major browsers  
**So that** all users have good experience

**Acceptance Criteria**:
- [ ] Tested on Chrome, Firefox, Safari, Edge
- [ ] No layout issues
- [ ] Charts render correctly
- [ ] Interactions work
- [ ] Document any known issues

**Technical Notes**:
- Use BrowserStack or manual testing

**Effort**: 3 hours  
**Dependencies**: All Feature 5 complete

---

# EPIC 6: MLOps & Deployment Pipeline 🚀

## Feature 6.1: Docker Containerization

### Story 6.1.1: Create Dockerfile for Backend (FastAPI)
**As a** DevOps engineer  
**I want** backend containerized  
**So that** deployment is consistent

**Acceptance Criteria**:
- [ ] `Dockerfile` created in API directory
- [ ] Base image: `python:3.10-slim`
- [ ] Installs dependencies from `requirements.txt`
- [ ] Exposes port 8000
- [ ] CMD runs uvicorn
- [ ] Multi-stage build for optimization
- [ ] Builds successfully

**Technical Notes**:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Effort**: 4 hours  
**Dependencies**: Epic 4 complete

---

### Story 6.1.2: Create Dockerfile for Frontend (React)
**As a** DevOps engineer  
**I want** frontend containerized  
**So that** it can be deployed anywhere

**Acceptance Criteria**:
- [ ] `Dockerfile` created in dashboard directory
- [ ] Multi-stage build (build + serve)
- [ ] Stage 1: Build React app (`node:18-alpine`)
- [ ] Stage 2: Serve with nginx (`nginx:alpine`)
- [ ] Exposes port 80
- [ ] Builds successfully

**Technical Notes**:
```dockerfile
# Stage 1: Build
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Effort**: 4 hours  
**Dependencies**: Epic 5 complete

---

### Story 6.1.3: Create Docker Compose for Local Development
**As a** developer  
**I want** Docker Compose for local setup  
**So that** I can run entire stack easily

**Acceptance Criteria**:
- [ ] `docker-compose.yml` created
- [ ] Services: API, frontend, database, redis
- [ ] Volume mounts for database persistence
- [ ] Environment variables configured
- [ ] Networking between services
- [ ] `docker-compose up` works successfully
- [ ] Documentation

**Technical Notes**:
```yaml
version: '3.8'
services:
  db:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: energy_forecasting
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  api:
    build: ./src/energy-price-forecasting/api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@db:5432/energy_forecasting
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./src/energy-price-forecasting/dashboard
    ports:
      - "3000:80"
    depends_on:
      - api

volumes:
  db_data:
```

**Effort**: 5 hours  
**Dependencies**: Stories 6.1.1, 6.1.2

---

### Story 6.1.4: Create .dockerignore Files
**As a** DevOps engineer  
**I want** .dockerignore configured  
**So that** builds are fast and lean

**Acceptance Criteria**:
- [ ] `.dockerignore` for backend (exclude `__pycache__`, `.env`, `tests/`)
- [ ] `.dockerignore` for frontend (exclude `node_modules/`, `.env`)
- [ ] Build times improved
- [ ] Image sizes reduced

**Technical Notes**:
- Exclude unnecessary files from Docker context

**Effort**: 1 hour  
**Dependencies**: Stories 6.1.1, 6.1.2

---

## Feature 6.2: CI/CD Pipeline Setup (GitHub Actions)

### Story 6.2.1: Create Test Workflow
**As a** DevOps engineer  
**I want** automated testing on every push  
**So that** code quality is maintained

**Acceptance Criteria**:
- [ ] Workflow file `.github/workflows/test.yml` created
- [ ] Runs on push and pull request
- [ ] Sets up Python environment
- [ ] Installs dependencies
- [ ] Runs pytest
- [ ] Runs linter (flake8)
- [ ] Reports test results

**Technical Notes**:
```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest
      - run: flake8
```

**Effort**: 4 hours  
**Dependencies**: Epic 8 Feature 8.1 complete

---

### Story 6.2.2: Create Build Workflow (Docker Images)
**As a** DevOps engineer  
**I want** Docker images built automatically  
**So that** deployment is automated

**Acceptance Criteria**:
- [ ] Workflow file `.github/workflows/build.yml` created
- [ ] Runs on merge to `main` or `develop`
- [ ] Builds backend Docker image
- [ ] Builds frontend Docker image
- [ ] Tags images with version/commit hash
- [ ] Pushes to Docker Hub or GitHub Container Registry
- [ ] Documentation

**Technical Notes**:
```yaml
name: Build
on:
  push:
    branches: [main, develop]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      - uses: docker/build-push-action@v4
        with:
          context: ./src/energy-price-forecasting/api
          push: true
          tags: username/energy-api:latest
```

**Effort**: 5 hours  
**Dependencies**: Feature 6.1 complete

---

### Story 6.2.3: Create Deployment Workflow (Staging)
**As a** DevOps engineer  
**I want** automatic deployment to staging  
**So that** testing is streamlined

**Acceptance Criteria**:
- [ ] Workflow file `.github/workflows/deploy-staging.yml` created
- [ ] Runs on merge to `develop`
- [ ] Deploys to staging environment
- [ ] Runs smoke tests post-deployment
- [ ] Notifications on success/failure
- [ ] Documentation

**Technical Notes**:
- Deploy to staging server via SSH or cloud platform API
- Staging: separate environment (e.g., staging.yourdomain.com)

**Effort**: 6 hours  
**Dependencies**: Story 6.2.2

---

### Story 6.2.4: Create Deployment Workflow (Production)
**As a** DevOps engineer  
**I want** production deployment with approval  
**So that** releases are controlled

**Acceptance Criteria**:
- [ ] Workflow file `.github/workflows/deploy-production.yml` created
- [ ] Runs on merge to `main`
- [ ] Requires manual approval
- [ ] Deploys to production environment
- [ ] Runs health checks post-deployment
- [ ] Rollback on failure
- [ ] Notifications
- [ ] Documentation

**Technical Notes**:
- Use GitHub Actions `environment` with required reviewers

**Effort**: 6 hours  
**Dependencies**: Story 6.2.3

---

## Feature 6.3: Automated Model Training Pipeline

### Story 6.3.1: Create Model Training Script
**As a** ML engineer  
**I want** a standalone training script  
**So that** models can be retrained easily

**Acceptance Criteria**:
- [ ] Script `train_models.py` created
- [ ] Fetches latest data from database
- [ ] Trains all model types (ARIMA, LSTM)
- [ ] Evaluates on validation set
- [ ] Logs to MLflow
- [ ] Saves models
- [ ] CLI interface
- [ ] Unit tests

**Technical Notes**:
- Command: `python train_models.py --commodity WTI --model lstm`

**Effort**: 6 hours  
**Dependencies**: Epic 2 complete

---

### Story 6.3.2: Create Scheduled Training Workflow (GitHub Actions)
**As a** ML engineer  
**I want** models retrained weekly  
**So that** they stay current

**Acceptance Criteria**:
- [ ] Workflow file `.github/workflows/train-models.yml` created
- [ ] Runs on schedule (cron: weekly)
- [ ] Runs on manual trigger (workflow_dispatch)
- [ ] Executes training script
- [ ] Logs results
- [ ] Notifications on completion/failure
- [ ] Documentation

**Technical Notes**:
```yaml
name: Train Models
on:
  schedule:
    - cron: '0 6 * * 0'  # Sunday 6 AM
  workflow_dispatch:
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: python train_models.py
```

**Effort**: 4 hours  
**Dependencies**: Story 6.3.1

---

### Story 6.3.3: Store Training Results and Artifacts
**As a** ML engineer  
**I want** training results stored  
**So that** I can track model evolution

**Acceptance Criteria**:
- [ ] Training results logged to MLflow
- [ ] Model artifacts stored (MLflow or S3)
- [ ] Training metadata stored (date, parameters, metrics)
- [ ] Accessible via MLflow UI or API
- [ ] Unit tests

**Technical Notes**:
- Use MLflow artifact storage

**Effort**: 3 hours  
**Dependencies**: Story 6.3.1, Epic 2 Feature 2.6

---

## Feature 6.4: Model Validation Gates

### Story 6.4.1: Define Performance Thresholds
**As a** ML engineer  
**I want** performance thresholds defined  
**So that** poor models are rejected

**Acceptance Criteria**:
- [ ] Thresholds documented:
  - Directional Accuracy: >70%
  - Sharpe Ratio: >1.0
  - RMSE: < baseline + 10%
- [ ] Configurable in config file
- [ ] Documentation

**Technical Notes**:
- File: `config/model_validation_thresholds.yaml`

**Effort**: 2 hours  
**Dependencies**: None

---

### Story 6.4.2: Implement Validation Function
**As a** ML engineer  
**I want** automated validation checks  
**So that** only good models are deployed

**Acceptance Criteria**:
- [ ] Function `validate_model(model, validation_results, thresholds)` implemented
- [ ] Checks all thresholds
- [ ] Returns pass/fail and detailed report
- [ ] Logs validation results
- [ ] Unit tests

**Technical Notes**:
```python
def validate_model(metrics, thresholds):
    passed = True
    report = {}
    
    if metrics['directional_accuracy'] < thresholds['min_directional_accuracy']:
        passed = False
        report['directional_accuracy'] = 'FAIL'
    
    # ... check other metrics
    
    return passed, report
```

**Effort**: 4 hours  
**Dependencies**: Story 6.4.1, Epic 3 complete

---

### Story 6.4.3: Integrate Validation into Training Pipeline
**As a** ML engineer  
**I want** validation run automatically after training  
**So that** bad models are caught early

**Acceptance Criteria**:
- [ ] Validation called at end of training script
- [ ] If validation fails, model not registered/deployed
- [ ] Validation report saved
- [ ] Alert/notification on failure
- [ ] Integration tests

**Technical Notes**:
- After training, run validation
- Only register to MLflow if validation passes

**Effort**: 3 hours  
**Dependencies**: Story 6.4.2, Feature 6.3

---

## Feature 6.5: A/B Testing Framework (Champion/Challenger)

### Story 6.5.1: Design A/B Testing Architecture
**As a** ML engineer  
**I want** A/B testing architecture designed  
**So that** implementation is clear

**Acceptance Criteria**:
- [ ] Architecture documented
- [ ] Decision: traffic splitting approach (by user, random, etc.)
- [ ] Metrics collection strategy
- [ ] Statistical significance testing method
- [ ] Document in design decisions

**Technical Notes**:
- Champion: Current production model
- Challenger: New model being tested
- Split: 90% champion, 10% challenger (configurable)

**Effort**: 3 hours  
**Dependencies**: Epic 4 complete

---

### Story 6.5.2: Implement Traffic Splitting Logic
**As a** backend developer  
**I want** requests routed to champion or challenger  
**So that** A/B testing works

**Acceptance Criteria**:
- [ ] Function `select_model(user_id, split_ratio)` implemented
- [ ] Returns 'champion' or 'challenger' based on ratio
- [ ] Deterministic for same user (consistent experience)
- [ ] Configurable split ratio
- [ ] Unit tests

**Technical Notes**:
```python
def select_model(user_id: str, split_ratio: float = 0.9) -> str:
    hash_value = hash(user_id) % 100
    return 'champion' if hash_value < split_ratio * 100 else 'challenger'
```

**Effort**: 4 hours  
**Dependencies**: Story 6.5.1

---

### Story 6.5.3: Track A/B Test Results
**As a** ML engineer  
**I want** A/B test results tracked  
**So that** I can compare models

**Acceptance Criteria**:
- [ ] Log which model served each prediction
- [ ] Store predictions and actual outcomes
- [ ] Calculate metrics per model
- [ ] Statistical significance test (t-test, chi-square)
- [ ] Unit tests

**Technical Notes**:
- Store: {user_id, timestamp, model_version, prediction, actual}
- After 2+ weeks, compare metrics

**Effort**: 5 hours  
**Dependencies**: Story 6.5.2

---

### Story 6.5.4: Implement Model Promotion Logic
**As a** ML engineer  
**I want** challengers auto-promoted if better  
**So that** best model is always in production

**Acceptance Criteria**:
- [ ] Function `promote_model(challenger_metrics, champion_metrics)` implemented
- [ ] Checks if challenger significantly better
- [ ] Updates model registry (promote to production)
- [ ] Notifications on promotion
- [ ] Unit tests

**Technical Notes**:
- Promotion criteria: Challenger Sharpe Ratio > Champion + 0.1 and statistically significant

**Effort**: 4 hours  
**Dependencies**: Story 6.5.3

---

## Feature 6.6: Model Performance Monitoring

### Story 6.6.1: Collect Prediction vs Actual Data
**As a** ML engineer  
**I want** predictions and actuals logged  
**So that** I can monitor performance

**Acceptance Criteria**:
- [ ] Log every prediction to database
- [ ] Fields: timestamp, model_version, commodity, prediction, actual (updated later)
- [ ] Function `log_prediction(...)` implemented
- [ ] Function `update_actual(prediction_id, actual_value)` implemented
- [ ] Unit tests

**Technical Notes**:
- Table: `predictions` with columns above
- Actuals updated when available (next day)

**Effort**: 5 hours  
**Dependencies**: Epic 4 complete

---

### Story 6.6.2: Calculate Rolling Performance Metrics
**As a** ML engineer  
**I want** rolling metrics calculated  
**So that** I detect degradation

**Acceptance Criteria**:
- [ ] Function `calculate_rolling_metrics(window_days)` implemented
- [ ] Calculates RMSE, MAE, directional accuracy over last N days
- [ ] Stores results in monitoring table
- [ ] Scheduled daily job
- [ ] Unit tests

**Technical Notes**:
- Rolling window: 7, 30 days

**Effort**: 4 hours  
**Dependencies**: Story 6.6.1

---

### Story 6.6.3: Implement Model Drift Detection
**As a** ML engineer  
**I want** data/model drift detected  
**So that** retraining is triggered

**Acceptance Criteria**:
- [ ] Compare recent feature distributions to training data
- [ ] Statistical test (KS test, chi-square)
- [ ] Flag drift if p-value < threshold
- [ ] Alert on drift detected
- [ ] Unit tests

**Technical Notes**:
- Data drift: Input feature distributions changed
- Model drift: Performance degraded

**Effort**: 6 hours  
**Dependencies**: Story 6.6.2

---

### Story 6.6.4: Create Monitoring Dashboard (Grafana Optional)
**As a** ML engineer  
**I want** monitoring visualized  
**So that** I can see trends

**Acceptance Criteria**:
- [ ] Dashboard shows rolling RMSE, MAE, directional accuracy
- [ ] Time-series plots
- [ ] Alerts visualized
- [ ] Accessible via web interface
- [ ] Documentation

**Technical Notes**:
- Option 1: Custom React dashboard
- Option 2: Grafana + Prometheus

**Effort**: 8 hours (Optional)  
**Dependencies**: Story 6.6.2

---

## Feature 6.7: Automated Deployment to Staging/Production

### Story 6.7.1: Setup Staging Environment
**As a** DevOps engineer  
**I want** staging environment configured  
**So that** I can test deployments

**Acceptance Criteria**:
- [ ] Staging server/cluster provisioned
- [ ] Environment variables configured
- [ ] Database and Redis instances
- [ ] Accessible via staging URL
- [ ] Documentation

**Technical Notes**:
- Cloud: AWS EC2, Azure VM, DigitalOcean Droplet
- Or: Kubernetes cluster

**Effort**: 6 hours  
**Dependencies**: Feature 6.1 complete

---

### Story 6.7.2: Setup Production Environment
**As a** DevOps engineer  
**I want** production environment configured  
**So that** app can be deployed

**Acceptance Criteria**:
- [ ] Production server/cluster provisioned
- [ ] Environment variables configured
- [ ] Database and Redis instances (production-grade)
- [ ] SSL/TLS certificates configured
- [ ] Accessible via production URL
- [ ] Documentation

**Technical Notes**:
- Similar to staging but with production settings
- Ensure backups, monitoring, security

**Effort**: 6 hours  
**Dependencies**: Story 6.7.1

---

### Story 6.7.3: Implement Deployment Script
**As a** DevOps engineer  
**I want** deployment script  
**So that** deployment is automated

**Acceptance Criteria**:
- [ ] Script `deploy.sh` created
- [ ] Pulls latest Docker images
- [ ] Stops old containers
- [ ] Starts new containers
- [ ] Runs health checks
- [ ] Rolls back on failure
- [ ] Documentation

**Technical Notes**:
```bash
#!/bin/bash
docker-compose pull
docker-compose down
docker-compose up -d
# Health check
curl http://localhost:8000/health
```

**Effort**: 4 hours  
**Dependencies**: Feature 6.1 complete

---

### Story 6.7.4: Integrate Deployment into CI/CD
**As a** DevOps engineer  
**I want** deployment automated in CI/CD  
**So that** manual steps are eliminated

**Acceptance Criteria**:
- [ ] Deployment workflows call deployment script
- [ ] SSH access configured (if needed)
- [ ] Secrets managed securely (GitHub Secrets)
- [ ] Post-deployment smoke tests
- [ ] Documentation

**Technical Notes**:
- Use GitHub Actions secrets for SSH keys, API tokens

**Effort**: 4 hours  
**Dependencies**: Story 6.7.3, Feature 6.2

---

## Feature 6.8: Rollback Mechanism

### Story 6.8.1: Implement Model Rollback Function
**As a** ML engineer  
**I want** to rollback to previous model  
**So that** bad deployments can be reverted

**Acceptance Criteria**:
- [ ] Function `rollback_model(commodity, previous_version)` implemented
- [ ] Updates MLflow registry stage (demote new, promote old)
- [ ] API serves previous model
- [ ] Logs rollback action
- [ ] Unit tests

**Technical Notes**:
- MLflow: Change model stage from Production to Archived
- Promote previous version to Production

**Effort**: 4 hours  
**Dependencies**: Epic 2 Feature 2.6

---

### Story 6.8.2: Implement Application Rollback
**As a** DevOps engineer  
**I want** to rollback application deployment  
**So that** bad releases can be reverted

**Acceptance Criteria**:
- [ ] Script `rollback.sh` created
- [ ] Redeploys previous Docker image version
- [ ] Runs health checks
- [ ] Notifications on rollback
- [ ] Documentation

**Technical Notes**:
```bash
#!/bin/bash
# Rollback to previous image tag
docker-compose down
docker tag username/energy-api:previous username/energy-api:latest
docker-compose up -d
```

**Effort**: 3 hours  
**Dependencies**: Feature 6.7 complete

---

### Story 6.8.3: Create Manual Rollback Trigger (Admin Endpoint)
**As a** admin  
**I want** manual rollback endpoint  
**So that** I can trigger rollback quickly

**Acceptance Criteria**:
- [ ] `POST /api/v1/admin/rollback` endpoint
- [ ] Authentication required
- [ ] Triggers model or application rollback
- [ ] Returns status
- [ ] Logs rollback action
- [ ] Integration tests

**Technical Notes**:
- Restricted to admin API key

**Effort**: 3 hours  
**Dependencies**: Stories 6.8.1, 6.8.2

---

### Story 6.8.4: Test Rollback Process
**As a** QA engineer  
**I want** rollback tested  
**So that** it works when needed

**Acceptance Criteria**:
- [ ] Deploy new version
- [ ] Trigger rollback
- [ ] Verify previous version running
- [ ] Verify health checks pass
- [ ] Document rollback process
- [ ] Integration tests

**Technical Notes**:
- Perform in staging environment first

**Effort**: 3 hours  
**Dependencies**: Stories 6.8.1-6.8.3

---

# EPIC 7: Advanced Analytics & Insights 🔍

## Feature 7.1-7.7: (Similar detailed user stories pattern)

**Note**: Due to length, I'll provide summary structure for Epic 7. Each feature would follow the same detailed pattern as above.

**Epic 7 Features**:
- 7.1: Correlation Analysis (3-4 stories)
- 7.2: Seasonality Detection (3-4 stories)
- 7.3: Volatility Forecasting (4-5 stories)
- 7.4: Anomaly Detection (3-4 stories)
- 7.5: Market Regime Detection (4-5 stories)
- 7.6: Feature Importance (SHAP) (3-4 stories)
- 7.7: Automated Insight Generation (3-4 stories)

**Total Epic 7 Stories**: ~25-30 stories

---

# EPIC 8: Quality Assurance & Documentation ✅

## Feature 8.1-8.12: (Similar detailed user stories pattern)

**Epic 8 Features**:
- 8.1: Unit Testing Framework Setup (2-3 stories)
- 8.2: Unit Tests for All Modules (Ongoing, ~20 stories)
- 8.3: Integration Tests (4-5 stories)
- 8.4: End-to-End Tests (4-5 stories)
- 8.5: Performance Tests (3-4 stories)
- 8.6: Code Coverage Reporting (2-3 stories)
- 8.7: Project README (3-4 stories)
- 8.8: API Documentation (Covered in Epic 4)
- 8.9: Architecture Documentation (4-5 stories)
- 8.10: Model Methodology Documentation (3-4 stories)
- 8.11: Deployment Guide (3-4 stories)
- 8.12: User Guide (3-4 stories)

**Total Epic 8 Stories**: ~50-60 stories

---

## Summary

**User Stories Created**:
- **Epics 1-3**: ~100 stories (detailed in previous document)
- **Epics 4-6**: ~75 stories (detailed above)
- **Epics 7-8**: ~75-90 stories (summarized structure)

**Total Estimated User Stories**: ~250-270 stories across all 64 features

**Each story includes**:
- User story statement
- Detailed acceptance criteria
- Technical implementation notes
- Effort estimation
- Dependencies

---

**Status**: ✅ Complete User Story Documentation  
**Next Step**: Begin Implementation

Would you like me to expand Epics 7-8 with full detailed stories as well?

