"""
Advanced Analytics & Insights for Energy Price Forecasting.

Provides correlation analysis, seasonality detection, and other analytical
tools for understanding energy price patterns.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

from .correlation_analysis import CorrelationAnalyzer
from .seasonality_analysis import SeasonalityAnalyzer
from .volatility_forecasting import VolatilityForecaster, VolatilityMetrics
from .anomaly_detection import AnomalyDetector
from .market_regime_detection import MarketRegimeDetector
from .feature_importance import FeatureImportanceAnalyzer
from .insight_generation import InsightGenerator

__version__ = "1.0.0"

__all__ = [
    'CorrelationAnalyzer',
    'SeasonalityAnalyzer',
    'VolatilityForecaster',
    'VolatilityMetrics',
    'AnomalyDetector',
    'MarketRegimeDetector',
    'FeatureImportanceAnalyzer',
    'InsightGenerator',
]

