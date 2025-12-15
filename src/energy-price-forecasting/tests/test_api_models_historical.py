"""
Unit tests for historical data Pydantic models (Story 4.3.1).
"""

import pytest
from pydantic import ValidationError

from api.models.historical import (
    HistoricalDataRequest,
    HistoricalDataResponse,
    PricePoint
)


class TestHistoricalDataRequest:
    """Test HistoricalDataRequest model."""
    
    def test_valid_request(self):
        """Test valid historical data request."""
        request = HistoricalDataRequest(
            commodity="WTI",
            start_date="2025-01-01",
            end_date="2025-01-31",
            limit=100,
            offset=0
        )
        
        assert request.commodity == "WTI"
        assert request.start_date == "2025-01-01"
        assert request.end_date == "2025-01-31"
        assert request.limit == 100
        assert request.offset == 0
    
    def test_default_values(self):
        """Test default values for limit and offset."""
        request = HistoricalDataRequest(
            commodity="BRENT",
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        
        assert request.limit == 1000
        assert request.offset == 0
    
    def test_commodity_uppercase_conversion(self):
        """Test that commodity is converted to uppercase."""
        request = HistoricalDataRequest(
            commodity="wti",
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        
        assert request.commodity == "WTI"
    
    def test_invalid_commodity(self):
        """Test invalid commodity."""
        with pytest.raises(ValidationError):
            HistoricalDataRequest(
                commodity="INVALID",
                start_date="2025-01-01",
                end_date="2025-01-31"
            )
    
    def test_invalid_date_format(self):
        """Test invalid date format."""
        with pytest.raises(ValidationError):
            HistoricalDataRequest(
                commodity="WTI",
                start_date="01-01-2025",
                end_date="2025-01-31"
            )
    
    def test_end_date_before_start_date(self):
        """Test that end_date must be after start_date."""
        with pytest.raises(ValidationError):
            HistoricalDataRequest(
                commodity="WTI",
                start_date="2025-01-31",
                end_date="2025-01-01"
            )
    
    def test_limit_too_low(self):
        """Test limit validation (must be >= 1)."""
        with pytest.raises(ValidationError):
            HistoricalDataRequest(
                commodity="WTI",
                start_date="2025-01-01",
                end_date="2025-01-31",
                limit=0
            )
    
    def test_limit_too_high(self):
        """Test limit validation (must be <= 10000)."""
        with pytest.raises(ValidationError):
            HistoricalDataRequest(
                commodity="WTI",
                start_date="2025-01-01",
                end_date="2025-01-31",
                limit=10001
            )
    
    def test_offset_negative(self):
        """Test offset validation (must be >= 0)."""
        with pytest.raises(ValidationError):
            HistoricalDataRequest(
                commodity="WTI",
                start_date="2025-01-01",
                end_date="2025-01-31",
                offset=-1
            )
    
    def test_get_start_date_as_date(self):
        """Test conversion of start_date to date object."""
        request = HistoricalDataRequest(
            commodity="WTI",
            start_date="2025-01-15",
            end_date="2025-01-31"
        )
        
        date_obj = request.get_start_date_as_date()
        assert date_obj.year == 2025
        assert date_obj.month == 1
        assert date_obj.day == 15
    
    def test_get_end_date_as_date(self):
        """Test conversion of end_date to date object."""
        request = HistoricalDataRequest(
            commodity="WTI",
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        
        date_obj = request.get_end_date_as_date()
        assert date_obj.year == 2025
        assert date_obj.month == 1
        assert date_obj.day == 31


class TestPricePoint:
    """Test PricePoint model."""
    
    def test_valid_price_point(self):
        """Test valid price point."""
        point = PricePoint(
            date="2025-01-15",
            price=75.50
        )
        
        assert point.date == "2025-01-15"
        assert point.price == 75.50
        assert point.volume is None
    
    def test_price_point_with_all_fields(self):
        """Test price point with all optional fields."""
        point = PricePoint(
            date="2025-01-15",
            price=75.50,
            volume=1000000.0,
            open=75.00,
            high=76.00,
            low=74.50,
            close=75.50
        )
        
        assert point.volume == 1000000.0
        assert point.open == 75.00
        assert point.high == 76.00
        assert point.low == 74.50
        assert point.close == 75.50
    
    def test_price_must_be_positive(self):
        """Test that price must be positive."""
        with pytest.raises(ValidationError):
            PricePoint(
                date="2025-01-15",
                price=-10.0
            )
    
    def test_high_must_be_greater_than_low(self):
        """Test that high must be >= low."""
        with pytest.raises(ValidationError):
            PricePoint(
                date="2025-01-15",
                price=75.50,
                high=74.00,
                low=75.00
            )
    
    def test_invalid_date_format(self):
        """Test invalid date format."""
        with pytest.raises(ValidationError):
            PricePoint(
                date="01-15-2025",
                price=75.50
            )


class TestHistoricalDataResponse:
    """Test HistoricalDataResponse model."""
    
    def test_valid_response(self):
        """Test valid historical data response."""
        price_points = [
            PricePoint(date="2025-01-01", price=75.00),
            PricePoint(date="2025-01-02", price=75.50)
        ]
        
        response = HistoricalDataResponse(
            commodity="WTI",
            start_date="2025-01-01",
            end_date="2025-01-31",
            data=price_points,
            total_count=100,
            limit=1000,
            offset=0,
            has_more=False
        )
        
        assert response.commodity == "WTI"
        assert len(response.data) == 2
        assert response.total_count == 100
        assert response.has_more is False
    
    def test_response_with_more_data(self):
        """Test response indicating more data available."""
        price_points = [
            PricePoint(date="2025-01-01", price=75.00)
        ]
        
        response = HistoricalDataResponse(
            commodity="BRENT",
            start_date="2025-01-01",
            end_date="2025-01-31",
            data=price_points,
            total_count=5000,
            limit=1000,
            offset=0,
            has_more=True
        )
        
        assert response.has_more is True
        assert response.total_count == 5000
    
    def test_empty_data_response(self):
        """Test response with no data."""
        response = HistoricalDataResponse(
            commodity="NG",
            start_date="2025-01-01",
            end_date="2025-01-31",
            data=[],
            total_count=0,
            limit=1000,
            offset=0,
            has_more=False
        )
        
        assert len(response.data) == 0
        assert response.total_count == 0
    
    def test_invalid_date_format(self):
        """Test invalid date format in response."""
        with pytest.raises(ValidationError):
            HistoricalDataResponse(
                commodity="WTI",
                start_date="01-01-2025",
                end_date="2025-01-31",
                data=[],
                total_count=0,
                limit=1000,
                offset=0,
                has_more=False
            )

