"""
Unit tests for database models.

Tests cover:
- Model creation and attributes
- Relationships between models
- Model methods (to_dict, __repr__)
- SQLAlchemy ORM behavior

Author: Energy Trading AI Team
Created: 2025-12-14
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, Commodity, DataSource, PriceData


@pytest.fixture
def engine():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create a database session for testing."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestCommodityModel:
    """Tests for Commodity model."""
    
    def test_create_commodity(self, session):
        """Test creating a commodity."""
        commodity = Commodity(
            symbol="WTI",
            name="West Texas Intermediate Crude Oil",
            description="Light sweet crude oil benchmark",
            unit="USD/barrel"
        )
        session.add(commodity)
        session.commit()
        
        assert commodity.id is not None
        assert commodity.symbol == "WTI"
        assert commodity.name == "West Texas Intermediate Crude Oil"
        assert commodity.unit == "USD/barrel"
        assert commodity.created_at is not None
        assert commodity.updated_at is not None
    
    def test_commodity_unique_symbol(self, session):
        """Test that commodity symbol must be unique."""
        commodity1 = Commodity(symbol="WTI", name="WTI Crude")
        session.add(commodity1)
        session.commit()
        
        commodity2 = Commodity(symbol="WTI", name="Another WTI")
        session.add(commodity2)
        
        with pytest.raises(Exception):  # IntegrityError
            session.commit()
    
    def test_commodity_repr(self, session):
        """Test commodity __repr__ method."""
        commodity = Commodity(id=1, symbol="WTI", name="WTI Crude")
        repr_str = repr(commodity)
        
        assert "WTI" in repr_str
        assert "WTI Crude" in repr_str
        assert "Commodity" in repr_str


class TestDataSourceModel:
    """Tests for DataSource model."""
    
    def test_create_data_source(self, session):
        """Test creating a data source."""
        source = DataSource(
            name="EIA",
            description="U.S. Energy Information Administration",
            base_url="https://api.eia.gov",
            api_version="v2"
        )
        session.add(source)
        session.commit()
        
        assert source.id is not None
        assert source.name == "EIA"
        assert source.description == "U.S. Energy Information Administration"
        assert source.base_url == "https://api.eia.gov"
        assert source.api_version == "v2"
    
    def test_data_source_unique_name(self, session):
        """Test that data source name must be unique."""
        source1 = DataSource(name="EIA")
        session.add(source1)
        session.commit()
        
        source2 = DataSource(name="EIA")
        session.add(source2)
        
        with pytest.raises(Exception):  # IntegrityError
            session.commit()
    
    def test_data_source_repr(self, session):
        """Test data source __repr__ method."""
        source = DataSource(id=1, name="EIA")
        repr_str = repr(source)
        
        assert "EIA" in repr_str
        assert "DataSource" in repr_str


class TestPriceDataModel:
    """Tests for PriceData model."""
    
    def test_create_price_data(self, session):
        """Test creating price data."""
        # Create commodity and source
        commodity = Commodity(symbol="WTI", name="WTI Crude")
        source = DataSource(name="EIA")
        session.add_all([commodity, source])
        session.commit()
        
        # Create price data
        price_data = PriceData(
            timestamp=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            commodity_id=commodity.id,
            source_id=source.id,
            price=Decimal("75.50")
        )
        session.add(price_data)
        session.commit()
        
        assert price_data.timestamp.replace(tzinfo=None) == datetime(2024, 1, 1, 0, 0, 0)
        assert price_data.commodity_id == commodity.id
        assert price_data.source_id == source.id
        assert price_data.price == Decimal("75.50")
    
    def test_price_data_with_ohlcv(self, session):
        """Test creating price data with OHLCV fields."""
        commodity = Commodity(symbol="WTI", name="WTI Crude")
        source = DataSource(name="YAHOO")
        session.add_all([commodity, source])
        session.commit()
        
        price_data = PriceData(
            timestamp=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            commodity_id=commodity.id,
            source_id=source.id,
            price=Decimal("75.50"),
            volume=1000000,
            open_price=Decimal("75.00"),
            high_price=Decimal("76.00"),
            low_price=Decimal("74.50"),
            close_price=Decimal("75.50")
        )
        session.add(price_data)
        session.commit()
        
        assert price_data.volume == 1000000
        assert price_data.open_price == Decimal("75.00")
        assert price_data.high_price == Decimal("76.00")
        assert price_data.low_price == Decimal("74.50")
        assert price_data.close_price == Decimal("75.50")
    
    def test_price_data_composite_primary_key(self, session):
        """Test that price data has composite primary key."""
        commodity = Commodity(symbol="WTI", name="WTI Crude")
        source = DataSource(name="EIA")
        session.add_all([commodity, source])
        session.commit()
        
        # First record
        price_data1 = PriceData(
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
            commodity_id=commodity.id,
            source_id=source.id,
            price=Decimal("75.50")
        )
        session.add(price_data1)
        session.commit()
        
        # Duplicate record (same timestamp, commodity, source)
        price_data2 = PriceData(
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
            commodity_id=commodity.id,
            source_id=source.id,
            price=Decimal("76.00")
        )
        session.add(price_data2)
        
        with pytest.raises(Exception):  # IntegrityError
            session.commit()
    
    def test_price_data_repr(self, session):
        """Test price data __repr__ method."""
        price_data = PriceData(
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
            commodity_id=1,
            source_id=1,
            price=Decimal("75.50")
        )
        repr_str = repr(price_data)
        
        assert "2024-01-01" in repr_str
        assert "75.50" in repr_str
        assert "PriceData" in repr_str
    
    def test_price_data_to_dict(self, session):
        """Test price data to_dict method."""
        commodity = Commodity(symbol="WTI", name="WTI Crude")
        source = DataSource(name="EIA")
        session.add_all([commodity, source])
        session.commit()
        
        price_data = PriceData(
            timestamp=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            commodity_id=commodity.id,
            source_id=source.id,
            price=Decimal("75.50"),
            volume=1000000
        )
        session.add(price_data)
        session.commit()
        
        data_dict = price_data.to_dict()
        
        assert data_dict["commodity_id"] == commodity.id
        assert data_dict["source_id"] == source.id
        assert data_dict["price"] == 75.50
        assert data_dict["volume"] == 1000000
        assert isinstance(data_dict["timestamp"], str)


class TestRelationships:
    """Tests for model relationships."""
    
    def test_commodity_price_data_relationship(self, session):
        """Test relationship between commodity and price_data."""
        commodity = Commodity(symbol="WTI", name="WTI Crude")
        source = DataSource(name="EIA")
        session.add_all([commodity, source])
        session.commit()
        
        # Add price data (use naive datetimes for SQLite)
        price1 = PriceData(
            timestamp=datetime(2024, 1, 1),
            commodity_id=commodity.id,
            source_id=source.id,
            price=Decimal("75.50")
        )
        price2 = PriceData(
            timestamp=datetime(2024, 1, 2),
            commodity_id=commodity.id,
            source_id=source.id,
            price=Decimal("76.00")
        )
        session.add_all([price1, price2])
        session.commit()
        
        # Refresh from database
        session.expire_all()
        
        # Access via relationship
        assert len(commodity.price_data) == 2
        assert price1.commodity == commodity
        assert price2.commodity == commodity
    
    def test_data_source_price_data_relationship(self, session):
        """Test relationship between data_source and price_data."""
        commodity = Commodity(symbol="WTI", name="WTI Crude")
        source = DataSource(name="EIA")
        session.add_all([commodity, source])
        session.commit()
        
        # Add price data
        price = PriceData(
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
            commodity_id=commodity.id,
            source_id=source.id,
            price=Decimal("75.50")
        )
        session.add(price)
        session.commit()
        
        # Access via relationship
        assert len(source.price_data) == 1
        assert price.data_source == source
    
    def test_cascade_delete(self, session):
        """Test that deleting commodity cascades to price_data."""
        commodity = Commodity(symbol="WTI", name="WTI Crude")
        source = DataSource(name="EIA")
        session.add_all([commodity, source])
        session.commit()
        
        # Add price data
        price = PriceData(
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
            commodity_id=commodity.id,
            source_id=source.id,
            price=Decimal("75.50")
        )
        session.add(price)
        session.commit()
        
        # Delete commodity
        session.delete(commodity)
        session.commit()
        
        # Price data should be deleted
        remaining_prices = session.query(PriceData).count()
        assert remaining_prices == 0

