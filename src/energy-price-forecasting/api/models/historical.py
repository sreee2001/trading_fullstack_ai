"""
Pydantic models for historical data requests and responses.

This module defines the data models for querying historical energy price data.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date


class HistoricalDataRequest(BaseModel):
    """
    Pydantic model for a historical data request (query parameters).
    
    Used for GET /api/v1/historical endpoint.
    """
    commodity: str = Field(
        ...,
        pattern="^(WTI|BRENT|NG)$",
        description="Commodity symbol (WTI, BRENT, or NG)"
    )
    start_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Start date for historical data (YYYY-MM-DD)"
    )
    end_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="End date for historical data (YYYY-MM-DD)"
    )
    limit: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum number of records to return (1-10000)"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of records to skip (for pagination)"
    )

    @field_validator("commodity", mode="before")
    @classmethod
    def commodity_to_upper(cls, v: str) -> str:
        """Convert commodity to uppercase."""
        return v.upper()

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format."""
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: str, info) -> str:
        """Validate that end_date is after start_date."""
        if "start_date" in info.data:
            start_date = date.fromisoformat(info.data["start_date"])
            end_date = date.fromisoformat(v)
            if end_date < start_date:
                raise ValueError("end_date must be after or equal to start_date")
        return v

    def get_start_date_as_date(self) -> date:
        """Convert the start_date string to a datetime.date object."""
        return date.fromisoformat(self.start_date)

    def get_end_date_as_date(self) -> date:
        """Convert the end_date string to a datetime.date object."""
        return date.fromisoformat(self.end_date)


class PricePoint(BaseModel):
    """
    Pydantic model for a single historical price point.
    """
    date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Date of the price point (YYYY-MM-DD)"
    )
    price: float = Field(
        ...,
        gt=0,
        description="Price value"
    )
    volume: Optional[float] = Field(
        default=None,
        ge=0,
        description="Trading volume (if available)"
    )
    open: Optional[float] = Field(
        default=None,
        gt=0,
        description="Opening price (if available)"
    )
    high: Optional[float] = Field(
        default=None,
        gt=0,
        description="High price (if available)"
    )
    low: Optional[float] = Field(
        default=None,
        gt=0,
        description="Low price (if available)"
    )
    close: Optional[float] = Field(
        default=None,
        gt=0,
        description="Closing price (if available)"
    )

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format."""
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

    @field_validator("high")
    @classmethod
    def validate_high(cls, v: Optional[float], info) -> Optional[float]:
        """Validate that high >= low if both are present."""
        if v is not None and "low" in info.data and info.data["low"] is not None:
            if v < info.data["low"]:
                raise ValueError("high must be >= low")
        return v

    @field_validator("low")
    @classmethod
    def validate_low(cls, v: Optional[float], info) -> Optional[float]:
        """Validate that low <= high if both are present."""
        if v is not None and "high" in info.data and info.data["high"] is not None:
            if v > info.data["high"]:
                raise ValueError("low must be <= high")
        return v


class HistoricalDataResponse(BaseModel):
    """
    Pydantic model for a historical data response.
    """
    commodity: str = Field(..., description="Commodity symbol")
    start_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Start date of the query (YYYY-MM-DD)"
    )
    end_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="End date of the query (YYYY-MM-DD)"
    )
    data: List[PricePoint] = Field(..., description="List of historical price points")
    total_count: int = Field(..., ge=0, description="Total number of records matching the query")
    limit: int = Field(..., ge=1, description="Limit used for pagination")
    offset: int = Field(..., ge=0, description="Offset used for pagination")
    has_more: bool = Field(..., description="Whether there are more records available")

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format."""
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

