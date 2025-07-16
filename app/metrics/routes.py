from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.metrics import service
from app.database import get_db
from app.schemas import MetricCreate, MetricOut
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[MetricOut])
def get_metrics(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return service.get_all_metrics(db)

@router.post("/", response_model=MetricOut)
def create_metric(metric: MetricCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return service.create_metric(metric, db)

@router.put("/{metric_id}", response_model=MetricOut)
def update_metric(metric_id: str, updated_metric: MetricCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
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
