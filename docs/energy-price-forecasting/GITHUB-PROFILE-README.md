# 🔮 Energy Price Forecasting System

**A production-ready ML system for forecasting WTI crude oil, Brent crude, and natural gas prices**

[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)]()
[![Epic 1](https://img.shields.io/badge/Epic%201-Complete-success)]()
[![Epic 2](https://img.shields.io/badge/Epic%202-Complete-success)]()
[![Epic 3](https://img.shields.io/badge/Epic%203-Complete-success)]()
[![Python](https://img.shields.io/badge/Python-3.13-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

---

## 🎯 What This Project Does

An **end-to-end machine learning system** that forecasts energy commodity prices (WTI, Brent, Natural Gas) using:
- **Multi-source data ingestion** from EIA, FRED, and Yahoo Finance APIs
- **Advanced ML models** (ARIMA, Prophet, LSTM) with hyperparameter tuning
- **Comprehensive backtesting** with walk-forward validation and risk metrics
- **Production-ready infrastructure** with PostgreSQL/TimescaleDB and MLflow tracking

**Perfect for**: Quantitative traders, energy analysts, ML engineers, and anyone interested in time-series forecasting and algorithmic trading systems.

---

## 💡 How It Can Help You

- **Learn ML Engineering**: See production-grade ML pipelines, experiment tracking, and model versioning
- **Understand Time-Series Forecasting**: Explore ARIMA, Prophet, and LSTM implementations with real-world data
- **Study Backtesting Systems**: Learn walk-forward validation, risk metrics (Sharpe, Sortino), and trading simulation
- **Explore MLOps Practices**: MLflow integration, automated testing, and deployment-ready architecture
- **Reference Implementation**: Use as a template for your own forecasting or trading systems

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Python 3.13, FastAPI (planned), PostgreSQL, TimescaleDB |
| **Machine Learning** | TensorFlow/Keras, scikit-learn, pmdarima, Prophet, Optuna |
| **Data Engineering** | pandas, numpy, yfinance, requests, APScheduler |
| **MLOps** | MLflow, pytest, coverage |
| **DevOps** | Docker, Git, CI/CD (planned) |
| **Visualization** | matplotlib, seaborn |

---

## 📊 High-Level Progress

| Epic | Features | Status | Description |
|------|----------|--------|-------------|
| **Epic 1** | 6/6 | ✅ **100%** | Data Foundation & Infrastructure |
| **Epic 2** | 7/7 | ✅ **100%** | Core ML Model Development |
| **Epic 3** | 7/7 | ✅ **100%** | Model Evaluation & Backtesting |
| **Epic 4** | 0/9 | 🔄 **Next** | API Service Layer |
| **Epic 5-8** | 0/33 | 📋 **Planned** | UI, MLOps, Analytics, QA |

**Overall**: 20/64 features complete (31.3%) | 100+ user stories implemented

---

## 🎨 Key Artifacts & Outputs

### 📈 Forecast Visualizations
- **Predicted vs Actual Prices**: Time-series plots comparing model predictions with real prices
- **Multi-Horizon Forecasts**: 1-day, 7-day, and 30-day forecast visualizations
- **Confidence Intervals**: Uncertainty quantification for predictions

### 📊 Backtesting Reports
- **Equity Curves**: Cumulative P&L over time with drawdown visualization
- **Trade Distribution**: Histograms showing win/loss distribution
- **Performance Metrics**: Comprehensive tables with Sharpe Ratio, Sortino Ratio, Max Drawdown, Win Rate

### 🔬 Model Comparison Dashboards
- **Statistical Metrics**: RMSE, MAE, MAPE, R² comparison across models
- **Risk-Adjusted Returns**: Sharpe and Sortino ratios for model selection
- **Best Model Selection**: Automated identification of top-performing models

### 📋 Experiment Tracking
- **MLflow Experiments**: Tracked hyperparameters, metrics, and model artifacts
- **Model Registry**: Versioned models with metadata and performance history
- **Visualization Artifacts**: Saved plots and reports for each experiment run

### 🗄️ Data Quality Reports
- **Validation Scores**: 98%+ data quality across all sources
- **Data Freshness**: Automated monitoring of data pipeline health
- **Quality Metrics**: Completeness, consistency, and accuracy scores

---

## 🚀 Quick Stats

- **Production Code**: ~16,000+ lines
- **Test Coverage**: ~85%+ (100+ unit tests)
- **Data Quality**: 98%+ across all sources
- **Models Implemented**: 3 types (ARIMA, Prophet, LSTM)
- **Features Generated**: 50+ from raw price data
- **Forecast Horizons**: 1-day, 7-day, 30-day
- **Documentation**: 50+ files, comprehensive guides

---

## 📚 Documentation Highlights

- [📖 Comprehensive Epic Documentation](docs/energy-price-forecasting/epics/)
- [🧪 Manual Test Cases](docs/energy-price-forecasting/test-cases/) (85+ test cases)
- [📊 Project Tracker](docs/energy-price-forecasting/project-plan/04-project-tracker.md)
- [🏗️ Architecture Documentation](docs/energy-price-forecasting/rules/)

---

## 🔗 Quick Links

- **Repository**: [trading_fullstack_ai](https://github.com/yourusername/trading_fullstack_ai)
- **Project Path**: `src/energy-price-forecasting/`
- **Documentation**: `docs/energy-price-forecasting/`
- **Examples**: `src/energy-price-forecasting/examples/`

---

**Status**: 🔄 Actively developing Epic 4 (API Service Layer)  
**Last Updated**: December 2025  
**License**: MIT

