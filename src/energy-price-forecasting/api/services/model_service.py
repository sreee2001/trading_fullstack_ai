"""
Model Loading and Management Service.

This module provides services for loading and managing ML models
for forecasting. Models are cached in memory for performance.

Supports:
- MLflow model registry integration
- Disk-based model loading (fallback)
- Model caching in memory
- Lazy loading (load on first request)
- Startup preloading (optional)
"""

from typing import Optional, Dict, Any, List
import logging
from pathlib import Path
import pickle
import os

from api.logging_config import get_logger

logger = get_logger(__name__)

# Global model cache
_model_cache: Dict[str, Any] = {}

# Try to import MLflow components
try:
    import mlflow
    from mlflow.tracking import MlflowClient
    from mlflow_tracking.model_registry import ModelRegistry
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None
    MlflowClient = None
    ModelRegistry = None


class ModelService:
    """
    Service for loading and managing ML models.
    
    Provides:
    - Model loading from MLflow registry
    - Model loading from disk (fallback)
    - Model caching in memory
    - Lazy loading (load on first request)
    - Startup preloading (optional)
    - Model retrieval by commodity/model type
    """
    
    def __init__(
        self,
        use_mlflow: bool = True,
        model_base_path: Optional[str] = None,
        preload_at_startup: bool = False
    ):
        """
        Initialize model service.
        
        Args:
            use_mlflow: Whether to use MLflow model registry (default: True)
            model_base_path: Base path for disk-based models (fallback)
            preload_at_startup: Whether to preload models at startup (default: False)
        """
        self.use_mlflow = use_mlflow and MLFLOW_AVAILABLE
        self.model_base_path = Path(model_base_path) if model_base_path else None
        self.preload_at_startup = preload_at_startup
        
        # Initialize MLflow registry if available
        self.registry: Optional[Any] = None
        if self.use_mlflow:
            try:
                self.registry = ModelRegistry()
                logger.info("MLflow model registry initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize MLflow registry: {e}. Will use disk-based loading.")
                self.use_mlflow = False
        
        self.models: Dict[str, Any] = {}
        logger.info(f"ModelService initialized (MLflow: {self.use_mlflow}, Preload: {preload_at_startup})")
    
    def load_model(
        self,
        commodity: str,
        model_type: str = "lstm",
        model_path: Optional[str] = None,
        version: Optional[int] = None,
        stage: Optional[str] = None
    ) -> Any:
        """
        Load a model for a commodity.
        
        Supports multiple loading strategies:
        1. MLflow registry (if available)
        2. Disk-based loading (fallback)
        3. Placeholder model (if neither available)
        
        Args:
            commodity: Commodity symbol (WTI, BRENT, NG)
            model_type: Type of model (lstm, arima, prophet)
            model_path: Optional path to model file (for disk loading)
            version: Model version (for MLflow registry)
            stage: Model stage (Production, Staging, etc.)
            
        Returns:
            Loaded model instance
            
        Raises:
            FileNotFoundError: If model not found on disk
            ValueError: If model_type is invalid
        """
        cache_key = f"{commodity}_{model_type}"
        
        # Check cache first
        if cache_key in _model_cache:
            logger.info(f"Using cached model: {cache_key}")
            return _model_cache[cache_key]
        
        logger.info(f"Loading model: {cache_key}")
        
        model = None
        
        # Try MLflow registry first
        if self.use_mlflow and self.registry:
            try:
                model = self._load_from_mlflow(commodity, model_type, version, stage)
                if model:
                    logger.info(f"Model loaded from MLflow registry: {cache_key}")
            except Exception as e:
                logger.warning(f"Failed to load from MLflow: {e}. Trying disk-based loading.")
        
        # Try disk-based loading if MLflow failed
        if model is None:
            try:
                model = self._load_from_disk(commodity, model_type, model_path)
                if model:
                    logger.info(f"Model loaded from disk: {cache_key}")
            except Exception as e:
                logger.warning(f"Failed to load from disk: {e}. Using placeholder model.")
        
        # Fallback to placeholder model
        if model is None:
            logger.warning(f"Using placeholder model for {cache_key}")
            model = self._create_placeholder_model(commodity, model_type)
        
        # Cache the model
        _model_cache[cache_key] = model
        self.models[cache_key] = model
        
        logger.info(f"Model loaded and cached: {cache_key}")
        return model
    
    def _load_from_mlflow(
        self,
        commodity: str,
        model_type: str,
        version: Optional[int] = None,
        stage: Optional[str] = None
    ) -> Optional[Any]:
        """
        Load model from MLflow registry.
        
        Args:
            commodity: Commodity symbol
            model_type: Type of model
            version: Model version (None = latest)
            stage: Model stage (None = any)
            
        Returns:
            Loaded model or None if not found
        """
        if not self.registry:
            return None
        
        try:
            # Construct model name (e.g., "WTI_LSTM", "BRENT_ARIMA")
            model_name = f"{commodity}_{model_type.upper()}"
            
            # Get model URI from registry
            model_uri = self.registry.get_model(
                name=model_name,
                version=version,
                stage=stage or "Production"
            )
            
            # Load model using MLflow
            model = mlflow.pyfunc.load_model(model_uri)
            
            logger.info(f"Loaded model from MLflow: {model_uri}")
            return model
            
        except ValueError as e:
            # Model not found in registry
            logger.debug(f"Model not found in MLflow registry: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading model from MLflow: {e}")
            return None
    
    def _load_from_disk(
        self,
        commodity: str,
        model_type: str,
        model_path: Optional[str] = None
    ) -> Optional[Any]:
        """
        Load model from disk.
        
        Args:
            commodity: Commodity symbol
            model_type: Type of model
            model_path: Optional specific path to model file
            
        Returns:
            Loaded model or None if not found
        """
        if model_path:
            # Use provided path
            path = Path(model_path)
        elif self.model_base_path:
            # Construct path from base path
            path = self.model_base_path / commodity.lower() / f"{model_type}.pkl"
        else:
            # Try default location
            default_path = Path("models") / commodity.lower() / f"{model_type}.pkl"
            if default_path.exists():
                path = default_path
            else:
                return None
        
        if not path.exists():
            return None
        
        try:
            # Load pickle file
            with open(path, 'rb') as f:
                model = pickle.load(f)
            
            logger.info(f"Loaded model from disk: {path}")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model from disk {path}: {e}")
            return None
    
    def _create_placeholder_model(self, commodity: str, model_type: str) -> Any:
        """
        Create a placeholder model for testing.
        
        In production, this would load actual trained models.
        """
        # This is a placeholder - actual model loading will be implemented
        # in Story 4.2.3 with MLflow integration
        logger.warning(
            f"Creating placeholder model for {commodity} ({model_type}). "
            "Actual model loading will be implemented in Story 4.2.3"
        )
        
        # Return a mock model object that has the expected interface
        class PlaceholderModel:
            def __init__(self, commodity: str, model_type: str):
                self.commodity = commodity
                self.model_type = model_type
                self.is_fitted = True  # Placeholder models are "fitted"
            
            def predict(self, steps: int = 1, return_conf_int: bool = False):
                """Generate placeholder predictions."""
                import pandas as pd
                import numpy as np
                
                # Generate dummy predictions
                base_price = 75.0 if commodity == "WTI" else 80.0 if commodity == "BRENT" else 3.0
                predictions = pd.Series([base_price] * steps)
                
                if return_conf_int:
                    # Generate confidence intervals
                    conf_lower = predictions * 0.95
                    conf_upper = predictions * 1.05
                    conf_int = pd.DataFrame({
                        'lower': conf_lower,
                        'upper': conf_upper
                    })
                    return predictions, conf_int
                
                return predictions
        
        return PlaceholderModel(commodity, model_type)
    
    def get_model(self, commodity: str, model_type: str = "lstm") -> Optional[Any]:
        """
        Get a cached model.
        
        Args:
            commodity: Commodity symbol
            model_type: Type of model
            
        Returns:
            Model instance or None if not loaded
        """
        cache_key = f"{commodity}_{model_type}"
        return _model_cache.get(cache_key)
    
    def preload_models(
        self,
        commodities: List[str] = ["WTI", "BRENT", "NG"],
        model_types: List[str] = ["lstm"]
    ):
        """
        Preload models at startup.
        
        Args:
            commodities: List of commodities to preload
            model_types: List of model types to preload
        """
        logger.info(f"Preloading models for {len(commodities)} commodities and {len(model_types)} model types...")
        
        loaded_count = 0
        failed_count = 0
        
        for commodity in commodities:
            for model_type in model_types:
                try:
                    self.load_model(commodity, model_type)
                    loaded_count += 1
                except Exception as e:
                    logger.warning(f"Failed to preload {commodity}_{model_type}: {e}")
                    failed_count += 1
        
        logger.info(
            f"Model preloading complete: {loaded_count} loaded, {failed_count} failed"
        )
    
    def clear_cache(self):
        """Clear the model cache."""
        global _model_cache
        _model_cache.clear()
        self.models.clear()
        logger.info("Model cache cleared")
    
    def get_cached_models(self) -> List[str]:
        """
        Get list of cached model keys.
        
        Returns:
            List of cache keys (format: "commodity_modeltype")
        """
        return list(_model_cache.keys())


# Global model service instance (singleton)
_model_service: Optional[ModelService] = None


def get_model_service(
    use_mlflow: Optional[bool] = None,
    model_base_path: Optional[str] = None,
    preload_at_startup: Optional[bool] = None
) -> ModelService:
    """
    Get the global model service instance.
    
    Args:
        use_mlflow: Whether to use MLflow (None = use settings)
        model_base_path: Base path for models (None = use settings)
        preload_at_startup: Whether to preload at startup (None = use settings)
    
    Returns:
        ModelService instance
    """
    global _model_service
    if _model_service is None:
        # Get settings if not provided
        if use_mlflow is None or model_base_path is None or preload_at_startup is None:
            from api.config import get_settings
            settings = get_settings()
            
            use_mlflow = use_mlflow if use_mlflow is not None else settings.use_mlflow
            model_base_path = model_base_path if model_base_path is not None else settings.model_base_path
            preload_at_startup = preload_at_startup if preload_at_startup is not None else settings.preload_models_at_startup
        
        _model_service = ModelService(
            use_mlflow=use_mlflow,
            model_base_path=model_base_path,
            preload_at_startup=preload_at_startup
        )
    return _model_service

