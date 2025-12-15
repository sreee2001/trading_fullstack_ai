"""
Exponential Smoothing Models for Energy Price Forecasting.

Implements Holt-Winters exponential smoothing (additive and multiplicative).

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Tuple
import logging
from datetime import datetime

try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
except ImportError:
    ExponentialSmoothing = None

logger = logging.getLogger(__name__)


class ExponentialSmoothingModel:
    """
    Exponential Smoothing model for time series forecasting.
    
    Supports Holt-Winters exponential smoothing with additive and multiplicative
    seasonality.
    
    Attributes:
        model: Fitted exponential smoothing model
        trend: Trend component type ('add', 'mul', None)
        seasonal: Seasonal component type ('add', 'mul', None)
        seasonal_periods: Number of periods in a season
        is_fitted: Whether the model has been fitted
    
    Example:
        >>> model = ExponentialSmoothingModel(seasonal_periods=7)
        >>> model.fit(train_data['price'])
        >>> forecasts = model.predict(steps=30)
    """
    
    def __init__(
        self,
        trend: Optional[str] = 'add',
        seasonal: Optional[str] = 'add',
        seasonal_periods: int = 7,
        damped_trend: bool = False,
        use_boxcox: bool = False
    ):
        """
        Initialize Exponential Smoothing model.
        
        Args:
            trend: Type of trend component ('add', 'mul', None)
            seasonal: Type of seasonal component ('add', 'mul', None)
            seasonal_periods: Number of periods in a season (default: 7 for weekly)
            damped_trend: Whether to use damped trend (default: False)
            use_boxcox: Whether to apply Box-Cox transformation (default: False)
        """
        if ExponentialSmoothing is None:
            raise ImportError("statsmodels is required for Exponential Smoothing. Install with: pip install statsmodels")
        
        self.trend = trend
        self.seasonal = seasonal
        self.seasonal_periods = seasonal_periods
        self.damped_trend = damped_trend
        self.use_boxcox = use_boxcox
        
        self.model = None
        self.is_fitted = False
        
        logger.info(f"ExponentialSmoothingModel initialized (trend={trend}, seasonal={seasonal}, periods={seasonal_periods})")
    
    def fit(self, data: pd.Series, verbose: bool = False) -> 'ExponentialSmoothingModel':
        """
        Fit the exponential smoothing model to the data.
        
        Args:
            data: Time series data (pandas Series)
            verbose: Whether to print fitting progress
        
        Returns:
            Self for method chaining
        """
        if len(data) < 2 * self.seasonal_periods:
            raise ValueError(
                f"Insufficient data for exponential smoothing. "
                f"Need at least {2 * self.seasonal_periods} observations, got {len(data)}"
            )
        
        # Convert to pandas Series if needed
        if isinstance(data, pd.DataFrame):
            if len(data.columns) == 1:
                data = data.iloc[:, 0]
            else:
                raise ValueError("DataFrame must have a single column for exponential smoothing")
        
        if not isinstance(data, pd.Series):
            data = pd.Series(data)
        
        # Remove NaN values
        data = data.dropna()
        
        if len(data) < 2 * self.seasonal_periods:
            raise ValueError(
                f"Insufficient data after removing NaN. "
                f"Need at least {2 * self.seasonal_periods} observations, got {len(data)}"
            )
        
        logger.info(f"Fitting Exponential Smoothing model on {len(data)} observations...")
        
        try:
            self.model = ExponentialSmoothing(
                data,
                trend=self.trend,
                seasonal=self.seasonal,
                seasonal_periods=self.seasonal_periods,
                damped_trend=self.damped_trend,
                use_boxcox=self.use_boxcox
            ).fit(optimized=True, remove_bias=True)
            
            self.is_fitted = True
            logger.info("Exponential Smoothing model fitted successfully")
            
        except Exception as e:
            logger.error(f"Error fitting Exponential Smoothing model: {e}")
            raise
        
        return self
    
    def predict(
        self,
        steps: int = 1,
        return_conf_int: bool = False,
        alpha: float = 0.05
    ) -> pd.Series | Tuple[pd.Series, pd.DataFrame]:
        """
        Generate forecasts.
        
        Args:
            steps: Number of steps ahead to forecast
            return_conf_int: Whether to return confidence intervals
            alpha: Significance level for confidence intervals (default: 0.05 for 95% CI)
        
        Returns:
            Forecasts as pandas Series, or tuple of (forecasts, confidence_intervals) if return_conf_int=True
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions. Call fit() first.")
        
        try:
            forecast = self.model.forecast(steps=steps)
            
            if return_conf_int:
                # Get confidence intervals
                conf_int = self.model.get_prediction(
                    start=len(self.model.fittedvalues),
                    end=len(self.model.fittedvalues) + steps - 1
                ).conf_int(alpha=alpha)
                return forecast, conf_int
            else:
                return forecast
        
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            raise
    
    def get_model_summary(self) -> Dict:
        """
        Get model summary information.
        
        Returns:
            Dictionary with model information
        """
        if not self.is_fitted:
            return {
                'is_fitted': False,
                'model_type': 'ExponentialSmoothing'
            }
        
        summary = {
            'is_fitted': True,
            'model_type': 'ExponentialSmoothing',
            'trend': self.trend,
            'seasonal': self.seasonal,
            'seasonal_periods': self.seasonal_periods,
            'damped_trend': self.damped_trend,
        }
        
        # Try to get AIC, BIC, SSE if available
        try:
            if hasattr(self.model, 'aic'):
                summary['aic'] = self.model.aic
            if hasattr(self.model, 'bic'):
                summary['bic'] = self.model.bic
            if hasattr(self.model, 'sse'):
                summary['sse'] = self.model.sse
        except:
            pass
        
        return summary
    
    def get_residuals(self) -> pd.Series:
        """
        Get model residuals.
        
        Returns:
            Residuals as pandas Series
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before getting residuals. Call fit() first.")
        
        try:
            return self.model.resid
        except Exception as e:
            logger.error(f"Error getting residuals: {e}")
            raise

