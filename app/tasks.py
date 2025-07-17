from sqlalchemy.exc import SQLAlchemyError

from app.models import Metric
from app.database import SessionLocal
from app.celery_worker import celery_app

@celery_app.task(name="app.tasks.create_metric_async")
def create_metric_async(metric_data: dict):
    db = SessionLocal()
    try:
        metric = Metric(**metric_data)
        db.add(metric)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        print("DB Error:", e)
    finally:
        db.close()
