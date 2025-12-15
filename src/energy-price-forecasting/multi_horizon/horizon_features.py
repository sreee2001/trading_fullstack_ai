"""
Horizon-Specific Feature Engineering.

Provides feature engineering optimized for different forecast horizons.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

from feature_engineering.pipeline import FeatureEngineer

logger = logging.getLogger(__name__)


class HorizonFeatureEngineer:
    """
    Feature engineering optimized for different forecast horizons.
    
    Provides horizon-specific feature sets:
    - Short-term (1-day): Intraday features, recent trends
    - Medium-term (7-day): Weekly patterns, short-term seasonality
    - Long-term (30-day): Monthly seasonality, long-term trends
    
    Attributes:
        horizons: List of forecast horizons
        feature_engineers: Dictionary of FeatureEngineer instances per horizon
    
    Example:
        >>> fe = HorizonFeatureEngineer(horizons=[1, 7, 30])
        >>> features_1d = fe.transform(data, horizon=1)
        >>> features_7d = fe.transform(data, horizon=7)
    """
    
    def __init__(
        self,
        horizons: List[int] = [1, 7, 30],
        config_path: Optional[str] = None
    ):
        """
        Initialize HorizonFeatureEngineer.
        
        Args:
            horizons: List of forecast horizons in days
            config_path: Path to feature engineering configuration file
        """
        self.horizons = sorted(horizons)
        self.config_path = config_path
        
        # Create feature engineers for each horizon
        self.feature_engineers = {}
        
        for horizon in self.horizons:
            # Create config based on horizon
            config = self._get_horizon_config(horizon)
            
            fe = FeatureEngineer(
                config_path=config_path,
                **config
            )
            self.feature_engineers[horizon] = fe
        
        logger.info(f"HorizonFeatureEngineer initialized for horizons: {horizons}")
    
    def _get_horizon_config(self, horizon: int) -> Dict:
        """
        Get feature engineering configuration for a specific horizon.
        
        Args:
            horizon: Forecast horizon in days
        
        Returns:
            Configuration dictionary
        """
        config = {}
        
        if horizon == 1:
            # Short-term: Focus on recent trends and intraday patterns
            config = {
                'price_col': 'price',
                'date_col': 'date',
                'has_ohlc': True
            }
        elif horizon <= 7:
            # Medium-term: Weekly patterns, short-term seasonality
            config = {
                'price_col': 'price',
                'date_col': 'date',
                'has_ohlc': True
            }
        else:
            # Long-term: Monthly seasonality, long-term trends
            config = {
                'price_col': 'price',
                'date_col': 'date',
                'has_ohlc': True
            }
        
        return config
    
    def transform(
        self,
        data: pd.DataFrame,
        horizon: Optional[int] = None
    ) -> pd.DataFrame | Dict[int, pd.DataFrame]:
        """
        Transform data with horizon-specific features.
        
        Args:
            data: Input DataFrame
            horizon: Specific horizon to transform for (None = all horizons)
        
        Returns:
            Transformed DataFrame(s)
        """
        if horizon is not None:
            if horizon not in self.feature_engineers:
                raise ValueError(f"Horizon {horizon} not in configured horizons: {self.horizons}")
            
            fe = self.feature_engineers[horizon]
            return fe.transform(data)
        else:
            # Transform for all horizons
            results = {}
            for h, fe in self.feature_engineers.items():
                results[h] = fe.transform(data)
            return results
    
    def get_feature_importance(
        self,
        horizon: Optional[int] = None
    ) -> pd.DataFrame | Dict[int, pd.DataFrame]:
        """
        Get feature importance for horizon(s).
        
        Args:
            horizon: Specific horizon (None = all horizons)
        
        Returns:
            Feature importance DataFrame(s)
        """
        if horizon is not None:
            if horizon not in self.feature_engineers:
                raise ValueError(f"Horizon {horizon} not in configured horizons: {self.horizons}")
            
            fe = self.feature_engineers[horizon]
            return fe.get_feature_importance()
        else:
            # Get importance for all horizons
            results = {}
            for h, fe in self.feature_engineers.items():
                results[h] = fe.get_feature_importance()
            return results

