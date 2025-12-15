# Streamlit Dashboard Module

**Purpose**: Python-based alternative dashboard using Streamlit

---

## Overview

The Streamlit dashboard provides a Python-only alternative to the React dashboard. It's ideal for rapid prototyping, data exploration, and Python-focused workflows.

---

## File Structure

```
dashboard-streamlit/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
└── README.md             # Usage guide
```

---

## Main Application

### app.py

**Purpose**: Streamlit application entry point

**Key Sections**:
- **Configuration**: API settings, environment variables
- **API Client**: Helper functions for API calls
- **Pages**: Forecast, Historical Data, Models, Backtest

**Usage**:
```bash
cd dashboard-streamlit
streamlit run app.py
```

---

## Pages

### Forecast Page

**Features**:
- Commodity selection
- Horizon slider (1-30 days)
- Date picker
- Forecast generation
- Interactive Plotly charts
- Confidence intervals
- Historical comparison
- CSV download

---

### Historical Data Page

**Features**:
- Commodity selection
- Date range selection
- Historical price charts
- Statistics display
- Data table
- CSV export

---

### Models Page

**Features**:
- Model list display
- Filter by commodity
- Performance metrics
- Model comparison charts
- Average metrics

---

### Backtest Page

**Features**:
- Model selection
- Date range configuration
- Capital settings
- Strategy parameters
- Backtest execution
- Performance metrics
- Equity curve visualization
- Trade history table

---

## API Integration

### API Client Function

**Location**: `app.py` - `call_api()` function

**Purpose**: Unified API client with error handling

**Features**:
- HTTP error handling
- Connection error handling
- Request/response logging
- Error display in UI

**Usage**:
```python
def call_api(endpoint, method="GET", params=None, json_data=None):
    headers = {"X-API-Key": API_KEY}
    url = f"{API_BASE_URL}/{endpoint}"
    # ... implementation
```

---

## Configuration

### Environment Variables

- `API_BASE_URL`: FastAPI backend URL (default: http://localhost:8000/api/v1)
- `STREAMLIT_API_KEY`: API key for authentication

**Set in**:
- Environment variables
- `.streamlit/secrets.toml`
- Hardcoded in `app.py` (not recommended)

---

## Visualization

**Library**: Plotly

**Chart Types**:
- Line charts (forecasts, historical)
- Scatter plots (with confidence intervals)
- Bar charts (metrics)
- Area charts (equity curves)

**Features**:
- Interactive zoom/pan
- Hover tooltips
- Export as PNG
- Responsive layout

---

## Dependencies

**requirements.txt**:
```
streamlit
requests
pandas
numpy
plotly
```

---

## Development

### Setup

```bash
cd dashboard-streamlit
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

### Configuration

Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
```

---

## Advantages

- ✅ **Python-Only**: No JavaScript knowledge needed
- ✅ **Rapid Prototyping**: Quick dashboard creation
- ✅ **Easy Customization**: Modify Python code directly
- ✅ **Simple Deployment**: Single Python app
- ✅ **Interactive**: Built-in interactivity

---

## Limitations

- ⚠️ **Performance**: Slower than React for large datasets
- ⚠️ **Customization**: Less flexible than React
- ⚠️ **Real-Time**: No WebSocket support (use polling)

---

## Integration

The Streamlit dashboard integrates with:
- **FastAPI Backend**: REST API endpoints
- **MLflow**: Model metadata (via API)
- **Database**: Historical data (via API)

---

## Best Practices

1. **Error Handling**: Use `call_api()` for consistent error handling
2. **Session State**: Use `st.session_state` for state management
3. **Caching**: Use `@st.cache_data` for expensive operations
4. **Layout**: Use columns for better organization
5. **User Experience**: Show loading spinners for long operations

---

## Extending

To add new features:

1. Add new page in sidebar navigation
2. Create page function
3. Add API calls using `call_api()`
4. Add visualizations with Plotly
5. Update documentation

---

## Comparison with React Dashboard

| Feature | Streamlit | React |
|---------|-----------|-------|
| Language | Python | TypeScript |
| Setup | Simple | More complex |
| Customization | Limited | Full control |
| Performance | Good | Excellent |
| Real-Time | Polling | WebSocket |
| Deployment | Simple | More complex |

---

**Last Updated**: December 15, 2025

