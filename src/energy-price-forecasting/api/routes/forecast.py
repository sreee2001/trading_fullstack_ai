"""
Forecast endpoint routes.

This module implements the /api/v1/forecast endpoint for generating
energy price forecasts.
"""

from datetime import date, datetime, timedelta
from typing import List
import pandas as pd
import numpy as np

from fastapi import APIRouter, HTTPException, status
from api.models.forecast import ForecastRequest, ForecastResponse, Prediction
from api.services.model_service import get_model_service
from api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Forecast"])


@router.post("/forecast", response_model=ForecastResponse, status_code=status.HTTP_200_OK)
async def forecast(request: ForecastRequest) -> ForecastResponse:
    """
    Generate price forecast for a commodity.
    
    Args:
        request: Forecast request with commodity, horizon, and start_date
        
    Returns:
        ForecastResponse with predictions
        
    Raises:
        HTTPException: If model not found or forecast generation fails
    """
    logger.info(
        f"Forecast request received: commodity={request.commodity}, "
        f"horizon={request.horizon}, start_date={request.start_date}"
    )
    
    try:
        # Get model service
        model_service = get_model_service()
        
        # Load model (default to LSTM for now)
        # In Story 4.2.3, this will support model selection
        model_type = "lstm"  # Default model type
        model = model_service.load_model(
            commodity=request.commodity,
            model_type=model_type
        )
        
        if model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model not found for commodity {request.commodity}"
            )
        
        # Check if model is fitted
        if not hasattr(model, 'is_fitted') or not model.is_fitted:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Model for {request.commodity} is not fitted"
            )
        
        # Generate forecast
        logger.info(f"Generating forecast for {request.horizon} days...")
        
        # Get predictions with confidence intervals
        try:
            if hasattr(model, 'predict'):
                # Try to get confidence intervals
                try:
                    forecast_result = model.predict(
                        steps=request.horizon,
                        return_conf_int=True
                    )
                    
                    if isinstance(forecast_result, tuple):
                        forecasts, conf_int = forecast_result
                    else:
                        forecasts = forecast_result
                        conf_int = None
                except TypeError:
                    # Model doesn't support return_conf_int
                    forecasts = model.predict(steps=request.horizon)
                    conf_int = None
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Model does not have predict method"
                )
        except Exception as e:
            logger.error(f"Error generating forecast: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate forecast: {str(e)}"
            )
        
        # Convert forecasts to list if pandas Series
        if isinstance(forecasts, pd.Series):
            forecast_values = forecasts.tolist()
        elif isinstance(forecasts, np.ndarray):
            forecast_values = forecasts.tolist()
        elif isinstance(forecasts, (list, tuple)):
            forecast_values = list(forecasts)
        else:
            forecast_values = [float(forecasts)]
        
        # Ensure we have the right number of predictions
        if len(forecast_values) != request.horizon:
            logger.warning(
                f"Model returned {len(forecast_values)} predictions, "
                f"expected {request.horizon}. Truncating or padding."
            )
            if len(forecast_values) > request.horizon:
                forecast_values = forecast_values[:request.horizon]
            else:
                # Pad with last value
                last_value = forecast_values[-1] if forecast_values else 0.0
                forecast_values.extend([last_value] * (request.horizon - len(forecast_values)))
        
        # Generate dates for predictions
        start_date_obj = request.get_start_date_as_date()
        prediction_dates = [
            (start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(request.horizon)
        ]
        
        # Build predictions list
        predictions: List[Prediction] = []
        
        for i, (pred_date, pred_price) in enumerate(zip(prediction_dates, forecast_values)):
            # Get confidence intervals if available
            if conf_int is not None:
                if isinstance(conf_int, pd.DataFrame):
                    conf_lower = float(conf_int.iloc[i, 0]) if len(conf_int.columns) > 0 else pred_price * 0.95
                    conf_upper = float(conf_int.iloc[i, 1]) if len(conf_int.columns) > 1 else pred_price * 1.05
                elif isinstance(conf_int, (list, tuple, np.ndarray)):
                    # Handle array-like confidence intervals
                    if len(conf_int) > i:
                        if isinstance(conf_int[i], (list, tuple, np.ndarray)) and len(conf_int[i]) >= 2:
                            conf_lower = float(conf_int[i][0])
                            conf_upper = float(conf_int[i][1])
                        else:
                            conf_lower = pred_price * 0.95
                            conf_upper = pred_price * 1.05
                    else:
                        conf_lower = pred_price * 0.95
                        conf_upper = pred_price * 1.05
                else:
                    conf_lower = pred_price * 0.95
                    conf_upper = pred_price * 1.05
            else:
                # Default confidence intervals (10% range)
                conf_lower = pred_price * 0.95
                conf_upper = pred_price * 1.05
            
            predictions.append(
                Prediction(
                    date=pred_date,
                    price=float(pred_price),
                    confidence_lower=float(conf_lower),
                    confidence_upper=float(conf_upper)
                )
            )
        
        # Build response
        response = ForecastResponse(
            commodity=request.commodity,
            forecast_date=datetime.now().strftime("%Y-%m-%d"),
            horizon=request.horizon,
            predictions=predictions,
            model_name=model_type.upper(),
            model_version="1.0.0"  # Placeholder - will come from model registry
        )
        
        logger.info(
            f"Forecast generated successfully: {len(predictions)} predictions "
            f"for {request.commodity}"
        )
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in forecast endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

