"""
Unit tests for feature engineering time features.

Tests lag features, rolling statistics, seasonal decomposition, and date features.

Author: AI Assistant
Date: December 14, 2025
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_engineering.time_features import (
    create_lag_features,
    calculate_rolling_statistics,
    seasonal_decompose_features,
    create_date_features,
    add_all_time_features
)


@pytest.fixture
def sample_time_series():
    """Create sample time series data."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100)
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    
    return pd.DataFrame({
        'date': dates,
        'price': prices
    })


@pytest.fixture
def sample_seasonal_data():
    """Create sample data with seasonal pattern."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100)
    
    # Create seasonal pattern
    trend = np.linspace(100, 110, 100)
    seasonal = 5 * np.sin(np.arange(100) * 2 * np.pi / 30)  # 30-day cycle
    noise = np.random.randn(100) * 0.5
    prices = trend + seasonal + noise
    
    return pd.DataFrame({
        'date': dates,
        'price': prices
    })


class TestLagFeatures:
    """Tests for lag features."""
    
    def test_lag_basic(self, sample_time_series):
        """Test basic lag feature creation."""
        df = create_lag_features(sample_time_series, lags=[1, 7])
        
        assert 'price_lag_1' in df.columns
        assert 'price_lag_7' in df.columns
        assert len(df) == len(sample_time_series)
    
    def test_lag_values(self, sample_time_series):
        """Test lag values are correct."""
        df = create_lag_features(sample_time_series, lags=[1])
        
        # First value should be NaN
        assert pd.isna(df['price_lag_1'].iloc[0])
        
        # Second value should equal first price
        assert df['price_lag_1'].iloc[1] == sample_time_series['price'].iloc[0]
        
        # Third value should equal second price
        assert df['price_lag_1'].iloc[2] == sample_time_series['price'].iloc[1]
    
    def test_lag_default_periods(self, sample_time_series):
        """Test lag with default periods."""
        df = create_lag_features(sample_time_series)
        
        assert 'price_lag_1' in df.columns
        assert 'price_lag_7' in df.columns
        assert 'price_lag_30' in df.columns
    
    def test_lag_invalid_column(self, sample_time_series):
        """Test lag with invalid column."""
        with pytest.raises(ValueError):
            create_lag_features(sample_time_series, column='invalid_col')


class TestRollingStatistics:
    """Tests for rolling statistics."""
    
    def test_rolling_basic(self, sample_time_series):
        """Test basic rolling statistics."""
        df = calculate_rolling_statistics(sample_time_series, windows=[7], statistics=['mean'])
        
        assert 'price_roll_7_mean' in df.columns
        assert len(df) == len(sample_time_series)
    
    def test_rolling_multiple_stats(self, sample_time_series):
        """Test multiple rolling statistics."""
        df = calculate_rolling_statistics(
            sample_time_series,
            windows=[7],
            statistics=['mean', 'std', 'min', 'max']
        )
        
        assert 'price_roll_7_mean' in df.columns
        assert 'price_roll_7_std' in df.columns
        assert 'price_roll_7_min' in df.columns
        assert 'price_roll_7_max' in df.columns
    
    def test_rolling_mean_values(self, sample_time_series):
        """Test rolling mean values are correct."""
        df = calculate_rolling_statistics(sample_time_series, windows=[5], statistics=['mean'])
        
        # 5th value should equal mean of first 5 prices
        expected = sample_time_series['price'].iloc[0:5].mean()
        assert abs(df['price_roll_5_mean'].iloc[4] - expected) < 0.01
    
    def test_rolling_min_max_relationship(self, sample_time_series):
        """Test that rolling max >= rolling min."""
        df = calculate_rolling_statistics(sample_time_series, windows=[7], statistics=['min', 'max'])
        
        assert (df['price_roll_7_max'] >= df['price_roll_7_min']).all()
    
    def test_rolling_default_windows(self, sample_time_series):
        """Test rolling with default windows and statistics."""
        df = calculate_rolling_statistics(sample_time_series)
        
        assert 'price_roll_7_mean' in df.columns
        assert 'price_roll_30_std' in df.columns
        assert 'price_roll_90_min' in df.columns


class TestSeasonalDecomposition:
    """Tests for seasonal decomposition."""
    
    def test_seasonal_basic(self, sample_seasonal_data):
        """Test basic seasonal decomposition."""
        df = seasonal_decompose_features(sample_seasonal_data, period=30)
        
        assert 'price_trend' in df.columns
        assert 'price_seasonal' in df.columns
        assert 'price_residual' in df.columns
        assert len(df) == len(sample_seasonal_data)
    
    def test_seasonal_insufficient_data(self):
        """Test seasonal decomposition with insufficient data."""
        df = pd.DataFrame({'price': [100, 101, 102, 103, 104]})
        
        # Should not raise error, but fill with NaN
        result = seasonal_decompose_features(df, period=30)
        
        assert pd.isna(result['price_trend']).all()
        assert pd.isna(result['price_seasonal']).all()
        assert pd.isna(result['price_residual']).all()
    
    def test_seasonal_additive_model(self, sample_seasonal_data):
        """Test additive seasonal model."""
        df = seasonal_decompose_features(sample_seasonal_data, model='additive', period=30)
        
        # For additive model: original = trend + seasonal + residual
        df_clean = df.dropna()
        reconstructed = df_clean['price_trend'] + df_clean['price_seasonal'] + df_clean['price_residual']
        original = df_clean['price']
        
        assert np.allclose(reconstructed, original, rtol=0.01)
    
    def test_seasonal_invalid_column(self, sample_seasonal_data):
        """Test seasonal decomposition with invalid column."""
        with pytest.raises(ValueError):
            seasonal_decompose_features(sample_seasonal_data, column='invalid_col')


class TestDateFeatures:
    """Tests for date features."""
    
    def test_date_features_basic(self, sample_time_series):
        """Test basic date feature extraction."""
        df = create_date_features(sample_time_series)
        
        assert 'day_of_week' in df.columns
        assert 'month' in df.columns
        assert 'quarter' in df.columns
        assert 'year' in df.columns
        assert 'day_of_month' in df.columns
        assert 'week_of_year' in df.columns
        assert 'is_weekend' in df.columns
    
    def test_date_features_values(self):
        """Test date feature values are correct."""
        df = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-15', '2024-12-31'])
        })
        
        result = create_date_features(df)
        
        # Check specific values
        assert result['month'].iloc[0] == 1  # January
        assert result['month'].iloc[2] == 12  # December
        assert result['day_of_month'].iloc[1] == 15
        assert result['year'].iloc[0] == 2024
    
    def test_date_features_weekend(self):
        """Test weekend detection."""
        df = pd.DataFrame({
            'date': pd.to_datetime(['2024-12-14', '2024-12-15'])  # Saturday, Sunday
        })
        
        result = create_date_features(df)
        
        # Both should be weekends
        assert result['is_weekend'].iloc[0] == 1
        assert result['is_weekend'].iloc[1] == 1
    
    def test_date_features_day_of_week_range(self, sample_time_series):
        """Test day of week is in valid range."""
        df = create_date_features(sample_time_series)
        
        assert (df['day_of_week'] >= 0).all()
        assert (df['day_of_week'] <= 6).all()
    
    def test_date_features_month_range(self, sample_time_series):
        """Test month is in valid range."""
        df = create_date_features(sample_time_series)
        
        assert (df['month'] >= 1).all()
        assert (df['month'] <= 12).all()
    
    def test_date_features_quarter_range(self, sample_time_series):
        """Test quarter is in valid range."""
        df = create_date_features(sample_time_series)
        
        assert (df['quarter'] >= 1).all()
        assert (df['quarter'] <= 4).all()


class TestAddAllTimeFeatures:
    """Tests for add_all_time_features."""
    
    def test_add_all_basic(self, sample_time_series):
        """Test adding all time features."""
        df = add_all_time_features(sample_time_series, date_col='date')
        
        # Should have lag features
        assert 'price_lag_1' in df.columns
        
        # Should have rolling statistics
        assert 'price_roll_7_mean' in df.columns
        
        # Should have seasonal decomposition
        assert 'price_trend' in df.columns
        
        # Should have date features
        assert 'day_of_week' in df.columns
    
    def test_add_all_no_date_features(self, sample_time_series):
        """Test adding all time features without date features."""
        df = add_all_time_features(sample_time_series, date_col=None)
        
        # Should NOT have date features
        assert 'day_of_week' not in df.columns
        assert 'month' not in df.columns
    
    def test_add_all_feature_count(self, sample_time_series):
        """Test that correct number of features are added."""
        original_cols = len(sample_time_series.columns)
        df = add_all_time_features(sample_time_series, date_col='date')
        
        # Expected features:
        # Lags: 3 (1, 7, 30)
        # Rolling: 12 (3 windows × 4 stats)
        # Seasonal: 3 (trend, seasonal, residual)
        # Date: 7 (day_of_week, month, quarter, year, day_of_month, week_of_year, is_weekend)
        # Total: 25 features
        expected_features = 25
        actual_features = len(df.columns) - original_cols
        
        assert actual_features == expected_features


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_dataframe(self):
        """Test time features with empty DataFrame."""
        df = pd.DataFrame({'price': []})
        
        # Should not raise error
        result = create_lag_features(df, lags=[1])
        assert len(result) == 0
    
    def test_single_row(self):
        """Test time features with single row."""
        df = pd.DataFrame({'price': [100]})
        
        result = create_lag_features(df, lags=[1])
        
        # Lag should be NaN
        assert pd.isna(result['price_lag_1'].iloc[0])
    
    def test_nan_values_in_input(self, sample_time_series):
        """Test time features with NaN values in input."""
        df = sample_time_series.copy()
        df.loc[10:15, 'price'] = np.nan
        
        # Should handle NaN gracefully
        result = create_lag_features(df, lags=[1])
        
        # Lag should propagate NaN
        assert pd.isna(result['price_lag_1'].iloc[11:16]).any()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

