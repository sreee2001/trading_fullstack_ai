"""
Rate Limiting Middleware for FastAPI.

This module provides FastAPI middleware for rate limiting API requests
based on API key.
"""

from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from fastapi import status

from api.logging_config import get_logger
from api.cache.rate_limiter import get_rate_limiter

logger = get_logger(__name__)

# API key header name
API_KEY_HEADER = "X-API-Key"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting API requests.
    
    Checks rate limits based on API key from X-API-Key header.
    Returns 429 (Too Many Requests) if rate limit exceeded.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 100,
        exempt_paths: list[str] = None
    ):
        """
        Initialize rate limiting middleware.
        
        Args:
            app: ASGI application
            requests_per_minute: Maximum requests per minute per API key (default: 100)
            exempt_paths: List of path prefixes to exempt from rate limiting (e.g., ["/health", "/docs"])
        """
        super().__init__(app)
        self.rate_limiter = get_rate_limiter(requests_per_minute=requests_per_minute)
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/api/docs", "/api/redoc", "/api/openapi.json"]
        logger.info(f"RateLimitMiddleware initialized (limit: {requests_per_minute} req/min)")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and check rate limit.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
            
        Returns:
            HTTP response
        """
        # Check if path is exempt from rate limiting
        path = request.url.path
        if any(path.startswith(exempt) for exempt in self.exempt_paths):
            return await call_next(request)
        
        # Get API key from header
        api_key = request.headers.get(API_KEY_HEADER)
        
        if not api_key:
            # No API key - allow request (authentication middleware will handle it)
            return await call_next(request)
        
        # Check rate limit
        is_allowed, retry_after = self.rate_limiter.is_allowed(api_key)
        
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {request.method} {path} "
                f"(API key: {api_key[:8]}..., retry after: {retry_after}s)"
            )
            
            response = Response(
                content=f"Rate limit exceeded. Retry after {retry_after} seconds.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.rate_limiter.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                }
            )
            return response
        
        # Request allowed - proceed
        response = await call_next(request)
        
        # Add rate limit headers to response
        remaining = self.rate_limiter.get_remaining_requests(api_key)
        if remaining is not None:
            response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response

