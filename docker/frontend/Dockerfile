# syntax=docker/dockerfile:1.6
# ---------------------------------------------------------------------------
# Frontend (Next.js 15) container - dev configuration
# ---------------------------------------------------------------------------
FROM node:20-alpine AS base

WORKDIR /app

# Install dependencies first for better layer caching
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
