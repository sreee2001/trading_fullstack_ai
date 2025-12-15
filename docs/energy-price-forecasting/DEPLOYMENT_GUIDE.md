# Energy Price Forecasting System - Deployment Guide

**Version**: 1.0  
**Last Updated**: December 15, 2025  
**Target Audience**: DevOps engineers, system administrators, developers

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [Environment Configuration](#environment-configuration)
5. [Staging Deployment](#staging-deployment)
6. [Production Deployment](#production-deployment)
7. [Cloud Deployment Options](#cloud-deployment-options)
8. [Database Setup and Migrations](#database-setup-and-migrations)
9. [Model Deployment](#model-deployment)
10. [Monitoring and Health Checks](#monitoring-and-health-checks)
11. [Rollback Procedures](#rollback-procedures)
12. [Troubleshooting](#troubleshooting)
13. [Security Best Practices](#security-best-practices)
14. [Scaling and Performance](#scaling-and-performance)

---

## Overview

This comprehensive guide covers deployment of the Energy Price Forecasting System across different environments:

- **Local Development**: Docker Compose setup for development
- **Staging**: Pre-production testing environment
- **Production**: Live production environment
- **Cloud Platforms**: AWS, Azure, GCP deployment options

### System Architecture

The system consists of:
- **FastAPI Backend**: REST API service (Port 8000)
- **React Frontend**: Web dashboard (Port 3000/80)
- **PostgreSQL + TimescaleDB**: Time-series database (Port 5432)
- **Redis**: Caching and rate limiting (Port 6379)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Docker** | 20.10+ | Container runtime |
| **Docker Compose** | 2.0+ | Multi-container orchestration |
| **Git** | Latest | Version control |
| **PostgreSQL Client** | 15+ | Database management (optional) |

### Required Access

- Docker registry access (if using remote images)
- Database and Redis instances (or Docker to run locally)
- API keys: EIA API, FRED API
- Environment variables configured

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB

**Recommended (Production)**:
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 50GB+ (SSD recommended)

---

## Local Development Setup

### Quick Start

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd trading_fullstack_ai/src/energy-price-forecasting
   ```

2. **Create Environment File**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start Services**:
   ```bash
   docker-compose up -d
   ```

4. **Verify Deployment**:
   ```bash
   # Check API
   curl http://localhost:8000/health
   
   # Check Frontend
   curl http://localhost:3000
   
   # Check Database
   docker exec -it energy_forecasting_db psql -U energy_user -d energy_forecasting -c "SELECT version();"
   ```

### Development Workflow

**Start Services**:
```bash
docker-compose up -d
```

**View Logs**:
```bash
docker-compose logs -f api
docker-compose logs -f frontend
```

**Stop Services**:
```bash
docker-compose down
```

**Rebuild After Code Changes**:
```bash
docker-compose up -d --build
```

**Access Services**:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Database: localhost:5432

---

## Environment Configuration

### Environment Variables

Create a `.env` file in `src/energy-price-forecasting/` with the following variables:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_forecasting
DB_USER=energy_user
DB_PASSWORD=energy_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys (Required)
EIA_API_KEY=your_eia_api_key_here
FRED_API_KEY=your_fred_api_key_here

# API Settings
API_ENV=development  # or staging, production
API_DEBUG=true
SECRET_KEY=your-secret-key-here

# MLflow (Optional)
MLFLOW_TRACKING_URI=http://localhost:5000

# Email Notifications (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Slack Notifications (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Environment-Specific Configurations

**Development**:
- `API_DEBUG=true`
- `API_ENV=development`
- Local database and Redis
- Detailed logging

**Staging**:
- `API_DEBUG=false`
- `API_ENV=staging`
- Separate staging database
- Production-like settings

**Production**:
- `API_DEBUG=false`
- `API_ENV=production`
- Production database with backups
- Optimized settings
- SSL/TLS enabled

---

## Staging Deployment

**Purpose**: Pre-production testing environment

**Configuration**:
- Environment: `staging`
- Database: Separate staging database instance
- Redis: Separate staging Redis instance
- URL: `https://staging.energy-forecasting.example.com`

**Setup Steps**:

1. **Provision Infrastructure**:
   ```bash
   # Option 1: Use Docker Compose (recommended for staging)
   docker-compose -f docker-compose.staging.yml up -d
   
   # Option 2: Use managed services
   # - Create PostgreSQL instance (AWS RDS, Azure Database, etc.)
   # - Create Redis instance (AWS ElastiCache, Azure Cache, etc.)
   # - Configure networking and security groups
   ```

2. **Configure Environment Variables**:
   ```bash
   # Create staging .env file
   cat > .env.staging << EOF
   DB_HOST=staging-db.example.com
   DB_PORT=5432
   DB_NAME=energy_forecasting_staging
   DB_USER=energy_user
   DB_PASSWORD=<staging_password>
   REDIS_HOST=staging-redis.example.com
   REDIS_PORT=6379
   API_ENV=staging
   API_DEBUG=false
   EIA_API_KEY=<your_eia_key>
   FRED_API_KEY=<your_fred_key>
   EOF
   ```

3. **Run Database Migrations**:
   ```bash
   # Connect to staging database
   docker exec -it energy_forecasting_api python -m database.migrations.run
   ```

4. **Deploy Services**:
   ```bash
   # Using deployment script
   ./scripts/deploy-staging.sh
   
   # Or manually
   docker-compose -f docker-compose.staging.yml up -d
   ```

5. **Verify Deployment**:
   ```bash
   # Health checks
   curl https://staging.energy-forecasting.example.com/health
   curl https://staging.energy-forecasting.example.com/ready
   
   # Check logs
   docker-compose logs -f
   ```

### Production Environment

**Purpose**: Live production environment

**Configuration**:
- Environment: `production`
- Database: Production database instance (with backups)
- Redis: Production Redis instance (with persistence)
- URL: `https://energy-forecasting.example.com`

**Setup Steps**:

1. **Pre-Deployment Checklist**:
   - [ ] All tests passing
   - [ ] Code reviewed and approved
   - [ ] Database backup created
   - [ ] Rollback plan prepared
   - [ ] Monitoring configured
   - [ ] Alerts configured

2. **Provision Infrastructure**:
   ```bash
   # Production-grade infrastructure:
   # - Managed PostgreSQL with automated backups
   # - Managed Redis with persistence
   # - Load balancer (AWS ALB, Azure LB, etc.)
   # - SSL/TLS certificates (Let's Encrypt, AWS ACM)
   # - CDN for frontend (CloudFront, Cloudflare)
   # - Monitoring (CloudWatch, Datadog, etc.)
   ```

3. **Configure Environment Variables**:
   ```bash
   # Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
   # Never store in plain text
   
   # Production .env (use secrets management)
   DB_HOST=prod-db.example.com
   DB_PORT=5432
   DB_NAME=energy_forecasting_prod
   DB_USER=energy_user
   DB_PASSWORD=<secure_password_from_secrets>
   REDIS_HOST=prod-redis.example.com
   REDIS_PORT=6379
   API_ENV=production
   API_DEBUG=false
   SECRET_KEY=<strong_secret_key>
   EIA_API_KEY=<from_secrets>
   FRED_API_KEY=<from_secrets>
   ```

4. **Run Database Migrations**:
   ```bash
   # Backup first!
   pg_dump -h prod-db.example.com -U energy_user -d energy_forecasting_prod > backup_$(date +%Y%m%d_%H%M%S).sql
   
   # Run migrations
   docker exec -it energy_forecasting_api python -m database.migrations.run
   ```

5. **Deploy Services**:
   ```bash
   # Requires explicit confirmation
   export DEPLOY_CONFIRM=yes
   ./scripts/deploy-production.sh
   ```

6. **Post-Deployment Verification**:
   ```bash
   # Health checks
   curl https://energy-forecasting.example.com/health
   curl https://energy-forecasting.example.com/ready
   
   # Smoke tests
   curl -X POST https://energy-forecasting.example.com/api/v1/forecast \
     -H "X-API-Key: <test_key>" \
     -H "Content-Type: application/json" \
     -d '{"commodity": "WTI", "horizon": 1, "start_date": "2025-12-15"}'
   
   # Monitor logs
   docker-compose logs -f api
   ```

## Deployment Methods

### Method 1: Using Deployment Scripts

**Staging**:
```bash
cd src/energy-price-forecasting
./scripts/deploy-staging.sh
```

**Production**:
```bash
cd src/energy-price-forecasting
export DEPLOY_CONFIRM=yes
./scripts/deploy-production.sh
```

### Method 2: Using Docker Compose Directly

```bash
# Set environment
export ENVIRONMENT=staging  # or production

# Deploy
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Method 3: Using GitHub Actions

**Staging**: Automatically deploys on push to `develop` branch

**Production**: Requires manual approval, deploys on push to `main` branch

## Deployment Process

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] Docker images built and pushed
- [ ] Backup of current deployment (production only)

### Deployment Steps

1. **Pull Latest Images**:
   ```bash
   docker pull <registry>/energy-forecasting-api:<tag>
   docker pull <registry>/energy-forecasting-frontend:<tag>
   ```

2. **Stop Existing Services**:
   ```bash
   docker-compose down
   ```

3. **Start New Services**:
   ```bash
   docker-compose up -d
   ```

4. **Run Health Checks**:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:80
   ```

5. **Verify Deployment**:
   - Check API endpoints
   - Check frontend accessibility
   - Monitor logs for errors
   - Verify database connectivity

### Post-Deployment Verification

- [ ] API health endpoint responding
- [ ] Frontend accessible
- [ ] Database connections working
- [ ] Redis connections working
- [ ] Model loading successful
- [ ] Forecast endpoint functional
- [ ] No errors in logs

## Rollback Procedure

If deployment fails or issues are detected:

1. **Stop New Services**:
   ```bash
   docker-compose down
   ```

2. **Revert to Previous Version**:
   ```bash
   export IMAGE_TAG=<previous_tag>
   docker-compose up -d
   ```

3. **Verify Rollback**:
   ```bash
   curl http://localhost:8000/health
   ```

## Monitoring

### Health Checks

**API Health**:
```bash
curl http://localhost:8000/health
```

**Frontend Health**:
```bash
curl http://localhost:80
```

### Logs

**View All Logs**:
```bash
docker-compose logs -f
```

**View API Logs**:
```bash
docker-compose logs -f api
```

**View Frontend Logs**:
```bash
docker-compose logs -f frontend
```

## Troubleshooting

### Common Issues

1. **Services Not Starting**:
   - Check Docker daemon: `docker ps`
   - Check logs: `docker-compose logs`
   - Verify environment variables

2. **Database Connection Errors**:
   - Verify database is accessible
   - Check credentials
   - Verify network connectivity

3. **Port Conflicts**:
   - Check if ports are already in use: `netstat -tulpn | grep <port>`
   - Modify `docker-compose.yml` to use different ports

4. **Image Pull Errors**:
   - Verify Docker registry credentials
   - Check network connectivity
   - Try pulling manually: `docker pull <image>`

## Security Considerations

### Production Deployment

- Use strong passwords for database and Redis
- Enable SSL/TLS for all connections
- Restrict network access (firewall rules)
- Regular security updates
- Monitor for security vulnerabilities
- Use secrets management (e.g., Docker secrets, Kubernetes secrets)

### Environment Variables

Never commit sensitive data:
- Database passwords
- API keys
- Secret keys
- Private keys

Use environment variables or secrets management systems.

## Continuous Deployment

### GitHub Actions Workflows

- **Staging**: Auto-deploys on `develop` branch
- **Production**: Requires approval, deploys on `main` branch

### Manual Deployment

Use deployment scripts for manual deployments:
```bash
./scripts/deploy-staging.sh
./scripts/deploy-production.sh
```

## Backup and Recovery

### Database Backups

**Before Production Deployment**:
```bash
pg_dump -h <db_host> -U <user> -d <database> > backup_$(date +%Y%m%d).sql
```

**Restore**:
```bash
psql -h <db_host> -U <user> -d <database> < backup_YYYYMMDD.sql
```

### Configuration Backups

Save current `docker-compose.yml` and environment variables before deployment.

---

## Cloud Deployment Options

### AWS Deployment

**Services Used**:
- **EC2/ECS/EKS**: Container hosting
- **RDS PostgreSQL**: Managed database
- **ElastiCache Redis**: Managed Redis
- **ALB**: Load balancer
- **CloudWatch**: Monitoring
- **S3**: Model storage

**Deployment Steps**:
```bash
# 1. Build and push images to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker build -t energy-forecasting-api -f api/Dockerfile .
docker tag energy-forecasting-api:latest <account>.dkr.ecr.<region>.amazonaws.com/energy-forecasting-api:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/energy-forecasting-api:latest

# 2. Deploy using ECS/EKS
# (Use AWS Console or Terraform/CloudFormation)
```

### Azure Deployment

**Services Used**:
- **Azure Container Instances / AKS**: Container hosting
- **Azure Database for PostgreSQL**: Managed database
- **Azure Cache for Redis**: Managed Redis
- **Azure Load Balancer**: Load balancing
- **Application Insights**: Monitoring

**Deployment Steps**:
```bash
# 1. Build and push to Azure Container Registry
az acr build --registry <registry-name> --image energy-forecasting-api:latest .

# 2. Deploy using ACI or AKS
az container create --resource-group <rg> --name energy-api --image <registry>/energy-forecasting-api:latest
```

### GCP Deployment

**Services Used**:
- **Cloud Run / GKE**: Container hosting
- **Cloud SQL PostgreSQL**: Managed database
- **Memorystore Redis**: Managed Redis
- **Cloud Load Balancing**: Load balancing
- **Cloud Monitoring**: Monitoring

**Deployment Steps**:
```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/<project>/energy-forecasting-api

# 2. Deploy to Cloud Run
gcloud run deploy energy-api --image gcr.io/<project>/energy-forecasting-api --platform managed
```

---

## Database Setup and Migrations

### Initial Database Setup

1. **Create Database**:
   ```sql
   CREATE DATABASE energy_forecasting;
   ```

2. **Enable TimescaleDB Extension**:
   ```sql
   \c energy_forecasting
   CREATE EXTENSION IF NOT EXISTS timescaledb;
   ```

3. **Run Initial Schema**:
   ```bash
   psql -h <host> -U <user> -d energy_forecasting -f database/init.sql
   ```

### Running Migrations

**Using Python**:
```bash
python -m database.migrations.run
```

**Using Docker**:
```bash
docker exec -it energy_forecasting_api python -m database.migrations.run
```

**Manual Migration**:
```bash
psql -h <host> -U <user> -d energy_forecasting -f database/migrations/001_migration.sql
```

### Database Backups

**Automated Backup** (Production):
```bash
# Daily backup script
pg_dump -h <host> -U <user> -d energy_forecasting -F c -f backup_$(date +%Y%m%d).dump

# Restore
pg_restore -h <host> -U <user> -d energy_forecasting backup_YYYYMMDD.dump
```

---

## Model Deployment

### Deploying Trained Models

1. **Train Models**:
   ```bash
   python -m training.train_all_models
   ```

2. **Register in MLflow**:
   ```bash
   # Models automatically registered during training
   # Check MLflow UI: http://localhost:5000
   ```

3. **Load Models in API**:
   ```python
   # Models loaded automatically on API startup
   # Check /api/v1/models endpoint for available models
   ```

### Model Versioning

- Models versioned in MLflow Model Registry
- Production models tagged with `Production` stage
- Rollback via MLflow UI or API

---

## Monitoring and Health Checks

### Health Check Endpoints

**API Health**:
```bash
curl http://localhost:8000/health
# Returns: {"status": "healthy"}
```

**Readiness Check**:
```bash
curl http://localhost:8000/ready
# Returns: {"status": "ready", "components": {...}}
```

**Metrics Endpoint** (if enabled):
```bash
curl http://localhost:8000/metrics
# Prometheus format metrics
```

### Logging

**View Logs**:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f timescaledb
```

**Log Locations**:
- API: `logs/api.log`
- Pipeline: `logs/pipeline.log`
- Scheduler: `logs/scheduler.log`

### Monitoring Setup

**Key Metrics to Monitor**:
- API response times
- Request rates
- Error rates
- Database connection pool
- Redis cache hit rate
- Model prediction latency
- System resources (CPU, memory, disk)

---

## Rollback Procedures

### Application Rollback

1. **Stop Current Services**:
   ```bash
   docker-compose down
   ```

2. **Revert to Previous Image**:
   ```bash
   export IMAGE_TAG=<previous_tag>
   docker-compose up -d
   ```

3. **Verify Rollback**:
   ```bash
   curl http://localhost:8000/health
   ```

### Database Rollback

1. **Restore Database Backup**:
   ```bash
   pg_restore -h <host> -U <user> -d energy_forecasting backup_YYYYMMDD.dump
   ```

2. **Revert Migrations** (if needed):
   ```bash
   psql -h <host> -U <user> -d energy_forecasting -f database/migrations/rollback/001_rollback.sql
   ```

### Model Rollback

1. **Via MLflow UI**:
   - Navigate to Model Registry
   - Demote current production model
   - Promote previous version

2. **Via API**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/admin/rollback \
     -H "X-API-Key: <admin_key>" \
     -d '{"commodity": "WTI", "version": "previous"}'
   ```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Services Not Starting

**Symptoms**: Containers exit immediately

**Solutions**:
```bash
# Check logs
docker-compose logs api

# Check Docker daemon
docker ps

# Verify environment variables
docker-compose config

# Check port conflicts
netstat -tulpn | grep 8000
```

#### 2. Database Connection Errors

**Symptoms**: `Connection refused` or `Authentication failed`

**Solutions**:
```bash
# Verify database is running
docker ps | grep timescaledb

# Test connection
docker exec -it energy_forecasting_db psql -U energy_user -d energy_forecasting

# Check credentials in .env
cat .env | grep DB_

# Verify network connectivity
docker network inspect energy_forecasting_network
```

#### 3. Redis Connection Errors

**Symptoms**: `Connection refused` or cache not working

**Solutions**:
```bash
# Verify Redis is running
docker ps | grep redis

# Test connection
docker exec -it energy_forecasting_redis redis-cli ping

# Check Redis logs
docker-compose logs redis
```

#### 4. API Not Responding

**Symptoms**: 502 Bad Gateway or connection timeout

**Solutions**:
```bash
# Check API container
docker ps | grep api

# Check API logs
docker-compose logs api

# Test health endpoint
curl -v http://localhost:8000/health

# Check if port is accessible
telnet localhost 8000
```

#### 5. Frontend Not Loading

**Symptoms**: Blank page or 404 errors

**Solutions**:
```bash
# Check frontend container
docker ps | grep frontend

# Check frontend logs
docker-compose logs frontend

# Verify API URL in frontend config
docker exec -it energy_forecasting_frontend cat /usr/share/nginx/html/config.js

# Check browser console for errors
```

#### 6. Model Loading Failures

**Symptoms**: 500 errors on forecast endpoint

**Solutions**:
```bash
# Check model files exist
ls -la models/

# Check MLflow connection
curl http://localhost:5000

# Verify model registry
# Access MLflow UI: http://localhost:5000
```

#### 7. High Memory Usage

**Symptoms**: Containers being killed (OOM)

**Solutions**:
```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
# Add to service:
deploy:
  resources:
    limits:
      memory: 4G
```

#### 8. Slow Performance

**Symptoms**: Slow API responses

**Solutions**:
```bash
# Check database query performance
docker exec -it energy_forecasting_db psql -U energy_user -d energy_forecasting -c "EXPLAIN ANALYZE SELECT ..."

# Check Redis cache hit rate
docker exec -it energy_forecasting_redis redis-cli INFO stats

# Monitor API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
```

---

## Security Best Practices

### Production Security Checklist

- [ ] Use strong, unique passwords for all services
- [ ] Enable SSL/TLS for all connections
- [ ] Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
- [ ] Restrict network access (firewall rules, security groups)
- [ ] Enable database encryption at rest
- [ ] Enable Redis persistence with encryption
- [ ] Regular security updates
- [ ] Monitor for security vulnerabilities
- [ ] Use API key authentication
- [ ] Implement rate limiting
- [ ] Enable CORS restrictions
- [ ] Use HTTPS only in production
- [ ] Regular security audits
- [ ] Backup encryption

### Environment Variables Security

**Never commit**:
- Database passwords
- API keys
- Secret keys
- Private keys
- JWT secrets

**Use**:
- Environment variables
- Secrets management systems
- Encrypted configuration files

---

## Scaling and Performance

### Horizontal Scaling

**API Scaling**:
```bash
# Scale API instances
docker-compose up -d --scale api=3

# Use load balancer for multiple instances
```

**Database Scaling**:
- Use read replicas for read-heavy workloads
- Consider connection pooling (PgBouncer)

**Redis Scaling**:
- Use Redis Cluster for high availability
- Consider Redis Sentinel for failover

### Performance Tuning

**Database**:
- Enable query caching
- Optimize indexes
- Use connection pooling
- Monitor slow queries

**API**:
- Enable response caching
- Use async processing for long operations
- Optimize model loading
- Monitor response times

**Frontend**:
- Enable CDN
- Use browser caching
- Optimize bundle size
- Lazy load components

---

## Support

For deployment issues:

1. **Check Logs**: `docker-compose logs`
2. **Review This Guide**: Check troubleshooting section
3. **Check Documentation**: [README.md](../README.md)
4. **GitHub Issues**: Report issues on GitHub
5. **Contact**: DevOps team or project maintainers

---

**Last Updated**: December 15, 2025  
**Version**: 1.0  
**Status**: Complete

