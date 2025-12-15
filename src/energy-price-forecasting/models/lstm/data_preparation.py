"""
Sequence Data Preparation for LSTM Models.

Prepares time series data into sequences suitable for LSTM training.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, List
import logging
from sklearn.preprocessing import MinMaxScaler, StandardScaler

logger = logging.getLogger(__name__)


class SequenceDataPreparator:
    """
    Prepares time series data for LSTM models.
    
    Converts time series data into sequences of fixed length for LSTM training.
    Supports both univariate and multivariate time series.
    
    Attributes:
        sequence_length: Length of input sequences
        forecast_horizon: Number of steps to forecast ahead
        scaler: Scaler for data normalization
        feature_columns: Columns to use as features
    
    Example:
        >>> preparator = SequenceDataPreparator(sequence_length=60, forecast_horizon=1)
        >>> X_train, y_train, X_test, y_test = preparator.prepare_data(train_data, test_data)
    """
    
    def __init__(
        self,
        sequence_length: int = 60,
        forecast_horizon: int = 1,
        scaler_type: str = 'minmax',
        feature_columns: Optional[List[str]] = None
    ):
        """
        Initialize SequenceDataPreparator.
        
        Args:
            sequence_length: Length of input sequences (number of time steps to look back)
            forecast_horizon: Number of steps ahead to forecast (default: 1)
            scaler_type: Type of scaler ('minmax' or 'standard', default: 'minmax')
            feature_columns: List of column names to use as features (None = use all numeric columns)
        """
        self.sequence_length = sequence_length
        self.forecast_horizon = forecast_horizon
        
        if scaler_type == 'minmax':
            self.scaler = MinMaxScaler()
        elif scaler_type == 'standard':
            self.scaler = StandardScaler()
        else:
            raise ValueError(f"Unknown scaler_type: {scaler_type}. Use 'minmax' or 'standard'")
        
        self.feature_columns = feature_columns
        self.is_fitted = False
        
        logger.info(
            f"SequenceDataPreparator initialized: "
            f"sequence_length={sequence_length}, forecast_horizon={forecast_horizon}, scaler={scaler_type}"
        )
    
    def prepare_data(
        self,
        train_data: pd.DataFrame | pd.Series,
        test_data: Optional[pd.DataFrame | pd.Series] = None,
        target_column: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Prepare data for LSTM training.
        
        Args:
            train_data: Training data (DataFrame or Series)
            test_data: Test data (optional, DataFrame or Series)
            target_column: Name of target column (if DataFrame, default: last column)
        
        Returns:
            Tuple of (X_train, y_train, X_test, y_test)
            - X_train, X_test: 3D arrays (samples, sequence_length, features)
            - y_train, y_test: 2D arrays (samples, forecast_horizon)
        """
        # Convert Series to DataFrame
        if isinstance(train_data, pd.Series):
            train_data = train_data.to_frame(name='value')
            if target_column is None:
                target_column = 'value'
        
        # Select feature columns
        if self.feature_columns is None:
            # Use all numeric columns
            numeric_cols = train_data.select_dtypes(include=[np.number]).columns.tolist()
            if target_column and target_column in numeric_cols:
                # Remove target from features if it's in the list
                feature_cols = [col for col in numeric_cols if col != target_column]
                if not feature_cols:
                    # If no other features, use target as feature (univariate)
                    feature_cols = [target_column]
            else:
                feature_cols = numeric_cols
        else:
            feature_cols = self.feature_columns
        
        # Determine target column
        if target_column is None:
            target_column = train_data.columns[-1]
        
        logger.info(f"Using features: {feature_cols}, target: {target_column}")
        
        # Extract features and target
        X_train_raw = train_data[feature_cols].values
        y_train_raw = train_data[target_column].values.reshape(-1, 1)
        
        # Fit scaler on training data
        logger.info("Fitting scaler on training data...")
        X_train_scaled = self.scaler.fit_transform(X_train_raw)
        y_train_scaled = self.scaler.fit_transform(y_train_raw)
        self.is_fitted = True
        
        # Create sequences
        X_train, y_train = self._create_sequences(X_train_scaled, y_train_scaled)
        
        logger.info(f"Created training sequences: X_train shape {X_train.shape}, y_train shape {y_train.shape}")
        
        # Process test data if provided
        X_test, y_test = None, None
        if test_data is not None:
            if isinstance(test_data, pd.Series):
                test_data = test_data.to_frame(name='value')
            
            X_test_raw = test_data[feature_cols].values
            y_test_raw = test_data[target_column].values.reshape(-1, 1)
            
            # Transform test data using fitted scaler
            X_test_scaled = self.scaler.transform(X_test_raw)
            y_test_scaled = self.scaler.transform(y_test_raw)
            
            X_test, y_test = self._create_sequences(X_test_scaled, y_test_scaled)
            
            logger.info(f"Created test sequences: X_test shape {X_test.shape}, y_test shape {y_test.shape}")
        
        return X_train, y_train, X_test, y_test
    
    def _create_sequences(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences from time series data.
        
        Args:
            X: Feature data (samples, features)
            y: Target data (samples, 1)
        
        Returns:
            Tuple of (X_sequences, y_sequences)
            - X_sequences: (samples, sequence_length, features)
            - y_sequences: (samples, forecast_horizon)
        """
        X_sequences = []
        y_sequences = []
        
        for i in range(len(X) - self.sequence_length - self.forecast_horizon + 1):
            # Input sequence
            X_seq = X[i:i + self.sequence_length]
            X_sequences.append(X_seq)
            
            # Target sequence (forecast horizon)
            y_seq = y[i + self.sequence_length:i + self.sequence_length + self.forecast_horizon].flatten()
            y_sequences.append(y_seq)
        
        return np.array(X_sequences), np.array(y_sequences)
    
    def inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """
        Inverse transform scaled data back to original scale.
        
        Args:
            data: Scaled data to inverse transform
        
        Returns:
            Data in original scale
        """
        if not self.is_fitted:
            raise ValueError("Scaler must be fitted before inverse transform. Call prepare_data() first.")
        
        # Reshape if needed
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        return self.scaler.inverse_transform(data)
    
    def get_feature_count(self) -> int:
        """
        Get number of features after preparation.
        
        Returns:
            Number of features
        """
        if self.feature_columns:
            return len(self.feature_columns)
        return 1  # Default to 1 for univariate

