#!/bin/bash
# Deployment Script for Energy Price Forecasting System
# Supports deployment to staging and production environments

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${ENVIRONMENT:-staging}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker.io}"
DOCKER_USERNAME="${DOCKER_USERNAME:-}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
COMPOSE_FILE="docker-compose.yml"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check environment variables
    if [ -z "$DOCKER_USERNAME" ]; then
        log_warn "DOCKER_USERNAME not set, using local images"
    fi
    
    log_info "Prerequisites check passed"
}

pull_images() {
    log_info "Pulling Docker images..."
    
    if [ -n "$DOCKER_USERNAME" ]; then
        docker pull "${DOCKER_REGISTRY}/${DOCKER_USERNAME}/energy-forecasting-api:${IMAGE_TAG}" || log_warn "Failed to pull API image"
        docker pull "${DOCKER_REGISTRY}/${DOCKER_USERNAME}/energy-forecasting-frontend:${IMAGE_TAG}" || log_warn "Failed to pull frontend image"
    else
        log_warn "Skipping image pull (no registry configured)"
    fi
}

deploy_services() {
    log_info "Deploying services to ${ENVIRONMENT}..."
    
    # Set environment-specific variables
    export ENV=${ENVIRONMENT}
    
    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose -f ${COMPOSE_FILE} down || true
    
    # Start services
    log_info "Starting services..."
    docker-compose -f ${COMPOSE_FILE} up -d
    
    log_info "Services deployed successfully"
}

run_health_checks() {
    log_info "Running health checks..."
    
    # Wait for services to be ready
    sleep 10
    
    # Check API health
    API_URL="http://localhost:8000/health"
    if curl -f ${API_URL} > /dev/null 2>&1; then
        log_info "API health check passed"
    else
        log_error "API health check failed"
        return 1
    fi
    
    # Check frontend (if accessible)
    FRONTEND_URL="http://localhost:80"
    if curl -f ${FRONTEND_URL} > /dev/null 2>&1; then
        log_info "Frontend health check passed"
    else
        log_warn "Frontend health check failed (may not be accessible)"
    fi
    
    log_info "Health checks completed"
}

rollback() {
    log_error "Deployment failed, rolling back..."
    docker-compose -f ${COMPOSE_FILE} down
    log_info "Rollback completed"
}

# Main deployment flow
main() {
    log_info "Starting deployment to ${ENVIRONMENT} environment"
    
    # Trap errors for rollback
    trap rollback ERR
    
    check_prerequisites
    pull_images
    deploy_services
    run_health_checks
    
    log_info "Deployment to ${ENVIRONMENT} completed successfully"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --environment|-e)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --tag|-t)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --registry|-r)
            DOCKER_REGISTRY="$2"
            shift 2
            ;;
        --username|-u)
            DOCKER_USERNAME="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -e, --environment ENV    Deployment environment (staging|production)"
            echo "  -t, --tag TAG           Docker image tag (default: latest)"
            echo "  -r, --registry REG      Docker registry URL"
            echo "  -u, --username USER     Docker registry username"
            echo "  -h, --help              Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main

