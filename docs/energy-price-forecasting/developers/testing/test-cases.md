# Test Cases Reference

**Purpose**: Comprehensive reference for all test cases in the system

---

## Overview

This document provides a reference to all test cases organized by module and feature. For detailed test case descriptions, see the individual test case documents.

---

## Test Case Documents

### Epic Test Cases

- **[Epic 1 Test Cases](../test-cases/EPIC-1-MANUAL-TEST-CASES.md)** - 42 test cases
  - Data ingestion (EIA, FRED, Yahoo Finance)
  - Database operations
  - Data validation
  - Pipeline orchestration

- **[Epic 2 Test Cases](../test-cases/EPIC-2-MANUAL-TEST-CASES.md)** - 43 test cases
  - Feature engineering
  - Model training (ARIMA, Prophet, LSTM)
  - Hyperparameter tuning
  - MLflow integration

- **[Epic 3 & 4 Test Cases](../test-cases/EPIC-3-EPIC-4-MANUAL-TEST-CASES.md)** - 89 test cases
  - Walk-forward validation
  - Backtesting
  - Trading simulation
  - API endpoints

### Feature Test Cases

- **[WebSocket Test Cases](../test-cases/WEBSOCKET-TEST-CASES.md)** - 10 test cases
  - WebSocket connection
  - Real-time streaming
  - Authentication
  - Error handling

- **[Streamlit Test Cases](../test-cases/STREAMLIT-TEST-CASES.md)** - 18 test cases
  - Dashboard functionality
  - API integration
  - Data visualization
  - Error handling

---

## Test Case Categories

### Functional Tests

**Purpose**: Verify features work as expected

**Examples**:
- Forecast generation
- Backtest execution
- Model training
- Data ingestion

---

### Integration Tests

**Purpose**: Verify component interactions

**Examples**:
- Data pipeline end-to-end
- API to database integration
- Model to API integration
- Frontend to backend integration

---

### Performance Tests

**Purpose**: Verify performance requirements

**Examples**:
- API response time
- Model inference time
- Data ingestion throughput
- Database query performance

---

### Security Tests

**Purpose**: Verify security requirements

**Examples**:
- API key validation
- Rate limiting
- Input validation
- SQL injection prevention

---

### Usability Tests

**Purpose**: Verify user experience

**Examples**:
- Dashboard navigation
- Error messages
- Loading states
- Responsive design

---

## Test Case Format

### Standard Format

```markdown
### Test Case ID: TC-XXX

**Description**: Brief description of what is tested

**Preconditions**: What must be true before test

**Steps**:
1. Step 1
2. Step 2
3. Step 3

**Expected Result**: What should happen

**Actual Result**: What actually happened (filled during execution)

**Status**: Pass/Fail/Skip
```

---

## Test Execution

### Automated Tests

**Location**: `tests/` directory

**Run**:
```bash
pytest tests/
```

### Manual Tests

**Location**: `docs/energy-price-forecasting/test-cases/`

**Execution**: Follow test case steps manually

**Recording**: Document results in test case document

---

## Test Coverage by Module

| Module | Automated Tests | Manual Tests | Coverage |
|--------|----------------|--------------|----------|
| Data Ingestion | 58 | 15 | 90%+ |
| Database | 15 | 8 | 95%+ |
| Models | 45 | 20 | 85%+ |
| API | 35 | 25 | 90%+ |
| Backtesting | 30 | 15 | 85%+ |
| Analytics | 20 | 10 | 80%+ |
| Dashboard | 25 | 18 | 85%+ |

---

## Test Maintenance

### Adding New Tests

1. Create test file in `tests/`
2. Follow naming convention: `test_<module>_<feature>.py`
3. Write test cases
4. Add to test suite
5. Update coverage

### Updating Tests

1. Review test case
2. Update if requirements changed
3. Verify test still passes
4. Update documentation

### Removing Tests

1. Identify obsolete test
2. Verify it's no longer needed
3. Remove test code
4. Update documentation

---

## Test Reporting

### Coverage Reports

**HTML Report**:
```bash
pytest --cov=. --cov-report=html
```

**Terminal Report**:
```bash
pytest --cov=. --cov-report=term-missing
```

### Test Results

**JUnit XML**:
```bash
pytest --junitxml=results.xml
```

---

## Best Practices

1. **Comprehensive**: Cover all features and edge cases
2. **Maintainable**: Keep tests simple and clear
3. **Fast**: Tests should run quickly
4. **Reliable**: Tests should be deterministic
5. **Documented**: Tests should be well documented

---

**Last Updated**: December 15, 2025

