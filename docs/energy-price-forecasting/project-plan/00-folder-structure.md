# Energy Price Forecasting System - Folder Structure

**Created**: December 14, 2025

---

## Project Organization

```
trading_fullstack_ai/
│
├── src/
│   └── energy-price-forecasting/          # Main project source code
│       ├── data-ingestion/                # Data collection and ETL pipeline
│       ├── models/                        # ML models (LSTM, ARIMA, etc.)
│       ├── api/                           # REST API service (FastAPI)
│       ├── backtesting/                   # Backtesting framework
│       ├── dashboard/                     # Frontend visualization (React)
│       ├── utils/                         # Shared utilities
│       ├── config/                        # Configuration files
│       └── tests/                         # Unit, integration tests
│
└── docs/
    └── energy-price-forecasting/          # Project documentation
        ├── project-plan/                  # Planning documents
        │   ├── 00-folder-structure.md     # This file
        │   ├── 01-high-level-features-proposal.md  # Feature proposals
        │   ├── 02-epic-breakdown.md       # (To be created)
        │   ├── 03-feature-breakdown.md    # (To be created)
        │   └── 04-tracker.md              # (To be created)
        │
        ├── architecture/                  # Architecture diagrams and docs
        │   └── (To be created after approval)
        │
        ├── design-decisions/              # ADRs and design rationale
        │   └── (To be created during implementation)
        │
        └── user-stories/                  # Detailed user stories
            └── (To be created after feature approval)
```

---

## Source Code Modules

### **data-ingestion/**
- API clients for EIA, FRED, Yahoo Finance
- Data validation and cleaning
- Database connectors
- ETL pipeline orchestration

### **models/**
- ARIMA/SARIMA statistical models
- LSTM neural network models
- Transformer models (stretch goal)
- Model training scripts
- Feature engineering
- Model registry integration

### **api/**
- FastAPI application
- Route handlers (forecast, historical, models, backtest)
- Request/response models (Pydantic)
- Authentication and rate limiting
- API documentation (Swagger)

### **backtesting/**
- Walk-forward validation
- Performance metrics calculation
- Trading signal generation
- P&L simulation
- Visualization utilities

### **dashboard/**
- React application
- TypeScript components
- Chart components (Chart.js/Plotly)
- API integration layer
- State management

### **utils/**
- Logging configuration
- Database utilities
- Date/time helpers
- Math/statistics utilities
- Data transformation helpers

### **config/**
- Environment configuration
- Model hyperparameters
- API keys management
- Database connection strings
- Feature flags

### **tests/**
- Unit tests (test_*.py)
- Integration tests
- Fixtures and test data
- Test configuration

---

## Documentation Structure

### **project-plan/**
High-level planning documents including:
- Feature proposals
- Epic and feature breakdowns
- Project tracker
- Timeline and milestones

### **architecture/**
Technical architecture documentation:
- System architecture diagrams
- Data flow diagrams
- Component interaction diagrams
- Technology stack details
- Scalability considerations

### **design-decisions/**
Architectural Decision Records (ADRs):
- Model selection rationale
- Technology choices
- Design pattern selections
- Trade-off analyses

### **user-stories/**
Detailed user stories for each feature:
- Acceptance criteria
- Technical requirements
- Dependencies
- Estimation

---

## File Naming Conventions

### Documentation Files
- `NN-descriptive-name.md` (where NN is sequence number)
- Example: `01-high-level-features-proposal.md`

### Source Code Files
- Python: `snake_case.py`
- TypeScript: `camelCase.ts` or `PascalCase.tsx` (for components)
- Tests: `test_module_name.py`

### Configuration Files
- `.env.example` - Example environment variables
- `config.yaml` - Application configuration
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies

---

## Current Status

✅ Folder structure created  
✅ High-level features proposal document created  
⏳ Awaiting approval on feature proposal  
⏳ Epic breakdown (next step)  
⏳ Feature breakdown (next step)  
⏳ User stories (next step)  

---

## Next Actions

1. **Review**: `01-high-level-features-proposal.md`
2. **Approval**: Provide feedback on proposed features
3. **Refinement**: Make any requested changes
4. **Proceed**: Move to Epic and Feature breakdown phase

