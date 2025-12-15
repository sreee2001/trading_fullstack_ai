"""
Feature Engineering Pipeline.

Main orchestrator class that combines all feature engineering transformations
into a single, configurable pipeline.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
import yaml
from pathlib import Path

from .indicators import add_all_technical_indicators
from .time_features import add_all_time_features

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Main feature engineering pipeline class.
    
    Orchestrates all feature engineering transformations including:
    - Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR)
    - Time-based features (lags, rolling statistics, seasonal decomposition)
    - Date features (day of week, month, etc.)
    
    Attributes:
        config: Configuration dictionary
        price_col: Column name for price data
        date_col: Column name for date data
        has_ohlc: Whether data includes OHLC columns
        features_added: List of feature columns added
    
    Example:
        >>> df = pd.DataFrame({
        ...     'date': pd.date_range('2024-01-01', periods=100),
        ...     'price': np.random.randn(100) + 100
        ... })
        >>> engineer = FeatureEngineer()
        >>> df_enriched = engineer.transform(df)
        >>> print(f"Original: {len(df.columns)} columns")
        >>> print(f"Enriched: {len(df_enriched.columns)} columns")
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        price_col: str = 'price',
        date_col: Optional[str] = 'date',
        has_ohlc: bool = False
    ):
        """
        Initialize Feature Engineer.
        
        Args:
            config_path: Path to configuration YAML file (optional)
            price_col: Column name for price data (default: 'price')
            date_col: Column name for date data (default: 'date')
            has_ohlc: Whether data includes OHLC columns (default: False)
        """
        self.price_col = price_col
        self.date_col = date_col
        self.has_ohlc = has_ohlc
        self.features_added = []
        
        # Load configuration
        if config_path:
            self.config = self._load_config(config_path)
        else:
            self.config = self._default_config()
        
        logger.info(f"FeatureEngineer initialized with price_col='{price_col}', date_col='{date_col}'")
    
    def _load_config(self, config_path: str) -> Dict:
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
            'technical_indicators': {
                'enabled': True,
                'sma_windows': [5, 10, 20, 50, 200],
                'ema_windows': [5, 10, 20, 50, 200],
                'rsi_period': 14,
                'macd_params': [12, 26, 9],
                'bb_period': 20,
                'atr_period': 14
            },
            'time_features': {
                'enabled': True,
                'lag_periods': [1, 7, 30],
                'rolling_windows': [7, 30, 90],
                'rolling_statistics': ['mean', 'std', 'min', 'max'],
                'seasonal_period': None,  # Auto-detect
                'seasonal_model': 'additive'
            },
            'date_features': {
                'enabled': True
            },
            'preprocessing': {
                'handle_missing': 'forward_fill',  # Options: 'forward_fill', 'drop', 'mean', 'zero'
                'drop_na_threshold': 0.5  # Drop rows with more than 50% NaN
            }
        }
    
    def transform(
        self,
        df: pd.DataFrame,
        copy: bool = True,
        verbose: bool = True
    ) -> pd.DataFrame:
        """
        Apply all feature engineering transformations.
        
        Args:
            df: Input DataFrame with price data
            copy: Whether to copy DataFrame (default: True)
            verbose: Whether to log progress (default: True)
        
        Returns:
            DataFrame with all features added
        
        Example:
            >>> df = pd.DataFrame({'price': np.random.randn(100) + 100})
            >>> engineer = FeatureEngineer()
            >>> df_transformed = engineer.transform(df)
            >>> print(f"Added {len(engineer.features_added)} features")
        """
        if copy:
            df_result = df.copy()
        else:
            df_result = df
        
        original_columns = set(df_result.columns)
        
        if verbose:
            logger.info(f"Starting feature engineering on DataFrame with shape {df_result.shape}")
        
        # Add technical indicators
        if self.config['technical_indicators']['enabled']:
            if verbose:
                logger.info("Adding technical indicators...")
            
            ti_config = self.config['technical_indicators']
            df_result = add_all_technical_indicators(
                df_result,
                price_col=self.price_col,
                has_ohlc=self.has_ohlc,
                sma_windows=ti_config['sma_windows'],
                ema_windows=ti_config['ema_windows'],
                rsi_period=ti_config['rsi_period'],
                macd_params=tuple(ti_config['macd_params']),
                bb_period=ti_config['bb_period'],
                atr_period=ti_config['atr_period']
            )
        
        # Add time-based features
        if self.config['time_features']['enabled']:
            if verbose:
                logger.info("Adding time-based features...")
            
            tf_config = self.config['time_features']
            df_result = add_all_time_features(
                df_result,
                price_col=self.price_col,
                date_col=self.date_col if self.config['date_features']['enabled'] else None,
                lag_periods=tf_config['lag_periods'],
                rolling_windows=tf_config['rolling_windows'],
                rolling_statistics=tf_config['rolling_statistics'],
                seasonal_period=tf_config['seasonal_period'],
                seasonal_model=tf_config['seasonal_model']
            )
        
        # Handle missing values
        df_result = self._handle_missing_values(df_result)
        
        # Track features added
        self.features_added = list(set(df_result.columns) - original_columns)
        
        if verbose:
            logger.info(f"Feature engineering complete. Added {len(self.features_added)} features.")
            logger.info(f"Final DataFrame shape: {df_result.shape}")
        
        return df_result
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values according to configuration.
        
        Args:
            df: DataFrame with potential NaN values
        
        Returns:
            DataFrame with missing values handled
        """
        method = self.config['preprocessing']['handle_missing']
        threshold = self.config['preprocessing']['drop_na_threshold']
        
        # Drop rows with too many NaN values
        nan_pct = df.isnull().sum(axis=1) / len(df.columns)
        rows_to_drop = nan_pct > threshold
        if rows_to_drop.any():
            n_dropped = rows_to_drop.sum()
            df = df[~rows_to_drop]
            logger.info(f"Dropped {n_dropped} rows with >{threshold*100}% missing values")
        
        # Handle remaining NaN values
        if method == 'forward_fill':
            df = df.fillna(method='ffill')
        elif method == 'drop':
            df = df.dropna()
        elif method == 'mean':
            df = df.fillna(df.mean())
        elif method == 'zero':
            df = df.fillna(0)
        else:
            logger.warning(f"Unknown missing value method: {method}. Using forward fill.")
            df = df.fillna(method='ffill')
        
        # Final check: fill any remaining NaN with 0
        if df.isnull().any().any():
            remaining_nan = df.isnull().sum().sum()
            logger.warning(f"Filling {remaining_nan} remaining NaN values with 0")
            df = df.fillna(0)
        
        return df
    
    def get_feature_importance(
        self,
        df: pd.DataFrame,
        target_col: str = 'price'
    ) -> pd.DataFrame:
        """
        Calculate feature importance using correlation with target.
        
        Args:
            df: DataFrame with features
            target_col: Target column name (default: 'price')
        
        Returns:
            DataFrame with feature names and importance scores, sorted by importance
        
        Example:
            >>> df_enriched = engineer.transform(df)
            >>> importance = engineer.get_feature_importance(df_enriched)
            >>> print(importance.head(10))  # Top 10 most important features
        """
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in DataFrame")
        
        # Calculate correlation with target
        correlations = df.corr()[target_col].abs()
        
        # Remove target itself
        correlations = correlations.drop(target_col)
        
        # Sort by importance
        importance_df = pd.DataFrame({
            'feature': correlations.index,
            'importance': correlations.values
        }).sort_values('importance', ascending=False)
        
        logger.info(f"Calculated feature importance for {len(importance_df)} features")
        
        return importance_df.reset_index(drop=True)
    
    def select_top_features(
        self,
        df: pd.DataFrame,
        target_col: str = 'price',
        top_n: int = 20,
        include_target: bool = True
    ) -> pd.DataFrame:
        """
        Select top N most important features.
        
        Args:
            df: DataFrame with features
            target_col: Target column name (default: 'price')
            top_n: Number of top features to select (default: 20)
            include_target: Whether to include target column (default: True)
        
        Returns:
            DataFrame with only top N features (and optionally target)
        
        Example:
            >>> df_enriched = engineer.transform(df)
            >>> df_top = engineer.select_top_features(df_enriched, top_n=15)
            >>> print(f"Selected {len(df_top.columns)} features")
        """
        importance = self.get_feature_importance(df, target_col)
        
        # Get top feature names
        top_features = importance.head(top_n)['feature'].tolist()
        
        # Add target if requested
        if include_target:
            top_features.append(target_col)
        
        # Add date column if it exists
        if self.date_col and self.date_col in df.columns:
            top_features.append(self.date_col)
        
        logger.info(f"Selected top {top_n} features out of {len(importance)} total features")
        
        return df[top_features]
    
    def get_summary(self) -> Dict:
        """
        Get summary of feature engineering configuration and results.
        
        Returns:
            Dictionary with configuration and feature counts
        """
        return {
            'configuration': {
                'price_column': self.price_col,
                'date_column': self.date_col,
                'has_ohlc': self.has_ohlc,
                'technical_indicators_enabled': self.config['technical_indicators']['enabled'],
                'time_features_enabled': self.config['time_features']['enabled'],
                'date_features_enabled': self.config['date_features']['enabled']
            },
            'features': {
                'total_features_added': len(self.features_added),
                'feature_names': self.features_added
            },
            'preprocessing': self.config['preprocessing']
        }

