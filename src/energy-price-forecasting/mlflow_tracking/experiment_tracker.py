"""
MLflow Experiment Tracker.

Tracks experiments, logs parameters, metrics, and artifacts.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import os
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None

from .mlflow_manager import MLflowManager

logger = logging.getLogger(__name__)


class ExperimentTracker:
    """
    Tracks ML experiments using MLflow.
    
    Provides methods to log parameters, metrics, artifacts, and models.
    
    Attributes:
        manager: MLflowManager instance
        run_id: Current run ID
        active_run: Current active MLflow run
    
    Example:
        >>> tracker = ExperimentTracker(experiment_name='energy_forecasting')
        >>> tracker.start_run()
        >>> tracker.log_params({'learning_rate': 0.001})
        >>> tracker.log_metrics({'rmse': 2.5})
        >>> tracker.end_run()
    """
    
    def __init__(
        self,
        experiment_name: str,
        tracking_uri: Optional[str] = None,
        run_name: Optional[str] = None
    ):
        """
        Initialize ExperimentTracker.
        
        Args:
            experiment_name: Name of the experiment
            tracking_uri: MLflow tracking URI
            run_name: Name for the run (optional)
        
        Raises:
            ImportError: If MLflow is not installed
        """
        if not MLFLOW_AVAILABLE:
            raise ImportError(
                "MLflow is required. Install it with: pip install mlflow"
            )
        
        self.manager = MLflowManager(tracking_uri=tracking_uri, experiment_name=experiment_name)
        self.experiment_name = experiment_name
        self.run_name = run_name
        self.run_id = None
        self.active_run = None
        
        logger.info(f"ExperimentTracker initialized for experiment: {experiment_name}")
    
    def start_run(self, run_name: Optional[str] = None, tags: Optional[Dict[str, str]] = None):
        """
        Start a new MLflow run.
        
        Args:
            run_name: Name for this run
            tags: Dictionary of tags to add to the run
        """
        if self.active_run is not None:
            logger.warning("Run already active. Ending previous run.")
            self.end_run()
        
        run_name = run_name or self.run_name or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.active_run = mlflow.start_run(run_name=run_name)
        self.run_id = self.active_run.info.run_id
        
        if tags:
            self.log_tags(tags)
        
        logger.info(f"Started run: {run_name} (ID: {self.run_id})")
    
    def end_run(self, status: str = 'FINISHED'):
        """
        End the current MLflow run.
        
        Args:
            status: Run status ('FINISHED', 'FAILED', 'KILLED')
        """
        if self.active_run is not None:
            mlflow.end_run(status=status)
            logger.info(f"Ended run: {self.run_id} (Status: {status})")
            self.active_run = None
            self.run_id = None
        else:
            logger.warning("No active run to end")
    
    def log_params(self, params: Dict[str, Any]):
        """
        Log parameters to the current run.
        
        Args:
            params: Dictionary of parameter names and values
        """
        if self.active_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        
        # Convert all values to strings (MLflow requirement)
        params_str = {k: str(v) for k, v in params.items()}
        mlflow.log_params(params_str)
        logger.debug(f"Logged parameters: {list(params.keys())}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """
        Log metrics to the current run.
        
        Args:
            metrics: Dictionary of metric names and values
            step: Optional step number for time-series metrics
        """
        if self.active_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        
        if step is not None:
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value, step=step)
        else:
            mlflow.log_metrics(metrics)
        
        logger.debug(f"Logged metrics: {list(metrics.keys())}")
    
    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        """
        Log an artifact (file) to the current run.
        
        Args:
            local_path: Path to local file to log
            artifact_path: Optional path within artifact directory
        """
        if self.active_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Artifact not found: {local_path}")
        
        mlflow.log_artifact(local_path, artifact_path)
        logger.debug(f"Logged artifact: {local_path}")
    
    def log_artifacts(self, local_dir: str, artifact_path: Optional[str] = None):
        """
        Log all files in a directory as artifacts.
        
        Args:
            local_dir: Path to local directory
            artifact_path: Optional path within artifact directory
        """
        if self.active_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        
        if not os.path.exists(local_dir):
            raise FileNotFoundError(f"Directory not found: {local_dir}")
        
        mlflow.log_artifacts(local_dir, artifact_path)
        logger.debug(f"Logged artifacts from: {local_dir}")
    
    def log_model(
        self,
        model,
        artifact_path: str = 'model',
        registered_model_name: Optional[str] = None
    ):
        """
        Log a model to the current run.
        
        Args:
            model: Model object (must support MLflow model logging)
            artifact_path: Path within artifact directory
            registered_model_name: Optional name to register model in registry
        """
        if self.active_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        
        try:
            # Try to log using model's mlflow integration
            if hasattr(model, 'log_model'):
                model.log_model(artifact_path=artifact_path)
            else:
                # Generic model logging
                mlflow.pyfunc.log_model(artifact_path=artifact_path, python_model=model)
            
            logger.info(f"Logged model to: {artifact_path}")
            
            # Register model if name provided
            if registered_model_name:
                model_uri = f"runs:/{self.run_id}/{artifact_path}"
                mlflow.register_model(model_uri, registered_model_name)
                logger.info(f"Registered model: {registered_model_name}")
        
        except Exception as e:
            logger.error(f"Failed to log model: {e}")
            raise
    
    def log_tags(self, tags: Dict[str, str]):
        """
        Log tags to the current run.
        
        Args:
            tags: Dictionary of tag names and values
        """
        if self.active_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        
        mlflow.set_tags(tags)
        logger.debug(f"Logged tags: {list(tags.keys())}")
    
    def set_tag(self, key: str, value: str):
        """
        Set a single tag on the current run.
        
        Args:
            key: Tag key
            value: Tag value
        """
        if self.active_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        
        mlflow.set_tag(key, value)
        logger.debug(f"Set tag: {key} = {value}")
    
    def search_runs(
        self,
        filter_string: Optional[str] = None,
        max_results: int = 100,
        order_by: Optional[List[str]] = None
    ) -> list:
        """
        Search runs in the experiment.
        
        Args:
            filter_string: MLflow filter string (e.g., "metrics.rmse < 3.0")
            max_results: Maximum number of results
            order_by: List of columns to order by (e.g., ["metrics.rmse ASC"])
        
        Returns:
            List of run dictionaries
        """
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        if experiment is None:
            return []
        
        runs = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string=filter_string,
            max_results=max_results,
            order_by=order_by
        )
        
        return runs.to_dict('records')
    
    def get_best_run(self, metric: str = 'rmse', ascending: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get the best run based on a metric.
        
        Args:
            metric: Metric name to optimize
            ascending: Whether lower is better (True) or higher is better (False)
        
        Returns:
            Dictionary with best run information, or None if no runs found
        """
        order_by = [f"metrics.{metric} {'ASC' if ascending else 'DESC'}"]
        runs = self.search_runs(max_results=1, order_by=order_by)
        
        if runs:
            return runs[0]
        return None

