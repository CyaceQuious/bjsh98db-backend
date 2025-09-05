#!/bin/sh
python manage.py makemigrations
python manage.py migrate

PORT="${PORT:-10000}"
TIMEOUT="${TIMEOUT:-600}"

# python3 manage.py runserver 80
uwsgi --module=BackEnd.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=BackEnd.settings \
    --master \
    --http=0.0.0.0:${PORT} \
    --processes=5 \
    --harakiri=${TIMEOUT} \
    --max-requests=5000 \
    --vacuum \
    --buffer-size=65535