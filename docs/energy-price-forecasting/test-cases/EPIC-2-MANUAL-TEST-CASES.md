# Epic 2: Core ML Model Development - Manual Test Cases

**Project**: Energy Price Forecasting System  
**Date**: December 15, 2025  
**Epic 2 Status**: ✅ 100% Complete (7/7 features)

---

## Executive Summary

### Epic 2: Core ML Model Development
**Status**: ✅ **COMPLETE** (100%)  
**Description**: Comprehensive machine learning forecasting system with feature engineering, multiple model types (ARIMA, Prophet, LSTM), hyperparameter tuning, experiment tracking (MLflow), and multi-horizon forecasting capabilities.

**Features**:
1. ✅ Feature Engineering Pipeline
2. ✅ Baseline Statistical Models (ARIMA/SARIMA, Prophet)
3. ✅ LSTM Neural Network Model
4. ✅ Model Training Infrastructure
5. ✅ Hyperparameter Tuning Framework
6. ✅ Model Versioning & Experiment Tracking (MLflow)
7. ✅ Multi-Horizon Forecasting Implementation

---

## How to Test Epic Completion

### Epic 2 Testing Approach
1. **Unit Tests**: Run `pytest tests/` in `src/energy-price-forecasting/`
2. **Manual Integration Tests**: Use example scripts in `src/energy-price-forecasting/examples/`
3. **Feature-Specific Tests**: Each feature has dedicated test scripts
4. **Visual Inspection**: Review generated plots and reports
5. **MLflow UI**: Check experiment tracking in MLflow UI

---

## Manual Test Cases

### EPIC 2: Core ML Model Development

#### Feature 2.1: Feature Engineering Pipeline

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-2.1.1 | Basic Feature Engineering | Run: `python examples/test_epic2_step1_feature_engineering.py`. Verify features created. | 50+ features created. Original columns preserved. No errors. |
| TC-2.1.2 | Technical Indicators | Create FeatureEngineer. Transform data. Check SMA, EMA, RSI, MACD, Bollinger Bands. | All indicators calculated. Values reasonable. No NaN values (except initial periods). |
| TC-2.1.3 | Time-Based Features | Transform data. Check lag features, rolling statistics, seasonal decomposition. | Lag features created (1, 7, 30 days). Rolling stats calculated. Seasonal components present. |
| TC-2.1.4 | Date Features | Transform data. Check date features: day_of_week, month, quarter, year, is_weekend. | All date features created. Values correct. Weekend flag accurate. |
| TC-2.1.5 | Feature Importance | Call `get_feature_importance()`. Verify ranking. | Importance scores calculated. Features ranked. Top features identified. |
| TC-2.1.6 | Feature Selection | Call `select_top_features(top_n=20)`. Verify selection. | Top 20 features selected. DataFrame reduced. Important features retained. |
| TC-2.1.7 | Configuration Management | Load configuration from YAML. Verify settings applied. | Configuration loaded. Settings applied. Custom config works. |
| TC-2.1.8 | Missing Value Handling | Transform data with missing values. Check handling strategy. | Missing values handled (forward_fill/drop/mean/zero). No errors. Data quality maintained. |

#### Feature 2.2: Baseline Statistical Models

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-2.2.1 | ARIMA Model Training | Run: `python examples/test_epic2_step2_baseline_models.py`. Train ARIMA model. | Model trains successfully. Auto-ARIMA selects parameters. No errors. |
| TC-2.2.2 | ARIMA Prediction | Generate predictions with trained ARIMA model. | Predictions generated. Length matches requested steps. Values reasonable. |
| TC-2.2.3 | Prophet Model Training | Train Prophet model with time series data. | Model trains successfully. Trend and seasonality captured. No errors. |
| TC-2.2.4 | Prophet Prediction | Generate predictions with Prophet. | Predictions generated. Confidence intervals present. Values reasonable. |
| TC-2.2.5 | Model Comparison | Compare ARIMA and Prophet models. Get comparison DataFrame. | Comparison table generated. Metrics calculated for both. Best model identified. |
| TC-2.2.6 | Exponential Smoothing | Train Exponential Smoothing model. Generate predictions. | Model trains. Predictions generated. Trend and seasonality handled. |

#### Feature 2.3: LSTM Neural Network Model

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-2.3.1 | LSTM Model Training | Run: `python examples/test_epic2_step3_lstm.py`. Train basic LSTM. | Model trains. Training progress displayed. Loss decreases. No errors. |
| TC-2.3.2 | LSTM Prediction | Generate predictions with trained LSTM. | Predictions generated. Shape correct. Values reasonable. |
| TC-2.3.3 | Bidirectional LSTM | Train bidirectional LSTM. Compare with basic LSTM. | Bidirectional LSTM trains. Performance may differ. Both models work. |
| TC-2.3.4 | LSTM with Features | Train LSTM with feature-engineered data. Verify integration. | Features integrated. Model trains with multiple features. Performance improved. |
| TC-2.3.5 | Sequence Preparation | Check sequence data preparation. Verify shapes. | Sequences created correctly. Input/output shapes match. No shape errors. |
| TC-2.3.6 | Model Architecture | Inspect LSTM architecture. Verify layers and parameters. | Architecture correct. Layers configured. Parameters match specification. |
| TC-2.3.7 | Multi-Output LSTM | Train multi-output LSTM for multiple horizons. | Multi-output model trains. Predictions for all horizons generated. |

#### Feature 2.4: Model Training Infrastructure

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-2.4.1 | Time Series Splitting | Run: `python examples/test_epic2_step4_training_infrastructure.py`. Split data temporally. | Train/validation/test splits created. Temporal order preserved. No leakage. |
| TC-2.4.2 | Model Evaluation | Evaluate model with ModelEvaluator. Check all metrics. | RMSE, MAE, MAPE, R², Directional Accuracy calculated. All metrics valid. |
| TC-2.4.3 | Walk-Forward Validation | Run walk-forward validation. Verify expanding window. | Validation runs. Expanding window works. Metrics calculated per fold. |
| TC-2.4.4 | Walk-Forward Rolling Window | Run walk-forward with rolling window. Verify sliding window. | Rolling window works. Window size constant. Window slides forward. |
| TC-2.4.5 | Aggregated Metrics | Get aggregated metrics from walk-forward validation. | Mean, std, min, max calculated. Summary statistics accurate. |
| TC-2.4.6 | Temporal Integrity | Verify no temporal leakage in validation. | Test data always after training data. No overlap. Temporal order maintained. |

#### Feature 2.5: Hyperparameter Tuning Framework

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-2.5.1 | Grid Search Tuning | Run: `python examples/test_epic2_step5_hyperparameter_tuning.py`. Use grid search. | Grid search completes. All combinations tested. Best parameters found. |
| TC-2.5.2 | Random Search Tuning | Use random search method. Verify sampling. | Random search completes. Parameters sampled randomly. Best result tracked. |
| TC-2.5.3 | Bayesian Optimization | Use Bayesian optimization (Optuna). Verify intelligent search. | Bayesian optimization completes. Fewer trials than grid search. Good results. |
| TC-2.5.4 | Best Result Retrieval | Get best result from tuner. Verify parameters and score. | Best parameters returned. Best score tracked. Model available. |
| TC-2.5.5 | Trial History | Access trial history. Verify all trials logged. | History available. All trials recorded. Parameters and scores tracked. |

#### Feature 2.6: Model Versioning & Experiment Tracking (MLflow)

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-2.6.1 | MLflow Setup | Run: `python examples/test_epic2_step6_mlflow.py`. Setup MLflow experiment. | Experiment created. MLflow tracking server accessible. No errors. |
| TC-2.6.2 | Log Parameters | Log hyperparameters to MLflow. Verify in UI. | Parameters logged. Visible in MLflow UI. All parameters recorded. |
| TC-2.6.3 | Log Metrics | Log evaluation metrics. Verify in UI. | Metrics logged. Visible in MLflow UI. Metrics tracked over time. |
| TC-2.6.4 | Log Artifacts | Log model artifacts and plots. Verify storage. | Artifacts logged. Files stored. Accessible in MLflow UI. |
| TC-2.6.5 | Model Registry | Register model in MLflow registry. Verify versioning. | Model registered. Version assigned. Metadata stored. |
| TC-2.6.6 | Search Runs | Search for runs by parameters/metrics. Verify filtering. | Runs found. Filtering works. Search results accurate. |

#### Feature 2.7: Multi-Horizon Forecasting Implementation

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-2.7.1 | Multi-Horizon Forecaster | Run: `python examples/test_epic2_step7_multi_horizon.py`. Create forecaster. | Forecaster initialized. Supports multiple horizons. No errors. |
| TC-2.7.2 | Multi-Output Model | Train multi-output model for 1, 7, 30-day horizons. | Model trains. Predictions for all horizons generated. All horizons work. |
| TC-2.7.3 | Separate Horizon Models | Train separate models for each horizon. Compare performance. | Separate models train. Each horizon has dedicated model. Performance may vary. |
| TC-2.7.4 | Horizon Evaluation | Evaluate predictions per horizon. Check metrics. | Metrics calculated per horizon. Horizon-specific performance visible. |
| TC-2.7.5 | Horizon Comparison | Compare performance across horizons. Identify best horizon. | Comparison table generated. Best horizon identified. Performance trends visible. |

---

## Test Execution Summary

### Test Results Summary

| Feature | Test Cases | Passed | Failed | Status |
|---------|------------|--------|--------|--------|
| 2.1 Feature Engineering | 8 | 8 | 0 | ✅ Complete |
| 2.2 Baseline Models | 6 | 6 | 0 | ✅ Complete |
| 2.3 LSTM Models | 7 | 7 | 0 | ✅ Complete |
| 2.4 Training Infrastructure | 6 | 6 | 0 | ✅ Complete |
| 2.5 Hyperparameter Tuning | 5 | 5 | 0 | ✅ Complete |
| 2.6 MLflow Integration | 6 | 6 | 0 | ✅ Complete |
| 2.7 Multi-Horizon | 5 | 5 | 0 | ✅ Complete |
| **TOTAL** | **43** | **43** | **0** | ✅ **100%** |

### Test Execution Instructions

1. **Environment Setup**:
   ```bash
   cd src/energy-price-forecasting
   source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
   pip install -r requirements.txt
   ```

2. **Install Epic 2 Dependencies** (if not already installed):
   ```bash
   pip install pmdarima prophet tensorflow mlflow optuna
   ```

3. **Run Unit Tests**:
   ```bash
   pytest tests/ -v
   ```

4. **Run Manual Tests**:
   ```bash
   python examples/test_epic2_step1_feature_engineering.py
   python examples/test_epic2_step2_baseline_models.py
   python examples/test_epic2_step3_lstm.py
   python examples/test_epic2_step4_training_infrastructure.py
   python examples/test_epic2_step5_hyperparameter_tuning.py
   python examples/test_epic2_step6_mlflow.py
   python examples/test_epic2_step7_multi_horizon.py
   ```

5. **Check MLflow UI** (if MLflow tracking server running):
   ```bash
   mlflow ui
   # Open http://localhost:5000 in browser
   ```

---

## Related Documentation

- [Epic 2 Comprehensive Documentation](../epics/epic-2/EPIC-2-COMPREHENSIVE-DOCUMENTATION.md)
- [Epic 2 Kickoff](../epics/epic-2/EPIC-2-KICKOFF.md)
- [Epic 2 Celebration](../status/epic-completion/EPIC-2-CELEBRATION.md)
- [Epic 2 Manual Testing Guide](../instructions/testing/EPIC-2-MANUAL-TESTING-GUIDE.md)
- [Epic 2 Test Results](../status/test-results/EPIC-2-MANUAL-TESTING-RESULTS.md)
- [Epic 2 Dependency Setup](../instructions/setup/EPIC-2-DEPENDENCY-SETUP.md)

---

**Last Updated**: December 15, 2025  
**Test Cases**: 43  
**Status**: ✅ All Test Cases Defined

