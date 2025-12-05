from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=2000, description="User message to send to the agent")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: Optional[str] = Field(None, description="Agent's response text")
    blocked: bool = Field(False, description="Whether the response was blocked by Model Armor")
    blocked_reason: Optional[str] = Field(None, description="Reason for blocking if blocked")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Health status of the service")
    timestamp: datetime = Field(..., description="Current server timestamp")
