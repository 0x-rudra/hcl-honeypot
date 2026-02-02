"""Main FastAPI application for Honeypot API."""

from fastapi import FastAPI, Depends, HTTPException, status
import logging

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.config import Config
from app.auth import validate_api_key
from app.schemas import HoneypotRequest, HoneypotResponse, ExtractedIntelligence
from app.scam_detector import ScamDetector
from app.persona import PersonaGenerator
from app.extractor import IntelligenceExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agentic Honeypot API",
    description="Detects scams, generates honeypot replies, and extracts scam intelligence",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup."""
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.warning("API will not function properly without GEMINI_API_KEY")


@app.post("/honeypot", response_model=HoneypotResponse)
async def honeypot(
    request: HoneypotRequest,
    api_key: str = Depends(validate_api_key),
) -> HoneypotResponse:
    """
    Main honeypot endpoint.

    Detects scams, generates honeypot replies, and extracts intelligence.

    Args:
        request: Request containing the message to analyze
        api_key: Validated API key from header

    Returns:
        Structured response with scam detection results
    """
    try:
        message = request.message.strip()

        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty",
            )

        logger.info(f"Processing message: {message[:50]}...")

        # Step 1: Detect if it's a scam
        logger.info("Step 1: Starting scam detection...")
        detection_result = ScamDetector.detect(message)
        is_scam = detection_result["is_scam"]
        confidence = detection_result["confidence"]
        reasoning = detection_result["reasoning"]
        logger.info(f"Scam detection result: is_scam={is_scam}, confidence={confidence:.3f}")

        # Step 2: Extract intelligence from the message
        logger.info("Step 2: Extracting intelligence...")
        intelligence = IntelligenceExtractor.extract(message)
        extracted_intelligence = ExtractedIntelligence(
            bank_accounts=intelligence.get("bank_accounts", []),
            upi_ids=intelligence.get("upi_ids", []),
            phone_numbers=intelligence.get("phone_numbers", []),
            phishing_urls=intelligence.get("phishing_urls", []),
        )
        logger.info(f"Intelligence extracted: {sum(len(v) for v in intelligence.values())} total indicators")

        # Step 3: Generate honeypot reply if it's a scam
        agent_reply = ""
        if is_scam:
            logger.info("Step 3: Generating honeypot reply...")
            agent_reply = PersonaGenerator.generate_reply(message)
            logger.info(f"Generated honeypot reply: {agent_reply[:50]}...")
        else:
            logger.info("Step 3: Skipping honeypot reply (not a scam)")

        # Step 4: Build final response
        logger.info("Step 4: Building final response...")
        response = HoneypotResponse(
            is_scam=is_scam,
            confidence=confidence,
            agent_reply=agent_reply,
            extracted_intelligence=extracted_intelligence,
            reasoning=reasoning,
        )

        logger.info(f"✓ Request completed successfully: is_scam={is_scam}, confidence={confidence:.3f}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict:
    """Root endpoint with API info."""
    return {
        "name": "Agentic Honeypot API",
        "version": "1.0.0",
        "endpoint": "/honeypot",
        "method": "POST",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
    )
