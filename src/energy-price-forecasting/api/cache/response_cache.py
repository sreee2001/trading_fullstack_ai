"""
Response Caching for API endpoints.

This module provides response caching functionality using Redis to cache
GET endpoint responses with configurable TTL.
"""

import json
import hashlib
from typing import Optional, Any
from datetime import timedelta

from api.logging_config import get_logger
from api.cache.redis_client import get_redis_client, is_redis_available

logger = get_logger(__name__)


class ResponseCache:
    """
    Response cache using Redis.
    
    Caches GET endpoint responses with configurable TTL per endpoint.
    """
    
    def __init__(
        self,
        redis_client: Optional[object] = None,
        default_ttl: int = 300  # 5 minutes default
    ):
        """
        Initialize response cache.
        
        Args:
            redis_client: Optional Redis client (uses global client if not provided)
            default_ttl: Default TTL in seconds (default: 300 = 5 minutes)
        """
        self.redis_client = redis_client or get_redis_client()
        self.default_ttl = default_ttl
        logger.info(f"ResponseCache initialized (default TTL: {default_ttl}s)")
    
    def _generate_cache_key(
        self,
        endpoint: str,
        query_params: dict = None
    ) -> str:
        """
        Generate cache key from endpoint and query parameters.
        
        Args:
            endpoint: API endpoint path
            query_params: Query parameters dictionary
            
        Returns:
            Cache key string
        """
        # Normalize endpoint (remove trailing slashes)
        endpoint = endpoint.rstrip('/')
        
        # Create key components
        key_parts = [f"cache:{endpoint}"]
        
        if query_params:
            # Sort params for consistent key generation
            sorted_params = sorted(query_params.items())
            params_str = json.dumps(sorted_params, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()
            key_parts.append(params_hash)
        
        return ":".join(key_parts)
    
    def get(
        self,
        endpoint: str,
        query_params: dict = None
    ) -> Optional[Any]:
        """
        Get cached response for an endpoint.
        
        Args:
            endpoint: API endpoint path
            query_params: Query parameters dictionary
            
        Returns:
            Cached response data (JSON deserialized) or None if not found
        """
        if not is_redis_available():
            logger.debug("Redis not available, cache miss")
            return None
        
        cache_key = self._generate_cache_key(endpoint, query_params)
        
        try:
            client = self.redis_client.client
            if not client:
                return None
            
            cached_data = client.get(cache_key)
            
            if cached_data:
                logger.debug(f"Cache hit for {endpoint}")
                return json.loads(cached_data)
            else:
                logger.debug(f"Cache miss for {endpoint}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting cache for {endpoint}: {e}")
            return None
    
    def set(
        self,
        endpoint: str,
        data: Any,
        ttl: Optional[int] = None,
        query_params: dict = None
    ) -> bool:
        """
        Cache response for an endpoint.
        
        Args:
            endpoint: API endpoint path
            data: Response data to cache (will be JSON serialized)
            ttl: TTL in seconds (uses default if None)
            query_params: Query parameters dictionary
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not is_redis_available():
            logger.debug("Redis not available, skipping cache")
            return False
        
        cache_key = self._generate_cache_key(endpoint, query_params)
        ttl = ttl or self.default_ttl
        
        try:
            client = self.redis_client.client
            if not client:
                return False
            
            # Serialize data to JSON
            json_data = json.dumps(data, default=str)  # default=str handles datetime, etc.
            
            # Store in Redis with TTL
            client.setex(cache_key, ttl, json_data)
            
            logger.debug(f"Cached response for {endpoint} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error caching response for {endpoint}: {e}")
            return False
    
    def delete(
        self,
        endpoint: str,
        query_params: dict = None
    ) -> bool:
        """
        Delete cached response for an endpoint.
        
        Args:
            endpoint: API endpoint path
            query_params: Query parameters dictionary
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if not is_redis_available():
            return False
        
        cache_key = self._generate_cache_key(endpoint, query_params)
        
        try:
            client = self.redis_client.client
            if not client:
                return False
            
            deleted = client.delete(cache_key)
            logger.debug(f"Deleted cache for {endpoint}")
            return deleted > 0
            
        except Exception as e:
            logger.error(f"Error deleting cache for {endpoint}: {e}")
            return False
    
    def clear_pattern(
        self,
        pattern: str
    ) -> int:
        """
        Clear all cache keys matching a pattern.
        
        Args:
            pattern: Redis key pattern (e.g., "cache:/api/v1/historical:*")
            
        Returns:
            Number of keys deleted
        """
        if not is_redis_available():
            return 0
        
        try:
            client = self.redis_client.client
            if not client:
                return 0
            
            # Find all keys matching pattern
            keys = client.keys(pattern)
            
            if keys:
                deleted = client.delete(*keys)
                logger.info(f"Cleared {deleted} cache keys matching pattern: {pattern}")
                return deleted
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0


# Global response cache instance (singleton)
_response_cache: Optional[ResponseCache] = None


def get_response_cache(default_ttl: int = 300) -> ResponseCache:
    """
    Get the global response cache instance.
    
    Args:
        default_ttl: Default TTL in seconds (default: 300)
        
    Returns:
        ResponseCache instance
    """
    global _response_cache
    if _response_cache is None or _response_cache.default_ttl != default_ttl:
        _response_cache = ResponseCache(default_ttl=default_ttl)
    return _response_cache

