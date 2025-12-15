"""
Integration utilities for LSTM models with feature engineering.

Provides seamless integration between feature engineering pipeline
and LSTM model training.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict
import logging

try:
    from feature_engineering import FeatureEngineer
    FEATURE_ENG_AVAILABLE = True
except ImportError:
    FEATURE_ENG_AVAILABLE = False
    FeatureEngineer = None

from .lstm_model import LSTMForecaster

logger = logging.getLogger(__name__)


class LSTMWithFeatures:
    """
    LSTM forecaster with integrated feature engineering.
    
    Combines feature engineering pipeline with LSTM model for
    end-to-end forecasting with rich feature sets.
    
    Attributes:
        feature_engineer: FeatureEngineer instance
        lstm_forecaster: LSTMForecaster instance
        is_fitted: Whether both components are fitted
    
    Example:
        >>> forecaster = LSTMWithFeatures(sequence_length=60)
        >>> forecaster.fit(train_data, target_col='price')
        >>> predictions = forecaster.predict(test_data)
    """
    
    def __init__(
        self,
        sequence_length: int = 60,
        forecast_horizon: int = 1,
        model_type: str = 'lstm',
        lstm_units: List[int] = [50, 50],
        feature_engineering_config: Optional[str] = None,
        **lstm_kwargs
    ):
        """
        Initialize LSTM with feature engineering.
        
        Args:
            sequence_length: Length of input sequences
            forecast_horizon: Number of steps to forecast
            model_type: Type of LSTM model ('lstm', 'bidirectional', 'stacked')
            lstm_units: List of LSTM units
            feature_engineering_config: Path to feature engineering config YAML
            **lstm_kwargs: Additional arguments for LSTMForecaster
        """
        if not FEATURE_ENG_AVAILABLE:
            raise ImportError("Feature engineering module is required. Ensure feature_engineering is installed.")
        
        # Initialize feature engineer
        self.feature_engineer = FeatureEngineer(config_path=feature_engineering_config)
        
        # Initialize LSTM forecaster
        self.lstm_forecaster = LSTMForecaster(
            sequence_length=sequence_length,
            forecast_horizon=forecast_horizon,
            model_type=model_type,
            lstm_units=lstm_units,
            **lstm_kwargs
        )
        
        self.is_fitted = False
        
        logger.info("LSTMWithFeatures initialized with feature engineering integration")
    
    def fit(
        self,
        train_data: pd.DataFrame | pd.Series,
        validation_data: Optional[pd.DataFrame | pd.Series] = None,
        target_col: str = 'price',
        epochs: int = 50,
        batch_size: int = 32,
        **kwargs
    ) -> 'LSTMWithFeatures':
        """
        Fit the model with feature engineering.
        
        Args:
            train_data: Training data
            validation_data: Validation data (optional)
            target_col: Name of target column
            epochs: Number of training epochs
            batch_size: Batch size
            **kwargs: Additional arguments for LSTM training
        
        Returns:
            Self for method chaining
        """
        logger.info("Starting LSTM training with feature engineering...")
        
        # Apply feature engineering to training data
        logger.info("Applying feature engineering to training data...")
        train_features = self.feature_engineer.transform(train_data.copy())
        
        # Apply feature engineering to validation data if provided
        if validation_data is not None:
            logger.info("Applying feature engineering to validation data...")
            val_features = self.feature_engineer.transform(validation_data.copy())
        else:
            val_features = None
        
        # Train LSTM model
        logger.info("Training LSTM model on engineered features...")
        # Remove target_column from kwargs if present to avoid duplicate
        fit_kwargs = {k: v for k, v in kwargs.items() if k not in ('target_column', 'target_col')}
        self.lstm_forecaster.fit(
            train_features,
            validation_data=val_features,
            target_column=target_col,
            epochs=epochs,
            batch_size=batch_size,
            **fit_kwargs
        )
        
        self.is_fitted = True
        logger.info("LSTM training with features complete")
        
        return self
    
    def predict(
        self,
        data: pd.DataFrame | pd.Series,
        target_col: str = 'price',
        return_original_scale: bool = True
    ) -> np.ndarray:
        """
        Generate predictions with feature engineering.
        
        Args:
            data: Input data
            target_col: Name of target column
            return_original_scale: Whether to return in original scale
        
        Returns:
            Predictions as numpy array
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction. Call fit() first.")
        
        # Apply feature engineering
        logger.info("Applying feature engineering to prediction data...")
        data_features = self.feature_engineer.transform(data.copy())
        
        # Generate predictions
        predictions = self.lstm_forecaster.predict(
            data_features,
            target_column=target_col,
            return_original_scale=return_original_scale
        )
        
        return predictions
    
    def evaluate(
        self,
        test_data: pd.DataFrame | pd.Series,
        target_col: str = 'price'
    ) -> Dict[str, float]:
        """
        Evaluate model on test data.
        
        Args:
            test_data: Test data
            target_col: Name of target column
        
        Returns:
            Dictionary of evaluation metrics
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before evaluation. Call fit() first.")
        
        # Apply feature engineering
        test_features = self.feature_engineer.transform(test_data.copy())
        
        # Evaluate
        return self.lstm_forecaster.evaluate(test_features, target_column=target_col)
    
    def get_summary(self) -> Dict:
        """
        Get summary of model and features.
        
        Returns:
            Dictionary with model and feature information
        """
        summary = {
            'is_fitted': self.is_fitted,
            'feature_engineering': self.feature_engineer.get_summary(),
            'lstm_model': self.lstm_forecaster.get_model_summary()
        }
        
        return summary

