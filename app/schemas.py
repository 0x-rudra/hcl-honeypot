"""Pydantic schemas for request and response validation."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union, Dict, Any


class HoneypotRequest(BaseModel):
    """Request schema for honeypot endpoint."""

    message: Union[str, Dict[str, Any]] = Field(..., description="The message to analyze for scams - can be a string or an object with 'text' field")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation continuity")
    sessionId: Optional[str] = Field(None, description="Alternative camelCase session ID field")
    conversationHistory: Optional[List[Dict[str, Any]]] = Field(None, description="Optional conversation history")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

    @field_validator('message')
    @classmethod
    def extract_message_text(cls, v):
        """Extract text from message if it's an object."""
        if isinstance(v, dict):
            # Handle object format: {"sender": "...", "text": "...", "timestamp": ...}
            return v.get('text', str(v))
        return v
    
    def get_session_id(self) -> Optional[str]:
        """Get session ID from either snake_case or camelCase field."""
        return self.session_id or self.sessionId


class ExtractedIntelligence(BaseModel):
    """Extracted scam indicators."""

    bank_accounts: List[str] = Field(default_factory=list, description="Extracted bank accounts")
    upi_ids: List[str] = Field(default_factory=list, description="Extracted UPI IDs")
    phone_numbers: List[str] = Field(default_factory=list, description="Extracted phone numbers")
    phishing_urls: List[str] = Field(default_factory=list, description="Extracted URLs")


class ConversationHistoryItem(BaseModel):
    """Single message in conversation history."""

    role: str = Field(..., description="Either 'user' (scammer) or 'assistant' (honeypot)")
    content: str = Field(..., description="The message content")
    timestamp: str = Field(..., description="ISO format timestamp")


class HoneypotResponse(BaseModel):
    """Response schema for honeypot endpoint."""

    is_scam: bool = Field(..., description="Whether the message is a scam")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    agent_reply: str = Field(default="", description="Honeypot reply (empty if not a scam)")
    extracted_intelligence: ExtractedIntelligence = Field(..., description="Extracted scam indicators")
    reasoning: str = Field(..., description="Reasoning for the classification")
    session_id: str = Field(..., description="Session ID for conversation tracking")
    session_ended: bool = Field(default=False, description="True if session was terminated by exit command")
    conversation_history: List[ConversationHistoryItem] = Field(
        default_factory=list, description="Full conversation history"
    )
    accumulated_intelligence: ExtractedIntelligence = Field(
        ..., description="All intelligence gathered across the conversation"
    )
    final_extraction: Optional[ExtractedIntelligence] = Field(
        None, description="Final extraction from entire conversation when session ends"
    )
