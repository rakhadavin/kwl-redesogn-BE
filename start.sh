#!/bin/bash
set -e

# Create required folders
mkdir -p /usr/src/app/app_logs
mkdir -p /var/log/supervisor

echo ">> Starting Django setup..."

python manage.py showmigrations
echo ">> showmigrations done"

python manage.py migrate --noinput
echo ">> migrate done"

python manage.py createcachetable
echo ">> createcachetable done"

python manage.py collectstatic --noinput
echo ">> collectstatic done"

if python manage.py showmigrations | grep -q data; then
  python manage.py loaddata data
else
  echo ">> no data fixture, skipping loaddata"
fi

echo "✅ Django setup complete. Starting Uvicorn..."
exec uvicorn kwl.asgi:application --host 0.0.0.0 --port 8042
