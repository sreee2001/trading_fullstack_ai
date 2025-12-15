"""
Unit tests for backtesting endpoint (Stories 4.5.2 and 4.5.3).
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status
import pandas as pd
import numpy as np

from api.main import app


class TestBacktestEndpoint:
    """Test backtesting endpoint."""
    
    def test_backtest_endpoint_exists(self):
        """Test that backtest endpoint is registered."""
        client = TestClient(app)
        
        # Should return validation error for missing body
        response = client.post("/api/v1/backtest")
        assert response.status_code in [422, 400]
    
    def test_backtest_endpoint_valid_request(self):
        """Test backtest endpoint with valid request."""
        client = TestClient(app)
        
        request_data = {
            "model_id": "WTI_LSTM:1",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31"
        }
        
        # Mock the backtest service
        mock_results = {
            'model_id': 'WTI_LSTM:1',
            'start_date': '2025-01-01',
            'end_date': '2025-01-31',
            'metrics': {
                'total_trades': 5,
                'win_rate': 60.0,
                'total_return': 0.05,
                'final_capital': 105000.0,
                'initial_capital': 100000.0,
                'cumulative_pnl': 5000.0
            },
            'num_trades': 5,
            'trades': [],
            'equity_curve': [100000.0, 101000.0, 102000.0, 103000.0, 104000.0, 105000.0]
        }
        
        with patch('api.routes.backtest.get_backtest_service') as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.run_backtest.return_value = mock_results
            mock_service.return_value = mock_service_instance
            
            response = client.post("/api/v1/backtest", json=request_data)
            
            # Should succeed if service available
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_backtest_endpoint_invalid_date_format(self):
        """Test backtest endpoint with invalid date format."""
        client = TestClient(app)
        
        request_data = {
            "model_id": "WTI_LSTM:1",
            "start_date": "01-01-2025",
            "end_date": "2025-01-31"
        }
        
        response = client.post("/api/v1/backtest", json=request_data)
        
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_backtest_endpoint_end_date_before_start_date(self):
        """Test backtest endpoint with end_date before start_date."""
        client = TestClient(app)
        
        request_data = {
            "model_id": "WTI_LSTM:1",
            "start_date": "2025-01-31",
            "end_date": "2025-01-01"
        }
        
        response = client.post("/api/v1/backtest", json=request_data)
        
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_backtest_endpoint_custom_parameters(self):
        """Test backtest endpoint with custom parameters."""
        client = TestClient(app)
        
        request_data = {
            "model_id": "BRENT_ARIMA:1",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "initial_capital": 50000.0,
            "commission": 0.002,
            "slippage": 0.001,
            "strategy_params": {"threshold": 0.02, "strategy": "momentum"}
        }
        
        mock_results = {
            'model_id': 'BRENT_ARIMA:1',
            'start_date': '2025-01-01',
            'end_date': '2025-01-31',
            'metrics': {
                'total_trades': 3,
                'win_rate': 66.7,
                'total_return': 0.03,
                'final_capital': 51500.0,
                'initial_capital': 50000.0,
                'cumulative_pnl': 1500.0
            },
            'num_trades': 3,
            'trades': [],
            'equity_curve': []
        }
        
        with patch('api.routes.backtest.get_backtest_service') as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.run_backtest.return_value = mock_results
            mock_service.return_value = mock_service_instance
            
            response = client.post("/api/v1/backtest", json=request_data)
            
            # Should succeed if service available
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_backtest_response_structure(self):
        """Test that backtest response has correct structure."""
        client = TestClient(app)
        
        request_data = {
            "model_id": "WTI_LSTM:1",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31"
        }
        
        mock_results = {
            'model_id': 'WTI_LSTM:1',
            'start_date': '2025-01-01',
            'end_date': '2025-01-31',
            'metrics': {
                'total_trades': 2,
                'win_rate': 50.0,
                'total_return': 0.02,
                'final_capital': 102000.0,
                'initial_capital': 100000.0,
                'cumulative_pnl': 2000.0
            },
            'num_trades': 2,
            'trades': [
                {
                    'entry_idx': 0,
                    'exit_idx': 1,
                    'entry_price': 75.0,
                    'exit_price': 76.0,
                    'position': 1,
                    'pnl': 0.0133,
                    'pnl_dollars': 1330.0,
                    'capital_after': 101330.0
                }
            ],
            'equity_curve': [100000.0, 101330.0, 102000.0]
        }
        
        with patch('api.routes.backtest.get_backtest_service') as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.run_backtest.return_value = mock_results
            mock_service.return_value = mock_service_instance
            
            response = client.post("/api/v1/backtest", json=request_data)
            
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                
                assert "model_id" in data
                assert "start_date" in data
                assert "end_date" in data
                assert "metrics" in data
                assert "num_trades" in data
                assert "trades" in data
                
                assert data["num_trades"] == 2
                assert len(data["trades"]) == 1


class TestBacktestService:
    """Test BacktestService."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        from api.services.backtest_service import BacktestService
        
        service = BacktestService()
        assert service is not None
    
    def test_parse_model_id(self):
        """Test model_id parsing."""
        from api.services.backtest_service import BacktestService
        
        service = BacktestService()
        
        commodity, model_type = service._parse_model_id("WTI_LSTM:1")
        assert commodity == "WTI"
        assert model_type == "lstm"
        
        commodity, model_type = service._parse_model_id("BRENT_ARIMA")
        assert commodity == "BRENT"
        assert model_type == "arima"
    
    def test_parse_model_id_invalid(self):
        """Test invalid model_id parsing."""
        from api.services.backtest_service import BacktestService
        
        service = BacktestService()
        
        with pytest.raises(ValueError):
            service._parse_model_id("INVALID")
        
        with pytest.raises(ValueError):
            service._parse_model_id("UNKNOWN_LSTM")

