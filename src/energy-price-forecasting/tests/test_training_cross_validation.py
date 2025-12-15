"""
Unit tests for cross-validation.

Tests TimeSeriesCrossValidator class.

Author: AI Assistant
Date: December 14, 2025
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from training.cross_validation import TimeSeriesCrossValidator
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False
    pytest.skip("Training module not available", allow_module_level=True)


@pytest.fixture
def sample_time_series():
    """Create sample time series data."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    prices = 70 + np.cumsum(np.random.randn(200) * 0.5)
    
    return pd.Series(prices, index=dates, name='price')


class TestTimeSeriesCrossValidatorInitialization:
    """Tests for TimeSeriesCrossValidator initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        cv = TimeSeriesCrossValidator()
        
        assert cv.n_splits == 5
        assert cv.test_size == 30
        assert cv.gap == 0
        assert cv.expanding_window == True
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        cv = TimeSeriesCrossValidator(n_splits=3, test_size=20, gap=5, expanding_window=False)
        
        assert cv.n_splits == 3
        assert cv.test_size == 20
        assert cv.gap == 5
        assert cv.expanding_window == False


class TestTimeSeriesCrossValidatorSplit:
    """Tests for TimeSeriesCrossValidator.split()."""
    
    def test_split_basic(self, sample_time_series):
        """Test basic splitting."""
        cv = TimeSeriesCrossValidator(n_splits=3, test_size=20)
        splits = cv.split(sample_time_series)
        
        assert len(splits) == 3
        assert all(isinstance(split, tuple) and len(split) == 2 for split in splits)
    
    def test_split_temporal_order(self, sample_time_series):
        """Test that splits respect temporal order."""
        cv = TimeSeriesCrossValidator(n_splits=3, test_size=20)
        splits = cv.split(sample_time_series)
        
        for train_idx, test_idx in splits:
            # Train should come before test
            assert train_idx[-1] < test_idx[0]
    
    def test_split_insufficient_data(self):
        """Test splitting with insufficient data."""
        data = pd.Series([100] * 50)  # Only 50 points
        
        cv = TimeSeriesCrossValidator(n_splits=5, test_size=20)
        
        with pytest.raises(ValueError, match="Insufficient data"):
            cv.split(data)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

