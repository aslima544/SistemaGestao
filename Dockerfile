FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile
COPY frontend/ .
RUN yarn build

# FORCE REBUILD - Railway cache fix - 2024-12-25
# Use python:3.11-slim - more reliable on Railway platform - updated v2
FROM python:3.11-slim

# Install system dependencies (Python already included in slim image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    nginx \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

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

# Create necessary directories and setup nginx
RUN mkdir -p /var/log/supervisor /var/log/nginx /var/run \
    && rm -f /etc/nginx/sites-enabled/default \
    && ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

# Expose port
EXPOSE 8080

# Start supervisor
CMD ["supervisord", "-c", "/etc/supervisord.conf"]