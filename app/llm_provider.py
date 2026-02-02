"""LLM provider abstraction for easy switching between different AI models."""

import google.generativeai as genai
from app.config import Config
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LLMProvider:
    """
    Abstraction layer for LLM providers.

    Supports easy switching between different AI models by just changing API keys.
    Currently supports Google Gemini/Gemma models.
    Can be extended to support OpenAI, Anthropic, etc.
    """

    @staticmethod
    def generate_content(
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 0.95,
        top_k: int = 40,
    ) -> str:
        """
        Generate content using configured LLM provider.

        Args:
            prompt: The prompt to send to the model
            system_instruction: System-level instructions for the model
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter

        Returns:
            Generated text response

        Raises:
            Exception: If generation fails
        """
        logger.info(f"LLMProvider.generate_content called: model={Config.GEMINI_MODEL}, temp={temperature}, max_tokens={max_tokens}")
        try:
            # Build full prompt with system instructions
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            logger.debug(f"Full prompt length: {len(full_prompt)} chars, Has system instruction: {bool(system_instruction)}")

            # Configure Gemini API
            genai.configure(api_key=Config.GEMINI_API_KEY)
            logger.debug(f"Gemini API configured with key: {Config.GEMINI_API_KEY[:10]}...")

            generation_config = genai.GenerationConfig(
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                max_output_tokens=max_tokens,
            )
            logger.debug(f"Generation config: temp={temperature}, top_p={top_p}, top_k={top_k}")

            model = genai.GenerativeModel(
                model_name=Config.GEMINI_MODEL,
                generation_config=generation_config,
            )

            logger.info(f"Sending request to Gemini API with model: {Config.GEMINI_MODEL}")
            response = model.generate_content(full_prompt)
            result = response.text.strip()

            logger.info(f"Content generated successfully - Response length: {len(result)} chars")
            return result

        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}", exc_info=True)
            raise


class GeminiProvider:
    """
    Google Gemini/Gemma specific provider.
    Handles all Gemini and Gemma model interactions.
    """

    @staticmethod
    def is_configured() -> bool:
        """Check if Gemini API is properly configured."""
        is_conf = bool(Config.GEMINI_API_KEY)
        logger.info(f"GeminiProvider.is_configured: {is_conf} (model: {Config.GEMINI_MODEL})")
        return is_conf

    @staticmethod
    def get_model_info() -> dict:
        """Get current model configuration info."""
        info = {
            "provider": "Google Gemini/Gemma",
            "model": Config.GEMINI_MODEL,
            "api_key_set": bool(Config.GEMINI_API_KEY),
        }
        logger.info(f"GeminiProvider.get_model_info: {info}")
        return info


# Future providers can be added here:
# class OpenAIProvider:
#     """OpenAI GPT provider implementation."""
#     pass
#
# class AnthropicProvider:
#     """Anthropic Claude provider implementation."""
#     pass
def get_llm_provider() -> LLMProvider:
    """
    Get the configured LLM provider.

    Returns:
        LLMProvider instance configured for the current setup
    """
    logger.info("get_llm_provider: Initializing LLM provider...")
    # Currently only supports Gemini, but can be extended:
    # if Config.OPENAI_API_KEY:
    #     return OpenAIProvider()
    # elif Config.ANTHROPIC_API_KEY:
    #     return AnthropicProvider()
    # else:
    #     return GeminiProvider()

    logger.info(f"Returning LLMProvider with Gemini model: {Config.GEMINI_MODEL}")
    return LLMProvider()
