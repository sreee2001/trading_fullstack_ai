"""
Health check and monitoring endpoints.

This module implements health check endpoints for monitoring API availability
and component status.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status

from api.logging_config import get_logger
from api.lifecycle import get_database_manager, get_ml_models
from api.cache.redis_client import is_redis_available

logger = get_logger(__name__)

router = APIRouter(prefix="", tags=["Health"])


@router.get(
    "/health",
    summary="Basic Health Check",
    description="""
    Simple liveness check endpoint.
    
    Returns 200 if the API is running and responding to requests.
    This endpoint does not check component availability - use `/ready` for that.
    
    **Use Cases:**
    - Load balancer health checks
    - Container orchestration liveness probes
    - Basic API availability monitoring
    
    **Response:**
    - `200 OK`: API is running
    - Always returns healthy (no authentication required)
    """,
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "healthy"}
                }
            }
        }
    }
)
def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.
    
    Returns:
        Dictionary with health status
    """
    return {"status": "healthy"}


@router.get(
    "/ready",
    summary="Readiness Check",
    description="""
    Detailed readiness check endpoint.
    
    Checks the availability of all critical components:
    - Database connectivity
    - Redis connectivity (if configured)
    - ML models availability (if preloaded)
    
    **Use Cases:**
    - Kubernetes readiness probes
    - Deployment verification
    - Component health monitoring
    
    **Response:**
    - `200 OK`: All components are ready
    - `503 Service Unavailable`: One or more components are not ready
    
    **Component Status:**
    - `database`: Database connection status
    - `redis`: Redis connection status (optional)
    - `models`: ML models availability status
    """,
    responses={
        200: {
            "description": "All components are ready",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ready",
                        "components": {
                            "database": "healthy",
                            "redis": "healthy",
                            "models": "available"
                        }
                    }
                }
            }
        },
        503: {
            "description": "One or more components are not ready",
            "content": {
                "application/json": {
                    "example": {
                        "status": "not_ready",
                        "components": {
                            "database": "unhealthy",
                            "redis": "healthy",
                            "models": "available"
                        }
                    }
                }
            }
        }
    }
)
def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint.
    
    Checks the availability of critical components:
    - Database connection
    - Redis connection (if configured)
    - ML models (if preloaded)
    
    Returns:
        Dictionary with readiness status and component health
        
    Raises:
        HTTPException: 503 if not ready
    """
    components = {}
    all_ready = True
    
    # Check database
    try:
        db_manager = get_database_manager()
        if db_manager:
            db_manager.verify_connection()
            components["database"] = "healthy"
        else:
            components["database"] = "not_configured"
            # Database not configured is acceptable (some features won't work)
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        components["database"] = "unhealthy"
        all_ready = False
    
    # Check Redis (optional)
    try:
        if is_redis_available():
            components["redis"] = "healthy"
        else:
            components["redis"] = "not_configured"
            # Redis not configured is acceptable (caching/rate limiting disabled)
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        components["redis"] = "unhealthy"
        # Redis is optional, so don't fail readiness if it's down
    
    # Check ML models (optional)
    try:
        ml_models = get_ml_models()
        if ml_models:
            components["models"] = "available"
        else:
            components["models"] = "lazy_loading"
            # Models loaded on-demand is acceptable
    except Exception as e:
        logger.warning(f"Models health check failed: {e}")
        components["models"] = "unavailable"
        # Models are optional (loaded on-demand), so don't fail readiness
    
    # Determine overall readiness
    # Database is critical, Redis and models are optional
    if components.get("database") == "healthy":
        status_code = status.HTTP_200_OK
        status_message = "ready"
    else:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        status_message = "not_ready"
        all_ready = False
    
    response = {
        "status": status_message,
        "components": components
    }
    
    if status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        # Return 503 with response body (not using HTTPException to preserve response structure)
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=status_code, content=response)
    
    return response

