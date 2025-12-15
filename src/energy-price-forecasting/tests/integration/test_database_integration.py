"""
Integration Tests for Database Operations.

Tests database connectivity, CRUD operations, and data integrity.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import pytest
import os
import sys
from datetime import datetime, timedelta
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from database.utils import get_database_manager
from database.operations import (
    get_price_data,
    insert_price_data,
    get_or_create_commodity,
    get_or_create_data_source
)
from database.models import PriceData, Commodity, DataSource
from sqlalchemy.orm import Session


@pytest.fixture(scope="module")
def db_session():
    """Create database session for testing."""
    db_manager = get_database_manager()
    if db_manager:
        session = db_manager.get_session()
        yield session
        session.close()
    else:
        pytest.skip("Database not available")


@pytest.fixture(scope="module")
def test_commodity(db_session: Session):
    """Create test commodity."""
    commodity = get_or_create_commodity(
        db_session,
        symbol="TEST_WTI",
        name="Test WTI",
        unit="USD/barrel"
    )
    db_session.commit()
    return commodity


@pytest.fixture(scope="module")
def test_source(db_session: Session):
    """Create test data source."""
    source = get_or_create_data_source(
        db_session,
        name="TEST_EIA",
        description="Test EIA source"
    )
    db_session.commit()
    return source


class TestDatabaseConnection:
    """Test database connectivity."""
    
    def test_database_connection(self):
        """Test that database connection works."""
        db_manager = get_database_manager()
        if db_manager:
            assert db_manager.verify_connection() is True
        else:
            pytest.skip("Database not configured")
    
    def test_database_session(self, db_session):
        """Test that database session works."""
        assert db_session is not None


class TestCommodityOperations:
    """Test commodity CRUD operations."""
    
    def test_create_commodity(self, db_session: Session):
        """Test creating a commodity."""
        commodity = get_or_create_commodity(
            db_session,
            symbol="TEST_COMM",
            name="Test Commodity",
            unit="USD/unit"
        )
        db_session.commit()
        
        assert commodity.id is not None
        assert commodity.symbol == "TEST_COMM"
    
    def test_get_commodity(self, db_session: Session, test_commodity):
        """Test retrieving a commodity."""
        commodity = db_session.query(Commodity).filter_by(
            symbol=test_commodity.symbol
        ).first()
        
        assert commodity is not None
        assert commodity.symbol == test_commodity.symbol


class TestPriceDataOperations:
    """Test price data operations."""
    
    def test_insert_price_data(
        self,
        db_session: Session,
        test_commodity: Commodity,
        test_source: DataSource
    ):
        """Test inserting price data."""
        timestamp = datetime.now()
        price = 75.50
        
        price_data = PriceData(
            timestamp=timestamp,
            commodity_id=test_commodity.id,
            source_id=test_source.id,
            price=price
        )
        
        db_session.add(price_data)
        db_session.commit()
        
        assert price_data.timestamp == timestamp
        assert price_data.price == price
    
    def test_get_price_data(
        self,
        db_session: Session,
        test_commodity: Commodity
    ):
        """Test retrieving price data."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        data, count = get_price_data(
            commodity=test_commodity.symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        # Should return data or empty DataFrame
        assert data is not None
        assert isinstance(data, pd.DataFrame) or len(data) == 0
    
    def test_price_data_query_performance(
        self,
        db_session: Session,
        test_commodity: Commodity
    ):
        """Test that price data queries are performant."""
        import time
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        start_time = time.time()
        data, count = get_price_data(
            commodity=test_commodity.symbol,
            start_date=start_date,
            end_date=end_date
        )
        query_time = time.time() - start_time
        
        # Query should complete in reasonable time (< 5 seconds)
        assert query_time < 5.0


class TestDataIntegrity:
    """Test data integrity constraints."""
    
    def test_unique_constraint(
        self,
        db_session: Session,
        test_commodity: Commodity,
        test_source: DataSource
    ):
        """Test that duplicate price data is prevented."""
        timestamp = datetime.now()
        price = 75.50
        
        # Insert first record
        price_data1 = PriceData(
            timestamp=timestamp,
            commodity_id=test_commodity.id,
            source_id=test_source.id,
            price=price
        )
        db_session.add(price_data1)
        db_session.commit()
        
        # Try to insert duplicate (should fail)
        price_data2 = PriceData(
            timestamp=timestamp,
            commodity_id=test_commodity.id,
            source_id=test_source.id,
            price=price + 1.0
        )
        db_session.add(price_data2)
        
        # Should raise integrity error
        with pytest.raises(Exception):
            db_session.commit()
        
        db_session.rollback()

