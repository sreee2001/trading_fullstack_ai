"""
Horizon-Specific Evaluator.

Evaluates forecasts for each horizon separately.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

from training.evaluation import ModelEvaluator

logger = logging.getLogger(__name__)


class HorizonEvaluator:
    """
    Evaluates multi-horizon forecasts with horizon-specific metrics.
    
    Provides evaluation for each forecast horizon separately and
    aggregated metrics across all horizons.
    
    Attributes:
        horizons: List of forecast horizons
        evaluator: ModelEvaluator instance
    
    Example:
        >>> evaluator = HorizonEvaluator(horizons=[1, 7, 30])
        >>> results = evaluator.evaluate_all(y_true, predictions)
    """
    
    def __init__(self, horizons: List[int] = [1, 7, 30], metrics: Optional[List[str]] = None):
        """
        Initialize HorizonEvaluator.
        
        Args:
            horizons: List of forecast horizons in days
            metrics: List of metrics to calculate (default: ['MAE', 'RMSE', 'MAPE', 'R2'])
        """
        self.horizons = sorted(horizons)
        self.evaluator = ModelEvaluator(metrics=metrics)
        
        logger.info(f"HorizonEvaluator initialized for horizons: {horizons}")
    
    def evaluate_horizon(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        horizon: int
    ) -> Dict[str, float]:
        """
        Evaluate predictions for a specific horizon.
        
        Args:
            y_true: True values (should be aligned with predictions)
            y_pred: Predicted values for the horizon
            horizon: Forecast horizon in days
        
        Returns:
            Dictionary of metric names and values
        """
        # Align lengths
        min_len = min(len(y_true), len(y_pred))
        y_true_aligned = y_true[:min_len]
        y_pred_aligned = y_pred[:min_len]
        
        metrics = self.evaluator.evaluate(y_true_aligned, y_pred_aligned)
        metrics['horizon'] = horizon
        
        return metrics
    
    def evaluate_all(
        self,
        y_true: Dict[int, np.ndarray] | np.ndarray,
        predictions: Dict[int, np.ndarray]
    ) -> Dict[int, Dict[str, float]]:
        """
        Evaluate predictions for all horizons.
        
        Args:
            y_true: True values (dict mapping horizon to values, or single array)
            predictions: Dictionary mapping horizon to predictions
        
        Returns:
            Dictionary mapping horizon to metrics dictionary
        """
        results = {}
        
        for horizon in self.horizons:
            if horizon not in predictions:
                logger.warning(f"No predictions for horizon {horizon}")
                continue
            
            # Get true values for this horizon
            if isinstance(y_true, dict):
                if horizon in y_true:
                    y_true_h = y_true[horizon]
                else:
                    logger.warning(f"No true values for horizon {horizon}, using first available")
                    y_true_h = list(y_true.values())[0]
            else:
                y_true_h = y_true
            
            results[horizon] = self.evaluate_horizon(
                y_true_h,
                predictions[horizon],
                horizon
            )
        
        return results
    
    def compare_horizons(
        self,
        results: Dict[int, Dict[str, float]],
        metric: str = 'RMSE'
    ) -> pd.DataFrame:
        """
        Compare performance across horizons.
        
        Args:
            results: Results from evaluate_all()
            metric: Metric to compare
        
        Returns:
            DataFrame with horizon comparison
        """
        comparison_data = []
        
        for horizon, metrics in results.items():
            comparison_data.append({
                'horizon': horizon,
                'metric': metric,
                'value': metrics.get(metric, np.nan)
            })
        
        df = pd.DataFrame(comparison_data)
        return df.sort_values('horizon')
    
    def get_summary(
        self,
        results: Dict[int, Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Get summary statistics across all horizons.
        
        Args:
            results: Results from evaluate_all()
        
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'horizons': list(results.keys()),
            'metrics': {}
        }
        
        # Aggregate metrics across horizons
        all_metrics = set()
        for metrics in results.values():
            all_metrics.update(metrics.keys())
        
        for metric in all_metrics:
            if metric == 'horizon':
                continue
            
            values = [metrics.get(metric, np.nan) for metrics in results.values()]
            values = [v for v in values if not np.isnan(v)]
            
            if values:
                summary['metrics'][metric] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'values': {h: results[h].get(metric, np.nan) for h in results.keys()}
                }
        
        return summary

