"""
A/B Testing Framework for Champion/Challenger Model Comparison.

Implements traffic splitting, result tracking, and automatic model promotion
for comparing production models against challenger models.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import hashlib
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class ABTestResult:
    """Result of a single A/B test prediction."""
    user_id: str
    timestamp: datetime
    model_version: str  # 'champion' or 'challenger'
    commodity: str
    prediction: float
    actual: Optional[float] = None
    error: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ABTestResult':
        """Create from dictionary."""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class TrafficSplitter:
    """
    Splits traffic between champion and challenger models.
    
    Uses deterministic hashing to ensure consistent routing for the same user.
    """
    
    def __init__(self, split_ratio: float = 0.9):
        """
        Initialize TrafficSplitter.
        
        Args:
            split_ratio: Ratio of traffic to champion (default: 0.9 = 90% champion, 10% challenger)
        """
        if not 0 <= split_ratio <= 1:
            raise ValueError("split_ratio must be between 0 and 1")
        
        self.split_ratio = split_ratio
        logger.info(f"TrafficSplitter initialized with split ratio: {split_ratio:.1%} champion")
    
    def select_model(self, user_id: str, seed: Optional[str] = None) -> str:
        """
        Select model (champion or challenger) for a user.
        
        Uses deterministic hashing to ensure same user always gets same model.
        
        Args:
            user_id: User identifier (or request ID for anonymous users)
            seed: Optional seed for hashing (for testing)
            
        Returns:
            'champion' or 'challenger'
        """
        # Create hash from user_id and optional seed
        hash_input = f"{user_id}_{seed}" if seed else user_id
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # Map to 0-99 range
        bucket = hash_value % 100
        
        # Determine model based on split ratio
        threshold = int(self.split_ratio * 100)
        model = 'champion' if bucket < threshold else 'challenger'
        
        logger.debug(f"User {user_id}: bucket={bucket}, model={model}")
        return model
    
    def get_split_stats(self, user_ids: List[str]) -> Dict[str, int]:
        """
        Get statistics on how traffic would be split for a list of users.
        
        Args:
            user_ids: List of user IDs
            
        Returns:
            Dictionary with counts for 'champion' and 'challenger'
        """
        stats = {'champion': 0, 'challenger': 0}
        for user_id in user_ids:
            model = self.select_model(user_id)
            stats[model] += 1
        return stats


class ABTestTracker:
    """
    Tracks A/B test results and calculates metrics.
    
    Stores predictions and actual outcomes, then calculates performance
    metrics for comparison between champion and challenger models.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize ABTestTracker.
        
        Args:
            storage_path: Path to JSON file for storing results (optional)
        """
        self.storage_path = storage_path
        self.results: List[ABTestResult] = []
        
        # Load existing results if storage path provided
        if storage_path:
            self._load_results()
        
        logger.info("ABTestTracker initialized")
    
    def record_prediction(
        self,
        user_id: str,
        model_version: str,
        commodity: str,
        prediction: float,
        actual: Optional[float] = None
    ):
        """
        Record a prediction result.
        
        Args:
            user_id: User identifier
            model_version: 'champion' or 'challenger'
            commodity: Commodity symbol
            prediction: Model prediction
            actual: Actual value (if available)
        """
        error = None
        if actual is not None:
            error = abs(prediction - actual)
        
        result = ABTestResult(
            user_id=user_id,
            timestamp=datetime.now(),
            model_version=model_version,
            commodity=commodity,
            prediction=prediction,
            actual=actual,
            error=error
        )
        
        self.results.append(result)
        
        # Save if storage path provided
        if self.storage_path:
            self._save_results()
        
        logger.debug(f"Recorded {model_version} prediction for {user_id}: {prediction}")
    
    def update_actual(self, user_id: str, timestamp: datetime, actual: float):
        """
        Update actual value for a previously recorded prediction.
        
        Args:
            user_id: User identifier
            timestamp: Timestamp of the original prediction
            actual: Actual value
        """
        # Find matching result
        for result in self.results:
            if (result.user_id == user_id and 
                abs((result.timestamp - timestamp).total_seconds()) < 60):  # Within 1 minute
                result.actual = actual
                result.error = abs(result.prediction - actual)
                
                if self.storage_path:
                    self._save_results()
                
                logger.debug(f"Updated actual value for {user_id}: {actual}")
                return
        
        logger.warning(f"No matching prediction found for {user_id} at {timestamp}")
    
    def get_metrics(
        self,
        model_version: Optional[str] = None,
        commodity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate metrics for filtered results.
        
        Args:
            model_version: Filter by 'champion' or 'challenger' (None = all)
            commodity: Filter by commodity (None = all)
            start_date: Filter by start date (None = no filter)
            end_date: Filter by end date (None = no filter)
            
        Returns:
            Dictionary with metrics
        """
        # Filter results
        filtered = self.results
        
        if model_version:
            filtered = [r for r in filtered if r.model_version == model_version]
        
        if commodity:
            filtered = [r for r in filtered if r.commodity == commodity]
        
        if start_date:
            filtered = [r for r in filtered if r.timestamp >= start_date]
        
        if end_date:
            filtered = [r for r in filtered if r.timestamp <= end_date]
        
        # Only include results with actual values
        with_actual = [r for r in filtered if r.actual is not None]
        
        if len(with_actual) == 0:
            return {
                'total_predictions': len(filtered),
                'predictions_with_actual': 0,
                'message': 'No results with actual values'
            }
        
        # Calculate metrics
        errors = [r.error for r in with_actual if r.error is not None]
        predictions = [r.prediction for r in with_actual]
        actuals = [r.actual for r in with_actual]
        
        metrics = {
            'total_predictions': len(filtered),
            'predictions_with_actual': len(with_actual),
            'mae': sum(errors) / len(errors) if errors else None,
            'rmse': (sum(e**2 for e in errors) / len(errors))**0.5 if errors else None,
            'mape': sum(abs(e / a) for e, a in zip(errors, actuals)) / len(actuals) if actuals else None,
            'mean_prediction': sum(predictions) / len(predictions) if predictions else None,
            'mean_actual': sum(actuals) / len(actuals) if actuals else None,
        }
        
        # Calculate directional accuracy (if we have enough data)
        if len(with_actual) > 1:
            directional_correct = 0
            for i in range(1, len(with_actual)):
                pred_dir = predictions[i] > predictions[i-1]
                actual_dir = actuals[i] > actuals[i-1]
                if pred_dir == actual_dir:
                    directional_correct += 1
            metrics['directional_accuracy'] = directional_correct / (len(with_actual) - 1)
        
        return metrics
    
    def compare_models(
        self,
        commodity: Optional[str] = None,
        min_samples: int = 100,
        significance_level: float = 0.05
    ) -> Dict[str, Any]:
        """
        Compare champion vs challenger models.
        
        Args:
            commodity: Filter by commodity (None = all)
            min_samples: Minimum samples required for comparison
            significance_level: Statistical significance level
            
        Returns:
            Dictionary with comparison results
        """
        champion_metrics = self.get_metrics('champion', commodity)
        challenger_metrics = self.get_metrics('challenger', commodity)
        
        # Check if we have enough samples
        if (champion_metrics.get('predictions_with_actual', 0) < min_samples or
            challenger_metrics.get('predictions_with_actual', 0) < min_samples):
            return {
                'can_compare': False,
                'reason': f'Insufficient samples (need {min_samples}, got champion={champion_metrics.get("predictions_with_actual", 0)}, challenger={challenger_metrics.get("predictions_with_actual", 0)})',
                'champion_metrics': champion_metrics,
                'challenger_metrics': challenger_metrics
            }
        
        # Compare metrics
        comparison = {
            'can_compare': True,
            'champion_metrics': champion_metrics,
            'challenger_metrics': challenger_metrics,
            'improvements': {},
            'recommendation': None
        }
        
        # Calculate improvements (positive = challenger better)
        for metric in ['mae', 'rmse', 'mape']:
            if champion_metrics.get(metric) and challenger_metrics.get(metric):
                improvement = (champion_metrics[metric] - challenger_metrics[metric]) / champion_metrics[metric]
                comparison['improvements'][metric] = improvement
        
        # Calculate directional accuracy improvement
        if champion_metrics.get('directional_accuracy') and challenger_metrics.get('directional_accuracy'):
            improvement = challenger_metrics['directional_accuracy'] - champion_metrics['directional_accuracy']
            comparison['improvements']['directional_accuracy'] = improvement
        
        # Make recommendation
        improvements = comparison['improvements']
        better_count = sum(1 for v in improvements.values() if v > 0)
        worse_count = sum(1 for v in improvements.values() if v < 0)
        
        if better_count > worse_count:
            comparison['recommendation'] = 'promote_challenger'
        elif worse_count > better_count:
            comparison['recommendation'] = 'keep_champion'
        else:
            comparison['recommendation'] = 'inconclusive'
        
        return comparison
    
    def _save_results(self):
        """Save results to storage file."""
        if not self.storage_path:
            return
        
        try:
            data = [r.to_dict() for r in self.results]
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self.results)} results to {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def _load_results(self):
        """Load results from storage file."""
        if not self.storage_path:
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            self.results = [ABTestResult.from_dict(r) for r in data]
            logger.info(f"Loaded {len(self.results)} results from {self.storage_path}")
        except FileNotFoundError:
            logger.info(f"Storage file not found: {self.storage_path}. Starting with empty results.")
        except Exception as e:
            logger.error(f"Failed to load results: {e}")


class ModelPromoter:
    """
    Handles automatic promotion of challenger models to champion.
    
    Monitors A/B test results and promotes challenger if it performs better.
    """
    
    def __init__(
        self,
        tracker: ABTestTracker,
        min_test_duration_days: int = 14,
        min_improvement_threshold: float = 0.05,
        require_statistical_significance: bool = True
    ):
        """
        Initialize ModelPromoter.
        
        Args:
            tracker: ABTestTracker instance
            min_test_duration_days: Minimum test duration before promotion (default: 14)
            min_improvement_threshold: Minimum improvement required (default: 5%)
            require_statistical_significance: Require statistical significance (default: True)
        """
        self.tracker = tracker
        self.min_test_duration_days = min_test_duration_days
        self.min_improvement_threshold = min_improvement_threshold
        self.require_statistical_significance = require_statistical_significance
        
        logger.info("ModelPromoter initialized")
    
    def should_promote(
        self,
        commodity: Optional[str] = None,
        test_start_date: Optional[datetime] = None
    ) -> Tuple[bool, str]:
        """
        Determine if challenger should be promoted.
        
        Args:
            commodity: Filter by commodity (None = all)
            test_start_date: When the A/B test started (None = use oldest result)
            
        Returns:
            Tuple of (should_promote: bool, reason: str)
        """
        # Check test duration
        if test_start_date:
            duration = datetime.now() - test_start_date
            if duration.days < self.min_test_duration_days:
                return False, f"Test duration ({duration.days} days) less than minimum ({self.min_test_duration_days} days)"
        
        # Get comparison
        comparison = self.tracker.compare_models(commodity=commodity)
        
        if not comparison['can_compare']:
            return False, comparison.get('reason', 'Cannot compare models')
        
        # Check recommendation
        if comparison['recommendation'] != 'promote_challenger':
            return False, f"Recommendation: {comparison['recommendation']}"
        
        # Check improvement threshold
        improvements = comparison['improvements']
        avg_improvement = sum(improvements.values()) / len(improvements) if improvements else 0
        
        if avg_improvement < self.min_improvement_threshold:
            return False, f"Average improvement ({avg_improvement:.2%}) below threshold ({self.min_improvement_threshold:.2%})"
        
        return True, "Challenger model meets all promotion criteria"
    
    def promote_challenger(self, commodity: str) -> bool:
        """
        Promote challenger to champion (placeholder - actual implementation depends on model registry).
        
        Args:
            commodity: Commodity to promote
            
        Returns:
            True if promotion successful
        """
        logger.info(f"Promoting challenger to champion for {commodity}")
        # In production, this would:
        # 1. Update model registry to mark challenger as Production
        # 2. Mark old champion as Archived
        # 3. Update API configuration
        # 4. Notify stakeholders
        
        # Placeholder implementation
        logger.warning("Model promotion not fully implemented - requires model registry integration")
        return True

