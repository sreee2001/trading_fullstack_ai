"""
Data Validation Example Script.

This script demonstrates the usage of the DataValidator class for
comprehensive data quality validation of energy price data.

Author: AI Assistant
Date: December 14, 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_validation import DataValidator
from data_ingestion.eia_client import EIAAPIClient


def create_sample_data():
    """Create sample price data for demonstration."""
    print("Creating sample data...")
    
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    
    df = pd.DataFrame({
        'timestamp': dates,
        'price': np.random.uniform(70, 80, len(dates)),
        'commodity': ['WTI_CRUDE'] * len(dates),
        'source': ['EIA'] * len(dates),
        'volume': np.random.uniform(1000, 2000, len(dates))
    })
    
    # Inject some data quality issues for demonstration
    df.loc[10, 'price'] = 150  # Outlier
    df.loc[15:17, 'price'] = np.nan  # Missing values
    
    return df


def demonstrate_schema_validation(validator, df):
    """Demonstrate schema validation."""
    print("\n" + "="*80)
    print("1. SCHEMA VALIDATION")
    print("="*80)
    
    result = validator.validate_schema(df)
    
    print(f"Valid: {result['valid']}")
    print(f"Schema Compliance Score: {result['schema_compliance_score']}%")
    print(f"Errors: {len(result['errors'])}")
    print(f"Warnings: {len(result['warnings'])}")
    
    if result['errors']:
        print("\nErrors Found:")
        for error in result['errors'][:5]:
            print(f"  - {error}")
    
    return result


def demonstrate_outlier_detection(validator, df):
    """Demonstrate outlier detection."""
    print("\n" + "="*80)
    print("2. OUTLIER DETECTION")
    print("="*80)
    
    df_with_outliers = validator.detect_outliers(df, column='price', methods=['zscore', 'iqr'])
    
    outlier_count = df_with_outliers['outlier_any'].sum()
    outlier_pct = (outlier_count / len(df_with_outliers)) * 100
    
    print(f"Total Outliers Detected: {outlier_count} ({outlier_pct:.2f}%)")
    print(f"  - Z-score method: {df_with_outliers['outlier_zscore'].sum()}")
    print(f"  - IQR method: {df_with_outliers['outlier_iqr'].sum()}")
    
    if outlier_count > 0:
        print("\nOutlier Records:")
        outlier_df = df_with_outliers[df_with_outliers['outlier_any']]
        print(outlier_df[['timestamp', 'price', 'outlier_zscore', 'outlier_iqr']].head())
    
    return df_with_outliers


def demonstrate_completeness_check(validator, df):
    """Demonstrate completeness checking."""
    print("\n" + "="*80)
    print("3. COMPLETENESS CHECKS")
    print("="*80)
    
    result = validator.check_completeness(df)
    
    print(f"Completeness Score: {result['completeness_score']}%")
    print(f"Total Records: {result['total_records']}")
    print(f"Expected Records: {result['expected_records']}")
    print(f"Missing Records: {result['missing_records']}")
    print(f"Gaps Found: {result['gap_count']}")
    
    print("\nMissing Values by Column:")
    for col, count in result['missing_values'].items():
        if count > 0:
            print(f"  - {col}: {count}")
    
    if result['gaps']:
        print("\nTime Series Gaps:")
        for gap in result['gaps'][:5]:
            print(f"  - {gap['start']} to {gap['end']} ({gap['gap_days']} days)")
    
    return result


def demonstrate_cross_source_validation(validator):
    """Demonstrate cross-source consistency validation."""
    print("\n" + "="*80)
    print("4. CROSS-SOURCE CONSISTENCY VALIDATION")
    print("="*80)
    
    # Create two slightly different datasets (simulating different sources)
    dates = pd.date_range('2024-01-01', periods=30)
    
    df1 = pd.DataFrame({
        'timestamp': dates,
        'price': np.random.uniform(70, 80, 30)
    })
    
    df2 = pd.DataFrame({
        'timestamp': dates,
        'price': df1['price'] * np.random.uniform(0.98, 1.02, 30)  # 2% variation
    })
    
    result = validator.validate_cross_source(df1, df2, tolerance=0.05)
    
    print(f"Consistency Score: {result['consistency_score']}%")
    print(f"Common Dates: {result['common_dates']}")
    print(f"Discrepancies Found: {result['total_discrepancies']}")
    print(f"Average Difference: ${result['avg_difference']:.4f}")
    print(f"Max Difference: ${result['max_difference']:.4f}")
    
    if result['discrepancies']:
        print("\nSample Discrepancies:")
        for disc in result['discrepancies'][:3]:
            print(f"  - {disc['timestamp']}: Source1=${disc['source1_value']:.2f}, "
                  f"Source2=${disc['source2_value']:.2f}, Diff={disc['pct_difference']*100:.2f}%")
    
    return result


def demonstrate_quality_report(validator, df, validation_results):
    """Demonstrate quality report generation."""
    print("\n" + "="*80)
    print("5. DATA QUALITY REPORT")
    print("="*80)
    
    # Create output directory
    output_dir = Path(__file__).parent / "logs" / "validation"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "quality_report"
    
    report = validator.generate_quality_report(
        df,
        validation_results,
        output_path=str(output_path)
    )
    
    print(f"Overall Quality Score: {report['summary']['overall_quality_score']}")
    print(f"Quality Level: {report['summary']['quality_level']}")
    print(f"Total Records: {report['summary']['total_records']}")
    
    print("\nDetailed Scores:")
    for metric, score in report['scores'].items():
        print(f"  - {metric.replace('_', ' ').title()}: {score}")
    
    print("\nRecommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print(f"\nReports saved to:")
    print(f"  - JSON: {output_path}.json")
    print(f"  - TXT: {output_path}.txt")
    
    return report


def demonstrate_with_real_data(validator):
    """Demonstrate validation with real EIA data."""
    print("\n" + "="*80)
    print("6. VALIDATION WITH REAL DATA (EIA API)")
    print("="*80)
    
    try:
        # Fetch real data from EIA
        eia_client = EIAAPIClient()
        df = eia_client.fetch_wti_prices(
            start_date='2024-01-01',
            end_date='2024-01-31'
        )
        
        if df.empty:
            print("No data fetched from EIA. Skipping real data validation.")
            return
        
        # Rename columns to match expected schema
        df = df.rename(columns={'date': 'timestamp'})
        df['commodity'] = 'WTI_CRUDE'
        df['source'] = 'EIA'
        
        print(f"Fetched {len(df)} records from EIA")
        
        # Run all validations
        print("\nRunning comprehensive validation...")
        
        schema_result = validator.validate_schema(df)
        completeness_result = validator.check_completeness(df)
        df_with_outliers = validator.detect_outliers(df, column='price')
        
        validation_results = {
            'schema': schema_result,
            'completeness': completeness_result,
            'consistency': {'consistency_score': 100.0}  # Single source
        }
        
        report = validator.generate_quality_report(df_with_outliers, validation_results)
        
        print(f"\nReal Data Quality Score: {report['summary']['overall_quality_score']}")
        print(f"Quality Level: {report['summary']['quality_level']}")
        
    except Exception as e:
        print(f"Error fetching real data: {e}")


def main():
    """Main demonstration function."""
    print("="*80)
    print("DATA VALIDATION FRAMEWORK DEMONSTRATION")
    print("Energy Price Forecasting System")
    print("="*80)
    
    # Initialize validator
    validator = DataValidator()
    print("DataValidator initialized successfully")
    
    # Create sample data
    df = create_sample_data()
    print(f"Created sample dataset with {len(df)} records")
    
    # Collect validation results
    validation_results = {}
    
    # 1. Schema Validation
    validation_results['schema'] = demonstrate_schema_validation(validator, df)
    
    # 2. Outlier Detection
    df_with_outliers = demonstrate_outlier_detection(validator, df)
    
    # 3. Completeness Checks
    validation_results['completeness'] = demonstrate_completeness_check(validator, df)
    
    # 4. Cross-Source Validation
    validation_results['consistency'] = demonstrate_cross_source_validation(validator)
    
    # 5. Quality Report
    report = demonstrate_quality_report(validator, df_with_outliers, validation_results)
    
    # 6. Real Data Validation (optional)
    demonstrate_with_real_data(validator)
    
    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nNext Steps:")
    print("1. Review the generated quality reports in examples/logs/validation/")
    print("2. Integrate validation into your data pipeline")
    print("3. Configure validation rules in data_validation/validation_config.yaml")
    print("4. Run automated validation before model training")


if __name__ == '__main__':
    main()

