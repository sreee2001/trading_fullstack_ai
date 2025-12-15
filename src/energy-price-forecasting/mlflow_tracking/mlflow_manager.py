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
        
        self.active_run = None
        self.run_id = None
        
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
    
    def create_experiment(self, experiment_name: str) -> str:
        """
        Backwards-compatible helper to create or get an experiment.

        Some example scripts call create_experiment(); this simply delegates
        to setup_experiment() which already handles create-or-get logic.
        """
        return self.setup_experiment(experiment_name)

    # ------------------------------------------------------------------
    # Run-level helpers (simple convenience wrappers around mlflow API)
    # ------------------------------------------------------------------
    def start_run(self, run_name: Optional[str] = None):
        """
        Start a new MLflow run using the current tracking URI/experiment.
        """
        if self.active_run is not None:
            logger.warning("Run already active. Ending previous run before starting a new one.")
            self.end_run()
        
        self.active_run = mlflow.start_run(run_name=run_name)
        self.run_id = self.active_run.info.run_id
        logger.info(f"Started run: {self.run_id}")
        return self.active_run
    
    def end_run(self, status: str = 'FINISHED'):
        """
        End the current MLflow run.
        """
        if self.active_run is not None:
            mlflow.end_run(status=status)
            logger.info(f"Ended run: {self.run_id} (Status: {status})")
            self.active_run = None
            self.run_id = None
        else:
            logger.warning("No active run to end.")
    
    def log_params(self, params: Dict[str, Any]):
        """
        Log parameters to the active run.
        """
        if self.active_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        
        params_str = {k: str(v) for k, v in params.items()}
        mlflow.log_params(params_str)
        logger.debug(f"Logged parameters: {list(params.keys())}")
    
    def log_metrics(self, metrics: Dict[str, float]):
        """
        Log metrics to the active run.
        """
        if self.active_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        
        mlflow.log_metrics(metrics)
        logger.debug(f"Logged metrics: {list(metrics.keys())}")
    
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

