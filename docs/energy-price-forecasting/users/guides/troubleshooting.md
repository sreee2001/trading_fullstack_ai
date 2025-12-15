# Troubleshooting Guide

**Time to Read**: 2 minutes

---

## Common Issues & Solutions

### System Won't Start

**Problem**: Docker containers fail to start

**Solutions**:
```bash
# Check Docker Desktop is running
docker ps

# View logs
docker compose logs

# Restart services
docker compose restart

# Rebuild if needed
docker compose up -d --build
```

---

### API Not Responding

**Problem**: API returns errors or timeouts

**Solutions**:
```bash
# Check API health
curl http://localhost:8000/health

# View API logs
docker logs energy_forecasting_api

# Check database connection
docker logs energy_forecasting_db

# Restart API
docker restart energy_forecasting_api
```

---

### Database Connection Errors

**Problem**: "Connection refused" or "Connection timeout"

**Solutions**:
```bash
# Check database is running
docker ps | grep timescaledb

# Check database health
docker exec energy_forecasting_db pg_isready

# Verify connection string
# Check DB_HOST, DB_PORT, DB_NAME in .env
```

---

### Dashboard Not Loading

**Problem**: Dashboard shows blank page or errors

**Solutions**:
- Clear browser cache
- Check browser console for errors
- Verify frontend container: `docker ps | grep frontend`
- Check API is accessible: http://localhost:8000/health
- Restart frontend: `docker restart energy_forecasting_frontend`

---

### "Model Not Found" Errors

**Problem**: Forecast requests return 404 Model Not Found

**Solutions**:
- Models need to be trained first
- Check available models: `GET /api/v1/models`
- Train models using training scripts
- See [Model Training Guide](../../developers/modules/models/README.md)

---

### Rate Limit Exceeded

**Problem**: 429 Too Many Requests errors

**Solutions**:
- Wait 60 seconds before retrying
- Implement exponential backoff
- Use WebSocket for real-time updates instead of polling
- Request higher rate limit (if available)

---

### Forecast Errors

**Problem**: Forecast generation fails

**Solutions**:
- Verify commodity is valid (WTI, BRENT, NG)
- Check horizon is 1-30 days
- Ensure start_date is valid format (YYYY-MM-DD)
- Check model is trained for that commodity
- View API logs for detailed error

---

### Backtest Errors

**Problem**: Backtest fails or returns errors

**Solutions**:
- Verify model_id exists
- Check date range is valid
- Ensure start_date < end_date
- Verify sufficient historical data exists
- Check strategy parameters are valid

---

### Data Quality Issues

**Problem**: Low data quality scores

**Solutions**:
- Check data source APIs are accessible
- Verify API keys are valid
- Check network connectivity
- Review validation logs
- Re-run data pipeline

---

### Port Already in Use

**Problem**: "Port already in use" errors

**Solutions**:
```bash
# Find process using port
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Kill process or change port in docker-compose.yml
```

---

### WebSocket Connection Fails

**Problem**: WebSocket won't connect

**Solutions**:
- Verify WebSocket endpoint: `ws://localhost:8000/api/v1/ws/forecast`
- Check API is running
- Verify WebSocket support in browser
- Check firewall settings
- Review WebSocket logs

---

## Getting Help

### Check Logs

```bash
# API logs
docker logs energy_forecasting_api

# Database logs
docker logs energy_forecasting_db

# Frontend logs
docker logs energy_forecasting_frontend

# All logs
docker compose logs
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
docker exec energy_forecasting_db pg_isready

# Redis health
docker exec energy_forecasting_redis redis-cli ping
```

### Verify Services

```bash
# List all containers
docker ps

# Check container status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Restart all services
docker compose restart
```

---

## Still Having Issues?

1. **Check Documentation**: See [Developer Documentation](../../developers/index.md)
2. **Review Logs**: Check container logs for errors
3. **Verify Configuration**: Check `.env` and `docker-compose.yml`
4. **Rebuild**: Try rebuilding containers: `docker compose up -d --build`

---

**Last Updated**: December 15, 2025

