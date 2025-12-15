"""
Seasonality Analysis for Energy Price Data.

Detects and analyzes seasonal patterns in energy commodity prices.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.stattools import acf, pacf
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    seasonal_decompose = None
    acf = None
    pacf = None

logger = logging.getLogger(__name__)


class SeasonalityAnalyzer:
    """
    Analyzes seasonal patterns in energy price time series.
    
    Provides methods to detect seasonality, decompose time series,
    and identify seasonal components.
    """
    
    def __init__(self):
        """Initialize SeasonalityAnalyzer."""
        if not STATSMODELS_AVAILABLE:
            logger.warning("statsmodels not available - some features will be limited")
        logger.info("SeasonalityAnalyzer initialized")
    
    def detect_seasonality(
        self,
        series: pd.Series,
        period: Optional[int] = None,
        max_period: int = 365
    ) -> Dict[str, any]:
        """
        Detect seasonality in a time series.
        
        Args:
            series: Time series data
            period: Known seasonal period (None = auto-detect)
            max_period: Maximum period to test
            
        Returns:
            Dictionary with seasonality detection results
        """
        logger.info("Detecting seasonality...")
        
        if len(series) < 2 * max_period:
            logger.warning(f"Insufficient data for seasonality detection (need at least {2 * max_period} points)")
            return {
                'has_seasonality': False,
                'reason': 'Insufficient data'
            }
        
        # Remove NaN values
        clean_series = series.dropna()
        
        if len(clean_series) < 2 * max_period:
            return {
                'has_seasonality': False,
                'reason': 'Insufficient data after cleaning'
            }
        
        # If period is specified, test it
        if period:
            periods_to_test = [period]
        else:
            # Test common periods
            periods_to_test = [7, 30, 90, 180, 365]  # Weekly, monthly, quarterly, semi-annual, annual
        
        best_period = None
        best_score = 0
        
        for test_period in periods_to_test:
            if test_period > max_period:
                continue
            
            if len(clean_series) < 2 * test_period:
                continue
            
            # Calculate autocorrelation at seasonal lag
            try:
                autocorr = clean_series.autocorr(lag=test_period)
                if not np.isnan(autocorr) and abs(autocorr) > best_score:
                    best_score = abs(autocorr)
                    best_period = test_period
            except:
                continue
        
        has_seasonality = best_period is not None and best_score > 0.3
        
        return {
            'has_seasonality': has_seasonality,
            'detected_period': best_period,
            'autocorrelation': best_score,
            'tested_periods': periods_to_test
        }
    
    def decompose_time_series(
        self,
        series: pd.Series,
        model: str = 'additive',
        period: Optional[int] = None,
        extrapolate_trend: int = 0
    ) -> Dict[str, pd.Series]:
        """
        Decompose time series into trend, seasonal, and residual components.
        
        Args:
            series: Time series data
            model: Decomposition model ('additive' or 'multiplicative')
            period: Seasonal period (None = auto-detect)
            extrapolate_trend: Number of points to extrapolate trend
            
        Returns:
            Dictionary with decomposed components
        """
        if not STATSMODELS_AVAILABLE:
            logger.error("statsmodels required for time series decomposition")
            return {}
        
        logger.info(f"Decomposing time series (model={model})...")
        
        # Remove NaN values
        clean_series = series.dropna()
        
        if len(clean_series) < 2 * (period or 7):
            logger.warning("Insufficient data for decomposition")
            return {}
        
        # Auto-detect period if not provided
        if period is None:
            seasonality_result = self.detect_seasonality(clean_series)
            period = seasonality_result.get('detected_period', 7)
        
        try:
            decomposition = seasonal_decompose(
                clean_series,
                model=model,
                period=period,
                extrapolate_trend=extrapolate_trend
            )
            
            result = {
                'observed': decomposition.observed,
                'trend': decomposition.trend,
                'seasonal': decomposition.seasonal,
                'residual': decomposition.resid,
                'period': period,
                'model': model
            }
            
            logger.info("Time series decomposition complete")
            return result
            
        except Exception as e:
            logger.error(f"Failed to decompose time series: {e}")
            return {}
    
    def calculate_seasonal_strength(
        self,
        series: pd.Series,
        period: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Calculate seasonal strength metrics.
        
        Args:
            series: Time series data
            period: Seasonal period (None = auto-detect)
            
        Returns:
            Dictionary with seasonal strength metrics
        """
        logger.info("Calculating seasonal strength...")
        
        # Decompose time series
        decomposition = self.decompose_time_series(series, period=period)
        
        if not decomposition:
            return {
                'seasonal_strength': 0.0,
                'trend_strength': 0.0
            }
        
        seasonal = decomposition.get('seasonal')
        trend = decomposition.get('trend')
        residual = decomposition.get('residual')
        
        if seasonal is None or trend is None or residual is None:
            return {
                'seasonal_strength': 0.0,
                'trend_strength': 0.0
            }
        
        # Calculate variances
        var_seasonal = seasonal.var()
        var_residual = residual.var()
        var_trend = trend.var() if trend is not None else 0
        
        total_var = var_seasonal + var_residual
        
        # Seasonal strength: Var(seasonal) / (Var(seasonal) + Var(residual))
        seasonal_strength = var_seasonal / total_var if total_var > 0 else 0.0
        
        # Trend strength: Var(trend) / (Var(trend) + Var(residual))
        trend_total_var = var_trend + var_residual
        trend_strength = var_trend / trend_total_var if trend_total_var > 0 else 0.0
        
        return {
            'seasonal_strength': seasonal_strength,
            'trend_strength': trend_strength,
            'var_seasonal': var_seasonal,
            'var_trend': var_trend,
            'var_residual': var_residual
        }
    
    def identify_seasonal_patterns(
        self,
        series: pd.Series,
        period: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Identify seasonal patterns and characteristics.
        
        Args:
            series: Time series data
            period: Seasonal period (None = auto-detect)
            
        Returns:
            Dictionary with seasonal pattern information
        """
        logger.info("Identifying seasonal patterns...")
        
        # Detect seasonality
        detection = self.detect_seasonality(series, period=period)
        
        if not detection.get('has_seasonality'):
            return {
                'has_seasonality': False,
                'patterns': []
            }
        
        detected_period = detection.get('detected_period')
        
        # Decompose to get seasonal component
        decomposition = self.decompose_time_series(series, period=detected_period)
        
        if not decomposition or 'seasonal' not in decomposition:
            return {
                'has_seasonality': True,
                'patterns': []
            }
        
        seasonal = decomposition['seasonal']
        
        # Analyze seasonal component
        seasonal_mean = seasonal.mean()
        seasonal_std = seasonal.std()
        seasonal_min = seasonal.min()
        seasonal_max = seasonal.max()
        
        # Identify peak and trough periods
        peak_idx = seasonal.idxmax()
        trough_idx = seasonal.idxmin()
        
        patterns = {
            'period': detected_period,
            'mean': seasonal_mean,
            'std': seasonal_std,
            'min': seasonal_min,
            'max': seasonal_max,
            'range': seasonal_max - seasonal_min,
            'peak_period': peak_idx,
            'trough_period': trough_idx,
            'amplitude': (seasonal_max - seasonal_min) / 2
        }
        
        return {
            'has_seasonality': True,
            'detection': detection,
            'patterns': patterns,
            'seasonal_component': seasonal
        }

