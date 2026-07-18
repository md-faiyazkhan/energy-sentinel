from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.api.routes import monitoring, health, analytics, recommendations
from src.db.session import create_tables
from src.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on application startup and shutdown.
    - Startup: create database tables if DB is available
    - Shutdown: nothing required
    """
    logger.info("Energy Sentinel API starting up...")
    try:
        create_tables()
    except Exception as e:
        logger.warning(f"Database not available — skipping table creation: {e}")
    yield
    logger.info("Energy Sentinel API shutting down...")


app = FastAPI(
    title="Energy Sentinel API",
    description="REST API for household energy monitoring and appliance anomaly detection.",
    version="1.0.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(monitoring.router)
app.include_router(health.router)
app.include_router(analytics.router)
app.include_router(recommendations.router)


@app.get("/", tags=["Root"])
def root():
    """Health check endpoint."""
    return {"message": "Energy Sentinel API is running."}