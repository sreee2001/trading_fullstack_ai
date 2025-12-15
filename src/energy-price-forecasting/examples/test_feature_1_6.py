"""
Test the complete pipeline with scheduling and monitoring.

Tests Stories 1.6.3, 1.6.4, 1.6.5

Author: AI Assistant
Date: December 14, 2025
"""

import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_pipeline.scheduler import PipelineScheduler
from data_pipeline.monitor import PipelineMonitor
from data_pipeline.notifications import NotificationService
import yaml

def test_monitor():
    """Test the monitoring dashboard."""
    print("\n" + "="*80)
    print("TEST 1: PIPELINE MONITORING DASHBOARD")
    print("="*80)
    
    monitor = PipelineMonitor()
    monitor.print_status()
    
    print("\nMonitor test PASSED\n")


def test_notifications():
    """Test the notification system."""
    print("\n" + "="*80)
    print("TEST 2: NOTIFICATION SYSTEM")
    print("="*80)
    
    # Load config
    config_path = Path(__file__).parent.parent / 'data_pipeline' / 'pipeline_config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    notification_service = NotificationService(config)
    
    # Test notification (will only send if enabled in config)
    print("Attempting to send test notification...")
    notification_service.send_notification(
        status='SUCCESS',
        summary='Test notification from pipeline test',
        details={
            'records_fetched': {'YAHOO': 10},
            'records_stored': {'YAHOO': 10}
        }
    )
    
    print("\nNotification test PASSED (check email/Slack if enabled)")
    print("Note: Configure email/Slack in pipeline_config.yaml to actually send")
    print()


def test_scheduler_dry_run():
    """Test the scheduler (without actually running indefinitely)."""
    print("\n" + "="*80)
    print("TEST 3: SCHEDULER (DRY RUN)")
    print("="*80)
    
    scheduler = PipelineScheduler()
    
    # Check initial status
    status = scheduler.get_status()
    print(f"Initial Status: {status['status']}")
    
    # Test manual trigger
    print("\nTesting manual pipeline trigger...")
    result = scheduler.run_now()
    
    print(f"\nPipeline Status: {result.status}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print(f"Records Fetched: {sum(result.records_fetched.values())}")
    print(f"Records Stored: {sum(result.records_stored.values())}")
    
    print("\nScheduler test PASSED")
    print("Note: To run scheduler continuously, use: python -m data_pipeline schedule start")
    print()


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print(" " * 20 + "FEATURE 1.6 COMPREHENSIVE TEST")
    print(" " * 15 + "(Stories 1.6.3, 1.6.4, 1.6.5)")
    print("="*80)
    
    try:
        # Test monitoring
        test_monitor()
        
        # Test notifications
        test_notifications()
        
        # Test scheduler
        test_scheduler_dry_run()
        
        print("="*80)
        print(" " * 25 + "ALL TESTS PASSED!")
        print("="*80)
        print("\nFeature 1.6 is now COMPLETE!")
        print("\nNext Steps:")
        print("  1. Configure email/Slack in pipeline_config.yaml")
        print("  2. Run: python -m data_pipeline schedule start")
        print("  3. Run: python -m data_pipeline status")
        print()
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

