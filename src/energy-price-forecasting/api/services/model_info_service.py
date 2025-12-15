"""
Model Information Service.

This module provides services for retrieving model metadata
from the MLflow model registry.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from api.logging_config import get_logger

# Try to import MLflow components
try:
    from mlflow_tracking.model_registry import ModelRegistry
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    ModelRegistry = None

logger = get_logger(__name__)


class ModelInfoService:
    """
    Service for retrieving model information from MLflow registry.
    
    Provides:
    - Query MLflow model registry
    - Filter models by commodity
    - Extract model metadata and metrics
    - Convert to API response format
    """
    
    def __init__(self):
        """Initialize model info service."""
        self.registry: Optional[Any] = None
        
        if MLFLOW_AVAILABLE:
            try:
                self.registry = ModelRegistry()
                logger.info("ModelInfoService initialized with MLflow registry")
            except Exception as e:
                logger.warning(f"Failed to initialize MLflow registry: {e}. Model info will be limited.")
                self.registry = None
        else:
            logger.warning("MLflow not available. Model info service will return placeholder data.")
    
    def get_all_models(self, commodity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all registered models.
        
        Args:
            commodity_filter: Optional commodity symbol to filter by (WTI, BRENT, NG)
            
        Returns:
            List of model information dictionaries
        """
        logger.info(f"Retrieving models (commodity_filter: {commodity_filter})")
        
        if not self.registry:
            # Return placeholder data if MLflow not available
            return self._get_placeholder_models(commodity_filter)
        
        try:
            # Search for all registered models
            # MLflow doesn't have a direct "list all models" API, so we need to search
            # We'll search for models with names matching our pattern: {COMMODITY}_{MODEL_TYPE}
            all_models = []
            
            # Define model name patterns to search for
            commodities = ["WTI", "BRENT", "NG"] if not commodity_filter else [commodity_filter]
            model_types = ["LSTM", "ARIMA", "PROPHET", "EXPONENTIAL_SMOOTHING"]
            
            for commodity in commodities:
                for model_type in model_types:
                    model_name = f"{commodity}_{model_type}"
                    
                    try:
                        # Get latest versions for this model
                        versions = self.registry.get_latest_versions(model_name, stages=["Production", "Staging", "Archived"])
                        
                        for version_info in versions:
                            # Get detailed model information
                            model_info = self._get_model_info_from_version(
                                model_name=model_name,
                                version=version_info['version'],
                                stage=version_info.get('stage', 'None')
                            )
                            
                            if model_info:
                                all_models.append(model_info)
                    
                    except Exception as e:
                        # Model doesn't exist or error retrieving - skip
                        logger.debug(f"Model {model_name} not found or error: {e}")
                        continue
            
            logger.info(f"Retrieved {len(all_models)} models")
            return all_models
            
        except Exception as e:
            logger.error(f"Error retrieving models from MLflow: {e}", exc_info=True)
            # Return placeholder data on error
            return self._get_placeholder_models(commodity_filter)
    
    def _get_model_info_from_version(
        self,
        model_name: str,
        version: str,
        stage: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed model information from MLflow version.
        
        Args:
            model_name: Model name
            version: Model version
            stage: Model stage
            
        Returns:
            Model information dictionary or None
        """
        try:
            # Get model lineage (includes run info, metrics, parameters)
            lineage = self.registry.get_model_lineage(model_name, int(version))
            
            if not lineage:
                return None
            
            # Extract commodity and model type from model name
            parts = model_name.split('_', 1)
            commodity = parts[0] if len(parts) > 0 else "UNKNOWN"
            model_type = parts[1] if len(parts) > 1 else "UNKNOWN"
            
            # Extract metrics from run data
            metrics = lineage.get('metrics', {})
            model_metrics = {
                'rmse': metrics.get('rmse'),
                'mae': metrics.get('mae'),
                'mape': metrics.get('mape'),
                'r2': metrics.get('r2'),
                'directional_accuracy': metrics.get('directional_accuracy'),
                'sharpe_ratio': metrics.get('sharpe_ratio'),
                'sortino_ratio': metrics.get('sortino_ratio'),
                'max_drawdown': metrics.get('max_drawdown'),
                'win_rate': metrics.get('win_rate'),
            }
            
            # Remove None values
            model_metrics = {k: v for k, v in model_metrics.items() if v is not None}
            
            # Extract training date from creation timestamp
            creation_timestamp = lineage.get('creation_timestamp', 0)
            training_date = None
            created_at = None
            
            if creation_timestamp:
                dt = datetime.fromtimestamp(creation_timestamp / 1000.0)
                training_date = dt.date().isoformat()
                created_at = dt.isoformat()
            
            # Extract tags
            tags = lineage.get('tags', {})
            
            model_info = {
                'model_id': f"{model_name}:{version}",
                'model_name': model_name,
                'commodity': commodity,
                'model_type': model_type,
                'version': str(version),
                'stage': stage,
                'training_date': training_date,
                'created_at': created_at,
                'metrics': model_metrics if model_metrics else None,
                'run_id': lineage.get('run_id'),
                'experiment_id': str(lineage.get('experiment_id', '')),
                'tags': tags if tags else None,
                'description': tags.get('description') if tags else None,
            }
            
            return model_info
            
        except Exception as e:
            logger.error(f"Error getting model info for {model_name} v{version}: {e}")
            return None
    
    def _get_placeholder_models(self, commodity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get placeholder model information when MLflow is not available.
        
        Args:
            commodity_filter: Optional commodity filter
            
        Returns:
            List of placeholder model information
        """
        commodities = ["WTI", "BRENT", "NG"] if not commodity_filter else [commodity_filter]
        model_types = ["LSTM", "ARIMA", "PROPHET"]
        
        placeholder_models = []
        
        for commodity in commodities:
            for model_type in model_types:
                placeholder_models.append({
                    'model_id': f"{commodity}_{model_type}:1",
                    'model_name': f"{commodity}_{model_type}",
                    'commodity': commodity,
                    'model_type': model_type,
                    'version': "1",
                    'stage': "Production",
                    'training_date': None,
                    'created_at': None,
                    'metrics': None,
                    'run_id': None,
                    'experiment_id': None,
                    'tags': None,
                    'description': f"Placeholder {model_type} model for {commodity}",
                })
        
        logger.info(f"Returning {len(placeholder_models)} placeholder models")
        return placeholder_models


# Global service instance (singleton)
_model_info_service: Optional[ModelInfoService] = None


def get_model_info_service() -> ModelInfoService:
    """
    Get the global model info service instance.
    
    Returns:
        ModelInfoService instance
    """
    global _model_info_service
    if _model_info_service is None:
        _model_info_service = ModelInfoService()
    return _model_info_service

