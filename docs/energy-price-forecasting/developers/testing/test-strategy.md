# Test Strategy

**Purpose**: Comprehensive testing approach for the Energy Price Forecasting System

---

## Overview

The system uses a multi-layered testing strategy covering unit tests, integration tests, end-to-end tests, and manual test cases. The goal is to maintain 85%+ code coverage with 100% coverage for critical paths.

---

## Testing Pyramid

```
        /\
       /  \
      / E2E \        (10%)
     /--------\
    /          \
   / Integration \  (30%)
  /--------------\
 /                \
/   Unit Tests      \  (60%)
\--------------------
```

### Unit Tests (60%)

**Purpose**: Test individual functions and classes in isolation

**Coverage**:
- All data ingestion clients
- All model implementations
- All database operations
- All utility functions
- All API routes and services

**Tools**: `pytest`

**Example**:
```python
def test_eia_client_fetch_wti():
    client = EIAAPIClient(api_key="test_key")
    data = client.fetch_wti_prices("2024-01-01", "2024-01-31")
    assert len(data) > 0
    assert "date" in data.columns
```

---

### Integration Tests (30%)

**Purpose**: Test component interactions

**Coverage**:
- Data pipeline end-to-end
- Model training pipeline
- API endpoint workflows
- Database operations with real database
- Cache operations with Redis

**Tools**: `pytest` with test fixtures

**Example**:
```python
def test_forecast_endpoint_integration(client, api_key):
    response = client.post(
        "/api/v1/forecast",
        json={"commodity": "WTI", "horizon": 7},
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    assert "predictions" in response.json()
```

---

### End-to-End Tests (10%)

**Purpose**: Test complete user workflows

**Coverage**:
- Full forecast generation workflow
- Complete backtest execution
- Data ingestion to forecast pipeline
- Model training to deployment pipeline

**Tools**: `pytest` with test database

**Example**:
```python
def test_full_forecast_workflow():
    # Ingest data
    pipeline.run()
    # Train model
    train_model("WTI", "lstm")
    # Generate forecast
    forecast = generate_forecast("WTI", 7)
    assert len(forecast.predictions) == 7
```

---

## Test Organization

### Test Structure

```
tests/
├── test_data_ingestion/    # Data ingestion tests
├── test_database/          # Database tests
├── test_models/            # Model tests
├── test_api/               # API tests
├── test_backtesting/       # Backtesting tests
├── test_analytics/         # Analytics tests
└── fixtures/               # Test fixtures
```

---

## Test Coverage Targets

| Module | Target Coverage | Critical Paths |
|--------|----------------|----------------|
| Data Ingestion | 90%+ | 100% |
| Database | 95%+ | 100% |
| Models | 85%+ | 100% |
| API | 90%+ | 100% |
| Backtesting | 85%+ | 100% |
| Analytics | 80%+ | 100% |
| **Overall** | **85%+** | **100%** |

---

## Testing Tools

### pytest

**Primary Testing Framework**

**Features**:
- Fixtures for test setup
- Parametrized tests
- Test discovery
- Coverage reporting

**Configuration**: `pytest.ini`

---

### Coverage Tools

**pytest-cov**: Coverage reporting

**Usage**:
```bash
pytest --cov=. --cov-report=html
```

---

## Test Data Management

### Fixtures

**Purpose**: Reusable test data and setup

**Location**: `tests/fixtures/`

**Types**:
- Database fixtures
- API client fixtures
- Model fixtures
- Data fixtures

---

### Mock Data

**Purpose**: Simulate external dependencies

**Usage**:
- Mock API responses
- Mock database queries
- Mock file operations

---

## Continuous Integration

### GitHub Actions

**Workflow**:
1. Run unit tests
2. Run integration tests
3. Check coverage
4. Run linters
5. Build Docker images

**Triggers**:
- Push to main
- Pull requests
- Scheduled runs

---

## Manual Testing

### Test Cases

**Location**: `docs/energy-price-forecasting/test-cases/`

**Coverage**:
- Epic 1: 42 test cases
- Epic 2: 43 test cases
- Epic 3 & 4: 89 test cases
- WebSocket: 10 test cases
- Streamlit: 18 test cases

**Purpose**: User acceptance testing and edge cases

---

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Fast Tests**: Unit tests should run quickly
3. **Clear Names**: Test names should describe what they test
4. **Arrange-Act-Assert**: Follow AAA pattern
5. **Test Data**: Use realistic test data
6. **Edge Cases**: Test boundary conditions
7. **Error Cases**: Test error handling

---

## Running Tests

### All Tests

```bash
pytest
```

### Specific Module

```bash
pytest tests/test_api_*.py
```

### With Coverage

```bash
pytest --cov=. --cov-report=term-missing
```

### Watch Mode

```bash
pytest-watch
```

---

## Test Maintenance

### Regular Updates

- Update tests when code changes
- Add tests for new features
- Remove obsolete tests
- Refactor test code

### Coverage Monitoring

- Track coverage trends
- Set coverage gates in CI
- Review uncovered code
- Add tests for critical paths

---

**Last Updated**: December 15, 2025

