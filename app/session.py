"""Session management for conversation tracking."""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ConversationMessage:
    """Represents a single message in a conversation."""

    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """
        Initialize a conversation message.

        Args:
            role: Either 'user' (scammer) or 'assistant' (honeypot)
            content: The message content
            timestamp: When the message was sent
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict:
        """Convert message to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }


class Session:
    """Represents a conversation session."""

    def __init__(self, session_id: str):
        """
        Initialize a session.

        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.messages: List[ConversationMessage] = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.extracted_intelligence = {
            "bank_accounts": set(),
            "upi_ids": set(),
            "phone_numbers": set(),
            "phishing_urls": set(),
        }

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation.

        Args:
            role: Either 'user' or 'assistant'
            content: The message content
        """
        message = ConversationMessage(role, content)
        self.messages.append(message)
        self.last_activity = datetime.now()
        logger.info(
            f"Session {self.session_id}: Added {role} message "
            f"(total messages: {len(self.messages)})"
        )

    def get_conversation_history(self) -> List[dict]:
        """Get all messages in the conversation."""
        history = [msg.to_dict() for msg in self.messages]
        logger.debug(f"Session {self.session_id}: Retrieved {len(history)} messages")
        return history

    def get_message_count(self) -> int:
        """Get total number of messages exchanged in this session."""
        return len(self.messages)

    def get_context_for_llm(self, max_messages: int = 10) -> str:
        """
        Get recent conversation history formatted for LLM context.

        Args:
            max_messages: Maximum number of recent messages to include

        Returns:
            Formatted conversation history
        """
        recent_messages = self.messages[-max_messages:]
        context_lines = []

        for msg in recent_messages:
            role_label = "Scammer" if msg.role == "user" else "You (Honeypot)"
            context_lines.append(f"{role_label}: {msg.content}")

        context = "\n".join(context_lines)
        logger.debug(
            f"Session {self.session_id}: Generated LLM context with "
            f"{len(recent_messages)} messages"
        )
        return context

    def update_intelligence(self, intelligence: dict) -> None:
        """
        Update accumulated intelligence from this session.

        Args:
            intelligence: Dictionary with extracted indicators
        """
        try:
            if not intelligence or not isinstance(intelligence, dict):
                return

            for key in self.extracted_intelligence:
                if key in intelligence and intelligence[key]:
                    # Ensure it's iterable before updating
                    if isinstance(intelligence[key], (list, set, tuple)):
                        self.extracted_intelligence[key].update(intelligence[key])

            logger.info(
                f"Session {self.session_id}: Updated intelligence - "
                f"Total indicators: {sum(len(v) for v in self.extracted_intelligence.values())}"
            )
        except Exception as e:
            logger.error(f"Error updating intelligence for session {self.session_id}: {e}")

    def get_accumulated_intelligence(self) -> dict:
        """Get all intelligence accumulated during the session."""
        result = {
            key: list(value) for key, value in self.extracted_intelligence.items()
        }
        total = sum(len(v) for v in result.values())
        logger.debug(f"Session {self.session_id}: Retrieved {total} accumulated indicators")
        return result

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """
        Check if session has expired.

        Args:
            timeout_minutes: Session timeout in minutes (default 30)

        Returns:
            True if session is expired
        """
        expiry_time = self.last_activity + timedelta(minutes=timeout_minutes)
        is_expired = datetime.now() > expiry_time
        if is_expired:
            logger.debug(f"Session {self.session_id}: Expired (inactive for {timeout_minutes}min)")
        return is_expired

    def get_full_conversation_json(self) -> dict:
        """
        Get the complete conversation history in JSON format.

        Returns:
            Dictionary with session info, conversation history, and extracted intelligence
        """
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "ended_at": datetime.now().isoformat(),
            "total_messages": len(self.messages),
            "conversation_history": self.get_conversation_history(),
            "extracted_intelligence": self.get_accumulated_intelligence(),
        }

    @staticmethod
    def is_exit_message(message: str) -> bool:
        """
        Check if message contains exit keywords.

        Args:
            message: The user message to check

        Returns:
            True if message indicates user wants to exit
        """
        exit_words = {
            'exit', 'quit', 'bye', 'goodbye', 'end', 'stop',
            'close', 'terminate', 'finish', 'done', 'leave',
            'end conversation', 'end chat', 'stop conversation',
            'reset', 'clear', 'new conversation', 'start over',
            'restart', 'fresh start'
        }

        message_lower = message.lower().strip()

        # Check for exact matches or if message starts/ends with exit word
        for word in exit_words:
            if message_lower == word or message_lower.startswith(word + ' ') or message_lower.endswith(' ' + word):
                logger.info(f"Exit keyword detected: '{word}' in message: '{message[:50]}'")
                return True

        return False


class SessionManager:
    """Manages conversation sessions."""

    def __init__(self, session_timeout_minutes: int = 30):
        """
        Initialize the session manager.

        Args:
            session_timeout_minutes: How long to keep inactive sessions (default 30 minutes)
        """
        self.sessions: Dict[str, Session] = {}
        self.api_key_sessions: Dict[str, str] = {}  # Maps API key to session_id
        self.session_timeout_minutes = session_timeout_minutes
        logger.info(f"SessionManager initialized with {session_timeout_minutes}min timeout")

    def create_session(self) -> str:
        """
        Create a new conversation session.

        Returns:
            Unique session ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = Session(session_id)
        logger.info(f"Created new session: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get an existing session.

        Args:
            session_id: The session identifier

        Returns:
            Session object or None if not found/expired
        """
        self._cleanup_expired_sessions()

        session = self.sessions.get(session_id)
        if session and session.is_expired(self.session_timeout_minutes):
            logger.info(f"Session {session_id} expired, extracting and removing")

            # Extract intelligence before deletion
            if len(session.messages) > 0:
                try:
                    self._extract_from_conversation(session)
                    conversation_json = session.get_full_conversation_json()
                    logger.info(f"Extracted intelligence from expired session {session_id}")
                except Exception as e:
                    logger.error(f"Error extracting from expired session {session_id}: {e}")

            del self.sessions[session_id]
            return None

        return session

    def get_or_create_session(self, session_id: Optional[str] = None, api_key: Optional[str] = None) -> tuple[str, Session]:
        """
        Get existing session or create new one.
        Supports automatic session tracking by API key when session_id is not provided.

        Args:
            session_id: Optional existing session ID (explicit mode)
            api_key: Optional API key for automatic session tracking

        Returns:
            Tuple of (session_id, session)
        """
        # Mode 1: Explicit session_id provided (priority)
        if session_id:
            session = self.get_session(session_id)
            if session:
                logger.info(
                    f"Retrieved existing session: {session_id} "
                    f"(messages: {len(session.messages)})"
                )
                return session_id, session
            else:
                logger.warning(f"Session {session_id} not found or expired, creating new session")

        # Mode 2: Automatic session tracking by API key
        elif api_key:
            # Check if API key has an active session
            if api_key in self.api_key_sessions:
                tracked_session_id = self.api_key_sessions[api_key]
                session = self.get_session(tracked_session_id)
                if session:
                    logger.info(
                        f"Auto-retrieved session for API key: {tracked_session_id} "
                        f"(messages: {len(session.messages)})"
                    )
                    return tracked_session_id, session
                else:
                    # Session expired, remove from tracking
                    logger.info(f"Auto-tracked session expired for API key")
                    del self.api_key_sessions[api_key]

        # Create new session if not found or expired
        new_session_id = self.create_session()

        # Track by API key if provided
        if api_key and not session_id:
            self.api_key_sessions[api_key] = new_session_id
            logger.info(f"Auto-tracking new session {new_session_id} for API key")

        return new_session_id, self.sessions[new_session_id]

    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions and extract intelligence from them."""
        expired_ids = [
            sid
            for sid, session in self.sessions.items()
            if session.is_expired(self.session_timeout_minutes)
        ]

        for sid in expired_ids:
            session = self.sessions[sid]
            message_count = len(session.messages)

            # Extract intelligence from expired session if it has messages
            if message_count > 0:
                logger.info(f"Extracting intelligence from expired session {sid} with {message_count} messages")
                try:
                    self._extract_from_conversation(session)
                    # Save conversation JSON before deletion
                    conversation_json = session.get_full_conversation_json()
                    logger.info(f"Saved conversation data from expired session {sid}")
                except Exception as e:
                    logger.error(f"Error extracting from expired session {sid}: {e}")

            del self.sessions[sid]

        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired sessions")

    def get_active_session_count(self) -> int:
        """Get the number of active sessions."""
        self._cleanup_expired_sessions()
        count = len(self.sessions)
        logger.debug(f"Active sessions: {count}")
        return count

    def clear_api_key_session(self, api_key: str) -> None:
        """
        Clear session tracking for an API key to start fresh conversation.

        Args:
            api_key: The API key to clear session for
        """
        if api_key in self.api_key_sessions:
            old_session_id = self.api_key_sessions[api_key]
            del self.api_key_sessions[api_key]
            logger.info(f"Cleared API key tracking (old session: {old_session_id})")

    def end_session(self, session_id: str, extract_intelligence: bool = True) -> Optional[dict]:
        """
        End and remove a session, optionally extracting final intelligence.

        Args:
            session_id: The session identifier to end
            extract_intelligence: Whether to extract intelligence from full conversation

        Returns:
            Dictionary with conversation JSON and extracted intelligence if successful, None otherwise
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            message_count = len(session.messages)

            # Get full conversation data before deletion
            conversation_json = session.get_full_conversation_json()

            # Extract intelligence from full conversation if requested
            final_extraction = None
            if extract_intelligence and message_count > 0:
                logger.info(f"Extracting intelligence from session {session_id} with {message_count} messages")
                final_extraction = self._extract_from_conversation(session)

            # Delete the session
            del self.sessions[session_id]
            logger.info(f"Session {session_id} ended (had {message_count} messages)")

            return {
                "conversation_data": conversation_json,
                "final_extraction": final_extraction,
            }
        else:
            logger.warning(f"Attempted to end non-existent session: {session_id}")
            return None

    def _extract_from_conversation(self, session: Session) -> dict:
        """
        Extract intelligence from the entire conversation history.

        Args:
            session: The session to extract from

        Returns:
            Dictionary with extracted intelligence
        """
        from app.extractor import IntelligenceExtractor

        # Combine all conversation messages into one text for extraction
        full_conversation = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in session.messages
        ])

        # Extract intelligence from the full conversation
        extracted = IntelligenceExtractor.extract(full_conversation)
        logger.info(
            f"Final extraction from session {session.session_id}: "
            f"{sum(len(v) for v in extracted.values())} total indicators"
        )

        return extracted


# Global session manager instance with 30-minute timeout
session_manager = SessionManager(session_timeout_minutes=30)
