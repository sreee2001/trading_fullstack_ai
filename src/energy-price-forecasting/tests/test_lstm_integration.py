"""
Unit tests for LSTM with Feature Engineering integration.

Tests LSTMWithFeatures class.

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
    from models.lstm.integration import LSTMWithFeatures
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    pytest.skip("LSTM integration not available", allow_module_level=True)


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame with price and date."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    
    return pd.DataFrame({
        'date': dates,
        'price': 70 + np.cumsum(np.random.randn(200) * 0.5),
        'volume': np.random.randint(1000000, 2000000, 200)
    })


class TestLSTMWithFeaturesInitialization:
    """Tests for LSTMWithFeatures initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        forecaster = LSTMWithFeatures(sequence_length=10)
        
        assert forecaster.feature_engineer is not None
        assert forecaster.lstm_forecaster is not None
        assert forecaster.is_fitted == False
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        forecaster = LSTMWithFeatures(
            sequence_length=30,
            forecast_horizon=7,
            model_type='bidirectional'
        )
        
        assert forecaster.lstm_forecaster.sequence_length == 30
        assert forecaster.lstm_forecaster.forecast_horizon == 7
        assert forecaster.lstm_forecaster.model_type == 'bidirectional'


class TestLSTMWithFeaturesFit:
    """Tests for LSTMWithFeatures.fit()."""
    
    def test_fit_basic(self, sample_dataframe):
        """Test basic fitting with feature engineering."""
        forecaster = LSTMWithFeatures(sequence_length=10)
        
        # Fit with minimal epochs for testing
        forecaster.fit(
            sample_dataframe[:150],
            target_col='price',
            epochs=2,
            verbose=0
        )
        
        assert forecaster.is_fitted == True
        assert forecaster.lstm_forecaster.is_fitted == True
    
    def test_fit_with_validation(self, sample_dataframe):
        """Test fitting with validation data."""
        forecaster = LSTMWithFeatures(sequence_length=10)
        
        forecaster.fit(
            sample_dataframe[:100],
            validation_data=sample_dataframe[100:150],
            target_col='price',
            epochs=2,
            verbose=0
        )
        
        assert forecaster.is_fitted == True


class TestLSTMWithFeaturesPredict:
    """Tests for LSTMWithFeatures.predict()."""
    
    def test_predict_basic(self, sample_dataframe):
        """Test basic prediction."""
        forecaster = LSTMWithFeatures(sequence_length=10)
        forecaster.fit(sample_dataframe[:150], target_col='price', epochs=2, verbose=0)
        
        predictions = forecaster.predict(sample_dataframe[150:], target_col='price')
        
        assert predictions is not None
        assert isinstance(predictions, np.ndarray)
        assert len(predictions) > 0
    
    def test_predict_not_fitted(self, sample_dataframe):
        """Test prediction without fitting."""
        forecaster = LSTMWithFeatures()
        
        with pytest.raises(ValueError, match="must be fitted"):
            forecaster.predict(sample_dataframe)


class TestLSTMWithFeaturesEvaluate:
    """Tests for LSTMWithFeatures.evaluate()."""
    
    def test_evaluate_basic(self, sample_dataframe):
        """Test basic evaluation."""
        forecaster = LSTMWithFeatures(sequence_length=10)
        forecaster.fit(sample_dataframe[:150], target_col='price', epochs=2, verbose=0)
        
        metrics = forecaster.evaluate(sample_dataframe[150:], target_col='price')
        
        assert isinstance(metrics, dict)
        assert 'loss' in metrics


class TestLSTMWithFeaturesSummary:
    """Tests for LSTMWithFeatures.get_summary()."""
    
    def test_summary(self, sample_dataframe):
        """Test getting summary."""
        forecaster = LSTMWithFeatures(sequence_length=10)
        forecaster.fit(sample_dataframe[:150], target_col='price', epochs=2, verbose=0)
        
        summary = forecaster.get_summary()
        
        assert 'is_fitted' in summary
        assert 'feature_engineering' in summary
        assert 'lstm_model' in summary


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

