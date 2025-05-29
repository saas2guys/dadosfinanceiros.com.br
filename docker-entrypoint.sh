#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Create cache table
echo "Creating cache table..."
python manage.py createcachetable

# Start Gunicorn
echo "Starting Gunicorn..."
exec "$@" 