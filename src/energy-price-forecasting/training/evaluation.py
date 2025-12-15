"""
Model Evaluation Framework.

Provides comprehensive evaluation metrics and utilities for forecasting models.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Evaluate forecasting models with comprehensive metrics.
    
    Provides multiple evaluation metrics including MAE, RMSE, MAPE, R2,
    and directional accuracy for time series forecasting.
    
    Attributes:
        metrics: List of metrics to calculate
    
    Example:
        >>> evaluator = ModelEvaluator()
        >>> results = evaluator.evaluate(y_true, y_pred)
    """
    
    def __init__(self, metrics: Optional[List[str]] = None):
        """
        Initialize ModelEvaluator.
        
        Args:
            metrics: List of metrics to calculate (default: ['MAE', 'RMSE', 'MAPE', 'R2'])
        """
        if metrics is None:
            metrics = ['MAE', 'RMSE', 'MAPE', 'R2', 'Directional_Accuracy']
        
        self.metrics = metrics
        logger.info(f"ModelEvaluator initialized with metrics: {metrics}")
    
    def evaluate(
        self,
        y_true: np.ndarray | pd.Series,
        y_pred: np.ndarray | pd.Series,
        return_breakdown: bool = False
    ) -> Dict[str, float] | Tuple[Dict[str, float], Dict]:
        """
        Evaluate predictions against true values.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            return_breakdown: Whether to return detailed breakdown (default: False)
        
        Returns:
            Dictionary of metric names and values, or tuple of (metrics, breakdown) if return_breakdown=True
        """
        # Convert to numpy arrays
        if isinstance(y_true, pd.Series):
            y_true = y_true.values
        if isinstance(y_pred, pd.Series):
            y_pred = y_pred.values
        
        # Flatten if needed
        y_true = y_true.flatten()
        y_pred = y_pred.flatten()
        
        # Remove NaN values
        mask = ~(np.isnan(y_true) | np.isnan(y_pred))
        y_true_clean = y_true[mask]
        y_pred_clean = y_pred[mask]
        
        if len(y_true_clean) == 0:
            logger.warning("No valid data points for evaluation after removing NaN")
            return {metric: np.nan for metric in self.metrics}
        
        results = {}
        breakdown = {}
        
        for metric in self.metrics:
            if metric == 'MAE':
                value = np.mean(np.abs(y_true_clean - y_pred_clean))
                results['MAE'] = value
            
            elif metric == 'RMSE':
                value = np.sqrt(np.mean((y_true_clean - y_pred_clean) ** 2))
                results['RMSE'] = value
            
            elif metric == 'MAPE':
                # Avoid division by zero
                mask_nonzero = y_true_clean != 0
                if mask_nonzero.sum() > 0:
                    value = np.mean(
                        np.abs((y_true_clean[mask_nonzero] - y_pred_clean[mask_nonzero]) / y_true_clean[mask_nonzero])
                    ) * 100
                else:
                    value = np.nan
                results['MAPE'] = value
            
            elif metric == 'R2':
                ss_res = np.sum((y_true_clean - y_pred_clean) ** 2)
                ss_tot = np.sum((y_true_clean - np.mean(y_true_clean)) ** 2)
                if ss_tot > 0:
                    value = 1 - (ss_res / ss_tot)
                else:
                    value = np.nan
                results['R2'] = value
            
            elif metric == 'Directional_Accuracy':
                # Calculate percentage of correct direction predictions
                if len(y_true_clean) > 1:
                    true_direction = np.diff(y_true_clean) > 0
                    pred_direction = np.diff(y_pred_clean) > 0
                    value = np.mean(true_direction == pred_direction) * 100
                else:
                    value = np.nan
                results['Directional_Accuracy'] = value
            
            elif metric == 'MAE_percent':
                mean_actual = np.mean(np.abs(y_true_clean))
                if mean_actual > 0:
                    value = (results.get('MAE', 0) / mean_actual) * 100
                else:
                    value = np.nan
                results['MAE_percent'] = value
        
        if return_breakdown:
            breakdown = {
                'n_samples': len(y_true_clean),
                'n_original': len(y_true),
                'n_nan_removed': len(y_true) - len(y_true_clean),
                'mean_actual': float(np.mean(y_true_clean)),
                'mean_predicted': float(np.mean(y_pred_clean)),
                'std_actual': float(np.std(y_true_clean)),
                'std_predicted': float(np.std(y_pred_clean))
            }
            return results, breakdown
        
        return results
    
    def evaluate_by_horizon(
        self,
        y_true: np.ndarray | pd.Series,
        y_pred: np.ndarray | pd.Series,
        horizons: Optional[List[int]] = None
    ) -> Dict[int, Dict[str, float]]:
        """
        Evaluate predictions for different forecast horizons.
        
        Args:
            y_true: True values (can be multi-horizon)
            y_pred: Predicted values (can be multi-horizon)
            horizons: List of horizons to evaluate (None = auto-detect)
        
        Returns:
            Dictionary mapping horizon to metrics
        """
        # Convert to numpy arrays
        if isinstance(y_true, pd.Series):
            y_true = y_true.values
        if isinstance(y_pred, pd.Series):
            y_pred = y_pred.values
        
        # Handle multi-horizon predictions
        if y_pred.ndim > 1 and y_pred.shape[1] > 1:
            # Multi-horizon predictions
            if horizons is None:
                horizons = list(range(1, y_pred.shape[1] + 1))
            
            results = {}
            for i, horizon in enumerate(horizons):
                if i < y_pred.shape[1]:
                    y_true_h = y_true if y_true.ndim == 1 else y_true[:, i] if y_true.shape[1] > i else y_true[:, 0]
                    y_pred_h = y_pred[:, i]
                    results[horizon] = self.evaluate(y_true_h, y_pred_h)
        else:
            # Single horizon
            results = {1: self.evaluate(y_true, y_pred)}
        
        return results
    
    def compare_models(
        self,
        y_true: np.ndarray | pd.Series,
        predictions: Dict[str, np.ndarray | pd.Series]
    ) -> pd.DataFrame:
        """
        Compare multiple models' predictions.
        
        Args:
            y_true: True values
            predictions: Dictionary mapping model names to predictions
        
        Returns:
            DataFrame with metrics for each model
        """
        results = {}
        
        for model_name, y_pred in predictions.items():
            metrics = self.evaluate(y_true, y_pred)
            results[model_name] = metrics
        
        return pd.DataFrame(results).T

