"""
API Routes for Energy Price Forecasting API.

This package contains all API route handlers.
"""

from api.routes import forecast, historical, models, backtest

__all__ = [
    "forecast",
    "historical",
    "models",
    "backtest",
]

