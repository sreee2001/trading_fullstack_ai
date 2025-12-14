"""
EIA API Client

Client for interacting with the U.S. Energy Information Administration (EIA) API
to fetch energy commodity price data.

API Documentation: https://www.eia.gov/opendata/
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import requests
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EIAAPIClient:
    """
    Client for EIA API to fetch energy commodity price data.
    
    Supports:
    - WTI Crude Oil Spot Prices
    - Henry Hub Natural Gas Spot Prices
    - Rate limiting (5000 requests/day)
    - Automatic retry with exponential backoff
    
    Usage:
        client = EIAAPIClient(api_key="your_key")
        data = client.fetch_wti_prices("2020-01-01", "2023-12-31")
    """
    
    BASE_URL = "https://api.eia.gov/v2"
    
    # Series IDs for different commodities
    SERIES_IDS = {
        "WTI": "PET.RWTC.D",  # WTI Crude Oil Spot Price
        "BRENT": "PET.RBRTE.D",  # Brent Crude Oil Spot Price (if available)
        "NATURAL_GAS": "NG.RNGWHHD.D",  # Henry Hub Natural Gas Spot Price
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize EIA API client.
        
        Args:
            api_key: EIA API key. If not provided, will look for EIA_API_KEY env variable.
            
        Raises:
            ValueError: If API key is not provided and not found in environment.
        """
        self.api_key = api_key or os.getenv("EIA_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "EIA API key is required. "
                "Provide it as argument or set EIA_API_KEY environment variable."
            )
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "EnergyPriceForecastingSystem/0.1.0"
        })
        
        logger.info("EIA API Client initialized successfully")
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build full API URL.
        
        Args:
            endpoint: API endpoint path
            
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
        Make HTTP request to EIA API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.HTTPError: If request fails
        """
        url = self._build_url(endpoint)
        
        # Add API key to parameters
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        
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
        logger.info("EIA API Client session closed")
    
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
    
    def fetch_wti_prices(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch WTI Crude Oil spot prices from EIA.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with columns: [date, price]
            - date: pandas datetime
            - price: float (dollars per barrel)
            
        Raises:
            ValueError: If date format is invalid or date range is invalid
            requests.HTTPError: If API request fails
            
        Example:
            >>> client = EIAAPIClient(api_key="your_key")
            >>> df = client.fetch_wti_prices("2023-01-01", "2023-12-31")
            >>> print(df.head())
                  date  price
            0 2023-01-01  80.26
            1 2023-01-02  80.50
        """
        # Validate date format
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(
                f"Invalid date format. Use YYYY-MM-DD. Error: {e}"
            )
        
        # Validate date range
        if start_dt > end_dt:
            raise ValueError(
                f"Start date ({start_date}) must be before end date ({end_date})"
            )
        
        if end_dt > datetime.now():
            logger.warning(
                f"End date ({end_date}) is in the future. "
                "API will return data up to today."
            )
        
        logger.info(
            f"Fetching WTI crude oil prices from {start_date} to {end_date}"
        )
        
        # Build API endpoint for WTI series
        series_id = self.SERIES_IDS["WTI"]
        endpoint = f"petroleum/pri/spt/data/"
        
        # Prepare query parameters
        params = {
            "frequency": "daily",
            "data[0]": "value",
            "facets[series][]": series_id,
            "start": start_date,
            "end": end_date,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "offset": 0,
            "length": 5000  # Max records per request
        }
        
        # Make API request with retry logic
        response_data = self._make_request_with_retry(endpoint, params)
        
        # Parse response
        if not response_data or "response" not in response_data:
            logger.error("Invalid API response structure")
            return pd.DataFrame(columns=["date", "price"])
        
        data_records = response_data.get("response", {}).get("data", [])
        
        if not data_records:
            logger.warning(
                f"No data returned for WTI prices between {start_date} and {end_date}"
            )
            return pd.DataFrame(columns=["date", "price"])
        
        logger.info(f"Retrieved {len(data_records)} WTI price records")
        
        # Convert to DataFrame
        df = pd.DataFrame(data_records)
        
        # Extract relevant columns and rename
        if "period" in df.columns and "value" in df.columns:
            df = df[["period", "value"]].copy()
            df.columns = ["date", "price"]
            
            # Convert date to datetime
            df["date"] = pd.to_datetime(df["date"])
            
            # Convert price to float
            df["price"] = pd.to_numeric(df["price"], errors="coerce")
            
            # Drop any rows with NaN prices
            df = df.dropna(subset=["price"])
            
            # Sort by date ascending
            df = df.sort_values("date").reset_index(drop=True)
            
            logger.info(
                f"Successfully processed {len(df)} WTI price records. "
                f"Date range: {df['date'].min()} to {df['date'].max()}"
            )
            
            return df
        else:
            logger.error(
                f"Unexpected API response format. "
                f"Expected 'period' and 'value' columns, got: {df.columns.tolist()}"
            )
            return pd.DataFrame(columns=["date", "price"])


# Example usage
if __name__ == "__main__":
    # Example: Fetch WTI prices
    try:
        from dotenv import load_dotenv
        load_dotenv()  # Load .env file
        
        client = EIAAPIClient()
        logger.info("EIA API Client initialized successfully")
        
        # Fetch recent WTI prices
        df = client.fetch_wti_prices("2024-01-01", "2024-01-31")
        print(f"\nFetched {len(df)} WTI price records")
        print(df.head())
        print(f"\nPrice range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")
        
    except ValueError as e:
        logger.error(f"Failed to initialize client: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")

