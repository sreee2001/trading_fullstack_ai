"""
Example: Fetching OHLCV Data from Yahoo Finance

This example demonstrates:
1. Using YahooFinanceClient to fetch commodity futures data
2. Fetching data at different intervals (daily, hourly)
3. Working with multiple tickers

Requirements:
- No API key required (Yahoo Finance is free)
- Internet connection

Usage:
    python examples/fetch_yahoo_finance_example.py
"""

import sys
from pathlib import Path

# Add parent directory to path to import data_ingestion module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file (not needed for Yahoo Finance, but good practice)
from dotenv import load_dotenv
load_dotenv()

from data_ingestion.yahoo_finance_client import YahooFinanceClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Fetch and display OHLCV data from Yahoo Finance."""
    try:
        # Initialize client
        client = YahooFinanceClient()
        
        print("\n" + "="*70)
        print("Fetching Commodity Futures OHLCV Data - Yahoo Finance")
        print("="*70)
        
        # Example 1: WTI Crude Oil Futures (Daily Data)
        print("\n[EXAMPLE 1] WTI Crude Oil Futures (CL=F) - Daily Data")
        print("-" * 70)
        
        wti_df = client.fetch_ohlcv(
            ticker="CL=F",
            start_date="2024-01-01",
            end_date="2024-01-31",
            interval="1d"
        )
        
        if not wti_df.empty:
            print(f"\n[SUCCESS] Fetched {len(wti_df)} daily records")
            print(f"   Date range: {wti_df['date'].min()} to {wti_df['date'].max()}")
            print(f"   Close price range: ${wti_df['close'].min():.2f} - ${wti_df['close'].max():.2f}")
            
            print("\n[FIRST 5 RECORDS]")
            print(wti_df.head().to_string(index=False))
            
            print("\n[LAST 5 RECORDS]")
            print(wti_df.tail().to_string(index=False))
            
            # Calculate price change
            price_change = wti_df['close'].iloc[-1] - wti_df['close'].iloc[0]
            price_change_pct = (price_change / wti_df['close'].iloc[0]) * 100
            
            print(f"\n[PRICE CHANGE]")
            print(f"   Start Close: ${wti_df['close'].iloc[0]:.2f}")
            print(f"   End Close: ${wti_df['close'].iloc[-1]:.2f}")
            print(f"   Change: ${price_change:+.2f} ({price_change_pct:+.2f}%)")
            
            # Save to CSV
            wti_df.to_csv("wti_futures_daily_jan_2024.csv", index=False)
            print(f"\n[SAVED] Data saved to: wti_futures_daily_jan_2024.csv")
        else:
            print("[WARNING] No data returned for WTI Crude Oil Futures")
        
        # Example 2: Brent Crude Oil Futures (Daily Data)
        print("\n" + "="*70)
        print("[EXAMPLE 2] Brent Crude Oil Futures (BZ=F) - Daily Data")
        print("-" * 70)
        
        brent_df = client.fetch_ohlcv(
            ticker="BZ=F",
            start_date="2024-01-01",
            end_date="2024-01-31",
            interval="1d"
        )
        
        if not brent_df.empty:
            print(f"\n[SUCCESS] Fetched {len(brent_df)} daily records")
            print(f"   Date range: {brent_df['date'].min()} to {brent_df['date'].max()}")
            print(f"   Close price range: ${brent_df['close'].min():.2f} - ${brent_df['close'].max():.2f}")
            
            print("\n[FIRST 3 RECORDS]")
            print(brent_df.head(3).to_string(index=False))
            
            print("\n[LAST 3 RECORDS]")
            print(brent_df.tail(3).to_string(index=False))
            
            # Save to CSV
            brent_df.to_csv("brent_futures_daily_jan_2024.csv", index=False)
            print(f"\n[SAVED] Data saved to: brent_futures_daily_jan_2024.csv")
        else:
            print("[WARNING] No data returned for Brent Crude Oil Futures")
        
        # Example 3: Natural Gas Futures (Weekly view - daily interval)
        print("\n" + "="*70)
        print("[EXAMPLE 3] Natural Gas Futures (NG=F) - Daily Data")
        print("-" * 70)
        
        ng_df = client.fetch_ohlcv(
            ticker="NG=F",
            start_date="2024-01-01",
            end_date="2024-01-31",
            interval="1d"
        )
        
        if not ng_df.empty:
            print(f"\n[SUCCESS] Fetched {len(ng_df)} daily records")
            print(f"   Close price range: ${ng_df['close'].min():.2f} - ${ng_df['close'].max():.2f}")
            print(f"   Average daily volume: {ng_df['volume'].mean():,.0f}")
            
            print("\n[SAMPLE RECORDS] (First 3):")
            print(ng_df.head(3).to_string(index=False))
            
            # Save to CSV
            ng_df.to_csv("natural_gas_futures_daily_jan_2024.csv", index=False)
            print(f"\n[SAVED] Data saved to: natural_gas_futures_daily_jan_2024.csv")
        else:
            print("[WARNING] No data returned for Natural Gas Futures")
        
        print("\n" + "="*70)
        print("[COMPLETE] Yahoo Finance OHLCV Demo Complete!")
        print("="*70)
        print("\n[TIPS]")
        print("   - No API key required for Yahoo Finance")
        print("   - Daily data (1d) is most reliable")
        print("   - Intraday data (1h, 1m) may have limited history")
        print("   - Data availability varies by ticker and interval")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n[ERROR] {e}")


if __name__ == "__main__":
    main()

