"""
Unit tests for hyperparameter search space.

Tests HyperparameterSearchSpace class.

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
    from hyperparameter_tuning.search_space import HyperparameterSearchSpace
    SPACE_AVAILABLE = True
except ImportError:
    SPACE_AVAILABLE = False
    pytest.skip("Hyperparameter tuning module not available", allow_module_level=True)


class TestHyperparameterSearchSpaceInitialization:
    """Tests for HyperparameterSearchSpace initialization."""
    
    def test_init_default(self):
        """Test initialization with default search spaces."""
        space = HyperparameterSearchSpace()
        
        assert space.search_spaces is not None
        assert 'lstm' in space.search_spaces
        assert 'arima' in space.search_spaces
    
    def test_init_with_file(self):
        """Test initialization with config file."""
        config_dict = {
            'lstm': {
                'lstm_units': [50, 64]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            config_path = f.name
        
        try:
            space = HyperparameterSearchSpace(config_path=config_path)
            assert space.get_search_space('lstm')['lstm_units'] == [50, 64]
        finally:
            os.unlink(config_path)


class TestHyperparameterSearchSpaceGet:
    """Tests for HyperparameterSearchSpace.get_search_space()."""
    
    def test_get_lstm_space(self):
        """Test getting LSTM search space."""
        space = HyperparameterSearchSpace()
        lstm_space = space.get_search_space('lstm')
        
        assert 'lstm_units' in lstm_space
        assert 'lstm_layers' in lstm_space
        assert isinstance(lstm_space['lstm_units'], list)
    
    def test_get_arima_space(self):
        """Test getting ARIMA search space."""
        space = HyperparameterSearchSpace()
        arima_space = space.get_search_space('arima')
        
        assert 'p' in arima_space
        assert 'd' in arima_space
        assert 'q' in arima_space
    
    def test_get_unknown_model(self):
        """Test getting search space for unknown model."""
        space = HyperparameterSearchSpace()
        
        with pytest.raises(ValueError, match="Unknown model type"):
            space.get_search_space('unknown_model')


class TestHyperparameterSearchSpaceAdd:
    """Tests for HyperparameterSearchSpace.add_search_space()."""
    
    def test_add_search_space(self):
        """Test adding a new search space."""
        space = HyperparameterSearchSpace()
        
        new_space = {
            'param1': [1, 2, 3],
            'param2': [0.1, 0.2]
        }
        
        space.add_search_space('new_model', new_space)
        
        assert space.get_search_space('new_model') == new_space


class TestHyperparameterSearchSpaceSave:
    """Tests for HyperparameterSearchSpace.save()."""
    
    def test_save_search_spaces(self):
        """Test saving search spaces to file."""
        space = HyperparameterSearchSpace()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, 'test_config.yaml')
            space.save(config_path)
            
            assert os.path.exists(config_path)
            
            # Verify it can be loaded
            loaded_space = HyperparameterSearchSpace(config_path=config_path)
            assert 'lstm' in loaded_space.search_spaces


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

