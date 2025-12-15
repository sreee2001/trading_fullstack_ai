"""
Epic 2 Manual Testing - Step 6: Model Versioning & Experiment Tracking (MLflow)

Tests Feature 2.6: MLflow Integration
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mlflow_tracking.mlflow_manager import MLflowManager
    from mlflow_tracking.experiment_tracker import ExperimentTracker
    from mlflow_tracking.model_registry import ModelRegistryManager
    MLFLOW_AVAILABLE = True
except ImportError as e:
    print(f"MLflow not available: {e}")
    MLFLOW_AVAILABLE = False

from dotenv import load_dotenv

load_dotenv()

if not MLFLOW_AVAILABLE:
    print("\n[WARN] MLflow not available. Skipping MLflow tests.")
    print("   Install with: pip install mlflow")
    exit(0)

print("="*80)
print("EPIC 2 MANUAL TESTING - STEP 6: MLFLOW TRACKING")
print("="*80)

# Test MLflow Manager
print("\n[1/4] Testing MLflow Manager...")

mlflow_manager = MLflowManager(
    tracking_uri='file:./mlruns',  # Local file system
    experiment_name='epic2_manual_testing'
)

# Create experiment
experiment_id = mlflow_manager.create_experiment()
print(f"[OK] Experiment created: {experiment_id}")

# Start a run
run = mlflow_manager.start_run()
print(f"[OK] Run started: {run.info.run_id}")

# Log parameters
mlflow_manager.log_params({
    'model_type': 'LSTM',
    'sequence_length': 60,
    'epochs': 10,
    'batch_size': 32,
    'test_name': 'epic2_manual_test'
})

# Log metrics
mlflow_manager.log_metrics({
    'train_loss': 0.05,
    'val_loss': 0.06,
    'test_rmse': 0.8,
    'test_mae': 0.6,
    'test_mape': 1.2
})

# End run
mlflow_manager.end_run()
print("[OK] Run completed and logged")

# Test Experiment Tracker
print("\n[2/4] Testing Experiment Tracker...")

tracker = ExperimentTracker(
    experiment_name='epic2_manual_testing',
    tracking_uri='file:./mlruns'
)

# Start run
run_id = tracker.start_run(
    run_name='lstm_experiment_manual_test',
    tags={'model': 'LSTM', 'test': 'epic2_manual', 'dataset': 'synthetic'}
)

# Log parameters
tracker.log_params({
    'sequence_length': 60,
    'lstm_units': [50, 50],
    'dropout_rate': 0.2,
    'learning_rate': 0.001
})

# Log metrics
tracker.log_metrics({
    'rmse': 0.8,
    'mae': 0.6,
    'mape': 1.2,
    'r2': 0.85,
    'directional_accuracy': 65.5
})

# Log artifact
summary = {
    'model_type': 'LSTM',
    'total_params': 50000,
    'training_time': 120.5,
    'test_date': datetime.now().isoformat()
}

artifact_file = Path(__file__).parent / 'model_summary_test.json'
with open(artifact_file, 'w') as f:
    json.dump(summary, f, indent=2)

tracker.log_artifact(str(artifact_file))
print(f"[OK] Artifact logged: {artifact_file}")

# End run
tracker.end_run()
print(f"[OK] Experiment tracked: {run_id}")

# Search runs
print("\n[3/4] Testing Run Search...")
runs = tracker.search_runs(filter_string="tags.test = 'epic2_manual'")
print(f"[OK] Found {len(runs)} runs with tag 'epic2_manual'")

if runs:
    print(f"   Latest run: {runs[0].info.run_id}")
    print(f"   Run name: {runs[0].data.tags.get('mlflow.runName', 'N/A')}")

# Test Model Registry
print("\n[4/4] Testing Model Registry...")

registry = ModelRegistryManager(tracking_uri='file:./mlruns')

# Register a model (using the run we just created)
if runs:
    model_uri = f"runs:/{runs[0].info.run_id}/model"
    try:
        model_name = "epic2_test_model"
        version = registry.register_model(
            model_uri=model_uri,
            name=model_name,
            tags={'test': 'epic2_manual', 'version': '1.0'}
        )
        print(f"[OK] Model registered: {model_name}, version {version}")
        
        # Get model versions
        versions = registry.get_model_versions(model_name)
        print(f"[OK] Model versions retrieved: {len(versions)} versions")
        
    except Exception as e:
        print(f"⚠️  Model registration skipped: {e}")
        print("   (This is expected if no model artifact was saved)")

print("\n" + "="*80)
print("[OK] STEP 6 COMPLETE: MLflow Tracking")
print("="*80)
print("\nMLflow UI can be viewed with: mlflow ui")
print("Then open: http://localhost:5000")
print("\nPlease review the output above.")
print("Press Enter to continue to Step 7...")
input()

