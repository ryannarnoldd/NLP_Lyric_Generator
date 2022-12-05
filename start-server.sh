#!/usr/bin/env bash
# start-server.sh
python3 manage.py makemigrations
python3 manage.py migrate
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (python manage.py createsuperuser --no-input --email $DJANGO_SUPERUSER_EMAIL)
fi
(gunicorn Generator_Website.wsgi --user www-data --bind 0.0.0.0:8000 --workers 3 --timeout 120) &
nginx -g "daemon off;"
chown -R www-data:www-data /opt/app

