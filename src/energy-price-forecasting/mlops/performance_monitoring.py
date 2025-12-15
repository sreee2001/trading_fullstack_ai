"""
Model Performance Monitoring.

Tracks predictions vs actuals, calculates rolling metrics, and detects model drift.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PredictionRecord:
    """Record of a prediction made by a model."""
    id: Optional[int] = None
    timestamp: datetime = None
    model_version: str = None  # Model identifier
    commodity: str = None
    horizon: int = None
    prediction: float = None
    actual: Optional[float] = None
    error: Optional[float] = None
    model_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        if self.timestamp:
            data['timestamp'] = self.timestamp.isoformat()
        return data


class PredictionLogger:
    """
    Logs predictions and updates with actual values.
    
    Stores predictions in database for later analysis and monitoring.
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize PredictionLogger.
        
        Args:
            db_manager: Database manager instance (optional)
        """
        self.db_manager = db_manager
        self._in_memory_storage: List[PredictionRecord] = []
        logger.info("PredictionLogger initialized")
    
    def log_prediction(
        self,
        model_version: str,
        commodity: str,
        horizon: int,
        prediction: float,
        model_type: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> int:
        """
        Log a prediction.
        
        Args:
            model_version: Model identifier/version
            commodity: Commodity symbol
            horizon: Forecast horizon in days
            prediction: Predicted value
            model_type: Type of model (optional)
            timestamp: Timestamp of prediction (default: now)
            
        Returns:
            Prediction ID (for later updates)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        record = PredictionRecord(
            timestamp=timestamp,
            model_version=model_version,
            commodity=commodity,
            horizon=horizon,
            prediction=prediction,
            model_type=model_type
        )
        
        # Try to save to database
        if self.db_manager:
            try:
                record_id = self._save_to_database(record)
                record.id = record_id
                logger.debug(f"Logged prediction to database: ID={record_id}")
                return record_id
            except Exception as e:
                logger.warning(f"Failed to save to database: {e}. Using in-memory storage.")
        
        # Fallback to in-memory storage
        record.id = len(self._in_memory_storage)
        self._in_memory_storage.append(record)
        logger.debug(f"Logged prediction to memory: ID={record.id}")
        return record.id
    
    def update_actual(
        self,
        prediction_id: int,
        actual: float,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Update prediction with actual value.
        
        Args:
            prediction_id: ID of the prediction record
            actual: Actual value
            timestamp: Timestamp when actual value was observed
            
        Returns:
            True if update successful
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Try to update in database
        if self.db_manager:
            try:
                return self._update_database(prediction_id, actual, timestamp)
            except Exception as e:
                logger.warning(f"Failed to update database: {e}. Updating in-memory storage.")
        
        # Fallback to in-memory storage
        if 0 <= prediction_id < len(self._in_memory_storage):
            record = self._in_memory_storage[prediction_id]
            record.actual = actual
            record.error = abs(record.prediction - actual)
            logger.debug(f"Updated prediction {prediction_id} with actual: {actual}")
            return True
        
        logger.warning(f"Prediction ID {prediction_id} not found")
        return False
    
    def _save_to_database(self, record: PredictionRecord) -> int:
        """Save prediction record to database."""
        # Placeholder - actual implementation would use database manager
        # CREATE TABLE IF NOT EXISTS predictions (
        #     id SERIAL PRIMARY KEY,
        #     timestamp TIMESTAMP NOT NULL,
        #     model_version VARCHAR(100) NOT NULL,
        #     commodity VARCHAR(10) NOT NULL,
        #     horizon INTEGER NOT NULL,
        #     prediction FLOAT NOT NULL,
        #     actual FLOAT,
        #     error FLOAT,
        #     model_type VARCHAR(50)
        # );
        logger.debug("Database save not implemented - using placeholder")
        return len(self._in_memory_storage)
    
    def _update_database(self, prediction_id: int, actual: float, timestamp: datetime) -> bool:
        """Update prediction record in database."""
        # Placeholder - actual implementation would use database manager
        logger.debug("Database update not implemented - using placeholder")
        return True
    
    def get_predictions(
        self,
        model_version: Optional[str] = None,
        commodity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        with_actual_only: bool = False
    ) -> List[PredictionRecord]:
        """
        Get predictions matching criteria.
        
        Args:
            model_version: Filter by model version
            commodity: Filter by commodity
            start_date: Filter by start date
            end_date: Filter by end date
            with_actual_only: Only return predictions with actual values
            
        Returns:
            List of prediction records
        """
        records = self._in_memory_storage.copy()
        
        if model_version:
            records = [r for r in records if r.model_version == model_version]
        
        if commodity:
            records = [r for r in records if r.commodity == commodity]
        
        if start_date:
            records = [r for r in records if r.timestamp >= start_date]
        
        if end_date:
            records = [r for r in records if r.timestamp <= end_date]
        
        if with_actual_only:
            records = [r for r in records if r.actual is not None]
        
        return records


class RollingMetricsCalculator:
    """
    Calculates rolling performance metrics over time windows.
    
    Computes metrics like RMSE, MAE, MAPE, and directional accuracy
    over rolling windows (e.g., last 7 days, last 30 days).
    """
    
    def __init__(self, logger: PredictionLogger):
        """
        Initialize RollingMetricsCalculator.
        
        Args:
            logger: PredictionLogger instance
        """
        self.logger = logger
        logger.info("RollingMetricsCalculator initialized")
    
    def calculate_rolling_metrics(
        self,
        window_days: int = 7,
        model_version: Optional[str] = None,
        commodity: Optional[str] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate rolling metrics over a time window.
        
        Args:
            window_days: Number of days in rolling window
            model_version: Filter by model version
            commodity: Filter by commodity
            end_date: End date for window (default: now)
            
        Returns:
            Dictionary with metrics
        """
        if end_date is None:
            end_date = datetime.now()
        
        start_date = end_date - timedelta(days=window_days)
        
        # Get predictions with actuals
        predictions = self.logger.get_predictions(
            model_version=model_version,
            commodity=commodity,
            start_date=start_date,
            end_date=end_date,
            with_actual_only=True
        )
        
        if len(predictions) == 0:
            return {
                'window_days': window_days,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'sample_count': 0,
                'message': 'No predictions with actual values in window'
            }
        
        # Extract values
        pred_values = [p.prediction for p in predictions]
        actual_values = [p.actual for p in predictions]
        errors = [p.error for p in predictions if p.error is not None]
        
        # Calculate metrics
        metrics = {
            'window_days': window_days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'sample_count': len(predictions),
            'mae': np.mean(errors) if errors else None,
            'rmse': np.sqrt(np.mean([e**2 for e in errors])) if errors else None,
            'mape': np.mean([abs(e / a) for e, a in zip(errors, actual_values) if a != 0]) if actual_values else None,
            'mean_prediction': np.mean(pred_values) if pred_values else None,
            'mean_actual': np.mean(actual_values) if actual_values else None,
        }
        
        # Calculate directional accuracy
        if len(predictions) > 1:
            directional_correct = 0
            for i in range(1, len(predictions)):
                pred_dir = pred_values[i] > pred_values[i-1]
                actual_dir = actual_values[i] > actual_values[i-1]
                if pred_dir == actual_dir:
                    directional_correct += 1
            metrics['directional_accuracy'] = directional_correct / (len(predictions) - 1)
        
        return metrics
    
    def calculate_multiple_windows(
        self,
        windows: List[int] = [7, 30],
        model_version: Optional[str] = None,
        commodity: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate metrics for multiple rolling windows.
        
        Args:
            windows: List of window sizes in days
            model_version: Filter by model version
            commodity: Filter by commodity
            
        Returns:
            Dictionary with metrics for each window
        """
        results = {}
        for window in windows:
            results[f'{window}_day'] = self.calculate_rolling_metrics(
                window_days=window,
                model_version=model_version,
                commodity=commodity
            )
        return results


class DriftDetector:
    """
    Detects data drift and model performance degradation.
    
    Compares recent data distributions and performance metrics
    against baseline (training) data to detect drift.
    """
    
    def __init__(self, logger: PredictionLogger):
        """
        Initialize DriftDetector.
        
        Args:
            logger: PredictionLogger instance
        """
        self.logger = logger
        self.baseline_metrics: Dict[str, Any] = {}
        logger.info("DriftDetector initialized")
    
    def set_baseline(
        self,
        metrics: Dict[str, float],
        model_version: Optional[str] = None,
        commodity: Optional[str] = None
    ):
        """
        Set baseline metrics for drift detection.
        
        Args:
            metrics: Dictionary of baseline metrics (e.g., {'mae': 2.5, 'rmse': 3.0})
            model_version: Model version identifier
            commodity: Commodity identifier
        """
        key = f"{model_version}_{commodity}" if model_version and commodity else "default"
        self.baseline_metrics[key] = metrics
        logger.info(f"Set baseline metrics for {key}: {metrics}")
    
    def detect_performance_drift(
        self,
        window_days: int = 30,
        model_version: Optional[str] = None,
        commodity: Optional[str] = None,
        degradation_threshold: float = 0.20  # 20% degradation
    ) -> Dict[str, Any]:
        """
        Detect performance degradation (model drift).
        
        Args:
            window_days: Window size for recent metrics
            model_version: Model version to check
            commodity: Commodity to check
            degradation_threshold: Threshold for degradation (default: 20%)
            
        Returns:
            Dictionary with drift detection results
        """
        key = f"{model_version}_{commodity}" if model_version and commodity else "default"
        baseline = self.baseline_metrics.get(key)
        
        if not baseline:
            return {
                'drift_detected': False,
                'reason': 'No baseline metrics set',
                'baseline': None
            }
        
        # Calculate recent metrics
        calculator = RollingMetricsCalculator(self.logger)
        recent_metrics = calculator.calculate_rolling_metrics(
            window_days=window_days,
            model_version=model_version,
            commodity=commodity
        )
        
        if recent_metrics.get('sample_count', 0) == 0:
            return {
                'drift_detected': False,
                'reason': 'Insufficient recent data',
                'baseline': baseline,
                'recent': recent_metrics
            }
        
        # Compare metrics
        drift_detected = False
        degradations = {}
        
        for metric in ['mae', 'rmse', 'mape']:
            baseline_value = baseline.get(metric)
            recent_value = recent_metrics.get(metric)
            
            if baseline_value and recent_value and baseline_value > 0:
                degradation = (recent_value - baseline_value) / baseline_value
                degradations[metric] = degradation
                
                if degradation > degradation_threshold:
                    drift_detected = True
        
        # Check directional accuracy degradation
        baseline_da = baseline.get('directional_accuracy')
        recent_da = recent_metrics.get('directional_accuracy')
        
        if baseline_da and recent_da:
            degradation = (baseline_da - recent_da) / baseline_da
            degradations['directional_accuracy'] = degradation
            
            if degradation > degradation_threshold:
                drift_detected = True
        
        result = {
            'drift_detected': drift_detected,
            'baseline': baseline,
            'recent': recent_metrics,
            'degradations': degradations,
            'degradation_threshold': degradation_threshold
        }
        
        if drift_detected:
            logger.warning(f"Performance drift detected for {key}: {degradations}")
        else:
            logger.info(f"No performance drift detected for {key}")
        
        return result
    
    def detect_data_drift(
        self,
        recent_data: pd.Series,
        baseline_data: pd.Series,
        test_type: str = 'ks'  # 'ks' (Kolmogorov-Smirnov) or 'chi2'
    ) -> Dict[str, Any]:
        """
        Detect data distribution drift using statistical tests.
        
        Args:
            recent_data: Recent data distribution
            baseline_data: Baseline (training) data distribution
            test_type: Type of statistical test ('ks' or 'chi2')
            
        Returns:
            Dictionary with drift detection results
        """
        try:
            from scipy import stats
        except ImportError:
            logger.warning("scipy not available for statistical tests")
            return {
                'drift_detected': False,
                'reason': 'scipy not available',
                'test_type': test_type
            }
        
        if test_type == 'ks':
            # Kolmogorov-Smirnov test
            statistic, p_value = stats.ks_2samp(baseline_data, recent_data)
            drift_detected = p_value < 0.05  # Significance level
            
            return {
                'drift_detected': drift_detected,
                'test_type': 'ks',
                'statistic': statistic,
                'p_value': p_value,
                'significance_level': 0.05
            }
        
        elif test_type == 'chi2':
            # Chi-square test (for categorical or binned data)
            # This is a simplified version - would need proper binning
            logger.warning("Chi-square test not fully implemented")
            return {
                'drift_detected': False,
                'reason': 'Chi-square test not implemented',
                'test_type': 'chi2'
            }
        
        else:
            return {
                'drift_detected': False,
                'reason': f'Unknown test type: {test_type}',
                'test_type': test_type
            }

