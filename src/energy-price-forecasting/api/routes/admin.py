"""
Admin routes for API key management.

Story 4.6.4: Implement API Key Revocation
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from api.logging_config import get_logger
from api.auth.api_key_manager import get_api_key_manager
from database.models import APIKey

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


class APIKeyCreateRequest(BaseModel):
    """Request model for creating an API key."""
    user_id: str = Field(None, description="User identifier")
    name: str = Field(None, description="Name/description for the key")
    expires_in_days: int = Field(None, description="Expiration in days (None = no expiration)")


class APIKeyCreateResponse(BaseModel):
    """Response model for creating an API key."""
    api_key: str = Field(..., description="Plain text API key (returned once)")
    key_id: int = Field(..., description="API key ID")
    message: str = Field(..., description="Success message")


class APIKeyInfo(BaseModel):
    """API key information (without hash)."""
    id: int
    user_id: Optional[str] = None
    name: Optional[str] = None
    created_at: str
    expires_at: Optional[str] = None
    is_active: bool
    last_used_at: Optional[str] = None


class APIKeyListResponse(BaseModel):
    """Response model for listing API keys."""
    keys: List[APIKeyInfo]
    total_count: int


@router.post("/keys", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(request: APIKeyCreateRequest):
    """
    Create a new API key.
    
    **Note**: The plain text key is returned ONCE and should be stored securely.
    It cannot be retrieved later.
    """
    manager = get_api_key_manager()
    
    try:
        api_key, key_id = manager.create_api_key(
            user_id=request.user_id,
            name=request.name,
            expires_in_days=request.expires_in_days
        )
        
        logger.info(f"API key created via admin endpoint (ID: {key_id})")
        
        return APIKeyCreateResponse(
            api_key=api_key,
            key_id=key_id,
            message="API key created successfully. Store it securely - it cannot be retrieved later."
        )
    except Exception as e:
        logger.error(f"Error creating API key: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API key: {str(e)}"
        )


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key(key_id: int):
    """
    Revoke an API key by setting is_active=False.
    
    Args:
        key_id: API key ID to revoke
    """
    manager = get_api_key_manager()
    
    success = manager.revoke_api_key(key_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key not found (ID: {key_id})"
        )
    
    logger.info(f"API key revoked via admin endpoint (ID: {key_id})")
    return None


@router.get("/keys", response_model=APIKeyListResponse)
def list_api_keys(user_id: str = None, active_only: bool = True):
    """
    List API keys.
    
    Args:
        user_id: Optional user ID filter
        active_only: Whether to return only active keys
    """
    manager = get_api_key_manager()
    
    keys = manager.list_api_keys(user_id=user_id, active_only=active_only)
    
    key_infos = [
        APIKeyInfo(
            id=k.id,
            user_id=k.user_id,
            name=k.name,
            created_at=k.created_at.isoformat() if k.created_at else None,
            expires_at=k.expires_at.isoformat() if k.expires_at else None,
            is_active=k.is_active,
            last_used_at=k.last_used_at.isoformat() if k.last_used_at else None,
        )
        for k in keys
    ]
    
    return APIKeyListResponse(keys=key_infos, total_count=len(key_infos))


@router.get("/keys/{key_id}", response_model=APIKeyInfo)
def get_api_key(key_id: int):
    """
    Get API key information by ID.
    
    Args:
        key_id: API key ID
    """
    manager = get_api_key_manager()
    
    key = manager.get_api_key(key_id)
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key not found (ID: {key_id})"
        )
    
    return APIKeyInfo(
        id=key.id,
        user_id=key.user_id,
        name=key.name,
        created_at=key.created_at.isoformat() if key.created_at else None,
        expires_at=key.expires_at.isoformat() if key.expires_at else None,
        is_active=key.is_active,
        last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
    )

