#!/bin/bash

# Start Cron
# service cron start

# Start Django server
python3 manage.py runserver 0.0.0.0:8042 >> /app/be-kowl.log 2>&1