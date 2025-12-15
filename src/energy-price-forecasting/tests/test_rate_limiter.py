"""
Unit tests for rate limiter (Story 4.7.2).
"""

import pytest
import time
from unittest.mock import patch, MagicMock

from api.cache.rate_limiter import RateLimiter, get_rate_limiter
from api.cache.redis_client import RedisClient


class TestRateLimiter:
    """Test rate limiter functionality."""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(requests_per_minute=100)
        assert limiter.requests_per_minute == 100
        assert limiter.redis_client is not None
    
    def test_is_allowed_without_redis(self):
        """Test rate limiter allows requests when Redis is unavailable."""
        with patch('api.cache.rate_limiter.is_redis_available', return_value=False):
            limiter = RateLimiter(requests_per_minute=100)
            is_allowed, retry_after = limiter.is_allowed("test_key")
            
            assert is_allowed is True
            assert retry_after is None
    
    def test_is_allowed_with_redis(self):
        """Test rate limiter with Redis available."""
        mock_client = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_client.client = mock_client
        mock_redis_client.is_available = True
        
        # Mock Redis pipeline operations
        mock_pipe = MagicMock()
        mock_client.pipeline.return_value = mock_pipe
        mock_pipe.execute.return_value = [None, 50, None, None]  # current_count = 50
        
        with patch('api.cache.rate_limiter.is_redis_available', return_value=True):
            with patch('api.cache.rate_limiter.get_redis_client', return_value=mock_redis_client):
                limiter = RateLimiter(requests_per_minute=100, redis_client=mock_redis_client)
                is_allowed, retry_after = limiter.is_allowed("test_key")
                
                assert is_allowed is True
                assert retry_after is None
                mock_pipe.execute.assert_called_once()
    
    def test_is_allowed_rate_limit_exceeded(self):
        """Test rate limiter when limit is exceeded."""
        mock_client = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_client.client = mock_client
        mock_redis_client.is_available = True
        
        # Mock Redis pipeline operations - count = 100 (limit exceeded)
        mock_pipe = MagicMock()
        mock_client.pipeline.return_value = mock_pipe
        mock_pipe.execute.return_value = [None, 100, None, None]  # current_count = 100
        
        # Mock zrange for retry_after calculation
        current_time = int(time.time())
        mock_client.zrange.return_value = [(b"timestamp", current_time - 30)]
        
        with patch('api.cache.rate_limiter.is_redis_available', return_value=True):
            with patch('api.cache.rate_limiter.get_redis_client', return_value=mock_redis_client):
                limiter = RateLimiter(requests_per_minute=100, redis_client=mock_redis_client)
                is_allowed, retry_after = limiter.is_allowed("test_key")
                
                assert is_allowed is False
                assert retry_after is not None
                assert retry_after > 0
    
    def test_get_remaining_requests(self):
        """Test getting remaining requests."""
        mock_client = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_client.client = mock_client
        mock_redis_client.is_available = True
        
        mock_client.zremrangebyscore.return_value = 0
        mock_client.zcard.return_value = 50  # 50 requests used
        
        with patch('api.cache.rate_limiter.is_redis_available', return_value=True):
            with patch('api.cache.rate_limiter.get_redis_client', return_value=mock_redis_client):
                limiter = RateLimiter(requests_per_minute=100, redis_client=mock_redis_client)
                remaining = limiter.get_remaining_requests("test_key")
                
                assert remaining == 50  # 100 - 50 = 50 remaining
    
    def test_get_remaining_requests_without_redis(self):
        """Test getting remaining requests when Redis is unavailable."""
        with patch('api.cache.rate_limiter.is_redis_available', return_value=False):
            limiter = RateLimiter(requests_per_minute=100)
            remaining = limiter.get_remaining_requests("test_key")
            
            assert remaining is None
    
    def test_get_rate_limiter_singleton(self):
        """Test get_rate_limiter returns singleton instance."""
        # Clear global singleton
        import api.cache.rate_limiter
        api.cache.rate_limiter._rate_limiter = None
        
        limiter1 = get_rate_limiter(requests_per_minute=100)
        limiter2 = get_rate_limiter(requests_per_minute=100)
        
        assert limiter1 is limiter2
        assert limiter1.requests_per_minute == 100
    
    def test_get_rate_limiter_different_limits(self):
        """Test get_rate_limiter creates new instance for different limits."""
        # Clear global singleton
        import api.cache.rate_limiter
        api.cache.rate_limiter._rate_limiter = None
        
        limiter1 = get_rate_limiter(requests_per_minute=100)
        limiter2 = get_rate_limiter(requests_per_minute=200)
        
        assert limiter1 is not limiter2
        assert limiter1.requests_per_minute == 100
        assert limiter2.requests_per_minute == 200


class TestRateLimitMiddleware:
    """Test rate limiting middleware."""
    
    # Note: Async middleware tests are covered by integration tests
    # The middleware functionality is tested through actual endpoint calls using TestClient
    # These tests verify the middleware structure and configuration

