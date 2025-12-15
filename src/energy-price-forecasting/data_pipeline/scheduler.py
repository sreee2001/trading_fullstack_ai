"""
Scheduled Pipeline Runner using APScheduler.

Runs the data pipeline automatically on a configurable schedule.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import logging
from datetime import datetime
from pathlib import Path
import sys
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_pipeline import DataPipelineOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PipelineScheduler:
    """
    Scheduler for automated pipeline execution.
    
    Uses APScheduler to run the data pipeline on a configurable schedule.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the pipeline scheduler.
        
        Args:
            config_path: Path to pipeline configuration file
        """
        self.orchestrator = DataPipelineOrchestrator(config_path)
        self.config = self.orchestrator.config
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        
        logger.info("PipelineScheduler initialized")
    
    def start(self):
        """Start the scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        schedule_config = self.config.get('schedule', {})
        
        if not schedule_config.get('enabled', False):
            logger.warning("Scheduling is disabled in configuration")
            return
        
        # Parse schedule time
        time_str = schedule_config.get('time', '06:00')
        hour, minute = map(int, time_str.split(':'))
        
        # Create cron trigger
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone=schedule_config.get('timezone', 'America/New_York')
        )
        
        # Add job
        self.scheduler.add_job(
            func=self._run_pipeline_job,
            trigger=trigger,
            id='data_pipeline_job',
            name='Energy Price Data Pipeline',
            replace_existing=True
        )
        
        # Start scheduler
        self.scheduler.start()
        self.is_running = True
        
        logger.info(
            f"Scheduler started. Pipeline will run daily at {time_str} "
            f"{schedule_config.get('timezone', 'America/New_York')}"
        )
        
        # Print next run time
        next_run = self.scheduler.get_job('data_pipeline_job').next_run_time
        logger.info(f"Next scheduled run: {next_run}")
    
    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Scheduler stopped")
    
    def run_now(self):
        """Run the pipeline immediately (manual trigger)."""
        logger.info("Manual pipeline trigger")
        return self._run_pipeline_job()
    
    def _run_pipeline_job(self):
        """Internal job function that runs the pipeline."""
        logger.info("="*80)
        logger.info("SCHEDULED PIPELINE EXECUTION STARTING")
        logger.info("="*80)
        
        try:
            result = self.orchestrator.run_pipeline(mode='incremental')
            
            logger.info(f"Pipeline completed with status: {result.status}")
            logger.info(f"Records stored: {sum(result.records_stored.values())}")
            
            # Log summary
            for line in result.summary.split('\n'):
                logger.info(line)
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            raise
    
    def get_status(self):
        """Get scheduler status information."""
        if not self.is_running:
            return {
                'status': 'STOPPED',
                'next_run': None
            }
        
        job = self.scheduler.get_job('data_pipeline_job')
        
        return {
            'status': 'RUNNING',
            'next_run': job.next_run_time.isoformat() if job else None,
            'last_run': None  # Would need to track this separately
        }


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pipeline Scheduler')
    parser.add_argument(
        'command',
        choices=['start', 'stop', 'run-now', 'status'],
        help='Scheduler command'
    )
    
    args = parser.parse_args()
    
    scheduler = PipelineScheduler()
    
    if args.command == 'start':
        print("Starting scheduler...")
        scheduler.start()
        print("Scheduler started. Press Ctrl+C to stop.")
        
        try:
            # Keep process alive
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping scheduler...")
            scheduler.stop()
            print("Scheduler stopped.")
    
    elif args.command == 'stop':
        scheduler.stop()
    
    elif args.command == 'run-now':
        print("Running pipeline now...")
        result = scheduler.run_now()
        print(f"\nStatus: {result.status}")
        print(f"Records stored: {sum(result.records_stored.values())}")
    
    elif args.command == 'status':
        status = scheduler.get_status()
        print(f"Scheduler Status: {status['status']}")
        if status['next_run']:
            print(f"Next Run: {status['next_run']}")


if __name__ == '__main__':
    main()

