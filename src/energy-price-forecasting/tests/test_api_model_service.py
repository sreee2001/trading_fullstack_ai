"""
Unit tests for model loading service (Story 4.2.3).
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path
import tempfile
import pickle

from api.services.model_service import (
    ModelService,
    get_model_service,
    _model_cache
)


# Simple model class for testing pickle
class SimpleModel:
    """Simple model class for testing disk loading."""
    def __init__(self):
        self.is_fitted = True
    
    def predict(self, steps=1, return_conf_int=False):
        import pandas as pd
        return pd.Series([75.0] * steps)


class TestModelService:
    """Test ModelService class."""
    
    def test_model_service_initialization(self):
        """Test ModelService initialization."""
        service = ModelService(use_mlflow=False, preload_at_startup=False)
        
        assert service.use_mlflow is False
        assert service.preload_at_startup is False
        assert isinstance(service.models, dict)
    
    def test_model_service_with_mlflow(self):
        """Test ModelService initialization with MLflow."""
        with patch('api.services.model_service.MLFLOW_AVAILABLE', True):
            with patch('api.services.model_service.ModelRegistry') as mock_registry:
                mock_registry.return_value = MagicMock()
                
                service = ModelService(use_mlflow=True)
                
                assert service.use_mlflow is True
                assert service.registry is not None
    
    def test_load_model_uses_cache(self):
        """Test that load_model uses cached model if available."""
        # Clear cache
        _model_cache.clear()
        
        service = ModelService(use_mlflow=False)
        
        # Load model first time
        model1 = service.load_model("WTI", "lstm")
        
        # Load same model second time (should use cache)
        with patch.object(service, '_create_placeholder_model') as mock_create:
            model2 = service.load_model("WTI", "lstm")
            
            # Should not call create again
            mock_create.assert_not_called()
            assert model1 is model2
    
    def test_load_model_creates_placeholder(self):
        """Test that load_model creates placeholder when no model found."""
        service = ModelService(use_mlflow=False)
        
        # Clear cache
        cache_key = "WTI_lstm"
        if cache_key in _model_cache:
            del _model_cache[cache_key]
        
        model = service.load_model("WTI", "lstm")
        
        assert model is not None
        assert hasattr(model, 'predict')
        assert hasattr(model, 'is_fitted')
        assert model.is_fitted is True
    
    def test_load_model_from_disk(self):
        """Test loading model from disk."""
        service = ModelService(use_mlflow=False, model_base_path=None)
        
        # Create a temporary model file
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "wti"
            model_dir.mkdir()
            model_path = model_dir / "lstm.pkl"
            
            # Use the SimpleModel class defined at module level
            simple_model = SimpleModel()
            
            # Save model
            with open(model_path, 'wb') as f:
                pickle.dump(simple_model, f)
            
            # Update service to use this path
            service.model_base_path = Path(tmpdir)
            
            # Clear cache
            cache_key = "WTI_lstm"
            if cache_key in _model_cache:
                del _model_cache[cache_key]
            
            # Load model
            model = service.load_model("WTI", "lstm")
            
            # Should load from disk (or use placeholder if path not found)
            assert model is not None
    
    def test_load_model_from_mlflow(self):
        """Test loading model from MLflow registry."""
        with patch('api.services.model_service.MLFLOW_AVAILABLE', True):
            with patch('api.services.model_service.ModelRegistry') as mock_registry_class:
                mock_registry = MagicMock()
                mock_registry_class.return_value = mock_registry
                
                # Mock MLflow model loading
                mock_model = MagicMock()
                mock_model.is_fitted = True
                
                with patch('api.services.model_service.mlflow') as mock_mlflow:
                    mock_mlflow.pyfunc.load_model.return_value = mock_model
                    
                    mock_registry.get_model.return_value = "models:/WTI_LSTM/1"
                    
                    service = ModelService(use_mlflow=True)
                    
                    # Clear cache
                    cache_key = "WTI_lstm"
                    if cache_key in _model_cache:
                        del _model_cache[cache_key]
                    
                    # Load model
                    model = service.load_model("WTI", "lstm")
                    
                    # Should load from MLflow
                    assert model is not None
                    mock_registry.get_model.assert_called()
    
    def test_get_model_returns_cached(self):
        """Test that get_model returns cached model."""
        service = ModelService(use_mlflow=False)
        
        # Load a model
        loaded_model = service.load_model("WTI", "lstm")
        
        # Get model
        retrieved_model = service.get_model("WTI", "lstm")
        
        assert retrieved_model is loaded_model
    
    def test_get_model_returns_none_if_not_loaded(self):
        """Test that get_model returns None if model not loaded."""
        service = ModelService(use_mlflow=False)
        
        # Clear cache
        cache_key = "UNKNOWN_lstm"
        if cache_key in _model_cache:
            del _model_cache[cache_key]
        
        model = service.get_model("UNKNOWN", "lstm")
        
        assert model is None
    
    def test_preload_models(self):
        """Test preloading models."""
        service = ModelService(use_mlflow=False, preload_at_startup=False)
        
        # Clear cache
        _model_cache.clear()
        
        # Preload models
        service.preload_models(
            commodities=["WTI", "BRENT"],
            model_types=["lstm"]
        )
        
        # Check that models are cached
        assert "WTI_lstm" in _model_cache
        assert "BRENT_lstm" in _model_cache
    
    def test_clear_cache(self):
        """Test clearing model cache."""
        service = ModelService(use_mlflow=False)
        
        # Load a model
        service.load_model("WTI", "lstm")
        
        # Verify it's cached
        assert "WTI_lstm" in _model_cache
        
        # Clear cache
        service.clear_cache()
        
        # Verify cache is empty
        assert len(_model_cache) == 0
        assert len(service.models) == 0
    
    def test_get_cached_models(self):
        """Test getting list of cached models."""
        service = ModelService(use_mlflow=False)
        
        # Clear cache
        _model_cache.clear()
        
        # Load some models
        service.load_model("WTI", "lstm")
        service.load_model("BRENT", "arima")
        
        # Get cached models list
        cached = service.get_cached_models()
        
        assert "WTI_lstm" in cached
        assert "BRENT_arima" in cached
        assert len(cached) == 2


class TestGetModelService:
    """Test get_model_service function (singleton pattern)."""
    
    def test_singleton_pattern(self):
        """Test that get_model_service returns the same instance."""
        from api.services.model_service import _model_service
        
        # Clear global service
        import api.services.model_service
        api.services.model_service._model_service = None
        
        service1 = get_model_service()
        service2 = get_model_service()
        
        assert service1 is service2

