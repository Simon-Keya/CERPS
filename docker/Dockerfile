# Base image
FROM python:3.12-slim

# Set workdir
WORKDIR /usr/src/app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY ../requirements.txt .

# Install Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY ../manage.py .
COPY ../cerps ./cerps
COPY ../apps ./apps
COPY ../scripts ./scripts

# Collect static files
RUN mkdir -p /usr/src/app/staticfiles
RUN mkdir -p /usr/src/app/media
