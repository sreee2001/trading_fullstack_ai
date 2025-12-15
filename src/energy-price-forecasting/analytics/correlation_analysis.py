"""
Correlation Analysis for Energy Commodities.

Analyzes correlations between different energy commodities and external factors
to identify relationships and dependencies.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class CorrelationAnalyzer:
    """
    Analyzes correlations between energy commodities and external factors.
    
    Provides methods to calculate correlation coefficients, identify
    significant relationships, and visualize correlation matrices.
    """
    
    def __init__(self):
        """Initialize CorrelationAnalyzer."""
        logger.info("CorrelationAnalyzer initialized")
    
    def calculate_correlation_matrix(
        self,
        data: pd.DataFrame,
        method: str = 'pearson',
        min_periods: int = 30
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for all numeric columns.
        
        Args:
            data: DataFrame with time series data
            method: Correlation method ('pearson', 'spearman', 'kendall')
            min_periods: Minimum number of observations required
            
        Returns:
            Correlation matrix DataFrame
        """
        logger.info(f"Calculating {method} correlation matrix...")
        
        # Select only numeric columns
        numeric_data = data.select_dtypes(include=[np.number])
        
        if len(numeric_data.columns) < 2:
            logger.warning("Insufficient numeric columns for correlation analysis")
            return pd.DataFrame()
        
        # Calculate correlation
        corr_matrix = numeric_data.corr(method=method, min_periods=min_periods)
        
        logger.info(f"Correlation matrix calculated: {len(corr_matrix)}x{len(corr_matrix)}")
        return corr_matrix
    
    def calculate_pairwise_correlation(
        self,
        series1: pd.Series,
        series2: pd.Series,
        method: str = 'pearson'
    ) -> Dict[str, float]:
        """
        Calculate correlation between two time series.
        
        Args:
            series1: First time series
            series2: Second time series
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            Dictionary with correlation coefficient and p-value
        """
        # Align series by index
        aligned = pd.DataFrame({
            'series1': series1,
            'series2': series2
        }).dropna()
        
        if len(aligned) < 30:
            logger.warning(f"Insufficient data points ({len(aligned)}) for correlation")
            return {
                'correlation': np.nan,
                'p_value': np.nan,
                'sample_size': len(aligned)
            }
        
        if method == 'pearson':
            corr, p_value = stats.pearsonr(aligned['series1'], aligned['series2'])
        elif method == 'spearman':
            corr, p_value = stats.spearmanr(aligned['series1'], aligned['series2'])
        elif method == 'kendall':
            corr, p_value = stats.kendalltau(aligned['series1'], aligned['series2'])
        else:
            raise ValueError(f"Unknown correlation method: {method}")
        
        return {
            'correlation': corr,
            'p_value': p_value,
            'sample_size': len(aligned),
            'method': method
        }
    
    def find_strong_correlations(
        self,
        corr_matrix: pd.DataFrame,
        threshold: float = 0.7,
        exclude_diagonal: bool = True
    ) -> List[Dict[str, any]]:
        """
        Find pairs with strong correlations.
        
        Args:
            corr_matrix: Correlation matrix
            threshold: Minimum absolute correlation value
            exclude_diagonal: Exclude diagonal (self-correlations)
            
        Returns:
            List of dictionaries with correlation pairs
        """
        strong_correlations = []
        
        for i, col1 in enumerate(corr_matrix.columns):
            for j, col2 in enumerate(corr_matrix.columns):
                if exclude_diagonal and i == j:
                    continue
                
                corr_value = corr_matrix.loc[col1, col2]
                
                if not np.isnan(corr_value) and abs(corr_value) >= threshold:
                    strong_correlations.append({
                        'variable1': col1,
                        'variable2': col2,
                        'correlation': corr_value,
                        'abs_correlation': abs(corr_value)
                    })
        
        # Sort by absolute correlation (descending)
        strong_correlations.sort(key=lambda x: x['abs_correlation'], reverse=True)
        
        logger.info(f"Found {len(strong_correlations)} strong correlations (|r| >= {threshold})")
        return strong_correlations
    
    def calculate_lagged_correlation(
        self,
        series1: pd.Series,
        series2: pd.Series,
        max_lag: int = 30,
        method: str = 'pearson'
    ) -> pd.DataFrame:
        """
        Calculate correlation at different lags (lead/lag analysis).
        
        Args:
            series1: First time series
            series2: Second time series
            max_lag: Maximum lag to test (in periods)
            method: Correlation method
            
        Returns:
            DataFrame with lag and correlation values
        """
        logger.info(f"Calculating lagged correlations (max_lag={max_lag})...")
        
        results = []
        
        for lag in range(-max_lag, max_lag + 1):
            if lag == 0:
                shifted_series2 = series2
            elif lag > 0:
                # series2 leads series1
                shifted_series2 = series2.shift(-lag)
            else:
                # series2 lags series1
                shifted_series2 = series2.shift(-lag)
            
            # Align and calculate correlation
            aligned = pd.DataFrame({
                'series1': series1,
                'series2': shifted_series2
            }).dropna()
            
            if len(aligned) < 30:
                continue
            
            if method == 'pearson':
                corr, _ = stats.pearsonr(aligned['series1'], aligned['series2'])
            elif method == 'spearman':
                corr, _ = stats.spearmanr(aligned['series1'], aligned['series2'])
            else:
                corr = aligned['series1'].corr(aligned['series2'], method=method)
            
            results.append({
                'lag': lag,
                'correlation': corr,
                'abs_correlation': abs(corr)
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values('abs_correlation', ascending=False)
        
        logger.info(f"Lagged correlation analysis complete")
        return df
    
    def analyze_commodity_correlations(
        self,
        price_data: Dict[str, pd.Series],
        external_factors: Optional[Dict[str, pd.Series]] = None
    ) -> Dict[str, any]:
        """
        Analyze correlations between commodities and external factors.
        
        Args:
            price_data: Dictionary of commodity price series
            external_factors: Optional dictionary of external factor series
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("Analyzing commodity correlations...")
        
        # Combine all data
        all_data = {}
        all_data.update(price_data)
        if external_factors:
            all_data.update(external_factors)
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Calculate correlation matrix
        corr_matrix = self.calculate_correlation_matrix(df)
        
        # Find strong correlations
        strong_corrs = self.find_strong_correlations(corr_matrix, threshold=0.7)
        
        # Analyze commodity-to-commodity correlations
        commodity_corrs = []
        commodity_names = list(price_data.keys())
        
        for i, comm1 in enumerate(commodity_names):
            for comm2 in commodity_names[i+1:]:
                if comm1 in df.columns and comm2 in df.columns:
                    result = self.calculate_pairwise_correlation(
                        df[comm1],
                        df[comm2]
                    )
                    commodity_corrs.append({
                        'commodity1': comm1,
                        'commodity2': comm2,
                        **result
                    })
        
        return {
            'correlation_matrix': corr_matrix,
            'strong_correlations': strong_corrs,
            'commodity_correlations': commodity_corrs,
            'summary': {
                'total_variables': len(df.columns),
                'strong_correlations_count': len(strong_corrs),
                'commodity_pairs': len(commodity_corrs)
            }
        }

