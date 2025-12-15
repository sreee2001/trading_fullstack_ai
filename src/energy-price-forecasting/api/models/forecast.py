"""
Pydantic models for forecast endpoints.

This module defines request and response models for the forecast API endpoint.
"""

from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator


class ForecastRequest(BaseModel):
    """
    Request model for forecast endpoint.
    
    Attributes:
        commodity: Commodity symbol (WTI, BRENT, NG)
        horizon: Forecast horizon in days (1-30)
        start_date: Start date for forecast (YYYY-MM-DD format)
    """
    
    commodity: str = Field(
        ...,
        description="Commodity symbol",
        examples=["WTI", "BRENT", "NG"]
    )
    horizon: int = Field(
        ...,
        ge=1,
        le=30,
        description="Forecast horizon in days (1-30)"
    )
    start_date: str = Field(
        ...,
        description="Start date for forecast (YYYY-MM-DD format)",
        examples=["2025-01-01"]
    )
    
    @field_validator("commodity")
    @classmethod
    def validate_commodity(cls, v: str) -> str:
        """Validate commodity symbol."""
        allowed_commodities = ["WTI", "BRENT", "NG"]
        v_upper = v.upper()
        if v_upper not in allowed_commodities:
            raise ValueError(
                f"Commodity must be one of {allowed_commodities}, got {v}"
            )
        return v_upper
    
    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, v: str) -> str:
        """Validate date format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                "start_date must be in YYYY-MM-DD format"
            )
        return v
    
    def get_start_date_as_date(self) -> date:
        """Convert start_date string to date object."""
        return datetime.strptime(self.start_date, "%Y-%m-%d").date()


class Prediction(BaseModel):
    """
    Single prediction data point.
    
    Attributes:
        date: Prediction date (YYYY-MM-DD format)
        price: Predicted price
        confidence_lower: Lower bound of confidence interval
        confidence_upper: Upper bound of confidence interval
    """
    
    date: str = Field(
        ...,
        description="Prediction date (YYYY-MM-DD format)",
        examples=["2025-01-01"]
    )
    price: float = Field(
        ...,
        ge=0,
        description="Predicted price"
    )
    confidence_lower: float = Field(
        ...,
        ge=0,
        description="Lower bound of confidence interval"
    )
    confidence_upper: float = Field(
        ...,
        ge=0,
        description="Upper bound of confidence interval"
    )
    
    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate date format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                "date must be in YYYY-MM-DD format"
            )
        return v
    
    @field_validator("confidence_upper")
    @classmethod
    def validate_confidence_interval(cls, v: float, info) -> float:
        """Validate that confidence_upper >= confidence_lower."""
        if "confidence_lower" in info.data:
            if v < info.data["confidence_lower"]:
                raise ValueError(
                    "confidence_upper must be >= confidence_lower"
                )
        return v


class ForecastResponse(BaseModel):
    """
    Response model for forecast endpoint.
    
    Attributes:
        commodity: Commodity symbol
        forecast_date: Date when forecast was generated (YYYY-MM-DD)
        horizon: Forecast horizon in days
        predictions: List of predictions
        model_name: Name of the model used (optional)
        model_version: Version of the model used (optional)
    """
    
    commodity: str = Field(
        ...,
        description="Commodity symbol",
        examples=["WTI", "BRENT", "NG"]
    )
    forecast_date: str = Field(
        ...,
        description="Date when forecast was generated (YYYY-MM-DD)",
        examples=["2025-01-01"]
    )
    horizon: int = Field(
        ...,
        ge=1,
        le=30,
        description="Forecast horizon in days"
    )
    predictions: List[Prediction] = Field(
        ...,
        min_length=1,
        description="List of predictions"
    )
    model_name: Optional[str] = Field(
        None,
        description="Name of the model used"
    )
    model_version: Optional[str] = Field(
        None,
        description="Version of the model used"
    )
    
    @field_validator("forecast_date")
    @classmethod
    def validate_forecast_date(cls, v: str) -> str:
        """Validate date format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                "forecast_date must be in YYYY-MM-DD format"
            )
        return v
    
    @field_validator("predictions")
    @classmethod
    def validate_predictions_count(cls, v: List[Prediction], info) -> List[Prediction]:
        """Validate that predictions count matches horizon."""
        if "horizon" in info.data:
            horizon = info.data["horizon"]
            if len(v) != horizon:
                raise ValueError(
                    f"Number of predictions ({len(v)}) must match horizon ({horizon})"
                )
        return v

