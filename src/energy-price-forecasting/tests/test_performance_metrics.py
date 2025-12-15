"""
Unit tests for performance metrics.

Tests PerformanceMetrics class.

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
    from evaluation.performance_metrics import PerformanceMetrics
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    pytest.skip("Evaluation module not available", allow_module_level=True)


@pytest.fixture
def sample_returns():
    """Create sample returns."""
    np.random.seed(42)
    return pd.Series(np.random.randn(100) * 0.02)


@pytest.fixture
def sample_prices():
    """Create sample prices."""
    np.random.seed(42)
    returns = np.random.randn(100) * 0.02
    prices = 100 * (1 + returns).cumprod()
    return pd.Series(prices)


class TestPerformanceMetricsInitialization:
    """Tests for PerformanceMetrics initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        metrics = PerformanceMetrics()
        
        assert metrics.risk_free_rate == 0.02
    
    def test_init_custom_rate(self):
        """Test initialization with custom risk-free rate."""
        metrics = PerformanceMetrics(risk_free_rate=0.03)
        
        assert metrics.risk_free_rate == 0.03


class TestPerformanceMetricsCalculations:
    """Tests for PerformanceMetrics calculation methods."""
    
    def test_calculate_returns(self, sample_prices):
        """Test calculating returns from prices."""
        metrics = PerformanceMetrics()
        
        returns = metrics.calculate_returns(sample_prices)
        
        assert isinstance(returns, pd.Series)
        assert len(returns) == len(sample_prices) - 1
    
    def test_calculate_sharpe_ratio(self, sample_returns):
        """Test calculating Sharpe ratio."""
        metrics = PerformanceMetrics()
        
        sharpe = metrics.calculate_sharpe_ratio(sample_returns)
        
        assert isinstance(sharpe, (int, float))
        assert not np.isnan(sharpe) or len(sample_returns) == 0
    
    def test_calculate_sortino_ratio(self, sample_returns):
        """Test calculating Sortino ratio."""
        metrics = PerformanceMetrics()
        
        sortino = metrics.calculate_sortino_ratio(sample_returns)
        
        assert isinstance(sortino, (int, float))
    
    def test_calculate_max_drawdown(self, sample_prices):
        """Test calculating maximum drawdown."""
        metrics = PerformanceMetrics()
        
        max_dd, start_idx, end_idx = metrics.calculate_max_drawdown(sample_prices)
        
        assert isinstance(max_dd, (int, float))
        assert max_dd >= 0
        assert isinstance(start_idx, (int, np.integer))
        assert isinstance(end_idx, (int, np.integer))
    
    def test_calculate_directional_accuracy(self):
        """Test calculating directional accuracy."""
        metrics = PerformanceMetrics()
        
        y_true = np.array([100, 101, 102, 101, 100])
        y_pred = np.array([100, 101.5, 101.5, 100.5, 99.5])
        
        accuracy = metrics.calculate_directional_accuracy(y_true, y_pred)
        
        assert isinstance(accuracy, (int, float))
        assert 0 <= accuracy <= 1


class TestPerformanceMetricsCalculateAll:
    """Tests for PerformanceMetrics.calculate_all()."""
    
    def test_calculate_all(self, sample_prices, sample_returns):
        """Test calculating all metrics."""
        metrics = PerformanceMetrics()
        
        results = metrics.calculate_all(
            prices=sample_prices,
            returns=sample_returns
        )
        
        assert isinstance(results, dict)
        assert 'total_return' in results or 'sharpe_ratio' in results


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

