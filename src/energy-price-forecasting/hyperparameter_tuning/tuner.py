"""
Unified Hyperparameter Tuner.

Provides a unified interface for all hyperparameter tuning methods.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
from typing import Dict, List, Any, Callable, Optional, Tuple
import logging

from .search_space import HyperparameterSearchSpace
from .grid_search import GridSearchTuner
from .random_search import RandomSearchTuner
from .bayesian_optimization import BayesianOptimizer

logger = logging.getLogger(__name__)


class HyperparameterTuner:
    """
    Unified hyperparameter tuner.
    
    Provides a single interface for grid search, random search, and
    Bayesian optimization.
    
    Attributes:
        method: Tuning method ('grid', 'random', 'bayesian')
        tuner: Underlying tuner instance
    
    Example:
        >>> tuner = HyperparameterTuner(method='bayesian', n_trials=50)
        >>> best_params, best_model = tuner.tune(
        ...     model_factory, 'lstm', train_data, val_data
        ... )
    """
    
    def __init__(
        self,
        method: str = 'random',
        search_space_config: Optional[str] = None,
        scoring_metric: str = 'rmse',
        minimize: bool = True,
        **method_kwargs
    ):
        """
        Initialize HyperparameterTuner.
        
        Args:
            method: Tuning method ('grid', 'random', 'bayesian')
            search_space_config: Path to search space configuration file
            scoring_metric: Metric to optimize ('rmse', 'mae', 'mape', 'r2')
            minimize: Whether to minimize (True) or maximize (False) the metric
            **method_kwargs: Additional arguments for specific method:
                - grid: (none)
                - random: n_iter (default: 20), random_state
                - bayesian: n_trials (default: 50), study_name, storage, random_state
        """
        self.method = method.lower()
        self.scoring_metric = scoring_metric
        self.minimize = minimize
        
        # Initialize search space
        self.search_space = HyperparameterSearchSpace(search_space_config)
        
        # Initialize appropriate tuner
        if self.method == 'grid':
            self.tuner = GridSearchTuner(
                scoring_metric=scoring_metric,
                minimize=minimize
            )
        elif self.method == 'random':
            n_iter = method_kwargs.get('n_iter', 20)
            random_state = method_kwargs.get('random_state', None)
            self.tuner = RandomSearchTuner(
                n_iter=n_iter,
                scoring_metric=scoring_metric,
                minimize=minimize,
                random_state=random_state
            )
        elif self.method == 'bayesian':
            n_trials = method_kwargs.get('n_trials', 50)
            study_name = method_kwargs.get('study_name', None)
            storage = method_kwargs.get('storage', None)
            load_if_exists = method_kwargs.get('load_if_exists', False)
            random_state = method_kwargs.get('random_state', None)
            self.tuner = BayesianOptimizer(
                n_trials=n_trials,
                scoring_metric=scoring_metric,
                minimize=minimize,
                study_name=study_name,
                storage=storage,
                load_if_exists=load_if_exists,
                random_state=random_state
            )
        else:
            raise ValueError(
                f"Unknown tuning method: {method}. "
                f"Choose from: 'grid', 'random', 'bayesian'"
            )
        
        logger.info(f"HyperparameterTuner initialized with method: {method}")
    
    def tune(
        self,
        model_factory: Callable,
        model_type: str,
        train_data: pd.DataFrame | pd.Series,
        val_data: pd.DataFrame | pd.Series,
        target_column: Optional[str] = None,
        param_space: Optional[Dict[str, List[Any]]] = None,
        fit_kwargs: Optional[Dict] = None,
        predict_kwargs: Optional[Dict] = None,
        verbose: int = 1
    ) -> Tuple[Dict[str, Any], Any]:
        """
        Tune hyperparameters for a model.
        
        Args:
            model_factory: Function that creates model with parameters: model_factory(**params)
            model_type: Type of model ('lstm', 'arima', 'prophet', etc.)
            train_data: Training data
            val_data: Validation data
            target_column: Name of target column (for DataFrame)
            param_space: Custom parameter search space (overrides default for model_type)
            fit_kwargs: Additional arguments for model.fit()
            predict_kwargs: Additional arguments for model.predict()
            verbose: Verbosity level (0, 1, or 2)
        
        Returns:
            Tuple of (best_params, best_model)
        """
        # Get search space
        if param_space is None:
            param_space = self.search_space.get_search_space(model_type)
        
        # Convert search space format for Bayesian optimization
        if self.method == 'bayesian':
            # Convert list-based space to Optuna format
            optuna_space = {}
            for param_name, param_values in param_space.items():
                if isinstance(param_values, list):
                    if all(isinstance(v, int) for v in param_values):
                        # Integer parameter
                        optuna_space[param_name] = {
                            'type': 'int',
                            'low': min(param_values),
                            'high': max(param_values)
                        }
                    elif all(isinstance(v, float) for v in param_values):
                        # Float parameter
                        optuna_space[param_name] = {
                            'type': 'float',
                            'low': min(param_values),
                            'high': max(param_values),
                            'log': False
                        }
                    else:
                        # Categorical parameter
                        optuna_space[param_name] = {
                            'type': 'categorical',
                            'choices': param_values
                        }
                else:
                    optuna_space[param_name] = param_values
            
            # Use Bayesian optimizer
            return self.tuner.optimize(
                model_factory,
                optuna_space,
                train_data,
                val_data,
                target_column,
                fit_kwargs,
                predict_kwargs,
                verbose
            )
        else:
            # Use grid or random search
            return self.tuner.search(
                model_factory,
                param_space,
                train_data,
                val_data,
                target_column,
                fit_kwargs,
                predict_kwargs,
                verbose
            )
    
    def get_results(self) -> pd.DataFrame:
        """
        Get tuning results as DataFrame.
        
        Returns:
            DataFrame with trial results
        """
        if hasattr(self.tuner, 'get_results_dataframe'):
            return self.tuner.get_results_dataframe()
        else:
            return pd.DataFrame()
    
    def get_best_result(self) -> Dict[str, Any]:
        """
        Get best tuning result.
        
        Returns:
            Dictionary with best_params, best_score, best_model
        """
        return self.tuner.get_best_result()
    
    def get_parameter_importance(self) -> pd.DataFrame:
        """
        Get parameter importance (Bayesian optimization only).
        
        Returns:
            DataFrame with parameter importance scores
        """
        if self.method == 'bayesian' and hasattr(self.tuner, 'get_parameter_importance'):
            return self.tuner.get_parameter_importance()
        else:
            logger.warning("Parameter importance only available for Bayesian optimization")
            return pd.DataFrame(columns=['parameter', 'importance'])

