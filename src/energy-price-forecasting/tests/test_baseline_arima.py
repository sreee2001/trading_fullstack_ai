"""
Unit tests for ARIMA/SARIMA baseline model.

Tests ARIMAModel class including fitting, prediction, and model summary.

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
    from models.baseline.arima_model import ARIMAModel
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False
    pytest.skip("pmdarima not available", allow_module_level=True)


@pytest.fixture
def sample_time_series():
    """Create sample time series data."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    # Create realistic price series with trend and seasonality
    trend = np.linspace(70, 75, 100)
    seasonal = 2 * np.sin(np.arange(100) * 2 * np.pi / 7)  # Weekly seasonality
    noise = np.random.randn(100) * 0.5
    prices = trend + seasonal + noise
    
    return pd.Series(prices, index=dates, name='price')


@pytest.fixture
def sample_series_no_index():
    """Create sample time series without datetime index."""
    np.random.seed(42)
    prices = 70 + np.cumsum(np.random.randn(100) * 0.1)
    return pd.Series(prices, name='price')


class TestARIMAModelInitialization:
    """Tests for ARIMAModel initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        model = ARIMAModel()
        
        assert model.auto_select == True
        assert model.seasonal == True
        assert model.is_fitted == False
        assert model.model_type == 'SARIMA'
    
    def test_init_arima_not_sarima(self):
        """Test initialization with seasonal=False."""
        model = ARIMAModel(seasonal=False)
        
        assert model.seasonal == False
        assert model.model_type == 'ARIMA'
    
    def test_init_manual_order(self):
        """Test initialization with manual order."""
        model = ARIMAModel(order=(1, 1, 1), auto_select=False, seasonal=False)
        
        assert model.order == (1, 1, 1)
        assert model.auto_select == False
    
    def test_init_manual_seasonal_order(self):
        """Test initialization with manual seasonal order."""
        model = ARIMAModel(
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 7),
            auto_select=False,
            seasonal=True
        )
        
        assert model.order == (1, 1, 1)
        assert model.seasonal_order == (1, 1, 1, 7)


class TestARIMAModelFit:
    """Tests for ARIMAModel.fit()."""
    
    def test_fit_basic(self, sample_time_series):
        """Test basic fitting."""
        model = ARIMAModel(seasonal=False)
        model.fit(sample_time_series)
        
        assert model.is_fitted == True
        assert model.model is not None
        assert model.fitted_order is not None
    
    def test_fit_sarima(self, sample_time_series):
        """Test fitting SARIMA model."""
        model = ARIMAModel(seasonal=True, seasonal_periods=7)
        model.fit(sample_time_series)
        
        assert model.is_fitted == True
        assert model.model is not None
    
    def test_fit_auto_select(self, sample_time_series):
        """Test fitting with auto parameter selection."""
        model = ARIMAModel(auto_select=True)
        model.fit(sample_time_series)
        
        assert model.is_fitted == True
        assert model.fitted_order is not None
    
    def test_fit_manual_order(self, sample_time_series):
        """Test fitting with manual order."""
        model = ARIMAModel(
            order=(1, 1, 1),
            auto_select=False,
            seasonal=False
        )
        model.fit(sample_time_series)
        
        assert model.is_fitted == True
        assert model.fitted_order == (1, 1, 1)
    
    def test_fit_insufficient_data(self):
        """Test fitting with insufficient data."""
        data = pd.Series([100, 101, 102, 103, 104])  # Only 5 points
        
        model = ARIMAModel()
        
        with pytest.raises(ValueError, match="Insufficient data"):
            model.fit(data)
    
    def test_fit_with_nan(self, sample_time_series):
        """Test fitting with NaN values."""
        data = sample_time_series.copy()
        data.iloc[10:15] = np.nan
        
        model = ARIMAModel()
        model.fit(data)
        
        assert model.is_fitted == True
    
    def test_fit_dataframe_single_column(self, sample_time_series):
        """Test fitting with DataFrame (single column)."""
        df = sample_time_series.to_frame()
        
        model = ARIMAModel()
        model.fit(df)
        
        assert model.is_fitted == True


class TestARIMAModelPredict:
    """Tests for ARIMAModel.predict()."""
    
    def test_predict_basic(self, sample_time_series):
        """Test basic prediction."""
        model = ARIMAModel(seasonal=False)
        model.fit(sample_time_series)
        
        predictions = model.predict(steps=10)
        
        assert len(predictions) == 10
        assert isinstance(predictions, pd.Series)
    
    def test_predict_with_conf_int(self, sample_time_series):
        """Test prediction with confidence intervals."""
        model = ARIMAModel(seasonal=False)
        model.fit(sample_time_series)
        
        forecast, conf_int = model.predict(steps=10, return_conf_int=True)
        
        assert len(forecast) == 10
        assert conf_int is not None
        assert len(conf_int) == 10
    
    def test_predict_not_fitted(self):
        """Test prediction without fitting."""
        model = ARIMAModel()
        
        with pytest.raises(ValueError, match="must be fitted"):
            model.predict(steps=10)
    
    def test_predict_different_steps(self, sample_time_series):
        """Test prediction with different step sizes."""
        model = ARIMAModel(seasonal=False)
        model.fit(sample_time_series)
        
        pred_1 = model.predict(steps=1)
        pred_5 = model.predict(steps=5)
        pred_30 = model.predict(steps=30)
        
        assert len(pred_1) == 1
        assert len(pred_5) == 5
        assert len(pred_30) == 30


class TestARIMAModelSummary:
    """Tests for ARIMAModel.get_model_summary()."""
    
    def test_summary_not_fitted(self):
        """Test summary when model not fitted."""
        model = ARIMAModel()
        summary = model.get_model_summary()
        
        assert summary['is_fitted'] == False
        assert summary['model_type'] == 'SARIMA'
    
    def test_summary_fitted(self, sample_time_series):
        """Test summary when model fitted."""
        model = ARIMAModel(seasonal=False)
        model.fit(sample_time_series)
        summary = model.get_model_summary()
        
        assert summary['is_fitted'] == True
        assert 'order' in summary
        assert summary['order'] is not None


class TestARIMAModelResiduals:
    """Tests for ARIMAModel.get_residuals()."""
    
    def test_residuals_basic(self, sample_time_series):
        """Test getting residuals."""
        model = ARIMAModel(seasonal=False)
        model.fit(sample_time_series)
        
        residuals = model.get_residuals()
        
        assert isinstance(residuals, pd.Series)
        assert len(residuals) > 0
    
    def test_residuals_not_fitted(self):
        """Test getting residuals without fitting."""
        model = ARIMAModel()
        
        with pytest.raises(ValueError, match="must be fitted"):
            model.get_residuals()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

