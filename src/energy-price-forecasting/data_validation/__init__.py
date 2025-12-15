"""
Data Validation Package for Energy Price Forecasting System.

This package provides comprehensive data validation functionality for energy price data,
including schema validation, outlier detection, completeness checks, and quality reporting.

Classes:
    DataValidator: Main validation class with all validation methods

Usage:
    from data_validation import DataValidator
    
    validator = DataValidator()
    schema_result = validator.validate_schema(df)
    completeness_result = validator.check_completeness(df)
    
Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

from .validator import DataValidator

__all__ = ['DataValidator']
__version__ = '1.0.0'

