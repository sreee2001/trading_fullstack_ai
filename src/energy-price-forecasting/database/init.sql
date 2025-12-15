-- PostgreSQL + TimescaleDB Database Schema
-- Energy Price Forecasting System
-- Created: 2025-12-14

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================================
-- Table: commodities
-- Purpose: Stores commodity metadata (WTI, Brent, Natural Gas, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS commodities (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    unit VARCHAR(20),  -- e.g., "USD/barrel", "USD/MMBtu"
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE commodities IS 'Commodity definitions and metadata';
COMMENT ON COLUMN commodities.symbol IS 'Short symbol (e.g., WTI, BRENT, NATGAS)';
COMMENT ON COLUMN commodities.unit IS 'Price unit (e.g., USD/barrel, USD/MMBtu)';

-- ============================================================================
-- Table: data_sources
-- Purpose: Stores data source metadata (EIA, FRED, Yahoo Finance, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    base_url VARCHAR(255),
    api_version VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_sources IS 'External data source definitions';
COMMENT ON COLUMN data_sources.name IS 'Source identifier (e.g., EIA, FRED, YAHOO)';

-- ============================================================================
-- Table: price_data
-- Purpose: Main time-series table for commodity price data
-- ============================================================================
CREATE TABLE IF NOT EXISTS price_data (
    timestamp TIMESTAMPTZ NOT NULL,
    commodity_id INTEGER NOT NULL REFERENCES commodities(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
    price DECIMAL(12,4) NOT NULL,
    volume BIGINT,
    open_price DECIMAL(12,4),
    high_price DECIMAL(12,4),
    low_price DECIMAL(12,4),
    close_price DECIMAL(12,4),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (timestamp, commodity_id, source_id)
);

COMMENT ON TABLE price_data IS 'Time-series commodity price data';
COMMENT ON COLUMN price_data.price IS 'Spot or closing price';
COMMENT ON COLUMN price_data.volume IS 'Trading volume (if available)';
COMMENT ON COLUMN price_data.open_price IS 'Opening price (for OHLCV data)';
COMMENT ON COLUMN price_data.high_price IS 'Daily high price';
COMMENT ON COLUMN price_data.low_price IS 'Daily low price';
COMMENT ON COLUMN price_data.close_price IS 'Closing price (for OHLCV data)';

-- ============================================================================
-- Convert price_data to TimescaleDB Hypertable
-- Purpose: Optimize time-series queries and enable automatic partitioning
-- ============================================================================
SELECT create_hypertable(
    'price_data',
    'timestamp',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 day'
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_price_data_commodity 
    ON price_data (commodity_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_price_data_source 
    ON price_data (source_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_price_data_commodity_source 
    ON price_data (commodity_id, source_id, timestamp DESC);

-- ============================================================================
-- Compression Policy (Optional, for production)
-- Purpose: Automatically compress older data to save space
-- ============================================================================
-- Compress data older than 7 days
-- SELECT add_compression_policy('price_data', INTERVAL '7 days');

-- ============================================================================
-- Retention Policy (Optional, for production)
-- Purpose: Automatically drop old data
-- ============================================================================
-- Drop data older than 5 years
-- SELECT add_retention_policy('price_data', INTERVAL '5 years');

-- ============================================================================
-- Initial Data: Commodities
-- ============================================================================
INSERT INTO commodities (symbol, name, description, unit) VALUES
    ('WTI', 'West Texas Intermediate Crude Oil', 'Light sweet crude oil benchmark', 'USD/barrel'),
    ('BRENT', 'Brent Crude Oil', 'International crude oil benchmark', 'USD/barrel'),
    ('NATGAS', 'Natural Gas (Henry Hub)', 'Natural gas spot price at Henry Hub', 'USD/MMBtu')
ON CONFLICT (symbol) DO NOTHING;

-- ============================================================================
-- Initial Data: Data Sources
-- ============================================================================
INSERT INTO data_sources (name, description, base_url, api_version) VALUES
    ('EIA', 'U.S. Energy Information Administration', 'https://api.eia.gov', 'v2'),
    ('FRED', 'Federal Reserve Economic Data', 'https://api.stlouisfed.org/fred', 'v1'),
    ('YAHOO', 'Yahoo Finance', 'https://finance.yahoo.com', 'N/A')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- Table: api_keys
-- Purpose: Stores API keys for authentication
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    last_used_at TIMESTAMPTZ
);

COMMENT ON TABLE api_keys IS 'API keys for authentication (hashed only)';
COMMENT ON COLUMN api_keys.key_hash IS 'Bcrypt hash of the API key (never store plain text)';
COMMENT ON COLUMN api_keys.user_id IS 'User identifier (optional, for future user management)';
COMMENT ON COLUMN api_keys.name IS 'Optional name/description for the key';
COMMENT ON COLUMN api_keys.expires_at IS 'Optional expiration timestamp';
COMMENT ON COLUMN api_keys.is_active IS 'Whether the key is active (can be revoked)';
COMMENT ON COLUMN api_keys.last_used_at IS 'Timestamp when key was last used';

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys (user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_is_active ON api_keys (is_active);
CREATE INDEX IF NOT EXISTS idx_api_keys_expires_at ON api_keys (expires_at) WHERE expires_at IS NOT NULL;

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function: Get latest price for a commodity
CREATE OR REPLACE FUNCTION get_latest_price(
    p_commodity_symbol VARCHAR(10),
    p_source_name VARCHAR(50)
)
RETURNS TABLE (
    timestamp TIMESTAMPTZ,
    price DECIMAL(12,4),
    volume BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT pd.timestamp, pd.price, pd.volume
    FROM price_data pd
    JOIN commodities c ON pd.commodity_id = c.id
    JOIN data_sources ds ON pd.source_id = ds.id
    WHERE c.symbol = p_commodity_symbol
      AND ds.name = p_source_name
    ORDER BY pd.timestamp DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function: Get price statistics for a date range
CREATE OR REPLACE FUNCTION get_price_stats(
    p_commodity_symbol VARCHAR(10),
    p_start_date TIMESTAMPTZ,
    p_end_date TIMESTAMPTZ
)
RETURNS TABLE (
    avg_price DECIMAL(12,4),
    min_price DECIMAL(12,4),
    max_price DECIMAL(12,4),
    total_volume BIGINT,
    record_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        AVG(pd.price)::DECIMAL(12,4) as avg_price,
        MIN(pd.price) as min_price,
        MAX(pd.price) as max_price,
        SUM(pd.volume) as total_volume,
        COUNT(*)::BIGINT as record_count
    FROM price_data pd
    JOIN commodities c ON pd.commodity_id = c.id
    WHERE c.symbol = p_commodity_symbol
      AND pd.timestamp BETWEEN p_start_date AND p_end_date;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Grants (for energy_user)
-- ============================================================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO energy_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO energy_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO energy_user;

-- ============================================================================
-- Verification Queries (for manual testing)
-- ============================================================================

-- Verify TimescaleDB hypertable
-- SELECT * FROM timescaledb_information.hypertables WHERE hypertable_name = 'price_data';

-- Check data counts
-- SELECT 
--     c.symbol, 
--     ds.name, 
--     COUNT(*) as record_count,
--     MIN(pd.timestamp) as earliest_date,
--     MAX(pd.timestamp) as latest_date
-- FROM price_data pd
-- JOIN commodities c ON pd.commodity_id = c.id
-- JOIN data_sources ds ON pd.source_id = ds.id
-- GROUP BY c.symbol, ds.name;



