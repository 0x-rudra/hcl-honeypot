"""Scam detection engine using Google AI Studio agent-based analysis."""

import google.generativeai as genai
from app.config import Config
import logging

logger = logging.getLogger(__name__)

SCAM_DETECTOR_AGENT_INSTRUCTIONS = """You are a scam detection expert agent. Your role is to analyze messages and determine if they are scams.

Your expertise includes:
- Identifying phishing attempts and social engineering tactics
- Recognizing urgency manipulation and authority impersonation
- Detecting requests for sensitive information (OTP, passwords, bank details)
- Spotting suspicious patterns in financial transaction requests

Analyze each message objectively and provide clear, evidence-based reasoning."""


class ScamDetector:
    """Detects scams using keyword scoring and LLM analysis."""

    # High-weight scam keywords and phrases
    SCAM_KEYWORDS = {
        "verify": 2,
        "confirm": 2,
        "update": 2,
        "urgent": 3,
        "immediate": 3,
        "account blocked": 4,
        "account suspended": 4,
        "verify identity": 3,
        "confirm password": 4,
        "click here": 2,
        "click link": 2,
        "send money": 4,
        "transfer funds": 4,
        "pay now": 3,
        "pay immediately": 4,
        "upi": 2,
        "bank account": 2,
        "credit card": 2,
        "debit card": 2,
        "otp": 3,
        "one-time password": 3,
        "security code": 3,
        "cvv": 3,
        "atm pin": 3,
        "password": 2,
        "login": 2,
        "confirm details": 3,
        "unusual activity": 2,
        "suspicious": 2,
        "claim reward": 3,
        "won": 2,
        "prize": 2,
        "lottery": 3,
        "refund": 2,
        "tax return": 2,
        "inheritance": 3,
        "impersonate": 4,
        "bank officer": 2,
        "government": 2,
        "police": 2,
        "amazon": 1,
        "google": 1,
        "microsoft": 1,
        "apple": 1,
    }

    @staticmethod
    def calculate_keyword_score(message: str) -> float:
        """
        Calculate initial scam likelihood using keyword scoring.

        Args:
            message: The message text to analyze

        Returns:
            A score between 0 and 1
        """
        message_lower = message.lower()
        total_score = 0
        max_possible_score = sum(ScamDetector.SCAM_KEYWORDS.values())

        for keyword, weight in ScamDetector.SCAM_KEYWORDS.items():
            if keyword in message_lower:
                total_score += weight

        # Normalize score to 0-1 range
        if max_possible_score == 0:
            return 0.0

        score = min(total_score / max_possible_score, 1.0)
        logger.debug(f"Keyword score calculated: {score:.3f} (matched {total_score} points)")
        return score

    @staticmethod
    def classify_with_llm(message: str, keyword_score: float) -> dict:
        """
        Use Gemini API to classify scam and provide reasoning.

        Args:
            message: The message text to analyze
            keyword_score: Pre-calculated keyword score

        Returns:
            Dictionary with is_scam, confidence, and reasoning
        """
        prompt = f"""Analyze this message and determine if it's a scam.

Message: "{message}"

Provide your analysis in this exact format:
1. Is it a scam? (YES or NO)
2. Confidence (0.0 to 1.0, where 1.0 is definitely a scam)
3. Reasoning (2-3 sentences explaining why)

Context:
- Keyword score: {keyword_score:.2f}
- Be conservative: only mark as scam if there's clear evidence
- Consider urgency, requests for sensitive info, impersonation
- Return ONLY the three lines, nothing else
"""

        genai.configure(api_key=Config.GEMINI_API_KEY)
        generation_config = genai.GenerationConfig(
            temperature=Config.AGENT_TEMPERATURE,
            top_p=Config.AGENT_TOP_P,
            top_k=Config.AGENT_TOP_K,
            max_output_tokens=Config.AGENT_MAX_OUTPUT_TOKENS,
        )

        model = genai.GenerativeModel(
            model_name=Config.GEMINI_MODEL,
            generation_config=generation_config,
            system_instruction=SCAM_DETECTOR_AGENT_INSTRUCTIONS,
        )

        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Parse the response
        lines = response_text.split("\n")
        is_scam = False
        confidence = keyword_score
        reasoning = message

        try:
            # Line 1: Is it a scam?
            if len(lines) > 0:
                is_scam = "YES" in lines[0].upper()

            # Line 2: Confidence
            if len(lines) > 1:
                conf_text = lines[1].split(":")[-1].strip()
                confidence = float(conf_text)

            # Line 3: Reasoning
            if len(lines) > 2:
                reasoning = lines[2].split(":", 1)[-1].strip()
        except (ValueError, IndexError):
            # If parsing fails, use defaults
            pass

        result = {
            "is_scam": is_scam,
            "confidence": max(0.0, min(1.0, confidence)),  # Clamp to 0-1
            "reasoning": reasoning,
        }
        logger.info(f"LLM classification complete: is_scam={is_scam}, confidence={result['confidence']:.3f}")
        return result

    @staticmethod
    def detect(message: str) -> dict:
        """
        Main detection method combining keyword scoring and LLM analysis.

        Args:
            message: The message text to analyze

        Returns:
            Dictionary with is_scam, confidence, and reasoning
        """
        # Step 1: Keyword scoring
        keyword_score = ScamDetector.calculate_keyword_score(message)

        # Step 2: LLM classification
        llm_result = ScamDetector.classify_with_llm(message, keyword_score)

        logger.info(f"Scam detection complete: {llm_result['is_scam']} (confidence: {llm_result['confidence']:.3f})")
        return llm_result
