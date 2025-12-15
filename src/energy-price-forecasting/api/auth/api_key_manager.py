"""
API Key Manager.

This module provides functions for generating, storing, and validating API keys.
"""

import secrets
import hashlib
from typing import Optional, Tuple
from datetime import datetime, timedelta

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    bcrypt = None

from api.logging_config import get_logger
from database.models import APIKey
from database.utils import get_session

logger = get_logger(__name__)


def generate_api_key(prefix: str = "epf_") -> str:
    """
    Generate a cryptographically secure API key.
    
    Args:
        prefix: Prefix for the key (default: "epf_")
        
    Returns:
        API key string (format: prefix + random string)
        
    Example:
        >>> key = generate_api_key()
        >>> print(key)  # "epf_a1b2c3d4e5f6..."
    """
    # Generate 32 bytes of random data (256 bits)
    random_bytes = secrets.token_bytes(32)
    # Convert to hex string (64 characters)
    random_hex = random_bytes.hex()
    
    api_key = f"{prefix}{random_hex}"
    
    logger.info(f"Generated API key with prefix: {prefix}")
    return api_key


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key using bcrypt.
    
    Args:
        api_key: Plain text API key
        
    Returns:
        Bcrypt hash string
        
    Raises:
        ImportError: If bcrypt is not installed
    """
    if not BCRYPT_AVAILABLE:
        # Fallback to SHA-256 if bcrypt not available (less secure, but works)
        logger.warning("bcrypt not available, using SHA-256 hash (less secure)")
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    # Use bcrypt with cost factor 12 (good balance of security and performance)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(api_key.encode('utf-8'), salt)
    
    return hashed.decode('utf-8')


def verify_api_key_hash(api_key: str, key_hash: str) -> bool:
    """
    Verify an API key against its hash.
    
    Args:
        api_key: Plain text API key
        key_hash: Stored hash
        
    Returns:
        True if key matches hash, False otherwise
    """
    if not BCRYPT_AVAILABLE:
        # Fallback to SHA-256 verification
        expected_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return expected_hash == key_hash
    
    try:
        return bcrypt.checkpw(api_key.encode('utf-8'), key_hash.encode('utf-8'))
    except Exception as e:
        logger.error(f"Error verifying API key hash: {e}")
        return False


class APIKeyManager:
    """
    Manager for API key operations.
    
    Provides:
    - Generate and store API keys
    - Validate API keys
    - Revoke API keys
    - Track key usage
    """
    
    def __init__(self):
        """Initialize API key manager."""
        logger.info("APIKeyManager initialized")
    
    def create_api_key(
        self,
        user_id: Optional[str] = None,
        name: Optional[str] = None,
        expires_in_days: Optional[int] = None
    ) -> Tuple[str, int]:
        """
        Create a new API key.
        
        Args:
            user_id: Optional user identifier
            name: Optional name/description for the key
            expires_in_days: Optional expiration in days (None = no expiration)
            
        Returns:
            Tuple of (plain_text_key, key_id)
            
        Note:
            The plain text key is returned ONCE and should be stored securely
            by the user. It cannot be retrieved later.
        """
        # Generate API key
        api_key = generate_api_key()
        
        # Hash the key
        key_hash = hash_api_key(api_key)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        # Store in database
        with get_session() as session:
            api_key_record = APIKey(
                key_hash=key_hash,
                user_id=user_id,
                name=name,
                expires_at=expires_at,
                is_active=True
            )
            session.add(api_key_record)
            session.commit()
            session.refresh(api_key_record)
            
            key_id = api_key_record.id
            logger.info(f"Created API key (ID: {key_id}) for user: {user_id}")
            
            return api_key, key_id
    
    def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """
        Validate an API key.
        
        Args:
            api_key: Plain text API key
            
        Returns:
            APIKey record if valid, None otherwise
        """
        # Hash the provided key
        key_hash = hash_api_key(api_key)
        
        # Search for matching hash in database
        with get_session() as session:
            # Note: We need to check all keys since we can't reverse the hash
            # In production, you might want to add a lookup table or use a different approach
            # For now, we'll iterate through active keys (not ideal for large datasets)
            api_key_records = session.query(APIKey).filter(
                APIKey.is_active == True
            ).all()
            
            for record in api_key_records:
                if verify_api_key_hash(api_key, record.key_hash):
                    # Check expiration
                    if record.expires_at and record.expires_at < datetime.now():
                        logger.warning(f"API key expired (ID: {record.id})")
                        return None
                    
                    # Update last_used_at
                    record.last_used_at = datetime.now()
                    session.commit()
                    
                    logger.debug(f"API key validated (ID: {record.id})")
                    return record
            
            logger.warning("API key validation failed: key not found or invalid")
            return None
    
    def revoke_api_key(self, key_id: int) -> bool:
        """
        Revoke an API key by setting is_active=False.
        
        Args:
            key_id: API key ID
            
        Returns:
            True if revoked successfully, False otherwise
        """
        with get_session() as session:
            api_key_record = session.query(APIKey).filter(
                APIKey.id == key_id
            ).first()
            
            if not api_key_record:
                logger.warning(f"API key not found (ID: {key_id})")
                return False
            
            api_key_record.is_active = False
            session.commit()
            
            logger.info(f"API key revoked (ID: {key_id})")
            return True
    
    def get_api_key(self, key_id: int) -> Optional[APIKey]:
        """
        Get API key record by ID.
        
        Args:
            key_id: API key ID
            
        Returns:
            APIKey record or None
        """
        with get_session() as session:
            return session.query(APIKey).filter(APIKey.id == key_id).first()
    
    def list_api_keys(
        self,
        user_id: Optional[str] = None,
        active_only: bool = True
    ) -> list[APIKey]:
        """
        List API keys.
        
        Args:
            user_id: Optional user ID filter
            active_only: Whether to return only active keys
            
        Returns:
            List of APIKey records
        """
        with get_session() as session:
            query = session.query(APIKey)
            
            if user_id:
                query = query.filter(APIKey.user_id == user_id)
            
            if active_only:
                query = query.filter(APIKey.is_active == True)
            
            return query.all()


# Global manager instance (singleton)
_api_key_manager: Optional[APIKeyManager] = None


def get_api_key_manager() -> APIKeyManager:
    """
    Get the global API key manager instance.
    
    Returns:
        APIKeyManager instance
    """
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager

