# Data Pipeline Workflow

**Version**: 1.0  
**Date**: December 15, 2025  
**Status**: ✅ Complete

---

## Data Pipeline Workflow Diagram

```mermaid
flowchart TD
    START([Scheduler Trigger<br/>Daily 6:00 AM EST]) --> INIT[Initialize Pipeline]
    INIT --> PARALLEL{Parallel Fetch}
    
    PARALLEL --> EIA_FETCH[Fetch EIA Data]
    PARALLEL --> FRED_FETCH[Fetch FRED Data]
    PARALLEL --> YAHOO_FETCH[Fetch Yahoo Finance Data]
    
    EIA_FETCH --> EIA_RETRY{Success?}
    EIA_RETRY -->|No| EIA_BACKOFF[Exponential Backoff]
    EIA_BACKOFF --> EIA_FETCH
    EIA_RETRY -->|Yes| EIA_DATA[EIA Data]
    
    FRED_FETCH --> FRED_RETRY{Success?}
    FRED_RETRY -->|No| FRED_BACKOFF[Exponential Backoff]
    FRED_BACKOFF --> FRED_FETCH
    FRED_RETRY -->|Yes| FRED_DATA[FRED Data]
    
    YAHOO_FETCH --> YAHOO_RETRY{Success?}
    YAHOO_RETRY -->|No| YAHOO_BACKOFF[Exponential Backoff]
    YAHOO_BACKOFF --> YAHOO_FETCH
    YAHOO_RETRY -->|Yes| YAHOO_DATA[Yahoo Data]
    
    EIA_DATA --> VALIDATE[Data Validation]
    FRED_DATA --> VALIDATE
    YAHOO_DATA --> VALIDATE
    
    VALIDATE --> SCHEMA{Schema Valid?}
    SCHEMA -->|No| SCHEMA_ERROR[Log Schema Error]
    SCHEMA -->|Yes| OUTLIER{Outliers?}
    
    OUTLIER -->|Yes| OUTLIER_FLAG[Flag Outliers]
    OUTLIER -->|No| COMPLETE{Complete?}
    OUTLIER_FLAG --> COMPLETE
    
    COMPLETE -->|No| MISSING[Log Missing Data]
    COMPLETE -->|Yes| QUALITY[Calculate Quality Score]
    
    QUALITY --> QUALITY_CHECK{Quality >= 98%?}
    QUALITY_CHECK -->|No| QUALITY_FAIL[Log Quality Failure]
    QUALITY_CHECK -->|Yes| STORE[Store in Database]
    
    STORE --> UPSERT[Upsert to TimescaleDB]
    UPSERT --> SUCCESS{All Sources Success?}
    
    SUCCESS -->|Yes| NOTIFY_SUCCESS[Send Success Notification]
    SUCCESS -->|Partial| NOTIFY_PARTIAL[Send Partial Success]
    SUCCESS -->|No| NOTIFY_FAIL[Send Failure Alert]
    
    SCHEMA_ERROR --> NOTIFY_FAIL
    MISSING --> NOTIFY_FAIL
    QUALITY_FAIL --> NOTIFY_FAIL
    
    NOTIFY_SUCCESS --> END([Pipeline Complete])
    NOTIFY_PARTIAL --> END
    NOTIFY_FAIL --> END
    
    style START fill:#e1f5ff
    style VALIDATE fill:#fff4e1
    style STORE fill:#fff4e1
    style NOTIFY_SUCCESS fill:#e8f5e9
    style NOTIFY_FAIL fill:#ffebee
```

---

## Data Validation Workflow

```mermaid
flowchart LR
    RAW[Raw Data] --> SCHEMA[Schema Validation]
    SCHEMA --> OUTLIER[Outlier Detection]
    OUTLIER --> COMPLETE[Completeness Check]
    COMPLETE --> CONSISTENCY[Consistency Check]
    CONSISTENCY --> QUALITY[Quality Score]
    QUALITY --> DECISION{Pass?}
    DECISION -->|Yes| STORE[Store Data]
    DECISION -->|No| REJECT[Reject & Alert]
    
    style RAW fill:#e1f5ff
    style QUALITY fill:#fff4e1
    style STORE fill:#e8f5e9
    style REJECT fill:#ffebee
```

---

## Pipeline Error Handling

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Fetching: Schedule Trigger
    Fetching --> Validating: Data Received
    Fetching --> Retrying: Network Error
    Retrying --> Fetching: Retry
    Retrying --> Failed: Max Retries
    Validating --> Storing: Validation Pass
    Validating --> Failed: Validation Fail
    Storing --> Success: Store Complete
    Storing --> Failed: Store Error
    Success --> Idle
    Failed --> Alerting
    Alerting --> Idle
```

---

**Last Updated**: December 15, 2025

