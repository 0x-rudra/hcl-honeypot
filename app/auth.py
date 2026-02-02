"""Authentication module for API key validation."""

from fastapi import Header, HTTPException, status
from app.config import Config


async def validate_api_key(x_api_key: str = Header(None)) -> str:
    """
    Validate the x-api-key header.

    Args:
        x_api_key: API key from request header

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing x-api-key header",
        )

    if x_api_key != Config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return x_api_key
