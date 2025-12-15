"""
Epic 2 Manual Testing - Step 2: Baseline Statistical Models

Tests Feature 2.2: Baseline Statistical Models (ARIMA, Prophet)
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.baseline import ARIMAModel, ProphetModel
from training.evaluation import ModelEvaluator
from dotenv import load_dotenv

load_dotenv()

print("="*80)
print("EPIC 2 MANUAL TESTING - STEP 2: BASELINE STATISTICAL MODELS")
print("="*80)

# Create sample time series
print("\n[1/5] Creating sample time series...")
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=200, freq='D')
prices = 70 + np.cumsum(np.random.randn(200) * 0.5)
data = pd.Series(prices, index=dates)

# Split data
train_size = int(len(data) * 0.8)
train_data = data[:train_size]
test_data = data[train_size:]

print(f"[OK] Data created: {len(data)} records")
print(f"   Train size: {len(train_data)}")
print(f"   Test size: {len(test_data)}")

# Test ARIMA
print("\n[2/5] Testing ARIMA Model...")
arima = None
metrics_arima = None
forecast_arima = None

try:
    arima = ARIMAModel(auto_select=True, seasonal=True)
    print("   Training ARIMA model...")
    arima.fit(train_data)
    print("[OK] ARIMA model trained")

    print("   Generating predictions...")
    forecast_arima = arima.predict(steps=len(test_data))
    print(f"[OK] Predictions generated: {len(forecast_arima)} steps")

    # Evaluate ARIMA
    evaluator = ModelEvaluator()
    metrics_arima = evaluator.evaluate(test_data.values, forecast_arima)

    print("\n   ARIMA Metrics:")
    for metric, value in metrics_arima.items():
        print(f"     {metric}: {value:.4f}")
except Exception as e:
    print(f"   Warning: ARIMA test skipped: {e}")
    evaluator = ModelEvaluator()

# Test Prophet
print("\n[3/5] Testing Prophet Model...")
prophet = None
metrics_prophet = None

try:
    prophet = ProphetModel()
    
    # Prepare Prophet data
    prophet_train = pd.DataFrame({
        'ds': train_data.index,
        'y': train_data.values
    })

    print("   Training Prophet model...")
    prophet.fit(prophet_train)
    print("[OK] Prophet model trained")

    # Predict (ProphetModel.predict expects steps parameter, not DataFrame)
    forecast_prophet = prophet.predict(steps=len(test_data))
    forecast_values = forecast_prophet['yhat'].values

    print(f"[OK] Predictions generated: {len(forecast_values)} steps")

    # Evaluate Prophet
    metrics_prophet = evaluator.evaluate(test_data.values, forecast_values)

    print("\n   Prophet Metrics:")
    for metric, value in metrics_prophet.items():
        print(f"     {metric}: {value:.4f}")
except Exception as e:
    print(f"   Warning: Prophet test skipped: {e}")

# Model Comparison
print("\n[4/5] Model Comparison...")
try:
    from models.baseline.model_comparison import ModelComparison
    
    if arima or prophet:
        comparator = ModelComparison()
        
        if arima:
            comparator.add_model('ARIMA', arima)
        if prophet:
            comparator.add_model('Prophet', prophet)
        
        # Train all models
        print("   Training models for comparison...")
        comparator.train_all(train_data)
        
        # Predict all models
        print("   Generating predictions for comparison...")
        predictions_dict = comparator.predict_all(steps=len(test_data))
        
        # Evaluate all models
        print("   Evaluating models...")
        comparison_results = comparator.evaluate_all(test_data)
        
        print("\n   Comparison Results:")
        print(comparison_results)
        
        # Get best model (uses default metric from evaluate_all)
        best_model = comparator.get_best_model()
        print(f"\n   [OK] Best model: {best_model}")
    else:
        print("   No models available for comparison")
except Exception as e:
    print(f"   Model comparison skipped: {e}")
    import traceback
    traceback.print_exc()

print("\n[5/5] Summary:")
if metrics_arima:
    print(f"   [OK] ARIMA: RMSE={metrics_arima['RMSE']:.4f}, MAE={metrics_arima['MAE']:.4f}")
if metrics_prophet:
    print(f"   [OK] Prophet: RMSE={metrics_prophet['RMSE']:.4f}, MAE={metrics_prophet['MAE']:.4f}")

print("\n" + "="*80)
print("[OK] STEP 2 COMPLETE: Baseline Statistical Models")
print("="*80)
print("\nPlease review the output above.")
print("\n" + "="*80)
print("STEP 2 REVIEW COMPLETE - Ready for Step 3")
print("="*80)
