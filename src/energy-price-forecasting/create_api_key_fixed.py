#!/usr/bin/env python3
"""
Script to create an API key for the dashboard.
This version ensures the table exists first.
"""

import secrets
import hashlib
from database.utils import get_session
from sqlalchemy import text

def generate_api_key(prefix: str = "epf_") -> str:
    """Generate a cryptographically secure API key."""
    random_bytes = secrets.token_bytes(32)
    random_hex = random_bytes.hex()
    return f"{prefix}{random_hex}"

def hash_api_key(api_key: str) -> str:
    """Hash an API key using SHA-256."""
    return hashlib.sha256(api_key.encode()).hexdigest()

def ensure_table_exists():
    """Ensure api_keys table exists."""
    with get_session() as session:
        # Check if table exists
        result = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_keys'
            );
        """))
        
        if not result.scalar():
            print("Creating api_keys table...")
            session.execute(text("""
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
            """))
            
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys (user_id);
                CREATE INDEX IF NOT EXISTS idx_api_keys_is_active ON api_keys (is_active);
            """))
            
            session.commit()
            print("Table created successfully!")
        else:
            print("Table already exists.")

def create_api_key_direct():
    """Create API key by inserting directly into database."""
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    
    with get_session() as session:
        result = session.execute(
            text("""
                INSERT INTO api_keys (key_hash, user_id, name, is_active)
                VALUES (:key_hash, :user_id, :name, :is_active)
                RETURNING id, created_at
            """),
            {
                "key_hash": key_hash,
                "user_id": "dashboard_user",
                "name": "Dashboard Key",
                "is_active": True
            }
        )
        
        row = result.fetchone()
        key_id = row[0]
        session.commit()
        
        return api_key, key_id

def main():
    print("\n" + "="*60)
    print("Creating API Key for Dashboard")
    print("="*60)
    
    try:
        # Ensure table exists
        ensure_table_exists()
        
        # Create the key
        print("\nGenerating API key...")
        api_key, key_id = create_api_key_direct()
        
        print(f"\nSUCCESS! API KEY CREATED!")
        print(f"\n{'='*60}")
        print(f"API Key: {api_key}")
        print(f"Key ID: {key_id}")
        print(f"{'='*60}")
        print("\nNext Steps:")
        print("1. Copy the API key above")
        print("2. Open the dashboard at http://localhost:5173")
        print("3. Click 'Enter API Key' in the header")
        print("4. Paste the key and click 'Save'")
        print("\n   OR")
        print("\n5. Create dashboard/.env file with:")
        print(f"   VITE_API_KEY={api_key}")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure the database is running: docker ps")
        print("2. Check database connection settings in .env file")
        raise

if __name__ == "__main__":
    main()

