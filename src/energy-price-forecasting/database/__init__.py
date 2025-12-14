"""
Database package for Energy Price Forecasting System.

This package provides:
- ORM models (Commodity, DataSource, PriceData)
- Database utilities (connection management, session handling)
- Data operations (insert, retrieve, update)

Usage:
    ```python
    from database import get_session, Commodity, PriceData
    from database.operations import insert_price_data, get_price_data
    
    # Query data
    with get_session() as session:
        wti = session.query(Commodity).filter_by(symbol="WTI").first()
        print(wti.name)
    
    # Insert data
    import pandas as pd
    df = pd.DataFrame({"date": [...], "price": [...]})
    insert_price_data(df, commodity_symbol="WTI", source_name="EIA")
    ```
"""

from database.models import Base, Commodity, DataSource, PriceData
from database.utils import (
    DatabaseConfig,
    DatabaseManager,
    get_database_manager,
    close_database_manager,
    get_session,
)

__all__ = [
    # Models
    "Base",
    "Commodity",
    "DataSource",
    "PriceData",
    # Utils
    "DatabaseConfig",
    "DatabaseManager",
    "get_database_manager",
    "close_database_manager",
    "get_session",
]

