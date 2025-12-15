# Backtesting Workflow

**Version**: 1.0  
**Date**: December 15, 2025  
**Status**: ✅ Complete

---

## Backtesting Workflow Diagram

```mermaid
flowchart TD
    START([Backtest Request]) --> LOAD[Load Historical Data]
    LOAD --> LOAD_MODEL[Load Model]
    LOAD_MODEL --> WALK_FORWARD[Walk-Forward Validation]
    
    WALK_FORWARD --> TRAIN_WIN[Training Window]
    TRAIN_WIN --> TEST_WIN[Test Window]
    TEST_WIN --> GENERATE[Generate Predictions]
    
    GENERATE --> SIGNALS[Generate Trading Signals]
    SIGNALS --> STRATEGY{Select Strategy}
    
    STRATEGY --> THRESHOLD[Threshold Strategy]
    STRATEGY --> MOMENTUM[Momentum Strategy]
    STRATEGY --> MEAN_REV[Mean Reversion]
    STRATEGY --> BREAKOUT[Breakout Strategy]
    STRATEGY --> ENSEMBLE[Ensemble Strategy]
    
    THRESHOLD --> SIMULATE[Trading Simulation]
    MOMENTUM --> SIMULATE
    MEAN_REV --> SIMULATE
    BREAKOUT --> SIMULATE
    ENSEMBLE --> SIMULATE
    
    SIMULATE --> INIT_CAP[Initialize Capital]
    INIT_CAP --> LOOP[For Each Period]
    
    LOOP --> CHECK_SIGNAL{Signal?}
    CHECK_SIGNAL -->|Buy| BUY[Execute Buy]
    CHECK_SIGNAL -->|Sell| SELL[Execute Sell]
    CHECK_SIGNAL -->|Hold| HOLD[No Action]
    
    BUY --> COMMISSION[Apply Commission]
    SELL --> COMMISSION
    HOLD --> UPDATE[Update Position]
    COMMISSION --> SLIPPAGE[Apply Slippage]
    SLIPPAGE --> UPDATE
    
    UPDATE --> PNL[Calculate P&L]
    PNL --> MORE{More Periods?}
    MORE -->|Yes| LOOP
    MORE -->|No| METRICS[Calculate Metrics]
    
    METRICS --> STATS[Statistical Metrics<br/>RMSE, MAE, MAPE]
    METRICS --> RISK[Risk Metrics<br/>Sharpe, Sortino, Max DD]
    METRICS --> TRADE[Trade Metrics<br/>Win Rate, Avg Return]
    
    STATS --> AGGREGATE[Aggregate Results]
    RISK --> AGGREGATE
    TRADE --> AGGREGATE
    
    AGGREGATE --> EQUITY[Generate Equity Curve]
    EQUITY --> TRADES[Generate Trade History]
    TRADES --> RESPONSE[Backtest Response]
    
    style START fill:#e1f5ff
    style SIMULATE fill:#fff4e1
    style METRICS fill:#fff9c4
    style RESPONSE fill:#e8f5e9
```

---

## Trading Signal Generation Flow

```mermaid
flowchart LR
    PREDICT[Model Prediction] --> COMPARE{Compare with<br/>Current Price}
    COMPARE --> THRESHOLD{Threshold<br/>Met?}
    THRESHOLD -->|Yes| DIRECTION{Price<br/>Direction?}
    THRESHOLD -->|No| HOLD[Hold Signal]
    
    DIRECTION -->|Up| BUY[Buy Signal]
    DIRECTION -->|Down| SELL[Sell Signal]
    
    BUY --> CONFIDENCE[Calculate Confidence]
    SELL --> CONFIDENCE
    HOLD --> CONFIDENCE
    
    CONFIDENCE --> SIGNAL[Return Signal]
    
    style PREDICT fill:#e1f5ff
    style SIGNAL fill:#e8f5e9
```

---

## Risk Metrics Calculation Flow

```mermaid
flowchart TD
    TRADES[Trade History] --> RETURNS[Calculate Returns]
    RETURNS --> STATS[Statistical Analysis]
    
    STATS --> SHARPE[Sharpe Ratio<br/>Return/Risk]
    STATS --> SORTINO[Sortino Ratio<br/>Downside Risk]
    STATS --> MAX_DD[Max Drawdown<br/>Peak to Trough]
    STATS --> VOLATILITY[Volatility<br/>Std Dev]
    
    RETURNS --> EQUITY[Equity Curve]
    EQUITY --> DRAWDOWN[Drawdown Series]
    DRAWDOWN --> MAX_DD
    
    SHARPE --> METRICS[Risk Metrics]
    SORTINO --> METRICS
    MAX_DD --> METRICS
    VOLATILITY --> METRICS
    
    style TRADES fill:#e1f5ff
    style METRICS fill:#e8f5e9
```

---

## Model Comparison Workflow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Backtest
    participant Models
    participant Comparator

    User->>API: Request Comparison
    API->>Models: Get All Models
    Models-->>API: Model List
    
    loop For Each Model
        API->>Backtest: Run Backtest
        Backtest-->>API: Results
    end
    
    API->>Comparator: Compare Results
    Comparator->>Comparator: Rank Models
    Comparator->>Comparator: Calculate Metrics
    Comparator-->>API: Comparison Report
    API-->>User: Return Comparison
```

---

**Last Updated**: December 15, 2025

