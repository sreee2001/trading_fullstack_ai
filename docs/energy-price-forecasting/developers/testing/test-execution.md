# Test Execution Guide

**Purpose**: How to run and execute tests in the Energy Price Forecasting System

---

## Prerequisites

### Required Tools

- **Python 3.10+**: Python interpreter
- **pytest**: Testing framework
- **pytest-cov**: Coverage plugin
- **Docker**: For integration tests (optional)

### Installation

```bash
pip install pytest pytest-cov pytest-asyncio
```

---

## Running Tests

### All Tests

```bash
# From project root
pytest

# From src/energy-price-forecasting
cd src/energy-price-forecasting
pytest
```

### Specific Test File

```bash
pytest tests/test_eia_client.py
```

### Specific Test Function

```bash
pytest tests/test_eia_client.py::test_fetch_wti_prices
```

### Tests Matching Pattern

```bash
pytest tests/test_api_*.py
```

---

## Test Output

### Verbose Output

```bash
pytest -v
```

### Very Verbose Output

```bash
pytest -vv
```

### Show Print Statements

```bash
pytest -s
```

---

## Coverage Reports

### Terminal Coverage

```bash
pytest --cov=. --cov-report=term-missing
```

### HTML Coverage Report

```bash
pytest --cov=. --cov-report=html
```

**View Report**: Open `htmlcov/index.html` in browser

### XML Coverage Report

```bash
pytest --cov=. --cov-report=xml
```

---

## Test Categories

### Run by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow
```

### Skip Tests

```bash
# Skip slow tests
pytest -m "not slow"
```

---

## Test Configuration

### pytest.ini

**Location**: `src/energy-price-forecasting/pytest.ini`

**Configuration**:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

---

## Test Fixtures

### Using Fixtures

```python
def test_example(db_session):
    # db_session is a fixture
    result = db_session.query(Model).all()
    assert len(result) > 0
```

### Custom Fixtures

**Location**: `tests/conftest.py`

**Example**:
```python
@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100),
        'price': [70 + i*0.1 for i in range(100)]
    })
```

---

## Integration Tests

### Database Setup

```bash
# Start test database
docker compose up -d timescaledb

# Run integration tests
pytest tests/test_database_*.py -m integration
```

### API Tests

```bash
# Start API server
uvicorn api.main:app --reload

# Run API tests
pytest tests/test_api_*.py
```

---

## Continuous Integration

### GitHub Actions

Tests run automatically on:
- Push to main branch
- Pull requests
- Scheduled runs

**View Results**: GitHub Actions tab

---

## Debugging Tests

### Run with Debugger

```bash
pytest --pdb
```

### Print Debug Info

```python
def test_example():
    import pdb; pdb.set_trace()
    # Test code
```

### Verbose Output

```bash
pytest -vv -s
```

---

## Test Performance

### Parallel Execution

```bash
pip install pytest-xdist
pytest -n auto
```

### Test Timing

```bash
pytest --durations=10
```

---

## Best Practices

1. **Run Tests Frequently**: Run tests before committing
2. **Fix Failing Tests**: Don't commit with failing tests
3. **Maintain Coverage**: Keep coverage above 85%
4. **Fast Tests**: Keep unit tests fast
5. **Clear Output**: Use descriptive test names

---

## Troubleshooting

### Tests Not Found

```bash
# Check test discovery
pytest --collect-only
```

### Import Errors

```bash
# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Database Connection Errors

```bash
# Check database is running
docker ps | grep timescaledb
```

---

**Last Updated**: December 15, 2025

