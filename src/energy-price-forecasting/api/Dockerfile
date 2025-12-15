# Multi-stage Dockerfile for FastAPI Backend
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code (from parent directory to include all modules)
COPY ../api /app/api
COPY ../models /app/models
COPY ../database /app/database
COPY ../evaluation /app/evaluation
COPY ../trading /app/trading
COPY ../feature_engineering /app/feature_engineering
COPY ../training /app/training
COPY ../mlflow_tracking /app/mlflow_tracking
COPY ../multi_horizon /app/multi_horizon
COPY ../utils /app/utils
COPY ../requirements.txt /app/requirements.txt

# Set working directory to API directory
WORKDIR /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

