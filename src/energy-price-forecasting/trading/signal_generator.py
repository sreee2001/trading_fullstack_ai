"""
Trading Signal Generator.

Generates trading signals from model predictions.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable, Any
import logging

from .signal_strategies import SignalStrategies

logger = logging.getLogger(__name__)


class SignalGenerator:
    """
    Generate trading signals from model predictions.
    
    Converts model predictions into actionable trading signals
    using various strategies.
    
    Attributes:
        strategy: Strategy function for signal generation
        strategy_name: Name of the strategy
    
    Example:
        >>> generator = SignalGenerator(strategy='threshold', threshold=0.02)
        >>> signals = generator.generate(predictions, prices)
    """
    
    def __init__(
        self,
        strategy: str | Callable = 'threshold',
        **strategy_kwargs
    ):
        """
        Initialize SignalGenerator.
        
        Args:
            strategy: Strategy name ('threshold', 'momentum', 'mean_reversion', 'trend_following', 'combined')
                     or custom strategy function
            **strategy_kwargs: Additional arguments for the strategy
        """
        self.strategy_kwargs = strategy_kwargs
        
        if isinstance(strategy, str):
            self.strategy_name = strategy
            self.strategy = self._get_strategy(strategy)
        else:
            self.strategy_name = 'custom'
            self.strategy = strategy
        
        logger.info(f"SignalGenerator initialized with strategy: {self.strategy_name}")
    
    def _get_strategy(self, strategy_name: str) -> Callable:
        """
        Get strategy function by name.
        
        Args:
            strategy_name: Name of the strategy
        
        Returns:
            Strategy function
        """
        strategies = {
            'threshold': self._threshold_strategy,
            'momentum': self._momentum_strategy,
            'mean_reversion': self._mean_reversion_strategy,
            'trend_following': self._trend_following_strategy,
            'combined': self._combined_strategy
        }
        
        if strategy_name not in strategies:
            raise ValueError(
                f"Unknown strategy: {strategy_name}. "
                f"Available: {list(strategies.keys())}"
            )
        
        return strategies[strategy_name]
    
    def _threshold_strategy(self, prediction: float, current_price: float) -> int:
        """Threshold-based strategy."""
        threshold = self.strategy_kwargs.get('threshold', 0.02)
        return SignalStrategies.threshold_strategy(prediction, current_price, threshold)
    
    def _momentum_strategy(
        self,
        prediction: float,
        current_price: float,
        recent_prices: Optional[np.ndarray] = None
    ) -> int:
        """Momentum-based strategy."""
        momentum_threshold = self.strategy_kwargs.get('momentum_threshold', 0.01)
        return SignalStrategies.momentum_strategy(
            prediction, current_price, recent_prices or np.array([]), momentum_threshold
        )
    
    def _mean_reversion_strategy(
        self,
        prediction: float,
        current_price: float,
        mean_price: Optional[float] = None,
        std_price: Optional[float] = None
    ) -> int:
        """Mean reversion strategy."""
        z_score_threshold = self.strategy_kwargs.get('z_score_threshold', 1.5)
        if mean_price is None or std_price is None:
            return 0
        return SignalStrategies.mean_reversion_strategy(
            prediction, current_price, mean_price, std_price, z_score_threshold
        )
    
    def _trend_following_strategy(
        self,
        prediction: float,
        current_price: float,
        trend_direction: Optional[float] = None
    ) -> int:
        """Trend following strategy."""
        trend_strength = self.strategy_kwargs.get('trend_strength', 0.5)
        if trend_direction is None:
            return 0
        return SignalStrategies.trend_following_strategy(
            prediction, current_price, trend_direction, trend_strength
        )
    
    def _combined_strategy(
        self,
        prediction: float,
        current_price: float,
        **kwargs
    ) -> int:
        """Combined strategy."""
        weights = self.strategy_kwargs.get('weights', None)
        return SignalStrategies.combined_strategy(
            prediction, current_price,
            recent_prices=kwargs.get('recent_prices'),
            mean_price=kwargs.get('mean_price'),
            std_price=kwargs.get('std_price'),
            weights=weights
        )
    
    def generate(
        self,
        predictions: pd.Series | np.ndarray,
        prices: pd.Series | np.ndarray,
        **additional_data
    ) -> pd.Series:
        """
        Generate trading signals from predictions.
        
        Args:
            predictions: Model predictions
            prices: Current prices (aligned with predictions)
            **additional_data: Additional data for strategies (recent_prices, mean_price, etc.)
        
        Returns:
            Series of trading signals (1 = buy, -1 = sell, 0 = hold)
        """
        # Convert to numpy arrays
        if isinstance(predictions, pd.Series):
            predictions = predictions.values
        if isinstance(prices, pd.Series):
            prices = prices.values
        
        # Align lengths
        min_len = min(len(predictions), len(prices))
        predictions = predictions[:min_len]
        prices = prices[:min_len]
        
        signals = []
        
        for i in range(len(predictions)):
            prediction = predictions[i]
            current_price = prices[i]
            
            # Prepare additional data for this point
            strategy_data = {}
            
            if 'recent_prices' in additional_data:
                recent = additional_data['recent_prices']
                if isinstance(recent, (list, np.ndarray)) and len(recent) > i:
                    strategy_data['recent_prices'] = recent[:i+1] if i > 0 else np.array([current_price])
            
            if 'mean_price' in additional_data:
                mean = additional_data['mean_price']
                if isinstance(mean, (list, np.ndarray)) and len(mean) > i:
                    strategy_data['mean_price'] = mean[i]
            
            if 'std_price' in additional_data:
                std = additional_data['std_price']
                if isinstance(std, (list, np.ndarray)) and len(std) > i:
                    strategy_data['std_price'] = std[i]
            
            if 'trend_direction' in additional_data:
                trend = additional_data['trend_direction']
                if isinstance(trend, (list, np.ndarray)) and len(trend) > i:
                    strategy_data['trend_direction'] = trend[i]
            
            # Generate signal
            try:
                signal = self.strategy(prediction, current_price, **strategy_data)
                signals.append(signal)
            except Exception as e:
                logger.error(f"Error generating signal at index {i}: {e}")
                signals.append(0)  # Default to hold
        
        return pd.Series(signals, index=range(len(signals)))
    
    def generate_single(
        self,
        prediction: float,
        current_price: float,
        **additional_data
    ) -> int:
        """
        Generate a single trading signal.
        
        Args:
            prediction: Model prediction
            current_price: Current price
            **additional_data: Additional data for strategies
        
        Returns:
            Trading signal (1 = buy, -1 = sell, 0 = hold)
        """
        return self.strategy(prediction, current_price, **additional_data)
    
    def get_signal_summary(self, signals: pd.Series) -> Dict[str, Any]:
        """
        Get summary statistics for signals.
        
        Args:
            signals: Series of trading signals
        
        Returns:
            Dictionary with signal statistics
        """
        signals_array = signals.values if isinstance(signals, pd.Series) else signals
        
        return {
            'total_signals': len(signals_array),
            'buy_signals': int(np.sum(signals_array == 1)),
            'sell_signals': int(np.sum(signals_array == -1)),
            'hold_signals': int(np.sum(signals_array == 0)),
            'buy_percentage': (np.sum(signals_array == 1) / len(signals_array)) * 100,
            'sell_percentage': (np.sum(signals_array == -1) / len(signals_array)) * 100,
            'hold_percentage': (np.sum(signals_array == 0) / len(signals_array)) * 100
        }

