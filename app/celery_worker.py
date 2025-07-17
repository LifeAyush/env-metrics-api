from celery import Celery
from app.config import settings
from app.logger import setup_logger

logger = setup_logger(__name__)

celery_app = Celery(
    "metrics_app",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

celery_app.autodiscover_tasks(["app.tasks"])

logger.info("Celery worker configured successfully")