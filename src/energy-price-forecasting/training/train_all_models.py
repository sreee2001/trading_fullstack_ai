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
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mlflow_tracking.experiment_tracker import ExperimentTracker
from mlflow_tracking.model_registry import ModelRegistry
from database.utils import get_database_manager
from database.operations import get_price_data
from api.logging_config import setup_api_logging
from api.services.model_service import get_model_service
from models.baseline.arima_model import ARIMAModel
from models.baseline.prophet_model import ProphetModel
from models.lstm.lstm_model import LSTMForecaster

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
                    existing_model = model_service.load_model(commodity, model_type)
                    if existing_model is not None:
                        # Check if it's a real model (not placeholder)
                        if hasattr(existing_model, 'is_fitted') and existing_model.is_fitted:
                            # Additional check: not a placeholder
                            if not (hasattr(existing_model, 'commodity') and existing_model.commodity == commodity and hasattr(existing_model, 'model_type')):
                                logger.info(f"Model {model_id} already exists, skipping (use --retrain to force)")
                                results['models_trained'].append({
                                    'model_id': model_id,
                                    'status': 'skipped',
                                    'reason': 'already_exists'
                                })
                                continue
                
                # Start MLflow run
                run_name = f"{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                tracker.start_run(run_name=run_name, tags={
                    'commodity': commodity,
                    'model_type': model_type,
                    'horizon': str(horizon),
                    'automated': 'true'
                })
                
                # Get training data
                logger.info(f"Fetching training data for {commodity}...")
                db_manager = get_database_manager()
                if not db_manager:
                    raise Exception("Database manager not available")
                
                # Get historical data (last 2 years for training)
                end_date = datetime.now().date()
                start_date = pd.Timestamp(end_date) - pd.Timedelta(days=730)
                price_data, _ = get_price_data(
                    commodity=commodity,
                    start_date=start_date,
                    end_date=end_date,
                    limit=10000
                )
                
                if price_data is None or len(price_data) < 100:
                    raise Exception(f"Insufficient data for training: {len(price_data) if price_data is not None else 0} records")
                
                # Prepare data
                if isinstance(price_data, pd.DataFrame):
                    if 'price' in price_data.columns:
                        train_series = price_data['price']
                    elif len(price_data.columns) == 1:
                        train_series = price_data.iloc[:, 0]
                    else:
                        raise ValueError("Cannot determine price column")
                else:
                    train_series = price_data
                
                # Create and train model
                logger.info(f"Creating {model_type} model...")
                if model_type == 'arima':
                    model = ARIMAModel()
                    model.fit(train_series)
                elif model_type == 'prophet':
                    model = ProphetModel()
                    # Prophet needs DataFrame with 'ds' and 'y' columns
                    if isinstance(train_series, pd.Series):
                        df = pd.DataFrame({
                            'ds': train_series.index if isinstance(train_series.index, pd.DatetimeIndex) else pd.date_range(start='2020-01-01', periods=len(train_series), freq='D'),
                            'y': train_series.values
                        })
                    else:
                        df = train_series
                    model.fit(df)
                elif model_type == 'lstm':
                    model = LSTMForecaster(forecast_horizon=horizon)
                    # LSTM needs DataFrame
                    if isinstance(train_series, pd.Series):
                        df = pd.DataFrame({'price': train_series.values}, index=train_series.index)
                    else:
                        df = train_series
                    model.fit(df, target_column='price', epochs=50, batch_size=32)
                else:
                    raise ValueError(f"Unknown model type: {model_type}")
                
                # Calculate metrics (simplified - in production would use evaluation module)
                metrics = {}
                if hasattr(model, 'metrics'):
                    metrics = model.metrics
                else:
                    # Basic metrics placeholder
                    metrics = {
                        'model_type': model_type,
                        'commodity': commodity,
                        'horizon': horizon
                    }
                
                logger.info(f"Successfully trained {model_id}")
                logger.info(f"Metrics: {metrics}")
                
                # Log parameters and metrics to MLflow
                tracker.log_params({
                    'commodity': commodity,
                    'model_type': model_type,
                    'horizon': str(horizon),
                    'training_samples': len(train_series)
                })
                tracker.log_metrics(metrics)
                
                # Log model to MLflow
                run_id = tracker.run_id
                try:
                    # Try to log model (may not work for all model types)
                    tracker.log_model(model, artifact_path="model", registered_model_name=f"{commodity}_{model_type}")
                    logger.info(f"Logged model to MLflow run {run_id}")
                except Exception as e:
                    logger.warning(f"Failed to log model to MLflow: {e}. Model trained but not logged.")
                    # Continue even if logging fails
                
                # End MLflow run
                tracker.end_run()
                
                results['models_trained'].append({
                    'model_id': model_id,
                    'status': 'success',
                    'metrics': metrics,
                    'run_id': run_id
                })
                results['success_count'] += 1
                    
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
