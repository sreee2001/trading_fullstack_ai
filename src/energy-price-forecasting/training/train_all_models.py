"""
Automated Model Training Script.

This script trains all models for all commodities in a scheduled manner.
Can be run manually or via CI/CD pipeline.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mlflow_tracking.experiment_tracker import ExperimentTracker
from mlflow_tracking.model_registry import ModelRegistry
from database.utils import get_database_manager
from api.logging_config import setup_api_logging

# Import model training functions
# Note: Adjust imports based on actual training module structure
try:
    from models.arima_model import ARIMAModel
    from models.prophet_model import ProphetModel
    from models.lstm_model import LSTMModel
except ImportError:
    # Fallback if direct imports don't work
    ARIMAModel = None
    ProphetModel = None
    LSTMModel = None

# Setup logging
setup_api_logging()
logger = logging.getLogger(__name__)

# Commodities and model types to train
COMMODITIES = ['WTI', 'BRENT', 'NG']
MODEL_TYPES = ['arima', 'prophet', 'lstm']


def train_all_models(
    commodities: Optional[List[str]] = None,
    model_types: Optional[List[str]] = None,
    horizon: int = 7,
    retrain: bool = False,
    experiment_name: Optional[str] = None
) -> dict:
    """
    Train all models for specified commodities and model types.
    
    Args:
        commodities: List of commodities to train (default: all)
        model_types: List of model types to train (default: all)
        horizon: Forecast horizon in days (default: 7)
        retrain: Whether to retrain existing models (default: False)
        experiment_name: MLflow experiment name (default: auto-generated)
        
    Returns:
        Dictionary with training results
    """
    if commodities is None:
        commodities = COMMODITIES
    if model_types is None:
        model_types = MODEL_TYPES
    
    if experiment_name is None:
        experiment_name = f"automated_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    logger.info(f"Starting automated model training")
    logger.info(f"Commodities: {commodities}")
    logger.info(f"Model types: {model_types}")
    logger.info(f"Horizon: {horizon} days")
    logger.info(f"Experiment: {experiment_name}")
    
    # Initialize MLflow tracker
    tracker = ExperimentTracker(experiment_name=experiment_name)
    
    # Initialize model registry
    registry = ModelRegistry()
    
    # Initialize model service (for checking existing models)
    model_service = get_model_service()
    
    results = {
        'experiment_name': experiment_name,
        'start_time': datetime.now().isoformat(),
        'commodities': commodities,
        'model_types': model_types,
        'horizon': horizon,
        'models_trained': [],
        'models_failed': [],
        'total_models': len(commodities) * len(model_types),
        'success_count': 0,
        'failure_count': 0
    }
    
    # Train each combination
    for commodity in commodities:
        for model_type in model_types:
            model_id = f"{commodity}_{model_type.upper()}"
            logger.info(f"Training {model_id}...")
            
            try:
                # Check if model already exists
                if not retrain:
                    existing_model = trainer.load_model(commodity, model_type)
                    if existing_model is not None:
                        logger.info(f"Model {model_id} already exists, skipping (use --retrain to force)")
                        results['models_trained'].append({
                            'model_id': model_id,
                            'status': 'skipped',
                            'reason': 'already_exists'
                        })
                        continue
                
                # Train model
                model, metrics = trainer.train_model(
                    commodity=commodity,
                    model_type=model_type,
                    horizon=horizon,
                    experiment_name=experiment_name
                )
                
                if model is not None:
                    logger.info(f"Successfully trained {model_id}")
                    logger.info(f"Metrics: {metrics}")
                    
                    results['models_trained'].append({
                        'model_id': model_id,
                        'status': 'success',
                        'metrics': metrics
                    })
                    results['success_count'] += 1
                else:
                    raise Exception("Training returned None")
                    
            except Exception as e:
                logger.error(f"Failed to train {model_id}: {e}", exc_info=True)
                # End MLflow run if it's still active
                try:
                    if tracker.active_run:
                        tracker.end_run()
                except:
                    pass
                results['models_failed'].append({
                    'model_id': model_id,
                    'status': 'failed',
                    'error': str(e)
                })
                results['failure_count'] += 1
    
    results['end_time'] = datetime.now().isoformat()
    results['success_rate'] = results['success_count'] / results['total_models'] if results['total_models'] > 0 else 0
    
    logger.info(f"Training completed: {results['success_count']}/{results['total_models']} successful")
    logger.info(f"Success rate: {results['success_rate']:.2%}")
    
    return results


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(description='Train all models for energy price forecasting')
    
    parser.add_argument(
        '--commodities',
        nargs='+',
        choices=COMMODITIES,
        default=COMMODITIES,
        help='Commodities to train (default: all)'
    )
    
    parser.add_argument(
        '--model-types',
        nargs='+',
        choices=MODEL_TYPES,
        default=MODEL_TYPES,
        help='Model types to train (default: all)'
    )
    
    parser.add_argument(
        '--horizon',
        type=int,
        default=7,
        help='Forecast horizon in days (default: 7)'
    )
    
    parser.add_argument(
        '--retrain',
        action='store_true',
        help='Retrain existing models'
    )
    
    parser.add_argument(
        '--experiment-name',
        type=str,
        default=None,
        help='MLflow experiment name (default: auto-generated)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file for results JSON (optional)'
    )
    
    args = parser.parse_args()
    
    try:
        # Verify database connection
        db_manager = get_database_manager()
        if db_manager:
            db_manager.verify_connection()
            logger.info("Database connection verified")
        else:
            logger.warning("Database manager not configured, continuing without database")
        
        # Train models
        results = train_all_models(
            commodities=args.commodities,
            model_types=args.model_types,
            horizon=args.horizon,
            retrain=args.retrain,
            experiment_name=args.experiment_name
        )
        
        # Output results
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {args.output}")
        else:
            import json
            print(json.dumps(results, indent=2))
        
        # Exit with appropriate code
        sys.exit(0 if results['failure_count'] == 0 else 1)
        
    except Exception as e:
        logger.error(f"Training script failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

