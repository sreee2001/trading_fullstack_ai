"""
Pydantic models for API request/response validation.

This package contains all Pydantic models used for:
- Request validation
- Response serialization
- Data transfer objects (DTOs)
"""

from api.models.forecast import (
    ForecastRequest,
    ForecastResponse,
    Prediction,
)

__all__ = [
    "ForecastRequest",
    "ForecastResponse",
    "Prediction",
]

