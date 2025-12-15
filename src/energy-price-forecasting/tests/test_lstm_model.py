"""
Unit tests for LSTM Forecaster.

Tests LSTMForecaster class.

Author: AI Assistant
Date: December 14, 2025
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path
import tempfile
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from models.lstm.lstm_model import LSTMForecaster
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False
    pytest.skip("LSTM models not available (TensorFlow required)", allow_module_level=True)


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


class TestLSTMForecasterInitialization:
    """Tests for LSTMForecaster initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        forecaster = LSTMForecaster()
        
        assert forecaster.sequence_length == 60
        assert forecaster.forecast_horizon == 1
        assert forecaster.model_type == 'lstm'
        assert forecaster.is_fitted == False
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        forecaster = LSTMForecaster(
            sequence_length=30,
            forecast_horizon=7,
            model_type='bidirectional',
            lstm_units=[64, 32]
        )
        
        assert forecaster.sequence_length == 30
        assert forecaster.forecast_horizon == 7
        assert forecaster.model_type == 'bidirectional'
        assert forecaster.lstm_units == [64, 32]
    
    def test_init_invalid_model_type(self):
        """Test initialization with invalid model type."""
        with pytest.raises(ValueError, match="Unknown model_type"):
            LSTMForecaster(model_type='invalid')


class TestLSTMForecasterFit:
    """Tests for LSTMForecaster.fit()."""
    
    def test_fit_basic(self, sample_time_series):
        """Test basic fitting."""
        forecaster = LSTMForecaster(sequence_length=10, forecast_horizon=1)
        
        forecaster.fit(
            sample_time_series[:150],
            epochs=2,  # Use small number for testing
            batch_size=16,
            verbose=0
        )
        
        assert forecaster.is_fitted == True
        assert forecaster.model is not None
        assert forecaster.history is not None
    
    def test_fit_with_validation(self, sample_time_series):
        """Test fitting with validation data."""
        forecaster = LSTMForecaster(sequence_length=10)
        
        forecaster.fit(
            sample_time_series[:100],
            validation_data=sample_time_series[100:150],
            epochs=2,
            verbose=0
        )
        
        assert forecaster.is_fitted == True
        assert 'val_loss' in forecaster.history.history or 'loss' in forecaster.history.history
    
    def test_fit_different_model_types(self, sample_time_series):
        """Test fitting different model types."""
        for model_type in ['lstm', 'bidirectional', 'stacked']:
            forecaster = LSTMForecaster(
                sequence_length=10,
                model_type=model_type
            )
            
            forecaster.fit(
                sample_time_series[:150],
                epochs=2,
                verbose=0
            )
            
            assert forecaster.is_fitted == True


class TestLSTMForecasterPredict:
    """Tests for LSTMForecaster.predict()."""
    
    def test_predict_basic(self, sample_time_series):
        """Test basic prediction."""
        forecaster = LSTMForecaster(sequence_length=10)
        forecaster.fit(sample_time_series[:150], epochs=2, verbose=0)
        
        predictions = forecaster.predict(sample_time_series[150:])
        
        assert predictions is not None
        assert isinstance(predictions, np.ndarray)
        assert len(predictions) > 0
    
    def test_predict_not_fitted(self, sample_time_series):
        """Test prediction without fitting."""
        forecaster = LSTMForecaster()
        
        with pytest.raises(ValueError, match="must be fitted"):
            forecaster.predict(sample_time_series)
    
    def test_predict_dataframe(self, sample_dataframe):
        """Test prediction with DataFrame."""
        forecaster = LSTMForecaster(sequence_length=10)
        forecaster.fit(sample_dataframe[:150], target_column='price', epochs=2, verbose=0)
        
        predictions = forecaster.predict(sample_dataframe[150:], target_column='price')
        
        assert predictions is not None
        assert len(predictions) > 0


class TestLSTMForecasterEvaluate:
    """Tests for LSTMForecaster.evaluate()."""
    
    def test_evaluate_basic(self, sample_time_series):
        """Test basic evaluation."""
        forecaster = LSTMForecaster(sequence_length=10)
        forecaster.fit(sample_time_series[:150], epochs=2, verbose=0)
        
        metrics = forecaster.evaluate(sample_time_series[150:])
        
        assert isinstance(metrics, dict)
        assert 'loss' in metrics
        assert 'mae' in metrics or 'mse' in metrics
    
    def test_evaluate_not_fitted(self, sample_time_series):
        """Test evaluation without fitting."""
        forecaster = LSTMForecaster()
        
        with pytest.raises(ValueError, match="must be fitted"):
            forecaster.evaluate(sample_time_series)


class TestLSTMForecasterSaveLoad:
    """Tests for LSTMForecaster.save_model() and load_model()."""
    
    def test_save_model(self, sample_time_series):
        """Test saving model."""
        forecaster = LSTMForecaster(sequence_length=10)
        forecaster.fit(sample_time_series[:150], epochs=2, verbose=0)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = os.path.join(tmpdir, 'test_model')
            forecaster.save_model(model_path)
            
            assert os.path.exists(model_path) or os.path.exists(f"{model_path}.h5")
    
    def test_load_model(self, sample_time_series):
        """Test loading model."""
        forecaster = LSTMForecaster(sequence_length=10)
        forecaster.fit(sample_time_series[:150], epochs=2, verbose=0)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = os.path.join(tmpdir, 'test_model')
            forecaster.save_model(model_path)
            
            # Create new forecaster and load
            new_forecaster = LSTMForecaster(sequence_length=10)
            new_forecaster.load_model(model_path)
            
            assert new_forecaster.is_fitted == True
            assert new_forecaster.model is not None
    
    def test_save_not_fitted(self):
        """Test saving model without fitting."""
        forecaster = LSTMForecaster()
        
        with pytest.raises(ValueError, match="must be fitted"):
            forecaster.save_model('test_model')


class TestLSTMForecasterSummary:
    """Tests for LSTMForecaster.get_model_summary()."""
    
    def test_summary_not_fitted(self):
        """Test summary when model not fitted."""
        forecaster = LSTMForecaster()
        summary = forecaster.get_model_summary()
        
        assert summary['is_fitted'] == False
        assert summary['model_type'] == 'lstm'
    
    def test_summary_fitted(self, sample_time_series):
        """Test summary when model fitted."""
        forecaster = LSTMForecaster(sequence_length=10)
        forecaster.fit(sample_time_series[:150], epochs=2, verbose=0)
        summary = forecaster.get_model_summary()
        
        assert summary['is_fitted'] == True
        assert 'n_features' in summary
        assert 'training_history' in summary


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

