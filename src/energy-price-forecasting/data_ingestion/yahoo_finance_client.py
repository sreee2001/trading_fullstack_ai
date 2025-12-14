"""
Yahoo Finance Client

Client for interacting with Yahoo Finance API via yfinance library
to fetch historical commodity futures data.

Library Documentation: https://github.com/ranaroussi/yfinance
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YahooFinanceClient:
    """
    Client for Yahoo Finance to fetch historical commodity futures data.
    
    Supports:
    - WTI Crude Oil Futures (CL=F)
    - Brent Crude Oil Futures (BZ=F)
    - Natural Gas Futures (NG=F)
    - Gold Futures (GC=F)
    - Silver Futures (SI=F)
    - OHLCV (Open, High, Low, Close, Volume) data
    
    Usage:
        client = YahooFinanceClient()
        data = client.fetch_ohlcv("CL=F", "2020-01-01", "2023-12-31")
    """
    
    # Common commodity futures tickers
    TICKERS = {
        "WTI": "CL=F",           # WTI Crude Oil Futures
        "BRENT": "BZ=F",         # Brent Crude Oil Futures
        "NATURAL_GAS": "NG=F",   # Natural Gas Futures
        "GOLD": "GC=F",          # Gold Futures
        "SILVER": "SI=F",        # Silver Futures
        "COPPER": "HG=F",        # Copper Futures
    }
    
    def __init__(self, enable_cache: bool = True):
        """
        Initialize Yahoo Finance client.
        
        Args:
            enable_cache: Whether to enable yfinance's built-in caching (default: True)
        """
        self.enable_cache = enable_cache
        
        # Cache for ticker objects to avoid recreating them
        self._ticker_cache: Dict[str, yf.Ticker] = {}
        
        logger.info(f"Yahoo Finance Client initialized (cache: {enable_cache})")
    
    def _get_ticker(self, symbol: str) -> yf.Ticker:
        """
        Get or create a yfinance Ticker object.
        
        Args:
            symbol: Ticker symbol (e.g., "CL=F")
            
        Returns:
            yfinance Ticker object
        """
        if symbol not in self._ticker_cache:
            self._ticker_cache[symbol] = yf.Ticker(symbol)
            logger.debug(f"Created ticker object for {symbol}")
        return self._ticker_cache[symbol]
    
    def _validate_date_format(self, date_str: str, param_name: str = "date") -> datetime:
        """
        Validate date string format and convert to datetime.
        
        Args:
            date_str: Date string to validate
            param_name: Parameter name for error messages
            
        Returns:
            datetime object
            
        Raises:
            ValueError: If date format is invalid
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(
                f"Invalid {param_name} format: '{date_str}'. "
                f"Expected YYYY-MM-DD. Error: {e}"
            )
    
    def _validate_date_range(self, start_date: str, end_date: str) -> tuple[datetime, datetime]:
        """
        Validate date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Tuple of (start_datetime, end_datetime)
            
        Raises:
            ValueError: If dates are invalid or range is invalid
        """
        start_dt = self._validate_date_format(start_date, "start_date")
        end_dt = self._validate_date_format(end_date, "end_date")
        
        if start_dt > end_dt:
            raise ValueError(
                f"Start date ({start_date}) must be before or equal to end date ({end_date})"
            )
        
        if end_dt > datetime.now():
            logger.warning(
                f"End date ({end_date}) is in the future. "
                "Yahoo Finance will return data up to the most recent available date."
            )
        
        return start_dt, end_dt
    
    def fetch_ohlcv(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data for a ticker.
        
        Args:
            ticker: Ticker symbol (e.g., "CL=F" for WTI futures)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            interval: Data interval (default: "1d" for daily)
                     Options: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
            
        Returns:
            DataFrame with columns: [date, open, high, low, close, volume]
            - date: pandas Timestamp (index)
            - open, high, low, close: float (prices)
            - volume: int (trading volume)
            
        Raises:
            ValueError: If date format is invalid or date range is invalid
            Exception: If data fetching fails
            
        Example:
            >>> client = YahooFinanceClient()
            >>> df = client.fetch_ohlcv("CL=F", "2023-01-01", "2023-12-31")
            >>> print(df.head())
                            open   high    low  close    volume
            date
            2023-01-01  80.26  81.50  79.80  80.50  150000
        """
        # Validate dates
        self._validate_date_range(start_date, end_date)
        
        logger.info(
            f"Fetching OHLCV data for '{ticker}' from {start_date} to {end_date} (interval: {interval})"
        )
        
        try:
            # Get ticker object
            ticker_obj = self._get_ticker(ticker)
            
            # Fetch historical data
            df = ticker_obj.history(
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=True,  # Adjust for splits and dividends
                actions=False      # Don't include dividends/splits columns
            )
            
            if df.empty:
                logger.warning(
                    f"No data returned for ticker '{ticker}' between {start_date} and {end_date}"
                )
                return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
            
            logger.info(f"Retrieved {len(df)} records for '{ticker}'")
            
            # Clean up column names (lowercase)
            df.columns = [col.lower() for col in df.columns]
            
            # Keep only OHLCV columns
            required_cols = ["open", "high", "low", "close", "volume"]
            df = df[required_cols].copy()
            
            # Reset index to make date a column
            df = df.reset_index()
            df = df.rename(columns={"index": "date"})
            
            # Ensure date column is named correctly
            if "Date" in df.columns:
                df = df.rename(columns={"Date": "date"})
            
            # Drop rows with NaN in price columns
            price_cols = ["open", "high", "low", "close"]
            nan_count = df[price_cols].isna().any(axis=1).sum()
            if nan_count > 0:
                logger.warning(
                    f"Found {nan_count} records with missing price data for '{ticker}'. "
                    "These records will be dropped."
                )
                df = df.dropna(subset=price_cols)
            
            # Sort by date
            df = df.sort_values("date").reset_index(drop=True)
            
            logger.info(
                f"Successfully processed {len(df)} records for '{ticker}'. "
                f"Date range: {df['date'].min()} to {df['date'].max()}"
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch data for '{ticker}': {e}")
            raise


# Example usage
if __name__ == "__main__":
    # Example: Fetch WTI crude oil futures data
    try:
        client = YahooFinanceClient()
        logger.info("Yahoo Finance Client initialized successfully")
        
        # Fetch WTI futures (CL=F)
        print("\n" + "="*70)
        print("WTI CRUDE OIL FUTURES (CL=F)")
        print("="*70)
        wti_df = client.fetch_ohlcv("CL=F", "2024-01-01", "2024-01-31")
        print(f"\nFetched {len(wti_df)} records")
        print(wti_df.head())
        if len(wti_df) > 0:
            print(f"\nClose price range: ${wti_df['close'].min():.2f} - ${wti_df['close'].max():.2f}")
        
        # Fetch Brent futures (BZ=F)
        print("\n" + "="*70)
        print("BRENT CRUDE OIL FUTURES (BZ=F)")
        print("="*70)
        brent_df = client.fetch_ohlcv("BZ=F", "2024-01-01", "2024-01-31")
        print(f"\nFetched {len(brent_df)} records")
        print(brent_df.head())
        if len(brent_df) > 0:
            print(f"\nClose price range: ${brent_df['close'].min():.2f} - ${brent_df['close'].max():.2f}")
        
    except Exception as e:
        logger.error(f"Error: {e}")

