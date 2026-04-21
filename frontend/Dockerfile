# Stage 1: install dependencies
FROM node:18-alpine AS builder

WORKDIR /app
COPY package.json .
RUN npm install --omit=dev


# Stage 2: production image
FROM node:18-alpine

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /app/node_modules ./node_modules

# Copy application code (no .env files)
COPY app.js .
COPY views/ ./views/

# Create and switch to non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:3000/ || exit 1

CMD ["node", "app.js"]
