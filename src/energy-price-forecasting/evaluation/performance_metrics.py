"""
Performance Metrics for Trading and Forecasting.

Calculates trading performance metrics including Sharpe ratio, Sortino ratio,
maximum drawdown, and other risk-adjusted returns.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """
    Calculate performance metrics for trading and forecasting.
    
    Provides comprehensive metrics including:
    - Return metrics (total, annualized, cumulative)
    - Risk metrics (volatility, Sharpe, Sortino)
    - Drawdown metrics (max drawdown, drawdown duration)
    - Accuracy metrics (directional accuracy, hit rate)
    
    Attributes:
        risk_free_rate: Risk-free rate for Sharpe/Sortino calculations
    
    Example:
        >>> metrics = PerformanceMetrics(risk_free_rate=0.02)
        >>> results = metrics.calculate_all(returns, prices)
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize PerformanceMetrics.
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 0.02 = 2%)
        """
        self.risk_free_rate = risk_free_rate
        
        logger.info(f"PerformanceMetrics initialized with risk_free_rate={risk_free_rate}")
    
    def calculate_returns(
        self,
        prices: pd.Series | np.ndarray
    ) -> pd.Series | np.ndarray:
        """
        Calculate returns from prices.
        
        Args:
            prices: Price series
        
        Returns:
            Returns series
        """
        if isinstance(prices, pd.Series):
            return prices.pct_change().dropna()
        else:
            return np.diff(prices) / prices[:-1]
    
    def calculate_sharpe_ratio(
        self,
        returns: pd.Series | np.ndarray,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: Returns series
            periods_per_year: Number of periods per year (default: 252 for daily)
        
        Returns:
            Sharpe ratio
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        if len(returns) == 0 or np.std(returns) == 0:
            return np.nan
        
        excess_returns = returns - (self.risk_free_rate / periods_per_year)
        sharpe = np.sqrt(periods_per_year) * np.mean(excess_returns) / np.std(returns)
        
        return sharpe
    
    def calculate_sortino_ratio(
        self,
        returns: pd.Series | np.ndarray,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate Sortino ratio (downside deviation only).
        
        Args:
            returns: Returns series
            periods_per_year: Number of periods per year (default: 252)
        
        Returns:
            Sortino ratio
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        if len(returns) == 0:
            return np.nan
        
        excess_returns = returns - (self.risk_free_rate / periods_per_year)
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or np.std(downside_returns) == 0:
            return np.nan
        
        sortino = np.sqrt(periods_per_year) * np.mean(excess_returns) / np.std(downside_returns)
        
        return sortino
    
    def calculate_max_drawdown(
        self,
        prices: pd.Series | np.ndarray
    ) -> Tuple[float, int, int]:
        """
        Calculate maximum drawdown.
        
        Args:
            prices: Price series
        
        Returns:
            Tuple of (max_drawdown, start_index, end_index)
        """
        if isinstance(prices, pd.Series):
            prices = prices.values
        
        # Calculate running maximum
        running_max = np.maximum.accumulate(prices)
        
        # Calculate drawdown
        drawdown = (prices - running_max) / running_max
        
        # Find maximum drawdown
        max_dd_idx = np.argmin(drawdown)
        max_drawdown = drawdown[max_dd_idx]
        
        # Find start of drawdown (peak before max_dd)
        peak_idx = np.argmax(prices[:max_dd_idx + 1]) if max_dd_idx > 0 else 0
        
        return abs(max_drawdown), peak_idx, max_dd_idx
    
    def calculate_directional_accuracy(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> float:
        """
        Calculate directional accuracy (percentage of correct direction predictions).
        
        Args:
            y_true: True price changes
            y_pred: Predicted price changes
        
        Returns:
            Directional accuracy (0-1)
        """
        if len(y_true) < 2 or len(y_pred) < 2:
            return np.nan
        
        # Calculate direction
        true_direction = np.diff(y_true) > 0
        pred_direction = np.diff(y_pred) > 0
        
        # Calculate accuracy
        accuracy = np.mean(true_direction == pred_direction)
        
        return accuracy
    
    def calculate_all(
        self,
        prices: Optional[pd.Series | np.ndarray] = None,
        returns: Optional[pd.Series | np.ndarray] = None,
        y_true: Optional[np.ndarray] = None,
        y_pred: Optional[np.ndarray] = None,
        periods_per_year: int = 252
    ) -> Dict[str, float]:
        """
        Calculate all performance metrics.
        
        Args:
            prices: Price series (optional if returns provided)
            returns: Returns series (optional if prices provided)
            y_true: True values for accuracy metrics (optional)
            y_pred: Predicted values for accuracy metrics (optional)
            periods_per_year: Number of periods per year
        
        Returns:
            Dictionary of all metrics
        """
        results = {}
        
        # Calculate returns if not provided
        if returns is None and prices is not None:
            returns = self.calculate_returns(prices)
        
        if returns is not None:
            # Return metrics
            if isinstance(returns, pd.Series):
                returns_array = returns.values
            else:
                returns_array = returns
            
            returns_array = returns_array[~np.isnan(returns_array)]
            
            if len(returns_array) > 0:
                results['total_return'] = np.prod(1 + returns_array) - 1
                results['annualized_return'] = (1 + results['total_return']) ** (periods_per_year / len(returns_array)) - 1
                results['volatility'] = np.std(returns_array) * np.sqrt(periods_per_year)
                
                # Risk-adjusted metrics
                results['sharpe_ratio'] = self.calculate_sharpe_ratio(returns_array, periods_per_year)
                results['sortino_ratio'] = self.calculate_sortino_ratio(returns_array, periods_per_year)
        
        # Drawdown metrics
        if prices is not None:
            max_dd, start_idx, end_idx = self.calculate_max_drawdown(prices)
            results['max_drawdown'] = max_dd
            results['max_drawdown_start'] = start_idx
            results['max_drawdown_end'] = end_idx
        
        # Accuracy metrics
        if y_true is not None and y_pred is not None:
            results['directional_accuracy'] = self.calculate_directional_accuracy(y_true, y_pred)
        
        return results

