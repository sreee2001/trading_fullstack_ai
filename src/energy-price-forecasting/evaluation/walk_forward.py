"""
Walk-Forward Validation.

Implements walk-forward validation for time series models.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable, Any, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Optional import to handle ARIMAModel-specific behavior
try:
    from models.baseline import ARIMAModel
except Exception:
    ARIMAModel = None

class WalkForwardValidator:
    """
    Walk-forward validation for time series forecasting models.
    
    Implements expanding or rolling window walk-forward validation
    that respects temporal ordering.
    
    Attributes:
        train_window: Size of training window
        test_window: Size of test window
        step_size: Step size for moving forward
        expanding: Whether to use expanding window (True) or rolling (False)
    
    Example:
        >>> validator = WalkForwardValidator(train_window=365, test_window=30, step_size=30)
        >>> results = validator.validate(model_factory, data)
    """
    
    def __init__(
        self,
        train_window: int = 365,
        test_window: int = 30,
        step_size: int = 30,
        expanding: bool = True,
        min_train_size: Optional[int] = None
    ):
        """
        Initialize WalkForwardValidator.
        
        Args:
            train_window: Size of training window (days)
            test_window: Size of test window (days)
            step_size: Step size for moving forward (days)
            expanding: Whether to use expanding window (True) or rolling (False)
            min_train_size: Minimum training size required (default: train_window)
        """
        self.train_window = train_window
        self.test_window = test_window
        self.step_size = step_size
        self.expanding = expanding
        self.min_train_size = min_train_size or train_window
        
        logger.info(
            f"WalkForwardValidator initialized: train_window={train_window}, "
            f"test_window={test_window}, step_size={step_size}, expanding={expanding}"
        )
    
    def validate(
        self,
        model_factory: Callable,
        data: pd.DataFrame | pd.Series,
        target_column: Optional[str] = None,
        fit_kwargs: Optional[Dict] = None,
        predict_kwargs: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Perform walk-forward validation.
        
        Args:
            model_factory: Function that creates a new model instance
            data: Time series data
            target_column: Name of target column (for DataFrame)
            fit_kwargs: Additional arguments for model.fit()
            predict_kwargs: Additional arguments for model.predict()
        
        Returns:
            Dictionary with validation results
        """
        logger.info("="*80)
        logger.info("STARTING WALK-FORWARD VALIDATION")
        logger.info("="*80)
        
        if fit_kwargs is None:
            fit_kwargs = {}
        if predict_kwargs is None:
            predict_kwargs = {}
        
        # Convert Series to DataFrame if needed
        if isinstance(data, pd.Series):
            data = data.to_frame()
            if target_column is None:
                target_column = data.columns[0]
        
        # Ensure data is sorted by date
        if isinstance(data.index, pd.DatetimeIndex):
            data = data.sort_index()
        elif target_column and 'date' in data.columns:
            data = data.sort_values('date')
        
        n_total = len(data)
        results = []
        train_start = 0
        
        # Perform walk-forward validation
        while train_start + self.train_window + self.test_window <= n_total:
            # Define windows
            train_end = train_start + self.train_window
            test_start = train_end
            test_end = min(test_start + self.test_window, n_total)
            
            if test_end - test_start < self.test_window:
                break  # Not enough data for test window
            
            # Extract windows
            train_data = data.iloc[train_start:train_end].copy()
            test_data = data.iloc[test_start:test_end].copy()
            
            logger.info(
                f"Fold: train=[{train_start}:{train_end}], test=[{test_start}:{test_end}]"
            )
            
            try:
                # Create and train model
                model = model_factory()
                
                if hasattr(model, 'fit'):
                    try:
                        if isinstance(train_data, pd.DataFrame) and target_column:
                            model.fit(train_data, target_column=target_column, **fit_kwargs)
                        else:
                            model.fit(train_data, **fit_kwargs)
                    except TypeError:
                        # Fallback for models expecting Series/array only (e.g., ARIMAModel)
                        target_series = train_data[target_column] if isinstance(train_data, pd.DataFrame) and target_column else train_data
                        model.fit(target_series, **fit_kwargs)
                else:
                    raise ValueError("Model must have a fit() method")
                
                # Predict on test set
                if hasattr(model, 'predict'):
                    try:
                        if ARIMAModel is not None and isinstance(model, ARIMAModel):
                            predictions = model.predict(steps=len(test_data), **predict_kwargs)
                        else:
                            predictions = model.predict(test_data, **predict_kwargs)
                    except TypeError:
                        # Fallback for models that take steps instead of data (e.g., ARIMAModel)
                        predictions = model.predict(steps=len(test_data), **predict_kwargs)
                else:
                    raise ValueError("Model must have a predict() method")
                
                # Get true values
                if isinstance(test_data, pd.DataFrame):
                    if target_column:
                        y_true = test_data[target_column].values
                    else:
                        y_true = test_data.iloc[:, -1].values
                else:
                    y_true = test_data.values
                
                # Handle predictions format
                if isinstance(predictions, pd.DataFrame):
                    if 'yhat' in predictions.columns:
                        predictions = predictions['yhat'].values
                    else:
                        predictions = predictions.iloc[:, 0].values
                elif isinstance(predictions, tuple):
                    predictions = predictions[0]
                
                # Flatten if needed
                if predictions.ndim > 1 and predictions.shape[1] == 1:
                    predictions = predictions.flatten()
                if y_true.ndim > 1 and y_true.shape[1] == 1:
                    y_true = y_true.flatten()
                
                # Align lengths
                min_len = min(len(y_true), len(predictions))
                y_true = y_true[:min_len]
                predictions = predictions[:min_len]
                
                # Store results
                result = {
                    'fold': len(results) + 1,
                    'train_start': train_start,
                    'train_end': train_end,
                    'test_start': test_start,
                    'test_end': test_end,
                    'train_size': len(train_data),
                    'test_size': len(test_data),
                    'y_true': y_true,
                    'y_pred': predictions,
                    'timestamp': datetime.now().isoformat()
                }
                results.append(result)
                
            except Exception as e:
                logger.error(f"Fold {len(results) + 1} failed: {e}")
                result = {
                    'fold': len(results) + 1,
                    'train_start': train_start,
                    'train_end': train_end,
                    'test_start': test_start,
                    'test_end': test_end,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                results.append(result)
            
            # Move forward
            if self.expanding:
                # Expanding window: keep start fixed at 0, slide forward by step_size
                train_start += self.step_size
            else:
                # Rolling window: move both start and end
                train_start += self.step_size
        
        logger.info(f"Walk-forward validation complete: {len(results)} folds")
        
        return {
            'results': results,
            'n_folds': len(results),
            'train_window': self.train_window,
            'test_window': self.test_window,
            'step_size': self.step_size,
            'expanding': self.expanding
        }
    
    def get_aggregated_metrics(
        self,
        validation_results: Dict[str, Any],
        metrics: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Calculate aggregated metrics across all folds.
        
        Args:
            validation_results: Results from validate()
            metrics: List of metrics to calculate (default: ['MAE', 'RMSE', 'MAPE', 'R2'])
        
        Returns:
            DataFrame with metrics per fold and aggregated statistics
        """
        from training.evaluation import ModelEvaluator
        
        if metrics is None:
            metrics = ['MAE', 'RMSE', 'MAPE', 'R2']
        
        evaluator = ModelEvaluator(metrics=metrics)
        fold_metrics = []
        
        for result in validation_results['results']:
            if 'error' in result:
                continue
            
            y_true = result['y_true']
            y_pred = result['y_pred']
            
            metrics_dict = evaluator.evaluate(y_true, y_pred)
            metrics_dict['fold'] = result['fold']
            fold_metrics.append(metrics_dict)
        
        df = pd.DataFrame(fold_metrics)
        
        # Add aggregated statistics
        if len(df) > 0:
            agg_stats = {}
            for metric in metrics:
                if metric in df.columns:
                    agg_stats[f'{metric}_mean'] = df[metric].mean()
                    agg_stats[f'{metric}_std'] = df[metric].std()
                    agg_stats[f'{metric}_min'] = df[metric].min()
                    agg_stats[f'{metric}_max'] = df[metric].max()
            
            # Add as summary row
            summary_row = {'fold': 'Summary', **agg_stats}
            df = pd.concat([df, pd.DataFrame([summary_row])], ignore_index=True)
        
        return df

