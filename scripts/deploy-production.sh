#!/bin/bash
# Production Deployment Script
# Wrapper script for production-specific deployment with additional safety checks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Safety checks for production
if [ -z "$DEPLOY_CONFIRM" ]; then
    echo "ERROR: Production deployment requires explicit confirmation"
    echo "Set DEPLOY_CONFIRM=yes to proceed"
    exit 1
fi

export ENVIRONMENT=production
export IMAGE_TAG="${IMAGE_TAG:-latest}"

# Additional production checks
echo "WARNING: This will deploy to PRODUCTION"
echo "Press Ctrl+C to cancel, or wait 10 seconds to continue..."
sleep 10

# Source main deployment script
source "${SCRIPT_DIR}/deploy.sh"

