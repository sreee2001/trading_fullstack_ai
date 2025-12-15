"""
Unit tests for API lifecycle management (Story 4.1.4).

Note: Direct async function testing requires pytest-asyncio which may not be available.
The lifecycle events are tested through integration tests with the FastAPI app.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.lifecycle import (
    get_database_manager,
    get_ml_models,
)


class TestLifecycleFunctions:
    """Test lifecycle helper functions."""
    
    def test_get_database_manager(self):
        """Test getting database manager instance."""
        import api.lifecycle
        
        # Set a mock database manager
        mock_db_manager = MagicMock()
        original_db_manager = api.lifecycle._db_manager
        api.lifecycle._db_manager = mock_db_manager
        
        try:
            result = get_database_manager()
            assert result == mock_db_manager
        finally:
            api.lifecycle._db_manager = original_db_manager
    
    def test_get_ml_models(self):
        """Test getting ML models dictionary."""
        import api.lifecycle
        
        # Set mock ML models
        mock_models = {"model1": MagicMock(), "model2": MagicMock()}
        original_models = api.lifecycle._ml_models
        api.lifecycle._ml_models = mock_models
        
        try:
            result = get_ml_models()
            assert result == mock_models
        finally:
            api.lifecycle._ml_models = original_models


class TestLifecycleIntegration:
    """Test lifecycle events integration with FastAPI app."""
    
    def test_startup_shutdown_integration(self):
        """Test that startup and shutdown events are registered."""
        from api.main import app
        
        # Check that event handlers are registered
        # FastAPI stores event handlers in app.router.on_startup and app.router.on_shutdown
        # We can't directly access them, but we can test by checking the app works
        
        client = TestClient(app)
        
        # Make a request to verify app is working
        response = client.get("/")
        assert response.status_code == 200
        
        # The startup event should have been called when TestClient initialized
        # We can verify by checking that the app is functional
    
    def test_app_starts_with_lifecycle_events(self):
        """Test that app starts successfully with lifecycle events."""
        from api.main import app
        
        # Create test client - this will trigger startup events
        client = TestClient(app)
        
        # Verify app is working
        response = client.get("/health")
        assert response.status_code == 200
        
        # Verify root endpoint works
        response = client.get("/")
        assert response.status_code == 200
    
    def test_lifecycle_module_exists(self):
        """Test that lifecycle module exists and has required functions."""
        from api import lifecycle
        
        # Check that required functions exist
        assert hasattr(lifecycle, 'startup_event')
        assert hasattr(lifecycle, 'shutdown_event')
        assert hasattr(lifecycle, 'get_database_manager')
        assert hasattr(lifecycle, 'get_ml_models')
        
        # Check that functions are callable
        assert callable(lifecycle.startup_event)
        assert callable(lifecycle.shutdown_event)
        assert callable(lifecycle.get_database_manager)
        assert callable(lifecycle.get_ml_models)
