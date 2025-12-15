"""
Unit tests for unified hyperparameter tuner.

Tests HyperparameterTuner class.

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
    from hyperparameter_tuning.tuner import HyperparameterTuner
    TUNER_AVAILABLE = True
except ImportError:
    TUNER_AVAILABLE = False
    pytest.skip("Hyperparameter tuning module not available", allow_module_level=True)


# Mock model class for testing
class MockModel:
    """Mock model for testing."""
    def __init__(self, **params):
        self.params = params
        self.is_fitted = False
    
    def fit(self, train_data, **kwargs):
        self.is_fitted = True
        return self
    
    def predict(self, test_data, **kwargs):
        n = len(test_data) if isinstance(test_data, pd.DataFrame) else len(test_data)
        return np.random.randn(n) * 0.1 + 100


@pytest.fixture
def sample_data():
    """Create sample data."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    return pd.DataFrame({
        'date': dates,
        'price': 70 + np.cumsum(np.random.randn(100) * 0.5)
    })


@pytest.fixture
def mock_model_factory():
    """Create mock model factory."""
    return lambda **params: MockModel(**params)


class TestHyperparameterTunerInitialization:
    """Tests for HyperparameterTuner initialization."""
    
    def test_init_grid(self):
        """Test initialization with grid search."""
        tuner = HyperparameterTuner(method='grid')
        
        assert tuner.method == 'grid'
        assert tuner.tuner is not None
    
    def test_init_random(self):
        """Test initialization with random search."""
        tuner = HyperparameterTuner(method='random', n_iter=10)
        
        assert tuner.method == 'random'
        assert tuner.tuner.n_iter == 10
    
    def test_init_invalid_method(self):
        """Test initialization with invalid method."""
        with pytest.raises(ValueError, match="Unknown tuning method"):
            HyperparameterTuner(method='invalid')


class TestHyperparameterTunerTune:
    """Tests for HyperparameterTuner.tune()."""
    
    def test_tune_grid(self, sample_data, mock_model_factory):
        """Test tuning with grid search."""
        tuner = HyperparameterTuner(method='grid')
        
        train_data = sample_data[:70]
        val_data = sample_data[70:]
        
        # Use custom param space
        param_space = {
            'lstm_units': [50, 64],
            'dropout_rate': [0.2, 0.3]
        }
        
        best_params, best_model = tuner.tune(
            mock_model_factory,
            'lstm',
            train_data,
            val_data,
            target_column='price',
            param_space=param_space,
            verbose=0
        )
        
        assert best_params is not None
        assert best_model is not None
    
    def test_tune_random(self, sample_data, mock_model_factory):
        """Test tuning with random search."""
        tuner = HyperparameterTuner(method='random', n_iter=3)
        
        train_data = sample_data[:70]
        val_data = sample_data[70:]
        
        param_space = {
            'lstm_units': [50, 64, 128],
            'dropout_rate': [0.2, 0.3, 0.4]
        }
        
        best_params, best_model = tuner.tune(
            mock_model_factory,
            'lstm',
            train_data,
            val_data,
            target_column='price',
            param_space=param_space,
            verbose=0
        )
        
        assert best_params is not None
        assert best_model is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

