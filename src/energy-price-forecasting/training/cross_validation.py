"""
Time Series Cross-Validation Utilities.

Provides time series cross-validation that respects temporal ordering.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class TimeSeriesCrossValidator:
    """
    Time series cross-validation that respects temporal ordering.
    
    Implements walk-forward validation and expanding/rolling window
    cross-validation for time series data.
    
    Attributes:
        n_splits: Number of CV splits
        test_size: Size of test set in each split
        gap: Gap between train and test sets
    
    Example:
        >>> cv = TimeSeriesCrossValidator(n_splits=5, test_size=30)
        >>> for train_idx, test_idx in cv.split(data):
        ...     train_data = data.iloc[train_idx]
        ...     test_data = data.iloc[test_idx]
    """
    
    def __init__(
        self,
        n_splits: int = 5,
        test_size: int = 30,
        gap: int = 0,
        expanding_window: bool = True
    ):
        """
        Initialize TimeSeriesCrossValidator.
        
        Args:
            n_splits: Number of CV splits (default: 5)
            test_size: Size of test set in each split (default: 30)
            gap: Gap between train and test sets (default: 0)
            expanding_window: Whether to use expanding window (True) or rolling window (False)
        """
        self.n_splits = n_splits
        self.test_size = test_size
        self.gap = gap
        self.expanding_window = expanding_window
        
        logger.info(
            f"TimeSeriesCrossValidator initialized: "
            f"n_splits={n_splits}, test_size={test_size}, expanding={expanding_window}"
        )
    
    def split(
        self,
        data: pd.DataFrame | pd.Series
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate train/test indices for time series cross-validation.
        
        Args:
            data: Input data
        
        Yields:
            Tuple of (train_indices, test_indices) for each split
        """
        n = len(data)
        min_train_size = n - (self.n_splits * self.test_size) - self.gap
        
        if min_train_size < self.test_size:
            raise ValueError(
                f"Insufficient data for {self.n_splits} splits with test_size={self.test_size}. "
                f"Need at least {self.n_splits * self.test_size + self.gap + self.test_size} samples."
            )
        
        splits = []
        
        for i in range(self.n_splits):
            # Calculate test indices
            test_start = n - (self.n_splits - i) * self.test_size
            test_end = test_start + self.test_size
            test_indices = np.arange(test_start, min(test_end, n))
            
            # Calculate train indices
            if self.expanding_window:
                # Expanding window: train from start to test_start - gap
                train_end = test_start - self.gap
                train_indices = np.arange(0, max(0, train_end))
            else:
                # Rolling window: train from (test_start - gap - test_size) to (test_start - gap)
                train_start = max(0, test_start - self.gap - self.test_size)
                train_end = test_start - self.gap
                train_indices = np.arange(train_start, max(0, train_end))
            
            if len(train_indices) > 0 and len(test_indices) > 0:
                splits.append((train_indices, test_indices))
        
        logger.info(f"Generated {len(splits)} CV splits")
        
        return splits
    
    def cross_validate(
        self,
        data: pd.DataFrame | pd.Series,
        model_factory: Callable,
        fit_func: Callable,
        predict_func: Callable,
        target_column: Optional[str] = None
    ) -> Dict[str, List[float]]:
        """
        Perform cross-validation with a model.
        
        Args:
            data: Input data
            model_factory: Function that creates a new model instance
            fit_func: Function to fit the model (model, train_data) -> model
            predict_func: Function to predict (model, test_data) -> predictions
            target_column: Name of target column (for DataFrame)
        
        Returns:
            Dictionary mapping metric names to lists of scores across folds
        """
        from .evaluation import ModelEvaluator
        
        evaluator = ModelEvaluator()
        splits = self.split(data)
        
        all_scores = {}
        
        for fold, (train_idx, test_idx) in enumerate(splits):
            logger.info(f"CV Fold {fold + 1}/{len(splits)}")
            
            # Split data
            if isinstance(data, pd.DataFrame):
                train_data = data.iloc[train_idx]
                test_data = data.iloc[test_idx]
            else:
                train_data = data.iloc[train_idx]
                test_data = data.iloc[test_idx]
            
            # Create and train model
            model = model_factory()
            model = fit_func(model, train_data)
            
            # Predict
            predictions = predict_func(model, test_data)
            
            # Get true values
            if isinstance(test_data, pd.DataFrame):
                if target_column:
                    y_true = test_data[target_column].values
                else:
                    y_true = test_data.iloc[:, -1].values
            else:
                y_true = test_data.values
            
            # Evaluate
            scores = evaluator.evaluate(y_true, predictions)
            
            # Store scores
            for metric, value in scores.items():
                if metric not in all_scores:
                    all_scores[metric] = []
                all_scores[metric].append(value)
        
        # Calculate mean and std
        cv_results = {
            'mean': {metric: np.mean(values) for metric, values in all_scores.items()},
            'std': {metric: np.std(values) for metric, values in all_scores.items()},
            'scores': all_scores
        }
        
        logger.info(f"Cross-validation complete. Mean scores: {cv_results['mean']}")
        
        return cv_results

