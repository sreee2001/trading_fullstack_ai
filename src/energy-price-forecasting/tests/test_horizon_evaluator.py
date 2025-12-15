"""
Unit tests for horizon evaluator.

Tests HorizonEvaluator class.

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
    from multi_horizon.horizon_evaluator import HorizonEvaluator
    EVALUATOR_AVAILABLE = True
except ImportError:
    EVALUATOR_AVAILABLE = False
    pytest.skip("Multi-horizon module not available", allow_module_level=True)


@pytest.fixture
def sample_predictions():
    """Create sample predictions."""
    return {
        1: np.array([100, 101, 102, 103, 104]),
        7: np.array([105, 106, 107, 108, 109]),
        30: np.array([110, 111, 112, 113, 114])
    }


@pytest.fixture
def sample_true_values():
    """Create sample true values."""
    return np.array([100, 101, 102, 103, 104])


class TestHorizonEvaluatorInitialization:
    """Tests for HorizonEvaluator initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        evaluator = HorizonEvaluator(horizons=[1, 7, 30])
        
        assert evaluator.horizons == [1, 7, 30]
        assert evaluator.evaluator is not None
    
    def test_init_default_horizons(self):
        """Test initialization with default horizons."""
        evaluator = HorizonEvaluator()
        
        assert evaluator.horizons == [1, 7, 30]


class TestHorizonEvaluatorEvaluate:
    """Tests for HorizonEvaluator evaluation methods."""
    
    def test_evaluate_horizon(self, sample_true_values):
        """Test evaluating a single horizon."""
        evaluator = HorizonEvaluator()
        
        y_pred = sample_true_values + np.random.randn(5) * 0.1
        
        results = evaluator.evaluate_horizon(sample_true_values, y_pred, horizon=1)
        
        assert 'horizon' in results
        assert results['horizon'] == 1
        assert 'MAE' in results or 'RMSE' in results
    
    def test_evaluate_all(self, sample_predictions, sample_true_values):
        """Test evaluating all horizons."""
        evaluator = HorizonEvaluator(horizons=[1, 7, 30])
        
        results = evaluator.evaluate_all(sample_true_values, sample_predictions)
        
        assert isinstance(results, dict)
        assert 1 in results
        assert 7 in results
        assert 30 in results
    
    def test_compare_horizons(self, sample_predictions, sample_true_values):
        """Test comparing horizons."""
        evaluator = HorizonEvaluator(horizons=[1, 7, 30])
        
        results = evaluator.evaluate_all(sample_true_values, sample_predictions)
        comparison = evaluator.compare_horizons(results, metric='RMSE')
        
        assert isinstance(comparison, pd.DataFrame)
        assert 'horizon' in comparison.columns
        assert 'value' in comparison.columns
    
    def test_get_summary(self, sample_predictions, sample_true_values):
        """Test getting summary statistics."""
        evaluator = HorizonEvaluator(horizons=[1, 7, 30])
        
        results = evaluator.evaluate_all(sample_true_values, sample_predictions)
        summary = evaluator.get_summary(results)
        
        assert 'horizons' in summary
        assert 'metrics' in summary


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

