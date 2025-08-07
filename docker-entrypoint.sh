#!/bin/sh
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create cache table for database cache backend
echo "Creating cache table..."
python manage.py createcachetable rate_limit_cache

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Daphne
echo "Starting Daphne server..."
exec daphne -b 0.0.0.0 -p 8080 proxy_project.asgi:application