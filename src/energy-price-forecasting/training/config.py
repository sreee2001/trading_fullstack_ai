"""
Training Configuration Management.

Manages training configuration for models.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TrainingConfig:
    """
    Training configuration manager.
    
    Loads and manages training configuration from YAML files or dictionaries.
    
    Attributes:
        config: Configuration dictionary
    
    Example:
        >>> config = TrainingConfig('training_config.yaml')
        >>> train_ratio = config.get('data_splitting', 'train_ratio')
    """
    
    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[Dict] = None):
        """
        Initialize TrainingConfig.
        
        Args:
            config_path: Path to YAML configuration file
            config_dict: Configuration dictionary (alternative to file)
        """
        if config_path:
            self.config = self._load_from_file(config_path)
        elif config_dict:
            self.config = config_dict
        else:
            self.config = self._default_config()
        
        logger.info("TrainingConfig initialized")
    
    def _load_from_file(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"Config file not found: {config_path}. Using default config.")
            return self._default_config()
        
        try:
            with open(path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}. Using default config.")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Get default configuration."""
        return {
            'data_splitting': {
                'train_ratio': 0.7,
                'val_ratio': 0.15,
                'test_ratio': 0.15,
                'date_column': None
            },
            'evaluation': {
                'metrics': ['MAE', 'RMSE', 'MAPE', 'R2', 'Directional_Accuracy']
            },
            'cross_validation': {
                'enabled': False,
                'n_splits': 5,
                'test_size': 30,
                'gap': 0,
                'expanding_window': True
            },
            'model_training': {
                'epochs': 50,
                'batch_size': 32,
                'early_stopping': {
                    'enabled': True,
                    'patience': 10,
                    'monitor': 'val_loss'
                },
                'learning_rate': {
                    'initial': 0.001,
                    'scheduling': {
                        'enabled': True,
                        'factor': 0.5,
                        'patience': 5
                    }
                }
            }
        }
    
    def get(self, *keys, default=None) -> Any:
        """
        Get configuration value by nested keys.
        
        Args:
            *keys: Nested keys to access (e.g., 'data_splitting', 'train_ratio')
            default: Default value if key not found
        
        Returns:
            Configuration value
        
        Example:
            >>> train_ratio = config.get('data_splitting', 'train_ratio')
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, *keys, value: Any):
        """
        Set configuration value by nested keys.
        
        Args:
            *keys: Nested keys to set
            value: Value to set
        
        Example:
            >>> config.set('data_splitting', 'train_ratio', 0.8)
        """
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
    
    def save(self, filepath: str):
        """
        Save configuration to YAML file.
        
        Args:
            filepath: Path to save configuration
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
        
        logger.info(f"Configuration saved to {filepath}")
    
    def to_dict(self) -> Dict:
        """Get configuration as dictionary."""
        return self.config.copy()

