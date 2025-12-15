# Data Flow Architecture Diagram

**Version**: 1.0  
**Date**: December 15, 2025  
**Status**: ✅ Complete

---

## Complete Data Flow

```mermaid
flowchart TD
    subgraph "Data Sources"
        EIA[EIA API]
        FRED[FRED API]
        YAHOO[Yahoo Finance]
    end
    
    subgraph "Ingestion Layer"
        EIA_CLIENT[EIA Client]
        FRED_CLIENT[FRED Client]
        YAHOO_CLIENT[Yahoo Client]
    end
    
    subgraph "Validation Layer"
        VALIDATOR[Data Validator]
        QUALITY_CHECK{Quality Check}
    end
    
    subgraph "Storage Layer"
        POSTGRES[(PostgreSQL)]
        TIMESCALE[TimescaleDB<br/>Hypertables]
    end
    
    subgraph "Processing Layer"
        FEATURE_ENG[Feature Engineering]
        MODEL_TRAIN[Model Training]
        FORECAST_GEN[Forecast Generation]
    end
    
    subgraph "API Layer"
        FASTAPI[FastAPI]
        CACHE[Redis Cache]
    end
    
    subgraph "Frontend Layer"
        REACT[React Dashboard]
        STREAMLIT[Streamlit Dashboard]
    end
    
    EIA --> EIA_CLIENT
    FRED --> FRED_CLIENT
    YAHOO --> YAHOO_CLIENT
    
    EIA_CLIENT --> VALIDATOR
    FRED_CLIENT --> VALIDATOR
    YAHOO_CLIENT --> VALIDATOR
    
    VALIDATOR --> QUALITY_CHECK
    QUALITY_CHECK -->|Pass 98%+| POSTGRES
    QUALITY_CHECK -->|Fail| ALERT[Alert & Log]
    
    POSTGRES --> TIMESCALE
    TIMESCALE --> FEATURE_ENG
    FEATURE_ENG --> MODEL_TRAIN
    MODEL_TRAIN --> FORECAST_GEN
    
    TIMESCALE --> FASTAPI
    FORECAST_GEN --> FASTAPI
    FASTAPI --> CACHE
    FASTAPI --> REACT
    FASTAPI --> STREAMLIT
    
    style EIA fill:#e1f5ff
    style FRED fill:#e1f5ff
    style YAHOO fill:#e1f5ff
    style POSTGRES fill:#fff4e1
    style TIMESCALE fill:#fff4e1
    style CACHE fill:#fff4e1
    style FASTAPI fill:#e8f5e9
    style REACT fill:#f3e5f5
    style STREAMLIT fill:#f3e5f5
```

---

## Data Pipeline Flow

```mermaid
sequenceDiagram
    participant Scheduler
    participant Pipeline
    participant EIA
    participant FRED
    participant Yahoo
    participant Validator
    participant Database
    participant Notifier

    Scheduler->>Pipeline: Trigger Daily Run
    Pipeline->>EIA: Fetch WTI Data
    EIA-->>Pipeline: Price Data
    Pipeline->>FRED: Fetch Brent Data
    FRED-->>Pipeline: Price Data
    Pipeline->>Yahoo: Fetch NG Data
    Yahoo-->>Pipeline: Price Data
    Pipeline->>Validator: Validate All Data
    Validator->>Validator: Check Quality
    alt Quality Pass
        Validator->>Database: Store Data
        Database-->>Pipeline: Success
        Pipeline->>Notifier: Send Success Notification
    else Quality Fail
        Validator-->>Pipeline: Validation Errors
        Pipeline->>Notifier: Send Alert
    end
```

---

## Forecast Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Auth
    participant Cache
    participant ModelService
    participant Database
    participant Model

    User->>Frontend: Request Forecast
    Frontend->>API: POST /forecast
    API->>Auth: Validate API Key
    Auth-->>API: Authorized
    API->>Cache: Check Cache Key
    alt Cache Hit
        Cache-->>API: Cached Forecast
        API-->>Frontend: Return Cached
    else Cache Miss
        API->>ModelService: Load Model
        ModelService->>Database: Get Historical Data
        Database-->>ModelService: Price Series
        ModelService->>Model: Generate Forecast
        Model-->>ModelService: Predictions
        ModelService-->>API: Forecast Result
        API->>Cache: Store in Cache
        API-->>Frontend: Return Forecast
    end
    Frontend-->>User: Display Forecast
```

---

## Model Training Data Flow

```mermaid
flowchart LR
    DB[(Database)] --> EXTRACT[Extract Historical Data]
    EXTRACT --> SPLIT[Train/Test Split]
    SPLIT --> FEATURE[Feature Engineering]
    FEATURE --> TRAIN[Train Model]
    TRAIN --> EVAL[Evaluate Model]
    EVAL --> CHECK{Performance OK?}
    CHECK -->|Yes| REGISTER[Register in MLflow]
    CHECK -->|No| TUNE[Hyperparameter Tuning]
    TUNE --> TRAIN
    REGISTER --> DEPLOY[Deploy to API]
    
    style DB fill:#fff4e1
    style REGISTER fill:#fff9c4
    style DEPLOY fill:#e8f5e9
```

---

**Last Updated**: December 15, 2025

