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
from api.services.historical_data_service import get_historical_data_service
from database.operations import get_price_data
from api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Forecast"])


@router.post(
    "/forecast",
    response_model=ForecastResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Energy Commodity Price Forecast",
    description="""
    Generate price forecasts for energy commodities (WTI, BRENT, Natural Gas).
    
    **Features:**
    - Supports multiple commodities: WTI, BRENT, NG
    - Forecast horizon: 1-30 days
    - Returns predictions with confidence intervals
    - Uses trained ML models (LSTM, ARIMA, Prophet)
    
    **Example Request:**
    ```json
    {
        "commodity": "WTI",
        "horizon": 7,
        "start_date": "2025-01-01"
    }
    ```
    
    **Response includes:**
    - List of predictions with dates and prices
    - Confidence intervals (lower/upper bounds)
    - Model information
    """,
    responses={
        200: {
            "description": "Forecast generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "commodity": "WTI",
                        "forecast_date": "2025-01-01",
                        "horizon": 7,
                        "predictions": [
                            {
                                "date": "2025-01-01",
                                "price": 75.50,
                                "confidence_lower": 71.73,
                                "confidence_upper": 79.28
                            }
                        ]
                    }
                }
            }
        },
        404: {"description": "Model not found for commodity"},
        503: {"description": "Model not fitted"},
        500: {"description": "Internal server error"}
    }
)
async def forecast(request: ForecastRequest) -> ForecastResponse:
    """
    Generate price forecast for an energy commodity.
    
    **Parameters:**
    - **commodity**: Commodity symbol (WTI, BRENT, or NG)
    - **horizon**: Number of days to forecast (1-30)
    - **start_date**: Start date for the forecast (YYYY-MM-DD)
    
    **Returns:**
    - ForecastResponse with predictions and confidence intervals
    
    **Example:**
    ```python
    {
        "commodity": "WTI",
        "horizon": 7,
        "start_date": "2025-01-01"
    }
    ```
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
        
        # Determine if model needs historical data (LSTM models require data input)
        # Check model type and also inspect predict method signature
        model_needs_data = False
        if model_type.lower() == "lstm":
            model_needs_data = True
        elif hasattr(model, 'predict'):
            # Check if predict method requires 'data' parameter
            try:
                import inspect
                sig = inspect.signature(model.predict)
                params = list(sig.parameters.keys())
                # If 'data' is in the first few parameters, model needs data
                if 'data' in params[:3]:
                    model_needs_data = True
            except Exception:
                # If inspection fails, default to False (ARIMA/Prophet style)
                pass
        
        # For LSTM models, fetch historical data to use as input
        historical_data_df = None
        if model_needs_data:
            try:
                logger.info(f"Fetching historical data for {model_type} model...")
                # Get data from the past 60 days (LSTM typically needs sequence_length days)
                # We'll get more than needed to ensure we have enough
                start_date_for_data = request.get_start_date_as_date() - timedelta(days=90)
                start_datetime = datetime.combine(start_date_for_data, datetime.min.time())
                end_datetime = datetime.combine(request.get_start_date_as_date(), datetime.max.time())
                
                # Fetch historical data as DataFrame
                historical_data_df = get_price_data(
                    commodity_symbol=request.commodity,
                    source_name="EIA",  # Default to EIA, could be made configurable
                    start_date=start_datetime,
                    end_date=end_datetime,
                    limit=None
                )
                
                if historical_data_df is None or historical_data_df.empty:
                    logger.warning(f"No historical data found for {request.commodity}. Using model without data.")
                    model_needs_data = False
                else:
                    # Ensure we have a 'price' column
                    if 'price' not in historical_data_df.columns:
                        logger.error(f"Historical data missing 'price' column. Columns: {historical_data_df.columns.tolist()}")
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Historical data format error: missing 'price' column"
                        )
                    logger.info(f"Retrieved {len(historical_data_df)} historical data points for forecasting")
            except Exception as e:
                logger.warning(f"Failed to fetch historical data: {e}. Attempting forecast without data.")
                model_needs_data = False
        
        # Get predictions with confidence intervals
        try:
            if hasattr(model, 'predict'):
                conf_int = None
                
                if model_needs_data and historical_data_df is not None:
                    # LSTM models need data input and don't support return_conf_int
                    logger.info(f"Calling {model_type} model.predict() with historical data...")
                    try:
                        # Try calling with data parameter (for real LSTM models)
                        forecasts = model.predict(data=historical_data_df, steps=request.horizon)
                    except TypeError as e:
                        # Model doesn't accept 'data' parameter (e.g., placeholder model)
                        # Fall back to calling without data
                        logger.warning(
                            f"Model doesn't accept 'data' parameter ({e}). "
                            f"Calling predict() with steps only."
                        )
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
                        except (TypeError, ValueError) as e2:
                            # Model doesn't support return_conf_int either
                            logger.debug(f"Model doesn't support return_conf_int: {e2}. Using without it.")
                            forecasts = model.predict(steps=request.horizon)
                            conf_int = None
                else:
                    # ARIMA/Prophet models can predict with just steps
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
                    except (TypeError, ValueError) as e:
                        # Model doesn't support return_conf_int
                        logger.debug(f"Model doesn't support return_conf_int: {e}. Using without it.")
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
        
        # Convert forecasts to list, handling different output formats
        if isinstance(forecasts, pd.Series):
            forecast_values = forecasts.tolist()
        elif isinstance(forecasts, np.ndarray):
            # Handle 2D arrays (LSTM might return shape like (1, horizon) or (n_samples, horizon))
            if forecasts.ndim == 2:
                # If 2D, take the first row (or last row if it has multiple rows)
                if forecasts.shape[0] > 1:
                    # Multiple samples - take the last one (most recent prediction)
                    forecast_values = forecasts[-1].tolist()
                else:
                    # Single row
                    forecast_values = forecasts[0].tolist()
            else:
                # 1D array
                forecast_values = forecasts.tolist()
        elif isinstance(forecasts, (list, tuple)):
            forecast_values = list(forecasts)
        else:
            # Single value
            forecast_values = [float(forecasts)]
        
        logger.info(f"Extracted {len(forecast_values)} forecast values from model output")
        
        # Log the first few values to help debug
        if len(forecast_values) > 0:
            sample_values = forecast_values[:min(5, len(forecast_values))]
            logger.info(f"Sample forecast values: {sample_values}")
        
        # Check if all values are the same (potential issue)
        if len(forecast_values) > 1:
            unique_values = len(set(forecast_values))
            if unique_values == 1:
                logger.warning(
                    f"WARNING: All {len(forecast_values)} forecast values are identical: {forecast_values[0]}. "
                    f"This may indicate a model issue."
                )
        
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
                logger.warning(
                    f"Padded forecast with last value {last_value}. "
                    f"Final forecast_values length: {len(forecast_values)}"
                )
        
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

