from sqlalchemy.exc import SQLAlchemyError

from app.models import Metric
from app.database import SessionLocal
from app.celery_worker import celery_app
from app.logger import setup_logger

logger = setup_logger(__name__)

@celery_app.task(name="app.tasks.create_metric_async")
def create_metric_async(metric_data: dict):
    """
    Asynchronously create a metric in the database.
    
    Args:
        metric_data: Dictionary containing metric data
        
    Returns:
        Success status and metric ID if successful
    """
    db = SessionLocal()
    try:
        logger.info(f"Processing async metric creation: {metric_data.get('id', 'unknown')}")
        
        # Validate required fields
        required_fields = ['id', 'name', 'category', 'value', 'unit', 'date']
        missing_fields = [field for field in required_fields if field not in metric_data]
        
        if missing_fields:
            logger.error(f"Missing required fields for metric creation: {missing_fields}")
            return {"success": False, "error": f"Missing required fields: {missing_fields}"}
        
        # Create metric object
        metric = Metric(**metric_data)
        db.add(metric)
        db.commit()
        
        logger.info(f"Metric created successfully via async task: {metric_data['id']}")
        return {"success": True, "metric_id": metric_data['id']}
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during async metric creation: {e}")
        return {"success": False, "error": "Database operation failed"}
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during async metric creation: {e}")
        return {"success": False, "error": "Unexpected error occurred"}
    finally:
        db.close()
        logger.debug("Database session closed for async task")
