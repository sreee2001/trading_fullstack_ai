"""
Historical data endpoint routes.

This module implements the /api/v1/historical endpoint for retrieving
historical energy price data.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from api.models.historical import HistoricalDataRequest, HistoricalDataResponse, PricePoint
from api.services.historical_data_service import get_historical_data_service
from api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Historical Data"])


@router.get("/historical", response_model=HistoricalDataResponse, status_code=status.HTTP_200_OK)
async def get_historical_data(
    commodity: str = Query(..., description="Commodity symbol (WTI, BRENT, NG)"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    limit: int = Query(default=1000, ge=1, le=10000, description="Maximum number of records (1-10000)"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    source: Optional[str] = Query(default=None, description="Data source name (optional, defaults to all sources)")
) -> HistoricalDataResponse:
    """
    Get historical price data for a commodity.
    
    Args:
        commodity: Commodity symbol (WTI, BRENT, NG)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Maximum number of records to return (default: 1000, max: 10000)
        offset: Number of records to skip for pagination (default: 0)
        source: Optional data source name (if not specified, aggregates across all sources)
        
    Returns:
        HistoricalDataResponse with price data and pagination info
        
    Raises:
        HTTPException: If validation fails or data retrieval fails
    """
    logger.info(
        f"Historical data request: commodity={commodity}, "
        f"start_date={start_date}, end_date={end_date}, "
        f"limit={limit}, offset={offset}, source={source}"
    )
    
    try:
        # Validate request using Pydantic model
        request = HistoricalDataRequest(
            commodity=commodity,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        # Get service
        service = get_historical_data_service()
        
        # Retrieve data
        price_points_dicts, total_count = service.get_historical_data(
            commodity=request.commodity,
            start_date=request.get_start_date_as_date(),
            end_date=request.get_end_date_as_date(),
            limit=request.limit,
            offset=request.offset,
            source=source
        )
        
        # Convert dicts to Pydantic PricePoint models
        price_points = [
            PricePoint(**point_dict)
            for point_dict in price_points_dicts
        ]
        
        # Determine if there are more records
        has_more = (offset + len(price_points)) < total_count
        
        # Build response
        response = HistoricalDataResponse(
            commodity=request.commodity,
            start_date=request.start_date,
            end_date=request.end_date,
            data=price_points,
            total_count=total_count,
            limit=request.limit,
            offset=request.offset,
            has_more=has_more
        )
        
        logger.info(
            f"Historical data retrieved successfully: {len(price_points)} records "
            f"(total: {total_count})"
        )
        
        return response
        
    except ValueError as e:
        # Validation errors from Pydantic
        logger.warning(f"Validation error in historical data request: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid request parameters: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error retrieving historical data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve historical data: {str(e)}"
        )

