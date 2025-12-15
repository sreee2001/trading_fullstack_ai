"""
Unit tests for Facebook Prophet baseline model.

Tests ProphetModel class.

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
    from models.baseline.prophet_model import ProphetModel
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    pytest.skip("prophet not available", allow_module_level=True)


@pytest.fixture
def sample_time_series():
    """Create sample time series data with datetime index."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    trend = np.linspace(70, 75, 100)
    seasonal = 2 * np.sin(np.arange(100) * 2 * np.pi / 7)
    noise = np.random.randn(100) * 0.5
    prices = trend + seasonal + noise
    
    return pd.Series(prices, index=dates, name='price')


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame with ds and y columns."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    prices = 70 + np.cumsum(np.random.randn(100) * 0.1)
    
    return pd.DataFrame({
        'ds': dates,
        'y': prices
    })


class TestProphetModelInitialization:
    """Tests for ProphetModel initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        model = ProphetModel()
        
        assert model.yearly_seasonality == True
        assert model.weekly_seasonality == True
        assert model.daily_seasonality == False
        assert model.is_fitted == False
    
    def test_init_no_seasonality(self):
        """Test initialization without seasonality."""
        model = ProphetModel(
            yearly_seasonality=False,
            weekly_seasonality=False
        )
        
        assert model.yearly_seasonality == False
        assert model.weekly_seasonality == False


class TestProphetModelFit:
    """Tests for ProphetModel.fit()."""
    
    def test_fit_with_series(self, sample_time_series):
        """Test fitting with Series (datetime index)."""
        model = ProphetModel()
        model.fit(sample_time_series)
        
        assert model.is_fitted == True
        assert model.model is not None
    
    def test_fit_with_dataframe_ds_y(self, sample_dataframe):
        """Test fitting with DataFrame (ds, y columns)."""
        model = ProphetModel()
        model.fit(sample_dataframe)
        
        assert model.is_fitted == True
    
    def test_fit_with_dataframe_custom_cols(self):
        """Test fitting with DataFrame (custom column names)."""
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'price': 70 + np.random.randn(50) * 0.5
        })
        
        model = ProphetModel()
        model.fit(df, date_col='date', value_col='price')
        
        assert model.is_fitted == True
    
    def test_fit_insufficient_data(self):
        """Test fitting with insufficient data."""
        data = pd.Series([100, 101], index=pd.date_range('2024-01-01', periods=2))
        
        model = ProphetModel()
        
        with pytest.raises(ValueError, match="Insufficient data"):
            model.fit(data)
    
    def test_fit_series_no_datetime_index(self):
        """Test fitting with Series without datetime index."""
        data = pd.Series([100, 101, 102, 103, 104])
        
        model = ProphetModel()
        
        with pytest.raises(ValueError, match="DatetimeIndex"):
            model.fit(data)


class TestProphetModelPredict:
    """Tests for ProphetModel.predict()."""
    
    def test_predict_basic(self, sample_time_series):
        """Test basic prediction."""
        model = ProphetModel()
        model.fit(sample_time_series)
        
        predictions = model.predict(steps=10)
        
        assert isinstance(predictions, pd.DataFrame)
        assert 'ds' in predictions.columns or 'yhat' in predictions.columns
    
    def test_predict_with_dates(self, sample_time_series):
        """Test prediction with specific dates."""
        model = ProphetModel()
        model.fit(sample_time_series)
        
        start_date = datetime(2024, 4, 10)
        end_date = datetime(2024, 4, 20)
        
        predictions = model.predict(start_date=start_date, end_date=end_date)
        
        assert isinstance(predictions, pd.DataFrame)
    
    def test_predict_not_fitted(self):
        """Test prediction without fitting."""
        model = ProphetModel()
        
        with pytest.raises(ValueError, match="must be fitted"):
            model.predict(steps=10)


class TestProphetModelSummary:
    """Tests for ProphetModel.get_model_summary()."""
    
    def test_summary_not_fitted(self):
        """Test summary when model not fitted."""
        model = ProphetModel()
        summary = model.get_model_summary()
        
        assert summary['is_fitted'] == False
    
    def test_summary_fitted(self, sample_time_series):
        """Test summary when model fitted."""
        model = ProphetModel()
        model.fit(sample_time_series)
        summary = model.get_model_summary()
        
        assert summary['is_fitted'] == True
        assert 'yearly_seasonality' in summary


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

