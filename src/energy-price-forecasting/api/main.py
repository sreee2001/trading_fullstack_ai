"""
FastAPI Application Entry Point.

This module initializes the FastAPI application and configures
middleware, routes, and event handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging

from api.config import get_settings
from api.logging_config import setup_api_logging, get_logger

# Get application settings
settings = get_settings()

# Setup logging
setup_api_logging()

# Get logger for this module
logger = get_logger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Energy Price Forecasting API",
    description="REST API for energy price forecasting, historical data, and model management",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

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


@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring.
    
    Returns:
        Dictionary with health status
    """
    return {"status": "healthy"}


# Include API routes
from api.routes import forecast, historical, models, backtest, admin
app.include_router(forecast.router)
app.include_router(historical.router)
app.include_router(models.router)
app.include_router(backtest.router)
app.include_router(admin.router)


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

