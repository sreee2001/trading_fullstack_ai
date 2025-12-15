# API Key Schema Documentation

**Created**: December 15, 2025  
**Version**: 1.0

## Overview

The `api_keys` table stores API keys for authentication. **Important**: Only hashed keys are stored - plain text keys are never persisted in the database.

## Table Schema

### Table: `api_keys`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Unique identifier |
| `key_hash` | VARCHAR(255) | UNIQUE, NOT NULL, INDEXED | Bcrypt hash of the API key |
| `user_id` | VARCHAR(100) | NULLABLE, INDEXED | User identifier (optional) |
| `name` | VARCHAR(100) | NULLABLE | Optional name/description |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `expires_at` | TIMESTAMPTZ | NULLABLE | Expiration timestamp (optional) |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE, INDEXED | Whether key is active |
| `last_used_at` | TIMESTAMPTZ | NULLABLE | Last usage timestamp |

## Indexes

- `idx_api_keys_user_id`: Index on `user_id` for user-based queries
- `idx_api_keys_is_active`: Index on `is_active` for filtering active keys
- `idx_api_keys_expires_at`: Partial index on `expires_at` (only non-null values)

## Security Considerations

1. **Never store plain text keys**: Only bcrypt hashes are stored
2. **Key format**: `epf_` prefix + random string (e.g., `epf_a1b2c3d4e5f6...`)
3. **Key generation**: Use `secrets` module for cryptographically secure random generation
4. **Key hashing**: Use bcrypt with appropriate cost factor (default: 12 rounds)
5. **Key expiration**: Optional expiration can be set via `expires_at`
6. **Key revocation**: Set `is_active=False` to revoke without deletion

## Usage Example

```python
from database.models import APIKey
from database.utils import get_session

# Create new API key (hash is stored, plain key returned once)
with get_session() as session:
    api_key = APIKey(
        key_hash=hashed_key,
        user_id="user123",
        name="Production Key",
        expires_at=None,  # No expiration
        is_active=True
    )
    session.add(api_key)
    session.commit()
```

## Migration

To apply this schema:

```bash
psql -d energy_forecasting -f database/migrations/002_add_api_keys.sql
```

Or use Alembic (if configured):

```bash
alembic upgrade head
```

