# API Key Setup Guide

## Overview

The Energy Price Forecasting Dashboard requires an API key to authenticate with the backend API. This is **different** from the EIA and FRED API keys used by the backend for data ingestion.

## Two Types of API Keys

### 1. Backend API Keys (EIA/FRED) - For Data Ingestion
- **Location**: `src/energy-price-forecasting/.env`
- **Purpose**: Used by the backend to fetch data from external APIs
- **Keys**: `EIA_API_KEY` and `FRED_API_KEY`
- **Not used by the frontend**

### 2. Frontend API Key - For Dashboard Authentication
- **Location**: `src/energy-price-forecasting/dashboard/.env` (or enter manually in UI)
- **Purpose**: Used by the frontend to authenticate API requests
- **Key**: `VITE_API_KEY`
- **Format**: `epf_<random_string>` (e.g., `epf_a1b2c3d4e5f6...`)

## How to Get an API Key

### Option 1: Create via API (Recommended)

1. **Start the backend server** (if not already running):
   ```bash
   cd src/energy-price-forecasting
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Use Swagger UI** (Easiest):
   - Open http://localhost:8000/api/docs in your browser
   - Navigate to the `Admin` section
   - Find `POST /api/v1/admin/keys`
   - Click "Try it out"
   - Optionally fill in:
     - `user_id`: Your user identifier (optional)
     - `name`: Description for the key (optional)
     - `expires_in_days`: Expiration in days (optional, leave empty for no expiration)
   - Click "Execute"
   - **Copy the `api_key` value** - this is shown only once!

3. **Or use curl**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/admin/keys" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "your_user_id", "name": "Dashboard Key"}'
   ```

### Option 2: Enter Manually in UI

1. Open the dashboard at http://localhost:5173
2. Click "Enter API Key" button in the header
3. Paste your API key (format: `epf_...`)
4. Click "Save"

## Setting Up Environment Variable

### For Development

1. **Create `.env` file** in `src/energy-price-forecasting/dashboard/`:
   ```bash
   cd src/energy-price-forecasting/dashboard
   cp .env.example .env
   ```

2. **Edit `.env` file**:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   VITE_API_KEY=epf_your_actual_api_key_here
   ```

3. **Restart the development server**:
   ```bash
   npm run dev
   ```

### File Locations

```
trading_fullstack_ai/
├── src/
│   └── energy-price-forecasting/
│       ├── .env                    # Backend: EIA_API_KEY, FRED_API_KEY
│       └── dashboard/
│           └── .env                 # Frontend: VITE_API_KEY, VITE_API_BASE_URL
```

## Example .env Files

### Backend `.env` (src/energy-price-forecasting/.env)
```env
# API Keys for Data Ingestion
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

### Frontend `.env` (src/energy-price-forecasting/dashboard/.env)
```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=epf_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

## Troubleshooting

### "Please configure your API key" Message

This message appears when:
- No API key is set in environment variables (`VITE_API_KEY`)
- No API key is stored in browser localStorage
- The API key is invalid or expired

**Solutions**:
1. Set `VITE_API_KEY` in `dashboard/.env` and restart the dev server
2. Or click "Enter API Key" in the UI header and enter it manually
3. Verify the API key is valid by checking the backend logs

### API Key Not Working

1. **Check the key format**: Should start with `epf_`
2. **Verify backend is running**: http://localhost:8000/health
3. **Check key is active**: Use Swagger UI to list keys at `/api/v1/admin/keys`
4. **Check expiration**: Keys may have expired if `expires_in_days` was set

### Environment Variable Not Loading

- **Vite requires restart**: After changing `.env`, restart `npm run dev`
- **Check file location**: `.env` must be in `dashboard/` directory
- **Check variable name**: Must be `VITE_API_KEY` (Vite requires `VITE_` prefix)

## Security Notes

- **Never commit `.env` files** to version control
- **API keys are sensitive**: Store them securely
- **Keys shown once**: If you lose a key, create a new one
- **Revoke unused keys**: Use `/api/v1/admin/keys/{key_id}` DELETE endpoint

## Additional Resources

- **API Documentation**: http://localhost:8000/api/docs
- **Backend README**: `src/energy-price-forecasting/api/README.md`
- **Dashboard README**: `src/energy-price-forecasting/dashboard/README.md`

