"""
Unit tests for FRED API Client

Tests cover initialization, HTTP requests, retry logic, and context manager.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import pandas as pd
from datetime import datetime

from data_ingestion.fred_client import FREDAPIClient


class TestFREDAPIClientInitialization:
    """Test cases for FREDAPIClient initialization."""
    
    def test_init_with_api_key(self):
        """Test initialization with API key provided."""
        client = FREDAPIClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.session is not None
    
    @patch.dict(os.environ, {"FRED_API_KEY": "env_test_key"})
    def test_init_with_env_variable(self):
        """Test initialization with API key from environment."""
        client = FREDAPIClient()
        assert client.api_key == "env_test_key"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key(self):
        """Test that initialization fails without API key."""
        with pytest.raises(ValueError, match="FRED API key is required"):
            FREDAPIClient()
    
    def test_session_headers(self):
        """Test that session has correct headers."""
        client = FREDAPIClient(api_key="test_key")
        assert "User-Agent" in client.session.headers
        assert "EnergyPriceForecastingSystem" in client.session.headers["User-Agent"]


class TestFREDAPIClientURLBuilding:
    """Test cases for URL building."""
    
    def test_build_url(self):
        """Test URL building."""
        client = FREDAPIClient(api_key="test_key")
        url = client._build_url("series/observations")
        assert url == "https://api.stlouisfed.org/fred/series/observations"


class TestFREDAPIClientRequests:
    """Test cases for HTTP requests."""
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful API request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"observations": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = FREDAPIClient(api_key="test_key")
        result = client._make_request("series/observations")
        
        assert result == {"observations": []}
        mock_get.assert_called_once()
        
        # Verify that API key and file_type are in params
        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["api_key"] == "test_key"
        assert params["file_type"] == "json"
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_make_request_http_error(self, mock_get):
        """Test HTTP error handling."""
        # Setup mock to raise HTTPError
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response
        
        client = FREDAPIClient(api_key="test_key")
        
        with pytest.raises(requests.exceptions.HTTPError):
            client._make_request("invalid/endpoint")


class TestFREDAPIClientRetry:
    """Test cases for retry logic."""
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_retry_on_rate_limit(self, mock_get):
        """Test retry on rate limit (429) error."""
        # Setup mock to return 429 then success
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response_429
        )
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"observations": []}
        mock_response_success.raise_for_status = Mock()
        
        mock_get.side_effect = [mock_response_429, mock_response_success]
        
        client = FREDAPIClient(api_key="test_key")
        result = client._make_request_with_retry("series/observations")
        
        assert result == {"observations": []}
        assert mock_get.call_count == 2  # First failed, second succeeded
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_retry_on_server_error(self, mock_get):
        """Test retry on server error (500+)."""
        # Setup mock to return 503 then success
        mock_response_503 = Mock()
        mock_response_503.status_code = 503
        mock_response_503.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response_503
        )
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"observations": []}
        mock_response_success.raise_for_status = Mock()
        
        mock_get.side_effect = [mock_response_503, mock_response_success]
        
        client = FREDAPIClient(api_key="test_key")
        result = client._make_request_with_retry("series/observations")
        
        assert result == {"observations": []}
        assert mock_get.call_count == 2


class TestFREDAPIClientContextManager:
    """Test cases for context manager functionality."""
    
    def test_context_manager(self):
        """Test client works as context manager."""
        with FREDAPIClient(api_key="test_key") as client:
            assert client.api_key == "test_key"
            assert client.session is not None
    
    @patch('data_ingestion.fred_client.requests.Session.close')
    def test_context_manager_closes_session(self, mock_close):
        """Test that context manager closes session on exit."""
        with FREDAPIClient(api_key="test_key") as client:
            pass
        # Should be called at least once
        assert mock_close.called


class TestFREDAPIClientConstants:
    """Test cases for class constants."""
    
    def test_base_url(self):
        """Test that BASE_URL is correct."""
        assert FREDAPIClient.BASE_URL == "https://api.stlouisfed.org/fred"
    
    def test_series_ids_exist(self):
        """Test that common series IDs are defined."""
        assert "WTI" in FREDAPIClient.SERIES_IDS
        assert "BRENT" in FREDAPIClient.SERIES_IDS
        assert "NATURAL_GAS" in FREDAPIClient.SERIES_IDS
        assert isinstance(FREDAPIClient.SERIES_IDS["WTI"], str)


class TestFREDAPIClientFetchSeries:
    """Test cases for fetching FRED series data."""
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_fetch_series_success(self, mock_get):
        """Test successful series data fetching."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "observations": [
                {"date": "2024-01-01", "value": "80.26"},
                {"date": "2024-01-02", "value": "80.50"},
                {"date": "2024-01-03", "value": "79.80"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Fetch data
        client = FREDAPIClient(api_key="test_key")
        df = client.fetch_series("DCOILWTICO", "2024-01-01", "2024-01-03")
        
        # Assertions
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["date", "value"]
        assert df["value"].iloc[0] == 80.26
        assert df["value"].iloc[1] == 80.50
        assert df["value"].iloc[2] == 79.80
        
        # Check dates are datetime
        assert isinstance(df["date"].iloc[0], pd.Timestamp)
    
    def test_fetch_series_invalid_date_format(self):
        """Test error handling for invalid date format."""
        client = FREDAPIClient(api_key="test_key")
        
        with pytest.raises(ValueError, match="Invalid.*format"):
            client.fetch_series("DCOILWTICO", "2024-13-01", "2024-12-31")
    
    def test_fetch_series_invalid_date_range(self):
        """Test error handling for invalid date range."""
        client = FREDAPIClient(api_key="test_key")
        
        with pytest.raises(ValueError, match="must be before or equal to"):
            client.fetch_series("DCOILWTICO", "2024-12-31", "2024-01-01")
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_fetch_series_empty_response(self, mock_get):
        """Test handling of empty API response."""
        # Setup mock with empty observations
        mock_response = Mock()
        mock_response.json.return_value = {
            "observations": []
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = FREDAPIClient(api_key="test_key")
        df = client.fetch_series("INVALID_SERIES", "2024-01-01", "2024-01-03")
        
        # Should return empty DataFrame with correct columns
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["date", "value"]
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_fetch_series_with_missing_values(self, mock_get):
        """Test handling of missing values (represented as '.' in FRED)."""
        # Setup mock with some missing values
        mock_response = Mock()
        mock_response.json.return_value = {
            "observations": [
                {"date": "2024-01-01", "value": "80.26"},
                {"date": "2024-01-02", "value": "."},  # Missing value
                {"date": "2024-01-03", "value": "79.80"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = FREDAPIClient(api_key="test_key")
        df = client.fetch_series("DCOILWTICO", "2024-01-01", "2024-01-03")
        
        # Should drop rows with missing values
        assert len(df) == 2
        assert df["value"].iloc[0] == 80.26
        assert df["value"].iloc[1] == 79.80
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_fetch_series_sorting(self, mock_get):
        """Test that results are sorted by date ascending."""
        # Setup mock with unsorted data
        mock_response = Mock()
        mock_response.json.return_value = {
            "observations": [
                {"date": "2024-01-03", "value": "79.80"},
                {"date": "2024-01-01", "value": "80.26"},
                {"date": "2024-01-02", "value": "80.50"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = FREDAPIClient(api_key="test_key")
        df = client.fetch_series("DCOILWTICO", "2024-01-01", "2024-01-03")
        
        # Should be sorted by date
        assert df["date"].iloc[0] == pd.Timestamp("2024-01-01")
        assert df["date"].iloc[1] == pd.Timestamp("2024-01-02")
        assert df["date"].iloc[2] == pd.Timestamp("2024-01-03")
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_fetch_series_http_error(self, mock_get):
        """Test handling of HTTP errors during fetch."""
        # Setup mock to raise HTTPError
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response
        
        client = FREDAPIClient(api_key="test_key")
        
        with pytest.raises(requests.exceptions.HTTPError):
            client.fetch_series("INVALID_SERIES", "2024-01-01", "2024-01-03")
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_fetch_series_api_parameters(self, mock_get):
        """Test that correct parameters are sent to API."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {
            "observations": []
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = FREDAPIClient(api_key="test_key")
        client.fetch_series("DCOILWTICO", "2024-01-01", "2024-01-31")
        
        # Verify API call was made
        assert mock_get.called
        call_args = mock_get.call_args
        
        # Check parameters include series_id and date range
        params = call_args[1]["params"]
        assert params["series_id"] == "DCOILWTICO"
        assert params["observation_start"] == "2024-01-01"
        assert params["observation_end"] == "2024-01-31"
        assert params["api_key"] == "test_key"


class TestFREDAPIClientCaching:
    """Test cases for caching functionality."""
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_cache_hit(self, mock_get):
        """Test that second request hits cache."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "observations": [
                {"date": "2024-01-01", "value": "80.26"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = FREDAPIClient(api_key="test_key", enable_cache=True)
        
        # First call - should hit API
        df1 = client.fetch_series("DCOILWTICO", "2024-01-01", "2024-01-03")
        assert len(df1) == 1
        assert mock_get.call_count == 1
        
        # Second call - should hit cache
        df2 = client.fetch_series("DCOILWTICO", "2024-01-01", "2024-01-03")
        assert len(df2) == 1
        assert mock_get.call_count == 1  # No additional API call
        
        # Check cache stats
        stats = client.get_cache_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["total_requests"] == 2
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_cache_disabled(self, mock_get):
        """Test that caching can be disabled."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "observations": [
                {"date": "2024-01-01", "value": "80.26"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = FREDAPIClient(api_key="test_key", enable_cache=False)
        
        # Two calls - both should hit API
        df1 = client.fetch_series("DCOILWTICO", "2024-01-01", "2024-01-03")
        df2 = client.fetch_series("DCOILWTICO", "2024-01-01", "2024-01-03")
        
        assert mock_get.call_count == 2  # Two API calls
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_cache_different_queries(self, mock_get):
        """Test that different queries don't hit same cache."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "observations": [
                {"date": "2024-01-01", "value": "80.26"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = FREDAPIClient(api_key="test_key", enable_cache=True)
        
        # Different queries
        df1 = client.fetch_series("DCOILWTICO", "2024-01-01", "2024-01-03")
        df2 = client.fetch_series("DCOILBRENTEU", "2024-01-01", "2024-01-03")
        df3 = client.fetch_series("DCOILWTICO", "2024-01-04", "2024-01-06")
        
        assert mock_get.call_count == 3  # Three different queries, three API calls
    
    @patch('data_ingestion.fred_client.requests.Session.get')
    def test_clear_cache(self, mock_get):
        """Test cache clearing."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "observations": [
                {"date": "2024-01-01", "value": "80.26"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = FREDAPIClient(api_key="test_key", enable_cache=True)
        
        # First call
        df1 = client.fetch_series("DCOILWTICO", "2024-01-01", "2024-01-03")
        assert mock_get.call_count == 1
        
        # Clear cache
        client.clear_cache()
        
        # Second call - should hit API again
        df2 = client.fetch_series("DCOILWTICO", "2024-01-01", "2024-01-03")
        assert mock_get.call_count == 2
    
    def test_cache_stats(self):
        """Test cache statistics."""
        client = FREDAPIClient(api_key="test_key", enable_cache=True, cache_ttl_minutes=10)
        
        stats = client.get_cache_stats()
        
        assert stats["enabled"] is True
        assert stats["ttl_minutes"] == 10
        assert stats["cache_size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

