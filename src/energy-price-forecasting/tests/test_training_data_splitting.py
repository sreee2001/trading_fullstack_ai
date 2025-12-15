"""
Unit tests for training data splitting.

Tests TimeSeriesSplitter class.

Author: AI Assistant
Date: December 14, 2025
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from training.data_splitting import TimeSeriesSplitter
    SPLITTER_AVAILABLE = True
except ImportError:
    SPLITTER_AVAILABLE = False
    pytest.skip("Training module not available", allow_module_level=True)


@pytest.fixture
def sample_time_series():
    """Create sample time series data."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    prices = 70 + np.cumsum(np.random.randn(200) * 0.5)
    
    return pd.Series(prices, index=dates, name='price')


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    
    return pd.DataFrame({
        'date': dates,
        'price': 70 + np.cumsum(np.random.randn(200) * 0.5),
        'volume': np.random.randint(1000000, 2000000, 200)
    })


class TestTimeSeriesSplitterInitialization:
    """Tests for TimeSeriesSplitter initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        splitter = TimeSeriesSplitter()
        
        assert splitter.train_ratio == 0.7
        assert splitter.val_ratio == 0.15
        assert splitter.test_ratio == 0.15
    
    def test_init_custom_ratios(self):
        """Test initialization with custom ratios."""
        splitter = TimeSeriesSplitter(train_ratio=0.8, val_ratio=0.1, test_ratio=0.1)
        
        assert splitter.train_ratio == 0.8
        assert splitter.val_ratio == 0.1
        assert splitter.test_ratio == 0.1
    
    def test_init_invalid_ratios(self):
        """Test initialization with invalid ratios."""
        with pytest.raises(ValueError, match="must sum to 1.0"):
            TimeSeriesSplitter(train_ratio=0.8, val_ratio=0.1, test_ratio=0.2)


class TestTimeSeriesSplitterSplit:
    """Tests for TimeSeriesSplitter.split()."""
    
    def test_split_series(self, sample_time_series):
        """Test splitting Series."""
        splitter = TimeSeriesSplitter()
        train, val, test = splitter.split(sample_time_series)
        
        assert len(train) > 0
        assert len(val) > 0
        assert len(test) > 0
        assert len(train) + len(val) + len(test) == len(sample_time_series)
    
    def test_split_dataframe(self, sample_dataframe):
        """Test splitting DataFrame."""
        splitter = TimeSeriesSplitter()
        train, val, test = splitter.split(sample_dataframe)
        
        assert len(train) > 0
        assert len(val) > 0
        assert len(test) > 0
    
    def test_split_ratios(self, sample_time_series):
        """Test that split ratios are approximately correct."""
        splitter = TimeSeriesSplitter(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
        train, val, test = splitter.split(sample_time_series)
        
        total = len(sample_time_series)
        assert abs(len(train) / total - 0.7) < 0.05  # Within 5%
        assert abs(len(val) / total - 0.15) < 0.05
        assert abs(len(test) / total - 0.15) < 0.05
    
    def test_split_temporal_order(self, sample_time_series):
        """Test that split preserves temporal order."""
        splitter = TimeSeriesSplitter()
        train, val, test = splitter.split(sample_time_series)
        
        # Check that train comes before val, val before test
        assert train.index[-1] < val.index[0]
        assert val.index[-1] < test.index[0]


class TestTimeSeriesSplitterSplitWithDates:
    """Tests for TimeSeriesSplitter.split_with_dates()."""
    
    def test_split_with_dates(self, sample_dataframe):
        """Test splitting with specific dates."""
        splitter = TimeSeriesSplitter(date_column='date')
        train, val, test = splitter.split_with_dates(
            sample_dataframe,
            train_end_date='2024-04-01',
            val_end_date='2024-05-01'
        )
        
        assert len(train) > 0
        assert len(val) > 0
        assert len(test) > 0
    
    def test_split_with_dates_datetime_index(self, sample_time_series):
        """Test splitting with DatetimeIndex."""
        splitter = TimeSeriesSplitter()
        train, val, test = splitter.split_with_dates(
            sample_time_series,
            train_end_date='2024-04-01',
            val_end_date='2024-05-01'
        )
        
        assert len(train) > 0
        assert len(val) > 0
        assert len(test) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

