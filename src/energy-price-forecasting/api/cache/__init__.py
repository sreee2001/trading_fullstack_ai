"""
Cache module for Energy Price Forecasting API.

This package provides:
- Redis connection management
- Rate limiting
- Response caching
"""

from api.cache.redis_client import (
    get_redis_client,
    RedisClient,
    is_redis_available
)

__all__ = [
    "get_redis_client",
    "RedisClient",
    "is_redis_available",
]

