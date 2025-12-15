"""
Unit tests for grid search hyperparameter tuning.

Tests GridSearchTuner class.

Author: AI Assistant
Date: December 14, 2025
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from hyperparameter_tuning.grid_search import GridSearchTuner
    GRID_SEARCH_AVAILABLE = True
except ImportError:
    GRID_SEARCH_AVAILABLE = False
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
        # Return mock predictions
        if isinstance(test_data, pd.DataFrame):
            n = len(test_data)
        else:
            n = len(test_data)
        # Add some noise based on params to make different scores
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


class TestGridSearchTunerInitialization:
    """Tests for GridSearchTuner initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        tuner = GridSearchTuner()
        
        assert tuner.scoring_metric == 'rmse'
        assert tuner.minimize == True
    
    def test_init_custom_metric(self):
        """Test initialization with custom metric."""
        tuner = GridSearchTuner(scoring_metric='mae', minimize=True)
        
        assert tuner.scoring_metric == 'mae'


class TestGridSearchTunerSearch:
    """Tests for GridSearchTuner.search()."""
    
    def test_search_basic(self, sample_data, mock_model_factory):
        """Test basic grid search."""
        tuner = GridSearchTuner(scoring_metric='rmse')
        
        param_grid = {
            'noise_factor': [0.1, 0.2],
            'param2': [1, 2]
        }
        
        train_data = sample_data[:70]
        val_data = sample_data[70:]
        
        best_params, best_model = tuner.search(
            mock_model_factory,
            param_grid,
            train_data,
            val_data,
            target_column='price',
            verbose=0
        )
        
        assert best_params is not None
        assert best_model is not None
        assert len(tuner.results) == 4  # 2 * 2 combinations
    
    def test_search_best_params(self, sample_data, mock_model_factory):
        """Test that best params are stored."""
        tuner = GridSearchTuner()
        
        param_grid = {'noise_factor': [0.1, 0.2]}
        
        train_data = sample_data[:70]
        val_data = sample_data[70:]
        
        best_params, _ = tuner.search(
            mock_model_factory,
            param_grid,
            train_data,
            val_data,
            target_column='price',
            verbose=0
        )
        
        assert tuner.best_params == best_params
        assert tuner.best_score is not None


class TestGridSearchTunerResults:
    """Tests for GridSearchTuner results."""
    
    def test_get_results_dataframe(self, sample_data, mock_model_factory):
        """Test getting results as DataFrame."""
        tuner = GridSearchTuner()
        
        param_grid = {'noise_factor': [0.1]}
        
        train_data = sample_data[:70]
        val_data = sample_data[70:]
        
        tuner.search(
            mock_model_factory,
            param_grid,
            train_data,
            val_data,
            target_column='price',
            verbose=0
        )
        
        results_df = tuner.get_results_dataframe()
        
        assert isinstance(results_df, pd.DataFrame)
        assert len(results_df) > 0
        assert 'params' in results_df.columns
        assert 'score' in results_df.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

