"""
System Validation Script

This script validates that all components of the system are working correctly.
Run this to diagnose issues and verify the system is functioning.

Usage:
    python validate_system.py
    python validate_system.py --component data
    python validate_system.py --component models
    python validate_system.py --component api
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import traceback

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Fix Windows encoding
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Print formatted header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_success(text):
    """Print success message."""
    try:
        print(f"{GREEN}[OK] {text}{RESET}")
    except UnicodeEncodeError:
        print(f"[OK] {text}")


def print_error(text):
    """Print error message."""
    try:
        print(f"{RED}[FAIL] {text}{RESET}")
    except UnicodeEncodeError:
        print(f"[FAIL] {text}")


def print_warning(text):
    """Print warning message."""
    try:
        print(f"{YELLOW}[WARN] {text}{RESET}")
    except UnicodeEncodeError:
        print(f"[WARN] {text}")


def validate_database():
    """Validate database connection and data."""
    print_header("VALIDATING DATABASE")
    
    try:
        from database.utils import get_session
        from database.operations import get_price_data
        from database.models import Commodity, DataSource
        
        # Test connection
        with get_session() as session:
            commodities = session.query(Commodity).all()
            print_success(f"Database connection: OK")
            print(f"   Found {len(commodities)} commodities")
            
            for comm in commodities:
                print(f"   - {comm.symbol}: {comm.name}")
        
        # Test data retrieval
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        for commodity in ["WTI", "BRENT", "NG"]:
            try:
                df = get_price_data(
                    commodity_symbol=commodity,
                    source_name="EIA",
                    start_date=start_date,
                    end_date=end_date
                )
                
                if df is not None and not df.empty:
                    print_success(f"{commodity} data: {len(df)} records")
                    print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
                    print(f"   Price range: ${df['price'].min():.2f} to ${df['price'].max():.2f}")
                else:
                    print_warning(f"{commodity} data: No records found")
            except Exception as e:
                print_error(f"{commodity} data retrieval failed: {e}")
        
        return True
        
    except Exception as e:
        print_error(f"Database validation failed: {e}")
        traceback.print_exc()
        return False


def validate_models():
    """Validate model training and loading."""
    print_header("VALIDATING MODELS")
    
    try:
        from database.operations import get_price_data
        from models.baseline.arima_model import ARIMAModel
        from models.baseline.prophet_model import ProphetModel
        from api.services.model_service import get_model_service
        
        # Get data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)
        
        df = get_price_data(
            commodity_symbol="WTI",
            source_name="EIA",
            start_date=start_date,
            end_date=end_date
        )
        
        if df is None or df.empty:
            print_warning("No data available for model testing")
            return False
        
        print_success(f"Test data: {len(df)} records")
        
        # Test ARIMA
        try:
            print("\nTesting ARIMA model...")
            arima = ARIMAModel()
            arima.fit(df['price'], verbose=False)
            assert arima.is_fitted, "ARIMA should be fitted"
            
            forecast = arima.predict(steps=7)
            assert len(forecast) == 7, "Should return 7 predictions"
            
            unique_values = len(set([round(f, 2) for f in forecast]))
            print_success(f"ARIMA: Trained and predicting")
            print(f"   Forecast: {forecast.tolist()[:3]}...")
            print(f"   Unique values: {unique_values}/7")
            
            if unique_values == 1:
                print_warning("ARIMA: All forecast values are identical")
        except Exception as e:
            print_error(f"ARIMA model failed: {e}")
            traceback.print_exc()
        
        # Test Prophet
        try:
            print("\nTesting Prophet model...")
            prophet_df = df[['timestamp', 'price']].copy()
            prophet_df.columns = ['ds', 'y']
            
            prophet = ProphetModel()
            prophet.fit(prophet_df, date_col='ds', value_col='y', verbose=False)
            assert prophet.is_fitted, "Prophet should be fitted"
            
            forecast = prophet.predict(steps=7)
            print_success(f"Prophet: Trained and predicting")
            print(f"   Forecast shape: {forecast.shape}")
        except Exception as e:
            print_error(f"Prophet model failed: {e}")
            traceback.print_exc()
        
        # Test model service
        try:
            print("\nTesting model service...")
            service = get_model_service()
            model = service.load_model("WTI", "lstm")
            
            assert model is not None, "Model should not be None"
            assert hasattr(model, 'is_fitted'), "Model should have is_fitted"
            assert model.is_fitted, "Model should be fitted"
            
            print_success(f"Model service: Model loaded")
            print(f"   Model type: {type(model).__name__}")
            print(f"   Is fitted: {model.is_fitted}")
        except Exception as e:
            print_error(f"Model service failed: {e}")
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print_error(f"Model validation failed: {e}")
        traceback.print_exc()
        return False


def validate_api():
    """Validate API endpoints."""
    print_header("VALIDATING API")
    
    try:
        from fastapi.testclient import TestClient
        from api.main import app
        
        client = TestClient(app)
        
        # Test health endpoint
        try:
            response = client.get("/health")
            if response.status_code == 200:
                print_success("Health endpoint: OK")
            else:
                print_warning(f"Health endpoint: Status {response.status_code}")
        except Exception as e:
            print_error(f"Health endpoint failed: {e}")
        
        # Test forecast endpoint
        try:
            print("\nTesting forecast endpoint...")
            request_data = {
                "commodity": "WTI",
                "horizon": 7,
                "start_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            response = client.post("/api/v1/forecast", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                predictions = data.get("predictions", [])
                prices = [p["price"] for p in predictions]
                
                print_success("Forecast endpoint: OK")
                print(f"   Predictions: {len(predictions)}")
                print(f"   Prices: {[round(p, 2) for p in prices]}")
                
                # Check variation
                unique_prices = len(set([round(p, 2) for p in prices]))
                if unique_prices == 1:
                    print_error(f"CRITICAL: All prices are identical: {prices[0]}")
                    print_error("This is the bug we're trying to fix!")
                    return False
                else:
                    print_success(f"Prices vary: {unique_prices} unique values")
                    print(f"   Range: ${min(prices):.2f} to ${max(prices):.2f}")
                    return True
            else:
                print_error(f"Forecast endpoint failed: Status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Forecast endpoint failed: {e}")
            traceback.print_exc()
            return False
        
    except Exception as e:
        print_error(f"API validation failed: {e}")
        traceback.print_exc()
        return False


def validate_full_pipeline():
    """Validate complete pipeline."""
    print_header("VALIDATING FULL PIPELINE")
    
    results = {
        "database": False,
        "models": False,
        "api": False
    }
    
    results["database"] = validate_database()
    results["models"] = validate_models()
    results["api"] = validate_api()
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    for component, passed in results.items():
        if passed:
            print_success(f"{component.upper()}: PASSED")
        else:
            print_error(f"{component.upper()}: FAILED")
    
    all_passed = all(results.values())
    
    if all_passed:
        print_success("\n🎉 ALL COMPONENTS VALIDATED SUCCESSFULLY!")
    else:
        print_error("\n❌ SOME COMPONENTS FAILED VALIDATION")
        print("   Check the errors above and fix issues.")
    
    return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate system components")
    parser.add_argument(
        "--component",
        choices=["database", "models", "api", "all"],
        default="all",
        help="Component to validate"
    )
    
    args = parser.parse_args()
    
    if args.component == "all":
        success = validate_full_pipeline()
    elif args.component == "database":
        success = validate_database()
    elif args.component == "models":
        success = validate_models()
    elif args.component == "api":
        success = validate_api()
    else:
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

