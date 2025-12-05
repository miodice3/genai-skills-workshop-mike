"""Health check endpoint."""

from fastapi import APIRouter
from app.models import HealthResponse
from datetime import datetime

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the service is running.

    Returns:
        HealthResponse with status and current timestamp
    """
    return HealthResponse(status="healthy", timestamp=datetime.now())
