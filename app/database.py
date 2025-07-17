from typing import Generator, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.models import Base
from app.config import settings
from app.logger import setup_logger

logger = setup_logger(__name__)

def get_database_config() -> Tuple[str, Dict[str, Any]]:
    """
    Get database URL and connection arguments based on database type.
    
    Returns:
        Tuple of (database_url, connect_args)
    """
    url = settings.DATABASE_URL
    
    # SQLite-specific configuration
    if url.startswith("sqlite"):
        logger.info("Using SQLite database")
        return url, {"check_same_thread": False}
    
    # PostgreSQL/MySQL configuration
    elif url.startswith(("postgresql", "mysql")):
        logger.info("Using PostgreSQL/MySQL database")
        return url, {}
    
    # Default fallback
    else:
        logger.warning(f"Unknown database type: {url}")
        return url, {}

DATABASE_URL, connect_args = get_database_config()

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        raise

def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed")
