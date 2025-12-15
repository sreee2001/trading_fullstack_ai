# Data Ingestion Module

**Purpose**: Fetch energy commodity price data from multiple authoritative sources (EIA, FRED, Yahoo Finance)

---

## Overview

The data ingestion module provides clients for three major data sources:
- **EIA (Energy Information Administration)**: Official U.S. energy data
- **FRED (Federal Reserve Economic Data)**: Economic data including energy prices
- **Yahoo Finance**: Market data for futures and spot prices

---

## File Structure

```
data_ingestion/
├── __init__.py              # Module exports
├── eia_client.py            # EIA API client (500+ lines)
├── fred_client.py           # FRED API client (400+ lines)
└── yahoo_finance_client.py  # Yahoo Finance client (350+ lines)
```

---

## Key Classes

### EIAAPIClient

**File**: `eia_client.py`  
**Purpose**: Fetch data from EIA API

**Key Methods**:
- `fetch_wti_prices(start_date, end_date)`: Fetch WTI crude oil prices
- `fetch_brent_prices(start_date, end_date)`: Fetch Brent crude oil prices
- `fetch_natural_gas_prices(start_date, end_date)`: Fetch natural gas prices
- `_make_request(endpoint, params)`: Internal request method with retry logic

**Usage**:
```python
from data_ingestion.eia_client import EIAAPIClient

client = EIAAPIClient(api_key="your_key")
data = client.fetch_wti_prices("2024-01-01", "2024-12-31")
```

**Features**:
- Automatic retry with exponential backoff
- Rate limiting (5000 requests/day)
- Error handling and logging
- Data normalization

---

### FREDAPIClient

**File**: `fred_client.py`  
**Purpose**: Fetch data from FRED API

**Key Methods**:
- `fetch_series(series_id, start_date, end_date)`: Fetch any FRED series
- `fetch_wti_prices(start_date, end_date)`: Fetch WTI prices
- `fetch_brent_prices(start_date, end_date)`: Fetch Brent prices
- `fetch_natural_gas_prices(start_date, end_date)`: Fetch natural gas prices

**Usage**:
```python
from data_ingestion.fred_client import FREDAPIClient

client = FREDAPIClient(api_key="your_key")
data = client.fetch_wti_prices("2024-01-01", "2024-12-31")
```

**Features**:
- Caching support (Redis)
- Rate limiting
- Data validation
- Multiple series support

---

### YahooFinanceClient

**File**: `yahoo_finance_client.py`  
**Purpose**: Fetch market data from Yahoo Finance

**Key Methods**:
- `fetch_ohlcv(symbol, start_date, end_date)`: Fetch OHLCV data
- `fetch_wti_futures(start_date, end_date)`: Fetch WTI futures
- `fetch_brent_futures(start_date, end_date)`: Fetch Brent futures
- `fetch_natural_gas_futures(start_date, end_date)`: Fetch NG futures

**Usage**:
```python
from data_ingestion.yahoo_finance_client import YahooFinanceClient

client = YahooFinanceClient()
data = client.fetch_wti_futures("2024-01-01", "2024-12-31")
```

**Features**:
- yfinance library integration
- Multiple data types (OHLCV, volume)
- Automatic symbol resolution
- Error handling

---

## Data Format

All clients return data in standardized format:

```python
{
    "commodity": "WTI",
    "data": [
        {
            "date": "2024-01-01",
            "price": 72.50,
            "source": "EIA"
        }
    ],
    "metadata": {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "total_records": 365
    }
}
```

---

## Error Handling

All clients implement:
- **Retry Logic**: Exponential backoff for transient errors
- **Rate Limiting**: Respect API rate limits
- **Validation**: Data format validation
- **Logging**: Comprehensive error logging

---

## Testing

**Test Files**:
- `tests/test_eia_client.py` (23 tests)
- `tests/test_fred_client.py` (20 tests)
- `tests/test_yahoo_finance_client.py` (15 tests)

**Run Tests**:
```bash
pytest tests/test_eia_client.py -v
pytest tests/test_fred_client.py -v
pytest tests/test_yahoo_finance_client.py -v
```

---

## Dependencies

- `requests`: HTTP requests
- `pandas`: Data manipulation
- `tenacity`: Retry logic
- `yfinance`: Yahoo Finance data (for YahooFinanceClient)

---

## Configuration

API keys should be set in environment variables:
- `EIA_API_KEY`: EIA API key
- `FRED_API_KEY`: FRED API key

Or passed to client constructors.

---

## Integration

Clients are used by:
- **Data Pipeline**: `data_pipeline/__init__.py` - Orchestrates data fetching
- **Database Operations**: `database/operations.py` - Stores fetched data
- **Validation**: `data_validation/validator.py` - Validates fetched data

---

## Extending

To add a new data source:

1. Create new client class in `data_ingestion/`
2. Implement standard interface:
   - `fetch_wti_prices(start_date, end_date)`
   - `fetch_brent_prices(start_date, end_date)`
   - `fetch_natural_gas_prices(start_date, end_date)`
3. Return standardized data format
4. Add to pipeline orchestrator
5. Add tests

---

**Last Updated**: December 15, 2025

