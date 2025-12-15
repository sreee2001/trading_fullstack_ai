"""
Pydantic models for model information endpoints.

This module defines the data models for querying model metadata
from the MLflow model registry.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class ModelMetrics(BaseModel):
    """
    Pydantic model for model performance metrics.
    """
    rmse: Optional[float] = Field(None, ge=0, description="Root Mean Squared Error")
    mae: Optional[float] = Field(None, ge=0, description="Mean Absolute Error")
    mape: Optional[float] = Field(None, ge=0, le=100, description="Mean Absolute Percentage Error (%)")
    r2: Optional[float] = Field(None, description="R-squared score")
    directional_accuracy: Optional[float] = Field(None, ge=0, le=100, description="Directional Accuracy (%)")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe Ratio")
    sortino_ratio: Optional[float] = Field(None, description="Sortino Ratio")
    max_drawdown: Optional[float] = Field(None, le=0, description="Maximum Drawdown")
    win_rate: Optional[float] = Field(None, ge=0, le=100, description="Win Rate (%)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rmse": 2.5,
                "mae": 1.8,
                "mape": 2.3,
                "r2": 0.95,
                "directional_accuracy": 75.0,
                "sharpe_ratio": 1.2,
                "sortino_ratio": 1.5,
                "max_drawdown": -0.15,
                "win_rate": 60.0
            }
        }
    )


class ModelInfo(BaseModel):
    """
    Pydantic model for model metadata.
    """
    model_id: str = Field(..., description="Unique model identifier (name:version)")
    model_name: str = Field(..., description="Model name")
    commodity: str = Field(..., description="Commodity symbol (WTI, BRENT, NG)")
    model_type: str = Field(..., description="Model type (LSTM, ARIMA, Prophet, etc.)")
    version: str = Field(..., description="Model version")
    stage: str = Field(..., description="Model stage (Production, Staging, Archived)")
    training_date: Optional[str] = Field(None, description="Date when model was trained (YYYY-MM-DD)")
    created_at: Optional[str] = Field(None, description="Date when model was registered (ISO format)")
    metrics: Optional[ModelMetrics] = Field(None, description="Model performance metrics")
    run_id: Optional[str] = Field(None, description="MLflow run ID")
    experiment_id: Optional[str] = Field(None, description="MLflow experiment ID")
    tags: Optional[Dict[str, str]] = Field(None, description="Model tags")
    description: Optional[str] = Field(None, description="Model description")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "model_id": "WTI_LSTM:1",
                "model_name": "WTI_LSTM",
                "commodity": "WTI",
                "model_type": "LSTM",
                "version": "1",
                "stage": "Production",
                "training_date": "2025-01-15",
                "created_at": "2025-01-15T10:30:00Z",
                "metrics": {
                    "rmse": 2.5,
                    "mae": 1.8,
                    "directional_accuracy": 75.0
                },
                "run_id": "abc123",
                "experiment_id": "exp456"
            }
        }
    )


class ModelsListResponse(BaseModel):
    """
    Pydantic model for models list response.
    """
    models: List[ModelInfo] = Field(..., description="List of model information")
    total_count: int = Field(..., ge=0, description="Total number of models")
    commodity_filter: Optional[str] = Field(None, description="Commodity filter applied (if any)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "models": [
                    {
                        "model_id": "WTI_LSTM:1",
                        "model_name": "WTI_LSTM",
                        "commodity": "WTI",
                        "model_type": "LSTM",
                        "version": "1",
                        "stage": "Production"
                    }
                ],
                "total_count": 1,
                "commodity_filter": "WTI"
            }
        }
    )

