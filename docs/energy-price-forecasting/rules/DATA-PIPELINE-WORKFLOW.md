# Data Pipeline Workflow Documentation

**Project**: Energy Price Forecasting System  
**Feature**: 1.6 - Automated Data Pipeline Orchestration  
**Version**: 1.0  
**Date**: December 14, 2025

---

## Overview

The Data Pipeline Orchestration system automates the process of fetching, validating, and storing energy price data from multiple sources. This ensures data freshness, quality, and consistency for downstream ML model training and forecasting.

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA PIPELINE ORCHESTRATOR                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │    1. INITIALIZATION & CONFIGURATION   │
         │    - Load configuration                │
         │    - Initialize API clients            │
         │    - Initialize validator              │
         │    - Connect to database               │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │    2. DATA FETCHING (Parallel)         │
         │    ┌──────────┬──────────┬──────────┐  │
         │    │   EIA    │  FRED    │  Yahoo   │  │
         │    │  Client  │  Client  │ Finance  │  │
         │    └──────────┴──────────┴──────────┘  │
         │    - Fetch WTI, Brent, Natural Gas     │
         │    - Date range: configurable          │
         │    - Retry on transient failures       │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │    3. DATA VALIDATION                  │
         │    - Schema validation                 │
         │    - Completeness checks               │
         │    - Outlier detection                 │
         │    - Cross-source consistency          │
         │    - Generate quality reports          │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │    4. DATA STORAGE                     │
         │    - Upsert to TimescaleDB             │
         │    - Maintain data lineage             │
         │    - Update metadata tables            │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │    5. REPORTING & NOTIFICATIONS        │
         │    - Log pipeline execution            │
         │    - Generate summary report           │
         │    - Send notifications (on failure)   │
         │    - Update pipeline status            │
         └────────────────────────────────────────┘
```

---

## Workflow Steps

### Step 1: Initialization & Configuration

**Purpose**: Set up all required components for pipeline execution.

**Actions**:
1. Load pipeline configuration from YAML file
2. Initialize API clients (EIA, FRED, Yahoo Finance)
3. Initialize DataValidator
4. Connect to TimescaleDB database
5. Set up logging

**Error Handling**:
- If configuration missing: Use defaults, log warning
- If API key missing: Skip that source, log error
- If database connection fails: Abort pipeline, alert operator

**Success Criteria**: All components initialized successfully

---

### Step 2: Data Fetching (Parallel Execution)

**Purpose**: Retrieve energy price data from multiple sources.

**Sources**:
1. **EIA API**
   - WTI Crude Oil (daily)
   - Natural Gas (monthly/annual)

2. **FRED API**
   - WTI Crude Oil (daily)
   - Brent Crude Oil (daily)
   - Natural Gas (daily)

3. **Yahoo Finance**
   - CL=F (WTI Futures)
   - BZ=F (Brent Futures)
   - NG=F (Natural Gas Futures)

**Configuration**:
- **Date Range**: Configurable (default: last 30 days)
- **Commodities**: Configurable list
- **Sources**: Configurable list
- **Parallel**: Fetch from all sources concurrently

**Retry Logic**:
- **Transient Errors** (429, 500): Retry 3 times with exponential backoff
- **Persistent Errors** (401, 404): Log and skip source
- **Timeout**: 30 seconds per request

**Error Handling**:
- If all sources fail: Abort pipeline, alert operator
- If some sources fail: Continue with available data, log warnings
- If partial data returned: Validate and store what's available

**Success Criteria**: At least one source returns valid data

---

### Step 3: Data Validation

**Purpose**: Ensure data quality before storage.

**Validation Steps**:

1. **Schema Validation**
   - Check column names and types
   - Verify required fields present
   - Score: 0-100%

2. **Completeness Checks**
   - Detect gaps in time series
   - Identify missing values
   - Score: 0-100%

3. **Outlier Detection**
   - Z-score method (threshold: 3.0)
   - IQR method (multiplier: 1.5)
   - Flag, don't remove

4. **Cross-Source Consistency** (if multiple sources)
   - Compare prices for same commodity/date
   - Tolerance: 5%
   - Score: 0-100%

5. **Quality Report Generation**
   - Overall quality score (weighted)
   - Quality level (Excellent, Good, Fair, Poor, Unusable)
   - Actionable recommendations

**Quality Thresholds**:
- **Excellent (95-100%)**: Proceed with storage
- **Good (85-94%)**: Proceed with storage, log info
- **Fair (70-84%)**: Proceed with caution, log warning
- **Poor (50-69%)**: Review required, log error
- **Unusable (<50%)**: Reject data, log critical error

**Error Handling**:
- If quality < 50%: Reject batch, alert operator
- If quality 50-70%: Store with quality flag, alert operator
- If quality > 70%: Store normally

**Success Criteria**: Quality score >= 50% for at least one source

---

### Step 4: Data Storage

**Purpose**: Persist validated data to TimescaleDB.

**Storage Strategy**:
- **Upsert**: Update existing records, insert new ones
- **Batch Processing**: Insert in batches of 1000 records
- **Transaction**: All-or-nothing for each batch
- **Idempotency**: Safe to re-run pipeline without duplicates

**Database Operations**:
1. Begin transaction
2. Upsert commodity metadata
3. Upsert data source metadata
4. Upsert price data (using ON CONFLICT DO UPDATE)
5. Commit transaction
6. Update pipeline_runs metadata table

**Error Handling**:
- If database unavailable: Retry 3 times, then abort
- If constraint violation: Log error, skip record
- If transaction fails: Rollback, log error
- If partial insert fails: Rollback entire batch

**Success Criteria**: All validated data stored successfully

---

### Step 5: Reporting & Notifications

**Purpose**: Provide visibility into pipeline execution.

**Reporting**:
1. **Execution Summary**
   - Pipeline start/end time
   - Total records fetched
   - Total records stored
   - Quality scores per source
   - Errors/warnings encountered

2. **Quality Report**
   - Overall quality assessment
   - Per-source quality breakdown
   - Validation issues found
   - Recommendations

3. **Pipeline Status**
   - SUCCESS: All steps completed without errors
   - PARTIAL_SUCCESS: Some sources failed
   - FAILED: Pipeline aborted due to errors

**Notification Strategy**:

| **Event** | **Notification** | **Channel** |
|-----------|-----------------|-------------|
| Pipeline success | Log INFO | Log file |
| Partial success | Log WARNING | Log file + Optional email |
| Pipeline failure | Log ERROR | Log file + Optional email |
| Quality < 70% | Log WARNING | Log file |
| Quality < 50% | Log ERROR | Log file + Optional email |
| Database error | Log CRITICAL | Log file + Optional email |

**Notification Channels**:
- **Log File**: Always enabled (`logs/pipeline.log`)
- **Email**: Optional, configured via SMTP settings
- **Slack**: Optional, configured via webhook URL
- **CLI Output**: Real-time during manual runs

**Success Criteria**: Summary report generated and logged

---

## Error Handling Strategy

### Error Categories

1. **Transient Errors** (Retry)
   - Network timeouts
   - HTTP 429 (Rate limit)
   - HTTP 500, 502, 503 (Server errors)
   - Database connection timeout

2. **Persistent Errors** (Skip & Log)
   - HTTP 401 (Unauthorized - bad API key)
   - HTTP 404 (Not found)
   - Invalid data format
   - Schema validation failure

3. **Critical Errors** (Abort Pipeline)
   - All sources failed
   - Database unavailable after retries
   - Configuration file missing/invalid
   - Insufficient disk space

### Retry Logic

**Exponential Backoff**:
```
Attempt 1: Immediate
Attempt 2: Wait 2 seconds
Attempt 3: Wait 4 seconds
Attempt 4: Wait 8 seconds
(Max 3 retries)
```

**Retry Conditions**:
- Network errors: Retry 3 times
- HTTP 429/500: Retry 3 times
- Database errors: Retry 3 times
- Validation errors: No retry (skip)

### Partial Failure Handling

**Scenario**: Some sources succeed, others fail

**Strategy**:
1. Continue with available data
2. Log warnings for failed sources
3. Store successful fetches
4. Mark pipeline as PARTIAL_SUCCESS
5. Send notification with details

**Example**:
```
EIA: SUCCESS (21 records)
FRED: FAILED (API timeout)
Yahoo Finance: SUCCESS (20 records)
Result: PARTIAL_SUCCESS - 41 records stored
```

---

## Pipeline Configuration

**File**: `pipeline_config.yaml`

```yaml
pipeline:
  name: "Energy Price Data Pipeline"
  version: "1.0"
  
schedule:
  enabled: true
  time: "06:00"  # 6:00 AM EST
  timezone: "America/New_York"
  frequency: "daily"

data_sources:
  eia:
    enabled: true
    commodities: ["WTI_CRUDE", "NATURAL_GAS"]
  fred:
    enabled: true
    series: ["DCOILWTICO", "DCOILBRENTEU", "DHHNGSP"]
  yahoo_finance:
    enabled: true
    tickers: ["CL=F", "BZ=F", "NG=F"]

date_range:
  mode: "incremental"  # or "full_refresh"
  lookback_days: 30
  max_history_days: 3650  # 10 years

validation:
  quality_threshold: 70  # Minimum acceptable quality %
  exclude_weekends: true
  outlier_detection: true

storage:
  batch_size: 1000
  upsert: true
  create_backup: false

notifications:
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    from_email: "pipeline@example.com"
    to_emails: ["admin@example.com"]
  slack:
    enabled: false
    webhook_url: ""

logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "logs/pipeline.log"
  max_file_size_mb: 100
  backup_count: 10
  console_output: true

error_handling:
  retry_attempts: 3
  retry_backoff: 2  # seconds
  continue_on_partial_failure: true
  abort_on_critical: true
```

---

## Pipeline Modes

### 1. Incremental Mode (Default)

**Purpose**: Update with latest data only

**Behavior**:
- Fetch data from (last_stored_date + 1) to today
- Efficient for daily updates
- Recommended for scheduled runs

**Example**:
```
Last stored date: 2024-12-10
Today: 2024-12-14
Fetch range: 2024-12-11 to 2024-12-14 (4 days)
```

### 2. Full Refresh Mode

**Purpose**: Re-fetch all historical data

**Behavior**:
- Fetch data for entire configured history (e.g., 10 years)
- Used for initial load or data corrections
- Run manually, not scheduled

**Example**:
```
Today: 2024-12-14
Max history: 10 years
Fetch range: 2014-12-14 to 2024-12-14 (3650 days)
```

### 3. Backfill Mode

**Purpose**: Fill gaps in historical data

**Behavior**:
- Detect gaps in stored data
- Fetch only missing date ranges
- Efficient for fixing data gaps

**Example**:
```
Stored data: 2024-01-01 to 2024-01-31 (with gap 2024-01-15 to 2024-01-20)
Fetch only: 2024-01-15 to 2024-01-20 (6 days)
```

---

## Pipeline Execution

### Manual Execution

**Command**:
```bash
python -m data_pipeline run --mode incremental --commodities WTI,BRENT --days 30
```

**Options**:
- `--mode`: incremental, full_refresh, backfill
- `--commodities`: Comma-separated list (or "all")
- `--sources`: Comma-separated list (or "all")
- `--days`: Number of days to fetch
- `--start-date`: Start date (YYYY-MM-DD)
- `--end-date`: End date (YYYY-MM-DD)
- `--dry-run`: Validate without storing

### Scheduled Execution

**Using APScheduler** (In-process):
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    run_pipeline,
    'cron',
    hour=6,
    minute=0,
    timezone='America/New_York'
)
scheduler.start()
```

**Using Cron** (External):
```bash
0 6 * * * cd /path/to/project && /path/to/venv/bin/python -m data_pipeline run >> logs/cron.log 2>&1
```

---

## Monitoring & Observability

### Metrics Tracked

1. **Execution Metrics**
   - Pipeline start/end time
   - Total execution duration
   - Records fetched per source
   - Records stored per source
   - Success/failure counts

2. **Quality Metrics**
   - Quality scores per source
   - Validation issues count
   - Outliers detected
   - Cross-source discrepancies

3. **Error Metrics**
   - Errors per source
   - Retry attempts
   - Failed batches
   - Critical errors

### Status Dashboard (CLI)

**Command**:
```bash
python -m data_pipeline status
```

**Output**:
```
Pipeline Status Report
======================
Last Run: 2024-12-14 06:00:15
Status: SUCCESS
Duration: 45.3 seconds
Records Stored: 63

Source Status:
  EIA: SUCCESS (21 records, quality: 98.18%)
  FRED: SUCCESS (21 records, quality: 98.18%)
  Yahoo: SUCCESS (21 records, quality: 98.10%)

Data Freshness:
  WTI_CRUDE: 2024-12-14 (0 days old)
  BRENT_CRUDE: 2024-12-14 (0 days old)
  NATURAL_GAS: 2024-12-13 (1 days old)

Next Scheduled Run: 2024-12-15 06:00:00
```

---

## Disaster Recovery

### Backup Strategy

1. **Database Backups**
   - Automated daily backups via pg_dump
   - Retention: 30 days
   - Location: `backups/db/`

2. **Pipeline State**
   - Track last successful run
   - Store in `pipeline_runs` table
   - Can resume from last checkpoint

3. **Raw Data Cache**
   - Optional: Store raw API responses
   - Location: `cache/raw_data/`
   - Retention: 7 days

### Recovery Procedures

**Scenario 1: Pipeline failure mid-run**
- Pipeline automatically rolls back uncommitted transactions
- Re-run pipeline with same date range
- Idempotent upserts prevent duplicates

**Scenario 2: Database corruption**
- Restore from latest backup
- Run backfill mode for missing dates

**Scenario 3: Bad data stored**
- Delete affected date range
- Re-run pipeline for that range
- Validation prevents most bad data

---

## Performance Optimization

### Current Performance

- **Fetch time**: ~5-10 seconds (parallel)
- **Validation time**: ~1-2 seconds
- **Storage time**: ~2-3 seconds
- **Total**: ~10-15 seconds for 30 days of data

### Optimization Strategies

1. **Parallel Fetching**: Already implemented
2. **Batch Inserts**: Insert 1000 records at a time
3. **Connection Pooling**: Reuse database connections
4. **Caching**: Cache API responses (5-minute TTL)
5. **Incremental Mode**: Fetch only new data

---

## Testing Strategy

### Unit Tests
- Test each pipeline component independently
- Mock API responses
- Test error scenarios

### Integration Tests
- Test full pipeline end-to-end
- Use test database
- Verify data integrity

### Load Tests
- Test with 10 years of historical data
- Measure performance metrics
- Identify bottlenecks

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Dec 14, 2025 | Initial workflow design | AI Assistant |

---

**Status**: ✅ Ready for Implementation

