# Data Validation Rules

**Project**: Energy Price Forecasting System  
**Version**: 1.0  
**Date**: December 14, 2025  
**Status**: ✅ Active

---

## Overview

This document defines the data validation rules for the Energy Price Forecasting System. These rules ensure data quality, consistency, and reliability across all data sources (EIA, FRED, Yahoo Finance).

---

## 1. Price Validation Rules

### 1.1 Price Range Rules

| **Commodity** | **Min Price (USD)** | **Max Price (USD)** | **Rationale** |
|---------------|---------------------|---------------------|---------------|
| WTI Crude Oil | 0.01 | 300.00 | Historical range: $10-$150, buffer for extremes |
| Brent Crude Oil | 0.01 | 300.00 | Similar to WTI |
| Natural Gas (Henry Hub) | 0.01 | 50.00 | Historical range: $1-$15, buffer for spikes |
| Gold (per oz) | 0.01 | 10000.00 | Historical range: $250-$2100, buffer for future |
| Silver (per oz) | 0.01 | 500.00 | Historical range: $5-$50, buffer for extremes |

### 1.2 Price Change Rules

- **Maximum Daily Change**: ±50% from previous day
  - **Rationale**: Extreme volatility events (e.g., 2020 oil crash) saw ~30% daily moves
  - **Action**: Flag for review if exceeded

- **Maximum Weekly Change**: ±70% from previous week
  - **Rationale**: Allows accumulation of daily volatility
  - **Action**: Flag for review if exceeded

### 1.3 Price Value Rules

- **Price must be > 0**: No negative or zero prices allowed (except for special cases like 2020 WTI futures)
- **Price must not be NULL**: Missing prices must be explicitly handled
- **Price precision**: Maximum 4 decimal places

---

## 2. Volume Validation Rules

### 2.1 Volume Range Rules

- **Minimum Volume**: 0 (zero volume is valid for non-trading days)
- **Maximum Volume**: No hard limit, but >10x average should be flagged
- **Volume must not be negative**

### 2.2 Volume Consistency Rules

- **Zero volume on weekends/holidays**: Expected for most commodities
- **Non-zero volume on trading days**: Missing volume on trading days should be flagged
- **Sudden volume spikes**: >5x average volume should be flagged for review

---

## 3. Timestamp Validation Rules

### 3.1 Format Rules

- **Format**: ISO 8601 (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- **Timezone**: UTC (all timestamps normalized to UTC)
- **Precision**: Daily or intraday (depending on source)

### 3.2 Sequential Rules

- **Chronological Order**: Timestamps must be in ascending order
- **No Duplicates**: No duplicate timestamps for same commodity/source
- **No Future Dates**: Timestamps cannot be in the future (beyond current date + 1 day buffer)

### 3.3 Completeness Rules

- **Maximum Gap**: 2 consecutive business days for daily data
  - **Exception**: Holidays, weekends (configurable calendar)
- **Minimum Data Points**: At least 30 data points for any analysis

---

## 4. Completeness Validation Rules

### 4.1 Missing Data Rules

- **Maximum Missing Rate**: <5% for any 30-day rolling window
- **Consecutive Missing**: No more than 2 consecutive business days
- **Required Fields**: timestamp, price (volume optional for some sources)

### 4.2 Gap Detection Rules

- **Daily Data**: Gap >2 business days triggers flag
- **Intraday Data**: Gap >1 hour (during market hours) triggers flag
- **Holiday Calendar**: Use commodity-specific holiday calendar to exclude expected gaps

---

## 5. Cross-Source Consistency Rules

### 5.1 Price Consistency Tolerance

| **Comparison** | **Tolerance** | **Rationale** |
|----------------|---------------|---------------|
| EIA WTI vs FRED WTI | ±5% | Different data sources, timing differences |
| Yahoo Finance vs EIA/FRED | ±10% | Futures vs spot prices |
| Same commodity, same source | ±0.1% | Should be identical, small tolerance for rounding |

### 5.2 Consistency Check Rules

- **Same Date Comparison**: Compare prices for the same date across sources
- **Flag Discrepancies**: Flag if difference exceeds tolerance
- **Action**: Investigate and resolve discrepancies before using data

---

## 6. Schema Validation Rules

### 6.1 Required Columns

**For Price Data:**
- `timestamp` (datetime): Required
- `price` (float): Required
- `commodity` (string): Required
- `source` (string): Required

**Optional Columns:**
- `volume` (float): Optional
- `open` (float): Optional (for OHLCV data)
- `high` (float): Optional (for OHLCV data)
- `low` (float): Optional (for OHLCV data)
- `close` (float): Optional (for OHLCV data)

### 6.2 Data Type Rules

```python
EXPECTED_SCHEMA = {
    'timestamp': 'datetime64[ns]',
    'price': 'float64',
    'commodity': 'object',  # string
    'source': 'object',      # string
    'volume': 'float64',     # optional
    'open': 'float64',       # optional
    'high': 'float64',       # optional
    'low': 'float64',        # optional
    'close': 'float64',      # optional
}
```

---

## 7. Outlier Detection Rules

### 7.1 Z-Score Method

- **Threshold**: Z-score > 3.0 or < -3.0
- **Application**: Flag prices that are >3 standard deviations from mean
- **Window**: Use 30-day rolling window for calculation

### 7.2 IQR (Interquartile Range) Method

- **Threshold**: Q1 - 1.5*IQR or Q3 + 1.5*IQR
- **Application**: Flag prices outside IQR bounds
- **Window**: Use 30-day rolling window for calculation

### 7.3 Outlier Action Rules

- **Flag, Don't Remove**: Outliers are flagged but not automatically removed
- **Human Review**: Flagged outliers require human review before action
- **Document**: All outlier decisions should be logged

---

## 8. Data Quality Thresholds

### 8.1 Quality Scores

| **Score** | **Range** | **Action** |
|-----------|-----------|------------|
| **Excellent** | 95-100% | Use data as-is |
| **Good** | 85-94% | Use with minor cleanup |
| **Fair** | 70-84% | Use with caution, investigate issues |
| **Poor** | 50-69% | High risk, extensive cleanup needed |
| **Unusable** | <50% | Do not use, find alternative source |

### 8.2 Quality Calculation

```
Quality Score = (
    0.4 * Completeness Score +
    0.3 * Consistency Score +
    0.2 * Schema Compliance Score +
    0.1 * Outlier Score
)

Where:
- Completeness Score = (1 - missing_rate) * 100
- Consistency Score = (1 - cross_source_discrepancy_rate) * 100
- Schema Compliance Score = (1 - schema_violation_rate) * 100
- Outlier Score = (1 - outlier_rate) * 100
```

---

## 9. Validation Workflow

### 9.1 Validation Stages

1. **Stage 1: Schema Validation**
   - Check column names
   - Check data types
   - Check required fields

2. **Stage 2: Range Validation**
   - Check price ranges
   - Check volume ranges
   - Check timestamp ranges

3. **Stage 3: Completeness Validation**
   - Check for missing values
   - Check for data gaps
   - Calculate completeness score

4. **Stage 4: Outlier Detection**
   - Apply Z-score method
   - Apply IQR method
   - Flag outliers

5. **Stage 5: Cross-Source Validation** (if multiple sources available)
   - Compare prices across sources
   - Calculate discrepancies
   - Flag inconsistencies

6. **Stage 6: Quality Report Generation**
   - Calculate quality score
   - Generate validation report
   - Log results

### 9.2 Validation Actions

| **Validation Result** | **Action** |
|-----------------------|------------|
| **Pass All Checks** | Proceed with data ingestion |
| **Minor Issues (<5% data affected)** | Log warnings, proceed with caution |
| **Moderate Issues (5-15% data affected)** | Investigate, cleanup, re-validate |
| **Major Issues (>15% data affected)** | Block ingestion, escalate to data engineer |

---

## 10. Configuration

All validation rules are configurable via:

**File**: `src/energy-price-forecasting/data_validation/validation_config.yaml`

**Example Configuration**:

```yaml
price_ranges:
  WTI_CRUDE:
    min: 0.01
    max: 300.00
  NATURAL_GAS:
    min: 0.01
    max: 50.00

tolerances:
  cross_source_tolerance: 0.05  # 5%
  max_daily_change: 0.50        # 50%
  max_weekly_change: 0.70       # 70%

completeness:
  max_gap_days: 2
  min_data_points: 30
  max_missing_rate: 0.05  # 5%

outliers:
  z_score_threshold: 3.0
  iqr_multiplier: 1.5
  rolling_window_days: 30

quality_thresholds:
  excellent: 95
  good: 85
  fair: 70
  poor: 50
```

---

## 11. Error Codes

| **Code** | **Description** | **Severity** |
|----------|-----------------|--------------|
| `VAL-001` | Schema validation failed | ERROR |
| `VAL-002` | Price out of range | WARNING |
| `VAL-003` | Volume out of range | WARNING |
| `VAL-004` | Invalid timestamp | ERROR |
| `VAL-005` | Duplicate timestamp | ERROR |
| `VAL-006` | Missing required field | ERROR |
| `VAL-007` | Data gap detected | WARNING |
| `VAL-008` | Outlier detected (Z-score) | INFO |
| `VAL-009` | Outlier detected (IQR) | INFO |
| `VAL-010` | Cross-source discrepancy | WARNING |
| `VAL-011` | Low completeness score | ERROR |
| `VAL-012` | Low quality score | ERROR |

---

## 12. References

- **Industry Standards**: ISO 8601 (timestamps), IEEE 754 (floating point)
- **Statistical Methods**: Z-score, IQR for outlier detection
- **Data Quality Frameworks**: DAMA DMBOK, ISO 8000

---

**Version History**:

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Dec 14, 2025 | Initial validation rules defined | AI Assistant |

---

**Status**: ✅ Ready for Implementation

