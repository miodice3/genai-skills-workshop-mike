"""Chat endpoint for interacting with the GenAI agent."""

from fastapi import APIRouter, HTTPException, Depends
from app.models import ChatRequest, ChatResponse
from app.agent.core import generate
from app.config import get_settings, Settings
import logging

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, settings: Settings = Depends(get_settings)):
    """
    Send a message to the GenAI agent and receive a response.

    The agent has access to:
    - Weather information via Google Maps and NOAA APIs
    - Alaska Department of Snow knowledge base via RAG

    All prompts and responses are validated with Model Armor.

    Args:
        request: ChatRequest containing the user's message

    Returns:
        ChatResponse with the agent's response or blocking information

    Raises:
        HTTPException: If an error occurs during processing
    """
    try:
        logger.info(f"Received chat request: {request.message[:100]}...")

        # Call the agent's generate function
        result = generate(request.message)

        if result is None:
            # Response was blocked by Model Armor
            return ChatResponse(
                response=None,
                blocked=True,
                blocked_reason="Response was blocked by Model Armor for safety reasons",
            )
        else:
            # Successful response
            return ChatResponse(response=result, blocked=False, blocked_reason=None)

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"An error occurred while processing your request: {str(e)}"
        )
