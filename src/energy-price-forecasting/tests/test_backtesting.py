"""
Unit tests for backtesting engine.

Tests BacktestingEngine class.

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
    from evaluation.backtesting import BacktestingEngine
    BACKTESTING_AVAILABLE = True
except ImportError:
    BACKTESTING_AVAILABLE = False
    pytest.skip("Evaluation module not available", allow_module_level=True)


@pytest.fixture
def sample_predictions():
    """Create sample predictions."""
    np.random.seed(42)
    return pd.Series(100 + np.cumsum(np.random.randn(100) * 0.5))


@pytest.fixture
def sample_prices():
    """Create sample prices."""
    np.random.seed(42)
    returns = np.random.randn(100) * 0.02
    prices = 100 * (1 + returns).cumprod()
    return pd.Series(prices)


class TestBacktestingEngineInitialization:
    """Tests for BacktestingEngine initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        engine = BacktestingEngine()
        
        assert engine.initial_capital == 10000.0
        assert engine.commission == 0.001
        assert engine.slippage == 0.0005
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        engine = BacktestingEngine(
            initial_capital=50000.0,
            commission=0.002,
            slippage=0.001
        )
        
        assert engine.initial_capital == 50000.0
        assert engine.commission == 0.002
        assert engine.slippage == 0.001


class TestBacktestingEngineBacktest:
    """Tests for BacktestingEngine.backtest()."""
    
    def test_backtest_basic(self, sample_predictions, sample_prices):
        """Test basic backtest."""
        engine = BacktestingEngine(initial_capital=10000.0)
        
        results = engine.backtest(sample_predictions, sample_prices)
        
        assert 'performance' in results
        assert 'trades' in results
        assert 'equity_curve' in results
        assert 'final_capital' in results
    
    def test_backtest_custom_strategy(self, sample_predictions, sample_prices):
        """Test backtest with custom strategy."""
        def custom_strategy(pred, price):
            return 1 if pred > price * 1.01 else -1
        
        engine = BacktestingEngine()
        
        results = engine.backtest(
            sample_predictions,
            sample_prices,
            strategy=custom_strategy
        )
        
        assert 'performance' in results
        assert 'total_trades' in results['performance']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

