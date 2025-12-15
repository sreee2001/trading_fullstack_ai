# Energy Price Forecasting System - System Architecture

**Version**: 2.0  
**Last Updated**: December 15, 2025  
**Status**: Epic 1-7 Complete

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Deployment Architecture](#deployment-architecture)
7. [Security Architecture](#security-architecture)
8. [Scalability Considerations](#scalability-considerations)

---

## Overview

The Energy Price Forecasting System is a production-ready, full-stack machine learning platform for forecasting energy commodity prices (WTI, Brent, Natural Gas). The system follows a microservices-oriented architecture with clear separation of concerns across data ingestion, ML processing, API services, and frontend visualization.

### Key Architectural Principles

- **Separation of Concerns**: Clear boundaries between data, ML, API, and presentation layers
- **Modularity**: Independent, reusable components
- **Scalability**: Horizontal scaling capabilities
- **Observability**: Comprehensive logging, monitoring, and tracking
- **Testability**: Unit, integration, and E2E test coverage
- **Maintainability**: Clean code, documentation, and version control

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENERGY PRICE FORECASTING SYSTEM                  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│  Data Layer  │          │   ML Layer   │          │  API Layer   │
│              │          │              │          │              │
│ • Ingestion  │─────────▶│ • Training   │─────────▶│ • FastAPI    │
│ • Validation │          │ • Inference  │          │ • Auth       │
│ • Storage    │          │ • Tracking   │          │ • Rate Limit │
│ • Pipeline   │          │ • Registry  │          │ • Caching    │
└──────────────┘          └──────────────┘          └──────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│ Backtesting  │          │  Analytics   │          │  Frontend    │
│              │          │              │          │              │
│ • Simulation │          │ • Correlation│          │ • React      │
│ • Metrics    │          │ • Seasonality│          │ • Charts     │
│ • Signals    │          │ • Volatility │          │ • Dashboard  │
│ • Risk       │          │ • Anomalies  │          │              │
└──────────────┘          └──────────────┘          └──────────────┘
```

### Layer Responsibilities

#### 1. Data Layer
- **Purpose**: Data ingestion, validation, and storage
- **Components**:
  - Data ingestion clients (EIA, FRED, Yahoo Finance)
  - Data validation framework
  - PostgreSQL + TimescaleDB database
  - Automated pipeline orchestration
- **Key Features**:
  - Multi-source data collection
  - Data quality validation (98%+ quality target)
  - Time-series optimized storage
  - Automated scheduling and monitoring

#### 2. ML Layer
- **Purpose**: Model training, inference, and management
- **Components**:
  - Feature engineering pipeline
  - Model implementations (ARIMA, Prophet, LSTM)
  - Training infrastructure
  - Hyperparameter tuning framework
  - MLflow experiment tracking
  - Model registry
- **Key Features**:
  - Multi-model support
  - Automated training pipelines
  - Model versioning and tracking
  - A/B testing framework
  - Performance monitoring

#### 3. API Layer
- **Purpose**: RESTful API service for model access
- **Components**:
  - FastAPI application
  - Authentication (API keys)
  - Rate limiting (Redis)
  - Response caching
  - Endpoint routing
- **Key Features**:
  - Forecast endpoints
  - Historical data endpoints
  - Backtesting endpoints
  - Model information endpoints
  - Health checks

#### 4. Backtesting Layer
- **Purpose**: Model evaluation and trading simulation
- **Components**:
  - Walk-forward validation
  - Trading signal generation
  - Simulation engine
  - Risk metrics calculation
  - Performance visualization
- **Key Features**:
  - Multiple validation strategies
  - Trading signal strategies
  - P&L tracking
  - Risk-adjusted metrics
  - Model comparison

#### 5. Analytics Layer
- **Purpose**: Advanced analytics and insights
- **Components**:
  - Correlation analysis
  - Seasonality detection
  - Volatility forecasting
  - Anomaly detection
  - Market regime detection
  - Feature importance analysis
  - Insight generation
- **Key Features**:
  - Statistical analysis
  - ML-based detection
  - Automated insights
  - Visualization support

#### 6. Frontend Layer
- **Purpose**: User interface and visualization
- **Components**:
  - React application
  - Chart components (Recharts)
  - Dashboard pages
  - API integration
- **Key Features**:
  - Forecast visualization
  - Historical data charts
  - Backtest results display
  - Model comparison views
  - Export functionality

---

## Component Architecture

### Data Ingestion Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Ingestion Layer                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  EIA Client  │  │ FRED Client  │  │ Yahoo Client │      │
│  │              │  │              │  │              │      │
│  │ • API v2     │  │ • API v1     │  │ • yfinance   │      │
│  │ • Retry      │  │ • Retry      │  │ • Historical  │      │
│  │ • Normalize  │  │ • Normalize  │  │ • Real-time  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                            ▼                                 │
│                  ┌──────────────────┐                         │
│                  │ Data Validator   │                         │
│                  │                  │                         │
│                  │ • Rules Engine  │                         │
│                  │ • Quality Checks│                         │
│                  │ • Error Handling│                         │
│                  └────────┬─────────┘                         │
│                           │                                   │
│                           ▼                                   │
│                  ┌──────────────────┐                         │
│                  │  Database        │                         │
│                  │  (PostgreSQL +   │                         │
│                  │   TimescaleDB)   │                         │
│                  └──────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### ML Components

```
┌─────────────────────────────────────────────────────────────┐
│                      ML Layer                                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Feature Engineering Pipeline                 │    │
│  │  • Technical Indicators  • Lag Features              │    │
│  │  • Time Features        • Seasonal Decomposition     │    │
│  └──────────────────┬──────────────────────────────────┘    │
│                     │                                         │
│         ┌───────────┼───────────┐                            │
│         │           │           │                            │
│         ▼           ▼           ▼                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                    │
│  │  ARIMA   │ │  Prophet  │ │   LSTM   │                    │
│  │  Model   │ │  Model    │ │  Model   │                    │
│  └────┬─────┘ └────┬──────┘ └────┬─────┘                    │
│       │            │              │                            │
│       └────────────┼──────────────┘                            │
│                    │                                           │
│                    ▼                                           │
│         ┌──────────────────────┐                              │
│         │   MLflow Tracking    │                              │
│         │   • Experiments      │                              │
│         │   • Model Registry   │                              │
│         │   • Artifacts        │                              │
│         └──────────────────────┘                              │
│                    │                                           │
│                    ▼                                           │
│         ┌──────────────────────┐                              │
│         │  Hyperparameter      │                              │
│         │  Tuning              │                              │
│         │  • Grid Search       │                              │
│         │  • Random Search     │                              │
│         │  • Bayesian (Optuna) │                              │
│         └──────────────────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

### API Components

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              FastAPI Application                     │    │
│  │                                                       │    │
│  │  ┌──────────────┐  ┌──────────────┐                │    │
│  │  │  Middleware   │  │   Routes     │                │    │
│  │  │              │  │              │                │    │
│  │  │ • CORS       │  │ • Forecast   │                │    │
│  │  │ • Logging    │  │ • Historical │                │    │
│  │  │ • Rate Limit │  │ • Backtest   │                │    │
│  │  │ • Auth       │  │ • Models     │                │    │
│  │  └──────────────┘  └──────────────┘                │    │
│  └─────────────────────────────────────────────────────┘    │
│                     │                                         │
│         ┌───────────┼───────────┐                            │
│         │           │           │                            │
│         ▼           ▼           ▼                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                    │
│  │   Auth   │ │   Rate    │ │  Cache   │                    │
│  │  Service │ │  Limiter  │ │ (Redis)  │                    │
│  │          │ │  (Redis)  │ │          │                    │
│  └──────────┘ └──────────┘ └──────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Forecast Request Flow

```
User Request
    │
    ▼
FastAPI Endpoint
    │
    ▼
Authentication Check (API Key)
    │
    ▼
Rate Limiting Check (Redis)
    │
    ▼
Cache Check (Redis)
    │
    ├─── Cache Hit ───▶ Return Cached Response
    │
    └─── Cache Miss ───▶
            │
            ▼
    Load Model (MLflow Registry)
            │
            ▼
    Fetch Historical Data (Database)
            │
            ▼
    Feature Engineering
            │
            ▼
    Model Inference
            │
            ▼
    Cache Result (Redis)
            │
            ▼
    Return Forecast Response
```

### Training Pipeline Flow

```
Scheduled Trigger / Manual Trigger
    │
    ▼
Data Ingestion (EIA, FRED, Yahoo)
    │
    ▼
Data Validation
    │
    ▼
Data Storage (Database)
    │
    ▼
Feature Engineering
    │
    ▼
Data Splitting (Train/Validation/Test)
    │
    ▼
Model Training
    │
    ▼
Hyperparameter Tuning (Optional)
    │
    ▼
Model Evaluation
    │
    ▼
MLflow Logging (Metrics, Artifacts)
    │
    ▼
Model Validation Gates
    │
    ├─── Pass ───▶ Model Registration (MLflow)
    │                    │
    │                    ▼
    │            A/B Testing Setup
    │
    └─── Fail ───▶ Alert & Log Failure
```

---

## Technology Stack

### Backend
- **Language**: Python 3.13
- **Framework**: FastAPI 0.108.0
- **Database**: PostgreSQL 15+ with TimescaleDB extension
- **Cache**: Redis 5.0+
- **ML Framework**: TensorFlow/Keras, scikit-learn, statsmodels
- **Time Series**: pmdarima, Prophet
- **MLOps**: MLflow 2.9.2
- **Hyperparameter Tuning**: Optuna 3.5+

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Routing**: React Router

### DevOps
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **Code Quality**: flake8, TypeScript compiler

### Infrastructure
- **Database**: PostgreSQL + TimescaleDB
- **Cache**: Redis
- **Web Server**: Nginx (for frontend)
- **API Server**: Uvicorn (ASGI)

---

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────────────────────────────┐
│              Docker Compose (Local Development)               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │   FastAPI    │      │
│  │  :5432       │  │    :6379     │  │    :8000     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐                                           │
│  │   React      │                                           │
│  │   :3000      │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

### Production Environment

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Deployment                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │   FastAPI    │      │
│  │  (Primary)    │  │  (Cluster)   │  │  (Multiple    │      │
│  │              │  │              │  │   Instances)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                            ▼                                 │
│                  ┌──────────────────┐                         │
│                  │   Load Balancer │                         │
│                  │   (Nginx)       │                         │
│                  └────────┬─────────┘                         │
│                           │                                   │
│                           ▼                                   │
│                  ┌──────────────────┐                         │
│                  │   CDN / Edge    │                         │
│                  │   (Frontend)     │                         │
│                  └──────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Architecture

### Authentication & Authorization

- **API Key Authentication**: Bcrypt hashed API keys stored in database
- **Rate Limiting**: Per-API-key rate limits enforced via Redis
- **CORS**: Configured for specific origins
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries

### Data Security

- **Database Credentials**: Environment variables, never hardcoded
- **API Keys**: Encrypted storage, secure transmission
- **Logging**: Sensitive data excluded from logs
- **HTTPS**: Required in production (via reverse proxy)

---

## Scalability Considerations

### Horizontal Scaling

- **API Layer**: Stateless FastAPI instances can scale horizontally
- **Database**: Read replicas for read-heavy workloads
- **Cache**: Redis cluster for distributed caching
- **ML Inference**: Model serving can be separated into dedicated services

### Performance Optimizations

- **Caching**: Redis caching for frequently accessed data
- **Database Indexing**: Optimized indexes on time-series tables
- **Connection Pooling**: SQLAlchemy connection pooling
- **Async Operations**: FastAPI async endpoints for I/O-bound operations
- **Batch Processing**: Batch inference for multiple forecasts

### Monitoring & Observability

- **Logging**: Structured logging throughout the application
- **Metrics**: MLflow tracking for model performance
- **Health Checks**: Endpoint health monitoring
- **Alerting**: Automated alerts for failures and performance degradation

---

## Future Enhancements

1. **Microservices Migration**: Split into separate services (data, ML, API)
2. **Message Queue**: Add message queue (RabbitMQ/Kafka) for async processing
3. **Model Serving**: Dedicated model serving service (TensorFlow Serving)
4. **Real-time Streaming**: WebSocket support for real-time forecasts
5. **Multi-region Deployment**: Geographic distribution for low latency

---

**Document Version**: 2.0  
**Last Updated**: December 15, 2025  
**Maintained By**: Development Team

