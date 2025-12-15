"""
Redis Client for caching and rate limiting.

This module provides Redis connection management with graceful fallback
if Redis is unavailable.
"""

from typing import Optional
import logging

try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None
    redis = None

from api.config import get_settings
from api.logging_config import get_logger

logger = get_logger(__name__)


class RedisClient:
    """
    Redis client wrapper with connection management.
    
    Provides:
    - Connection initialization
    - Health checks
    - Graceful fallback if Redis unavailable
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        password: Optional[str] = None,
        url: Optional[str] = None
    ):
        """
        Initialize Redis client.
        
        Args:
            host: Redis host (default: from settings)
            port: Redis port (default: from settings)
            db: Redis database number (default: from settings)
            password: Redis password (default: from settings)
            url: Redis URL (alternative to host/port/db)
        """
        self.settings = get_settings()
        self._client: Optional[Redis] = None
        self._available = False
        
        # Use provided parameters or fall back to settings
        redis_host = host or self.settings.redis_host
        redis_port = port or self.settings.redis_port
        redis_db = db if db is not None else self.settings.redis_db
        redis_password = password or getattr(self.settings, 'redis_password', None)
        redis_url = url or getattr(self.settings, 'redis_url', None)
        
        if not REDIS_AVAILABLE:
            logger.warning("Redis library not installed. Redis features will be disabled.")
            return
        
        try:
            if redis_url:
                # Use Redis URL if provided
                self._client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            else:
                # Use host/port/db if URL not provided
                self._client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    password=redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            
            # Test connection
            self._client.ping()
            self._available = True
            logger.info(f"Redis client connected (host: {redis_host}, port: {redis_port}, db: {redis_db})")
            
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Redis features will be disabled.")
            self._client = None
            self._available = False
    
    @property
    def client(self) -> Optional[Redis]:
        """
        Get Redis client instance.
        
        Returns:
            Redis client or None if unavailable
        """
        return self._client
    
    @property
    def is_available(self) -> bool:
        """
        Check if Redis is available.
        
        Returns:
            True if Redis is connected, False otherwise
        """
        if not self._available or not self._client:
            return False
        
        try:
            self._client.ping()
            return True
        except Exception:
            self._available = False
            return False
    
    def ping(self) -> bool:
        """
        Ping Redis server to check connection.
        
        Returns:
            True if connection is alive, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            self._client.ping()
            return True
        except Exception as e:
            logger.warning(f"Redis ping failed: {e}")
            self._available = False
            return False
    
    def close(self):
        """Close Redis connection."""
        if self._client:
            try:
                self._client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {e}")
            finally:
                self._client = None
                self._available = False


# Global Redis client instance (singleton)
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """
    Get the global Redis client instance.
    
    Returns:
        RedisClient instance
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client


def is_redis_available() -> bool:
    """
    Check if Redis is available.
    
    Returns:
        True if Redis is connected and available, False otherwise
    """
    client = get_redis_client()
    return client.is_available

