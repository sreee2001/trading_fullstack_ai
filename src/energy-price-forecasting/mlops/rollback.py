"""
Model and Deployment Rollback Mechanism.

Provides functionality to rollback models and deployments to previous versions
when issues are detected.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelRollback:
    """
    Handles rollback of ML models to previous versions.
    
    Manages model version history and provides rollback functionality
    when a deployed model performs poorly or causes issues.
    """
    
    def __init__(self, registry=None):
        """
        Initialize ModelRollback.
        
        Args:
            registry: Model registry instance (MLflow or custom)
        """
        self.registry = registry
        logger.info("ModelRollback initialized")
    
    def get_model_versions(
        self,
        model_name: str,
        stage: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all versions of a model.
        
        Args:
            model_name: Name of the model
            stage: Filter by stage (Production, Staging, etc.)
            
        Returns:
            List of model version dictionaries
        """
        if not self.registry:
            logger.warning("Model registry not available")
            return []
        
        try:
            versions = self.registry.get_model_versions(model_name)
            
            if stage:
                versions = [v for v in versions if v.get('stage') == stage]
            
            # Sort by version number (descending)
            versions.sort(key=lambda x: int(x.get('version', 0)), reverse=True)
            
            return versions
        except Exception as e:
            logger.error(f"Failed to get model versions: {e}")
            return []
    
    def get_current_production_version(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get current production version of a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model version dictionary or None
        """
        versions = self.get_model_versions(model_name, stage='Production')
        return versions[0] if versions else None
    
    def rollback_model(
        self,
        model_name: str,
        target_version: Optional[int] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rollback model to a previous version.
        
        Args:
            model_name: Name of the model
            target_version: Version to rollback to (None = previous version)
            reason: Reason for rollback
            
        Returns:
            Dictionary with rollback result
        """
        logger.info(f"Rolling back model {model_name} to version {target_version}")
        
        if not self.registry:
            return {
                'success': False,
                'error': 'Model registry not available'
            }
        
        try:
            # Get current production version
            current = self.get_current_production_version(model_name)
            if not current:
                return {
                    'success': False,
                    'error': 'No production version found'
                }
            
            current_version = int(current.get('version', 0))
            
            # Determine target version
            if target_version is None:
                # Rollback to previous version
                all_versions = self.get_model_versions(model_name)
                if len(all_versions) < 2:
                    return {
                        'success': False,
                        'error': 'No previous version available'
                    }
                target_version = int(all_versions[1].get('version', 0))
            
            if target_version >= current_version:
                return {
                    'success': False,
                    'error': f'Target version {target_version} is not older than current {current_version}'
                }
            
            # Transition current version to Archived
            self.registry.transition_model_stage(
                model_name=model_name,
                version=str(current_version),
                stage='Archived'
            )
            
            # Transition target version to Production
            self.registry.transition_model_stage(
                model_name=model_name,
                version=str(target_version),
                stage='Production'
            )
            
            logger.info(f"Successfully rolled back {model_name} from v{current_version} to v{target_version}")
            
            return {
                'success': True,
                'model_name': model_name,
                'previous_version': current_version,
                'new_version': target_version,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to rollback model: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_rollback_history(self, model_name: str) -> List[Dict[str, Any]]:
        """
        Get rollback history for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            List of rollback events
        """
        # In production, this would query a rollback history table
        logger.info(f"Getting rollback history for {model_name}")
        return []


class DeploymentRollback:
    """
    Handles rollback of deployments to previous versions.
    
    Manages deployment history and provides rollback functionality
    when a deployment fails or causes issues.
    """
    
    def __init__(self, deployment_history_path: Optional[str] = None):
        """
        Initialize DeploymentRollback.
        
        Args:
            deployment_history_path: Path to deployment history file
        """
        self.history_path = Path(deployment_history_path) if deployment_history_path else None
        self.history: List[Dict[str, Any]] = []
        
        if self.history_path and self.history_path.exists():
            self._load_history()
        
        logger.info("DeploymentRollback initialized")
    
    def record_deployment(
        self,
        environment: str,
        version: str,
        image_tag: str,
        timestamp: Optional[datetime] = None
    ):
        """
        Record a deployment event.
        
        Args:
            environment: Deployment environment (staging/production)
            version: Application version
            image_tag: Docker image tag
            timestamp: Deployment timestamp (default: now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        deployment = {
            'environment': environment,
            'version': version,
            'image_tag': image_tag,
            'timestamp': timestamp.isoformat(),
            'status': 'deployed'
        }
        
        self.history.append(deployment)
        
        # Keep only last 50 deployments
        if len(self.history) > 50:
            self.history = self.history[-50:]
        
        if self.history_path:
            self._save_history()
        
        logger.info(f"Recorded deployment: {environment} v{version} ({image_tag})")
    
    def get_deployment_history(
        self,
        environment: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get deployment history.
        
        Args:
            environment: Filter by environment (None = all)
            limit: Maximum number of records to return
            
        Returns:
            List of deployment records
        """
        history = self.history.copy()
        
        if environment:
            history = [d for d in history if d['environment'] == environment]
        
        # Sort by timestamp (descending)
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return history[:limit]
    
    def get_current_deployment(self, environment: str) -> Optional[Dict[str, Any]]:
        """
        Get current deployment for an environment.
        
        Args:
            environment: Deployment environment
            
        Returns:
            Current deployment record or None
        """
        history = self.get_deployment_history(environment, limit=1)
        return history[0] if history else None
    
    def rollback_deployment(
        self,
        environment: str,
        target_version: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rollback deployment to a previous version.
        
        Args:
            environment: Deployment environment
            target_version: Version to rollback to (None = previous version)
            reason: Reason for rollback
            
        Returns:
            Dictionary with rollback result
        """
        logger.info(f"Rolling back {environment} deployment to version {target_version}")
        
        # Get current deployment
        current = self.get_current_deployment(environment)
        if not current:
            return {
                'success': False,
                'error': f'No current deployment found for {environment}'
            }
        
        # Determine target version
        if target_version is None:
            # Rollback to previous version
            history = self.get_deployment_history(environment, limit=2)
            if len(history) < 2:
                return {
                    'success': False,
                    'error': 'No previous deployment available'
                }
            target_version = history[1]['version']
        
        # Record rollback event
        rollback_record = {
            'environment': environment,
            'version': target_version,
            'image_tag': f"{target_version}",
            'timestamp': datetime.now().isoformat(),
            'status': 'rolled_back',
            'previous_version': current['version'],
            'reason': reason
        }
        
        self.history.append(rollback_record)
        
        if self.history_path:
            self._save_history()
        
        logger.info(f"Rolled back {environment} from {current['version']} to {target_version}")
        
        return {
            'success': True,
            'environment': environment,
            'previous_version': current['version'],
            'new_version': target_version,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def _load_history(self):
        """Load deployment history from file."""
        try:
            import json
            with open(self.history_path, 'r') as f:
                self.history = json.load(f)
            logger.info(f"Loaded {len(self.history)} deployment records")
        except Exception as e:
            logger.warning(f"Failed to load deployment history: {e}")
            self.history = []
    
    def _save_history(self):
        """Save deployment history to file."""
        try:
            import json
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_path, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.debug(f"Saved deployment history to {self.history_path}")
        except Exception as e:
            logger.error(f"Failed to save deployment history: {e}")


class RollbackManager:
    """
    Unified rollback manager for both models and deployments.
    
    Provides a single interface for rolling back models and deployments.
    """
    
    def __init__(
        self,
        model_registry=None,
        deployment_history_path: Optional[str] = None
    ):
        """
        Initialize RollbackManager.
        
        Args:
            model_registry: Model registry instance
            deployment_history_path: Path to deployment history file
        """
        self.model_rollback = ModelRollback(model_registry)
        self.deployment_rollback = DeploymentRollback(deployment_history_path)
        logger.info("RollbackManager initialized")
    
    def rollback_all(
        self,
        model_name: Optional[str] = None,
        environment: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rollback both model and deployment.
        
        Args:
            model_name: Model to rollback (None = skip model rollback)
            environment: Environment to rollback (None = skip deployment rollback)
            reason: Reason for rollback
            
        Returns:
            Dictionary with rollback results
        """
        results = {
            'model_rollback': None,
            'deployment_rollback': None,
            'success': True
        }
        
        # Rollback model if specified
        if model_name:
            model_result = self.model_rollback.rollback_model(
                model_name=model_name,
                reason=reason
            )
            results['model_rollback'] = model_result
            if not model_result.get('success'):
                results['success'] = False
        
        # Rollback deployment if specified
        if environment:
            deployment_result = self.deployment_rollback.rollback_deployment(
                environment=environment,
                reason=reason
            )
            results['deployment_rollback'] = deployment_result
            if not deployment_result.get('success'):
                results['success'] = False
        
        return results

