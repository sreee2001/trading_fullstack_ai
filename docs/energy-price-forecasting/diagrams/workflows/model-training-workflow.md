# Model Training Workflow

**Version**: 1.0  
**Date**: December 15, 2025  
**Status**: ✅ Complete

---

## Model Training Workflow Diagram

```mermaid
flowchart TD
    START([Training Trigger<br/>Manual or Scheduled]) --> LOAD[Load Historical Data]
    LOAD --> SPLIT[Train/Test/Validation Split]
    SPLIT --> FEATURE[Feature Engineering]
    
    FEATURE --> INDICATORS[Technical Indicators]
    FEATURE --> LAGS[Lag Features]
    FEATURE --> SEASONAL[Seasonal Decomposition]
    
    INDICATORS --> PREP[Data Preparation]
    LAGS --> PREP
    SEASONAL --> PREP
    
    PREP --> SELECT_MODEL{Select Model Type}
    
    SELECT_MODEL --> ARIMA[ARIMA Model]
    SELECT_MODEL --> PROPHET[Prophet Model]
    SELECT_MODEL --> LSTM[LSTM Model]
    
    ARIMA --> TRAIN_ARIMA[Train ARIMA]
    PROPHET --> TRAIN_PROPHET[Train Prophet]
    LSTM --> TRAIN_LSTM[Train LSTM]
    
    TRAIN_ARIMA --> EVAL[Evaluate Model]
    TRAIN_PROPHET --> EVAL
    TRAIN_LSTM --> EVAL
    
    EVAL --> METRICS[Calculate Metrics<br/>RMSE, MAE, MAPE, R²]
    METRICS --> CHECK{Performance OK?}
    
    CHECK -->|No| TUNE[Hyperparameter Tuning]
    TUNE --> GRID[Grid Search]
    TUNE --> RANDOM[Random Search]
    TUNE --> BAYESIAN[Bayesian Optimization]
    
    GRID --> SELECT_MODEL
    RANDOM --> SELECT_MODEL
    BAYESIAN --> SELECT_MODEL
    
    CHECK -->|Yes| MLFLOW[Log to MLflow]
    MLFLOW --> REGISTER[Register Model]
    REGISTER --> DEPLOY[Deploy to Production]
    DEPLOY --> MONITOR[Monitor Performance]
    
    style START fill:#e1f5ff
    style FEATURE fill:#fff4e1
    style EVAL fill:#fff9c4
    style REGISTER fill:#fff9c4
    style DEPLOY fill:#e8f5e9
```

---

## Hyperparameter Tuning Workflow

```mermaid
sequenceDiagram
    participant Trainer
    participant Tuner
    participant GridSearch
    participant RandomSearch
    participant BayesianOpt
    participant Model
    participant MLflow

    Trainer->>Tuner: Start Tuning
    Tuner->>GridSearch: Grid Search
    GridSearch->>Model: Train with Params
    Model-->>GridSearch: Performance
    GridSearch-->>Tuner: Best Params
    
    Tuner->>RandomSearch: Random Search
    RandomSearch->>Model: Train with Params
    Model-->>RandomSearch: Performance
    RandomSearch-->>Tuner: Best Params
    
    Tuner->>BayesianOpt: Bayesian Optimization
    BayesianOpt->>Model: Train with Params
    Model-->>BayesianOpt: Performance
    BayesianOpt-->>Tuner: Best Params
    
    Tuner->>Tuner: Compare Results
    Tuner->>MLflow: Log Best Model
    MLflow-->>Trainer: Model Registered
```

---

## Walk-Forward Validation Workflow

```mermaid
flowchart TD
    START([Start Walk-Forward]) --> INIT[Initialize Windows]
    INIT --> TRAIN_WIN[Training Window]
    TRAIN_WIN --> TEST_WIN[Test Window]
    TEST_WIN --> TRAIN[Train Model]
    TRAIN --> PREDICT[Generate Predictions]
    PREDICT --> EVAL[Evaluate on Test]
    EVAL --> STORE[Store Results]
    STORE --> SHIFT{More Windows?}
    SHIFT -->|Yes| EXPAND[Expand/Shift Window]
    EXPAND --> TRAIN_WIN
    SHIFT -->|No| AGGREGATE[Aggregate Results]
    AGGREGATE --> METRICS[Calculate Overall Metrics]
    METRICS --> END([Validation Complete])
    
    style START fill:#e1f5ff
    style TRAIN fill:#fff4e1
    style EVAL fill:#fff9c4
    style METRICS fill:#e8f5e9
```

---

## MLflow Experiment Tracking Flow

```mermaid
sequenceDiagram
    participant Training
    participant MLflow
    participant Registry
    participant API

    Training->>MLflow: Start Experiment
    MLflow-->>Training: Experiment ID
    Training->>Training: Train Model
    Training->>MLflow: Log Parameters
    Training->>MLflow: Log Metrics
    Training->>MLflow: Log Artifacts
    Training->>MLflow: End Run
    MLflow->>Registry: Register Model
    Registry-->>MLflow: Model Version
    MLflow-->>Training: Training Complete
    API->>Registry: Request Model
    Registry-->>API: Load Model
```

---

**Last Updated**: December 15, 2025

