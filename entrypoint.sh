#!/bin/bash

cd /home/appuser/app/imgservice/

python manage.py migrate

exec "$@"