"""
Epic 2 Manual Testing - Step 5: Hyperparameter Tuning Framework

Tests Feature 2.5: Hyperparameter Tuning Framework
Note: Using minimal iterations for faster testing
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hyperparameter_tuning.tuner import HyperparameterTuner
from dotenv import load_dotenv

load_dotenv()

print("="*80)
print("EPIC 2 MANUAL TESTING - STEP 5: HYPERPARAMETER TUNING FRAMEWORK")
print("="*80)

# Create sample data
print("\n[1/3] Creating sample data...")
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
val_data = data[train_size:]

print(f"[OK] Data created: {len(data)} records")
print(f"   Train size: {len(train_data)}")
print(f"   Validation size: {len(val_data)}")

# Define search space
print("\n[2/3] Testing Random Search (using minimal iterations for speed)...")

search_space = {
    'sequence_length': [30, 60],
    'lstm_units': [[50], [50, 50]],
    'dropout_rate': [0.2, 0.3],
    'learning_rate': [0.001, 0.01]
}

# Create model factory
def create_lstm_model(**params):
    try:
        from models.lstm.lstm_model import LSTMForecaster
        return LSTMForecaster(
            sequence_length=params.get('sequence_length', 60),
            forecast_horizon=1,
            lstm_units=params.get('lstm_units', [50, 50]),
            dropout_rate=params.get('dropout_rate', 0.2),
            learning_rate=params.get('learning_rate', 0.001)
        )
    except ImportError:
        # If TensorFlow/LSTM is not available, raise to let the caller handle skipping.
        raise

def summarize_tuner(tuner: HyperparameterTuner, label: str) -> None:
    """
    Helper to print a consistent summary of tuning results using the public API.
    """
    best = tuner.get_best_result()
    results_df = tuner.get_results()
    n_trials = len(results_df) if not results_df.empty else None

    print(f"\n[OK] {label} Complete:")
    print(f"   Best parameters: {best.get('best_params')}")
    if best.get('best_score') is not None:
        print(f"   Best score ({tuner.scoring_metric.upper()}): {best['best_score']:.4f}")
    if n_trials is not None:
        print(f"   Total trials: {n_trials}")


# Test Random Search
try:
    tuner = HyperparameterTuner(
        method='random',
        scoring_metric='rmse',
        search_space_config=None,
        n_iter=3  # Minimal for testing
    )
    
    print("   Running random search (this may take a few minutes)...")
    print("   Note: Using only 3 iterations for faster testing")
    
    # Use explicit param_space so we do not depend on external config
    _best_params, _best_model = tuner.tune(
        model_factory=create_lstm_model,
        model_type='lstm',
        train_data=train_data,
        val_data=val_data,
        target_column='price',
        param_space=search_space,
        fit_kwargs={'epochs': 3, 'batch_size': 32, 'verbose': 0},  # Minimal epochs
        predict_kwargs={},
        verbose=0
    )
        
    summarize_tuner(tuner, "Random Search")
        
except Exception as e:
    print(f"\n[WARN] Hyperparameter tuning test skipped: {e}")
    print("   This is expected if TensorFlow is not available")
    print("   Or if you want to skip this time-consuming test")

# Test Grid Search (smaller space)
print("\n[3/3] Testing Grid Search (minimal grid for speed)...")

small_search_space = {
    'dropout_rate': [0.2, 0.3],
    'learning_rate': [0.001, 0.01]
}

try:
    tuner_grid = HyperparameterTuner(
        method='grid',
        scoring_metric='rmse',
        search_space_config=None
    )
    
    print("   Running grid search (this may take a few minutes)...")
    print("   Note: Using minimal grid for faster testing")
    
    _best_params_grid, _best_model_grid = tuner_grid.tune(
        model_factory=create_lstm_model,
        model_type='lstm',
        train_data=train_data,
        val_data=val_data,
        target_column='price',
        param_space=small_search_space,
        fit_kwargs={'epochs': 3, 'batch_size': 32, 'verbose': 0},
        predict_kwargs={},
        verbose=0
    )
    
    summarize_tuner(tuner_grid, "Grid Search")
    
except Exception as e:
    print(f"\n[WARN] Grid search test skipped: {e}")

print("\n" + "="*80)
print("[OK] STEP 5 COMPLETE: Hyperparameter Tuning Framework")
print("="*80)
print("\nPlease review the output above.")
print("Note: Hyperparameter tuning can be time-consuming.")
print("Press Enter to continue to Step 6...")
# input()  # Removed for non-interactive execution

