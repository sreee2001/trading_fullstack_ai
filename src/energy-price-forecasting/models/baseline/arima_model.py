"""
ARIMA/SARIMA Model Implementation for Energy Price Forecasting.

Implements Auto ARIMA and SARIMA models for time series forecasting.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Tuple, List
import logging
from datetime import datetime

try:
    from pmdarima import auto_arima
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
except ImportError as e:
    logging.warning(f"ARIMA dependencies not installed: {e}")
    auto_arima = None
    ARIMA = None
    SARIMAX = None

logger = logging.getLogger(__name__)


class ARIMAModel:
    """
    ARIMA/SARIMA model for time series forecasting.
    
    Supports both ARIMA and seasonal ARIMA (SARIMA) models with automatic
    parameter selection using auto_arima.
    
    Attributes:
        model: Fitted ARIMA/SARIMA model
        order: ARIMA order (p, d, q)
        seasonal_order: SARIMA seasonal order (P, D, Q, s)
        is_fitted: Whether the model has been fitted
        model_type: 'ARIMA' or 'SARIMA'
    
    Example:
        >>> model = ARIMAModel()
        >>> model.fit(train_data['price'])
        >>> forecasts = model.predict(steps=30)
        >>> print(f"Forecast: {forecasts}")
    """
    
    def __init__(
        self,
        order: Optional[Tuple[int, int, int]] = None,
        seasonal_order: Optional[Tuple[int, int, int, int]] = None,
        auto_select: bool = True,
        seasonal: bool = True,
        max_p: int = 5,
        max_d: int = 2,
        max_q: int = 5,
        max_P: int = 2,
        max_D: int = 1,
        max_Q: int = 2,
        seasonal_periods: int = 7,
        information_criterion: str = 'aic'
    ):
        """
        Initialize ARIMA/SARIMA model.
        
        Args:
            order: Manual ARIMA order (p, d, q). If None and auto_select=True, will be auto-selected.
            seasonal_order: Manual SARIMA seasonal order (P, D, Q, s). If None and auto_select=True, will be auto-selected.
            auto_select: Whether to automatically select best parameters (default: True)
            seasonal: Whether to use seasonal ARIMA (SARIMA) (default: True)
            max_p, max_d, max_q: Maximum values for ARIMA order search
            max_P, max_D, max_Q: Maximum values for SARIMA seasonal order search
            seasonal_periods: Seasonal period (default: 7 for weekly seasonality)
            information_criterion: Information criterion for model selection ('aic', 'bic', 'aicc')
        """
        if auto_arima is None:
            raise ImportError("pmdarima is required for ARIMA models. Install with: pip install pmdarima")
        
        self.order = order
        self.seasonal_order = seasonal_order
        self.auto_select = auto_select
        self.seasonal = seasonal
        self.max_p = max_p
        self.max_d = max_d
        self.max_q = max_q
        self.max_P = max_P
        self.max_D = max_D
        self.max_Q = max_Q
        self.seasonal_periods = seasonal_periods
        self.information_criterion = information_criterion
        
        self.model = None
        self.is_fitted = False
        self.model_type = 'SARIMA' if seasonal else 'ARIMA'
        self.fitted_order = None
        self.fitted_seasonal_order = None
        
        logger.info(f"ARIMAModel initialized (type: {self.model_type}, auto_select: {auto_select})")
    
    def fit(self, data: pd.Series, verbose: bool = False) -> 'ARIMAModel':
        """
        Fit the ARIMA/SARIMA model to the data.
        
        Args:
            data: Time series data (pandas Series with datetime index or numeric values)
            verbose: Whether to print model selection progress
        
        Returns:
            Self for method chaining
        
        Example:
            >>> model = ARIMAModel()
            >>> model.fit(train_data['price'])
        """
        if len(data) < 20:
            raise ValueError(f"Insufficient data for ARIMA model. Need at least 20 observations, got {len(data)}")
        
        # Convert to pandas Series if needed
        if isinstance(data, pd.DataFrame):
            if len(data.columns) == 1:
                data = data.iloc[:, 0]
            else:
                raise ValueError("DataFrame must have a single column for ARIMA")
        
        if not isinstance(data, pd.Series):
            data = pd.Series(data)
        
        # Remove NaN values
        data = data.dropna()
        
        if len(data) < 20:
            raise ValueError(f"Insufficient data after removing NaN. Need at least 20 observations, got {len(data)}")
        
        logger.info(f"Fitting {self.model_type} model on {len(data)} observations...")
        
        try:
            if self.auto_select:
                # Use auto_arima to find best parameters
                logger.info("Auto-selecting best ARIMA parameters...")
                
                model = auto_arima(
                    data,
                    start_p=0,
                    start_q=0,
                    max_p=self.max_p,
                    max_d=self.max_d,
                    max_q=self.max_q,
                    start_P=0,
                    start_Q=0,
                    max_P=self.max_P,
                    max_D=self.max_D,
                    max_Q=self.max_Q,
                    seasonal=self.seasonal,
                    m=self.seasonal_periods if self.seasonal else 1,
                    stepwise=True,
                    suppress_warnings=True,
                    error_action='ignore',
                    information_criterion=self.information_criterion,
                    verbose=1 if verbose else 0
                )
                
                self.model = model
                self.fitted_order = model.order
                self.fitted_seasonal_order = model.seasonal_order if self.seasonal else None
                
                logger.info(f"Best {self.model_type} order: {self.fitted_order}")
                if self.fitted_seasonal_order:
                    logger.info(f"Best seasonal order: {self.fitted_seasonal_order}")
            
            else:
                # Use manual parameters
                if self.order is None:
                    raise ValueError("order must be specified when auto_select=False")
                
                if self.seasonal and self.seasonal_order is None:
                    raise ValueError("seasonal_order must be specified when seasonal=True and auto_select=False")
                
                if self.seasonal:
                    self.model = SARIMAX(
                        data,
                        order=self.order,
                        seasonal_order=self.seasonal_order
                    ).fit(disp=1 if verbose else 0)
                else:
                    self.model = ARIMA(data, order=self.order).fit()
                
                self.fitted_order = self.order
                self.fitted_seasonal_order = self.seasonal_order if self.seasonal else None
            
            self.is_fitted = True
            logger.info(f"{self.model_type} model fitted successfully")
            
        except Exception as e:
            logger.error(f"Error fitting {self.model_type} model: {e}")
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
        
        Example:
            >>> forecasts = model.predict(steps=30)
            >>> forecasts, conf_int = model.predict(steps=30, return_conf_int=True)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions. Call fit() first.")
        
        try:
            if hasattr(self.model, 'predict'):
                # pmdarima auto_arima model
                forecast = self.model.predict(n_periods=steps)
                
                if return_conf_int:
                    conf_int = self.model.predict(n_periods=steps, return_conf_int=True)[1]
                    return forecast, conf_int
                else:
                    return forecast
            
            else:
                # statsmodels ARIMA/SARIMA model
                forecast = self.model.forecast(steps=steps)
                
                if return_conf_int:
                    conf_int = self.model.get_forecast(steps=steps).conf_int(alpha=alpha)
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
                'model_type': self.model_type
            }
        
        summary = {
            'is_fitted': True,
            'model_type': self.model_type,
            'order': self.fitted_order,
            'seasonal_order': self.fitted_seasonal_order,
        }
        
        # Try to get AIC, BIC if available
        try:
            if hasattr(self.model, 'aic'):
                summary['aic'] = self.model.aic
            if hasattr(self.model, 'bic'):
                summary['bic'] = self.model.bic
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
            if hasattr(self.model, 'resid'):
                return self.model.resid
            elif hasattr(self.model, 'residuals'):
                return self.model.residuals
            else:
                raise ValueError("Model does not have residuals attribute")
        except Exception as e:
            logger.error(f"Error getting residuals: {e}")
            raise

