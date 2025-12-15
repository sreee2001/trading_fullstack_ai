"""
Trading Simulation Engine.

Enhanced trading simulation with detailed P&L tracking and win rate calculation.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable, Any, Tuple
import logging
from datetime import datetime

from .backtesting import BacktestingEngine
from .performance_metrics import PerformanceMetrics

logger = logging.getLogger(__name__)


class TradingSimulator:
    """
    Enhanced trading simulation engine.
    
    Provides detailed P&L tracking, win rate calculation, and
    comprehensive trade analysis.
    
    Attributes:
        engine: BacktestingEngine instance
        metrics: PerformanceMetrics instance
    
    Example:
        >>> simulator = TradingSimulator(initial_capital=10000)
        >>> results = simulator.simulate(signals, prices)
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0005
    ):
        """
        Initialize TradingSimulator.
        
        Args:
            initial_capital: Starting capital (default: 10000)
            commission: Commission per trade as fraction (default: 0.001)
            slippage: Slippage per trade as fraction (default: 0.0005)
        """
        self.engine = BacktestingEngine(initial_capital, commission, slippage)
        self.metrics = PerformanceMetrics()
        
        logger.info("TradingSimulator initialized")
    
    def simulate(
        self,
        signals: pd.Series | np.ndarray,
        prices: pd.Series | np.ndarray,
        position_size: float = 1.0
    ) -> Dict[str, Any]:
        """
        Simulate trading based on signals.
        
        Args:
            signals: Trading signals (1 = buy, -1 = sell, 0 = hold)
            prices: Price series
            position_size: Position size as fraction of capital (default: 1.0 = 100%)
        
        Returns:
            Dictionary with simulation results
        """
        logger.info("="*80)
        logger.info("STARTING TRADING SIMULATION")
        logger.info("="*80)
        
        # Convert to numpy arrays
        if isinstance(signals, pd.Series):
            signals = signals.values
        if isinstance(prices, pd.Series):
            prices = prices.values
        
        # Align lengths
        min_len = min(len(signals), len(prices))
        signals = signals[:min_len]
        prices = prices[:min_len]
        
        # Initialize tracking
        capital = self.engine.initial_capital
        position = 0  # 1 = long, -1 = short, 0 = flat
        trades = []
        equity_curve = [capital]
        positions = []
        
        # Simulate trading
        for i in range(1, len(signals)):
            current_price = prices[i]
            previous_price = prices[i-1]
            signal = signals[i]
            
            # Execute trade if signal changes
            if signal != position and signal != 0:
                # Close previous position
                if position != 0:
                    # Calculate P&L
                    if position == 1:  # Long
                        pnl_pct = (current_price - previous_price) / previous_price
                    else:  # Short
                        pnl_pct = (previous_price - current_price) / previous_price
                    
                    # Apply commission and slippage
                    pnl_pct -= (self.engine.commission + self.engine.slippage)
                    
                    # Calculate P&L in dollars
                    position_value = capital * position_size
                    pnl_dollars = position_value * pnl_pct
                    capital += pnl_dollars
                    
                    trades.append({
                        'entry_idx': i - 1,
                        'exit_idx': i,
                        'entry_price': previous_price,
                        'exit_price': current_price,
                        'position': position,
                        'pnl_pct': pnl_pct,
                        'pnl_dollars': pnl_dollars,
                        'capital_after': capital,
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Open new position
                position = signal
                capital *= (1 - self.engine.commission - self.engine.slippage)  # Pay costs
            
            positions.append(position)
            equity_curve.append(capital)
        
        # Close final position
        if position != 0 and len(prices) > 1:
            final_price = prices[-1]
            prev_price = prices[-2]
            
            if position == 1:  # Long
                pnl_pct = (final_price - prev_price) / prev_price
            else:  # Short
                pnl_pct = (prev_price - final_price) / prev_price
            
            pnl_pct -= (self.engine.commission + self.engine.slippage)
            position_value = capital * position_size
            pnl_dollars = position_value * pnl_pct
            capital += pnl_dollars
            
            trades.append({
                'entry_idx': len(prices) - 2,
                'exit_idx': len(prices) - 1,
                'entry_price': prev_price,
                'exit_price': final_price,
                'position': position,
                'pnl_pct': pnl_pct,
                'pnl_dollars': pnl_dollars,
                'capital_after': capital,
                'timestamp': datetime.now().isoformat()
            })
        
        # Calculate performance metrics
        equity_series = pd.Series(equity_curve)
        returns = equity_series.pct_change().dropna()
        
        performance = self.metrics.calculate_all(
            prices=equity_series.values,
            returns=returns.values
        )
        
        # Calculate additional metrics
        if trades:
            winning_trades = [t for t in trades if t['pnl_dollars'] > 0]
            losing_trades = [t for t in trades if t['pnl_dollars'] < 0]
            
            performance['total_trades'] = len(trades)
            performance['winning_trades'] = len(winning_trades)
            performance['losing_trades'] = len(losing_trades)
            performance['win_rate'] = len(winning_trades) / len(trades) if trades else 0
            performance['avg_win'] = np.mean([t['pnl_dollars'] for t in winning_trades]) if winning_trades else 0
            performance['avg_loss'] = np.mean([t['pnl_dollars'] for t in losing_trades]) if losing_trades else 0
            performance['profit_factor'] = abs(sum([t['pnl_dollars'] for t in winning_trades]) / 
                                             sum([t['pnl_dollars'] for t in losing_trades])) if losing_trades else np.inf
        else:
            performance['total_trades'] = 0
            performance['winning_trades'] = 0
            performance['losing_trades'] = 0
            performance['win_rate'] = 0
            performance['avg_win'] = 0
            performance['avg_loss'] = 0
            performance['profit_factor'] = 0
        
        performance['final_capital'] = capital
        performance['total_return'] = (capital - self.engine.initial_capital) / self.engine.initial_capital
        
        logger.info(f"Simulation complete: {len(trades)} trades, {performance['total_return']*100:.2f}% return")
        
        return {
            'performance': performance,
            'trades': trades,
            'equity_curve': equity_series.values,
            'positions': positions,
            'initial_capital': self.engine.initial_capital,
            'final_capital': capital
        }
    
    def get_trade_statistics(self, trades: List[Dict]) -> Dict[str, Any]:
        """
        Get detailed trade statistics.
        
        Args:
            trades: List of trade dictionaries
        
        Returns:
            Dictionary with trade statistics
        """
        if not trades:
            return {}
        
        df = pd.DataFrame(trades)
        
        stats = {
            'total_trades': len(trades),
            'winning_trades': len(df[df['pnl_dollars'] > 0]),
            'losing_trades': len(df[df['pnl_dollars'] < 0]),
            'win_rate': len(df[df['pnl_dollars'] > 0]) / len(trades),
            'total_pnl': df['pnl_dollars'].sum(),
            'avg_pnl': df['pnl_dollars'].mean(),
            'max_win': df['pnl_dollars'].max(),
            'max_loss': df['pnl_dollars'].min(),
            'avg_win': df[df['pnl_dollars'] > 0]['pnl_dollars'].mean() if len(df[df['pnl_dollars'] > 0]) > 0 else 0,
            'avg_loss': df[df['pnl_dollars'] < 0]['pnl_dollars'].mean() if len(df[df['pnl_dollars'] < 0]) > 0 else 0,
            'profit_factor': abs(df[df['pnl_dollars'] > 0]['pnl_dollars'].sum() / 
                                df[df['pnl_dollars'] < 0]['pnl_dollars'].sum()) if len(df[df['pnl_dollars'] < 0]) > 0 else np.inf
        }
        
        return stats

