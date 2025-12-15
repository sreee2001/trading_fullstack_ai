"""
Unit tests for statistical metrics.

Tests StatisticalMetrics class.

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
    from evaluation.statistical_metrics import StatisticalMetrics
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    pytest.skip("Evaluation module not available", allow_module_level=True)


@pytest.fixture
def sample_predictions():
    """Create sample predictions and true values."""
    np.random.seed(42)
    y_true = np.array([100, 101, 102, 103, 104, 105, 106, 107, 108, 109])
    y_pred = y_true + np.random.randn(10) * 0.5
    
    return y_true, y_pred


class TestStatisticalMetricsInitialization:
    """Tests for StatisticalMetrics initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        metrics = StatisticalMetrics()
        
        assert 'RMSE' in metrics.metrics
        assert 'MAE' in metrics.metrics
    
    def test_init_custom_metrics(self):
        """Test initialization with custom metrics."""
        metrics = StatisticalMetrics(metrics=['RMSE', 'MAE'])
        
        assert metrics.metrics == ['RMSE', 'MAE']


class TestStatisticalMetricsCalculations:
    """Tests for StatisticalMetrics calculation methods."""
    
    def test_calculate_rmse(self, sample_predictions):
        """Test RMSE calculation."""
        y_true, y_pred = sample_predictions
        metrics = StatisticalMetrics()
        
        rmse = metrics.calculate_rmse(y_true, y_pred)
        
        assert isinstance(rmse, (int, float))
        assert rmse >= 0
    
    def test_calculate_mae(self, sample_predictions):
        """Test MAE calculation."""
        y_true, y_pred = sample_predictions
        metrics = StatisticalMetrics()
        
        mae = metrics.calculate_mae(y_true, y_pred)
        
        assert isinstance(mae, (int, float))
        assert mae >= 0
    
    def test_calculate_mape(self, sample_predictions):
        """Test MAPE calculation."""
        y_true, y_pred = sample_predictions
        metrics = StatisticalMetrics()
        
        mape = metrics.calculate_mape(y_true, y_pred)
        
        assert isinstance(mape, (int, float))
        assert mape >= 0 or np.isnan(mape)
    
    def test_calculate_r2(self, sample_predictions):
        """Test R² calculation."""
        y_true, y_pred = sample_predictions
        metrics = StatisticalMetrics()
        
        r2 = metrics.calculate_r2(y_true, y_pred)
        
        assert isinstance(r2, (int, float))
    
    def test_calculate_directional_accuracy(self, sample_predictions):
        """Test directional accuracy calculation."""
        y_true, y_pred = sample_predictions
        metrics = StatisticalMetrics()
        
        accuracy = metrics.calculate_directional_accuracy(y_true, y_pred)
        
        assert isinstance(accuracy, (int, float))
        assert 0 <= accuracy <= 100 or np.isnan(accuracy)


class TestStatisticalMetricsCalculateAll:
    """Tests for StatisticalMetrics.calculate_all()."""
    
    def test_calculate_all(self, sample_predictions):
        """Test calculating all metrics."""
        y_true, y_pred = sample_predictions
        metrics = StatisticalMetrics()
        
        results = metrics.calculate_all(y_true, y_pred)
        
        assert isinstance(results, dict)
        assert 'RMSE' in results or 'MAE' in results
    
    def test_calculate_per_horizon(self):
        """Test per-horizon metrics calculation."""
        metrics = StatisticalMetrics()
        
        y_true = {1: np.array([100, 101, 102]), 7: np.array([105, 106, 107])}
        y_pred = {1: np.array([100.5, 101.5, 102.5]), 7: np.array([105.5, 106.5, 107.5])}
        
        results = metrics.calculate_per_horizon(y_true, y_pred)
        
        assert isinstance(results, dict)
        assert 1 in results
        assert 7 in results
    
    def test_compare_models(self, sample_predictions):
        """Test model comparison."""
        y_true, _ = sample_predictions
        metrics = StatisticalMetrics()
        
        predictions = {
            'Model1': y_true + 0.1,
            'Model2': y_true + 0.2,
            'Model3': y_true + 0.3
        }
        
        comparison = metrics.compare_models(y_true, predictions)
        
        assert isinstance(comparison, pd.DataFrame)
        assert len(comparison) == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

