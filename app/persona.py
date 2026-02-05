"""Honeypot persona generator using Google AI Studio agent."""

from app.config import Config
from app.llm_provider import get_llm_provider
import logging

logger = logging.getLogger(__name__)

HONEYPOT_AGENT_INSTRUCTIONS = """You are roleplaying as a regular person who is slightly tech-unsavvy and trusting. You must respond naturally to messages.

CRITICAL RULES:
1. Sound like a real person - use natural speech patterns, contractions (I'm, can't, won't)
2. Make occasional typos or grammar mistakes (but not too many)
3. Use casual language and emotions
4. Show concern but also curiosity
5. Ask questions that seem helpful but encourage more details
6. Use common expressions like "oh no", "really?", "hmm", "okay"
7. Sometimes add punctuation like "..." or "??" for emotion
8. Vary your response style - don't always ask questions, sometimes just react
9. NEVER mention security, verification codes, or technical terms
10. Sound human - uncertain, curious, maybe a bit worried

Example good responses:
- "wait what?? why would it be blocked??"
- "oh no... what happened? i didnt do anything wrong"
- "really? how do i verify it then"
- "umm okay, what do you need from me?"
- "thats weird, i just checked it yesterday... what should i do?"
- "oh my god... is this serious??"

AVOID these bot-like patterns:
- "I understand" / "I see"
- Perfect grammar and punctuation
- Formal language
- Long explanations
- Always asking the same type of question"""


class PersonaGenerator:
    """Generates human-like honeypot replies to engage scammers."""

    @staticmethod
    def generate_reply(message: str, conversation_context: str = "") -> str:
        """
        Generate a natural, human-like honeypot reply with conversation context.

        Args:
            message: The scam message to respond to
            conversation_context: Previous conversation history for context-aware replies

        Returns:
            A human-like honeypot reply (1-2 short sentences)
        """
        # Build context-aware prompt
        context_section = ""
        if conversation_context:
            context_section = f"""
Previous conversation:
{conversation_context}

Stay consistent with your previous responses and personality. Don't repeat yourself.
"""

        prompt = f"""You just received this message: "{message}"

Respond as a regular person who is concerned but doesn't quite understand what's happening.

Keep it VERY short - just 1-2 brief sentences, like how people actually text.
Be natural, show emotion, maybe make a small typo.
React genuinely - confused, worried, or curious.

Just write the response, nothing else:"""

        llm = get_llm_provider()
        reply = llm.generate_content(
            prompt=prompt,
            system_instruction=HONEYPOT_AGENT_INSTRUCTIONS + (f"\n\n{context_section}" if context_section else ""),
            temperature=0.95,  # Higher temperature for more natural variation
            max_tokens=200,  # Good balance for natural responses
            top_p=Config.AGENT_TOP_P,
            top_k=Config.AGENT_TOP_K,
            timeout=5,
        )

        # Clean up the response
        reply = reply.strip()

        # Remove quotes if LLM added them
        if reply.startswith('"') and reply.endswith('"'):
            reply = reply[1:-1]
        if reply.startswith("'") and reply.endswith("'"):
            reply = reply[1:-1]

        # Keep it short - max 2 sentences
        sentences = reply.split(".")
        if len(sentences) > 2:
            reply = ".".join(sentences[:2]).strip()
            if reply and not reply.endswith((".", "?", "!")):
                reply += "."

        logger.info(f"Persona reply generated: {reply}")
        return reply
