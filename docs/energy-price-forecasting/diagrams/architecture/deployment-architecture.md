# Deployment Architecture Diagram

**Version**: 1.0  
**Date**: December 15, 2025  
**Status**: ✅ Complete

---

## Docker Compose Deployment

```mermaid
graph TB
    subgraph "Docker Network: energy_forecasting_network"
        subgraph "Database Services"
            TIMESCALE[TimescaleDB Container<br/>Port: 5432<br/>Volume: timescale_data]
        end
        
        subgraph "Cache Services"
            REDIS[Redis Container<br/>Port: 6379<br/>Volume: redis_data]
        end
        
        subgraph "Application Services"
            API[FastAPI Container<br/>Port: 8000<br/>Depends: TimescaleDB, Redis]
            FRONTEND[React Frontend Container<br/>Port: 3000<br/>Depends: API]
        end
    end
    
    subgraph "External"
        USER[Users/Browsers]
        EIA_API[EIA API]
        FRED_API[FRED API]
        YAHOO_API[Yahoo Finance]
    end
    
    USER --> FRONTEND
    USER --> API
    API --> TIMESCALE
    API --> REDIS
    API --> EIA_API
    API --> FRED_API
    API --> YAHOO_API
    
    style TIMESCALE fill:#fff4e1
    style REDIS fill:#fff4e1
    style API fill:#e8f5e9
    style FRONTEND fill:#f3e5f5
```

---

## Production Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx/Cloud Load Balancer]
    end
    
    subgraph "Application Tier"
        API1[FastAPI Instance 1]
        API2[FastAPI Instance 2]
        API3[FastAPI Instance N]
    end
    
    subgraph "Database Tier"
        DB_PRIMARY[(PostgreSQL Primary)]
        DB_REPLICA[(PostgreSQL Replica)]
    end
    
    subgraph "Cache Tier"
        REDIS_CLUSTER[Redis Cluster]
    end
    
    subgraph "Storage Tier"
        MLFLOW_STORE[MLflow Artifact Store<br/>S3/GCS]
        MODEL_STORAGE[Model Storage<br/>S3/GCS]
    end
    
    subgraph "Monitoring"
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana]
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> DB_PRIMARY
    API2 --> DB_PRIMARY
    API3 --> DB_PRIMARY
    DB_PRIMARY --> DB_REPLICA
    
    API1 --> REDIS_CLUSTER
    API2 --> REDIS_CLUSTER
    API3 --> REDIS_CLUSTER
    
    API1 --> MLFLOW_STORE
    API2 --> MLFLOW_STORE
    API3 --> MLFLOW_STORE
    
    API1 --> MODEL_STORAGE
    API2 --> MODEL_STORAGE
    API3 --> MODEL_STORAGE
    
    API1 --> PROMETHEUS
    API2 --> PROMETHEUS
    API3 --> PROMETHEUS
    PROMETHEUS --> GRAFANA
    
    style LB fill:#e8f5e9
    style DB_PRIMARY fill:#fff4e1
    style REDIS_CLUSTER fill:#fff4e1
    style MLFLOW_STORE fill:#fff9c4
    style PROMETHEUS fill:#f3e5f5
```

---

## CI/CD Pipeline Architecture

```mermaid
flowchart LR
    DEV[Developer] --> GIT[Git Commit]
    GIT --> GITHUB[GitHub Repository]
    GITHUB --> TRIGGER[GitHub Actions Trigger]
    
    TRIGGER --> TEST[Run Tests]
    TEST --> LINT[Lint Code]
    LINT --> BUILD[Build Docker Images]
    BUILD --> SECURITY[Security Scan]
    SECURITY --> PUSH[Push to Registry]
    
    PUSH --> STAGING[Deploy to Staging]
    STAGING --> E2E[E2E Tests]
    E2E --> APPROVAL{Manual Approval}
    
    APPROVAL -->|Approve| PROD[Deploy to Production]
    APPROVAL -->|Reject| ROLLBACK[Rollback]
    
    PROD --> MONITOR[Monitor]
    MONITOR --> ALERT[Alert on Issues]
    
    style TEST fill:#e8f5e9
    style BUILD fill:#fff9c4
    style PROD fill:#e1f5ff
    style MONITOR fill:#f3e5f5
```

---

## Service Communication

```mermaid
graph LR
    subgraph "Frontend Services"
        REACT[React App<br/>Port 3000]
        STREAMLIT[Streamlit App<br/>Port 8501]
    end
    
    subgraph "API Services"
        REST[REST API<br/>Port 8000]
        WS[WebSocket<br/>Port 8000/ws]
    end
    
    subgraph "Data Services"
        DB[(PostgreSQL<br/>Port 5432)]
        REDIS[Redis<br/>Port 6379]
    end
    
    subgraph "ML Services"
        MLFLOW[MLflow Server<br/>Port 5000]
        TRAINING[Training Jobs<br/>Scheduled]
    end
    
    REACT --> REST
    REACT --> WS
    STREAMLIT --> REST
    REST --> DB
    REST --> REDIS
    WS --> DB
    TRAINING --> MLFLOW
    REST --> MLFLOW
    
    style REACT fill:#f3e5f5
    style REST fill:#e8f5e9
    style DB fill:#fff4e1
    style MLFLOW fill:#fff9c4
```

---

**Last Updated**: December 15, 2025

