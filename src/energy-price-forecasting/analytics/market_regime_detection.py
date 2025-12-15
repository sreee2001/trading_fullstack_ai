"""
Market Regime Detection for Energy Prices.

Identifies different market regimes (bull, bear, sideways, volatile, calm)
using statistical and machine learning methods.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.mixture import GaussianMixture
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    KMeans = None
    StandardScaler = None
    GaussianMixture = None

logger = logging.getLogger(__name__)


class MarketRegimeDetector:
    """
    Detects market regimes in energy price time series.
    
    Identifies different market states such as:
    - Bull market (rising prices)
    - Bear market (falling prices)
    - Sideways/consolidation
    - High volatility
    - Low volatility
    """
    
    def __init__(self):
        """Initialize MarketRegimeDetector."""
        logger.info("MarketRegimeDetector initialized")
    
    def calculate_regime_features(
        self,
        prices: pd.Series,
        window: int = 30
    ) -> pd.DataFrame:
        """
        Calculate features for regime detection.
        
        Args:
            prices: Price series
            window: Rolling window size
            
        Returns:
            DataFrame with regime features
        """
        logger.info("Calculating regime features...")
        
        # Calculate returns
        returns = np.log(prices / prices.shift(1)).dropna()
        
        # Calculate rolling statistics
        rolling_mean = returns.rolling(window=window).mean()
        rolling_std = returns.rolling(window=window).std()
        rolling_skew = returns.rolling(window=window).skew()
        rolling_kurt = returns.rolling(window=window).kurtosis()
        
        # Calculate trend (slope)
        trend = prices.rolling(window=window).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) == window else np.nan
        )
        
        # Calculate volatility regime
        volatility = rolling_std * np.sqrt(252)  # Annualized
        
        # Calculate momentum
        momentum = prices.pct_change(window)
        
        features = pd.DataFrame({
            'returns_mean': rolling_mean,
            'returns_std': rolling_std,
            'returns_skew': rolling_skew,
            'returns_kurt': rolling_kurt,
            'trend': trend,
            'volatility': volatility,
            'momentum': momentum,
            'price': prices
        })
        
        return features.dropna()
    
    def detect_regimes_kmeans(
        self,
        features: pd.DataFrame,
        n_regimes: int = 3,
        feature_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Detect regimes using K-Means clustering.
        
        Args:
            features: DataFrame with regime features
            n_regimes: Number of regimes to identify
            feature_cols: Columns to use for clustering (None = all numeric)
            
        Returns:
            DataFrame with regime labels
        """
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn required for K-Means clustering")
            return pd.DataFrame()
        
        logger.info(f"Detecting regimes using K-Means (n_regimes={n_regimes})...")
        
        # Select features
        if feature_cols:
            X = features[feature_cols].select_dtypes(include=[np.number])
        else:
            X = features.select_dtypes(include=[np.number])
        
        if len(X.columns) == 0:
            logger.warning("No numeric features available")
            return pd.DataFrame()
        
        # Handle missing values
        X_clean = X.dropna()
        
        if len(X_clean) < n_regimes:
            logger.warning(f"Insufficient data for {n_regimes} regimes")
            return pd.DataFrame()
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_clean)
        
        # Fit K-Means
        kmeans = KMeans(n_clusters=n_regimes, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        
        # Create result DataFrame
        result = pd.DataFrame(index=X_clean.index)
        result['regime'] = labels
        result['regime_name'] = result['regime'].map(lambda x: f'Regime_{x}')
        
        # Reindex to match original features
        result = result.reindex(features.index, fill_value=-1)
        
        # Add feature values
        for col in X.columns:
            result[col] = features[col]
        
        logger.info(f"Detected {n_regimes} regimes")
        return result
    
    def detect_regimes_gmm(
        self,
        features: pd.DataFrame,
        n_regimes: int = 3,
        feature_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Detect regimes using Gaussian Mixture Model (GMM).
        
        Args:
            features: DataFrame with regime features
            n_regimes: Number of regimes to identify
            feature_cols: Columns to use for clustering
            
        Returns:
            DataFrame with regime labels and probabilities
        """
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn required for GMM")
            return pd.DataFrame()
        
        logger.info(f"Detecting regimes using GMM (n_regimes={n_regimes})...")
        
        # Select features
        if feature_cols:
            X = features[feature_cols].select_dtypes(include=[np.number])
        else:
            X = features.select_dtypes(include=[np.number])
        
        if len(X.columns) == 0:
            logger.warning("No numeric features available")
            return pd.DataFrame()
        
        # Handle missing values
        X_clean = X.dropna()
        
        if len(X_clean) < n_regimes:
            logger.warning(f"Insufficient data for {n_regimes} regimes")
            return pd.DataFrame()
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_clean)
        
        # Fit GMM
        gmm = GaussianMixture(n_components=n_regimes, random_state=42)
        labels = gmm.fit_predict(X_scaled)
        probabilities = gmm.predict_proba(X_scaled)
        
        # Create result DataFrame
        result = pd.DataFrame(index=X_clean.index)
        result['regime'] = labels
        result['regime_name'] = result['regime'].map(lambda x: f'Regime_{x}')
        result['regime_probability'] = probabilities.max(axis=1)
        
        # Add probabilities for each regime
        for i in range(n_regimes):
            result[f'prob_regime_{i}'] = probabilities[:, i]
        
        # Reindex to match original features
        result = result.reindex(features.index, fill_value=-1)
        
        # Add feature values
        for col in X.columns:
            result[col] = features[col]
        
        logger.info(f"Detected {n_regimes} regimes using GMM")
        return result
    
    def label_regimes(
        self,
        regime_data: pd.DataFrame,
        method: str = 'trend_volatility'
    ) -> pd.DataFrame:
        """
        Label regimes with descriptive names based on characteristics.
        
        Args:
            regime_data: DataFrame with regime labels and features
            method: Labeling method ('trend_volatility', 'simple')
            
        Returns:
            DataFrame with labeled regimes
        """
        logger.info(f"Labeling regimes (method={method})...")
        
        result = regime_data.copy()
        
        if method == 'trend_volatility':
            # Label based on trend and volatility
            if 'trend' in result.columns and 'volatility' in result.columns:
                # Calculate regime characteristics
                regime_stats = result.groupby('regime').agg({
                    'trend': 'mean',
                    'volatility': 'mean',
                    'returns_mean': 'mean'
                })
                
                # Create labels
                labels_map = {}
                for regime_id, stats in regime_stats.iterrows():
                    trend = stats['trend']
                    vol = stats['volatility']
                    returns = stats['returns_mean']
                    
                    if trend > 0 and vol < vol.median():
                        label = 'Bull_Calm'
                    elif trend > 0 and vol >= vol.median():
                        label = 'Bull_Volatile'
                    elif trend < 0 and vol < vol.median():
                        label = 'Bear_Calm'
                    elif trend < 0 and vol >= vol.median():
                        label = 'Bear_Volatile'
                    elif abs(trend) < 0.001:
                        label = 'Sideways'
                    else:
                        label = f'Regime_{regime_id}'
                    
                    labels_map[regime_id] = label
                
                result['regime_label'] = result['regime'].map(labels_map)
        
        elif method == 'simple':
            # Simple labeling based on returns
            if 'returns_mean' in result.columns:
                regime_stats = result.groupby('regime')['returns_mean'].mean()
                
                labels_map = {}
                sorted_regimes = regime_stats.sort_values()
                
                labels_map[sorted_regimes.index[0]] = 'Bear'
                labels_map[sorted_regimes.index[-1]] = 'Bull'
                
                if len(sorted_regimes) > 2:
                    for i, regime_id in enumerate(sorted_regimes.index[1:-1]):
                        labels_map[regime_id] = f'Sideways_{i+1}'
                
                result['regime_label'] = result['regime'].map(labels_map)
        
        return result
    
    def detect_regime_changes(
        self,
        regime_labels: pd.Series,
        min_duration: int = 5
    ) -> List[Dict[str, any]]:
        """
        Detect regime changes and transitions.
        
        Args:
            regime_labels: Series with regime labels
            min_duration: Minimum duration for a regime (in periods)
            
        Returns:
            List of regime change events
        """
        logger.info("Detecting regime changes...")
        
        changes = []
        current_regime = None
        regime_start = None
        
        for i, regime in enumerate(regime_labels):
            if regime != current_regime:
                # Regime change detected
                if current_regime is not None and regime_start is not None:
                    duration = i - regime_start
                    if duration >= min_duration:
                        changes.append({
                            'start_index': regime_start,
                            'end_index': i - 1,
                            'regime': current_regime,
                            'duration': duration,
                            'change_index': i
                        })
                
                current_regime = regime
                regime_start = i
        
        # Add final regime
        if current_regime is not None and regime_start is not None:
            duration = len(regime_labels) - regime_start
            if duration >= min_duration:
                changes.append({
                    'start_index': regime_start,
                    'end_index': len(regime_labels) - 1,
                    'regime': current_regime,
                    'duration': duration,
                    'change_index': None
                })
        
        logger.info(f"Detected {len(changes)} regime periods")
        return changes
    
    def analyze_regime_characteristics(
        self,
        prices: pd.Series,
        regime_labels: pd.Series
    ) -> Dict[str, any]:
        """
        Analyze characteristics of each regime.
        
        Args:
            prices: Price series
            regime_labels: Regime labels
            
        Returns:
            Dictionary with regime characteristics
        """
        logger.info("Analyzing regime characteristics...")
        
        # Combine data
        data = pd.DataFrame({
            'price': prices,
            'regime': regime_labels
        }).dropna()
        
        if len(data) == 0:
            return {}
        
        # Calculate returns
        data['returns'] = np.log(data['price'] / data['price'].shift(1))
        
        # Group by regime
        regime_stats = data.groupby('regime').agg({
            'price': ['mean', 'std', 'min', 'max'],
            'returns': ['mean', 'std', 'count']
        })
        
        # Calculate additional metrics
        characteristics = {}
        for regime in data['regime'].unique():
            regime_data = data[data['regime'] == regime]
            
            if len(regime_data) > 0:
                characteristics[regime] = {
                    'mean_price': regime_data['price'].mean(),
                    'price_std': regime_data['price'].std(),
                    'mean_returns': regime_data['returns'].mean(),
                    'returns_std': regime_data['returns'].std(),
                    'volatility': regime_data['returns'].std() * np.sqrt(252),  # Annualized
                    'duration': len(regime_data),
                    'price_range': regime_data['price'].max() - regime_data['price'].min(),
                    'sharpe_ratio': regime_data['returns'].mean() / regime_data['returns'].std() * np.sqrt(252) if regime_data['returns'].std() > 0 else 0
                }
        
        return characteristics

