# Epic 3 & Epic 4: Manual Test Cases

**Project**: Energy Price Forecasting System  
**Date**: December 15, 2025  
**Epic 3 Status**: ✅ 100% Complete (7/7 features)  
**Epic 4 Status**: 📋 Not Started (0/9 features)

---

## Executive Summary

### Epic 3: Model Evaluation & Backtesting
**Status**: ✅ **COMPLETE** (100%)  
**Description**: Comprehensive backtesting framework with walk-forward validation, statistical metrics, trading signal generation, simulation engine, risk metrics, model comparison, and visualization tools.

**Features**:
1. ✅ Walk-Forward Validation Framework
2. ✅ Statistical Metrics Calculation
3. ✅ Trading Signal Generation Logic
4. ✅ Trading Simulation Engine
5. ✅ Risk Metrics Module
6. ✅ Model Comparison Dashboard
7. ✅ Backtesting Visualization Tools

### Epic 4: API Service Layer
**Status**: 📋 **NOT STARTED** (0%)  
**Description**: Production-ready REST API service to expose forecasting functionality.

**Features** (Planned):
1. 📋 FastAPI Application Setup
2. 📋 Forecast Endpoint (`/forecast`)
3. 📋 Historical Data Endpoint (`/historical`)
4. 📋 Model Info Endpoint (`/models`)
5. 📋 Backtesting Endpoint (`/backtest`)
6. 📋 Authentication & API Key Management
7. 📋 Rate Limiting & Caching (Redis)
8. 📋 API Documentation (Swagger UI)
9. 📋 Health Check & Monitoring Endpoints

---

## How to Test Epic Completion

### Epic 3 Testing Approach
1. **Unit Tests**: Run `pytest tests/` in `src/energy-price-forecasting/`
2. **Manual Integration Tests**: Use example scripts in `src/energy-price-forecasting/examples/`
3. **Feature-Specific Tests**: Each feature has dedicated test scripts
4. **Visual Inspection**: Review generated plots and reports

### Epic 4 Testing Approach
1. **API Endpoint Tests**: Use `curl`, Postman, or Python `requests`
2. **Integration Tests**: Test end-to-end workflows
3. **Performance Tests**: Measure response times
4. **Security Tests**: Validate authentication and rate limiting
5. **Documentation Tests**: Verify Swagger UI accessibility

---

## Manual Test Cases

### EPIC 3: Model Evaluation & Backtesting

#### Feature 3.1: Walk-Forward Validation Framework

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-3.1.1 | Walk-Forward Expanding Window Validation | Run: `python examples/test_epic2_step4_training_infrastructure.py` (includes walk-forward). Verify expanding window mode creates increasing training sets. | Training window expands with each fold. All folds complete without errors. Metrics calculated for each fold. |
| TC-3.1.2 | Walk-Forward Rolling Window Validation | Modify test script to use `expanding=False` in `WalkForwardValidator`. Run validation. | Training window size remains constant. Window slides forward by step_size. All folds complete successfully. |
| TC-3.1.3 | Walk-Forward Temporal Integrity | Run walk-forward validation. Check that test data never overlaps with training data. | No temporal leakage. Test indices always after training indices. Validation results are realistic. |
| TC-3.1.4 | Walk-Forward Aggregated Metrics | Run validation and call `get_aggregated_metrics()`. Verify mean, std, min, max calculated. | Aggregated metrics DataFrame returned. Summary statistics calculated correctly. No NaN values in summary. |
| TC-3.1.5 | Walk-Forward Error Handling | Run validation with insufficient data (less than train_window + test_window). | Appropriate error message. Validation fails gracefully. No crashes. |

#### Feature 3.2: Statistical Metrics Calculation

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-3.2.1 | Calculate RMSE | Create `StatisticalMetrics()` instance. Call `calculate_rmse(y_true, y_pred)` with known values. | RMSE calculated correctly. Matches manual calculation. Returns float. |
| TC-3.2.2 | Calculate MAE | Call `calculate_mae(y_true, y_pred)` with test data. | MAE calculated correctly. Always positive. Returns float. |
| TC-3.2.3 | Calculate MAPE | Call `calculate_mape(y_true, y_pred)` with test data. | MAPE calculated correctly. Returns percentage (0-100). Handles zero values gracefully. |
| TC-3.2.4 | Calculate R² | Call `calculate_r2(y_true, y_pred)` with test data. | R² calculated correctly. Value between -inf and 1.0. Higher is better. |
| TC-3.2.5 | Calculate Directional Accuracy | Call `calculate_directional_accuracy(y_true, y_pred)` with price series. | Accuracy between 0 and 1. Correctly identifies direction matches. Returns float. |
| TC-3.2.6 | Calculate All Metrics | Call `calculate_all(y_true, y_pred)`. Verify all metrics returned. | Dictionary with RMSE, MAE, MAPE, R2, Directional_Accuracy. All values valid. |
| TC-3.2.7 | Per-Horizon Metrics | Call `calculate_per_horizon()` with multi-horizon predictions. | Metrics calculated for each horizon (1-day, 7-day, 30-day). Dictionary structure correct. |
| TC-3.2.8 | Model Comparison | Call `compare_models(y_true, predictions_dict)` with multiple models. | DataFrame returned with models as rows, metrics as columns. All models compared. |

#### Feature 3.3: Trading Signal Generation Logic

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-3.3.1 | Threshold Strategy | Create `SignalGenerator(strategy='threshold', threshold=0.02)`. Call `generate(predictions, prices)`. | Signals generated: 1 (buy), -1 (sell), 0 (hold). Signals match threshold logic. |
| TC-3.3.2 | Momentum Strategy | Create `SignalGenerator(strategy='momentum')`. Generate signals with price series. | Signals based on momentum. Positive momentum → buy, negative → sell. |
| TC-3.3.3 | Mean Reversion Strategy | Create `SignalGenerator(strategy='mean_reversion')`. Generate signals. | Signals based on deviation from mean. Overvalued → sell, undervalued → buy. |
| TC-3.3.4 | Trend Following Strategy | Create `SignalGenerator(strategy='trend_following')`. Generate signals. | Signals follow trend direction. Uptrend → buy, downtrend → sell. |
| TC-3.3.5 | Combined Strategy | Create `SignalGenerator(strategy='combined')`. Generate signals. | Signals combine multiple strategies. Weighted decision making. |
| TC-3.3.6 | Custom Strategy | Create `SignalGenerator(strategy=custom_function)`. Generate signals. | Custom function called correctly. Signals generated as expected. |
| TC-3.3.7 | Signal Summary Statistics | Call `get_signal_summary(signals)`. | Dictionary with buy_count, sell_count, hold_count, signal_distribution. Statistics accurate. |

#### Feature 3.4: Trading Simulation Engine

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-3.4.1 | Basic Backtest | Create `BacktestingEngine()`. Call `backtest(predictions, prices)`. | Results dictionary returned. Contains 'performance', 'trades', 'equity_curve'. No errors. |
| TC-3.4.2 | Custom Strategy Backtest | Create engine. Call `backtest(predictions, prices, strategy=custom_strategy)`. | Custom strategy used. Results reflect strategy logic. Trades executed correctly. |
| TC-3.4.3 | Commission and Slippage | Create engine with `commission=0.001, slippage=0.0005`. Run backtest. | Transaction costs applied. Final capital accounts for costs. Costs visible in trade records. |
| TC-3.4.4 | P&L Tracking | Run backtest. Check 'trades' list. Verify P&L per trade. | Each trade has 'pnl' field. P&L calculated correctly. Cumulative P&L matches equity curve. |
| TC-3.4.5 | Win Rate Calculation | Run backtest. Check `performance['win_rate']`. | Win rate between 0 and 1. Calculated as winning_trades / total_trades. Accurate count. |
| TC-3.4.6 | Equity Curve | Run backtest. Check 'equity_curve' in results. | Equity curve array returned. Length matches number of periods. Monotonically increasing/decreasing appropriately. |
| TC-3.4.7 | Final Capital | Run backtest. Check `performance['final_capital']` and `results['final_capital']`. | Final capital calculated. Accounts for all trades and costs. Matches last value in equity curve. |

#### Feature 3.5: Risk Metrics Module

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-3.5.1 | Sharpe Ratio Calculation | Create `PerformanceMetrics()`. Call `calculate_sharpe_ratio(returns)`. | Sharpe ratio calculated. Annualized correctly. Accounts for risk-free rate. Returns float. |
| TC-3.5.2 | Sortino Ratio Calculation | Call `calculate_sortino_ratio(returns)`. | Sortino ratio calculated. Uses downside deviation only. Higher than Sharpe for asymmetric returns. |
| TC-3.5.3 | Maximum Drawdown | Call `calculate_max_drawdown(prices)`. | Returns (max_dd, start_idx, end_idx). Max drawdown is positive percentage. Indices valid. |
| TC-3.5.4 | Volatility Calculation | Call `calculate_all(prices=prices, returns=returns)`. Check 'volatility'. | Annualized volatility calculated. Standard deviation * sqrt(252). Returns float. |
| TC-3.5.5 | Total Return | Call `calculate_all()` with returns. Check 'total_return'. | Total return calculated. Cumulative product of (1 + returns) - 1. Accurate. |
| TC-3.5.6 | Annualized Return | Check 'annualized_return' in results. | Annualized return calculated. Accounts for number of periods. Realistic value. |
| TC-3.5.7 | Comprehensive Metrics | Call `calculate_all()` with prices, returns, y_true, y_pred. | All metrics returned: sharpe, sortino, max_drawdown, volatility, total_return, directional_accuracy. Dictionary complete. |

#### Feature 3.6: Model Comparison Dashboard

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-3.6.1 | Model Comparison Table | Create `ModelComparisonDashboard()`. Call `compare_models(y_true, predictions, equity_curves)`. | DataFrame returned. Models as rows, metrics as columns. Statistical and risk metrics included. |
| TC-3.6.2 | Comparison Table Sorting | Call `get_comparison_table(sort_by='sharpe_ratio')`. | DataFrame sorted by Sharpe ratio. Descending order. NaN values handled. |
| TC-3.6.3 | Best Model Selection | Call `select_best_model(primary_metric='sharpe_ratio')`. | Dictionary returned with 'model_name', 'primary_metric', 'primary_value', 'metrics'. Best model identified correctly. |
| TC-3.6.4 | Best Model Tie Breaking | Create scenario with tied primary metric. Call `select_best_model()` with secondary_metric. | Best model selected using secondary metric. Tie broken correctly. |
| TC-3.6.5 | Export CSV | Call `export_comparison_report('output.csv', format='csv')`. | CSV file created. Contains comparison table. Metadata included as comments. |
| TC-3.6.6 | Export JSON | Call `export_comparison_report('output.json', format='json')`. | JSON file created. Contains comparison_table, metadata, best_model. Valid JSON structure. |
| TC-3.6.7 | Summary Generation | Call `get_summary()`. | Dictionary with num_models, metrics_available, best_model, comparison_table. Summary accurate. |

#### Feature 3.7: Backtesting Visualization Tools

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-3.7.1 | Predicted vs Actual Plot | Create `BacktestingVisualizer()`. Call `plot_predicted_vs_actual(y_true, y_pred, dates)`. | Matplotlib figure returned. Two lines plotted (actual, predicted). Legend present. Title set. |
| TC-3.7.2 | Forecast Error Plot | Call `plot_forecast_error(y_true=y_true, y_pred=y_pred)`. | Error line plotted. Zero line highlighted. Errors calculated correctly. |
| TC-3.7.3 | Cumulative P&L Chart | Call `plot_cumulative_pnl(equity_curve=equity, initial_capital=10000)`. | P&L line plotted. Break-even line (y=0) shown. P&L calculated from equity curve. |
| TC-3.7.4 | Drawdown Chart | Call `plot_drawdown(equity_curve=equity)`. | Area plot created. Drawdown filled in red. Maximum drawdown annotated. |
| TC-3.7.5 | Trade Distribution Histogram | Call `plot_trade_distribution(trade_pnls)`. | Histogram created. Zero line shown. Mean and std lines displayed. |
| TC-3.7.6 | Metrics Summary Table | Call `plot_metrics_summary(metrics_dict)`. | Table created. Metrics and values displayed. Header styled. |
| TC-3.7.7 | Save Plot PNG | Create plot. Call `save_plot(fig, 'test.png')`. | PNG file created. High resolution (300 DPI). File exists and is readable. |
| TC-3.7.8 | Save Plot PDF | Call `save_plot(fig, 'test.pdf', format='pdf')`. | PDF file created. Vector format. File exists. |
| TC-3.7.9 | Comprehensive Report | Call `generate_backtest_report(results, 'output_dir')`. | All plots generated. Files saved with consistent naming. Directory contains all visualizations. |

---

### EPIC 4: API Service Layer

**Note**: Epic 4 is not yet implemented. Test cases below are based on planned features and should be executed once implementation is complete.

#### Feature 4.1: FastAPI Application Setup

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-4.1.1 | Application Initialization | Start FastAPI app: `uvicorn main:app --reload`. Check root endpoint: `curl http://localhost:8000/`. | App starts without errors. Root endpoint returns `{"message": "Energy Price Forecasting API", "version": "1.0.0"}`. |
| TC-4.1.2 | CORS Configuration | Make cross-origin request from browser console: `fetch('http://localhost:8000/')`. | CORS headers present. Request succeeds. No CORS errors. |
| TC-4.1.3 | Environment Variables | Set environment variables. Start app. Check settings loaded. | Settings loaded from .env file. Required variables validated. App starts successfully. |
| TC-4.1.4 | Application Structure | Review project structure. Verify `main.py`, `api/`, `models/`, `config/` directories. | Structure follows FastAPI best practices. Modules organized logically. |

#### Feature 4.2: Forecast Endpoint (`/forecast`)

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-4.2.1 | Basic Forecast Request | POST to `/api/v1/forecast` with `{"commodity": "WTI", "horizon": 7, "model_id": "lstm_wti_v1"}`. | Response 200. Contains 'forecast', 'confidence_intervals', 'model_info'. Forecast values are floats. |
| TC-4.2.2 | Multiple Horizons | Request with `"horizon": [1, 7, 30]`. | Response contains forecasts for all horizons. Structure: `{"1": [...], "7": [...], "30": [...]}`. |
| TC-4.2.3 | Invalid Commodity | Request with `"commodity": "INVALID"`. | Response 400. Error message: "Invalid commodity. Available: WTI, BRENT, NATURAL_GAS". |
| TC-4.2.4 | Invalid Model | Request with `"model_id": "nonexistent"`. | Response 404. Error message: "Model not found". |
| TC-4.2.5 | Missing Required Fields | POST with empty body `{}`. | Response 422. Validation error listing missing fields. |
| TC-4.2.6 | Response Time | Measure time for forecast request. | Response time < 500ms (95th percentile). Acceptable for production. |

#### Feature 4.3: Historical Data Endpoint (`/historical`)

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-4.3.1 | Get Historical Data | GET `/api/v1/historical?commodity=WTI&start_date=2024-01-01&end_date=2024-12-31`. | Response 200. JSON array of price records. Each record has 'date', 'price', 'volume'. |
| TC-4.3.2 | Pagination | GET with `limit=10&offset=0`. Then `limit=10&offset=10`. | First request returns 10 records. Second returns next 10. No duplicates. |
| TC-4.3.3 | Date Range Validation | GET with `start_date=2024-12-31&end_date=2024-01-01` (invalid). | Response 400. Error: "start_date must be before end_date". |
| TC-4.3.4 | Filter by Commodity | GET with `commodity=BRENT`. | Only BRENT prices returned. No WTI or other commodities. |
| TC-4.3.5 | Empty Result | GET with date range that has no data. | Response 200. Empty array `[]`. No error. |
| TC-4.3.6 | Large Date Range | GET with 5-year range. | Response time acceptable. Data returned (may be paginated). |

#### Feature 4.4: Model Info Endpoint (`/models`)

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-4.4.1 | List All Models | GET `/api/v1/models`. | Response 200. JSON with 'models' array. Each model has 'model_id', 'commodity', 'model_type', 'version', 'metrics'. |
| TC-4.4.2 | Filter by Commodity | GET `/api/v1/models?commodity=WTI`. | Only WTI models returned. Filtering works correctly. |
| TC-4.4.3 | Model Metrics | Check metrics in response: 'rmse', 'mae', 'sharpe_ratio', etc. | All metrics present. Values are floats. Metrics are recent/accurate. |
| TC-4.4.4 | Model Metadata | Check 'training_date', 'version', 'model_type' fields. | All metadata present. Dates are valid. Versions are strings. |
| TC-4.4.5 | Empty Model List | Request when no models registered. | Response 200. Empty array `[]`. No error. |

#### Feature 4.5: Backtesting Endpoint (`/backtest`)

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-4.5.1 | Basic Backtest Request | POST `/api/v1/backtest` with `{"model_id": "lstm_wti_v1", "start_date": "2024-01-01", "end_date": "2024-12-31", "initial_capital": 100000}`. | Response 200 or 202 (async). Contains 'backtest_id' or full results. Results include 'performance', 'trades', 'equity_curve'. |
| TC-4.5.2 | Async Backtest | POST backtest request. Check response has 'backtest_id'. GET `/api/v1/backtest/{backtest_id}/status`. | Initial response 202. Status endpoint shows progress. Final status 'completed' with results. |
| TC-4.5.3 | Strategy Parameters | POST with `"strategy_params": {"threshold": 0.02, "strategy": "threshold"}`. | Backtest uses custom strategy. Results reflect strategy parameters. |
| TC-4.5.4 | Invalid Date Range | POST with `start_date` after `end_date`. | Response 400. Error message about invalid date range. |
| TC-4.5.5 | Backtest Results Caching | Run same backtest twice. Check response times. | Second request faster (cached). Results identical. Cache TTL respected. |
| TC-4.5.6 | Large Backtest | POST with 2-year date range. | Request accepted. Processing time acceptable or async. Results complete. |

#### Feature 4.6: Authentication & API Key Management

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-4.6.1 | API Key Generation | POST `/api/v1/auth/generate-key` with user credentials. | Response 200. Returns API key. Key is long random string. Stored securely (hashed). |
| TC-4.6.2 | Authenticated Request | GET `/api/v1/forecast` with header `X-API-Key: {valid_key}`. | Request succeeds. Response 200. Forecast returned. |
| TC-4.6.3 | Missing API Key | GET `/api/v1/forecast` without API key header. | Response 401. Error: "API key required". No data returned. |
| TC-4.6.4 | Invalid API Key | GET with header `X-API-Key: invalid_key`. | Response 401. Error: "Invalid API key". |
| TC-4.6.5 | Revoked API Key | Revoke key via admin endpoint. Then use revoked key. | Response 401. Error: "API key revoked". Key no longer works. |
| TC-4.6.6 | Key Expiration | Use expired API key. | Response 401. Error: "API key expired". |
| TC-4.6.7 | Rate Limit per Key | Make 100 requests rapidly with same key. | After rate limit (e.g., 100/hour), response 429. Error: "Rate limit exceeded". |

#### Feature 4.7: Rate Limiting & Caching

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-4.7.1 | Rate Limiting | Make 100 requests rapidly to `/api/v1/forecast`. | After limit (e.g., 100/hour), response 429. Header `X-RateLimit-Remaining: 0`. |
| TC-4.7.2 | Rate Limit Headers | Check response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`. | Headers present. Values accurate. Reset time is future timestamp. |
| TC-4.7.3 | Caching Forecast | Make identical forecast request twice. | Second response faster. Response time < 50ms (cached). Results identical. |
| TC-4.7.4 | Cache Invalidation | Update model. Make forecast request. | Cache invalidated. Fresh forecast returned. Not using stale cache. |
| TC-4.7.5 | Redis Connection | Check Redis is running. Make cached request. | Cache works. No Redis connection errors. |
| TC-4.7.6 | Cache TTL | Make request. Wait for TTL expiration. Make same request. | First request cached. After TTL, fresh data returned. Cache expired correctly. |

#### Feature 4.8: API Documentation (Swagger UI)

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-4.8.1 | Swagger UI Access | Open browser: `http://localhost:8000/docs`. | Swagger UI loads. All endpoints visible. Interactive documentation works. |
| TC-4.8.2 | OpenAPI Schema | GET `/openapi.json`. | Valid OpenAPI 3.0 schema returned. All endpoints documented. Request/response schemas present. |
| TC-4.8.3 | Endpoint Documentation | Check each endpoint in Swagger UI. | Descriptions present. Parameters documented. Example requests shown. |
| TC-4.8.4 | Try It Out | Use "Try it out" in Swagger UI for `/forecast`. Execute request. | Request executes. Response shown. Works as documented. |
| TC-4.8.5 | ReDoc Access | Open `http://localhost:8000/redoc`. | ReDoc loads. Alternative documentation format. All endpoints visible. |

#### Feature 4.9: Health Check & Monitoring Endpoints

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-4.9.1 | Health Check | GET `/health`. | Response 200. `{"status": "healthy", "timestamp": "..."}`. |
| TC-4.9.2 | Readiness Check | GET `/ready`. | Response 200 if all dependencies available. Checks database, Redis, ML models. |
| TC-4.9.3 | Liveness Check | GET `/live`. | Response 200. Simple liveness probe. Always returns 200 if app running. |
| TC-4.9.4 | Health Check Failure | Stop database. GET `/ready`. | Response 503. `{"status": "unhealthy", "dependencies": {"database": "down"}}`. |
| TC-4.9.5 | Metrics Endpoint | GET `/metrics` (Prometheus format). | Metrics returned. Includes request_count, error_count, response_time. Format correct. |
| TC-4.9.6 | Status Endpoint | GET `/status`. | Detailed status: uptime, version, dependencies, cache status. JSON response. |

---

## Test Execution Summary

### Epic 3 Test Execution
1. **Prerequisites**: 
   - Python 3.8+ installed
   - Dependencies: `pip install -r requirements.txt`
   - Test data available in `examples/` directory

2. **Execution Order**:
   - Run unit tests: `pytest tests/ -v`
   - Run feature-specific manual tests: `python examples/test_epic2_step*.py`
   - Execute manual test cases TC-3.1.1 through TC-3.7.9
   - Review generated visualizations and reports

3. **Success Criteria**:
   - All unit tests pass
   - All manual test cases execute without errors
   - Visualizations generated correctly
   - Metrics calculated accurately

### Epic 4 Test Execution
1. **Prerequisites**:
   - FastAPI application running
   - Database connected
   - Redis running (for caching)
   - API keys generated

2. **Execution Order**:
   - Start API server: `uvicorn main:app --reload`
   - Test endpoints using curl, Postman, or Python requests
   - Execute manual test cases TC-4.1.1 through TC-4.9.6
   - Verify Swagger UI and documentation

3. **Success Criteria**:
   - All endpoints respond correctly
   - Authentication works
   - Rate limiting enforced
   - Documentation accessible
   - Health checks pass

---

## Notes

- **Epic 3**: All features are implemented and tested. Manual test cases can be executed immediately.
- **Epic 4**: Not yet implemented. Test cases are based on planned features and should be executed after implementation.
- **Test Data**: Use sample data from `examples/` directory or generate synthetic data for testing.
- **Environment**: Ensure all dependencies are installed and services (database, Redis) are running before testing.

---

**Document Version**: 1.0  
**Last Updated**: December 15, 2025  
**Status**: Ready for Manual Testing

