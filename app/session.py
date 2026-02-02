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
        for key in self.extracted_intelligence:
            if key in intelligence and intelligence[key]:
                self.extracted_intelligence[key].update(intelligence[key])

        logger.info(
            f"Session {self.session_id}: Updated intelligence - "
            f"Total indicators: {sum(len(v) for v in self.extracted_intelligence.values())}"
        )

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
            timeout_minutes: Session timeout in minutes

        Returns:
            True if session is expired
        """
        expiry_time = self.last_activity + timedelta(minutes=timeout_minutes)
        is_expired = datetime.now() > expiry_time
        if is_expired:
            logger.debug(f"Session {self.session_id}: Expired (inactive for {timeout_minutes}min)")
        return is_expired


class SessionManager:
    """Manages conversation sessions."""

    def __init__(self, session_timeout_minutes: int = 30):
        """
        Initialize the session manager.

        Args:
            session_timeout_minutes: How long to keep inactive sessions
        """
        self.sessions: Dict[str, Session] = {}
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
            logger.info(f"Session {session_id} expired, removing")
            del self.sessions[session_id]
            return None

        return session

    def get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, Session]:
        """
        Get existing session or create new one.

        Args:
            session_id: Optional existing session ID

        Returns:
            Tuple of (session_id, session)
        """
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

        # Create new session if not found or expired
        new_session_id = self.create_session()
        return new_session_id, self.sessions[new_session_id]

    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions."""
        expired_ids = [
            sid
            for sid, session in self.sessions.items()
            if session.is_expired(self.session_timeout_minutes)
        ]

        for sid in expired_ids:
            del self.sessions[sid]

        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired sessions")

    def get_active_session_count(self) -> int:
        """Get the number of active sessions."""
        self._cleanup_expired_sessions()
        count = len(self.sessions)
        logger.debug(f"Active sessions: {count}")
        return count


# Global session manager instance
session_manager = SessionManager(session_timeout_minutes=30)
