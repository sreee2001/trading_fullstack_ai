"""
Authentication module for Energy Price Forecasting API.

This package provides:
- API key generation and management
- API key validation
- Authentication middleware
"""

from api.auth.api_key_manager import (
    APIKeyManager,
    get_api_key_manager,
    generate_api_key,
    hash_api_key,
    verify_api_key_hash
)
from api.auth.middleware import APIKeyAuth, get_api_key_auth

__all__ = [
    "APIKeyManager",
    "get_api_key_manager",
    "generate_api_key",
    "hash_api_key",
    "verify_api_key_hash",
    "APIKeyAuth",
    "get_api_key_auth",
]

