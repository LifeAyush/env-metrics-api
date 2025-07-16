import uuid
from sqlalchemy.orm import Session

from app.models import Metric
from app.schemas import MetricCreate

def get_all_metrics(db: Session):
    return db.query(Metric).all()

def get_metric_by_id(metric_id: str, db: Session):
    return db.query(Metric).filter(Metric.id == metric_id).first()

def create_metric(metric: MetricCreate, db: Session):
    new_metric = Metric(
        id=str(uuid.uuid4()),
        name=metric.name,
        category=metric.category,
        value=metric.value,
        unit=metric.unit,
        date=metric.date
    )
    db.add(new_metric)
    db.commit()
    db.refresh(new_metric)
    return new_metric

def update_metric(metric_id: str, updated: MetricCreate, db: Session):
    metric = get_metric_by_id(metric_id, db)
    if not metric:
        return None
    metric.name = updated.name
    metric.category = updated.category
    metric.value = updated.value
    metric.unit = updated.unit
    metric.date = updated.date
    db.commit()
    db.refresh(metric)
    return metric

def delete_metric(metric_id: str, db: Session):
    metric = get_metric_by_id(metric_id, db)
    if not metric:
        return None
    db.delete(metric)
    db.commit()
    return True
