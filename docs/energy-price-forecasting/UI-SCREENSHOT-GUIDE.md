# UI Screenshot Guide

**Purpose**: Guide for running the dashboards and taking screenshots for portfolio presentation

---

## Available UIs

### 1. React Dashboard (Recommended for Screenshots)

**Location**: `src/energy-price-forecasting/dashboard/`

**Pages Available**:
- **Home Page** (`/`) - Landing page with feature cards
- **Forecast Page** (`/forecast`) - Interactive forecast charts
- **Models Page** (`/models`) - Model comparison table
- **Backtest Page** (`/backtest`) - Equity curves and trade history

---

## Quick Start for Screenshots

### Option 1: React Dashboard (Best for Screenshots)

#### Step 1: Start Backend Services

```bash
cd src/energy-price-forecasting

# Start database and Redis
docker compose up -d timescaledb redis

# Start API (in separate terminal)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 2: Start React Dashboard

```bash
cd dashboard
npm install  # If not already done
npm run dev
```

**Dashboard will open at**: http://localhost:5173

#### Step 3: Take Screenshots

**Recommended Screenshots**:

1. **Home Page** (`http://localhost:5173/`)
   - Shows feature cards and overview
   - Clean landing page

2. **Forecast Page** (`http://localhost:5173/forecast`)
   - Select commodity (WTI, BRENT, NG)
   - Set horizon (7 days recommended)
   - Click "Generate Forecast"
   - Screenshot: Chart with forecast and confidence intervals

3. **Models Page** (`http://localhost:5173/models`)
   - Shows model comparison table
   - Performance metrics
   - Screenshot: Model comparison view

4. **Backtest Page** (`http://localhost:5173/backtest`)
   - Select model and date range
   - Run backtest
   - Screenshot: Equity curve and performance metrics

---

### Option 2: Streamlit Dashboard

#### Step 1: Start Backend Services

```bash
cd src/energy-price-forecasting

# Start database and Redis
docker compose up -d timescaledb redis

# Start API (in separate terminal)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 2: Start Streamlit Dashboard

```bash
cd dashboard-streamlit
pip install -r requirements.txt
streamlit run app.py
```

**Dashboard will open at**: http://localhost:8501

#### Step 3: Take Screenshots

**Recommended Screenshots**:
- Forecast page with Plotly charts
- Historical data visualization
- Model comparison metrics
- Backtest results with equity curves

---

## Screenshot Tips

### Best Practices

1. **Use Full Screen**: Maximize browser window for clean screenshots
2. **Generate Data First**: Ensure forecasts/backtests are generated before screenshot
3. **Clean State**: Use fresh browser session for clean UI
4. **Multiple Angles**: Take screenshots of different pages and features
5. **High Resolution**: Use browser zoom or high-DPI screenshots

### Recommended Screenshot Set

1. **Home Page** - Overview and navigation
2. **Forecast Page** - With forecast chart showing predictions
3. **Models Page** - Model comparison table
4. **Backtest Page** - Equity curve and metrics
5. **Historical Data** - Price history chart (if available)

---

## Mock Data Setup (If API Not Available)

If you want to take screenshots without running the full backend, you can:

1. **Use Browser DevTools**: Mock API responses
2. **Static Screenshots**: Use the built dashboard (`npm run build`)
3. **Demo Mode**: Add demo data mode to dashboard

---

## Export Functionality

The dashboards include export functionality:
- **PNG Export**: Charts can be exported as PNG
- **CSV Export**: Data tables can be exported

Use these for high-quality images!

---

## Browser Recommendations

- **Chrome/Edge**: Best for screenshots, DevTools for mocking
- **Firefox**: Good alternative
- **Screenshot Tools**: 
  - Windows: Snipping Tool, ShareX
  - Mac: Cmd+Shift+4
  - Browser extensions: Full Page Screen Capture

---

## Example Screenshot Workflow

```bash
# Terminal 1: Start services
cd src/energy-price-forecasting
docker compose up -d
uvicorn api.main:app --reload

# Terminal 2: Start React dashboard
cd dashboard
npm run dev

# Browser: Open http://localhost:5173
# 1. Navigate to Forecast page
# 2. Generate a forecast
# 3. Take screenshot
# 4. Navigate to Models page
# 5. Take screenshot
# 6. Navigate to Backtest page
# 7. Run backtest
# 8. Take screenshot
```

---

## Troubleshooting

### Dashboard Won't Load
- Check API is running: `curl http://localhost:8000/health`
- Check React dev server: `npm run dev`
- Check browser console for errors

### No Data Showing
- Ensure database has data
- Check API endpoints are working
- Verify API key if required

### Charts Not Rendering
- Check browser console for errors
- Verify Recharts/Plotly is loaded
- Check data format matches expected structure

---

**Last Updated**: December 15, 2025



