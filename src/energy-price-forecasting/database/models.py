"""
SQLAlchemy ORM Models for Energy Price Forecasting System.

This module defines the database models using SQLAlchemy ORM:
- Commodity: Commodity definitions (WTI, Brent, Natural Gas, etc.)
- DataSource: External data source definitions (EIA, FRED, Yahoo, etc.)
- PriceData: Time-series price data (main table)

Author: Energy Trading AI Team
Created: 2025-12-14
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    BigInteger,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Commodity(Base):
    """
    Commodity model representing energy commodities.
    
    Attributes:
        id: Primary key
        symbol: Short symbol (e.g., WTI, BRENT, NATGAS)
        name: Full commodity name
        description: Detailed description
        unit: Price unit (e.g., USD/barrel, USD/MMBtu)
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    
    __tablename__ = "commodities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    unit = Column(String(20))
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
    
    # Relationships
    price_data = relationship(
        "PriceData",
        back_populates="commodity",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Commodity(id={self.id}, symbol='{self.symbol}', name='{self.name}')>"


class DataSource(Base):
    """
    Data source model representing external data providers.
    
    Attributes:
        id: Primary key
        name: Source identifier (e.g., EIA, FRED, YAHOO)
        description: Detailed description
        base_url: API base URL
        api_version: API version string
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    base_url = Column(String(255))
    api_version = Column(String(20))
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
    
    # Relationships
    price_data = relationship(
        "PriceData",
        back_populates="data_source",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<DataSource(id={self.id}, name='{self.name}')>"


class PriceData(Base):
    """
    Price data model for time-series commodity prices.
    
    This is the main table for storing historical price data.
    It's converted to a TimescaleDB hypertable for optimized time-series queries.
    
    Attributes:
        timestamp: Price timestamp (part of composite primary key)
        commodity_id: Foreign key to commodities table
        source_id: Foreign key to data_sources table
        price: Spot or closing price
        volume: Trading volume (optional)
        open_price: Opening price for OHLCV data (optional)
        high_price: Daily high price (optional)
        low_price: Daily low price (optional)
        close_price: Closing price for OHLCV data (optional)
        created_at: Timestamp when record was inserted
    """
    
    __tablename__ = "price_data"
    __table_args__ = (
        # Composite primary key
        UniqueConstraint(
            "timestamp",
            "commodity_id",
            "source_id",
            name="price_data_pkey"
        ),
        # Indexes for common query patterns
        Index(
            "idx_price_data_commodity",
            "commodity_id",
            "timestamp",
            postgresql_ops={"timestamp": "DESC"}
        ),
        Index(
            "idx_price_data_source",
            "source_id",
            "timestamp",
            postgresql_ops={"timestamp": "DESC"}
        ),
        Index(
            "idx_price_data_commodity_source",
            "commodity_id",
            "source_id",
            "timestamp",
            postgresql_ops={"timestamp": "DESC"}
        ),
    )
    
    timestamp = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    commodity_id = Column(
        Integer,
        ForeignKey("commodities.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    source_id = Column(
        Integer,
        ForeignKey("data_sources.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    price = Column(Numeric(12, 4), nullable=False)
    volume = Column(BigInteger)
    open_price = Column(Numeric(12, 4))
    high_price = Column(Numeric(12, 4))
    low_price = Column(Numeric(12, 4))
    close_price = Column(Numeric(12, 4))
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False
    )
    
    # Relationships
    commodity = relationship("Commodity", back_populates="price_data")
    data_source = relationship("DataSource", back_populates="price_data")
    
    def __repr__(self) -> str:
        return (
            f"<PriceData(timestamp={self.timestamp}, "
            f"commodity_id={self.commodity_id}, "
            f"source_id={self.source_id}, "
            f"price={self.price})>"
        )
    
    def to_dict(self) -> dict:
        """Convert model instance to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "commodity_id": self.commodity_id,
            "source_id": self.source_id,
            "price": float(self.price) if self.price else None,
            "volume": self.volume,
            "open_price": float(self.open_price) if self.open_price else None,
            "high_price": float(self.high_price) if self.high_price else None,
            "low_price": float(self.low_price) if self.low_price else None,
            "close_price": float(self.close_price) if self.close_price else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

