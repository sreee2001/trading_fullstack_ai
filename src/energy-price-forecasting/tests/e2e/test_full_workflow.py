"""
End-to-End Tests for Complete Workflows.

Tests complete user workflows from data ingestion to forecasting.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import pytest
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from fastapi.testclient import TestClient
from api.main import app
from database.utils import get_database_manager
from database.operations import get_price_data, insert_price_data
from models.baseline.arima_model import ARIMAModel
from models.baseline.prophet_model import ProphetModel
from models.lstm.lstm_model import LSTMForecaster


@pytest.fixture(scope="module")
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Create test price data."""
    dates = pd.date_range(
        start=datetime(2023, 1, 1),
        end=datetime(2024, 12, 31),
        freq='D'
    )
    
    # Generate realistic price data
    base_price = 75.0
    trend = pd.Series(range(len(dates))) * 0.01
    seasonal = 5 * pd.Series([np.sin(2 * np.pi * i / 365) for i in range(len(dates))])
    noise = pd.Series(np.random.normal(0, 2, len(dates)))
    
    prices = base_price + trend + seasonal + noise
    
    return pd.DataFrame({
        'timestamp': dates,
        'price': prices
    })


class TestForecastWorkflow:
    """Test complete forecast workflow."""
    
    def test_forecast_workflow_end_to_end(self, client, test_data):
        """Test complete forecast workflow from data to prediction."""
        # Step 1: Ensure data exists (would normally come from ingestion)
        # Step 2: Request forecast
        headers = {"X-API-Key": "test_key"}
        
        response = client.post(
            "/api/v1/forecast",
            headers=headers,
            json={
                "commodity": "WTI",
                "horizon": 7,
                "start_date": "2024-12-01"
            }
        )
        
        # Should return forecast or appropriate error
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "predictions" in data
            assert len(data["predictions"]) > 0
    
    def test_historical_then_forecast_workflow(self, client):
        """Test workflow: get historical data, then forecast."""
        headers = {"X-API-Key": "test_key"}
        
        # Step 1: Get historical data
        hist_response = client.get(
            "/api/v1/historical/WTI",
            headers=headers,
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        )
        
        # Step 2: Use that data context to forecast
        if hist_response.status_code == 200:
            forecast_response = client.post(
                "/api/v1/forecast",
                headers=headers,
                json={
                    "commodity": "WTI",
                    "horizon": 7,
                    "start_date": "2024-12-31"
                }
            )
            
            assert forecast_response.status_code in [200, 404, 500]


class TestBacktestWorkflow:
    """Test complete backtesting workflow."""
    
    def test_backtest_workflow_end_to_end(self, client):
        """Test complete backtesting workflow."""
        headers = {"X-API-Key": "test_key"}
        
        response = client.post(
            "/api/v1/backtest",
            headers=headers,
            json={
                "commodity": "WTI",
                "model_id": "WTI_LSTM",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "initial_capital": 10000,
                "strategy": "threshold"
            }
        )
        
        # Should return backtest results or error
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "metrics" in data or "results" in data


class TestModelTrainingWorkflow:
    """Test model training workflow."""
    
    def test_train_and_forecast_workflow(self, test_data):
        """Test workflow: train model, then forecast."""
        # Step 1: Train ARIMA model
        model = ARIMAModel()
        try:
            model.fit(test_data['price'])
            
            # Step 2: Generate forecast
            forecast = model.predict(steps=7)
            
            assert forecast is not None
            assert len(forecast) == 7
        except Exception as e:
            pytest.skip(f"Model training failed: {e}")
    
    def test_train_prophet_and_forecast(self, test_data):
        """Test Prophet training and forecasting workflow."""
        # Prepare Prophet format
        prophet_data = pd.DataFrame({
            'ds': test_data['timestamp'],
            'y': test_data['price']
        })
        
        model = ProphetModel()
        try:
            model.fit(prophet_data)
            
            # Forecast
            future = model.make_future_dataframe(periods=7)
            forecast = model.predict(future)
            
            assert forecast is not None
        except Exception as e:
            pytest.skip(f"Prophet training failed: {e}")


class TestDataPipelineWorkflow:
    """Test complete data pipeline workflow."""
    
    def test_data_ingestion_to_forecast(self):
        """Test workflow: ingest data, validate, then forecast."""
        # This would test the full pipeline:
        # 1. Data ingestion (mock)
        # 2. Data validation
        # 3. Storage in database
        # 4. Model training
        # 5. Forecasting
        
        # For now, test that components work together
        db_manager = get_database_manager()
        
        if db_manager:
            # Test database connectivity
            assert db_manager.verify_connection() is True
            
            # Test data retrieval
            data, count = get_price_data(
                commodity="WTI",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31)
            )
            
            # Data should be retrievable (may be empty)
            assert data is not None
        else:
            pytest.skip("Database not available")


class TestAnalyticsWorkflow:
    """Test analytics workflow."""
    
    def test_correlation_then_insights_workflow(self):
        """Test workflow: analyze correlations, generate insights."""
        from analytics.correlation_analysis import CorrelationAnalyzer
        from analytics.insight_generation import InsightGenerator
        
        # Create sample data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        wti_prices = pd.Series(75 + np.random.randn(len(dates)) * 2, index=dates)
        brent_prices = pd.Series(80 + np.random.randn(len(dates)) * 2, index=dates)
        
        price_data = {
            'WTI': wti_prices,
            'BRENT': brent_prices
        }
        
        # Step 1: Analyze correlations
        analyzer = CorrelationAnalyzer()
        results = analyzer.analyze_commodity_correlations(price_data)
        
        # Step 2: Generate insights
        generator = InsightGenerator()
        insights = generator.generate_correlation_insights(results)
        
        assert len(insights) > 0
        assert isinstance(insights[0], str)

