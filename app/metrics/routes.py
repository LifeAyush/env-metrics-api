import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query

from app.metrics import service
from app.database import get_db
from app.tasks import create_metric_async
from app.schemas import MetricBase, MetricResponse
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("", response_model=List[MetricResponse])
def get_metrics(
    category: Optional[str] = Query(None, regex="^(Energy|Water|Waste)$"),
    sort_by: Optional[str] = Query(None, regex="^(value|date)$"),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return service.get_metrics_with_filters(db, category, sort_by, order, page, limit)

@router.get("/{metric_id}/related", response_model=List[MetricResponse])
def related_metrics(
    metric_id: str,
    db: Session = Depends(get_db),
    user= Depends(get_current_user),
):
    return service.get_related_metrics(db, metric_id)

@router.post("", status_code=202)
def create_metric(metric: MetricBase, user=Depends(get_current_user)):
    metric_data = metric.model_dump()
    metric_data["id"] = str(uuid.uuid4())
    create_metric_async.delay(metric_data)
    return {"message": "Metric is being processed"}

@router.put("/{metric_id}", response_model=MetricResponse)
def update_metric(metric_id: str, updated_metric: MetricBase, db: Session = Depends(get_db), user=Depends(get_current_user)):
    metric = service.update_metric(metric_id, updated_metric, db)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric

@router.delete("/{metric_id}")
def delete_metric(metric_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    success = service.delete_metric(metric_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Metric not found")
    return {"message": "Metric deleted successfully"}
