# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=settings
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    pkg-config \
    libmariadb-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install and upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY webapp/requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the entire project to the working directory
COPY . /app/

# Run collectstatic and migrations
RUN python /app/sitnfly/manage.py collectstatic --noinput
RUN python /app/sitnfly/manage.py migrate

# Expose the port the app runs on
EXPOSE 8000

# Set the entrypoint
CMD cd /app/sitnfly && exec gunicorn wsgi:application --bind 0.0.0.0:8000 --log-level debug --log-file -
