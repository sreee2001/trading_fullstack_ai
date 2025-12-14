"""
Tests for EIA API Client

Tests cover:
- Client initialization
- API key validation
- Request building
- Error handling
- Retry logic
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import pandas as pd
from datetime import datetime

from data_ingestion.eia_client import EIAAPIClient


class TestEIAAPIClientInitialization:
    """Test cases for EIA API Client initialization."""
    
    def test_init_with_api_key(self):
        """Test initialization with API key provided as argument."""
        client = EIAAPIClient(api_key="test_api_key")
        assert client.api_key == "test_api_key"
        assert client.session is not None
    
    def test_init_with_env_variable(self, monkeypatch):
        """Test initialization with API key from environment variable."""
        monkeypatch.setenv("EIA_API_KEY", "env_api_key")
        client = EIAAPIClient()
        assert client.api_key == "env_api_key"
    
    def test_init_without_api_key(self, monkeypatch):
        """Test initialization fails without API key."""
        monkeypatch.delenv("EIA_API_KEY", raising=False)
        with pytest.raises(ValueError, match="EIA API key is required"):
            EIAAPIClient()
    
    def test_session_headers(self):
        """Test that session has correct headers."""
        client = EIAAPIClient(api_key="test_key")
        assert "User-Agent" in client.session.headers
        assert "EnergyPriceForecastingSystem" in client.session.headers["User-Agent"]


class TestEIAAPIClientURLBuilding:
    """Test cases for URL building."""
    
    def test_build_url(self):
        """Test URL construction."""
        client = EIAAPIClient(api_key="test_key")
        url = client._build_url("petroleum/pri/spt/data")
        assert url == "https://api.eia.gov/v2/petroleum/pri/spt/data"
        assert url.startswith(client.BASE_URL)


class TestEIAAPIClientRequests:
    """Test cases for making API requests."""
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful API request."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test_data"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Make request
        client = EIAAPIClient(api_key="test_key")
        result = client._make_request("test/endpoint", {"param": "value"})
        
        # Assertions
        assert result == {"data": "test_data"}
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "api_key" in call_args[1]["params"]
        assert call_args[1]["params"]["api_key"] == "test_key"
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_make_request_http_error(self, mock_get):
        """Test request handling HTTP errors."""
        # Setup mock to raise HTTPError
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response
        
        # Make request
        client = EIAAPIClient(api_key="test_key")
        with pytest.raises(requests.exceptions.HTTPError):
            client._make_request("test/endpoint")


class TestEIAAPIClientRetry:
    """Test cases for retry logic."""
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_retry_on_rate_limit(self, mock_get):
        """Test retry on 429 rate limit error."""
        # Setup mock to fail twice then succeed
        mock_response_fail = Mock()
        mock_response_fail.status_code = 429
        mock_response_fail.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response_fail)
        
        mock_response_success = Mock()
        mock_response_success.json.return_value = {"data": "success"}
        mock_response_success.raise_for_status = Mock()
        
        mock_get.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]
        
        # Make request with retry
        client = EIAAPIClient(api_key="test_key")
        result = client._make_request_with_retry("test/endpoint")
        
        # Should succeed after retries
        assert result == {"data": "success"}
        assert mock_get.call_count == 3
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_retry_on_server_error(self, mock_get):
        """Test retry on 500 server error."""
        # Setup mock
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response_fail)
        
        mock_response_success = Mock()
        mock_response_success.json.return_value = {"data": "success"}
        mock_response_success.raise_for_status = Mock()
        
        mock_get.side_effect = [mock_response_fail, mock_response_success]
        
        # Make request
        client = EIAAPIClient(api_key="test_key")
        result = client._make_request_with_retry("test/endpoint")
        
        assert result == {"data": "success"}
        assert mock_get.call_count == 2


class TestEIAAPIClientContextManager:
    """Test cases for context manager functionality."""
    
    def test_context_manager(self):
        """Test client works as context manager."""
        with EIAAPIClient(api_key="test_key") as client:
            assert client.api_key == "test_key"
            assert client.session is not None
    
    @patch('data_ingestion.eia_client.requests.Session.close')
    def test_context_manager_closes_session(self, mock_close):
        """Test that context manager closes session on exit."""
        with EIAAPIClient(api_key="test_key") as client:
            pass
        # Should be called at least once (may be called multiple times by __del__ as well)
        assert mock_close.called


class TestEIAAPIClientConstants:
    """Test cases for class constants."""
    
    def test_base_url(self):
        """Test BASE_URL is correctly defined."""
        assert EIAAPIClient.BASE_URL == "https://api.eia.gov/v2"
    
    def test_series_ids_exist(self):
        """Test SERIES_IDS dictionary contains expected commodities."""
        assert "WTI" in EIAAPIClient.SERIES_IDS
        assert "NATURAL_GAS" in EIAAPIClient.SERIES_IDS
        assert isinstance(EIAAPIClient.SERIES_IDS["WTI"], str)


class TestEIAAPIClientFetchWTIPrices:
    """Test cases for fetching WTI crude oil prices."""
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_wti_prices_success(self, mock_get):
        """Test successful WTI price fetching."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": [
                    {"period": "2024-01-01", "value": "75.50"},
                    {"period": "2024-01-02", "value": "76.25"},
                    {"period": "2024-01-03", "value": "75.80"}
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Fetch data
        client = EIAAPIClient(api_key="test_key")
        df = client.fetch_wti_prices("2024-01-01", "2024-01-03")
        
        # Assertions
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["date", "price"]
        assert df["price"].iloc[0] == 75.50
        assert df["price"].iloc[1] == 76.25
        assert df["price"].iloc[2] == 75.80
        
        # Check dates are datetime
        assert isinstance(df["date"].iloc[0], pd.Timestamp)
    
    def test_fetch_wti_prices_invalid_date_format(self):
        """Test error handling for invalid date format."""
        client = EIAAPIClient(api_key="test_key")
        
        with pytest.raises(ValueError, match="Invalid.*format"):
            client.fetch_wti_prices("2024-13-01", "2024-12-31")  # Invalid month
        
        with pytest.raises(ValueError, match="Invalid.*format"):
            client.fetch_wti_prices("01/01/2024", "12/31/2024")  # Wrong format
    
    def test_fetch_wti_prices_invalid_date_range(self):
        """Test error handling for invalid date range."""
        client = EIAAPIClient(api_key="test_key")
        
        with pytest.raises(ValueError, match="Start date.*must be before or equal to end date"):
            client.fetch_wti_prices("2024-12-31", "2024-01-01")  # End before start
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_wti_prices_empty_response(self, mock_get):
        """Test handling of empty API response."""
        # Setup mock with empty data
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": []
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = EIAAPIClient(api_key="test_key")
        df = client.fetch_wti_prices("2024-01-01", "2024-01-03")
        
        # Should return empty DataFrame with correct columns
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["date", "price"]
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_wti_prices_invalid_response_structure(self, mock_get):
        """Test handling of unexpected API response structure."""
        # Setup mock with invalid structure
        mock_response = Mock()
        mock_response.json.return_value = {
            "unexpected": "structure"
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = EIAAPIClient(api_key="test_key")
        df = client.fetch_wti_prices("2024-01-01", "2024-01-03")
        
        # Should return empty DataFrame
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["date", "price"]
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_wti_prices_with_nan_values(self, mock_get):
        """Test handling of NaN values in price data."""
        # Setup mock with some invalid prices
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": [
                    {"period": "2024-01-01", "value": "75.50"},
                    {"period": "2024-01-02", "value": "N/A"},  # Invalid
                    {"period": "2024-01-03", "value": "76.25"}
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = EIAAPIClient(api_key="test_key")
        df = client.fetch_wti_prices("2024-01-01", "2024-01-03")
        
        # Should drop rows with NaN prices
        assert len(df) == 2
        assert df["price"].iloc[0] == 75.50
        assert df["price"].iloc[1] == 76.25
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_wti_prices_sorting(self, mock_get):
        """Test that results are sorted by date ascending."""
        # Setup mock with unsorted data
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": [
                    {"period": "2024-01-03", "value": "75.80"},
                    {"period": "2024-01-01", "value": "75.50"},
                    {"period": "2024-01-02", "value": "76.25"}
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = EIAAPIClient(api_key="test_key")
        df = client.fetch_wti_prices("2024-01-01", "2024-01-03")
        
        # Should be sorted by date
        assert df["date"].iloc[0] == pd.Timestamp("2024-01-01")
        assert df["date"].iloc[1] == pd.Timestamp("2024-01-02")
        assert df["date"].iloc[2] == pd.Timestamp("2024-01-03")
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_wti_prices_http_error(self, mock_get):
        """Test handling of HTTP errors during fetch."""
        # Setup mock to raise HTTPError
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response
        
        client = EIAAPIClient(api_key="test_key")
        
        with pytest.raises(requests.exceptions.HTTPError):
            client.fetch_wti_prices("2024-01-01", "2024-01-03")
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_wti_prices_api_parameters(self, mock_get):
        """Test that correct parameters are sent to API."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {"data": []}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = EIAAPIClient(api_key="test_key")
        client.fetch_wti_prices("2024-01-01", "2024-01-31")
        
        # Verify API call was made
        assert mock_get.called
        call_args = mock_get.call_args
        
        # Check parameters include date range
        params = call_args[1]["params"]
        assert params["start"] == "2024-01-01"
        assert params["end"] == "2024-01-31"
        assert params["api_key"] == "test_key"


class TestEIAAPIClientFetchNaturalGasPrices:
    """Test cases for fetching Henry Hub Natural Gas prices."""
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_natural_gas_prices_success(self, mock_get):
        """Test successful natural gas price fetching."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": [
                    {"period": "2024-01-01", "value": "3.15"},
                    {"period": "2024-01-02", "value": "3.20"},
                    {"period": "2024-01-03", "value": "3.18"}
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Fetch data
        client = EIAAPIClient(api_key="test_key")
        df = client.fetch_natural_gas_prices("2024-01-01", "2024-01-03")
        
        # Assertions
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["date", "price"]
        assert df["price"].iloc[0] == 3.15
        assert df["price"].iloc[1] == 3.20
        assert df["price"].iloc[2] == 3.18
        
        # Check dates are datetime
        assert isinstance(df["date"].iloc[0], pd.Timestamp)
    
    def test_fetch_natural_gas_prices_invalid_date_format(self):
        """Test error handling for invalid date format."""
        client = EIAAPIClient(api_key="test_key")
        
        with pytest.raises(ValueError, match="Invalid.*format"):
            client.fetch_natural_gas_prices("2024-13-01", "2024-12-31")  # Invalid month
        
        with pytest.raises(ValueError, match="Invalid.*format"):
            client.fetch_natural_gas_prices("01/01/2024", "12/31/2024")  # Wrong format
    
    def test_fetch_natural_gas_prices_invalid_date_range(self):
        """Test error handling for invalid date range."""
        client = EIAAPIClient(api_key="test_key")
        
        with pytest.raises(ValueError, match="Start date.*must be before or equal to end date"):
            client.fetch_natural_gas_prices("2024-12-31", "2024-01-01")  # End before start
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_natural_gas_prices_empty_response(self, mock_get):
        """Test handling of empty API response."""
        # Setup mock with empty data
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": []
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = EIAAPIClient(api_key="test_key")
        df = client.fetch_natural_gas_prices("2024-01-01", "2024-01-03")
        
        # Should return empty DataFrame with correct columns
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["date", "price"]
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_natural_gas_prices_invalid_response_structure(self, mock_get):
        """Test handling of unexpected API response structure."""
        # Setup mock with invalid structure
        mock_response = Mock()
        mock_response.json.return_value = {
            "unexpected": "structure"
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = EIAAPIClient(api_key="test_key")
        df = client.fetch_natural_gas_prices("2024-01-01", "2024-01-03")
        
        # Should return empty DataFrame
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["date", "price"]
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_natural_gas_prices_with_nan_values(self, mock_get):
        """Test handling of NaN values in price data."""
        # Setup mock with some invalid prices
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": [
                    {"period": "2024-01-01", "value": "3.15"},
                    {"period": "2024-01-02", "value": "N/A"},  # Invalid
                    {"period": "2024-01-03", "value": "3.20"}
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = EIAAPIClient(api_key="test_key")
        df = client.fetch_natural_gas_prices("2024-01-01", "2024-01-03")
        
        # Should drop rows with NaN prices
        assert len(df) == 2
        assert df["price"].iloc[0] == 3.15
        assert df["price"].iloc[1] == 3.20
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_natural_gas_prices_sorting(self, mock_get):
        """Test that results are sorted by date ascending."""
        # Setup mock with unsorted data
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": [
                    {"period": "2024-01-03", "value": "3.18"},
                    {"period": "2024-01-01", "value": "3.15"},
                    {"period": "2024-01-02", "value": "3.20"}
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = EIAAPIClient(api_key="test_key")
        df = client.fetch_natural_gas_prices("2024-01-01", "2024-01-03")
        
        # Should be sorted by date
        assert df["date"].iloc[0] == pd.Timestamp("2024-01-01")
        assert df["date"].iloc[1] == pd.Timestamp("2024-01-02")
        assert df["date"].iloc[2] == pd.Timestamp("2024-01-03")
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_natural_gas_prices_http_error(self, mock_get):
        """Test handling of HTTP errors during fetch."""
        # Setup mock to raise HTTPError
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response
        
        client = EIAAPIClient(api_key="test_key")
        
        with pytest.raises(requests.exceptions.HTTPError):
            client.fetch_natural_gas_prices("2024-01-01", "2024-01-03")
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_fetch_natural_gas_prices_api_parameters(self, mock_get):
        """Test that correct parameters are sent to API."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {"data": []}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = EIAAPIClient(api_key="test_key")
        client.fetch_natural_gas_prices("2024-01-01", "2024-01-31")
        
        # Verify API call was made
        assert mock_get.called
        call_args = mock_get.call_args
        
        # Check parameters include date range
        params = call_args[1]["params"]
        assert params["start"] == "2024-01-01"
        assert params["end"] == "2024-01-31"
        assert params["api_key"] == "test_key"


class TestEIAAPIClientValidation:
    """Test cases for validation helper methods."""
    
    def test_validate_date_format_success(self):
        """Test successful date format validation."""
        client = EIAAPIClient(api_key="test_key")
        
        result = client._validate_date_format("2024-01-15", "test_date")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
    
    def test_validate_date_format_invalid(self):
        """Test invalid date format raises error."""
        client = EIAAPIClient(api_key="test_key")
        
        with pytest.raises(ValueError, match="Invalid test_date format"):
            client._validate_date_format("2024/01/15", "test_date")
    
    def test_validate_date_range_success(self):
        """Test successful date range validation."""
        client = EIAAPIClient(api_key="test_key")
        
        start_dt, end_dt = client._validate_date_range("2024-01-01", "2024-12-31")
        assert isinstance(start_dt, datetime)
        assert isinstance(end_dt, datetime)
        assert start_dt < end_dt
    
    def test_validate_date_range_invalid(self):
        """Test invalid date range raises error."""
        client = EIAAPIClient(api_key="test_key")
        
        with pytest.raises(ValueError, match="must be before or equal to"):
            client._validate_date_range("2024-12-31", "2024-01-01")


class TestEIAAPIClientNormalization:
    """Test cases for response normalization."""
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_normalize_response_success(self, mock_get):
        """Test successful response normalization."""
        client = EIAAPIClient(api_key="test_key")
        
        raw_data = {
            "response": {
                "data": [
                    {"period": "2024-01-01", "value": "75.50"},
                    {"period": "2024-01-02", "value": "76.25"}
                ]
            }
        }
        
        df = client._normalize_response(raw_data, "test_commodity")
        
        assert len(df) == 2
        assert list(df.columns) == ["date", "price"]
        assert df["price"].iloc[0] == 75.50
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_normalize_response_empty(self, mock_get):
        """Test normalization of empty response."""
        client = EIAAPIClient(api_key="test_key")
        
        raw_data = {"response": {"data": []}}
        df = client._normalize_response(raw_data, "test_commodity")
        
        assert len(df) == 0
        assert list(df.columns) == ["date", "price"]
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_normalize_response_invalid_structure(self, mock_get):
        """Test normalization handles invalid structure."""
        client = EIAAPIClient(api_key="test_key")
        
        raw_data = {"invalid": "structure"}
        df = client._normalize_response(raw_data, "test_commodity")
        
        assert len(df) == 0
        assert list(df.columns) == ["date", "price"]
    
    @patch('data_ingestion.eia_client.requests.Session.get')
    def test_validate_and_convert_types_with_nan(self, mock_get):
        """Test type conversion handles NaN values."""
        client = EIAAPIClient(api_key="test_key")
        
        df = pd.DataFrame({
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "price": ["75.50", "invalid", "76.25"]
        })
        
        result = client._validate_and_convert_types(df, "test_commodity")
        
        # Should drop the invalid row
        assert len(result) == 2
        assert result["price"].iloc[0] == 75.50
        assert result["price"].iloc[1] == 76.25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

