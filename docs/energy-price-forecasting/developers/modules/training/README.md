# Training Module

**Purpose**: Model training infrastructure including data splitting, cross-validation, and evaluation

---

## Overview

The training module provides comprehensive infrastructure for training ML models, including time-series data splitting, walk-forward validation, model evaluation, and automated training pipelines.

---

## File Structure

```
training/
├── __init__.py              # Module exports
├── data_splitting.py        # Time-series data splitting
├── training_pipeline.py     # Training orchestration
├── evaluation.py            # Model evaluation
├── cross_validation.py      # Cross-validation
├── train_all_models.py     # Automated training script
├── config.py               # Training configuration
└── config.yaml             # Configuration file
```

---

## Key Classes

### TimeSeriesSplitter (`data_splitting.py`)

**Purpose**: Split time-series data for training/validation/testing

**Key Methods**:
- `split(train_ratio, val_ratio, test_ratio)`: Split data by ratios
- `split_by_date(train_end, val_end)`: Split by dates
- `walk_forward_split(window_size, step_size)`: Walk-forward splits

**Usage**:
```python
from training.data_splitting import TimeSeriesSplitter
import pandas as pd

data = pd.DataFrame({
    'date': pd.date_range('2020-01-01', periods=1000),
    'price': [70 + i*0.1 for i in range(1000)]
})

splitter = TimeSeriesSplitter(data, date_column='date')
train, val, test = splitter.split(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
```

---

### TrainingPipeline (`training_pipeline.py`)

**Purpose**: Orchestrate model training process

**Key Methods**:
- `train(model, train_data, val_data)`: Train a model
- `evaluate(model, test_data)`: Evaluate model performance
- `save_model(model, path)`: Save trained model
- `load_model(path)`: Load saved model

**Usage**:
```python
from training.training_pipeline import TrainingPipeline
from models.lstm.lstm_model import LSTMForecaster

pipeline = TrainingPipeline()
model = LSTMForecaster(sequence_length=60, forecast_horizon=7)

# Train
pipeline.train(model, train_data, val_data)

# Evaluate
metrics = pipeline.evaluate(model, test_data)

# Save
pipeline.save_model(model, 'models/lstm_wti_v1.pkl')
```

---

### ModelEvaluator (`evaluation.py`)

**Purpose**: Evaluate model performance with multiple metrics

**Key Methods**:
- `evaluate(model, test_data)`: Calculate all metrics
- `calculate_rmse(predictions, actuals)`: Root Mean Squared Error
- `calculate_mae(predictions, actuals)`: Mean Absolute Error
- `calculate_mape(predictions, actuals)`: Mean Absolute Percentage Error
- `calculate_r2(predictions, actuals)`: R² score
- `calculate_directional_accuracy(predictions, actuals)`: Directional accuracy

**Usage**:
```python
from training.evaluation import ModelEvaluator

evaluator = ModelEvaluator()
metrics = evaluator.evaluate(model, test_data)

print(f"RMSE: {metrics['rmse']}")
print(f"MAE: {metrics['mae']}")
print(f"MAPE: {metrics['mape']}")
print(f"R²: {metrics['r2']}")
```

---

### TimeSeriesCrossValidator (`cross_validation.py`)

**Purpose**: Time-series cross-validation

**Key Methods**:
- `split(n_splits)`: Generate cross-validation splits
- `validate(model, data)`: Run cross-validation

**Usage**:
```python
from training.cross_validation import TimeSeriesCrossValidator

validator = TimeSeriesCrossValidator(data, date_column='date')
scores = validator.validate(model, n_splits=5)
```

---

## Training Configuration

**config.yaml**:
```yaml
training:
  train_ratio: 0.7
  val_ratio: 0.15
  test_ratio: 0.15
  sequence_length: 60
  forecast_horizon: 7
  epochs: 50
  batch_size: 32
  early_stopping:
    patience: 10
    monitor: 'val_loss'
```

---

## Automated Training

**train_all_models.py**:
- Trains all models for all commodities
- Supports parallel training
- Automatic model registration in MLflow
- Configurable via command-line arguments

**Usage**:
```bash
# Train all models
python -m training.train_all_models

# Train specific commodity
python -m training.train_all_models --commodity WTI

# Train specific model type
python -m training.train_all_models --model-type lstm
```

---

## Training Process

1. **Data Preparation**: Load and preprocess data
2. **Feature Engineering**: Create features
3. **Data Splitting**: Split into train/val/test
4. **Model Training**: Train model on training data
5. **Validation**: Evaluate on validation data
6. **Hyperparameter Tuning**: Optimize parameters
7. **Final Evaluation**: Evaluate on test data
8. **Model Registration**: Register in MLflow

---

## Testing

**Test Files**:
- `tests/test_training_pipeline.py`
- `tests/test_data_splitting.py`
- `tests/test_evaluation.py`

**Run Tests**:
```bash
pytest tests/test_training_*.py -v
```

---

## Dependencies

- `pandas`: Data manipulation
- `numpy`: Numerical operations
- `scikit-learn`: Evaluation metrics
- `mlflow`: Model tracking

---

## Integration

The training module is used by:
- **Training Scripts**: Automated model training
- **API**: Model loading and inference
- **Backtesting**: Model evaluation on historical data

---

## Best Practices

1. **Time-Series Splitting**: Always use time-series aware splitting
2. **Walk-Forward Validation**: Use for time-series models
3. **Early Stopping**: Prevent overfitting
4. **Model Checkpointing**: Save best models during training
5. **Experiment Tracking**: Log all training runs to MLflow

---

## Extending

To add new training functionality:

1. Create new class or function
2. Add to training pipeline
3. Update configuration
4. Add tests
5. Update documentation

---

**Last Updated**: December 15, 2025

