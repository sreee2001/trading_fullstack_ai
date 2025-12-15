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


@router.post("/backtest", response_model=BacktestResponse, status_code=status.HTTP_200_OK)
async def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """
    Run a backtest for a model.
    
    Args:
        request: Backtest request with model_id, date range, and parameters
        
    Returns:
        BacktestResponse with backtest results
        
    Raises:
        HTTPException: If validation fails or backtest fails
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

