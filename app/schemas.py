"""Pydantic schemas for request and response validation."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union, Dict, Any


class MessageObject(BaseModel):
    """Message structure from hackathon format."""
    sender: str = Field(..., description="'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: int = Field(..., description="Epoch time in milliseconds")


class ConversationHistoryItem(BaseModel):
    """Single message in conversation history from hackathon."""
    sender: str = Field(..., description="'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: int = Field(..., description="Epoch time in milliseconds")


class MetadataObject(BaseModel):
    """Metadata from hackathon format."""
    channel: Optional[str] = Field(None, description="SMS / WhatsApp / Email / Chat")
    language: Optional[str] = Field(None, description="Language used")
    locale: Optional[str] = Field(None, description="Country or region")


class HoneypotRequest(BaseModel):
    """Request schema matching hackathon format exactly."""
    sessionId: str = Field(..., description="Unique session ID")
    message: Union[MessageObject, Dict[str, Any], str] = Field(..., description="Message object or string")
    conversationHistory: List[ConversationHistoryItem] = Field(default_factory=list, description="Previous messages")
    metadata: Optional[MetadataObject] = Field(None, description="Optional metadata")

    @field_validator('message')
    @classmethod
    def extract_message_text(cls, v):
        """Extract text from message object."""
        if isinstance(v, dict):
            return v.get('text', str(v))
        elif hasattr(v, 'text'):
            return v.text
        return str(v)


class ExtractedIntelligence(BaseModel):
    """Extracted scam indicators matching hackathon format."""
    bankAccounts: List[str] = Field(default_factory=list, description="Bank account numbers")
    upiIds: List[str] = Field(default_factory=list, description="UPI IDs")
    phishingLinks: List[str] = Field(default_factory=list, description="Phishing URLs")
    phoneNumbers: List[str] = Field(default_factory=list, description="Phone numbers")
    suspiciousKeywords: List[str] = Field(default_factory=list, description="Suspicious keywords detected")


class HoneypotResponse(BaseModel):
    """Response schema matching hackathon format."""
    status: str = Field(..., description="'success' or 'error'")
    reply: str = Field(..., description="Agent's response to the scammer")
    scamDetected: Optional[bool] = Field(None, description="Whether scam was detected")
    confidence: Optional[float] = Field(None, description="Confidence score (0.0-1.0)")
    extractedIntelligence: Optional[ExtractedIntelligence] = Field(None, description="Intelligence extracted")
    sessionId: Optional[str] = Field(None, description="Session ID")


class FinalResultPayload(BaseModel):
    """Payload for final result callback to GUVI."""
    sessionId: str = Field(..., description="Session ID")
    scamDetected: bool = Field(..., description="Whether scam was confirmed")
    totalMessagesExchanged: int = Field(..., description="Total messages in conversation")
    extractedIntelligence: ExtractedIntelligence = Field(..., description="All extracted intelligence")
    agentNotes: str = Field(..., description="Summary of scammer behavior")
