"""
Trading Signal Strategies.

Defines various trading signal generation strategies.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import numpy as np
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)


class SignalStrategies:
    """
    Collection of trading signal generation strategies.
    
    Provides various strategies for generating trading signals
    based on model predictions and price data.
    
    Example:
        >>> strategies = SignalStrategies()
        >>> signal = strategies.threshold_strategy(prediction, current_price, threshold=0.02)
    """
    
    @staticmethod
    def threshold_strategy(
        prediction: float,
        current_price: float,
        threshold: float = 0.02
    ) -> int:
        """
        Generate signal based on prediction threshold.
        
        Args:
            prediction: Predicted future price
            current_price: Current price
            threshold: Minimum price change threshold (default: 0.02 = 2%)
        
        Returns:
            Signal: 1 (buy), -1 (sell), 0 (hold)
        """
        price_change = (prediction - current_price) / current_price
        
        if price_change > threshold:
            return 1  # Buy
        elif price_change < -threshold:
            return -1  # Sell
        else:
            return 0  # Hold
    
    @staticmethod
    def momentum_strategy(
        prediction: float,
        current_price: float,
        recent_prices: np.ndarray,
        momentum_threshold: float = 0.01
    ) -> int:
        """
        Generate signal based on momentum and prediction.
        
        Args:
            prediction: Predicted future price
            current_price: Current price
            recent_prices: Array of recent prices for momentum calculation
            momentum_threshold: Momentum threshold (default: 0.01 = 1%)
        
        Returns:
            Signal: 1 (buy), -1 (sell), 0 (hold)
        """
        if len(recent_prices) < 2:
            return 0
        
        # Calculate momentum
        momentum = (current_price - recent_prices[-1]) / recent_prices[-1]
        
        # Combine prediction and momentum
        pred_change = (prediction - current_price) / current_price
        combined = (pred_change + momentum) / 2
        
        if combined > momentum_threshold:
            return 1  # Buy
        elif combined < -momentum_threshold:
            return -1  # Sell
        else:
            return 0  # Hold
    
    @staticmethod
    def mean_reversion_strategy(
        prediction: float,
        current_price: float,
        mean_price: float,
        std_price: float,
        z_score_threshold: float = 1.5
    ) -> int:
        """
        Generate signal based on mean reversion.
        
        Args:
            prediction: Predicted future price
            current_price: Current price
            mean_price: Mean price (e.g., from moving average)
            std_price: Standard deviation of prices
            z_score_threshold: Z-score threshold (default: 1.5)
        
        Returns:
            Signal: 1 (buy), -1 (sell), 0 (hold)
        """
        if std_price == 0:
            return 0
        
        z_score = (current_price - mean_price) / std_price
        
        # If price is far below mean, buy (expect reversion up)
        # If price is far above mean, sell (expect reversion down)
        if z_score < -z_score_threshold:
            return 1  # Buy (oversold)
        elif z_score > z_score_threshold:
            return -1  # Sell (overbought)
        else:
            return 0  # Hold
    
    @staticmethod
    def trend_following_strategy(
        prediction: float,
        current_price: float,
        trend_direction: float,
        trend_strength: float = 0.5
    ) -> int:
        """
        Generate signal based on trend following.
        
        Args:
            prediction: Predicted future price
            current_price: Current price
            trend_direction: Trend direction (-1 to 1, negative = down, positive = up)
            trend_strength: Trend strength threshold (default: 0.5)
        
        Returns:
            Signal: 1 (buy), -1 (sell), 0 (hold)
        """
        pred_change = (prediction - current_price) / current_price
        
        # Follow trend if strong and prediction agrees
        if trend_direction > trend_strength and pred_change > 0:
            return 1  # Buy (uptrend)
        elif trend_direction < -trend_strength and pred_change < 0:
            return -1  # Sell (downtrend)
        else:
            return 0  # Hold
    
    @staticmethod
    def combined_strategy(
        prediction: float,
        current_price: float,
        recent_prices: Optional[np.ndarray] = None,
        mean_price: Optional[float] = None,
        std_price: Optional[float] = None,
        weights: Optional[dict] = None
    ) -> int:
        """
        Generate signal using combined strategies.
        
        Args:
            prediction: Predicted future price
            current_price: Current price
            recent_prices: Array of recent prices
            mean_price: Mean price for mean reversion
            std_price: Standard deviation for mean reversion
            weights: Dictionary of strategy weights (default: equal weights)
        
        Returns:
            Signal: 1 (buy), -1 (sell), 0 (hold)
        """
        if weights is None:
            weights = {'threshold': 0.4, 'momentum': 0.3, 'mean_reversion': 0.3}
        
        signals = []
        weights_list = []
        
        # Threshold strategy
        threshold_signal = SignalStrategies.threshold_strategy(prediction, current_price)
        signals.append(threshold_signal)
        weights_list.append(weights.get('threshold', 0.33))
        
        # Momentum strategy
        if recent_prices is not None and len(recent_prices) >= 2:
            momentum_signal = SignalStrategies.momentum_strategy(
                prediction, current_price, recent_prices
            )
            signals.append(momentum_signal)
            weights_list.append(weights.get('momentum', 0.33))
        
        # Mean reversion strategy
        if mean_price is not None and std_price is not None and std_price > 0:
            mr_signal = SignalStrategies.mean_reversion_strategy(
                prediction, current_price, mean_price, std_price
            )
            signals.append(mr_signal)
            weights_list.append(weights.get('mean_reversion', 0.33))
        
        # Weighted average
        if signals:
            weights_array = np.array(weights_list)
            weights_array = weights_array / weights_array.sum()  # Normalize
            
            weighted_signal = np.sum(np.array(signals) * weights_array)
            
            if weighted_signal > 0.3:
                return 1  # Buy
            elif weighted_signal < -0.3:
                return -1  # Sell
            else:
                return 0  # Hold
        
        return 0

