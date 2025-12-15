"""
Time Series Data Splitting Utilities.

Provides train/validation/test split utilities for time series data
that respect temporal ordering.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class TimeSeriesSplitter:
    """
    Split time series data into train/validation/test sets.
    
    Respects temporal ordering (no random shuffling) and provides
    flexible splitting strategies for time series data.
    
    Attributes:
        train_ratio: Fraction of data for training
        val_ratio: Fraction of data for validation
        test_ratio: Fraction of data for testing
    
    Example:
        >>> splitter = TimeSeriesSplitter(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
        >>> train, val, test = splitter.split(data)
    """
    
    def __init__(
        self,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        date_column: Optional[str] = None
    ):
        """
        Initialize TimeSeriesSplitter.
        
        Args:
            train_ratio: Fraction of data for training (default: 0.7)
            val_ratio: Fraction of data for validation (default: 0.15)
            test_ratio: Fraction of data for testing (default: 0.15)
            date_column: Name of date column for sorting (None = use index)
        
        Raises:
            ValueError: If ratios don't sum to 1.0
        """
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
            raise ValueError(
                f"Ratios must sum to 1.0. Got: train={train_ratio}, val={val_ratio}, test={test_ratio}"
            )
        
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.date_column = date_column
        
        logger.info(
            f"TimeSeriesSplitter initialized: "
            f"train={train_ratio}, val={val_ratio}, test={test_ratio}"
        )
    
    def split(
        self,
        data: pd.DataFrame | pd.Series,
        sort_by_date: bool = True
    ) -> Tuple[pd.DataFrame | pd.Series, pd.DataFrame | pd.Series, pd.DataFrame | pd.Series]:
        """
        Split data into train/validation/test sets.
        
        Args:
            data: Input data (DataFrame or Series)
            sort_by_date: Whether to sort by date before splitting (default: True)
        
        Returns:
            Tuple of (train_data, val_data, test_data)
        """
        # Convert Series to DataFrame if needed
        if isinstance(data, pd.Series):
            data = data.to_frame()
        
        # Sort by date if requested
        if sort_by_date:
            if self.date_column and self.date_column in data.columns:
                data = data.sort_values(self.date_column)
            elif isinstance(data.index, pd.DatetimeIndex):
                data = data.sort_index()
            else:
                logger.warning("Cannot sort by date - no date column or DatetimeIndex found")
        
        # Calculate split indices
        n_total = len(data)
        n_train = int(n_total * self.train_ratio)
        n_val = int(n_total * self.val_ratio)
        
        # Split data
        train_data = data.iloc[:n_train].copy()
        val_data = data.iloc[n_train:n_train + n_val].copy()
        test_data = data.iloc[n_train + n_val:].copy()
        
        logger.info(
            f"Split data: train={len(train_data)}, val={len(val_data)}, test={len(test_data)}"
        )
        
        # Convert back to Series if input was Series
        if isinstance(data, pd.Series):
            train_data = train_data.iloc[:, 0]
            val_data = val_data.iloc[:, 0]
            test_data = test_data.iloc[:, 0]
        
        return train_data, val_data, test_data


def split_time_series(
    data: pd.DataFrame | pd.Series,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    date_column: Optional[str] = None,
    sort_by_date: bool = True
) -> Tuple[pd.DataFrame | pd.Series, pd.DataFrame | pd.Series, pd.DataFrame | pd.Series]:
    """
    Convenience wrapper for splitting time series data.

    Args:
        data: Input data (DataFrame or Series)
        train_ratio: Training split ratio
        val_ratio: Validation split ratio
        test_ratio: Test split ratio
        date_column: Optional date column to sort by
        sort_by_date: Whether to sort by date before splitting

    Returns:
        Tuple of (train, validation, test) datasets
    """
    splitter = TimeSeriesSplitter(
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
        date_column=date_column
    )
    return splitter.split(data, sort_by_date=sort_by_date)
    
    def split_with_dates(
        self,
        data: pd.DataFrame | pd.Series,
        train_end_date: Optional[str] = None,
        val_end_date: Optional[str] = None
    ) -> Tuple[pd.DataFrame | pd.Series, pd.DataFrame | pd.Series, pd.DataFrame | pd.Series]:
        """
        Split data using specific dates.
        
        Args:
            data: Input data
            train_end_date: End date for training set (YYYY-MM-DD)
            val_end_date: End date for validation set (YYYY-MM-DD)
        
        Returns:
            Tuple of (train_data, val_data, test_data)
        """
        # Convert Series to DataFrame if needed
        if isinstance(data, pd.Series):
            data = data.to_frame()
        
        # Determine date column
        date_col = self.date_column
        if date_col is None and isinstance(data.index, pd.DatetimeIndex):
            # Use index
            date_col = None
        elif date_col is None:
            # Try to find date column
            for col in ['date', 'timestamp', 'time']:
                if col in data.columns:
                    date_col = col
                    break
        
        if date_col is None and not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Cannot split by dates: no date column or DatetimeIndex found")
        
        # Sort by date
        if date_col:
            data = data.sort_values(date_col)
            dates = pd.to_datetime(data[date_col])
        else:
            dates = data.index
        
        # Split by dates
        if train_end_date:
            train_mask = dates <= pd.to_datetime(train_end_date)
            train_data = data[train_mask].copy()
        else:
            # Use ratio
            n_train = int(len(data) * self.train_ratio)
            train_data = data.iloc[:n_train].copy()
            train_mask = dates <= dates.iloc[n_train - 1]
        
        remaining_data = data[~train_mask].copy()
        remaining_dates = dates[~train_mask]
        
        if val_end_date:
            val_mask = remaining_dates <= pd.to_datetime(val_end_date)
            val_data = remaining_data[val_mask].copy()
            test_data = remaining_data[~val_mask].copy()
        else:
            # Use ratio on remaining data
            n_val = int(len(remaining_data) * (self.val_ratio / (self.val_ratio + self.test_ratio)))
            val_data = remaining_data.iloc[:n_val].copy()
            test_data = remaining_data.iloc[n_val:].copy()
        
        logger.info(
            f"Split by dates: train={len(train_data)}, val={len(val_data)}, test={len(test_data)}"
        )
        
        # Convert back to Series if input was Series
        if isinstance(data, pd.Series):
            train_data = train_data.iloc[:, 0]
            val_data = val_data.iloc[:, 0]
            test_data = test_data.iloc[:, 0]
        
        return train_data, val_data, test_data

