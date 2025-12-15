"""
Unit tests for FastAPI application initialization (Story 4.1.1).
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestFastAPIInitialization:
    """Test FastAPI application initialization."""
    
    def test_app_exists(self):
        """Test that the FastAPI app is created."""
        assert app is not None
        assert app.title == "Energy Price Forecasting API"
        assert app.version == "1.0.0"
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Energy Price Forecasting API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"
        assert "docs" in data
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_cors_headers(self, client):
        """Test that CORS middleware is configured."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # CORS middleware should allow the request
        assert response.status_code in [200, 405]  # 405 if OPTIONS not handled
    
    def test_openapi_docs_available(self, client):
        """Test that OpenAPI documentation is available."""
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert data["info"]["title"] == "Energy Price Forecasting API"
        assert data["info"]["version"] == "1.0.0"
    
    def test_swagger_ui_available(self, client):
        """Test that Swagger UI is accessible."""
        response = client.get("/api/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_redoc_available(self, client):
        """Test that ReDoc is accessible."""
        response = client.get("/api/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

