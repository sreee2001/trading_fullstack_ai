"""
Unit tests for random search hyperparameter tuning.

Tests RandomSearchTuner class.

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
    from hyperparameter_tuning.random_search import RandomSearchTuner
    RANDOM_SEARCH_AVAILABLE = True
except ImportError:
    RANDOM_SEARCH_AVAILABLE = False
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
        noise = self.params.get('noise_factor', 0.1)
        return np.random.randn(n) * noise + 100


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


class TestRandomSearchTunerInitialization:
    """Tests for RandomSearchTuner initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        tuner = RandomSearchTuner(n_iter=10)
        
        assert tuner.n_iter == 10
        assert tuner.scoring_metric == 'rmse'
    
    def test_init_with_random_state(self):
        """Test initialization with random state."""
        tuner = RandomSearchTuner(n_iter=10, random_state=42)
        
        assert tuner.random_state == 42


class TestRandomSearchTunerSearch:
    """Tests for RandomSearchTuner.search()."""
    
    def test_search_basic(self, sample_data, mock_model_factory):
        """Test basic random search."""
        tuner = RandomSearchTuner(n_iter=5, random_state=42)
        
        param_distributions = {
            'noise_factor': [0.1, 0.2, 0.3],
            'param2': [1, 2, 3]
        }
        
        train_data = sample_data[:70]
        val_data = sample_data[70:]
        
        best_params, best_model = tuner.search(
            mock_model_factory,
            param_distributions,
            train_data,
            val_data,
            target_column='price',
            verbose=0
        )
        
        assert best_params is not None
        assert best_model is not None
        assert len(tuner.results) == 5
    
    def test_search_n_iter(self, sample_data, mock_model_factory):
        """Test that n_iter trials are run."""
        tuner = RandomSearchTuner(n_iter=3, random_state=42)
        
        param_distributions = {'noise_factor': [0.1, 0.2]}
        
        train_data = sample_data[:70]
        val_data = sample_data[70:]
        
        tuner.search(
            mock_model_factory,
            param_distributions,
            train_data,
            val_data,
            target_column='price',
            verbose=0
        )
        
        assert len(tuner.results) == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

