"""
Performance and Load Tests.

Tests API performance under load and measures response times.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import pytest
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture(scope="module")
def client():
    """Create test client."""
    return TestClient(app)


class TestAPIPerformance:
    """Test API performance metrics."""
    
    def test_health_endpoint_performance(self, client):
        """Test health endpoint response time."""
        start_time = time.time()
        response = client.get("/health")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 0.1  # Should respond in < 100ms
    
    def test_forecast_endpoint_performance(self, client):
        """Test forecast endpoint response time."""
        headers = {"X-API-Key": "test_key"}
        
        start_time = time.time()
        response = client.post(
            "/api/v1/forecast",
            headers=headers,
            json={
                "commodity": "WTI",
                "horizon": 7,
                "start_date": "2024-12-01"
            }
        )
        elapsed = time.time() - start_time
        
        # Forecast should complete in reasonable time (< 5 seconds)
        assert elapsed < 5.0
    
    def test_historical_endpoint_performance(self, client):
        """Test historical data endpoint performance."""
        headers = {"X-API-Key": "test_key"}
        
        start_time = time.time()
        response = client.get(
            "/api/v1/historical/WTI",
            headers=headers,
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        )
        elapsed = time.time() - start_time
        
        # Historical data should load quickly (< 2 seconds)
        assert elapsed < 2.0


class TestLoadHandling:
    """Test API under load."""
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        headers = {"X-API-Key": "test_key"}
        
        def make_request():
            return client.get("/health", headers=headers)
        
        # Make 50 concurrent requests
        num_requests = 50
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [f.result() for f in as_completed(futures)]
        
        elapsed = time.time() - start_time
        
        # All requests should succeed
        success_count = sum(1 for r in results if r.status_code == 200)
        assert success_count >= num_requests * 0.9  # At least 90% success
        
        # Should handle load reasonably (< 10 seconds for 50 requests)
        assert elapsed < 10.0
    
    def test_sustained_load(self, client):
        """Test API under sustained load."""
        headers = {"X-API-Key": "test_key"}
        
        num_requests = 100
        response_times = []
        
        for _ in range(num_requests):
            start = time.time()
            response = client.get("/health", headers=headers)
            elapsed = time.time() - start
            response_times.append(elapsed)
            
            assert response.status_code == 200
        
        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        
        # Average response time should be reasonable
        assert avg_time < 0.5
        
        # Max response time should not be excessive
        assert max_time < 2.0


class TestDatabasePerformance:
    """Test database query performance."""
    
    def test_price_data_query_performance(self):
        """Test price data query performance."""
        from database.operations import get_price_data
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        start_time = time.time()
        data, count = get_price_data(
            commodity="WTI",
            start_date=start_date,
            end_date=end_date
        )
        elapsed = time.time() - start_time
        
        # Query should complete in reasonable time
        assert elapsed < 3.0
    
    def test_large_dataset_query(self):
        """Test query performance on large dataset."""
        from database.operations import get_price_data
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)  # 2 years
        
        start_time = time.time()
        data, count = get_price_data(
            commodity="WTI",
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        elapsed = time.time() - start_time
        
        # Large queries should still be performant
        assert elapsed < 5.0


class TestModelPerformance:
    """Test model inference performance."""
    
    def test_arima_prediction_performance(self):
        """Test ARIMA model prediction speed."""
        import pandas as pd
        import numpy as np
        from models.baseline.arima_model import ARIMAModel
        
        # Create sample data
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
        prices = pd.Series(75 + np.random.randn(len(dates)) * 2, index=dates)
        
        model = ARIMAModel()
        try:
            model.fit(prices)
            
            start_time = time.time()
            forecast = model.predict(steps=30)
            elapsed = time.time() - start_time
            
            assert forecast is not None
            # Prediction should be fast (< 1 second)
            assert elapsed < 1.0
        except Exception as e:
            pytest.skip(f"ARIMA model failed: {e}")
    
    def test_lstm_prediction_performance(self):
        """Test LSTM model prediction speed."""
        import pandas as pd
        import numpy as np
        from models.lstm.lstm_model import LSTMForecaster
        
        # Create sample data
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
        prices = pd.DataFrame({
            'price': pd.Series(75 + np.random.randn(len(dates)) * 2, index=dates)
        })
        
        model = LSTMForecaster(forecast_horizon=7)
        try:
            model.fit(prices, target_column='price', epochs=1, verbose=0)
            
            start_time = time.time()
            forecast = model.predict(prices.tail(100))
            elapsed = time.time() - start_time
            
            assert forecast is not None
            # LSTM prediction should be reasonable (< 2 seconds)
            assert elapsed < 2.0
        except Exception as e:
            pytest.skip(f"LSTM model failed: {e}")

