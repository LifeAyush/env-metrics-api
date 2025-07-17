import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.database import init_db
from app.auth.routes import router as auth_router
from app.metrics.routes import router as metrics_router
from app.exceptions import MetricsAPIException
from app.logger import setup_logger

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Run on startup
    try:
        if os.getenv("ENV") != "production":
            logger.info("Initializing database tables (if not exist)...")
            init_db()
        else:
            logger.info("Production environment detected, skipping database initialization")
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    yield
    # Run on shutdown
    logger.info("Application shutdown complete")

app = FastAPI(
    title="Metrics API",
    description="A FastAPI application for managing environmental metrics",
    version="1.0.0",
    lifespan=lifespan
)

# Global exception handler for custom exceptions
@app.exception_handler(MetricsAPIException)
async def metrics_api_exception_handler(request: Request, exc: MetricsAPIException):
    """Handle custom API exceptions."""
    logger.warning(f"API Exception: {exc.detail} (Code: {exc.error_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "error_code": exc.error_code,
            "extra_data": exc.extra_data
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "metrics-api"}

# Routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(metrics_router, prefix="/metrics", tags=["Metrics"])

logger.info("FastAPI application configured successfully")
