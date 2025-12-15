# Energy Price Forecasting Dashboard

React + TypeScript dashboard for the Energy Price Forecasting System.

## Features

- **Forecast**: Generate and view price forecasts for energy commodities
- **Models**: Explore ML model performance and metadata
- **Backtest**: Run backtests on forecasting models

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API configuration
```

3. Start development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Project Structure

```
src/
├── components/       # Reusable components
│   └── Layout.tsx   # Main layout with navigation
├── context/         # React Context for state management
│   └── AppContext.tsx
├── lib/             # Utility libraries
│   └── apiClient.ts # Axios API client configuration
├── pages/           # Page components
│   ├── Home.tsx
│   ├── Forecast.tsx
│   ├── Models.tsx
│   └── Backtest.tsx
├── App.tsx          # Main app component with routing
└── main.tsx         # Entry point
```

## Technologies

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Routing
- **Axios** - HTTP client
- **Context API** - State management

## API Integration

The dashboard communicates with the FastAPI backend at `http://localhost:8000` by default.

API endpoints:
- `POST /api/v1/forecast` - Generate forecasts
- `GET /api/v1/historical` - Get historical data
- `GET /api/v1/models` - Get model information
- `POST /api/v1/backtest` - Run backtests

## Development

- Development server: `http://localhost:5173` (Vite default)
- Hot module replacement (HMR) enabled
- TypeScript strict mode enabled

## License

MIT
