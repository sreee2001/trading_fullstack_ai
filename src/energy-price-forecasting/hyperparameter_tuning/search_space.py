"""
Hyperparameter Search Space Definitions.

Defines search spaces for different model types.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

from typing import Dict, List, Any, Optional
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HyperparameterSearchSpace:
    """
    Define and manage hyperparameter search spaces.
    
    Provides search space definitions for different model types
    including LSTM, ARIMA, and other forecasting models.
    
    Attributes:
        search_spaces: Dictionary of search spaces by model type
    
    Example:
        >>> space = HyperparameterSearchSpace()
        >>> lstm_space = space.get_search_space('lstm')
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize HyperparameterSearchSpace.
        
        Args:
            config_path: Path to YAML configuration file with search spaces
        """
        if config_path:
            self.search_spaces = self._load_from_file(config_path)
        else:
            self.search_spaces = self._default_search_spaces()
        
        logger.info(f"HyperparameterSearchSpace initialized with {len(self.search_spaces)} model types")
    
    def _load_from_file(self, config_path: str) -> Dict[str, Dict]:
        """Load search spaces from YAML file."""
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"Config file not found: {config_path}. Using default search spaces.")
            return self._default_search_spaces()
        
        try:
            with open(path, 'r') as f:
                spaces = yaml.safe_load(f)
            logger.info(f"Loaded search spaces from {config_path}")
            return spaces
        except Exception as e:
            logger.error(f"Failed to load search spaces: {e}. Using default.")
            return self._default_search_spaces()
    
    def _default_search_spaces(self) -> Dict[str, Dict]:
        """Get default search spaces for all model types."""
        return {
            'lstm': {
                'lstm_units': [50, 64, 128],
                'lstm_layers': [2, 3],
                'dropout_rate': [0.2, 0.3, 0.4],
                'learning_rate': [0.001, 0.005, 0.01],
                'sequence_length': [30, 60, 90],
                'batch_size': [16, 32, 64],
                'dense_units': [[25], [50], [25, 25]]
            },
            'arima': {
                'p': [0, 1, 2, 3],
                'd': [0, 1, 2],
                'q': [0, 1, 2, 3],
                'seasonal': [True, False],
                'seasonal_periods': [7, 12, 30]
            },
            'prophet': {
                'changepoint_prior_scale': [0.001, 0.01, 0.1, 0.5],
                'seasonality_prior_scale': [0.01, 0.1, 1.0, 10.0],
                'holidays_prior_scale': [0.01, 0.1, 1.0],
                'seasonality_mode': ['additive', 'multiplicative'],
                'growth': ['linear', 'logistic']
            },
            'exponential_smoothing': {
                'trend': ['add', 'mul', None],
                'seasonal': ['add', 'mul', None],
                'seasonal_periods': [7, 12, 30],
                'damped_trend': [True, False]
            }
        }
    
    def get_search_space(self, model_type: str) -> Dict[str, List[Any]]:
        """
        Get search space for a model type.
        
        Args:
            model_type: Type of model ('lstm', 'arima', 'prophet', etc.)
        
        Returns:
            Dictionary of parameter names to lists of values
        
        Raises:
            ValueError: If model_type not found
        """
        if model_type not in self.search_spaces:
            raise ValueError(
                f"Unknown model type: {model_type}. "
                f"Available types: {list(self.search_spaces.keys())}"
            )
        
        return self.search_spaces[model_type].copy()
    
    def add_search_space(self, model_type: str, search_space: Dict[str, List[Any]]):
        """
        Add or update search space for a model type.
        
        Args:
            model_type: Type of model
            search_space: Dictionary of parameter names to lists of values
        """
        self.search_spaces[model_type] = search_space
        logger.info(f"Added search space for {model_type}")
    
    def save(self, filepath: str):
        """
        Save search spaces to YAML file.
        
        Args:
            filepath: Path to save search spaces
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            yaml.dump(self.search_spaces, f, default_flow_style=False)
        
        logger.info(f"Search spaces saved to {filepath}")
    
    def to_dict(self) -> Dict[str, Dict]:
        """Get all search spaces as dictionary."""
        return self.search_spaces.copy()

