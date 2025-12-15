"""
Configuration Management for Energy Price Forecasting API.

This module provides Pydantic Settings for managing environment variables
and application configuration.
"""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses pydantic-settings to load from .env file and environment variables.
    Environment variables take precedence over .env file values.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )
    
    # Application Settings
    app_name: str = Field(default="Energy Price Forecasting API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    
    # Database Settings
    database_url: Optional[str] = Field(
        default=None,
        alias="DATABASE_URL",
        description="Full database connection URL"
    )
    db_host: Optional[str] = Field(
        default="localhost",
        alias="DB_HOST",
        description="Database host"
    )
    db_port: int = Field(
        default=5432,
        ge=1,
        le=65535,
        alias="DB_PORT",
        description="Database port"
    )
    db_name: Optional[str] = Field(
        default="energy_forecasting",
        alias="DB_NAME",
        description="Database name"
    )
    db_user: Optional[str] = Field(
        default="energy_user",
        alias="DB_USER",
        description="Database user"
    )
    db_password: Optional[str] = Field(
        default=None,
        alias="DB_PASSWORD",
        description="Database password"
    )
    db_pool_size: int = Field(
        default=5,
        ge=1,
        alias="DB_POOL_SIZE",
        description="Database connection pool size"
    )
    db_max_overflow: int = Field(
        default=10,
        ge=0,
        alias="DB_MAX_OVERFLOW",
        description="Database connection pool max overflow"
    )
    
    # API Keys
    eia_api_key: Optional[str] = Field(
        default=None,
        alias="EIA_API_KEY",
        description="EIA API key"
    )
    fred_api_key: Optional[str] = Field(
        default=None,
        alias="FRED_API_KEY",
        description="FRED API key"
    )
    
    # Security
    secret_key: Optional[str] = Field(
        default=None,
        alias="SECRET_KEY",
        description="Secret key for JWT/session management"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_file: Optional[str] = Field(
        default=None,
        alias="LOG_FILE",
        description="Log file path (optional, logs to console if not set)"
    )
    
    # Redis (Optional, for caching and rate limiting)
    redis_host: Optional[str] = Field(
        default=None,
        alias="REDIS_HOST",
        description="Redis host"
    )
    redis_port: int = Field(
        default=6379,
        ge=1,
        le=65535,
        alias="REDIS_PORT",
        description="Redis port"
    )
    redis_db: int = Field(
        default=0,
        ge=0,
        alias="REDIS_DB",
        description="Redis database number"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"LOG_LEVEL must be one of {allowed_levels}, got {v}")
        return v_upper
    
    def get_database_url(self) -> str:
        """
        Get the database URL, constructing it from components if not provided.
        
        Returns:
            Database connection URL string
            
        Raises:
            ValueError: If required database settings are missing
        """
        if self.database_url:
            return self.database_url
        
        # Construct URL from components
        if not all([self.db_host, self.db_name, self.db_user]):
            raise ValueError(
                "Database configuration incomplete. Provide either DATABASE_URL "
                "or DB_HOST, DB_NAME, and DB_USER"
            )
        
        password_part = f":{self.db_password}" if self.db_password else ""
        return f"postgresql+psycopg://{self.db_user}{password_part}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    def is_redis_configured(self) -> bool:
        """Check if Redis is configured."""
        return self.redis_host is not None
    
    def get_redis_url(self) -> Optional[str]:
        """Get Redis connection URL if configured."""
        if not self.is_redis_configured():
            return None
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


# Global settings instance
# This will be initialized when the module is imported
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Creates a new instance if one doesn't exist (singleton pattern).
    
    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """
    Reload settings from environment variables.
    
    Useful for testing or when environment variables change.
    
    Returns:
        New Settings instance
    """
    global _settings
    _settings = Settings()
    return _settings

