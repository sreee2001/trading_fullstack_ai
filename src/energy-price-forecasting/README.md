# Energy Price Forecasting System

An AI-powered system for forecasting energy commodity prices (WTI Crude Oil, Brent Crude, Natural Gas) using advanced machine learning techniques including LSTM neural networks and statistical models.

## 🎯 Project Overview

This project demonstrates enterprise-level AI/ML engineering for energy trading applications, showcasing:
- **Machine Learning**: LSTM, ARIMA/SARIMA time-series forecasting
- **Full-Stack Development**: FastAPI backend + React TypeScript frontend
- **Data Engineering**: Multi-source ETL pipeline with PostgreSQL/TimescaleDB
- **MLOps**: Model versioning, A/B testing, performance monitoring
- **Trading Analytics**: Backtesting, risk metrics (Sharpe ratio, max drawdown)

**Target Use Case**: Energy trading desks requiring accurate price forecasts and trading signals

---

## 🏗️ Architecture

```
src/energy-price-forecasting/
├── data-ingestion/     # ETL pipeline, API clients (EIA, FRED, Yahoo Finance)
├── models/             # ML models (LSTM, ARIMA)
├── backtesting/        # Trading simulation and evaluation
├── api/                # FastAPI REST API
├── dashboard/          # React TypeScript frontend
├── utils/              # Shared utilities
├── config/             # Configuration management
└── tests/              # Comprehensive test suite
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 15+ with TimescaleDB extension
- Redis (for caching)
- Node.js 18+ (for frontend)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd trading_fullstack_ai/src/energy-price-forecasting
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Setup database**
```bash
# Install PostgreSQL + TimescaleDB
# Create database
createdb energy_forecasting

# Run migrations (coming soon)
# python scripts/init_db.py
```

---

## 📊 Features

### Implemented ✅
- [x] Project structure and documentation
- [ ] EIA API integration
- [ ] FRED API integration
- [ ] Yahoo Finance data ingestion
- [ ] PostgreSQL + TimescaleDB setup
- [ ] Data validation framework
- [ ] Feature engineering pipeline
- [ ] LSTM forecasting model
- [ ] ARIMA baseline models
- [ ] Backtesting framework
- [ ] FastAPI REST API
- [ ] React dashboard
- [ ] Docker deployment

### Roadmap 🗓️
See `docs/energy-price-forecasting/project-plan/04-project-tracker.md` for detailed progress tracking.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_eia_client.py
```

---

## 📖 Documentation

Comprehensive documentation available in `docs/energy-price-forecasting/`:

- **Project Plan**: Epic breakdown, feature specs, tracker
- **User Stories**: Detailed implementation guides (~175 stories)
- **Architecture**: System design and component diagrams (coming soon)
- **API Docs**: Available at `http://localhost:8000/docs` when API running

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Languages** | Python, TypeScript, SQL |
| **ML/AI** | PyTorch/TensorFlow, scikit-learn, statsmodels |
| **Data** | Pandas, NumPy, PostgreSQL, TimescaleDB |
| **Backend** | FastAPI, Pydantic, SQLAlchemy |
| **Frontend** | React, TypeScript, Chart.js/Recharts |
| **DevOps** | Docker, GitHub Actions, MLflow |
| **Testing** | pytest, pytest-cov |

---

## 📈 Model Performance

*Coming soon - will include accuracy metrics, Sharpe ratios, and backtesting results*

---

## 🤝 Contributing

This is a portfolio project. For questions or suggestions, please open an issue.

---

## 📝 License

MIT License - see LICENSE file for details

---

## 👤 Author

**Srikanth**
- Portfolio project for AI/ML Software Engineer positions
- Demonstrates skills in energy trading, ML, full-stack development, and MLOps

---

## 🙏 Acknowledgments

- Data sources: EIA, FRED, Yahoo Finance
- Inspired by real-world energy trading applications

---

**Status**: 🔄 In Development  
**Current Phase**: Epic 1 - Data Foundation & Infrastructure  
**Last Updated**: December 14, 2025

