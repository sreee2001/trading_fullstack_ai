"""
Data Validation Module for Energy Price Forecasting System.

This module provides comprehensive data validation functionality including:
- Schema validation
- Range and outlier detection
- Completeness checks
- Cross-source consistency validation
- Data quality reporting

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
import yaml
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataValidator:
    """
    Comprehensive data validation class for energy price data.
    
    Validates data schema, detects outliers, checks completeness,
    and generates quality reports.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the DataValidator.
        
        Args:
            config_path: Path to validation configuration YAML file.
                        If None, uses default config.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "validation_config.yaml"
        
        self.config = self._load_config(config_path)
        logger.info("DataValidator initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load validation configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded validation config from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            # Return default config if file not found
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default validation configuration."""
        return {
            'price_ranges': {
                'WTI_CRUDE': {'min': 0.01, 'max': 300.00},
                'BRENT_CRUDE': {'min': 0.01, 'max': 300.00},
                'NATURAL_GAS': {'min': 0.01, 'max': 50.00},
            },
            'tolerances': {
                'cross_source_tolerance': 0.05,
                'max_daily_change': 0.50,
            },
            'completeness': {
                'max_gap_days': 2,
                'min_data_points': 30,
                'max_missing_rate': 0.05,
            },
            'outliers': {
                'z_score_threshold': 3.0,
                'iqr_multiplier': 1.5,
                'rolling_window_days': 30,
            },
            'quality_weights': {
                'completeness': 0.4,
                'consistency': 0.3,
                'schema_compliance': 0.2,
                'outlier': 0.1,
            }
        }
    
    # ============================================================
    # SCHEMA VALIDATION (Story 1.5.2)
    # ============================================================
    
    def validate_schema(
        self,
        df: pd.DataFrame,
        schema_name: str = "price_data"
    ) -> Dict[str, Any]:
        """
        Validate DataFrame schema against expected schema.
        
        Args:
            df: DataFrame to validate
            schema_name: Name of schema to validate against
        
        Returns:
            Dictionary with validation results:
            {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'missing_columns': List[str],
                'type_mismatches': List[Dict]
            }
        """
        logger.info(f"Validating schema for {len(df)} records")
        
        errors = []
        warnings = []
        missing_columns = []
        type_mismatches = []
        
        # Get expected schema from config
        schema_config = self.config.get('schemas', {}).get(schema_name, {})
        required_columns = schema_config.get('required', [])
        optional_columns = schema_config.get('optional', [])
        expected_types = schema_config.get('types', {})
        
        # Check required columns
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
                errors.append(f"VAL-006: Missing required column '{col}'")
        
        # Check data types
        for col in df.columns:
            if col in expected_types:
                expected_type = expected_types[col]
                actual_type = str(df[col].dtype)
                
                # Handle datetime types
                if expected_type == "datetime64[ns]":
                    if not pd.api.types.is_datetime64_any_dtype(df[col]):
                        type_mismatches.append({
                            'column': col,
                            'expected': expected_type,
                            'actual': actual_type
                        })
                        errors.append(
                            f"VAL-001: Column '{col}' has type '{actual_type}', "
                            f"expected '{expected_type}'"
                        )
                # Handle numeric types
                elif expected_type == "float64":
                    if not pd.api.types.is_numeric_dtype(df[col]):
                        type_mismatches.append({
                            'column': col,
                            'expected': expected_type,
                            'actual': actual_type
                        })
                        errors.append(
                            f"VAL-001: Column '{col}' has type '{actual_type}', "
                            f"expected '{expected_type}'"
                        )
                # Handle string types
                elif expected_type == "object":
                    if df[col].dtype.name != "object":
                        warnings.append(
                            f"Column '{col}' has type '{actual_type}', "
                            f"expected 'object' (string)"
                        )
        
        is_valid = len(errors) == 0
        
        result = {
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'missing_columns': missing_columns,
            'type_mismatches': type_mismatches,
            'schema_compliance_score': self._calculate_schema_compliance(
                df, required_columns, type_mismatches
            )
        }
        
        if is_valid:
            logger.info("Schema validation passed")
        else:
            logger.warning(f"Schema validation failed with {len(errors)} errors")
        
        return result
    
    def _calculate_schema_compliance(
        self,
        df: pd.DataFrame,
        required_columns: List[str],
        type_mismatches: List[Dict]
    ) -> float:
        """Calculate schema compliance score (0-100)."""
        if not required_columns:
            return 100.0
        
        total_checks = len(required_columns) + len(df.columns)
        failed_checks = len([col for col in required_columns if col not in df.columns])
        failed_checks += len(type_mismatches)
        
        score = max(0.0, (1.0 - failed_checks / total_checks) * 100)
        return round(score, 2)
    
    # ============================================================
    # OUTLIER DETECTION (Story 1.5.3)
    # ============================================================
    
    def detect_outliers(
        self,
        df: pd.DataFrame,
        column: str = 'price',
        methods: List[str] = ['zscore', 'iqr']
    ) -> pd.DataFrame:
        """
        Detect outliers in a DataFrame column using multiple methods.
        
        Args:
            df: DataFrame to analyze
            column: Column name to check for outliers
            methods: List of methods to use ('zscore', 'iqr')
        
        Returns:
            DataFrame with additional outlier flag columns:
            - 'outlier_zscore': bool
            - 'outlier_iqr': bool
            - 'outlier_any': bool (True if any method flags it)
        """
        logger.info(f"Detecting outliers in column '{column}' using methods: {methods}")
        
        df = df.copy()
        
        if column not in df.columns:
            logger.error(f"Column '{column}' not found in DataFrame")
            return df
        
        # Z-score method
        if 'zscore' in methods:
            threshold = self.config['outliers']['z_score_threshold']
            window = self.config['outliers']['rolling_window_days']
            
            # Calculate rolling mean and std
            rolling_mean = df[column].rolling(window=window, min_periods=1).mean()
            rolling_std = df[column].rolling(window=window, min_periods=1).std()
            
            # Calculate z-scores
            z_scores = np.abs((df[column] - rolling_mean) / rolling_std)
            df['outlier_zscore'] = z_scores > threshold
            
            outlier_count_z = df['outlier_zscore'].sum()
            logger.info(f"Z-score method: {outlier_count_z} outliers detected")
        
        # IQR method
        if 'iqr' in methods:
            multiplier = self.config['outliers']['iqr_multiplier']
            
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR
            
            df['outlier_iqr'] = (df[column] < lower_bound) | (df[column] > upper_bound)
            
            outlier_count_iqr = df['outlier_iqr'].sum()
            logger.info(f"IQR method: {outlier_count_iqr} outliers detected")
        
        # Combined outlier flag
        outlier_cols = [col for col in df.columns if col.startswith('outlier_')]
        if outlier_cols:
            df['outlier_any'] = df[outlier_cols].any(axis=1)
            logger.info(f"Total outliers (any method): {df['outlier_any'].sum()}")
        
        return df
    
    # ============================================================
    # COMPLETENESS CHECKS (Story 1.5.4)
    # ============================================================
    
    def check_completeness(
        self,
        df: pd.DataFrame,
        timestamp_col: str = 'timestamp',
        expected_frequency: str = 'D',
        exclude_weekends: bool = True
    ) -> Dict[str, Any]:
        """
        Check data completeness and detect gaps in time series.
        
        Args:
            df: DataFrame to check
            timestamp_col: Name of timestamp column
            expected_frequency: Expected frequency ('D' for daily, 'H' for hourly)
            exclude_weekends: Whether to exclude weekends from expected records (default: True)
        
        Returns:
            Dictionary with completeness analysis:
            {
                'completeness_score': float (0-100),
                'missing_values': Dict[str, int],
                'gaps': List[Dict],
                'total_records': int,
                'expected_records': int,
                'missing_records': int
            }
        """
        logger.info(f"Checking completeness for {len(df)} records")
        
        if timestamp_col not in df.columns:
            logger.error(f"Timestamp column '{timestamp_col}' not found")
            return {'completeness_score': 0.0, 'error': 'Timestamp column not found'}
        
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
            try:
                df[timestamp_col] = pd.to_datetime(df[timestamp_col])
            except Exception as e:
                logger.error(f"Failed to convert timestamp column: {e}")
                return {'completeness_score': 0.0, 'error': 'Invalid timestamp format'}
        
        # Sort by timestamp
        df = df.sort_values(timestamp_col).reset_index(drop=True)
        
        # Check for missing values in each column
        missing_values = df.isnull().sum().to_dict()
        
        # Detect gaps in time series
        gaps = []
        max_gap_days = self.config['completeness']['max_gap_days']
        
        if len(df) > 1:
            for i in range(1, len(df)):
                time_diff = (df[timestamp_col].iloc[i] - df[timestamp_col].iloc[i-1])
                gap_days = time_diff.days
                
                if gap_days > max_gap_days:
                    gaps.append({
                        'start': df[timestamp_col].iloc[i-1],
                        'end': df[timestamp_col].iloc[i],
                        'gap_days': gap_days,
                        'code': 'VAL-007'
                    })
        
        # Calculate expected vs actual records
        if len(df) > 0:
            date_range = pd.date_range(
                start=df[timestamp_col].min(),
                end=df[timestamp_col].max(),
                freq=expected_frequency
            )
            
            # Exclude weekends if requested (for trading days)
            if exclude_weekends and expected_frequency == 'D':
                # Filter out Saturdays (5) and Sundays (6)
                date_range = date_range[date_range.dayofweek < 5]
            
            expected_records = len(date_range)
            actual_records = len(df)
            missing_records = expected_records - actual_records
        else:
            expected_records = 0
            actual_records = 0
            missing_records = 0
        
        # Calculate completeness score
        if expected_records > 0:
            completeness_score = (actual_records / expected_records) * 100
        else:
            completeness_score = 0.0
        
        result = {
            'completeness_score': round(completeness_score, 2),
            'missing_values': missing_values,
            'gaps': gaps,
            'total_records': actual_records,
            'expected_records': expected_records,
            'missing_records': missing_records,
            'gap_count': len(gaps),
            'exclude_weekends': exclude_weekends
        }
        
        logger.info(f"Completeness check: {completeness_score:.2f}% complete, {len(gaps)} gaps found")
        
        return result
    
    # ============================================================
    # CROSS-SOURCE CONSISTENCY VALIDATION (Story 1.5.5)
    # ============================================================
    
    def validate_cross_source(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        timestamp_col: str = 'timestamp',
        value_col: str = 'price',
        tolerance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Validate consistency across two data sources.
        
        Args:
            df1: First DataFrame (source 1)
            df2: Second DataFrame (source 2)
            timestamp_col: Name of timestamp column
            value_col: Name of value column to compare
            tolerance: Tolerance for price differences (default from config)
        
        Returns:
            Dictionary with consistency analysis:
            {
                'consistency_score': float (0-100),
                'discrepancies': List[Dict],
                'common_dates': int,
                'avg_difference': float,
                'max_difference': float
            }
        """
        logger.info("Validating cross-source consistency")
        
        if tolerance is None:
            tolerance = self.config['tolerances']['cross_source_tolerance']
        
        # Merge on timestamp
        merged = pd.merge(
            df1[[timestamp_col, value_col]],
            df2[[timestamp_col, value_col]],
            on=timestamp_col,
            suffixes=('_source1', '_source2'),
            how='inner'
        )
        
        if len(merged) == 0:
            logger.warning("No common dates between sources")
            return {
                'consistency_score': 0.0,
                'discrepancies': [],
                'common_dates': 0,
                'error': 'No common dates'
            }
        
        # Calculate differences
        value1_col = f"{value_col}_source1"
        value2_col = f"{value_col}_source2"
        
        merged['abs_diff'] = np.abs(merged[value1_col] - merged[value2_col])
        merged['pct_diff'] = merged['abs_diff'] / merged[value1_col]
        
        # Find discrepancies
        discrepancies = []
        for idx, row in merged[merged['pct_diff'] > tolerance].iterrows():
            discrepancies.append({
                'timestamp': row[timestamp_col],
                'source1_value': row[value1_col],
                'source2_value': row[value2_col],
                'difference': row['abs_diff'],
                'pct_difference': row['pct_diff'],
                'code': 'VAL-010'
            })
        
        # Calculate metrics
        common_dates = len(merged)
        avg_difference = merged['abs_diff'].mean()
        max_difference = merged['abs_diff'].max()
        discrepancy_rate = len(discrepancies) / common_dates if common_dates > 0 else 0
        consistency_score = (1.0 - discrepancy_rate) * 100
        
        result = {
            'consistency_score': round(consistency_score, 2),
            'discrepancies': discrepancies[:100],  # Limit to 100 for performance
            'total_discrepancies': len(discrepancies),
            'common_dates': common_dates,
            'avg_difference': round(avg_difference, 4),
            'max_difference': round(max_difference, 4),
            'tolerance_used': tolerance
        }
        
        logger.info(
            f"Cross-source validation: {consistency_score:.2f}% consistent, "
            f"{len(discrepancies)} discrepancies found"
        )
        
        return result
    
    # ============================================================
    # DATA QUALITY REPORT (Story 1.5.6)
    # ============================================================
    
    def generate_quality_report(
        self,
        df: pd.DataFrame,
        validation_results: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive data quality report.
        
        Args:
            df: DataFrame that was validated
            validation_results: Dictionary containing all validation results
            output_path: Optional path to save report (JSON and TXT)
        
        Returns:
            Dictionary with quality report
        """
        logger.info("Generating data quality report")
        
        # Extract scores from validation results
        schema_score = validation_results.get('schema', {}).get('schema_compliance_score', 100.0)
        completeness_score = validation_results.get('completeness', {}).get('completeness_score', 100.0)
        consistency_score = validation_results.get('consistency', {}).get('consistency_score', 100.0)
        
        # Calculate outlier score
        if 'outliers' in df.columns:
            outlier_rate = df['outlier_any'].sum() / len(df) if len(df) > 0 else 0
        else:
            outlier_rate = 0
        outlier_score = (1.0 - outlier_rate) * 100
        
        # Calculate overall quality score
        weights = self.config['quality_weights']
        quality_score = (
            weights['completeness'] * completeness_score +
            weights['consistency'] * consistency_score +
            weights['schema_compliance'] * schema_score +
            weights['outlier'] * outlier_score
        )
        
        # Determine quality level
        quality_level = self._get_quality_level(quality_score)
        
        # Build report
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'overall_quality_score': round(quality_score, 2),
                'quality_level': quality_level,
                'total_records': len(df),
                'date_range': {
                    'start': str(df['timestamp'].min()) if 'timestamp' in df.columns else None,
                    'end': str(df['timestamp'].max()) if 'timestamp' in df.columns else None
                }
            },
            'scores': {
                'schema_compliance': round(schema_score, 2),
                'completeness': round(completeness_score, 2),
                'consistency': round(consistency_score, 2),
                'outlier': round(outlier_score, 2)
            },
            'validation_results': validation_results,
            'recommendations': self._generate_recommendations(quality_score, validation_results)
        }
        
        # Save report if output path provided
        if output_path:
            self._save_report(report, output_path)
        
        logger.info(f"Quality report generated: Score = {quality_score:.2f}, Level = {quality_level}")
        
        return report
    
    def _get_quality_level(self, score: float) -> str:
        """Determine quality level based on score."""
        thresholds = self.config['quality_thresholds']
        
        if score >= thresholds['excellent']['min']:
            return 'EXCELLENT'
        elif score >= thresholds['good']['min']:
            return 'GOOD'
        elif score >= thresholds['fair']['min']:
            return 'FAIR'
        elif score >= thresholds['poor']['min']:
            return 'POOR'
        else:
            return 'UNUSABLE'
    
    def _generate_recommendations(self, score: float, validation_results: Dict) -> List[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []
        
        if score >= 95:
            recommendations.append("Data quality is excellent. Proceed with analysis.")
        elif score >= 85:
            recommendations.append("Data quality is good. Minor cleanup recommended.")
        elif score >= 70:
            recommendations.append("Data quality is fair. Investigate and resolve issues before use.")
        else:
            recommendations.append("Data quality is poor. Extensive cleanup or alternative sources needed.")
        
        # Specific recommendations based on validation results
        if 'schema' in validation_results:
            if validation_results['schema'].get('errors'):
                recommendations.append("Fix schema errors: missing columns or type mismatches.")
        
        if 'completeness' in validation_results:
            if validation_results['completeness'].get('gap_count', 0) > 0:
                recommendations.append("Address data gaps in time series.")
        
        if 'consistency' in validation_results:
            if validation_results['consistency'].get('total_discrepancies', 0) > 0:
                recommendations.append("Investigate cross-source discrepancies.")
        
        return recommendations
    
    def _save_report(self, report: Dict, output_path: str):
        """Save report to JSON and TXT files."""
        try:
            # Create directory if it doesn't exist
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save JSON
            json_path = output_path if output_path.endswith('.json') else f"{output_path}.json"
            with open(json_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Report saved to {json_path}")
            
            # Save TXT (human-readable)
            txt_path = json_path.replace('.json', '.txt')
            with open(txt_path, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("DATA QUALITY REPORT\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Generated: {report['generated_at']}\n\n")
                
                f.write("SUMMARY:\n")
                f.write(f"  Overall Quality Score: {report['summary']['overall_quality_score']}\n")
                f.write(f"  Quality Level: {report['summary']['quality_level']}\n")
                f.write(f"  Total Records: {report['summary']['total_records']}\n\n")
                
                f.write("DETAILED SCORES:\n")
                for key, value in report['scores'].items():
                    f.write(f"  {key.replace('_', ' ').title()}: {value}\n")
                
                f.write("\nRECOMMENDATIONS:\n")
                for i, rec in enumerate(report['recommendations'], 1):
                    f.write(f"  {i}. {rec}\n")
                
                f.write("\n" + "=" * 80 + "\n")
            
            logger.info(f"Human-readable report saved to {txt_path}")
            
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

