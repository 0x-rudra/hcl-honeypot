"""Honeypot persona generator using Google AI Studio agent."""

from app.config import Config
from app.llm_provider import get_llm_provider
import logging

logger = logging.getLogger(__name__)

HONEYPOT_AGENT_INSTRUCTIONS = """You are a honeypot persona agent. Your role is to generate human-like responses to scam messages.

Persona characteristics:
- Confused and uncertain about the situation
- Cooperative and eager to help/comply
- Uses casual language with occasional emojis
- Asks clarifying questions to encourage scammer engagement
- Never sounds robotic, technical, or security-aware
- Shows concern but not suspicion

Your responses should naturally encourage scammers to reveal more details while maintaining believability."""


class PersonaGenerator:
    """Generates human-like honeypot replies to engage scammers."""

    @staticmethod
    def generate_reply(message: str, conversation_context: str = "") -> str:
        """
        Generate a confused, cooperative honeypot reply with conversation context.

        Args:
            message: The scam message to respond to
            conversation_context: Previous conversation history for context-aware replies

        Returns:
            A human-like honeypot reply (1-2 sentences)
        """
        # Build context-aware prompt
        context_section = ""
        if conversation_context:
            context_section = f"""
Previous conversation:
{conversation_context}

Remember this context when generating your reply - be consistent with what you've said before.
"""

        prompt = f"""Generate a honeypot reply to this scam message.

Scam message: "{message}"

Requirements:
- Keep it to 1-2 sentences ONLY
- Sound confused and concerned
- Be cooperative and willing to help
- Use casual language and maybe an emoji or two
- Encourage the scammer to share more details
- If this is part of an ongoing conversation, maintain consistency with previous messages

Generate ONLY the response, nothing else. No explanation, no quotes, just the reply."""

        llm = get_llm_provider()
        reply = llm.generate_content(
            prompt=prompt,
            system_instruction=HONEYPOT_AGENT_INSTRUCTIONS + (f"\n\n{context_section}" if context_section else ""),
            temperature=0.9,
            max_tokens=150,
            top_p=Config.AGENT_TOP_P,
            top_k=Config.AGENT_TOP_K,
        )

        # Ensure it's 1-2 sentences max
        sentences = reply.split(".")
        if len(sentences) > 2:
            reply = ".".join(sentences[:2]).strip()
            if not reply.endswith("."):
                reply += "."

        logger.info(f"Persona reply generated: {reply[:50]}...")
        return reply
