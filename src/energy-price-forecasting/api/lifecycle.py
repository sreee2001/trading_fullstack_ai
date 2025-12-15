"""
Application Lifecycle Management for Energy Price Forecasting API.

This module handles startup and shutdown events for the FastAPI application,
including database connection pool initialization and cleanup.
"""

from typing import Optional
import logging

from api.config import get_settings
from api.logging_config import get_logger
from api.services.model_service import get_model_service
from api.cache.redis_client import get_redis_client

logger = get_logger(__name__)

# Global references to resources
_db_manager: Optional[object] = None
_ml_models: dict = {}
_redis_client: Optional[object] = None
_redis_client: Optional[object] = None


async def startup_event():
    """
    Startup event handler.
    
    Initializes:
    - Database connection pool
    - ML models (optional, lazy loading)
    - Other application resources
    """
    global _db_manager, _ml_models
    
    settings = get_settings()
    logger.info("Starting up Energy Price Forecasting API...")
    
    try:
        # Initialize database connection pool
        logger.info("Initializing database connection pool...")
        from database.utils import get_database_manager
        
        try:
            database_url = settings.get_database_url()
        except ValueError as e:
            logger.warning(f"Database URL not configured: {e}. Database features will be unavailable.")
            database_url = None
        
        if database_url:
            _db_manager = get_database_manager(
                database_url=database_url,
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_max_overflow,
                echo=settings.debug
            )
            
            # Test database connection
            try:
                _db_manager.verify_connection()
                logger.info("Database connection pool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to verify database connection: {e}")
                # Don't raise - allow app to start but log the error
                # In production, you might want to raise here
        else:
            logger.warning("Database URL not configured. Skipping database initialization.")
        
        # Preload ML models if configured
        if settings.preload_models_at_startup:
            logger.info("Preloading ML models...")
            model_service = get_model_service()
            model_service.preload_models(
                commodities=settings.preload_commodities if hasattr(settings, 'preload_commodities') else ["WTI", "BRENT", "NG"],
                model_types=settings.preload_model_types if hasattr(settings, 'preload_model_types') else ["lstm"]
            )
            _ml_models = model_service.get_cached_models()
        else:
            logger.info("ML models will be loaded on-demand")
            _ml_models = {}
        
        # Initialize Redis client
        logger.info("Initializing Redis client...")
        try:
            _redis_client = get_redis_client()
            if _redis_client.is_available:
                logger.info("Redis client initialized successfully")
            else:
                logger.warning("Redis is not available. Caching and rate limiting will be disabled.")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis client: {e}. Caching and rate limiting will be disabled.")
            _redis_client = None
        
        logger.info("Startup complete")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)
        # Re-raise to prevent app from starting with broken state
        raise


async def shutdown_event():
    """
    Shutdown event handler.
    
    Cleans up:
    - Database connection pool
    - ML models (if loaded)
    - Redis connection
    - Other application resources
    """
    global _db_manager, _ml_models, _redis_client
    
    logger.info("Shutting down Energy Price Forecasting API...")
    
    try:
        # Close database connection pool
        if _db_manager is not None:
            logger.info("Closing database connection pool...")
            try:
                _db_manager.close()
                logger.info("Database connection pool closed successfully")
            except Exception as e:
                logger.error(f"Error closing database connection pool: {e}")
            finally:
                _db_manager = None
        
        # Clear ML models from memory
        if _ml_models:
            logger.info("Clearing ML models from memory...")
            _ml_models.clear()
        
        # Close Redis connection
        if _redis_client:
            logger.info("Closing Redis connection...")
            try:
                _redis_client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                _redis_client = None
        
        logger.info("Shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)
        # Don't re-raise during shutdown - log and continue


def get_database_manager():
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager instance or None if not initialized
    """
    return _db_manager


def get_ml_models():
    """
    Get the loaded ML models dictionary.
    
    Returns:
        Dictionary of loaded ML models
    """
    return _ml_models

