"""
Unit tests for backtesting visualization.

Tests BacktestingVisualizer class.

Author: AI Assistant
Date: December 15, 2025
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from evaluation.visualization import BacktestingVisualizer, MATPLOTLIB_AVAILABLE
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    pytest.skip("Visualization module not available", allow_module_level=True)

if not MATPLOTLIB_AVAILABLE:
    pytest.skip("matplotlib not available", allow_module_level=True)


@pytest.fixture
def sample_y_true():
    """Create sample true values."""
    np.random.seed(42)
    return np.array(100 + np.cumsum(np.random.randn(100) * 0.5))


@pytest.fixture
def sample_y_pred():
    """Create sample predictions."""
    np.random.seed(42)
    return np.array(100 + np.cumsum(np.random.randn(100) * 0.5) + np.random.randn(100) * 0.1)


@pytest.fixture
def sample_dates():
    """Create sample dates."""
    return pd.date_range(start='2024-01-01', periods=100, freq='D')


@pytest.fixture
def sample_equity_curve():
    """Create sample equity curve."""
    np.random.seed(42)
    returns = np.random.randn(100) * 0.02
    return 10000 * (1 + returns).cumprod()


@pytest.fixture
def sample_trades():
    """Create sample trades."""
    return [
        {'pnl': 0.01, 'entry_price': 100, 'exit_price': 101},
        {'pnl': -0.005, 'entry_price': 101, 'exit_price': 100.5},
        {'pnl': 0.02, 'entry_price': 100.5, 'exit_price': 102.5},
    ]


class TestBacktestingVisualizerInitialization:
    """Tests for BacktestingVisualizer initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        visualizer = BacktestingVisualizer()
        
        assert visualizer.figsize == (12, 6)
    
    def test_init_custom(self):
        """Test initialization with custom parameters."""
        visualizer = BacktestingVisualizer(figsize=(10, 8), style='default')
        
        assert visualizer.figsize == (10, 8)


class TestBacktestingVisualizerPlots:
    """Tests for BacktestingVisualizer plot methods."""
    
    def test_plot_predicted_vs_actual(self, sample_y_true, sample_y_pred):
        """Test predicted vs actual plot."""
        visualizer = BacktestingVisualizer()
        
        fig = visualizer.plot_predicted_vs_actual(
            y_true=sample_y_true,
            y_pred=sample_y_pred
        )
        
        assert fig is not None
    
    def test_plot_predicted_vs_actual_with_dates(self, sample_dates, sample_y_true, sample_y_pred):
        """Test predicted vs actual plot with dates."""
        visualizer = BacktestingVisualizer()
        
        fig = visualizer.plot_predicted_vs_actual(
            dates=sample_dates,
            y_true=sample_y_true,
            y_pred=sample_y_pred
        )
        
        assert fig is not None
    
    def test_plot_forecast_error(self, sample_y_true, sample_y_pred):
        """Test forecast error plot."""
        visualizer = BacktestingVisualizer()
        
        fig = visualizer.plot_forecast_error(
            y_true=sample_y_true,
            y_pred=sample_y_pred
        )
        
        assert fig is not None
    
    def test_plot_forecast_error_with_errors(self):
        """Test forecast error plot with errors directly."""
        visualizer = BacktestingVisualizer()
        errors = np.random.randn(100) * 0.1
        
        fig = visualizer.plot_forecast_error(errors=errors)
        
        assert fig is not None
    
    def test_plot_cumulative_pnl(self, sample_equity_curve):
        """Test cumulative P&L plot."""
        visualizer = BacktestingVisualizer()
        
        fig = visualizer.plot_cumulative_pnl(
            equity_curve=sample_equity_curve,
            initial_capital=10000.0
        )
        
        assert fig is not None
    
    def test_plot_drawdown(self, sample_equity_curve):
        """Test drawdown plot."""
        visualizer = BacktestingVisualizer()
        
        fig = visualizer.plot_drawdown(equity_curve=sample_equity_curve)
        
        assert fig is not None
    
    def test_plot_trade_distribution(self, sample_trades):
        """Test trade distribution plot."""
        visualizer = BacktestingVisualizer()
        trade_pnls = [t['pnl'] * 10000 for t in sample_trades]
        
        fig = visualizer.plot_trade_distribution(trade_pnls)
        
        assert fig is not None
    
    def test_plot_metrics_summary(self):
        """Test metrics summary plot."""
        visualizer = BacktestingVisualizer()
        metrics = {
            'RMSE': 0.5,
            'MAE': 0.3,
            'Sharpe Ratio': 1.2,
            'Max Drawdown': 0.15
        }
        
        fig = visualizer.plot_metrics_summary(metrics)
        
        assert fig is not None


class TestBacktestingVisualizerSave:
    """Tests for BacktestingVisualizer.save_plot()."""
    
    def test_save_plot_png(self, sample_y_true, sample_y_pred):
        """Test saving plot as PNG."""
        visualizer = BacktestingVisualizer()
        fig = visualizer.plot_predicted_vs_actual(y_true=sample_y_true, y_pred=sample_y_pred)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test.png'
            visualizer.save_plot(fig, output_path)
            
            assert output_path.exists()
    
    def test_save_plot_pdf(self, sample_y_true, sample_y_pred):
        """Test saving plot as PDF."""
        visualizer = BacktestingVisualizer()
        fig = visualizer.plot_predicted_vs_actual(y_true=sample_y_true, y_pred=sample_y_pred)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test.pdf'
            visualizer.save_plot(fig, output_path, format='pdf')
            
            assert output_path.exists()


class TestBacktestingVisualizerReport:
    """Tests for BacktestingVisualizer.generate_backtest_report()."""
    
    def test_generate_backtest_report(self, sample_y_true, sample_y_pred, sample_equity_curve, sample_trades):
        """Test generating comprehensive backtest report."""
        visualizer = BacktestingVisualizer()
        
        results = {
            'y_true': sample_y_true,
            'y_pred': sample_y_pred,
            'equity_curve': sample_equity_curve,
            'trades': sample_trades,
            'performance': {'RMSE': 0.5, 'MAE': 0.3, 'Sharpe Ratio': 1.2},
            'initial_capital': 10000.0
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            visualizer.generate_backtest_report(results, tmpdir)
            
            # Check that plots were created
            output_dir = Path(tmpdir)
            plot_files = list(output_dir.glob('backtest_*.png'))
            
            assert len(plot_files) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

