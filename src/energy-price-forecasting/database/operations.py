"""
Database operations for Energy Price Forecasting System.

This module provides high-level functions for inserting and retrieving
price data, handling bulk operations, and common query patterns.

Features:
- Bulk insert with upsert (INSERT ... ON CONFLICT)
- Query price data by commodity, source, date range
- Get latest prices
- Get price statistics
- Pandas DataFrame integration

Author: Energy Trading AI Team
Created: 2025-12-14
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple

import pandas as pd
from sqlalchemy import and_, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from database.models import Commodity, DataSource, PriceData
from database.utils import get_session

logger = logging.getLogger(__name__)


def get_or_create_commodity(
    session: Session,
    symbol: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    unit: Optional[str] = None
) -> Commodity:
    """
    Get existing commodity or create if it doesn't exist.
    
    Args:
        session: SQLAlchemy session
        symbol: Commodity symbol (e.g., WTI, BRENT)
        name: Commodity name (required if creating new)
        description: Commodity description (optional)
        unit: Price unit (optional, e.g., USD/barrel)
    
    Returns:
        Commodity: Existing or newly created commodity
    
    Raises:
        ValueError: If commodity doesn't exist and name is not provided
    """
    commodity = session.query(Commodity).filter_by(symbol=symbol).first()
    
    if commodity is None:
        if name is None:
            raise ValueError(
                f"Commodity '{symbol}' does not exist and name was not provided"
            )
        
        commodity = Commodity(
            symbol=symbol,
            name=name,
            description=description,
            unit=unit
        )
        session.add(commodity)
        session.flush()  # Get the ID without committing
        logger.info(f"Created new commodity: {symbol} (ID: {commodity.id})")
    
    return commodity


def get_or_create_data_source(
    session: Session,
    name: str,
    description: Optional[str] = None,
    base_url: Optional[str] = None,
    api_version: Optional[str] = None
) -> DataSource:
    """
    Get existing data source or create if it doesn't exist.
    
    Args:
        session: SQLAlchemy session
        name: Source name (e.g., EIA, FRED, YAHOO)
        description: Source description (optional)
        base_url: API base URL (optional)
        api_version: API version (optional)
    
    Returns:
        DataSource: Existing or newly created data source
    """
    source = session.query(DataSource).filter_by(name=name).first()
    
    if source is None:
        source = DataSource(
            name=name,
            description=description,
            base_url=base_url,
            api_version=api_version
        )
        session.add(source)
        session.flush()  # Get the ID without committing
        logger.info(f"Created new data source: {name} (ID: {source.id})")
    
    return source


def insert_price_data(
    commodity: str,
    source: str,
    timestamp: datetime,
    price: float,
    volume: Optional[float] = None,
    open_price: Optional[float] = None,
    high_price: Optional[float] = None,
    low_price: Optional[float] = None,
    close_price: Optional[float] = None
) -> int:
    """
    Insert a single price data record into the database.
    
    Args:
        commodity: Commodity symbol (e.g., WTI_CRUDE)
        source: Data source name (e.g., EIA)
        timestamp: Price timestamp
        price: Price value
        volume: Trading volume (optional)
        open_price: Opening price (optional)
        high_price: High price (optional)
        low_price: Low price (optional)
        close_price: Closing price (optional)
    
    Returns:
        int: Number of records inserted (0 or 1)
    """
    with get_session() as session:
        # Get or create commodity and data source
        try:
            commodity_obj = get_or_create_commodity(session, commodity)
        except ValueError:
            commodity_obj = get_or_create_commodity(
                session,
                symbol=commodity,
                name=commodity
            )
        source_obj = get_or_create_data_source(session, source)
        
        # Prepare record
        record = {
            "timestamp": timestamp,
            "commodity_id": commodity_obj.id,
            "source_id": source_obj.id,
            "price": price,
        }
        
        if volume is not None:
            record["volume"] = int(volume)
        if open_price is not None:
            record["open_price"] = open_price
        if high_price is not None:
            record["high_price"] = high_price
        if low_price is not None:
            record["low_price"] = low_price
        if close_price is not None:
            record["close_price"] = close_price
        
        # Perform upsert
        stmt = insert(PriceData).values([record])
        stmt = stmt.on_conflict_do_update(
            index_elements=["timestamp", "commodity_id", "source_id"],
            set_={
                "price": stmt.excluded.price,
                "volume": stmt.excluded.volume,
                "open_price": stmt.excluded.open_price,
                "high_price": stmt.excluded.high_price,
                "low_price": stmt.excluded.low_price,
                "close_price": stmt.excluded.close_price,
            }
        )
        
        result = session.execute(stmt)
        inserted_count = result.rowcount
        
        return inserted_count


def insert_price_data_bulk(
    df: pd.DataFrame,
    commodity_symbol: str,
    source_name: str,
    upsert: bool = True
) -> int:
    """
    Insert price data from a Pandas DataFrame into the database.
    
    This function performs bulk insertion with optional upsert behavior.
    If upsert=True, existing records are updated; otherwise, they're skipped.
    
    Args:
        df: DataFrame with columns: date, price, and optionally volume, open, high, low, close
        commodity_symbol: Commodity symbol (e.g., WTI)
        source_name: Data source name (e.g., EIA)
        upsert: If True, update existing records; if False, skip duplicates
    
    Returns:
        int: Number of records inserted/updated
    
    Raises:
        ValueError: If DataFrame is missing required columns
    
    Example:
        ```python
        df = pd.DataFrame({
            "date": ["2024-01-01", "2024-01-02"],
            "price": [75.50, 76.20]
        })
        count = insert_price_data(df, "WTI", "EIA")
        print(f"Inserted {count} records")
        ```
    """
    # Validate required columns
    if "date" not in df.columns or "price" not in df.columns:
        raise ValueError("DataFrame must contain 'date' and 'price' columns")
    
    if df.empty:
        logger.warning("Empty DataFrame provided, no data to insert")
        return 0
    
    with get_session() as session:
        # Get or create commodity and data source
        # For commodities, provide a default name if creating new
        try:
            commodity = get_or_create_commodity(session, commodity_symbol)
        except ValueError:
            # Create with default name if not exists
            commodity = get_or_create_commodity(
                session,
                symbol=commodity_symbol,
                name=commodity_symbol  # Use symbol as default name
            )
        source = get_or_create_data_source(session, source_name)
        
        # Prepare records for insertion
        records = []
        for _, row in df.iterrows():
            # Parse date
            timestamp = pd.to_datetime(row["date"])
            if timestamp.tzinfo is None:
                timestamp = timestamp.tz_localize("UTC")
            else:
                timestamp = timestamp.tz_convert("UTC")
            
            record = {
                "timestamp": timestamp,
                "commodity_id": commodity.id,
                "source_id": source.id,
                "price": float(row["price"]),
            }
            
            # Add optional columns if present
            if "volume" in df.columns and pd.notna(row.get("volume")):
                record["volume"] = int(row["volume"])
            
            if "open" in df.columns and pd.notna(row.get("open")):
                record["open_price"] = float(row["open"])
            
            if "high" in df.columns and pd.notna(row.get("high")):
                record["high_price"] = float(row["high"])
            
            if "low" in df.columns and pd.notna(row.get("low")):
                record["low_price"] = float(row["low"])
            
            if "close" in df.columns and pd.notna(row.get("close")):
                record["close_price"] = float(row["close"])
            
            records.append(record)
        
        # Perform bulk insert with upsert or skip duplicates
        stmt = insert(PriceData).values(records)
        
        if upsert:
            # Update existing records
            stmt = stmt.on_conflict_do_update(
                index_elements=["timestamp", "commodity_id", "source_id"],
                set_={
                    "price": stmt.excluded.price,
                    "volume": stmt.excluded.volume,
                    "open_price": stmt.excluded.open_price,
                    "high_price": stmt.excluded.high_price,
                    "low_price": stmt.excluded.low_price,
                    "close_price": stmt.excluded.close_price,
                }
            )
        else:
            # Skip existing records
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["timestamp", "commodity_id", "source_id"]
            )
        
        result = session.execute(stmt)
        inserted_count = result.rowcount
        
        logger.info(
            f"Inserted/updated {inserted_count} records for "
            f"{commodity_symbol} from {source_name}"
        )
        
        return inserted_count


def get_price_data(
    commodity_symbol: str,
    source_name: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: Optional[int] = None
) -> pd.DataFrame:
    """
    Retrieve price data as a Pandas DataFrame.
    
    Args:
        commodity_symbol: Commodity symbol (e.g., WTI)
        source_name: Data source name (e.g., EIA)
        start_date: Start date (inclusive, optional)
        end_date: End date (inclusive, optional)
        limit: Maximum number of records (optional)
    
    Returns:
        pd.DataFrame: Price data with columns: timestamp, price, volume, etc.
    
    Example:
        ```python
        from datetime import datetime
        
        df = get_price_data(
            "WTI",
            "EIA",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        print(df.head())
        ```
    """
    with get_session() as session:
        # Build query
        query = (
            session.query(PriceData)
            .join(Commodity)
            .join(DataSource)
            .filter(Commodity.symbol == commodity_symbol)
            .filter(DataSource.name == source_name)
        )
        
        # Add date filters
        if start_date:
            query = query.filter(PriceData.timestamp >= start_date)
        
        if end_date:
            query = query.filter(PriceData.timestamp <= end_date)
        
        # Order by timestamp
        query = query.order_by(PriceData.timestamp.desc())
        
        # Apply limit
        if limit:
            query = query.limit(limit)
        
        # Execute query
        results = query.all()
        
        if not results:
            logger.warning(
                f"No data found for {commodity_symbol} from {source_name} "
                f"(date range: {start_date} to {end_date})"
            )
            return pd.DataFrame()
        
        # Convert to DataFrame
        data = [
            {
                "timestamp": row.timestamp,
                "price": float(row.price),
                "volume": row.volume,
                "open": float(row.open_price) if row.open_price else None,
                "high": float(row.high_price) if row.high_price else None,
                "low": float(row.low_price) if row.low_price else None,
                "close": float(row.close_price) if row.close_price else None,
            }
            for row in results
        ]
        
        df = pd.DataFrame(data)
        logger.info(f"Retrieved {len(df)} records for {commodity_symbol} from {source_name}")
        
        return df


def get_latest_price_date() -> Optional[datetime]:
    """
    Get the most recent date for which we have price data across all sources.
    
    Returns:
        Optional[datetime]: Latest timestamp or None if no data exists
    
    Example:
        ```python
        latest_date = get_latest_price_date()
        if latest_date:
            print(f"Data is current up to: {latest_date}")
        ```
    """
    with get_session() as session:
        result = (
            session.query(func.max(PriceData.timestamp))
            .scalar()
        )
        
        if result:
            logger.info(f"Latest price date in database: {result}")
            return result
        else:
            logger.info("No price data found in database")
            return None


def get_latest_price(
    commodity_symbol: str,
    source_name: str
) -> Optional[Tuple[datetime, float]]:
    """
    Get the latest price for a commodity from a specific source.
    
    Args:
        commodity_symbol: Commodity symbol (e.g., WTI)
        source_name: Data source name (e.g., EIA)
    
    Returns:
        Optional[Tuple[datetime, float]]: (timestamp, price) or None if not found
    
    Example:
        ```python
        latest = get_latest_price("WTI", "EIA")
        if latest:
            timestamp, price = latest
            print(f"Latest WTI price: ${price} at {timestamp}")
        ```
    """
    with get_session() as session:
        result = (
            session.query(PriceData.timestamp, PriceData.price)
            .join(Commodity)
            .join(DataSource)
            .filter(Commodity.symbol == commodity_symbol)
            .filter(DataSource.name == source_name)
            .order_by(PriceData.timestamp.desc())
            .first()
        )
        
        if result:
            logger.info(f"Latest price for {commodity_symbol} from {source_name}: ${result[1]}")
            return result
        else:
            logger.warning(f"No price data found for {commodity_symbol} from {source_name}")
            return None


def get_price_statistics(
    commodity_symbol: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> dict:
    """
    Get statistical summary of price data across all sources.
    
    Args:
        commodity_symbol: Commodity symbol (e.g., WTI)
        start_date: Start date (inclusive, optional)
        end_date: End date (inclusive, optional)
    
    Returns:
        dict: Statistics (avg_price, min_price, max_price, total_volume, record_count)
    
    Example:
        ```python
        from datetime import datetime
        
        stats = get_price_statistics(
            "WTI",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        print(f"Average WTI price in Jan 2024: ${stats['avg_price']:.2f}")
        ```
    """
    with get_session() as session:
        # Build query
        query = (
            session.query(
                func.avg(PriceData.price).label("avg_price"),
                func.min(PriceData.price).label("min_price"),
                func.max(PriceData.price).label("max_price"),
                func.sum(PriceData.volume).label("total_volume"),
                func.count(PriceData.timestamp).label("record_count"),
            )
            .join(Commodity)
            .filter(Commodity.symbol == commodity_symbol)
        )
        
        # Add date filters
        if start_date:
            query = query.filter(PriceData.timestamp >= start_date)
        
        if end_date:
            query = query.filter(PriceData.timestamp <= end_date)
        
        # Execute query
        result = query.first()
        
        stats = {
            "avg_price": float(result.avg_price) if result.avg_price else 0.0,
            "min_price": float(result.min_price) if result.min_price else 0.0,
            "max_price": float(result.max_price) if result.max_price else 0.0,
            "total_volume": int(result.total_volume) if result.total_volume else 0,
            "record_count": result.record_count,
        }
        
        logger.info(f"Price statistics for {commodity_symbol}: {stats}")
        
        return stats


def delete_price_data(
    commodity_symbol: str,
    source_name: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> int:
    """
    Delete price data for a specific commodity and source.
    
    WARNING: This operation is irreversible!
    
    Args:
        commodity_symbol: Commodity symbol (e.g., WTI)
        source_name: Data source name (e.g., EIA)
        start_date: Start date (inclusive, optional)
        end_date: End date (inclusive, optional)
    
    Returns:
        int: Number of records deleted
    """
    with get_session() as session:
        # Get commodity and source IDs first
        commodity = (
            session.query(Commodity)
            .filter_by(symbol=commodity_symbol)
            .first()
        )
        source = (
            session.query(DataSource)
            .filter_by(name=source_name)
            .first()
        )
        
        if not commodity or not source:
            logger.warning(
                f"Cannot delete: commodity '{commodity_symbol}' or "
                f"source '{source_name}' not found"
            )
            return 0
        
        # Build query without joins (to allow delete)
        query = session.query(PriceData).filter(
            PriceData.commodity_id == commodity.id,
            PriceData.source_id == source.id
        )
        
        # Add date filters
        if start_date:
            query = query.filter(PriceData.timestamp >= start_date)
        
        if end_date:
            query = query.filter(PriceData.timestamp <= end_date)
        
        # Delete
        deleted_count = query.delete(synchronize_session=False)
        
        logger.warning(
            f"Deleted {deleted_count} records for {commodity_symbol} "
            f"from {source_name} (date range: {start_date} to {end_date})"
        )
        
        return deleted_count

