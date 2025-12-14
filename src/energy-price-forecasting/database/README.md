# Database Setup Guide

## Energy Price Forecasting System - PostgreSQL + TimescaleDB

This guide explains how to set up and use the PostgreSQL database with TimescaleDB extension for storing time-series energy price data.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start with Docker](#quick-start-with-docker)
4. [Manual PostgreSQL Installation](#manual-postgresql-installation)
5. [Database Schema](#database-schema)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The system uses:
- **PostgreSQL 15+**: Robust relational database
- **TimescaleDB**: Extension for optimized time-series queries
- **SQLAlchemy**: Python ORM for database operations
- **psycopg3**: PostgreSQL adapter (Python 3.13 compatible)

**Key Features:**
- Automatic time-series partitioning (1-day chunks)
- Optimized indexes for commodity and date queries
- Bulk insert with upsert capability
- Connection pooling for performance
- Pandas DataFrame integration

---

## Prerequisites

**Option A: Docker (Recommended)**
- Docker Desktop installed
- Docker Compose installed

**Option B: Manual Installation**
- PostgreSQL 15+ installed
- TimescaleDB extension installed
- Basic PostgreSQL knowledge

---

## Quick Start with Docker

### Step 1: Start Database Container

```bash
# Navigate to project directory
cd src/energy-price-forecasting

# Start PostgreSQL + TimescaleDB container
docker-compose up -d

# Check status
docker-compose ps
```

Expected output:
```
NAME                       COMMAND                  SERVICE        STATUS
energy_forecasting_db      docker-entrypoint.s...   timescaledb    running
```

### Step 2: Verify Database

```bash
# Connect to database
docker exec -it energy_forecasting_db psql -U energy_user -d energy_forecasting

# Inside psql, check tables
\dt

# Check TimescaleDB extension
SELECT * FROM timescaledb_information.hypertables;

# Exit psql
\q
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp env.example .env

# Edit .env and add your API keys (database config is already set for Docker)
```

Default Docker credentials:
- **Host:** localhost
- **Port:** 5432
- **Database:** energy_forecasting
- **User:** energy_user
- **Password:** energy_password

### Step 4: Test Database Connection

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Run database example
python examples/database_example.py
```

### Step 5: Stop Database (when done)

```bash
# Stop container (data persists in volume)
docker-compose stop

# Stop and remove container (data persists)
docker-compose down

# Stop and remove ALL data (caution!)
docker-compose down -v
```

---

## Manual PostgreSQL Installation

### Windows

1. Download PostgreSQL 15 from https://www.postgresql.org/download/windows/
2. Install PostgreSQL
3. Install TimescaleDB:
   ```bash
   # Download TimescaleDB installer
   # https://docs.timescale.com/self-hosted/latest/install/installation-windows/
   ```

4. Create database and user:
   ```sql
   CREATE DATABASE energy_forecasting;
   CREATE USER energy_user WITH PASSWORD 'energy_password';
   GRANT ALL PRIVILEGES ON DATABASE energy_forecasting TO energy_user;
   ```

5. Run initialization script:
   ```bash
   psql -U postgres -d energy_forecasting -f database/init.sql
   ```

### Linux

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Install TimescaleDB
sudo apt-get install timescaledb-postgresql-15

# Create database
sudo -u postgres psql
CREATE DATABASE energy_forecasting;
CREATE USER energy_user WITH PASSWORD 'energy_password';
GRANT ALL PRIVILEGES ON DATABASE energy_forecasting TO energy_user;
\q

# Run initialization script
sudo -u postgres psql -d energy_forecasting -f database/init.sql
```

---

## Database Schema

### Tables

#### 1. `commodities`
Stores commodity metadata (WTI, Brent, Natural Gas, etc.)

```sql
CREATE TABLE commodities (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    unit VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. `data_sources`
Stores data source metadata (EIA, FRED, Yahoo Finance, etc.)

```sql
CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    base_url VARCHAR(255),
    api_version VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. `price_data` (TimescaleDB Hypertable)
Main time-series table for commodity price data

```sql
CREATE TABLE price_data (
    timestamp TIMESTAMPTZ NOT NULL,
    commodity_id INTEGER NOT NULL REFERENCES commodities(id),
    source_id INTEGER NOT NULL REFERENCES data_sources(id),
    price DECIMAL(12,4) NOT NULL,
    volume BIGINT,
    open_price DECIMAL(12,4),
    high_price DECIMAL(12,4),
    low_price DECIMAL(12,4),
    close_price DECIMAL(12,4),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (timestamp, commodity_id, source_id)
);

-- Convert to hypertable
SELECT create_hypertable('price_data', 'timestamp');
```

### Indexes

- `idx_price_data_commodity`: (commodity_id, timestamp DESC)
- `idx_price_data_source`: (source_id, timestamp DESC)
- `idx_price_data_commodity_source`: (commodity_id, source_id, timestamp DESC)

### Helper Functions

- `get_latest_price(commodity_symbol, source_name)`: Get latest price
- `get_price_stats(commodity_symbol, start_date, end_date)`: Get statistics

---

## Usage Examples

### Python - Using ORM

```python
from database import get_session, Commodity, PriceData
from database.operations import insert_price_data, get_price_data

# Insert data from DataFrame
import pandas as pd
df = pd.DataFrame({
    "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
    "price": [75.50, 76.20, 74.80]
})

count = insert_price_data(df, commodity_symbol="WTI", source_name="EIA")
print(f"Inserted {count} records")

# Query data
from datetime import datetime
df = get_price_data(
    commodity_symbol="WTI",
    source_name="EIA",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 31)
)
print(df.head())

# Get latest price
from database.operations import get_latest_price
latest = get_latest_price("WTI", "EIA")
if latest:
    timestamp, price = latest
    print(f"Latest: ${price} at {timestamp}")
```

### SQL - Direct Queries

```sql
-- Get latest WTI price from EIA
SELECT * FROM get_latest_price('WTI', 'EIA');

-- Get price statistics for January 2024
SELECT * FROM get_price_stats('WTI', '2024-01-01', '2024-01-31');

-- Manual query: Last 10 WTI prices
SELECT 
    pd.timestamp,
    pd.price,
    pd.volume,
    c.symbol,
    ds.name AS source
FROM price_data pd
JOIN commodities c ON pd.commodity_id = c.id
JOIN data_sources ds ON pd.source_id = ds.id
WHERE c.symbol = 'WTI'
ORDER BY pd.timestamp DESC
LIMIT 10;

-- Get daily average price across all sources
SELECT 
    DATE(timestamp) AS date,
    AVG(price) AS avg_price,
    COUNT(*) AS source_count
FROM price_data pd
JOIN commodities c ON pd.commodity_id = c.id
WHERE c.symbol = 'WTI'
GROUP BY DATE(timestamp)
ORDER BY date DESC
LIMIT 30;
```

---

## Troubleshooting

### Issue: "Connection refused" error

**Solution:**
```bash
# Check if Docker container is running
docker-compose ps

# If not running, start it
docker-compose up -d

# Check logs
docker-compose logs timescaledb
```

### Issue: "password authentication failed"

**Solution:**
```bash
# Check .env file has correct credentials
cat .env | grep DB_

# Default Docker credentials:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_forecasting
DB_USER=energy_user
DB_PASSWORD=energy_password
```

### Issue: "TimescaleDB extension not found"

**Solution:**
```bash
# Connect to database
docker exec -it energy_forecasting_db psql -U energy_user -d energy_forecasting

# Enable extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

# Verify
SELECT extname FROM pg_extension WHERE extname = 'timescaledb';
```

### Issue: "Table already exists" during init

**Solution:**
The `init.sql` script uses `IF NOT EXISTS` clauses, so it's safe to run multiple times. If you need to reset:

```bash
# WARNING: This deletes ALL data!

# Stop container
docker-compose down

# Remove volume (deletes data)
docker volume rm energy-price-forecasting_timescale_data

# Start fresh
docker-compose up -d
```

### Issue: "Module not found: database"

**Solution:**
```bash
# Make sure you're in the project directory
cd src/energy-price-forecasting

# Reinstall in editable mode
pip install -e .

# Verify
python -c "import database; print('OK')"
```

---

## Performance Tips

1. **Use bulk insert**: `insert_price_data()` uses bulk insert for efficiency
2. **Enable upsert**: Set `upsert=True` to update existing records
3. **Query with date ranges**: Always use `start_date` and `end_date` for large datasets
4. **Use indexes**: Queries on `commodity_id` and `timestamp` are optimized
5. **Connection pooling**: Reuse `get_database_manager()` instance

---

## Next Steps

- Run `python examples/database_example.py` to test full workflow
- Integrate FRED data into database
- Integrate Yahoo Finance data into database
- Set up automated data ingestion pipeline
- Implement data validation before insertion

---

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [psycopg3 Documentation](https://www.psycopg.org/psycopg3/docs/)

