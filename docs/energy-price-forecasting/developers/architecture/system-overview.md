# System Architecture Overview

**Purpose**: High-level system architecture and design principles

---

## Architecture Diagram

See [System Architecture Diagram](../../diagrams/architecture/system-architecture.md) for visual representation.

---

## System Layers

### 1. Data Layer

**Purpose**: Data ingestion, validation, and storage

**Components**:
- **Data Ingestion**: EIA, FRED, Yahoo Finance clients
- **Data Validation**: Quality framework (98%+ target)
- **Database**: PostgreSQL + TimescaleDB
- **Pipeline**: Automated orchestration

**Key Files**:
- `data_ingestion/`: API clients
- `data_validation/`: Validation framework
- `database/`: Database layer
- `data_pipeline/`: Pipeline orchestration

---

### 2. ML Layer

**Purpose**: Model training, inference, and management

**Components**:
- **Feature Engineering**: Technical indicators, lag features
- **Models**: ARIMA, Prophet, LSTM
- **Training**: Training infrastructure
- **MLflow**: Experiment tracking and registry

**Key Files**:
- `feature_engineering/`: Feature creation
- `models/`: Model implementations
- `training/`: Training pipeline
- `mlflow_tracking/`: MLflow integration

---

### 3. API Layer

**Purpose**: RESTful API service

**Components**:
- **FastAPI**: Web framework
- **Authentication**: API key management
- **Caching**: Redis caching
- **Rate Limiting**: Request throttling

**Key Files**:
- `api/main.py`: Application entry point
- `api/routes/`: API endpoints
- `api/services/`: Business logic
- `api/auth/`: Authentication

---

### 4. Frontend Layer

**Purpose**: User interfaces

**Components**:
- **React Dashboard**: Modern web interface
- **Streamlit Dashboard**: Python interface
- **Charts**: Interactive visualizations

**Key Files**:
- `dashboard/`: React application
- `dashboard-streamlit/`: Streamlit application

---

### 5. Analytics Layer

**Purpose**: Advanced market analysis

**Components**:
- **Correlation Analysis**: Commodity relationships
- **Volatility Forecasting**: Risk estimation
- **Anomaly Detection**: Unusual patterns
- **Seasonality**: Cyclical patterns

**Key Files**:
- `analytics/`: Analytics modules

---

## Design Principles

### Separation of Concerns

Each layer has a single, well-defined responsibility:
- **Data Layer**: Data management only
- **ML Layer**: Model logic only
- **API Layer**: Request handling only
- **Frontend Layer**: Presentation only

### Dependency Injection

Services are injected via factories:
```python
from api.services.model_service import get_model_service

model_service = get_model_service()
model = model_service.load_model(commodity="WTI")
```

### Repository Pattern

Data access is abstracted:
```python
from database.operations import get_price_data

data = get_price_data(commodity="WTI", start_date="2024-01-01")
```

---

## Technology Stack

### Backend
- **Python 3.10+**: Core language
- **FastAPI**: Web framework
- **PostgreSQL + TimescaleDB**: Database
- **Redis**: Caching
- **MLflow**: Model tracking

### ML
- **PyTorch/TensorFlow**: Deep learning
- **scikit-learn**: Traditional ML
- **Statsmodels**: Statistical models
- **Prophet**: Facebook's tool

### Frontend
- **React + TypeScript**: Web framework
- **Streamlit**: Python dashboard
- **Recharts/Plotly**: Visualizations

### DevOps
- **Docker**: Containerization
- **GitHub Actions**: CI/CD
- **pytest**: Testing

---

## Data Flow

1. **Ingestion**: External APIs → Data Clients
2. **Validation**: Data Clients → Validator
3. **Storage**: Validator → Database
4. **Feature Engineering**: Database → Feature Pipeline
5. **Training**: Features → Models
6. **Inference**: Models → API
7. **Presentation**: API → Frontend

See [Data Flow Architecture](../../diagrams/architecture/data-flow-architecture.md) for details.

---

## Scalability Considerations

### Horizontal Scaling
- **API**: Multiple FastAPI instances behind load balancer
- **Database**: Read replicas for queries
- **Cache**: Redis cluster

### Vertical Scaling
- **Database**: TimescaleDB hypertables for partitioning
- **ML**: GPU support for LSTM training
- **Cache**: Redis memory optimization

---

## Security Architecture

### Authentication
- **API Keys**: Per-application keys
- **Key Management**: Secure storage and rotation
- **Rate Limiting**: Per-key limits

### Data Security
- **Encryption**: Data at rest and in transit
- **Access Control**: Database user permissions
- **API Security**: HTTPS, CORS, input validation

---

## Monitoring & Observability

### Logging
- **Structured Logging**: JSON format
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Log Aggregation**: Centralized logging

### Metrics
- **API Metrics**: Request rate, latency, errors
- **Model Metrics**: Prediction accuracy, latency
- **System Metrics**: CPU, memory, disk

### Health Checks
- **API Health**: `/health` endpoint
- **Database Health**: Connection checks
- **Service Health**: Dependency checks

---

## Deployment Architecture

See [Deployment Architecture](../../diagrams/architecture/deployment-architecture.md) for details.

### Development
- **Docker Compose**: Local development
- **Hot Reload**: Fast iteration

### Production
- **Kubernetes**: Container orchestration (optional)
- **Load Balancer**: Nginx/Cloud LB
- **Database**: Managed PostgreSQL
- **Cache**: Managed Redis

---

## Extension Points

### Adding New Data Source
1. Create client in `data_ingestion/`
2. Add to pipeline orchestrator
3. Add validation rules

### Adding New Model
1. Create model in `models/`
2. Add to training pipeline
3. Register in model service

### Adding New Endpoint
1. Create route in `api/routes/`
2. Add service logic
3. Add request/response models

---

**Last Updated**: December 15, 2025

