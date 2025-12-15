"""
Unit tests for model information endpoint (Stories 4.4.2 and 4.4.3).
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status

from api.main import app


class TestModelsEndpoint:
    """Test models endpoint."""
    
    def test_models_endpoint_exists(self):
        """Test that models endpoint is registered."""
        client = TestClient(app)
        
        response = client.get("/api/v1/models")
        
        # Should succeed (200) with placeholder data or actual data
        assert response.status_code == status.HTTP_200_OK
    
    def test_models_endpoint_returns_list(self):
        """Test that models endpoint returns list of models."""
        client = TestClient(app)
        
        response = client.get("/api/v1/models")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "models" in data
        assert "total_count" in data
        assert isinstance(data["models"], list)
        assert isinstance(data["total_count"], int)
    
    def test_models_endpoint_with_commodity_filter(self):
        """Test models endpoint with commodity filter."""
        client = TestClient(app)
        
        response = client.get("/api/v1/models", params={"commodity": "WTI"})
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["commodity_filter"] == "WTI"
        
        # All models should be for WTI
        for model in data["models"]:
            assert model["commodity"] == "WTI"
    
    def test_models_endpoint_invalid_commodity_filter(self):
        """Test models endpoint with invalid commodity filter."""
        client = TestClient(app)
        
        response = client.get("/api/v1/models", params={"commodity": "INVALID"})
        
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_models_response_structure(self):
        """Test that models response has correct structure."""
        client = TestClient(app)
        
        response = client.get("/api/v1/models")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        
        # Check required fields
        assert "models" in data
        assert "total_count" in data
        
        # Check model structure if models exist
        if len(data["models"]) > 0:
            model = data["models"][0]
            
            assert "model_id" in model
            assert "model_name" in model
            assert "commodity" in model
            assert "model_type" in model
            assert "version" in model
            assert "stage" in model
    
    def test_models_endpoint_with_mlflow_mock(self):
        """Test models endpoint with mocked MLflow."""
        client = TestClient(app)
        
        mock_models = [
            {
                'model_id': 'WTI_LSTM:1',
                'model_name': 'WTI_LSTM',
                'commodity': 'WTI',
                'model_type': 'LSTM',
                'version': '1',
                'stage': 'Production',
                'training_date': '2025-01-15',
                'created_at': '2025-01-15T10:30:00Z',
                'metrics': {'rmse': 2.5, 'mae': 1.8},
                'run_id': 'abc123',
                'experiment_id': 'exp456',
                'tags': {},
                'description': None
            }
        ]
        
        with patch('api.routes.models.get_model_info_service') as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.get_all_models.return_value = mock_models
            mock_service.return_value = mock_service_instance
            
            response = client.get("/api/v1/models")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert len(data["models"]) == 1
            assert data["models"][0]["model_id"] == "WTI_LSTM:1"


class TestModelInfoService:
    """Test ModelInfoService."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        from api.services.model_info_service import ModelInfoService
        
        service = ModelInfoService()
        assert service is not None
    
    def test_get_all_models_returns_list(self):
        """Test that get_all_models returns a list."""
        from api.services.model_info_service import ModelInfoService
        
        service = ModelInfoService()
        models = service.get_all_models()
        
        assert isinstance(models, list)
    
    def test_get_all_models_with_commodity_filter(self):
        """Test get_all_models with commodity filter."""
        from api.services.model_info_service import ModelInfoService
        
        service = ModelInfoService()
        models = service.get_all_models(commodity_filter="WTI")
        
        # All models should be for WTI (if any)
        for model in models:
            assert model['commodity'] == "WTI"
    
    def test_placeholder_models_structure(self):
        """Test that placeholder models have correct structure."""
        from api.services.model_info_service import ModelInfoService
        
        service = ModelInfoService()
        # Force placeholder mode by setting registry to None
        service.registry = None
        
        models = service.get_all_models()
        
        assert len(models) > 0
        
        for model in models:
            assert 'model_id' in model
            assert 'model_name' in model
            assert 'commodity' in model
            assert 'model_type' in model
            assert 'version' in model
            assert 'stage' in model

