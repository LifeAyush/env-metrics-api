import uuid
from typing import Optional
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.models import Metric
from app.schemas import MetricBase

def get_metric_by_id(metric_id: str, db: Session):
    return db.query(Metric).filter(Metric.id == metric_id).first()

def get_metrics_with_filters(
    db: Session,
    category: Optional[str] = None,
    sort_by: Optional[str] = None,
    order: Optional[str] = "asc",
    page: int = 1,
    limit: int = 10
) -> dict:
    query = db.query(Metric)

    if category:
        query = query.filter(Metric.category == category)

    if sort_by in {"value", "date"}:
        sort_column = getattr(Metric, sort_by)
        query = query.order_by(asc(sort_column) if order == "asc" else desc(sort_column))

    total = query.count()
    results = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "data": results,
        "total": total,
        "page": page,
        "limit": limit
    }
    
def get_related_metrics(db: Session, metric_id: str, limit: int = 3):
    current = db.query(Metric).filter(Metric.id == metric_id).first()
    if not current:
        return []

    # Dummy logic: Get other metrics in same category, excluding self
    related_metrics = db.query(Metric).filter(Metric.category == current.category, Metric.id != metric_id).limit(limit).all()
    return related_metrics


def create_metric(metric: MetricBase, db: Session):
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

def update_metric(metric_id: str, updated: MetricBase, db: Session):
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
