# Deployment Guide

## Overview

This guide covers deployment of the Energy Price Forecasting System to staging and production environments.

## Prerequisites

- Docker and Docker Compose installed
- Access to Docker registry (if using remote images)
- Environment variables configured
- Database and Redis instances available

## Environment Setup

### Staging Environment

**Purpose**: Pre-production testing environment

**Configuration**:
- Environment: `staging`
- Database: Separate staging database instance
- Redis: Separate staging Redis instance
- URL: `https://staging.energy-forecasting.example.com`

**Setup Steps**:

1. **Provision Infrastructure**:
   ```bash
   # Create staging database
   # Create staging Redis instance
   # Configure networking
   ```

2. **Configure Environment Variables**:
   ```bash
   export DB_HOST=staging-db.example.com
   export DB_PORT=5432
   export DB_NAME=energy_forecasting_staging
   export DB_USER=energy_user
   export DB_PASSWORD=<staging_password>
   export REDIS_HOST=staging-redis.example.com
   export REDIS_PORT=6379
   ```

3. **Deploy**:
   ```bash
   ./scripts/deploy-staging.sh
   ```

### Production Environment

**Purpose**: Live production environment

**Configuration**:
- Environment: `production`
- Database: Production database instance (with backups)
- Redis: Production Redis instance (with persistence)
- URL: `https://energy-forecasting.example.com`

**Setup Steps**:

1. **Provision Infrastructure**:
   ```bash
   # Create production database (with backups)
   # Create production Redis (with persistence)
   # Configure load balancer
   # Setup SSL certificates
   ```

2. **Configure Environment Variables**:
   ```bash
   export DB_HOST=prod-db.example.com
   export DB_PORT=5432
   export DB_NAME=energy_forecasting_prod
   export DB_USER=energy_user
   export DB_PASSWORD=<production_password>
   export REDIS_HOST=prod-redis.example.com
   export REDIS_PORT=6379
   export DEPLOY_CONFIRM=yes
   ```

3. **Deploy**:
   ```bash
   ./scripts/deploy-production.sh
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

## Support

For deployment issues:
1. Check logs: `docker-compose logs`
2. Review this guide
3. Check GitHub Issues
4. Contact DevOps team

