"""
Database utilities for Energy Price Forecasting System.

This module provides database connection management, session handling,
and utility functions for interacting with PostgreSQL + TimescaleDB.

Features:
- Connection pooling using SQLAlchemy
- Environment-based configuration
- Context manager for sessions
- Helper functions for common operations

Author: Energy Trading AI Team
Created: 2025-12-14
"""

import logging
import os
from contextlib import contextmanager
from typing import Optional, Generator
from urllib.parse import quote_plus

from sqlalchemy import create_engine, event, exc, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from database.models import Base, Commodity, DataSource, PriceData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """
    Database configuration from environment variables.
    
    Environment Variables:
        DATABASE_URL: Full PostgreSQL connection URL (if provided, overrides others)
        DB_HOST: Database host (default: localhost)
        DB_PORT: Database port (default: 5432)
        DB_NAME: Database name (default: energy_forecasting)
        DB_USER: Database user (default: energy_user)
        DB_PASSWORD: Database password (default: energy_password)
    """
    
    def __init__(self):
        # Option 1: Use DATABASE_URL if provided
        self.database_url = os.getenv("DATABASE_URL")
        
        # Option 2: Build from individual components
        if not self.database_url:
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            name = os.getenv("DB_NAME", "energy_forecasting")
            user = os.getenv("DB_USER", "energy_user")
            password = os.getenv("DB_PASSWORD", "energy_password")
            
            # URL-encode password to handle special characters
            encoded_password = quote_plus(password)
            
            self.database_url = (
                f"postgresql+psycopg://{user}:{encoded_password}"
                f"@{host}:{port}/{name}"
            )
    
    def get_url(self) -> str:
        """Get the database connection URL."""
        return self.database_url


class DatabaseManager:
    """
    Database manager for connection pooling and session management.
    
    This class provides:
    - Connection pooling using SQLAlchemy
    - Session management with context managers
    - Health check and verification
    - Schema creation and migration
    
    Example:
        ```python
        db = DatabaseManager()
        
        # Use context manager for automatic session cleanup
        with db.get_session() as session:
            commodities = session.query(Commodity).all()
        ```
    """
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        pool_size: int = 5,
        max_overflow: int = 10,
        echo: bool = False
    ):
        """
        Initialize database manager.
        
        Args:
            database_url: PostgreSQL connection URL (if None, uses env config)
            pool_size: Number of connections to maintain in pool
            max_overflow: Max number of connections beyond pool_size
            echo: If True, log all SQL statements (useful for debugging)
        """
        config = DatabaseConfig()
        self.database_url = database_url or config.get_url()
        
        # Create engine with connection pooling
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # Verify connections before using
            echo=echo
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )
        
        # Add connection pool logging
        self._setup_connection_logging()
        
        logger.info(
            f"Database manager initialized with pool_size={pool_size}, "
            f"max_overflow={max_overflow}"
        )
    
    def _setup_connection_logging(self):
        """Setup logging for connection pool events."""
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.debug("Database connection established")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            logger.debug("Connection checked out from pool")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_conn, connection_record):
            logger.debug("Connection returned to pool")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        
        Automatically handles:
        - Session creation
        - Commit on success
        - Rollback on error
        - Session cleanup
        
        Yields:
            Session: SQLAlchemy session
        
        Example:
            ```python
            with db.get_session() as session:
                commodity = session.query(Commodity).filter_by(symbol="WTI").first()
                print(commodity.name)
            ```
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session rolled back due to error: {e}")
            raise
        finally:
            session.close()
    
    def create_all_tables(self):
        """
        Create all database tables if they don't exist.
        
        Note: This does NOT create the TimescaleDB hypertable.
        Use init.sql for initial schema setup with TimescaleDB.
        """
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def drop_all_tables(self):
        """
        Drop all database tables.
        
        WARNING: This will delete all data. Use with caution!
        """
        try:
            Base.metadata.drop_all(self.engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
    def check_connection(self) -> bool:
        """
        Check if database connection is working.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection check: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"Database connection check: FAILED - {e}")
            return False
    
    def check_timescale_extension(self) -> bool:
        """
        Check if TimescaleDB extension is installed.
        
        Returns:
            bool: True if TimescaleDB is available, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT extname FROM pg_extension WHERE extname = 'timescaledb'")
                )
                has_timescale = result.fetchone() is not None
                
                if has_timescale:
                    logger.info("TimescaleDB extension: AVAILABLE")
                else:
                    logger.warning("TimescaleDB extension: NOT FOUND")
                
                return has_timescale
        except Exception as e:
            logger.error(f"Failed to check TimescaleDB extension: {e}")
            return False
    
    def get_pool_status(self) -> dict:
        """
        Get connection pool statistics.
        
        Returns:
            dict: Pool statistics (size, checked_in, checked_out, overflow)
        """
        pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow()
        }
    
    def close(self):
        """Close all database connections and dispose of the engine."""
        try:
            self.engine.dispose()
            logger.info("Database engine disposed, all connections closed")
        except Exception as e:
            logger.error(f"Failed to dispose engine: {e}")
            raise


# Global database manager instance (singleton pattern)
_db_manager: Optional[DatabaseManager] = None


def get_database_manager(
    database_url: Optional[str] = None,
    pool_size: int = 5,
    max_overflow: int = 10,
    echo: bool = False
) -> DatabaseManager:
    """
    Get or create the global database manager instance.
    
    Args:
        database_url: PostgreSQL connection URL (if None, uses env config)
        pool_size: Number of connections to maintain in pool
        max_overflow: Max number of connections beyond pool_size
        echo: If True, log all SQL statements
    
    Returns:
        DatabaseManager: Global database manager instance
    """
    global _db_manager
    
    if _db_manager is None:
        _db_manager = DatabaseManager(
            database_url=database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=echo
        )
    
    return _db_manager


def close_database_manager():
    """Close and dispose of the global database manager."""
    global _db_manager
    
    if _db_manager is not None:
        _db_manager.close()
        _db_manager = None


# Convenience function for getting a session
@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Convenience function to get a database session.
    
    This is a shortcut for get_database_manager().get_session()
    
    Yields:
        Session: SQLAlchemy session
    
    Example:
        ```python
        from database.utils import get_session
        
        with get_session() as session:
            commodities = session.query(Commodity).all()
        ```
    """
    db = get_database_manager()
    with db.get_session() as session:
        yield session



