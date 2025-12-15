"""
Unit tests for response cache (Story 4.7.3).
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from api.cache.response_cache import ResponseCache, get_response_cache


class TestResponseCache:
    """Test response cache functionality."""
    
    def test_response_cache_initialization(self):
        """Test response cache initialization."""
        cache = ResponseCache(default_ttl=300)
        assert cache.default_ttl == 300
        assert cache.redis_client is not None
    
    def test_generate_cache_key(self):
        """Test cache key generation."""
        cache = ResponseCache()
        
        key1 = cache._generate_cache_key("/api/v1/historical", {"commodity": "WTI"})
        key2 = cache._generate_cache_key("/api/v1/historical", {"commodity": "WTI"})
        
        # Same params should generate same key
        assert key1 == key2
        
        # Different params should generate different key
        key3 = cache._generate_cache_key("/api/v1/historical", {"commodity": "BRENT"})
        assert key1 != key3
    
    def test_get_without_redis(self):
        """Test cache get when Redis is unavailable."""
        with patch('api.cache.response_cache.is_redis_available', return_value=False):
            cache = ResponseCache()
            result = cache.get("/api/v1/historical")
            
            assert result is None
    
    def test_get_cache_hit(self):
        """Test cache get with cache hit."""
        mock_client = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_client.client = mock_client
        mock_redis_client.is_available = True
        
        cached_data = {"commodity": "WTI", "data": []}
        mock_client.get.return_value = json.dumps(cached_data)
        
        with patch('api.cache.response_cache.is_redis_available', return_value=True):
            with patch('api.cache.response_cache.get_redis_client', return_value=mock_redis_client):
                cache = ResponseCache(redis_client=mock_redis_client)
                result = cache.get("/api/v1/historical")
                
                assert result == cached_data
                mock_client.get.assert_called_once()
    
    def test_get_cache_miss(self):
        """Test cache get with cache miss."""
        mock_client = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_client.client = mock_client
        mock_redis_client.is_available = True
        
        mock_client.get.return_value = None
        
        with patch('api.cache.response_cache.is_redis_available', return_value=True):
            with patch('api.cache.response_cache.get_redis_client', return_value=mock_redis_client):
                cache = ResponseCache(redis_client=mock_redis_client)
                result = cache.get("/api/v1/historical")
                
                assert result is None
    
    def test_set_cache(self):
        """Test cache set."""
        mock_client = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_client.client = mock_client
        mock_redis_client.is_available = True
        
        data = {"commodity": "WTI", "data": []}
        
        with patch('api.cache.response_cache.is_redis_available', return_value=True):
            with patch('api.cache.response_cache.get_redis_client', return_value=mock_redis_client):
                cache = ResponseCache(redis_client=mock_redis_client)
                result = cache.set("/api/v1/historical", data, ttl=300)
                
                assert result is True
                mock_client.setex.assert_called_once()
                # Verify JSON serialization
                call_args = mock_client.setex.call_args
                assert call_args[0][0].startswith("cache:/api/v1/historical")
                assert call_args[0][1] == 300
                assert json.loads(call_args[0][2]) == data
    
    def test_delete_cache(self):
        """Test cache delete."""
        mock_client = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_client.client = mock_client
        mock_redis_client.is_available = True
        
        mock_client.delete.return_value = 1
        
        with patch('api.cache.response_cache.is_redis_available', return_value=True):
            with patch('api.cache.response_cache.get_redis_client', return_value=mock_redis_client):
                cache = ResponseCache(redis_client=mock_redis_client)
                result = cache.delete("/api/v1/historical")
                
                assert result is True
                mock_client.delete.assert_called_once()
    
    def test_clear_pattern(self):
        """Test clearing cache by pattern."""
        mock_client = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_client.client = mock_client
        mock_redis_client.is_available = True
        
        mock_client.keys.return_value = [b"cache:/api/v1/historical:abc123", b"cache:/api/v1/historical:def456"]
        mock_client.delete.return_value = 2
        
        with patch('api.cache.response_cache.is_redis_available', return_value=True):
            with patch('api.cache.response_cache.get_redis_client', return_value=mock_redis_client):
                cache = ResponseCache(redis_client=mock_redis_client)
                result = cache.clear_pattern("cache:/api/v1/historical:*")
                
                assert result == 2
                mock_client.keys.assert_called_once_with("cache:/api/v1/historical:*")
                mock_client.delete.assert_called_once()
    
    def test_get_response_cache_singleton(self):
        """Test get_response_cache returns singleton instance."""
        # Clear global singleton
        import api.cache.response_cache
        api.cache.response_cache._response_cache = None
        
        cache1 = get_response_cache(default_ttl=300)
        cache2 = get_response_cache(default_ttl=300)
        
        assert cache1 is cache2
        assert cache1.default_ttl == 300

