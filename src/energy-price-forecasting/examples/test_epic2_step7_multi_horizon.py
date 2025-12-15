"""
Epic 2 Manual Testing - Step 7: Multi-Horizon Forecasting

Tests Feature 2.7: Multi-Horizon Forecasting Implementation
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_horizon import MultiHorizonForecaster, HorizonEvaluator
from dotenv import load_dotenv

load_dotenv()

print("="*80)
print("EPIC 2 MANUAL TESTING - STEP 7: MULTI-HORIZON FORECASTING")
print("="*80)

# Create sample data
print("\n[1/4] Creating sample data...")
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=300, freq='D')
prices = 70 + np.cumsum(np.random.randn(300) * 0.5)

data = pd.DataFrame({
    'date': dates,
    'price': prices
})

# Split data
train_size = int(len(data) * 0.8)
train_data = data[:train_size]
test_data = data[train_size:]

print(f"[OK] Data created: {len(data)} records")
print(f"   Train size: {len(train_data)}")
print(f"   Test size: {len(test_data)}")

# Test Multi-Horizon Forecaster (ARIMA for speed)
print("\n[2/4] Testing Multi-Horizon Forecaster (ARIMA)...")

forecaster = MultiHorizonForecaster(
    model_type='arima',  # Use ARIMA for faster testing
    horizons=[1, 7, 30],
    use_multi_output=False
)

print("   Training multi-horizon forecaster...")
forecaster.fit(train_data, target_col='price')
print("[OK] Models trained for all horizons")

# Predict
print("\n   Generating multi-horizon predictions...")
predictions = forecaster.predict(test_data, target_col='price')

print(f"[OK] Predictions generated:")
for horizon, pred in predictions.items():
    print(f"   {horizon}-day horizon: {len(pred)} predictions")
    print(f"      First 3: {pred[:3]}")
    print(f"      Last 3: {pred[-3:]}")

# Test Horizon Evaluator
print("\n[3/4] Testing Horizon Evaluator...")

evaluator = HorizonEvaluator(horizons=[1, 7, 30])

# Prepare true values (for demonstration, use test data aligned with predictions)
y_true = {}
for horizon in [1, 7, 30]:
    # Use test data values (aligned with prediction length)
    y_true[horizon] = test_data['price'].values[:len(predictions[horizon])]

# Evaluate
results = evaluator.evaluate_all(y_true, predictions)

print("[OK] Evaluation complete:")
for horizon, metrics in results.items():
    print(f"\n   {horizon}-day horizon metrics:")
    for metric, value in metrics.items():
        if metric != 'horizon':
            print(f"      {metric}: {value:.4f}")

# Compare horizons
print("\n[4/4] Comparing Horizons...")
comparison = evaluator.compare_horizons(results, metric='RMSE')
print("\n   Horizon Comparison (RMSE):")
print(comparison)

# Get summary
summary = evaluator.get_summary(results)
print("\n   Summary Statistics:")
print(f"      Horizons tested: {summary['horizons']}")
print(f"      Metrics calculated: {list(summary['metrics'].keys())}")

print("\n" + "="*80)
print("[OK] STEP 7 COMPLETE: Multi-Horizon Forecasting")
print("="*80)
print("\nPlease review the output above.")
print("\n" + "="*80)
print("🎉 EPIC 2 MANUAL TESTING COMPLETE!")
print("="*80)
print("\nAll 7 features have been tested:")
print("  [OK] Feature 2.1: Feature Engineering Pipeline")
print("  [OK] Feature 2.2: Baseline Statistical Models")
print("  [OK] Feature 2.3: LSTM Neural Network Model")
print("  [OK] Feature 2.4: Model Training Infrastructure")
print("  [OK] Feature 2.5: Hyperparameter Tuning Framework")
print("  [OK] Feature 2.6: Model Versioning & Experiment Tracking")
print("  [OK] Feature 2.7: Multi-Horizon Forecasting")
print("\nPress Enter to exit...")
input()

