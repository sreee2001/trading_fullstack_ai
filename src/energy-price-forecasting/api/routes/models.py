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

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Models"])


@router.get("/models", response_model=ModelsListResponse, status_code=status.HTTP_200_OK)
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
        
        logger.info(f"Retrieved {len(models)} models")
        
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving models: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve models: {str(e)}"
        )

