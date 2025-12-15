# Energy Price Forecasting System - Model Methodology

**Version**: 1.0  
**Last Updated**: December 15, 2025  
**Status**: Epic 2 Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Model Selection Rationale](#model-selection-rationale)
3. [Baseline Models](#baseline-models)
4. [Deep Learning Models](#deep-learning-models)
5. [Feature Engineering](#feature-engineering)
6. [Training Methodology](#training-methodology)
7. [Evaluation Methodology](#evaluation-methodology)
8. [Hyperparameter Tuning](#hyperparameter-tuning)
9. [Model Comparison](#model-comparison)

---

## Overview

The Energy Price Forecasting System employs multiple forecasting models to predict energy commodity prices (WTI, Brent, Natural Gas) across different time horizons (1-day, 7-day, 30-day). The system uses an ensemble approach, combining statistical models and deep learning models to achieve robust predictions.

### Forecasting Objectives

- **Short-term (1-day)**: Daily price movements for trading decisions
- **Medium-term (7-day)**: Weekly trends for position management
- **Long-term (30-day)**: Monthly outlook for strategic planning

### Model Types

1. **Baseline Statistical Models**: ARIMA/SARIMA, Prophet, Exponential Smoothing
2. **Deep Learning Models**: LSTM (Long Short-Term Memory) networks
3. **Ensemble Approaches**: Weighted combinations of model predictions

---

## Model Selection Rationale

### Why Multiple Models?

1. **Diversity**: Different models capture different patterns
2. **Robustness**: Ensemble reduces overfitting risk
3. **Horizon-Specific**: Some models perform better at specific horizons
4. **Baseline Comparison**: Statistical models provide interpretable baselines

### Model Selection Criteria

- **Accuracy**: RMSE, MAE, MAPE metrics
- **Directional Accuracy**: Ability to predict price direction
- **Robustness**: Performance across different market conditions
- **Interpretability**: Understanding model decisions
- **Computational Cost**: Training and inference time

---

## Baseline Models

### 1. ARIMA/SARIMA Models

**Purpose**: Capture linear trends and seasonal patterns

**Methodology**:
- **ARIMA (AutoRegressive Integrated Moving Average)**: Models non-seasonal time series
- **SARIMA (Seasonal ARIMA)**: Extends ARIMA with seasonal components
- **Auto-selection**: Uses `pmdarima` for automatic order selection

**Mathematical Formulation**:
```
ARIMA(p, d, q):
(1 - φ₁B - ... - φₚBᵖ)(1 - B)ᵈyₜ = (1 + θ₁B + ... + θₑBᵑ)εₜ

SARIMA(p, d, q)(P, D, Q)ₛ:
Adds seasonal components with period s
```

**Strengths**:
- Interpretable parameters
- Handles trends and seasonality
- Fast training and inference
- Good baseline performance

**Limitations**:
- Assumes linear relationships
- Requires stationary data
- Limited to univariate forecasting

**Implementation**:
- Library: `pmdarima` (auto_arima)
- Order selection: AIC/BIC minimization
- Differencing: Automatic stationarity detection

### 2. Facebook Prophet

**Purpose**: Robust forecasting with built-in seasonality handling

**Methodology**:
- **Additive Model**: Decomposes time series into components
- **Trend**: Piecewise linear or logistic growth
- **Seasonality**: Fourier series for daily/weekly/yearly patterns
- **Holidays**: Custom holiday effects

**Mathematical Formulation**:
```
y(t) = g(t) + s(t) + h(t) + εₜ

where:
- g(t): trend component
- s(t): seasonal component
- h(t): holiday effects
- εₜ: error term
```

**Strengths**:
- Handles missing data and outliers
- Automatic seasonality detection
- Interpretable components
- Robust to regime changes

**Limitations**:
- Assumes additive seasonality
- May struggle with rapid changes
- Requires sufficient historical data

**Implementation**:
- Library: `prophet`
- Parameters: Growth rate, seasonality modes, changepoints
- Cross-validation: Time-series cross-validation

### 3. Exponential Smoothing

**Purpose**: Simple, interpretable forecasting for trended data

**Methodology**:
- **Simple Exponential Smoothing**: Level only
- **Holt's Method**: Level + trend
- **Holt-Winters**: Level + trend + seasonality

**Mathematical Formulation**:
```
Holt-Winters (Additive):
ŷₜ₊ₕ = (lₜ + hbₜ) + sₜ₊ₕ₋ₘ₊₁

where:
- lₜ: level
- bₜ: trend
- sₜ: seasonal component
- m: seasonal period
```

**Strengths**:
- Simple and fast
- Good for short-term forecasts
- Interpretable components

**Limitations**:
- Limited to additive seasonality
- May not capture complex patterns

**Implementation**:
- Library: `statsmodels` (ExponentialSmoothing)
- Parameters: Smoothing constants (α, β, γ)

---

## Deep Learning Models

### LSTM (Long Short-Term Memory)

**Purpose**: Capture complex non-linear patterns and long-term dependencies

**Architecture**:
```
Input Layer → LSTM Layer(s) → Dense Layer(s) → Output Layer
```

**LSTM Cell Structure**:
```
Forget Gate: fₜ = σ(Wf · [hₜ₋₁, xₜ] + bf)
Input Gate:  iₜ = σ(Wi · [hₜ₋₁, xₜ] + bi)
Output Gate: oₜ = σ(Wo · [hₜ₋₁, xₜ] + bo)
Cell State:  Cₜ = fₜ * Cₜ₋₁ + iₜ * tanh(WC · [hₜ₋₁, xₜ] + bC)
Hidden State: hₜ = oₜ * tanh(Cₜ)
```

**Model Configuration**:
- **Layers**: 2-3 LSTM layers (64-128 units each)
- **Dense Layers**: 1-2 fully connected layers (32-64 units)
- **Dropout**: 0.2-0.3 for regularization
- **Activation**: ReLU (hidden), Linear (output)
- **Optimizer**: Adam with learning rate 0.001-0.01
- **Loss Function**: Mean Squared Error (MSE)

**Input Features**:
- Historical prices (lagged features)
- Technical indicators (RSI, MACD, Bollinger Bands)
- Time-based features (day of week, month, season)
- Seasonal decomposition components

**Training Process**:
1. **Data Preparation**: 
   - Sequence creation (lookback window: 30-60 days)
   - Feature scaling (StandardScaler)
   - Train/validation/test split (70/15/15)

2. **Training**:
   - Batch size: 32-64
   - Epochs: 50-100 (with early stopping)
   - Validation monitoring: Validation loss
   - Callbacks: EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

3. **Multi-Horizon Forecasting**:
   - Single model with multiple outputs (1-day, 7-day, 30-day)
   - Separate models per horizon
   - Recursive forecasting (1-day model chained)

**Strengths**:
- Captures non-linear patterns
- Handles long-term dependencies
- Flexible feature engineering
- Can learn complex relationships

**Limitations**:
- Requires large datasets
- Computationally expensive
- Less interpretable than statistical models
- Hyperparameter sensitivity

**Implementation**:
- Framework: TensorFlow/Keras
- Architecture: Sequential or Functional API
- Multi-output: Multiple dense outputs for different horizons

---

## Feature Engineering

### Technical Indicators

1. **Moving Averages**:
   - SMA (Simple Moving Average): 7, 14, 30 days
   - EMA (Exponential Moving Average): 7, 14, 30 days

2. **Momentum Indicators**:
   - RSI (Relative Strength Index): 14-day period
   - MACD (Moving Average Convergence Divergence)
   - Stochastic Oscillator

3. **Volatility Indicators**:
   - Bollinger Bands (20-day, 2 std dev)
   - ATR (Average True Range)

4. **Trend Indicators**:
   - ADX (Average Directional Index)
   - Parabolic SAR

### Time-Based Features

- **Temporal**: Day of week, Month, Quarter, Year
- **Cyclical Encoding**: Sine/cosine encoding for cyclical patterns
- **Holiday Indicators**: Trading holidays, month-end effects

### Lag Features

- **Price Lags**: 1, 7, 14, 30 days
- **Return Lags**: Daily returns, weekly returns
- **Volume Lags**: (if available)

### Seasonal Decomposition

- **STL Decomposition**: Trend, Seasonal, Residual components
- **Fourier Features**: Frequency domain features

### Feature Selection

- **Correlation Analysis**: Remove highly correlated features
- **Feature Importance**: SHAP values for LSTM models
- **Permutation Importance**: For statistical models

---

## Training Methodology

### Data Splitting Strategy

**Time-Series Split**:
- **Training**: 70% (oldest data)
- **Validation**: 15% (middle data)
- **Test**: 15% (newest data)

**Walk-Forward Validation**:
- Expanding window: Training set grows over time
- Rolling window: Fixed-size training window

### Cross-Validation

**Time-Series Cross-Validation**:
- K-fold with temporal ordering preserved
- No data leakage between folds
- Stratified by market regime (if applicable)

### Training Process

1. **Data Preparation**:
   - Missing value handling (forward fill, interpolation)
   - Outlier detection and treatment
   - Feature scaling (StandardScaler/MinMaxScaler)

2. **Model Training**:
   - Baseline models: Fit on training set
   - LSTM: Train with validation monitoring
   - Early stopping: Prevent overfitting

3. **Validation**:
   - Evaluate on validation set
   - Tune hyperparameters
   - Select best model configuration

4. **Testing**:
   - Final evaluation on test set
   - Report metrics (RMSE, MAE, MAPE, R²)
   - Compare with baseline

---

## Evaluation Methodology

### Statistical Metrics

1. **RMSE (Root Mean Squared Error)**:
   ```
   RMSE = √(Σ(yᵢ - ŷᵢ)² / n)
   ```
   - Measures average prediction error magnitude
   - Sensitive to outliers

2. **MAE (Mean Absolute Error)**:
   ```
   MAE = Σ|yᵢ - ŷᵢ| / n
   ```
   - Average absolute prediction error
   - Less sensitive to outliers than RMSE

3. **MAPE (Mean Absolute Percentage Error)**:
   ```
   MAPE = (100/n) × Σ|yᵢ - ŷᵢ| / |yᵢ|
   ```
   - Percentage error, scale-independent
   - Useful for comparing across commodities

4. **R² (Coefficient of Determination)**:
   ```
   R² = 1 - (SS_res / SS_tot)
   ```
   - Proportion of variance explained
   - Range: 0 to 1 (higher is better)

5. **Directional Accuracy**:
   ```
   DA = (Correct Direction Predictions / Total Predictions) × 100
   ```
   - Percentage of correct direction predictions
   - Important for trading applications

### Risk-Adjusted Metrics

1. **Sharpe Ratio**:
   ```
   Sharpe = (Mean Return - Risk-Free Rate) / Std Dev of Returns
   ```
   - Risk-adjusted return measure

2. **Sortino Ratio**:
   ```
   Sortino = (Mean Return - Risk-Free Rate) / Downside Deviation
   ```
   - Focuses on downside risk

3. **Maximum Drawdown**:
   ```
   MDD = max((Peak - Trough) / Peak)
   ```
   - Largest peak-to-trough decline

### Horizon-Specific Evaluation

- **1-Day Horizon**: Focus on directional accuracy and RMSE
- **7-Day Horizon**: Balance accuracy and trend capture
- **30-Day Horizon**: Emphasize trend accuracy over daily precision

---

## Hyperparameter Tuning

### Tuning Methods

1. **Grid Search**:
   - Exhaustive search over parameter grid
   - Guaranteed to find best in grid
   - Computationally expensive

2. **Random Search**:
   - Random sampling from parameter space
   - More efficient than grid search
   - Good for high-dimensional spaces

3. **Bayesian Optimization (Optuna)**:
   - Uses previous evaluations to guide search
   - Most efficient for expensive evaluations
   - Best for LSTM models

### Hyperparameters by Model

**ARIMA/SARIMA**:
- Order (p, d, q): Auto-selected by pmdarima
- Seasonal order (P, D, Q, s): Auto-selected

**Prophet**:
- Growth: 'linear' or 'logistic'
- Seasonality modes: 'additive' or 'multiplicative'
- Changepoint prior scale: 0.05-0.5
- Seasonality prior scale: 1-10

**LSTM**:
- LSTM units: [32, 64, 128]
- Number of layers: [1, 2, 3]
- Dropout rate: [0.1, 0.2, 0.3]
- Learning rate: [0.001, 0.01, 0.1]
- Batch size: [16, 32, 64]
- Lookback window: [30, 60, 90]

### Tuning Process

1. **Define Search Space**: Parameter ranges/distributions
2. **Select Optimization Method**: Grid/Random/Bayesian
3. **Run Trials**: Train and evaluate models
4. **Select Best**: Based on validation metric
5. **Final Evaluation**: Test set evaluation

---

## Model Comparison

### Comparison Framework

**Statistical Metrics**:
- RMSE, MAE, MAPE, R²
- Directional Accuracy
- Horizon-specific performance

**Risk Metrics**:
- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown
- Win Rate

**Operational Metrics**:
- Training time
- Inference time
- Model size
- Interpretability

### Model Selection Strategy

1. **Baseline Comparison**: All models vs. naive forecast
2. **Horizon Analysis**: Best model per horizon
3. **Ensemble Consideration**: Weighted combination
4. **Production Selection**: Balance accuracy and operational cost

### Ensemble Approaches

**Weighted Average**:
```
ŷ_ensemble = Σ(wᵢ × ŷᵢ)

where:
- wᵢ: weight for model i
- ŷᵢ: prediction from model i
- Σwᵢ = 1
```

**Weight Assignment**:
- Equal weights: Simple average
- Performance-based: Weighted by validation RMSE
- Horizon-specific: Different weights per horizon

---

## Best Practices

1. **Data Quality**: Ensure high-quality input data (98%+ quality target)
2. **Feature Engineering**: Domain knowledge + data-driven features
3. **Validation**: Proper time-series cross-validation
4. **Monitoring**: Track model performance over time
5. **Retraining**: Regular retraining with new data
6. **Versioning**: Track model versions and experiments
7. **Documentation**: Document model decisions and rationale

---

**Document Version**: 1.0  
**Last Updated**: December 15, 2025  
**Maintained By**: ML Team

