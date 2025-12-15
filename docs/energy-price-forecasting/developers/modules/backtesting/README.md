# Backtesting Module

**Purpose**: Trading simulation and performance evaluation for ML models

---

## Overview

The backtesting module provides comprehensive tools for simulating trading strategies on historical data, calculating performance metrics, and visualizing results. It includes walk-forward validation, trading signal generation, and risk metrics calculation.

---

## File Structure

```
evaluation/
├── __init__.py                    # Module exports
├── walk_forward.py               # Walk-forward validation
├── trading_simulator.py          # Trading simulation engine
├── statistical_metrics.py        # Statistical evaluation metrics
├── performance_metrics.py         # Risk-adjusted performance metrics
├── backtesting.py                 # Main backtesting engine
├── visualization.py               # Result visualization
└── model_comparison_dashboard.py # Model comparison tools
```

---

## Key Classes

### WalkForwardValidator (`walk_forward.py`)

**Purpose**: Walk-forward validation for time-series models

**Key Methods**:
- `validate(model, data, train_window, test_window)`: Run walk-forward validation
- `expanding_window()`: Expanding training window
- `rolling_window()`: Rolling training window

**Usage**:
```python
from evaluation.walk_forward import WalkForwardValidator

validator = WalkForwardValidator()
results = validator.validate(
    model=model,
    data=data,
    train_window=365,  # 1 year
    test_window=30    # 1 month
)
```

---

### TradingSimulator (`trading_simulator.py`)

**Purpose**: Simulate trading strategies on historical data

**Key Methods**:
- `simulate(strategy, data, initial_capital)`: Run trading simulation
- `generate_signals(predictions, strategy)`: Generate trading signals
- `execute_trade(signal, price, commission, slippage)`: Execute trade
- `calculate_pnl(positions)`: Calculate profit/loss

**Usage**:
```python
from evaluation.trading_simulator import TradingSimulator

simulator = TradingSimulator()
results = simulator.simulate(
    strategy='threshold',
    data=historical_data,
    initial_capital=100000,
    commission=0.001,
    slippage=0.0005
)
```

---

### StatisticalMetrics (`statistical_metrics.py`)

**Purpose**: Calculate statistical evaluation metrics

**Key Methods**:
- `calculate_rmse(predictions, actuals)`: Root Mean Squared Error
- `calculate_mae(predictions, actuals)`: Mean Absolute Error
- `calculate_mape(predictions, actuals)`: Mean Absolute Percentage Error
- `calculate_r2(predictions, actuals)`: R² score
- `calculate_directional_accuracy(predictions, actuals)`: Directional accuracy

**Usage**:
```python
from evaluation.statistical_metrics import StatisticalMetrics

metrics = StatisticalMetrics()
rmse = metrics.calculate_rmse(predictions, actuals)
mae = metrics.calculate_mae(predictions, actuals)
mape = metrics.calculate_mape(predictions, actuals)
```

---

### PerformanceMetrics (`performance_metrics.py`)

**Purpose**: Calculate risk-adjusted performance metrics

**Key Methods**:
- `calculate_sharpe_ratio(returns, risk_free_rate)`: Sharpe ratio
- `calculate_sortino_ratio(returns, risk_free_rate)`: Sortino ratio
- `calculate_max_drawdown(equity_curve)`: Maximum drawdown
- `calculate_calmar_ratio(returns, max_drawdown)`: Calmar ratio
- `calculate_win_rate(trades)`: Win rate

**Usage**:
```python
from evaluation.performance_metrics import PerformanceMetrics

metrics = PerformanceMetrics()
sharpe = metrics.calculate_sharpe_ratio(returns, risk_free_rate=0.02)
max_dd = metrics.calculate_max_drawdown(equity_curve)
win_rate = metrics.calculate_win_rate(trades)
```

---

### BacktestingEngine (`backtesting.py`)

**Purpose**: Main backtesting orchestration

**Key Methods**:
- `run_backtest(model, data, strategy, params)`: Run complete backtest
- `generate_equity_curve(trades)`: Generate equity curve
- `generate_trade_history(trades)`: Generate trade history

**Usage**:
```python
from evaluation.backtesting import BacktestingEngine

engine = BacktestingEngine()
results = engine.run_backtest(
    model=model,
    data=historical_data,
    strategy='threshold',
    params={'threshold': 0.02}
)
```

---

## Trading Strategies

### Threshold Strategy
Buy when forecast predicts price increase above threshold, sell when decrease.

### Momentum Strategy
Follow price momentum trends.

### Mean Reversion Strategy
Trade when price deviates from mean.

### Breakout Strategy
Trade when price breaks resistance/support levels.

### Ensemble Strategy
Combine signals from multiple models.

---

## Performance Metrics

### Statistical Metrics
- **RMSE**: Root Mean Squared Error
- **MAE**: Mean Absolute Error
- **MAPE**: Mean Absolute Percentage Error
- **R²**: Coefficient of determination
- **Directional Accuracy**: Percentage of correct direction predictions

### Risk Metrics
- **Sharpe Ratio**: Risk-adjusted return
- **Sortino Ratio**: Downside risk-adjusted return
- **Max Drawdown**: Largest peak-to-trough decline
- **Calmar Ratio**: Return / Max Drawdown
- **Win Rate**: Percentage of profitable trades

---

## Visualization

**BacktestingVisualizer** (`visualization.py`):
- Equity curve plots
- Trade history visualization
- Performance metrics charts
- Drawdown visualization

**Usage**:
```python
from evaluation.visualization import BacktestingVisualizer

visualizer = BacktestingVisualizer()
visualizer.plot_equity_curve(results['equity_curve'])
visualizer.plot_trades(results['trades'])
```

---

## Testing

**Test Files**:
- `tests/test_backtesting.py`
- `tests/test_trading_simulator.py`
- `tests/test_performance_metrics.py`

**Run Tests**:
```bash
pytest tests/test_backtesting.py -v
pytest tests/test_trading_simulator.py -v
```

---

## Dependencies

- `pandas`: Data manipulation
- `numpy`: Numerical operations
- `matplotlib`: Visualization
- `scipy`: Statistical functions

---

## Integration

The backtesting module is used by:
- **API**: Backtest endpoint
- **Model Evaluation**: Model comparison
- **Strategy Development**: Strategy testing

---

## Best Practices

1. **Realistic Parameters**: Include commission and slippage
2. **Sufficient Data**: Use at least 6 months of data
3. **Multiple Strategies**: Test different strategies
4. **Risk Management**: Monitor max drawdown
5. **Out-of-Sample Testing**: Reserve data for final validation

---

## Extending

To add new strategies:

1. Create strategy function
2. Add to `TradingSimulator`
3. Update configuration
4. Add tests
5. Update documentation

---

**Last Updated**: December 15, 2025

