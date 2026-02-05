"""Honeypot persona generator using Google AI Studio agent."""

from app.config import Config
from app.llm_provider import get_llm_provider
import logging

logger = logging.getLogger(__name__)

HONEYPOT_AGENT_INSTRUCTIONS = """You are roleplaying as a real person texting naturally. You're slightly tech-unsavvy and trusting.

CRITICAL RULES:
1. Write EXACTLY like texting - short, casual, natural
2. Use contractions: I'm, can't, don't, what's, that's
3. Add emotion naturally: oh, hmm, wow, wait, huh
4. Make small typos occasionally: "recieved", "wierd", "ment"
5. Use informal punctuation: ..., ??, !!
6. Vary your style:
   - Sometimes question: "why tho?"
   - Sometimes react: "oh no..."
   - Sometimes comply: "okay i can do that"
7. Show vulnerability and trust
8. Be curious but not suspicious
9. NEVER use formal language or perfect grammar
10. Each response MUST be different - never repeat patterns

GOOD examples (varied styles):
- "wait what?? why would it be blocked"
- "oh no... what happened?"
- "okay how do i fix it"
- "hmm idk, what should i do then"
- "really? thats wierd"
- "ok sure, what info do you need"
- "omg is this serious??"
- "alright... so what now?"
- "can u tell me more about this"

BAD (avoid these bot patterns):
- "Thank you for your message" (TOO FORMAL)
- "I understand your concern" (TOO POLITE)
- "Could you please provide" (TOO PROFESSIONAL)
- Perfect sentences with correct punctuation
- Same question patterns every time

Be UNPREDICTABLE - vary tone, length, emotion each time!"""


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

        prompt = f"""Incoming text message: "{message}"

You're a regular person receiving this. Respond naturally like you're texting.

CRITICAL: Make this response UNIQUE and different from previous ones. Vary your words, tone, and style.

RULES:
- Write 1-2 SHORT sentences max (like real texts)
- Be casual, natural, conversational
- Show real human emotion (confusion, worry, curiosity)
- Use informal language and punctuation
- Don't be formal or polite
- Make it feel spontaneous and DIFFERENT each time

Write your unique text response (nothing else):"""

        import random
        # Add randomization for maximum variety
        random_temp = random.uniform(0.95, 1.0)
        random_top_p = random.uniform(0.92, 0.98)
        random_top_k = random.randint(45, 60)
        
        llm = get_llm_provider()
        reply = llm.generate_content(
            prompt=prompt,
            system_instruction=HONEYPOT_AGENT_INSTRUCTIONS + (f"\n\n{context_section}" if context_section else ""),
            temperature=random_temp,  # Randomized for variation
            max_tokens=150,
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

        # Keep it short - max 2 sentences
        sentences = reply.split(".")
        if len(sentences) > 2:
            reply = ".".join(sentences[:2]).strip()
            if reply and not reply.endswith((".", "?", "!")):
                reply += "."

        logger.info(f"Persona reply generated: {reply}")
        return reply
