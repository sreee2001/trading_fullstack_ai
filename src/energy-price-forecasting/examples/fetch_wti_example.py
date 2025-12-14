"""
Example: Fetching WTI Crude Oil Prices from EIA API

This example demonstrates how to use the EIAAPIClient to fetch
historical WTI crude oil spot prices.

Requirements:
- EIA_API_KEY environment variable set (or in .env file)
- Valid date range (not too far in the past based on data availability)

Usage:
    python examples/fetch_wti_example.py
"""

import sys
from pathlib import Path

# Add parent directory to path to import data_ingestion module
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_ingestion.eia_client import EIAAPIClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Fetch and display WTI price data."""
    try:
        # Initialize client (will read API key from environment)
        client = EIAAPIClient()
        
        # Fetch WTI prices for January 2024
        print("\n" + "="*70)
        print("Fetching WTI Crude Oil Spot Prices - January 2024")
        print("="*70)
        
        df = client.fetch_wti_prices("2024-01-01", "2024-01-31")
        
        if df.empty:
            print("\n⚠️  No data returned. Check date range and API key.")
            return
        
        # Display summary statistics
        print(f"\n📊 Summary Statistics:")
        print(f"   Total records: {len(df)}")
        print(f"   Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
        print(f"   Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")
        print(f"   Average price: ${df['price'].mean():.2f}")
        print(f"   Median price: ${df['price'].median():.2f}")
        
        # Display first and last 5 records
        print(f"\n📈 First 5 Records:")
        print(df.head().to_string(index=False))
        
        print(f"\n📉 Last 5 Records:")
        print(df.tail().to_string(index=False))
        
        # Calculate price change
        price_change = df['price'].iloc[-1] - df['price'].iloc[0]
        price_change_pct = (price_change / df['price'].iloc[0]) * 100
        
        print(f"\n💹 Price Change:")
        print(f"   Start: ${df['price'].iloc[0]:.2f}")
        print(f"   End: ${df['price'].iloc[-1]:.2f}")
        print(f"   Change: ${price_change:+.2f} ({price_change_pct:+.2f}%)")
        
        # Optional: Save to CSV
        output_file = "wti_prices_jan_2024.csv"
        df.to_csv(output_file, index=False)
        print(f"\n💾 Data saved to: {output_file}")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print("\n❌ Error: Please ensure EIA_API_KEY is set in your .env file")
        print("   Get your free API key at: https://www.eia.gov/opendata/register.php")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

