"""
Direct Forecast Fix Validation Test

This test directly validates that the forecast endpoint returns varying values.
It uses existing database data and tests the API endpoint.

Run with: pytest tests/integration/test_forecast_fix_validation.py -v -s
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from api.main import app


class TestForecastFix:
    """Test that forecast endpoint returns varying values (the bug fix)."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_forecast_returns_varying_values(self, client):
        """CRITICAL TEST: Verify forecast values vary (not all same)."""
        print("\n" + "="*80)
        print("FORECAST VALUE VARIATION TEST (CRITICAL BUG FIX VALIDATION)")
        print("="*80)
        
        # Create forecast request
        request_data = {
            "commodity": "WTI",
            "horizon": 7,
            "start_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        print(f"Request: {request_data}")
        
        # Make API call
        response = client.post("/api/v1/forecast", json=request_data)
        
        print(f"Response status: {response.status_code}")
        
        # Check response
        if response.status_code != 200:
            print(f"ERROR: API returned {response.status_code}")
            print(f"Response: {response.text}")
            pytest.fail(f"Expected 200, got {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Validate structure
        assert "predictions" in data, "Response should have 'predictions'"
        assert len(data["predictions"]) == 7, f"Should have 7 predictions, got {len(data['predictions'])}"
        
        # Extract prices
        predictions = data["predictions"]
        prices = [p["price"] for p in predictions]
        
        print(f"\nForecast prices: {[round(p, 2) for p in prices]}")
        
        # CRITICAL CHECK: Are prices varying?
        unique_prices = len(set([round(p, 4) for p in prices]))  # Round to avoid float precision
        
        print(f"\nTotal predictions: {len(prices)}")
        print(f"Unique prices (rounded to 4 decimals): {unique_prices}")
        print(f"Min price: ${min(prices):.2f}")
        print(f"Max price: ${max(prices):.2f}")
        print(f"Price range: ${max(prices) - min(prices):.2f}")
        print(f"Price std dev: ${np.std(prices):.2f}")
        
        # Validate all prices are valid
        assert all(isinstance(p, (int, float)) for p in prices), "All prices should be numbers"
        assert all(p > 0 for p in prices), "All prices should be positive"
        assert all(np.isfinite(p) for p in prices), "All prices should be finite"
        
        # THE CRITICAL TEST: Prices must vary
        if unique_prices == 1:
            print("\n" + "="*80)
            print("FAIL: All forecast values are IDENTICAL!")
            print("="*80)
            print(f"All values: {prices[0]}")
            print("This indicates the forecast bug is STILL PRESENT!")
            print("The API is not properly passing data to models or extracting values.")
            pytest.fail(
                f"CRITICAL BUG: All forecast values are the same ({prices[0]}). "
                f"The fix did not work. Check API logs and model.predict() calls."
            )
        else:
            print("\n" + "="*80)
            print("SUCCESS: Forecast values are VARYING correctly!")
            print("="*80)
            print(f"Found {unique_prices} unique values out of {len(prices)} predictions")
            
            # Additional validation: prices should have reasonable variation
            price_range = max(prices) - min(prices)
            if price_range < 0.01:
                print(f"WARNING: Price range is very small (${price_range:.4f})")
                print("This might indicate the model is not working correctly")
            else:
                print(f"Price range is reasonable: ${price_range:.2f}")
        
        # Validate dates
        dates = [p["date"] for p in predictions]
        assert len(set(dates)) == 7, "Should have 7 unique dates"
        print(f"All dates are unique: {len(set(dates))} unique dates")
        
        return prices
    
    def test_multiple_forecasts_consistency(self, client):
        """Test multiple forecasts to ensure consistency."""
        print("\n" + "="*80)
        print("MULTIPLE FORECAST CONSISTENCY TEST")
        print("="*80)
        
        horizons = [1, 7, 14]
        results = {}
        
        for horizon in horizons:
            request_data = {
                "commodity": "WTI",
                "horizon": horizon,
                "start_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            response = client.post("/api/v1/forecast", json=request_data)
            assert response.status_code == 200, f"Failed for horizon {horizon}"
            
            data = response.json()
            predictions = data["predictions"]
            prices = [p["price"] for p in predictions]
            unique_count = len(set([round(p, 4) for p in prices]))
            
            results[horizon] = {
                'count': len(predictions),
                'unique_prices': unique_count,
                'prices': prices
            }
            
            print(f"\nHorizon {horizon} days:")
            print(f"  Predictions: {len(predictions)}")
            print(f"  Unique prices: {unique_count}")
            print(f"  Price range: ${min(prices):.2f} - ${max(prices):.2f}")
            
            # Each horizon should have varying values (except horizon=1 which only has 1 prediction)
            if horizon > 1:
                assert unique_count > 1, f"Horizon {horizon} should have varying values"
            else:
                # Horizon 1 only has 1 prediction, so it can't vary
                assert unique_count == 1, f"Horizon 1 should have exactly 1 prediction"
        
        print("\nAll horizons produce varying forecasts")
        return results
    
    def test_different_commodities(self, client):
        """Test forecast for different commodities."""
        print("\n" + "="*80)
        print("DIFFERENT COMMODITIES TEST")
        print("="*80)
        
        commodities = ["WTI", "BRENT", "NG"]
        results = {}
        
        for commodity in commodities:
            request_data = {
                "commodity": commodity,
                "horizon": 7,
                "start_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            response = client.post("/api/v1/forecast", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                predictions = data["predictions"]
                prices = [p["price"] for p in predictions]
                unique_count = len(set([round(p, 4) for p in prices]))
                
                results[commodity] = {
                    'unique_prices': unique_count,
                    'prices': prices
                }
                
                print(f"\n{commodity}:")
                print(f"  Unique prices: {unique_count}")
                print(f"  Price range: ${min(prices):.2f} - ${max(prices):.2f}")
                
                # Should have varying values
                assert unique_count > 1, f"{commodity} should have varying values"
            else:
                print(f"\n{commodity}: API returned {response.status_code} (may not have data)")
        
        return results


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])

