import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query

from app.metrics import service
from app.database import get_db
from app.tasks import create_metric_async
from app.schemas import MetricBase, MetricResponse
from app.auth.dependencies import get_current_user
from app.exceptions import ResourceNotFoundError, ValidationError, DatabaseError
from app.logger import setup_logger

logger = setup_logger(__name__)
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
    """
    Get metrics with filtering, sorting, and pagination.
    
    Args:
        category: Filter by category (Energy, Water, Waste)
        sort_by: Sort field (value or date)
        order: Sort order (asc or desc)
        page: Page number (minimum 1)
        limit: Items per page (1-100)
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of metrics matching the criteria
    """
    try:
        logger.info(f"Metrics request - User: {current_user.email}, Category: {category}, Page: {page}")
        result = service.get_metrics_with_filters(db, category, sort_by, order, page, limit)
        return result["data"]
        
    except (ValidationError, DatabaseError):
        # Re-raise these specific exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_metrics: {e}")
        raise DatabaseError("Failed to retrieve metrics")

@router.get("/{metric_id}/related", response_model=List[MetricResponse])
def related_metrics(
    metric_id: str,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    """
    Get related metrics for a specific metric.
    
    Args:
        metric_id: Metric identifier
        db: Database session
        user: Authenticated user
        
    Returns:
        List of related metrics
    """
    try:
        logger.info(f"Related metrics request - User: {user.email}, Metric: {metric_id}")
        return service.get_related_metrics(db, metric_id)
        
    except DatabaseError:
        # Re-raise database errors
        raise
    except Exception as e:
        logger.error(f"Unexpected error in related_metrics for {metric_id}: {e}")
        raise DatabaseError("Failed to retrieve related metrics")

@router.post("", status_code=202)
def create_metric(metric: MetricBase, user = Depends(get_current_user)):
    """
    Create a new metric asynchronously.
    
    Args:
        metric: Metric data
        user: Authenticated user
        
    Returns:
        Processing confirmation message
    """
    try:
        metric_data = metric.model_dump()
        metric_data["id"] = str(uuid.uuid4())
        
        # Queue the task for async processing
        create_metric_async.delay(metric_data)
        
        logger.info(f"Metric creation queued - User: {user.email}, Metric: {metric_data['id']}")
        return {"message": "Metric is being processed", "metric_id": metric_data["id"]}
        
    except Exception as e:
        logger.error(f"Error queuing metric creation: {e}")
        raise DatabaseError("Failed to queue metric creation")

@router.put("/{metric_id}", response_model=MetricResponse)
def update_metric(
    metric_id: str, 
    updated_metric: MetricBase, 
    db: Session = Depends(get_db), 
    user = Depends(get_current_user)
):
    """
    Update an existing metric.
    
    Args:
        metric_id: Metric identifier
        updated_metric: Updated metric data
        db: Database session
        user: Authenticated user
        
    Returns:
        Updated metric object
    """
    try:
        logger.info(f"Metric update request - User: {user.email}, Metric: {metric_id}")
        metric = service.update_metric(metric_id, updated_metric, db)
        
        if not metric:
            raise ResourceNotFoundError("Metric", metric_id)
            
        return metric
        
    except (ResourceNotFoundError, ValidationError, DatabaseError):
        # Re-raise these specific exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating metric {metric_id}: {e}")
        raise DatabaseError("Failed to update metric")

@router.delete("/{metric_id}")
def delete_metric(
    metric_id: str, 
    db: Session = Depends(get_db), 
    user = Depends(get_current_user)
):
    """
    Delete a metric.
    
    Args:
        metric_id: Metric identifier
        db: Database session
        user: Authenticated user
        
    Returns:
        Success message
    """
    try:
        logger.info(f"Metric deletion request - User: {user.email}, Metric: {metric_id}")
        success = service.delete_metric(metric_id, db)
        
        if not success:
            raise ResourceNotFoundError("Metric", metric_id)
            
        return {"message": "Metric deleted successfully"}
        
    except (ResourceNotFoundError, DatabaseError):
        # Re-raise these specific exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting metric {metric_id}: {e}")
        raise DatabaseError("Failed to delete metric")
