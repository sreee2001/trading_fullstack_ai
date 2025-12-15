# Dashboard Module

**Purpose**: React-based web dashboard for energy price forecasting visualization

---

## Overview

The dashboard module provides a modern, responsive web interface built with React and TypeScript. It includes interactive charts, real-time updates via WebSocket, and comprehensive visualization of forecasts, models, backtests, and historical data.

---

## File Structure

```
dashboard/
├── src/
│   ├── components/          # React components
│   │   ├── Forecast/
│   │   ├── Models/
│   │   ├── Backtest/
│   │   ├── Historical/
│   │   └── common/
│   ├── hooks/               # Custom React hooks
│   │   └── useWebSocket.ts  # WebSocket hook
│   ├── context/             # React context
│   │   └── AppContext.tsx   # Application state
│   ├── services/            # API services
│   │   └── api.ts           # API client
│   ├── types/               # TypeScript types
│   │   └── api.ts           # API type definitions
│   ├── utils/               # Utility functions
│   └── App.tsx              # Main application component
├── public/                  # Static assets
├── package.json             # Dependencies
├── vite.config.ts           # Vite configuration
└── Dockerfile               # Container definition
```

---

## Key Components

### Forecast Component

**Location**: `src/components/Forecast/`

**Purpose**: Generate and display price forecasts

**Features**:
- Commodity selection (WTI, BRENT, NG)
- Horizon selection (1-30 days)
- Date picker
- Interactive forecast chart with confidence intervals
- Prediction table
- Historical comparison

**Usage**:
```tsx
import ForecastPage from './components/Forecast/ForecastPage';

<ForecastPage />
```

---

### Models Component

**Location**: `src/components/Models/`

**Purpose**: Display and compare ML models

**Features**:
- Model list with metadata
- Performance metrics comparison
- Filter by commodity
- Model details view

---

### Backtest Component

**Location**: `src/components/Backtest/`

**Purpose**: Run and visualize backtests

**Features**:
- Model selection
- Strategy configuration
- Parameter inputs
- Equity curve visualization
- Trade history table
- Performance metrics display

---

### Historical Component

**Location**: `src/components/Historical/`

**Purpose**: Explore historical price data

**Features**:
- Date range selection
- Commodity filtering
- Interactive price charts
- Statistical analysis
- Data export

---

## Custom Hooks

### useWebSocket Hook

**Location**: `src/hooks/useWebSocket.ts`

**Purpose**: WebSocket connection management

**Usage**:
```typescript
import useWebSocket from './hooks/useWebSocket';

const { isConnected, lastMessage, error } = useWebSocket(
  'ws://localhost:8000/api/v1/ws/forecast/WTI/7',
  apiKey
);
```

**Features**:
- Automatic reconnection
- Connection state management
- Error handling
- Message parsing

---

## API Integration

### API Client

**Location**: `src/services/api.ts`

**Purpose**: REST API client

**Key Methods**:
- `getForecast(commodity, horizon, startDate)`: Get forecast
- `getHistoricalData(commodity, startDate, endDate)`: Get historical data
- `getModels(commodity)`: Get models
- `runBacktest(params)`: Run backtest

**Usage**:
```typescript
import { api } from './services/api';

const forecast = await api.getForecast('WTI', 7, '2025-12-15');
```

---

## State Management

### App Context

**Location**: `src/context/AppContext.tsx`

**Purpose**: Global application state

**State**:
- API key
- User preferences
- Current selections
- Error state

**Usage**:
```typescript
import { useApp } from './context/AppContext';

const { state, dispatch } = useApp();
```

---

## Charting

**Libraries**:
- **Recharts**: Primary charting library
- **Plotly**: Advanced visualizations (optional)

**Chart Types**:
- Line charts (forecasts, historical)
- Area charts (confidence intervals)
- Bar charts (metrics)
- Scatter plots (correlations)

---

## Styling

**Approach**: CSS Modules

**Structure**:
- Component-specific styles
- Shared styles in `common/`
- Responsive design
- Dark mode support

---

## Testing

**Test Files**:
- `src/components/**/*.test.tsx`
- `src/hooks/**/*.test.ts`
- `src/services/**/*.test.ts`

**Run Tests**:
```bash
npm test
```

---

## Dependencies

- **React 18+**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Recharts**: Charting library
- **Axios**: HTTP client
- **React Router**: Routing

---

## Development

### Setup

```bash
cd dashboard
npm install
npm run dev
```

### Build

```bash
npm run build
```

### Docker

```bash
docker build -t energy-forecasting-dashboard -f dashboard/Dockerfile .
```

---

## Integration

The dashboard integrates with:
- **FastAPI Backend**: REST API endpoints
- **WebSocket**: Real-time updates
- **MLflow**: Model metadata (via API)

---

## Best Practices

1. **Component Composition**: Break down into smaller components
2. **Type Safety**: Use TypeScript types
3. **Error Handling**: Handle API errors gracefully
4. **Loading States**: Show loading indicators
5. **Responsive Design**: Mobile-friendly layouts

---

## Extending

To add new features:

1. Create component in `src/components/`
2. Add route in `App.tsx`
3. Add API method in `services/api.ts`
4. Add types in `types/api.ts`
5. Add tests
6. Update documentation

---

**Last Updated**: December 15, 2025

