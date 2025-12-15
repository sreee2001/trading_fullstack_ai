#!/bin/bash
# Staging Deployment Script
# Wrapper script for staging-specific deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export ENVIRONMENT=staging
export IMAGE_TAG="${IMAGE_TAG:-staging}"

# Source main deployment script
source "${SCRIPT_DIR}/deploy.sh"

