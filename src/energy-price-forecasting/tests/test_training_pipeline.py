"""
Unit tests for training pipeline.

Tests TrainingPipeline class.

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
    from training.training_pipeline import TrainingPipeline
    from training.config import TrainingConfig
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False
    pytest.skip("Training module not available", allow_module_level=True)


# Mock model class for testing
class MockModel:
    """Mock model for testing."""
    def __init__(self):
        self.is_fitted = False
    
    def fit(self, train_data, validation_data=None, **kwargs):
        self.is_fitted = True
        return self
    
    def predict(self, test_data, **kwargs):
        # Return mock predictions
        if isinstance(test_data, pd.DataFrame):
            n = len(test_data)
        else:
            n = len(test_data)
        return np.random.randn(n) * 0.5 + 100


@pytest.fixture
def sample_time_series():
    """Create sample time series data."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    prices = 70 + np.cumsum(np.random.randn(200) * 0.5)
    
    return pd.Series(prices, index=dates, name='price')


@pytest.fixture
def mock_model_factory():
    """Create mock model factory."""
    return lambda: MockModel()


class TestTrainingPipelineInitialization:
    """Tests for TrainingPipeline initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        pipeline = TrainingPipeline()
        
        assert pipeline.splitter is not None
        assert pipeline.evaluator is not None
        assert pipeline.config is not None
    
    def test_init_with_config(self):
        """Test initialization with config."""
        config = TrainingConfig()
        pipeline = TrainingPipeline(config=config)
        
        assert pipeline.config == config


class TestTrainingPipelineTrain:
    """Tests for TrainingPipeline.train()."""
    
    def test_train_basic(self, sample_time_series, mock_model_factory):
        """Test basic training."""
        pipeline = TrainingPipeline()
        
        results = pipeline.train(mock_model_factory, sample_time_series)
        
        assert 'model_type' in results
        assert 'test_metrics' in results
        assert 'train_size' in results
        assert 'test_size' in results
    
    def test_train_with_dataframe(self, mock_model_factory):
        """Test training with DataFrame."""
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=200, freq='D'),
            'price': 70 + np.cumsum(np.random.randn(200) * 0.5)
        })
        
        pipeline = TrainingPipeline()
        results = pipeline.train(mock_model_factory, df, target_column='price')
        
        assert 'test_metrics' in results


class TestTrainingPipelineResults:
    """Tests for TrainingPipeline results."""
    
    def test_get_results(self, sample_time_series, mock_model_factory):
        """Test getting results."""
        pipeline = TrainingPipeline()
        pipeline.train(mock_model_factory, sample_time_series)
        
        results = pipeline.get_results()
        
        assert isinstance(results, dict)
        assert 'test_metrics' in results


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

