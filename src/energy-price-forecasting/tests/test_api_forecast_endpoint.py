"""
Unit tests for forecast endpoint (Story 4.2.2).
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status
import pandas as pd

from api.main import app
from api.models.forecast import ForecastRequest, ForecastResponse


class TestForecastEndpoint:
    """Test forecast endpoint."""
    
    def test_forecast_endpoint_exists(self):
        """Test that forecast endpoint is registered."""
        client = TestClient(app)
        
        # Check that endpoint exists (should return 422 for missing body)
        response = client.post("/api/v1/forecast")
        assert response.status_code in [422, 400]  # Validation error expected
    
    def test_forecast_endpoint_valid_request(self):
        """Test forecast endpoint with valid request."""
        client = TestClient(app)
        
        request_data = {
            "commodity": "WTI",
            "horizon": 7,
            "start_date": "2025-01-01"
        }
        
        response = client.post("/api/v1/forecast", json=request_data)
        
        # Should succeed (200) with placeholder model
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["commodity"] == "WTI"
        assert data["horizon"] == 7
        assert len(data["predictions"]) == 7
        assert "forecast_date" in data
        assert "model_name" in data
    
    def test_forecast_endpoint_invalid_commodity(self):
        """Test forecast endpoint with invalid commodity."""
        client = TestClient(app)
        
        request_data = {
            "commodity": "INVALID",
            "horizon": 7,
            "start_date": "2025-01-01"
        }
        
        response = client.post("/api/v1/forecast", json=request_data)
        
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_forecast_endpoint_invalid_horizon(self):
        """Test forecast endpoint with invalid horizon."""
        client = TestClient(app)
        
        request_data = {
            "commodity": "WTI",
            "horizon": 0,  # Invalid: must be >= 1
            "start_date": "2025-01-01"
        }
        
        response = client.post("/api/v1/forecast", json=request_data)
        
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_forecast_endpoint_invalid_date_format(self):
        """Test forecast endpoint with invalid date format."""
        client = TestClient(app)
        
        request_data = {
            "commodity": "WTI",
            "horizon": 7,
            "start_date": "01-01-2025"  # Wrong format
        }
        
        response = client.post("/api/v1/forecast", json=request_data)
        
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_forecast_endpoint_different_commodities(self):
        """Test forecast endpoint with different commodities."""
        client = TestClient(app)
        
        for commodity in ["WTI", "BRENT", "NG"]:
            request_data = {
                "commodity": commodity,
                "horizon": 1,
                "start_date": "2025-01-01"
            }
            
            response = client.post("/api/v1/forecast", json=request_data)
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["commodity"] == commodity
    
    def test_forecast_endpoint_different_horizons(self):
        """Test forecast endpoint with different horizons."""
        client = TestClient(app)
        
        for horizon in [1, 7, 30]:
            request_data = {
                "commodity": "WTI",
                "horizon": horizon,
                "start_date": "2025-01-01"
            }
            
            response = client.post("/api/v1/forecast", json=request_data)
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert len(data["predictions"]) == horizon
    
    def test_forecast_response_structure(self):
        """Test that forecast response has correct structure."""
        client = TestClient(app)
        
        request_data = {
            "commodity": "WTI",
            "horizon": 3,
            "start_date": "2025-01-01"
        }
        
        response = client.post("/api/v1/forecast", json=request_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        
        # Check required fields
        assert "commodity" in data
        assert "forecast_date" in data
        assert "horizon" in data
        assert "predictions" in data
        
        # Check predictions structure
        assert isinstance(data["predictions"], list)
        assert len(data["predictions"]) == 3
        
        for pred in data["predictions"]:
            assert "date" in pred
            assert "price" in pred
            assert "confidence_lower" in pred
            assert "confidence_upper" in pred
            assert isinstance(pred["price"], (int, float))
            assert pred["price"] >= 0
            assert pred["confidence_lower"] >= 0
            assert pred["confidence_upper"] >= pred["confidence_lower"]
    
    def test_forecast_predictions_have_correct_dates(self):
        """Test that predictions have correct dates."""
        client = TestClient(app)
        
        request_data = {
            "commodity": "WTI",
            "horizon": 5,
            "start_date": "2025-01-01"
        }
        
        response = client.post("/api/v1/forecast", json=request_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        predictions = data["predictions"]
        
        # Check dates are sequential
        expected_dates = [
            "2025-01-01",
            "2025-01-02",
            "2025-01-03",
            "2025-01-04",
            "2025-01-05"
        ]
        
        for i, pred in enumerate(predictions):
            assert pred["date"] == expected_dates[i]

