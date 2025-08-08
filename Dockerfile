FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend

# Copy package files (handle case where yarn.lock might be missing)
COPY frontend/package.json ./
COPY frontend/yarn.lock* ./

# Install dependencies
RUN yarn install --frozen-lockfile || yarn install

COPY frontend/ .
RUN yarn build

# RAILWAY MEMORY FIX - Avoid apt-get completely
FROM python:3.11-slim

# Skip apt-get - use Python to serve static files instead of nginx
# Install Python dependencies only
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ ./backend/

# Copy built frontend to be served by Python
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Create simple start script
RUN echo '#!/bin/bash\ncd /app/backend && python -m uvicorn server:app --host 0.0.0.0 --port 8080' > /app/start.sh
RUN chmod +x /app/start.sh

# Expose port
EXPOSE 8080

# Start backend directly (serve frontend via Python static files)
CMD ["/app/start.sh"]