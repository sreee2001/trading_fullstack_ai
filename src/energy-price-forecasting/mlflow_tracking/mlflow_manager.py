"""
MLflow Manager for setup and configuration.

Manages MLflow tracking server connection and configuration.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import os
from typing import Optional, Dict, Any
import logging

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None
    MlflowClient = None

logger = logging.getLogger(__name__)


class MLflowManager:
    """
    Manages MLflow tracking server connection and configuration.
    
    Handles MLflow server setup, connection, and basic configuration.
    
    Attributes:
        tracking_uri: MLflow tracking URI
        client: MLflow client instance
    
    Example:
        >>> manager = MLflowManager(tracking_uri='http://localhost:5000')
        >>> manager.setup_experiment('energy_forecasting')
    """
    
    def __init__(
        self,
        tracking_uri: Optional[str] = None,
        experiment_name: Optional[str] = None
    ):
        """
        Initialize MLflowManager.
        
        Args:
            tracking_uri: MLflow tracking URI (default: local file store)
            experiment_name: Name of experiment to use/create
        
        Raises:
            ImportError: If MLflow is not installed
        """
        if not MLFLOW_AVAILABLE:
            raise ImportError(
                "MLflow is required. Install it with: pip install mlflow"
            )
        
        # Set tracking URI
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        else:
            # Use default local file store
            default_uri = os.getenv('MLFLOW_TRACKING_URI', 'file:./mlruns')
            mlflow.set_tracking_uri(default_uri)
        
        self.tracking_uri = mlflow.get_tracking_uri()
        self.client = MlflowClient(tracking_uri=self.tracking_uri)
        
        # Set experiment if provided
        if experiment_name:
            self.setup_experiment(experiment_name)
        
        logger.info(f"MLflowManager initialized with tracking URI: {self.tracking_uri}")
    
    def setup_experiment(self, experiment_name: str) -> str:
        """
        Set up or get existing experiment.
        
        Args:
            experiment_name: Name of the experiment
        
        Returns:
            Experiment ID
        """
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                logger.info(f"Created new experiment: {experiment_name} (ID: {experiment_id})")
            else:
                experiment_id = experiment.experiment_id
                logger.info(f"Using existing experiment: {experiment_name} (ID: {experiment_id})")
            
            mlflow.set_experiment(experiment_name)
            return experiment_id
        except Exception as e:
            logger.error(f"Failed to setup experiment: {e}")
            raise
    
    def get_experiment(self, experiment_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get experiment information.
        
        Args:
            experiment_name: Name of experiment (None = current)
        
        Returns:
            Dictionary with experiment information
        """
        if experiment_name:
            experiment = mlflow.get_experiment_by_name(experiment_name)
        else:
            experiment = mlflow.get_experiment(mlflow.get_experiment_by_name(
                mlflow.get_experiment(mlflow.active_run().info.experiment_id).name
            ).experiment_id)
        
        if experiment is None:
            raise ValueError(f"Experiment not found: {experiment_name}")
        
        return {
            'experiment_id': experiment.experiment_id,
            'name': experiment.name,
            'artifact_location': experiment.artifact_location,
            'lifecycle_stage': experiment.lifecycle_stage,
            'tags': experiment.tags
        }
    
    def list_experiments(self) -> list:
        """
        List all experiments.
        
        Returns:
            List of experiment dictionaries
        """
        experiments = self.client.search_experiments()
        return [
            {
                'experiment_id': exp.experiment_id,
                'name': exp.name,
                'artifact_location': exp.artifact_location,
                'lifecycle_stage': exp.lifecycle_stage
            }
            for exp in experiments
        ]
    
    def delete_experiment(self, experiment_name: str):
        """
        Delete an experiment.
        
        Args:
            experiment_name: Name of experiment to delete
        """
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment:
            self.client.delete_experiment(experiment.experiment_id)
            logger.info(f"Deleted experiment: {experiment_name}")
        else:
            logger.warning(f"Experiment not found: {experiment_name}")

