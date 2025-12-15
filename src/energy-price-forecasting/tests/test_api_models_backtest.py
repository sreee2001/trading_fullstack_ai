"""
Unit tests for backtest Pydantic models (Story 4.5.1).
"""

import pytest
from pydantic import ValidationError

from api.models.backtest import (
    BacktestRequest,
    BacktestResponse,
    BacktestMetrics,
    Trade
)


class TestBacktestRequest:
    """Test BacktestRequest model."""
    
    def test_valid_request(self):
        """Test valid backtest request."""
        request = BacktestRequest(
            model_id="WTI_LSTM:1",
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        
        assert request.model_id == "WTI_LSTM:1"
        assert request.start_date == "2025-01-01"
        assert request.end_date == "2025-01-31"
        assert request.initial_capital == 100000.0
        assert request.commission == 0.001
        assert request.slippage == 0.0005
    
    def test_custom_parameters(self):
        """Test backtest request with custom parameters."""
        request = BacktestRequest(
            model_id="BRENT_ARIMA:2",
            start_date="2025-01-01",
            end_date="2025-01-31",
            initial_capital=50000.0,
            commission=0.002,
            slippage=0.001,
            strategy_params={"threshold": 0.02, "strategy": "momentum"}
        )
        
        assert request.initial_capital == 50000.0
        assert request.commission == 0.002
        assert request.slippage == 0.001
        assert request.strategy_params["threshold"] == 0.02
    
    def test_invalid_date_format(self):
        """Test invalid date format."""
        with pytest.raises(ValidationError):
            BacktestRequest(
                model_id="WTI_LSTM:1",
                start_date="01-01-2025",
                end_date="2025-01-31"
            )
    
    def test_end_date_before_start_date(self):
        """Test that end_date must be after start_date."""
        with pytest.raises(ValidationError):
            BacktestRequest(
                model_id="WTI_LSTM:1",
                start_date="2025-01-31",
                end_date="2025-01-01"
            )
    
    def test_initial_capital_must_be_positive(self):
        """Test that initial_capital must be positive."""
        with pytest.raises(ValidationError):
            BacktestRequest(
                model_id="WTI_LSTM:1",
                start_date="2025-01-01",
                end_date="2025-01-31",
                initial_capital=-1000.0
            )
    
    def test_commission_range(self):
        """Test commission validation (0-0.1)."""
        with pytest.raises(ValidationError):
            BacktestRequest(
                model_id="WTI_LSTM:1",
                start_date="2025-01-01",
                end_date="2025-01-31",
                commission=0.2  # Too high
            )


class TestTrade:
    """Test Trade model."""
    
    def test_valid_trade(self):
        """Test valid trade."""
        trade = Trade(
            entry_idx=0,
            exit_idx=1,
            entry_price=75.0,
            exit_price=76.0,
            position=1,
            pnl=0.0133,
            pnl_dollars=1330.0,
            capital_after=101330.0
        )
        
        assert trade.entry_price == 75.0
        assert trade.exit_price == 76.0
        assert trade.position == 1
        assert trade.pnl == 0.0133


class TestBacktestMetrics:
    """Test BacktestMetrics model."""
    
    def test_valid_metrics(self):
        """Test valid backtest metrics."""
        metrics = BacktestMetrics(
            total_trades=10,
            win_rate=60.0,
            total_return=0.15,
            sharpe_ratio=1.2,
            final_capital=115000.0,
            initial_capital=100000.0,
            cumulative_pnl=15000.0
        )
        
        assert metrics.total_trades == 10
        assert metrics.win_rate == 60.0
        assert metrics.total_return == 0.15
        assert metrics.cumulative_pnl == 15000.0
    
    def test_optional_fields(self):
        """Test that optional fields can be omitted."""
        metrics = BacktestMetrics(
            total_trades=5,
            total_return=0.05,
            final_capital=105000.0,
            initial_capital=100000.0,
            cumulative_pnl=5000.0
        )
        
        assert metrics.sharpe_ratio is None
        assert metrics.win_rate is None


class TestBacktestResponse:
    """Test BacktestResponse model."""
    
    def test_valid_response(self):
        """Test valid backtest response."""
        metrics = BacktestMetrics(
            total_trades=10,
            win_rate=60.0,
            total_return=0.15,
            final_capital=115000.0,
            initial_capital=100000.0,
            cumulative_pnl=15000.0
        )
        
        trades = [
            Trade(
                entry_idx=0,
                exit_idx=1,
                entry_price=75.0,
                exit_price=76.0,
                position=1,
                pnl=0.0133
            )
        ]
        
        response = BacktestResponse(
            model_id="WTI_LSTM:1",
            start_date="2025-01-01",
            end_date="2025-01-31",
            metrics=metrics,
            num_trades=10,
            trades=trades
        )
        
        assert response.model_id == "WTI_LSTM:1"
        assert len(response.trades) == 1
        assert response.num_trades == 10
    
    def test_response_without_trades(self):
        """Test response without trades list."""
        metrics = BacktestMetrics(
            total_trades=0,
            total_return=0.0,
            final_capital=100000.0,
            initial_capital=100000.0,
            cumulative_pnl=0.0
        )
        
        response = BacktestResponse(
            model_id="WTI_LSTM:1",
            start_date="2025-01-01",
            end_date="2025-01-31",
            metrics=metrics,
            num_trades=0
        )
        
        assert response.num_trades == 0
        assert len(response.trades) == 0

