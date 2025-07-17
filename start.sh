#!/bin/bash

# Only start FastAPI OR Celery based on ENV
if [ "$WORKER" = "true" ]; then
    echo "Starting Celery Worker..."
    celery -A app.celery_worker.celery_app worker --loglevel=info
else
    echo "Starting FastAPI Server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
