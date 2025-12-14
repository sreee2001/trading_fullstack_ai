# Energy Price Forecasting System - User Stories

**Project**: Energy Price Forecasting System  
**Version**: 1.0  
**Date**: December 14, 2025  
**Status**: ✅ Ready for Review & Approval

---

## Overview

This document contains detailed user stories for all 64 features across 8 Epics. Each user story follows the standard format:

**Format**: As a [role], I want [feature], so that [benefit]

**Components**:
- **Story**: User story statement
- **Acceptance Criteria**: Testable conditions for completion
- **Technical Notes**: Implementation guidance
- **Estimated Effort**: Story points or hours
- **Dependencies**: Required prior stories/features

---

## Table of Contents

- [Epic 1: Data Foundation & Infrastructure](#epic-1-data-foundation--infrastructure)
- [Epic 2: Core ML Model Development](#epic-2-core-ml-model-development)
- [Epic 3: Model Evaluation & Backtesting](#epic-3-model-evaluation--backtesting)
- [Epic 4: API Service Layer](#epic-4-api-service-layer)
- [Epic 5: Visualization & User Interface](#epic-5-visualization--user-interface)
- [Epic 6: MLOps & Deployment Pipeline](#epic-6-mlops--deployment-pipeline)
- [Epic 7: Advanced Analytics & Insights](#epic-7-advanced-analytics--insights)
- [Epic 8: Quality Assurance & Documentation](#epic-8-quality-assurance--documentation)

---

# EPIC 1: Data Foundation & Infrastructure 🏗️

## Feature 1.1: EIA API Integration

### Story 1.1.1: Create EIA API Client Class
**As a** data engineer  
**I want** a reusable EIA API client class  
**So that** I can fetch energy price data consistently and reliably

**Acceptance Criteria**:
- [ ] Class `EIAAPIClient` created with proper initialization
- [ ] API key loaded from environment variable
- [ ] Base URL configured
- [ ] Constructor validates API key presence
- [ ] Unit tests cover initialization

**Technical Notes**:
- File: `src/energy-price-forecasting/data-ingestion/eia_client.py`
- Use `requests` library
- Environment variable: `EIA_API_KEY`

**Effort**: 4 hours  
**Dependencies**: None

---

### Story 1.1.2: Implement EIA WTI Crude Oil Data Fetching
**As a** data engineer  
**I want** to fetch WTI crude oil spot prices from EIA  
**So that** I can use historical data for model training

**Acceptance Criteria**:
- [ ] Method `fetch_wti_prices(start_date, end_date)` implemented
- [ ] Returns DataFrame with columns: [date, price]
- [ ] Handles date range validation
- [ ] Handles empty responses gracefully
- [ ] Unit tests with mocked API responses

**Technical Notes**:
- Series ID: `PET.RWTC.D` (WTI Daily Spot Price)
- API Endpoint: `/v2/petroleum/pri/spt/data/`
- Date format: YYYY-MM-DD

**Effort**: 6 hours  
**Dependencies**: Story 1.1.1

---

### Story 1.1.3: Implement EIA Natural Gas Data Fetching
**As a** data engineer  
**I want** to fetch Henry Hub natural gas prices from EIA  
**So that** I can support multiple commodity forecasting

**Acceptance Criteria**:
- [ ] Method `fetch_natural_gas_prices(start_date, end_date)` implemented
- [ ] Returns DataFrame with columns: [date, price]
- [ ] Handles API errors appropriately
- [ ] Unit tests with mocked responses

**Technical Notes**:
- Series ID: `NG.RNGWHHD.D` (Henry Hub Natural Gas Spot Price)

**Effort**: 4 hours  
**Dependencies**: Story 1.1.1

---

### Story 1.1.4: Implement Rate Limiting and Retry Logic
**As a** data engineer  
**I want** automatic rate limiting and retry on failures  
**So that** the API client respects limits and handles transient errors

**Acceptance Criteria**:
- [ ] Rate limiter implemented (5000 requests/day)
- [ ] Exponential backoff retry logic (3 attempts)
- [ ] Handles 429 (rate limit) responses
- [ ] Handles 500 (server error) responses
- [ ] Logs retry attempts
- [ ] Unit tests for rate limiting and retries

**Technical Notes**:
- Use `tenacity` library for retries
- Implement token bucket or simple counter for rate limiting

**Effort**: 6 hours  
**Dependencies**: Story 1.1.1

---

### Story 1.1.5: Normalize and Validate EIA API Responses
**As a** data engineer  
**I want** API responses normalized to a standard format  
**So that** downstream modules have consistent data

**Acceptance Criteria**:
- [ ] Method `_normalize_response(raw_data)` implemented
- [ ] Converts to standard DataFrame format
- [ ] Handles missing fields gracefully
- [ ] Validates data types
- [ ] Handles timezone conversions (to UTC)
- [ ] Unit tests for normalization

**Technical Notes**:
- Standard format: DataFrame with [timestamp, value, metadata]
- Handle null/missing values

**Effort**: 4 hours  
**Dependencies**: Story 1.1.2, 1.1.3

---

## Feature 1.2: FRED API Integration

### Story 1.2.1: Create FRED API Client Class
**As a** data engineer  
**I want** a reusable FRED API client  
**So that** I can fetch economic indicators and commodity prices

**Acceptance Criteria**:
- [ ] Class `FREDAPIClient` created
- [ ] API key loaded from environment variable
- [ ] Constructor validates API key
- [ ] Unit tests cover initialization

**Technical Notes**:
- File: `src/energy-price-forecasting/data-ingestion/fred_client.py`
- Environment variable: `FRED_API_KEY`
- API URL: `https://api.stlouisfed.org/fred`

**Effort**: 3 hours  
**Dependencies**: None

---

### Story 1.2.2: Implement FRED WTI/Brent Crude Oil Data Fetching
**As a** data engineer  
**I want** to fetch WTI and Brent crude prices from FRED  
**So that** I have cross-validated data from multiple sources

**Acceptance Criteria**:
- [ ] Method `fetch_series(series_id, start_date, end_date)` implemented
- [ ] Fetch DCOILWTICO (WTI) series
- [ ] Fetch DCOILBRENTEU (Brent) series
- [ ] Returns DataFrame with [date, value]
- [ ] Handles API errors
- [ ] Unit tests with mocked responses

**Technical Notes**:
- Endpoint: `/fred/series/observations`
- Series IDs: `DCOILWTICO`, `DCOILBRENTEU`

**Effort**: 5 hours  
**Dependencies**: Story 1.2.1

---

### Story 1.2.3: Implement FRED Caching to Respect Rate Limits
**As a** data engineer  
**I want** responses cached locally  
**So that** I don't exceed FRED's rate limits (120/minute)

**Acceptance Criteria**:
- [ ] In-memory cache implemented (TTL: 5 minutes)
- [ ] Cache key based on series_id and date range
- [ ] Rate limiter (120 requests/minute)
- [ ] Logs cache hits/misses
- [ ] Unit tests for caching behavior

**Technical Notes**:
- Use `cachetools` or simple dict with timestamps
- Rate limit: 120 requests/60 seconds

**Effort**: 4 hours  
**Dependencies**: Story 1.2.1

---

## Feature 1.3: Yahoo Finance Data Ingestion

### Story 1.3.1: Setup Yahoo Finance Client
**As a** data engineer  
**I want** to use the yfinance library  
**So that** I can fetch historical commodity futures data

**Acceptance Criteria**:
- [ ] `yfinance` library added to requirements.txt
- [ ] Wrapper class `YahooFinanceClient` created
- [ ] Constructor initializes ticker symbols
- [ ] Unit tests cover initialization

**Technical Notes**:
- File: `src/energy-price-forecasting/data-ingestion/yahoo_finance_client.py`
- Library: `yfinance`
- Tickers: CL=F (WTI), BZ=F (Brent), NG=F (Natural Gas)

**Effort**: 2 hours  
**Dependencies**: None

---

### Story 1.3.2: Fetch Historical OHLCV Data for Crude Oil Futures
**As a** data engineer  
**I want** to fetch OHLCV data for WTI and Brent crude futures  
**So that** I have detailed intraday price information

**Acceptance Criteria**:
- [ ] Method `fetch_ohlcv(ticker, start_date, end_date)` implemented
- [ ] Returns DataFrame with [date, open, high, low, close, volume]
- [ ] Handles missing data (weekends, holidays)
- [ ] Supports CL=F and BZ=F tickers
- [ ] Unit tests with mocked yfinance responses

**Technical Notes**:
- Use `yfinance.Ticker(ticker).history(start, end)`
- Handle gaps in data appropriately

**Effort**: 5 hours  
**Dependencies**: Story 1.3.1

---

### Story 1.3.3: Fetch Historical Data for Natural Gas Futures
**As a** data engineer  
**I want** to fetch natural gas futures data  
**So that** the system supports multiple commodities

**Acceptance Criteria**:
- [ ] Fetch NG=F ticker data
- [ ] Same OHLCV format as crude oil
- [ ] Handle data gaps
- [ ] Unit tests

**Technical Notes**:
- Ticker: NG=F (Natural Gas Futures)

**Effort**: 3 hours  
**Dependencies**: Story 1.3.1

---

### Story 1.3.4: Normalize Yahoo Finance Data to Standard Format
**As a** data engineer  
**I want** Yahoo Finance data normalized  
**So that** it matches other data sources' format

**Acceptance Criteria**:
- [ ] Method `normalize_ohlcv(raw_df)` implemented
- [ ] Converts to standard timestamp format (UTC)
- [ ] Renames columns to standard names
- [ ] Handles timezone conversions
- [ ] Unit tests

**Technical Notes**:
- Standard columns: timestamp, open, high, low, close, volume
- Convert timezone to UTC

**Effort**: 3 hours  
**Dependencies**: Story 1.3.2, 1.3.3

---

## Feature 1.4: Database Setup (PostgreSQL + TimescaleDB)

### Story 1.4.1: Install and Configure PostgreSQL with TimescaleDB
**As a** DevOps engineer  
**I want** PostgreSQL with TimescaleDB extension installed  
**So that** I have optimized time-series data storage

**Acceptance Criteria**:
- [ ] PostgreSQL 15+ installed (local or Docker)
- [ ] TimescaleDB extension installed
- [ ] Database `energy_forecasting` created
- [ ] User and permissions configured
- [ ] Connection tested successfully
- [ ] Documentation in deployment guide

**Technical Notes**:
- Docker option: Use `timescale/timescaledb:latest-pg15` image
- Create database, user, grant permissions

**Effort**: 4 hours  
**Dependencies**: None

---

### Story 1.4.2: Design and Create Database Schema
**As a** database engineer  
**I want** a well-designed schema for time-series price data  
**So that** data is organized and query-efficient

**Acceptance Criteria**:
- [ ] Tables created: `commodities`, `data_sources`, `price_data`
- [ ] Proper primary keys and foreign keys
- [ ] Indexes on timestamp and commodity_id
- [ ] Schema migration script created
- [ ] Schema documented

**Technical Notes**:
```sql
CREATE TABLE commodities (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(10) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL
);

CREATE TABLE data_sources (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE price_data (
  timestamp TIMESTAMPTZ NOT NULL,
  commodity_id INTEGER NOT NULL REFERENCES commodities(id),
  source_id INTEGER NOT NULL REFERENCES data_sources(id),
  price DECIMAL(12,4) NOT NULL,
  volume BIGINT,
  open_price DECIMAL(12,4),
  high_price DECIMAL(12,4),
  low_price DECIMAL(12,4),
  close_price DECIMAL(12,4),
  PRIMARY KEY (timestamp, commodity_id, source_id)
);
```

**Effort**: 4 hours  
**Dependencies**: Story 1.4.1

---

### Story 1.4.3: Convert price_data to TimescaleDB Hypertable
**As a** database engineer  
**I want** price_data as a TimescaleDB hypertable  
**So that** time-series queries are optimized

**Acceptance Criteria**:
- [ ] Hypertable created on `price_data`
- [ ] Partitioned by timestamp (1 day chunks recommended)
- [ ] Compression policy configured (optional)
- [ ] Retention policy configured (optional)
- [ ] Migration script updated

**Technical Notes**:
```sql
SELECT create_hypertable('price_data', 'timestamp');
```

**Effort**: 2 hours  
**Dependencies**: Story 1.4.2

---

### Story 1.4.4: Create Database Utility Module
**As a** developer  
**I want** reusable database utilities  
**So that** I can connect and query the database easily

**Acceptance Criteria**:
- [ ] Module `database_utils.py` created
- [ ] Function `get_connection()` returns DB connection
- [ ] Function `execute_query(query, params)` executes queries
- [ ] Connection pooling configured
- [ ] Environment variables for DB credentials
- [ ] Unit tests with test database

**Technical Notes**:
- Library: `psycopg2` or `asyncpg`
- Connection pooling: `psycopg2.pool` or `SQLAlchemy`
- Env vars: `DATABASE_URL` or separate `DB_HOST`, `DB_PORT`, etc.

**Effort**: 5 hours  
**Dependencies**: Story 1.4.1

---

### Story 1.4.5: Implement Data Insertion Functions
**As a** developer  
**I want** functions to insert price data  
**So that** ingested data can be stored in the database

**Acceptance Criteria**:
- [ ] Function `insert_price_data(df, commodity_id, source_id)` implemented
- [ ] Batch insertion for performance
- [ ] Duplicate handling (upsert or ignore)
- [ ] Transaction support
- [ ] Error handling and logging
- [ ] Unit tests

**Technical Notes**:
- Use `COPY` or bulk insert for performance
- Handle conflicts with `ON CONFLICT DO NOTHING`

**Effort**: 5 hours  
**Dependencies**: Story 1.4.4

---

## Feature 1.5: Data Validation & Quality Framework

### Story 1.5.1: Define Data Validation Rules
**As a** data engineer  
**I want** clear validation rules defined  
**So that** data quality is ensured

**Acceptance Criteria**:
- [ ] Validation rules documented
- [ ] Rules for price (>0, within reasonable range)
- [ ] Rules for volume (>=0)
- [ ] Rules for timestamps (valid, sequential)
- [ ] Rules for completeness (no gaps >2 days)
- [ ] Cross-source tolerance (±5%)

**Technical Notes**:
- Document in `docs/data-validation-rules.md`
- Rules should be configurable

**Effort**: 2 hours  
**Dependencies**: None

---

### Story 1.5.2: Implement Schema Validation
**As a** data engineer  
**I want** automatic schema validation  
**So that** data conforms to expected types and formats

**Acceptance Criteria**:
- [ ] Function `validate_schema(df, expected_schema)` implemented
- [ ] Checks column names
- [ ] Checks data types
- [ ] Checks for required columns
- [ ] Returns validation report
- [ ] Unit tests

**Technical Notes**:
- Use `pandas` dtype checking
- Consider `pandera` library for schema validation

**Effort**: 4 hours  
**Dependencies**: Story 1.5.1

---

### Story 1.5.3: Implement Range and Outlier Detection
**As a** data engineer  
**I want** automatic outlier detection  
**So that** anomalous data is flagged

**Acceptance Criteria**:
- [ ] Function `detect_outliers(df, column, method)` implemented
- [ ] Z-score method (threshold=3)
- [ ] IQR method
- [ ] Flags outliers (doesn't remove)
- [ ] Returns DataFrame with outlier flag column
- [ ] Unit tests

**Technical Notes**:
- Methods: Z-score, IQR (Interquartile Range)
- Flagging vs. removal: Flag only, let human decide

**Effort**: 5 hours  
**Dependencies**: Story 1.5.1

---

### Story 1.5.4: Implement Completeness Checks
**As a** data engineer  
**I want** automatic detection of data gaps  
**So that** missing data is identified

**Acceptance Criteria**:
- [ ] Function `check_completeness(df, expected_frequency)` implemented
- [ ] Detects gaps in time series (>2 days)
- [ ] Detects missing values
- [ ] Returns completeness report
- [ ] Unit tests

**Technical Notes**:
- Expected frequency: Daily for energy prices
- Account for weekends/holidays (optional)

**Effort**: 4 hours  
**Dependencies**: Story 1.5.1

---

### Story 1.5.5: Implement Cross-Source Consistency Validation
**As a** data engineer  
**I want** validation across data sources  
**So that** discrepancies are identified

**Acceptance Criteria**:
- [ ] Function `validate_cross_source(df1, df2, tolerance)` implemented
- [ ] Compares prices for same commodity/date
- [ ] Flags discrepancies >5%
- [ ] Returns consistency report
- [ ] Unit tests

**Technical Notes**:
- Tolerance: Configurable, default 5%
- Handle missing data in one source

**Effort**: 5 hours  
**Dependencies**: Story 1.5.1

---

### Story 1.5.6: Create Data Quality Report Generator
**As a** data engineer  
**I want** automated quality reports  
**So that** I can monitor data health

**Acceptance Criteria**:
- [ ] Function `generate_quality_report(df, validation_results)` implemented
- [ ] Report includes: completeness, outliers, consistency
- [ ] Report format: JSON and human-readable text
- [ ] Save report to file
- [ ] Unit tests

**Technical Notes**:
- Output: JSON for programmatic access, TXT for humans
- Save to `logs/data-quality-YYYYMMDD.json`

**Effort**: 4 hours  
**Dependencies**: Stories 1.5.2-1.5.5

---

## Feature 1.6: Automated Data Pipeline Orchestration

### Story 1.6.1: Design Data Pipeline Workflow
**As a** data engineer  
**I want** a clear pipeline workflow designed  
**So that** automation is well-structured

**Acceptance Criteria**:
- [ ] Workflow documented (fetch → validate → store)
- [ ] Error handling strategy defined
- [ ] Retry logic defined
- [ ] Notification strategy defined
- [ ] Document in architecture docs

**Technical Notes**:
- Workflow: Fetch from APIs → Validate → Store in DB → Report
- Error handling: Retry transient errors, alert on persistent failures

**Effort**: 3 hours  
**Dependencies**: Features 1.1-1.5

---

### Story 1.6.2: Implement Pipeline Orchestrator Class
**As a** data engineer  
**I want** a pipeline orchestrator  
**So that** I can run the entire pipeline programmatically

**Acceptance Criteria**:
- [ ] Class `DataPipelineOrchestrator` created
- [ ] Method `run_pipeline(commodities, sources, date_range)` implemented
- [ ] Calls API clients to fetch data
- [ ] Validates data
- [ ] Stores in database
- [ ] Generates quality report
- [ ] Comprehensive logging
- [ ] Unit and integration tests

**Technical Notes**:
- File: `src/energy-price-forecasting/data-ingestion/pipeline_orchestrator.py`
- Use dependency injection for API clients

**Effort**: 8 hours  
**Dependencies**: Features 1.1-1.5

---

### Story 1.6.3: Implement Scheduled Job (Daily Refresh)
**As a** data engineer  
**I want** the pipeline to run automatically daily  
**So that** data stays up-to-date

**Acceptance Criteria**:
- [ ] Scheduler configured (APScheduler or cron)
- [ ] Daily job at 6:00 AM EST
- [ ] Job calls `run_pipeline()` with default parameters
- [ ] Logs job execution
- [ ] Handles job failures gracefully
- [ ] Documentation for setup

**Technical Notes**:
- Option 1: Python APScheduler (in-process)
- Option 2: Cron job (external scheduler)
- Option 3: Airflow DAG (if using Airflow)

**Effort**: 4 hours  
**Dependencies**: Story 1.6.2

---

### Story 1.6.4: Implement Pipeline Error Handling and Notifications
**As a** data engineer  
**I want** notifications on pipeline failures  
**So that** I can respond to issues quickly

**Acceptance Criteria**:
- [ ] Try-catch blocks around critical operations
- [ ] Log errors with full stack traces
- [ ] Send notification on failure (email or log)
- [ ] Partial success handling (some sources fail)
- [ ] Retry logic for transient errors
- [ ] Unit tests for error scenarios

**Technical Notes**:
- Notification: Log to file initially, optionally email/Slack
- Use Python's `logging` module

**Effort**: 4 hours  
**Dependencies**: Story 1.6.2

---

### Story 1.6.5: Create Pipeline Monitoring Dashboard (CLI)
**As a** data engineer  
**I want** to view pipeline status via CLI  
**So that** I can monitor pipeline health

**Acceptance Criteria**:
- [ ] CLI command `python -m pipeline status` implemented
- [ ] Shows last run time, success/failure
- [ ] Shows data freshness
- [ ] Shows quality metrics
- [ ] Color-coded output (green/yellow/red)
- [ ] Unit tests

**Technical Notes**:
- Use `click` or `argparse` for CLI
- Read from logs or database metadata

**Effort**: 5 hours  
**Dependencies**: Story 1.6.2

---

# EPIC 2: Core ML Model Development 🤖

## Feature 2.1: Feature Engineering Pipeline

### Story 2.1.1: Implement Technical Indicators (Moving Averages)
**As a** ML engineer  
**I want** moving average features calculated  
**So that** models can use trend information

**Acceptance Criteria**:
- [ ] Function `calculate_moving_averages(df, windows)` implemented
- [ ] Simple Moving Average (SMA) for 5, 10, 20, 50, 200 days
- [ ] Exponential Moving Average (EMA) for same windows
- [ ] Returns DataFrame with MA columns
- [ ] Handles edge cases (insufficient data)
- [ ] Unit tests

**Technical Notes**:
- Use `pandas.rolling()` for SMA
- Use `pandas.ewm()` for EMA

**Effort**: 4 hours  
**Dependencies**: Epic 1 complete

---

### Story 2.1.2: Implement Technical Indicators (RSI, MACD, Bollinger Bands)
**As a** ML engineer  
**I want** additional technical indicators  
**So that** models have rich feature sets

**Acceptance Criteria**:
- [ ] RSI (Relative Strength Index) calculated
- [ ] MACD (Moving Average Convergence Divergence) calculated
- [ ] Bollinger Bands calculated (upper, middle, lower)
- [ ] ATR (Average True Range) calculated
- [ ] Returns DataFrame with indicator columns
- [ ] Unit tests

**Technical Notes**:
- Consider using `ta-lib` library or implement manually
- RSI period: 14 days
- MACD: 12, 26, 9 periods
- Bollinger: 20-day MA, 2 std

**Effort**: 6 hours  
**Dependencies**: Story 2.1.1

---

### Story 2.1.3: Implement Lag Features
**As a** ML engineer  
**I want** lag features (past prices)  
**So that** models can use historical patterns

**Acceptance Criteria**:
- [ ] Function `create_lag_features(df, lags)` implemented
- [ ] Lags: 1, 7, 30 days
- [ ] Returns DataFrame with lag columns (e.g., price_lag_1)
- [ ] Handles NaN values appropriately
- [ ] Unit tests

**Technical Notes**:
- Use `pandas.shift()`
- Lag columns: price_lag_1, price_lag_7, price_lag_30

**Effort**: 3 hours  
**Dependencies**: Epic 1 complete

---

### Story 2.1.4: Implement Rolling Statistics
**As a** ML engineer  
**I want** rolling statistics features  
**So that** models capture recent volatility and trends

**Acceptance Criteria**:
- [ ] Function `calculate_rolling_stats(df, windows)` implemented
- [ ] Rolling mean, std, min, max for 7, 30 days
- [ ] Returns DataFrame with rolling stat columns
- [ ] Unit tests

**Technical Notes**:
- Use `pandas.rolling()`

**Effort**: 3 hours  
**Dependencies**: Epic 1 complete

---

### Story 2.1.5: Implement Seasonality and Calendar Features
**As a** ML engineer  
**I want** seasonality features  
**So that** models capture periodic patterns

**Acceptance Criteria**:
- [ ] Day of week (Monday=0, Sunday=6)
- [ ] Month (1-12)
- [ ] Quarter (1-4)
- [ ] Year
- [ ] Is holiday (US holidays)
- [ ] Returns DataFrame with calendar columns
- [ ] Unit tests

**Technical Notes**:
- Use `pandas.dt` accessors
- Use `holidays` library for holiday detection

**Effort**: 4 hours  
**Dependencies**: Epic 1 complete

---

### Story 2.1.6: Implement Feature Scaling and Normalization
**As a** ML engineer  
**I want** features scaled appropriately  
**So that** models train effectively

**Acceptance Criteria**:
- [ ] Function `scale_features(df, method, fitted_scaler)` implemented
- [ ] StandardScaler (mean=0, std=1)
- [ ] MinMaxScaler (0-1 range)
- [ ] Scaler fitted on training data only
- [ ] Save/load scaler for production
- [ ] Returns scaled DataFrame and scaler
- [ ] Unit tests

**Technical Notes**:
- Use `sklearn.preprocessing.StandardScaler` or `MinMaxScaler`
- Important: Fit on training data, transform train/val/test

**Effort**: 4 hours  
**Dependencies**: Stories 2.1.1-2.1.5

---

### Story 2.1.7: Create Feature Engineering Pipeline Class
**As a** ML engineer  
**I want** a complete feature engineering pipeline  
**So that** I can transform raw data to model-ready features

**Acceptance Criteria**:
- [ ] Class `FeatureEngineeringPipeline` created
- [ ] Method `fit_transform(df)` for training data
- [ ] Method `transform(df)` for test/production data
- [ ] Chains all feature engineering steps
- [ ] Saves fitted scalers/transformers
- [ ] Returns feature matrix (X) and target (y)
- [ ] Unit and integration tests

**Technical Notes**:
- Use sklearn `Pipeline` or custom implementation
- Save pipeline to disk for production use

**Effort**: 6 hours  
**Dependencies**: Stories 2.1.1-2.1.6

---

## Feature 2.2: Baseline Statistical Models (ARIMA/SARIMA)

### Story 2.2.1: Implement ARIMA Model Class
**As a** ML engineer  
**I want** an ARIMA model implementation  
**So that** I have a statistical baseline

**Acceptance Criteria**:
- [ ] Class `ARIMAModel` created
- [ ] Method `fit(train_data, order)` trains model
- [ ] Method `predict(steps)` generates forecast
- [ ] Model persistence (save/load)
- [ ] Unit tests

**Technical Notes**:
- Library: `statsmodels.tsa.arima.model.ARIMA`
- Order: (p, d, q) - to be determined via ACF/PACF or auto-ARIMA

**Effort**: 5 hours  
**Dependencies**: Feature 2.1 complete

---

### Story 2.2.2: Implement SARIMA Model Class
**As a** ML engineer  
**I want** a SARIMA model implementation  
**So that** I can capture seasonality

**Acceptance Criteria**:
- [ ] Class `SARIMAModel` created (extends ARIMAModel)
- [ ] Method `fit(train_data, order, seasonal_order)` trains model
- [ ] Method `predict(steps)` generates forecast
- [ ] Model persistence
- [ ] Unit tests

**Technical Notes**:
- Library: `statsmodels.tsa.statespace.sarimax.SARIMAX`
- Seasonal order: (P, D, Q, m) - test with m=12 (monthly) or m=52 (weekly)

**Effort**: 4 hours  
**Dependencies**: Story 2.2.1

---

### Story 2.2.3: Implement Auto-ARIMA for Parameter Selection
**As a** ML engineer  
**I want** automatic parameter selection  
**So that** I don't manually tune ARIMA orders

**Acceptance Criteria**:
- [ ] Function `auto_arima_fit(train_data)` implemented
- [ ] Uses AIC/BIC for model selection
- [ ] Returns best model and parameters
- [ ] Reasonable search space to avoid long runtimes
- [ ] Unit tests

**Technical Notes**:
- Library: `pmdarima.auto_arima`
- Search space: p, q in [0, 5], d in [0, 2]

**Effort**: 3 hours  
**Dependencies**: Story 2.2.1

---

### Story 2.2.4: Train ARIMA/SARIMA on Historical Data
**As a** ML engineer  
**I want** models trained on historical energy price data  
**So that** I can generate baseline forecasts

**Acceptance Criteria**:
- [ ] Training script `train_arima.py` created
- [ ] Loads data from database
- [ ] Trains ARIMA and SARIMA models
- [ ] Saves trained models to disk
- [ ] Logs training parameters and metrics
- [ ] Integration test

**Technical Notes**:
- Use data from Epic 1
- Train on 80% of data, validate on 20%

**Effort**: 4 hours  
**Dependencies**: Stories 2.2.1-2.2.3

---

### Story 2.2.5: Generate Forecasts with ARIMA/SARIMA
**As a** ML engineer  
**I want** to generate forecasts for 1, 7, 30 days  
**So that** I have baseline predictions

**Acceptance Criteria**:
- [ ] Method `forecast(model, steps)` implemented
- [ ] Generates forecasts for 1, 7, 30 days
- [ ] Returns DataFrame with [date, predicted_price]
- [ ] Includes confidence intervals
- [ ] Unit tests

**Technical Notes**:
- ARIMA returns forecast with confidence intervals by default

**Effort**: 3 hours  
**Dependencies**: Story 2.2.4

---

## Feature 2.3: LSTM Neural Network Model

### Story 2.3.1: Design LSTM Model Architecture
**As a** ML engineer  
**I want** an LSTM architecture designed  
**So that** I can implement it effectively

**Acceptance Criteria**:
- [ ] Architecture documented (layers, units, dropout)
- [ ] Input shape defined (sequence_length, features)
- [ ] Output shape defined (forecast_horizon)
- [ ] Hyperparameters documented
- [ ] Architecture diagram created

**Technical Notes**:
- Suggested architecture:
  - LSTM Layer 1: 128 units, return_sequences=True
  - Dropout: 0.2
  - LSTM Layer 2: 64 units
  - Dropout: 0.2
  - Dense Layer: forecast_horizon units
- Input: (batch, 60 timesteps, n_features)
- Output: (batch, forecast_horizon)

**Effort**: 3 hours  
**Dependencies**: Feature 2.1 complete

---

### Story 2.3.2: Implement LSTM Model Class (PyTorch or TensorFlow)
**As a** ML engineer  
**I want** an LSTM model implementation  
**So that** I can train and predict

**Acceptance Criteria**:
- [ ] Class `LSTMModel` created
- [ ] Constructor defines architecture
- [ ] Forward pass implemented
- [ ] Compatible with training loop
- [ ] Unit tests

**Technical Notes**:
- Framework: PyTorch or TensorFlow (your choice)
- File: `src/energy-price-forecasting/models/lstm_model.py`
- PyTorch example:
```python
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, output_size)
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        output = self.fc(lstm_out[:, -1, :])
        return output
```

**Effort**: 6 hours  
**Dependencies**: Story 2.3.1

---

### Story 2.3.3: Implement Sliding Window Dataset Creation
**As a** ML engineer  
**I want** training data in sliding window format  
**So that** LSTM can learn sequential patterns

**Acceptance Criteria**:
- [ ] Function `create_sequences(data, seq_length, forecast_horizon)` implemented
- [ ] Returns (X, y) where X is (samples, seq_length, features), y is (samples, forecast_horizon)
- [ ] Handles edge cases (insufficient data)
- [ ] Unit tests

**Technical Notes**:
- Sequence length: 60 days (configurable)
- Forecast horizon: 1, 7, or 30 days
- Example: X[0] = data[0:60], y[0] = data[61]

**Effort**: 5 hours  
**Dependencies**: Feature 2.1 complete

---

### Story 2.3.4: Implement LSTM Training Loop
**As a** ML engineer  
**I want** a training loop for LSTM  
**So that** I can train the model

**Acceptance Criteria**:
- [ ] Function `train_lstm(model, train_loader, val_loader, epochs)` implemented
- [ ] Training loop with batches
- [ ] Validation after each epoch
- [ ] Early stopping (patience=10)
- [ ] Learning rate scheduling (optional)
- [ ] Loss and metrics logged per epoch
- [ ] Unit tests

**Technical Notes**:
- Loss: MSE or MAE
- Optimizer: Adam (lr=0.001)
- Early stopping: Stop if val loss doesn't improve for 10 epochs

**Effort**: 8 hours  
**Dependencies**: Stories 2.3.2, 2.3.3

---

### Story 2.3.5: Implement Model Checkpointing
**As a** ML engineer  
**I want** models saved during training  
**So that** I can recover best models

**Acceptance Criteria**:
- [ ] Save model checkpoint after each epoch
- [ ] Save only if validation loss improves
- [ ] Checkpoint includes model weights, optimizer state, epoch
- [ ] Function `save_checkpoint(model, optimizer, epoch, path)` implemented
- [ ] Function `load_checkpoint(path)` implemented
- [ ] Unit tests

**Technical Notes**:
- PyTorch: `torch.save()`
- TensorFlow: `model.save()`

**Effort**: 3 hours  
**Dependencies**: Story 2.3.4

---

### Story 2.3.6: Implement LSTM Prediction Function
**As a** ML engineer  
**I want** to generate predictions with trained LSTM  
**So that** I can forecast future prices

**Acceptance Criteria**:
- [ ] Function `predict_lstm(model, input_sequence, steps)` implemented
- [ ] Supports multi-step ahead forecasting
- [ ] Returns DataFrame with [date, predicted_price]
- [ ] Handles denormalization (inverse scaling)
- [ ] Unit tests

**Technical Notes**:
- For multi-step: Use recursive or direct multi-output approach
- Denormalize predictions using saved scaler

**Effort**: 5 hours  
**Dependencies**: Stories 2.3.2, 2.3.5

---

### Story 2.3.7: Enable GPU Support for Training
**As a** ML engineer  
**I want** GPU acceleration enabled  
**So that** training is faster

**Acceptance Criteria**:
- [ ] Automatic GPU detection
- [ ] Move model and data to GPU if available
- [ ] Fallback to CPU if GPU not available
- [ ] Log device being used
- [ ] Unit tests (mock GPU)

**Technical Notes**:
- PyTorch: `device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')`
- TensorFlow: Automatically uses GPU if available

**Effort**: 2 hours  
**Dependencies**: Story 2.3.2

---

## Feature 2.4: Model Training Infrastructure

### Story 2.4.1: Implement Train/Validation/Test Split Strategy
**As a** ML engineer  
**I want** proper data splitting  
**So that** models are evaluated fairly

**Acceptance Criteria**:
- [ ] Function `split_data(df, train_ratio, val_ratio, test_ratio)` implemented
- [ ] Time-series aware splitting (no shuffling)
- [ ] Returns train, val, test DataFrames
- [ ] Validates split ratios sum to 1.0
- [ ] Unit tests

**Technical Notes**:
- Typical split: 70% train, 15% val, 15% test
- No shuffling for time series!

**Effort**: 3 hours  
**Dependencies**: Epic 1 complete

---

### Story 2.4.2: Implement Time-Series Cross-Validation
**As a** ML engineer  
**I want** time-series cross-validation  
**So that** model performance is robust

**Acceptance Criteria**:
- [ ] Function `time_series_cv_split(df, n_splits)` implemented
- [ ] Uses expanding window approach
- [ ] Returns list of (train_idx, val_idx) tuples
- [ ] Unit tests

**Technical Notes**:
- Use `sklearn.model_selection.TimeSeriesSplit` or custom implementation
- Typical: 5 splits

**Effort**: 4 hours  
**Dependencies**: Story 2.4.1

---

### Story 2.4.3: Implement Training Progress Logging
**As a** ML engineer  
**I want** detailed training logs  
**So that** I can monitor training progress

**Acceptance Criteria**:
- [ ] Logger configured
- [ ] Log training loss per epoch
- [ ] Log validation loss per epoch
- [ ] Log training time per epoch
- [ ] Logs saved to file
- [ ] Unit tests

**Technical Notes**:
- Use Python `logging` module
- Log file: `logs/training-YYYYMMDD-HHMMSS.log`

**Effort**: 3 hours  
**Dependencies**: None

---

### Story 2.4.4: Implement Memory Optimization for Large Datasets
**As a** ML engineer  
**I want** efficient memory usage  
**So that** training doesn't run out of memory

**Acceptance Criteria**:
- [ ] Use data generators/DataLoader instead of loading all in memory
- [ ] Batch processing
- [ ] Memory profiling (optional)
- [ ] Documentation on memory considerations
- [ ] Unit tests

**Technical Notes**:
- PyTorch: Use `DataLoader` with `num_workers`
- TensorFlow: Use `tf.data.Dataset`

**Effort**: 4 hours  
**Dependencies**: Feature 2.3 complete

---

### Story 2.4.5: Create Model Training Script (CLI)
**As a** ML engineer  
**I want** a CLI script to train models  
**So that** training is easy to execute

**Acceptance Criteria**:
- [ ] Script `train_model.py` created
- [ ] CLI arguments: model_type, commodity, config_path
- [ ] Calls appropriate training function
- [ ] Saves trained model
- [ ] Logs to console and file
- [ ] Integration test

**Technical Notes**:
- Example: `python train_model.py --model lstm --commodity WTI --config config/lstm_config.yaml`
- Use `argparse` or `click`

**Effort**: 5 hours  
**Dependencies**: Features 2.2, 2.3

---

## Feature 2.5: Hyperparameter Tuning Framework

### Story 2.5.1: Define Hyperparameter Search Space
**As a** ML engineer  
**I want** search space defined  
**So that** tuning is structured

**Acceptance Criteria**:
- [ ] Search space documented for LSTM:
  - LSTM layers: [2, 3]
  - LSTM units: [50, 64, 128]
  - Dropout: [0.2, 0.3, 0.4]
  - Learning rate: [0.001, 0.005, 0.01]
  - Sequence length: [30, 60, 90]
- [ ] Search space in config file

**Technical Notes**:
- Config file: `config/hyperparam_search_space.yaml`

**Effort**: 2 hours  
**Dependencies**: Feature 2.3 complete

---

### Story 2.5.2: Implement Grid Search
**As a** ML engineer  
**I want** grid search implementation  
**So that** I can exhaustively search hyperparameters

**Acceptance Criteria**:
- [ ] Function `grid_search(model_class, param_grid, train_data, val_data)` implemented
- [ ] Trains model for each combination
- [ ] Evaluates on validation set
- [ ] Returns best parameters and model
- [ ] Logs all results
- [ ] Unit tests

**Technical Notes**:
- Use sklearn `GridSearchCV` or custom implementation
- Metric: Validation RMSE

**Effort**: 5 hours  
**Dependencies**: Story 2.5.1, Feature 2.4

---

### Story 2.5.3: Implement Random Search
**As a** ML engineer  
**I want** random search implementation  
**So that** I can efficiently explore hyperparameters

**Acceptance Criteria**:
- [ ] Function `random_search(model_class, param_distributions, n_iter, train_data, val_data)` implemented
- [ ] Randomly samples n_iter combinations
- [ ] Evaluates each
- [ ] Returns best parameters and model
- [ ] Logs all results
- [ ] Unit tests

**Technical Notes**:
- Use sklearn `RandomizedSearchCV` or custom
- n_iter: 20-50 typical

**Effort**: 4 hours  
**Dependencies**: Story 2.5.1, Feature 2.4

---

### Story 2.5.4: Implement Bayesian Optimization (Optional)
**As a** ML engineer  
**I want** Bayesian optimization  
**So that** I can intelligently search hyperparameters

**Acceptance Criteria**:
- [ ] Function `bayesian_optimization(model_class, param_space, n_iter, train_data, val_data)` implemented
- [ ] Uses Bayesian optimization library (Optuna)
- [ ] Defines objective function
- [ ] Returns best parameters
- [ ] Logs optimization progress
- [ ] Unit tests

**Technical Notes**:
- Library: `optuna`
- Objective: Minimize validation RMSE

**Effort**: 6 hours (Optional)  
**Dependencies**: Story 2.5.1, Feature 2.4

---

### Story 2.5.5: Persist Best Hyperparameters
**As a** ML engineer  
**I want** best hyperparameters saved  
**So that** I can reproduce results

**Acceptance Criteria**:
- [ ] Save best parameters to JSON file
- [ ] Include validation metrics
- [ ] Timestamp and metadata
- [ ] Function `save_hyperparameters(params, metrics, path)` implemented
- [ ] Unit tests

**Technical Notes**:
- File: `models/best_hyperparameters_LSTM_WTI.json`

**Effort**: 2 hours  
**Dependencies**: Stories 2.5.2-2.5.4

---

## Feature 2.6: Model Versioning & Experiment Tracking (MLflow)

### Story 2.6.1: Setup MLflow Tracking Server
**As a** ML engineer  
**I want** MLflow tracking server running  
**So that** I can log experiments

**Acceptance Criteria**:
- [ ] MLflow installed
- [ ] Tracking server started (local or remote)
- [ ] Tracking URI configured
- [ ] Accessible via browser
- [ ] Documentation for setup

**Technical Notes**:
- Install: `pip install mlflow`
- Start: `mlflow ui --backend-store-uri sqlite:///mlflow.db`
- Default URL: `http://localhost:5000`

**Effort**: 2 hours  
**Dependencies**: None

---

### Story 2.6.2: Integrate MLflow into Training Pipeline
**As a** ML engineer  
**I want** training runs logged to MLflow  
**So that** I can track all experiments

**Acceptance Criteria**:
- [ ] Start MLflow run at training start
- [ ] Log hyperparameters (learning rate, layers, etc.)
- [ ] Log metrics per epoch (train loss, val loss, RMSE, MAE)
- [ ] End MLflow run at training end
- [ ] Unit tests

**Technical Notes**:
```python
import mlflow
mlflow.start_run()
mlflow.log_param("learning_rate", lr)
mlflow.log_metric("val_rmse", rmse, step=epoch)
mlflow.end_run()
```

**Effort**: 4 hours  
**Dependencies**: Story 2.6.1, Feature 2.4

---

### Story 2.6.3: Log Model Artifacts to MLflow
**As a** ML engineer  
**I want** model artifacts logged  
**So that** I can retrieve trained models

**Acceptance Criteria**:
- [ ] Log model file (PyTorch .pth or TensorFlow SavedModel)
- [ ] Log training plots (loss curves)
- [ ] Log feature importance (if applicable)
- [ ] Function `log_artifacts(model, plots, path)` implemented
- [ ] Unit tests

**Technical Notes**:
```python
mlflow.log_artifact("model.pth")
mlflow.log_figure(fig, "loss_curve.png")
```

**Effort**: 3 hours  
**Dependencies**: Story 2.6.2

---

### Story 2.6.4: Register Models in MLflow Model Registry
**As a** ML engineer  
**I want** models registered  
**So that** I can manage model versions

**Acceptance Criteria**:
- [ ] Register model after successful training
- [ ] Model name: `lstm_wti_forecaster`
- [ ] Tag with version, date, metrics
- [ ] Stage: None, Staging, Production
- [ ] Function `register_model(model, name, metrics)` implemented
- [ ] Unit tests

**Technical Notes**:
```python
mlflow.register_model(f"runs:/{run_id}/model", "lstm_wti_forecaster")
```

**Effort**: 3 hours  
**Dependencies**: Story 2.6.3

---

### Story 2.6.5: Create MLflow Experiment Comparison UI Access
**As a** ML engineer  
**I want** to compare experiments in MLflow UI  
**So that** I can select the best model

**Acceptance Criteria**:
- [ ] MLflow UI accessible
- [ ] Experiments listed
- [ ] Runs comparable (sort by metric)
- [ ] Artifacts viewable
- [ ] Documentation on how to use UI

**Technical Notes**:
- Access UI at `http://localhost:5000`
- Compare runs by selecting multiple and clicking "Compare"

**Effort**: 1 hour (Mostly documentation)  
**Dependencies**: Stories 2.6.1-2.6.4

---

## Feature 2.7: Multi-Horizon Forecasting Implementation

### Story 2.7.1: Design Multi-Horizon Architecture
**As a** ML engineer  
**I want** multi-horizon architecture designed  
**So that** I can implement it efficiently

**Acceptance Criteria**:
- [ ] Architecture documented (multi-output vs separate models)
- [ ] Decision documented (choose one approach)
- [ ] Output shape defined for 1, 7, 30 days
- [ ] Document in design decisions

**Technical Notes**:
- Option 1: Single model with 3 outputs (1-day, 7-day, 30-day)
- Option 2: Three separate models
- Recommendation: Single multi-output model

**Effort**: 2 hours  
**Dependencies**: Feature 2.3 complete

---

### Story 2.7.2: Implement Multi-Output LSTM Model
**As a** ML engineer  
**I want** LSTM with multiple outputs  
**So that** I can forecast multiple horizons

**Acceptance Criteria**:
- [ ] Modify LSTM to output 3 values (1, 7, 30 days)
- [ ] Loss function handles multiple outputs
- [ ] Training loop updated
- [ ] Unit tests

**Technical Notes**:
- Output layer: 3 units (one per horizon)
- Loss: MSE over all 3 outputs (can weight differently)

**Effort**: 5 hours  
**Dependencies**: Story 2.7.1, Feature 2.3

---

### Story 2.7.3: Implement Horizon-Specific Feature Engineering
**As a** ML engineer  
**I want** features optimized per horizon  
**So that** predictions are more accurate

**Acceptance Criteria**:
- [ ] Short-term (1-day): Use intraday features
- [ ] Medium-term (7-day): Use weekly patterns
- [ ] Long-term (30-day): Use monthly seasonality
- [ ] Feature selection per horizon
- [ ] Unit tests

**Technical Notes**:
- May require separate feature sets or feature weighting

**Effort**: 6 hours  
**Dependencies**: Story 2.7.2, Feature 2.1

---

### Story 2.7.4: Calculate Confidence Intervals for Each Horizon
**As a** ML engineer  
**I want** confidence intervals per forecast  
**So that** users understand uncertainty

**Acceptance Criteria**:
- [ ] Method `calculate_confidence_intervals(predictions, method)` implemented
- [ ] Methods: Quantile regression or prediction std
- [ ] Returns lower and upper bounds (95% CI)
- [ ] Confidence intervals per horizon
- [ ] Unit tests

**Technical Notes**:
- Quantile regression: Train separate models for 5th and 95th percentiles
- Prediction std: Use ensemble or MC dropout

**Effort**: 6 hours  
**Dependencies**: Story 2.7.2

---

### Story 2.7.5: Evaluate Performance Per Horizon
**As a** ML engineer  
**I want** metrics calculated per horizon  
**So that** I know which horizons are accurate

**Acceptance Criteria**:
- [ ] Calculate RMSE, MAE, MAPE per horizon
- [ ] Comparison table (1-day vs 7-day vs 30-day)
- [ ] Log metrics to MLflow
- [ ] Unit tests

**Technical Notes**:
- Expected: Accuracy decreases with longer horizons

**Effort**: 3 hours  
**Dependencies**: Story 2.7.2, Epic 3

---

# EPIC 3: Model Evaluation & Backtesting 📊

## Feature 3.1: Walk-Forward Validation Framework

### Story 3.1.1: Implement Walk-Forward Split Generator
**As a** data scientist  
**I want** walk-forward splits generated  
**So that** I can validate models without look-ahead bias

**Acceptance Criteria**:
- [ ] Function `walk_forward_split(df, initial_train_size, step_size, validation_size)` implemented
- [ ] Returns generator of (train, val) DataFrames
- [ ] Temporal order maintained
- [ ] Configurable parameters
- [ ] Unit tests

**Technical Notes**:
- Initial train: 3 years
- Validation window: 1 month
- Step: 1 month

**Effort**: 5 hours  
**Dependencies**: Epic 2 complete

---

### Story 3.1.2: Implement Rolling Window Approach
**As a** data scientist  
**I want** rolling window validation  
**So that** I use a fixed training window

**Acceptance Criteria**:
- [ ] Function `rolling_window_split(df, window_size, step_size, validation_size)` implemented
- [ ] Fixed training window (e.g., last 3 years)
- [ ] Rolls forward in time
- [ ] Returns generator of (train, val) DataFrames
- [ ] Unit tests

**Technical Notes**:
- Window: 3 years
- Step: 1 month

**Effort**: 4 hours  
**Dependencies**: Story 3.1.1

---

### Story 3.1.3: Implement Expanding Window Approach
**As a** data scientist  
**I want** expanding window validation  
**So that** training set grows over time

**Acceptance Criteria**:
- [ ] Function `expanding_window_split(df, initial_train_size, step_size, validation_size)` implemented
- [ ] Training set expands with each split
- [ ] Returns generator of (train, val) DataFrames
- [ ] Unit tests

**Technical Notes**:
- Initial train: 1 year
- Expands by step_size each iteration

**Effort**: 3 hours  
**Dependencies**: Story 3.1.1

---

### Story 3.1.4: Aggregate Results Across Windows
**As a** data scientist  
**I want** results aggregated across validation windows  
**So that** I have overall performance metrics

**Acceptance Criteria**:
- [ ] Function `aggregate_results(results_list)` implemented
- [ ] Calculates mean and std of metrics
- [ ] Returns summary DataFrame
- [ ] Unit tests

**Technical Notes**:
- Metrics: RMSE, MAE, MAPE, directional accuracy
- Summary: mean ± std

**Effort**: 2 hours  
**Dependencies**: Stories 3.1.1-3.1.3

---

## Feature 3.2: Statistical Metrics Calculation

### Story 3.2.1: Implement RMSE Calculation
**As a** data scientist  
**I want** RMSE calculated  
**So that** I can measure prediction error

**Acceptance Criteria**:
- [ ] Function `calculate_rmse(y_true, y_pred)` implemented
- [ ] Handles numpy arrays and pandas Series
- [ ] Returns scalar RMSE value
- [ ] Unit tests

**Technical Notes**:
- RMSE = sqrt(mean((y_true - y_pred)^2))
- Use sklearn or numpy

**Effort**: 1 hour  
**Dependencies**: None

---

### Story 3.2.2: Implement MAE, MAPE, R² Calculations
**As a** data scientist  
**I want** additional metrics calculated  
**So that** I have comprehensive evaluation

**Acceptance Criteria**:
- [ ] Function `calculate_mae(y_true, y_pred)` implemented
- [ ] Function `calculate_mape(y_true, y_pred)` implemented
- [ ] Function `calculate_r2(y_true, y_pred)` implemented
- [ ] Unit tests for each

**Technical Notes**:
- MAE = mean(abs(y_true - y_pred))
- MAPE = mean(abs((y_true - y_pred) / y_true)) * 100
- R² = 1 - (SS_res / SS_tot)
- Use sklearn.metrics

**Effort**: 2 hours  
**Dependencies**: Story 3.2.1

---

### Story 3.2.3: Implement Directional Accuracy Calculation
**As a** data scientist  
**I want** directional accuracy calculated  
**So that** I know how often the model predicts the right direction

**Acceptance Criteria**:
- [ ] Function `calculate_directional_accuracy(y_true, y_pred)` implemented
- [ ] Compares direction of change (up/down)
- [ ] Returns percentage correct
- [ ] Unit tests

**Technical Notes**:
- Direction correct if sign(y_pred[t] - y_true[t-1]) == sign(y_true[t] - y_true[t-1])

**Effort**: 3 hours  
**Dependencies**: Story 3.2.1

---

### Story 3.2.4: Create Metrics Calculator Class
**As a** data scientist  
**I want** a unified metrics calculator  
**So that** all metrics are calculated consistently

**Acceptance Criteria**:
- [ ] Class `MetricsCalculator` created
- [ ] Method `calculate_all_metrics(y_true, y_pred)` returns dict of all metrics
- [ ] Method `calculate_per_horizon_metrics(y_true, y_pred, horizons)` for multi-horizon
- [ ] Unit tests

**Technical Notes**:
- Returns: {'rmse': ..., 'mae': ..., 'mape': ..., 'r2': ..., 'directional_accuracy': ...}

**Effort**: 3 hours  
**Dependencies**: Stories 3.2.1-3.2.3

---

## Feature 3.3: Trading Signal Generation Logic

### Story 3.3.1: Define Trading Signal Rules
**As a** quantitative analyst  
**I want** trading signal rules defined  
**So that** signal generation is consistent

**Acceptance Criteria**:
- [ ] Rules documented:
  - BUY: forecast > current_price * (1 + threshold)
  - SELL: forecast < current_price * (1 - threshold)
  - HOLD: otherwise
- [ ] Threshold configurable (default 2%)
- [ ] Document in design decisions

**Technical Notes**:
- Threshold: 0.02 (2%)
- Can be adjusted based on risk tolerance

**Effort**: 2 hours  
**Dependencies**: None

---

### Story 3.3.2: Implement Signal Generation Function
**As a** quantitative analyst  
**I want** signals generated from forecasts  
**So that** I can simulate trading

**Acceptance Criteria**:
- [ ] Function `generate_signals(current_prices, forecasts, threshold)` implemented
- [ ] Returns Series with signals: ['BUY', 'SELL', 'HOLD']
- [ ] Handles edge cases (NaN, infinity)
- [ ] Unit tests

**Technical Notes**:
- Input: current_prices (array), forecasts (array), threshold (float)
- Output: signals (array of strings)

**Effort**: 3 hours  
**Dependencies**: Story 3.3.1

---

### Story 3.3.3: Implement Signal Confidence Scoring
**As a** quantitative analyst  
**I want** confidence scores for signals  
**So that** users know signal reliability

**Acceptance Criteria**:
- [ ] Function `calculate_signal_confidence(forecast, confidence_interval, current_price)` implemented
- [ ] Confidence based on CI width and forecast magnitude
- [ ] Returns score 0-1
- [ ] Unit tests

**Technical Notes**:
- Higher confidence if CI is narrow and forecast is far from current price

**Effort**: 4 hours  
**Dependencies**: Story 3.3.2

---

### Story 3.3.4: Track Signal History
**As a** quantitative analyst  
**I want** signal history stored  
**So that** I can analyze signal performance over time

**Acceptance Criteria**:
- [ ] Function `store_signal(date, commodity, signal, confidence, forecast, actual)` implemented
- [ ] Stores in database or file
- [ ] Function `retrieve_signal_history(commodity, start_date, end_date)` implemented
- [ ] Unit tests

**Technical Notes**:
- Storage: Database table or CSV file
- Useful for post-analysis

**Effort**: 4 hours  
**Dependencies**: Story 3.3.2, Epic 1

---

## Feature 3.4: Trading Simulation Engine

### Story 3.4.1: Implement Position Management
**As a** quantitative analyst  
**I want** positions tracked (long/short/flat)  
**So that** I can simulate realistic trading

**Acceptance Criteria**:
- [ ] Class `PositionManager` created
- [ ] Tracks current position: 'LONG', 'SHORT', 'FLAT'
- [ ] Method `open_position(position_type, price, quantity, date)` implemented
- [ ] Method `close_position(price, date)` implemented
- [ ] Method `get_current_position()` implemented
- [ ] Unit tests

**Technical Notes**:
- Position types: LONG (bullish), SHORT (bearish), FLAT (no position)

**Effort**: 5 hours  
**Dependencies**: Feature 3.3 complete

---

### Story 3.4.2: Implement Trade Execution Simulation
**As a** quantitative analyst  
**I want** trades executed based on signals  
**So that** I can calculate P&L

**Acceptance Criteria**:
- [ ] Function `execute_trade(signal, current_position, price, date)` implemented
- [ ] Logic:
  - BUY signal + FLAT → Open LONG
  - SELL signal + LONG → Close LONG, Open SHORT (optional)
  - HOLD → No action
- [ ] Returns trade details
- [ ] Unit tests

**Technical Notes**:
- Simplified: Only LONG positions initially, can extend to SHORT

**Effort**: 5 hours  
**Dependencies**: Story 3.4.1

---

### Story 3.4.3: Calculate P&L Per Trade
**As a** quantitative analyst  
**I want** P&L calculated per trade  
**So that** I know profitability

**Acceptance Criteria**:
- [ ] Function `calculate_pnl(entry_price, exit_price, quantity, position_type)` implemented
- [ ] Handles LONG and SHORT positions
- [ ] Returns P&L (dollar amount)
- [ ] Unit tests

**Technical Notes**:
- LONG P&L = (exit_price - entry_price) * quantity
- SHORT P&L = (entry_price - exit_price) * quantity

**Effort**: 3 hours  
**Dependencies**: Story 3.4.2

---

### Story 3.4.4: Track Cumulative P&L
**As a** quantitative analyst  
**I want** cumulative P&L tracked  
**So that** I can see overall performance

**Acceptance Criteria**:
- [ ] Class `PortfolioTracker` created
- [ ] Tracks cumulative P&L over time
- [ ] Method `update_pnl(trade_pnl, date)` implemented
- [ ] Method `get_cumulative_pnl()` returns Series
- [ ] Unit tests

**Technical Notes**:
- Initialize with starting capital
- Track P&L over time

**Effort**: 4 hours  
**Dependencies**: Story 3.4.3

---

### Story 3.4.5: Calculate Win Rate and Average Profit/Loss
**As a** quantitative analyst  
**I want** win rate and avg profit/loss calculated  
**So that** I can evaluate strategy

**Acceptance Criteria**:
- [ ] Function `calculate_win_rate(trades)` implemented
- [ ] Function `calculate_avg_profit(trades)` implemented
- [ ] Function `calculate_avg_loss(trades)` implemented
- [ ] Returns metrics dictionary
- [ ] Unit tests

**Technical Notes**:
- Win rate = (# profitable trades) / (# total trades)
- Avg profit = mean(P&L of winning trades)
- Avg loss = mean(P&L of losing trades)

**Effort**: 3 hours  
**Dependencies**: Story 3.4.3

---

### Story 3.4.6: Implement Transaction Costs (Optional)
**As a** quantitative analyst  
**I want** transaction costs included  
**So that** simulation is realistic

**Acceptance Criteria**:
- [ ] Configurable transaction cost (e.g., 0.1% per trade)
- [ ] Deduct from P&L on each trade
- [ ] Unit tests

**Technical Notes**:
- Cost = trade_value * cost_rate
- Deduct from P&L

**Effort**: 2 hours (Optional)  
**Dependencies**: Story 3.4.3

---

## Feature 3.5: Risk Metrics Module

### Story 3.5.1: Calculate Sharpe Ratio
**As a** quantitative analyst  
**I want** Sharpe ratio calculated  
**So that** I can measure risk-adjusted return

**Acceptance Criteria**:
- [ ] Function `calculate_sharpe_ratio(returns, risk_free_rate)` implemented
- [ ] Annualized Sharpe ratio
- [ ] Risk-free rate configurable (default 2%)
- [ ] Unit tests

**Technical Notes**:
- Sharpe = (mean_return - risk_free_rate) / std_return
- Annualize: multiply by sqrt(252) for daily returns

**Effort**: 3 hours  
**Dependencies**: Feature 3.4 complete

---

### Story 3.5.2: Calculate Maximum Drawdown
**As a** quantitative analyst  
**I want** max drawdown calculated  
**So that** I know worst decline

**Acceptance Criteria**:
- [ ] Function `calculate_max_drawdown(cumulative_returns)` implemented
- [ ] Finds peak-to-trough decline
- [ ] Returns max drawdown as percentage
- [ ] Unit tests

**Technical Notes**:
- Max DD = min((cumulative_returns - running_max) / running_max)

**Effort**: 3 hours  
**Dependencies**: Feature 3.4 complete

---

### Story 3.5.3: Calculate Volatility (Annualized)
**As a** quantitative analyst  
**I want** volatility calculated  
**So that** I know risk level

**Acceptance Criteria**:
- [ ] Function `calculate_volatility(returns)` implemented
- [ ] Annualized volatility
- [ ] Unit tests

**Technical Notes**:
- Volatility = std(returns) * sqrt(252)

**Effort**: 2 hours  
**Dependencies**: Feature 3.4 complete

---

### Story 3.5.4: Calculate Sortino Ratio and Calmar Ratio (Optional)
**As a** quantitative analyst  
**I want** additional risk metrics  
**So that** I have comprehensive risk assessment

**Acceptance Criteria**:
- [ ] Function `calculate_sortino_ratio(returns, risk_free_rate)` implemented
- [ ] Function `calculate_calmar_ratio(returns, max_drawdown)` implemented
- [ ] Unit tests

**Technical Notes**:
- Sortino = (mean_return - risk_free_rate) / downside_std
- Calmar = annualized_return / abs(max_drawdown)

**Effort**: 3 hours (Optional)  
**Dependencies**: Stories 3.5.1, 3.5.2

---

### Story 3.5.5: Create Risk Metrics Summary Function
**As a** quantitative analyst  
**I want** all risk metrics in one function  
**So that** analysis is streamlined

**Acceptance Criteria**:
- [ ] Function `calculate_risk_metrics(returns, cumulative_returns, risk_free_rate)` implemented
- [ ] Returns dict with all risk metrics
- [ ] Unit tests

**Technical Notes**:
- Returns: {'sharpe': ..., 'max_drawdown': ..., 'volatility': ..., 'sortino': ..., 'calmar': ...}

**Effort**: 2 hours  
**Dependencies**: Stories 3.5.1-3.5.4

---

## Feature 3.6: Model Comparison Dashboard

### Story 3.6.1: Create Model Comparison Table
**As a** data scientist  
**I want** models compared in a table  
**So that** I can select the best model

**Acceptance Criteria**:
- [ ] Function `create_comparison_table(models_results)` implemented
- [ ] Table columns: Model Name, RMSE, MAE, MAPE, Directional Accuracy, Sharpe Ratio, Max Drawdown
- [ ] Sorted by primary metric (e.g., Sharpe Ratio)
- [ ] Returns pandas DataFrame
- [ ] Unit tests

**Technical Notes**:
- Input: List of dicts with model results

**Effort**: 3 hours  
**Dependencies**: Features 3.2, 3.4, 3.5 complete

---

### Story 3.6.2: Implement Best Model Selection Logic
**As a** data scientist  
**I want** automatic best model selection  
**So that** deployment is automated

**Acceptance Criteria**:
- [ ] Function `select_best_model(comparison_table, primary_metric)` implemented
- [ ] Selects model with best metric
- [ ] Handles ties (secondary metric)
- [ ] Returns best model name and metrics
- [ ] Unit tests

**Technical Notes**:
- Primary metric: Sharpe Ratio or Directional Accuracy
- Secondary: RMSE

**Effort**: 2 hours  
**Dependencies**: Story 3.6.1

---

### Story 3.6.3: Export Comparison Report
**As a** data scientist  
**I want** comparison report exported  
**So that** I can share results

**Acceptance Criteria**:
- [ ] Function `export_comparison_report(comparison_table, path)` implemented
- [ ] Exports as CSV and JSON
- [ ] Includes metadata (date, commodity)
- [ ] Unit tests

**Technical Notes**:
- CSV for Excel, JSON for programmatic access

**Effort**: 2 hours  
**Dependencies**: Story 3.6.1

---

## Feature 3.7: Backtesting Visualization Tools

### Story 3.7.1: Create Predicted vs Actual Price Plot
**As a** data scientist  
**I want** to visualize predicted vs actual prices  
**So that** I can see model accuracy

**Acceptance Criteria**:
- [ ] Function `plot_predicted_vs_actual(dates, y_true, y_pred)` implemented
- [ ] Line plot with two series
- [ ] Confidence intervals (optional)
- [ ] Saves plot to file
- [ ] Returns matplotlib figure
- [ ] Unit tests

**Technical Notes**:
- Library: matplotlib or seaborn
- X-axis: Date, Y-axis: Price

**Effort**: 4 hours  
**Dependencies**: Feature 3.2 complete

---

### Story 3.7.2: Create Forecast Error Over Time Plot
**As a** data scientist  
**I want** to visualize forecast errors over time  
**So that** I can identify patterns

**Acceptance Criteria**:
- [ ] Function `plot_forecast_error(dates, errors)` implemented
- [ ] Line or scatter plot
- [ ] Zero line highlighted
- [ ] Saves plot to file
- [ ] Unit tests

**Technical Notes**:
- Error = y_true - y_pred

**Effort**: 3 hours  
**Dependencies**: Feature 3.2 complete

---

### Story 3.7.3: Create Cumulative P&L Chart
**As a** quantitative analyst  
**I want** cumulative P&L visualized  
**So that** I can see strategy performance

**Acceptance Criteria**:
- [ ] Function `plot_cumulative_pnl(dates, cumulative_pnl)` implemented
- [ ] Line plot
- [ ] Zero line highlighted
- [ ] Saves plot to file
- [ ] Unit tests

**Technical Notes**:
- X-axis: Date, Y-axis: Cumulative P&L

**Effort**: 3 hours  
**Dependencies**: Feature 3.4 complete

---

### Story 3.7.4: Create Drawdown Chart
**As a** quantitative analyst  
**I want** drawdown visualized  
**So that** I can see risk periods

**Acceptance Criteria**:
- [ ] Function `plot_drawdown(dates, drawdown)` implemented
- [ ] Area plot (filled)
- [ ] Highlights maximum drawdown period
- [ ] Saves plot to file
- [ ] Unit tests

**Technical Notes**:
- Drawdown = (cumulative_return - running_max) / running_max

**Effort**: 3 hours  
**Dependencies**: Feature 3.5 complete

---

### Story 3.7.5: Create Trade Distribution Histogram
**As a** quantitative analyst  
**I want** trade P&L distribution visualized  
**So that** I can see profit/loss spread

**Acceptance Criteria**:
- [ ] Function `plot_trade_distribution(trade_pnls)` implemented
- [ ] Histogram with bins
- [ ] Vertical line at zero
- [ ] Shows mean and std
- [ ] Saves plot to file
- [ ] Unit tests

**Technical Notes**:
- X-axis: P&L, Y-axis: Frequency

**Effort**: 3 hours  
**Dependencies**: Feature 3.4 complete

---

### Story 3.7.6: Create Comprehensive Backtesting Report
**As a** data scientist  
**I want** all visualizations in one report  
**So that** analysis is comprehensive

**Acceptance Criteria**:
- [ ] Function `generate_backtest_report(results, output_dir)` implemented
- [ ] Generates all plots
- [ ] Creates summary PDF or HTML (optional)
- [ ] Saves plots as PNG
- [ ] Unit tests

**Technical Details**:
- Output: Folder with all plots
- Optional: Use matplotlib PDF backend or HTML report generator

**Effort**: 5 hours  
**Dependencies**: Stories 3.7.1-3.7.5

---

---

**Due to the comprehensive nature of this document, I'll create a summary section and note that Epics 4-8 follow the same detailed pattern. Would you like me to continue with the remaining Epics (4-8) in full detail, or would you prefer to review what's been created so far?**

**Current Progress:**
- ✅ Epic 1: Complete (6 features, ~30 user stories)
- ✅ Epic 2: Complete (7 features, ~37 user stories)
- ✅ Epic 3: Complete (7 features, ~33 user stories)
- ⏳ Epic 4-8: To be detailed (37 features remaining)

**Estimated Total User Stories:** ~150-180 stories across all 64 features

---

## Summary

This document provides detailed user stories for Epics 1-3 (first 20 features, ~100 user stories). Each story includes:
- Clear user story statement
- Detailed acceptance criteria
- Technical implementation notes
- Effort estimation
- Dependencies

**Next Steps:**
1. Review Epics 1-3 user stories
2. Provide feedback or approval
3. I will then complete Epics 4-8 user stories
4. Final approval before implementation begins

---

**Status**: ⏳ Awaiting Your Review (Epics 1-3 Complete)

