# Backtesting Features

**Time to Read**: 3 minutes

---

## Overview

Backtesting allows you to test trading strategies on historical data to evaluate performance before risking real capital. Simulate trades, calculate returns, and analyze risk metrics.

---

## What is Backtesting?

Backtesting simulates how a trading strategy would have performed on historical data. It helps you:
- **Evaluate Strategies**: Test if a strategy is profitable
- **Optimize Parameters**: Find best threshold values
- **Assess Risk**: Understand potential drawdowns
- **Compare Models**: See which model performs best

---

## How It Works

1. **Select Model**: Choose an ML model to test
2. **Set Date Range**: Historical period to test
3. **Configure Strategy**: Choose trading strategy and parameters
4. **Run Backtest**: System simulates trades
5. **View Results**: See performance metrics and trade history

---

## Trading Strategies

### 1. Threshold Strategy
Buy when forecast predicts price increase above threshold, sell when decrease.

**Parameters**:
- **Threshold**: Minimum price change to trigger trade (e.g., 2%)

### 2. Momentum Strategy
Follow price momentum trends.

**Parameters**:
- **Lookback Period**: Days to calculate momentum
- **Momentum Threshold**: Minimum momentum to trade

### 3. Mean Reversion Strategy
Trade when price deviates from mean.

**Parameters**:
- **Deviation Threshold**: Standard deviations from mean
- **Mean Period**: Days to calculate mean

### 4. Breakout Strategy
Trade when price breaks resistance/support levels.

**Parameters**:
- **Breakout Threshold**: Price change to confirm breakout

### 5. Ensemble Strategy
Combine signals from multiple models.

**Parameters**:
- **Voting Threshold**: Minimum models agreeing

---

## Using the Dashboard

### Step-by-Step

1. Navigate to **Backtest** page
2. Select **Model** from dropdown
3. Set **Date Range** (start and end dates)
4. Configure **Capital**:
   - Initial Capital: Starting amount (e.g., $100,000)
   - Commission: Trading fees (e.g., 0.1%)
   - Slippage: Price impact (e.g., 0.05%)
5. Select **Strategy** and set parameters
6. Click **Run Backtest**
7. View results:
   - Performance metrics
   - Equity curve chart
   - Trade history table

---

## Understanding Results

### Performance Metrics

- **Total Return**: Overall profit/loss percentage
- **Sharpe Ratio**: Risk-adjusted return (higher is better)
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Average Return**: Average profit per trade

### Equity Curve

Shows how your capital would have changed over time. Look for:
- **Upward Trend**: Profitable strategy
- **Smooth Growth**: Consistent performance
- **Large Drawdowns**: High risk periods

### Trade History

List of all simulated trades with:
- Entry/Exit dates and prices
- Position type (Long/Short)
- Profit/Loss per trade

---

## Using the API

### Request Example

```bash
POST /api/v1/backtest
Content-Type: application/json

{
  "model_id": "lstm_wti_v1",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000,
  "commission": 0.001,
  "slippage": 0.0005,
  "strategy": "threshold",
  "strategy_params": {
    "threshold": 0.02
  }
}
```

### Response Example

```json
{
  "model_id": "lstm_wti_v1",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "metrics": {
    "total_return": 0.15,
    "sharpe_ratio": 1.35,
    "max_drawdown": 0.08,
    "win_rate": 0.65
  },
  "equity_curve": {
    "dates": ["2024-01-01", ...],
    "values": [100000, ...]
  },
  "trades": [...]
}
```

---

## Best Practices

1. **Use Sufficient Data**: 
   - Test on at least 6 months of data
   - Include different market conditions

2. **Realistic Parameters**: 
   - Include commission and slippage
   - Use realistic capital amounts

3. **Multiple Strategies**: 
   - Test different strategies
   - Compare performance

4. **Risk Management**: 
   - Monitor max drawdown
   - Ensure Sharpe ratio > 1.0

5. **Out-of-Sample Testing**: 
   - Don't optimize on test data
   - Reserve some data for final validation

---

## Interpreting Results

### Good Performance Indicators

- ✅ Sharpe Ratio > 1.0
- ✅ Win Rate > 50%
- ✅ Max Drawdown < 20%
- ✅ Consistent equity curve growth

### Warning Signs

- ⚠️ High drawdowns (>30%)
- ⚠️ Low win rate (<40%)
- ⚠️ Negative Sharpe ratio
- ⚠️ Erratic equity curve

---

## Limitations

- **Past Performance ≠ Future Results**: Historical success doesn't guarantee future profits
- **Market Changes**: Strategies may stop working as markets evolve
- **Transaction Costs**: Real trading may have higher costs
- **Slippage**: Real execution may differ from backtest

---

## Next Steps

- **Compare Models**: Test multiple models to find the best
- **Optimize Strategies**: Adjust parameters for better performance
- **Analytics**: Use [Analytics Features](analytics.md) for deeper insights
- **Real Trading**: Start with paper trading before using real capital

---

**Last Updated**: December 15, 2025

