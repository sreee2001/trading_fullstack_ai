# Dashboard Features

**Time to Read**: 2 minutes

---

## Overview

The system provides two dashboard interfaces for accessing forecasts, models, and analytics:
- **React Dashboard**: Modern web interface (TypeScript)
- **Streamlit Dashboard**: Python-based interface

---

## React Dashboard

### Access

URL: http://localhost:3000 (after starting with Docker)

### Features

#### Forecast Page
- Generate price forecasts
- Interactive charts with confidence intervals
- Historical comparison
- CSV export

#### Models Page
- View all available models
- Compare model performance
- Filter by commodity
- View model metadata

#### Backtest Page
- Run backtests
- Configure trading strategies
- View equity curves
- Analyze trade history

#### Historical Data Page
- Explore historical prices
- Interactive price charts
- Statistical analysis
- Data export

### Key Features

- ✅ **Responsive Design**: Works on desktop and mobile
- ✅ **Real-Time Updates**: WebSocket support
- ✅ **Interactive Charts**: Zoom, pan, hover details
- ✅ **Export Functionality**: CSV and PNG export
- ✅ **Dark Mode**: Theme switching

---

## Streamlit Dashboard

### Access

```bash
cd dashboard-streamlit
streamlit run app.py
```

URL: http://localhost:8501

### Features

#### Forecast Page
- Generate forecasts
- Plotly interactive charts
- Forecast vs historical comparison
- CSV download

#### Models Page
- View model list
- Filter by commodity
- Model comparison metrics

#### Backtest Page
- Run backtests
- Configure all parameters
- View equity curves
- Trade history analysis

#### Historical Data Page
- Load historical data
- Price charts
- Statistics display
- Data export

### Key Features

- ✅ **Python-Only**: No JavaScript required
- ✅ **Rapid Prototyping**: Quick dashboard creation
- ✅ **Easy Configuration**: Sidebar settings
- ✅ **Interactive Charts**: Plotly visualizations

---

## Choosing a Dashboard

### Use React Dashboard If:
- You prefer modern web interfaces
- You need real-time WebSocket updates
- You want mobile-responsive design
- You're building production applications

### Use Streamlit Dashboard If:
- You prefer Python-only solutions
- You need rapid prototyping
- You're doing data exploration
- You want simpler deployment

---

## Common Tasks

### Generate Forecast

**React**:
1. Navigate to Forecast page
2. Select commodity, horizon, date
3. Click "Generate Forecast"

**Streamlit**:
1. Select Forecast page
2. Configure parameters in sidebar
3. Click "Generate Forecast"

### Run Backtest

**React**:
1. Navigate to Backtest page
2. Select model and date range
3. Configure strategy parameters
4. Click "Run Backtest"

**Streamlit**:
1. Select Backtest page
2. Configure all parameters
3. Click "Run Backtest"

### View Models

**React**:
1. Navigate to Models page
2. Click "Refresh Models"
3. Filter by commodity if needed

**Streamlit**:
1. Select Models page
2. Choose commodity filter
3. Click "Refresh Models"

---

## Tips & Tricks

### React Dashboard
- Use keyboard shortcuts for faster navigation
- Export charts as PNG for reports
- Use filters to focus on specific data
- Enable dark mode for better viewing

### Streamlit Dashboard
- Configure API settings in sidebar
- Use date pickers for easy date selection
- Download data for offline analysis
- Customize charts with Plotly

---

## Troubleshooting

### Dashboard Won't Load
- Check Docker containers are running
- Verify ports are not in use
- Clear browser cache

### Charts Not Displaying
- Check browser console for errors
- Verify API is responding
- Ensure data is available

### Slow Performance
- Reduce date range
- Use filters to limit data
- Check API response times

---

## Next Steps

- **API Integration**: See [API Usage Guide](../guides/api-usage.md)
- **Advanced Features**: Explore [Analytics Features](analytics.md)
- **Customization**: See [Developer Documentation](../../developers/index.md)

---

**Last Updated**: December 15, 2025

