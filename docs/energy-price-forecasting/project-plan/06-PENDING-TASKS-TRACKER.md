# Energy Price Forecasting System - Pending Tasks Tracker

**Project**: Energy Price Forecasting System  
**Date**: December 15, 2025  
**Status**: Project Complete - Optional Enhancements Only  
**Last Updated**: December 15, 2025

---

## Overview

This tracker documents optional enhancements and minor improvements identified during gap analysis. **All required features are complete**. These tasks are **nice-to-have** improvements, not blockers.

---

## Task Categories

### 🔴 Critical (Blockers)
**Status**: ✅ **NONE** - All critical features complete

---

### 🟡 High Priority (Important but not blocking)
**Status**: ✅ **NONE** - All high-priority features complete

---

### 🟢 Medium Priority (Documentation Cleanup)

#### Task M1: Remove WebSocket Mentions from README
- **Status**: 📋 Pending
- **Priority**: Medium
- **Effort**: 5 minutes
- **Description**: Remove WebSocket mentions from README files (not in scope)
- **Files**: `src/energy-price-forecasting/README.md`
- **Reason**: WebSocket was never part of approved scope, only mentioned in early planning docs
- **Impact**: Low - Documentation accuracy

#### Task M2: Remove Streamlit Mentions from README
- **Status**: 📋 Pending
- **Priority**: Medium
- **Effort**: 5 minutes
- **Description**: Remove Streamlit mentions from README files (React dashboard chosen instead)
- **Files**: `src/energy-price-forecasting/README.md`
- **Reason**: React dashboard was implemented, not Streamlit
- **Impact**: Low - Documentation accuracy

---

### 🔵 Low Priority (Optional Enhancements)

#### Task L1: Implement Calmar Ratio
- **Status**: 📋 Pending
- **Priority**: Low (Optional)
- **Effort**: 1 hour
- **Description**: Add Calmar Ratio calculation to risk metrics module
- **Location**: `src/energy-price-forecasting/evaluation/performance_metrics.py`
- **Dependencies**: None
- **Reason**: Marked as optional in user stories, Sortino Ratio already implemented
- **Impact**: Low - Sharpe Ratio is primary risk metric

#### Task L2: Add Logging to GARCH Exception Handling
- **Status**: 📋 Pending
- **Priority**: Low (Optional)
- **Effort**: 15 minutes
- **Description**: Add logging when GARCH model fitting fails in volatility forecasting
- **Location**: `src/energy-price-forecasting/analytics/volatility_forecasting.py:268`
- **Dependencies**: None
- **Reason**: Silent exception handling could benefit from logging for debugging
- **Impact**: Low - Helps with debugging but not critical

#### Task L3: Implement Async Backtesting with Job Queue
- **Status**: 📋 Pending
- **Priority**: Low (Optional)
- **Effort**: 8 hours
- **Description**: Implement asynchronous backtesting using Celery or FastAPI BackgroundTasks
- **Location**: `src/energy-price-forecasting/api/routes/backtest.py`
- **Dependencies**: Redis or database for job storage
- **Reason**: Marked as optional in user stories (Story 4.5.3)
- **Impact**: Low - Synchronous backtesting works fine for current use cases
- **Trigger**: Implement if backtesting takes >30 seconds or concurrent backtests needed

#### Task L4: Implement Prometheus Metrics Endpoint
- **Status**: 📋 Pending
- **Priority**: Low (Optional)
- **Effort**: 3 hours
- **Description**: Add `/metrics` endpoint for Prometheus scraping
- **Location**: `src/energy-price-forecasting/api/routes/health.py` (or new route)
- **Dependencies**: Prometheus monitoring infrastructure
- **Reason**: Marked as optional in user stories (Story 4.9.3)
- **Impact**: Low - Health checks and logging provide sufficient monitoring
- **Trigger**: Implement if Prometheus/Grafana stack is deployed

#### Task L5: Create Grafana Monitoring Dashboard
- **Status**: 📋 Pending
- **Priority**: Low (Optional)
- **Effort**: 8 hours
- **Description**: Create Grafana dashboard for visualizing model performance and API metrics
- **Location**: New directory `monitoring/grafana/`
- **Dependencies**: Prometheus metrics (Task L4), Grafana instance
- **Reason**: Marked as optional in user stories (Story 6.6.4)
- **Impact**: Low - Basic monitoring via health checks and logs is sufficient
- **Trigger**: Implement if production monitoring requires advanced dashboards

---

## Task Summary

| Priority | Count | Status |
|----------|-------|--------|
| Critical | 0 | ✅ None |
| High | 0 | ✅ None |
| Medium | 2 | 📋 Pending |
| Low | 5 | 📋 Pending |
| **TOTAL** | **7** | **All Optional** |

---

## Next Steps

### Immediate (Recommended)
1. **Task M1**: Remove WebSocket mentions (5 min)
2. **Task M2**: Remove Streamlit mentions (5 min)

**Total Effort**: 10 minutes  
**Impact**: Documentation accuracy

### Optional (As Needed)
- Implement any of the 5 low-priority tasks based on actual needs
- No timeline pressure - all are optional enhancements

---

## Notes

- **All required features are complete**: 64/64 features (100%)
- **All critical tasks are done**: No blockers
- **All high-priority tasks are done**: No important items pending
- **Pending tasks are optional**: Nice-to-have improvements only

---

**Last Updated**: December 15, 2025  
**Next Review**: As needed (no scheduled review)

