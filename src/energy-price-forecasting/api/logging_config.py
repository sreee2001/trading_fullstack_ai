"""
Logging Configuration for Energy Price Forecasting API.

This module provides logging setup with file and console handlers,
structured logging format, and request/response middleware.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json

from api.config import get_settings


def setup_logging(log_file: Optional[str] = None, log_level: str = "INFO") -> None:
    """
    Configure Python logging for the application.
    
    Sets up:
    - Console handler with formatted output
    - File handler (if log_file provided)
    - Structured logging format
    - Configurable log level
    
    Args:
        log_file: Optional path to log file. If None, logs only to console.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Get numeric log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if log_file provided)
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set levels for third-party loggers to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def setup_api_logging() -> None:
    """
    Setup logging for the API using settings from config.
    
    This should be called during application startup.
    """
    settings = get_settings()
    setup_logging(
        log_file=settings.log_file,
        log_level=settings.log_level
    )
    
    logger = get_logger(__name__)
    logger.info(f"Logging configured - Level: {settings.log_level}")
    if settings.log_file:
        logger.info(f"Log file: {settings.log_file}")


from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time


class RequestResponseLogger(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    
    Logs:
    - Request method, path, query parameters
    - Request processing time
    - Response status code
    - Error details (if any)
    """
    
    def __init__(self, app, logger_name: str = "api.middleware"):
        """
        Initialize request/response logger middleware.
        
        Args:
            app: FastAPI application instance
            logger_name: Name for the logger
        """
        super().__init__(app)
        self.logger = get_logger(logger_name)
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and log details.
        
        Args:
            request: Starlette request object
            call_next: Callable to proceed to next middleware
            
        Returns:
            Response object
        """
        # Extract request information
        method = request.method
        path = request.url.path
        query_string = str(request.url.query)
        
        # Start time for duration calculation
        start_time = time.time()
        
        # Log request
        if query_string:
            self.logger.info(f"Request: {method} {path}?{query_string}")
        else:
            self.logger.info(f"Request: {method} {path}")
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            self.logger.error(f"Request failed: {method} {path} - {str(e)}", exc_info=True)
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            if status_code:
                if status_code >= 500:
                    self.logger.error(
                        f"Response: {method} {path} - {status_code} "
                        f"({duration:.3f}s)"
                    )
                elif status_code >= 400:
                    self.logger.warning(
                        f"Response: {method} {path} - {status_code} "
                        f"({duration:.3f}s)"
                    )
                else:
                    self.logger.info(
                        f"Response: {method} {path} - {status_code} "
                        f"({duration:.3f}s)"
                    )
        
        return response

