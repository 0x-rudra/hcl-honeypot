"""Main FastAPI application for Honeypot API."""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.warning("API will not function properly without GEMINI_API_KEY")

    yield

    # Shutdown (if needed in future)
    logger.info("Application shutting down")


# Create FastAPI app
app = FastAPI(
    title="Agentic Honeypot API",
    description="Detects scams, generates honeypot replies, and extracts scam intelligence",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests and add timing information."""
    # Skip logging for health checks to reduce noise
    is_health_check = request.url.path in ["/health", "/"]

    start_time = time.time()

    # Log incoming request (except health checks)
    if not is_health_check:
        logger.info(f"Incoming request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)

        # Log completion (except health checks)
        if not is_health_check:
            logger.info(f"Request completed in {process_time:.3f}s with status {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with user-friendly messages."""
    errors = exc.errors()
    logger.error(f"Validation error: {errors}")

    # Extract field names that failed validation
    missing_fields = [err['loc'][-1] for err in errors if err['type'] == 'missing']

    if missing_fields:
        detail = f"Missing required field(s): {', '.join(missing_fields)}"
    else:
        detail = "Invalid request body format"

    return JSONResponse(
        status_code=422,
        content={
            "detail": detail,
            "errors": errors,
            "example_request": {
                "message": "Hello, I have a business opportunity for you"
            }
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to ensure proper JSON responses."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred. Please try again.",
        },
    )


@app.post("/test")
async def test_endpoint(raw_request: Request, api_key: str = Depends(validate_api_key)) -> dict:
    """
    Simple test endpoint for hackathon validation.
    Accepts any valid JSON and returns a success response.
    """
    try:
        body = await raw_request.json()
        logger.info(f"Test endpoint received: {body}")

        return {
            "status": "success",
            "message": "API is working correctly",
            "received": body,
            "authenticated": True
        }
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/honeypot")
async def honeypot_info() -> dict:
    """
    GET endpoint for /honeypot that provides usage information.

    Returns instructions on how to properly use the honeypot endpoint.
    """
    return {
        "error": "Method Not Allowed",
        "message": "This endpoint only accepts POST requests",
        "usage": {
            "method": "POST",
            "url": "/honeypot",
            "headers": {
                "x-api-key": "your-api-key-here",
                "Content-Type": "application/json"
            },
            "body": {
                "message": "Your message to analyze",
                "session_id": "optional-session-id"
            }
        },
        "example_curl": 'curl -X POST https://hcl-honeypot-api.onrender.com/honeypot -H "x-api-key: your-key" -H "Content-Type: application/json" -d \'{"message": "Test message"}\'',
        "documentation": "See POSTMAN_TESTING_GUIDE.md for detailed testing instructions"
    }


@app.post("/honeypot", response_model=HoneypotResponse)
async def honeypot(
    raw_request: Request,
    api_key: str = Depends(validate_api_key),
) -> HoneypotResponse:
    """
    Main honeypot endpoint with conversation support.

    Detects scams, generates context-aware honeypot replies, and extracts intelligence.

    Args:
        raw_request: Raw request object for flexible body parsing
        api_key: Validated API key from header

    Returns:
        Structured response with scam detection results and conversation history
    """
    try:
        # Parse request body with better error handling
        try:
            body = await raw_request.json()
            logger.info(f"Received body: {body}")
        except Exception as e:
            logger.error(f"Failed to parse JSON body: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body. Expected format: {\"message\": \"your message here\"}",
            )

        # Validate request against schema
        try:
            request = HoneypotRequest(**body)
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid request format: {str(e)}. Required field: 'message'",
            )

        # Input validation
        if not request.message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message field is required",
            )

        message = request.message.strip()

        if not message or len(message) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty",
            )

        # Validate message length (max 10000 characters for safety)
        if len(message) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message too long (max 10000 characters)",
            )

        # Validate session_id format if provided
        if request.session_id and len(request.session_id) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session_id format",
            )

        # Get or create session (supports automatic tracking by API key)
        session_id, session = session_manager.get_or_create_session(
            session_id=request.session_id,
            api_key=api_key  # Enable automatic session tracking
        )
        logger.info(f"Processing message in session {session_id}: {message[:50]}...")

        # Check for exit command
        session_ended = False
        final_extraction_data = None
        if session.is_exit_message(message):
            logger.info(f"Exit command detected in session {session_id}")
            session_ended = True

            # Clear API key tracking so next message starts fresh
            session_manager.clear_api_key_session(api_key)

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

            # End the session and extract final intelligence from full conversation
            end_result = session_manager.end_session(session_id, extract_intelligence=True)
            if end_result and end_result.get("final_extraction"):
                final_extraction_data = end_result["final_extraction"]
                logger.info(f"Final extraction completed: {sum(len(v) for v in final_extraction_data.values())} indicators")

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
                final_extraction=ExtractedIntelligence(**final_extraction_data) if final_extraction_data else None,
            )

        # Add user message to conversation history
        session.add_message("user", message)

        # Step 1: Detect if it's a scam
        logger.info("Step 1: Starting scam detection...")
        detection_result = ScamDetector.detect(message)

        # Validate detection result
        if not detection_result or not isinstance(detection_result, dict):
            raise ValueError("Invalid detection result")

        is_scam = detection_result.get("is_scam", False)
        confidence = detection_result.get("confidence", 0.0)
        reasoning = detection_result.get("reasoning", "Unable to determine classification")

        # Ensure confidence is valid
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            confidence = 0.0

        logger.info(f"Scam detection result: is_scam={is_scam}, confidence={confidence:.3f}")

        # Step 2: Extract intelligence from the message
        logger.info("Step 2: Extracting intelligence...")
        intelligence = IntelligenceExtractor.extract(message)

        # Validate intelligence result
        if not isinstance(intelligence, dict):
            intelligence = {}

        current_extraction = ExtractedIntelligence(
            bank_accounts=intelligence.get("bank_accounts", []) if intelligence else [],
            upi_ids=intelligence.get("upi_ids", []) if intelligence else [],
            phone_numbers=intelligence.get("phone_numbers", []) if intelligence else [],
            phishing_urls=intelligence.get("phishing_urls", []) if intelligence else [],
        )

        total_indicators = sum(len(v) for v in intelligence.values()) if intelligence else 0
        logger.info(f"Intelligence extracted: {total_indicators} total indicators")

        # Update session intelligence
        session.update_intelligence(intelligence)

        # Get accumulated intelligence across the conversation (including current message)
        accumulated_intelligence = ExtractedIntelligence(
            **session.get_accumulated_intelligence()
        )

        # Step 3: Generate context-aware honeypot reply if it's a scam
        agent_reply = ""
        if is_scam:
            try:
                logger.info("Step 3: Generating context-aware honeypot reply...")
                conversation_context = session.get_context_for_llm(max_messages=10)
                agent_reply = PersonaGenerator.generate_reply(message, conversation_context)

                # Validate reply
                if not agent_reply or not isinstance(agent_reply, str):
                    agent_reply = "I'm interested. Could you tell me more?"
                    logger.warning("Generated empty reply, using fallback")

                logger.info(f"Generated honeypot reply: {agent_reply[:50]}...")

                # Add assistant reply to conversation history
                session.add_message("assistant", agent_reply)
            except Exception as e:
                logger.error(f"Error generating reply: {e}")
                # Use fallback reply if generation fails
                agent_reply = "That sounds interesting. Can you provide more details?"
                session.add_message("assistant", agent_reply)
        else:
            logger.info("Step 3: Skipping honeypot reply (not a scam)")

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
            extracted_intelligence=accumulated_intelligence,  # Show all accumulated intelligence
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
            f"total_intelligence={sum(len(v) for v in accumulated_intelligence.model_dump().values())}"
        )
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is (already properly formatted)
        raise
    except ValueError as e:
        # Handle validation errors
        error_msg = str(e)
        logger.error(f"Validation error: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {error_msg}",
        )
    except KeyError as e:
        # Handle missing data errors
        logger.error(f"Missing required data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error: Missing required data",
        )
    except TimeoutError:
        # Handle timeout errors
        logger.error("Request timeout")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request timeout: The operation took too long to complete",
        )
    except Exception as e:
        # Catch all other errors
        error_msg = str(e)
        logger.error(f"Unexpected error processing request: {error_msg}", exc_info=True)

        # Check if it's a quota/rate limit error
        if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="API quota exceeded. Please try again later.",
            )

        # Generic error with safe message (don't expose internal details)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while processing request",
        )


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint to verify API status.

    Returns system health information including configuration status.
    """
    try:
        # Check if Gemini API key is configured
        config_valid = bool(Config.GEMINI_API_KEY)

        # Check active sessions
        active_sessions = session_manager.get_active_session_count()

        health_status = {
            "status": "healthy" if config_valid else "degraded",
            "timestamp": time.time(),
            "gemini_configured": config_valid,
            "active_sessions": active_sessions,
        }

        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }


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
