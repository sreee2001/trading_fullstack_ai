"""Quick connection test script."""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
dbname = os.getenv("DB_NAME", "energy_forecasting")
user = os.getenv("DB_USER", "energy_user")
password = os.getenv("DB_PASSWORD", "energy_password")

print(f"Attempting connection to:")
print(f"  Host: {host}")
print(f"  Port: {port}")
print(f"  Database: {dbname}")
print(f"  User: {user}")
print()

try:
    # Try with explicit connection timeout
    conn_string = f"host={host} port={port} dbname={dbname} user={user} password={password} connect_timeout=10"
    print(f"Connection string: {conn_string}")
    print("Connecting...")
    
    conn = psycopg.connect(conn_string)
    print("✅ SUCCESS! Connected to database")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL version: {version[0][:50]}...")
    
    cursor.close()
    conn.close()
    print("✅ Connection closed successfully")
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}")
    print(f"   Message: {e}")
    import traceback
    traceback.print_exc()

