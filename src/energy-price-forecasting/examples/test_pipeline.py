"""
Quick test of the DataPipelineOrchestrator.

Tests the pipeline with a small date range to verify functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_pipeline import DataPipelineOrchestrator

def main():
    """Test the pipeline orchestrator."""
    print("="*80)
    print("TESTING DATA PIPELINE ORCHESTRATOR")
    print("="*80)
    print()
    
    # Initialize orchestrator
    print("1. Initializing orchestrator...")
    orchestrator = DataPipelineOrchestrator()
    print("   OK - Orchestrator initialized")
    print()
    
    # Run pipeline with small date range
    print("2. Running pipeline (incremental mode, last 7 days)...")
    result = orchestrator.run_pipeline(
        mode='incremental',
        start_date='2024-12-07',
        end_date='2024-12-14'
    )
    print()
    
    # Print results
    print(result.summary)
    print()
    
    # Print result details
    print("DETAILED RESULTS:")
    print(f"  Status: {result.status}")
    print(f"  Duration: {result.duration_seconds:.2f}s")
    print(f"  Total Fetched: {sum(result.records_fetched.values())}")
    print(f"  Total Stored: {sum(result.records_stored.values())}")
    print()
    
    if result.status in ["SUCCESS", "PARTIAL_SUCCESS"]:
        print("SUCCESS - Pipeline test PASSED!")
        return 0
    else:
        print("FAILED - Pipeline test FAILED!")
        return 1


if __name__ == '__main__':
    sys.exit(main())

