FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile
COPY frontend/ .
RUN yarn build

# Use nginx base image to avoid apt-get install issues
FROM nginx:alpine AS nginx-base
RUN apk add --no-cache python3 py3-pip supervisor curl

FROM python:3.11-slim

# Copy nginx from alpine (more reliable than apt-get install)
COPY --from=nginx-base /usr/sbin/nginx /usr/sbin/nginx
COPY --from=nginx-base /etc/nginx /etc/nginx
COPY --from=nginx-base /usr/lib/nginx /usr/lib/nginx
COPY --from=nginx-base /var/log/nginx /var/log/nginx

# Install only supervisor and curl (smaller install)
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    curl \
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
RUN mkdir -p /var/log/supervisor /var/log/nginx /var/run /run

# Expose port
EXPOSE 8080

# Start supervisor
CMD ["supervisord", "-c", "/etc/supervisord.conf"]