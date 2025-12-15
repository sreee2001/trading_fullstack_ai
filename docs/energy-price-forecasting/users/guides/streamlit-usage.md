# Streamlit Dashboard Usage Guide

**Time to Read**: 2 minutes

---

## Overview

The Streamlit dashboard provides a Python-based interface for the Energy Price Forecasting System. Perfect for Python users who prefer a simpler, code-focused interface.

---

## Starting the Dashboard

```bash
cd src/energy-price-forecasting/dashboard-streamlit
pip install -r requirements.txt
streamlit run app.py
```

Dashboard opens at: http://localhost:8501

---

## Configuration

### API Settings

Configure in the sidebar:
- **API Base URL**: http://localhost:8000 (default)
- **API Key**: Your API key (optional)

Or set in `.streamlit/secrets.toml`:
```toml
API_BASE_URL = "http://localhost:8000"
API_KEY = "your_api_key_here"
```

---

## Using the Dashboard

### Forecast Page

1. Select **Forecast** from sidebar
2. Choose **Commodity** (WTI, BRENT, NG)
3. Set **Forecast Horizon** (1-30 days)
4. Choose **Start Date**
5. Click **Generate Forecast**
6. View:
   - Forecast metrics
   - Interactive chart
   - Prediction table
   - Download CSV button

### Models Page

1. Select **Models** from sidebar
2. Optionally filter by **Commodity**
3. Click **Refresh Models**
4. View:
   - Model list
   - Model comparison metrics

### Backtest Page

1. Select **Backtest** from sidebar
2. Configure all parameters:
   - Model selection
   - Date range
   - Capital settings
   - Strategy parameters
3. Click **Run Backtest**
4. View:
   - Performance metrics
   - Equity curve
   - Trade history

### Historical Data Page

1. Select **Historical Data** from sidebar
2. Choose **Commodity** and **Date Range**
3. Click **Load Historical Data**
4. View:
   - Price chart
   - Statistics
   - Data table
   - Download CSV button

---

## Features

### Interactive Charts

- **Plotly Charts**: Fully interactive
- **Zoom & Pan**: Click and drag
- **Hover Details**: Hover for values
- **Export**: Download as PNG

### Data Export

- **CSV Download**: All data tables
- **Timestamped Files**: Automatic naming
- **Complete Data**: All columns included

### Configuration

- **Sidebar Settings**: Easy API configuration
- **Session Persistence**: Settings saved during session
- **Environment Variables**: Support for secrets

---

## Advantages

- ✅ **Python-Only**: No JavaScript knowledge needed
- ✅ **Rapid Prototyping**: Quick dashboard creation
- ✅ **Easy Customization**: Modify Python code directly
- ✅ **Simple Deployment**: Single Python app

---

## Tips

1. **Configure API First**: Set API URL and key in sidebar
2. **Use Date Pickers**: Easy date selection
3. **Download Data**: Export for offline analysis
4. **Customize Code**: Modify `app.py` for custom features

---

## Troubleshooting

### Dashboard Won't Start
```bash
# Check dependencies
pip install -r requirements.txt

# Check Python version (3.10+)
python --version
```

### API Connection Errors
- Verify API is running
- Check API URL in sidebar
- Verify API key if required

### Charts Not Displaying
- Check browser console
- Verify Plotly is installed
- Check data is available

---

## Next Steps

- **React Dashboard**: See [Dashboard Usage Guide](dashboard-usage.md)
- **API Usage**: See [API Usage Guide](api-usage.md)
- **Troubleshooting**: See [Troubleshooting Guide](troubleshooting.md)

---

**Last Updated**: December 15, 2025

