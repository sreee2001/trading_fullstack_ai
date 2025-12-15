"""
Unit tests for feature engineering technical indicators.

Tests all technical indicator functions including SMA, EMA, RSI, MACD,
Bollinger Bands, and ATR.

Author: AI Assistant
Date: December 14, 2025
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_engineering.indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    add_all_technical_indicators
)


@pytest.fixture
def sample_price_data():
    """Create sample price data for testing."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100)
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    
    return pd.DataFrame({
        'date': dates,
        'price': prices
    })


@pytest.fixture
def sample_ohlc_data():
    """Create sample OHLC data for testing."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100)
    close_prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    
    return pd.DataFrame({
        'date': dates,
        'open': close_prices + np.random.randn(100) * 0.3,
        'high': close_prices + np.abs(np.random.randn(100)) * 0.5,
        'low': close_prices - np.abs(np.random.randn(100)) * 0.5,
        'close': close_prices,
        'price': close_prices
    })


class TestSMA:
    """Tests for Simple Moving Average."""
    
    def test_sma_basic(self, sample_price_data):
        """Test basic SMA calculation."""
        df = calculate_sma(sample_price_data, windows=[5, 10])
        
        assert 'sma_5' in df.columns
        assert 'sma_10' in df.columns
        assert len(df) == len(sample_price_data)
    
    def test_sma_values(self, sample_price_data):
        """Test SMA values are correct."""
        df = calculate_sma(sample_price_data, windows=[5])
        
        # 5th value should be mean of first 5 prices
        expected = sample_price_data['price'].iloc[0:5].mean()
        assert abs(df['sma_5'].iloc[4] - expected) < 0.01
        
        # 10th value should be mean of prices 5-10
        expected_10 = sample_price_data['price'].iloc[5:10].mean()
        assert abs(df['sma_5'].iloc[9] - expected_10) < 0.01
    
    def test_sma_invalid_column(self, sample_price_data):
        """Test SMA with invalid column."""
        with pytest.raises(ValueError):
            calculate_sma(sample_price_data, column='invalid_col')
    
    def test_sma_default_windows(self, sample_price_data):
        """Test SMA with default windows."""
        df = calculate_sma(sample_price_data)
        
        assert 'sma_5' in df.columns
        assert 'sma_10' in df.columns
        assert 'sma_20' in df.columns
        assert 'sma_50' in df.columns
        assert 'sma_200' in df.columns


class TestEMA:
    """Tests for Exponential Moving Average."""
    
    def test_ema_basic(self, sample_price_data):
        """Test basic EMA calculation."""
        df = calculate_ema(sample_price_data, windows=[5, 10])
        
        assert 'ema_5' in df.columns
        assert 'ema_10' in df.columns
        assert len(df) == len(sample_price_data)
    
    def test_ema_no_nans(self, sample_price_data):
        """Test EMA has no NaN values (EMA starts from first value)."""
        df = calculate_ema(sample_price_data, windows=[5])
        
        # EMA should not have NaN values (pandas ewm handles this)
        assert not pd.isna(df['ema_5'].iloc[-1])
    
    def test_ema_responds_faster_than_sma(self, sample_price_data):
        """Test that EMA responds faster to price changes than SMA."""
        # Create data with a sudden price spike
        df = sample_price_data.copy()
        df.loc[50:60, 'price'] = df.loc[50, 'price'] + 10
        
        df = calculate_sma(df, windows=[10])
        df = calculate_ema(df, windows=[10])
        
        # EMA should react faster (have larger value) at the spike
        assert df.loc[55, 'ema_10'] > df.loc[55, 'sma_10']


class TestRSI:
    """Tests for Relative Strength Index."""
    
    def test_rsi_basic(self, sample_price_data):
        """Test basic RSI calculation."""
        df = calculate_rsi(sample_price_data, period=14)
        
        assert 'rsi_14' in df.columns
        assert len(df) == len(sample_price_data)
    
    def test_rsi_range(self, sample_price_data):
        """Test RSI values are in 0-100 range."""
        df = calculate_rsi(sample_price_data, period=14)
        
        # Remove NaN values
        rsi_values = df['rsi_14'].dropna()
        
        assert (rsi_values >= 0).all()
        assert (rsi_values <= 100).all()
    
    def test_rsi_trending_up(self):
        """Test RSI on strongly trending up data."""
        df = pd.DataFrame({
            'price': np.arange(100, 200, 1)  # Strongly trending up
        })
        
        df = calculate_rsi(df, period=14)
        
        # RSI should be high (>70) for strongly trending up
        assert df['rsi_14'].iloc[-1] > 70


class TestMACD:
    """Tests for MACD."""
    
    def test_macd_basic(self, sample_price_data):
        """Test basic MACD calculation."""
        df = calculate_macd(sample_price_data, fast_period=12, slow_period=26, signal_period=9)
        
        assert 'macd' in df.columns
        assert 'macd_signal' in df.columns
        assert 'macd_histogram' in df.columns
        assert len(df) == len(sample_price_data)
    
    def test_macd_histogram_calculation(self, sample_price_data):
        """Test MACD histogram is correctly calculated."""
        df = calculate_macd(sample_price_data)
        
        # Remove NaN values
        df_clean = df.dropna()
        
        # Histogram should equal MACD - Signal
        expected_histogram = df_clean['macd'] - df_clean['macd_signal']
        actual_histogram = df_clean['macd_histogram']
        
        assert np.allclose(actual_histogram, expected_histogram, rtol=0.01)


class TestBollingerBands:
    """Tests for Bollinger Bands."""
    
    def test_bollinger_bands_basic(self, sample_price_data):
        """Test basic Bollinger Bands calculation."""
        df = calculate_bollinger_bands(sample_price_data, period=20, num_std=2)
        
        assert 'bb_middle' in df.columns
        assert 'bb_upper' in df.columns
        assert 'bb_lower' in df.columns
        assert 'bb_width' in df.columns
        assert len(df) == len(sample_price_data)
    
    def test_bollinger_bands_ordering(self, sample_price_data):
        """Test that upper > middle > lower."""
        df = calculate_bollinger_bands(sample_price_data, period=20)
        
        # Remove NaN values
        df_clean = df.dropna()
        
        assert (df_clean['bb_upper'] >= df_clean['bb_middle']).all()
        assert (df_clean['bb_middle'] >= df_clean['bb_lower']).all()
    
    def test_bollinger_bands_width(self, sample_price_data):
        """Test BB width calculation."""
        df = calculate_bollinger_bands(sample_price_data, period=20)
        
        # Remove NaN values
        df_clean = df.dropna()
        
        # Width should equal upper - lower
        expected_width = df_clean['bb_upper'] - df_clean['bb_lower']
        actual_width = df_clean['bb_width']
        
        assert np.allclose(actual_width, expected_width, rtol=0.01)


class TestATR:
    """Tests for Average True Range."""
    
    def test_atr_basic(self, sample_ohlc_data):
        """Test basic ATR calculation."""
        df = calculate_atr(sample_ohlc_data, period=14)
        
        assert 'atr_14' in df.columns
        assert len(df) == len(sample_ohlc_data)
    
    def test_atr_positive_values(self, sample_ohlc_data):
        """Test ATR values are positive."""
        df = calculate_atr(sample_ohlc_data, period=14)
        
        # Remove NaN values
        atr_values = df['atr_14'].dropna()
        
        assert (atr_values > 0).all()
    
    def test_atr_missing_columns(self, sample_price_data):
        """Test ATR with missing OHLC columns."""
        with pytest.raises(ValueError, match="high.*low.*close"):
            calculate_atr(sample_price_data, period=14)


class TestAddAllTechnicalIndicators:
    """Tests for add_all_technical_indicators."""
    
    def test_add_all_price_only(self, sample_price_data):
        """Test adding all indicators with price data only."""
        df = add_all_technical_indicators(sample_price_data, has_ohlc=False)
        
        # Should have SMA, EMA, RSI, MACD, BB
        assert 'sma_5' in df.columns
        assert 'ema_10' in df.columns
        assert 'rsi_14' in df.columns
        assert 'macd' in df.columns
        assert 'bb_upper' in df.columns
        
        # Should NOT have ATR (requires OHLC)
        assert 'atr_14' not in df.columns
    
    def test_add_all_with_ohlc(self, sample_ohlc_data):
        """Test adding all indicators with OHLC data."""
        df = add_all_technical_indicators(sample_ohlc_data, has_ohlc=True)
        
        # Should have all indicators including ATR
        assert 'sma_5' in df.columns
        assert 'ema_10' in df.columns
        assert 'rsi_14' in df.columns
        assert 'macd' in df.columns
        assert 'bb_upper' in df.columns
        assert 'atr_14' in df.columns
    
    def test_add_all_feature_count(self, sample_ohlc_data):
        """Test that correct number of features are added."""
        original_cols = len(sample_ohlc_data.columns)
        df = add_all_technical_indicators(sample_ohlc_data, has_ohlc=True)
        
        # Expected features:
        # SMA: 5, EMA: 5, RSI: 1, MACD: 3, BB: 4, ATR: 1 = 19 features
        expected_features = 19
        actual_features = len(df.columns) - original_cols
        
        assert actual_features == expected_features


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_dataframe(self):
        """Test indicators with empty DataFrame."""
        df = pd.DataFrame({'price': []})
        
        # Should not raise error, but return empty DataFrame
        result = calculate_sma(df, windows=[5])
        assert len(result) == 0
    
    def test_insufficient_data(self):
        """Test indicators with insufficient data."""
        df = pd.DataFrame({'price': [100, 101, 102]})
        
        # Should not raise error
        result = calculate_sma(df, windows=[5])
        
        # SMA should still calculate with available data (min_periods=1)
        # First value should be 100, second should be mean of [100, 101]
        assert result['sma_5'].iloc[0] == 100.0
        assert abs(result['sma_5'].iloc[1] - 100.5) < 0.01
    
    def test_nan_values_in_input(self, sample_price_data):
        """Test indicators with NaN values in input."""
        df = sample_price_data.copy()
        df.loc[10:15, 'price'] = np.nan
        
        # Should handle NaN gracefully
        result = calculate_sma(df, windows=[5])
        
        # Should have NaN where input had NaN
        assert pd.isna(result['sma_5'].iloc[10:20]).any()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

