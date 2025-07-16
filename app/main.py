import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import init_db
from app.auth.routes import router as auth_router
from app.metrics.routes import router as metrics_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run on startup
    if os.getenv("ENV") != "production":
        print("Initializing database tables (if not exist)...")
        init_db()
    yield
    # Run on shutdown
    print("Application shutdown complete.")

app = FastAPI(lifespan=lifespan)

# Routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(metrics_router, prefix="/metrics", tags=["Metrics"])
