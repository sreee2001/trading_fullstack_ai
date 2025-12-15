"""
Backtesting Service.

This module provides services for running backtests via the API,
integrating with Epic 3's backtesting framework.
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, date
import pandas as pd
import numpy as np

from api.logging_config import get_logger
from api.services.model_service import get_model_service
from api.services.historical_data_service import get_historical_data_service
from evaluation.backtesting import BacktestingEngine
from trading.signal_generator import SignalGenerator

logger = get_logger(__name__)


class BacktestService:
    """
    Service for running backtests.
    
    Provides:
    - Load model and historical data
    - Generate predictions
    - Run backtesting using Epic 3 framework
    - Return formatted results
    """
    
    def __init__(self):
        """Initialize backtest service."""
        self.model_service = get_model_service()
        self.historical_service = get_historical_data_service()
        logger.info("BacktestService initialized")
    
    def run_backtest(
        self,
        model_id: str,
        start_date: date,
        end_date: date,
        initial_capital: float = 100000.0,
        commission: float = 0.001,
        slippage: float = 0.0005,
        strategy_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run a backtest for a model.
        
        Args:
            model_id: Model identifier (format: 'commodity_modeltype' or 'model_name:version')
            start_date: Start date for backtest period
            end_date: End date for backtest period
            initial_capital: Initial capital
            commission: Commission per trade as fraction
            slippage: Slippage per trade as fraction
            strategy_params: Strategy parameters (e.g., {'threshold': 0.02, 'strategy': 'momentum'})
            
        Returns:
            Dictionary with backtest results
        """
        logger.info(
            f"Running backtest: model_id={model_id}, "
            f"start_date={start_date}, end_date={end_date}, "
            f"initial_capital={initial_capital}"
        )
        
        try:
            # Parse model_id to extract commodity and model_type
            commodity, model_type = self._parse_model_id(model_id)
            
            # Load model
            logger.info(f"Loading model: {commodity} ({model_type})")
            model = self.model_service.load_model(
                commodity=commodity,
                model_type=model_type.lower()
            )
            
            if model is None:
                raise ValueError(f"Model not found: {model_id}")
            
            # Get historical data for the period
            logger.info(f"Retrieving historical data: {start_date} to {end_date}")
            price_points, _ = self.historical_service.get_historical_data(
                commodity=commodity,
                start_date=start_date,
                end_date=end_date,
                limit=10000,  # Large limit to get all data
                offset=0
            )
            
            if not price_points:
                raise ValueError(f"No historical data found for {commodity} in date range {start_date} to {end_date}")
            
            # Convert price points to DataFrame
            prices_df = pd.DataFrame(price_points)
            prices_df['date'] = pd.to_datetime(prices_df['date'])
            prices_df = prices_df.sort_values('date')
            prices = prices_df['price'].values
            
            # Generate predictions using the model
            logger.info("Generating predictions...")
            predictions = self._generate_predictions(model, prices_df, model_type)
            
            if len(predictions) != len(prices):
                # Align lengths
                min_len = min(len(predictions), len(prices))
                predictions = predictions[:min_len]
                prices = prices[:min_len]
            
            # Create strategy function from strategy_params
            strategy = self._create_strategy(strategy_params)
            
            # Run backtest
            logger.info("Running backtesting engine...")
            engine = BacktestingEngine(
                initial_capital=initial_capital,
                commission=commission,
                slippage=slippage
            )
            
            backtest_results = engine.backtest(
                predictions=pd.Series(predictions),
                prices=pd.Series(prices),
                strategy=strategy
            )
            
            # Format results
            formatted_results = self._format_results(
                model_id=model_id,
                start_date=start_date,
                end_date=end_date,
                backtest_results=backtest_results
            )
            
            logger.info(f"Backtest complete: {formatted_results['metrics']['total_trades']} trades")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}", exc_info=True)
            raise
    
    def _parse_model_id(self, model_id: str) -> tuple[str, str]:
        """
        Parse model_id to extract commodity and model_type.
        
        Supports formats:
        - "WTI_LSTM:1" -> ("WTI", "lstm")
        - "WTI_LSTM" -> ("WTI", "lstm")
        - "commodity_modeltype" -> ("COMMODITY", "modeltype")
        """
        # Remove version if present
        if ':' in model_id:
            model_id = model_id.split(':')[0]
        
        # Split by underscore
        parts = model_id.split('_', 1)
        
        if len(parts) < 2:
            raise ValueError(f"Invalid model_id format: {model_id}. Expected format: 'COMMODITY_MODELTYPE'")
        
        commodity = parts[0].upper()
        model_type = parts[1].lower()
        
        # Validate commodity
        if commodity not in ["WTI", "BRENT", "NG"]:
            raise ValueError(f"Invalid commodity: {commodity}. Must be WTI, BRENT, or NG")
        
        return commodity, model_type
    
    def _generate_predictions(
        self,
        model: Any,
        prices_df: pd.DataFrame,
        model_type: str
    ) -> np.ndarray:
        """
        Generate predictions using the model.
        
        Args:
            model: Loaded model instance
            prices_df: DataFrame with historical prices
            model_type: Type of model
            
        Returns:
            Array of predictions
        """
        try:
            # Try to use model's predict method
            if hasattr(model, 'predict'):
                # For time series models, we need to predict step-by-step
                # For simplicity, use the last known price as a baseline
                # In production, this would use proper time series prediction
                
                # Get price series
                prices = prices_df['price'].values
                
                # Simple approach: predict next value based on current model
                # This is a placeholder - actual implementation would use proper forecasting
                predictions = []
                
                # Use a simple moving average as placeholder prediction
                # In production, this would call model.predict() properly
                window = min(10, len(prices))
                for i in range(len(prices)):
                    if i < window:
                        # Use current price for first few predictions
                        predictions.append(prices[i])
                    else:
                        # Use moving average
                        predictions.append(np.mean(prices[i-window:i]))
                
                return np.array(predictions)
            else:
                raise ValueError("Model does not have predict method")
                
        except Exception as e:
            logger.warning(f"Error generating predictions: {e}. Using price as prediction.")
            # Fallback: use prices as predictions
            return prices_df['price'].values
    
    def _create_strategy(self, strategy_params: Optional[Dict[str, Any]]) -> Optional[Callable]:
        """
        Create strategy function from parameters.
        
        Args:
            strategy_params: Strategy parameters dict
            
        Returns:
            Strategy function or None (for default)
        """
        if not strategy_params:
            return None
        
        strategy_type = strategy_params.get('strategy', 'default')
        threshold = strategy_params.get('threshold', 0.02)
        
        if strategy_type == 'momentum':
            def momentum_strategy(pred, price):
                change = (pred - price) / price
                if change > threshold:
                    return 1  # Buy
                elif change < -threshold:
                    return -1  # Sell
                return 0  # Hold
            
            return momentum_strategy
        
        elif strategy_type == 'mean_reversion':
            # Mean reversion strategy would need historical mean
            # For now, use default
            return None
        
        else:
            # Default strategy
            return None
    
    def _format_results(
        self,
        model_id: str,
        start_date: date,
        end_date: date,
        backtest_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format backtest results for API response.
        
        Args:
            model_id: Model identifier
            start_date: Start date
            end_date: End date
            backtest_results: Raw backtest results from BacktestingEngine
            
        Returns:
            Formatted results dictionary
        """
        performance = backtest_results.get('performance', {})
        trades = backtest_results.get('trades', [])
        equity_curve = backtest_results.get('equity_curve', [])
        
        # Calculate cumulative P&L
        initial_capital = backtest_results.get('initial_capital', 0)
        final_capital = backtest_results.get('final_capital', 0)
        cumulative_pnl = final_capital - initial_capital
        
        # Format metrics
        metrics = {
            'total_trades': performance.get('total_trades', len(trades)),
            'win_rate': performance.get('win_rate', 0) * 100 if performance.get('win_rate') else None,
            'total_return': performance.get('total_return', 0),
            'sharpe_ratio': performance.get('sharpe_ratio'),
            'sortino_ratio': performance.get('sortino_ratio'),
            'max_drawdown': performance.get('max_drawdown'),
            'final_capital': final_capital,
            'initial_capital': initial_capital,
            'cumulative_pnl': cumulative_pnl,
            'rmse': performance.get('rmse'),
            'mae': performance.get('mae'),
            'mape': performance.get('mape'),
        }
        
        # Format trades
        formatted_trades = []
        for trade in trades:
            formatted_trades.append({
                'entry_idx': trade.get('entry_idx'),
                'exit_idx': trade.get('exit_idx'),
                'entry_price': float(trade.get('entry_price', 0)),
                'exit_price': float(trade.get('exit_price', 0)),
                'position': trade.get('position', 0),
                'pnl': trade.get('pnl'),
                'pnl_dollars': trade.get('pnl_dollars'),
                'capital_after': trade.get('capital_after') or trade.get('capital'),
                'timestamp': trade.get('timestamp'),
            })
        
        return {
            'model_id': model_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'metrics': metrics,
            'num_trades': len(trades),
            'trades': formatted_trades,
            'equity_curve': equity_curve.tolist() if isinstance(equity_curve, np.ndarray) else list(equity_curve),
        }


# Global service instance (singleton)
_backtest_service: Optional[BacktestService] = None


def get_backtest_service() -> BacktestService:
    """
    Get the global backtest service instance.
    
    Returns:
        BacktestService instance
    """
    global _backtest_service
    if _backtest_service is None:
        _backtest_service = BacktestService()
    return _backtest_service

