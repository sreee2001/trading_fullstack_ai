"""
Multi-Horizon Forecaster.

Provides forecasting for multiple horizons (1, 7, 30 days).

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging

try:
    from models.lstm.lstm_model import LSTMForecaster
    from models.lstm.integration import LSTMWithFeatures
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False
    LSTMForecaster = None
    LSTMWithFeatures = None

from models.baseline import ARIMAForecaster, ProphetForecaster, ExponentialSmoothingForecaster

logger = logging.getLogger(__name__)


class MultiHorizonForecaster:
    """
    Multi-horizon forecaster supporting 1-day, 7-day, and 30-day forecasts.
    
    Provides unified interface for forecasting multiple horizons using
    different model types (LSTM, ARIMA, Prophet, etc.).
    
    Attributes:
        horizons: List of forecast horizons (default: [1, 7, 30])
        model_type: Type of model to use
        models: Dictionary of models per horizon (or single multi-output model)
    
    Example:
        >>> forecaster = MultiHorizonForecaster(model_type='lstm')
        >>> forecaster.fit(train_data, target_col='price')
        >>> predictions = forecaster.predict(test_data)
        >>> # predictions[1] = 1-day ahead, predictions[7] = 7-day ahead, etc.
    """
    
    def __init__(
        self,
        model_type: str = 'lstm',
        horizons: List[int] = [1, 7, 30],
        use_multi_output: bool = True,
        **model_kwargs
    ):
        """
        Initialize MultiHorizonForecaster.
        
        Args:
            model_type: Type of model ('lstm', 'arima', 'prophet', 'exponential_smoothing')
            horizons: List of forecast horizons in days (default: [1, 7, 30])
            use_multi_output: Whether to use single multi-output model (True) or separate models (False)
            **model_kwargs: Additional arguments for the underlying model
        """
        self.model_type = model_type.lower()
        self.horizons = sorted(horizons)
        self.use_multi_output = use_multi_output
        self.model_kwargs = model_kwargs
        
        # Initialize models
        if use_multi_output and self.model_type == 'lstm':
            # Single multi-output LSTM model
            self.models = self._create_multi_output_model()
        else:
            # Separate models for each horizon
            self.models = self._create_separate_models()
        
        self.is_fitted = False
        
        logger.info(
            f"MultiHorizonForecaster initialized: model_type={model_type}, "
            f"horizons={horizons}, use_multi_output={use_multi_output}"
        )
    
    def _create_multi_output_model(self):
        """Create a single multi-output model."""
        if not LSTM_AVAILABLE:
            raise ImportError("LSTM models require TensorFlow")
        
        # For multi-output, we'll use forecast_horizon=max(horizons) and extract specific horizons
        max_horizon = max(self.horizons)
        
        if 'lstm_config' in self.model_kwargs:
            lstm_config = self.model_kwargs.pop('lstm_config')
        else:
            lstm_config = {}
        
        # Create LSTM with features integration for better performance
        model = LSTMWithFeatures(
            sequence_length=self.model_kwargs.get('sequence_length', 60),
            forecast_horizon=max_horizon,
            lstm_config=lstm_config,
            **{k: v for k, v in self.model_kwargs.items() if k != 'sequence_length'}
        )
        
        return {'multi_output': model}
    
    def _create_separate_models(self):
        """Create separate models for each horizon."""
        models = {}
        
        for horizon in self.horizons:
            if self.model_type == 'lstm':
                if not LSTM_AVAILABLE:
                    raise ImportError("LSTM models require TensorFlow")
                
                if 'lstm_config' in self.model_kwargs:
                    lstm_config = self.model_kwargs.pop('lstm_config')
                else:
                    lstm_config = {}
                
                model = LSTMWithFeatures(
                    sequence_length=self.model_kwargs.get('sequence_length', 60),
                    forecast_horizon=horizon,
                    lstm_config=lstm_config,
                    **{k: v for k, v in self.model_kwargs.items() if k != 'sequence_length'}
                )
                models[horizon] = model
            
            elif self.model_type == 'arima':
                model = ARIMAForecaster(**self.model_kwargs)
                models[horizon] = model
            
            elif self.model_type == 'prophet':
                model = ProphetForecaster(**self.model_kwargs)
                models[horizon] = model
            
            elif self.model_type == 'exponential_smoothing':
                model = ExponentialSmoothingForecaster(**self.model_kwargs)
                models[horizon] = model
            
            else:
                raise ValueError(f"Unknown model type: {self.model_type}")
        
        return models
    
    def fit(
        self,
        train_data: pd.DataFrame,
        target_col: str = 'price',
        validation_data: Optional[pd.DataFrame] = None,
        **fit_kwargs
    ):
        """
        Train the forecaster(s) on training data.
        
        Args:
            train_data: Training DataFrame
            target_col: Name of target column
            validation_data: Optional validation DataFrame
            **fit_kwargs: Additional arguments for model.fit()
        """
        logger.info(f"Training multi-horizon forecaster for horizons: {self.horizons}")
        
        if self.use_multi_output and self.model_type == 'lstm':
            # Train single multi-output model
            model = self.models['multi_output']
            model.fit(
                train_data,
                target_col=target_col,
                validation_data=validation_data,
                **fit_kwargs
            )
        else:
            # Train separate models for each horizon
            for horizon, model in self.models.items():
                logger.info(f"Training model for {horizon}-day horizon")
                
                if self.model_type == 'lstm':
                    model.fit(
                        train_data,
                        target_col=target_col,
                        validation_data=validation_data,
                        **fit_kwargs
                    )
                else:
                    # For statistical models, prepare data for specific horizon
                    if hasattr(model, 'fit'):
                        model.fit(train_data[target_col], **fit_kwargs)
                    else:
                        raise ValueError(f"Model {type(model)} does not have fit() method")
        
        self.is_fitted = True
        logger.info("Multi-horizon forecaster training complete")
    
    def predict(
        self,
        data: pd.DataFrame,
        target_col: str = 'price'
    ) -> Dict[int, np.ndarray]:
        """
        Make predictions for all horizons.
        
        Args:
            data: Input DataFrame for prediction
            target_col: Name of target column
        
        Returns:
            Dictionary mapping horizon (days) to predictions array
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        
        predictions = {}
        
        if self.use_multi_output and self.model_type == 'lstm':
            # Use multi-output model
            model = self.models['multi_output']
            multi_predictions = model.predict_multi_horizon(data, num_steps=max(self.horizons))
            
            # Extract predictions for each horizon
            for horizon in self.horizons:
                if horizon in multi_predictions:
                    predictions[horizon] = multi_predictions[horizon]
                else:
                    # Use closest available horizon
                    closest = min(multi_predictions.keys(), key=lambda x: abs(x - horizon))
                    predictions[horizon] = multi_predictions[closest]
        else:
            # Use separate models
            for horizon, model in self.models.items():
                logger.info(f"Predicting for {horizon}-day horizon")
                
                if self.model_type == 'lstm':
                    pred = model.predict(data, target_col=target_col)
                    predictions[horizon] = pred
                else:
                    # For statistical models
                    if hasattr(model, 'predict'):
                        pred = model.predict(steps=horizon)
                        # Extract the horizon-th prediction
                        if isinstance(pred, (list, np.ndarray)):
                            if len(pred) >= horizon:
                                predictions[horizon] = np.array([pred[horizon - 1]])
                            else:
                                predictions[horizon] = np.array([pred[-1]])
                        else:
                            predictions[horizon] = np.array([pred])
                    else:
                        raise ValueError(f"Model {type(model)} does not have predict() method")
        
        return predictions
    
    def predict_single_horizon(
        self,
        data: pd.DataFrame,
        horizon: int,
        target_col: str = 'price'
    ) -> np.ndarray:
        """
        Make prediction for a single horizon.
        
        Args:
            data: Input DataFrame for prediction
            horizon: Forecast horizon in days
            target_col: Name of target column
        
        Returns:
            Predictions array for the specified horizon
        """
        if horizon not in self.horizons:
            raise ValueError(f"Horizon {horizon} not in configured horizons: {self.horizons}")
        
        all_predictions = self.predict(data, target_col=target_col)
        return all_predictions[horizon]
    
    def get_model_summary(self) -> Dict[str, Any]:
        """
        Get summary of all models.
        
        Returns:
            Dictionary with model summaries
        """
        summary = {
            'model_type': self.model_type,
            'horizons': self.horizons,
            'use_multi_output': self.use_multi_output,
            'is_fitted': self.is_fitted,
            'models': {}
        }
        
        if self.use_multi_output:
            summary['models']['multi_output'] = 'Multi-output model'
        else:
            for horizon, model in self.models.items():
                if hasattr(model, 'get_model_summary'):
                    summary['models'][horizon] = model.get_model_summary()
                else:
                    summary['models'][horizon] = f"{type(model).__name__} for {horizon}-day horizon"
        
        return summary

