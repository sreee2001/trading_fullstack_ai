# System Architecture Diagram

**Version**: 1.0  
**Date**: December 15, 2025  
**Status**: ✅ Complete

---

## High-Level System Architecture

```mermaid
graph TB
    subgraph "External Data Sources"
        EIA[EIA API<br/>Energy Information Administration]
        FRED[FRED API<br/>Federal Reserve Economic Data]
        YAHOO[Yahoo Finance<br/>Market Data]
    end

    subgraph "Data Layer"
        INGEST[Data Ingestion<br/>EIA/FRED/Yahoo Clients]
        VALIDATE[Data Validation<br/>Quality Framework]
        DB[(PostgreSQL + TimescaleDB<br/>Time-Series Database)]
        PIPELINE[Pipeline Orchestrator<br/>APScheduler]
    end

    subgraph "ML Layer"
        FE[Feature Engineering<br/>Technical Indicators]
        MODELS[ML Models<br/>ARIMA/Prophet/LSTM]
        TRAIN[Training Infrastructure<br/>Walk-Forward Validation]
        MLFLOW[MLflow<br/>Experiment Tracking]
        REGISTRY[Model Registry<br/>Version Management]
    end

    subgraph "API Layer"
        FASTAPI[FastAPI Application<br/>REST + WebSocket]
        AUTH[Authentication<br/>API Key Management]
        CACHE[Redis Cache<br/>Rate Limiting]
        ENDPOINTS[API Endpoints<br/>Forecast/Historical/Backtest]
    end

    subgraph "Frontend Layer"
        REACT[React Dashboard<br/>TypeScript]
        STREAMLIT[Streamlit Dashboard<br/>Python]
        CHARTS[Interactive Charts<br/>Recharts/Plotly]
    end

    subgraph "Analytics Layer"
        BACKTEST[Backtesting Engine<br/>Trading Simulation]
        ANALYTICS[Advanced Analytics<br/>Correlation/Volatility]
        METRICS[Performance Metrics<br/>Risk Analysis]
    end

    EIA --> INGEST
    FRED --> INGEST
    YAHOO --> INGEST
    INGEST --> VALIDATE
    VALIDATE --> DB
    PIPELINE --> INGEST
    
    DB --> FE
    FE --> MODELS
    MODELS --> TRAIN
    TRAIN --> MLFLOW
    MLFLOW --> REGISTRY
    
    REGISTRY --> FASTAPI
    DB --> FASTAPI
    FASTAPI --> AUTH
    FASTAPI --> CACHE
    FASTAPI --> ENDPOINTS
    
    ENDPOINTS --> REACT
    ENDPOINTS --> STREAMLIT
    REACT --> CHARTS
    STREAMLIT --> CHARTS
    
    MODELS --> BACKTEST
    DB --> BACKTEST
    BACKTEST --> ANALYTICS
    ANALYTICS --> METRICS
    METRICS --> REACT
    METRICS --> STREAMLIT

    style EIA fill:#e1f5ff
    style FRED fill:#e1f5ff
    style YAHOO fill:#e1f5ff
    style DB fill:#fff4e1
    style CACHE fill:#fff4e1
    style FASTAPI fill:#e8f5e9
    style REACT fill:#f3e5f5
    style STREAMLIT fill:#f3e5f5
    style MLFLOW fill:#fff9c4
```

---

## Component Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Auth
    participant Cache
    participant ModelService
    participant Database
    participant MLflow

    User->>Frontend: Request Forecast
    Frontend->>API: POST /api/v1/forecast
    API->>Auth: Validate API Key
    Auth-->>API: Authorized
    API->>Cache: Check Cache
    Cache-->>API: Cache Miss
    API->>ModelService: Load Model
    ModelService->>MLflow: Get Model Version
    MLflow-->>ModelService: Model Metadata
    ModelService->>Database: Fetch Historical Data
    Database-->>ModelService: Price Data
    ModelService->>ModelService: Generate Forecast
    ModelService-->>API: Forecast Result
    API->>Cache: Store in Cache
    API-->>Frontend: Forecast Response
    Frontend-->>User: Display Forecast
```

---

## Technology Stack Visualization

```mermaid
graph LR
    subgraph "Frontend"
        A[React + TypeScript]
        B[Streamlit]
        C[Recharts/Plotly]
    end
    
    subgraph "API"
        D[FastAPI]
        E[WebSocket]
        F[Pydantic]
    end
    
    subgraph "ML"
        G[PyTorch/TensorFlow]
        H[scikit-learn]
        I[Statsmodels]
        J[Prophet]
    end
    
    subgraph "Data"
        K[PostgreSQL]
        L[TimescaleDB]
        M[Redis]
    end
    
    subgraph "MLOps"
        N[MLflow]
        O[Docker]
        P[GitHub Actions]
    end
    
    A --> D
    B --> D
    D --> E
    D --> F
    D --> G
    D --> H
    G --> N
    H --> N
    D --> K
    K --> L
    D --> M
    N --> O
    O --> P
```

---

## Data Flow Architecture

```mermaid
flowchart TD
    START([Data Sources]) --> INGEST[Data Ingestion]
    INGEST --> VALIDATE{Validation}
    VALIDATE -->|Pass| STORE[Store in Database]
    VALIDATE -->|Fail| ALERT[Alert & Log]
    STORE --> FEATURE[Feature Engineering]
    FEATURE --> TRAIN[Model Training]
    TRAIN --> EVAL{Evaluation}
    EVAL -->|Good| REGISTER[Register Model]
    EVAL -->|Poor| TUNE[Hyperparameter Tuning]
    TUNE --> TRAIN
    REGISTER --> DEPLOY[Deploy to API]
    DEPLOY --> SERVE[Serve Forecasts]
    SERVE --> CLIENT[Client Applications]
    
    style START fill:#e1f5ff
    style STORE fill:#fff4e1
    style REGISTER fill:#fff9c4
    style SERVE fill:#e8f5e9
```

---

**Last Updated**: December 15, 2025

