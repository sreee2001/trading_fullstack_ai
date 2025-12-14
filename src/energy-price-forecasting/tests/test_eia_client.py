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
        mock_close.assert_called_once()


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

