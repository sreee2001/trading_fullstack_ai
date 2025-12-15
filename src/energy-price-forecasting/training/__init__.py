"""
Model Training Infrastructure for Energy Price Forecasting.

Provides training pipeline orchestration, data splitting, evaluation,
and cross-validation utilities.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

from .data_splitting import TimeSeriesSplitter
from .evaluation import ModelEvaluator
from .cross_validation import TimeSeriesCrossValidator
from .training_pipeline import TrainingPipeline
from .config import TrainingConfig

__version__ = "1.0.0"

__all__ = [
    'TimeSeriesSplitter',
    'ModelEvaluator',
    'TimeSeriesCrossValidator',
    'TrainingPipeline',
    'TrainingConfig',
]

