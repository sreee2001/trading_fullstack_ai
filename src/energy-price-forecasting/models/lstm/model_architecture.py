"""
LSTM Model Architectures for Energy Price Forecasting.

Provides various LSTM architectures including vanilla, bidirectional, and stacked LSTM.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import numpy as np
from typing import Optional, List, Dict, TYPE_CHECKING, Any
import logging

if TYPE_CHECKING:
    from tensorflow import keras

try:
    from tensorflow import keras
    from tensorflow.keras import layers, models
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    keras = None
    layers = None
    models = None

logger = logging.getLogger(__name__)


def create_lstm_model(
    sequence_length: int,
    n_features: int,
    lstm_units: List[int] = [50, 50],
    dropout_rate: float = 0.2,
    forecast_horizon: int = 1,
    dense_units: List[int] = [25],
    activation: str = 'relu',
    output_activation: str = 'linear'
):
    """
    Create a vanilla LSTM model.
    
    Args:
        sequence_length: Length of input sequences
        n_features: Number of features
        lstm_units: List of LSTM units for each layer (default: [50, 50])
        dropout_rate: Dropout rate (default: 0.2)
        forecast_horizon: Number of steps to forecast (default: 1)
        dense_units: List of dense layer units (default: [25])
        activation: Activation function for dense layers (default: 'relu')
        output_activation: Activation function for output layer (default: 'linear')
    
    Returns:
        Compiled Keras LSTM model
    
    Example:
        >>> model = create_lstm_model(sequence_length=60, n_features=10, lstm_units=[64, 32])
        >>> model.summary()
    """
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow is required for LSTM models. Install with: pip install tensorflow")
    
    model = keras.Sequential()
    
    # First LSTM layer (return sequences for stacked LSTM)
    model.add(layers.LSTM(
        lstm_units[0],
        return_sequences=len(lstm_units) > 1,
        input_shape=(sequence_length, n_features)
    ))
    model.add(layers.Dropout(dropout_rate))
    
    # Additional LSTM layers
    for units in lstm_units[1:]:
        model.add(layers.LSTM(units, return_sequences=False))
        model.add(layers.Dropout(dropout_rate))
    
    # Dense layers
    for units in dense_units:
        model.add(layers.Dense(units, activation=activation))
        model.add(layers.Dropout(dropout_rate))
    
    # Output layer
    model.add(layers.Dense(forecast_horizon, activation=output_activation))
    
    logger.info(f"Created LSTM model: {len(lstm_units)} LSTM layers, {len(dense_units)} dense layers")
    
    return model


def create_bidirectional_lstm(
    sequence_length: int,
    n_features: int,
    lstm_units: List[int] = [50, 50],
    dropout_rate: float = 0.2,
    forecast_horizon: int = 1,
    dense_units: List[int] = [25],
    activation: str = 'relu',
    output_activation: str = 'linear'
) -> Any:
    """
    Create a bidirectional LSTM model.
    
    Args:
        sequence_length: Length of input sequences
        n_features: Number of features
        lstm_units: List of LSTM units for each layer (default: [50, 50])
        dropout_rate: Dropout rate (default: 0.2)
        forecast_horizon: Number of steps to forecast (default: 1)
        dense_units: List of dense layer units (default: [25])
        activation: Activation function for dense layers (default: 'relu')
        output_activation: Activation function for output layer (default: 'linear')
    
    Returns:
        Compiled Keras bidirectional LSTM model
    """
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow is required for LSTM models. Install with: pip install tensorflow")
    
    model = keras.Sequential()
    
    # First bidirectional LSTM layer
    model.add(layers.Bidirectional(
        layers.LSTM(
            lstm_units[0],
            return_sequences=len(lstm_units) > 1
        ),
        input_shape=(sequence_length, n_features)
    ))
    model.add(layers.Dropout(dropout_rate))
    
    # Additional bidirectional LSTM layers
    for units in lstm_units[1:]:
        model.add(layers.Bidirectional(layers.LSTM(units, return_sequences=False)))
        model.add(layers.Dropout(dropout_rate))
    
    # Dense layers
    for units in dense_units:
        model.add(layers.Dense(units, activation=activation))
        model.add(layers.Dropout(dropout_rate))
    
    # Output layer
    model.add(layers.Dense(forecast_horizon, activation=output_activation))
    
    logger.info(f"Created Bidirectional LSTM model: {len(lstm_units)} LSTM layers")
    
    return model


def create_stacked_lstm(
    sequence_length: int,
    n_features: int,
    lstm_units: List[int] = [64, 32, 16],
    dropout_rate: float = 0.2,
    forecast_horizon: int = 1,
    dense_units: List[int] = [25],
    activation: str = 'relu',
    output_activation: str = 'linear'
) -> Any:
    """
    Create a stacked (deep) LSTM model.
    
    Args:
        sequence_length: Length of input sequences
        n_features: Number of features
        lstm_units: List of LSTM units for each layer (default: [64, 32, 16])
        dropout_rate: Dropout rate (default: 0.2)
        forecast_horizon: Number of steps to forecast (default: 1)
        dense_units: List of dense layer units (default: [25])
        activation: Activation function for dense layers (default: 'relu')
        output_activation: Activation function for output layer (default: 'linear')
    
    Returns:
        Compiled Keras stacked LSTM model
    """
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow is required for LSTM models. Install with: pip install tensorflow")
    
    model = keras.Sequential()
    
    # Stacked LSTM layers (all return sequences except the last)
    for i, units in enumerate(lstm_units):
        return_sequences = i < len(lstm_units) - 1
        
        if i == 0:
            model.add(layers.LSTM(
                units,
                return_sequences=return_sequences,
                input_shape=(sequence_length, n_features)
            ))
        else:
            model.add(layers.LSTM(units, return_sequences=return_sequences))
        
        model.add(layers.Dropout(dropout_rate))
    
    # Dense layers
    for units in dense_units:
        model.add(layers.Dense(units, activation=activation))
        model.add(layers.Dropout(dropout_rate))
    
    # Output layer
    model.add(layers.Dense(forecast_horizon, activation=output_activation))
    
    logger.info(f"Created Stacked LSTM model: {len(lstm_units)} LSTM layers")
    
    return model

