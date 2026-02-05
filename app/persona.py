"""Honeypot persona generator using Google AI Studio agent."""

from typing import List
from app.llm_provider import get_llm_provider
import logging

logger = logging.getLogger(__name__)

HONEYPOT_AGENT_INSTRUCTIONS = """You are a regular person receiving a text message. Write natural, casual text responses.

KEY STYLE RULES:
1. Keep it SHORT - 5 to 15 words maximum
2. Write like you're texting a stranger
3. Use lowercase mostly
4. Use contractions: i'm, can't, what's, that's, dont
5. Add casual fillers: oh, hmm, wait, huh, um, like
6. Simple punctuation: . ? ! ...
7. React naturally - confusion, curiosity, or concern

EXAMPLE NATURAL RESPONSES:
"wait what? why is my account blocked"
"oh no... what happened?"
"how do i fix this"
"ok what do i need to do"
"really? that seems weird"
"is this serious??"
"can u help me with this"
"hmm idk what to do"
"ok sure, what info"
"why tho?"

DO NOT:
- Say "Thank you for your message"
- Be overly polite or formal
- Write long explanations
- Use perfect grammar
- Repeat the same words over and over

Write naturally like a real person texting."""


class PersonaGenerator:
    """Generates human-like honeypot replies to engage scammers."""

    @staticmethod
    def generate_reply(message: str, conversation_context: str = "", recent_replies: List[str] = None) -> str:
        """
        Generate a natural, human-like honeypot reply with conversation context.

        Args:
            message: The scam message to respond to
            conversation_context: Previous conversation history for context-aware replies
            recent_replies: List of recent agent replies to avoid repetition

        Returns:
            A human-like honeypot reply (1-2 short sentences)
        """
        recent_replies = recent_replies or []

        # Build context-aware prompt
        context_section = ""
        if conversation_context:
            context_section = f"""
Previous conversation:
{conversation_context}

Stay consistent with your previous responses and personality.
"""

        # Add recent replies to avoid repetition
        avoid_section = ""
        if recent_replies:
            recent_list = "\n".join([f"- {r}" for r in recent_replies[-3:]])
            avoid_section = f"""
DO NOT repeat these previous responses:
{recent_list}

Your new response must be completely DIFFERENT in words and structure.
"""

        # Extract key words from message for context-aware response
        message_lower = message.lower()
        response_hints = ""
        if "account" in message_lower or "block" in message_lower:
            response_hints = "Show surprise about account issue."
        elif "verify" in message_lower or "confirm" in message_lower:
            response_hints = "Ask what needs to be verified."
        elif "urgent" in message_lower or "immediate" in message_lower:
            response_hints = "React to the urgency."
        elif "money" in message_lower or "pay" in message_lower or "payment" in message_lower:
            response_hints = "Ask about the payment."
        elif "otp" in message_lower or "code" in message_lower:
            response_hints = "Be slightly confused about the code."
        elif "click" in message_lower or "link" in message_lower:
            response_hints = "Ask what the link is for."
        else:
            response_hints = "React naturally to what they said."

        prompt = f"""Text received: "{message}"

{response_hints} Write a short, natural text response (5-15 words). Be casual and react like a real person would.

Your response:"""

        import random
        # Add randomization for variety
        random_temp = random.uniform(0.8, 0.95)
        random_top_p = random.uniform(0.85, 0.95)
        random_top_k = random.randint(40, 55)

        llm = get_llm_provider()
        reply = llm.generate_content(
            prompt=prompt,
            system_instruction=HONEYPOT_AGENT_INSTRUCTIONS + context_section + avoid_section,
            temperature=random_temp,
            max_tokens=50,  # Shorter to prevent rambling
            top_p=random_top_p,
            top_k=random_top_k,
            timeout=5,
        )

        # Clean up the response
        reply = reply.strip()

        # Remove quotes if LLM added them
        if reply.startswith('"') and reply.endswith('"'):
            reply = reply[1:-1]
        if reply.startswith("'") and reply.endswith("'"):
            reply = reply[1:-1]

        # Remove any markdown or formatting
        reply = reply.replace('*', '').replace('_', '').strip()

        # If too long, take first sentence/phrase
        if len(reply) > 80:
            # Try to break at natural points
            for delimiter in ['. ', '? ', '! ', ', ']:
                if delimiter in reply:
                    reply = reply.split(delimiter)[0] + delimiter.strip()
                    break
            # If still too long, just truncate
            if len(reply) > 80:
                reply = reply[:77] + '...'

        logger.info(f"Persona reply generated: {reply}")
        return reply
