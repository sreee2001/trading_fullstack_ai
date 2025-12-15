"""
Unit tests for multi-horizon forecaster.

Tests MultiHorizonForecaster class.

Author: AI Assistant
Date: December 14, 2025
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from multi_horizon.multi_horizon_forecaster import MultiHorizonForecaster
    FORECASTER_AVAILABLE = True
except ImportError:
    FORECASTER_AVAILABLE = False
    pytest.skip("Multi-horizon module not available", allow_module_level=True)


@pytest.fixture
def sample_data():
    """Create sample data."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    
    return pd.DataFrame({
        'date': dates,
        'price': 70 + np.cumsum(np.random.randn(200) * 0.5)
    })


class TestMultiHorizonForecasterInitialization:
    """Tests for MultiHorizonForecaster initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        forecaster = MultiHorizonForecaster(
            model_type='arima',
            horizons=[1, 7, 30],
            use_multi_output=False
        )
        
        assert forecaster.model_type == 'arima'
        assert forecaster.horizons == [1, 7, 30]
        assert forecaster.use_multi_output == False
    
    def test_init_default_horizons(self):
        """Test initialization with default horizons."""
        forecaster = MultiHorizonForecaster(model_type='arima')
        
        assert forecaster.horizons == [1, 7, 30]
    
    def test_init_invalid_model_type(self):
        """Test initialization with invalid model type."""
        with pytest.raises(ValueError, match="Unknown model type"):
            MultiHorizonForecaster(model_type='invalid')


class TestMultiHorizonForecasterFit:
    """Tests for MultiHorizonForecaster.fit()."""
    
    @patch('multi_horizon.multi_horizon_forecaster.ARIMAForecaster')
    def test_fit_separate_models(self, mock_arima_class, sample_data):
        """Test fitting with separate models."""
        mock_model = Mock()
        mock_arima_class.return_value = mock_model
        
        forecaster = MultiHorizonForecaster(
            model_type='arima',
            use_multi_output=False
        )
        
        forecaster.fit(sample_data, target_col='price')
        
        assert forecaster.is_fitted == True
        assert len(forecaster.models) == 3  # One for each horizon


class TestMultiHorizonForecasterPredict:
    """Tests for MultiHorizonForecaster.predict()."""
    
    @patch('multi_horizon.multi_horizon_forecaster.ARIMAForecaster')
    def test_predict_separate_models(self, mock_arima_class, sample_data):
        """Test prediction with separate models."""
        mock_model = Mock()
        mock_model.predict.return_value = np.array([100.0])
        mock_arima_class.return_value = mock_model
        
        forecaster = MultiHorizonForecaster(
            model_type='arima',
            use_multi_output=False
        )
        forecaster.is_fitted = True
        
        predictions = forecaster.predict(sample_data, target_col='price')
        
        assert isinstance(predictions, dict)
        assert 1 in predictions
        assert 7 in predictions
        assert 30 in predictions
    
    def test_predict_not_fitted(self, sample_data):
        """Test prediction without fitting."""
        forecaster = MultiHorizonForecaster(model_type='arima')
        
        with pytest.raises(RuntimeError, match="not fitted"):
            forecaster.predict(sample_data)


class TestMultiHorizonForecasterSingleHorizon:
    """Tests for MultiHorizonForecaster.predict_single_horizon()."""
    
    @patch('multi_horizon.multi_horizon_forecaster.ARIMAForecaster')
    def test_predict_single_horizon(self, mock_arima_class, sample_data):
        """Test single horizon prediction."""
        mock_model = Mock()
        mock_model.predict.return_value = np.array([100.0])
        mock_arima_class.return_value = mock_model
        
        forecaster = MultiHorizonForecaster(
            model_type='arima',
            use_multi_output=False
        )
        forecaster.is_fitted = True
        
        prediction = forecaster.predict_single_horizon(sample_data, horizon=7)
        
        assert isinstance(prediction, np.ndarray)
    
    def test_predict_single_horizon_invalid(self, sample_data):
        """Test single horizon prediction with invalid horizon."""
        forecaster = MultiHorizonForecaster(model_type='arima')
        forecaster.is_fitted = True
        
        with pytest.raises(ValueError, match="not in configured horizons"):
            forecaster.predict_single_horizon(sample_data, horizon=5)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

