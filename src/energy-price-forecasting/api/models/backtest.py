"""
Pydantic models for backtesting endpoints.

This module defines the data models for running backtests via the API.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Dict, Any, Optional, List
from datetime import date


class BacktestRequest(BaseModel):
    """
    Pydantic model for a backtest request.
    """
    model_id: str = Field(
        ...,
        description="Model identifier (format: 'model_name:version' or 'commodity_modeltype')"
    )
    start_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Start date for backtest period (YYYY-MM-DD)"
    )
    end_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="End date for backtest period (YYYY-MM-DD)"
    )
    initial_capital: float = Field(
        default=100000.0,
        gt=0,
        description="Initial capital for backtesting (default: 100000)"
    )
    commission: float = Field(
        default=0.001,
        ge=0,
        le=0.1,
        description="Commission per trade as fraction (default: 0.001 = 0.1%)"
    )
    slippage: float = Field(
        default=0.0005,
        ge=0,
        le=0.1,
        description="Slippage per trade as fraction (default: 0.0005 = 0.05%)"
    )
    strategy_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Strategy parameters (e.g., {'threshold': 0.02, 'strategy': 'momentum'})"
    )

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format."""
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: str, info) -> str:
        """Validate that end_date is after start_date."""
        if "start_date" in info.data:
            start_date = date.fromisoformat(info.data["start_date"])
            end_date = date.fromisoformat(v)
            if end_date < start_date:
                raise ValueError("end_date must be after or equal to start_date")
        return v

    def get_start_date_as_date(self) -> date:
        """Convert the start_date string to a datetime.date object."""
        return date.fromisoformat(self.start_date)

    def get_end_date_as_date(self) -> date:
        """Convert the end_date string to a datetime.date object."""
        return date.fromisoformat(self.end_date)


class Trade(BaseModel):
    """
    Pydantic model for a single trade.
    """
    entry_idx: int = Field(..., description="Index of entry")
    exit_idx: int = Field(..., description="Index of exit")
    entry_price: float = Field(..., gt=0, description="Entry price")
    exit_price: float = Field(..., gt=0, description="Exit price")
    position: int = Field(..., description="Position type (1 = long, -1 = short)")
    pnl: Optional[float] = Field(None, description="Profit/Loss as fraction")
    pnl_dollars: Optional[float] = Field(None, description="Profit/Loss in dollars")
    capital_after: Optional[float] = Field(None, description="Capital after trade")
    timestamp: Optional[str] = Field(None, description="Trade timestamp")


class BacktestMetrics(BaseModel):
    """
    Pydantic model for backtest performance metrics.
    """
    total_trades: int = Field(..., ge=0, description="Total number of trades")
    win_rate: Optional[float] = Field(None, ge=0, le=100, description="Win rate (%)")
    total_return: float = Field(..., description="Total return as fraction")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    sortino_ratio: Optional[float] = Field(None, description="Sortino ratio")
    max_drawdown: Optional[float] = Field(None, le=0, description="Maximum drawdown")
    final_capital: float = Field(..., gt=0, description="Final capital")
    initial_capital: float = Field(..., gt=0, description="Initial capital")
    cumulative_pnl: float = Field(..., description="Cumulative P&L")
    rmse: Optional[float] = Field(None, ge=0, description="Root Mean Squared Error")
    mae: Optional[float] = Field(None, ge=0, description="Mean Absolute Error")
    mape: Optional[float] = Field(None, ge=0, description="Mean Absolute Percentage Error (%)")


class BacktestResponse(BaseModel):
    """
    Pydantic model for a backtest response.
    """
    model_id: str = Field(..., description="Model identifier")
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Start date")
    end_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="End date")
    metrics: BacktestMetrics = Field(..., description="Backtest performance metrics")
    num_trades: int = Field(..., ge=0, description="Number of trades executed")
    trades: List[Trade] = Field(default_factory=list, description="List of trades")
    equity_curve: Optional[List[float]] = Field(None, description="Equity curve over time")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "model_id": "WTI_LSTM:1",
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
                "metrics": {
                    "total_trades": 10,
                    "win_rate": 60.0,
                    "total_return": 0.15,
                    "sharpe_ratio": 1.2,
                    "final_capital": 115000.0,
                    "initial_capital": 100000.0,
                    "cumulative_pnl": 15000.0
                },
                "num_trades": 10,
                "trades": []
            }
        }
    )

