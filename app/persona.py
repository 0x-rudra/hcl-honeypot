"""Honeypot persona generator using Google AI Studio agent."""

import google.generativeai as genai
from app.config import Config
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
    def generate_reply(message: str) -> str:
        """
        Generate a confused, cooperative honeypot reply.

        Args:
            message: The scam message to respond to

        Returns:
            A human-like honeypot reply (1-2 sentences)
        """
        prompt = f"""Generate a honeypot reply to this scam message.

Scam message: "{message}"

Requirements:
- Keep it to 1-2 sentences ONLY
- Sound confused and concerned
- Be cooperative and willing to help
- Use casual language and maybe an emoji or two
- Encourage the scammer to share more details

Generate ONLY the response, nothing else. No explanation, no quotes, just the reply."""

        genai.configure(api_key=Config.GEMINI_API_KEY)
        generation_config = genai.GenerationConfig(
            temperature=0.9,
            top_p=Config.AGENT_TOP_P,
            top_k=Config.AGENT_TOP_K,
            max_output_tokens=150,
        )

        model = genai.GenerativeModel(
            model_name=Config.GEMINI_MODEL,
            generation_config=generation_config,
            system_instruction=HONEYPOT_AGENT_INSTRUCTIONS,
        )

        response = model.generate_content(prompt)
        reply = response.text.strip()

        # Ensure it's 1-2 sentences max
        sentences = reply.split(".")
        if len(sentences) > 2:
            reply = ".".join(sentences[:2]).strip()
            if not reply.endswith("."):
                reply += "."

        logger.info(f"Persona reply generated: {reply[:50]}...")
        return reply
