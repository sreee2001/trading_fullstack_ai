"""
LSTM Forecaster for Energy Price Forecasting.

Main class for LSTM-based time series forecasting.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple
import logging
from pathlib import Path
from datetime import datetime

try:
    from tensorflow import keras
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    keras = None

from .data_preparation import SequenceDataPreparator
from .model_architecture import create_lstm_model, create_bidirectional_lstm, create_stacked_lstm

logger = logging.getLogger(__name__)


class LSTMForecaster:
    """
    LSTM-based forecaster for energy price prediction.
    
    Provides end-to-end LSTM forecasting including data preparation,
    model training, prediction, and model persistence.
    
    Attributes:
        model: Keras LSTM model
        preparator: SequenceDataPreparator instance
        is_fitted: Whether the model has been trained
        history: Training history
    
    Example:
        >>> forecaster = LSTMForecaster(sequence_length=60, forecast_horizon=1)
        >>> forecaster.fit(train_data, validation_data=val_data, epochs=50)
        >>> predictions = forecaster.predict(test_data)
    """
    
    def __init__(
        self,
        sequence_length: int = 60,
        forecast_horizon: int = 1,
        model_type: str = 'lstm',
        lstm_units: List[int] = [50, 50],
        dropout_rate: float = 0.2,
        dense_units: List[int] = [25],
        scaler_type: str = 'minmax',
        feature_columns: Optional[List[str]] = None,
        learning_rate: float = 0.001,
        loss: str = 'mse',
        metrics: List[str] = None
    ):
        """
        Initialize LSTM Forecaster.
        
        Args:
            sequence_length: Length of input sequences (default: 60)
            forecast_horizon: Number of steps to forecast (default: 1)
            model_type: Type of LSTM model ('lstm', 'bidirectional', 'stacked', default: 'lstm')
            lstm_units: List of LSTM units for each layer (default: [50, 50])
            dropout_rate: Dropout rate (default: 0.2)
            dense_units: List of dense layer units (default: [25])
            scaler_type: Type of scaler ('minmax' or 'standard', default: 'minmax')
            feature_columns: List of feature columns to use (None = use all)
            learning_rate: Learning rate for optimizer (default: 0.001)
            loss: Loss function (default: 'mse')
            metrics: List of metrics to track (default: ['mae', 'mse'])
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for LSTM models. Install with: pip install tensorflow")
        
        self.sequence_length = sequence_length
        self.forecast_horizon = forecast_horizon
        self.model_type = model_type
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.dense_units = dense_units
        self.learning_rate = learning_rate
        self.loss = loss
        
        if metrics is None:
            metrics = ['mae', 'mse']
        self.metrics = metrics
        
        # Initialize data preparator
        self.preparator = SequenceDataPreparator(
            sequence_length=sequence_length,
            forecast_horizon=forecast_horizon,
            scaler_type=scaler_type,
            feature_columns=feature_columns
        )
        
        self.model = None
        self.is_fitted = False
        self.history = None
        self.n_features = None
        
        logger.info(
            f"LSTMForecaster initialized: "
            f"type={model_type}, sequence_length={sequence_length}, forecast_horizon={forecast_horizon}"
        )
    
    def _create_model(self, n_features: int) -> keras.Model:
        """Create the LSTM model architecture."""
        if self.model_type == 'lstm':
            model = create_lstm_model(
                sequence_length=self.sequence_length,
                n_features=n_features,
                lstm_units=self.lstm_units,
                dropout_rate=self.dropout_rate,
                forecast_horizon=self.forecast_horizon,
                dense_units=self.dense_units
            )
        elif self.model_type == 'bidirectional':
            model = create_bidirectional_lstm(
                sequence_length=self.sequence_length,
                n_features=n_features,
                lstm_units=self.lstm_units,
                dropout_rate=self.dropout_rate,
                forecast_horizon=self.forecast_horizon,
                dense_units=self.dense_units
            )
        elif self.model_type == 'stacked':
            model = create_stacked_lstm(
                sequence_length=self.sequence_length,
                n_features=n_features,
                lstm_units=self.lstm_units,
                dropout_rate=self.dropout_rate,
                forecast_horizon=self.forecast_horizon,
                dense_units=self.dense_units
            )
        else:
            raise ValueError(f"Unknown model_type: {self.model_type}. Use 'lstm', 'bidirectional', or 'stacked'")
        
        # Compile model
        optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate)
        model.compile(optimizer=optimizer, loss=self.loss, metrics=self.metrics)
        
        return model
    
    def fit(
        self,
        train_data: pd.DataFrame | pd.Series,
        validation_data: Optional[pd.DataFrame | pd.Series] = None,
        target_column: Optional[str] = None,
        epochs: int = 50,
        batch_size: int = 32,
        verbose: int = 1,
        callbacks: Optional[List] = None,
        validation_split: float = 0.2
    ) -> 'LSTMForecaster':
        """
        Train the LSTM model.
        
        Args:
            train_data: Training data
            validation_data: Validation data (optional)
            target_column: Name of target column
            epochs: Number of training epochs (default: 50)
            batch_size: Batch size (default: 32)
            verbose: Verbosity level (default: 1)
            callbacks: List of Keras callbacks (optional)
            validation_split: Fraction of training data to use for validation (default: 0.2)
        
        Returns:
            Self for method chaining
        """
        logger.info("Starting LSTM model training...")
        
        # Prepare data
        if validation_data is not None:
            X_train, y_train, X_val, y_val = self.preparator.prepare_data(
                train_data, validation_data, target_column
            )
        else:
            X_train, y_train, _, _ = self.preparator.prepare_data(train_data, None, target_column)
            X_val, y_val = None, None
        
        # Get number of features
        self.n_features = X_train.shape[2]
        
        # Create model if not exists
        if self.model is None:
            self.model = self._create_model(self.n_features)
            logger.info("Created LSTM model:")
            self.model.summary(print_fn=logger.info)
        
        # Setup callbacks
        if callbacks is None:
            callbacks = []
            callbacks.append(EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ))
            callbacks.append(ReduceLROnPlateau(
                monitor='val_loss' if X_val is not None else 'loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ))
        
        # Train model
        logger.info(f"Training for {epochs} epochs with batch_size={batch_size}...")
        
        if X_val is not None:
            self.history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                verbose=verbose,
                callbacks=callbacks
            )
        else:
            self.history = self.model.fit(
                X_train, y_train,
                validation_split=validation_split,
                epochs=epochs,
                batch_size=batch_size,
                verbose=verbose,
                callbacks=callbacks
            )
        
        self.is_fitted = True
        logger.info("LSTM model training complete")
        
        return self
    
    def predict(
        self,
        data: pd.DataFrame | pd.Series,
        target_column: Optional[str] = None,
        return_original_scale: bool = True,
        steps: Optional[int] = None
    ) -> np.ndarray:
        """
        Generate predictions.
        
        Args:
            data: Input data for prediction
            target_column: Name of target column (for DataFrame)
            return_original_scale: Whether to return predictions in original scale (default: True)
            steps: Number of steps to predict (for multi-horizon, uses forecast_horizon if None)
        
        Returns:
            Predictions as numpy array
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions. Call fit() first.")
        
        # Prepare data
        X, _, _, _ = self.preparator.prepare_data(data, None, target_column)
        
        # Generate predictions
        predictions_scaled = self.model.predict(X, verbose=0)
        
        # Handle multi-horizon forecasting
        if steps is not None and steps != self.forecast_horizon:
            # For multi-horizon, we need to predict iteratively
            if steps > self.forecast_horizon:
                # Predict recursively
                current_data = data.copy()
                all_predictions = []
                
                for _ in range(steps // self.forecast_horizon):
                    X_current, _, _, _ = self.preparator.prepare_data(current_data, None, target_column)
                    pred_scaled = self.model.predict(X_current, verbose=0)
                    
                    if return_original_scale:
                        pred = self.preparator.inverse_transform(pred_scaled)
                    else:
                        pred = pred_scaled
                    
                    all_predictions.append(pred)
                    
                    # Update current_data with predictions for next iteration
                    # This is a simplified approach - in practice, you'd append to the sequence
                    break  # For now, just return first forecast_horizon steps
                
                predictions_scaled = predictions_scaled[:, :steps] if predictions_scaled.shape[1] > steps else predictions_scaled
        
        # Inverse transform if needed
        if return_original_scale:
            predictions = self.preparator.inverse_transform(predictions_scaled)
        else:
            predictions = predictions_scaled
        
        logger.info(f"Generated predictions: shape {predictions.shape}")
        
        return predictions
    
    def predict_multi_horizon(
        self,
        data: pd.DataFrame | pd.Series,
        horizons: List[int],
        target_column: Optional[str] = None,
        return_original_scale: bool = True
    ) -> Dict[int, np.ndarray]:
        """
        Generate predictions for multiple forecast horizons.
        
        Args:
            data: Input data for prediction
            horizons: List of forecast horizons (e.g., [1, 7, 30] for 1, 7, 30 days ahead)
            target_column: Name of target column
            return_original_scale: Whether to return in original scale
        
        Returns:
            Dictionary mapping horizon to predictions
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions. Call fit() first.")
        
        results = {}
        
        # For each horizon, we need to retrain or use a model trained for that horizon
        # For simplicity, we'll use the current model and predict iteratively
        # In production, you'd train separate models for each horizon
        
        logger.info(f"Generating multi-horizon predictions for horizons: {horizons}")
        
        # Prepare base data
        X, _, _, _ = self.preparator.prepare_data(data, None, target_column)
        
        # Generate base predictions
        base_predictions_scaled = self.model.predict(X, verbose=0)
        
        for horizon in horizons:
            if horizon <= self.forecast_horizon:
                # Use existing predictions
                pred_scaled = base_predictions_scaled[:, :horizon]
            else:
                # For longer horizons, use iterative prediction
                # This is simplified - in practice, use a model trained for that horizon
                pred_scaled = base_predictions_scaled[:, :min(horizon, self.forecast_horizon)]
                logger.warning(f"Horizon {horizon} exceeds model's forecast_horizon {self.forecast_horizon}. Using truncated prediction.")
            
            if return_original_scale:
                pred = self.preparator.inverse_transform(pred_scaled)
            else:
                pred = pred_scaled
            
            results[horizon] = pred
        
        return results
    
    def evaluate(
        self,
        test_data: pd.DataFrame | pd.Series,
        target_column: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Evaluate model on test data.
        
        Args:
            test_data: Test data
            target_column: Name of target column
        
        Returns:
            Dictionary of evaluation metrics
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before evaluation. Call fit() first.")
        
        # Prepare test data
        X_test, y_test, _, _ = self.preparator.prepare_data(test_data, None, target_column)
        
        # Evaluate
        results = self.model.evaluate(X_test, y_test, verbose=0)
        
        # Create metrics dictionary
        metrics_dict = {'loss': results[0]}
        for i, metric_name in enumerate(self.metrics, start=1):
            metrics_dict[metric_name] = results[i]
        
        logger.info(f"Model evaluation: {metrics_dict}")
        
        return metrics_dict
    
    def save_model(self, filepath: str | Path):
        """
        Save the trained model.
        
        Args:
            filepath: Path to save the model
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before saving. Call fit() first.")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        self.model.save(str(filepath))
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str | Path):
        """
        Load a trained model.
        
        Args:
            filepath: Path to the saved model
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for LSTM models")
        
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        self.model = keras.models.load_model(str(filepath))
        self.is_fitted = True
        logger.info(f"Model loaded from {filepath}")
    
    def get_model_summary(self) -> Dict:
        """
        Get model summary information.
        
        Returns:
            Dictionary with model information
        """
        summary = {
            'is_fitted': self.is_fitted,
            'model_type': self.model_type,
            'sequence_length': self.sequence_length,
            'forecast_horizon': self.forecast_horizon,
            'n_features': self.n_features,
            'lstm_units': self.lstm_units,
            'dropout_rate': self.dropout_rate,
            'dense_units': self.dense_units,
        }
        
        if self.history:
            summary['training_history'] = {
                'final_loss': float(self.history.history['loss'][-1]),
                'final_val_loss': float(self.history.history.get('val_loss', [0])[-1]),
                'epochs_trained': len(self.history.history['loss'])
            }
        
        return summary

