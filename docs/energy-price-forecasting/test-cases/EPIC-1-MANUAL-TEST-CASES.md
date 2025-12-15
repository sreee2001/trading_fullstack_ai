# Epic 1: Data Foundation & Infrastructure - Manual Test Cases

**Project**: Energy Price Forecasting System  
**Date**: December 15, 2025  
**Epic 1 Status**: ✅ 100% Complete (6/6 features)

---

## Executive Summary

### Epic 1: Data Foundation & Infrastructure
**Status**: ✅ **COMPLETE** (100%)  
**Description**: Complete data infrastructure including multi-source data ingestion (EIA, FRED, Yahoo Finance), PostgreSQL/TimescaleDB database, comprehensive validation framework, and automated pipeline orchestration.

**Features**:
1. ✅ EIA API Integration
2. ✅ FRED API Integration
3. ✅ Yahoo Finance Data Ingestion
4. ✅ Database Setup (PostgreSQL + TimescaleDB)
5. ✅ Data Validation & Quality Framework
6. ✅ Automated Data Pipeline Orchestration

---

## How to Test Epic Completion

### Epic 1 Testing Approach
1. **Unit Tests**: Run `pytest tests/` in `src/energy-price-forecasting/`
2. **Manual Integration Tests**: Use example scripts in `src/energy-price-forecasting/examples/`
3. **Feature-Specific Tests**: Each feature has dedicated test scripts
4. **Real Data Validation**: Test with actual API data
5. **Database Tests**: Verify database operations and performance

---

## Manual Test Cases

### EPIC 1: Data Foundation & Infrastructure

#### Feature 1.1: EIA API Integration

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-1.1.1 | EIA Client Initialization | Create `EIAAPIClient()` instance. Verify API key loaded from environment. | Client initialized. API key present. No errors. |
| TC-1.1.2 | Fetch WTI Prices | Call `client.fetch_wti_prices(start_date, end_date)`. Use real dates. | DataFrame returned with 'date' and 'price' columns. Data quality >95%. No errors. |
| TC-1.1.3 | Fetch Natural Gas Prices | Call `client.fetch_natural_gas_prices(start_date, end_date)`. | DataFrame returned. Natural gas prices valid. Data quality >95%. |
| TC-1.1.4 | Error Handling - Invalid API Key | Set invalid API key. Try to fetch data. | Appropriate error message. Graceful failure. No crashes. |
| TC-1.1.5 | Retry Logic | Simulate API failure (500 error). Verify retry with exponential backoff. | Retries attempted. Exponential backoff applied. Eventually succeeds or fails gracefully. |
| TC-1.1.6 | Response Normalization | Fetch data. Check DataFrame structure: columns, types, date format. | Standard format: 'date' (datetime), 'price' (float). UTC timezone. Consistent structure. |
| TC-1.1.7 | Data Quality Check | Fetch data. Run validation checks. Calculate quality score. | Quality score >95%. Validation checks pass. No missing critical data. |
| TC-1.1.8 | Rate Limiting | Make multiple rapid requests. Verify rate limit handling. | Rate limits respected. No 429 errors. Requests throttled appropriately. |

#### Feature 1.2: FRED API Integration

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-1.2.1 | FRED Client Initialization | Create `FREDAPIClient()` instance. Verify API key loaded. | Client initialized. API key present. Cache initialized. |
| TC-1.2.2 | Fetch WTI Series | Call `client.fetch_series('DCOILWTICO', start_date, end_date)`. | DataFrame returned. WTI prices valid. Data quality >95%. |
| TC-1.2.3 | Fetch Brent Series | Call `client.fetch_series('DCOILBRENTEU', start_date, end_date)`. | DataFrame returned. Brent prices valid. Data quality >95%. |
| TC-1.2.4 | Cache Functionality | Fetch same series twice within 5 minutes. Check cache hit. | Second request uses cache. Cache hit logged. Response time faster. |
| TC-1.2.5 | Cache Expiration | Fetch series. Wait 6 minutes. Fetch again. Verify cache miss. | Cache expired. New API request made. Cache miss logged. |
| TC-1.2.6 | Multiple Series Fetch | Fetch multiple series in one call. Verify all returned. | All series returned. Each series has correct data. No errors. |

#### Feature 1.3: Yahoo Finance Data Ingestion

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-1.3.1 | Yahoo Finance Client Initialization | Create `YahooFinanceClient()` instance. | Client initialized. No errors. |
| TC-1.3.2 | Fetch WTI Futures OHLCV | Call `client.fetch_ohlcv('CL=F', start_date, end_date)`. | DataFrame returned with 'date', 'open', 'high', 'low', 'close', 'volume'. All columns present. |
| TC-1.3.3 | Fetch Brent Futures OHLCV | Call `client.fetch_ohlcv('BZ=F', start_date, end_date)`. | OHLCV data returned. All price columns valid. Volume present. |
| TC-1.3.4 | Fetch Natural Gas Futures | Call `client.fetch_ohlcv('NG=F', start_date, end_date)`. | Natural gas OHLCV data returned. Data quality >95%. |
| TC-1.3.5 | Multiple Time Intervals | Fetch data with intervals: '1d', '1wk', '1mo'. Verify each. | All intervals work. Data structure consistent. Appropriate granularity. |
| TC-1.3.6 | Market Hours Handling | Fetch data including weekends/holidays. Check handling. | Missing days handled gracefully. No errors for non-trading days. Data continuous. |

#### Feature 1.4: Database Setup (PostgreSQL + TimescaleDB)

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-1.4.1 | Database Connection | Connect to PostgreSQL database. Verify connection. | Connection successful. Database accessible. No errors. |
| TC-1.4.2 | TimescaleDB Extension | Check TimescaleDB extension installed. Verify hypertable support. | Extension present. `create_hypertable` function available. |
| TC-1.4.3 | Schema Creation | Run migration script. Verify tables created: commodities, data_sources, price_data. | All tables created. Schema correct. Foreign keys present. |
| TC-1.4.4 | Hypertable Creation | Convert price_data to hypertable. Verify partitioning. | Hypertable created. Partitioned by timestamp. Chunks created. |
| TC-1.4.5 | Index Verification | Check indexes on timestamp and commodity_id. Verify performance. | Indexes present. Query performance <50ms. Indexes used in queries. |
| TC-1.4.6 | Data Insertion | Insert sample price data. Verify insertion. | Data inserted successfully. Can query back. No errors. |
| TC-1.4.7 | Query Performance | Query price_data for 1 year range. Measure response time. | Query completes in <50ms. TimescaleDB optimization working. |

#### Feature 1.5: Data Validation & Quality Framework

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-1.5.1 | Price Range Validation | Create validator. Validate prices within expected ranges (WTI: 0.01-300). | Valid prices pass. Out-of-range prices flagged. Error messages clear. |
| TC-1.5.2 | Volume Validation | Validate volume data. Check for negative or zero volumes (where appropriate). | Valid volumes pass. Invalid volumes flagged. Edge cases handled. |
| TC-1.5.3 | Completeness Check | Validate DataFrame completeness. Check for missing critical columns. | Missing columns detected. Completeness score calculated. Errors reported. |
| TC-1.5.4 | Consistency Validation | Validate price consistency (high >= low, close within range). | Consistent data passes. Inconsistent data flagged. Errors detailed. |
| TC-1.5.5 | Quality Score Calculation | Run full validation. Calculate quality score (0-100%). | Quality score calculated. Score >95% for good data. Breakdown provided. |
| TC-1.5.6 | Validation Rules Configuration | Modify validation rules. Verify custom rules applied. | Custom rules work. Configuration loaded correctly. Rules applied. |
| TC-1.5.7 | Real Data Validation | Validate data from all 3 sources (EIA, FRED, Yahoo). Check quality scores. | All sources pass validation. Quality scores >95%. No critical issues. |
| TC-1.5.8 | Error Reporting | Generate validation report. Check error details. | Report generated. Errors clearly listed. Recommendations provided. |

#### Feature 1.6: Automated Data Pipeline Orchestration

| Case # | Case Name | Case Details | Expected Outcome |
|--------|-----------|--------------|------------------|
| TC-1.6.1 | Pipeline Scheduler Setup | Create scheduler. Configure daily refresh schedule. | Scheduler configured. Schedule saved. No errors. |
| TC-1.6.2 | Manual Pipeline Run | Trigger pipeline manually. Verify all steps execute. | All steps execute. Data fetched from all sources. Data validated. Data stored. |
| TC-1.6.3 | Scheduled Pipeline Run | Wait for scheduled time. Verify pipeline runs automatically. | Pipeline runs at scheduled time. All steps complete. Logs created. |
| TC-1.6.4 | Pipeline Monitoring | Check pipeline health. Verify monitor detects issues. | Health status reported. Issues detected if present. Metrics tracked. |
| TC-1.6.5 | Error Handling | Simulate pipeline failure. Verify error recovery. | Error detected. Recovery attempted. Notification sent. Logs updated. |
| TC-1.6.6 | Notification System | Trigger error condition. Verify notification sent. | Notification sent (email/Slack). Error details included. Notification received. |
| TC-1.6.7 | Data Freshness Monitoring | Check data freshness. Verify stale data detection. | Freshness checked. Stale data detected if present. Alerts triggered. |

---

## Test Execution Summary

### Test Results Summary

| Feature | Test Cases | Passed | Failed | Status |
|---------|------------|--------|--------|--------|
| 1.1 EIA API | 8 | 8 | 0 | ✅ Complete |
| 1.2 FRED API | 6 | 6 | 0 | ✅ Complete |
| 1.3 Yahoo Finance | 6 | 6 | 0 | ✅ Complete |
| 1.4 Database Setup | 7 | 7 | 0 | ✅ Complete |
| 1.5 Data Validation | 8 | 8 | 0 | ✅ Complete |
| 1.6 Pipeline Orchestration | 7 | 7 | 0 | ✅ Complete |
| **TOTAL** | **42** | **42** | **0** | ✅ **100%** |

### Test Execution Instructions

1. **Environment Setup**:
   ```bash
   cd src/energy-price-forecasting
   source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
   pip install -r requirements.txt
   ```

2. **Run Unit Tests**:
   ```bash
   pytest tests/ -v
   ```

3. **Run Manual Tests**:
   ```bash
   python examples/fetch_wti_example.py
   python examples/fetch_fred_example.py
   python examples/fetch_yahoo_finance_example.py
   python examples/validation_example.py
   python examples/test_real_data_validation.py
   python examples/test_pipeline.py
   python examples/test_feature_1_6.py
   ```

4. **Verify Database**:
   ```bash
   python test_connection.py
   ```

---

## Related Documentation

- [Epic 1 Comprehensive Documentation](../epics/epic-1/EPIC-1-COMPREHENSIVE-DOCUMENTATION.md)
- [Epic 1 Status Report](../status/epic-completion/EPIC-1-STATUS-REPORT.md)
- [Testing Guide](../instructions/testing/TESTING-GUIDE.md)
- [Epic 1 Test Results](../status/test-results/)

---

**Last Updated**: December 15, 2025  
**Test Cases**: 42  
**Status**: ✅ All Test Cases Defined

