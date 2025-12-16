# Energy Price Forecasting System - Simple Overview

## 🎯 What This Project Does

**Predicts energy prices (oil, gas) using AI/ML models and displays forecasts in a web dashboard.**

---

## 📁 What Each Folder Does (1-2 Liners)

### **Data Layer** (Getting & Storing Data)
- **`data_ingestion/`** - Fetches price data from EIA, FRED, Yahoo Finance APIs
- **`data_validation/`** - Checks if data is good quality before storing it
- **`database/`** - PostgreSQL database that stores all historical price data
- **`data_pipeline/`** - Automated scheduler that runs data fetching daily

### **ML Layer** (Training & Models)
- **`feature_engineering/`** - Creates technical indicators (moving averages, etc.) from raw prices
- **`models/`** - Contains LSTM, ARIMA, Prophet forecasting models
- **`training/`** - Code that trains the ML models on historical data
- **`hyperparameter_tuning/`** - Finds best model settings automatically
- **`mlflow_tracking/`** - Tracks which models perform best (experiment tracking)
- **`multi_horizon/`** - Models that predict 1-day, 7-day, 30-day forecasts

### **API Layer** (Backend Server)
- **`api/`** - FastAPI server that provides REST API endpoints (forecast, historical data, etc.)
- **`api/routes/`** - API endpoints (like `/api/v1/forecast`)
- **`api/services/`** - Business logic (loads models, generates forecasts)
- **`api/auth/`** - API key authentication

### **Frontend Layer** (User Interface)
- **`dashboard/`** - React web app (main dashboard with charts and forecasts)
- **`dashboard-streamlit/`** - Alternative Python-based dashboard (simpler)

### **Analytics & Evaluation**
- **`analytics/`** - Market analysis tools (correlation, volatility, seasonality)
- **`evaluation/`** - Tests how good models are (metrics, backtesting)
- **`trading/`** - Trading signal generation and strategy logic

### **Infrastructure**
- **`mlops/`** - Model deployment and monitoring automation
- **`backtesting/`** - Tests trading strategies on historical data
- **`utils/`** - Shared helper functions used everywhere
- **`config/`** - Configuration files
- **`tests/`** - Unit tests and integration tests

---

## 🚀 Execution Order (What to Run & When)

### **Phase 1: Setup & Data Collection** (One-Time Setup)

1. **Database Setup**
   ```bash
   # Start PostgreSQL database
   docker-compose up -d postgres
   # Run migrations
   python -m database.utils (or similar)
   ```

2. **Data Fetching** (Get Historical Data)
   ```bash
   # Run data ingestion to fetch historical prices
   python -m data_ingestion.eia_client
   python -m data_ingestion.fred_client
   # Or use the pipeline scheduler
   python -m data_pipeline.scheduler
   ```
   **What it does**: Fetches months/years of historical price data and stores in database

---

### **Phase 2: ML Training** (Train Models - Run Periodically)

3. **Feature Engineering**
   ```bash
   python -m feature_engineering.pipeline
   ```
   **What it does**: Creates technical indicators from raw price data

4. **Train Models**
   ```bash
   python -m training.trainer
   # Or train specific models:
   python -m models.lstm.lstm_model (train)
   python -m models.baseline.arima_model (train)
   ```
   **What it does**: Trains LSTM/ARIMA/Prophet models on historical data, saves trained models

5. **Hyperparameter Tuning** (Optional but Recommended)
   ```bash
   python -m hyperparameter_tuning.tuner
   ```
   **What it does**: Finds best model parameters automatically

6. **Model Evaluation**
   ```bash
   python -m evaluation.performance_metrics
   ```
   **What it does**: Tests model accuracy, saves best models to MLflow registry

---

### **Phase 3: Production Services** (Run Continuously)

7. **Start API Server** (Backend)
   ```bash
   cd src/energy-price-forecasting
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```
   **What it does**: Starts FastAPI server that serves forecasts via REST API

8. **Start Frontend Dashboard** (Optional - React)
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```
   **What it does**: Starts React web app on http://localhost:5173

9. **Start Streamlit Dashboard** (Alternative - Simpler)
   ```bash
   cd dashboard-streamlit
   streamlit run app.py
   ```
   **What it does**: Starts Python-based dashboard on http://localhost:8501

---

### **Phase 4: Ongoing Operations** (Automated)

10. **Data Pipeline** (Scheduled Daily)
    ```bash
    python -m data_pipeline.scheduler
    ```
    **What it does**: Automatically fetches new price data daily, validates it, stores it

11. **Model Retraining** (Scheduled Weekly/Monthly)
    ```bash
    python -m training.trainer --auto-retrain
    ```
    **What it does**: Retrains models with new data, deploys better models automatically

---

## 🔄 Typical Daily Workflow

### **Morning (Automated)**
1. Data pipeline runs → Fetches yesterday's prices
2. Data validation → Checks quality
3. Database updated → New prices stored

### **When User Requests Forecast**
1. User opens dashboard → Frontend loads
2. User clicks "Generate Forecast" → Frontend calls API
3. API loads trained model → From MLflow or disk
4. API fetches recent historical data → Last 90 days
5. Model generates forecast → Predicts next 7/30 days
6. API returns forecast → JSON response
7. Frontend displays chart → Shows forecast with confidence intervals

---

## 🎯 Quick Start (Minimum to Get Running)

**If you just want to see forecasts working:**

1. **Start Database**
   ```bash
   docker-compose up -d postgres
   ```

2. **Fetch Some Data** (or use existing data if available)
   ```bash
   python -m data_ingestion.eia_client
   ```

3. **Train a Model** (or use placeholder model)
   ```bash
   python -m training.trainer
   ```

4. **Start API**
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

5. **Start Dashboard**
   ```bash
   cd dashboard
   npm run dev
   ```

6. **Open Browser** → http://localhost:5173 → Generate Forecast

---

## 🔍 Current Issue You're Experiencing

**Problem**: Forecast shows same value repeated

**Root Cause**: 
- LSTM models need historical data as input to predict
- API was calling `model.predict(steps=7)` without providing data
- Fixed: Now API fetches last 90 days of data and passes it to LSTM models

**What to Check**:
1. Is API server running? (port 8000)
2. Is database populated with historical data?
3. Are models trained? (or using placeholder models)
4. Check API logs for errors

---

## 📊 Data Flow Diagram (Simple)

```
External APIs (EIA, FRED, Yahoo)
    ↓
data_ingestion/ (fetches)
    ↓
data_validation/ (validates)
    ↓
database/ (stores in PostgreSQL)
    ↓
feature_engineering/ (creates indicators)
    ↓
training/ (trains models)
    ↓
models/ (saves trained models)
    ↓
api/ (loads models, generates forecasts)
    ↓
dashboard/ (displays to user)
```

---

## 🛠️ Key Files to Know

- **`api/main.py`** - API server entry point
- **`api/routes/forecast.py`** - Forecast endpoint (the one we just fixed!)
- **`api/services/model_service.py`** - Loads ML models
- **`models/lstm/lstm_model.py`** - LSTM model implementation
- **`database/operations.py`** - Database queries
- **`dashboard/src/pages/Forecast.tsx`** - Frontend forecast page

---

## 💡 Understanding the Forecast Issue Fix

**Before**: 
- API called `model.predict(steps=7)` 
- LSTM models need data → Error or same value

**After**:
- API detects LSTM model needs data
- Fetches last 90 days from database
- Calls `model.predict(data=historical_df, steps=7)`
- Extracts varying forecast values correctly

---

**That's it! This is the entire system in simple terms.**

