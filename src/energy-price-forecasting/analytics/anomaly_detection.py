"""
Anomaly Detection for Energy Price Data.

Detects anomalies in energy commodity prices using statistical and
machine learning methods.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    IsolationForest = None
    StandardScaler = None

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Detects anomalies in energy price time series.
    
    Provides multiple methods for anomaly detection including statistical
    methods (Z-score, IQR) and machine learning methods (Isolation Forest).
    """
    
    def __init__(self):
        """Initialize AnomalyDetector."""
        logger.info("AnomalyDetector initialized")
    
    def detect_zscore_anomalies(
        self,
        series: pd.Series,
        threshold: float = 3.0,
        window: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Detect anomalies using Z-score method.
        
        Args:
            series: Time series data
            threshold: Z-score threshold (default: 3.0)
            window: Rolling window for mean/std (None = global)
            
        Returns:
            DataFrame with anomaly flags and z-scores
        """
        logger.info(f"Detecting Z-score anomalies (threshold={threshold})...")
        
        if window:
            # Rolling z-score
            mean = series.rolling(window=window).mean()
            std = series.rolling(window=window).std()
        else:
            # Global z-score
            mean = series.mean()
            std = series.std()
        
        z_scores = (series - mean) / std
        anomalies = abs(z_scores) > threshold
        
        result = pd.DataFrame({
            'value': series,
            'z_score': z_scores,
            'is_anomaly': anomalies,
            'mean': mean if isinstance(mean, pd.Series) else mean,
            'std': std if isinstance(std, pd.Series) else std
        })
        
        anomaly_count = anomalies.sum()
        logger.info(f"Detected {anomaly_count} anomalies ({anomaly_count/len(series)*100:.2f}%)")
        
        return result
    
    def detect_iqr_anomalies(
        self,
        series: pd.Series,
        factor: float = 1.5,
        window: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Detect anomalies using Interquartile Range (IQR) method.
        
        Args:
            series: Time series data
            factor: IQR multiplier (default: 1.5)
            window: Rolling window (None = global)
            
        Returns:
            DataFrame with anomaly flags
        """
        logger.info(f"Detecting IQR anomalies (factor={factor})...")
        
        if window:
            # Rolling IQR
            q1 = series.rolling(window=window).quantile(0.25)
            q3 = series.rolling(window=window).quantile(0.75)
            iqr = q3 - q1
        else:
            # Global IQR
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
        
        lower_bound = q1 - factor * iqr
        upper_bound = q3 + factor * iqr
        
        anomalies = (series < lower_bound) | (series > upper_bound)
        
        result = pd.DataFrame({
            'value': series,
            'is_anomaly': anomalies,
            'lower_bound': lower_bound if isinstance(lower_bound, pd.Series) else lower_bound,
            'upper_bound': upper_bound if isinstance(upper_bound, pd.Series) else upper_bound,
            'q1': q1 if isinstance(q1, pd.Series) else q1,
            'q3': q3 if isinstance(q3, pd.Series) else q3,
            'iqr': iqr if isinstance(iqr, pd.Series) else iqr
        })
        
        anomaly_count = anomalies.sum()
        logger.info(f"Detected {anomaly_count} anomalies ({anomaly_count/len(series)*100:.2f}%)")
        
        return result
    
    def detect_isolation_forest_anomalies(
        self,
        data: pd.DataFrame,
        contamination: float = 0.1,
        features: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Detect anomalies using Isolation Forest algorithm.
        
        Args:
            data: DataFrame with features
            contamination: Expected proportion of anomalies (default: 0.1)
            features: List of feature columns (None = all numeric)
            
        Returns:
            DataFrame with anomaly flags and scores
        """
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn required for Isolation Forest")
            return pd.DataFrame()
        
        logger.info(f"Detecting anomalies using Isolation Forest (contamination={contamination})...")
        
        # Select features
        if features:
            X = data[features].select_dtypes(include=[np.number])
        else:
            X = data.select_dtypes(include=[np.number])
        
        if len(X.columns) == 0:
            logger.warning("No numeric features available")
            return pd.DataFrame()
        
        # Handle missing values
        X_clean = X.dropna()
        
        if len(X_clean) < 10:
            logger.warning("Insufficient data for Isolation Forest")
            return pd.DataFrame()
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_clean)
        
        # Fit Isolation Forest
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        predictions = iso_forest.fit_predict(X_scaled)
        
        # Convert predictions: -1 = anomaly, 1 = normal
        anomalies = predictions == -1
        scores = iso_forest.score_samples(X_scaled)
        
        # Create result DataFrame aligned with original data
        result = pd.DataFrame(index=X_clean.index)
        result['is_anomaly'] = anomalies
        result['anomaly_score'] = scores
        
        # Reindex to match original data
        result = result.reindex(data.index, fill_value=False)
        
        anomaly_count = anomalies.sum()
        logger.info(f"Detected {anomaly_count} anomalies ({anomaly_count/len(X_clean)*100:.2f}%)")
        
        return result
    
    def detect_change_point(
        self,
        series: pd.Series,
        method: str = 'mean',
        window: int = 30
    ) -> List[int]:
        """
        Detect change points in time series.
        
        Args:
            series: Time series data
            method: Detection method ('mean', 'variance')
            window: Window size for comparison
            
        Returns:
            List of change point indices
        """
        logger.info(f"Detecting change points (method={method})...")
        
        change_points = []
        
        for i in range(window, len(series) - window):
            window1 = series[i-window:i]
            window2 = series[i:i+window]
            
            if method == 'mean':
                mean1 = window1.mean()
                mean2 = window2.mean()
                std1 = window1.std()
                std2 = window2.std()
                
                # Two-sample t-test approximation
                if std1 > 0 and std2 > 0:
                    t_stat = abs(mean1 - mean2) / np.sqrt(std1**2/window + std2**2/window)
                    if t_stat > 2.0:  # Approximate threshold
                        change_points.append(i)
            
            elif method == 'variance':
                var1 = window1.var()
                var2 = window2.var()
                
                # F-test for variance
                if var1 > 0 and var2 > 0:
                    f_stat = max(var1, var2) / min(var1, var2)
                    if f_stat > 2.0:  # Approximate threshold
                        change_points.append(i)
        
        logger.info(f"Detected {len(change_points)} change points")
        return change_points
    
    def detect_all_anomalies(
        self,
        series: pd.Series,
        methods: List[str] = None
    ) -> pd.DataFrame:
        """
        Detect anomalies using multiple methods and combine results.
        
        Args:
            series: Time series data
            methods: List of methods to use (None = all)
            
        Returns:
            DataFrame with combined anomaly flags
        """
        if methods is None:
            methods = ['zscore', 'iqr']
        
        results = pd.DataFrame(index=series.index)
        results['value'] = series
        
        anomaly_flags = []
        
        if 'zscore' in methods:
            zscore_result = self.detect_zscore_anomalies(series)
            results['zscore_anomaly'] = zscore_result['is_anomaly']
            results['zscore'] = zscore_result['z_score']
            anomaly_flags.append('zscore_anomaly')
        
        if 'iqr' in methods:
            iqr_result = self.detect_iqr_anomalies(series)
            results['iqr_anomaly'] = iqr_result['is_anomaly']
            anomaly_flags.append('iqr_anomaly')
        
        # Combined flag: anomaly if detected by any method
        if anomaly_flags:
            results['is_anomaly'] = results[anomaly_flags].any(axis=1)
            results['anomaly_count'] = results[anomaly_flags].sum(axis=1)
        
        return results

