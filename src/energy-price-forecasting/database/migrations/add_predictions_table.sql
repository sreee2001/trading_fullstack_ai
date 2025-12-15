-- Migration: Add predictions table for performance monitoring
-- Date: 2025-12-15
-- Description: Table to store predictions and actual values for model monitoring

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(100) NOT NULL,
    commodity VARCHAR(10) NOT NULL,
    horizon INTEGER NOT NULL,
    prediction FLOAT NOT NULL,
    actual FLOAT,
    error FLOAT,
    model_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for efficient queries
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp);
CREATE INDEX IF NOT EXISTS idx_predictions_model_version ON predictions(model_version);
CREATE INDEX IF NOT EXISTS idx_predictions_commodity ON predictions(commodity);
CREATE INDEX IF NOT EXISTS idx_predictions_model_commodity ON predictions(model_version, commodity);
CREATE INDEX IF NOT EXISTS idx_predictions_actual ON predictions(actual) WHERE actual IS NOT NULL;

-- Create hypertable for TimescaleDB (if using TimescaleDB)
-- SELECT create_hypertable('predictions', 'timestamp', if_not_exists => TRUE);

COMMENT ON TABLE predictions IS 'Stores model predictions and actual values for performance monitoring';
COMMENT ON COLUMN predictions.id IS 'Unique identifier for prediction record';
COMMENT ON COLUMN predictions.timestamp IS 'When the prediction was made';
COMMENT ON COLUMN predictions.model_version IS 'Model identifier/version';
COMMENT ON COLUMN predictions.commodity IS 'Commodity symbol (WTI, BRENT, NG)';
COMMENT ON COLUMN predictions.horizon IS 'Forecast horizon in days';
COMMENT ON COLUMN predictions.prediction IS 'Predicted price value';
COMMENT ON COLUMN predictions.actual IS 'Actual price value (updated later)';
COMMENT ON COLUMN predictions.error IS 'Absolute error (|prediction - actual|)';
COMMENT ON COLUMN predictions.model_type IS 'Type of model (lstm, arima, prophet)';

