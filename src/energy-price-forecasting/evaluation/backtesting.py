"""
Backtesting Engine.

Simulates trading strategies based on model predictions.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable, Any
import logging
from datetime import datetime

from .performance_metrics import PerformanceMetrics

logger = logging.getLogger(__name__)


class BacktestingEngine:
    """
    Backtesting engine for trading strategies.
    
    Simulates trading based on model predictions and calculates
    performance metrics.
    
    Attributes:
        initial_capital: Starting capital
        commission: Commission per trade (as fraction)
        slippage: Slippage per trade (as fraction)
        metrics: PerformanceMetrics instance
    
    Example:
        >>> engine = BacktestingEngine(initial_capital=10000)
        >>> results = engine.backtest(strategy, predictions, prices)
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0005
    ):
        """
        Initialize BacktestingEngine.
        
        Args:
            initial_capital: Starting capital (default: 10000)
            commission: Commission per trade as fraction (default: 0.001 = 0.1%)
            slippage: Slippage per trade as fraction (default: 0.0005 = 0.05%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.metrics = PerformanceMetrics()
        
        logger.info(
            f"BacktestingEngine initialized: capital={initial_capital}, "
            f"commission={commission}, slippage={slippage}"
        )
    
    def backtest(
        self,
        predictions: pd.Series | np.ndarray,
        prices: pd.Series | np.ndarray,
        strategy: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run backtest on predictions.
        
        Args:
            predictions: Model predictions
            prices: Actual prices
            strategy: Optional strategy function (default: buy on positive prediction)
        
        Returns:
            Dictionary with backtest results
        """
        logger.info("="*80)
        logger.info("STARTING BACKTEST")
        logger.info("="*80)
        
        # Convert to numpy arrays
        if isinstance(predictions, pd.Series):
            predictions = predictions.values
        if isinstance(prices, pd.Series):
            prices = prices.values
        
        # Align lengths
        min_len = min(len(predictions), len(prices))
        predictions = predictions[:min_len]
        prices = prices[:min_len]
        
        # Default strategy: buy if prediction > current price, sell otherwise
        if strategy is None:
            def default_strategy(pred, price):
                return 1 if pred > price else -1
            strategy = default_strategy
        
        # Initialize tracking
        capital = self.initial_capital
        position = 0  # 1 = long, -1 = short, 0 = flat
        trades = []
        equity_curve = [capital]
        
        # Simulate trading
        for i in range(1, len(predictions)):
            current_price = prices[i]
            previous_price = prices[i-1]
            prediction = predictions[i]
            
            # Generate signal
            signal = strategy(prediction, current_price)
            
            # Execute trade if signal changes
            if signal != position:
                # Close previous position
                if position != 0:
                    # Calculate P&L
                    if position == 1:  # Long
                        pnl = (current_price - previous_price) / previous_price
                    else:  # Short
                        pnl = (previous_price - current_price) / previous_price
                    
                    # Apply commission and slippage
                    pnl -= (self.commission + self.slippage)
                    
                    capital *= (1 + pnl)
                    
                    trades.append({
                        'entry_idx': i - 1,
                        'exit_idx': i,
                        'entry_price': previous_price,
                        'exit_price': current_price,
                        'position': position,
                        'pnl': pnl,
                        'capital': capital
                    })
                
                # Open new position
                position = signal
                capital *= (1 - self.commission - self.slippage)  # Pay costs
        
        # Close final position
        if position != 0 and len(prices) > 1:
            final_price = prices[-1]
            prev_price = prices[-2]
            
            if position == 1:  # Long
                pnl = (final_price - prev_price) / prev_price
            else:  # Short
                pnl = (prev_price - final_price) / prev_price
            
            pnl -= (self.commission + self.slippage)
            capital *= (1 + pnl)
            
            trades.append({
                'entry_idx': len(prices) - 2,
                'exit_idx': len(prices) - 1,
                'entry_price': prev_price,
                'exit_price': final_price,
                'position': position,
                'pnl': pnl,
                'capital': capital
            })
        
        # Calculate performance metrics
        equity_series = pd.Series(equity_curve + [capital])
        returns = equity_series.pct_change().dropna()
        
        performance = self.metrics.calculate_all(
            prices=equity_series.values,
            returns=returns.values
        )
        
        # Add backtest-specific metrics
        performance['total_trades'] = len(trades)
        performance['final_capital'] = capital
        performance['total_return'] = (capital - self.initial_capital) / self.initial_capital
        performance['win_rate'] = np.mean([t['pnl'] > 0 for t in trades]) if trades else 0
        
        logger.info(f"Backtest complete: {len(trades)} trades, {performance['total_return']*100:.2f}% return")
        
        return {
            'performance': performance,
            'trades': trades,
            'equity_curve': equity_series.values,
            'initial_capital': self.initial_capital,
            'final_capital': capital
        }

