"""
Technical Indicators for Feature Engineering.

Implements common technical analysis indicators including:
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA)
- Relative Strength Index (RSI)
- Moving Average Convergence Divergence (MACD)
- Bollinger Bands
- Average True Range (ATR)

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_sma(df: pd.DataFrame, column: str = 'price', windows: List[int] = None) -> pd.DataFrame:
    """
    Calculate Simple Moving Average (SMA) for specified windows.
    
    Args:
        df: Input DataFrame with price data
        column: Column name to calculate SMA on (default: 'price')
        windows: List of window sizes (default: [5, 10, 20, 50, 200])
    
    Returns:
        DataFrame with SMA columns added (sma_5, sma_10, etc.)
    
    Example:
        >>> df = pd.DataFrame({'price': [100, 102, 101, 103, 105]})
        >>> df_with_sma = calculate_sma(df, windows=[3, 5])
        >>> print(df_with_sma.columns)
        Index(['price', 'sma_3', 'sma_5'], dtype='object')
    """
    if windows is None:
        windows = [5, 10, 20, 50, 200]
    
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    df_result = df.copy()
    
    for window in windows:
        col_name = f'sma_{window}'
        df_result[col_name] = df_result[column].rolling(window=window, min_periods=1).mean()
        logger.debug(f"Calculated {col_name} with window size {window}")
    
    return df_result


def calculate_ema(df: pd.DataFrame, column: str = 'price', windows: List[int] = None) -> pd.DataFrame:
    """
    Calculate Exponential Moving Average (EMA) for specified windows.
    
    EMA gives more weight to recent prices, making it more responsive to new information.
    
    Args:
        df: Input DataFrame with price data
        column: Column name to calculate EMA on (default: 'price')
        windows: List of window sizes (default: [5, 10, 20, 50, 200])
    
    Returns:
        DataFrame with EMA columns added (ema_5, ema_10, etc.)
    
    Example:
        >>> df = pd.DataFrame({'price': [100, 102, 101, 103, 105]})
        >>> df_with_ema = calculate_ema(df, windows=[3, 5])
        >>> print(df_with_ema.columns)
        Index(['price', 'ema_3', 'ema_5'], dtype='object')
    """
    if windows is None:
        windows = [5, 10, 20, 50, 200]
    
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    df_result = df.copy()
    
    for window in windows:
        col_name = f'ema_{window}'
        df_result[col_name] = df_result[column].ewm(span=window, adjust=False).mean()
        logger.debug(f"Calculated {col_name} with window size {window}")
    
    return df_result


def calculate_rsi(df: pd.DataFrame, column: str = 'price', period: int = 14) -> pd.DataFrame:
    """
    Calculate Relative Strength Index (RSI).
    
    RSI measures the magnitude of recent price changes to evaluate overbought
    or oversold conditions. Values range from 0 to 100.
    - RSI > 70: Overbought condition
    - RSI < 30: Oversold condition
    
    Args:
        df: Input DataFrame with price data
        column: Column name to calculate RSI on (default: 'price')
        period: Period for RSI calculation (default: 14)
    
    Returns:
        DataFrame with RSI column added (rsi_14)
    
    Example:
        >>> df = pd.DataFrame({'price': [100, 102, 101, 103, 105, 104, 106]})
        >>> df_with_rsi = calculate_rsi(df, period=5)
        >>> assert 'rsi_5' in df_with_rsi.columns
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    df_result = df.copy()
    
    # Calculate price changes
    delta = df_result[column].diff()
    
    # Separate gains and losses
    gains = delta.where(delta > 0, 0.0)
    losses = -delta.where(delta < 0, 0.0)
    
    # Calculate exponential moving average of gains and losses
    avg_gains = gains.ewm(span=period, adjust=False).mean()
    avg_losses = losses.ewm(span=period, adjust=False).mean()
    
    # Calculate Relative Strength (RS)
    rs = avg_gains / avg_losses
    
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    
    col_name = f'rsi_{period}'
    df_result[col_name] = rsi
    
    logger.debug(f"Calculated {col_name} with period {period}")
    
    return df_result


def calculate_macd(
    df: pd.DataFrame,
    column: str = 'price',
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> pd.DataFrame:
    """
    Calculate Moving Average Convergence Divergence (MACD).
    
    MACD is a trend-following momentum indicator that shows the relationship
    between two moving averages of prices.
    
    Components:
    - MACD Line: Fast EMA - Slow EMA
    - Signal Line: EMA of MACD Line
    - Histogram: MACD Line - Signal Line
    
    Args:
        df: Input DataFrame with price data
        column: Column name to calculate MACD on (default: 'price')
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line period (default: 9)
    
    Returns:
        DataFrame with MACD columns added (macd, macd_signal, macd_histogram)
    
    Example:
        >>> df = pd.DataFrame({'price': np.random.randn(100) + 100})
        >>> df_with_macd = calculate_macd(df)
        >>> assert all(col in df_with_macd.columns for col in ['macd', 'macd_signal', 'macd_histogram'])
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    df_result = df.copy()
    
    # Calculate fast and slow EMAs
    fast_ema = df_result[column].ewm(span=fast_period, adjust=False).mean()
    slow_ema = df_result[column].ewm(span=slow_period, adjust=False).mean()
    
    # Calculate MACD line
    macd_line = fast_ema - slow_ema
    
    # Calculate signal line (EMA of MACD line)
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Calculate histogram (MACD line - Signal line)
    histogram = macd_line - signal_line
    
    df_result['macd'] = macd_line
    df_result['macd_signal'] = signal_line
    df_result['macd_histogram'] = histogram
    
    logger.debug(f"Calculated MACD with periods: fast={fast_period}, slow={slow_period}, signal={signal_period}")
    
    return df_result


def calculate_bollinger_bands(
    df: pd.DataFrame,
    column: str = 'price',
    period: int = 20,
    num_std: float = 2.0
) -> pd.DataFrame:
    """
    Calculate Bollinger Bands.
    
    Bollinger Bands consist of:
    - Middle Band: SMA (typically 20-period)
    - Upper Band: Middle Band + (num_std * standard deviation)
    - Lower Band: Middle Band - (num_std * standard deviation)
    
    Args:
        df: Input DataFrame with price data
        column: Column name to calculate Bollinger Bands on (default: 'price')
        period: Period for moving average and std calculation (default: 20)
        num_std: Number of standard deviations (default: 2.0)
    
    Returns:
        DataFrame with Bollinger Band columns added (bb_middle, bb_upper, bb_lower, bb_width)
    
    Example:
        >>> df = pd.DataFrame({'price': np.random.randn(100) + 100})
        >>> df_with_bb = calculate_bollinger_bands(df)
        >>> assert all(col in df_with_bb.columns for col in ['bb_middle', 'bb_upper', 'bb_lower'])
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    df_result = df.copy()
    
    # Calculate middle band (SMA)
    middle_band = df_result[column].rolling(window=period, min_periods=1).mean()
    
    # Calculate standard deviation
    std = df_result[column].rolling(window=period, min_periods=1).std()
    
    # Calculate upper and lower bands
    upper_band = middle_band + (num_std * std)
    lower_band = middle_band - (num_std * std)
    
    # Calculate band width (useful for volatility analysis)
    band_width = upper_band - lower_band
    
    df_result['bb_middle'] = middle_band
    df_result['bb_upper'] = upper_band
    df_result['bb_lower'] = lower_band
    df_result['bb_width'] = band_width
    
    logger.debug(f"Calculated Bollinger Bands with period={period}, num_std={num_std}")
    
    return df_result


def calculate_atr(
    df: pd.DataFrame,
    high_col: str = 'high',
    low_col: str = 'low',
    close_col: str = 'close',
    period: int = 14
) -> pd.DataFrame:
    """
    Calculate Average True Range (ATR).
    
    ATR is a technical indicator that measures market volatility by decomposing
    the entire range of an asset price for that period.
    
    True Range is the greatest of:
    - Current High - Current Low
    - |Current High - Previous Close|
    - |Current Low - Previous Close|
    
    Args:
        df: Input DataFrame with OHLC data
        high_col: Column name for high prices (default: 'high')
        low_col: Column name for low prices (default: 'low')
        close_col: Column name for close prices (default: 'close')
        period: Period for ATR calculation (default: 14)
    
    Returns:
        DataFrame with ATR column added (atr_14)
    
    Example:
        >>> df = pd.DataFrame({
        ...     'high': [102, 104, 103, 105, 107],
        ...     'low': [98, 100, 99, 101, 103],
        ...     'close': [100, 102, 101, 103, 105]
        ... })
        >>> df_with_atr = calculate_atr(df)
        >>> assert 'atr_14' in df_with_atr.columns
    """
    required_cols = [high_col, low_col, close_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    df_result = df.copy()
    
    # Calculate True Range components
    high_low = df_result[high_col] - df_result[low_col]
    high_close = (df_result[high_col] - df_result[close_col].shift()).abs()
    low_close = (df_result[low_col] - df_result[close_col].shift()).abs()
    
    # True Range is the maximum of the three
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Calculate ATR as EMA of True Range
    atr = true_range.ewm(span=period, adjust=False).mean()
    
    col_name = f'atr_{period}'
    df_result[col_name] = atr
    
    logger.debug(f"Calculated {col_name} with period {period}")
    
    return df_result


def add_all_technical_indicators(
    df: pd.DataFrame,
    price_col: str = 'price',
    has_ohlc: bool = False,
    sma_windows: List[int] = None,
    ema_windows: List[int] = None,
    rsi_period: int = 14,
    macd_params: Tuple[int, int, int] = (12, 26, 9),
    bb_period: int = 20,
    atr_period: int = 14
) -> pd.DataFrame:
    """
    Add all technical indicators to the DataFrame.
    
    This is a convenience function that applies all technical indicators in one call.
    
    Args:
        df: Input DataFrame with price data
        price_col: Column name for price (default: 'price')
        has_ohlc: Whether DataFrame has OHLC data (high, low, close) for ATR (default: False)
        sma_windows: Windows for SMA (default: [5, 10, 20, 50, 200])
        ema_windows: Windows for EMA (default: [5, 10, 20, 50, 200])
        rsi_period: Period for RSI (default: 14)
        macd_params: Tuple of (fast, slow, signal) for MACD (default: (12, 26, 9))
        bb_period: Period for Bollinger Bands (default: 20)
        atr_period: Period for ATR (default: 14, only if has_ohlc=True)
    
    Returns:
        DataFrame with all technical indicators added
    
    Example:
        >>> df = pd.DataFrame({'price': np.random.randn(100) + 100})
        >>> df_enriched = add_all_technical_indicators(df)
        >>> assert 'sma_20' in df_enriched.columns
        >>> assert 'rsi_14' in df_enriched.columns
        >>> assert 'macd' in df_enriched.columns
    """
    df_result = df.copy()
    
    logger.info("Adding all technical indicators...")
    
    # Add moving averages
    df_result = calculate_sma(df_result, column=price_col, windows=sma_windows)
    df_result = calculate_ema(df_result, column=price_col, windows=ema_windows)
    
    # Add RSI
    df_result = calculate_rsi(df_result, column=price_col, period=rsi_period)
    
    # Add MACD
    fast, slow, signal = macd_params
    df_result = calculate_macd(df_result, column=price_col, fast_period=fast, slow_period=slow, signal_period=signal)
    
    # Add Bollinger Bands
    df_result = calculate_bollinger_bands(df_result, column=price_col, period=bb_period)
    
    # Add ATR if OHLC data is available
    if has_ohlc:
        df_result = calculate_atr(df_result, period=atr_period)
    
    num_indicators = len([col for col in df_result.columns if col not in df.columns])
    logger.info(f"Added {num_indicators} technical indicator features")
    
    return df_result

