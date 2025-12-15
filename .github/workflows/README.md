# GitHub Actions Workflows

This directory contains CI/CD workflows for the Energy Price Forecasting System.

## Workflows

### 1. Test (`test.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**
- **test-backend**: Runs Python tests, linting (flake8), and coverage reports
- **test-frontend**: Runs TypeScript checks, linting (ESLint), and builds the React app

**Services:**
- PostgreSQL + TimescaleDB (for backend tests)
- Redis (for backend tests)

### 2. Build (`build.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Tags matching `v*` pattern
- Manual workflow dispatch

**Jobs:**
- **build-backend**: Builds and pushes FastAPI backend Docker image
- **build-frontend**: Builds and pushes React frontend Docker image

**Features:**
- Docker layer caching for faster builds
- Multi-platform support (via Docker Buildx)
- Automatic tagging based on branch/PR/tag

### 3. Deploy Staging (`deploy-staging.yml`)

**Triggers:**
- Push to `develop` branch
- Manual workflow dispatch

**Features:**
- Deploys to staging environment
- Health checks after deployment
- Deployment notifications

### 4. Deploy Production (`deploy-production.yml`)

**Triggers:**
- Push to `main` branch
- Tags matching `v*` pattern
- Manual workflow dispatch (requires approval)

**Features:**
- Deploys to production environment
- Health checks after deployment
- Automatic rollback on failure
- Deployment notifications

## Required Secrets

Configure the following secrets in GitHub repository settings:

### Docker Hub
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password or access token

### External APIs
- `EIA_API_KEY`: EIA API key for testing
- `FRED_API_KEY`: FRED API key for testing

### Deployment (if using)
- `STAGING_HOST`: Staging server hostname/IP
- `STAGING_SSH_KEY`: SSH private key for staging server
- `PRODUCTION_HOST`: Production server hostname/IP
- `PRODUCTION_SSH_KEY`: SSH private key for production server

## Usage

### Running Tests Locally

```bash
# Backend tests
cd src/energy-price-forecasting
pytest tests/ -v

# Frontend tests
cd src/energy-price-forecasting/dashboard
npm run lint
npm run build
```

### Building Docker Images Locally

```bash
# Backend
cd src/energy-price-forecasting
docker build -f api/Dockerfile -t energy-forecasting-api:latest .

# Frontend
cd src/energy-price-forecasting/dashboard
docker build -f Dockerfile -t energy-forecasting-frontend:latest .
```

### Manual Workflow Dispatch

1. Go to GitHub Actions tab
2. Select the workflow you want to run
3. Click "Run workflow"
4. Select branch and click "Run workflow"

## Workflow Status Badges

Add these badges to your README.md:

```markdown
![Test](https://github.com/your-username/your-repo/workflows/Test/badge.svg)
![Build](https://github.com/your-username/your-repo/workflows/Build%20Docker%20Images/badge.svg)
```

## Troubleshooting

### Tests Failing
- Check that all required secrets are configured
- Verify database and Redis services are accessible
- Review test logs for specific error messages

### Build Failing
- Ensure Docker Hub credentials are correct
- Check Dockerfile syntax and paths
- Verify all dependencies are available

### Deployment Failing
- Verify deployment secrets are configured
- Check server connectivity
- Review deployment logs for errors

