"""
Trading Signal Generation Module.

Provides trading signal generation logic based on model predictions.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

from .signal_generator import SignalGenerator
from .signal_strategies import SignalStrategies

__version__ = "1.0.0"

__all__ = [
    'SignalGenerator',
    'SignalStrategies',
]

