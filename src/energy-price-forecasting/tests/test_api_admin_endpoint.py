"""
Integration tests for admin API endpoints (Story 4.6.4).
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status

from api.main import app
from database.models import APIKey


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestAdminAPIKeyEndpoints:
    """Test admin API key management endpoints."""
    
    def test_create_api_key_endpoint(self, client):
        """Test POST /api/v1/admin/keys endpoint."""
        with patch('api.routes.admin.get_api_key_manager') as mock_manager:
            mock_manager_instance = MagicMock()
            mock_manager.return_value = mock_manager_instance
            
            mock_manager_instance.create_api_key.return_value = ("epf_test123", 1)
            
            response = client.post(
                "/api/v1/admin/keys",
                json={
                    "user_id": "user123",
                    "name": "Test Key",
                    "expires_in_days": 30
                }
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert "api_key" in data
            assert data["api_key"].startswith("epf_")
            assert data["key_id"] == 1
    
    def test_revoke_api_key_endpoint(self, client):
        """Test DELETE /api/v1/admin/keys/{key_id} endpoint."""
        with patch('api.routes.admin.get_api_key_manager') as mock_manager:
            mock_manager_instance = MagicMock()
            mock_manager.return_value = mock_manager_instance
            
            mock_manager_instance.revoke_api_key.return_value = True
            
            response = client.delete("/api/v1/admin/keys/1")
            
            assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_revoke_api_key_not_found(self, client):
        """Test revoking non-existent API key."""
        with patch('api.routes.admin.get_api_key_manager') as mock_manager:
            mock_manager_instance = MagicMock()
            mock_manager.return_value = mock_manager_instance
            
            mock_manager_instance.revoke_api_key.return_value = False
            
            response = client.delete("/api/v1/admin/keys/999")
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_api_keys_endpoint(self, client):
        """Test GET /api/v1/admin/keys endpoint."""
        with patch('api.routes.admin.get_api_key_manager') as mock_manager:
            mock_manager_instance = MagicMock()
            mock_manager.return_value = mock_manager_instance
            
            # Create mock API key records
            mock_key1 = MagicMock(spec=APIKey)
            mock_key1.id = 1
            mock_key1.user_id = "user123"
            mock_key1.name = "Key 1"
            mock_key1.created_at = MagicMock()
            mock_key1.created_at.isoformat.return_value = "2025-01-01T00:00:00"
            mock_key1.expires_at = None
            mock_key1.is_active = True
            mock_key1.last_used_at = None
            
            mock_key2 = MagicMock(spec=APIKey)
            mock_key2.id = 2
            mock_key2.user_id = "user456"
            mock_key2.name = "Key 2"
            mock_key2.created_at = MagicMock()
            mock_key2.created_at.isoformat.return_value = "2025-01-02T00:00:00"
            mock_key2.expires_at = None
            mock_key2.is_active = True
            mock_key2.last_used_at = None
            
            mock_manager_instance.list_api_keys.return_value = [mock_key1, mock_key2]
            
            response = client.get("/api/v1/admin/keys")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "keys" in data
            assert len(data["keys"]) == 2
            assert data["total_count"] == 2
    
    def test_get_api_key_endpoint(self, client):
        """Test GET /api/v1/admin/keys/{key_id} endpoint."""
        with patch('api.routes.admin.get_api_key_manager') as mock_manager:
            mock_manager_instance = MagicMock()
            mock_manager.return_value = mock_manager_instance
            
            mock_key = MagicMock(spec=APIKey)
            mock_key.id = 1
            mock_key.user_id = "user123"
            mock_key.name = "Test Key"
            mock_key.created_at = MagicMock()
            mock_key.created_at.isoformat.return_value = "2025-01-01T00:00:00"
            mock_key.expires_at = None
            mock_key.is_active = True
            mock_key.last_used_at = None
            
            mock_manager_instance.get_api_key.return_value = mock_key
            
            response = client.get("/api/v1/admin/keys/1")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == 1
            assert data["user_id"] == "user123"
            assert data["name"] == "Test Key"
    
    def test_get_api_key_not_found(self, client):
        """Test getting non-existent API key."""
        with patch('api.routes.admin.get_api_key_manager') as mock_manager:
            mock_manager_instance = MagicMock()
            mock_manager.return_value = mock_manager_instance
            
            mock_manager_instance.get_api_key.return_value = None
            
            response = client.get("/api/v1/admin/keys/999")
            
            assert response.status_code == status.HTTP_404_NOT_FOUND

