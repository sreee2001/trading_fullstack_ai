"""
Pytest Configuration and Shared Fixtures.

Provides shared fixtures and configuration for all tests.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_data_dir():
    """Get test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def sample_price_data():
    """Create sample price data for testing."""
    import pandas as pd
    from datetime import datetime, timedelta
    
    dates = pd.date_range(
        start=datetime(2024, 1, 1),
        end=datetime(2024, 12, 31),
        freq='D'
    )
    
    # Generate sample price data
    prices = 75 + 5 * pd.Series(range(len(dates))) / len(dates) + \
             2 * pd.Series([i % 7 for i in range(len(dates))]) + \
             pd.Series([i % 30 for i in range(len(dates))]) * 0.1
    
    data = pd.DataFrame({
        'timestamp': dates,
        'price': prices,
        'commodity': 'WTI'
    })
    
    return data


@pytest.fixture(scope="session")
def sample_returns():
    """Create sample returns data for testing."""
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    returns = np.random.normal(0, 0.02, len(dates))
    
    return pd.Series(returns, index=dates)


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables."""
    # Set test environment variables
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    
    # Mock API keys if not set
    if not os.getenv("EIA_API_KEY"):
        monkeypatch.setenv("EIA_API_KEY", "test_eia_key")
    if not os.getenv("FRED_API_KEY"):
        monkeypatch.setenv("FRED_API_KEY", "test_fred_key")


@pytest.fixture(scope="function")
def clean_database():
    """Clean database before test (if needed)."""
    # This would clean test data if needed
    yield
    # Cleanup after test if needed

