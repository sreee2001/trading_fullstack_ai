"""
Unit tests for API authentication (Stories 4.6.2 and 4.6.3).
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from fastapi import status

from api.auth.api_key_manager import (
    generate_api_key,
    hash_api_key,
    verify_api_key_hash,
    APIKeyManager
)
from api.auth.middleware import APIKeyAuth, get_api_key_auth
from database.models import APIKey


class TestAPIKeyGeneration:
    """Test API key generation."""
    
    def test_generate_api_key_format(self):
        """Test that generated API key has correct format."""
        key = generate_api_key()
        
        assert key.startswith("epf_")
        assert len(key) > 10  # Should have prefix + random string
    
    def test_generate_api_key_unique(self):
        """Test that generated keys are unique."""
        key1 = generate_api_key()
        key2 = generate_api_key()
        
        assert key1 != key2
    
    def test_generate_api_key_custom_prefix(self):
        """Test custom prefix."""
        key = generate_api_key(prefix="test_")
        
        assert key.startswith("test_")


class TestAPIKeyHashing:
    """Test API key hashing."""
    
    def test_hash_api_key(self):
        """Test hashing an API key."""
        key = "epf_test123"
        key_hash = hash_api_key(key)
        
        assert key_hash is not None
        assert key_hash != key  # Should be different from original
    
    def test_verify_api_key_hash(self):
        """Test verifying API key hash."""
        key = "epf_test123"
        key_hash = hash_api_key(key)
        
        # Should verify correctly
        assert verify_api_key_hash(key, key_hash) is True
        
        # Wrong key should fail
        assert verify_api_key_hash("epf_wrong", key_hash) is False


class TestAPIKeyManager:
    """Test APIKeyManager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = APIKeyManager()
        assert manager is not None
    
    def test_create_api_key(self):
        """Test creating an API key."""
        manager = APIKeyManager()
        
        with patch('api.auth.api_key_manager.get_session') as mock_session:
            mock_session_instance = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            api_key_record = MagicMock()
            api_key_record.id = 1
            
            def refresh_side_effect(record):
                # Simulate refresh by setting id
                record.id = 1
            
            mock_session_instance.add = MagicMock()
            mock_session_instance.commit = MagicMock()
            mock_session_instance.refresh = MagicMock(side_effect=refresh_side_effect)
            
            # Mock query result
            mock_session_instance.query.return_value.filter.return_value.all.return_value = []
            
            key, key_id = manager.create_api_key(user_id="user123", name="Test Key")
            
            assert key.startswith("epf_")
            assert key_id == 1
            mock_session_instance.add.assert_called_once()
    
    def test_validate_api_key(self):
        """Test validating an API key."""
        manager = APIKeyManager()
        
        test_key = "epf_test123"
        key_hash = hash_api_key(test_key)
        
        # Create mock API key record
        mock_record = MagicMock(spec=APIKey)
        mock_record.id = 1
        mock_record.key_hash = key_hash
        mock_record.is_active = True
        mock_record.expires_at = None
        mock_record.last_used_at = None
        
        with patch('api.auth.api_key_manager.get_session') as mock_session:
            mock_session_instance = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_record]
            
            result = manager.validate_api_key(test_key)
            
            assert result is not None
            assert result.id == 1
    
    def test_validate_api_key_expired(self):
        """Test validating expired API key."""
        manager = APIKeyManager()
        
        test_key = "epf_test123"
        key_hash = hash_api_key(test_key)
        
        # Create mock expired API key record
        mock_record = MagicMock(spec=APIKey)
        mock_record.id = 1
        mock_record.key_hash = key_hash
        mock_record.is_active = True
        mock_record.expires_at = datetime.now() - timedelta(days=1)  # Expired
        
        with patch('api.auth.api_key_manager.get_session') as mock_session:
            mock_session_instance = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_record]
            
            result = manager.validate_api_key(test_key)
            
            assert result is None
    
    def test_revoke_api_key(self):
        """Test revoking an API key."""
        manager = APIKeyManager()
        
        mock_record = MagicMock(spec=APIKey)
        mock_record.id = 1
        mock_record.is_active = True
        
        with patch('api.auth.api_key_manager.get_session') as mock_session:
            mock_session_instance = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_record
            
            result = manager.revoke_api_key(1)
            
            assert result is True
            assert mock_record.is_active is False
            mock_session_instance.commit.assert_called_once()


class TestAPIKeyAuth:
    """Test APIKeyAuth middleware."""
    
    def test_auth_initialization(self):
        """Test authentication initialization."""
        auth = APIKeyAuth(required=True)
        assert auth.required is True
    
    def test_auth_optional(self):
        """Test optional authentication."""
        auth = APIKeyAuth(required=False)
        assert auth.required is False
    
    # Note: Async middleware tests are covered by integration tests in test_api_admin_endpoint.py
    # The middleware functionality is tested through actual endpoint calls using TestClient

