"""
Random Search Hyperparameter Tuning.

Implements random search for hyperparameter optimization.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import random
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Callable, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RandomSearchTuner:
    """
    Random search hyperparameter tuner.
    
    Randomly samples hyperparameter combinations from the search space.
    
    Attributes:
        results: List of all trial results
        best_params: Best hyperparameters found
        best_score: Best score achieved
    
    Example:
        >>> tuner = RandomSearchTuner(n_iter=20)
        >>> best_params, best_model = tuner.search(
        ...     model_factory, param_distributions, train_data, val_data
        ... )
    """
    
    def __init__(self, n_iter: int = 20, scoring_metric: str = 'rmse', minimize: bool = True, random_state: Optional[int] = None):
        """
        Initialize RandomSearchTuner.
        
        Args:
            n_iter: Number of random parameter combinations to try
            scoring_metric: Metric to optimize ('rmse', 'mae', 'mape', 'r2')
            minimize: Whether to minimize (True) or maximize (False) the metric
            random_state: Random seed for reproducibility
        """
        self.n_iter = n_iter
        self.scoring_metric = scoring_metric.lower()
        self.minimize = minimize
        self.random_state = random_state
        
        if random_state is not None:
            random.seed(random_state)
            np.random.seed(random_state)
        
        self.results = []
        self.best_params = None
        self.best_score = None
        self.best_model = None
        
        logger.info(
            f"RandomSearchTuner initialized: n_iter={n_iter}, metric={scoring_metric}, "
            f"minimize={minimize}, random_state={random_state}"
        )
    
    def search(
        self,
        model_factory: Callable,
        param_distributions: Dict[str, List[Any]],
        train_data: pd.DataFrame | pd.Series,
        val_data: pd.DataFrame | pd.Series,
        target_column: Optional[str] = None,
        fit_kwargs: Optional[Dict] = None,
        predict_kwargs: Optional[Dict] = None,
        verbose: int = 1
    ) -> Tuple[Dict[str, Any], Any]:
        """
        Perform random search over hyperparameters.
        
        Args:
            model_factory: Function that creates model with parameters: model_factory(**params)
            param_distributions: Dictionary of parameter names to lists of possible values
            train_data: Training data
            val_data: Validation data
            target_column: Name of target column (for DataFrame)
            fit_kwargs: Additional arguments for model.fit()
            predict_kwargs: Additional arguments for model.predict()
            verbose: Verbosity level (0, 1, or 2)
        
        Returns:
            Tuple of (best_params, best_model)
        """
        logger.info("="*80)
        logger.info("STARTING RANDOM SEARCH")
        logger.info("="*80)
        
        if fit_kwargs is None:
            fit_kwargs = {}
        if predict_kwargs is None:
            predict_kwargs = {}
        
        self.results = []
        best_score = float('inf') if self.minimize else float('-inf')
        best_params = None
        best_model = None
        
        # Randomly sample parameter combinations
        for i in range(self.n_iter):
            # Randomly select one value for each parameter
            params = {
                param_name: random.choice(param_values)
                for param_name, param_values in param_distributions.items()
            }
            
            if verbose >= 1:
                logger.info(f"Trial {i+1}/{self.n_iter}: {params}")
            
            try:
                # Create model with these parameters
                model = model_factory(**params)
                
                # Train model
                if hasattr(model, 'fit'):
                    if isinstance(train_data, pd.DataFrame) and target_column:
                        model.fit(train_data, target_column=target_column, **fit_kwargs)
                    else:
                        model.fit(train_data, **fit_kwargs)
                else:
                    raise ValueError("Model must have a fit() method")
                
                # Predict on validation set
                if hasattr(model, 'predict'):
                    predictions = model.predict(val_data, **predict_kwargs)
                else:
                    raise ValueError("Model must have a predict() method")
                
                # Get true values
                if isinstance(val_data, pd.DataFrame):
                    if target_column:
                        y_true = val_data[target_column].values
                    else:
                        y_true = val_data.iloc[:, -1].values
                else:
                    y_true = val_data.values
                
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
                
                # Calculate score
                score = self._calculate_score(y_true, predictions)
                
                # Store result
                result = {
                    'params': params,
                    'score': score,
                    'timestamp': datetime.now().isoformat(),
                    'trial': i + 1
                }
                self.results.append(result)
                
                # Update best if better
                is_better = (score < best_score) if self.minimize else (score > best_score)
                if is_better:
                    best_score = score
                    best_params = params.copy()
                    best_model = model
                    if verbose >= 1:
                        logger.info(f"New best score: {best_score:.6f}")
                
            except Exception as e:
                logger.error(f"Trial {i+1} failed with error: {e}")
                result = {
                    'params': params,
                    'score': None,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat(),
                    'trial': i + 1
                }
                self.results.append(result)
        
        self.best_params = best_params
        self.best_score = best_score
        self.best_model = best_model
        
        logger.info("="*80)
        logger.info("RANDOM SEARCH COMPLETE")
        logger.info(f"Best score: {best_score:.6f}")
        logger.info(f"Best parameters: {best_params}")
        logger.info("="*80)
        
        return best_params, best_model
    
    def _calculate_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate scoring metric.
        
        Args:
            y_true: True values
            y_pred: Predicted values
        
        Returns:
            Score value
        """
        # Remove NaN values
        mask = ~(np.isnan(y_true) | np.isnan(y_pred))
        y_true_clean = y_true[mask]
        y_pred_clean = y_pred[mask]
        
        if len(y_true_clean) == 0:
            return float('inf') if self.minimize else float('-inf')
        
        if self.scoring_metric == 'rmse':
            return np.sqrt(np.mean((y_true_clean - y_pred_clean) ** 2))
        elif self.scoring_metric == 'mae':
            return np.mean(np.abs(y_true_clean - y_pred_clean))
        elif self.scoring_metric == 'mape':
            mask_nonzero = y_true_clean != 0
            if mask_nonzero.sum() > 0:
                return np.mean(
                    np.abs((y_true_clean[mask_nonzero] - y_pred_clean[mask_nonzero]) / y_true_clean[mask_nonzero])
                ) * 100
            else:
                return float('inf')
        elif self.scoring_metric == 'r2':
            ss_res = np.sum((y_true_clean - y_pred_clean) ** 2)
            ss_tot = np.sum((y_true_clean - np.mean(y_true_clean)) ** 2)
            if ss_tot > 0:
                return 1 - (ss_res / ss_tot)
            else:
                return float('-inf')
        else:
            raise ValueError(f"Unknown scoring metric: {self.scoring_metric}")
    
    def get_results_dataframe(self) -> pd.DataFrame:
        """
        Get all results as a DataFrame.
        
        Returns:
            DataFrame with columns: params, score, timestamp, trial
        """
        return pd.DataFrame(self.results)
    
    def get_best_result(self) -> Dict[str, Any]:
        """
        Get best result.
        
        Returns:
            Dictionary with best_params, best_score, best_model
        """
        return {
            'params': self.best_params,
            'score': self.best_score,
            'model': self.best_model
        }

