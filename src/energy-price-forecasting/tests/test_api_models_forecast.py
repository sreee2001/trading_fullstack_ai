"""
Unit tests for forecast API models (Story 4.2.1).
"""

import pytest
from datetime import date, datetime
from pydantic import ValidationError

from api.models.forecast import (
    ForecastRequest,
    ForecastResponse,
    Prediction,
)


class TestForecastRequest:
    """Test ForecastRequest model."""
    
    def test_valid_request(self):
        """Test creating a valid forecast request."""
        request = ForecastRequest(
            commodity="WTI",
            horizon=7,
            start_date="2025-01-01"
        )
        
        assert request.commodity == "WTI"
        assert request.horizon == 7
        assert request.start_date == "2025-01-01"
    
    def test_commodity_case_insensitive(self):
        """Test that commodity is converted to uppercase."""
        request = ForecastRequest(
            commodity="wti",
            horizon=7,
            start_date="2025-01-01"
        )
        
        assert request.commodity == "WTI"
    
    def test_invalid_commodity(self):
        """Test that invalid commodity raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ForecastRequest(
                commodity="INVALID",
                horizon=7,
                start_date="2025-01-01"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("commodity",) for error in errors)
    
    def test_horizon_validation(self):
        """Test horizon validation (1-30)."""
        # Valid horizons
        for horizon in [1, 7, 30]:
            request = ForecastRequest(
                commodity="WTI",
                horizon=horizon,
                start_date="2025-01-01"
            )
            assert request.horizon == horizon
        
        # Invalid horizons
        with pytest.raises(ValidationError):
            ForecastRequest(
                commodity="WTI",
                horizon=0,
                start_date="2025-01-01"
            )
        
        with pytest.raises(ValidationError):
            ForecastRequest(
                commodity="WTI",
                horizon=31,
                start_date="2025-01-01"
            )
    
    def test_invalid_date_format(self):
        """Test that invalid date format raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ForecastRequest(
                commodity="WTI",
                horizon=7,
                start_date="01-01-2025"  # Wrong format
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("start_date",) for error in errors)
    
    def test_get_start_date_as_date(self):
        """Test converting start_date to date object."""
        request = ForecastRequest(
            commodity="WTI",
            horizon=7,
            start_date="2025-01-01"
        )
        
        result = request.get_start_date_as_date()
        assert isinstance(result, date)
        assert result == date(2025, 1, 1)


class TestPrediction:
    """Test Prediction model."""
    
    def test_valid_prediction(self):
        """Test creating a valid prediction."""
        prediction = Prediction(
            date="2025-01-01",
            price=75.50,
            confidence_lower=70.00,
            confidence_upper=80.00
        )
        
        assert prediction.date == "2025-01-01"
        assert prediction.price == 75.50
        assert prediction.confidence_lower == 70.00
        assert prediction.confidence_upper == 80.00
    
    def test_invalid_date_format(self):
        """Test that invalid date format raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Prediction(
                date="01-01-2025",
                price=75.50,
                confidence_lower=70.00,
                confidence_upper=80.00
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("date",) for error in errors)
    
    def test_negative_price(self):
        """Test that negative price raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Prediction(
                date="2025-01-01",
                price=-10.0,
                confidence_lower=70.00,
                confidence_upper=80.00
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("price",) for error in errors)
    
    def test_confidence_interval_validation(self):
        """Test that confidence_upper >= confidence_lower."""
        # Valid interval
        prediction = Prediction(
            date="2025-01-01",
            price=75.50,
            confidence_lower=70.00,
            confidence_upper=80.00
        )
        assert prediction.confidence_upper >= prediction.confidence_lower
        
        # Invalid interval
        with pytest.raises(ValidationError) as exc_info:
            Prediction(
                date="2025-01-01",
                price=75.50,
                confidence_lower=80.00,
                confidence_upper=70.00  # Lower than lower bound
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("confidence_upper",) for error in errors)


class TestForecastResponse:
    """Test ForecastResponse model."""
    
    def test_valid_response(self):
        """Test creating a valid forecast response."""
        predictions = [
            Prediction(
                date="2025-01-01",
                price=75.50,
                confidence_lower=70.00,
                confidence_upper=80.00
            ),
            Prediction(
                date="2025-01-02",
                price=76.00,
                confidence_lower=71.00,
                confidence_upper=81.00
            ),
        ]
        
        response = ForecastResponse(
            commodity="WTI",
            forecast_date="2025-01-01",
            horizon=2,
            predictions=predictions,
            model_name="LSTM",
            model_version="1.0.0"
        )
        
        assert response.commodity == "WTI"
        assert response.forecast_date == "2025-01-01"
        assert response.horizon == 2
        assert len(response.predictions) == 2
        assert response.model_name == "LSTM"
        assert response.model_version == "1.0.0"
    
    def test_predictions_count_matches_horizon(self):
        """Test that predictions count must match horizon."""
        predictions = [
            Prediction(
                date="2025-01-01",
                price=75.50,
                confidence_lower=70.00,
                confidence_upper=80.00
            ),
        ]
        
        # Valid: 1 prediction for horizon=1
        response = ForecastResponse(
            commodity="WTI",
            forecast_date="2025-01-01",
            horizon=1,
            predictions=predictions
        )
        assert len(response.predictions) == 1
        
        # Invalid: 1 prediction for horizon=2
        with pytest.raises(ValidationError) as exc_info:
            ForecastResponse(
                commodity="WTI",
                forecast_date="2025-01-01",
                horizon=2,
                predictions=predictions  # Only 1 prediction
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("predictions",) for error in errors)
    
    def test_optional_model_info(self):
        """Test that model_name and model_version are optional."""
        predictions = [
            Prediction(
                date="2025-01-01",
                price=75.50,
                confidence_lower=70.00,
                confidence_upper=80.00
            ),
        ]
        
        response = ForecastResponse(
            commodity="WTI",
            forecast_date="2025-01-01",
            horizon=1,
            predictions=predictions
        )
        
        assert response.model_name is None
        assert response.model_version is None
    
    def test_invalid_forecast_date_format(self):
        """Test that invalid forecast_date format raises ValidationError."""
        predictions = [
            Prediction(
                date="2025-01-01",
                price=75.50,
                confidence_lower=70.00,
                confidence_upper=80.00
            ),
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            ForecastResponse(
                commodity="WTI",
                forecast_date="01-01-2025",  # Wrong format
                horizon=1,
                predictions=predictions
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("forecast_date",) for error in errors)

