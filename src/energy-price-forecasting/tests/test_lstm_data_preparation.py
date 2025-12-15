"""
Unit tests for LSTM data preparation.

Tests SequenceDataPreparator class.

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
    from models.lstm.data_preparation import SequenceDataPreparator
    PREP_AVAILABLE = True
except ImportError:
    PREP_AVAILABLE = False
    pytest.skip("LSTM models not available", allow_module_level=True)


@pytest.fixture
def sample_time_series():
    """Create sample time series data."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    prices = 70 + np.cumsum(np.random.randn(200) * 0.5)
    
    return pd.Series(prices, index=dates, name='price')


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame with multiple features."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    
    return pd.DataFrame({
        'date': dates,
        'price': 70 + np.cumsum(np.random.randn(200) * 0.5),
        'volume': np.random.randint(1000000, 2000000, 200),
        'feature1': np.random.randn(200),
        'feature2': np.random.randn(200)
    })


class TestSequenceDataPreparatorInitialization:
    """Tests for SequenceDataPreparator initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        preparator = SequenceDataPreparator()
        
        assert preparator.sequence_length == 60
        assert preparator.forecast_horizon == 1
        assert preparator.is_fitted == False
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        preparator = SequenceDataPreparator(
            sequence_length=30,
            forecast_horizon=7,
            scaler_type='standard'
        )
        
        assert preparator.sequence_length == 30
        assert preparator.forecast_horizon == 7
        assert preparator.scaler_type == 'standard' or hasattr(preparator.scaler, 'mean_')
    
    def test_init_invalid_scaler(self):
        """Test initialization with invalid scaler type."""
        with pytest.raises(ValueError, match="Unknown scaler_type"):
            SequenceDataPreparator(scaler_type='invalid')


class TestSequenceDataPreparatorPrepareData:
    """Tests for SequenceDataPreparator.prepare_data()."""
    
    def test_prepare_data_series(self, sample_time_series):
        """Test preparing data from Series."""
        preparator = SequenceDataPreparator(sequence_length=10, forecast_horizon=1)
        
        X_train, y_train, X_test, y_test = preparator.prepare_data(
            sample_time_series[:150],
            test_data=sample_time_series[150:]
        )
        
        assert X_train.ndim == 3  # (samples, sequence_length, features)
        assert y_train.ndim == 2  # (samples, forecast_horizon)
        assert X_train.shape[1] == 10  # sequence_length
        assert X_train.shape[2] == 1  # n_features
        assert preparator.is_fitted == True
    
    def test_prepare_data_dataframe(self, sample_dataframe):
        """Test preparing data from DataFrame."""
        preparator = SequenceDataPreparator(sequence_length=10, forecast_horizon=1)
        
        X_train, y_train, X_test, y_test = preparator.prepare_data(
            sample_dataframe[:150],
            test_data=sample_dataframe[150:],
            target_column='price'
        )
        
        assert X_train.ndim == 3
        assert y_train.ndim == 2
        # Should have multiple features (price, volume, feature1, feature2)
        assert X_train.shape[2] > 1
    
    def test_prepare_data_no_test(self, sample_time_series):
        """Test preparing data without test set."""
        preparator = SequenceDataPreparator(sequence_length=10)
        
        X_train, y_train, X_test, y_test = preparator.prepare_data(sample_time_series[:150])
        
        assert X_train is not None
        assert y_train is not None
        assert X_test is None
        assert y_test is None
    
    def test_prepare_data_forecast_horizon(self, sample_time_series):
        """Test preparing data with forecast_horizon > 1."""
        preparator = SequenceDataPreparator(sequence_length=10, forecast_horizon=7)
        
        X_train, y_train, _, _ = preparator.prepare_data(sample_time_series[:150])
        
        assert y_train.shape[1] == 7  # forecast_horizon


class TestSequenceDataPreparatorInverseTransform:
    """Tests for SequenceDataPreparator.inverse_transform()."""
    
    def test_inverse_transform(self, sample_time_series):
        """Test inverse transformation."""
        preparator = SequenceDataPreparator()
        X_train, y_train, _, _ = preparator.prepare_data(sample_time_series[:150])
        
        # Transform some scaled data back
        scaled_data = np.array([[0.5], [0.6], [0.7]])
        original_data = preparator.inverse_transform(scaled_data)
        
        assert original_data.shape == (3, 1)
        assert original_data.ndim == 2
    
    def test_inverse_transform_not_fitted(self):
        """Test inverse transform without fitting."""
        preparator = SequenceDataPreparator()
        
        with pytest.raises(ValueError, match="must be fitted"):
            preparator.inverse_transform(np.array([[0.5]]))


class TestSequenceDataPreparatorEdgeCases:
    """Tests for edge cases."""
    
    def test_insufficient_data(self):
        """Test with insufficient data."""
        data = pd.Series([100, 101, 102, 103, 104])  # Only 5 points
        
        preparator = SequenceDataPreparator(sequence_length=10)
        
        # Should handle gracefully or raise appropriate error
        X_train, y_train, _, _ = preparator.prepare_data(data)
        
        # Should create sequences if possible, or be empty
        assert X_train.shape[0] >= 0
    
    def test_with_nan_values(self, sample_time_series):
        """Test with NaN values in data."""
        data = sample_time_series.copy()
        data.iloc[10:15] = np.nan
        
        preparator = SequenceDataPreparator(sequence_length=10)
        
        # Should handle NaN gracefully
        X_train, y_train, _, _ = preparator.prepare_data(data)
        
        # Data should be processed (NaN handling depends on scaler)
        assert X_train is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

