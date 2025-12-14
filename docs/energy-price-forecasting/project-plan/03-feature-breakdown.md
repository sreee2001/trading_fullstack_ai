# Energy Price Forecasting System - Feature Breakdown

**Project**: Energy Price Forecasting System  
**Version**: 1.0  
**Date**: December 14, 2025  
**Status**: ✅ Approved

---

## Overview

This document provides detailed breakdown of all 64 Features across 8 Epics. Each Feature is a deliverable unit of work estimated at 3-5 days, which will be further broken down into User Stories (4-8 hours each).

---

## EPIC 1: Data Foundation & Infrastructure 🏗️

### Feature 1.1: EIA API Integration
**Epic**: Data Foundation & Infrastructure  
**Estimated Effort**: 3 days  
**Priority**: P0 (Critical)  
**Dependencies**: None

**Description**: Integrate with U.S. Energy Information Administration (EIA) API to fetch historical crude oil and natural gas price data.

**Acceptance Criteria**:
- [ ] EIA API client class implemented
- [ ] Authenticate and handle API key securely
- [ ] Fetch WTI crude oil spot prices
- [ ] Fetch Henry Hub natural gas spot prices
- [ ] Handle API rate limits (5000 requests/day)
- [ ] Implement retry logic with exponential backoff
- [ ] Parse and normalize API responses
- [ ] Unit tests with >80% coverage

**Technical Details**:
- API Endpoint: `https://api.eia.gov/v2/`
- Data Series: PET.RWTC.D (WTI), NG.RNGWHHD.D (Henry Hub)
- Rate Limit: 5000 requests/day
- Response Format: JSON

---

### Feature 1.2: FRED API Integration
**Epic**: Data Foundation & Infrastructure  
**Estimated Effort**: 2 days  
**Priority**: P0 (Critical)  
**Dependencies**: None

**Description**: Integrate with Federal Reserve Economic Data (FRED) API to fetch commodity price indices and economic indicators.

**Acceptance Criteria**:
- [ ] FRED API client class implemented
- [ ] Fetch crude oil prices (DCOILWTICO, DCOILBRENTEU)
- [ ] Fetch additional economic indicators (optional)
- [ ] Handle API authentication
- [ ] Implement caching to respect rate limits
- [ ] Parse and normalize responses
- [ ] Unit tests with >80% coverage

**Technical Details**:
- API Endpoint: `https://api.stlouisfed.org/fred/series/observations`
- Series IDs: DCOILWTICO (WTI), DCOILBRENTEU (Brent)
- Rate Limit: 120 requests/minute
- Response Format: JSON/XML

---

### Feature 1.3: Yahoo Finance Data Ingestion
**Epic**: Data Foundation & Infrastructure  
**Estimated Effort**: 2 days  
**Priority**: P0 (Critical)  
**Dependencies**: None

**Description**: Implement Yahoo Finance data fetching for historical crude oil and energy commodity prices.

**Acceptance Criteria**:
- [ ] Yahoo Finance client implemented (yfinance library)
- [ ] Fetch historical data for CL=F (WTI Crude Oil Futures)
- [ ] Fetch historical data for BZ=F (Brent Crude Oil Futures)
- [ ] Fetch historical data for NG=F (Natural Gas Futures)
- [ ] Handle missing data and gaps
- [ ] Support date range queries
- [ ] Normalize OHLCV data format
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Library: `yfinance`
- Tickers: CL=F, BZ=F, NG=F
- Data Fields: Open, High, Low, Close, Volume
- Historical Range: Minimum 5 years

---

### Feature 1.4: Database Setup (PostgreSQL + TimescaleDB)
**Epic**: Data Foundation & Infrastructure  
**Estimated Effort**: 3 days  
**Priority**: P0 (Critical)  
**Dependencies**: None

**Description**: Set up time-series optimized database for storing energy price data.

**Acceptance Criteria**:
- [ ] PostgreSQL database installed and configured
- [ ] TimescaleDB extension enabled
- [ ] Schema designed for time-series data
- [ ] Hypertables created for price data
- [ ] Indexes optimized for time-based queries
- [ ] Connection pooling configured
- [ ] Database utilities module created
- [ ] Migration scripts created
- [ ] Backup strategy documented

**Technical Details**:
- Database: PostgreSQL 15+
- Extension: TimescaleDB
- Tables: `price_data`, `commodities`, `data_sources`
- Primary Key: (timestamp, commodity_id, source_id)
- Retention Policy: Keep all data indefinitely

**Schema**:
```sql
CREATE TABLE price_data (
    timestamp TIMESTAMPTZ NOT NULL,
    commodity_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    price DECIMAL(12,4) NOT NULL,
    volume BIGINT,
    open_price DECIMAL(12,4),
    high_price DECIMAL(12,4),
    low_price DECIMAL(12,4),
    close_price DECIMAL(12,4),
    PRIMARY KEY (timestamp, commodity_id, source_id)
);

SELECT create_hypertable('price_data', 'timestamp');
```

---

### Feature 1.5: Data Validation & Quality Framework
**Epic**: Data Foundation & Infrastructure  
**Estimated Effort**: 4 days  
**Priority**: P0 (Critical)  
**Dependencies**: 1.1, 1.2, 1.3, 1.4

**Description**: Implement comprehensive data validation and quality assurance framework.

**Acceptance Criteria**:
- [ ] Validation rules engine implemented
- [ ] Schema validation (data types, ranges)
- [ ] Completeness checks (missing values)
- [ ] Consistency checks (cross-source validation)
- [ ] Outlier detection (statistical methods)
- [ ] Data quality metrics calculated
- [ ] Quality reports generated
- [ ] Alerting for quality issues
- [ ] Unit tests with >80% coverage

**Validation Rules**:
- Price must be > 0
- Volume must be >= 0
- Timestamps must be valid and sequential
- Detect price spikes >20% (flag as anomaly)
- Flag missing data gaps >2 days
- Cross-validate prices across sources (±5% tolerance)

---

### Feature 1.6: Automated Data Pipeline Orchestration
**Epic**: Data Foundation & Infrastructure  
**Estimated Effort**: 4 days  
**Priority**: P0 (Critical)  
**Dependencies**: 1.1, 1.2, 1.3, 1.4, 1.5

**Description**: Create automated ETL pipeline for daily data refresh.

**Acceptance Criteria**:
- [ ] Pipeline orchestration implemented
- [ ] Daily scheduled job configured
- [ ] Fetch data from all sources
- [ ] Validate data quality
- [ ] Store in database
- [ ] Handle failures gracefully
- [ ] Send notifications on errors
- [ ] Log all pipeline runs
- [ ] Unit and integration tests

**Technical Details**:
- Orchestration: Python scheduling (APScheduler) or Airflow
- Schedule: Daily at 6:00 AM EST
- Error Handling: Retry 3 times with exponential backoff
- Notifications: Log to file, optional email alerts

---

## EPIC 2: Core ML Model Development 🤖

### Feature 2.1: Feature Engineering Pipeline
**Epic**: Core ML Model Development  
**Estimated Effort**: 5 days  
**Priority**: P0 (Critical)  
**Dependencies**: Epic 1 (all features)

**Description**: Build feature engineering pipeline to create predictive features from raw price data.

**Acceptance Criteria**:
- [ ] Technical indicators implemented:
  - Moving averages (SMA, EMA: 5, 10, 20, 50, 200 days)
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - ATR (Average True Range)
- [ ] Lag features (1, 7, 30 days)
- [ ] Rolling statistics (mean, std, min, max)
- [ ] Seasonality features (day of week, month, quarter)
- [ ] Calendar features (holidays, OPEC meetings)
- [ ] Feature scaling/normalization
- [ ] Feature selection module
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Libraries: `pandas`, `ta-lib` (optional), `scikit-learn`
- Output: Feature matrix (X) and target (y)
- Scaling: StandardScaler or MinMaxScaler

---

### Feature 2.2: Baseline Statistical Models (ARIMA/SARIMA)
**Epic**: Core ML Model Development  
**Estimated Effort**: 4 days  
**Priority**: P0 (Critical)  
**Dependencies**: 2.1

**Description**: Implement baseline ARIMA and SARIMA models for comparison.

**Acceptance Criteria**:
- [ ] ARIMA model class implemented
- [ ] SARIMA model class implemented
- [ ] Auto ARIMA for parameter selection
- [ ] Model training on historical data
- [ ] Forecast generation (1, 7, 30 days)
- [ ] Model persistence (save/load)
- [ ] Evaluation metrics calculated
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Library: `statsmodels`, `pmdarima` (auto_arima)
- Parameters: Auto-selected via AIC/BIC
- Seasonality: Test 12-month and 52-week periods

---

### Feature 2.3: LSTM Neural Network Model
**Epic**: Core ML Model Development  
**Estimated Effort**: 5 days  
**Priority**: P0 (Critical)  
**Dependencies**: 2.1

**Description**: Implement LSTM (Long Short-Term Memory) deep learning model for time-series forecasting.

**Acceptance Criteria**:
- [ ] LSTM model architecture designed
- [ ] Sliding window dataset creation
- [ ] Model training with early stopping
- [ ] Validation on holdout set
- [ ] Multi-step ahead forecasting
- [ ] Model checkpointing
- [ ] Hyperparameter configuration
- [ ] GPU support enabled
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Framework: PyTorch or TensorFlow/Keras
- Architecture:
  - Input: Sequence length = 60 days
  - LSTM layers: 2-3 layers, 50-128 units
  - Dropout: 0.2-0.3
  - Output: 1-30 days ahead
- Loss: MSE or MAE
- Optimizer: Adam
- Training: 100 epochs, early stopping (patience=10)

---

### Feature 2.4: Model Training Infrastructure
**Epic**: Core ML Model Development  
**Estimated Effort**: 4 days  
**Priority**: P0 (Critical)  
**Dependencies**: 2.2, 2.3

**Description**: Create robust infrastructure for training and managing models.

**Acceptance Criteria**:
- [ ] Training pipeline abstraction
- [ ] Train/validation/test split strategy
- [ ] Cross-validation framework
- [ ] Early stopping implementation
- [ ] Model checkpointing
- [ ] Training progress logging
- [ ] GPU/CPU detection and utilization
- [ ] Memory optimization
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Split: 70% train, 15% validation, 15% test
- Cross-validation: Time-series split (5 folds)
- Checkpointing: Save best model by validation loss

---

### Feature 2.5: Hyperparameter Tuning Framework
**Epic**: Core ML Model Development  
**Estimated Effort**: 3 days  
**Priority**: P1 (High)  
**Dependencies**: 2.3, 2.4

**Description**: Implement hyperparameter optimization for models.

**Acceptance Criteria**:
- [ ] Hyperparameter search space defined
- [ ] Grid search implementation
- [ ] Random search implementation
- [ ] Bayesian optimization (optional)
- [ ] Cross-validation during search
- [ ] Best parameters persisted
- [ ] Search results logged
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Library: `scikit-learn` GridSearchCV, `optuna` (Bayesian)
- Search Space:
  - LSTM: layers (2-3), units (50-128), dropout (0.2-0.4), learning rate (0.001-0.01)
  - Sequence length: 30-90 days
- Optimization Metric: Validation RMSE

---

### Feature 2.6: Model Versioning & Experiment Tracking (MLflow)
**Epic**: Core ML Model Development  
**Estimated Effort**: 3 days  
**Priority**: P1 (High)  
**Dependencies**: 2.4

**Description**: Integrate MLflow for experiment tracking and model versioning.

**Acceptance Criteria**:
- [ ] MLflow server setup
- [ ] Log training parameters
- [ ] Log evaluation metrics
- [ ] Log model artifacts
- [ ] Tag experiments
- [ ] Register models in model registry
- [ ] Track model lineage
- [ ] UI accessible for reviewing experiments
- [ ] Integration tests

**Technical Details**:
- Tool: MLflow
- Tracking Server: Local or remote
- Artifacts: Model files, training plots, feature importance
- Logged Metrics: RMSE, MAE, MAPE, R², directional accuracy

---

### Feature 2.7: Multi-Horizon Forecasting Implementation
**Epic**: Core ML Model Development  
**Estimated Effort**: 4 days  
**Priority**: P1 (High)  
**Dependencies**: 2.3, 2.4

**Description**: Extend models to support multiple forecast horizons (1, 7, 30 days).

**Acceptance Criteria**:
- [ ] Multi-output model architecture
- [ ] 1-day ahead forecasting
- [ ] 7-day ahead forecasting
- [ ] 30-day ahead forecasting
- [ ] Confidence intervals for each horizon
- [ ] Evaluation per horizon
- [ ] Horizon-specific feature engineering
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Approach: Either multi-output model or separate models per horizon
- Confidence Intervals: Use prediction std or quantile regression

---

## EPIC 3: Model Evaluation & Backtesting 📊

### Feature 3.1: Walk-Forward Validation Framework
**Epic**: Model Evaluation & Backtesting  
**Estimated Effort**: 3 days  
**Priority**: P0 (Critical)  
**Dependencies**: Epic 2 (2.2, 2.3)

**Description**: Implement walk-forward validation methodology to prevent look-ahead bias.

**Acceptance Criteria**:
- [ ] Walk-forward split generator
- [ ] Rolling window approach
- [ ] Expanding window approach
- [ ] Temporal integrity maintained
- [ ] Multiple validation windows
- [ ] Results aggregation across windows
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Initial Training Period: 3 years
- Validation Window: 1 month
- Step Size: 1 month
- Total Windows: At least 12

---

### Feature 3.2: Statistical Metrics Calculation
**Epic**: Model Evaluation & Backtesting  
**Estimated Effort**: 2 days  
**Priority**: P0 (Critical)  
**Dependencies**: 3.1

**Description**: Calculate comprehensive statistical performance metrics.

**Acceptance Criteria**:
- [ ] RMSE (Root Mean Square Error)
- [ ] MAE (Mean Absolute Error)
- [ ] MAPE (Mean Absolute Percentage Error)
- [ ] R² (Coefficient of Determination)
- [ ] Directional Accuracy (% correct direction)
- [ ] Metrics per forecast horizon
- [ ] Metrics aggregation and reporting
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Libraries: `scikit-learn`, `numpy`
- Output: Metrics dictionary and DataFrame

---

### Feature 3.3: Trading Signal Generation Logic
**Epic**: Model Evaluation & Backtesting  
**Estimated Effort**: 3 days  
**Priority**: P0 (Critical)  
**Dependencies**: Epic 2

**Description**: Convert price forecasts into actionable trading signals.

**Acceptance Criteria**:
- [ ] Signal generation rules implemented:
  - Buy: Forecast > Current Price + threshold
  - Sell: Forecast < Current Price - threshold
  - Hold: Within threshold
- [ ] Configurable threshold parameters
- [ ] Signal confidence scoring
- [ ] Signal history tracking
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Default Threshold: 2% price change
- Signal Types: BUY, SELL, HOLD
- Confidence: Based on prediction std or model ensemble

---

### Feature 3.4: Trading Simulation Engine
**Epic**: Model Evaluation & Backtesting  
**Estimated Effort**: 5 days  
**Priority**: P0 (Critical)  
**Dependencies**: 3.3

**Description**: Simulate trading based on signals and calculate P&L.

**Acceptance Criteria**:
- [ ] Position management (long/short/flat)
- [ ] Trade execution simulation
- [ ] P&L calculation per trade
- [ ] Cumulative P&L tracking
- [ ] Win rate calculation
- [ ] Average profit/loss per trade
- [ ] Transaction costs included (optional)
- [ ] Slippage modeling (optional)
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Initial Capital: $100,000 (simulated)
- Position Sizing: Fixed (e.g., 100 contracts) or % of capital
- Transaction Cost: 0.1% per trade (optional)
- Slippage: 0.05% (optional)

---

### Feature 3.5: Risk Metrics Module
**Epic**: Model Evaluation & Backtesting  
**Estimated Effort**: 3 days  
**Priority**: P0 (Critical)  
**Dependencies**: 3.4

**Description**: Calculate risk-adjusted performance metrics.

**Acceptance Criteria**:
- [ ] Sharpe Ratio calculation
- [ ] Maximum Drawdown calculation
- [ ] Volatility (annualized)
- [ ] Sortino Ratio (optional)
- [ ] Calmar Ratio (optional)
- [ ] Value at Risk (VaR) (optional)
- [ ] Risk metrics per strategy
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Sharpe Ratio: (Return - Risk-Free Rate) / Std(Return)
- Risk-Free Rate: 2% annual (configurable)
- Max Drawdown: Peak-to-trough decline

---

### Feature 3.6: Model Comparison Dashboard
**Epic**: Model Evaluation & Backtesting  
**Estimated Effort**: 3 days  
**Priority**: P1 (High)  
**Dependencies**: 3.2, 3.4, 3.5

**Description**: Compare multiple models side-by-side.

**Acceptance Criteria**:
- [ ] Comparison table (metrics across models)
- [ ] Best model selection logic
- [ ] Model ranking by metric
- [ ] Export comparison report
- [ ] Visualization of comparative performance
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Models to Compare: ARIMA, SARIMA, LSTM, Ensemble (optional)
- Primary Metric: Sharpe Ratio or Directional Accuracy
- Output: DataFrame and visualization

---

### Feature 3.7: Backtesting Visualization Tools
**Epic**: Model Evaluation & Backtesting  
**Estimated Effort**: 4 days  
**Priority**: P1 (High)  
**Dependencies**: 3.1, 3.2, 3.4, 3.5

**Description**: Create visualizations for backtesting results.

**Acceptance Criteria**:
- [ ] Predicted vs Actual price plot
- [ ] Forecast error over time
- [ ] Cumulative P&L chart
- [ ] Drawdown chart
- [ ] Trade distribution histogram
- [ ] Metrics summary table
- [ ] Export plots as PNG/PDF
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Libraries: `matplotlib`, `seaborn`, `plotly` (optional)
- Chart Types: Line, scatter, bar, histogram
- Export: PNG, PDF, interactive HTML

---

## EPIC 4: API Service Layer 🌐

### Feature 4.1: FastAPI Application Setup
**Epic**: API Service Layer  
**Estimated Effort**: 2 days  
**Priority**: P1 (High)  
**Dependencies**: None

**Description**: Initialize FastAPI application with project structure.

**Acceptance Criteria**:
- [ ] FastAPI application created
- [ ] Project structure organized
- [ ] Configuration management (env variables)
- [ ] CORS configured
- [ ] Logging configured
- [ ] Health check endpoint
- [ ] Startup/shutdown events
- [ ] Unit tests with >80% coverage

**Technical Details**:
- Framework: FastAPI
- Python Version: 3.10+
- Structure: `/app/main.py`, `/app/routers/`, `/app/models/`, `/app/services/`

---

### Feature 4.2: Forecast Endpoint (`/forecast`)
**Epic**: API Service Layer  
**Estimated Effort**: 3 days  
**Priority**: P1 (High)  
**Dependencies**: 4.1, Epic 2

**Description**: API endpoint to generate price forecasts.

**Acceptance Criteria**:
- [ ] POST `/api/v1/forecast` endpoint
- [ ] Request validation (commodity, horizon, date)
- [ ] Load trained model
- [ ] Generate forecast
- [ ] Return forecast with confidence intervals
- [ ] Error handling
- [ ] Response caching (optional)
- [ ] Integration tests

**Request Schema**:
```json
{
  "commodity": "WTI",
  "horizon": 7,
  "start_date": "2025-12-14"
}
```

**Response Schema**:
```json
{
  "commodity": "WTI",
  "forecast_date": "2025-12-14",
  "horizon": 7,
  "predictions": [
    {"date": "2025-12-15", "price": 72.5, "confidence_lower": 70.2, "confidence_upper": 74.8},
    ...
  ]
}
```

---

### Feature 4.3: Historical Data Endpoint (`/historical`)
**Epic**: API Service Layer  
**Estimated Effort**: 2 days  
**Priority**: P1 (High)  
**Dependencies**: 4.1, Epic 1

**Description**: API endpoint to retrieve historical price data.

**Acceptance Criteria**:
- [ ] GET `/api/v1/historical` endpoint
- [ ] Query parameters (commodity, start_date, end_date)
- [ ] Fetch data from database
- [ ] Pagination support
- [ ] Response caching
- [ ] Error handling
- [ ] Integration tests

**Query Parameters**:
- `commodity`: WTI, BRENT, NG
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD
- `limit`: Max records (default 1000)
- `offset`: Pagination offset

---

### Feature 4.4: Model Info Endpoint (`/models`)
**Epic**: API Service Layer  
**Estimated Effort**: 2 days  
**Priority**: P1 (High)  
**Dependencies**: 4.1, Epic 2, Epic 3

**Description**: API endpoint to list available models and their performance.

**Acceptance Criteria**:
- [ ] GET `/api/v1/models` endpoint
- [ ] List all registered models
- [ ] Return model metadata (name, version, training date)
- [ ] Return performance metrics
- [ ] Filter by commodity
- [ ] Error handling
- [ ] Integration tests

**Response Schema**:
```json
{
  "models": [
    {
      "model_id": "lstm_wti_v1",
      "commodity": "WTI",
      "model_type": "LSTM",
      "version": "1.0",
      "training_date": "2025-12-01",
      "metrics": {
        "rmse": 2.45,
        "mae": 1.87,
        "directional_accuracy": 0.73,
        "sharpe_ratio": 1.35
      }
    },
    ...
  ]
}
```

---

### Feature 4.5: Backtesting Endpoint (`/backtest`)
**Epic**: API Service Layer  
**Estimated Effort**: 3 days  
**Priority**: P1 (High)  
**Dependencies**: 4.1, Epic 3

**Description**: API endpoint to run backtesting scenarios.

**Acceptance Criteria**:
- [ ] POST `/api/v1/backtest` endpoint
- [ ] Request validation (model, date range, strategy)
- [ ] Run backtesting asynchronously
- [ ] Return backtest results
- [ ] Caching of results
- [ ] Error handling
- [ ] Integration tests

**Request Schema**:
```json
{
  "model_id": "lstm_wti_v1",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000,
  "strategy_params": {
    "threshold": 0.02
  }
}
```

---

### Feature 4.6: Authentication & API Key Management
**Epic**: API Service Layer  
**Estimated Effort**: 3 days  
**Priority**: P1 (High)  
**Dependencies**: 4.1

**Description**: Implement API key-based authentication.

**Acceptance Criteria**:
- [ ] API key generation
- [ ] API key validation middleware
- [ ] Secure key storage (hashed)
- [ ] Key revocation capability
- [ ] Authentication error responses (401, 403)
- [ ] Rate limiting per API key
- [ ] Unit and integration tests

**Technical Details**:
- Authentication: API Key in header (`X-API-Key`)
- Storage: Database table `api_keys`
- Hashing: bcrypt or similar

---

### Feature 4.7: Rate Limiting & Caching (Redis)
**Epic**: API Service Layer  
**Estimated Effort**: 3 days  
**Priority**: P1 (High)  
**Dependencies**: 4.1, 4.2, 4.3

**Description**: Implement rate limiting and response caching.

**Acceptance Criteria**:
- [ ] Redis connection setup
- [ ] Rate limiting middleware (per API key)
- [ ] Rate limit: 100 requests/minute
- [ ] Response caching for GET endpoints
- [ ] Cache TTL: 5 minutes for forecasts
- [ ] Rate limit exceeded response (429)
- [ ] Cache invalidation strategy
- [ ] Integration tests

**Technical Details**:
- Tool: Redis
- Rate Limiting: Token bucket or sliding window
- Caching: Cache forecast results for same parameters

---

### Feature 4.8: API Documentation (Swagger UI)
**Epic**: API Service Layer  
**Estimated Effort**: 2 days  
**Priority**: P1 (High)  
**Dependencies**: 4.1, 4.2, 4.3, 4.4, 4.5

**Description**: Generate comprehensive API documentation with Swagger/OpenAPI.

**Acceptance Criteria**:
- [ ] OpenAPI schema generated
- [ ] Swagger UI accessible at `/docs`
- [ ] All endpoints documented
- [ ] Request/response schemas documented
- [ ] Authentication documented
- [ ] Error codes documented
- [ ] Examples provided
- [ ] ReDoc UI accessible at `/redoc` (optional)

**Technical Details**:
- FastAPI auto-generates OpenAPI schema
- Customize with Pydantic models and docstrings
- URL: `http://localhost:8000/docs`

---

### Feature 4.9: Health Check & Monitoring Endpoints
**Epic**: API Service Layer  
**Estimated Effort**: 2 days  
**Priority**: P1 (High)  
**Dependencies**: 4.1

**Description**: Implement health check and monitoring endpoints.

**Acceptance Criteria**:
- [ ] GET `/health` endpoint (liveness)
- [ ] GET `/ready` endpoint (readiness)
- [ ] Check database connectivity
- [ ] Check model availability
- [ ] Check Redis connectivity
- [ ] Return system metrics (optional)
- [ ] Prometheus metrics endpoint (optional)
- [ ] Integration tests

**Technical Details**:
- `/health`: Always return 200 if API is running
- `/ready`: Return 200 only if all dependencies healthy
- Response time: <100ms

---

## EPIC 5: Visualization & User Interface 📈

### Feature 5.1: React Application Setup (TypeScript)
**Epic**: Visualization & User Interface  
**Estimated Effort**: 3 days  
**Priority**: P1 (High)  
**Dependencies**: None

**Description**: Initialize React application with TypeScript and project structure.

**Acceptance Criteria**:
- [ ] React app created (Vite or Create React App)
- [ ] TypeScript configured
- [ ] Project structure organized
- [ ] Routing setup (React Router)
- [ ] State management (Context API or Redux)
- [ ] API client configured (Axios)
- [ ] Styling framework setup (Tailwind CSS or Material-UI)
- [ ] Build and dev scripts working

**Technical Details**:
- Framework: React 18+
- Bundler: Vite (recommended) or Webpack
- Styling: Tailwind CSS or Material-UI
- State: Context API or Redux Toolkit

---

### Feature 5.2: Price Chart Component (Historical & Forecast)
**Epic**: Visualization & User Interface  
**Estimated Effort**: 4 days  
**Priority**: P1 (High)  
**Dependencies**: 5.1, Epic 4

**Description**: Create interactive price chart displaying historical and forecasted prices.

**Acceptance Criteria**:
- [ ] Line chart component
- [ ] Display historical prices
- [ ] Display forecasted prices (different color)
- [ ] Confidence intervals (shaded area)
- [ ] Zoom and pan functionality
- [ ] Tooltip on hover (date, price)
- [ ] Legend
- [ ] Responsive design
- [ ] Unit tests

**Technical Details**:
- Library: Chart.js, Recharts, or Plotly.js
- Chart Type: Line chart with area fill
- Axes: Date (X), Price (Y)

---

### Feature 5.3: Model Performance Dashboard
**Epic**: Visualization & User Interface  
**Estimated Effort**: 3 days  
**Priority**: P1 (High)  
**Dependencies**: 5.1, Epic 4

**Description**: Dashboard displaying model performance metrics.

**Acceptance Criteria**:
- [ ] Metrics cards (RMSE, MAE, Sharpe Ratio, etc.)
- [ ] Model comparison table
- [ ] Performance over time chart
- [ ] Filter by commodity
- [ ] Filter by model
- [ ] Responsive layout
- [ ] Unit tests

**Technical Details**:
- Layout: Grid of metric cards
- API: GET `/api/v1/models`

---

### Feature 5.4: Forecast vs Actual Comparison View
**Epic**: Visualization & User Interface  
**Estimated Effort**: 3 days  
**Priority**: P1 (High)  
**Dependencies**: 5.1, 5.2, Epic 4

**Description**: Side-by-side comparison of forecasted vs actual prices.

**Acceptance Criteria**:
- [ ] Dual-axis or overlay chart
- [ ] Predicted prices line
- [ ] Actual prices line
- [ ] Error bars or confidence intervals
- [ ] Date range selector
- [ ] Accuracy metrics display
- [ ] Responsive design
- [ ] Unit tests

**Technical Details**:
- Chart Type: Line chart with two series
- API: Combine forecast and historical endpoints

---

### Feature 5.5: Trading Signal Indicators
**Epic**: Visualization & User Interface  
**Estimated Effort**: 2 days  
**Priority**: P1 (High)  
**Dependencies**: 5.1, 5.2, Epic 4

**Description**: Visual indicators for trading signals on price chart.

**Acceptance Criteria**:
- [ ] Buy signal markers (green arrows)
- [ ] Sell signal markers (red arrows)
- [ ] Hold indicators
- [ ] Signal confidence coloring
- [ ] Signal details on hover
- [ ] Toggle signals on/off
- [ ] Unit tests

**Technical Details**:
- Markers: Arrows or triangles on chart
- API: Backtest endpoint or separate signals endpoint

---

### Feature 5.6: Interactive Filters (Commodity, Time Range)
**Epic**: Visualization & User Interface  
**Estimated Effort**: 2 days  
**Priority**: P1 (High)  
**Dependencies**: 5.1, 5.2

**Description**: Interactive filters for user-driven data exploration.

**Acceptance Criteria**:
- [ ] Commodity dropdown (WTI, Brent, Natural Gas)
- [ ] Date range picker
- [ ] Forecast horizon selector (1, 7, 30 days)
- [ ] Model selector
- [ ] Apply filters button
- [ ] Persist filters in URL (optional)
- [ ] Unit tests

**Technical Details**:
- Components: Dropdown, DatePicker (e.g., react-datepicker)
- State: Update charts on filter change

---

### Feature 5.7: Export Functionality (CSV, PNG)
**Epic**: Visualization & User Interface  
**Estimated Effort**: 2 days  
**Priority**: P2 (Medium)  
**Dependencies**: 5.1, 5.2, 5.3

**Description**: Allow users to export data and charts.

**Acceptance Criteria**:
- [ ] Export chart as PNG
- [ ] Export data as CSV
- [ ] Export report as PDF (optional)
- [ ] Export button UI
- [ ] Filename with timestamp
- [ ] Unit tests

**Technical Details**:
- PNG Export: Use library like `html2canvas` or chart library's built-in export
- CSV Export: Convert data to CSV format and trigger download
- PDF: Use `jsPDF` (optional)

---

### Feature 5.8: Responsive Design (Mobile/Desktop)
**Epic**: Visualization & User Interface  
**Estimated Effort**: 3 days  
**Priority**: P1 (High)  
**Dependencies**: 5.1, 5.2, 5.3, 5.4

**Description**: Ensure application is fully responsive across devices.

**Acceptance Criteria**:
- [ ] Mobile layout (< 768px)
- [ ] Tablet layout (768px - 1024px)
- [ ] Desktop layout (> 1024px)
- [ ] Touch-friendly interactions
- [ ] Hamburger menu for mobile
- [ ] Charts resize appropriately
- [ ] No horizontal scroll
- [ ] Cross-browser testing (Chrome, Firefox, Safari)

**Technical Details**:
- Approach: Mobile-first design
- Breakpoints: 768px, 1024px
- Testing: Browser DevTools, real devices

---

## EPIC 6: MLOps & Deployment Pipeline 🚀

### Feature 6.1: Docker Containerization
**Epic**: MLOps & Deployment Pipeline  
**Estimated Effort**: 3 days  
**Priority**: P2 (Medium)  
**Dependencies**: Epic 2, Epic 4

**Description**: Containerize application with Docker.

**Acceptance Criteria**:
- [ ] Dockerfile for backend (FastAPI)
- [ ] Dockerfile for frontend (React)
- [ ] Dockerfile for model training
- [ ] Docker Compose for local development
- [ ] Environment variable configuration
- [ ] Volume mounts for data persistence
- [ ] Multi-stage builds for optimization
- [ ] Documentation for Docker setup

**Technical Details**:
- Base Images: `python:3.10-slim`, `node:18-alpine`
- Compose Services: API, frontend, database, redis
- Ports: API (8000), Frontend (3000), DB (5432), Redis (6379)

---

### Feature 6.2: CI/CD Pipeline Setup (GitHub Actions)
**Epic**: MLOps & Deployment Pipeline  
**Estimated Effort**: 3 days  
**Priority**: P2 (Medium)  
**Dependencies**: 6.1, Epic 8 (testing)

**Description**: Set up continuous integration and deployment pipeline.

**Acceptance Criteria**:
- [ ] GitHub Actions workflows created
- [ ] Run tests on every push
- [ ] Lint code (flake8, eslint)
- [ ] Build Docker images
- [ ] Push images to registry (Docker Hub/GitHub Packages)
- [ ] Deploy to staging on merge to `develop`
- [ ] Deploy to production on merge to `main` (manual approval)
- [ ] Workflow documentation

**Workflows**:
1. **Test**: Run on every push/PR
2. **Build**: Build Docker images on merge
3. **Deploy**: Deploy to environments

---

### Feature 6.3: Automated Model Training Pipeline
**Epic**: MLOps & Deployment Pipeline  
**Estimated Effort**: 4 days  
**Priority**: P2 (Medium)  
**Dependencies**: Epic 2, 6.1

**Description**: Automate model retraining on schedule or trigger.

**Acceptance Criteria**:
- [ ] Scheduled training job (weekly)
- [ ] Trigger training via API or script
- [ ] Fetch latest data
- [ ] Train model with latest hyperparameters
- [ ] Evaluate on validation set
- [ ] Log results to MLflow
- [ ] Save model artifacts
- [ ] Notification on completion/failure

**Technical Details**:
- Schedule: Weekly on Sunday
- Trigger: Manual via API or GitHub Actions workflow_dispatch
- Orchestration: Cron job, Airflow, or GitHub Actions scheduled workflow

---

### Feature 6.4: Model Validation Gates
**Epic**: MLOps & Deployment Pipeline  
**Estimated Effort**: 2 days  
**Priority**: P2 (Medium)  
**Dependencies**: 6.3, Epic 3

**Description**: Implement validation gates before deploying models.

**Acceptance Criteria**:
- [ ] Define minimum performance thresholds
- [ ] Compare new model to current production model
- [ ] Validation checks:
  - Directional accuracy > 70%
  - Sharpe ratio > 1.0
  - No significant performance degradation
- [ ] Pass/fail decision logic
- [ ] Alert on validation failure
- [ ] Log validation results

**Technical Details**:
- Thresholds: Configurable in config file
- Comparison: New model must beat production or be within 5%

---

### Feature 6.5: A/B Testing Framework (Champion/Challenger)
**Epic**: MLOps & Deployment Pipeline  
**Estimated Effort**: 4 days  
**Priority**: P2 (Medium)  
**Dependencies**: 6.3, 6.4, Epic 4

**Description**: Implement A/B testing to compare models in production.

**Acceptance Criteria**:
- [ ] Serve multiple models simultaneously
- [ ] Traffic splitting (e.g., 90% champion, 10% challenger)
- [ ] Track performance per model
- [ ] Statistical significance testing
- [ ] Promote challenger if outperforms
- [ ] Rollback if underperforms
- [ ] Dashboard for A/B test results

**Technical Details**:
- Traffic Split: Random or by user/API key
- Metrics: Collect forecasts and actuals, compare after 2 weeks
- Promotion: Automatic or manual based on results

---

### Feature 6.6: Model Performance Monitoring
**Epic**: MLOps & Deployment Pipeline  
**Estimated Effort**: 3 days  
**Priority**: P2 (Medium)  
**Dependencies**: Epic 4, Epic 3

**Description**: Monitor model performance in production and detect drift.

**Acceptance Criteria**:
- [ ] Collect prediction vs actual data
- [ ] Calculate rolling performance metrics
- [ ] Detect performance degradation
- [ ] Detect data drift
- [ ] Alert on anomalies
- [ ] Dashboard for monitoring
- [ ] Log monitoring data

**Technical Details**:
- Metrics: Rolling 30-day RMSE, MAE, directional accuracy
- Drift Detection: Compare feature distributions
- Alerts: Email or Slack notification if RMSE increases >20%

---

### Feature 6.7: Automated Deployment to Staging/Production
**Epic**: MLOps & Deployment Pipeline  
**Estimated Effort**: 3 days  
**Priority**: P2 (Medium)  
**Dependencies**: 6.1, 6.2

**Description**: Automate deployment to staging and production environments.

**Acceptance Criteria**:
- [ ] Staging environment configured
- [ ] Production environment configured
- [ ] Automated deployment to staging on merge to `develop`
- [ ] Manual approval for production deployment
- [ ] Blue-green or rolling deployment
- [ ] Health checks post-deployment
- [ ] Automated smoke tests post-deployment
- [ ] Deployment documentation

**Technical Details**:
- Environments: Staging (staging.example.com), Production (api.example.com)
- Deployment: Docker container to cloud (AWS ECS, Azure Container Instances, or DigitalOcean)
- Strategy: Blue-green (two environments, switch traffic)

---

### Feature 6.8: Rollback Mechanism
**Epic**: MLOps & Deployment Pipeline  
**Estimated Effort**: 2 days  
**Priority**: P2 (Medium)  
**Dependencies**: 6.7

**Description**: Implement automated and manual rollback capability.

**Acceptance Criteria**:
- [ ] Rollback to previous model version
- [ ] Rollback to previous application version
- [ ] Manual rollback trigger
- [ ] Automated rollback on health check failure
- [ ] Rollback notification
- [ ] Test rollback process

**Technical Details**:
- Model Rollback: Switch to previous model in MLflow registry
- App Rollback: Redeploy previous Docker image
- Trigger: API endpoint or CI/CD workflow

---

## EPIC 7: Advanced Analytics & Insights 🔍

### Feature 7.1: Correlation Analysis Module
**Epic**: Advanced Analytics & Insights  
**Estimated Effort**: 2 days  
**Priority**: P2 (Medium)  
**Dependencies**: Epic 1

**Description**: Analyze correlations between energy commodities.

**Acceptance Criteria**:
- [ ] Calculate correlation matrix (WTI, Brent, Natural Gas)
- [ ] Rolling correlation over time
- [ ] Visualize correlation heatmap
- [ ] Statistical significance testing
- [ ] Export correlation data
- [ ] Unit tests

**Technical Details**:
- Method: Pearson correlation
- Rolling Window: 30, 90, 180 days
- Visualization: Seaborn heatmap

---

### Feature 7.2: Seasonality Detection & Visualization
**Epic**: Advanced Analytics & Insights  
**Estimated Effort**: 3 days  
**Priority**: P2 (Medium)  
**Dependencies**: Epic 1

**Description**: Detect and visualize seasonal patterns in energy prices.

**Acceptance Criteria**:
- [ ] Decompose time series (trend, seasonality, residual)
- [ ] Identify seasonal periods (monthly, quarterly, yearly)
- [ ] Seasonal strength metrics
- [ ] Seasonal plots (by month, day of week)
- [ ] Export seasonal analysis
- [ ] Unit tests

**Technical Details**:
- Method: STL decomposition or seasonal_decompose (statsmodels)
- Visualization: Seasonal plots, decomposition plots

---

### Feature 7.3: Volatility Forecasting (GARCH)
**Epic**: Advanced Analytics & Insights  
**Estimated Effort**: 4 days  
**Priority**: P2 (Medium)  
**Dependencies**: Epic 1

**Description**: Forecast price volatility using GARCH models.

**Acceptance Criteria**:
- [ ] Implement GARCH(1,1) model
- [ ] Train on historical returns
- [ ] Forecast volatility (1, 7, 30 days)
- [ ] Visualize volatility over time
- [ ] Compare to realized volatility
- [ ] Unit tests

**Technical Details**:
- Library: `arch` (Python ARCH/GARCH library)
- Model: GARCH(1,1)
- Input: Daily returns (log returns)

---

### Feature 7.4: Anomaly Detection System
**Epic**: Advanced Analytics & Insights  
**Estimated Effort**: 3 days  
**Priority**: P2 (Medium)  
**Dependencies**: Epic 1

**Description**: Detect anomalous price movements.

**Acceptance Criteria**:
- [ ] Statistical anomaly detection (Z-score, IQR)
- [ ] ML-based anomaly detection (Isolation Forest)
- [ ] Real-time anomaly detection
- [ ] Alert on anomalies
- [ ] Anomaly visualization
- [ ] Unit tests

**Technical Details**:
- Methods: Z-score (>3σ), Isolation Forest
- Threshold: Configurable
- Alerts: Log or notification

---

### Feature 7.5: Market Regime Detection
**Epic**: Advanced Analytics & Insights  
**Estimated Effort**: 3 days  
**Priority**: P2 (Medium)  
**Dependencies**: Epic 1

**Description**: Classify market conditions (trending, mean-reverting, high volatility).

**Acceptance Criteria**:
- [ ] Define regime states
- [ ] Hidden Markov Model or clustering
- [ ] Regime classification over time
- [ ] Regime transition probabilities
- [ ] Visualization of regimes
- [ ] Unit tests

**Technical Details**:
- Methods: Hidden Markov Model (HMM) or K-Means clustering
- States: Trending Up, Trending Down, Mean-Reverting, High Volatility
- Library: `hmmlearn` or `scikit-learn`

---

### Feature 7.6: Feature Importance Analysis (SHAP)
**Epic**: Advanced Analytics & Insights  
**Estimated Effort**: 3 days  
**Priority**: P2 (Medium)  
**Dependencies**: Epic 2

**Description**: Explain model predictions using feature importance.

**Acceptance Criteria**:
- [ ] Calculate SHAP values for LSTM model
- [ ] Feature importance ranking
- [ ] SHAP summary plot
- [ ] SHAP dependence plots
- [ ] Per-prediction explanation
- [ ] Unit tests

**Technical Details**:
- Library: `shap`
- Explainer: DeepExplainer (for LSTM)
- Visualization: Summary plot, dependence plot

---

### Feature 7.7: Automated Insight Generation
**Epic**: Advanced Analytics & Insights  
**Estimated Effort**: 3 days  
**Priority**: P2 (Medium)  
**Dependencies**: 7.1, 7.2, 7.3, 7.4, 7.5

**Description**: Generate natural language insights from analytics.

**Acceptance Criteria**:
- [ ] Template-based insight generation
- [ ] Insights for correlations ("WTI and Brent highly correlated at 0.95")
- [ ] Insights for seasonality ("Prices typically rise in Q4")
- [ ] Insights for volatility ("Volatility increased 20% this week")
- [ ] Insights for anomalies ("Price spike detected on 2025-12-14")
- [ ] Display insights in dashboard
- [ ] Unit tests

**Technical Details**:
- Approach: Rule-based templates
- Advanced: Use LLM (GPT) for natural language generation (optional)

---

## EPIC 8: Quality Assurance & Documentation ✅

### Feature 8.1: Unit Testing Framework Setup (pytest)
**Epic**: Quality Assurance & Documentation  
**Estimated Effort**: 1 day  
**Priority**: P0 (Critical)  
**Dependencies**: None

**Description**: Set up pytest framework for unit testing.

**Acceptance Criteria**:
- [ ] pytest installed and configured
- [ ] Test directory structure
- [ ] Fixtures for common test data
- [ ] Mocking framework configured
- [ ] Test runner scripts
- [ ] Integration with IDE

**Technical Details**:
- Framework: pytest
- Plugins: pytest-cov, pytest-mock, pytest-asyncio
- Structure: `/tests/unit/`, `/tests/integration/`, `/tests/e2e/`

---

### Feature 8.2: Unit Tests for All Modules
**Epic**: Quality Assurance & Documentation  
**Estimated Effort**: Ongoing (1 day per Epic)  
**Priority**: P0 (Critical)  
**Dependencies**: All feature implementations

**Description**: Write comprehensive unit tests for all modules.

**Acceptance Criteria**:
- [ ] Unit tests for data ingestion modules
- [ ] Unit tests for feature engineering
- [ ] Unit tests for models
- [ ] Unit tests for backtesting
- [ ] Unit tests for API endpoints
- [ ] Unit tests for utilities
- [ ] >80% code coverage

**Technical Details**:
- Follow AAA pattern (Arrange, Act, Assert)
- Use mocks for external dependencies
- Parametrize tests for multiple scenarios

---

### Feature 8.3: Integration Tests
**Epic**: Quality Assurance & Documentation  
**Estimated Effort**: 3 days  
**Priority**: P0 (Critical)  
**Dependencies**: Epic 1, Epic 2, Epic 4

**Description**: Test integration between components.

**Acceptance Criteria**:
- [ ] Database integration tests
- [ ] API endpoint integration tests
- [ ] Model training pipeline integration tests
- [ ] Data pipeline integration tests
- [ ] Test with real database (test DB)
- [ ] Cleanup after tests

**Technical Details**:
- Use test database
- Fixtures for setup/teardown
- Test realistic workflows

---

### Feature 8.4: End-to-End Tests
**Epic**: Quality Assurance & Documentation  
**Estimated Effort**: 3 days  
**Priority**: P1 (High)  
**Dependencies**: Epic 4, Epic 5

**Description**: Test complete user workflows end-to-end.

**Acceptance Criteria**:
- [ ] E2E test for forecasting workflow
- [ ] E2E test for backtesting workflow
- [ ] E2E test for dashboard interaction
- [ ] Automated browser testing (Selenium/Playwright)
- [ ] Screenshots on failure
- [ ] Run in CI/CD

**Technical Details**:
- Framework: Playwright or Selenium
- Browser: Chrome headless
- Scenarios: User requests forecast → API returns → Dashboard displays

---

### Feature 8.5: Performance Tests
**Epic**: Quality Assurance & Documentation  
**Estimated Effort**: 2 days  
**Priority**: P1 (High)  
**Dependencies**: Epic 4

**Description**: Test API performance and load handling.

**Acceptance Criteria**:
- [ ] Load testing (100 concurrent requests)
- [ ] Measure response times (p50, p95, p99)
- [ ] Identify bottlenecks
- [ ] Optimize if needed
- [ ] Document performance benchmarks

**Technical Details**:
- Tool: Locust or Apache JMeter
- Metrics: Requests/second, response time, error rate
- Target: <500ms p95 response time

---

### Feature 8.6: Code Coverage Reporting
**Epic**: Quality Assurance & Documentation  
**Estimated Effort**: 1 day  
**Priority**: P0 (Critical)  
**Dependencies**: 8.2

**Description**: Set up automated code coverage reporting.

**Acceptance Criteria**:
- [ ] pytest-cov configured
- [ ] Coverage report generation
- [ ] HTML coverage report
- [ ] Coverage badge for README
- [ ] Integrate with CI/CD
- [ ] Fail build if coverage <80%

**Technical Details**:
- Tool: pytest-cov
- Output: Terminal, HTML, XML (for CI)
- CI Integration: Upload to Codecov or Coveralls (optional)

---

### Feature 8.7: Project README
**Epic**: Quality Assurance & Documentation  
**Estimated Effort**: 2 days  
**Priority**: P0 (Critical)  
**Dependencies**: All Epics

**Description**: Comprehensive project README.

**Acceptance Criteria**:
- [ ] Project overview and goals
- [ ] Features list
- [ ] Technology stack
- [ ] Installation instructions
- [ ] Usage examples
- [ ] API documentation link
- [ ] Contributing guidelines
- [ ] License information
- [ ] Screenshots/GIFs

**Technical Details**:
- Format: Markdown
- Sections: Overview, Features, Installation, Usage, API, Testing, Contributing, License

---

### Feature 8.8: API Documentation (OpenAPI/Swagger)
**Epic**: Quality Assurance & Documentation  
**Estimated Effort**: Covered in Feature 4.8  
**Priority**: P1 (High)  
**Dependencies**: Epic 4

**Description**: See Feature 4.8 (already covered in Epic 4).

---

### Feature 8.9: Architecture Documentation
**Epic**: Quality Assurance & Documentation  
**Estimated Effort**: 2 days  
**Priority**: P0 (Critical)  
**Dependencies**: All Epics

**Description**: Document system architecture and design.

**Acceptance Criteria**:
- [ ] System architecture diagram
- [ ] Component interaction diagrams
- [ ] Data flow diagrams
- [ ] Database schema documentation
- [ ] Deployment architecture
- [ ] Technology choices rationale
- [ ] Scalability considerations

**Technical Details**:
- Format: Markdown + diagrams (draw.io, Mermaid, or PlantUML)
- Location: `docs/architecture/`

---

### Feature 8.10: Model Methodology Documentation
**Epic**: Quality Assurance & Documentation  
**Estimated Effort**: 2 days  
**Priority**: P0 (Critical)  
**Dependencies**: Epic 2, Epic 3

**Description**: Document model development and methodology.

**Acceptance Criteria**:
- [ ] Model selection rationale
- [ ] Feature engineering description
- [ ] Training process documentation
- [ ] Hyperparameter tuning results
- [ ] Evaluation methodology
- [ ] Performance benchmarks
- [ ] Limitations and assumptions
- [ ] Future improvements

**Technical Details**:
- Format: Markdown or Jupyter Notebook
- Location: `docs/models/`

---

### Feature 8.11: Deployment Guide
**Epic**: Quality Assurance & Documentation  
**Estimated Effort**: 1 day  
**Priority**: P1 (High)  
**Dependencies**: Epic 6

**Description**: Step-by-step deployment guide.

**Acceptance Criteria**:
- [ ] Local development setup
- [ ] Docker deployment instructions
- [ ] Cloud deployment guide (AWS/Azure)
- [ ] Environment variable configuration
- [ ] Database setup
- [ ] Troubleshooting section

**Technical Details**:
- Format: Markdown
- Location: `docs/deployment.md`

---

### Feature 8.12: User Guide
**Epic**: Quality Assurance & Documentation  
**Estimated Effort**: 2 days  
**Priority**: P1 (High)  
**Dependencies**: Epic 4, Epic 5

**Description**: End-user guide for using the system.

**Acceptance Criteria**:
- [ ] How to request forecasts
- [ ] How to interpret results
- [ ] How to use the dashboard
- [ ] How to run backtests
- [ ] API usage examples
- [ ] FAQ section
- [ ] Screenshots and examples

**Technical Details**:
- Format: Markdown
- Location: `docs/user-guide.md`

---

## Summary Statistics

### **Total Features**: 64
### **Total Estimated Effort**: ~150-180 days (6-7 months for one developer)

### **By Epic**:
- Epic 1: 6 features (18 days)
- Epic 2: 7 features (28 days)
- Epic 3: 7 features (23 days)
- Epic 4: 9 features (22 days)
- Epic 5: 8 features (22 days)
- Epic 6: 8 features (24 days)
- Epic 7: 7 features (21 days)
- Epic 8: 12 features (ongoing + 15 days)

### **By Priority**:
- P0 (Critical): 35 features
- P1 (High): 22 features
- P2 (Medium): 7 features

---

## Next Steps

✅ Feature breakdown complete  
⏭️ **NEXT**: Create Project Tracker (document 04)  
⏭️ **THEN**: Create User Stories for each feature  

---

**Status**: ✅ Ready for Tracker Creation

