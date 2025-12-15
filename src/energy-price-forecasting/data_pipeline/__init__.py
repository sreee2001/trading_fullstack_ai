"""
Data Pipeline Orchestrator for Energy Price Forecasting System.

This module provides automated orchestration of the data ingestion pipeline,
coordinating data fetching, validation, and storage from multiple sources.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

from data_ingestion.eia_client import EIAAPIClient
from data_ingestion.fred_client import FREDAPIClient
from data_ingestion.yahoo_finance_client import YahooFinanceClient
from data_validation import DataValidator
from database.operations import (
    insert_price_data,
    get_latest_price_date,
    get_or_create_commodity,
    get_or_create_data_source
)
from database.utils import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PipelineExecutionResult:
    """Container for pipeline execution results."""
    
    def __init__(self):
        self.status = "PENDING"  # PENDING, SUCCESS, PARTIAL_SUCCESS, FAILED
        self.start_time = datetime.now()
        self.end_time = None
        self.duration_seconds = 0
        self.records_fetched = {}  # {source: count}
        self.records_stored = {}   # {source: count}
        self.quality_scores = {}   # {source: score}
        self.errors = []
        self.warnings = []
        self.summary = ""
    
    def complete(self):
        """Mark pipeline as complete and calculate duration."""
        self.end_time = datetime.now()
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        
        # Determine overall status
        if not self.errors:
            self.status = "SUCCESS"
        elif self.records_stored:
            self.status = "PARTIAL_SUCCESS"
        else:
            self.status = "FAILED"
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary."""
        return {
            'status': self.status,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'records_fetched': self.records_fetched,
            'records_stored': self.records_stored,
            'quality_scores': self.quality_scores,
            'errors': self.errors,
            'warnings': self.warnings,
            'summary': self.summary
        }


class DataPipelineOrchestrator:
    """
    Orchestrates the automated data pipeline for energy price data.
    
    Coordinates:
    - Data fetching from multiple sources (EIA, FRED, Yahoo Finance)
    - Data validation and quality checks
    - Data storage to TimescaleDB
    - Error handling and reporting
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the pipeline orchestrator.
        
        Args:
            config_path: Path to pipeline configuration YAML file
        """
        self.config = self._load_config(config_path)
        self.validator = DataValidator()
        self.db_manager = DatabaseManager()
        
        # Initialize API clients if enabled
        self.eia_client = None
        self.fred_client = None
        self.yahoo_client = None
        
        if self.config['data_sources']['eia']['enabled']:
            try:
                self.eia_client = EIAAPIClient()
                logger.info("EIA client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize EIA client: {e}")
        
        if self.config['data_sources']['fred']['enabled']:
            try:
                self.fred_client = FREDAPIClient()
                logger.info("FRED client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize FRED client: {e}")
        
        if self.config['data_sources']['yahoo_finance']['enabled']:
            try:
                self.yahoo_client = YahooFinanceClient()
                logger.info("Yahoo Finance client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Yahoo Finance client: {e}")
        
        logger.info("DataPipelineOrchestrator initialized successfully")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load pipeline configuration."""
        if config_path is None:
            config_path = Path(__file__).parent / "pipeline_config.yaml"
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded pipeline config from {config_path}")
            return config
        except Exception as e:
            logger.warning(f"Failed to load config: {e}. Using defaults.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default pipeline configuration."""
        return {
            'pipeline': {
                'name': 'Energy Price Data Pipeline',
                'version': '1.0'
            },
            'data_sources': {
                'eia': {
                    'enabled': True,
                    'commodities': ['WTI_CRUDE', 'NATURAL_GAS']
                },
                'fred': {
                    'enabled': True,
                    'series': ['DCOILWTICO', 'DCOILBRENTEU']
                },
                'yahoo_finance': {
                    'enabled': True,
                    'tickers': ['CL=F', 'BZ=F']
                }
            },
            'date_range': {
                'mode': 'incremental',
                'lookback_days': 30
            },
            'validation': {
                'quality_threshold': 70,
                'exclude_weekends': True
            },
            'storage': {
                'batch_size': 1000,
                'upsert': True
            },
            'error_handling': {
                'retry_attempts': 3,
                'continue_on_partial_failure': True
            }
        }
    
    def run_pipeline(
        self,
        commodities: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        mode: str = 'incremental'
    ) -> PipelineExecutionResult:
        """
        Run the complete data pipeline.
        
        Args:
            commodities: List of commodities to fetch (or None for all)
            sources: List of sources to use (or None for all enabled)
            start_date: Start date (YYYY-MM-DD) or None for auto-calculate
            end_date: End date (YYYY-MM-DD) or None for today
            mode: Pipeline mode ('incremental', 'full_refresh', 'backfill')
        
        Returns:
            PipelineExecutionResult with execution details
        """
        result = PipelineExecutionResult()
        logger.info(f"Starting pipeline execution (mode: {mode})")
        
        try:
            # Step 1: Determine date range
            start_date, end_date = self._calculate_date_range(start_date, end_date, mode)
            logger.info(f"Date range: {start_date} to {end_date}")
            
            # Step 2: Fetch data from all sources (parallel)
            fetch_results = self._fetch_all_sources(
                commodities=commodities,
                sources=sources,
                start_date=start_date,
                end_date=end_date
            )
            
            # Track fetched records
            for source_name, data in fetch_results.items():
                if data is not None:
                    result.records_fetched[source_name] = len(data)
            
            # Step 3: Validate data
            validation_results = self._validate_all_data(fetch_results)
            
            # Track quality scores
            for source_name, val_result in validation_results.items():
                if val_result and 'quality_score' in val_result:
                    result.quality_scores[source_name] = val_result['quality_score']
            
            # Step 4: Store valid data
            storage_results = self._store_all_data(fetch_results, validation_results)
            
            # Track stored records
            for source_name, count in storage_results.items():
                result.records_stored[source_name] = count
            
            # Collect warnings
            for source_name, val_result in validation_results.items():
                if val_result and val_result.get('quality_score', 100) < 70:
                    result.warnings.append(
                        f"{source_name}: Low quality score ({val_result['quality_score']}%)"
                    )
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            result.errors.append(f"Pipeline exception: {str(e)}")
        
        # Mark pipeline complete
        result.complete()
        
        # Generate summary
        result.summary = self._generate_summary(result)
        logger.info(f"Pipeline completed with status: {result.status}")
        logger.info(result.summary)
        
        return result
    
    def _calculate_date_range(
        self,
        start_date: Optional[str],
        end_date: Optional[str],
        mode: str
    ) -> Tuple[str, str]:
        """Calculate date range for data fetching."""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        if start_date is None:
            if mode == 'incremental':
                # Fetch from last stored date
                try:
                    last_date = get_latest_price_date()
                    if last_date:
                        # Start from day after last stored date
                        start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
                    else:
                        # No data yet, use lookback days
                        lookback = self.config['date_range']['lookback_days']
                        start_date = (datetime.now() - timedelta(days=lookback)).strftime('%Y-%m-%d')
                except Exception as e:
                    logger.warning(f"Failed to get last stored date: {e}. Using lookback.")
                    lookback = self.config['date_range']['lookback_days']
                    start_date = (datetime.now() - timedelta(days=lookback)).strftime('%Y-%m-%d')
            else:
                # Use configured lookback
                lookback = self.config['date_range'].get('lookback_days', 30)
                start_date = (datetime.now() - timedelta(days=lookback)).strftime('%Y-%m-%d')
        
        return start_date, end_date
    
    def _fetch_all_sources(
        self,
        commodities: Optional[List[str]],
        sources: Optional[List[str]],
        start_date: str,
        end_date: str
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Fetch data from all enabled sources in parallel.
        
        Returns:
            Dictionary mapping source names to DataFrames (or None if failed)
        """
        results = {}
        
        # Prepare fetch tasks
        tasks = []
        
        if (sources is None or 'EIA' in sources) and self.eia_client:
            tasks.append(('EIA', self._fetch_eia_data, start_date, end_date))
        
        if (sources is None or 'FRED' in sources) and self.fred_client:
            tasks.append(('FRED', self._fetch_fred_data, start_date, end_date))
        
        if (sources is None or 'YAHOO' in sources) and self.yahoo_client:
            tasks.append(('YAHOO', self._fetch_yahoo_data, start_date, end_date))
        
        # Execute tasks in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_source = {
                executor.submit(fetch_func, start_date, end_date): source_name
                for source_name, fetch_func, start_date, end_date in tasks
            }
            
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    data = future.result()
                    results[source_name] = data
                    if data is not None:
                        logger.info(f"Fetched {len(data)} records from {source_name}")
                    else:
                        logger.warning(f"No data fetched from {source_name}")
                except Exception as e:
                    logger.error(f"Failed to fetch from {source_name}: {e}")
                    results[source_name] = None
        
        return results
    
    def _fetch_eia_data(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Fetch data from EIA API."""
        try:
            df = self.eia_client.fetch_wti_prices(start_date, end_date)
            if not df.empty:
                df = df.rename(columns={'date': 'timestamp'})
                df['commodity'] = 'WTI_CRUDE'
                df['source'] = 'EIA'
                return df
            return None
        except Exception as e:
            logger.error(f"EIA fetch failed: {e}")
            return None
    
    def _fetch_fred_data(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Fetch data from FRED API."""
        try:
            dfs = []
            series_map = {
                'DCOILWTICO': 'WTI_CRUDE',
                'DCOILBRENTEU': 'BRENT_CRUDE'
            }
            
            for series_id, commodity in series_map.items():
                df = self.fred_client.fetch_series(series_id, start_date, end_date)
                if not df.empty:
                    df = df.rename(columns={'date': 'timestamp', 'value': 'price'})
                    df['commodity'] = commodity
                    df['source'] = 'FRED'
                    dfs.append(df)
            
            if dfs:
                return pd.concat(dfs, ignore_index=True)
            return None
        except Exception as e:
            logger.error(f"FRED fetch failed: {e}")
            return None
    
    def _fetch_yahoo_data(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Fetch data from Yahoo Finance API."""
        try:
            dfs = []
            ticker_map = {
                'CL=F': 'WTI_CRUDE',
                'BZ=F': 'BRENT_CRUDE'
            }
            
            for ticker, commodity in ticker_map.items():
                df = self.yahoo_client.fetch_ohlcv(ticker, start_date, end_date)
                if not df.empty:
                    df = df.rename(columns={'date': 'timestamp', 'close': 'price'})
                    df['commodity'] = commodity
                    df['source'] = 'YAHOO_FINANCE'
                    dfs.append(df)
            
            if dfs:
                return pd.concat(dfs, ignore_index=True)
            return None
        except Exception as e:
            logger.error(f"Yahoo Finance fetch failed: {e}")
            return None
    
    def _validate_all_data(
        self,
        fetch_results: Dict[str, Optional[pd.DataFrame]]
    ) -> Dict[str, Optional[Dict]]:
        """
        Validate data from all sources.
        
        Returns:
            Dictionary mapping source names to validation results
        """
        validation_results = {}
        
        for source_name, df in fetch_results.items():
            if df is None or df.empty:
                validation_results[source_name] = None
                continue
            
            try:
                # Run all validations
                schema_result = self.validator.validate_schema(df)
                completeness_result = self.validator.check_completeness(
                    df,
                    exclude_weekends=self.config['validation']['exclude_weekends']
                )
                df_with_outliers = self.validator.detect_outliers(df, column='price')
                
                # Prepare validation results for quality report
                val_results = {
                    'schema': schema_result,
                    'completeness': completeness_result,
                    'consistency': {'consistency_score': 100.0}  # Single source
                }
                
                # Generate quality report
                report = self.validator.generate_quality_report(df_with_outliers, val_results)
                
                validation_results[source_name] = {
                    'quality_score': report['summary']['overall_quality_score'],
                    'quality_level': report['summary']['quality_level'],
                    'report': report,
                    'validated_data': df_with_outliers
                }
                
                logger.info(
                    f"{source_name} validation: {report['summary']['quality_level']} "
                    f"({report['summary']['overall_quality_score']}%)"
                )
                
            except Exception as e:
                logger.error(f"Validation failed for {source_name}: {e}")
                validation_results[source_name] = None
        
        return validation_results
    
    def _store_all_data(
        self,
        fetch_results: Dict[str, Optional[pd.DataFrame]],
        validation_results: Dict[str, Optional[Dict]]
    ) -> Dict[str, int]:
        """
        Store validated data to database.
        
        Returns:
            Dictionary mapping source names to number of records stored
        """
        storage_results = {}
        quality_threshold = self.config['validation']['quality_threshold']
        
        for source_name, df in fetch_results.items():
            if df is None or df.empty:
                storage_results[source_name] = 0
                continue
            
            val_result = validation_results.get(source_name)
            if val_result is None:
                logger.warning(f"Skipping storage for {source_name}: validation failed")
                storage_results[source_name] = 0
                continue
            
            # Check quality threshold
            quality_score = val_result['quality_score']
            if quality_score < quality_threshold:
                logger.warning(
                    f"Skipping storage for {source_name}: quality score {quality_score}% "
                    f"below threshold {quality_threshold}%"
                )
                storage_results[source_name] = 0
                continue
            
            # Store data
            try:
                validated_data = val_result['validated_data']
                records_stored = 0
                
                for _, row in validated_data.iterrows():
                    try:
                        insert_price_data(
                            commodity=row['commodity'],
                            source=row['source'],
                            timestamp=row['timestamp'],
                            price=float(row['price']),
                            volume=float(row.get('volume', 0)) if pd.notna(row.get('volume')) else None
                        )
                        records_stored += 1
                    except Exception as e:
                        logger.warning(f"Failed to insert record: {e}")
                
                storage_results[source_name] = records_stored
                logger.info(f"Stored {records_stored} records from {source_name}")
                
            except Exception as e:
                logger.error(f"Storage failed for {source_name}: {e}")
                storage_results[source_name] = 0
        
        return storage_results
    
    def _generate_summary(self, result: PipelineExecutionResult) -> str:
        """Generate human-readable summary of pipeline execution."""
        lines = []
        lines.append("="*80)
        lines.append("PIPELINE EXECUTION SUMMARY")
        lines.append("="*80)
        lines.append(f"Status: {result.status}")
        lines.append(f"Duration: {result.duration_seconds:.2f} seconds")
        lines.append(f"Start Time: {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"End Time: {result.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        lines.append("Records Fetched:")
        for source, count in result.records_fetched.items():
            lines.append(f"  {source}: {count}")
        lines.append(f"  TOTAL: {sum(result.records_fetched.values())}")
        lines.append("")
        
        lines.append("Records Stored:")
        for source, count in result.records_stored.items():
            lines.append(f"  {source}: {count}")
        lines.append(f"  TOTAL: {sum(result.records_stored.values())}")
        lines.append("")
        
        if result.quality_scores:
            lines.append("Quality Scores:")
            for source, score in result.quality_scores.items():
                lines.append(f"  {source}: {score}%")
            lines.append("")
        
        if result.warnings:
            lines.append("Warnings:")
            for warning in result.warnings:
                lines.append(f"  - {warning}")
            lines.append("")
        
        if result.errors:
            lines.append("Errors:")
            for error in result.errors:
                lines.append(f"  - {error}")
            lines.append("")
        
        lines.append("="*80)
        
        return "\n".join(lines)


if __name__ == '__main__':
    # Example usage
    orchestrator = DataPipelineOrchestrator()
    result = orchestrator.run_pipeline(mode='incremental')
    print(result.summary)

