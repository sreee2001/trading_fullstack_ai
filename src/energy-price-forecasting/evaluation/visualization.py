"""
Backtesting Visualization Tools for Epic 3.

Provides comprehensive visualization capabilities for backtesting results.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path
from datetime import datetime

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

logger = logging.getLogger(__name__)


class BacktestingVisualizer:
    """
    Visualize backtesting results.
    
    Provides comprehensive visualization capabilities including:
    - Predicted vs actual prices
    - Forecast errors over time
    - Cumulative P&L charts
    - Drawdown charts
    - Trade distribution histograms
    - Metrics summary tables
    
    Attributes:
        figsize: Default figure size (width, height)
        style: Matplotlib style (default: 'seaborn-v0_8')
    
    Example:
        >>> visualizer = BacktestingVisualizer()
        >>> fig = visualizer.plot_predicted_vs_actual(dates, y_true, y_pred)
        >>> visualizer.save_plot(fig, 'predicted_vs_actual.png')
    """
    
    def __init__(self, figsize: Tuple[float, float] = (12, 6), style: str = 'default'):
        """
        Initialize BacktestingVisualizer.
        
        Args:
            figsize: Default figure size (width, height)
            style: Matplotlib style (default: 'default')
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError(
                "matplotlib is required for visualization. Install with: pip install matplotlib"
            )
        
        self.figsize = figsize
        self.style = style
        
        # Set style
        try:
            plt.style.use(style)
        except OSError:
            plt.style.use('default')
        
        logger.info(f"BacktestingVisualizer initialized with figsize={figsize}, style={style}")
    
    def plot_predicted_vs_actual(
        self,
        y_true: np.ndarray | pd.Series,
        y_pred: np.ndarray | pd.Series,
        dates: Optional[pd.DatetimeIndex | np.ndarray] = None,
        confidence_intervals: Optional[Tuple[np.ndarray, np.ndarray]] = None,
        title: Optional[str] = None,
        figsize: Optional[Tuple[float, float]] = None
    ) -> plt.Figure:
        """
        Plot predicted vs actual prices.
        
        Args:
            dates: Date index (optional)
            y_true: True values
            y_pred: Predicted values
            confidence_intervals: Optional tuple of (lower, upper) confidence intervals
            title: Plot title (optional)
            figsize: Figure size (optional, uses default if not provided)
        
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize or self.figsize)
        
        # Convert to numpy arrays
        y_true_arr = np.array(y_true) if isinstance(y_true, pd.Series) else y_true
        y_pred_arr = np.array(y_pred) if isinstance(y_pred, pd.Series) else y_pred
        
        # Create x-axis
        if dates is not None:
            if isinstance(dates, pd.DatetimeIndex):
                x = dates
            else:
                x = pd.date_range(start='2024-01-01', periods=len(y_true_arr), freq='D')
        else:
            x = np.arange(len(y_true_arr))
        
        # Plot actual
        ax.plot(x, y_true_arr, label='Actual', linewidth=2, alpha=0.8)
        
        # Plot predicted
        ax.plot(x, y_pred_arr, label='Predicted', linewidth=2, alpha=0.8, linestyle='--')
        
        # Plot confidence intervals if provided
        if confidence_intervals is not None:
            lower, upper = confidence_intervals
            ax.fill_between(x, lower, upper, alpha=0.2, label='Confidence Interval')
        
        ax.set_xlabel('Date' if dates is not None else 'Index')
        ax.set_ylabel('Price')
        ax.set_title(title or 'Predicted vs Actual Prices')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        logger.info("Predicted vs actual plot created")
        
        return fig
    
    def plot_forecast_error(
        self,
        errors: Optional[np.ndarray | pd.Series] = None,
        y_true: Optional[np.ndarray | pd.Series] = None,
        y_pred: Optional[np.ndarray | pd.Series] = None,
        dates: Optional[pd.DatetimeIndex | np.ndarray] = None,
        title: Optional[str] = None,
        figsize: Optional[Tuple[float, float]] = None
    ) -> plt.Figure:
        """
        Plot forecast errors over time.
        
        Args:
            dates: Date index (optional)
            errors: Error values (y_true - y_pred) (optional if y_true/y_pred provided)
            y_true: True values (optional if errors provided)
            y_pred: Predicted values (optional if errors provided)
            title: Plot title (optional)
            figsize: Figure size (optional)
        
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize or self.figsize)
        
        # Calculate errors if not provided
        if errors is None:
            if y_true is None or y_pred is None:
                raise ValueError("Either errors or both y_true and y_pred must be provided")
            
            y_true_arr = np.array(y_true) if isinstance(y_true, pd.Series) else y_true
            y_pred_arr = np.array(y_pred) if isinstance(y_pred, pd.Series) else y_pred
            errors = y_true_arr - y_pred_arr
        else:
            errors = np.array(errors) if isinstance(errors, pd.Series) else errors
        
        # Create x-axis
        if dates is not None:
            if isinstance(dates, pd.DatetimeIndex):
                x = dates
            else:
                x = pd.date_range(start='2024-01-01', periods=len(errors), freq='D')
        else:
            x = np.arange(len(errors))
        
        # Plot errors
        ax.plot(x, errors, linewidth=1.5, alpha=0.7, label='Forecast Error')
        
        # Zero line
        ax.axhline(y=0, color='r', linestyle='--', linewidth=1, label='Zero')
        
        ax.set_xlabel('Date' if dates is not None else 'Index')
        ax.set_ylabel('Error (Actual - Predicted)')
        ax.set_title(title or 'Forecast Error Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        logger.info("Forecast error plot created")
        
        return fig
    
    def plot_cumulative_pnl(
        self,
        cumulative_pnl: Optional[np.ndarray | pd.Series] = None,
        equity_curve: Optional[np.ndarray | pd.Series] = None,
        initial_capital: Optional[float] = None,
        dates: Optional[pd.DatetimeIndex | np.ndarray] = None,
        title: Optional[str] = None,
        figsize: Optional[Tuple[float, float]] = None
    ) -> plt.Figure:
        """
        Plot cumulative P&L chart.
        
        Args:
            dates: Date index (optional)
            cumulative_pnl: Cumulative P&L values (optional if equity_curve provided)
            equity_curve: Equity curve values (optional if cumulative_pnl provided)
            initial_capital: Initial capital (required if equity_curve provided)
            title: Plot title (optional)
            figsize: Figure size (optional)
        
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize or self.figsize)
        
        # Calculate cumulative P&L if not provided
        if cumulative_pnl is None:
            if equity_curve is None:
                raise ValueError("Either cumulative_pnl or equity_curve must be provided")
            
            if initial_capital is None:
                raise ValueError("initial_capital required when using equity_curve")
            
            equity_arr = np.array(equity_curve) if isinstance(equity_curve, pd.Series) else equity_curve
            cumulative_pnl = equity_arr - initial_capital
        else:
            cumulative_pnl = np.array(cumulative_pnl) if isinstance(cumulative_pnl, pd.Series) else cumulative_pnl
        
        # Create x-axis
        if dates is not None:
            if isinstance(dates, pd.DatetimeIndex):
                x = dates
            else:
                x = pd.date_range(start='2024-01-01', periods=len(cumulative_pnl), freq='D')
        else:
            x = np.arange(len(cumulative_pnl))
        
        # Plot cumulative P&L
        ax.plot(x, cumulative_pnl, linewidth=2, label='Cumulative P&L')
        
        # Zero line
        ax.axhline(y=0, color='r', linestyle='--', linewidth=1, label='Break Even')
        
        ax.set_xlabel('Date' if dates is not None else 'Index')
        ax.set_ylabel('Cumulative P&L ($)')
        ax.set_title(title or 'Cumulative P&L Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        logger.info("Cumulative P&L plot created")
        
        return fig
    
    def plot_drawdown(
        self,
        drawdown: Optional[np.ndarray | pd.Series] = None,
        equity_curve: Optional[np.ndarray | pd.Series] = None,
        dates: Optional[pd.DatetimeIndex | np.ndarray] = None,
        title: Optional[str] = None,
        figsize: Optional[Tuple[float, float]] = None
    ) -> plt.Figure:
        """
        Plot drawdown chart.
        
        Args:
            dates: Date index (optional)
            drawdown: Drawdown values (optional if equity_curve provided)
            equity_curve: Equity curve values (optional if drawdown provided)
            title: Plot title (optional)
            figsize: Figure size (optional)
        
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize or self.figsize)
        
        # Calculate drawdown if not provided
        if drawdown is None:
            if equity_curve is None:
                raise ValueError("Either drawdown or equity_curve must be provided")
            
            equity_arr = np.array(equity_curve) if isinstance(equity_curve, pd.Series) else equity_curve
            running_max = np.maximum.accumulate(equity_arr)
            drawdown = (equity_arr - running_max) / running_max
        else:
            drawdown = np.array(drawdown) if isinstance(drawdown, pd.Series) else drawdown
        
        # Create x-axis
        if dates is not None:
            if isinstance(dates, pd.DatetimeIndex):
                x = dates
            else:
                x = pd.date_range(start='2024-01-01', periods=len(drawdown), freq='D')
        else:
            x = np.arange(len(drawdown))
        
        # Plot drawdown as area
        ax.fill_between(x, drawdown, 0, alpha=0.3, color='red', label='Drawdown')
        ax.plot(x, drawdown, linewidth=1.5, color='darkred', alpha=0.7)
        
        # Highlight maximum drawdown
        max_dd_idx = np.argmin(drawdown)
        max_dd = drawdown[max_dd_idx]
        ax.axvline(x=x[max_dd_idx], color='black', linestyle='--', linewidth=1, 
                   label=f'Max Drawdown: {max_dd*100:.2f}%')
        
        ax.set_xlabel('Date' if dates is not None else 'Index')
        ax.set_ylabel('Drawdown (%)')
        ax.set_title(title or 'Drawdown Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        logger.info("Drawdown plot created")
        
        return fig
    
    def plot_trade_distribution(
        self,
        trade_pnls: np.ndarray | pd.Series | List[float],
        title: Optional[str] = None,
        bins: int = 30,
        figsize: Optional[Tuple[float, float]] = None
    ) -> plt.Figure:
        """
        Plot trade P&L distribution histogram.
        
        Args:
            trade_pnls: List or array of trade P&L values
            title: Plot title (optional)
            bins: Number of histogram bins
            figsize: Figure size (optional)
        
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize or self.figsize)
        
        # Convert to numpy array
        pnls = np.array(trade_pnls) if isinstance(trade_pnls, (list, pd.Series)) else trade_pnls
        
        # Plot histogram
        ax.hist(pnls, bins=bins, alpha=0.7, edgecolor='black', label='Trade P&L Distribution')
        
        # Zero line
        ax.axvline(x=0, color='r', linestyle='--', linewidth=2, label='Zero')
        
        # Mean and std
        mean_pnl = np.mean(pnls)
        std_pnl = np.std(pnls)
        ax.axvline(x=mean_pnl, color='g', linestyle='--', linewidth=2, 
                   label=f'Mean: ${mean_pnl:.2f}')
        ax.axvline(x=mean_pnl + std_pnl, color='orange', linestyle=':', linewidth=1, alpha=0.7)
        ax.axvline(x=mean_pnl - std_pnl, color='orange', linestyle=':', linewidth=1, alpha=0.7,
                   label=f'Std: ${std_pnl:.2f}')
        
        ax.set_xlabel('Trade P&L ($)')
        ax.set_ylabel('Frequency')
        ax.set_title(title or 'Trade P&L Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        logger.info("Trade distribution plot created")
        
        return fig
    
    def plot_metrics_summary(
        self,
        metrics: Dict[str, float],
        title: Optional[str] = None,
        figsize: Optional[Tuple[float, float]] = None
    ) -> plt.Figure:
        """
        Plot metrics summary table.
        
        Args:
            metrics: Dictionary of metric names to values
            title: Plot title (optional)
            figsize: Figure size (optional)
        
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize or (10, 6))
        ax.axis('tight')
        ax.axis('off')
        
        # Create table
        table_data = [[name, f"{value:.4f}" if isinstance(value, (int, float)) else str(value)]
                      for name, value in metrics.items()]
        
        table = ax.table(cellText=table_data,
                        colLabels=['Metric', 'Value'],
                        cellLoc='left',
                        loc='center')
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        # Style header
        for i in range(2):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax.set_title(title or 'Metrics Summary', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        logger.info("Metrics summary table created")
        
        return fig
    
    def save_plot(
        self,
        fig: plt.Figure,
        filepath: str | Path,
        dpi: int = 300,
        format: Optional[str] = None
    ):
        """
        Save plot to file.
        
        Args:
            fig: Matplotlib figure
            filepath: Path to save file
            dpi: Resolution (default: 300)
            format: File format ('png', 'pdf', 'svg') (auto-detected from extension if not provided)
        """
        filepath = Path(filepath)
        
        # Determine format from extension if not provided
        if format is None:
            format = filepath.suffix[1:] if filepath.suffix else 'png'
        
        fig.savefig(filepath, dpi=dpi, format=format, bbox_inches='tight')
        logger.info(f"Plot saved to {filepath} ({format}, {dpi} dpi)")
        
        plt.close(fig)
    
    def generate_backtest_report(
        self,
        results: Dict[str, Any],
        output_dir: str | Path,
        dates: Optional[pd.DatetimeIndex | np.ndarray] = None,
        prefix: str = 'backtest'
    ):
        """
        Generate comprehensive backtesting report with all visualizations.
        
        Args:
            results: Dictionary containing backtest results with keys:
                    - 'y_true': True values
                    - 'y_pred': Predicted values
                    - 'equity_curve': Equity curve (optional)
                    - 'trades': List of trades (optional)
                    - 'performance': Performance metrics (optional)
                    - 'cumulative_pnl': Cumulative P&L (optional)
            output_dir: Directory to save plots
            dates: Date index (optional)
            prefix: Prefix for output files (default: 'backtest')
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating backtest report in {output_dir}")
        
        # Extract data
        y_true = results.get('y_true')
        y_pred = results.get('y_pred')
        equity_curve = results.get('equity_curve')
        trades = results.get('trades', [])
        performance = results.get('performance', {})
        initial_capital = results.get('initial_capital', 10000.0)
        
        # 1. Predicted vs Actual
        if y_true is not None and y_pred is not None:
            fig = self.plot_predicted_vs_actual(y_true, y_pred, dates=dates)
            self.save_plot(fig, output_dir / f'{prefix}_predicted_vs_actual.png')
        
        # 2. Forecast Error
        if y_true is not None and y_pred is not None:
            fig = self.plot_forecast_error(y_true=y_true, y_pred=y_pred, dates=dates)
            self.save_plot(fig, output_dir / f'{prefix}_forecast_error.png')
        
        # 3. Cumulative P&L
        if equity_curve is not None:
            fig = self.plot_cumulative_pnl(
                equity_curve=equity_curve,
                initial_capital=initial_capital,
                dates=dates
            )
            self.save_plot(fig, output_dir / f'{prefix}_cumulative_pnl.png')
        elif 'cumulative_pnl' in results:
            fig = self.plot_cumulative_pnl(cumulative_pnl=results['cumulative_pnl'], dates=dates)
            self.save_plot(fig, output_dir / f'{prefix}_cumulative_pnl.png')
        
        # 4. Drawdown
        if equity_curve is not None:
            fig = self.plot_drawdown(equity_curve=equity_curve, dates=dates)
            self.save_plot(fig, output_dir / f'{prefix}_drawdown.png')
        
        # 5. Trade Distribution
        if trades:
            trade_pnls = [t.get('pnl', 0) * initial_capital if isinstance(t, dict) else t 
                          for t in trades]
            if trade_pnls:
                fig = self.plot_trade_distribution(trade_pnls)
                self.save_plot(fig, output_dir / f'{prefix}_trade_distribution.png')
        
        # 6. Metrics Summary
        if performance:
            fig = self.plot_metrics_summary(performance)
            self.save_plot(fig, output_dir / f'{prefix}_metrics_summary.png')
        
        logger.info(f"Backtest report generated: {len(list(output_dir.glob(f'{prefix}_*.png')))} plots")

