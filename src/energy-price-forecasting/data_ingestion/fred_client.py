"""
FRED API Client

Client for interacting with the Federal Reserve Economic Data (FRED) API
to fetch economic indicators and commodity prices.

API Documentation: https://fred.stlouisfed.org/docs/api/fred/
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib

import requests
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FREDAPIClient:
    """
    Client for FRED API to fetch economic indicators and commodity prices.
    
    Supports:
    - WTI Crude Oil (DCOILWTICO)
    - Brent Crude Oil (DCOILBRENTEU)
    - Various economic indicators
    - Rate limiting (120 requests/minute)
    - Automatic retry with exponential backoff
    
    Usage:
        client = FREDAPIClient(api_key="your_key")
        data = client.fetch_series("DCOILWTICO", "2020-01-01", "2023-12-31")
    """
    
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    # Common series IDs for commodities
    SERIES_IDS = {
        "WTI": "DCOILWTICO",           # WTI Crude Oil Spot Price
        "BRENT": "DCOILBRENTEU",       # Brent Crude Oil Spot Price
        "NATURAL_GAS": "DHHNGSP",      # Henry Hub Natural Gas Spot Price
    }
    
    def __init__(self, api_key: Optional[str] = None, enable_cache: bool = True, cache_ttl_minutes: int = 5):
        """
        Initialize FRED API client.
        
        Args:
            api_key: FRED API key. If not provided, will look for FRED_API_KEY env variable.
            enable_cache: Whether to enable in-memory caching (default: True)
            cache_ttl_minutes: Cache time-to-live in minutes (default: 5)
            
        Raises:
            ValueError: If API key is not provided and not found in environment.
        """
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "FRED API key is required. "
                "Provide it as argument or set the FRED_API_KEY environment variable. "
                "Get your free API key at: https://fred.stlouisfed.org/docs/api/api_key.html"
            )
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "EnergyPriceForecastingSystem/0.1.0"
        })
        
        # Initialize cache
        self.enable_cache = enable_cache
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self._cache: Dict[str, tuple[pd.DataFrame, datetime]] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
        logger.info(f"FRED API Client initialized successfully (cache: {enable_cache}, TTL: {cache_ttl_minutes}min)")
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build full API URL.
        
        Args:
            endpoint: API endpoint path (e.g., "series/observations")
            
        Returns:
            Full URL string
        """
        return f"{self.BASE_URL}/{endpoint}"
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to FRED API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.HTTPError: If request fails
        """
        url = self._build_url(endpoint)
        
        # Add API key and file type to parameters
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        params["file_type"] = "json"  # Request JSON format
        
        logger.debug(f"Making request to {url} with params {params}")
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException,)),
        reraise=True
    )
    def _make_request_with_retry(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with automatic retry on failures.
        
        Uses exponential backoff:
        - Attempt 1: immediate
        - Attempt 2: wait 2 seconds
        - Attempt 3: wait 4 seconds
        - Max 3 attempts
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.HTTPError: If all retries fail
        """
        try:
            return self._make_request(endpoint, params)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning("Rate limit exceeded (429). Retrying with backoff...")
                raise
            elif e.response.status_code >= 500:
                logger.warning(f"Server error ({e.response.status_code}). Retrying...")
                raise
            else:
                # Don't retry on client errors (4xx except 429)
                logger.error(f"Client error ({e.response.status_code}): {e}")
                raise
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
        logger.info("FRED API Client session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Destructor to ensure session is closed."""
        if hasattr(self, 'session'):
            self.session.close()
    
    def _make_cache_key(self, series_id: str, start_date: str, end_date: str) -> str:
        """
        Generate cache key for a series request.
        
        Args:
            series_id: FRED series ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Cache key string
        """
        key_str = f"{series_id}:{start_date}:{end_date}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[pd.DataFrame]:
        """
        Retrieve data from cache if available and not expired.
        
        Args:
            cache_key: Cache key
            
        Returns:
            DataFrame if found and valid, None otherwise
        """
        if not self.enable_cache:
            return None
        
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            age = datetime.now() - timestamp
            
            if age < self.cache_ttl:
                self._cache_hits += 1
                logger.debug(f"Cache HIT: {cache_key} (age: {age.total_seconds():.1f}s)")
                return data.copy()  # Return copy to avoid mutation
            else:
                # Expired, remove from cache
                del self._cache[cache_key]
                logger.debug(f"Cache EXPIRED: {cache_key} (age: {age.total_seconds():.1f}s)")
        
        self._cache_misses += 1
        logger.debug(f"Cache MISS: {cache_key}")
        return None
    
    def _put_in_cache(self, cache_key: str, data: pd.DataFrame):
        """
        Store data in cache.
        
        Args:
            cache_key: Cache key
            data: DataFrame to cache
        """
        if self.enable_cache:
            self._cache[cache_key] = (data.copy(), datetime.now())
            logger.debug(f"Cache STORE: {cache_key} ({len(data)} rows)")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "enabled": self.enable_cache,
            "ttl_minutes": self.cache_ttl.total_seconds() / 60,
            "cache_size": len(self._cache),
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2)
        }
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        logger.info("Cache cleared")
    
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
                "API will return data up to the most recent available date."
            )
        
        return start_dt, end_dt
    
    def fetch_series(
        self,
        series_id: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch FRED economic data series (with caching).
        
        Args:
            series_id: FRED series ID (e.g., "DCOILWTICO" for WTI)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with columns: [date, value]
            - date: pandas Timestamp
            - value: float
            
        Raises:
            ValueError: If date format is invalid or date range is invalid
            requests.HTTPError: If API request fails
            
        Example:
            >>> client = FREDAPIClient(api_key="your_key")
            >>> df = client.fetch_series("DCOILWTICO", "2023-01-01", "2023-12-31")
            >>> print(df.head())
                  date  value
            0 2023-01-01  80.26
            1 2023-01-02  80.50
        """
        # Validate dates
        self._validate_date_range(start_date, end_date)
        
        # Check cache first
        cache_key = self._make_cache_key(series_id, start_date, end_date)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            logger.info(f"Returning cached data for series '{series_id}'")
            return cached_data
        
        logger.info(
            f"Fetching FRED series '{series_id}' from {start_date} to {end_date}"
        )
        
        # Build API endpoint for series observations
        endpoint = "series/observations"
        
        # Prepare query parameters
        params = {
            "series_id": series_id,
            "observation_start": start_date,
            "observation_end": end_date,
            "sort_order": "asc"
        }
        
        # Make API request with retry logic
        response_data = self._make_request_with_retry(endpoint, params)
        
        # Parse response
        if not response_data or "observations" not in response_data:
            logger.error(f"Invalid API response structure for series '{series_id}'")
            return pd.DataFrame(columns=["date", "value"])
        
        observations = response_data.get("observations", [])
        
        if not observations:
            logger.warning(
                f"No data returned for series '{series_id}' between {start_date} and {end_date}"
            )
            return pd.DataFrame(columns=["date", "value"])
        
        logger.info(f"Retrieved {len(observations)} observations for series '{series_id}'")
        
        # Convert to DataFrame
        df = pd.DataFrame(observations)
        
        # Extract relevant columns
        if "date" in df.columns and "value" in df.columns:
            df = df[["date", "value"]].copy()
            
            # Convert date to datetime
            df["date"] = pd.to_datetime(df["date"])
            
            # Convert value to float, handling "." (missing values)
            df["value"] = df["value"].replace(".", None)
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            
            # Drop any rows with NaN values
            nan_count = df["value"].isna().sum()
            if nan_count > 0:
                logger.warning(
                    f"Found {nan_count} missing/invalid values in series '{series_id}'. "
                    "These records will be dropped."
                )
                df = df.dropna(subset=["value"])
            
            # Sort by date ascending
            df = df.sort_values("date").reset_index(drop=True)
            
            logger.info(
                f"Successfully processed {len(df)} observations for series '{series_id}'. "
                f"Date range: {df['date'].min()} to {df['date'].max()}"
            )
            
            # Store in cache
            self._put_in_cache(cache_key, df)
            
            return df
        else:
            logger.error(
                f"Unexpected API response format for series '{series_id}'. "
                f"Expected 'date' and 'value' columns, got: {df.columns.tolist()}"
            )
            return pd.DataFrame(columns=["date", "value"])


# Example usage
if __name__ == "__main__":
    # Example: Fetch WTI and Brent crude oil prices with caching
    try:
        from dotenv import load_dotenv
        load_dotenv()  # Load .env file
        
        client = FREDAPIClient()
        logger.info("FRED API Client initialized successfully")
        
        # Fetch WTI crude oil prices (first call - cache miss)
        print("\n" + "="*70)
        print("WTI CRUDE OIL PRICES (FRED) - First Call")
        print("="*70)
        wti_df = client.fetch_series("DCOILWTICO", "2024-01-01", "2024-01-31")
        print(f"\nFetched {len(wti_df)} WTI price records")
        print(wti_df.head())
        if len(wti_df) > 0:
            print(f"Price range: ${wti_df['value'].min():.2f} - ${wti_df['value'].max():.2f}")
        
        # Fetch same data again (should hit cache)
        print("\n" + "="*70)
        print("WTI CRUDE OIL PRICES (FRED) - Second Call (Cached)")
        print("="*70)
        wti_df2 = client.fetch_series("DCOILWTICO", "2024-01-01", "2024-01-31")
        print(f"Fetched {len(wti_df2)} WTI price records (from cache)")
        
        # Display cache statistics
        print("\n" + "="*70)
        print("CACHE STATISTICS")
        print("="*70)
        stats = client.get_cache_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
        
    except ValueError as e:
        logger.error(f"Failed to initialize client: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")

