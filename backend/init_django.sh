#!/bin/bash
set -e

# Create Django project
django-admin startproject config .

# Create a new app
python manage.py startapp core

# Apply migrations
python manage.py migrate

# Create a superuser (optional)
# python manage.py createsuperuser --noinput

echo "Django project initialized successfully!" 