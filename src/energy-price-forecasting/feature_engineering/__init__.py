"""
Feature Engineering Module for Energy Price Forecasting.

This module provides comprehensive feature engineering capabilities for time series
price data, including technical indicators, lag features, rolling statistics,
and seasonal decomposition.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

from .indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    add_all_technical_indicators
)

from .time_features import (
    create_lag_features,
    calculate_rolling_statistics,
    seasonal_decompose_features,
    add_all_time_features
)

from .pipeline import FeatureEngineer

__version__ = "1.0.0"

__all__ = [
    # Technical Indicators
    'calculate_sma',
    'calculate_ema',
    'calculate_rsi',
    'calculate_macd',
    'calculate_bollinger_bands',
    'calculate_atr',
    'add_all_technical_indicators',
    
    # Time Features
    'create_lag_features',
    'calculate_rolling_statistics',
    'seasonal_decompose_features',
    'add_all_time_features',
    
    # Pipeline
    'FeatureEngineer',
]

