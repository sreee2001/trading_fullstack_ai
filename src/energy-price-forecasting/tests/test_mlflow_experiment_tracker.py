"""
Unit tests for MLflow experiment tracker.

Tests ExperimentTracker class.

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
    from mlflow_tracking.experiment_tracker import ExperimentTracker
    TRACKER_AVAILABLE = True
except ImportError:
    TRACKER_AVAILABLE = False
    pytest.skip("MLflow tracking module not available", allow_module_level=True)


class TestExperimentTrackerInitialization:
    """Tests for ExperimentTracker initialization."""
    
    @patch('mlflow_tracking.experiment_tracker.MLflowManager')
    def test_init_basic(self, mock_manager_class):
        """Test basic initialization."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        tracker = ExperimentTracker('test_experiment')
        
        assert tracker.experiment_name == 'test_experiment'
        assert tracker.manager is not None


class TestExperimentTrackerRunManagement:
    """Tests for ExperimentTracker run management."""
    
    @patch('mlflow_tracking.experiment_tracker.MLflowManager')
    @patch('mlflow_tracking.experiment_tracker.mlflow')
    def test_start_run(self, mock_mlflow, mock_manager_class):
        """Test starting a run."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        mock_run = MagicMock()
        mock_run.info.run_id = 'run_123'
        mock_mlflow.start_run.return_value.__enter__ = Mock(return_value=mock_run)
        mock_mlflow.start_run.return_value.__exit__ = Mock(return_value=None)
        
        tracker = ExperimentTracker('test_experiment')
        tracker.start_run('test_run')
        
        mock_mlflow.start_run.assert_called_once()
        assert tracker.run_id == 'run_123'
    
    @patch('mlflow_tracking.experiment_tracker.MLflowManager')
    @patch('mlflow_tracking.experiment_tracker.mlflow')
    def test_end_run(self, mock_mlflow, mock_manager_class):
        """Test ending a run."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        mock_run = MagicMock()
        mock_run.info.run_id = 'run_123'
        mock_mlflow.start_run.return_value = mock_run
        
        tracker = ExperimentTracker('test_experiment')
        tracker.active_run = mock_run
        tracker.run_id = 'run_123'
        
        tracker.end_run()
        
        mock_mlflow.end_run.assert_called_once()


class TestExperimentTrackerLogging:
    """Tests for ExperimentTracker logging methods."""
    
    @patch('mlflow_tracking.experiment_tracker.MLflowManager')
    @patch('mlflow_tracking.experiment_tracker.mlflow')
    def test_log_params(self, mock_mlflow, mock_manager_class):
        """Test logging parameters."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        mock_run = MagicMock()
        tracker = ExperimentTracker('test_experiment')
        tracker.active_run = mock_run
        
        params = {'learning_rate': 0.001, 'batch_size': 32}
        tracker.log_params(params)
        
        mock_mlflow.log_params.assert_called_once()
    
    @patch('mlflow_tracking.experiment_tracker.MLflowManager')
    @patch('mlflow_tracking.experiment_tracker.mlflow')
    def test_log_metrics(self, mock_mlflow, mock_manager_class):
        """Test logging metrics."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        mock_run = MagicMock()
        tracker = ExperimentTracker('test_experiment')
        tracker.active_run = mock_run
        
        metrics = {'rmse': 2.5, 'mae': 1.8}
        tracker.log_metrics(metrics)
        
        mock_mlflow.log_metrics.assert_called_once()
    
    @patch('mlflow_tracking.experiment_tracker.MLflowManager')
    @patch('mlflow_tracking.experiment_tracker.mlflow')
    def test_log_params_no_run(self, mock_mlflow, mock_manager_class):
        """Test logging parameters without active run."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        tracker = ExperimentTracker('test_experiment')
        
        with pytest.raises(RuntimeError, match="No active run"):
            tracker.log_params({'param': 'value'})


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

