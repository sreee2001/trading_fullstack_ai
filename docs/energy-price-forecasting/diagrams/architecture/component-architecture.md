# Component Architecture Diagram

**Version**: 1.0  
**Date**: December 15, 2025  
**Status**: ✅ Complete

---

## Detailed Component Architecture

```mermaid
graph TB
    subgraph "Data Ingestion Module"
        EIA_CLIENT[EIA Client<br/>eia_client.py]
        FRED_CLIENT[FRED Client<br/>fred_client.py]
        YAHOO_CLIENT[Yahoo Finance Client<br/>yahoo_finance_client.py]
    end

    subgraph "Data Validation Module"
        VALIDATOR[Data Validator<br/>validator.py]
        CONFIG[Validation Config<br/>validation_config.yaml]
    end

    subgraph "Database Module"
        DB_MODELS[Database Models<br/>models.py]
        DB_OPS[Database Operations<br/>operations.py]
        DB_UTILS[Database Utils<br/>utils.py]
    end

    subgraph "Feature Engineering Module"
        INDICATORS[Technical Indicators<br/>indicators.py]
        TIME_FEATURES[Time Features<br/>time_features.py]
        PIPELINE[Feature Pipeline<br/>pipeline.py]
    end

    subgraph "Models Module"
        ARIMA_MODEL[ARIMA Model<br/>arima_model.py]
        PROPHET_MODEL[Prophet Model<br/>prophet_model.py]
        LSTM_MODEL[LSTM Model<br/>lstm_model.py]
    end

    subgraph "Training Module"
        DATA_SPLIT[Data Splitting<br/>data_splitting.py]
        TRAINER[Trainer<br/>trainer.py]
        EVALUATOR[Evaluator<br/>evaluator.py]
    end

    subgraph "MLOps Module"
        MLFLOW_MGR[MLflow Manager<br/>mlflow_manager.py]
        EXP_TRACKER[Experiment Tracker<br/>experiment_tracker.py]
        MODEL_REG[Model Registry<br/>model_registry.py]
    end

    subgraph "API Module"
        MAIN[Main App<br/>main.py]
        ROUTES[Routes<br/>routes/]
        SERVICES[Services<br/>services/]
        AUTH_MOD[Auth Module<br/>auth/]
        CACHE_MOD[Cache Module<br/>cache/]
    end

    subgraph "Backtesting Module"
        WALK_FORWARD[Walk-Forward<br/>walk_forward.py]
        SIMULATOR[Trading Simulator<br/>trading_simulator.py]
        METRICS[Performance Metrics<br/>performance_metrics.py]
    end

    subgraph "Analytics Module"
        CORRELATION[Correlation Analysis<br/>correlation_analysis.py]
        VOLATILITY[Volatility Forecasting<br/>volatility_forecasting.py]
        ANOMALY[Anomaly Detection<br/>anomaly_detection.py]
    end

    EIA_CLIENT --> VALIDATOR
    FRED_CLIENT --> VALIDATOR
    YAHOO_CLIENT --> VALIDATOR
    VALIDATOR --> CONFIG
    VALIDATOR --> DB_OPS
    DB_OPS --> DB_MODELS
    DB_MODELS --> DB_UTILS
    
    DB_OPS --> PIPELINE
    PIPELINE --> INDICATORS
    PIPELINE --> TIME_FEATURES
    
    PIPELINE --> ARIMA_MODEL
    PIPELINE --> PROPHET_MODEL
    PIPELINE --> LSTM_MODEL
    
    ARIMA_MODEL --> DATA_SPLIT
    PROPHET_MODEL --> DATA_SPLIT
    LSTM_MODEL --> DATA_SPLIT
    DATA_SPLIT --> TRAINER
    TRAINER --> EVALUATOR
    
    TRAINER --> MLFLOW_MGR
    EVALUATOR --> EXP_TRACKER
    EXP_TRACKER --> MODEL_REG
    
    MODEL_REG --> SERVICES
    DB_OPS --> SERVICES
    SERVICES --> ROUTES
    ROUTES --> MAIN
    MAIN --> AUTH_MOD
    MAIN --> CACHE_MOD
    
    MODEL_REG --> WALK_FORWARD
    WALK_FORWARD --> SIMULATOR
    SIMULATOR --> METRICS
    
    DB_OPS --> CORRELATION
    DB_OPS --> VOLATILITY
    DB_OPS --> ANOMALY

    style VALIDATOR fill:#fff4e1
    style DB_MODELS fill:#fff4e1
    style MODEL_REG fill:#fff9c4
    style MAIN fill:#e8f5e9
    style METRICS fill:#f3e5f5
```

---

## Module Dependencies

```mermaid
graph LR
    A[Data Ingestion] --> B[Data Validation]
    B --> C[Database]
    C --> D[Feature Engineering]
    D --> E[Models]
    E --> F[Training]
    F --> G[MLOps]
    G --> H[API]
    E --> I[Backtesting]
    C --> J[Analytics]
    H --> K[Frontend]
    I --> K
    J --> K
    
    style A fill:#e1f5ff
    style C fill:#fff4e1
    style G fill:#fff9c4
    style H fill:#e8f5e9
    style K fill:#f3e5f5
```

---

## API Component Structure

```mermaid
graph TB
    subgraph "API Application"
        MAIN_APP[main.py<br/>FastAPI App]
    end
    
    subgraph "Routes"
        FORECAST[forecast.py<br/>Forecast Endpoint]
        HISTORICAL[historical.py<br/>Historical Data]
        MODELS[models.py<br/>Model Info]
        BACKTEST[backtest.py<br/>Backtesting]
        ADMIN[admin.py<br/>API Key Management]
        HEALTH[health.py<br/>Health Checks]
        WEBSOCKET[websocket.py<br/>WebSocket]
    end
    
    subgraph "Services"
        MODEL_SVC[model_service.py<br/>Model Loading]
        BACKTEST_SVC[backtest_service.py<br/>Backtest Logic]
        FORECAST_SVC[forecast_service.py<br/>Forecast Logic]
    end
    
    subgraph "Middleware"
        AUTH_MW[auth/middleware.py<br/>Authentication]
        RATE_LIMIT[cache/rate_limit_middleware.py<br/>Rate Limiting]
        LOGGING[logging_config.py<br/>Request Logging]
    end
    
    subgraph "Models"
        REQ_MODELS[models/*.py<br/>Request/Response Models]
    end
    
    MAIN_APP --> FORECAST
    MAIN_APP --> HISTORICAL
    MAIN_APP --> MODELS
    MAIN_APP --> BACKTEST
    MAIN_APP --> ADMIN
    MAIN_APP --> HEALTH
    MAIN_APP --> WEBSOCKET
    
    FORECAST --> FORECAST_SVC
    BACKTEST --> BACKTEST_SVC
    FORECAST --> MODEL_SVC
    MODELS --> MODEL_SVC
    
    FORECAST --> REQ_MODELS
    BACKTEST --> REQ_MODELS
    
    MAIN_APP --> AUTH_MW
    MAIN_APP --> RATE_LIMIT
    MAIN_APP --> LOGGING

    style MAIN_APP fill:#e8f5e9
    style MODEL_SVC fill:#fff9c4
    style AUTH_MW fill:#fff4e1
```

---

**Last Updated**: December 15, 2025

