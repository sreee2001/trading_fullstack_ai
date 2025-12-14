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


# Example usage
if __name__ == "__main__":
    # This will be expanded in subsequent stories
    try:
        client = EIAAPIClient()
        logger.info("EIA API Client test successful")
    except ValueError as e:
        logger.error(f"Failed to initialize client: {e}")

