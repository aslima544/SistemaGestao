FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend

# Copy package.json first (for caching)
COPY frontend/package.json ./

# Install dependencies without yarn.lock to avoid checksum issues
RUN yarn install

# Copy rest of frontend code
COPY frontend/ .

# Build the frontend
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