#!/bin/sh

python manage.py check && \
    python manage.py collectstatic --no-input && \
    python manage.py migrate --no-input && \
    python manage.py create_specs && \
    python manage.py create_groups && \
    python manage.py create_addresses && \
    gunicorn --config gunicorn.conf.py src.wsgi:application