"""
Authentication Middleware.

This module provides FastAPI middleware and dependencies for API key authentication.
"""

from typing import Optional
from datetime import datetime
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from api.logging_config import get_logger
from api.auth.api_key_manager import get_api_key_manager
from database.models import APIKey

logger = get_logger(__name__)

# API key header name
API_KEY_HEADER_NAME = "X-API-Key"

# Create API key header security scheme
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


class APIKeyAuth:
    """
    API Key Authentication dependency.
    
    Provides FastAPI dependency for protecting endpoints with API key authentication.
    """
    
    def __init__(self, required: bool = True):
        """
        Initialize API key authentication.
        
        Args:
            required: Whether API key is required (default: True)
        """
        self.required = required
        self.manager = get_api_key_manager()
        logger.info(f"APIKeyAuth initialized (required: {required})")
    
    async def __call__(
        self,
        api_key: Optional[str] = Security(api_key_header)
    ) -> Optional[APIKey]:
        """
        Validate API key from request header.
        
        Args:
            api_key: API key from X-API-Key header
            
        Returns:
            APIKey record if valid
            
        Raises:
            HTTPException: If authentication fails
        """
        if not self.required:
            # Authentication optional - return None if no key provided
            if not api_key:
                return None
        
        if not api_key:
            logger.warning("API key missing from request")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required. Provide X-API-Key header.",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        # Validate API key
        api_key_record = self.manager.validate_api_key(api_key)
        
        if not api_key_record:
            logger.warning("Invalid API key provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        # Check if key is active
        if not api_key_record.is_active:
            logger.warning(f"Inactive API key used (ID: {api_key_record.id})")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API key has been revoked",
            )
        
        # Check expiration
        if api_key_record.expires_at and api_key_record.expires_at < datetime.now():
            logger.warning(f"Expired API key used (ID: {api_key_record.id})")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API key has expired",
            )
        
        logger.debug(f"API key authenticated (ID: {api_key_record.id}, user: {api_key_record.user_id})")
        return api_key_record


# Global authentication instance (required by default)
_api_key_auth: Optional[APIKeyAuth] = None


def get_api_key_auth(required: bool = True) -> APIKeyAuth:
    """
    Get API key authentication dependency.
    
    Args:
        required: Whether API key is required (default: True)
        
    Returns:
        APIKeyAuth instance
    """
    global _api_key_auth
    if _api_key_auth is None or _api_key_auth.required != required:
        _api_key_auth = APIKeyAuth(required=required)
    return _api_key_auth

