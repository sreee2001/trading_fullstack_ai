"""
Automated Insight Generation from Analytics.

Generates natural language insights from analytical results including
correlations, seasonality, volatility, anomalies, and regime changes.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class InsightGenerator:
    """
    Generates natural language insights from analytical results.
    
    Provides template-based insight generation for various analytics
    including correlations, seasonality, volatility, anomalies, and regimes.
    """
    
    def __init__(self):
        """Initialize InsightGenerator."""
        logger.info("InsightGenerator initialized")
    
    def generate_correlation_insights(
        self,
        correlation_results: Dict[str, Any]
    ) -> List[str]:
        """
        Generate insights from correlation analysis.
        
        Args:
            correlation_results: Results from CorrelationAnalyzer
            
        Returns:
            List of insight strings
        """
        insights = []
        
        strong_corrs = correlation_results.get('strong_correlations', [])
        commodity_corrs = correlation_results.get('commodity_correlations', [])
        
        # Strong correlations insights
        if strong_corrs:
            for corr in strong_corrs[:5]:  # Top 5
                var1 = corr['variable1']
                var2 = corr['variable2']
                corr_value = corr['correlation']
                
                if abs(corr_value) > 0.9:
                    strength = "extremely high"
                elif abs(corr_value) > 0.7:
                    strength = "high"
                else:
                    strength = "moderate"
                
                direction = "positive" if corr_value > 0 else "negative"
                
                insight = (
                    f"{var1} and {var2} show {strength} {direction} correlation "
                    f"({corr_value:.2f}). "
                )
                
                if abs(corr_value) > 0.8:
                    insight += "These commodities tend to move together."
                
                insights.append(insight)
        
        # Commodity-specific insights
        if commodity_corrs:
            for corr in commodity_corrs:
                comm1 = corr['commodity1']
                comm2 = corr['commodity2']
                corr_value = corr.get('correlation', 0)
                
                if abs(corr_value) > 0.7:
                    insight = (
                        f"{comm1} and {comm2} prices are highly correlated "
                        f"({corr_value:.2f}), suggesting similar market dynamics."
                    )
                    insights.append(insight)
        
        return insights
    
    def generate_seasonality_insights(
        self,
        seasonality_results: Dict[str, Any]
    ) -> List[str]:
        """
        Generate insights from seasonality analysis.
        
        Args:
            seasonality_results: Results from SeasonalityAnalyzer
            
        Returns:
            List of insight strings
        """
        insights = []
        
        has_seasonality = seasonality_results.get('has_seasonality', False)
        
        if not has_seasonality:
            insights.append("No significant seasonality detected in the price data.")
            return insights
        
        patterns = seasonality_results.get('patterns', {})
        detection = seasonality_results.get('detection', {})
        
        period = detection.get('detected_period')
        if period:
            if period == 7:
                period_name = "weekly"
            elif period == 30:
                period_name = "monthly"
            elif period == 365:
                period_name = "annual"
            else:
                period_name = f"{period}-day"
            
            insights.append(
                f"Strong {period_name} seasonality detected (period: {period} days)."
            )
        
        # Peak and trough insights
        if patterns:
            peak = patterns.get('peak_period')
            trough = patterns.get('trough_period')
            amplitude = patterns.get('amplitude', 0)
            
            if peak and trough:
                insights.append(
                    f"Seasonal pattern shows peak around {peak} and trough around {trough}."
                )
            
            if amplitude > 0:
                insights.append(
                    f"Seasonal amplitude: {amplitude:.2f}, indicating "
                    f"{'strong' if amplitude > patterns.get('mean', 0) * 0.1 else 'moderate'} "
                    "seasonal variation."
                )
        
        # Seasonal strength
        strength_metrics = seasonality_results.get('strength_metrics', {})
        seasonal_strength = strength_metrics.get('seasonal_strength', 0)
        
        if seasonal_strength > 0.5:
            insights.append(
                f"High seasonal strength ({seasonal_strength:.2%}), "
                "indicating strong seasonal patterns."
            )
        
        return insights
    
    def generate_volatility_insights(
        self,
        volatility_results: Dict[str, Any],
        commodity: str = "commodity"
    ) -> List[str]:
        """
        Generate insights from volatility analysis.
        
        Args:
            volatility_results: Results from VolatilityForecaster
            commodity: Commodity name
            
        Returns:
            List of insight strings
        """
        insights = []
        
        forecast = volatility_results.get('forecast')
        if forecast is not None:
            mean_vol = volatility_results.get('mean_volatility', 0)
            horizon = volatility_results.get('horizon', 1)
            
            insights.append(
                f"Forecasted volatility for {commodity} over next {horizon} periods: "
                f"{mean_vol:.2%} (annualized)."
            )
        
        # Clustering analysis
        clustering = volatility_results.get('clustering_analysis', {})
        has_clustering = clustering.get('has_clustering', False)
        
        if has_clustering:
            insights.append(
                "Volatility clustering detected, indicating periods of high volatility "
                "tend to be followed by more high volatility."
            )
        
        return insights
    
    def generate_anomaly_insights(
        self,
        anomaly_results: pd.DataFrame,
        commodity: str = "commodity"
    ) -> List[str]:
        """
        Generate insights from anomaly detection.
        
        Args:
            anomaly_results: DataFrame with anomaly flags
            commodity: Commodity name
            
        Returns:
            List of insight strings
        """
        insights = []
        
        if len(anomaly_results) == 0:
            return insights
        
        anomaly_count = anomaly_results.get('is_anomaly', pd.Series()).sum()
        total_count = len(anomaly_results)
        
        if anomaly_count > 0:
            percentage = (anomaly_count / total_count) * 100
            
            insights.append(
                f"Detected {anomaly_count} anomalies ({percentage:.1f}%) "
                f"in {commodity} price data."
            )
            
            # Get most recent anomalies
            recent_anomalies = anomaly_results[anomaly_results['is_anomaly']].tail(5)
            
            if len(recent_anomalies) > 0:
                latest = recent_anomalies.index[-1]
                latest_value = recent_anomalies.iloc[-1].get('value', 'N/A')
                
                insights.append(
                    f"Most recent anomaly detected on {latest} with value {latest_value}."
                )
        else:
            insights.append(f"No anomalies detected in {commodity} price data.")
        
        return insights
    
    def generate_regime_insights(
        self,
        regime_results: Dict[str, Any],
        commodity: str = "commodity"
    ) -> List[str]:
        """
        Generate insights from market regime detection.
        
        Args:
            regime_results: Results from MarketRegimeDetector
            commodity: Commodity name
            
        Returns:
            List of insight strings
        """
        insights = []
        
        characteristics = regime_results.get('characteristics', {})
        changes = regime_results.get('regime_changes', [])
        
        if characteristics:
            insights.append(
                f"Identified {len(characteristics)} distinct market regimes "
                f"for {commodity}."
            )
            
            # Describe each regime
            for regime, stats in characteristics.items():
                mean_returns = stats.get('mean_returns', 0)
                volatility = stats.get('volatility', 0)
                duration = stats.get('duration', 0)
                
                if mean_returns > 0:
                    trend = "bullish"
                elif mean_returns < 0:
                    trend = "bearish"
                else:
                    trend = "neutral"
                
                vol_level = "high" if volatility > 0.3 else "low"
                
                insights.append(
                    f"{regime}: {trend} trend with {vol_level} volatility "
                    f"({volatility:.2%}), lasting {duration} periods."
                )
        
        if changes:
            insights.append(
                f"Detected {len(changes)} regime transitions over the analysis period."
            )
            
            # Most recent change
            if changes:
                latest_change = changes[-1]
                insights.append(
                    f"Current regime: {latest_change.get('regime', 'Unknown')}, "
                    f"started {latest_change.get('duration', 0)} periods ago."
                )
        
        return insights
    
    def generate_comprehensive_insights(
        self,
        correlation_results: Optional[Dict[str, Any]] = None,
        seasonality_results: Optional[Dict[str, Any]] = None,
        volatility_results: Optional[Dict[str, Any]] = None,
        anomaly_results: Optional[pd.DataFrame] = None,
        regime_results: Optional[Dict[str, Any]] = None,
        commodity: str = "commodity"
    ) -> Dict[str, List[str]]:
        """
        Generate comprehensive insights from all analytics.
        
        Args:
            correlation_results: Correlation analysis results
            seasonality_results: Seasonality analysis results
            volatility_results: Volatility analysis results
            anomaly_results: Anomaly detection results
            regime_results: Market regime detection results
            commodity: Commodity name
            
        Returns:
            Dictionary with insights by category
        """
        logger.info(f"Generating comprehensive insights for {commodity}...")
        
        all_insights = {
            'correlation': [],
            'seasonality': [],
            'volatility': [],
            'anomalies': [],
            'regimes': [],
            'summary': []
        }
        
        # Generate insights for each category
        if correlation_results:
            all_insights['correlation'] = self.generate_correlation_insights(
                correlation_results
            )
        
        if seasonality_results:
            all_insights['seasonality'] = self.generate_seasonality_insights(
                seasonality_results
            )
        
        if volatility_results:
            all_insights['volatility'] = self.generate_volatility_insights(
                volatility_results,
                commodity=commodity
            )
        
        if anomaly_results is not None:
            all_insights['anomalies'] = self.generate_anomaly_insights(
                anomaly_results,
                commodity=commodity
            )
        
        if regime_results:
            all_insights['regimes'] = self.generate_regime_insights(
                regime_results,
                commodity=commodity
            )
        
        # Generate summary
        total_insights = sum(len(v) for v in all_insights.values())
        all_insights['summary'].append(
            f"Generated {total_insights} insights across "
            f"{sum(1 for v in all_insights.values() if v)} analytical categories."
        )
        
        logger.info(f"Generated {total_insights} insights")
        return all_insights
    
    def format_insights_for_display(
        self,
        insights: Dict[str, List[str]],
        max_per_category: int = 5
    ) -> str:
        """
        Format insights for display in dashboard.
        
        Args:
            insights: Dictionary of insights by category
            max_per_category: Maximum insights per category
            
        Returns:
            Formatted string
        """
        formatted = []
        
        category_names = {
            'correlation': 'Correlation Analysis',
            'seasonality': 'Seasonality Patterns',
            'volatility': 'Volatility Forecasts',
            'anomalies': 'Anomaly Detection',
            'regimes': 'Market Regimes',
            'summary': 'Summary'
        }
        
        for category, category_insights in insights.items():
            if category_insights:
                category_name = category_names.get(category, category.title())
                formatted.append(f"## {category_name}\n")
                
                for i, insight in enumerate(category_insights[:max_per_category]):
                    formatted.append(f"{i+1}. {insight}\n")
                
                formatted.append("\n")
        
        return "".join(formatted)

