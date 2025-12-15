#!/bin/bash
# Rollback Script for Energy Price Forecasting System
# Supports rollback of deployments and models

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${ENVIRONMENT:-staging}"
ROLLBACK_TYPE="${ROLLBACK_TYPE:-deployment}"  # 'deployment' or 'model'
TARGET_VERSION="${TARGET_VERSION:-}"
REASON="${REASON:-Manual rollback}"

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

rollback_deployment() {
    log_info "Rolling back deployment for ${ENVIRONMENT}..."
    
    # Get current deployment version
    CURRENT_VERSION=$(docker-compose ps --format json | jq -r '.[0].Image' | cut -d: -f2 || echo "unknown")
    log_info "Current version: ${CURRENT_VERSION}"
    
    # Determine target version
    if [ -z "$TARGET_VERSION" ]; then
        # Get previous version from deployment history
        if [ -f "deployment_history.json" ]; then
            TARGET_VERSION=$(jq -r ".[] | select(.environment==\"${ENVIRONMENT}\") | .version" deployment_history.json | head -2 | tail -1)
        fi
        
        if [ -z "$TARGET_VERSION" ]; then
            log_error "No target version specified and no previous version found"
            exit 1
        fi
    fi
    
    log_info "Rolling back to version: ${TARGET_VERSION}"
    
    # Set target version
    export IMAGE_TAG="${TARGET_VERSION}"
    
    # Stop current deployment
    log_info "Stopping current deployment..."
    docker-compose down
    
    # Start previous version
    log_info "Starting previous version..."
    docker-compose up -d
    
    # Run health checks
    log_info "Running health checks..."
    sleep 10
    
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "Rollback successful - health check passed"
    else
        log_error "Rollback failed - health check failed"
        exit 1
    fi
}

rollback_model() {
    log_info "Rolling back model..."
    log_warn "Model rollback requires Python script execution"
    log_info "Use: python -m mlops.rollback --model-name <name> --target-version <version>"
}

# Main rollback flow
main() {
    log_info "Starting rollback for ${ROLLBACK_TYPE} in ${ENVIRONMENT} environment"
    
    case $ROLLBACK_TYPE in
        deployment)
            rollback_deployment
            ;;
        model)
            rollback_model
            ;;
        *)
            log_error "Unknown rollback type: ${ROLLBACK_TYPE}"
            exit 1
            ;;
    esac
    
    log_info "Rollback completed successfully"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --environment|-e)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --type|-t)
            ROLLBACK_TYPE="$2"
            shift 2
            ;;
        --version|-v)
            TARGET_VERSION="$2"
            shift 2
            ;;
        --reason|-r)
            REASON="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -e, --environment ENV    Environment (staging|production)"
            echo "  -t, --type TYPE         Rollback type (deployment|model)"
            echo "  -v, --version VERSION  Target version (default: previous)"
            echo "  -r, --reason REASON     Reason for rollback"
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

