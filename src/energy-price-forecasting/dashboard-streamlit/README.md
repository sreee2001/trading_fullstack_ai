# Energy Price Forecasting - Streamlit Dashboard

A Python-only dashboard for energy commodity price forecasting, model performance analysis, and backtesting.

## Features

- **Price Forecasting**: Generate and visualize price forecasts for WTI, BRENT, and Natural Gas
- **Model Performance**: View and compare ML model performance metrics
- **Backtesting**: Run backtests on forecasting models with custom trading strategies
- **Historical Data**: Explore historical price data with interactive charts

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API settings (optional):
   - Create `.streamlit/secrets.toml` file:
   ```toml
   API_BASE_URL = "http://localhost:8000"
   API_KEY = "your_api_key_here"
   ```
   - Or set environment variables:
   ```bash
   export API_BASE_URL=http://localhost:8000
   export API_KEY=your_api_key_here
   ```

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

## Pages

### Forecast
- Generate price forecasts for energy commodities
- Visualize forecasts with confidence intervals
- Compare forecasts with historical data
- Download forecast data as CSV

### Models
- View all available ML models
- Filter models by commodity
- Compare model performance metrics
- View model metadata

### Backtest
- Run backtests on forecasting models
- Configure trading strategies and parameters
- View equity curves and trade history
- Analyze performance metrics (Sharpe ratio, max drawdown, etc.)

### Historical Data
- Explore historical price data
- Interactive price charts
- Statistical analysis
- Download historical data as CSV

## Configuration

The dashboard connects to the FastAPI backend. Configure the API URL and authentication in the sidebar or via secrets/environment variables.

## Requirements

- Python 3.10+
- FastAPI backend running (see main project README)
- API key (optional, for protected endpoints)

