"""
Epic 2 Manual Testing - Step 1: Feature Engineering Pipeline

Tests Feature 2.1: Feature Engineering Pipeline
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_engineering.pipeline import FeatureEngineer
from dotenv import load_dotenv

load_dotenv()

print("="*80)
print("EPIC 2 MANUAL TESTING - STEP 1: FEATURE ENGINEERING PIPELINE")
print("="*80)

# Create sample data
print("\n[1/4] Creating sample data...")
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=200, freq='D')
prices = 70 + np.cumsum(np.random.randn(200) * 0.5)

data = pd.DataFrame({
    'date': dates,
    'price': prices,
    'open': prices + np.random.randn(200) * 0.1,
    'high': prices + np.abs(np.random.randn(200) * 0.2),
    'low': prices - np.abs(np.random.randn(200) * 0.2),
    'close': prices,
    'volume': np.random.randint(1000000, 5000000, 200)
})

print(f"[OK] Data created: {len(data)} records")
print(f"   Columns: {list(data.columns)}")
print(f"   Date range: {data['date'].min()} to {data['date'].max()}")

# Initialize FeatureEngineer
print("\n[2/4] Initializing FeatureEngineer...")
fe = FeatureEngineer(
    price_col='price',
    date_col='date',
    has_ohlc=True
)
print("[OK] FeatureEngineer initialized")

# Transform data
print("\n[3/4] Transforming data (adding features)...")
features_df = fe.transform(data, verbose=True)

print(f"\n[OK] Transformation complete:")
print(f"   Original columns: {len(data.columns)}")
print(f"   Feature columns: {len(features_df.columns)}")
print(f"   Features added: {len(features_df.columns) - len(data.columns)}")

# Show sample features
print("\n[4/4] Sample features:")
sample_cols = ['price', 'sma_5', 'sma_20', 'rsi_14', 'macd', 'price_lag_1', 'bb_upper']
available_cols = [col for col in sample_cols if col in features_df.columns]
print(features_df[available_cols].head(10))

# Feature importance
print("\n" + "-"*80)
print("FEATURE IMPORTANCE (Top 10)")
print("-"*80)
importance = fe.get_feature_importance(features_df, target_col='price')
print(importance.head(10))

print("\n" + "="*80)
print("[OK] STEP 1 COMPLETE: Feature Engineering Pipeline")
print("="*80)
print("\nPlease review the output above.")
print("\n" + "="*80)
print("STEP 1 REVIEW COMPLETE - Ready for Step 2")
print("="*80)

