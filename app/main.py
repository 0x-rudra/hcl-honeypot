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
from app.schemas import HoneypotRequest, HoneypotResponse, ExtractedIntelligence, ConversationHistoryItem
from app.scam_detector import ScamDetector
from app.persona import PersonaGenerator
from app.extractor import IntelligenceExtractor
from app.session import session_manager

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
    Main honeypot endpoint with conversation support.

    Detects scams, generates context-aware honeypot replies, and extracts intelligence.

    Args:
        request: Request containing the message and optional session_id
        api_key: Validated API key from header

    Returns:
        Structured response with scam detection results and conversation history
    """
    try:
        message = request.message.strip()

        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty",
            )

        # Get or create session
        session_id, session = session_manager.get_or_create_session(request.session_id)
        logger.info(f"Processing message in session {session_id}: {message[:50]}...")

        # Check for exit command
        session_ended = False
        if session.is_exit_message(message):
            logger.info(f"Exit command detected in session {session_id}")
            session_ended = True

            # Add user message to conversation history before ending
            session.add_message("user", message)

            # Get final conversation data before deleting session
            conversation_history = [
                ConversationHistoryItem(**msg)
                for msg in session.get_conversation_history()
            ]
            accumulated_intelligence = ExtractedIntelligence(
                **session.get_accumulated_intelligence()
            )

            # End the session
            session_manager.end_session(session_id)

            # Return final response with session ended flag
            return HoneypotResponse(
                is_scam=False,
                confidence=0.0,
                agent_reply="Goodbye! Session has been ended. Thank you for using the Honeypot API.",
                extracted_intelligence=ExtractedIntelligence(),
                reasoning="User requested to end the conversation",
                session_id=session_id,
                session_ended=True,
                conversation_history=conversation_history,
                accumulated_intelligence=accumulated_intelligence,
            )

        # Add user message to conversation history
        session.add_message("user", message)

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

        # Update session intelligence
        session.update_intelligence(intelligence)

        # Step 3: Generate context-aware honeypot reply if it's a scam
        agent_reply = ""
        if is_scam:
            logger.info("Step 3: Generating context-aware honeypot reply...")
            conversation_context = session.get_context_for_llm(max_messages=10)
            agent_reply = PersonaGenerator.generate_reply(message, conversation_context)
            logger.info(f"Generated honeypot reply: {agent_reply[:50]}...")

            # Add assistant reply to conversation history
            session.add_message("assistant", agent_reply)
        else:
            logger.info("Step 3: Skipping honeypot reply (not a scam)")

        # Get accumulated intelligence across the conversation
        accumulated_intelligence = ExtractedIntelligence(
            **session.get_accumulated_intelligence()
        )

        # Get conversation history
        conversation_history = [
            ConversationHistoryItem(**msg)
            for msg in session.get_conversation_history()
        ]

        # Step 4: Build final response
        logger.info("Step 4: Building final response...")
        response = HoneypotResponse(
            is_scam=is_scam,
            confidence=confidence,
            agent_reply=agent_reply,
            extracted_intelligence=extracted_intelligence,
            reasoning=reasoning,
            session_id=session_id,
            session_ended=False,
            conversation_history=conversation_history,
            accumulated_intelligence=accumulated_intelligence,
        )

        logger.info(
            f"✓ Request completed successfully: session={session_id}, "
            f"is_scam={is_scam}, confidence={confidence:.3f}, "
            f"total_messages={len(conversation_history)}, "
            f"total_intelligence={sum(len(v) for v in accumulated_intelligence.dict().values())}"
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing request: {error_msg}")

        # Check if it's a quota/rate limit error
        if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="API quota exceeded. Please try again later or check your Gemini API quota at https://ai.google.dev/gemini-api/docs/rate-limits",
            )

        # Generic error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {error_msg[:100]}",
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
