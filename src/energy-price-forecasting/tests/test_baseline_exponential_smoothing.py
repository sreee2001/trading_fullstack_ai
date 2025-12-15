"""
Unit tests for Exponential Smoothing baseline model.

Tests ExponentialSmoothingModel class.

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
    from models.baseline.exponential_smoothing import ExponentialSmoothingModel
    ES_AVAILABLE = True
except ImportError:
    ES_AVAILABLE = False
    pytest.skip("statsmodels not available", allow_module_level=True)


@pytest.fixture
def sample_time_series():
    """Create sample time series data."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    trend = np.linspace(70, 75, 100)
    seasonal = 2 * np.sin(np.arange(100) * 2 * np.pi / 7)
    noise = np.random.randn(100) * 0.5
    prices = trend + seasonal + noise
    
    return pd.Series(prices, index=dates, name='price')


class TestExponentialSmoothingInitialization:
    """Tests for ExponentialSmoothingModel initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        model = ExponentialSmoothingModel()
        
        assert model.trend == 'add'
        assert model.seasonal == 'add'
        assert model.seasonal_periods == 7
        assert model.is_fitted == False
    
    def test_init_multiplicative(self):
        """Test initialization with multiplicative seasonality."""
        model = ExponentialSmoothingModel(seasonal='mul')
        
        assert model.seasonal == 'mul'
    
    def test_init_damped_trend(self):
        """Test initialization with damped trend."""
        model = ExponentialSmoothingModel(damped_trend=True)
        
        assert model.damped_trend == True


class TestExponentialSmoothingFit:
    """Tests for ExponentialSmoothingModel.fit()."""
    
    def test_fit_basic(self, sample_time_series):
        """Test basic fitting."""
        model = ExponentialSmoothingModel()
        model.fit(sample_time_series)
        
        assert model.is_fitted == True
        assert model.model is not None
    
    def test_fit_insufficient_data(self):
        """Test fitting with insufficient data."""
        data = pd.Series([100, 101, 102, 103, 104])  # Only 5 points, need 14 for period=7
        
        model = ExponentialSmoothingModel(seasonal_periods=7)
        
        with pytest.raises(ValueError, match="Insufficient data"):
            model.fit(data)
    
    def test_fit_with_nan(self, sample_time_series):
        """Test fitting with NaN values."""
        data = sample_time_series.copy()
        data.iloc[10:15] = np.nan
        
        model = ExponentialSmoothingModel()
        model.fit(data)
        
        assert model.is_fitted == True


class TestExponentialSmoothingPredict:
    """Tests for ExponentialSmoothingModel.predict()."""
    
    def test_predict_basic(self, sample_time_series):
        """Test basic prediction."""
        model = ExponentialSmoothingModel()
        model.fit(sample_time_series)
        
        predictions = model.predict(steps=10)
        
        assert len(predictions) == 10
        assert isinstance(predictions, pd.Series)
    
    def test_predict_with_conf_int(self, sample_time_series):
        """Test prediction with confidence intervals."""
        model = ExponentialSmoothingModel()
        model.fit(sample_time_series)
        
        forecast, conf_int = model.predict(steps=10, return_conf_int=True)
        
        assert len(forecast) == 10
        assert conf_int is not None
    
    def test_predict_not_fitted(self):
        """Test prediction without fitting."""
        model = ExponentialSmoothingModel()
        
        with pytest.raises(ValueError, match="must be fitted"):
            model.predict(steps=10)


class TestExponentialSmoothingSummary:
    """Tests for ExponentialSmoothingModel.get_model_summary()."""
    
    def test_summary_not_fitted(self):
        """Test summary when model not fitted."""
        model = ExponentialSmoothingModel()
        summary = model.get_model_summary()
        
        assert summary['is_fitted'] == False
    
    def test_summary_fitted(self, sample_time_series):
        """Test summary when model fitted."""
        model = ExponentialSmoothingModel()
        model.fit(sample_time_series)
        summary = model.get_model_summary()
        
        assert summary['is_fitted'] == True
        assert 'trend' in summary
        assert 'seasonal' in summary


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

