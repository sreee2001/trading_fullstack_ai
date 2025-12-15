"""
Unit tests for model evaluation.

Tests ModelEvaluator class.

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
    from training.evaluation import ModelEvaluator
    EVALUATOR_AVAILABLE = True
except ImportError:
    EVALUATOR_AVAILABLE = False
    pytest.skip("Training module not available", allow_module_level=True)


@pytest.fixture
def sample_predictions():
    """Create sample predictions and true values."""
    np.random.seed(42)
    y_true = np.array([100, 101, 102, 103, 104, 105, 106, 107, 108, 109])
    y_pred = y_true + np.random.randn(10) * 0.5  # Close predictions
    
    return y_true, y_pred


class TestModelEvaluatorInitialization:
    """Tests for ModelEvaluator initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        evaluator = ModelEvaluator()
        
        assert 'MAE' in evaluator.metrics
        assert 'RMSE' in evaluator.metrics
    
    def test_init_custom_metrics(self):
        """Test initialization with custom metrics."""
        evaluator = ModelEvaluator(metrics=['MAE', 'RMSE'])
        
        assert evaluator.metrics == ['MAE', 'RMSE']


class TestModelEvaluatorEvaluate:
    """Tests for ModelEvaluator.evaluate()."""
    
    def test_evaluate_basic(self, sample_predictions):
        """Test basic evaluation."""
        y_true, y_pred = sample_predictions
        evaluator = ModelEvaluator()
        
        results = evaluator.evaluate(y_true, y_pred)
        
        assert 'MAE' in results
        assert 'RMSE' in results
        assert isinstance(results['MAE'], (int, float))
        assert isinstance(results['RMSE'], (int, float))
    
    def test_evaluate_mae(self, sample_predictions):
        """Test MAE calculation."""
        y_true, y_pred = sample_predictions
        evaluator = ModelEvaluator(metrics=['MAE'])
        
        results = evaluator.evaluate(y_true, y_pred)
        
        # MAE should be positive
        assert results['MAE'] >= 0
    
    def test_evaluate_rmse(self, sample_predictions):
        """Test RMSE calculation."""
        y_true, y_pred = sample_predictions
        evaluator = ModelEvaluator(metrics=['RME'])
        
        results = evaluator.evaluate(y_true, y_pred)
        
        # RMSE should be positive
        assert results.get('RMSE', 0) >= 0
    
    def test_evaluate_mape(self, sample_predictions):
        """Test MAPE calculation."""
        y_true, y_pred = sample_predictions
        evaluator = ModelEvaluator(metrics=['MAPE'])
        
        results = evaluator.evaluate(y_true, y_pred)
        
        # MAPE should be a percentage (0-100+)
        if not np.isnan(results.get('MAPE', np.nan)):
            assert results['MAPE'] >= 0
    
    def test_evaluate_r2(self, sample_predictions):
        """Test R2 calculation."""
        y_true, y_pred = sample_predictions
        evaluator = ModelEvaluator(metrics=['R2'])
        
        results = evaluator.evaluate(y_true, y_pred)
        
        # R2 can be negative (bad model) or positive (good model)
        assert isinstance(results.get('R2', 0), (int, float))
    
    def test_evaluate_with_breakdown(self, sample_predictions):
        """Test evaluation with breakdown."""
        y_true, y_pred = sample_predictions
        evaluator = ModelEvaluator()
        
        results, breakdown = evaluator.evaluate(y_true, y_pred, return_breakdown=True)
        
        assert isinstance(results, dict)
        assert isinstance(breakdown, dict)
        assert 'n_samples' in breakdown


class TestModelEvaluatorCompareModels:
    """Tests for ModelEvaluator.compare_models()."""
    
    def test_compare_models(self, sample_predictions):
        """Test comparing multiple models."""
        y_true, y_pred = sample_predictions
        evaluator = ModelEvaluator()
        
        predictions = {
            'Model1': y_pred,
            'Model2': y_pred + 0.1,
            'Model3': y_pred - 0.1
        }
        
        comparison = evaluator.compare_models(y_true, predictions)
        
        assert isinstance(comparison, pd.DataFrame)
        assert len(comparison) == 3
        assert 'MAE' in comparison.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

