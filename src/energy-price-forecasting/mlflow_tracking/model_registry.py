"""
MLflow Model Registry.

Manages model registration, versioning, and deployment stages.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

from typing import Dict, Any, Optional, List
import logging

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None
    MlflowClient = None

from .mlflow_manager import MLflowManager

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Manages model registration and versioning in MLflow.
    
    Provides methods to register models, manage versions, and track
    deployment stages.
    
    Attributes:
        manager: MLflowManager instance
        client: MLflow client instance
    
    Example:
        >>> registry = ModelRegistry()
        >>> registry.register_model(run_id, 'energy_forecasting_model')
        >>> registry.transition_model('energy_forecasting_model', 'Production', version=1)
    """
    
    def __init__(self, tracking_uri: Optional[str] = None):
        """
        Initialize ModelRegistry.
        
        Args:
            tracking_uri: MLflow tracking URI
        
        Raises:
            ImportError: If MLflow is not installed
        """
        if not MLFLOW_AVAILABLE:
            raise ImportError(
                "MLflow is required. Install it with: pip install mlflow"
            )
        
        self.manager = MLflowManager(tracking_uri=tracking_uri)
        self.client = self.manager.client
        
        logger.info("ModelRegistry initialized")
    
    def register_model(
        self,
        model_uri: str,
        name: str,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Register a model in the model registry.
        
        Args:
            model_uri: URI of the model (e.g., "runs:/run_id/model_path")
            name: Name for the registered model
            tags: Optional tags to add to the model
        
        Returns:
            Model version
        """
        try:
            model_version = mlflow.register_model(model_uri, name)
            
            if tags:
                self.client.set_model_version_tag(
                    name,
                    model_version.version,
                    **tags
                )
            
            logger.info(f"Registered model: {name} (Version: {model_version.version})")
            return model_version.version
        
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            raise
    
    def get_model_versions(self, name: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a registered model.
        
        Args:
            name: Name of the registered model
        
        Returns:
            List of model version dictionaries
        """
        try:
            versions = self.client.search_model_versions(f"name='{name}'")
            
            return [
                {
                    'version': v.version,
                    'stage': v.current_stage,
                    'run_id': v.run_id,
                    'creation_timestamp': v.creation_timestamp,
                    'status': v.status,
                    'tags': v.tags
                }
                for v in versions
            ]
        except Exception as e:
            logger.error(f"Failed to get model versions: {e}")
            return []
    
    def get_latest_versions(
        self,
        name: str,
        stages: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get latest versions of a model by stage.
        
        Args:
            name: Name of the registered model
            stages: List of stages (e.g., ['Production', 'Staging'])
        
        Returns:
            List of latest model version dictionaries
        """
        try:
            versions = self.client.get_latest_versions(name, stages=stages)
            
            return [
                {
                    'version': v.version,
                    'stage': v.current_stage,
                    'run_id': v.run_id,
                    'creation_timestamp': v.creation_timestamp,
                    'status': v.status
                }
                for v in versions
            ]
        except Exception as e:
            logger.error(f"Failed to get latest versions: {e}")
            return []
    
    def transition_model(
        self,
        name: str,
        stage: str,
        version: Optional[int] = None
    ):
        """
        Transition a model version to a new stage.
        
        Args:
            name: Name of the registered model
            stage: Target stage ('Staging', 'Production', 'Archived')
            version: Model version (None = latest)
        """
        try:
            if version is None:
                # Get latest version
                versions = self.get_latest_versions(name)
                if not versions:
                    raise ValueError(f"No versions found for model: {name}")
                version = versions[0]['version']
            
            self.client.transition_model_version_stage(
                name=name,
                version=str(version),
                stage=stage
            )
            
            logger.info(f"Transitioned model {name} v{version} to stage: {stage}")
        
        except Exception as e:
            logger.error(f"Failed to transition model: {e}")
            raise
    
    def get_model(self, name: str, version: Optional[int] = None, stage: Optional[str] = None):
        """
        Get a registered model.
        
        Args:
            name: Name of the registered model
            version: Model version (None = latest)
            stage: Model stage (None = any)
        
        Returns:
            Model URI
        """
        try:
            if version is not None:
                model_uri = f"models:/{name}/{version}"
            elif stage is not None:
                model_uri = f"models:/{name}/{stage}"
            else:
                # Get latest version
                versions = self.get_latest_versions(name)
                if not versions:
                    raise ValueError(f"No versions found for model: {name}")
                model_uri = f"models:/{name}/{versions[0]['version']}"
            
            logger.info(f"Retrieved model: {model_uri}")
            return model_uri
        
        except Exception as e:
            logger.error(f"Failed to get model: {e}")
            raise
    
    def delete_model_version(self, name: str, version: int):
        """
        Delete a model version.
        
        Args:
            name: Name of the registered model
            version: Model version to delete
        """
        try:
            self.client.delete_model_version(name, str(version))
            logger.info(f"Deleted model version: {name} v{version}")
        
        except Exception as e:
            logger.error(f"Failed to delete model version: {e}")
            raise
    
    def set_model_version_tag(
        self,
        name: str,
        version: int,
        key: str,
        value: str
    ):
        """
        Set a tag on a model version.
        
        Args:
            name: Name of the registered model
            version: Model version
            key: Tag key
            value: Tag value
        """
        try:
            self.client.set_model_version_tag(name, str(version), key, value)
            logger.debug(f"Set tag on {name} v{version}: {key} = {value}")
        
        except Exception as e:
            logger.error(f"Failed to set model version tag: {e}")
            raise
    
    def get_model_lineage(self, name: str, version: int) -> Dict[str, Any]:
        """
        Get model lineage information.
        
        Args:
            name: Name of the registered model
            version: Model version
        
        Returns:
            Dictionary with lineage information
        """
        try:
            version_info = self.client.get_model_version(name, str(version))
            
            # Get run information
            run = self.client.get_run(version_info.run_id)
            
            return {
                'model_name': name,
                'version': version,
                'stage': version_info.current_stage,
                'run_id': version_info.run_id,
                'run_name': run.info.run_name,
                'experiment_id': run.info.experiment_id,
                'parameters': run.data.params,
                'metrics': run.data.metrics,
                'tags': run.data.tags,
                'creation_timestamp': version_info.creation_timestamp
            }
        
        except Exception as e:
            logger.error(f"Failed to get model lineage: {e}")
            return {}

