"""
Time-Based Features for Feature Engineering.

Implements time series transformation features including:
- Lag features
- Rolling window statistics
- Seasonal decomposition

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging
from statsmodels.tsa.seasonal import seasonal_decompose

logger = logging.getLogger(__name__)


def create_lag_features(
    df: pd.DataFrame,
    column: str = 'price',
    lags: List[int] = None
) -> pd.DataFrame:
    """
    Create lag features for specified column.
    
    Lag features capture historical values, allowing models to learn from
    past patterns. For example, lag_1 is yesterday's price, lag_7 is the
    price from 7 days ago.
    
    Args:
        df: Input DataFrame with time series data
        column: Column name to create lags for (default: 'price')
        lags: List of lag periods (default: [1, 7, 30])
    
    Returns:
        DataFrame with lag columns added (price_lag_1, price_lag_7, etc.)
    
    Example:
        >>> df = pd.DataFrame({'price': [100, 102, 101, 103, 105]})
        >>> df_with_lags = create_lag_features(df, lags=[1, 2])
        >>> print(df_with_lags.columns)
        Index(['price', 'price_lag_1', 'price_lag_2'], dtype='object')
    """
    if lags is None:
        lags = [1, 7, 30]
    
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    df_result = df.copy()
    
    for lag in lags:
        col_name = f'{column}_lag_{lag}'
        df_result[col_name] = df_result[column].shift(lag)
        logger.debug(f"Created {col_name} with lag period {lag}")
    
    logger.info(f"Created {len(lags)} lag features for '{column}'")
    
    return df_result


def calculate_rolling_statistics(
    df: pd.DataFrame,
    column: str = 'price',
    windows: List[int] = None,
    statistics: List[str] = None
) -> pd.DataFrame:
    """
    Calculate rolling window statistics.
    
    Rolling statistics capture short-term and long-term trends and volatility
    in the time series data.
    
    Args:
        df: Input DataFrame with time series data
        column: Column name to calculate statistics for (default: 'price')
        windows: List of window sizes (default: [7, 30, 90])
        statistics: List of statistics to calculate (default: ['mean', 'std', 'min', 'max'])
    
    Returns:
        DataFrame with rolling statistic columns added
    
    Example:
        >>> df = pd.DataFrame({'price': np.random.randn(100) + 100})
        >>> df_with_stats = calculate_rolling_statistics(df, windows=[7, 30])
        >>> assert 'price_roll_7_mean' in df_with_stats.columns
        >>> assert 'price_roll_30_std' in df_with_stats.columns
    """
    if windows is None:
        windows = [7, 30, 90]
    
    if statistics is None:
        statistics = ['mean', 'std', 'min', 'max']
    
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    df_result = df.copy()
    feature_count = 0
    
    for window in windows:
        rolling_window = df_result[column].rolling(window=window, min_periods=1)
        
        for stat in statistics:
            col_name = f'{column}_roll_{window}_{stat}'
            
            if stat == 'mean':
                df_result[col_name] = rolling_window.mean()
            elif stat == 'std':
                df_result[col_name] = rolling_window.std()
            elif stat == 'min':
                df_result[col_name] = rolling_window.min()
            elif stat == 'max':
                df_result[col_name] = rolling_window.max()
            elif stat == 'median':
                df_result[col_name] = rolling_window.median()
            elif stat == 'var':
                df_result[col_name] = rolling_window.var()
            elif stat == 'skew':
                df_result[col_name] = rolling_window.skew()
            elif stat == 'kurt':
                df_result[col_name] = rolling_window.kurt()
            else:
                logger.warning(f"Unknown statistic '{stat}', skipping...")
                continue
            
            feature_count += 1
            logger.debug(f"Calculated {col_name} with window size {window}")
    
    logger.info(f"Created {feature_count} rolling statistic features for '{column}'")
    
    return df_result


def seasonal_decompose_features(
    df: pd.DataFrame,
    column: str = 'price',
    model: str = 'additive',
    period: Optional[int] = None,
    extrapolate_trend: str = 'freq'
) -> pd.DataFrame:
    """
    Perform seasonal decomposition and add components as features.
    
    Seasonal decomposition separates a time series into three components:
    - Trend: Long-term increase or decrease in the data
    - Seasonal: Regular pattern of ups and downs
    - Residual: Random, irregular influences
    
    Args:
        df: Input DataFrame with time series data
        column: Column name to decompose (default: 'price')
        model: 'additive' or 'multiplicative' (default: 'additive')
        period: Period of the seasonal component (default: None, auto-detected)
        extrapolate_trend: How to handle NaN in trend ('freq' or int)
    
    Returns:
        DataFrame with decomposition components added (trend, seasonal, residual)
    
    Example:
        >>> dates = pd.date_range('2024-01-01', periods=100)
        >>> df = pd.DataFrame({
        ...     'date': dates,
        ...     'price': np.random.randn(100) + 100 + np.sin(np.arange(100) * 0.1) * 5
        ... })
        >>> df_decomp = seasonal_decompose_features(df, period=30)
        >>> assert 'price_trend' in df_decomp.columns
        >>> assert 'price_seasonal' in df_decomp.columns
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    df_result = df.copy()
    
    # Check if we have enough data points
    min_points = period * 2 if period else 20
    if len(df_result) < min_points:
        logger.warning(f"Not enough data points for seasonal decomposition (need at least {min_points}). "
                      f"Filling with NaN values.")
        df_result[f'{column}_trend'] = np.nan
        df_result[f'{column}_seasonal'] = np.nan
        df_result[f'{column}_residual'] = np.nan
        return df_result
    
    try:
        # Perform seasonal decomposition
        decomposition = seasonal_decompose(
            df_result[column],
            model=model,
            period=period,
            extrapolate_trend=extrapolate_trend
        )
        
        # Add components as features
        df_result[f'{column}_trend'] = decomposition.trend
        df_result[f'{column}_seasonal'] = decomposition.seasonal
        df_result[f'{column}_residual'] = decomposition.resid
        
        logger.info(f"Performed seasonal decomposition for '{column}' with model='{model}', period={period}")
        
    except Exception as e:
        logger.error(f"Seasonal decomposition failed: {e}. Filling with NaN values.")
        df_result[f'{column}_trend'] = np.nan
        df_result[f'{column}_seasonal'] = np.nan
        df_result[f'{column}_residual'] = np.nan
    
    return df_result


def create_date_features(
    df: pd.DataFrame,
    date_column: str = 'date'
) -> pd.DataFrame:
    """
    Create features from date/timestamp column.
    
    Extracts useful temporal features like:
    - Day of week
    - Month
    - Quarter
    - Year
    - Day of month
    - Week of year
    - Is weekend
    
    Args:
        df: Input DataFrame with date column
        date_column: Name of the date column (default: 'date')
    
    Returns:
        DataFrame with date-based features added
    
    Example:
        >>> df = pd.DataFrame({
        ...     'date': pd.date_range('2024-01-01', periods=10),
        ...     'price': np.random.randn(10) + 100
        ... })
        >>> df_with_dates = create_date_features(df)
        >>> assert 'day_of_week' in df_with_dates.columns
        >>> assert 'month' in df_with_dates.columns
    """
    if date_column not in df.columns:
        raise ValueError(f"Column '{date_column}' not found in DataFrame")
    
    df_result = df.copy()
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df_result[date_column]):
        df_result[date_column] = pd.to_datetime(df_result[date_column])
    
    # Extract date features
    df_result['day_of_week'] = df_result[date_column].dt.dayofweek
    df_result['month'] = df_result[date_column].dt.month
    df_result['quarter'] = df_result[date_column].dt.quarter
    df_result['year'] = df_result[date_column].dt.year
    df_result['day_of_month'] = df_result[date_column].dt.day
    df_result['week_of_year'] = df_result[date_column].dt.isocalendar().week
    df_result['is_weekend'] = (df_result['day_of_week'] >= 5).astype(int)
    
    logger.info(f"Created 7 date-based features from '{date_column}'")
    
    return df_result


def add_all_time_features(
    df: pd.DataFrame,
    price_col: str = 'price',
    date_col: Optional[str] = None,
    lag_periods: List[int] = None,
    rolling_windows: List[int] = None,
    rolling_statistics: List[str] = None,
    seasonal_period: Optional[int] = None,
    seasonal_model: str = 'additive'
) -> pd.DataFrame:
    """
    Add all time-based features to the DataFrame.
    
    This is a convenience function that applies all time-based transformations in one call.
    
    Args:
        df: Input DataFrame with time series data
        price_col: Column name for price (default: 'price')
        date_col: Column name for date (default: None, skip date features)
        lag_periods: Periods for lag features (default: [1, 7, 30])
        rolling_windows: Windows for rolling statistics (default: [7, 30, 90])
        rolling_statistics: Statistics to calculate (default: ['mean', 'std', 'min', 'max'])
        seasonal_period: Period for seasonal decomposition (default: None, auto-detect)
        seasonal_model: 'additive' or 'multiplicative' (default: 'additive')
    
    Returns:
        DataFrame with all time-based features added
    
    Example:
        >>> df = pd.DataFrame({
        ...     'date': pd.date_range('2024-01-01', periods=100),
        ...     'price': np.random.randn(100) + 100
        ... })
        >>> df_enriched = add_all_time_features(df, date_col='date')
        >>> assert 'price_lag_1' in df_enriched.columns
        >>> assert 'price_roll_30_mean' in df_enriched.columns
    """
    df_result = df.copy()
    
    logger.info("Adding all time-based features...")
    
    # Add lag features
    df_result = create_lag_features(df_result, column=price_col, lags=lag_periods)
    
    # Add rolling statistics
    df_result = calculate_rolling_statistics(
        df_result,
        column=price_col,
        windows=rolling_windows,
        statistics=rolling_statistics
    )
    
    # Add seasonal decomposition
    if len(df_result) >= 20:  # Minimum required for decomposition
        df_result = seasonal_decompose_features(
            df_result,
            column=price_col,
            model=seasonal_model,
            period=seasonal_period
        )
    else:
        logger.warning("Not enough data for seasonal decomposition, skipping...")
    
    # Add date features if date column is specified
    if date_col and date_col in df_result.columns:
        df_result = create_date_features(df_result, date_column=date_col)
    
    num_features = len([col for col in df_result.columns if col not in df.columns])
    logger.info(f"Added {num_features} time-based features")
    
    return df_result

