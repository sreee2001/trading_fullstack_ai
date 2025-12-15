"""
Multi-Horizon Forecasting Module.

Provides multi-horizon forecasting capabilities for 1-day, 7-day, and 30-day
forecast horizons with horizon-specific evaluation.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

from .multi_horizon_forecaster import MultiHorizonForecaster
from .horizon_evaluator import HorizonEvaluator
from .horizon_features import HorizonFeatureEngineer

__version__ = "1.0.0"

__all__ = [
    'MultiHorizonForecaster',
    'HorizonEvaluator',
    'HorizonFeatureEngineer',
]

