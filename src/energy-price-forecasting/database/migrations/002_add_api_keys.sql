-- Migration: Add API Keys Table
-- Created: 2025-12-15
-- Purpose: Add API key authentication support

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

