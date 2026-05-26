#!/bin/bash
echo "=== Сборка проекта для Vercel ==="
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
echo "=== Сборка завершена успешно ==="
