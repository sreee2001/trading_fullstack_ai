# A/B Testing Architecture

## Overview

The A/B Testing Framework implements a Champion/Challenger pattern for comparing production models against new challenger models. This allows safe testing of new models in production with a small percentage of traffic.

## Architecture Components

### 1. Traffic Splitting

**Component**: `TrafficSplitter`

- **Purpose**: Routes requests to either champion (production) or challenger (test) model
- **Method**: Deterministic hashing based on user ID
- **Default Split**: 90% champion, 10% challenger (configurable)
- **Consistency**: Same user always gets same model (deterministic)

**Implementation**:
```python
splitter = TrafficSplitter(split_ratio=0.9)
model = splitter.select_model(user_id)  # Returns 'champion' or 'challenger'
```

### 2. Result Tracking

**Component**: `ABTestTracker`

- **Purpose**: Records predictions and actual outcomes for both models
- **Storage**: JSON file (can be extended to database)
- **Metrics Calculated**:
  - MAE (Mean Absolute Error)
  - RMSE (Root Mean Squared Error)
  - MAPE (Mean Absolute Percentage Error)
  - Directional Accuracy
  - Mean prediction vs actual

**Data Structure**:
```python
ABTestResult(
    user_id: str,
    timestamp: datetime,
    model_version: str,  # 'champion' or 'challenger'
    commodity: str,
    prediction: float,
    actual: Optional[float],
    error: Optional[float]
)
```

### 3. Model Comparison

**Component**: `ABTestTracker.compare_models()`

- **Purpose**: Compare performance metrics between champion and challenger
- **Requirements**: Minimum samples (default: 100) for statistical validity
- **Output**: 
  - Performance metrics for each model
  - Improvement percentages
  - Recommendation (promote_challenger, keep_champion, inconclusive)

### 4. Model Promotion

**Component**: `ModelPromoter`

- **Purpose**: Automatically promote challenger to champion if it performs better
- **Criteria**:
  - Minimum test duration: 14 days (configurable)
  - Minimum improvement: 5% (configurable)
  - Statistical significance: Optional
- **Process**:
  1. Check test duration
  2. Compare metrics
  3. Verify improvement threshold
  4. Promote if criteria met

## Traffic Splitting Strategy

### Deterministic Hashing

Uses MD5 hash of user ID to ensure:
- Same user always gets same model (consistent experience)
- Even distribution across models
- Reproducible results

### Split Ratio Configuration

- **Default**: 90% champion, 10% challenger
- **Rationale**: 
  - Minimize risk to production traffic
  - Collect sufficient data for comparison
  - Allow gradual rollout

### User Identification

- **Authenticated Users**: Use user ID
- **Anonymous Users**: Use request ID or IP address
- **Consistency**: Critical for accurate comparison

## Metrics Collection

### Prediction Recording

Every prediction is recorded with:
- User ID
- Timestamp
- Model version (champion/challenger)
- Commodity
- Prediction value
- Actual value (when available)

### Actual Value Updates

Actual values can be updated later when:
- Real prices become available
- Historical data is backfilled
- External validation is performed

## Statistical Analysis

### Comparison Metrics

1. **Error Metrics**:
   - MAE: Mean Absolute Error
   - RMSE: Root Mean Squared Error
   - MAPE: Mean Absolute Percentage Error

2. **Directional Accuracy**:
   - Percentage of correct direction predictions (up/down)

3. **Improvement Calculation**:
   ```
   improvement = (champion_metric - challenger_metric) / champion_metric
   ```
   Positive improvement = challenger is better

### Statistical Significance

- Minimum sample size: 100 predictions per model
- Significance level: 0.05 (configurable)
- Future: Implement t-test or chi-square test

## Promotion Criteria

### Requirements

1. **Test Duration**: Minimum 14 days
2. **Sample Size**: Minimum 100 predictions with actual values
3. **Improvement**: Average improvement > 5%
4. **Recommendation**: System recommends promotion

### Promotion Process

1. Check all criteria
2. Update model registry (mark challenger as Production)
3. Archive old champion
4. Update API configuration
5. Notify stakeholders
6. Reset A/B test for next challenger

## Integration Points

### API Integration

- Forecast endpoint uses `TrafficSplitter` to route requests
- Results recorded via `ABTestTracker`
- Actual values updated when available

### Model Registry Integration

- Champion: Model marked as "Production" in MLflow
- Challenger: Model marked as "Staging" in MLflow
- Promotion: Update model stages in registry

### Monitoring Integration

- Metrics exposed via monitoring endpoints
- Dashboards show A/B test progress
- Alerts on significant differences

## Configuration

### Environment Variables

```bash
AB_TEST_SPLIT_RATIO=0.9  # 90% champion
AB_TEST_MIN_DURATION_DAYS=14
AB_TEST_MIN_IMPROVEMENT=0.05  # 5%
AB_TEST_STORAGE_PATH=/data/ab_test_results.json
```

### YAML Configuration

```yaml
ab_testing:
  split_ratio: 0.9
  min_test_duration_days: 14
  min_improvement_threshold: 0.05
  require_statistical_significance: true
  storage_path: /data/ab_test_results.json
```

## Future Enhancements

1. **Database Storage**: Replace JSON file with database
2. **Statistical Tests**: Implement t-test, chi-square test
3. **Multi-variant Testing**: Support multiple challengers
4. **Real-time Monitoring**: Live dashboard for A/B test progress
5. **Automatic Rollback**: Revert if challenger performs worse
6. **Confidence Intervals**: Show uncertainty in metrics

## Usage Example

```python
from mlops.ab_testing import TrafficSplitter, ABTestTracker, ModelPromoter

# Initialize components
splitter = TrafficSplitter(split_ratio=0.9)
tracker = ABTestTracker(storage_path='ab_test_results.json')
promoter = ModelPromoter(tracker, min_test_duration_days=14)

# In forecast endpoint
user_id = request.user_id or request.headers.get('X-Request-ID')
model_version = splitter.select_model(user_id)

# Make prediction with selected model
prediction = make_prediction(model_version, commodity, horizon)

# Record result
tracker.record_prediction(
    user_id=user_id,
    model_version=model_version,
    commodity=commodity,
    prediction=prediction
)

# Later, update with actual value
tracker.update_actual(user_id, timestamp, actual_price)

# Check if promotion is warranted
should_promote, reason = promoter.should_promote(commodity=commodity)
if should_promote:
    promoter.promote_challenger(commodity)
```

