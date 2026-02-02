"""Authentication module for API key validation."""

from fastapi import Header, HTTPException, status
from typing import Optional
from app.config import Config
import logging

logger = logging.getLogger(__name__)


async def validate_api_key(
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
) -> str:
    """
    Validate the x-api-key header.

    Args:
        x_api_key: API key from request header

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not x_api_key or (isinstance(x_api_key, str) and x_api_key.strip() == ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing x-api-key header",
        )

    if x_api_key != Config.API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    logger.info("API key validated successfully")
    return x_api_key
