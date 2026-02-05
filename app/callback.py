"""Callback module for sending final results to GUVI evaluation endpoint."""

import requests
import logging
from app.schemas import FinalResultPayload, ExtractedIntelligence

logger = logging.getLogger(__name__)

GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"


def send_final_result(
    session_id: str,
    scam_detected: bool,
    total_messages: int,
    intelligence: ExtractedIntelligence,
    agent_notes: str
) -> bool:
    """
    Send final extraction results to GUVI evaluation endpoint.

    Args:
        session_id: Session ID
        scam_detected: Whether scam was confirmed
        total_messages: Total messages exchanged
        intelligence: Extracted intelligence object
        agent_notes: Summary of scammer behavior

    Returns:
        True if callback succeeded, False otherwise
    """
    try:
        payload = FinalResultPayload(
            sessionId=session_id,
            scamDetected=scam_detected,
            totalMessagesExchanged=total_messages,
            extractedIntelligence=intelligence,
            agentNotes=agent_notes
        )

        logger.info(f"Sending final result callback for session {session_id}")
        logger.debug(f"Payload: {payload.model_dump()}")

        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload.model_dump(),
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        response.raise_for_status()
        logger.info(f"Final result callback successful for session {session_id}: {response.status_code}")
        return True

    except requests.exceptions.Timeout:
        logger.error(f"Callback timeout for session {session_id}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Callback failed for session {session_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in callback for session {session_id}: {e}")
        return False
