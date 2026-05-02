# Multi-stage build: build frontend, then install Python deps and serve with uvicorn

# 1) Build frontend
FROM node:18-alpine AS build-frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund
COPY frontend/ .
RUN npm run build

# 2) Python runtime
FROM python:3.11-slim
WORKDIR /app

# Install system deps required by some packages (opencv, ffmpeg)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential ca-certificates ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend application
COPY backend ./backend

# Copy built frontend from previous stage
COPY --from=build-frontend /app/frontend/dist ./frontend/dist

ENV PYTHONPATH=/app/backend
WORKDIR /app/backend

EXPOSE 1050
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "1050"]
