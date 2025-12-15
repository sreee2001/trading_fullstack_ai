# Contributing Guide

**Thank you for your interest in contributing!**

This guide will help you contribute to the Energy Price Forecasting System.

---

## Development Setup

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for frontend)
- **Docker Desktop**
- **Git**

### Setup Steps

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/trading_fullstack_ai.git
cd trading_fullstack_ai/src/energy-price-forecasting
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
cd dashboard && npm install && cd ..
```

4. **Start Services**
```bash
docker compose up -d timescaledb redis
```

5. **Run Tests**
```bash
pytest
```

---

## Code Standards

### Python

- **Style**: Follow PEP 8
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Use Google-style docstrings
- **Line Length**: Max 100 characters
- **Imports**: Use absolute imports, group by standard/third-party/local

**Example**:
```python
from typing import Optional, List
import pandas as pd

from database.operations import get_price_data


def fetch_forecast(
    commodity: str,
    horizon: int,
    start_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetch forecast for given commodity.
    
    Args:
        commodity: Commodity symbol (WTI, BRENT, NG)
        horizon: Forecast horizon in days
        start_date: Start date (YYYY-MM-DD). Defaults to today.
    
    Returns:
        DataFrame with forecast predictions
    
    Raises:
        ValueError: If commodity is invalid
    """
    pass
```

### TypeScript

- **Style**: Follow ESLint rules
- **Type Safety**: Use TypeScript types, avoid `any`
- **Components**: Functional components with hooks
- **Naming**: PascalCase for components, camelCase for variables

**Example**:
```typescript
interface ForecastProps {
  commodity: string;
  horizon: number;
  onUpdate: (forecast: Forecast) => void;
}

export const ForecastComponent: React.FC<ForecastProps> = ({
  commodity,
  horizon,
  onUpdate
}) => {
  // Component implementation
};
```

---

## Testing Requirements

### Test Coverage

- **Minimum**: 80% code coverage
- **Target**: 90%+ coverage
- **Critical Code**: 100% coverage

### Writing Tests

1. **Unit Tests**: Test individual functions/classes
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Test full workflows

**Example**:
```python
import pytest
from data_ingestion.eia_client import EIAAPIClient

def test_fetch_wti_prices():
    client = EIAAPIClient(api_key="test_key")
    data = client.fetch_wti_prices("2024-01-01", "2024-01-31")
    assert len(data) > 0
    assert "date" in data.columns
    assert "price" in data.columns
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific file
pytest tests/test_eia_client.py -v

# Watch mode
pytest-watch
```

---

## Pull Request Process

### Before Submitting

1. **Update Tests**: Add tests for new features
2. **Update Documentation**: Update relevant docs
3. **Run Tests**: Ensure all tests pass
4. **Check Coverage**: Maintain coverage targets
5. **Lint Code**: Run linters and fix issues

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests passing
- [ ] Coverage maintained
- [ ] No linter errors
- [ ] Commit messages follow conventions

### Commit Messages

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style
- `refactor:` Code refactoring
- `test:` Tests
- `chore:` Maintenance

**Example**:
```
feat(api): Add WebSocket endpoint for real-time forecasts

- Implement WebSocket connection manager
- Add forecast streaming functionality
- Add authentication for WebSocket
- Add tests for WebSocket endpoint
```

---

## Project Structure

### Adding New Module

1. Create module directory
2. Add `__init__.py`
3. Implement module code
4. Add tests in `tests/`
5. Update documentation

### Adding New API Endpoint

1. Create route in `api/routes/`
2. Add request/response models in `api/models/`
3. Implement service logic in `api/services/`
4. Add authentication
5. Add tests
6. Update Swagger docs

### Adding New Model

1. Create model class in `models/`
2. Implement base interface
3. Add to training pipeline
4. Register in model service
5. Add tests
6. Update documentation

---

## Documentation

### Code Documentation

- **Docstrings**: All public functions/classes
- **Type Hints**: All function signatures
- **Comments**: Complex logic explanations

### User Documentation

- **User Guides**: Update `docs/users/`
- **API Docs**: Update Swagger/ReDoc
- **Examples**: Add usage examples

### Developer Documentation

- **Module Docs**: Update `docs/developers/modules/`
- **Architecture**: Update architecture docs
- **Workflows**: Update workflow docs

---

## Code Review

### Review Criteria

- **Functionality**: Does it work correctly?
- **Testing**: Are tests comprehensive?
- **Documentation**: Is it well documented?
- **Style**: Does it follow conventions?
- **Performance**: Is it efficient?
- **Security**: Are there security concerns?

### Review Process

1. **Automated Checks**: CI/CD runs tests and linters
2. **Manual Review**: At least one reviewer
3. **Feedback**: Address review comments
4. **Approval**: Merge after approval

---

## Getting Help

- **Questions**: Open GitHub issue
- **Bugs**: Report in GitHub issues
- **Feature Requests**: Open feature request issue
- **Documentation**: Check existing docs first

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** 🎉

---

**Last Updated**: December 15, 2025

