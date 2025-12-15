"""
Example script demonstrating database operations.

This script shows how to:
1. Connect to the database
2. Check TimescaleDB availability
3. Insert price data from API
4. Retrieve and query data
5. Get statistics

Prerequisites:
- PostgreSQL + TimescaleDB running (via Docker or locally)
- .env file configured with database credentials
- EIA API key configured

Usage:
    python examples/database_example.py
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from data_ingestion.eia_client import EIAAPIClient
from database import get_database_manager, get_session
from database.operations import (
    insert_price_data,
    get_price_data,
    get_latest_price,
    get_price_statistics,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    print("=" * 70)
    print("DATABASE OPERATIONS EXAMPLE")
    print("=" * 70)
    
    # Step 1: Initialize database manager and check connection
    print("\n[1/6] Initializing database connection...")
    db = get_database_manager()
    
    if not db.check_connection():
        print("ERROR: Failed to connect to database")
        print("\nMake sure:")
        print("1. Docker container is running: docker-compose up -d")
        print("2. Database credentials in .env file are correct")
        sys.exit(1)
    
    print("SUCCESS: Database connection established")
    
    # Step 2: Check TimescaleDB
    print("\n[2/6] Checking TimescaleDB extension...")
    if db.check_timescale_extension():
        print("SUCCESS: TimescaleDB is available")
    else:
        print("WARNING: TimescaleDB not found (hypertable features unavailable)")
    
    # Step 3: Check connection pool
    print("\n[3/6] Connection pool status:")
    pool_status = db.get_pool_status()
    for key, value in pool_status.items():
        print(f"  - {key}: {value}")
    
    # Step 4: Fetch and insert price data
    print("\n[4/6] Fetching WTI prices from EIA and inserting to database...")
    try:
        # Fetch data from EIA
        eia_client = EIAAPIClient()
        df = eia_client.fetch_wti_prices("2024-01-01", "2024-01-31")
        
        print(f"Fetched {len(df)} records from EIA")
        print("\nSample data:")
        print(df.head(3))
        
        # Insert to database
        inserted_count = insert_price_data(
            df,
            commodity_symbol="WTI",
            source_name="EIA",
            upsert=True  # Update if already exists
        )
        
        print(f"\nINSERTED/UPDATED: {inserted_count} records in database")
        
    except Exception as e:
        print(f"ERROR: Failed to fetch/insert data: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 5: Query data back from database
    print("\n[5/6] Querying price data from database...")
    try:
        # Get data for January 2024
        df_from_db = get_price_data(
            commodity_symbol="WTI",
            source_name="EIA",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            limit=10  # Get first 10 records
        )
        
        print(f"Retrieved {len(df_from_db)} records from database:")
        print(df_from_db.head())
        
        # Get latest price
        latest = get_latest_price("WTI", "EIA")
        if latest:
            timestamp, price = latest
            print(f"\nLatest WTI price: ${price:.2f} at {timestamp}")
        
    except Exception as e:
        print(f"ERROR: Failed to query data: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 6: Get statistics
    print("\n[6/6] Price statistics for January 2024:")
    try:
        stats = get_price_statistics(
            commodity_symbol="WTI",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        
        print(f"  - Record count: {stats['record_count']}")
        print(f"  - Average price: ${stats['avg_price']:.2f}")
        print(f"  - Min price: ${stats['min_price']:.2f}")
        print(f"  - Max price: ${stats['max_price']:.2f}")
        
    except Exception as e:
        print(f"ERROR: Failed to get statistics: {e}")
    
    print("\n" + "=" * 70)
    print("EXAMPLE COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("- Check data in database: psql -U energy_user -d energy_forecasting")
    print("- Run more examples: python examples/fetch_fred_example.py")
    print("- Integrate Yahoo Finance data into database")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()



