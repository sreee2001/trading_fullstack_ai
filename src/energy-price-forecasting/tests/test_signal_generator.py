"""
Unit tests for trading signal generation.

Tests SignalGenerator and SignalStrategies classes.

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
    from trading.signal_generator import SignalGenerator
    from trading.signal_strategies import SignalStrategies
    SIGNAL_AVAILABLE = True
except ImportError:
    SIGNAL_AVAILABLE = False
    pytest.skip("Trading module not available", allow_module_level=True)


class TestSignalStrategies:
    """Tests for SignalStrategies static methods."""
    
    def test_threshold_strategy_buy(self):
        """Test threshold strategy - buy signal."""
        signal = SignalStrategies.threshold_strategy(
            prediction=102,
            current_price=100,
            threshold=0.01
        )
        
        assert signal == 1  # Buy
    
    def test_threshold_strategy_sell(self):
        """Test threshold strategy - sell signal."""
        signal = SignalStrategies.threshold_strategy(
            prediction=98,
            current_price=100,
            threshold=0.01
        )
        
        assert signal == -1  # Sell
    
    def test_threshold_strategy_hold(self):
        """Test threshold strategy - hold signal."""
        signal = SignalStrategies.threshold_strategy(
            prediction=100.5,
            current_price=100,
            threshold=0.01
        )
        
        assert signal == 0  # Hold
    
    def test_momentum_strategy(self):
        """Test momentum strategy."""
        recent_prices = np.array([98, 99, 100])
        signal = SignalStrategies.momentum_strategy(
            prediction=102,
            current_price=100,
            recent_prices=recent_prices,
            momentum_threshold=0.01
        )
        
        assert signal in [-1, 0, 1]


class TestSignalGeneratorInitialization:
    """Tests for SignalGenerator initialization."""
    
    def test_init_threshold_strategy(self):
        """Test initialization with threshold strategy."""
        generator = SignalGenerator(strategy='threshold', threshold=0.02)
        
        assert generator.strategy_name == 'threshold'
        assert generator.strategy is not None
    
    def test_init_invalid_strategy(self):
        """Test initialization with invalid strategy."""
        with pytest.raises(ValueError, match="Unknown strategy"):
            SignalGenerator(strategy='invalid')


class TestSignalGeneratorGenerate:
    """Tests for SignalGenerator.generate()."""
    
    def test_generate_basic(self):
        """Test basic signal generation."""
        predictions = pd.Series([102, 98, 101, 99])
        prices = pd.Series([100, 100, 100, 100])
        
        generator = SignalGenerator(strategy='threshold', threshold=0.01)
        signals = generator.generate(predictions, prices)
        
        assert isinstance(signals, pd.Series)
        assert len(signals) == len(predictions)
        assert all(s in [-1, 0, 1] for s in signals.values)
    
    def test_get_signal_summary(self):
        """Test signal summary generation."""
        signals = pd.Series([1, 1, -1, 0, 0, 1])
        
        generator = SignalGenerator(strategy='threshold')
        summary = generator.get_signal_summary(signals)
        
        assert 'total_signals' in summary
        assert 'buy_signals' in summary
        assert 'sell_signals' in summary
        assert summary['buy_signals'] == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

