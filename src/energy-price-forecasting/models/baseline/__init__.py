"""
Baseline Statistical Models for Energy Price Forecasting.

This module provides baseline statistical forecasting models including:
- ARIMA/SARIMA models
- Exponential Smoothing
- Facebook Prophet

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

from .arima_model import ARIMAModel
from .exponential_smoothing import ExponentialSmoothingModel
from .prophet_model import ProphetModel
from .model_comparison import ModelComparison
from .benchmarking import ModelBenchmark

__version__ = "1.0.0"

__all__ = [
    'ARIMAModel',
    'ExponentialSmoothingModel',
    'ProphetModel',
    'ModelComparison',
    'ModelBenchmark',
]

