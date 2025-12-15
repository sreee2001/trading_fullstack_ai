# Epic 2: Core ML Model Development - Manual Testing Guide

**Epic**: 2 - Core ML Model Development  
**Date**: December 14, 2025  
**Status**: All 7 Features Complete (100%)  
**Purpose**: Comprehensive manual testing guide for Epic 2

---

## 📋 Prerequisites

### 1. Environment Setup

```powershell
# Navigate to project directory
cd C:\Users\Srikanth\source\repos\trading_fullstack_ai\src\energy-price-forecasting

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Verify Python version (should be 3.8+)
python --version

# Install/verify dependencies
pip install -r requirements.txt
```

### 2. Required Data

You'll need historical price data for testing. Options:

**Option A: Use Real API Data (Recommended)**
- Ensure `.env` file has API keys:
  ```
  EIA_API_KEY=your_key_here
  FRED_API_KEY=your_key_here
  ```
- Run data pipeline to fetch data:
  ```powershell
  python -m data_pipeline run --mode full_refresh
  ```

**Option B: Use Sample Data**
- Create sample time series data (see examples below)

### 3. Verify Database (Optional)

If testing with database:
```powershell
# Check database connection
python -c "from database.utils import check_database_health; print(check_database_health())"
```

---

## 🧪 Feature-by-Feature Testing

---

## Feature 2.1: Feature Engineering Pipeline

### Test 2.1.1: Basic Feature Engineering

**File**: Create `test_feature_engineering_manual.py`

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from feature_engineering.pipeline import FeatureEngineer

# Create sample data
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

# Initialize FeatureEngineer
fe = FeatureEngineer(
    price_col='price',
    date_col='date',
    has_ohlc=True
)

# Transform data
features_df = fe.transform(data)

print("="*80)
print("FEATURE ENGINEERING TEST")
print("="*80)
print(f"\nOriginal columns: {list(data.columns)}")
print(f"Original shape: {data.shape}")
print(f"\nFeature columns: {list(features_df.columns)}")
print(f"Feature shape: {features_df.shape}")
print(f"\nTotal features created: {len(features_df.columns) - len(data.columns)}")

# Check specific features
print("\n" + "="*80)
print("SAMPLE FEATURES")
print("="*80)
print(features_df[['price', 'sma_5', 'sma_20', 'rsi', 'macd', 'price_lag_1']].head(10))

# Feature importance
print("\n" + "="*80)
print("FEATURE IMPORTANCE (Top 10)")
print("="*80)
importance = fe.get_feature_importance()
print(importance.head(10))

print("\n✅ Feature Engineering Test PASSED")
```

**Run**:
```powershell
python test_feature_engineering_manual.py
```

**Expected Output**:
- Original data: 6 columns, 200 rows
- Features created: 50+ features
- Feature importance ranking
- No errors

---

### Test 2.1.2: Technical Indicators

```python
from feature_engineering.indicators import (
    calculate_sma, calculate_ema, calculate_rsi,
    calculate_macd, calculate_bollinger_bands, calculate_atr
)

# Test SMA
sma_20 = calculate_sma(data['price'], window=20)
print(f"SMA(20) - First 5 values: {sma_20.head()}")
print(f"SMA(20) - Last 5 values: {sma_20.tail()}")

# Test RSI
rsi = calculate_rsi(data['price'], period=14)
print(f"\nRSI - First 5 values: {rsi.head()}")
print(f"RSI range: {rsi.min():.2f} - {rsi.max():.2f}")

# Test MACD
macd_result = calculate_macd(data['price'])
print(f"\nMACD columns: {list(macd_result.columns)}")
print(f"MACD shape: {macd_result.shape}")

print("\n✅ Technical Indicators Test PASSED")
```

---

## Feature 2.2: Baseline Statistical Models

### Test 2.2.1: ARIMA Model

**File**: Create `test_baseline_models_manual.py`

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models.baseline import ARIMAForecaster

# Create sample time series (200 days)
dates = pd.date_range('2024-01-01', periods=200, freq='D')
prices = 70 + np.cumsum(np.random.randn(200) * 0.5)
data = pd.Series(prices, index=dates)

# Split data
train_size = int(len(data) * 0.8)
train_data = data[:train_size]
test_data = data[train_size:]

print("="*80)
print("ARIMA MODEL TEST")
print("="*80)

# Initialize ARIMA
arima = ARIMAForecaster(auto_arima=True, seasonal=True)

# Train
print("\nTraining ARIMA model...")
arima.fit(train_data)
print(f"✅ Model trained successfully")
print(f"Model order: {arima.model.order if hasattr(arima.model, 'order') else 'Auto-selected'}")

# Predict
print("\nGenerating predictions...")
forecast = arima.predict(steps=len(test_data))
print(f"✅ Predictions generated: {len(forecast)} steps")

# Evaluate
from training.evaluation import ModelEvaluator
evaluator = ModelEvaluator()
metrics = evaluator.evaluate(test_data.values, forecast)

print("\n" + "="*80)
print("ARIMA MODEL METRICS")
print("="*80)
for metric, value in metrics.items():
    print(f"{metric}: {value:.4f}")

print("\n✅ ARIMA Model Test PASSED")
```

**Run**:
```powershell
python test_baseline_models_manual.py
```

**Expected Output**:
- Model trains successfully
- Predictions generated
- Metrics displayed (MAE, RMSE, MAPE, R²)
- No errors

---

### Test 2.2.2: Prophet Model

```python
from models.baseline import ProphetForecaster

print("\n" + "="*80)
print("PROPHET MODEL TEST")
print("="*80)

# Initialize Prophet
prophet = ProphetForecaster()

# Prepare data (Prophet needs DataFrame with 'ds' and 'y')
prophet_data = pd.DataFrame({
    'ds': dates[:train_size],
    'y': train_data.values
})

# Train
print("\nTraining Prophet model...")
prophet.fit(prophet_data)
print("✅ Model trained successfully")

# Predict
future_dates = pd.date_range(train_data.index[-1], periods=len(test_data)+1, freq='D')[1:]
forecast_df = prophet.predict(pd.DataFrame({'ds': future_dates}))
forecast_values = forecast_df['yhat'].values

# Evaluate
metrics = evaluator.evaluate(test_data.values, forecast_values)

print("\n" + "="*80)
print("PROPHET MODEL METRICS")
print("="*80)
for metric, value in metrics.items():
    print(f"{metric}: {value:.4f}")

print("\n✅ Prophet Model Test PASSED")
```

---

### Test 2.2.3: Model Comparison

```python
from models.baseline.model_comparison import ModelComparator

print("\n" + "="*80)
print("MODEL COMPARISON TEST")
print("="*80)

# Prepare models
models = {
    'ARIMA': arima,
    'Prophet': prophet
}

# Compare
comparator = ModelComparator()
comparison_results = comparator.compare_models(
    train_data=train_data,
    test_data=test_data,
    models=models
)

print("\n" + "="*80)
print("MODEL COMPARISON RESULTS")
print("="*80)
print(comparison_results)

best_model = comparator.get_best_model(comparison_results, metric='RMSE')
print(f"\n✅ Best model (by RMSE): {best_model}")

print("\n✅ Model Comparison Test PASSED")
```

---

## Feature 2.3: LSTM Neural Network Model

### Test 2.3.1: LSTM Training

**File**: Create `test_lstm_manual.py`

```python
import pandas as pd
import numpy as np
from datetime import datetime
from models.lstm.lstm_model import LSTMForecaster

# Create sample data
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

print("="*80)
print("LSTM MODEL TEST")
print("="*80)
print(f"Train size: {len(train_data)}")
print(f"Validation size: {len(val_data)}")
print(f"Test size: {len(test_data)}")

# Initialize LSTM
lstm = LSTMForecaster(
    sequence_length=60,
    forecast_horizon=1,
    model_type='lstm',
    lstm_units=[50, 50],
    dropout_rate=0.2,
    learning_rate=0.001
)

# Train
print("\nTraining LSTM model...")
print("(This may take a few minutes)")
lstm.fit(
    train_data,
    target_col='price',
    validation_data=val_data,
    epochs=10,  # Use fewer epochs for testing
    batch_size=32,
    verbose=1
)
print("✅ Model trained successfully")

# Predict
print("\nGenerating predictions...")
predictions = lstm.predict(test_data, target_col='price')
print(f"✅ Predictions generated: {len(predictions)} values")

# Evaluate
from training.evaluation import ModelEvaluator
evaluator = ModelEvaluator()
metrics = evaluator.evaluate(test_data['price'].values, predictions)

print("\n" + "="*80)
print("LSTM MODEL METRICS")
print("="*80)
for metric, value in metrics.items():
    print(f"{metric}: {value:.4f}")

print("\n✅ LSTM Model Test PASSED")
```

**Run**:
```powershell
python test_lstm_manual.py
```

**Expected Output**:
- Model trains (may take 2-5 minutes)
- Training progress displayed
- Predictions generated
- Metrics displayed
- No errors

---

### Test 2.3.2: LSTM with Features

```python
from models.lstm.integration import LSTMWithFeatures
from feature_engineering.pipeline import FeatureEngineer

print("\n" + "="*80)
print("LSTM WITH FEATURES TEST")
print("="*80)

# Create features
fe = FeatureEngineer(price_col='price', date_col='date')
train_features = fe.transform(train_data)
val_features = fe.transform(val_data)
test_features = fe.transform(test_data)

# Initialize LSTM with features
lstm_features = LSTMWithFeatures(
    sequence_length=60,
    forecast_horizon=1,
    lstm_config={
        'lstm_units': [50, 50],
        'dropout_rate': 0.2,
        'learning_rate': 0.001
    }
)

# Train
print("\nTraining LSTM with features...")
lstm_features.fit(
    train_features,
    target_col='price',
    validation_data=val_features,
    epochs=10,
    batch_size=32,
    verbose=1
)
print("✅ Model trained successfully")

# Predict
predictions = lstm_features.predict(test_features, target_col='price')

# Evaluate
metrics = evaluator.evaluate(test_data['price'].values, predictions)

print("\n" + "="*80)
print("LSTM WITH FEATURES METRICS")
print("="*80)
for metric, value in metrics.items():
    print(f"{metric}: {value:.4f}")

print("\n✅ LSTM with Features Test PASSED")
```

---

## Feature 2.4: Model Training Infrastructure

### Test 2.4.1: Training Pipeline

**File**: Create `test_training_pipeline_manual.py`

```python
from training.training_pipeline import TrainingPipeline
from training.data_splitting import split_time_series
from training.config import TrainingConfig

print("="*80)
print("TRAINING PIPELINE TEST")
print("="*80)

# Prepare data
data = pd.DataFrame({
    'date': dates,
    'price': prices
})

# Split data
train, val, test = split_time_series(
    data,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15
)

print(f"Train size: {len(train)}")
print(f"Validation size: {len(val)}")
print(f"Test size: {len(test)}")

# Initialize training pipeline
pipeline = TrainingPipeline(
    model_type='lstm',
    config_path=None  # Use defaults
)

# Train
print("\nRunning training pipeline...")
results = pipeline.train(
    train_data=train,
    validation_data=val,
    test_data=test,
    target_col='price',
    epochs=10,
    batch_size=32
)

print("\n" + "="*80)
print("TRAINING PIPELINE RESULTS")
print("="*80)
print(f"Training completed: {results['status']}")
print(f"Best model saved: {results.get('model_path', 'N/A')}")
print(f"Training metrics: {results.get('train_metrics', {})}")
print(f"Test metrics: {results.get('test_metrics', {})}")

print("\n✅ Training Pipeline Test PASSED")
```

---

### Test 2.4.2: Cross-Validation

```python
from training.cross_validation import WalkForwardValidator

print("\n" + "="*80)
print("CROSS-VALIDATION TEST")
print("="*80)

# Create model factory
def create_model():
    from models.lstm.lstm_model import LSTMForecaster
    return LSTMForecaster(sequence_length=60, forecast_horizon=1)

# Run walk-forward validation
validator = WalkForwardValidator(
    train_window=100,
    test_window=20,
    step_size=20,
    expanding=True
)

print("\nRunning walk-forward validation...")
cv_results = validator.validate(
    model_factory=create_model,
    data=data,
    target_column='price',
    fit_kwargs={'epochs': 5, 'batch_size': 32, 'verbose': 0},
    predict_kwargs={}
)

print(f"\n✅ Cross-validation complete: {cv_results['n_folds']} folds")

# Get aggregated metrics
metrics_df = validator.get_aggregated_metrics(cv_results)
print("\n" + "="*80)
print("CROSS-VALIDATION METRICS")
print("="*80)
print(metrics_df)

print("\n✅ Cross-Validation Test PASSED")
```

---

## Feature 2.5: Hyperparameter Tuning Framework

### Test 2.5.1: Grid Search

**File**: Create `test_hyperparameter_tuning_manual.py`

```python
from hyperparameter_tuning.tuner import HyperparameterTuner
from hyperparameter_tuning.search_space import SearchSpace

print("="*80)
print("HYPERPARAMETER TUNING TEST")
print("="*80)

# Define search space
search_space = {
    'sequence_length': [30, 60, 90],
    'lstm_units': [[50], [50, 50], [100]],
    'dropout_rate': [0.2, 0.3, 0.4],
    'learning_rate': [0.001, 0.01]
}

# Create model factory
def create_model(**params):
    from models.lstm.lstm_model import LSTMForecaster
    return LSTMForecaster(
        sequence_length=params.get('sequence_length', 60),
        forecast_horizon=1,
        lstm_units=params.get('lstm_units', [50, 50]),
        dropout_rate=params.get('dropout_rate', 0.2),
        learning_rate=params.get('learning_rate', 0.001)
    )

# Initialize tuner
tuner = HyperparameterTuner(
    method='grid_search',
    search_space=search_space
)

# Run tuning (use smaller dataset for testing)
print("\nRunning grid search...")
print("(This may take 10-20 minutes)")
tuning_results = tuner.tune(
    model_factory=create_model,
    train_data=train_data,
    validation_data=val_data,
    target_col='price',
    fit_kwargs={'epochs': 5, 'batch_size': 32, 'verbose': 0},
    scoring_metric='RMSE'
)

print("\n" + "="*80)
print("HYPERPARAMETER TUNING RESULTS")
print("="*80)
print(f"Best parameters: {tuning_results['best_params']}")
print(f"Best score: {tuning_results['best_score']:.4f}")
print(f"Total trials: {tuning_results['n_trials']}")

print("\n✅ Hyperparameter Tuning Test PASSED")
```

**Note**: Grid search can take a long time. For quick testing, use random search or Bayesian optimization with fewer iterations.

---

### Test 2.5.2: Random Search

```python
print("\n" + "="*80)
print("RANDOM SEARCH TEST")
print("="*80)

tuner_random = HyperparameterTuner(
    method='random_search',
    search_space=search_space,
    n_iterations=5  # Use fewer iterations for testing
)

print("\nRunning random search...")
tuning_results = tuner_random.tune(
    model_factory=create_model,
    train_data=train_data,
    validation_data=val_data,
    target_col='price',
    fit_kwargs={'epochs': 5, 'batch_size': 32, 'verbose': 0},
    scoring_metric='RMSE'
)

print(f"\nBest parameters: {tuning_results['best_params']}")
print(f"Best score: {tuning_results['best_score']:.4f}")

print("\n✅ Random Search Test PASSED")
```

---

## Feature 2.6: Model Versioning & Experiment Tracking (MLflow)

### Test 2.6.1: MLflow Setup

**Prerequisites**: MLflow server (optional, can use local file system)

```python
from mlflow_tracking.mlflow_manager import MLflowManager

print("="*80)
print("MLFLOW TRACKING TEST")
print("="*80)

# Initialize MLflow manager
mlflow_manager = MLflowManager(
    tracking_uri='file:./mlruns',  # Local file system
    experiment_name='energy_price_forecasting'
)

# Create experiment
experiment_id = mlflow_manager.create_experiment()
print(f"✅ Experiment created: {experiment_id}")

# Start a run
run = mlflow_manager.start_run()
print(f"✅ Run started: {run.info.run_id}")

# Log parameters
mlflow_manager.log_params({
    'model_type': 'LSTM',
    'sequence_length': 60,
    'epochs': 10,
    'batch_size': 32
})

# Log metrics
mlflow_manager.log_metrics({
    'train_loss': 0.05,
    'val_loss': 0.06,
    'test_rmse': 0.8,
    'test_mae': 0.6
})

# End run
mlflow_manager.end_run()
print("✅ Run completed")

print("\n✅ MLflow Tracking Test PASSED")
```

---

### Test 2.6.2: Experiment Tracking

```python
from mlflow_tracking.experiment_tracker import ExperimentTracker

print("\n" + "="*80)
print("EXPERIMENT TRACKER TEST")
print("="*80)

# Initialize tracker
tracker = ExperimentTracker(
    experiment_name='energy_price_forecasting',
    tracking_uri='file:./mlruns'
)

# Start run
run_id = tracker.start_run(
    run_name='lstm_experiment_1',
    tags={'model': 'LSTM', 'dataset': 'WTI'}
)

# Log parameters
tracker.log_params({
    'sequence_length': 60,
    'lstm_units': [50, 50],
    'dropout_rate': 0.2
})

# Log metrics
tracker.log_metrics({
    'rmse': 0.8,
    'mae': 0.6,
    'mape': 1.2,
    'r2': 0.85
})

# Log artifact (example: save model summary)
import json
summary = {'model_type': 'LSTM', 'params': 50000}
with open('model_summary.json', 'w') as f:
    json.dump(summary, f)

tracker.log_artifact('model_summary.json')

# End run
tracker.end_run()

print(f"✅ Experiment tracked: {run_id}")

# Search runs
runs = tracker.search_runs(filter_string="tags.model = 'LSTM'")
print(f"✅ Found {len(runs)} LSTM runs")

print("\n✅ Experiment Tracking Test PASSED")
```

---

## Feature 2.7: Multi-Horizon Forecasting Implementation

### Test 2.7.1: Multi-Horizon Forecasting

**File**: Create `test_multi_horizon_manual.py`

```python
from multi_horizon import MultiHorizonForecaster

print("="*80)
print("MULTI-HORIZON FORECASTING TEST")
print("="*80)

# Prepare data
data = pd.DataFrame({
    'date': dates,
    'price': prices
})

# Split data
train_size = int(len(data) * 0.8)
train_data = data[:train_size]
test_data = data[train_size:]

# Initialize multi-horizon forecaster
forecaster = MultiHorizonForecaster(
    model_type='arima',  # Use ARIMA for faster testing
    horizons=[1, 7, 30],
    use_multi_output=False
)

# Train
print("\nTraining multi-horizon forecaster...")
forecaster.fit(train_data, target_col='price')
print("✅ Model trained successfully")

# Predict
print("\nGenerating multi-horizon predictions...")
predictions = forecaster.predict(test_data, target_col='price')

print("\n" + "="*80)
print("MULTI-HORIZON PREDICTIONS")
print("="*80)
for horizon, pred in predictions.items():
    print(f"{horizon}-day horizon: {len(pred)} predictions")
    print(f"  First 5: {pred[:5]}")
    print(f"  Last 5: {pred[-5:]}")

# Evaluate
from multi_horizon import HorizonEvaluator

evaluator = HorizonEvaluator(horizons=[1, 7, 30])

# Prepare true values (for demonstration, use test data)
y_true = {h: test_data['price'].values for h in [1, 7, 30]}

results = evaluator.evaluate_all(y_true, predictions)

print("\n" + "="*80)
print("MULTI-HORIZON EVALUATION")
print("="*80)
for horizon, metrics in results.items():
    print(f"\n{horizon}-day horizon:")
    for metric, value in metrics.items():
        if metric != 'horizon':
            print(f"  {metric}: {value:.4f}")

print("\n✅ Multi-Horizon Forecasting Test PASSED")
```

**Run**:
```powershell
python test_multi_horizon_manual.py
```

**Expected Output**:
- Models trained for each horizon
- Predictions for 1, 7, and 30 days
- Metrics for each horizon
- No errors

---

## 🎯 Complete End-to-End Test

### Full Pipeline Test

**File**: Create `test_epic2_end_to_end.py`

```python
"""
Complete Epic 2 End-to-End Test
Tests all features in sequence
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("="*80)
print("EPIC 2: COMPLETE END-TO-END TEST")
print("="*80)

# Step 1: Create sample data
print("\n[1/7] Creating sample data...")
dates = pd.date_range('2023-01-01', periods=500, freq='D')
prices = 70 + np.cumsum(np.random.randn(500) * 0.5)
data = pd.DataFrame({'date': dates, 'price': prices})
print(f"✅ Data created: {len(data)} records")

# Step 2: Feature Engineering
print("\n[2/7] Feature Engineering...")
from feature_engineering.pipeline import FeatureEngineer
fe = FeatureEngineer(price_col='price', date_col='date')
data_features = fe.transform(data)
print(f"✅ Features created: {len(data_features.columns)} columns")

# Step 3: Data Splitting
print("\n[3/7] Data Splitting...")
from training.data_splitting import split_time_series
train, val, test = split_time_series(data_features, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
print(f"✅ Data split: Train={len(train)}, Val={len(val)}, Test={len(test)}")

# Step 4: Train Baseline Model
print("\n[4/7] Training Baseline Model (ARIMA)...")
from models.baseline import ARIMAForecaster
arima = ARIMAForecaster(auto_arima=True)
arima.fit(train['price'])
forecast_arima = arima.predict(steps=len(test))
print(f"✅ ARIMA trained and predicted")

# Step 5: Train LSTM Model
print("\n[5/7] Training LSTM Model...")
from models.lstm.lstm_model import LSTMForecaster
lstm = LSTMForecaster(sequence_length=60, forecast_horizon=1, epochs=5, verbose=0)
lstm.fit(train, target_col='price', validation_data=val, epochs=5, batch_size=32, verbose=0)
forecast_lstm = lstm.predict(test, target_col='price')
print(f"✅ LSTM trained and predicted")

# Step 6: Model Comparison
print("\n[6/7] Model Comparison...")
from training.evaluation import ModelEvaluator
evaluator = ModelEvaluator()
metrics_arima = evaluator.evaluate(test['price'].values, forecast_arima)
metrics_lstm = evaluator.evaluate(test['price'].values, forecast_lstm)
print(f"✅ ARIMA RMSE: {metrics_arima['RMSE']:.4f}")
print(f"✅ LSTM RMSE: {metrics_lstm['RMSE']:.4f}")

# Step 7: Multi-Horizon Forecasting
print("\n[7/7] Multi-Horizon Forecasting...")
from multi_horizon import MultiHorizonForecaster
mh_forecaster = MultiHorizonForecaster(model_type='arima', horizons=[1, 7, 30])
mh_forecaster.fit(train, target_col='price')
mh_predictions = mh_forecaster.predict(test, target_col='price')
print(f"✅ Multi-horizon predictions: {list(mh_predictions.keys())}")

print("\n" + "="*80)
print("✅ EPIC 2 END-TO-END TEST COMPLETE")
print("="*80)
print("\nAll 7 features tested successfully!")
```

**Run**:
```powershell
python test_epic2_end_to_end.py
```

---

## 📊 Verification Checklist

After running all tests, verify:

- [ ] **Feature 2.1**: Features created (50+ features)
- [ ] **Feature 2.2**: ARIMA, Prophet models train and predict
- [ ] **Feature 2.3**: LSTM trains and predicts
- [ ] **Feature 2.4**: Training pipeline works
- [ ] **Feature 2.5**: Hyperparameter tuning runs (at least one method)
- [ ] **Feature 2.6**: MLflow tracking works
- [ ] **Feature 2.7**: Multi-horizon predictions generated

---

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```powershell
   # Ensure you're in the correct directory
   cd C:\Users\Srikanth\source\repos\trading_fullstack_ai\src\energy-price-forecasting
   
   # Verify Python path
   python -c "import sys; print(sys.path)"
   ```

2. **TensorFlow/Keras Errors**
   ```powershell
   # Reinstall TensorFlow if needed
   pip install --upgrade tensorflow
   ```

3. **Memory Issues (LSTM)**
   - Reduce `sequence_length` or `batch_size`
   - Use fewer epochs for testing

4. **MLflow Connection Issues**
   - Use local file system: `tracking_uri='file:./mlruns'`
   - Or start MLflow server: `mlflow ui`

---

## 📝 Notes

- **Testing Time**: Full end-to-end test takes ~15-30 minutes
- **LSTM Training**: Can take 5-10 minutes per model
- **Hyperparameter Tuning**: Can take 30+ minutes (use fewer iterations for testing)
- **Data Requirements**: At least 200-500 data points recommended

---

## ✅ Success Criteria

Epic 2 is successfully tested if:
1. All 7 features execute without errors
2. Models train and generate predictions
3. Metrics are calculated correctly
4. Multi-horizon forecasting works
5. MLflow tracking captures experiments

---

**Last Updated**: December 14, 2025  
**Epic 2 Status**: ✅ 100% Complete

