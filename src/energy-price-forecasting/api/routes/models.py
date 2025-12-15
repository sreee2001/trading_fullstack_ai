"""
Model information endpoint routes.

This module implements the /api/v1/models endpoint for retrieving
model metadata from the MLflow registry.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from api.models.models import ModelsListResponse, ModelInfo, ModelMetrics
from api.services.model_info_service import get_model_info_service
from api.logging_config import get_logger
from api.cache.response_cache import get_response_cache

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Models"])


@router.get(
    "/models",
    response_model=ModelsListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Available ML Models",
    description="""
    Retrieve metadata for all available ML models from the model registry.
    
    **Features:**
    - Lists all registered models
    - Optional commodity filtering
    - Includes performance metrics
    - Model version and stage information
    - Cached for 10 minutes
    
    **Query Parameters:**
    - `commodity`: Optional commodity filter (WTI, BRENT, NG)
    
    **Example:**
    ```
    GET /api/v1/models?commodity=WTI
    ```
    """,
    responses={
        200: {"description": "Model list retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
async def get_models(
    commodity: Optional[str] = Query(
        default=None,
        pattern="^(WTI|BRENT|NG)$",
        description="Filter by commodity symbol (WTI, BRENT, NG)"
    )
) -> ModelsListResponse:
    """
    Get list of all registered models.
    
    Args:
        commodity: Optional commodity symbol to filter by (WTI, BRENT, NG)
        
    Returns:
        ModelsListResponse with list of model information
        
    Raises:
        HTTPException: If model retrieval fails
    """
    logger.info(f"Models list request (commodity_filter: {commodity})")
    
    try:
        # Check cache (10 min TTL)
        cache = get_response_cache(default_ttl=600)
        cache_key_params = {"commodity": commodity} if commodity else {}
        
        cached_response = cache.get("/api/v1/models", query_params=cache_key_params)
        if cached_response:
            logger.info("Returning cached model info")
            return ModelsListResponse(**cached_response)
        
        # Get service
        service = get_model_info_service()
        
        # Retrieve models
        model_dicts = service.get_all_models(commodity_filter=commodity)
        
        # Convert dicts to Pydantic ModelInfo models
        models = []
        for model_dict in model_dicts:
            # Convert metrics dict to ModelMetrics if present
            metrics = None
            if model_dict.get('metrics'):
                metrics = ModelMetrics(**model_dict['metrics'])
            
            model_info = ModelInfo(
                model_id=model_dict['model_id'],
                model_name=model_dict['model_name'],
                commodity=model_dict['commodity'],
                model_type=model_dict['model_type'],
                version=model_dict['version'],
                stage=model_dict['stage'],
                training_date=model_dict.get('training_date'),
                created_at=model_dict.get('created_at'),
                metrics=metrics,
                run_id=model_dict.get('run_id'),
                experiment_id=model_dict.get('experiment_id'),
                tags=model_dict.get('tags'),
                description=model_dict.get('description'),
            )
            models.append(model_info)
        
        # Build response
        response = ModelsListResponse(
            models=models,
            total_count=len(models),
            commodity_filter=commodity
        )
        
        # Cache the response
        cache.set(
            "/api/v1/models",
            response.model_dump(),
            ttl=600,  # 10 minutes
            query_params=cache_key_params
        )
        
        logger.info(f"Retrieved {len(models)} models")
        
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving models: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve models: {str(e)}"
        )

