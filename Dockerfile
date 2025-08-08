FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile
COPY frontend/ .
RUN yarn build

FROM python:3.11-slim

# Install system dependencies in optimized way for Railway
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor=4.2.1-1+deb11u1 \
    nginx=1.18.0-6.1+deb11u3 \
    curl=7.74.0-1.3+deb11u7 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/archives/*

# Install Python dependencies
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ ./backend/

# Copy built frontend
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Copy configuration files
COPY supervisord.conf /etc/supervisord.conf
COPY nginx.conf /etc/nginx/sites-available/default

# Create necessary directories
RUN mkdir -p /var/log/supervisor /var/log/nginx /var/run

# Expose port
EXPOSE 8080

# Start supervisor
CMD ["supervisord", "-c", "/etc/supervisord.conf"]