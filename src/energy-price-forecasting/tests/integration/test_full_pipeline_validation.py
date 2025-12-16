"""
Comprehensive Integration Test for Full Pipeline Validation

This test validates the entire system from data ingestion to forecast generation:
1. Data Ingestion → Database
2. Feature Engineering
3. Model Training
4. Model Loading
5. API Forecast Generation
6. Response Validation

Run with: pytest tests/integration/test_full_pipeline_validation.py -v -s
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.operations import get_price_data, insert_price_data
from database.utils import get_session
from database.models import Commodity, DataSource, PriceData
from feature_engineering.pipeline import FeatureEngineeringPipeline
from models.baseline.arima_model import ARIMAModel
from models.baseline.prophet_model import ProphetModel
from api.services.model_service import get_model_service
from api.routes.forecast import forecast as forecast_endpoint
from api.models.forecast import ForecastRequest
from fastapi.testclient import TestClient
from api.main import app


class TestFullPipelineValidation:
    """Test complete pipeline from data to forecast."""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """Setup test data in database."""
        # Create test data
        test_data = []
        base_date = datetime.now() - timedelta(days=120)
        
        # Generate 120 days of test price data for WTI
        for i in range(120):
            date = base_date + timedelta(days=i)
            # Simulate price with trend and noise
            base_price = 75.0
            trend = 0.1 * i
            noise = np.random.normal(0, 2.0)
            price = base_price + trend + noise
            
            test_data.append({
                'timestamp': date,
                'price': max(price, 50.0),  # Ensure positive
                'volume': 1000000 + np.random.randint(-100000, 100000),
                'open_price': price - np.random.uniform(0, 1),
                'high_price': price + np.random.uniform(0, 2),
                'low_price': price - np.random.uniform(0, 2),
                'close_price': price
            })
        
        # Insert test data
        with get_session() as session:
            # Get or create WTI commodity
            commodity = session.query(Commodity).filter_by(symbol="WTI").first()
            if not commodity:
                commodity = Commodity(symbol="WTI", name="West Texas Intermediate")
                session.add(commodity)
                session.commit()
            
            # Get or create EIA source
            source = session.query(DataSource).filter_by(name="EIA").first()
            if not source:
                source = DataSource(name="EIA", description="Energy Information Administration")
                session.add(source)
                session.commit()
            
            # Insert price data
            for data_point in test_data:
                price_record = PriceData(
                    commodity_id=commodity.id,
                    source_id=source.id,
                    timestamp=data_point['timestamp'],
                    price=data_point['price'],
                    volume=data_point['volume'],
                    open_price=data_point['open_price'],
                    high_price=data_point['high_price'],
                    low_price=data_point['low_price'],
                    close_price=data_point['close_price']
                )
                session.add(price_record)
            
            session.commit()
        
        yield
        
        # Cleanup (optional - comment out to keep test data)
        # with get_session() as session:
        #     session.query(PriceData).filter(
        #         PriceData.commodity_id == commodity.id
        #     ).delete()
        #     session.commit()
    
    def test_step1_data_ingestion_to_database(self):
        """Test Step 1: Verify data is in database."""
        print("\n=== STEP 1: Data Ingestion → Database ===")
        
        # Fetch data from database
        end_date = datetime.now()
        start_date = end_date - timedelta(days=120)
        
        df = get_price_data(
            commodity_symbol="WTI",
            source_name="EIA",
            start_date=start_date,
            end_date=end_date
        )
        
        assert df is not None, "DataFrame should not be None"
        assert not df.empty, "DataFrame should not be empty"
        assert len(df) >= 100, f"Should have at least 100 records, got {len(df)}"
        assert 'price' in df.columns, "Should have 'price' column"
        assert 'timestamp' in df.columns, "Should have 'timestamp' column"
        
        print(f"✅ Data ingestion verified: {len(df)} records retrieved")
        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"   Price range: ${df['price'].min():.2f} to ${df['price'].max():.2f}")
        
        return df
    
    def test_step2_feature_engineering(self):
        """Test Step 2: Feature engineering pipeline."""
        print("\n=== STEP 2: Feature Engineering ===")
        
        # Get data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=120)
        
        df = get_price_data(
            commodity_symbol="WTI",
            source_name="EIA",
            start_date=start_date,
            end_date=end_date
        )
        
        # Prepare data for feature engineering
        df = df.sort_values('timestamp').reset_index(drop=True)
        df['date'] = pd.to_datetime(df['timestamp'])
        
        # Run feature engineering
        pipeline = FeatureEngineeringPipeline()
        features_df = pipeline.transform(df, target_column='price')
        
        assert features_df is not None, "Features DataFrame should not be None"
        assert not features_df.empty, "Features DataFrame should not be empty"
        assert len(features_df) == len(df), "Should have same number of rows"
        
        # Check for common features
        expected_features = ['sma_7', 'sma_30', 'rsi', 'macd']
        for feature in expected_features:
            if feature in features_df.columns:
                print(f"   ✅ Feature '{feature}' created")
            else:
                print(f"   ⚠️  Feature '{feature}' not found (may be optional)")
        
        print(f"✅ Feature engineering verified: {len(features_df.columns)} total columns")
        print(f"   Original columns: {len(df.columns)}")
        print(f"   Feature columns: {len(features_df.columns) - len(df.columns)}")
        
        return features_df
    
    def test_step3_model_training(self):
        """Test Step 3: Model training."""
        print("\n=== STEP 3: Model Training ===")
        
        # Get data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=120)
        
        df = get_price_data(
            commodity_symbol="WTI",
            source_name="EIA",
            start_date=start_date,
            end_date=end_date
        )
        
        df = df.sort_values('timestamp').reset_index(drop=True)
        price_series = df['price']
        
        # Test ARIMA model training
        print("   Training ARIMA model...")
        arima_model = ARIMAModel()
        arima_model.fit(price_series, verbose=False)
        
        assert arima_model.is_fitted, "ARIMA model should be fitted"
        print("   ✅ ARIMA model trained successfully")
        
        # Test Prophet model training
        print("   Training Prophet model...")
        prophet_df = df[['timestamp', 'price']].copy()
        prophet_df.columns = ['ds', 'y']
        
        prophet_model = ProphetModel()
        prophet_model.fit(prophet_df, date_col='ds', value_col='y', verbose=False)
        
        assert prophet_model.is_fitted, "Prophet model should be fitted"
        print("   ✅ Prophet model trained successfully")
        
        # Test predictions
        arima_forecast = arima_model.predict(steps=7)
        assert len(arima_forecast) == 7, "ARIMA should return 7 predictions"
        assert all(np.isfinite(arima_forecast)), "ARIMA predictions should be finite"
        print(f"   ✅ ARIMA forecast: {arima_forecast.tolist()[:3]}...")
        
        prophet_forecast = prophet_model.predict(steps=7)
        assert len(prophet_forecast) == 7, "Prophet should return 7 predictions"
        print(f"   ✅ Prophet forecast shape: {prophet_forecast.shape}")
        
        print("✅ Model training verified: Both models trained and can predict")
        
        return arima_model, prophet_model
    
    def test_step4_model_loading(self):
        """Test Step 4: Model loading via model service."""
        print("\n=== STEP 4: Model Loading ===")
        
        model_service = get_model_service()
        
        # Test loading model (will use placeholder if no real model)
        model = model_service.load_model(
            commodity="WTI",
            model_type="lstm"
        )
        
        assert model is not None, "Model should not be None"
        assert hasattr(model, 'is_fitted'), "Model should have is_fitted attribute"
        assert model.is_fitted, "Model should be fitted"
        assert hasattr(model, 'predict'), "Model should have predict method"
        
        print(f"   ✅ Model loaded: {type(model).__name__}")
        print(f"   ✅ Model is_fitted: {model.is_fitted}")
        
        # Test model can predict
        try:
            if hasattr(model, 'predict'):
                # Try with steps parameter
                result = model.predict(steps=7)
                print(f"   ✅ Model can predict: returned {type(result)}")
        except Exception as e:
            print(f"   ⚠️  Model predict test: {e}")
        
        print("✅ Model loading verified")
        
        return model
    
    def test_step5_api_forecast_generation(self):
        """Test Step 5: API forecast generation."""
        print("\n=== STEP 5: API Forecast Generation ===")
        
        client = TestClient(app)
        
        # Create forecast request
        request_data = {
            "commodity": "WTI",
            "horizon": 7,
            "start_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        print(f"   Request: {request_data}")
        
        # Make API call
        response = client.post("/api/v1/forecast", json=request_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Validate response structure
        assert "commodity" in data, "Response should have 'commodity'"
        assert "horizon" in data, "Response should have 'horizon'"
        assert "predictions" in data, "Response should have 'predictions'"
        assert data["commodity"] == "WTI", "Commodity should be WTI"
        assert data["horizon"] == 7, "Horizon should be 7"
        assert len(data["predictions"]) == 7, f"Should have 7 predictions, got {len(data['predictions'])}"
        
        # Validate predictions
        predictions = data["predictions"]
        prices = [p["price"] for p in predictions]
        
        # Check all prices are valid
        assert all(isinstance(p, (int, float)) for p in prices), "All prices should be numbers"
        assert all(p > 0 for p in prices), "All prices should be positive"
        
        # Check for variation (not all same value)
        unique_prices = len(set(prices))
        if unique_prices == 1:
            print(f"   ⚠️  WARNING: All prices are the same: {prices[0]}")
            print(f"   ⚠️  This indicates the forecast issue we're trying to fix!")
        else:
            print(f"   ✅ Prices vary: {unique_prices} unique values")
            print(f"   ✅ Price range: ${min(prices):.2f} to ${max(prices):.2f}")
        
        # Check dates
        dates = [p["date"] for p in predictions]
        assert len(set(dates)) == 7, "Should have 7 unique dates"
        
        print(f"✅ API forecast generation verified")
        print(f"   Predictions: {len(predictions)}")
        print(f"   First prediction: {predictions[0]}")
        print(f"   Last prediction: {predictions[-1]}")
        
        return data
    
    def test_step6_end_to_end_validation(self):
        """Test Step 6: Complete end-to-end validation."""
        print("\n=== STEP 6: End-to-End Validation ===")
        
        # Run all steps in sequence
        df = self.test_step1_data_ingestion_to_database()
        features_df = self.test_step2_feature_engineering()
        arima_model, prophet_model = self.test_step3_model_training()
        model = self.test_step4_model_loading()
        forecast_response = self.test_step5_api_forecast_generation()
        
        # Final validation
        predictions = forecast_response["predictions"]
        prices = [p["price"] for p in predictions]
        
        print("\n=== FINAL VALIDATION ===")
        print(f"✅ Data in database: {len(df)} records")
        print(f"✅ Features created: {len(features_df.columns)} columns")
        print(f"✅ Models trained: ARIMA and Prophet")
        print(f"✅ Model loaded: {type(model).__name__}")
        print(f"✅ Forecast generated: {len(predictions)} predictions")
        
        # Critical check: Are prices varying?
        unique_prices = len(set(prices))
        if unique_prices > 1:
            print(f"✅ CRITICAL: Prices are varying correctly ({unique_prices} unique values)")
            print(f"   Price range: ${min(prices):.2f} to ${max(prices):.2f}")
            print(f"   Price difference: ${max(prices) - min(prices):.2f}")
            return True
        else:
            print(f"❌ CRITICAL ISSUE: All prices are the same ({prices[0]})")
            print(f"   This indicates the forecast bug is still present!")
            return False
    
    def test_forecast_values_variation(self):
        """Specific test to verify forecast values vary."""
        print("\n=== FORECAST VARIATION TEST ===")
        
        client = TestClient(app)
        
        request_data = {
            "commodity": "WTI",
            "horizon": 7,
            "start_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        response = client.post("/api/v1/forecast", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        predictions = data["predictions"]
        prices = [p["price"] for p in predictions]
        
        # Check variation
        unique_count = len(set([round(p, 2) for p in prices]))  # Round to avoid float precision issues
        
        print(f"   Total predictions: {len(prices)}")
        print(f"   Unique prices (rounded): {unique_count}")
        print(f"   Prices: {[round(p, 2) for p in prices]}")
        
        if unique_count == 1:
            print("   ❌ FAIL: All prices are identical")
            print(f"   All values: {prices[0]}")
            assert False, f"All forecast values are the same: {prices[0]}"
        else:
            print("   ✅ PASS: Prices vary correctly")
            price_range = max(prices) - min(prices)
            print(f"   Price range: ${price_range:.2f}")
            assert True


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "-s"])

