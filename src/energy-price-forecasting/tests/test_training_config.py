"""
Unit tests for training configuration.

Tests TrainingConfig class.

Author: AI Assistant
Date: December 14, 2025
"""

import pytest
import tempfile
import os
import yaml
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from training.config import TrainingConfig
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    pytest.skip("Training module not available", allow_module_level=True)


class TestTrainingConfigInitialization:
    """Tests for TrainingConfig initialization."""
    
    def test_init_default(self):
        """Test initialization with default config."""
        config = TrainingConfig()
        
        assert config.config is not None
        assert 'data_splitting' in config.config
    
    def test_init_with_dict(self):
        """Test initialization with config dictionary."""
        config_dict = {
            'data_splitting': {
                'train_ratio': 0.8,
                'val_ratio': 0.1,
                'test_ratio': 0.1
            }
        }
        
        config = TrainingConfig(config_dict=config_dict)
        
        assert config.get('data_splitting', 'train_ratio') == 0.8
    
    def test_init_with_file(self):
        """Test initialization with config file."""
        config_dict = {
            'data_splitting': {
                'train_ratio': 0.75
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            config_path = f.name
        
        try:
            config = TrainingConfig(config_path=config_path)
            assert config.get('data_splitting', 'train_ratio') == 0.75
        finally:
            os.unlink(config_path)


class TestTrainingConfigGetSet:
    """Tests for TrainingConfig.get() and set()."""
    
    def test_get_basic(self):
        """Test getting configuration values."""
        config = TrainingConfig()
        
        train_ratio = config.get('data_splitting', 'train_ratio')
        
        assert train_ratio == 0.7
    
    def test_get_default(self):
        """Test getting with default value."""
        config = TrainingConfig()
        
        value = config.get('nonexistent', 'key', default='default_value')
        
        assert value == 'default_value'
    
    def test_set_basic(self):
        """Test setting configuration values."""
        config = TrainingConfig()
        
        config.set('data_splitting', 'train_ratio', 0.8)
        
        assert config.get('data_splitting', 'train_ratio') == 0.8


class TestTrainingConfigSave:
    """Tests for TrainingConfig.save()."""
    
    def test_save_config(self):
        """Test saving configuration."""
        config = TrainingConfig()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, 'test_config.yaml')
            config.save(config_path)
            
            assert os.path.exists(config_path)
            
            # Verify it can be loaded
            loaded_config = TrainingConfig(config_path=config_path)
            assert loaded_config.get('data_splitting', 'train_ratio') == 0.7


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

