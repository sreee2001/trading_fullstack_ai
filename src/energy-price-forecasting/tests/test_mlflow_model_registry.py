"""
Unit tests for MLflow model registry.

Tests ModelRegistry class.

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
    from mlflow_tracking.model_registry import ModelRegistry
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    pytest.skip("MLflow tracking module not available", allow_module_level=True)


class TestModelRegistryInitialization:
    """Tests for ModelRegistry initialization."""
    
    @patch('mlflow_tracking.model_registry.MLflowManager')
    def test_init_basic(self, mock_manager_class):
        """Test basic initialization."""
        mock_manager = Mock()
        mock_manager.client = Mock()
        mock_manager_class.return_value = mock_manager
        
        registry = ModelRegistry()
        
        assert registry.manager is not None
        assert registry.client is not None


class TestModelRegistryOperations:
    """Tests for ModelRegistry operations."""
    
    @patch('mlflow_tracking.model_registry.MLflowManager')
    @patch('mlflow_tracking.model_registry.mlflow')
    def test_register_model(self, mock_mlflow, mock_manager_class):
        """Test registering a model."""
        mock_manager = Mock()
        mock_client = Mock()
        mock_manager.client = mock_client
        mock_manager_class.return_value = mock_manager
        
        mock_model_version = Mock()
        mock_model_version.version = '1'
        mock_mlflow.register_model.return_value = mock_model_version
        
        registry = ModelRegistry()
        version = registry.register_model('runs:/run_123/model', 'test_model')
        
        assert version == '1'
        mock_mlflow.register_model.assert_called_once()
    
    @patch('mlflow_tracking.model_registry.MLflowManager')
    def test_get_model_versions(self, mock_manager_class):
        """Test getting model versions."""
        mock_manager = Mock()
        mock_client = Mock()
        
        mock_version = Mock()
        mock_version.version = '1'
        mock_version.current_stage = 'None'
        mock_version.run_id = 'run_123'
        mock_version.creation_timestamp = 1234567890
        mock_version.status = 'READY'
        mock_version.tags = {}
        
        mock_client.search_model_versions.return_value = [mock_version]
        mock_manager.client = mock_client
        mock_manager_class.return_value = mock_manager
        
        registry = ModelRegistry()
        versions = registry.get_model_versions('test_model')
        
        assert len(versions) == 1
        assert versions[0]['version'] == '1'
    
    @patch('mlflow_tracking.model_registry.MLflowManager')
    def test_transition_model(self, mock_manager_class):
        """Test transitioning a model stage."""
        mock_manager = Mock()
        mock_client = Mock()
        mock_manager.client = mock_client
        mock_manager_class.return_value = mock_manager
        
        registry = ModelRegistry()
        registry.get_latest_versions = Mock(return_value=[{'version': '1'}])
        
        registry.transition_model('test_model', 'Production', version=1)
        
        mock_client.transition_model_version_stage.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

