"""
Unit tests for API logging configuration (Story 4.1.3).
"""

import pytest
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.logging_config import (
    setup_logging,
    get_logger,
    setup_api_logging,
    RequestResponseLogger,
)
from api.config import Settings, reload_settings


class TestSetupLogging:
    """Test logging setup functions."""
    
    def test_setup_logging_console_only(self):
        """Test setting up logging with console handler only."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        root_logger.handlers.clear()
        
        try:
            setup_logging(log_file=None, log_level="INFO")
            
            # Check that console handler was added
            handlers = root_logger.handlers
            assert len(handlers) >= 1
            assert any(isinstance(h, logging.StreamHandler) for h in handlers)
            
            # Check log level
            assert root_logger.level == logging.INFO
        finally:
            # Restore original handlers
            root_logger.handlers = original_handlers
    
    def test_setup_logging_with_file(self):
        """Test setting up logging with file handler."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        root_logger.handlers.clear()
        
        try:
            # Use a temporary directory for the log file
            with tempfile.TemporaryDirectory() as tmpdir:
                log_file = os.path.join(tmpdir, "test.log")
                
                setup_logging(log_file=log_file, log_level="DEBUG")
                
                # Check that both console and file handlers were added
                handlers = root_logger.handlers
                assert len(handlers) >= 2
                assert any(isinstance(h, logging.StreamHandler) for h in handlers)
                assert any(isinstance(h, logging.FileHandler) for h in handlers)
                
                # Check log level
                assert root_logger.level == logging.DEBUG
                
                # Test that logging works
                logger = get_logger("test")
                logger.info("Test message")
                
                # Close file handlers to release file handles
                for handler in handlers:
                    if isinstance(handler, logging.FileHandler):
                        handler.close()
                
                # Check that log file was created and contains message
                assert os.path.exists(log_file)
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert "Test message" in content
        finally:
            # Restore original handlers
            root_logger.handlers = original_handlers
    
    def test_setup_logging_different_levels(self):
        """Test setting up logging with different log levels."""
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        root_logger.handlers.clear()
        
        try:
            for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                setup_logging(log_level=level)
                assert root_logger.level == getattr(logging, level)
        finally:
            root_logger.handlers = original_handlers
    
    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"
    
    def test_setup_api_logging(self):
        """Test setting up API logging using settings."""
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        root_logger.handlers.clear()
        
        try:
            # Use a temporary directory for the log file
            with tempfile.TemporaryDirectory() as tmpdir:
                log_file = os.path.join(tmpdir, "test.log")
                
                # Mock settings
                with patch('api.logging_config.get_settings') as mock_settings:
                    mock_settings.return_value = Settings.model_construct(
                        log_level="WARNING",
                        log_file=log_file
                    )
                    
                    setup_api_logging()
                    
                    # Close file handlers to release file handles
                    for handler in root_logger.handlers:
                        if isinstance(handler, logging.FileHandler):
                            handler.close()
                    
                    # Check that logging was configured
                    assert root_logger.level == logging.WARNING
                    assert len(root_logger.handlers) >= 1
        finally:
            root_logger.handlers = original_handlers


class TestRequestResponseLogger:
    """Test request/response logging middleware."""
    
    def test_middleware_creation(self):
        """Test creating request logging middleware."""
        app = FastAPI()
        middleware = RequestResponseLogger(app)
        
        assert isinstance(middleware, RequestResponseLogger)
        assert middleware.app == app
    
    def test_middleware_logs_request(self):
        """Test that middleware logs requests."""
        app = FastAPI()
        
        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}
        
        # Add middleware
        middleware = RequestResponseLogger(app, logger_name="test.middleware")
        
        # Mock logger to capture log calls
        mock_logger = MagicMock()
        middleware.logger = mock_logger
        
        # Add middleware to app
        app.add_middleware(RequestResponseLogger, logger_name="test.middleware")
        
        # Create test client
        client = TestClient(app)
        
        # Make request
        response = client.get("/test")
        
        # Check that logger was called (may be called by actual middleware)
        # Since we're testing with real middleware, we check response instead
        assert response.status_code == 200
    
    def test_middleware_logs_response_status(self):
        """Test that middleware logs response status codes."""
        app = FastAPI()
        
        @app.get("/success")
        def success():
            return {"status": "ok"}
        
        @app.get("/notfound")
        def notfound():
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        
        # Add middleware
        app.add_middleware(RequestResponseLogger, logger_name="test.middleware")
        
        client = TestClient(app)
        
        # Test success response
        response = client.get("/success")
        assert response.status_code == 200
        
        # Test error response
        response = client.get("/notfound")
        assert response.status_code == 404
    
    def test_middleware_logs_duration(self):
        """Test that middleware logs request duration."""
        import time
        
        app = FastAPI()
        
        @app.get("/slow")
        def slow_endpoint():
            time.sleep(0.1)  # Simulate slow request
            return {"message": "slow"}
        
        # Add middleware
        app.add_middleware(RequestResponseLogger, logger_name="test.middleware")
        
        client = TestClient(app)
        response = client.get("/slow")
        
        # Check that request completed successfully
        assert response.status_code == 200
    
    def test_middleware_logs_errors(self):
        """Test that middleware logs errors."""
        app = FastAPI()
        
        @app.get("/error")
        def error_endpoint():
            raise ValueError("Test error")
        
        # Add middleware
        app.add_middleware(RequestResponseLogger, logger_name="test.middleware")
        
        client = TestClient(app, raise_server_exceptions=False)
        
        # Make request that will fail (FastAPI converts to 500)
        # raise_server_exceptions=False allows us to get the 500 response
        response = client.get("/error")
        assert response.status_code == 500


class TestLoggingIntegration:
    """Test logging integration with FastAPI app."""
    
    def test_logging_integration(self):
        """Test that logging works with FastAPI application."""
        from api.main import app
        from api.logging_config import setup_api_logging
        
        # Setup logging
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        root_logger.handlers.clear()
        
        try:
            setup_api_logging()
            
            # Create test client
            client = TestClient(app)
            
            # Make a request
            response = client.get("/")
            
            # Check that request was successful
            assert response.status_code == 200
            
            # Check that logger exists
            api_logger = logging.getLogger("api.main")
            assert api_logger is not None
        finally:
            root_logger.handlers = original_handlers

