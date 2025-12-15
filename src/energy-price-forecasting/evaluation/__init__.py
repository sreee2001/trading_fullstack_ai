"""
Model Evaluation & Backtesting Module.

Provides comprehensive evaluation and backtesting capabilities for forecasting models.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

from .walk_forward import WalkForwardValidator
from .performance_metrics import PerformanceMetrics
from .backtesting import BacktestingEngine
from .statistical_metrics import StatisticalMetrics
from .trading_simulator import TradingSimulator
from .model_comparison_dashboard import ModelComparisonDashboard

__version__ = "1.0.0"

__all__ = [
    'WalkForwardValidator',
    'PerformanceMetrics',
    'BacktestingEngine',
    'StatisticalMetrics',
    'TradingSimulator',
    'ModelComparisonDashboard',
]

