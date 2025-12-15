"""
Real Data Validation Test Script.

Tests the data validation framework with real data from:
- EIA API (WTI Crude Oil)
- FRED API (WTI, Brent, Natural Gas)
- Yahoo Finance (CL=F, BZ=F, NG=F)

Author: AI Assistant
Date: December 14, 2025
"""

import sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_validation import DataValidator
from data_ingestion.eia_client import EIAAPIClient
from data_ingestion.fred_client import FREDAPIClient
from data_ingestion.yahoo_finance_client import YahooFinanceClient


def test_eia_data_validation(validator):
    """Test validation with EIA data."""
    print("\n" + "="*80)
    print("TEST 1: EIA API DATA VALIDATION")
    print("="*80)
    
    try:
        client = EIAAPIClient()
        df = client.fetch_wti_prices(start_date='2024-01-01', end_date='2024-01-31')
        
        if df.empty:
            print("No data from EIA. Skipping...")
            return None
        
        # Prepare data for validation
        df = df.rename(columns={'date': 'timestamp'})
        df['commodity'] = 'WTI_CRUDE'
        df['source'] = 'EIA'
        
        print(f"Fetched {len(df)} records from EIA")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")
        
        # Run validations
        print("\nRunning validations...")
        
        schema_result = validator.validate_schema(df)
        print(f"  Schema: {schema_result['schema_compliance_score']}% compliant")
        
        completeness_result = validator.check_completeness(df, exclude_weekends=True)
        print(f"  Completeness: {completeness_result['completeness_score']}%")
        print(f"  Gaps: {completeness_result['gap_count']}")
        
        df_with_outliers = validator.detect_outliers(df, column='price')
        outlier_count = df_with_outliers['outlier_any'].sum()
        print(f"  Outliers: {outlier_count} ({(outlier_count/len(df)*100):.2f}%)")
        
        # Generate quality report
        validation_results = {
            'schema': schema_result,
            'completeness': completeness_result,
            'consistency': {'consistency_score': 100.0}  # Single source
        }
        
        report = validator.generate_quality_report(df_with_outliers, validation_results)
        
        print(f"\nQuality Score: {report['summary']['overall_quality_score']}")
        print(f"Quality Level: {report['summary']['quality_level']}")
        
        return df, report
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_fred_data_validation(validator):
    """Test validation with FRED data."""
    print("\n" + "="*80)
    print("TEST 2: FRED API DATA VALIDATION")
    print("="*80)
    
    try:
        client = FREDAPIClient()
        df = client.fetch_series('DCOILWTICO', start_date='2024-01-01', end_date='2024-01-31')
        
        if df.empty:
            print("No data from FRED. Skipping...")
            return None
        
        # Prepare data for validation
        df = df.rename(columns={'date': 'timestamp', 'value': 'price'})
        df['commodity'] = 'WTI_CRUDE'
        df['source'] = 'FRED'
        
        print(f"Fetched {len(df)} records from FRED")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")
        
        # Run validations
        print("\nRunning validations...")
        
        schema_result = validator.validate_schema(df)
        print(f"  Schema: {schema_result['schema_compliance_score']}% compliant")
        
        completeness_result = validator.check_completeness(df, exclude_weekends=True)
        print(f"  Completeness: {completeness_result['completeness_score']}%")
        print(f"  Gaps: {completeness_result['gap_count']}")
        
        df_with_outliers = validator.detect_outliers(df, column='price')
        outlier_count = df_with_outliers['outlier_any'].sum()
        print(f"  Outliers: {outlier_count} ({(outlier_count/len(df)*100):.2f}%)")
        
        # Generate quality report
        validation_results = {
            'schema': schema_result,
            'completeness': completeness_result,
            'consistency': {'consistency_score': 100.0}
        }
        
        report = validator.generate_quality_report(df_with_outliers, validation_results)
        
        print(f"\nQuality Score: {report['summary']['overall_quality_score']}")
        print(f"Quality Level: {report['summary']['quality_level']}")
        
        return df, report
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_yahoo_data_validation(validator):
    """Test validation with Yahoo Finance data."""
    print("\n" + "="*80)
    print("TEST 3: YAHOO FINANCE DATA VALIDATION")
    print("="*80)
    
    try:
        client = YahooFinanceClient()
        df = client.fetch_ohlcv('CL=F', start_date='2024-01-01', end_date='2024-01-31', interval='1d')
        
        if df.empty:
            print("No data from Yahoo Finance. Skipping...")
            return None
        
        # Prepare data for validation
        df = df.rename(columns={'date': 'timestamp', 'close': 'price'})
        df['commodity'] = 'WTI_CRUDE'
        df['source'] = 'YAHOO_FINANCE'
        
        print(f"Fetched {len(df)} records from Yahoo Finance")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")
        
        # Run validations
        print("\nRunning validations...")
        
        schema_result = validator.validate_schema(df)
        print(f"  Schema: {schema_result['schema_compliance_score']}% compliant")
        
        completeness_result = validator.check_completeness(df, exclude_weekends=True)
        print(f"  Completeness: {completeness_result['completeness_score']}%")
        print(f"  Gaps: {completeness_result['gap_count']}")
        
        df_with_outliers = validator.detect_outliers(df, column='price')
        outlier_count = df_with_outliers['outlier_any'].sum()
        print(f"  Outliers: {outlier_count} ({(outlier_count/len(df)*100):.2f}%)")
        
        # Generate quality report
        validation_results = {
            'schema': schema_result,
            'completeness': completeness_result,
            'consistency': {'consistency_score': 100.0}
        }
        
        report = validator.generate_quality_report(df_with_outliers, validation_results)
        
        print(f"\nQuality Score: {report['summary']['overall_quality_score']}")
        print(f"Quality Level: {report['summary']['quality_level']}")
        
        return df, report
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_cross_source_validation(validator, eia_data, fred_data):
    """Test cross-source consistency validation."""
    print("\n" + "="*80)
    print("TEST 4: CROSS-SOURCE CONSISTENCY (EIA vs FRED)")
    print("="*80)
    
    if eia_data is None or fred_data is None:
        print("Need data from both sources. Skipping...")
        return
    
    try:
        # Compare EIA and FRED WTI prices
        result = validator.validate_cross_source(
            eia_data[['timestamp', 'price']],
            fred_data[['timestamp', 'price']],
            tolerance=0.05
        )
        
        print(f"Common dates: {result['common_dates']}")
        print(f"Consistency score: {result['consistency_score']}%")
        print(f"Discrepancies: {result['total_discrepancies']}")
        print(f"Avg difference: ${result['avg_difference']:.4f}")
        print(f"Max difference: ${result['max_difference']:.4f}")
        
        if result['total_discrepancies'] > 0:
            print("\nSample discrepancies:")
            for disc in result['discrepancies'][:3]:
                print(f"  {disc['timestamp']}: EIA=${disc['source1_value']:.2f}, "
                      f"FRED=${disc['source2_value']:.2f}, "
                      f"Diff={disc['pct_difference']*100:.2f}%")
        
    except Exception as e:
        print(f"Error: {e}")


def generate_summary_report(validator, results):
    """Generate summary report for all tests."""
    print("\n" + "="*80)
    print("SUMMARY REPORT")
    print("="*80)
    
    sources = ['EIA', 'FRED', 'Yahoo Finance']
    
    for i, (source, result) in enumerate(zip(sources, results)):
        if result is None:
            print(f"\n{source}: No data")
            continue
        
        df, report = result
        print(f"\n{source}:")
        print(f"  Records: {len(df)}")
        print(f"  Quality Score: {report['summary']['overall_quality_score']}")
        print(f"  Quality Level: {report['summary']['quality_level']}")
        print(f"  Schema: {report['scores']['schema_compliance']}")
        print(f"  Completeness: {report['scores']['completeness']}")
        print(f"  Outlier: {report['scores']['outlier']}")


def main():
    """Main test function."""
    print("="*80)
    print("REAL DATA VALIDATION TESTING")
    print("Energy Price Forecasting System")
    print("="*80)
    
    # Initialize validator
    validator = DataValidator()
    print("DataValidator initialized")
    
    # Test with each data source
    eia_result = test_eia_data_validation(validator)
    fred_result = test_fred_data_validation(validator)
    yahoo_result = test_yahoo_data_validation(validator)
    
    # Test cross-source validation
    if eia_result and fred_result:
        test_cross_source_validation(validator, eia_result[0], fred_result[0])
    
    # Generate summary
    generate_summary_report(validator, [eia_result, fred_result, yahoo_result])
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print("\nNext Steps:")
    print("1. Review validation results above")
    print("2. Check quality levels for each data source")
    print("3. Investigate any discrepancies or quality issues")
    print("4. Integrate validation into data pipeline")


if __name__ == '__main__':
    main()

