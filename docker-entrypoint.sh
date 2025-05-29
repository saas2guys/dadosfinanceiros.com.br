#!/bin/sh

set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Daphne
echo "Starting Daphne server..."
exec daphne -b 0.0.0.0 -p 80 proxy_project.asgi:application 