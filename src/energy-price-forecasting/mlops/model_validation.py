"""
Model Validation Gates.

Validates trained models against performance thresholds before deployment.
Ensures only high-quality models are promoted to production.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

from typing import Dict, Any, Optional, List
import logging
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


class ModelValidationThresholds:
    """
    Model validation thresholds configuration.
    
    Defines minimum performance requirements for models to pass validation.
    """
    
    DEFAULT_THRESHOLDS = {
        'directional_accuracy': {
            'min': 0.70,  # 70% minimum
            'description': 'Minimum directional accuracy (up/down prediction)'
        },
        'sharpe_ratio': {
            'min': 1.0,
            'description': 'Minimum Sharpe ratio for trading performance'
        },
        'rmse': {
            'max_multiplier': 1.1,  # RMSE should not exceed baseline by more than 10%
            'description': 'RMSE relative to baseline'
        },
        'mae': {
            'max_multiplier': 1.15,  # MAE should not exceed baseline by more than 15%
            'description': 'MAE relative to baseline'
        },
        'mape': {
            'max': 0.20,  # 20% maximum MAPE
            'description': 'Maximum Mean Absolute Percentage Error'
        },
        'r2': {
            'min': 0.50,  # Minimum R-squared
            'description': 'Minimum R-squared coefficient'
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize validation thresholds.
        
        Args:
            config_path: Path to YAML configuration file (optional)
        """
        if config_path and Path(config_path).exists():
            self.thresholds = self._load_from_file(config_path)
        else:
            self.thresholds = self.DEFAULT_THRESHOLDS.copy()
        
        logger.info("ModelValidationThresholds initialized")
    
    def _load_from_file(self, config_path: str) -> Dict[str, Any]:
        """Load thresholds from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded validation thresholds from {config_path}")
            return config.get('thresholds', self.DEFAULT_THRESHOLDS)
        except Exception as e:
            logger.warning(f"Failed to load thresholds from {config_path}: {e}. Using defaults.")
            return self.DEFAULT_THRESHOLDS
    
    def get_threshold(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """
        Get threshold configuration for a metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Threshold configuration dict or None
        """
        return self.thresholds.get(metric_name)
    
    def save_to_file(self, config_path: str):
        """Save thresholds to YAML file."""
        try:
            config = {'thresholds': self.thresholds}
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            logger.info(f"Saved validation thresholds to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save thresholds to {config_path}: {e}")


class ModelValidator:
    """
    Validates models against performance thresholds.
    
    Checks if a trained model meets minimum performance requirements
    before it can be deployed to production.
    """
    
    def __init__(self, thresholds: Optional[ModelValidationThresholds] = None):
        """
        Initialize ModelValidator.
        
        Args:
            thresholds: ModelValidationThresholds instance (default: uses defaults)
        """
        self.thresholds = thresholds or ModelValidationThresholds()
        logger.info("ModelValidator initialized")
    
    def validate(
        self,
        metrics: Dict[str, float],
        baseline_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Validate model metrics against thresholds.
        
        Args:
            metrics: Dictionary of model metrics (e.g., {'rmse': 2.5, 'mae': 1.8})
            baseline_metrics: Optional baseline metrics for comparison
            
        Returns:
            Dictionary with validation results:
            {
                'passed': bool,
                'checks': List[Dict],  # Individual check results
                'summary': str,  # Human-readable summary
                'failed_checks': List[str]  # Names of failed checks
            }
        """
        logger.info("Starting model validation...")
        
        checks = []
        failed_checks = []
        passed_checks = []
        
        # Check directional accuracy
        if 'directional_accuracy' in metrics:
            check_result = self._check_directional_accuracy(metrics['directional_accuracy'])
            checks.append(check_result)
            if check_result['passed']:
                passed_checks.append('directional_accuracy')
            else:
                failed_checks.append('directional_accuracy')
        
        # Check Sharpe ratio
        if 'sharpe_ratio' in metrics:
            check_result = self._check_sharpe_ratio(metrics['sharpe_ratio'])
            checks.append(check_result)
            if check_result['passed']:
                passed_checks.append('sharpe_ratio')
            else:
                failed_checks.append('sharpe_ratio')
        
        # Check RMSE (relative to baseline if provided)
        if 'rmse' in metrics:
            check_result = self._check_rmse(
                metrics['rmse'],
                baseline_metrics.get('rmse') if baseline_metrics else None
            )
            checks.append(check_result)
            if check_result['passed']:
                passed_checks.append('rmse')
            else:
                failed_checks.append('rmse')
        
        # Check MAE (relative to baseline if provided)
        if 'mae' in metrics:
            check_result = self._check_mae(
                metrics['mae'],
                baseline_metrics.get('mae') if baseline_metrics else None
            )
            checks.append(check_result)
            if check_result['passed']:
                passed_checks.append('mae')
            else:
                failed_checks.append('mae')
        
        # Check MAPE
        if 'mape' in metrics:
            check_result = self._check_mape(metrics['mape'])
            checks.append(check_result)
            if check_result['passed']:
                passed_checks.append('mape')
            else:
                failed_checks.append('mape')
        
        # Check R²
        if 'r2' in metrics or 'r_squared' in metrics:
            r2_value = metrics.get('r2') or metrics.get('r_squared')
            check_result = self._check_r2(r2_value)
            checks.append(check_result)
            if check_result['passed']:
                passed_checks.append('r2')
            else:
                failed_checks.append('r2')
        
        # Overall result
        passed = len(failed_checks) == 0
        
        # Generate summary
        summary = self._generate_summary(passed, passed_checks, failed_checks, checks)
        
        result = {
            'passed': passed,
            'checks': checks,
            'summary': summary,
            'failed_checks': failed_checks,
            'passed_checks': passed_checks,
            'total_checks': len(checks),
            'passed_count': len(passed_checks),
            'failed_count': len(failed_checks)
        }
        
        logger.info(f"Validation {'PASSED' if passed else 'FAILED'}: {len(passed_checks)}/{len(checks)} checks passed")
        
        return result
    
    def _check_directional_accuracy(self, value: float) -> Dict[str, Any]:
        """Check directional accuracy threshold."""
        threshold = self.thresholds.get_threshold('directional_accuracy')
        min_value = threshold['min'] if threshold else 0.70
        
        passed = value >= min_value
        
        return {
            'metric': 'directional_accuracy',
            'value': value,
            'threshold': min_value,
            'passed': passed,
            'message': f"Directional accuracy: {value:.2%} {'>=' if passed else '<'} {min_value:.2%}"
        }
    
    def _check_sharpe_ratio(self, value: float) -> Dict[str, Any]:
        """Check Sharpe ratio threshold."""
        threshold = self.thresholds.get_threshold('sharpe_ratio')
        min_value = threshold['min'] if threshold else 1.0
        
        passed = value >= min_value
        
        return {
            'metric': 'sharpe_ratio',
            'value': value,
            'threshold': min_value,
            'passed': passed,
            'message': f"Sharpe ratio: {value:.2f} {'>=' if passed else '<'} {min_value:.2f}"
        }
    
    def _check_rmse(self, value: float, baseline: Optional[float] = None) -> Dict[str, Any]:
        """Check RMSE threshold."""
        threshold = self.thresholds.get_threshold('rmse')
        
        if baseline is not None and threshold and 'max_multiplier' in threshold:
            max_value = baseline * threshold['max_multiplier']
            passed = value <= max_value
            message = f"RMSE: {value:.2f} {'<=' if passed else '>'} {max_value:.2f} (baseline: {baseline:.2f})"
        else:
            # No baseline comparison, just log the value
            passed = True  # Can't fail without baseline
            message = f"RMSE: {value:.2f} (no baseline for comparison)"
        
        return {
            'metric': 'rmse',
            'value': value,
            'baseline': baseline,
            'threshold': baseline * threshold['max_multiplier'] if baseline and threshold and 'max_multiplier' in threshold else None,
            'passed': passed,
            'message': message
        }
    
    def _check_mae(self, value: float, baseline: Optional[float] = None) -> Dict[str, Any]:
        """Check MAE threshold."""
        threshold = self.thresholds.get_threshold('mae')
        
        if baseline is not None and threshold and 'max_multiplier' in threshold:
            max_value = baseline * threshold['max_multiplier']
            passed = value <= max_value
            message = f"MAE: {value:.2f} {'<=' if passed else '>'} {max_value:.2f} (baseline: {baseline:.2f})"
        else:
            passed = True
            message = f"MAE: {value:.2f} (no baseline for comparison)"
        
        return {
            'metric': 'mae',
            'value': value,
            'baseline': baseline,
            'threshold': baseline * threshold['max_multiplier'] if baseline and threshold and 'max_multiplier' in threshold else None,
            'passed': passed,
            'message': message
        }
    
    def _check_mape(self, value: float) -> Dict[str, Any]:
        """Check MAPE threshold."""
        threshold = self.thresholds.get_threshold('mape')
        max_value = threshold['max'] if threshold else 0.20
        
        passed = value <= max_value
        
        return {
            'metric': 'mape',
            'value': value,
            'threshold': max_value,
            'passed': passed,
            'message': f"MAPE: {value:.2%} {'<=' if passed else '>'} {max_value:.2%}"
        }
    
    def _check_r2(self, value: float) -> Dict[str, Any]:
        """Check R² threshold."""
        threshold = self.thresholds.get_threshold('r2')
        min_value = threshold['min'] if threshold else 0.50
        
        passed = value >= min_value
        
        return {
            'metric': 'r2',
            'value': value,
            'threshold': min_value,
            'passed': passed,
            'message': f"R²: {value:.2f} {'>=' if passed else '<'} {min_value:.2f}"
        }
    
    def _generate_summary(
        self,
        passed: bool,
        passed_checks: List[str],
        failed_checks: List[str],
        checks: List[Dict[str, Any]]
    ) -> str:
        """Generate human-readable validation summary."""
        status = "PASSED" if passed else "FAILED"
        summary = f"Model Validation: {status}\n"
        summary += f"Total Checks: {len(checks)}\n"
        summary += f"Passed: {len(passed_checks)}\n"
        summary += f"Failed: {len(failed_checks)}\n\n"
        
        if passed_checks:
            summary += "Passed Checks:\n"
            for check_name in passed_checks:
                check = next((c for c in checks if c['metric'] == check_name), None)
                if check:
                    summary += f"  ✓ {check['message']}\n"
        
        if failed_checks:
            summary += "\nFailed Checks:\n"
            for check_name in failed_checks:
                check = next((c for c in checks if c['metric'] == check_name), None)
                if check:
                    summary += f"  ✗ {check['message']}\n"
        
        return summary

