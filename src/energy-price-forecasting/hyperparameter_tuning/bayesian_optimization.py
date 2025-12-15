"""
Bayesian Optimization Hyperparameter Tuning using Optuna.

Implements Bayesian optimization for hyperparameter tuning.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Callable, Optional, Tuple
import logging
from datetime import datetime

try:
    import optuna
    from optuna import Study, Trial
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    optuna = None
    Study = None
    Trial = None

logger = logging.getLogger(__name__)


class BayesianOptimizer:
    """
    Bayesian optimization hyperparameter tuner using Optuna.
    
    Uses Tree-structured Parzen Estimator (TPE) for intelligent
    hyperparameter search.
    
    Attributes:
        study: Optuna study object
        best_params: Best hyperparameters found
        best_score: Best score achieved
    
    Example:
        >>> optimizer = BayesianOptimizer(n_trials=50)
        >>> best_params, best_model = optimizer.optimize(
        ...     objective_func, param_space, train_data, val_data
        ... )
    """
    
    def __init__(
        self,
        n_trials: int = 50,
        scoring_metric: str = 'rmse',
        minimize: bool = True,
        study_name: Optional[str] = None,
        storage: Optional[str] = None,
        load_if_exists: bool = False,
        random_state: Optional[int] = None
    ):
        """
        Initialize BayesianOptimizer.
        
        Args:
            n_trials: Number of optimization trials
            scoring_metric: Metric to optimize ('rmse', 'mae', 'mape', 'r2')
            minimize: Whether to minimize (True) or maximize (False) the metric
            study_name: Name for the Optuna study
            storage: Storage URL for study persistence (e.g., 'sqlite:///study.db')
            load_if_exists: Whether to load existing study if it exists
            random_state: Random seed for reproducibility
        
        Raises:
            ImportError: If Optuna is not installed
        """
        if not OPTUNA_AVAILABLE:
            raise ImportError(
                "Optuna is required for Bayesian optimization. "
                "Install it with: pip install optuna"
            )
        
        self.n_trials = n_trials
        self.scoring_metric = scoring_metric.lower()
        self.minimize = minimize
        self.study_name = study_name or f"bayesian_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.storage = storage
        self.load_if_exists = load_if_exists
        self.random_state = random_state
        
        # Create or load study
        direction = 'minimize' if minimize else 'maximize'
        self.study = optuna.create_study(
            study_name=self.study_name,
            direction=direction,
            storage=storage,
            load_if_exists=load_if_exists,
            sampler=optuna.samplers.TPESampler(seed=random_state)
        )
        
        self.best_params = None
        self.best_score = None
        self.best_model = None
        
        logger.info(
            f"BayesianOptimizer initialized: n_trials={n_trials}, metric={scoring_metric}, "
            f"minimize={minimize}, study_name={self.study_name}"
        )
    
    def optimize(
        self,
        model_factory: Callable,
        param_space: Dict[str, Any],
        train_data: pd.DataFrame | pd.Series,
        val_data: pd.DataFrame | pd.Series,
        target_column: Optional[str] = None,
        fit_kwargs: Optional[Dict] = None,
        predict_kwargs: Optional[Dict] = None,
        verbose: int = 1
    ) -> Tuple[Dict[str, Any], Any]:
        """
        Perform Bayesian optimization.
        
        Args:
            model_factory: Function that creates model with parameters: model_factory(**params)
            param_space: Dictionary defining parameter search space (see Optuna docs)
            train_data: Training data
            val_data: Validation data
            target_column: Name of target column (for DataFrame)
            fit_kwargs: Additional arguments for model.fit()
            predict_kwargs: Additional arguments for model.predict()
            verbose: Verbosity level (0, 1, or 2)
        
        Returns:
            Tuple of (best_params, best_model)
        
        Example param_space:
            {
                'lstm_units': optuna.trial.Trial.suggest_int('lstm_units', 50, 128),
                'dropout_rate': optuna.trial.Trial.suggest_float('dropout_rate', 0.2, 0.4),
                'learning_rate': optuna.trial.Trial.suggest_loguniform('learning_rate', 0.001, 0.01)
            }
        """
        logger.info("="*80)
        logger.info("STARTING BAYESIAN OPTIMIZATION")
        logger.info("="*80)
        
        if fit_kwargs is None:
            fit_kwargs = {}
        if predict_kwargs is None:
            predict_kwargs = {}
        
        # Store data for objective function
        self._train_data = train_data
        self._val_data = val_data
        self._target_column = target_column
        self._fit_kwargs = fit_kwargs
        self._predict_kwargs = predict_kwargs
        self._model_factory = model_factory
        self._verbose = verbose
        
        # Define objective function
        def objective(trial: Trial) -> float:
            # Sample parameters from search space
            params = {}
            for param_name, param_spec in param_space.items():
                if isinstance(param_spec, dict):
                    # Handle Optuna suggest methods
                    if 'type' in param_spec:
                        if param_spec['type'] == 'int':
                            params[param_name] = trial.suggest_int(
                                param_name,
                                param_spec.get('low', 1),
                                param_spec.get('high', 100)
                            )
                        elif param_spec['type'] == 'float':
                            params[param_name] = trial.suggest_float(
                                param_name,
                                param_spec.get('low', 0.0),
                                param_spec.get('high', 1.0),
                                log=param_spec.get('log', False)
                            )
                        elif param_spec['type'] == 'categorical':
                            params[param_name] = trial.suggest_categorical(
                                param_name,
                                param_spec.get('choices', [])
                            )
                    else:
                        # Direct value (for fixed parameters)
                        params[param_name] = param_spec.get('value')
                elif isinstance(param_spec, list):
                    # List of choices (categorical)
                    params[param_name] = trial.suggest_categorical(param_name, param_spec)
                else:
                    # Direct value (for fixed parameters)
                    params[param_name] = param_spec
            
            # Create and train model
            try:
                model = model_factory(**params)
                
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
                
                if verbose >= 2:
                    logger.info(f"Trial {trial.number}: params={params}, score={score:.6f}")
                
                return score
                
            except Exception as e:
                logger.error(f"Trial {trial.number} failed: {e}")
                return float('inf') if self.minimize else float('-inf')
        
        # Run optimization
        self.study.optimize(objective, n_trials=self.n_trials, show_progress_bar=(verbose >= 1))
        
        # Get best results
        self.best_params = self.study.best_params
        self.best_score = self.study.best_value
        self.best_trial = self.study.best_trial
        
        # Recreate best model
        best_model = model_factory(**self.best_params)
        if hasattr(best_model, 'fit'):
            if isinstance(train_data, pd.DataFrame) and target_column:
                best_model.fit(train_data, target_column=target_column, **fit_kwargs)
            else:
                best_model.fit(train_data, **fit_kwargs)
        self.best_model = best_model
        
        logger.info("="*80)
        logger.info("BAYESIAN OPTIMIZATION COMPLETE")
        logger.info(f"Best score: {self.best_score:.6f}")
        logger.info(f"Best parameters: {self.best_params}")
        logger.info("="*80)
        
        return self.best_params, self.best_model
    
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
    
    def get_parameter_importance(self) -> pd.DataFrame:
        """
        Get parameter importance analysis.
        
        Returns:
            DataFrame with parameter importance scores
        """
        if not OPTUNA_AVAILABLE:
            raise ImportError("Optuna is required for parameter importance analysis")
        
        try:
            importance = optuna.importance.get_param_importances(self.study)
            return pd.DataFrame(
                list(importance.items()),
                columns=['parameter', 'importance']
            ).sort_values('importance', ascending=False)
        except Exception as e:
            logger.warning(f"Could not calculate parameter importance: {e}")
            return pd.DataFrame(columns=['parameter', 'importance'])
    
    def save_study(self, filepath: str):
        """
        Save study to file.
        
        Args:
            filepath: Path to save study (SQLite database)
        """
        if self.storage is None:
            # Create a new study with storage
            import sqlite3
            from pathlib import Path
            
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            storage_url = f"sqlite:///{filepath}"
            self.study = optuna.create_study(
                study_name=self.study_name,
                direction='minimize' if self.minimize else 'maximize',
                storage=storage_url,
                load_if_exists=True
            )
            logger.info(f"Study saved to {filepath}")
        else:
            logger.info(f"Study already persisted to {self.storage}")
    
    def load_study(self, filepath: str):
        """
        Load study from file.
        
        Args:
            filepath: Path to study file (SQLite database)
        """
        storage_url = f"sqlite:///{filepath}"
        self.study = optuna.load_study(
            study_name=self.study_name,
            storage=storage_url
        )
        self.best_params = self.study.best_params
        self.best_score = self.study.best_value
        logger.info(f"Study loaded from {filepath}")
    
    def get_results_dataframe(self) -> pd.DataFrame:
        """
        Get all trial results as a DataFrame.
        
        Returns:
            DataFrame with trial results
        """
        if not OPTUNA_AVAILABLE:
            return pd.DataFrame()
        
        trials = self.study.trials
        results = []
        
        for trial in trials:
            if trial.state == optuna.trial.TrialState.COMPLETE:
                results.append({
                    'trial': trial.number,
                    'params': trial.params,
                    'value': trial.value,
                    'datetime_start': trial.datetime_start,
                    'datetime_complete': trial.datetime_complete
                })
        
        return pd.DataFrame(results)
    
    def get_best_result(self) -> Dict[str, Any]:
        """
        Get best result.
        
        Returns:
            Dictionary with best_params, best_score, best_model
        """
        return {
            'params': self.best_params,
            'score': self.best_score,
            'model': self.best_model,
            'trial': self.best_trial
        }

