"""
Facebook Prophet Model for Energy Price Forecasting.

Implements Prophet model for time series forecasting with automatic
seasonality detection.

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
    from prophet import Prophet
except ImportError:
    Prophet = None

logger = logging.getLogger(__name__)


class ProphetModel:
    """
    Facebook Prophet model for time series forecasting.
    
    Prophet is designed for forecasting time series data with strong seasonal
    patterns and multiple seasons of different periods.
    
    Attributes:
        model: Fitted Prophet model
        is_fitted: Whether the model has been fitted
    
    Example:
        >>> model = ProphetModel()
        >>> model.fit(train_data[['date', 'price']])
        >>> forecasts = model.predict(steps=30)
    """
    
    def __init__(
        self,
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = True,
        daily_seasonality: bool = False,
        seasonality_mode: str = 'additive',
        changepoint_prior_scale: float = 0.05,
        seasonality_prior_scale: float = 10.0,
        holidays: Optional[pd.DataFrame] = None,
        growth: str = 'linear'
    ):
        """
        Initialize Prophet model.
        
        Args:
            yearly_seasonality: Whether to include yearly seasonality (default: True)
            weekly_seasonality: Whether to include weekly seasonality (default: True)
            daily_seasonality: Whether to include daily seasonality (default: False)
            seasonality_mode: 'additive' or 'multiplicative' (default: 'additive')
            changepoint_prior_scale: Flexibility of changepoints (default: 0.05)
            seasonality_prior_scale: Strength of seasonality (default: 10.0)
            holidays: DataFrame with holidays (columns: holiday, ds)
            growth: Growth model ('linear' or 'logistic')
        """
        if Prophet is None:
            raise ImportError("prophet is required for Prophet models. Install with: pip install prophet")
        
        self.yearly_seasonality = yearly_seasonality
        self.weekly_seasonality = weekly_seasonality
        self.daily_seasonality = daily_seasonality
        self.seasonality_mode = seasonality_mode
        self.changepoint_prior_scale = changepoint_prior_scale
        self.seasonality_prior_scale = seasonality_prior_scale
        self.holidays = holidays
        self.growth = growth
        
        self.model = None
        self.is_fitted = False
        
        logger.info(f"ProphetModel initialized (yearly={yearly_seasonality}, weekly={weekly_seasonality})")
    
    def fit(
        self,
        data: pd.DataFrame | pd.Series,
        date_col: Optional[str] = None,
        value_col: Optional[str] = None,
        verbose: bool = False
    ) -> 'ProphetModel':
        """
        Fit the Prophet model to the data.
        
        Args:
            data: Time series data. Can be:
                - DataFrame with 'ds' (date) and 'y' (value) columns
                - DataFrame with date and value columns (specify date_col and value_col)
                - Series with datetime index
            date_col: Name of date column (if DataFrame without 'ds' column)
            value_col: Name of value column (if DataFrame without 'y' column)
            verbose: Whether to print fitting progress
        
        Returns:
            Self for method chaining
        """
        # Prepare data for Prophet (needs 'ds' and 'y' columns)
        if isinstance(data, pd.Series):
            if not isinstance(data.index, pd.DatetimeIndex):
                raise ValueError("Series must have DatetimeIndex for Prophet")
            prophet_data = pd.DataFrame({
                'ds': data.index,
                'y': data.values
            })
        
        elif isinstance(data, pd.DataFrame):
            if 'ds' in data.columns and 'y' in data.columns:
                prophet_data = data[['ds', 'y']].copy()
            elif date_col and value_col:
                prophet_data = pd.DataFrame({
                    'ds': pd.to_datetime(data[date_col]),
                    'y': data[value_col].values
                })
            elif len(data.columns) == 2:
                # Assume first column is date, second is value
                prophet_data = pd.DataFrame({
                    'ds': pd.to_datetime(data.iloc[:, 0]),
                    'y': data.iloc[:, 1].values
                })
            else:
                raise ValueError(
                    "DataFrame must have 'ds' and 'y' columns, or specify date_col and value_col, "
                    "or have exactly 2 columns (date, value)"
                )
        else:
            raise ValueError("Data must be pandas DataFrame or Series")
        
        # Remove NaN values
        prophet_data = prophet_data.dropna()
        
        if len(prophet_data) < 2:
            raise ValueError(f"Insufficient data for Prophet model. Need at least 2 observations, got {len(prophet_data)}")
        
        # Ensure 'ds' is datetime
        prophet_data['ds'] = pd.to_datetime(prophet_data['ds'])
        
        # Sort by date
        prophet_data = prophet_data.sort_values('ds').reset_index(drop=True)
        
        logger.info(f"Fitting Prophet model on {len(prophet_data)} observations...")
        
        try:
            self.model = Prophet(
                yearly_seasonality=self.yearly_seasonality,
                weekly_seasonality=self.weekly_seasonality,
                daily_seasonality=self.daily_seasonality,
                seasonality_mode=self.seasonality_mode,
                changepoint_prior_scale=self.changepoint_prior_scale,
                seasonality_prior_scale=self.seasonality_prior_scale,
                holidays=self.holidays,
                growth=self.growth
            )
            
            self.model.fit(prophet_data)
            
            self.is_fitted = True
            logger.info("Prophet model fitted successfully")
            
        except Exception as e:
            logger.error(f"Error fitting Prophet model: {e}")
            raise
        
        return self
    
    def predict(
        self,
        steps: int = 1,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        return_conf_int: bool = False
    ) -> pd.DataFrame | Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate forecasts.
        
        Args:
            steps: Number of steps ahead to forecast (if start_date/end_date not provided)
            start_date: Start date for forecast period
            end_date: End date for forecast period
            return_conf_int: Whether to return confidence intervals
        
        Returns:
            DataFrame with forecasts (columns: ds, yhat, yhat_lower, yhat_upper),
            or tuple of (forecasts, None) if return_conf_int=False
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions. Call fit() first.")
        
        try:
            # Create future dates
            if start_date and end_date:
                future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
            else:
                # Get last date from training data
                last_date = self.model.history['ds'].max()
                future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps, freq='D')
            
            future_df = pd.DataFrame({'ds': future_dates})
            
            # Generate forecast
            forecast = self.model.predict(future_df)
            
            if return_conf_int:
                # Prophet always returns confidence intervals
                return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], None
            else:
                return forecast[['ds', 'yhat']]
        
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
                'model_type': 'Prophet'
            }
        
        summary = {
            'is_fitted': True,
            'model_type': 'Prophet',
            'yearly_seasonality': self.yearly_seasonality,
            'weekly_seasonality': self.weekly_seasonality,
            'daily_seasonality': self.daily_seasonality,
            'seasonality_mode': self.seasonality_mode,
            'growth': self.growth,
        }
        
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
            # Prophet doesn't directly provide residuals, calculate them
            fitted_values = self.model.predict(self.model.history)['yhat']
            actual_values = self.model.history['y'].values
            residuals = actual_values - fitted_values.values
            return pd.Series(residuals, index=self.model.history['ds'])
        except Exception as e:
            logger.error(f"Error getting residuals: {e}")
            raise

