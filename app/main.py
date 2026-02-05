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
from app.schemas import HoneypotRequest, HoneypotResponse, ExtractedIntelligence
from app.scam_detector import ScamDetector
from app.persona import PersonaGenerator
from app.extractor import IntelligenceExtractor
from app.session import session_manager
from app.callback import send_final_result

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    try:
        Config.validate()
        logger.info("=" * 60)
        logger.info("🚀 Honeypot API Starting Up")
        logger.info("Configuration validated successfully")
        logger.info("NOTE: Render cold start may add 90s initial delay")
        logger.info("=" * 60)
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

    Returns instructions on how to properly use the honeypot endpoint with hackathon format.
    """
    return {
        "error": "Method Not Allowed",
        "message": "This endpoint only accepts POST requests with hackathon format",
        "usage": {
            "method": "POST",
            "url": "/honeypot",
            "headers": {
                "x-api-key": "honeypot-test-key-2026-secure",
                "Content-Type": "application/json"
            },
            "body": {
                "sessionId": "wertyu-dfghj-ertyui",
                "message": {
                    "sender": "scammer",
                    "text": "Your bank account will be blocked today. Verify immediately.",
                    "timestamp": 1770005528731
                },
                "metadata": {
                    "channel": "SMS",
                    "language": "English",
                    "locale": "IN"
                },
                "conversationHistory": []
            }
        },
        "example_curl": 'curl -X POST https://honeypoy-hcl-api-production.up.railway.app/honeypot -H "x-api-key: honeypot-test-key-2026-secure" -H "Content-Type: application/json" -d \'{"sessionId":"wertyu-dfghj-ertyui","message":{"sender":"scammer","text":"Your bank account will be blocked today. Verify immediately.","timestamp":1770005528731},"conversationHistory":[],"metadata":{"channel":"SMS","language":"English","locale":"IN"}}\'',
        "response_format": {
            "status": "success",
            "reply": "Why is my account being suspended?"
        },
        "note": "Agent responses must be human-like and avoid revealing scam detection",
        "documentation": "See POSTMAN_TESTING_GUIDE.md for detailed testing instructions"
    }


@app.post("/honeypot", response_model=HoneypotResponse)
async def honeypot(
    raw_request: Request,
    api_key: str = Depends(validate_api_key),
) -> HoneypotResponse:
    """
    Main honeypot endpoint matching hackathon specification.

    Detects scam intent, activates AI Agent, and extracts intelligence.
    Returns simple success/reply format as per hackathon requirements.

    Args:
        raw_request: Raw request object
        api_key: Validated API key from header

    Returns:
        HoneypotResponse with status and reply
    """
    import time
    start_time = time.time()

    try:
        # Parse request body
        try:
            body = await raw_request.json()
            logger.info(f"Received request for session: {body.get('sessionId', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            return HoneypotResponse(
                status="error",
                reply="Invalid JSON format"
            )

        # Validate against schema
        try:
            request = HoneypotRequest(**body)
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return HoneypotResponse(
                status="error",
                reply=f"Invalid request format: {str(e)}"
            )

        # Extract message text
        message = request.message
        if isinstance(message, str):
            message_text = message
        else:
            message_text = str(message)

        message_text = message_text.strip()

        if not message_text:
            return HoneypotResponse(
                status="error",
                reply="Message cannot be empty"
            )

        session_id = request.sessionId
        logger.info(f"Processing message in session {session_id}: {message_text[:100]}...")

        # Get or create session
        _, session = session_manager.get_or_create_session(
            session_id=session_id,
            api_key=api_key
        )

        # Add user message to history
        session.add_message("user", message_text)

        # STEP 1: Scam detection with keyword scoring + AI validation
        step_start = time.time()
        logger.info("STEP 1: Detecting scam intent...")

        # Quick keyword check first (instant)
        from app.scam_detector import ScamDetector
        keyword_score = ScamDetector.calculate_keyword_score(message_text)

        # Use AI detection for better accuracy (with keyword score as context)
        detection_result = ScamDetector.detect(message_text)
        is_scam = detection_result.get("is_scam", keyword_score > 0.5)
        confidence = detection_result.get("confidence", keyword_score)

        step_time = time.time() - step_start
        logger.info(f"STEP 1 completed in {step_time:.2f}s - Scam: {is_scam}, Confidence: {confidence:.2f}, Keyword: {keyword_score:.2f}")

        # STEP 2: Generate AI agent response (ALWAYS use AI for human-like replies)
        step_start = time.time()
        logger.info("STEP 2: Generating AI agent response...")

        # Always generate a response using AI
        try:
            context = session.get_context_for_llm(max_messages=5)
            agent_reply = PersonaGenerator.generate_reply(message_text, conversation_context=context)

            # Validate reply is not empty
            if not agent_reply or len(agent_reply.strip()) < 3:
                logger.warning("Generated reply too short, regenerating...")
                agent_reply = PersonaGenerator.generate_reply(message_text, conversation_context="")

        except Exception as e:
            logger.error(f"Error generating reply: {e}", exc_info=True)
            # Fallback responses that vary based on message content
            if "account" in message_text.lower() or "block" in message_text.lower():
                agent_reply = "wait what?? why would that happen"
            elif "verify" in message_text.lower() or "confirm" in message_text.lower():
                agent_reply = "hmm okay... how do i do that?"
            elif "urgent" in message_text.lower() or "immediate" in message_text.lower():
                agent_reply = "oh no is this serious??"
            else:
                agent_reply = "what do you mean? can u explain"

        step_time = time.time() - step_start
        logger.info(f"STEP 2 completed in {step_time:.2f}s - Reply: {agent_reply[:50]}...")

        # Add agent reply to history
        session.add_message("assistant", agent_reply)

        # STEP 3: Extract intelligence in background (don't wait for it)
        step_start = time.time()
        logger.info("STEP 3: Extracting intelligence...")
        try:
            intelligence_raw = IntelligenceExtractor.extract(message_text)
            session.update_intelligence(intelligence_raw)
            step_time = time.time() - step_start
            logger.info(f"STEP 3 completed in {step_time:.2f}s")
        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Intelligence extraction failed after {step_time:.2f}s: {e}")
            intelligence_raw = {}

        # Convert intelligence to hackathon format
        intelligence_hackathon = IntelligenceExtractor.convert_to_hackathon_format(
            session.get_accumulated_intelligence()
        )

        intelligence_obj = ExtractedIntelligence(**intelligence_hackathon)

        # Check if we should send final callback (async, don't block response)
        message_count = session.get_message_count()
        total_indicators = sum(len(v) for v in intelligence_hackathon.values())

        # Send final callback if we have significant intelligence (5+ indicators or 10+ messages)
        if total_indicators >= 5 or message_count >= 10:
            logger.info(f"Triggering final callback: {total_indicators} indicators, {message_count} messages")
            reasoning = "Urgency tactics and information requests detected"
            agent_notes = f"Scam tactics: {reasoning}. Total engagement: {message_count} messages."

            # Send in background (don't wait for response)
            try:
                send_final_result(
                    session_id=session_id,
                    scam_detected=True,
                    total_messages=message_count,
                    intelligence=intelligence_obj,
                    agent_notes=agent_notes
                )
            except Exception as e:
                logger.error(f"Callback failed: {e}")

        # Return response
        elapsed_time = time.time() - start_time
        logger.info(f"✓ Request completed in {elapsed_time:.2f}s")

        return HoneypotResponse(
            status="success",
            reply=agent_reply,
            scamDetected=True,
            confidence=confidence,
            extractedIntelligence=intelligence_obj,
            sessionId=session_id
        )

    except TimeoutError:
        elapsed_time = time.time() - start_time
        logger.error(f"Request timeout after {elapsed_time:.2f}s")
        return HoneypotResponse(
            status="error",
            reply="Request timeout"
        )
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Error after {elapsed_time:.2f}s: {e}", exc_info=True)
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return HoneypotResponse(
            status="error",
            reply="Internal server error"
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
