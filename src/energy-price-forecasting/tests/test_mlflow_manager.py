"""
Unit tests for MLflow manager.

Tests MLflowManager class.

Author: AI Assistant
Date: December 14, 2025
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mlflow_tracking.mlflow_manager import MLflowManager
    MANAGER_AVAILABLE = True
except ImportError:
    MANAGER_AVAILABLE = False
    pytest.skip("MLflow tracking module not available", allow_module_level=True)


class TestMLflowManagerInitialization:
    """Tests for MLflowManager initialization."""
    
    @patch('mlflow_tracking.mlflow_manager.mlflow')
    @patch('mlflow_tracking.mlflow_manager.MlflowClient')
    def test_init_basic(self, mock_client, mock_mlflow):
        """Test basic initialization."""
        mock_mlflow.get_tracking_uri.return_value = 'file:./mlruns'
        
        manager = MLflowManager()
        
        assert manager.tracking_uri is not None
        assert manager.client is not None
    
    @patch('mlflow_tracking.mlflow_manager.mlflow')
    @patch('mlflow_tracking.mlflow_manager.MlflowClient')
    def test_init_with_uri(self, mock_client, mock_mlflow):
        """Test initialization with tracking URI."""
        mock_mlflow.get_tracking_uri.return_value = 'http://localhost:5000'
        
        manager = MLflowManager(tracking_uri='http://localhost:5000')
        
        mock_mlflow.set_tracking_uri.assert_called_with('http://localhost:5000')
    
    @patch('mlflow_tracking.mlflow_manager.mlflow')
    @patch('mlflow_tracking.mlflow_manager.MlflowClient')
    def test_init_with_experiment(self, mock_client, mock_mlflow):
        """Test initialization with experiment name."""
        mock_mlflow.get_tracking_uri.return_value = 'file:./mlruns'
        mock_mlflow.get_experiment_by_name.return_value = None
        mock_mlflow.create_experiment.return_value = 'exp_123'
        
        manager = MLflowManager(experiment_name='test_experiment')
        
        mock_mlflow.set_experiment.assert_called_with('test_experiment')


class TestMLflowManagerSetupExperiment:
    """Tests for MLflowManager.setup_experiment()."""
    
    @patch('mlflow_tracking.mlflow_manager.mlflow')
    @patch('mlflow_tracking.mlflow_manager.MlflowClient')
    def test_setup_new_experiment(self, mock_client, mock_mlflow):
        """Test setting up a new experiment."""
        mock_mlflow.get_tracking_uri.return_value = 'file:./mlruns'
        mock_mlflow.get_experiment_by_name.return_value = None
        mock_mlflow.create_experiment.return_value = 'exp_123'
        
        manager = MLflowManager()
        experiment_id = manager.setup_experiment('new_experiment')
        
        assert experiment_id == 'exp_123'
        mock_mlflow.create_experiment.assert_called_once()
    
    @patch('mlflow_tracking.mlflow_manager.mlflow')
    @patch('mlflow_tracking.mlflow_manager.MlflowClient')
    def test_setup_existing_experiment(self, mock_client, mock_mlflow):
        """Test setting up an existing experiment."""
        mock_experiment = Mock()
        mock_experiment.experiment_id = 'exp_456'
        mock_mlflow.get_tracking_uri.return_value = 'file:./mlruns'
        mock_mlflow.get_experiment_by_name.return_value = mock_experiment
        
        manager = MLflowManager()
        experiment_id = manager.setup_experiment('existing_experiment')
        
        assert experiment_id == 'exp_456'
        mock_mlflow.create_experiment.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

