# Database Module

**Purpose**: PostgreSQL + TimescaleDB database layer for time-series energy price data storage

---

## Overview

The database module provides a robust data storage layer optimized for time-series data using PostgreSQL with TimescaleDB extension. It includes ORM models, database operations, connection management, and utilities.

---

## File Structure

```
database/
├── __init__.py              # Module exports
├── models.py                # SQLAlchemy ORM models (230 lines)
├── operations.py            # CRUD operations (520 lines)
├── utils.py                 # Connection management (386 lines)
├── init.sql                 # Schema initialization
└── migrations/              # Database migrations
    └── 001_increase_symbol_length.sql
```

---

## Key Classes

### Database Models (`models.py`)

**Commodity Model**:
- Represents energy commodities (WTI, BRENT, NG)
- Fields: `id`, `symbol`, `name`, `description`

**DataSource Model**:
- Represents data sources (EIA, FRED, Yahoo Finance)
- Fields: `id`, `name`, `description`, `api_endpoint`

**PriceData Model**:
- Main time-series data table
- Fields: `id`, `commodity_id`, `source_id`, `date`, `price`, `volume`
- TimescaleDB hypertable for partitioning

**APIKey Model**:
- API key management
- Fields: `id`, `key_hash`, `name`, `created_at`, `is_active`

---

### Database Operations (`operations.py`)

**Key Functions**:

- `get_or_create_commodity(symbol, name)`: Get or create commodity
- `get_or_create_data_source(name, description)`: Get or create data source
- `insert_price_data(commodity, source, date, price, volume)`: Insert single record
- `insert_price_data_bulk(dataframe)`: Bulk insert with upsert
- `get_price_data(commodity, start_date, end_date)`: Retrieve price data
- `get_latest_price_date(commodity)`: Get most recent date
- `get_latest_price(commodity)`: Get most recent price
- `get_price_statistics(commodity, start_date, end_date)`: Calculate statistics
- `delete_price_data(commodity, start_date, end_date)`: Delete data

**Usage**:
```python
from database.operations import get_price_data, insert_price_data_bulk
from database.utils import get_database_manager

# Get price data
data = get_price_data(
    commodity="WTI",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Bulk insert
import pandas as pd
df = pd.DataFrame({
    'date': ['2024-01-01', '2024-01-02'],
    'price': [72.50, 73.00],
    'commodity': ['WTI', 'WTI']
})
insert_price_data_bulk(df)
```

---

### Database Manager (`utils.py`)

**DatabaseManager Class**:
- Manages database connections
- Connection pooling
- Health checks
- Session management

**Key Methods**:
- `connect()`: Establish connection
- `disconnect()`: Close connection
- `get_session()`: Get database session
- `check_health()`: Check database health

**Usage**:
```python
from database.utils import get_database_manager, get_session

# Get database manager
db_manager = get_database_manager()

# Use session context manager
with get_session() as session:
    # Use session for queries
    result = session.query(PriceData).filter_by(commodity_id=1).all()
```

---

## Database Schema

### TimescaleDB Hypertable

The `price_data` table is converted to a TimescaleDB hypertable for optimized time-series queries:

```sql
SELECT create_hypertable('price_data', 'date', chunk_time_interval => INTERVAL '1 day');
```

**Benefits**:
- Automatic partitioning by time
- Optimized queries for time ranges
- Efficient data retention policies

---

## Features

### Bulk Operations

- **Bulk Insert**: Efficient batch inserts with upsert
- **Pandas Integration**: Direct DataFrame to database
- **Transaction Management**: Automatic rollback on errors

### Query Optimization

- **Indexes**: Optimized indexes on `commodity_id`, `date`, `source_id`
- **TimescaleDB**: Automatic time-based partitioning
- **Connection Pooling**: Reuse connections for performance

### Data Integrity

- **Foreign Keys**: Enforce referential integrity
- **Constraints**: Unique constraints on commodity/date combinations
- **Validation**: Data validation before insertion

---

## Testing

**Test Files**:
- `tests/test_database_models.py` (8 tests)
- `tests/test_database_operations.py` (7 tests)

**Run Tests**:
```bash
pytest tests/test_database_models.py -v
pytest tests/test_database_operations.py -v
```

---

## Dependencies

- `sqlalchemy`: ORM framework
- `psycopg3`: PostgreSQL adapter
- `pandas`: Data manipulation
- `timescaledb`: TimescaleDB extension (PostgreSQL)

---

## Configuration

**Environment Variables**:
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name (default: energy_forecasting)
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password

**Connection String**:
```
postgresql://user:password@host:port/database
```

---

## Migrations

Database migrations are stored in `migrations/`:
- `001_increase_symbol_length.sql`: Increase symbol field length

**Apply Migrations**:
```bash
psql -U user -d energy_forecasting -f migrations/001_increase_symbol_length.sql
```

---

## Integration

The database module is used by:
- **Data Pipeline**: Stores ingested data
- **API**: Retrieves data for forecasts
- **Training**: Provides training data
- **Backtesting**: Provides historical data

---

## Performance Considerations

### TimescaleDB Optimization

- **Chunking**: 1-day chunks for optimal query performance
- **Compression**: Enable compression for old data
- **Retention**: Automatic data retention policies

### Query Optimization

- Use date range filters for time-series queries
- Leverage TimescaleDB continuous aggregates
- Use indexes for commodity filtering

---

## Extending

To add new tables:

1. Create model in `models.py`
2. Add migration in `migrations/`
3. Add operations in `operations.py`
4. Add tests
5. Update documentation

---

**Last Updated**: December 15, 2025

