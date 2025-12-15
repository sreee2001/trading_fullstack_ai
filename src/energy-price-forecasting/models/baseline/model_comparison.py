"""
Model Comparison Framework for Baseline Models.

Compares multiple baseline models and provides evaluation metrics.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

from .arima_model import ARIMAModel
from .exponential_smoothing import ExponentialSmoothingModel
from .prophet_model import ProphetModel

logger = logging.getLogger(__name__)


class ModelComparison:
    """
    Compare multiple baseline forecasting models.
    
    Provides unified interface for training, evaluating, and comparing
    different baseline models.
    
    Attributes:
        models: Dictionary of model instances
        results: Dictionary of model evaluation results
        best_model: Name of best performing model
    
    Example:
        >>> comparison = ModelComparison()
        >>> comparison.add_model('ARIMA', ARIMAModel())
        >>> comparison.add_model('Prophet', ProphetModel())
        >>> comparison.train_all(train_data)
        >>> results = comparison.evaluate_all(test_data)
        >>> best = comparison.get_best_model()
    """
    
    def __init__(self):
        """Initialize ModelComparison."""
        self.models: Dict[str, any] = {}
        self.results: Dict[str, Dict] = {}
        self.best_model: Optional[str] = None
        
        logger.info("ModelComparison initialized")
    
    def add_model(self, name: str, model: ARIMAModel | ExponentialSmoothingModel | ProphetModel):
        """
        Add a model to the comparison.
        
        Args:
            name: Name identifier for the model
            model: Model instance (ARIMA, ExponentialSmoothing, or Prophet)
        
        Example:
            >>> comparison.add_model('ARIMA', ARIMAModel())
        """
        if not isinstance(model, (ARIMAModel, ExponentialSmoothingModel, ProphetModel)):
            raise ValueError(
                "Model must be an instance of ARIMAModel, ExponentialSmoothingModel, or ProphetModel"
            )
        
        self.models[name] = model
        logger.info(f"Added model: {name} ({type(model).__name__})")
    
    def train_all(self, train_data: pd.Series | pd.DataFrame, **kwargs):
        """
        Train all models on the training data.
        
        Args:
            train_data: Training time series data
            **kwargs: Additional arguments to pass to model.fit()
        
        Example:
            >>> comparison.train_all(train_data['price'])
        """
        logger.info(f"Training {len(self.models)} models...")
        
        for name, model in self.models.items():
            try:
                logger.info(f"Training {name}...")
                
                if isinstance(model, ProphetModel):
                    # Prophet needs DataFrame with date and value columns
                    if isinstance(train_data, pd.Series):
                        if isinstance(train_data.index, pd.DatetimeIndex):
                            df = pd.DataFrame({
                                'ds': train_data.index,
                                'y': train_data.values
                            })
                            model.fit(df, **kwargs)
                        else:
                            raise ValueError("Prophet requires Series with DatetimeIndex")
                    else:
                        model.fit(train_data, **kwargs)
                else:
                    # ARIMA and Exponential Smoothing work with Series
                    if isinstance(train_data, pd.DataFrame):
                        if len(train_data.columns) == 1:
                            train_data = train_data.iloc[:, 0]
                        else:
                            raise ValueError("DataFrame must have single column for ARIMA/ExponentialSmoothing")
                    
                    model.fit(train_data, **kwargs)
                
                logger.info(f"{name} trained successfully")
            
            except Exception as e:
                logger.error(f"Error training {name}: {e}")
                raise
    
    def predict_all(self, steps: int = 1, **kwargs) -> Dict[str, pd.Series | pd.DataFrame]:
        """
        Generate predictions from all models.
        
        Args:
            steps: Number of steps to forecast
            **kwargs: Additional arguments to pass to model.predict()
        
        Returns:
            Dictionary mapping model names to predictions
        
        Example:
            >>> predictions = comparison.predict_all(steps=30)
        """
        predictions = {}
        
        for name, model in self.models.items():
            if not model.is_fitted:
                logger.warning(f"{name} is not fitted, skipping prediction")
                continue
            
            try:
                pred = model.predict(steps=steps, **kwargs)
                
                # Handle tuple return (forecast, conf_int)
                if isinstance(pred, tuple):
                    pred = pred[0]
                
                predictions[name] = pred
                logger.info(f"{name} prediction generated")
            
            except Exception as e:
                logger.error(f"Error predicting with {name}: {e}")
                predictions[name] = None
        
        return predictions
    
    def evaluate_all(
        self,
        test_data: pd.Series | pd.DataFrame,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """
        Evaluate all models on test data.
        
        Args:
            test_data: Test time series data
            metrics: List of metrics to calculate (default: ['MAE', 'RMSE', 'MAPE'])
        
        Returns:
            Dictionary mapping model names to evaluation metrics
        
        Example:
            >>> results = comparison.evaluate_all(test_data['price'])
        """
        if metrics is None:
            metrics = ['MAE', 'RMSE', 'MAPE', 'R2']
        
        logger.info(f"Evaluating {len(self.models)} models on test data...")
        
        # Convert test_data to Series if needed
        if isinstance(test_data, pd.DataFrame):
            if len(test_data.columns) == 1:
                test_data = test_data.iloc[:, 0]
            else:
                raise ValueError("DataFrame must have single column for evaluation")
        
        if not isinstance(test_data, pd.Series):
            test_data = pd.Series(test_data)
        
        results = {}
        
        for name, model in self.models.items():
            if not model.is_fitted:
                logger.warning(f"{name} is not fitted, skipping evaluation")
                continue
            
            try:
                # Generate predictions for test period
                steps = len(test_data)
                predictions = model.predict(steps=steps)
                
                # Handle tuple return (forecast, conf_int)
                if isinstance(predictions, tuple):
                    predictions = predictions[0]
                
                # Handle DataFrame return (Prophet)
                if isinstance(predictions, pd.DataFrame):
                    if 'yhat' in predictions.columns:
                        predictions = predictions['yhat']
                    else:
                        predictions = predictions.iloc[:, 0]
                
                # Ensure predictions is Series
                if not isinstance(predictions, pd.Series):
                    predictions = pd.Series(predictions)
                
                # Align indices
                if len(predictions) != len(test_data):
                    predictions = predictions.iloc[:len(test_data)]
                
                # Calculate metrics
                model_results = self._calculate_metrics(test_data, predictions, metrics)
                results[name] = model_results
                
                logger.info(f"{name} evaluation complete: {model_results}")
            
            except Exception as e:
                logger.error(f"Error evaluating {name}: {e}")
                results[name] = {'error': str(e)}
        
        self.results = results
        
        # Determine best model
        self.best_model = self._get_best_model(results, metrics)
        
        return results
    
    def _calculate_metrics(
        self,
        actual: pd.Series,
        predicted: pd.Series,
        metrics: List[str]
    ) -> Dict[str, float]:
        """Calculate evaluation metrics."""
        results = {}
        
        # Remove NaN values for calculation
        mask = ~(actual.isna() | predicted.isna())
        actual_clean = actual[mask]
        predicted_clean = predicted[mask]
        
        if len(actual_clean) == 0:
            return {metric: np.nan for metric in metrics}
        
        for metric in metrics:
            if metric == 'MAE':
                results['MAE'] = np.mean(np.abs(actual_clean - predicted_clean))
            
            elif metric == 'RMSE':
                results['RMSE'] = np.sqrt(np.mean((actual_clean - predicted_clean) ** 2))
            
            elif metric == 'MAPE':
                # Avoid division by zero
                mask_nonzero = actual_clean != 0
                if mask_nonzero.sum() > 0:
                    results['MAPE'] = np.mean(
                        np.abs((actual_clean[mask_nonzero] - predicted_clean[mask_nonzero]) / actual_clean[mask_nonzero])
                    ) * 100
                else:
                    results['MAPE'] = np.nan
            
            elif metric == 'R2':
                ss_res = np.sum((actual_clean - predicted_clean) ** 2)
                ss_tot = np.sum((actual_clean - np.mean(actual_clean)) ** 2)
                if ss_tot > 0:
                    results['R2'] = 1 - (ss_res / ss_tot)
                else:
                    results['R2'] = np.nan
            
            elif metric == 'MAE_percent':
                mean_actual = np.mean(np.abs(actual_clean))
                if mean_actual > 0:
                    results['MAE_percent'] = (results.get('MAE', 0) / mean_actual) * 100
                else:
                    results['MAE_percent'] = np.nan
        
        return results
    
    def _get_best_model(self, results: Dict[str, Dict], metrics: List[str]) -> Optional[str]:
        """Determine best model based on metrics."""
        if not results:
            return None
        
        # Use RMSE as primary metric (lower is better)
        if 'RMSE' in metrics:
            best_rmse = float('inf')
            best_model = None
            
            for name, result in results.items():
                if 'error' in result:
                    continue
                if 'RMSE' in result and not np.isnan(result['RMSE']):
                    if result['RMSE'] < best_rmse:
                        best_rmse = result['RMSE']
                        best_model = name
            
            return best_model
        
        # Fallback to first model without error
        for name, result in results.items():
            if 'error' not in result:
                return name
        
        return None
    
    def get_best_model(self) -> Optional[str]:
        """Get the name of the best performing model."""
        return self.best_model
    
    def get_comparison_table(self) -> pd.DataFrame:
        """
        Get comparison table of all models.
        
        Returns:
            DataFrame with model names as index and metrics as columns
        """
        if not self.results:
            return pd.DataFrame()
        
        return pd.DataFrame(self.results).T
    
    def get_summary(self) -> Dict:
        """
        Get summary of comparison.
        
        Returns:
            Dictionary with summary information
        """
        return {
            'num_models': len(self.models),
            'num_evaluated': len(self.results),
            'best_model': self.best_model,
            'results': self.results
        }

