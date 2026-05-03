# syntax=docker/dockerfile:1.6
# ---------------------------------------------------------------------------
# Backend (Django + Celery) container
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System packages required by:
#   - psycopg / Postgres client headers
#   - Pillow (libjpeg, zlib)
#   - Tesseract OCR + language data
#   - WeasyPrint / cairo for PDF rendering
#   - poppler for pdf2image
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libjpeg-dev zlib1g-dev \
        tesseract-ocr \
        libtesseract-dev \
        poppler-utils \
        libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app

RUN mkdir -p /app/media /app/staticfiles /app/uploads /app/reports_out

EXPOSE 8000

CMD ["gunicorn", "compliance_audit.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
