#!/bin/bash
# Vercel build step: установка зависимостей и сборка статических файлов админки/whitenoise
set -e

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput --clear
