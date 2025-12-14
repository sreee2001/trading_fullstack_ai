"""
Unit tests for Yahoo Finance Client

Tests cover initialization, data fetching, and error handling.
Uses mocking to avoid actual API calls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime

from data_ingestion.yahoo_finance_client import YahooFinanceClient


class TestYahooFinanceClientInitialization:
    """Test cases for YahooFinanceClient initialization."""
    
    def test_init_default(self):
        """Test initialization with default settings."""
        client = YahooFinanceClient()
        assert client.enable_cache is True
        assert isinstance(client._ticker_cache, dict)
    
    def test_init_cache_disabled(self):
        """Test initialization with caching disabled."""
        client = YahooFinanceClient(enable_cache=False)
        assert client.enable_cache is False


class TestYahooFinanceClientConstants:
    """Test cases for class constants."""
    
    def test_tickers_exist(self):
        """Test that common ticker symbols are defined."""
        assert "WTI" in YahooFinanceClient.TICKERS
        assert "BRENT" in YahooFinanceClient.TICKERS
        assert "NATURAL_GAS" in YahooFinanceClient.TICKERS
        assert "GOLD" in YahooFinanceClient.TICKERS
        assert "SILVER" in YahooFinanceClient.TICKERS
        
        assert YahooFinanceClient.TICKERS["WTI"] == "CL=F"
        assert YahooFinanceClient.TICKERS["BRENT"] == "BZ=F"


class TestYahooFinanceClientValidation:
    """Test cases for validation methods."""
    
    def test_validate_date_format_success(self):
        """Test successful date format validation."""
        client = YahooFinanceClient()
        
        result = client._validate_date_format("2024-01-15", "test_date")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
    
    def test_validate_date_format_invalid(self):
        """Test invalid date format raises error."""
        client = YahooFinanceClient()
        
        with pytest.raises(ValueError, match="Invalid.*format"):
            client._validate_date_format("2024/01/15", "test_date")
    
    def test_validate_date_range_success(self):
        """Test successful date range validation."""
        client = YahooFinanceClient()
        
        start_dt, end_dt = client._validate_date_range("2024-01-01", "2024-12-31")
        assert isinstance(start_dt, datetime)
        assert isinstance(end_dt, datetime)
        assert start_dt < end_dt
    
    def test_validate_date_range_invalid(self):
        """Test invalid date range raises error."""
        client = YahooFinanceClient()
        
        with pytest.raises(ValueError, match="must be before or equal to"):
            client._validate_date_range("2024-12-31", "2024-01-01")


class TestYahooFinanceClientFetchOHLCV:
    """Test cases for fetching OHLCV data."""
    
    @patch('data_ingestion.yahoo_finance_client.yf.Ticker')
    def test_fetch_ohlcv_success(self, mock_ticker_class):
        """Test successful OHLCV data fetching."""
        # Create mock data
        mock_data = pd.DataFrame({
            "Open": [80.0, 81.0, 82.0],
            "High": [81.0, 82.0, 83.0],
            "Low": [79.0, 80.0, 81.0],
            "Close": [80.5, 81.5, 82.5],
            "Volume": [100000, 110000, 105000]
        }, index=pd.date_range("2024-01-01", periods=3, freq="D"))
        
        # Setup mock ticker
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker_class.return_value = mock_ticker_instance
        
        # Fetch data
        client = YahooFinanceClient()
        df = client.fetch_ohlcv("CL=F", "2024-01-01", "2024-01-03")
        
        # Assertions
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]
        assert df["close"].iloc[0] == 80.5
        assert df["close"].iloc[1] == 81.5
        assert df["close"].iloc[2] == 82.5
    
    def test_fetch_ohlcv_invalid_date_format(self):
        """Test error handling for invalid date format."""
        client = YahooFinanceClient()
        
        with pytest.raises(ValueError, match="Invalid.*format"):
            client.fetch_ohlcv("CL=F", "2024-13-01", "2024-12-31")
    
    def test_fetch_ohlcv_invalid_date_range(self):
        """Test error handling for invalid date range."""
        client = YahooFinanceClient()
        
        with pytest.raises(ValueError, match="must be before or equal to"):
            client.fetch_ohlcv("CL=F", "2024-12-31", "2024-01-01")
    
    @patch('data_ingestion.yahoo_finance_client.yf.Ticker')
    def test_fetch_ohlcv_empty_response(self, mock_ticker_class):
        """Test handling of empty response."""
        # Setup mock ticker with empty data
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker_class.return_value = mock_ticker_instance
        
        client = YahooFinanceClient()
        df = client.fetch_ohlcv("INVALID", "2024-01-01", "2024-01-03")
        
        # Should return empty DataFrame with correct columns
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]
    
    @patch('data_ingestion.yahoo_finance_client.yf.Ticker')
    def test_fetch_ohlcv_with_nan_values(self, mock_ticker_class):
        """Test handling of NaN values in data."""
        # Create mock data with NaN
        mock_data = pd.DataFrame({
            "Open": [80.0, None, 82.0],
            "High": [81.0, 82.0, 83.0],
            "Low": [79.0, 80.0, 81.0],
            "Close": [80.5, None, 82.5],
            "Volume": [100000, 110000, 105000]
        }, index=pd.date_range("2024-01-01", periods=3, freq="D"))
        
        # Setup mock ticker
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker_class.return_value = mock_ticker_instance
        
        client = YahooFinanceClient()
        df = client.fetch_ohlcv("CL=F", "2024-01-01", "2024-01-03")
        
        # Should drop rows with NaN in price columns
        assert len(df) == 2
        assert df["close"].iloc[0] == 80.5
        assert df["close"].iloc[1] == 82.5
    
    @patch('data_ingestion.yahoo_finance_client.yf.Ticker')
    def test_fetch_ohlcv_sorting(self, mock_ticker_class):
        """Test that results are sorted by date ascending."""
        # Create mock data (unsorted)
        dates = pd.to_datetime(["2024-01-03", "2024-01-01", "2024-01-02"])
        mock_data = pd.DataFrame({
            "Open": [82.0, 80.0, 81.0],
            "High": [83.0, 81.0, 82.0],
            "Low": [81.0, 79.0, 80.0],
            "Close": [82.5, 80.5, 81.5],
            "Volume": [105000, 100000, 110000]
        }, index=dates)
        
        # Setup mock ticker
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker_class.return_value = mock_ticker_instance
        
        client = YahooFinanceClient()
        df = client.fetch_ohlcv("CL=F", "2024-01-01", "2024-01-03")
        
        # Should be sorted by date
        assert df["date"].iloc[0] == pd.Timestamp("2024-01-01")
        assert df["date"].iloc[1] == pd.Timestamp("2024-01-02")
        assert df["date"].iloc[2] == pd.Timestamp("2024-01-03")
    
    @patch('data_ingestion.yahoo_finance_client.yf.Ticker')
    def test_fetch_ohlcv_ticker_caching(self, mock_ticker_class):
        """Test that ticker objects are cached."""
        # Setup mock ticker
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker_class.return_value = mock_ticker_instance
        
        client = YahooFinanceClient()
        
        # Fetch same ticker twice
        client.fetch_ohlcv("CL=F", "2024-01-01", "2024-01-03")
        client.fetch_ohlcv("CL=F", "2024-01-04", "2024-01-06")
        
        # Ticker should only be created once
        assert mock_ticker_class.call_count == 1
        assert "CL=F" in client._ticker_cache
    
    @patch('data_ingestion.yahoo_finance_client.yf.Ticker')
    def test_fetch_ohlcv_different_intervals(self, mock_ticker_class):
        """Test fetching with different intervals."""
        mock_data = pd.DataFrame({
            "Open": [80.0],
            "High": [81.0],
            "Low": [79.0],
            "Close": [80.5],
            "Volume": [100000]
        }, index=pd.date_range("2024-01-01", periods=1, freq="D"))
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker_class.return_value = mock_ticker_instance
        
        client = YahooFinanceClient()
        
        # Fetch with 1-hour interval
        df = client.fetch_ohlcv("CL=F", "2024-01-01", "2024-01-03", interval="1h")
        
        # Verify interval was passed to yfinance
        call_args = mock_ticker_instance.history.call_args
        assert call_args[1]["interval"] == "1h"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

