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
from api.cache.rate_limiter import (
    RateLimiter,
    get_rate_limiter
)
from api.cache.rate_limit_middleware import RateLimitMiddleware
from api.cache.response_cache import (
    ResponseCache,
    get_response_cache
)

__all__ = [
    "get_redis_client",
    "RedisClient",
    "is_redis_available",
    "RateLimiter",
    "get_rate_limiter",
    "RateLimitMiddleware",
    "ResponseCache",
    "get_response_cache",
]

