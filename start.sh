#!/bin/bash

set -e

LOGFILE=app_logs/django_startup.log

echo ">> Starting Django setup..." | tee -a $LOGFILE

python manage.py showmigrations | tee -a $LOGFILE
echo ">> showmigrations done" | tee -a $LOGFILE

python manage.py makemigrations --noinput | tee -a $LOGFILE
echo ">> makemigrations done" | tee -a $LOGFILE

python manage.py migrate --noinput | tee -a $LOGFILE
echo ">> migrate done" | tee -a $LOGFILE

python manage.py createcachetable | tee -a $LOGFILE
echo ">> createcachetable done" | tee -a $LOGFILE

python manage.py collectstatic --noinput | tee -a $LOGFILE
echo ">> collectstatic done" | tee -a $LOGFILE

if python manage.py showmigrations | grep -q data; then
  python manage.py loaddata data
else
  echo ">> no data fixture, skipping loaddata"
fi


# Start Cron
# service cron start

# Start Django server
# python3 manage.py runserver 0.0.0.0:8042 >> /app/be-kowl.log 2>&1

echo "✅ Django setup complete. Starting Uvicorn..." | tee -a $LOGFILE

exec uvicorn kwl.asgi:application --host 0.0.0.0 --port 8042