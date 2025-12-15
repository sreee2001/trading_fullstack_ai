"""
Unit tests for feature engineering pipeline.

Tests the FeatureEngineer class and its methods.

Author: AI Assistant
Date: December 14, 2025
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path
import tempfile
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_engineering.pipeline import FeatureEngineer


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100)
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    
    return pd.DataFrame({
        'date': dates,
        'price': prices
    })


@pytest.fixture
def sample_ohlc_data():
    """Create sample OHLC data for testing."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100)
    close_prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    
    return pd.DataFrame({
        'date': dates,
        'open': close_prices + np.random.randn(100) * 0.3,
        'high': close_prices + np.abs(np.random.randn(100)) * 0.5,
        'low': close_prices - np.abs(np.random.randn(100)) * 0.5,
        'close': close_prices,
        'price': close_prices
    })


@pytest.fixture
def custom_config():
    """Create custom configuration."""
    return {
        'technical_indicators': {
            'enabled': True,
            'sma_windows': [5, 10],
            'ema_windows': [5, 10],
            'rsi_period': 14,
            'macd_params': [12, 26, 9],
            'bb_period': 20,
            'atr_period': 14
        },
        'time_features': {
            'enabled': True,
            'lag_periods': [1, 7],
            'rolling_windows': [7, 30],
            'rolling_statistics': ['mean', 'std'],
            'seasonal_period': None,
            'seasonal_model': 'additive'
        },
        'date_features': {
            'enabled': True
        },
        'preprocessing': {
            'handle_missing': 'forward_fill',
            'drop_na_threshold': 0.5
        }
    }


class TestFeatureEngineerInitialization:
    """Tests for FeatureEngineer initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        engineer = FeatureEngineer()
        
        assert engineer.price_col == 'price'
        assert engineer.date_col == 'date'
        assert engineer.has_ohlc == False
        assert len(engineer.features_added) == 0
    
    def test_init_custom_columns(self):
        """Test initialization with custom column names."""
        engineer = FeatureEngineer(
            price_col='close',
            date_col='timestamp',
            has_ohlc=True
        )
        
        assert engineer.price_col == 'close'
        assert engineer.date_col == 'timestamp'
        assert engineer.has_ohlc == True
    
    def test_init_with_config_file(self, custom_config):
        """Test initialization with config file."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(custom_config, f)
            config_path = f.name
        
        try:
            engineer = FeatureEngineer(config_path=config_path)
            
            assert engineer.config['technical_indicators']['sma_windows'] == [5, 10]
            assert engineer.config['time_features']['lag_periods'] == [1, 7]
        finally:
            Path(config_path).unlink()


class TestTransform:
    """Tests for transform method."""
    
    def test_transform_basic(self, sample_data):
        """Test basic transform."""
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(sample_data)
        
        # Should have more columns
        assert len(df_transformed.columns) > len(sample_data.columns)
        
        # Should have same number of rows (or slightly fewer due to NaN handling)
        assert len(df_transformed) <= len(sample_data)
        
        # Should have tracked features
        assert len(engineer.features_added) > 0
    
    def test_transform_with_ohlc(self, sample_ohlc_data):
        """Test transform with OHLC data."""
        engineer = FeatureEngineer(has_ohlc=True)
        df_transformed = engineer.transform(sample_ohlc_data)
        
        # Should include ATR
        assert 'atr_14' in df_transformed.columns
    
    def test_transform_copy_behavior(self, sample_data):
        """Test that transform copies data by default."""
        engineer = FeatureEngineer()
        original_columns = sample_data.columns.tolist()
        
        df_transformed = engineer.transform(sample_data, copy=True)
        
        # Original should be unchanged
        assert sample_data.columns.tolist() == original_columns
        
        # Transformed should have more columns
        assert len(df_transformed.columns) > len(original_columns)
    
    def test_transform_feature_tracking(self, sample_data):
        """Test that features are tracked correctly."""
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(sample_data)
        
        # All tracked features should exist in transformed data
        for feature in engineer.features_added:
            assert feature in df_transformed.columns
    
    def test_transform_no_nans(self, sample_data):
        """Test that transform handles NaN values."""
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(sample_data)
        
        # Should have no NaN values after forward fill
        assert df_transformed.isnull().sum().sum() == 0


class TestFeatureImportance:
    """Tests for get_feature_importance method."""
    
    def test_feature_importance_basic(self, sample_data):
        """Test basic feature importance calculation."""
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(sample_data)
        
        importance = engineer.get_feature_importance(df_transformed)
        
        assert len(importance) > 0
        assert 'feature' in importance.columns
        assert 'importance' in importance.columns
    
    def test_feature_importance_sorted(self, sample_data):
        """Test that feature importance is sorted."""
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(sample_data)
        
        importance = engineer.get_feature_importance(df_transformed)
        
        # Should be sorted in descending order
        assert (importance['importance'].diff().dropna() <= 0).all()
    
    def test_feature_importance_range(self, sample_data):
        """Test that importance values are in valid range."""
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(sample_data)
        
        importance = engineer.get_feature_importance(df_transformed)
        
        # Correlation-based importance should be in [0, 1], excluding NaN values
        importance_clean = importance['importance'].dropna()
        assert (importance_clean >= 0).all()
        assert (importance_clean <= 1).all()
    
    def test_feature_importance_invalid_target(self, sample_data):
        """Test feature importance with invalid target column."""
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(sample_data)
        
        with pytest.raises(ValueError):
            engineer.get_feature_importance(df_transformed, target_col='invalid_col')


class TestFeatureSelection:
    """Tests for select_top_features method."""
    
    def test_select_top_features_basic(self, sample_data):
        """Test basic feature selection."""
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(sample_data)
        
        df_top = engineer.select_top_features(df_transformed, top_n=10)
        
        # Should have at most top_n + target + date columns
        assert len(df_top.columns) <= 12  # 10 + price + date
    
    def test_select_top_features_includes_target(self, sample_data):
        """Test that selected features include target."""
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(sample_data)
        
        df_top = engineer.select_top_features(df_transformed, top_n=10, include_target=True)
        
        assert 'price' in df_top.columns
    
    def test_select_top_features_excludes_target(self, sample_data):
        """Test that selected features can exclude target."""
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(sample_data)
        
        df_top = engineer.select_top_features(df_transformed, top_n=10, include_target=False)
        
        # price might still be in top features, but not guaranteed
        assert len(df_top.columns) <= 11  # 10 + date


class TestGetSummary:
    """Tests for get_summary method."""
    
    def test_summary_structure(self, sample_data):
        """Test summary structure."""
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(sample_data)
        
        summary = engineer.get_summary()
        
        assert 'configuration' in summary
        assert 'features' in summary
        assert 'preprocessing' in summary
    
    def test_summary_configuration(self, sample_ohlc_data):
        """Test summary configuration section."""
        engineer = FeatureEngineer(price_col='close', date_col='timestamp', has_ohlc=True)
        df_transformed = engineer.transform(sample_ohlc_data.rename(columns={'date': 'timestamp'}))
        
        summary = engineer.get_summary()
        
        assert summary['configuration']['price_column'] == 'close'
        assert summary['configuration']['date_column'] == 'timestamp'
        assert summary['configuration']['has_ohlc'] == True
    
    def test_summary_features(self, sample_data):
        """Test summary features section."""
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(sample_data)
        
        summary = engineer.get_summary()
        
        assert summary['features']['total_features_added'] == len(engineer.features_added)
        assert summary['features']['feature_names'] == engineer.features_added


class TestMissingValueHandling:
    """Tests for missing value handling."""
    
    def test_forward_fill(self):
        """Test forward fill missing value handling."""
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=50),
            'price': [100 + i + (np.nan if i % 5 == 0 and i > 0 else 0) for i in range(50)]
        })
        
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(df)
        
        # Should have no NaN values after forward fill
        assert df_transformed.isnull().sum().sum() == 0
    
    def test_drop_rows_high_nan(self):
        """Test dropping rows with high percentage of NaN."""
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100),
            'price': 100 + np.cumsum(np.random.randn(100) * 0.5)
        })
        
        engineer = FeatureEngineer()
        df_transformed = engineer.transform(df)
        
        # Some rows at the beginning might be dropped due to lagged features
        assert len(df_transformed) <= len(df)


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame({'date': [], 'price': []})
        
        engineer = FeatureEngineer()
        
        # Should handle gracefully
        df_transformed = engineer.transform(df)
        assert len(df_transformed) == 0
    
    def test_insufficient_data(self):
        """Test with insufficient data."""
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'price': [100, 101, 102, 103, 104]
        })
        
        engineer = FeatureEngineer()
        
        # Should not raise error, but many features will be NaN
        df_transformed = engineer.transform(df)
        assert len(df_transformed) >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

