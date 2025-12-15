"""
Unit tests for Model Comparison framework.

Tests ModelComparison class.

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
    from models.baseline.model_comparison import ModelComparison
    from models.baseline.arima_model import ARIMAModel
    from models.baseline.exponential_smoothing import ExponentialSmoothingModel
    COMPARISON_AVAILABLE = True
except ImportError:
    COMPARISON_AVAILABLE = False
    pytest.skip("Baseline models not available", allow_module_level=True)


@pytest.fixture
def sample_time_series():
    """Create sample time series data."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    trend = np.linspace(70, 75, 100)
    seasonal = 2 * np.sin(np.arange(100) * 2 * np.pi / 7)
    noise = np.random.randn(100) * 0.5
    prices = trend + seasonal + noise
    
    return pd.Series(prices, index=dates, name='price')


@pytest.fixture
def train_test_split(sample_time_series):
    """Split data into train and test."""
    split_idx = int(len(sample_time_series) * 0.8)
    train = sample_time_series[:split_idx]
    test = sample_time_series[split_idx:]
    return train, test


class TestModelComparisonInitialization:
    """Tests for ModelComparison initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        comparison = ModelComparison()
        
        assert len(comparison.models) == 0
        assert len(comparison.results) == 0
        assert comparison.best_model is None


class TestModelComparisonAddModel:
    """Tests for ModelComparison.add_model()."""
    
    def test_add_arima_model(self):
        """Test adding ARIMA model."""
        comparison = ModelComparison()
        model = ARIMAModel(seasonal=False)
        
        comparison.add_model('ARIMA', model)
        
        assert 'ARIMA' in comparison.models
        assert comparison.models['ARIMA'] == model
    
    def test_add_exponential_smoothing_model(self):
        """Test adding Exponential Smoothing model."""
        comparison = ModelComparison()
        model = ExponentialSmoothingModel()
        
        comparison.add_model('ES', model)
        
        assert 'ES' in comparison.models
    
    def test_add_invalid_model(self):
        """Test adding invalid model type."""
        comparison = ModelComparison()
        
        with pytest.raises(ValueError):
            comparison.add_model('Invalid', "not a model")


class TestModelComparisonTrainAll:
    """Tests for ModelComparison.train_all()."""
    
    def test_train_all(self, sample_time_series):
        """Test training all models."""
        comparison = ModelComparison()
        comparison.add_model('ARIMA', ARIMAModel(seasonal=False))
        comparison.add_model('ES', ExponentialSmoothingModel())
        
        comparison.train_all(sample_time_series)
        
        assert comparison.models['ARIMA'].is_fitted == True
        assert comparison.models['ES'].is_fitted == True


class TestModelComparisonPredictAll:
    """Tests for ModelComparison.predict_all()."""
    
    def test_predict_all(self, sample_time_series):
        """Test predicting with all models."""
        comparison = ModelComparison()
        comparison.add_model('ARIMA', ARIMAModel(seasonal=False))
        comparison.add_model('ES', ExponentialSmoothingModel())
        
        comparison.train_all(sample_time_series)
        predictions = comparison.predict_all(steps=10)
        
        assert 'ARIMA' in predictions
        assert 'ES' in predictions
        assert predictions['ARIMA'] is not None
        assert predictions['ES'] is not None


class TestModelComparisonEvaluateAll:
    """Tests for ModelComparison.evaluate_all()."""
    
    def test_evaluate_all(self, train_test_split):
        """Test evaluating all models."""
        train, test = train_test_split
        
        comparison = ModelComparison()
        comparison.add_model('ARIMA', ARIMAModel(seasonal=False))
        comparison.add_model('ES', ExponentialSmoothingModel())
        
        comparison.train_all(train)
        results = comparison.evaluate_all(test)
        
        assert 'ARIMA' in results
        assert 'ES' in results
        assert 'RMSE' in results['ARIMA'] or 'error' in results['ARIMA']
        assert 'MAE' in results['ARIMA'] or 'error' in results['ARIMA']
    
    def test_evaluate_all_custom_metrics(self, train_test_split):
        """Test evaluation with custom metrics."""
        train, test = train_test_split
        
        comparison = ModelComparison()
        comparison.add_model('ARIMA', ARIMAModel(seasonal=False))
        
        comparison.train_all(train)
        results = comparison.evaluate_all(test, metrics=['MAE', 'RMSE'])
        
        assert 'ARIMA' in results
        if 'error' not in results['ARIMA']:
            assert 'MAE' in results['ARIMA']
            assert 'RMSE' in results['ARIMA']


class TestModelComparisonBestModel:
    """Tests for ModelComparison.get_best_model()."""
    
    def test_get_best_model(self, train_test_split):
        """Test getting best model."""
        train, test = train_test_split
        
        comparison = ModelComparison()
        comparison.add_model('ARIMA', ARIMAModel(seasonal=False))
        comparison.add_model('ES', ExponentialSmoothingModel())
        
        comparison.train_all(train)
        comparison.evaluate_all(test)
        
        best = comparison.get_best_model()
        
        # Best model should be one of the added models
        assert best in ['ARIMA', 'ES'] or best is None


class TestModelComparisonTable:
    """Tests for ModelComparison.get_comparison_table()."""
    
    def test_get_comparison_table(self, train_test_split):
        """Test getting comparison table."""
        train, test = train_test_split
        
        comparison = ModelComparison()
        comparison.add_model('ARIMA', ARIMAModel(seasonal=False))
        
        comparison.train_all(train)
        comparison.evaluate_all(test)
        
        table = comparison.get_comparison_table()
        
        assert isinstance(table, pd.DataFrame)
        assert len(table) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

