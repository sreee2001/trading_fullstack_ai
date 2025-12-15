"""
Epic 2 Manual Testing - Step 4: Model Training Infrastructure

Tests Feature 2.4: Model Training Infrastructure
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from training.data_splitting import split_time_series
from training.evaluation import ModelEvaluator
from training.cross_validation import WalkForwardValidator
from dotenv import load_dotenv

load_dotenv()

print("="*80)
print("EPIC 2 MANUAL TESTING - STEP 4: MODEL TRAINING INFRASTRUCTURE")
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

print(f"[OK] Data created: {len(data)} records")

# Test Data Splitting
print("\n[2/4] Testing Data Splitting...")
train, val, test = split_time_series(
    data,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15
)

print(f"[OK] Data split:")
print(f"   Train: {len(train)} records ({len(train)/len(data)*100:.1f}%)")
print(f"   Validation: {len(val)} records ({len(val)/len(data)*100:.1f}%)")
print(f"   Test: {len(test)} records ({len(test)/len(data)*100:.1f}%)")

# Verify temporal ordering
print(f"\n   Temporal ordering verified:")
print(f"   Train: {train['date'].min()} to {train['date'].max()}")
print(f"   Validation: {val['date'].min()} to {val['date'].max()}")
print(f"   Test: {test['date'].min()} to {test['date'].max()}")

# Test Model Evaluation
print("\n[3/4] Testing Model Evaluation Framework...")
evaluator = ModelEvaluator(metrics=['MAE', 'RMSE', 'MAPE', 'R2', 'Directional_Accuracy'])

# Create dummy predictions
y_true = test['price'].values
y_pred = test['price'].values + np.random.randn(len(test)) * 0.5

metrics = evaluator.evaluate(y_true, y_pred)

print("[OK] Evaluation metrics calculated:")
for metric, value in metrics.items():
    print(f"   {metric}: {value:.4f}")

# Test Walk-Forward Validation
print("\n[4/4] Testing Walk-Forward Validation...")

# Create simple model factory
def create_arima_model():
    from models.baseline import ARIMAForecaster
    return ARIMAForecaster(auto_arima=True)

validator = WalkForwardValidator(
    train_window=100,
    test_window=20,
    step_size=20,
    expanding=True
)

print("   Running walk-forward validation (this may take 1-2 minutes)...")
cv_results = validator.validate(
    model_factory=create_arima_model,
    data=data,
    target_column='price',
    fit_kwargs={},
    predict_kwargs={}
)

print(f"[OK] Walk-forward validation complete: {cv_results['n_folds']} folds")

# Get aggregated metrics
metrics_df = validator.get_aggregated_metrics(cv_results)
print("\n   Aggregated Metrics:")
print(metrics_df.head())

print("\n" + "="*80)
print("[OK] STEP 4 COMPLETE: Model Training Infrastructure")
print("="*80)
print("\nPlease review the output above.")
print("Press Enter to continue to Step 5...")
input()

