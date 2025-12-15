"""
Historical Data Service.

This module provides services for retrieving historical price data
from the database.
"""

from typing import List, Optional, Tuple
from datetime import datetime, date
import pandas as pd

from api.logging_config import get_logger
from database.operations import get_price_data
from database.utils import get_session
from database.models import PriceData, Commodity, DataSource
from sqlalchemy import func

logger = get_logger(__name__)


class HistoricalDataService:
    """
    Service for retrieving historical price data.
    
    Provides:
    - Query historical data from database
    - Support pagination (limit, offset)
    - Aggregate across sources or filter by source
    - Convert to API response format
    """
    
    def __init__(self, default_source: str = "EIA"):
        """
        Initialize historical data service.
        
        Args:
            default_source: Default data source to use if not specified
        """
        self.default_source = default_source
        logger.info(f"HistoricalDataService initialized (default_source: {default_source})")
    
    def get_historical_data(
        self,
        commodity: str,
        start_date: date,
        end_date: date,
        limit: int = 1000,
        offset: int = 0,
        source: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        """
        Get historical price data for a commodity.
        
        Args:
            commodity: Commodity symbol (WTI, BRENT, NG)
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            limit: Maximum number of records to return
            offset: Number of records to skip
            source: Data source name (None = aggregate across all sources)
            
        Returns:
            Tuple of (list of price point dicts, total count)
        """
        logger.info(
            f"Retrieving historical data: commodity={commodity}, "
            f"start_date={start_date}, end_date={end_date}, "
            f"limit={limit}, offset={offset}, source={source}"
        )
        
        # Convert date objects to datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # If source is specified, use existing function
        if source:
            df = get_price_data(
                commodity_symbol=commodity,
                source_name=source,
                start_date=start_datetime,
                end_date=end_datetime,
                limit=None  # We'll handle limit/offset ourselves
            )
            
            # Get total count
            total_count = len(df)
            
            # Apply pagination
            df_paginated = df.iloc[offset:offset + limit]
            
            # Convert to list of dicts
            price_points = self._dataframe_to_price_points(df_paginated)
            
            return price_points, total_count
        
        # If no source specified, aggregate across all sources
        # Use the most recent price for each date (or average if multiple sources)
        return self._get_aggregated_data(
            commodity=commodity,
            start_date=start_datetime,
            end_date=end_datetime,
            limit=limit,
            offset=offset
        )
    
    def _get_aggregated_data(
        self,
        commodity: str,
        start_date: datetime,
        end_date: datetime,
        limit: int,
        offset: int
    ) -> Tuple[List[dict], int]:
        """
        Get aggregated historical data across all sources.
        
        For each date, uses the most recent price from any source.
        """
        with get_session() as session:
            # Get total count first
            count_query = (
                session.query(func.count(func.distinct(func.date(PriceData.timestamp))))
                .join(Commodity)
                .filter(Commodity.symbol == commodity)
                .filter(PriceData.timestamp >= start_date)
                .filter(PriceData.timestamp <= end_date)
            )
            total_count = count_query.scalar() or 0
            
            # Get data with pagination
            # Group by date and get the most recent price for each date
            subquery = (
                session.query(
                    func.date(PriceData.timestamp).label("date"),
                    func.max(PriceData.timestamp).label("max_timestamp")
                )
                .join(Commodity)
                .filter(Commodity.symbol == commodity)
                .filter(PriceData.timestamp >= start_date)
                .filter(PriceData.timestamp <= end_date)
                .group_by(func.date(PriceData.timestamp))
                .order_by(func.date(PriceData.timestamp).desc())
                .offset(offset)
                .limit(limit)
                .subquery()
            )
            
            # Get the actual price data for those timestamps
            query = (
                session.query(PriceData)
                .join(subquery, PriceData.timestamp == subquery.c.max_timestamp)
                .order_by(PriceData.timestamp.desc())
            )
            
            results = query.all()
            
            # Convert to price points
            price_points = []
            for row in results:
                price_points.append({
                    "date": row.timestamp.date().isoformat(),
                    "price": float(row.price),
                    "volume": float(row.volume) if row.volume else None,
                    "open": float(row.open_price) if row.open_price else None,
                    "high": float(row.high_price) if row.high_price else None,
                    "low": float(row.low_price) if row.low_price else None,
                    "close": float(row.close_price) if row.close_price else None,
                })
            
            logger.info(f"Retrieved {len(price_points)} records (total: {total_count})")
            return price_points, total_count
    
    def _dataframe_to_price_points(self, df: pd.DataFrame) -> List[dict]:
        """
        Convert pandas DataFrame to list of price point dicts.
        
        Args:
            df: DataFrame with columns: timestamp, price, volume, open, high, low, close
            
        Returns:
            List of price point dictionaries
        """
        if df.empty:
            return []
        
        price_points = []
        for _, row in df.iterrows():
            # Convert timestamp to date string
            if isinstance(row['timestamp'], pd.Timestamp):
                date_str = row['timestamp'].date().isoformat()
            elif isinstance(row['timestamp'], datetime):
                date_str = row['timestamp'].date().isoformat()
            else:
                date_str = str(row['timestamp'])
            
            price_points.append({
                "date": date_str,
                "price": float(row['price']) if pd.notna(row['price']) else 0.0,
                "volume": float(row['volume']) if 'volume' in row and pd.notna(row.get('volume')) else None,
                "open": float(row['open']) if 'open' in row and pd.notna(row.get('open')) else None,
                "high": float(row['high']) if 'high' in row and pd.notna(row.get('high')) else None,
                "low": float(row['low']) if 'low' in row and pd.notna(row.get('low')) else None,
                "close": float(row['close']) if 'close' in row and pd.notna(row.get('close')) else None,
            })
        
        return price_points


# Global service instance (singleton)
_historical_data_service: Optional[HistoricalDataService] = None


def get_historical_data_service() -> HistoricalDataService:
    """
    Get the global historical data service instance.
    
    Returns:
        HistoricalDataService instance
    """
    global _historical_data_service
    if _historical_data_service is None:
        _historical_data_service = HistoricalDataService()
    return _historical_data_service

