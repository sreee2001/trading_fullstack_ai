"""
Unit tests for health check endpoints (Stories 4.9.1 and 4.9.2).
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status

from api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthCheckEndpoint:
    """Test basic health check endpoint."""
    
    def test_health_check_endpoint_exists(self, client):
        """Test that /health endpoint exists."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
    
    def test_health_check_response(self, client):
        """Test health check response structure."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_health_check_no_auth_required(self, client):
        """Test that health check doesn't require authentication."""
        # Should work without API key
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK


class TestReadinessCheckEndpoint:
    """Test readiness check endpoint."""
    
    def test_readiness_check_endpoint_exists(self, client):
        """Test that /ready endpoint exists."""
        response = client.get("/ready")
        # May return 200 or 503 depending on component status
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
    
    def test_readiness_check_response_structure(self, client):
        """Test readiness check response structure."""
        with patch('api.routes.health.get_database_manager') as mock_db:
            mock_db_manager = MagicMock()
            mock_db_manager.verify_connection.return_value = None
            mock_db.return_value = mock_db_manager
            
            with patch('api.routes.health.is_redis_available', return_value=False):
                with patch('api.routes.health.get_ml_models', return_value={}):
                    response = client.get("/ready")
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert "status" in data
                    assert "components" in data
                    assert "database" in data["components"]
    
    def test_readiness_check_database_unhealthy(self, client):
        """Test readiness check when database is unhealthy."""
        with patch('api.routes.health.get_database_manager') as mock_db:
            mock_db_manager = MagicMock()
            mock_db_manager.verify_connection.side_effect = Exception("Connection failed")
            mock_db.return_value = mock_db_manager
            
            with patch('api.routes.health.is_redis_available', return_value=False):
                with patch('api.routes.health.get_ml_models', return_value={}):
                    response = client.get("/ready")
                    
                    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
                    data = response.json()
                    assert data["status"] == "not_ready"
                    assert data["components"]["database"] == "unhealthy"
    
    def test_readiness_check_all_healthy(self, client):
        """Test readiness check when all components are healthy."""
        with patch('api.routes.health.get_database_manager') as mock_db:
            mock_db_manager = MagicMock()
            mock_db_manager.verify_connection.return_value = None
            mock_db.return_value = mock_db_manager
            
            with patch('api.routes.health.is_redis_available', return_value=True):
                with patch('api.routes.health.get_ml_models', return_value={"WTI": "model"}):
                    response = client.get("/ready")
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert data["status"] == "ready"
                    assert data["components"]["database"] == "healthy"
                    assert data["components"]["redis"] == "healthy"
                    assert data["components"]["models"] == "available"
    
    def test_readiness_check_redis_optional(self, client):
        """Test that Redis being unavailable doesn't fail readiness."""
        with patch('api.routes.health.get_database_manager') as mock_db:
            mock_db_manager = MagicMock()
            mock_db_manager.verify_connection.return_value = None
            mock_db.return_value = mock_db_manager
            
            with patch('api.routes.health.is_redis_available', return_value=False):
                with patch('api.routes.health.get_ml_models', return_value={}):
                    response = client.get("/ready")
                    
                    # Should still be ready if database is healthy
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert data["components"]["redis"] == "not_configured"
    
    def test_readiness_check_no_auth_required(self, client):
        """Test that readiness check doesn't require authentication."""
        with patch('api.routes.health.get_database_manager') as mock_db:
            mock_db_manager = MagicMock()
            mock_db_manager.verify_connection.return_value = None
            mock_db.return_value = mock_db_manager
            
            with patch('api.routes.health.is_redis_available', return_value=False):
                with patch('api.routes.health.get_ml_models', return_value={}):
                    # Should work without API key
                    response = client.get("/ready")
                    assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]

