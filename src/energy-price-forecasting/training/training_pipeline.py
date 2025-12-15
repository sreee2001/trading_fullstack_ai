"""
Training Pipeline Orchestrator.

Orchestrates the complete training pipeline including data splitting,
model training, evaluation, and cross-validation.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Callable
import logging
from pathlib import Path
from datetime import datetime

from .data_splitting import TimeSeriesSplitter
from .evaluation import ModelEvaluator
from .cross_validation import TimeSeriesCrossValidator
from .config import TrainingConfig

logger = logging.getLogger(__name__)


class TrainingPipeline:
    """
    Orchestrates the complete training pipeline.
    
    Provides end-to-end training workflow including:
    - Data splitting
    - Model training
    - Evaluation
    - Cross-validation (optional)
    - Results tracking
    
    Attributes:
        config: TrainingConfig instance
        splitter: TimeSeriesSplitter instance
        evaluator: ModelEvaluator instance
        results: Training results
    
    Example:
        >>> pipeline = TrainingPipeline(config_path='training_config.yaml')
        >>> results = pipeline.train(model_factory, data)
    """
    
    def __init__(self, config_path: Optional[str] = None, config: Optional[TrainingConfig] = None):
        """
        Initialize TrainingPipeline.
        
        Args:
            config_path: Path to training configuration YAML file
            config: TrainingConfig instance (alternative to file)
        """
        if config:
            self.config = config
        else:
            self.config = TrainingConfig(config_path)
        
        # Initialize components
        self.splitter = TimeSeriesSplitter(
            train_ratio=self.config.get('data_splitting', 'train_ratio'),
            val_ratio=self.config.get('data_splitting', 'val_ratio'),
            test_ratio=self.config.get('data_splitting', 'test_ratio'),
            date_column=self.config.get('data_splitting', 'date_column')
        )
        
        metrics = self.config.get('evaluation', 'metrics')
        self.evaluator = ModelEvaluator(metrics=metrics)
        
        cv_config = self.config.get('cross_validation', {})
        if cv_config.get('enabled', False):
            self.cv = TimeSeriesCrossValidator(
                n_splits=cv_config.get('n_splits', 5),
                test_size=cv_config.get('test_size', 30),
                gap=cv_config.get('gap', 0),
                expanding_window=cv_config.get('expanding_window', True)
            )
        else:
            self.cv = None
        
        self.results = {}
        
        logger.info("TrainingPipeline initialized")
    
    def train(
        self,
        model_factory: Callable,
        data: pd.DataFrame | pd.Series,
        target_column: Optional[str] = None,
        fit_kwargs: Optional[Dict] = None,
        predict_kwargs: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Train a model using the pipeline.
        
        Args:
            model_factory: Function that creates a new model instance
            data: Training data
            target_column: Name of target column (for DataFrame)
            fit_kwargs: Additional arguments for model.fit()
            predict_kwargs: Additional arguments for model.predict()
        
        Returns:
            Dictionary with training results
        """
        logger.info("="*80)
        logger.info("STARTING TRAINING PIPELINE")
        logger.info("="*80)
        
        if fit_kwargs is None:
            fit_kwargs = {}
        if predict_kwargs is None:
            predict_kwargs = {}
        
        # Merge config training parameters
        train_config = self.config.get('model_training', {})
        fit_kwargs.setdefault('epochs', train_config.get('epochs', 50))
        fit_kwargs.setdefault('batch_size', train_config.get('batch_size', 32))
        
        # Split data
        logger.info("Splitting data into train/validation/test sets...")
        train_data, val_data, test_data = self.splitter.split(data)
        
        # Create model
        logger.info("Creating model...")
        model = model_factory()
        
        # Train model
        logger.info("Training model...")
        if hasattr(model, 'fit'):
            # Standard fit interface
            if val_data is not None and len(val_data) > 0:
                model.fit(train_data, validation_data=val_data, **fit_kwargs)
            else:
                model.fit(train_data, **fit_kwargs)
        else:
            raise ValueError("Model must have a fit() method")
        
        # Evaluate on test set
        logger.info("Evaluating on test set...")
        if hasattr(model, 'predict'):
            predictions = model.predict(test_data, **predict_kwargs)
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
        
        # Evaluate
        test_metrics = self.evaluator.evaluate(y_true, predictions)
        
        # Store results
        self.results = {
            'model_type': type(model).__name__,
            'train_size': len(train_data),
            'val_size': len(val_data) if val_data is not None else 0,
            'test_size': len(test_data),
            'test_metrics': test_metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add model summary if available
        if hasattr(model, 'get_model_summary'):
            self.results['model_summary'] = model.get_model_summary()
        
        logger.info("Training pipeline complete")
        logger.info(f"Test metrics: {test_metrics}")
        
        return self.results
    
    def cross_validate(
        self,
        model_factory: Callable,
        data: pd.DataFrame | pd.Series,
        target_column: Optional[str] = None,
        fit_kwargs: Optional[Dict] = None,
        predict_kwargs: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Perform cross-validation.
        
        Args:
            model_factory: Function that creates a new model instance
            data: Training data
            target_column: Name of target column
            fit_kwargs: Additional arguments for model.fit()
            predict_kwargs: Additional arguments for model.predict()
        
        Returns:
            Dictionary with CV results
        """
        if self.cv is None:
            raise ValueError("Cross-validation is not enabled in configuration")
        
        logger.info("Starting cross-validation...")
        
        def fit_func(model, train_data):
            if fit_kwargs:
                if hasattr(model, 'fit'):
                    if isinstance(train_data, pd.DataFrame) and target_column:
                        model.fit(train_data, target_column=target_column, **fit_kwargs)
                    else:
                        model.fit(train_data, **fit_kwargs)
            else:
                if hasattr(model, 'fit'):
                    model.fit(train_data)
            return model
        
        def predict_func(model, test_data):
            if predict_kwargs:
                if hasattr(model, 'predict'):
                    return model.predict(test_data, **predict_kwargs)
            else:
                if hasattr(model, 'predict'):
                    return model.predict(test_data)
            return None
        
        cv_results = self.cv.cross_validate(
            data,
            model_factory,
            fit_func,
            predict_func,
            target_column
        )
        
        self.results['cross_validation'] = cv_results
        
        logger.info(f"Cross-validation complete. Mean scores: {cv_results['mean']}")
        
        return cv_results
    
    def get_results(self) -> Dict[str, Any]:
        """Get training results."""
        return self.results.copy()
    
    def save_results(self, filepath: str):
        """
        Save training results to file.
        
        Args:
            filepath: Path to save results (JSON or YAML)
        """
        import json
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if path.suffix == '.json':
            with open(path, 'w') as f:
                json.dump(self.results, f, indent=2)
        else:
            import yaml
            with open(path, 'w') as f:
                yaml.dump(self.results, f, default_flow_style=False)
        
        logger.info(f"Results saved to {filepath}")

