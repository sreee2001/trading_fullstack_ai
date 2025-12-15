"""
Unit tests for model comparison dashboard.

Tests ModelComparisonDashboard class.

Author: AI Assistant
Date: December 15, 2025
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from evaluation.model_comparison_dashboard import ModelComparisonDashboard
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False
    pytest.skip("Evaluation module not available", allow_module_level=True)


@pytest.fixture
def sample_y_true():
    """Create sample true values."""
    np.random.seed(42)
    return np.array(100 + np.cumsum(np.random.randn(100) * 0.5))


@pytest.fixture
def sample_predictions():
    """Create sample predictions."""
    np.random.seed(42)
    return {
        'ARIMA': np.array(100 + np.cumsum(np.random.randn(100) * 0.5) + np.random.randn(100) * 0.1),
        'LSTM': np.array(100 + np.cumsum(np.random.randn(100) * 0.5) + np.random.randn(100) * 0.05),
        'Prophet': np.array(100 + np.cumsum(np.random.randn(100) * 0.5) + np.random.randn(100) * 0.15)
    }


@pytest.fixture
def sample_equity_curves():
    """Create sample equity curves."""
    np.random.seed(42)
    returns = np.random.randn(100) * 0.02
    base_equity = 10000 * (1 + returns).cumprod()
    
    return {
        'ARIMA': base_equity,
        'LSTM': base_equity * 1.1,  # Better performance
        'Prophet': base_equity * 0.95  # Worse performance
    }


class TestModelComparisonDashboardInitialization:
    """Tests for ModelComparisonDashboard initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        dashboard = ModelComparisonDashboard()
        
        assert dashboard.statistical_metrics is not None
        assert dashboard.performance_metrics is not None
        assert dashboard.results == {}
    
    def test_init_custom_rate(self):
        """Test initialization with custom risk-free rate."""
        dashboard = ModelComparisonDashboard(risk_free_rate=0.03)
        
        assert dashboard.performance_metrics.risk_free_rate == 0.03


class TestModelComparisonDashboardCompare:
    """Tests for ModelComparisonDashboard.compare_models()."""
    
    def test_compare_models_basic(self, sample_y_true, sample_predictions):
        """Test basic model comparison."""
        dashboard = ModelComparisonDashboard()
        
        df = dashboard.compare_models(sample_y_true, sample_predictions)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(sample_predictions)
        assert 'RMSE' in df.columns
        assert 'MAE' in df.columns
        assert 'MAPE' in df.columns
    
    def test_compare_models_with_equity(self, sample_y_true, sample_predictions, sample_equity_curves):
        """Test model comparison with equity curves."""
        dashboard = ModelComparisonDashboard()
        
        df = dashboard.compare_models(
            sample_y_true,
            sample_predictions,
            equity_curves=sample_equity_curves
        )
        
        assert 'sharpe_ratio' in df.columns
        assert 'max_drawdown' in df.columns
        assert 'volatility' in df.columns
    
    def test_get_comparison_table(self, sample_y_true, sample_predictions):
        """Test getting comparison table."""
        dashboard = ModelComparisonDashboard()
        dashboard.compare_models(sample_y_true, sample_predictions)
        
        df = dashboard.get_comparison_table()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(sample_predictions)
    
    def test_get_comparison_table_sorted(self, sample_y_true, sample_predictions, sample_equity_curves):
        """Test getting sorted comparison table."""
        dashboard = ModelComparisonDashboard()
        dashboard.compare_models(
            sample_y_true,
            sample_predictions,
            equity_curves=sample_equity_curves
        )
        
        df = dashboard.get_comparison_table(sort_by='sharpe_ratio', ascending=False)
        
        assert isinstance(df, pd.DataFrame)
        # Check that it's sorted (highest Sharpe first)
        if len(df) > 1 and df['sharpe_ratio'].notna().any():
            sharpe_values = df['sharpe_ratio'].dropna()
            if len(sharpe_values) > 1:
                assert sharpe_values.iloc[0] >= sharpe_values.iloc[1]


class TestModelComparisonDashboardBestModel:
    """Tests for ModelComparisonDashboard.select_best_model()."""
    
    def test_select_best_model_by_sharpe(self, sample_y_true, sample_predictions, sample_equity_curves):
        """Test selecting best model by Sharpe ratio."""
        dashboard = ModelComparisonDashboard()
        dashboard.compare_models(
            sample_y_true,
            sample_predictions,
            equity_curves=sample_equity_curves
        )
        
        best = dashboard.select_best_model(primary_metric='sharpe_ratio')
        
        assert best is not None
        assert 'model_name' in best
        assert 'primary_metric' in best
        assert 'primary_value' in best
        assert 'metrics' in best
    
    def test_select_best_model_by_rmse(self, sample_y_true, sample_predictions):
        """Test selecting best model by RMSE."""
        dashboard = ModelComparisonDashboard()
        dashboard.compare_models(sample_y_true, sample_predictions)
        
        best = dashboard.select_best_model(primary_metric='RMSE')
        
        assert best is not None
        assert best['primary_metric'] == 'RMSE'


class TestModelComparisonDashboardExport:
    """Tests for ModelComparisonDashboard.export_comparison_report()."""
    
    def test_export_csv(self, sample_y_true, sample_predictions):
        """Test exporting to CSV."""
        dashboard = ModelComparisonDashboard()
        dashboard.compare_models(sample_y_true, sample_predictions)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'comparison.csv'
            dashboard.export_comparison_report(output_path, format='csv')
            
            assert output_path.exists()
            
            # Verify it can be read back
            df = pd.read_csv(output_path, index_col=0, comment='#')
            assert len(df) == len(sample_predictions)
    
    def test_export_json(self, sample_y_true, sample_predictions):
        """Test exporting to JSON."""
        dashboard = ModelComparisonDashboard()
        dashboard.compare_models(sample_y_true, sample_predictions)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'comparison.json'
            dashboard.export_comparison_report(
                output_path,
                format='json',
                metadata={'commodity': 'WTI_CRUDE', 'date': '2024-01-01'}
            )
            
            assert output_path.exists()
            
            # Verify it can be read back
            import json
            with open(output_path) as f:
                report = json.load(f)
            
            assert 'metadata' in report
            assert 'comparison_table' in report


class TestModelComparisonDashboardSummary:
    """Tests for ModelComparisonDashboard.get_summary()."""
    
    def test_get_summary(self, sample_y_true, sample_predictions):
        """Test getting summary."""
        dashboard = ModelComparisonDashboard()
        dashboard.compare_models(sample_y_true, sample_predictions)
        
        summary = dashboard.get_summary()
        
        assert 'num_models' in summary
        assert 'metrics_available' in summary
        assert 'comparison_table' in summary
        assert summary['num_models'] == len(sample_predictions)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

