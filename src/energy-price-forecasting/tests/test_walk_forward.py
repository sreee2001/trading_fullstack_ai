"""
Unit tests for walk-forward validation.

Tests WalkForwardValidator class.

Author: AI Assistant
Date: December 14, 2025
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from unittest.mock import Mock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from evaluation.walk_forward import WalkForwardValidator
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False
    pytest.skip("Evaluation module not available", allow_module_level=True)


@pytest.fixture
def sample_data():
    """Create sample time series data."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=500, freq='D')
    
    return pd.DataFrame({
        'date': dates,
        'price': 70 + np.cumsum(np.random.randn(500) * 0.5)
    })


# Mock model class for testing
class MockModel:
    """Mock model for testing."""
    def __init__(self):
        self.is_fitted = False
    
    def fit(self, train_data, **kwargs):
        self.is_fitted = True
        return self
    
    def predict(self, test_data, **kwargs):
        if isinstance(test_data, pd.DataFrame):
            n = len(test_data)
        else:
            n = len(test_data)
        return np.random.randn(n) * 0.5 + 100


@pytest.fixture
def mock_model_factory():
    """Create mock model factory."""
    return lambda: MockModel()


class TestWalkForwardValidatorInitialization:
    """Tests for WalkForwardValidator initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        validator = WalkForwardValidator()
        
        assert validator.train_window == 365
        assert validator.test_window == 30
        assert validator.step_size == 30
        assert validator.expanding == True
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        validator = WalkForwardValidator(
            train_window=180,
            test_window=15,
            step_size=15,
            expanding=False
        )
        
        assert validator.train_window == 180
        assert validator.test_window == 15
        assert validator.step_size == 15
        assert validator.expanding == False


class TestWalkForwardValidatorValidate:
    """Tests for WalkForwardValidator.validate()."""
    
    def test_validate_basic(self, sample_data, mock_model_factory):
        """Test basic walk-forward validation."""
        validator = WalkForwardValidator(
            train_window=100,
            test_window=20,
            step_size=20
        )
        
        results = validator.validate(
            mock_model_factory,
            sample_data,
            target_column='price'
        )
        
        assert 'results' in results
        assert 'n_folds' in results
        assert len(results['results']) > 0
    
    def test_validate_expanding_window(self, sample_data, mock_model_factory):
        """Test expanding window validation."""
        validator = WalkForwardValidator(
            train_window=100,
            test_window=20,
            step_size=20,
            expanding=True
        )
        
        results = validator.validate(
            mock_model_factory,
            sample_data,
            target_column='price'
        )
        
        # Check that train_start stays at 0 for expanding window
        for result in results['results']:
            if 'error' not in result:
                assert result['train_start'] == 0
    
    def test_validate_rolling_window(self, sample_data, mock_model_factory):
        """Test rolling window validation."""
        validator = WalkForwardValidator(
            train_window=100,
            test_window=20,
            step_size=20,
            expanding=False
        )
        
        results = validator.validate(
            mock_model_factory,
            sample_data,
            target_column='price'
        )
        
        # Check that train_start increases for rolling window
        train_starts = [r['train_start'] for r in results['results'] if 'error' not in r]
        if len(train_starts) > 1:
            assert train_starts[1] > train_starts[0]


class TestWalkForwardValidatorMetrics:
    """Tests for WalkForwardValidator.get_aggregated_metrics()."""
    
    def test_get_aggregated_metrics(self, sample_data, mock_model_factory):
        """Test getting aggregated metrics."""
        validator = WalkForwardValidator(
            train_window=100,
            test_window=20,
            step_size=20
        )
        
        results = validator.validate(
            mock_model_factory,
            sample_data,
            target_column='price'
        )
        
        metrics_df = validator.get_aggregated_metrics(results)
        
        assert isinstance(metrics_df, pd.DataFrame)
        assert len(metrics_df) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

