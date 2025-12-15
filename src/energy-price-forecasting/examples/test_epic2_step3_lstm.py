"""
Epic 2 Manual Testing - Step 3: LSTM Neural Network Model

Tests Feature 2.3: LSTM Neural Network Model
Note: This test uses minimal epochs for faster execution
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from models.lstm.lstm_model import LSTMForecaster
    from models.lstm.integration import LSTMWithFeatures
    from training.evaluation import ModelEvaluator
    LSTM_AVAILABLE = True
except ImportError as e:
    print(f"LSTM not available: {e}")
    LSTM_AVAILABLE = False

from dotenv import load_dotenv

load_dotenv()

if not LSTM_AVAILABLE:
    print("\n⚠️  TensorFlow/Keras not available. Skipping LSTM tests.")
    print("   Install with: pip install tensorflow")
    input("\nPress Enter to continue...")
    exit(0)

print("="*80)
print("EPIC 2 MANUAL TESTING - STEP 3: LSTM NEURAL NETWORK MODEL")
print("="*80)

# Create sample data
print("\n[1/4] Creating sample data...")
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=500, freq='D')
prices = 70 + np.cumsum(np.random.randn(500) * 0.5)

data = pd.DataFrame({
    'date': dates,
    'price': prices
})

# Split data
train_size = int(len(data) * 0.7)
val_size = int(len(data) * 0.15)

train_data = data[:train_size]
val_data = data[train_size:train_size+val_size]
test_data = data[train_size+val_size:]

print(f"[OK] Data created: {len(data)} records")
print(f"   Train size: {len(train_data)}")
print(f"   Validation size: {len(val_data)}")
print(f"   Test size: {len(test_data)}")

# Test Basic LSTM
print("\n[2/4] Testing Basic LSTM Model...")
lstm = LSTMForecaster(
    sequence_length=60,
    forecast_horizon=1,
    model_type='lstm',
    lstm_units=[50, 50],
    dropout_rate=0.2,
    learning_rate=0.001
)

print("   Training LSTM model (this may take 2-3 minutes)...")
print("   Using 5 epochs for faster testing...")
lstm.fit(
    train_data,
    target_column='price',
    validation_data=val_data,
    epochs=5,  # Reduced for testing
    batch_size=32,
    verbose=1
)
print("[OK] LSTM model trained")

print("   Generating predictions...")
predictions = lstm.predict(test_data, target_column='price')
print(f"[OK] Predictions generated: {len(predictions)} values")

# Evaluate (align predictions with test data - predictions may be shorter due to sequence length)
evaluator = ModelEvaluator()
# Align predictions: take last len(predictions) values from test_data
test_values = test_data['price'].values[-len(predictions):]
metrics = evaluator.evaluate(test_values, predictions)

print("\n   LSTM Metrics:")
for metric, value in metrics.items():
    print(f"     {metric}: {value:.4f}")

# Test LSTM with Features
print("\n[3/4] Testing LSTM with Feature Engineering...")
from feature_engineering.pipeline import FeatureEngineer

fe = FeatureEngineer(price_col='price', date_col='date')
train_features = fe.transform(train_data)
val_features = fe.transform(val_data)
test_features = fe.transform(test_data)

lstm_features = LSTMWithFeatures(
    sequence_length=60,
    forecast_horizon=1,
    lstm_units=[50, 50],
    dropout_rate=0.2,
    learning_rate=0.001
)

print("   Training LSTM with features (this may take 2-3 minutes)...")
lstm_features.fit(
    train_features,
    target_col='price',  # Use target_col for LSTMWithFeatures
    validation_data=val_features,
    epochs=5,  # Reduced for testing
    batch_size=32,
    verbose=1
)
print("[OK] LSTM with features trained")

predictions_features = lstm_features.predict(test_features, target_col='price')
# Align predictions with test data
test_values_features = test_features['price'].values[-len(predictions_features):]
metrics_features = evaluator.evaluate(test_values_features, predictions_features)

print("\n   LSTM with Features Metrics:")
for metric, value in metrics_features.items():
    print(f"     {metric}: {value:.4f}")

# Summary
print("\n[4/4] Summary:")
print(f"   [OK] Basic LSTM: RMSE={metrics['RMSE']:.4f}, MAE={metrics['MAE']:.4f}")
print(f"   [OK] LSTM with Features: RMSE={metrics_features['RMSE']:.4f}, MAE={metrics_features['MAE']:.4f}")

print("\n" + "="*80)
print("[OK] STEP 3 COMPLETE: LSTM Neural Network Model")
print("="*80)
print("\nPlease review the output above.")
print("Press Enter to continue to Step 4...")
# input()  # Removed for non-interactive execution

