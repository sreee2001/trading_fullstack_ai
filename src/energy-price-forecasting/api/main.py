"""
FastAPI Application Entry Point.

This module initializes the FastAPI application and configures
middleware, routes, and event handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from typing import Dict, Any
import logging

from api.config import get_settings
from api.logging_config import setup_api_logging, get_logger
from api.auth.middleware import API_KEY_HEADER_NAME

# Get application settings
settings = get_settings()

# Setup logging
setup_api_logging()

# Get logger for this module
logger = get_logger(__name__)

# Initialize FastAPI application with comprehensive OpenAPI metadata
app = FastAPI(
    title="Energy Price Forecasting API",
    description="""
    REST API for energy commodity price forecasting, historical data retrieval, and ML model management.
    
    ## Features
    
    * **Forecasting**: Generate price forecasts for WTI, BRENT, and Natural Gas commodities
    * **Historical Data**: Retrieve historical price data with pagination and filtering
    * **Model Management**: Query ML model metadata and performance metrics
    * **Backtesting**: Run backtests on forecasting models with custom trading strategies
    * **API Key Authentication**: Secure access with API key-based authentication
    * **Rate Limiting**: 100 requests per minute per API key
    
    ## Authentication
    
    Most endpoints require an API key. Include it in the `X-API-Key` header:
    
    ```
    X-API-Key: epf_your_api_key_here
    ```
    
    To obtain an API key, contact the administrator or use the admin endpoints.
    """,
    version="1.0.0",
    contact={
        "name": "Energy Trading AI Team",
        "email": "support@energy-trading-ai.com",
        "url": "https://github.com/energy-trading-ai"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {
            "name": "Root",
            "description": "Root endpoint and API information"
        },
        {
            "name": "Health",
            "description": "Health check and monitoring endpoints"
        },
        {
            "name": "Forecast",
            "description": "Generate energy commodity price forecasts"
        },
        {
            "name": "Historical Data",
            "description": "Retrieve historical price data"
        },
        {
            "name": "Models",
            "description": "Query ML model metadata and performance metrics"
        },
        {
            "name": "Backtest",
            "description": "Run backtests on forecasting models"
        },
        {
            "name": "Admin",
            "description": "Administrative endpoints for API key management"
        },
        {
            "name": "WebSocket",
            "description": "WebSocket endpoints for real-time forecast updates"
        }
    ]
)

# Configure API Key security scheme for OpenAPI/Swagger UI
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

# Add security scheme to OpenAPI
app.openapi_schema = None  # Force regeneration

def custom_openapi():
    """Custom OpenAPI schema with security scheme."""
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": API_KEY_HEADER_NAME,
            "description": "API Key authentication. Get your API key from the admin endpoints."
        }
    }
    
    # Add security requirement to protected endpoints
    # (Endpoints using APIKeyAuth dependency will automatically require it)
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request/response logging middleware
from api.logging_config import RequestResponseLogger
app.add_middleware(RequestResponseLogger)

# Add rate limiting middleware
from api.cache.rate_limit_middleware import RateLimitMiddleware
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=100,
    exempt_paths=["/health", "/docs", "/api/docs", "/api/redoc", "/api/openapi.json"]
)

# Register startup and shutdown event handlers
from api.lifecycle import startup_event, shutdown_event

@app.on_event("startup")
async def startup():
    """Application startup event handler."""
    await startup_event()

@app.on_event("shutdown")
async def shutdown():
    """Application shutdown event handler."""
    await shutdown_event()

@app.get("/", tags=["Root"])
def root() -> Dict[str, Any]:
    """
    Root endpoint providing API information.
    
    Returns:
        Dictionary with API name and version
    """
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/api/docs",
    }


# Include API routes
from api.routes import forecast, historical, models, backtest, admin, health, websocket
app.include_router(forecast.router)
app.include_router(historical.router)
app.include_router(models.router)
app.include_router(backtest.router)
app.include_router(admin.router)
app.include_router(health.router)
app.include_router(websocket.router)


# Log application startup
logger.info("FastAPI application initialized")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

