"""
Model Benchmarking Utilities for Baseline Models.

Provides benchmarking and performance evaluation tools.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
import time
from datetime import datetime

from .model_comparison import ModelComparison
from .arima_model import ARIMAModel
from .exponential_smoothing import ExponentialSmoothingModel
from .prophet_model import ProphetModel

logger = logging.getLogger(__name__)


class ModelBenchmark:
    """
    Benchmark baseline models for performance and accuracy.
    
    Provides comprehensive benchmarking including:
    - Training time
    - Prediction time
    - Memory usage
    - Accuracy metrics
    - Model comparison
    
    Attributes:
        results: Dictionary of benchmark results
        comparison: ModelComparison instance
    
    Example:
        >>> benchmark = ModelBenchmark()
        >>> results = benchmark.run_benchmark(train_data, test_data)
        >>> benchmark.print_summary()
    """
    
    def __init__(self):
        """Initialize ModelBenchmark."""
        self.results: Dict[str, Dict] = {}
        self.comparison = ModelComparison()
        
        logger.info("ModelBenchmark initialized")
    
    def add_model(self, name: str, model: ARIMAModel | ExponentialSmoothingModel | ProphetModel):
        """
        Add a model to the benchmark.
        
        Args:
            name: Name identifier for the model
            model: Model instance
        """
        self.comparison.add_model(name, model)
        logger.info(f"Added model to benchmark: {name}")
    
    def run_benchmark(
        self,
        train_data: pd.Series | pd.DataFrame,
        test_data: pd.Series | pd.DataFrame,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """
        Run comprehensive benchmark on all models.
        
        Args:
            train_data: Training time series data
            test_data: Test time series data
            metrics: List of metrics to calculate
        
        Returns:
            Dictionary of benchmark results for each model
        
        Example:
            >>> results = benchmark.run_benchmark(train_data, test_data)
        """
        if metrics is None:
            metrics = ['MAE', 'RMSE', 'MAPE', 'R2']
        
        logger.info("="*80)
        logger.info("STARTING MODEL BENCHMARK")
        logger.info("="*80)
        
        results = {}
        
        for name, model in self.comparison.models.items():
            logger.info(f"\n{'='*80}")
            logger.info(f"BENCHMARKING: {name}")
            logger.info(f"{'='*80}")
            
            model_results = {
                'model_name': name,
                'model_type': type(model).__name__
            }
            
            try:
                # Training time
                logger.info("Measuring training time...")
                start_time = time.time()
                
                if isinstance(model, ProphetModel):
                    if isinstance(train_data, pd.Series):
                        if isinstance(train_data.index, pd.DatetimeIndex):
                            df = pd.DataFrame({
                                'ds': train_data.index,
                                'y': train_data.values
                            })
                            model.fit(df)
                        else:
                            raise ValueError("Prophet requires Series with DatetimeIndex")
                    else:
                        model.fit(train_data)
                else:
                    if isinstance(train_data, pd.DataFrame):
                        if len(train_data.columns) == 1:
                            train_data_series = train_data.iloc[:, 0]
                        else:
                            raise ValueError("DataFrame must have single column")
                    else:
                        train_data_series = train_data
                    model.fit(train_data_series)
                
                training_time = time.time() - start_time
                model_results['training_time_seconds'] = training_time
                logger.info(f"Training time: {training_time:.2f} seconds")
                
                # Prediction time
                logger.info("Measuring prediction time...")
                start_time = time.time()
                
                steps = len(test_data) if isinstance(test_data, pd.Series) else len(test_data)
                predictions = model.predict(steps=steps)
                
                prediction_time = time.time() - start_time
                model_results['prediction_time_seconds'] = prediction_time
                logger.info(f"Prediction time: {prediction_time:.2f} seconds")
                
                # Handle tuple return (forecast, conf_int)
                if isinstance(predictions, tuple):
                    predictions = predictions[0]
                
                # Handle DataFrame return (Prophet)
                if isinstance(predictions, pd.DataFrame):
                    if 'yhat' in predictions.columns:
                        predictions = predictions['yhat']
                    else:
                        predictions = predictions.iloc[:, 0]
                
                # Ensure predictions is Series
                if not isinstance(predictions, pd.Series):
                    predictions = pd.Series(predictions)
                
                # Convert test_data to Series if needed
                if isinstance(test_data, pd.DataFrame):
                    if len(test_data.columns) == 1:
                        test_data_series = test_data.iloc[:, 0]
                    else:
                        raise ValueError("DataFrame must have single column")
                else:
                    test_data_series = test_data
                
                # Align predictions with test data
                if len(predictions) != len(test_data_series):
                    predictions = predictions.iloc[:len(test_data_series)]
                
                # Calculate accuracy metrics
                logger.info("Calculating accuracy metrics...")
                accuracy_metrics = self._calculate_metrics(test_data_series, predictions, metrics)
                model_results.update(accuracy_metrics)
                
                # Model summary
                model_summary = model.get_model_summary()
                model_results['model_summary'] = model_summary
                
                # Memory usage (approximate)
                import sys
                model_size = sys.getsizeof(model) / 1024  # KB
                model_results['model_size_kb'] = model_size
                
                results[name] = model_results
                
                logger.info(f"{name} benchmark complete:")
                logger.info(f"  Training time: {training_time:.2f}s")
                logger.info(f"  Prediction time: {prediction_time:.2f}s")
                logger.info(f"  RMSE: {accuracy_metrics.get('RMSE', 'N/A'):.4f}")
                logger.info(f"  MAE: {accuracy_metrics.get('MAE', 'N/A'):.4f}")
            
            except Exception as e:
                logger.error(f"Error benchmarking {name}: {e}")
                results[name] = {
                    'model_name': name,
                    'error': str(e)
                }
        
        self.results = results
        
        logger.info("\n" + "="*80)
        logger.info("BENCHMARK COMPLETE")
        logger.info("="*80)
        
        return results
    
    def _calculate_metrics(
        self,
        actual: pd.Series,
        predicted: pd.Series,
        metrics: List[str]
    ) -> Dict[str, float]:
        """Calculate evaluation metrics."""
        results = {}
        
        # Remove NaN values for calculation
        mask = ~(actual.isna() | predicted.isna())
        actual_clean = actual[mask]
        predicted_clean = predicted[mask]
        
        if len(actual_clean) == 0:
            return {metric: np.nan for metric in metrics}
        
        for metric in metrics:
            if metric == 'MAE':
                results['MAE'] = np.mean(np.abs(actual_clean - predicted_clean))
            
            elif metric == 'RMSE':
                results['RMSE'] = np.sqrt(np.mean((actual_clean - predicted_clean) ** 2))
            
            elif metric == 'MAPE':
                # Avoid division by zero
                mask_nonzero = actual_clean != 0
                if mask_nonzero.sum() > 0:
                    results['MAPE'] = np.mean(
                        np.abs((actual_clean[mask_nonzero] - predicted_clean[mask_nonzero]) / actual_clean[mask_nonzero])
                    ) * 100
                else:
                    results['MAPE'] = np.nan
            
            elif metric == 'R2':
                ss_res = np.sum((actual_clean - predicted_clean) ** 2)
                ss_tot = np.sum((actual_clean - np.mean(actual_clean)) ** 2)
                if ss_tot > 0:
                    results['R2'] = 1 - (ss_res / ss_tot)
                else:
                    results['R2'] = np.nan
        
        return results
    
    def get_results_table(self) -> pd.DataFrame:
        """
        Get benchmark results as a DataFrame.
        
        Returns:
            DataFrame with model names as index and metrics as columns
        """
        if not self.results:
            return pd.DataFrame()
        
        # Extract key metrics
        table_data = {}
        for name, result in self.results.items():
            if 'error' in result:
                continue
            
            row = {
                'Model': name,
                'Training Time (s)': result.get('training_time_seconds', np.nan),
                'Prediction Time (s)': result.get('prediction_time_seconds', np.nan),
                'RMSE': result.get('RMSE', np.nan),
                'MAE': result.get('MAE', np.nan),
                'MAPE': result.get('MAPE', np.nan),
                'R2': result.get('R2', np.nan),
            }
            table_data[name] = row
        
        return pd.DataFrame(table_data).T
    
    def print_summary(self):
        """Print benchmark summary."""
        if not self.results:
            print("No benchmark results available.")
            return
        
        print("\n" + "="*80)
        print("MODEL BENCHMARK SUMMARY")
        print("="*80)
        
        table = self.get_results_table()
        if not table.empty:
            print("\nPerformance Metrics:")
            print(table.to_string())
        
        # Find best models
        print("\n" + "-"*80)
        print("Best Models:")
        print("-"*80)
        
        valid_results = {k: v for k, v in self.results.items() if 'error' not in v}
        
        if valid_results:
            # Best RMSE
            best_rmse = min(valid_results.items(), key=lambda x: x[1].get('RMSE', float('inf')))
            print(f"Best RMSE: {best_rmse[0]} ({best_rmse[1].get('RMSE', 'N/A'):.4f})")
            
            # Best MAE
            best_mae = min(valid_results.items(), key=lambda x: x[1].get('MAE', float('inf')))
            print(f"Best MAE: {best_mae[0]} ({best_mae[1].get('MAE', 'N/A'):.4f})")
            
            # Fastest training
            fastest_train = min(valid_results.items(), key=lambda x: x[1].get('training_time_seconds', float('inf')))
            print(f"Fastest Training: {fastest_train[0]} ({fastest_train[1].get('training_time_seconds', 'N/A'):.2f}s)")
            
            # Fastest prediction
            fastest_pred = min(valid_results.items(), key=lambda x: x[1].get('prediction_time_seconds', float('inf')))
            print(f"Fastest Prediction: {fastest_pred[0]} ({fastest_pred[1].get('prediction_time_seconds', 'N/A'):.2f}s)")
        
        print("\n" + "="*80)
    
    def get_best_model(self, metric: str = 'RMSE') -> Optional[str]:
        """
        Get the best model based on a specific metric.
        
        Args:
            metric: Metric to use for comparison ('RMSE', 'MAE', 'MAPE', 'R2')
        
        Returns:
            Name of best model, or None if no valid results
        """
        valid_results = {k: v for k, v in self.results.items() if 'error' not in v and metric in v}
        
        if not valid_results:
            return None
        
        if metric in ['RMSE', 'MAE', 'MAPE']:
            # Lower is better
            best = min(valid_results.items(), key=lambda x: x[1].get(metric, float('inf')))
        else:  # R2
            # Higher is better
            best = max(valid_results.items(), key=lambda x: x[1].get(metric, float('-inf')))
        
        return best[0]

