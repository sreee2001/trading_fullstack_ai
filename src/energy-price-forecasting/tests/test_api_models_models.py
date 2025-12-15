"""
Unit tests for model information Pydantic models (Story 4.4.1).
"""

import pytest
from pydantic import ValidationError

from api.models.models import (
    ModelMetrics,
    ModelInfo,
    ModelsListResponse
)


class TestModelMetrics:
    """Test ModelMetrics model."""
    
    def test_valid_metrics(self):
        """Test valid model metrics."""
        metrics = ModelMetrics(
            rmse=2.5,
            mae=1.8,
            mape=2.3,
            r2=0.95,
            directional_accuracy=75.0,
            sharpe_ratio=1.2
        )
        
        assert metrics.rmse == 2.5
        assert metrics.mae == 1.8
        assert metrics.directional_accuracy == 75.0
    
    def test_optional_fields(self):
        """Test that all fields are optional."""
        metrics = ModelMetrics()
        
        assert metrics.rmse is None
        assert metrics.mae is None
    
    def test_rmse_must_be_non_negative(self):
        """Test that RMSE must be non-negative."""
        with pytest.raises(ValidationError):
            ModelMetrics(rmse=-1.0)
    
    def test_mape_must_be_in_range(self):
        """Test that MAPE must be between 0 and 100."""
        with pytest.raises(ValidationError):
            ModelMetrics(mape=150.0)
    
    def test_directional_accuracy_range(self):
        """Test directional accuracy range."""
        with pytest.raises(ValidationError):
            ModelMetrics(directional_accuracy=150.0)


class TestModelInfo:
    """Test ModelInfo model."""
    
    def test_valid_model_info(self):
        """Test valid model info."""
        metrics = ModelMetrics(rmse=2.5, mae=1.8)
        
        model_info = ModelInfo(
            model_id="WTI_LSTM:1",
            model_name="WTI_LSTM",
            commodity="WTI",
            model_type="LSTM",
            version="1",
            stage="Production",
            metrics=metrics
        )
        
        assert model_info.model_id == "WTI_LSTM:1"
        assert model_info.commodity == "WTI"
        assert model_info.model_type == "LSTM"
        assert model_info.metrics.rmse == 2.5
    
    def test_model_info_with_all_fields(self):
        """Test model info with all optional fields."""
        model_info = ModelInfo(
            model_id="BRENT_ARIMA:2",
            model_name="BRENT_ARIMA",
            commodity="BRENT",
            model_type="ARIMA",
            version="2",
            stage="Staging",
            training_date="2025-01-15",
            created_at="2025-01-15T10:30:00Z",
            run_id="abc123",
            experiment_id="exp456",
            tags={"environment": "production"},
            description="ARIMA model for Brent crude"
        )
        
        assert model_info.training_date == "2025-01-15"
        assert model_info.run_id == "abc123"
        assert model_info.tags == {"environment": "production"}
    
    def test_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError):
            ModelInfo(
                model_name="WTI_LSTM",
                commodity="WTI",
                model_type="LSTM",
                version="1",
                stage="Production"
            )


class TestModelsListResponse:
    """Test ModelsListResponse model."""
    
    def test_valid_response(self):
        """Test valid models list response."""
        model1 = ModelInfo(
            model_id="WTI_LSTM:1",
            model_name="WTI_LSTM",
            commodity="WTI",
            model_type="LSTM",
            version="1",
            stage="Production"
        )
        
        model2 = ModelInfo(
            model_id="BRENT_ARIMA:1",
            model_name="BRENT_ARIMA",
            commodity="BRENT",
            model_type="ARIMA",
            version="1",
            stage="Production"
        )
        
        response = ModelsListResponse(
            models=[model1, model2],
            total_count=2
        )
        
        assert len(response.models) == 2
        assert response.total_count == 2
    
    def test_response_with_commodity_filter(self):
        """Test response with commodity filter."""
        model = ModelInfo(
            model_id="WTI_LSTM:1",
            model_name="WTI_LSTM",
            commodity="WTI",
            model_type="LSTM",
            version="1",
            stage="Production"
        )
        
        response = ModelsListResponse(
            models=[model],
            total_count=1,
            commodity_filter="WTI"
        )
        
        assert response.commodity_filter == "WTI"
    
    def test_empty_response(self):
        """Test empty models list response."""
        response = ModelsListResponse(
            models=[],
            total_count=0
        )
        
        assert len(response.models) == 0
        assert response.total_count == 0
    
    def test_total_count_must_be_non_negative(self):
        """Test that total_count must be non-negative."""
        model = ModelInfo(
            model_id="WTI_LSTM:1",
            model_name="WTI_LSTM",
            commodity="WTI",
            model_type="LSTM",
            version="1",
            stage="Production"
        )
        
        with pytest.raises(ValidationError):
            ModelsListResponse(
                models=[model],
                total_count=-1
            )

