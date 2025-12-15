"""
Backtesting endpoint routes.

This module implements the /api/v1/backtest endpoint for running
backtests on models.
"""

from fastapi import APIRouter, HTTPException, status
from api.models.backtest import BacktestRequest, BacktestResponse, BacktestMetrics, Trade
from api.services.backtest_service import get_backtest_service
from api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Backtesting"])


@router.post(
    "/backtest",
    response_model=BacktestResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Backtest on Forecasting Model",
    description="""
    Run a backtest simulation on a forecasting model with custom trading strategies.
    
    **Features:**
    - Simulates trading based on model predictions
    - Customizable trading strategies (threshold, momentum, mean reversion, etc.)
    - Configurable commission and slippage
    - Returns performance metrics and trade history
    - Equity curve visualization data
    
    **Request Parameters:**
    - `model_id`: Model identifier (e.g., "WTI_LSTM_v1_Production")
    - `start_date`: Backtest start date (YYYY-MM-DD)
    - `end_date`: Backtest end date (YYYY-MM-DD)
    - `initial_capital`: Starting capital (default: 100000)
    - `commission`: Commission per trade (default: 0.001 = 0.1%)
    - `slippage`: Slippage per trade (default: 0.0005 = 0.05%)
    - `strategy_params`: Trading strategy parameters
    
    **Example Request:**
    ```json
    {
        "model_id": "WTI_LSTM_v1_Production",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "initial_capital": 100000,
        "strategy_params": {
            "strategy_name": "threshold",
            "threshold": 0.02
        }
    }
    ```
    
    **Response includes:**
    - Performance metrics (Sharpe ratio, Sortino ratio, max drawdown, etc.)
    - Trade history with entry/exit prices and P&L
    - Equity curve data
    """,
    responses={
        200: {"description": "Backtest completed successfully"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"}
    }
)
async def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """
    Run a backtest simulation on a forecasting model.
    
    **Parameters:**
    - **model_id**: Model identifier (format: COMMODITY_MODELTYPE_VERSION_STAGE)
    - **start_date**: Backtest start date (YYYY-MM-DD)
    - **end_date**: Backtest end date (YYYY-MM-DD)
    - **initial_capital**: Starting capital for simulation (default: 100000)
    - **commission**: Commission per trade as fraction (default: 0.001)
    - **slippage**: Slippage per trade as fraction (default: 0.0005)
    - **strategy_params**: Trading strategy configuration
    
    **Returns:**
    - BacktestResponse with metrics, trades, and equity curve
    """
    logger.info(
        f"Backtest request received: model_id={request.model_id}, "
        f"start_date={request.start_date}, end_date={request.end_date}"
    )
    
    try:
        # Get service
        service = get_backtest_service()
        
        # Run backtest
        results = service.run_backtest(
            model_id=request.model_id,
            start_date=request.get_start_date_as_date(),
            end_date=request.get_end_date_as_date(),
            initial_capital=request.initial_capital,
            commission=request.commission,
            slippage=request.slippage,
            strategy_params=request.strategy_params
        )
        
        # Convert results to Pydantic models
        metrics = BacktestMetrics(**results['metrics'])
        
        trades = [
            Trade(**trade_dict)
            for trade_dict in results['trades']
        ]
        
        # Build response
        response = BacktestResponse(
            model_id=results['model_id'],
            start_date=results['start_date'],
            end_date=results['end_date'],
            metrics=metrics,
            num_trades=results['num_trades'],
            trades=trades,
            equity_curve=results.get('equity_curve')
        )
        
        logger.info(
            f"Backtest completed successfully: {results['num_trades']} trades, "
            f"total_return={metrics.total_return*100:.2f}%"
        )
        
        return response
        
    except ValueError as e:
        # Validation errors
        logger.warning(f"Validation error in backtest request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error running backtest: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run backtest: {str(e)}"
        )

