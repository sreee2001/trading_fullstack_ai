# Dashboard Usage Guide

**Time to Read**: 2 minutes

---

## Overview

The React dashboard provides an intuitive web interface for generating forecasts, running backtests, and analyzing models. This guide covers common tasks and features.

---

## Accessing the Dashboard

**URL**: http://localhost:3000

After starting the system with Docker Compose, the dashboard is automatically available.

---

## Navigation

### Main Pages

- **Home**: Overview and navigation
- **Forecast**: Generate price forecasts
- **Models**: View and compare models
- **Backtest**: Run backtests
- **Historical**: Explore historical data

---

## Common Tasks

### Generate a Forecast

1. Click **Forecast** in navigation
2. Select **Commodity** (WTI, BRENT, NG)
3. Adjust **Horizon** slider (1-30 days)
4. Choose **Start Date**
5. Click **Generate Forecast**
6. View:
   - Forecast chart with confidence intervals
   - Prediction table
   - Metrics (average price, range)

### Run a Backtest

1. Click **Backtest** in navigation
2. Select **Model** from dropdown
3. Set **Date Range** (start and end)
4. Configure **Capital**:
   - Initial Capital
   - Commission
   - Slippage
5. Select **Strategy** and set parameters
6. Click **Run Backtest**
7. View:
   - Performance metrics
   - Equity curve
   - Trade history

### View Models

1. Click **Models** in navigation
2. Optionally filter by **Commodity**
3. Click **Refresh Models**
4. View:
   - Model list with metadata
   - Performance metrics
   - Model comparison

### Explore Historical Data

1. Click **Historical** in navigation
2. Select **Commodity**
3. Set **Date Range**
4. Click **Load Historical Data**
5. View:
   - Price chart
   - Statistics
   - Data table

---

## Features

### Interactive Charts

- **Zoom**: Click and drag to zoom
- **Pan**: Click and drag to pan
- **Hover**: Hover for detailed values
- **Export**: Right-click to save as PNG

### Export Functionality

- **CSV Export**: Download data as CSV
- **PNG Export**: Save charts as images
- **Timestamped Files**: Automatic file naming

### Responsive Design

- **Desktop**: Full-featured interface
- **Tablet**: Optimized layout
- **Mobile**: Mobile-friendly navigation

---

## Tips

1. **Use Filters**: Narrow down data for faster loading
2. **Compare Models**: Use Models page to compare performance
3. **Export Data**: Download results for offline analysis
4. **Check Dates**: Ensure date ranges are valid
5. **Refresh**: Click refresh buttons to get latest data

---

## Troubleshooting

### Charts Not Loading
- Check API is running
- Verify data is available
- Clear browser cache

### Slow Performance
- Reduce date range
- Use filters
- Check network connection

### Errors
- Check browser console
- Verify API health
- Check API logs

---

## Next Steps

- **API Usage**: See [API Usage Guide](api-usage.md)
- **Streamlit Dashboard**: See [Streamlit Usage Guide](streamlit-usage.md)
- **Troubleshooting**: See [Troubleshooting Guide](troubleshooting.md)

---

**Last Updated**: December 15, 2025

