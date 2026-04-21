# Stage 1: install dependencies
FROM python:3.11-alpine AS builder

WORKDIR /app
COPY requirements.txt .
# hadolint ignore=DL3013,DL3018
RUN apk add --no-cache gcc musl-dev && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: production image
FROM python:3.11-alpine

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code (no .env files)
COPY worker.py .

# Create and switch to non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import redis, os; r = redis.Redis(host=os.getenv('REDIS_HOST','localhost'), port=int(os.getenv('REDIS_PORT',6379)), password=os.getenv('REDIS_PASSWORD')); r.ping()"

CMD ["python", "worker.py"]
