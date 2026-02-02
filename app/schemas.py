"""Pydantic schemas for request and response validation."""

from pydantic import BaseModel, Field
from typing import List


class HoneypotRequest(BaseModel):
    """Request schema for honeypot endpoint."""

    message: str = Field(..., description="The message to analyze for scams")


class ExtractedIntelligence(BaseModel):
    """Extracted scam indicators."""

    bank_accounts: List[str] = Field(default_factory=list, description="Extracted bank accounts")
    upi_ids: List[str] = Field(default_factory=list, description="Extracted UPI IDs")
    phone_numbers: List[str] = Field(default_factory=list, description="Extracted phone numbers")
    phishing_urls: List[str] = Field(default_factory=list, description="Extracted URLs")


class HoneypotResponse(BaseModel):
    """Response schema for honeypot endpoint."""

    is_scam: bool = Field(..., description="Whether the message is a scam")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    agent_reply: str = Field(default="", description="Honeypot reply (empty if not a scam)")
    extracted_intelligence: ExtractedIntelligence = Field(..., description="Extracted scam indicators")
    reasoning: str = Field(..., description="Reasoning for the classification")
