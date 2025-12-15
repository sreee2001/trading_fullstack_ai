# Getting Started Guide

**Time to Read**: 5 minutes  
**Difficulty**: Beginner

---

## Overview

This guide will help you get the Energy Price Forecasting System up and running and generate your first forecast in under 10 minutes.

---

## Prerequisites

Before you begin, ensure you have:

- **Docker Desktop** installed and running
- **Git** installed
- **API Keys** (optional, for production use):
  - EIA API key (free from [eia.gov](https://www.eia.gov/opendata/))
  - FRED API key (free from [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html))

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/trading_fullstack_ai.git
cd trading_fullstack_ai/src/energy-price-forecasting
```

---

## Step 2: Start the System

The easiest way to run the system is using Docker Compose:

```bash
docker compose up -d
```

This starts:
- **PostgreSQL + TimescaleDB** (database) on port 5432
- **Redis** (caching) on port 6379
- **FastAPI** (backend API) on port 8000
- **React Dashboard** (frontend) on port 3000

**Wait 30-60 seconds** for all services to start.

---

## Step 3: Verify System is Running

### Check Services

```bash
docker ps
```

You should see 4 containers running:
- `energy_forecasting_db`
- `energy_forecasting_redis`
- `energy_forecasting_api`
- `energy_forecasting_frontend`

### Check API Health

Open your browser and visit:
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

You should see the Swagger UI and a health status response.

### Check Dashboard

Visit: http://localhost:3000

You should see the Energy Price Forecasting dashboard.

---

## Step 4: Generate Your First Forecast

### Option A: Using the Dashboard (Easiest)

1. Open http://localhost:3000
2. Navigate to **Forecast** page
3. Select:
   - **Commodity**: WTI
   - **Horizon**: 7 days
   - **Start Date**: Today
4. Click **Generate Forecast**
5. View the forecast chart and predictions!

### Option B: Using the API

```bash
curl -X POST "http://localhost:8000/api/v1/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "commodity": "WTI",
    "horizon": 7,
    "start_date": "2025-12-15"
  }'
```

You'll receive a JSON response with forecast predictions.

### Option C: Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/forecast",
    json={
        "commodity": "WTI",
        "horizon": 7,
        "start_date": "2025-12-15"
    }
)

forecast = response.json()
print(f"Forecast for {forecast['commodity']}:")
for pred in forecast['predictions']:
    print(f"  {pred['date']}: ${pred['price']:.2f}")
```

---

## Step 5: Explore the Dashboard

### Forecast Page
- Generate forecasts for different commodities
- View confidence intervals
- Compare with historical data

### Models Page
- View available ML models
- Compare model performance
- Filter by commodity

### Backtest Page
- Run backtests on historical data
- Test trading strategies
- View performance metrics

---

## What's Next?

Now that you have the system running:

1. **Learn More**: Read [Features Documentation](features/)
2. **Use the API**: See [API Usage Guide](guides/api-usage.md)
3. **Customize**: Configure API keys in `.env` file
4. **Deploy**: See [Deployment Guide](../../DEPLOYMENT_GUIDE.md)

---

## Troubleshooting

### Services Won't Start

```bash
# Check Docker Desktop is running
docker ps

# View logs
docker compose logs

# Restart services
docker compose restart
```

### API Not Responding

```bash
# Check API health
curl http://localhost:8000/health

# View API logs
docker logs energy_forecasting_api
```

### Dashboard Not Loading

- Clear browser cache
- Check browser console for errors
- Verify frontend container is running: `docker ps`

---

## Common Issues

**Problem**: "Connection refused" errors  
**Solution**: Ensure Docker Desktop is running and containers are healthy

**Problem**: "Model not found" errors  
**Solution**: Models need to be trained first. See [Model Training Guide](../../developers/modules/models/README.md)

**Problem**: Port already in use  
**Solution**: Change ports in `docker-compose.yml` or stop conflicting services

---

## Quick Reference

| Service | URL | Port |
|---------|-----|------|
| API | http://localhost:8000 | 8000 |
| API Docs | http://localhost:8000/api/docs | 8000 |
| Dashboard | http://localhost:3000 | 3000 |
| Database | localhost:5432 | 5432 |
| Redis | localhost:6379 | 6379 |

---

**Congratulations!** You've successfully set up and used the Energy Price Forecasting System. 🎉

---

**Last Updated**: December 15, 2025

