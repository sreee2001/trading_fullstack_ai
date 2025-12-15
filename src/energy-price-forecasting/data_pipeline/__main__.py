"""
Main entry point for data_pipeline module.

Allows running pipeline commands via:
    python -m data_pipeline <command>

Commands:
    run         Run the pipeline
    schedule    Start/stop scheduler
    status      View pipeline status

Author: AI Assistant
Date: December 14, 2025
"""

import sys
import argparse

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Energy Price Data Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the pipeline')
    run_parser.add_argument('--mode', choices=['incremental', 'full_refresh', 'backfill'],
                           default='incremental', help='Pipeline mode')
    run_parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    run_parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    run_parser.add_argument('--sources', help='Comma-separated list of sources')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Manage scheduler')
    schedule_parser.add_argument('action', choices=['start', 'stop', 'status'],
                                help='Scheduler action')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='View pipeline status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'run':
        from data_pipeline import DataPipelineOrchestrator
        
        orchestrator = DataPipelineOrchestrator()
        sources = args.sources.split(',') if args.sources else None
        
        result = orchestrator.run_pipeline(
            mode=args.mode,
            sources=sources,
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        print(result.summary)
        return 0 if result.status == 'SUCCESS' else 1
    
    elif args.command == 'schedule':
        from data_pipeline.scheduler import PipelineScheduler
        
        scheduler = PipelineScheduler()
        
        if args.action == 'start':
            scheduler.start()
            print("Scheduler started. Running in background...")
            
            # Keep alive
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                scheduler.stop()
                print("Scheduler stopped.")
        
        elif args.action == 'stop':
            scheduler.stop()
        
        elif args.action == 'status':
            status = scheduler.get_status()
            print(f"Scheduler: {status['status']}")
            if status['next_run']:
                print(f"Next Run: {status['next_run']}")
        
        return 0
    
    elif args.command == 'status':
        from data_pipeline.monitor import PipelineMonitor
        
        monitor = PipelineMonitor()
        monitor.print_status()
        return 0

if __name__ == '__main__':
    sys.exit(main())

