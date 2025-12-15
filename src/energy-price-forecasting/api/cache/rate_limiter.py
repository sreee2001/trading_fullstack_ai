"""
Rate Limiting for API requests.

This module provides rate limiting functionality using Redis to track
requests per API key with a sliding window algorithm.
"""

from typing import Optional
import time
from fastapi import HTTPException, status

from api.logging_config import get_logger
from api.cache.redis_client import get_redis_client, is_redis_available

logger = get_logger(__name__)


class RateLimiter:
    """
    Rate limiter using Redis sliding window algorithm.
    
    Tracks requests per API key and enforces rate limits.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 100,
        redis_client: Optional[object] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute (default: 100)
            redis_client: Optional Redis client (uses global client if not provided)
        """
        self.requests_per_minute = requests_per_minute
        self.redis_client = redis_client or get_redis_client()
        logger.info(f"RateLimiter initialized (limit: {requests_per_minute} req/min)")
    
    def is_allowed(
        self,
        api_key: str,
        window_seconds: int = 60
    ) -> tuple[bool, Optional[int]]:
        """
        Check if a request is allowed for the given API key.
        
        Args:
            api_key: API key identifier
            window_seconds: Time window in seconds (default: 60 for 1 minute)
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
            - is_allowed: True if request is allowed, False if rate limit exceeded
            - retry_after_seconds: Seconds until next request is allowed (None if allowed)
        """
        if not is_redis_available():
            # If Redis is not available, allow all requests (graceful degradation)
            logger.debug("Redis not available, allowing request (rate limiting disabled)")
            return True, None
        
        redis_key = f"rate_limit:{api_key}"
        current_time = int(time.time())
        window_start = current_time - window_seconds
        
        try:
            client = self.redis_client.client
            if not client:
                logger.warning("Redis client not available, allowing request")
                return True, None
            
            # Use Redis pipeline for atomic operations
            pipe = client.pipeline()
            
            # Remove old entries outside the window
            pipe.zremrangebyscore(redis_key, 0, window_start)
            
            # Count current requests in the window
            pipe.zcard(redis_key)
            
            # Add current request timestamp
            pipe.zadd(redis_key, {str(current_time): current_time})
            
            # Set expiration on the key (slightly longer than window to avoid edge cases)
            pipe.expire(redis_key, window_seconds + 10)
            
            # Execute pipeline
            results = pipe.execute()
            
            current_count = results[1]  # Count before adding current request
            new_count = current_count + 1  # Count after adding current request
            
            if new_count > self.requests_per_minute:
                # Rate limit exceeded
                # Calculate retry_after: time until oldest request expires
                oldest_timestamp = client.zrange(redis_key, 0, 0, withscores=True)
                if oldest_timestamp:
                    oldest_time = int(oldest_timestamp[0][1])
                    retry_after = (oldest_time + window_seconds) - current_time + 1
                    retry_after = max(1, retry_after)  # At least 1 second
                else:
                    retry_after = 1
                
                logger.warning(
                    f"Rate limit exceeded for API key {api_key[:8]}... "
                    f"({new_count}/{self.requests_per_minute} requests)"
                )
                return False, retry_after
            
            logger.debug(
                f"Rate limit check passed for API key {api_key[:8]}... "
                f"({new_count}/{self.requests_per_minute} requests)"
            )
            return True, None
            
        except Exception as e:
            # On error, allow the request (fail open)
            logger.error(f"Error checking rate limit: {e}. Allowing request.")
            return True, None
    
    def get_remaining_requests(
        self,
        api_key: str,
        window_seconds: int = 60
    ) -> Optional[int]:
        """
        Get remaining requests for an API key in the current window.
        
        Args:
            api_key: API key identifier
            window_seconds: Time window in seconds (default: 60)
            
        Returns:
            Number of remaining requests, or None if Redis unavailable
        """
        if not is_redis_available():
            return None
        
        redis_key = f"rate_limit:{api_key}"
        current_time = int(time.time())
        window_start = current_time - window_seconds
        
        try:
            client = self.redis_client.client
            if not client:
                return None
            
            # Remove old entries and count current
            client.zremrangebyscore(redis_key, 0, window_start)
            count = client.zcard(redis_key)
            
            remaining = max(0, self.requests_per_minute - count)
            return remaining
            
        except Exception as e:
            logger.error(f"Error getting remaining requests: {e}")
            return None


# Global rate limiter instance (singleton)
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(requests_per_minute: int = 100) -> RateLimiter:
    """
    Get the global rate limiter instance.
    
    Args:
        requests_per_minute: Maximum requests per minute (default: 100)
        
    Returns:
        RateLimiter instance
    """
    global _rate_limiter
    if _rate_limiter is None or _rate_limiter.requests_per_minute != requests_per_minute:
        _rate_limiter = RateLimiter(requests_per_minute=requests_per_minute)
    return _rate_limiter

