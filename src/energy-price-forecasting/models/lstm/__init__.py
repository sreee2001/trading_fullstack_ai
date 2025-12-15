"""
LSTM Neural Network Models for Energy Price Forecasting.

This module provides LSTM-based forecasting models including:
- Vanilla LSTM
- Bidirectional LSTM
- Stacked LSTM
- LSTM with Attention

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

from .lstm_model import LSTMForecaster
from .data_preparation import SequenceDataPreparator
from .model_architecture import create_lstm_model, create_bidirectional_lstm, create_stacked_lstm

__version__ = "1.0.0"

__all__ = [
    'LSTMForecaster',
    'SequenceDataPreparator',
    'create_lstm_model',
    'create_bidirectional_lstm',
    'create_stacked_lstm',
]

