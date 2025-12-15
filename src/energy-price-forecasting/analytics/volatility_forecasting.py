"""
Volatility Forecasting using GARCH Models.

Forecasts volatility of energy commodity prices using GARCH (Generalized
Autoregressive Conditional Heteroskedasticity) models.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

try:
    from arch import arch_model
    ARCH_AVAILABLE = True
except ImportError:
    ARCH_AVAILABLE = False
    arch_model = None

logger = logging.getLogger(__name__)


class VolatilityForecaster:
    """
    Forecasts volatility using GARCH models.
    
    Provides methods to fit GARCH models and forecast future volatility
    for energy commodity prices.
    """
    
    def __init__(self):
        """Initialize VolatilityForecaster."""
        if not ARCH_AVAILABLE:
            logger.warning("arch library not available - GARCH models will not work")
        logger.info("VolatilityForecaster initialized")
    
    def calculate_returns(self, prices: pd.Series, method: str = 'log') -> pd.Series:
        """
        Calculate returns from price series.
        
        Args:
            prices: Price series
            method: Return calculation method ('log' or 'simple')
            
        Returns:
            Returns series
        """
        if method == 'log':
            returns = np.log(prices / prices.shift(1))
        else:  # simple
            returns = (prices - prices.shift(1)) / prices.shift(1)
        
        return returns.dropna()
    
    def calculate_realized_volatility(
        self,
        returns: pd.Series,
        window: int = 30,
        annualized: bool = True
    ) -> pd.Series:
        """
        Calculate realized volatility (rolling standard deviation).
        
        Args:
            returns: Returns series
            window: Rolling window size
            annualized: Whether to annualize volatility
            
        Returns:
            Realized volatility series
        """
        volatility = returns.rolling(window=window).std()
        
        if annualized:
            # Annualize: multiply by sqrt(252) for daily data
            volatility = volatility * np.sqrt(252)
        
        return volatility
    
    def fit_garch_model(
        self,
        returns: pd.Series,
        p: int = 1,
        q: int = 1,
        vol: str = 'GARCH',
        dist: str = 'normal'
    ) -> Optional[any]:
        """
        Fit a GARCH model to returns.
        
        Args:
            returns: Returns series
            p: GARCH order (lag of ARCH terms)
            q: ARCH order (lag of squared residuals)
            vol: Volatility model ('GARCH', 'EGARCH', 'GJR-GARCH')
            dist: Distribution ('normal', 't', 'skewt')
            
        Returns:
            Fitted GARCH model or None
        """
        if not ARCH_AVAILABLE:
            logger.error("arch library required for GARCH models")
            return None
        
        if len(returns) < 100:
            logger.warning(f"Insufficient data for GARCH model (need at least 100 points, got {len(returns)})")
            return None
        
        logger.info(f"Fitting GARCH({p},{q}) model with {vol} volatility...")
        
        try:
            model = arch_model(
                returns * 100,  # Scale returns (arch expects percentage)
                vol=vol,
                p=p,
                q=q,
                dist=dist
            )
            
            fitted_model = model.fit(disp='off')
            
            logger.info(f"GARCH model fitted successfully")
            return fitted_model
            
        except Exception as e:
            logger.error(f"Failed to fit GARCH model: {e}", exc_info=True)
            return None
    
    def forecast_volatility(
        self,
        model: any,
        horizon: int = 1,
        start: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Forecast volatility using fitted GARCH model.
        
        Args:
            model: Fitted GARCH model
            horizon: Forecast horizon (number of periods)
            start: Starting point for forecast (None = end of sample)
            
        Returns:
            Dictionary with volatility forecasts
        """
        if model is None:
            return {
                'forecast': None,
                'error': 'Model not available'
            }
        
        try:
            forecast = model.forecast(horizon=horizon, start=start)
            
            # Extract volatility forecasts
            variance_forecast = forecast.variance.values[-1]
            volatility_forecast = np.sqrt(variance_forecast) / 100  # Convert back from percentage
            
            return {
                'forecast': volatility_forecast,
                'variance_forecast': variance_forecast,
                'mean_volatility': np.mean(volatility_forecast),
                'horizon': horizon
            }
            
        except Exception as e:
            logger.error(f"Failed to forecast volatility: {e}", exc_info=True)
            return {
                'forecast': None,
                'error': str(e)
            }
    
    def analyze_volatility_clustering(
        self,
        returns: pd.Series,
        window: int = 30
    ) -> Dict[str, float]:
        """
        Analyze volatility clustering (ARCH effects).
        
        Args:
            returns: Returns series
            window: Window size for analysis
            
        Returns:
            Dictionary with clustering metrics
        """
        # Calculate squared returns (proxy for volatility)
        squared_returns = returns ** 2
        
        # Calculate autocorrelation of squared returns
        autocorr = squared_returns.autocorr(lag=1)
        
        # Ljung-Box test for serial correlation
        if ARCH_AVAILABLE:
            try:
                from arch.unitroot import LjungBox
                lb_test = LjungBox(squared_returns.dropna(), lags=10)
                lb_stat = lb_test.stat
                lb_pvalue = lb_test.pvalue
            except:
                lb_stat = None
                lb_pvalue = None
        else:
            lb_stat = None
            lb_pvalue = None
        
        # Calculate rolling volatility
        rolling_vol = self.calculate_realized_volatility(returns, window=window)
        
        return {
            'autocorrelation_squared_returns': autocorr,
            'ljung_box_statistic': lb_stat,
            'ljung_box_pvalue': lb_pvalue,
            'has_clustering': autocorr > 0.1 if not np.isnan(autocorr) else False,
            'mean_volatility': rolling_vol.mean(),
            'volatility_std': rolling_vol.std()
        }
    
    def compare_volatility_models(
        self,
        returns: pd.Series,
        models: List[Tuple[int, int, str]] = None
    ) -> pd.DataFrame:
        """
        Compare different GARCH model specifications.
        
        Args:
            returns: Returns series
            models: List of (p, q, vol) tuples to compare
            
        Returns:
            DataFrame with model comparison results
        """
        if models is None:
            models = [
                (1, 1, 'GARCH'),
                (1, 2, 'GARCH'),
                (2, 1, 'GARCH'),
                (1, 1, 'EGARCH'),
                (1, 1, 'GJR-GARCH')
            ]
        
        results = []
        
        for p, q, vol in models:
            model = self.fit_garch_model(returns, p=p, q=q, vol=vol)
            
            if model is not None:
                try:
                    aic = model.aic
                    bic = model.bic
                    log_likelihood = model.loglikelihood
                    
                    results.append({
                        'p': p,
                        'q': q,
                        'vol': vol,
                        'aic': aic,
                        'bic': bic,
                        'log_likelihood': log_likelihood
                    })
                except:
                    pass
        
        if results:
            df = pd.DataFrame(results)
            df = df.sort_values('aic')  # Lower AIC is better
            return df
        else:
            return pd.DataFrame()


class VolatilityMetrics:
    """
    Calculates various volatility metrics.
    
    Provides methods to calculate historical volatility, realized volatility,
    and other volatility-related metrics.
    """
    
    @staticmethod
    def calculate_historical_volatility(
        prices: pd.Series,
        window: int = 30,
        annualized: bool = True
    ) -> pd.Series:
        """
        Calculate historical volatility (rolling standard deviation of returns).
        
        Args:
            prices: Price series
            window: Rolling window size
            annualized: Whether to annualize
            
        Returns:
            Historical volatility series
        """
        returns = np.log(prices / prices.shift(1))
        volatility = returns.rolling(window=window).std()
        
        if annualized:
            volatility = volatility * np.sqrt(252)
        
        return volatility
    
    @staticmethod
    def calculate_parkinson_volatility(
        high: pd.Series,
        low: pd.Series,
        annualized: bool = True
    ) -> pd.Series:
        """
        Calculate Parkinson volatility estimator (uses high-low range).
        
        Args:
            high: High price series
            low: Low price series
            annualized: Whether to annualize
            
        Returns:
            Parkinson volatility series
        """
        # Parkinson estimator: sqrt(1/(4*ln(2)) * ln(high/low)^2)
        volatility = np.sqrt(1 / (4 * np.log(2)) * np.log(high / low) ** 2)
        
        if annualized:
            volatility = volatility * np.sqrt(252)
        
        return volatility
    
    @staticmethod
    def calculate_garman_klass_volatility(
        high: pd.Series,
        low: pd.Series,
        open_price: pd.Series,
        close_price: pd.Series,
        annualized: bool = True
    ) -> pd.Series:
        """
        Calculate Garman-Klass volatility estimator (uses OHLC data).
        
        Args:
            high: High price series
            low: Low price series
            open_price: Open price series
            close_price: Close price series
            annualized: Whether to annualize
            
        Returns:
            Garman-Klass volatility series
        """
        # Garman-Klass estimator
        volatility = np.sqrt(
            0.5 * (np.log(high / low) ** 2) -
            (2 * np.log(2) - 1) * (np.log(close_price / open_price) ** 2)
        )
        
        if annualized:
            volatility = volatility * np.sqrt(252)
        
        return volatility

