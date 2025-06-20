#!/bin/sh
python manage.py makemigrations
python manage.py migrate

# python3 manage.py runserver 80
uwsgi --module=BackEnd.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=BackEnd.settings \
    --master \
    --http=0.0.0.0:80 \
    --processes=5 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum