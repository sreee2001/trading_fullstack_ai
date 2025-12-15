# Developer Documentation

**Welcome, Developers!**

This documentation provides comprehensive technical details for developers who want to understand, modify, or extend the Energy Price Forecasting System.

---

## 🎯 Overview

This system is a production-ready, full-stack ML platform built with:
- **Python 3.10+** for backend and ML
- **TypeScript/React** for frontend
- **FastAPI** for REST API
- **PostgreSQL + TimescaleDB** for time-series data
- **Docker** for containerization

---

## 📚 Documentation Sections

### Architecture & Design

| Document | Description | Read Time |
|----------|-------------|-----------|
| [System Architecture](architecture/system-overview.md) | High-level system design | 10 min |
| [Component Details](architecture/component-details.md) | Detailed component breakdown | 15 min |
| [Data Flow](architecture/data-flow.md) | Complete data flow architecture | 10 min |
| [Deployment Architecture](architecture/deployment-architecture.md) | Infrastructure and deployment | 10 min |

### Module Documentation

| Module | Documentation | Key Files |
|--------|---------------|-----------|
| [Data Ingestion](modules/data-ingestion/README.md) | EIA, FRED, Yahoo Finance clients | `eia_client.py`, `fred_client.py` |
| [Data Validation](modules/data-validation/README.md) | Data quality framework | `validator.py` |
| [Database](modules/database/README.md) | PostgreSQL + TimescaleDB | `models.py`, `operations.py` |
| [Feature Engineering](modules/feature-engineering/README.md) | Technical indicators, features | `pipeline.py`, `indicators.py` |
| [Models](modules/models/README.md) | ML model implementations | `arima_model.py`, `lstm_model.py` |
| [Training](modules/training/README.md) | Model training infrastructure | `trainer.py`, `evaluator.py` |
| [API](modules/api/README.md) | FastAPI application | `main.py`, `routes/`, `services/` |
| [Backtesting](modules/backtesting/README.md) | Trading simulation | `trading_simulator.py`, `walk_forward.py` |
| [Analytics](modules/analytics/README.md) | Advanced analytics | `correlation_analysis.py`, `volatility_forecasting.py` |
| [Dashboard](modules/dashboard/README.md) | React frontend | `src/`, components, hooks |
| [Streamlit Dashboard](modules/streamlit/README.md) | Streamlit interface | `app.py` |

### Testing & Quality

| Document | Description |
|----------|-------------|
| [Test Strategy](testing/test-strategy.md) | Testing approach and coverage |
| [Test Cases](testing/test-cases.md) | Comprehensive test case reference |
| [Test Execution](testing/test-execution.md) | How to run tests |

### Workflows & Processes

| Document | Description |
|----------|-------------|
| [Data Pipeline Workflow](workflows/data-pipeline.md) | Data ingestion and processing |
| [Model Training Workflow](workflows/model-training.md) | Model development process |
| [Forecast Generation Workflow](workflows/forecast-generation.md) | API request processing |
| [Backtesting Workflow](workflows/backtesting.md) | Backtest execution flow |

### Contributing

| Document | Description |
|----------|-------------|
| [Contributing Guide](contributing.md) | How to contribute to the project |
| [Development Setup](contributing.md#development-setup) | Local development environment |
| [Code Standards](contributing.md#code-standards) | Coding conventions |
| [Pull Request Process](contributing.md#pull-request-process) | PR guidelines |

---

## 🚀 Quick Start for Developers

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/trading_fullstack_ai.git
cd trading_fullstack_ai/src/energy-price-forecasting

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Services

```bash
# Start database and Redis
docker compose up -d timescaledb redis

# Run API
uvicorn api.main:app --reload

# Run frontend (separate terminal)
cd dashboard
npm install
npm run dev
```

### 3. Run Tests

```bash
# All tests
pytest

# Specific module
pytest tests/test_api_*.py

# With coverage
pytest --cov=. --cov-report=html
```

---

## 📖 Key Concepts

### Architecture Patterns

- **Layered Architecture**: Clear separation of data, ML, API, and presentation
- **Dependency Injection**: Services injected via factories
- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic encapsulation

### Design Principles

- **SOLID Principles**: Applied throughout codebase
- **DRY**: No code duplication
- **Separation of Concerns**: Each module has single responsibility
- **Testability**: All code designed for testing

---

## 🔧 Development Tools

### Required Tools

- **Python 3.10+**: Backend development
- **Node.js 18+**: Frontend development
- **Docker Desktop**: Containerization
- **PostgreSQL**: Database (via Docker)
- **Git**: Version control

### Recommended Tools

- **VS Code**: Code editor with Python/TypeScript extensions
- **Postman**: API testing
- **pgAdmin**: Database management
- **MLflow UI**: Model tracking

---

## 📝 Code Organization

```
src/energy-price-forecasting/
├── data_ingestion/      # Data source clients
├── data_validation/     # Quality framework
├── database/            # Database layer
├── feature_engineering/ # Feature creation
├── models/              # ML model implementations
├── training/            # Training infrastructure
├── evaluation/          # Model evaluation
├── backtesting/         # Trading simulation
├── analytics/           # Advanced analytics
├── api/                 # FastAPI application
├── dashboard/           # React frontend
├── dashboard-streamlit/ # Streamlit dashboard
└── tests/              # Test suite
```

---

## 🧪 Testing

### Test Structure

- **Unit Tests**: Individual functions/classes
- **Integration Tests**: Component interactions
- **E2E Tests**: Full workflow testing
- **Performance Tests**: Load and stress testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=term-missing

# Specific test file
pytest tests/test_api_main.py

# Watch mode
pytest-watch
```

---

## 📦 Module Details

Each module has detailed documentation covering:
- **Purpose**: What the module does
- **File Structure**: Key files and their roles
- **Key Classes**: Main classes and their methods
- **Usage Examples**: Code examples
- **Testing**: How to test the module
- **Dependencies**: What it depends on

See [Module Documentation](modules/) for details.

---

## 🔄 Workflows

Detailed workflow documentation includes:
- **Sequence Diagrams**: Step-by-step flows
- **State Diagrams**: State transitions
- **Code References**: Where to find implementation
- **Error Handling**: How errors are handled

See [Workflow Documentation](workflows/) for details.

---

## 🛠️ Common Development Tasks

### Adding a New Model

1. Create model class in `models/`
2. Implement `fit()` and `predict()` methods
3. Add to training pipeline
4. Register in model service
5. Add tests

### Adding a New API Endpoint

1. Create route in `api/routes/`
2. Define request/response models
3. Implement service logic
4. Add authentication
5. Add tests
6. Update Swagger docs

### Adding a New Data Source

1. Create client in `data_ingestion/`
2. Implement fetch methods
3. Add to pipeline orchestrator
4. Add validation rules
5. Add tests

---

## 📚 Additional Resources

- **Architecture Diagrams**: [Diagrams](../diagrams/architecture/)
- **Workflow Diagrams**: [Workflows](../diagrams/workflows/)
- **API Documentation**: http://localhost:8000/api/docs
- **Test Cases**: [Test Cases](../test-cases/)

---

## 🆘 Getting Help

- **Code Issues**: Check module documentation
- **Architecture Questions**: See [Architecture Docs](architecture/)
- **Testing Issues**: See [Testing Docs](testing/)
- **Workflow Questions**: See [Workflow Docs](workflows/)

---

**Last Updated**: December 15, 2025

