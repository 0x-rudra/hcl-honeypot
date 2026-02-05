#!/bin/bash
# Start script for Fly.io deployment

# Run database migrations if any (none for this project)
# python manage.py migrate

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
