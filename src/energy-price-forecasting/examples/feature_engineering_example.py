"""
Feature Engineering Example Script.

Demonstrates the complete feature engineering pipeline using real data
from the database.

Author: AI Assistant
Date: December 14, 2025
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_engineering import FeatureEngineer
from database.operations import get_price_data
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_sample_data_from_db():
    """Load sample price data from database."""
    print("\n" + "="*80)
    print("LOADING DATA FROM DATABASE")
    print("="*80)
    
    try:
        # Get last 90 days of WTI_CRUDE data from Yahoo Finance
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        df = get_price_data(
            commodity_symbol='WTI_CRUDE',
            source_name='YAHOO_FINANCE',
            start_date=start_date,
            end_date=end_date
        )
        
        if df.empty:
            print("No data found in database. Creating synthetic data...")
            return create_synthetic_data()
        
        print(f"Loaded {len(df)} records from database")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"Columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"Error loading from database: {e}")
        print("Creating synthetic data instead...")
        return create_synthetic_data()


def create_synthetic_data():
    """Create synthetic price data for demonstration."""
    print("\nCreating synthetic price data...")
    
    # Generate 100 days of data
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    
    # Create realistic-looking price series
    np.random.seed(42)
    trend = np.linspace(70, 75, 100)
    seasonal = 3 * np.sin(np.arange(100) * 0.1)
    noise = np.random.randn(100) * 0.5
    prices = trend + seasonal + noise
    
    # Create OHLCV data
    df = pd.DataFrame({
        'date': dates,
        'open': prices + np.random.randn(100) * 0.3,
        'high': prices + np.abs(np.random.randn(100)) * 0.5,
        'low': prices - np.abs(np.random.randn(100)) * 0.5,
        'close': prices,
        'volume': np.random.randint(1000000, 2000000, 100),
        'price': prices  # Use close as price
    })
    
    print(f"Created synthetic data with {len(df)} records")
    
    return df


def demonstrate_feature_engineering():
    """Main demonstration function."""
    print("\n" + "="*80)
    print("FEATURE ENGINEERING DEMONSTRATION")
    print("="*80)
    
    # Load data
    df = load_sample_data_from_db()
    
    # Check if we have OHLC data
    has_ohlc = all(col in df.columns for col in ['open', 'high', 'low', 'close'])
    
    print(f"\nInput DataFrame:")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Has OHLC: {has_ohlc}")
    
    # Initialize Feature Engineer
    print("\n" + "-"*80)
    print("INITIALIZING FEATURE ENGINEER")
    print("-"*80)
    
    engineer = FeatureEngineer(
        price_col='price',
        date_col='date',
        has_ohlc=has_ohlc
    )
    
    # Transform data
    print("\n" + "-"*80)
    print("TRANSFORMING DATA (Adding Features)")
    print("-"*80)
    
    df_enriched = engineer.transform(df, verbose=True)
    
    # Show results
    print("\n" + "="*80)
    print("TRANSFORMATION RESULTS")
    print("="*80)
    
    print(f"\nOriginal DataFrame: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"Enriched DataFrame: {df_enriched.shape[0]} rows × {df_enriched.shape[1]} columns")
    print(f"Features Added: {len(engineer.features_added)}")
    
    # Show sample of enriched data
    print(f"\nSample of enriched data (first 5 rows, selected columns):")
    sample_cols = ['date', 'price', 'sma_20', 'ema_10', 'rsi_14', 'macd', 'bb_upper', 'price_lag_1']
    available_cols = [col for col in sample_cols if col in df_enriched.columns]
    print(df_enriched[available_cols].head())
    
    # Show feature categories
    print(f"\nFeature Categories:")
    
    sma_features = [f for f in engineer.features_added if 'sma_' in f]
    ema_features = [f for f in engineer.features_added if 'ema_' in f]
    rsi_features = [f for f in engineer.features_added if 'rsi_' in f]
    macd_features = [f for f in engineer.features_added if 'macd' in f]
    bb_features = [f for f in engineer.features_added if 'bb_' in f]
    lag_features = [f for f in engineer.features_added if '_lag_' in f]
    roll_features = [f for f in engineer.features_added if '_roll_' in f]
    seasonal_features = [f for f in engineer.features_added if any(x in f for x in ['trend', 'seasonal', 'residual'])]
    date_features = [f for f in engineer.features_added if f in ['day_of_week', 'month', 'quarter', 'year', 'is_weekend']]
    
    print(f"  Simple Moving Averages (SMA): {len(sma_features)}")
    print(f"  Exponential Moving Averages (EMA): {len(ema_features)}")
    print(f"  RSI Indicators: {len(rsi_features)}")
    print(f"  MACD Indicators: {len(macd_features)}")
    print(f"  Bollinger Bands: {len(bb_features)}")
    print(f"  Lag Features: {len(lag_features)}")
    print(f"  Rolling Statistics: {len(roll_features)}")
    print(f"  Seasonal Decomposition: {len(seasonal_features)}")
    print(f"  Date Features: {len(date_features)}")
    
    # Calculate feature importance
    print("\n" + "-"*80)
    print("FEATURE IMPORTANCE ANALYSIS")
    print("-"*80)
    
    importance = engineer.get_feature_importance(df_enriched, target_col='price')
    
    print(f"\nTop 15 Most Important Features:")
    print(importance.head(15).to_string(index=False))
    
    # Select top features
    print("\n" + "-"*80)
    print("FEATURE SELECTION")
    print("-"*80)
    
    df_top = engineer.select_top_features(df_enriched, target_col='price', top_n=20)
    
    print(f"\nSelected top 20 features for modeling:")
    feature_cols = [col for col in df_top.columns if col not in ['date', 'price']]
    print(f"Features: {feature_cols}")
    
    # Show summary
    print("\n" + "="*80)
    print("FEATURE ENGINEERING SUMMARY")
    print("="*80)
    
    summary = engineer.get_summary()
    print(f"\nConfiguration:")
    for key, value in summary['configuration'].items():
        print(f"  {key}: {value}")
    
    print(f"\nFeatures:")
    print(f"  Total features added: {summary['features']['total_features_added']}")
    
    print(f"\nPreprocessing:")
    for key, value in summary['preprocessing'].items():
        print(f"  {key}: {value}")
    
    # Save enriched data sample
    print("\n" + "-"*80)
    print("SAVING SAMPLE OUTPUT")
    print("-"*80)
    
    output_file = Path(__file__).parent / 'feature_engineering_output.csv'
    df_enriched.head(50).to_csv(output_file, index=False)
    print(f"Saved first 50 rows of enriched data to: {output_file}")
    
    print("\n" + "="*80)
    print("FEATURE ENGINEERING DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nNext Steps:")
    print("  1. Use enriched features for model training")
    print("  2. Experiment with different feature combinations")
    print("  3. Perform feature selection based on model performance")
    print("  4. Monitor feature importance over time")
    print()


if __name__ == '__main__':
    demonstrate_feature_engineering()

