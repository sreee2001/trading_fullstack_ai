"""
Statistical Metrics for Model Evaluation.

Provides comprehensive statistical metrics for forecasting model evaluation.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class StatisticalMetrics:
    """
    Calculate comprehensive statistical metrics for forecasting models.
    
    Provides metrics including RMSE, MAE, MAPE, R², directional accuracy,
    and horizon-specific metrics.
    
    Attributes:
        metrics: List of metrics to calculate
    
    Example:
        >>> metrics = StatisticalMetrics()
        >>> results = metrics.calculate_all(y_true, y_pred)
    """
    
    def __init__(self, metrics: Optional[List[str]] = None):
        """
        Initialize StatisticalMetrics.
        
        Args:
            metrics: List of metrics to calculate (default: all available)
        """
        if metrics is None:
            metrics = ['RMSE', 'MAE', 'MAPE', 'R2', 'Directional_Accuracy', 'MAE_percent']
        
        self.metrics = metrics
        logger.info(f"StatisticalMetrics initialized with metrics: {metrics}")
    
    def calculate_rmse(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> float:
        """
        Calculate Root Mean Squared Error.
        
        Args:
            y_true: True values
            y_pred: Predicted values
        
        Returns:
            RMSE value
        """
        mask = ~(np.isnan(y_true) | np.isnan(y_pred))
        y_true_clean = y_true[mask]
        y_pred_clean = y_pred[mask]
        
        if len(y_true_clean) == 0:
            return np.nan
        
        return np.sqrt(np.mean((y_true_clean - y_pred_clean) ** 2))
    
    def calculate_mae(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> float:
        """
        Calculate Mean Absolute Error.
        
        Args:
            y_true: True values
            y_pred: Predicted values
        
        Returns:
            MAE value
        """
        mask = ~(np.isnan(y_true) | np.isnan(y_pred))
        y_true_clean = y_true[mask]
        y_pred_clean = y_pred[mask]
        
        if len(y_true_clean) == 0:
            return np.nan
        
        return np.mean(np.abs(y_true_clean - y_pred_clean))
    
    def calculate_mape(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> float:
        """
        Calculate Mean Absolute Percentage Error.
        
        Args:
            y_true: True values
            y_pred: Predicted values
        
        Returns:
            MAPE value (percentage)
        """
        mask = ~(np.isnan(y_true) | np.isnan(y_pred))
        y_true_clean = y_true[mask]
        y_pred_clean = y_pred[mask]
        
        if len(y_true_clean) == 0:
            return np.nan
        
        mask_nonzero = y_true_clean != 0
        if mask_nonzero.sum() > 0:
            return np.mean(
                np.abs((y_true_clean[mask_nonzero] - y_pred_clean[mask_nonzero]) / y_true_clean[mask_nonzero])
            ) * 100
        else:
            return np.nan
    
    def calculate_r2(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> float:
        """
        Calculate R-squared (Coefficient of Determination).
        
        Args:
            y_true: True values
            y_pred: Predicted values
        
        Returns:
            R² value
        """
        mask = ~(np.isnan(y_true) | np.isnan(y_pred))
        y_true_clean = y_true[mask]
        y_pred_clean = y_pred[mask]
        
        if len(y_true_clean) == 0:
            return np.nan
        
        ss_res = np.sum((y_true_clean - y_pred_clean) ** 2)
        ss_tot = np.sum((y_true_clean - np.mean(y_true_clean)) ** 2)
        
        if ss_tot > 0:
            return 1 - (ss_res / ss_tot)
        else:
            return np.nan
    
    def calculate_directional_accuracy(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> float:
        """
        Calculate directional accuracy (percentage of correct direction predictions).
        
        Args:
            y_true: True values
            y_pred: Predicted values
        
        Returns:
            Directional accuracy (0-100)
        """
        if len(y_true) < 2 or len(y_pred) < 2:
            return np.nan
        
        true_direction = np.diff(y_true) > 0
        pred_direction = np.diff(y_pred) > 0
        
        accuracy = np.mean(true_direction == pred_direction) * 100
        return accuracy
    
    def calculate_mae_percent(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> float:
        """
        Calculate MAE as percentage of mean actual value.
        
        Args:
            y_true: True values
            y_pred: Predicted values
        
        Returns:
            MAE percentage
        """
        mae = self.calculate_mae(y_true, y_pred)
        mean_actual = np.mean(np.abs(y_true[~np.isnan(y_true)]))
        
        if mean_actual > 0:
            return (mae / mean_actual) * 100
        else:
            return np.nan
    
    def calculate_all(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate all configured metrics.
        
        Args:
            y_true: True values
            y_pred: Predicted values
        
        Returns:
            Dictionary of metric names and values
        """
        results = {}
        
        for metric in self.metrics:
            if metric == 'RMSE':
                results['RMSE'] = self.calculate_rmse(y_true, y_pred)
            elif metric == 'MAE':
                results['MAE'] = self.calculate_mae(y_true, y_pred)
            elif metric == 'MAPE':
                results['MAPE'] = self.calculate_mape(y_true, y_pred)
            elif metric == 'R2':
                results['R2'] = self.calculate_r2(y_true, y_pred)
            elif metric == 'Directional_Accuracy':
                results['Directional_Accuracy'] = self.calculate_directional_accuracy(y_true, y_pred)
            elif metric == 'MAE_percent':
                results['MAE_percent'] = self.calculate_mae_percent(y_true, y_pred)
        
        return results
    
    def calculate_per_horizon(
        self,
        y_true: Dict[int, np.ndarray],
        y_pred: Dict[int, np.ndarray]
    ) -> Dict[int, Dict[str, float]]:
        """
        Calculate metrics for each forecast horizon.
        
        Args:
            y_true: Dictionary mapping horizon to true values
            y_pred: Dictionary mapping horizon to predicted values
        
        Returns:
            Dictionary mapping horizon to metrics dictionary
        """
        results = {}
        
        for horizon in y_true.keys():
            if horizon in y_pred:
                results[horizon] = self.calculate_all(y_true[horizon], y_pred[horizon])
            else:
                logger.warning(f"No predictions for horizon {horizon}")
        
        return results
    
    def compare_models(
        self,
        y_true: np.ndarray,
        predictions: Dict[str, np.ndarray]
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
            metrics = self.calculate_all(y_true, y_pred)
            results[model_name] = metrics
        
        return pd.DataFrame(results).T

