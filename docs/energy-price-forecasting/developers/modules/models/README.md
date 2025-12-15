# Models Module

**Purpose**: Machine learning model implementations for energy price forecasting

---

## Overview

The models module contains implementations of multiple ML models:
- **ARIMA/SARIMA**: Statistical time-series models
- **Prophet**: Facebook's forecasting tool
- **LSTM**: Deep learning neural networks
- **Exponential Smoothing**: Traditional forecasting

---

## File Structure

```
models/
├── baseline/
│   ├── __init__.py
│   ├── arima_model.py          # ARIMA/SARIMA model
│   ├── prophet_model.py        # Prophet model
│   ├── exponential_smoothing.py # Exponential smoothing
│   ├── model_comparison.py      # Model comparison utilities
│   └── benchmarking.py         # Benchmarking tools
├── lstm/
│   ├── __init__.py
│   ├── lstm_model.py           # Main LSTM forecaster
│   ├── model_architecture.py   # LSTM architectures
│   ├── data_preparation.py     # Sequence preparation
│   └── integration.py          # Feature integration
└── __init__.py
```

---

## Key Classes

### ARIMAModel

**File**: `models/baseline/arima_model.py`  
**Purpose**: ARIMA/SARIMA statistical forecasting

**Key Methods**:
- `fit(data)`: Train the model
- `predict(steps, return_conf_int)`: Generate forecasts
- `get_model_summary()`: Get model statistics
- `save_model(path)`: Persist model
- `load_model(path)`: Load saved model

**Usage**:
```python
from models.baseline.arima_model import ARIMAModel

model = ARIMAModel(order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
model.fit(train_data)
forecasts, conf_int = model.predict(steps=7, return_conf_int=True)
```

**Features**:
- Automatic order selection (AIC)
- Seasonal ARIMA support
- Confidence intervals
- Model persistence

---

### ProphetModel

**File**: `models/baseline/prophet_model.py`  
**Purpose**: Facebook Prophet forecasting

**Key Methods**:
- `fit(data)`: Train the model
- `predict(steps, return_conf_int)`: Generate forecasts
- `add_regressor(name, values)`: Add external regressors
- `save_model(path)`: Persist model
- `load_model(path)`: Load saved model

**Usage**:
```python
from models.baseline.prophet_model import ProphetModel

model = ProphetModel()
model.fit(train_data)
forecasts = model.predict(steps=7)
```

**Features**:
- Automatic seasonality detection
- Holiday effects
- External regressors
- Uncertainty intervals

---

### LSTMForecaster

**File**: `models/lstm/lstm_model.py`  
**Purpose**: Deep learning LSTM forecasting

**Key Methods**:
- `fit(train_data, validation_data, epochs)`: Train the model
- `predict(data)`: Generate forecasts
- `evaluate(test_data)`: Evaluate model performance
- `save_model(path)`: Persist model
- `load_model(path)`: Load saved model

**Usage**:
```python
from models.lstm.lstm_model import LSTMForecaster

model = LSTMForecaster(sequence_length=60, forecast_horizon=7)
model.fit(train_data, validation_data=val_data, epochs=50)
forecasts = model.predict(test_data)
```

**Features**:
- Multiple architectures (vanilla, bidirectional, stacked)
- Early stopping
- Learning rate scheduling
- Model checkpointing
- Feature integration

---

### ExponentialSmoothingModel

**File**: `models/baseline/exponential_smoothing.py`  
**Purpose**: Exponential smoothing forecasting

**Key Methods**:
- `fit(data)`: Train the model
- `predict(steps)`: Generate forecasts
- `save_model(path)`: Persist model
- `load_model(path)`: Load saved model

**Usage**:
```python
from models.baseline.exponential_smoothing import ExponentialSmoothingModel

model = ExponentialSmoothingModel(trend='add', seasonal='add')
model.fit(train_data)
forecasts = model.predict(steps=7)
```

---

## Model Interface

All models implement a common interface:

```python
class BaseModel:
    def fit(self, data: pd.DataFrame) -> None:
        """Train the model"""
        pass
    
    def predict(self, steps: int, return_conf_int: bool = False):
        """Generate forecasts"""
        pass
    
    def save_model(self, path: str) -> None:
        """Save model to disk"""
        pass
    
    def load_model(self, path: str) -> None:
        """Load model from disk"""
        pass
```

---

## Model Selection

Models are selected based on:
- **Commodity**: Different models for WTI, BRENT, NG
- **Horizon**: Short-term vs long-term
- **Performance**: Best performing model on validation data
- **A/B Testing**: Champion/challenger framework

---

## Model Training

Models are trained via:
- **Training Pipeline**: `training/training_pipeline.py`
- **Hyperparameter Tuning**: `hyperparameter_tuning/`
- **MLflow Tracking**: `mlflow_tracking/`

See [Training Module](../training/README.md) for details.

---

## Model Evaluation

Models are evaluated using:
- **Statistical Metrics**: RMSE, MAE, MAPE, R²
- **Walk-Forward Validation**: Time-series cross-validation
- **Backtesting**: Trading simulation

See [Evaluation Module](../evaluation/README.md) for details.

---

## Model Registry

Models are registered in MLflow:
- **Versioning**: Automatic versioning
- **Staging**: Development → Staging → Production
- **Metadata**: Performance metrics, parameters

See [MLflow Tracking](../mlflow/README.md) for details.

---

## Testing

**Test Files**:
- `tests/test_arima_model.py`
- `tests/test_prophet_model.py`
- `tests/test_lstm_model.py`

**Run Tests**:
```bash
pytest tests/test_arima_model.py -v
pytest tests/test_prophet_model.py -v
pytest tests/test_lstm_model.py -v
```

---

## Dependencies

- `statsmodels`: ARIMA, exponential smoothing
- `prophet`: Prophet model
- `tensorflow/keras`: LSTM models
- `pandas`: Data manipulation
- `numpy`: Numerical operations

---

## Extending

To add a new model:

1. Create model class in `models/`
2. Implement base interface
3. Add to training pipeline
4. Register in model service
5. Add tests
6. Document in this README

---

**Last Updated**: December 15, 2025

