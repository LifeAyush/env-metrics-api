import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import Metric
from app.schemas import MetricBase
from app.exceptions import DatabaseError, ValidationError
from app.logger import setup_logger

logger = setup_logger(__name__)

def get_metric_by_id(metric_id: str, db: Session) -> Optional[Metric]:
    """
    Get metric by ID.
    
    Args:
        metric_id: Metric identifier
        db: Database session
        
    Returns:
        Metric object if found, None otherwise
    """
    try:
        metric = db.query(Metric).filter(Metric.id == metric_id).first()
        logger.debug(f"Metric lookup for id: {metric_id}, found: {metric is not None}")
        return metric
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching metric {metric_id}: {e}")
        raise DatabaseError("Failed to fetch metric")
    except Exception as e:
        logger.error(f"Unexpected error while fetching metric {metric_id}: {e}")
        raise DatabaseError("Unexpected error occurred")

def get_metrics_with_filters(
    db: Session,
    category: Optional[str] = None,
    sort_by: Optional[str] = None,
    order: Optional[str] = "asc",
    page: int = 1,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get metrics with filtering, sorting, and pagination.
    
    Args:
        db: Database session
        category: Filter by category
        sort_by: Sort field (value or date)
        order: Sort order (asc or desc)
        page: Page number
        limit: Items per page
        
    Returns:
        Dictionary with metrics data and pagination info
    """
    try:
        query = db.query(Metric)

        # Apply category filter
        if category:
            if category not in ["Energy", "Water", "Waste"]:
                raise ValidationError(f"Invalid category: {category}")
            query = query.filter(Metric.category == category)
            logger.debug(f"Applied category filter: {category}")

        # Apply sorting
        if sort_by in {"value", "date"}:
            sort_column = getattr(Metric, sort_by)
            if order == "asc":
                query = query.order_by(asc(sort_column))
            elif order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                raise ValidationError(f"Invalid sort order: {order}")
            logger.debug(f"Applied sorting: {sort_by} {order}")
        elif sort_by is not None:
            raise ValidationError(f"Invalid sort field: {sort_by}")

        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        results = query.offset(offset).limit(limit).all()
        
        logger.info(f"Retrieved {len(results)} metrics (page {page}, limit {limit}, total {total})")
        
        return {
            "data": results,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
        
    except (ValidationError, DatabaseError):
        # Re-raise these specific exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching metrics: {e}")
        raise DatabaseError("Failed to fetch metrics")
    except Exception as e:
        logger.error(f"Unexpected error while fetching metrics: {e}")
        raise DatabaseError("Unexpected error occurred")
    
def get_related_metrics(db: Session, metric_id: str, limit: int = 3) -> List[Metric]:
    """
    Get related metrics based on category.
    
    Args:
        db: Database session
        metric_id: Current metric ID
        limit: Maximum number of related metrics to return
        
    Returns:
        List of related metrics
    """
    try:
        current = get_metric_by_id(metric_id, db)
        if not current:
            logger.warning(f"Related metrics requested for non-existent metric: {metric_id}")
            return []

        # Get other metrics in same category, excluding self
        related_metrics = db.query(Metric).filter(
            Metric.category == current.category, 
            Metric.id != metric_id
        ).limit(limit).all()
        
        logger.info(f"Found {len(related_metrics)} related metrics for {metric_id}")
        return related_metrics
        
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching related metrics for {metric_id}: {e}")
        raise DatabaseError("Failed to fetch related metrics")
    except Exception as e:
        logger.error(f"Unexpected error while fetching related metrics for {metric_id}: {e}")
        raise DatabaseError("Unexpected error occurred")

def create_metric(metric: MetricBase, db: Session) -> Metric:
    """
    Create a new metric.
    
    Args:
        metric: Metric data
        db: Database session
        
    Returns:
        Created metric object
    """
    try:
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
        
        logger.info(f"Metric created successfully: {new_metric.id} ({new_metric.name})")
        return new_metric
        
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating metric: {e}")
        db.rollback()
        raise DatabaseError("Failed to create metric")
    except Exception as e:
        logger.error(f"Unexpected error while creating metric: {e}")
        db.rollback()
        raise DatabaseError("Unexpected error occurred")

def update_metric(metric_id: str, updated: MetricBase, db: Session) -> Optional[Metric]:
    """
    Update an existing metric.
    
    Args:
        metric_id: Metric identifier
        updated: Updated metric data
        db: Database session
        
    Returns:
        Updated metric object if found, None otherwise
    """
    try:
        metric = get_metric_by_id(metric_id, db)
        if not metric:
            logger.warning(f"Update attempted on non-existent metric: {metric_id}")
            return None
            
        # Update fields
        metric.name = updated.name
        metric.category = updated.category
        metric.value = updated.value
        metric.unit = updated.unit
        metric.date = updated.date
        
        db.commit()
        db.refresh(metric)
        
        logger.info(f"Metric updated successfully: {metric_id}")
        return metric
        
    except SQLAlchemyError as e:
        logger.error(f"Database error while updating metric {metric_id}: {e}")
        db.rollback()
        raise DatabaseError("Failed to update metric")
    except Exception as e:
        logger.error(f"Unexpected error while updating metric {metric_id}: {e}")
        db.rollback()
        raise DatabaseError("Unexpected error occurred")

def delete_metric(metric_id: str, db: Session) -> bool:
    """
    Delete a metric.
    
    Args:
        metric_id: Metric identifier
        db: Database session
        
    Returns:
        True if deleted successfully, False if not found
    """
    try:
        metric = get_metric_by_id(metric_id, db)
        if not metric:
            logger.warning(f"Delete attempted on non-existent metric: {metric_id}")
            return False
            
        db.delete(metric)
        db.commit()
        
        logger.info(f"Metric deleted successfully: {metric_id}")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting metric {metric_id}: {e}")
        db.rollback()
        raise DatabaseError("Failed to delete metric")
    except Exception as e:
        logger.error(f"Unexpected error while deleting metric {metric_id}: {e}")
        db.rollback()
        raise DatabaseError("Unexpected error occurred")
