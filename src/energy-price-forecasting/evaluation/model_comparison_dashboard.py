"""
Model Comparison Dashboard for Epic 3.

Compares multiple models with both statistical and risk metrics.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from pathlib import Path
import json

from .statistical_metrics import StatisticalMetrics
from .performance_metrics import PerformanceMetrics

logger = logging.getLogger(__name__)


class ModelComparisonDashboard:
    """
    Compare multiple models with comprehensive metrics.
    
    Provides unified comparison including:
    - Statistical metrics (RMSE, MAE, MAPE, R², Directional Accuracy)
    - Risk metrics (Sharpe Ratio, Max Drawdown, Volatility)
    - Best model selection
    - Export capabilities
    
    Attributes:
        statistical_metrics: StatisticalMetrics instance
        performance_metrics: PerformanceMetrics instance
        results: Dictionary of model results
    
    Example:
        >>> dashboard = ModelComparisonDashboard()
        >>> results = dashboard.compare_models(
        ...     y_true=y_true,
        ...     predictions={'ARIMA': arima_pred, 'LSTM': lstm_pred},
        ...     equity_curves={'ARIMA': arima_equity, 'LSTM': lstm_equity}
        ... )
        >>> table = dashboard.get_comparison_table()
        >>> best = dashboard.select_best_model('sharpe_ratio')
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize ModelComparisonDashboard.
        
        Args:
            risk_free_rate: Risk-free rate for Sharpe/Sortino calculations
        """
        self.statistical_metrics = StatisticalMetrics()
        self.performance_metrics = PerformanceMetrics(risk_free_rate=risk_free_rate)
        self.results: Dict[str, Dict[str, Any]] = {}
        
        logger.info("ModelComparisonDashboard initialized")
    
    def compare_models(
        self,
        y_true: np.ndarray | pd.Series,
        predictions: Dict[str, np.ndarray | pd.Series],
        equity_curves: Optional[Dict[str, np.ndarray | pd.Series]] = None,
        returns: Optional[Dict[str, np.ndarray | pd.Series]] = None
    ) -> pd.DataFrame:
        """
        Compare multiple models with comprehensive metrics.
        
        Args:
            y_true: True values
            predictions: Dictionary mapping model names to predictions
            equity_curves: Optional dictionary mapping model names to equity curves
            returns: Optional dictionary mapping model names to returns
        
        Returns:
            DataFrame with all metrics for each model
        """
        logger.info(f"Comparing {len(predictions)} models...")
        
        results = {}
        
        for model_name, y_pred in predictions.items():
            # Calculate statistical metrics
            stat_metrics = self.statistical_metrics.calculate_all(
                np.array(y_true) if isinstance(y_true, pd.Series) else y_true,
                np.array(y_pred) if isinstance(y_pred, pd.Series) else y_pred
            )
            
            # Calculate risk metrics if equity curve or returns provided
            risk_metrics = {}
            if equity_curves and model_name in equity_curves:
                equity = equity_curves[model_name]
                if returns and model_name in returns:
                    rets = returns[model_name]
                else:
                    rets = None
                
                perf_metrics = self.performance_metrics.calculate_all(
                    prices=equity,
                    returns=rets,
                    y_true=y_true if isinstance(y_true, np.ndarray) else y_true.values,
                    y_pred=y_pred if isinstance(y_pred, np.ndarray) else y_pred.values
                )
                
                # Extract relevant risk metrics
                risk_metrics = {
                    'sharpe_ratio': perf_metrics.get('sharpe_ratio', np.nan),
                    'sortino_ratio': perf_metrics.get('sortino_ratio', np.nan),
                    'max_drawdown': perf_metrics.get('max_drawdown', np.nan),
                    'volatility': perf_metrics.get('volatility', np.nan),
                    'total_return': perf_metrics.get('total_return', np.nan),
                    'annualized_return': perf_metrics.get('annualized_return', np.nan)
                }
            
            # Combine metrics
            results[model_name] = {
                **stat_metrics,
                **risk_metrics
            }
            
            logger.info(f"{model_name} comparison complete")
        
        self.results = results
        
        return self.get_comparison_table()
    
    def get_comparison_table(
        self,
        sort_by: Optional[str] = None,
        ascending: bool = False
    ) -> pd.DataFrame:
        """
        Get comparison table of all models.
        
        Args:
            sort_by: Column to sort by (default: 'sharpe_ratio' if available, else 'RMSE')
            ascending: Whether to sort ascending (True) or descending (False)
        
        Returns:
            DataFrame with model names as index and metrics as columns
        """
        if not self.results:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.results).T
        
        # Sort if requested
        if sort_by:
            if sort_by in df.columns:
                df = df.sort_values(by=sort_by, ascending=ascending)
        else:
            # Default sorting: Sharpe ratio if available, else RMSE
            if 'sharpe_ratio' in df.columns and df['sharpe_ratio'].notna().any():
                df = df.sort_values(by='sharpe_ratio', ascending=False, na_position='last')
            elif 'RMSE' in df.columns:
                df = df.sort_values(by='RMSE', ascending=True, na_position='last')
        
        return df
    
    def select_best_model(
        self,
        primary_metric: str = 'sharpe_ratio',
        secondary_metric: Optional[str] = 'RMSE'
    ) -> Optional[Dict[str, Any]]:
        """
        Select best model based on primary metric.
        
        Args:
            primary_metric: Primary metric to optimize (default: 'sharpe_ratio')
            secondary_metric: Secondary metric for tie-breaking (default: 'RMSE')
        
        Returns:
            Dictionary with best model name and metrics, or None if no results
        """
        if not self.results:
            return None
        
        df = self.get_comparison_table()
        
        if df.empty:
            return None
        
        # Check if primary metric exists
        if primary_metric not in df.columns:
            # Fallback to RMSE if available
            if 'RMSE' in df.columns:
                primary_metric = 'RMSE'
            else:
                # Return first model if no valid metric
                return {
                    'model_name': df.index[0],
                    'primary_metric': 'none',
                    'primary_value': None,
                    'metrics': self.results[df.index[0]]
                }
        
        # Determine if higher or lower is better
        higher_is_better = primary_metric in [
            'sharpe_ratio', 'sortino_ratio', 'R2', 'Directional_Accuracy',
            'total_return', 'annualized_return'
        ]
        
        # Filter out NaN values
        valid_df = df[df[primary_metric].notna()].copy()
        
        if valid_df.empty:
            return None
        
        # Sort by primary metric
        ascending = not higher_is_better
        valid_df = valid_df.sort_values(by=primary_metric, ascending=ascending)
        
        # Get best value
        best_value = valid_df[primary_metric].iloc[0]
        
        # Find all models with best value (ties)
        best_models = valid_df[valid_df[primary_metric] == best_value]
        
        if len(best_models) > 1 and secondary_metric and secondary_metric in df.columns:
            # Break tie with secondary metric
            higher_is_better_secondary = secondary_metric in [
                'sharpe_ratio', 'sortino_ratio', 'R2', 'Directional_Accuracy'
            ]
            ascending_secondary = not higher_is_better_secondary
            
            best_models = best_models.sort_values(
                by=secondary_metric,
                ascending=ascending_secondary
            )
        
        best_model_name = best_models.index[0]
        best_metrics = self.results[best_model_name]
        
        return {
            'model_name': best_model_name,
            'primary_metric': primary_metric,
            'primary_value': best_value,
            'metrics': best_metrics
        }
    
    def export_comparison_report(
        self,
        output_path: str | Path,
        format: str = 'csv',
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Export comparison report to file.
        
        Args:
            output_path: Path to output file
            format: Export format ('csv' or 'json')
            metadata: Optional metadata to include
        """
        output_path = Path(output_path)
        
        df = self.get_comparison_table()
        
        if format.lower() == 'csv':
            # Add metadata as comments or separate section
            with open(output_path, 'w') as f:
                if metadata:
                    f.write("# Model Comparison Report\n")
                    f.write(f"# Generated: {datetime.now().isoformat()}\n")
                    for key, value in metadata.items():
                        f.write(f"# {key}: {value}\n")
                    f.write("\n")
                
                df.to_csv(f)
            
            logger.info(f"Comparison report exported to CSV: {output_path}")
        
        elif format.lower() == 'json':
            report = {
                'metadata': {
                    'generated': datetime.now().isoformat(),
                    **(metadata or {})
                },
                'comparison_table': df.to_dict('index'),
                'best_model': self.select_best_model()
            }
            
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Comparison report exported to JSON: {output_path}")
        
        else:
            raise ValueError(f"Unknown format: {format}. Use 'csv' or 'json'")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of comparison.
        
        Returns:
            Dictionary with summary information
        """
        df = self.get_comparison_table()
        
        summary = {
            'num_models': len(self.results),
            'metrics_available': list(df.columns) if not df.empty else [],
            'best_model': None,
            'comparison_table': df.to_dict('index') if not df.empty else {}
        }
        
        best = self.select_best_model()
        if best:
            summary['best_model'] = best['model_name']
            summary['best_metric'] = best['primary_metric']
            summary['best_value'] = best['primary_value']
        
        return summary

