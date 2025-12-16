# Environment Variables Setup Guide

## Quick Reference

### Frontend Dashboard (`.env` file location)
**Path**: `src/energy-price-forecasting/dashboard/.env`

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=epf_your_api_key_here
```

### Backend API (`.env` file location)
**Path**: `src/energy-price-forecasting/.env`

```env
# External API Keys (for data ingestion)
EIA_API_KEY=your_eia_api_key_here
FRED_API_KEY=your_fred_api_key_here

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_forecasting
DB_USER=energy_user
DB_PASSWORD=energy_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## Detailed Explanation

### Frontend API Key (`VITE_API_KEY`)

**What it is**: Authentication key for the dashboard to communicate with the backend API.

**How to get it**:
1. Start the backend: `uvicorn api.main:app --reload`
2. Open http://localhost:8000/api/docs
3. Go to `Admin` → `POST /api/v1/admin/keys`
4. Click "Try it out" and "Execute"
5. Copy the `api_key` value (shown only once!)

**Alternative**: Enter it manually in the UI by clicking "Enter API Key" in the header.

### Backend API Keys (`EIA_API_KEY`, `FRED_API_KEY`)

**What they are**: Keys for external data sources (not for dashboard authentication).

**How to get them**:
- **EIA**: https://www.eia.gov/opendata/register.php (free)
- **FRED**: https://fred.stlouisfed.org/docs/api/api_key.html (free)

**Note**: These are only needed if you want to fetch real data. For UI testing, you can use placeholder values.

## File Structure

```
trading_fullstack_ai/
└── src/
    └── energy-price-forecasting/
        ├── .env                          ← Backend: EIA/FRED keys
        └── dashboard/
            └── .env                      ← Frontend: VITE_API_KEY
```

## Important Notes

1. **Never commit `.env` files** - They contain sensitive keys
2. **Restart required**: After changing `.env`, restart the dev server
3. **Vite prefix**: Frontend env vars must start with `VITE_`
4. **Two different keys**: 
   - `VITE_API_KEY` = Dashboard authentication
   - `EIA_API_KEY` / `FRED_API_KEY` = Data fetching

For more details, see [API_KEY_SETUP.md](./API_KEY_SETUP.md)

