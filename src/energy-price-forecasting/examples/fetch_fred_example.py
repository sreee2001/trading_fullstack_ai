"""
Example: Fetching Multiple Commodity Prices from FRED API

This example demonstrates:
1. Using the FREDAPIClient to fetch commodity prices
2. Caching mechanism (subsequent calls are faster)
3. Cache statistics tracking

Requirements:
- FRED_API_KEY environment variable set (or in .env file)
- Valid date range

Usage:
    python examples/fetch_fred_example.py
"""

import sys
from pathlib import Path

# Add parent directory to path to import data_ingestion module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()  # This will load from .env in the current directory or parent directories

from data_ingestion.fred_client import FREDAPIClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Fetch and display commodity price data from FRED with caching demonstration."""
    try:
        # Initialize client with 5-minute cache
        client = FREDAPIClient(cache_ttl_seconds=300)
        
        # Define series to fetch
        series = {
            "DCOILWTICO": "WTI Crude Oil",
            "DCOILBRENTEU": "Brent Crude Oil",
            "DHHNGSP": "Henry Hub Natural Gas"
        }
        
        print("\n" + "="*70)
        print("Fetching Commodity Prices from FRED - January 2024")
        print("="*70)
        
        # First fetch - should be cache misses
        print("\n[FIRST FETCH] (expect cache misses):")
        results = {}
        
        for series_id, name in series.items():
            print(f"\nFetching {name} ({series_id})...")
            df = client.fetch_series(series_id, "2024-01-01", "2024-01-31")
            results[name] = df
            
            if not df.empty:
                print(f"   [SUCCESS] Fetched {len(df)} records")
                print(f"   [RANGE] Price range: ${df['value'].min():.2f} - ${df['value'].max():.2f}")
                print(f"   [LATEST] Latest: ${df['value'].iloc[-1]:.2f} ({df['date'].iloc[-1].strftime('%Y-%m-%d')})")
        
        # Show cache stats
        stats = client.get_cache_stats()
        print(f"\n[CACHE STATS] After First Fetch:")
        print(f"   Cache Hits: {stats['hits']}")
        print(f"   Cache Misses: {stats['misses']}")
        print(f"   Hit Rate: {stats['hit_rate_percent']}%")
        print(f"   Cache Size: {stats['current_size']}/{stats['max_size']}")
        
        # Second fetch - should be cache hits
        print("\n" + "="*70)
        print("[SECOND FETCH] (expect cache hits - should be instant!):")
        print("="*70)
        
        for series_id, name in series.items():
            print(f"\nFetching {name} ({series_id}) again...")
            df = client.fetch_series(series_id, "2024-01-01", "2024-01-31")
            print(f"   [SUCCESS] Returned {len(df)} records (from cache)")
        
        # Show updated cache stats
        stats = client.get_cache_stats()
        print(f"\n[CACHE STATS] After Second Fetch:")
        print(f"   Cache Hits: {stats['hits']} (increased)")
        print(f"   Cache Misses: {stats['misses']}")
        print(f"   Hit Rate: {stats['hit_rate_percent']}%")
        print(f"   Cache Size: {stats['current_size']}/{stats['max_size']}")
        
        # Display sample data for WTI
        print("\n" + "="*70)
        print("[SAMPLE DATA] WTI Crude Oil (First 5 & Last 5 records):")
        print("="*70)
        wti_df = results["WTI Crude Oil"]
        print("\nFirst 5 records:")
        print(wti_df.head().to_string(index=False))
        print("\nLast 5 records:")
        print(wti_df.tail().to_string(index=False))
        
        # Optional: Save to CSV
        for name, df in results.items():
            filename = f"{name.lower().replace(' ', '_')}_jan_2024.csv"
            df.to_csv(filename, index=False)
            print(f"[SAVED] {name} data saved to: {filename}")
        
        print("\n[COMPLETE] Demo complete! Notice how the second fetch was instant due to caching.")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print("\n[ERROR] Please ensure FRED_API_KEY is set in your .env file")
        print("   Get your free API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n[ERROR] {e}")


if __name__ == "__main__":
    main()

