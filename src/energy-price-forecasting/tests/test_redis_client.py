"""
Unit tests for Redis client (Story 4.7.1).
"""

import pytest
from unittest.mock import patch, MagicMock

from api.cache.redis_client import RedisClient, get_redis_client, is_redis_available


class TestRedisClient:
    """Test Redis client initialization and connection."""
    
    def test_redis_client_initialization_without_redis(self):
        """Test Redis client initialization when Redis library is not available."""
        with patch('api.cache.redis_client.REDIS_AVAILABLE', False):
            client = RedisClient()
            assert client.client is None
            assert client.is_available is False
    
    def test_redis_client_initialization_with_redis(self):
        """Test Redis client initialization when Redis is available."""
        with patch('api.cache.redis_client.REDIS_AVAILABLE', True):
            mock_redis = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            
            with patch('api.cache.redis_client.redis') as mock_redis_module:
                mock_redis_module.Redis.return_value = mock_client
                mock_redis_module.from_url.return_value = mock_client
                
                client = RedisClient(host="localhost", port=6379, db=0)
                
                assert client.client is not None
                assert client.is_available is True
    
    def test_redis_client_connection_failure(self):
        """Test Redis client handles connection failure gracefully."""
        with patch('api.cache.redis_client.REDIS_AVAILABLE', True):
            mock_redis = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.side_effect = Exception("Connection failed")
            
            with patch('api.cache.redis_client.redis') as mock_redis_module:
                mock_redis_module.Redis.return_value = mock_client
                
                client = RedisClient(host="localhost", port=6379, db=0)
                
                assert client.client is not None
                assert client.is_available is False
    
    def test_redis_ping(self):
        """Test Redis ping method."""
        with patch('api.cache.redis_client.REDIS_AVAILABLE', True):
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            
            with patch('api.cache.redis_client.redis') as mock_redis_module:
                mock_redis_module.Redis.return_value = mock_client
                
                client = RedisClient(host="localhost", port=6379, db=0)
                result = client.ping()
                
                assert result is True
                mock_client.ping.assert_called_once()
    
    def test_redis_ping_failure(self):
        """Test Redis ping handles failures."""
        with patch('api.cache.redis_client.REDIS_AVAILABLE', True):
            mock_client = MagicMock()
            mock_client.ping.side_effect = Exception("Connection lost")
            
            with patch('api.cache.redis_client.redis') as mock_redis_module:
                mock_redis_module.Redis.return_value = mock_client
                
                client = RedisClient(host="localhost", port=6379, db=0)
                result = client.ping()
                
                assert result is False
    
    def test_redis_close(self):
        """Test Redis connection close."""
        with patch('api.cache.redis_client.REDIS_AVAILABLE', True):
            mock_client = MagicMock()
            
            with patch('api.cache.redis_client.redis') as mock_redis_module:
                mock_redis_module.Redis.return_value = mock_client
                
                client = RedisClient(host="localhost", port=6379, db=0)
                client.close()
                
                mock_client.close.assert_called_once()
                assert client.client is None
                assert client.is_available is False
    
    def test_get_redis_client_singleton(self):
        """Test get_redis_client returns singleton instance."""
        with patch('api.cache.redis_client.RedisClient') as mock_client_class:
            mock_instance = MagicMock()
            mock_client_class.return_value = mock_instance
            
            client1 = get_redis_client()
            client2 = get_redis_client()
            
            assert client1 is client2
            mock_client_class.assert_called_once()
    
    def test_is_redis_available(self):
        """Test is_redis_available helper function."""
        with patch('api.cache.redis_client.get_redis_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.is_available = True
            mock_get_client.return_value = mock_client
            
            result = is_redis_available()
            
            assert result is True

