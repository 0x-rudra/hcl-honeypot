"""Intelligence extractor using Google AI Studio agent for scam indicators."""

import re
from typing import List
from app.config import Config
from app.llm_provider import get_llm_provider
import logging

logger = logging.getLogger(__name__)

EXTRACTOR_AGENT_INSTRUCTIONS = """You are an intelligence extraction agent specialized in identifying scam indicators.

Your expertise includes:
- Extracting UPI IDs (format: user@upi)
- Identifying phone numbers (especially Indian format)
- Finding URLs and potentially malicious links
- Detecting bank account numbers

Be precise and only extract valid, complete indicators. Ignore partial or invalid patterns."""


class IntelligenceExtractor:
    """Extracts scam intelligence using regex and LLM fallback."""

    # Enhanced regex patterns for comprehensive extraction

    # UPI ID patterns - handles various formats
    UPI_PATTERN = r"\b[\w][\w\.\-]{2,}@(?:upi|UPI|paytm|phonepe|gpay|googlepay|bhim|amazonpay|whatsapp|okaxis|oksbi|okicici|okhdfcbank|axl|apl|yapl|ibl|icici|airtel|freecharge|mobikwik)\b"

    # Phone number patterns - Indian and international
    # Handles: +91-9876543210, 91 9876543210, 9876543210, +1-234-567-8900, etc.
    PHONE_PATTERN = r"""
        (?:
            (?:\+|00)?                    # Optional + or 00 prefix
            (?:91|1|44|61|971|65|60)?     # Country codes: India, US, UK, Australia, UAE, Singapore, Malaysia
            [-.\s]?                        # Optional separator
            (?:\(?\d{3,4}\)?[-.\s]?)?     # Optional area code with parentheses
            \d{3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}  # Main number with separators
        )
    """

    # URL patterns - comprehensive URL detection
    URL_PATTERN = r"""
        (?:
            (?:https?|ftp|ftps)://         # Protocol
            |www\.                          # Or www.
            |(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/|\b)  # Domain without protocol
        )
        (?:[^\s<>"{}|\\^`\[\]]+)?          # Path and query
    """

    # Bank account patterns - multiple formats
    BANK_ACCOUNT_PATTERN = r"(?:(?:account|acc|acct|bank\s*account|bank\s*acc)(?:\s*(?:no|number|num|#|:|\.))?)\s*[:\-.]?\s*(\d{9,18})|(?:(?:IFSC|ifsc)\s*[:\-.]?\s*([A-Z]{4}0[A-Z0-9]{6}))"


    @staticmethod
    def extract_upi_ids(text: str) -> List[str]:
        """Extract UPI IDs from text with comprehensive pattern matching."""
        matches = re.findall(IntelligenceExtractor.UPI_PATTERN, text, re.IGNORECASE | re.VERBOSE)
        # Also check for @upi pattern as fallback
        basic_upi = re.findall(r"\b[\w][\w\.\-]{2,}@upi\b", text, re.IGNORECASE)
        all_matches = matches + basic_upi

        # Validate and normalize
        valid_upis = []
        for match in all_matches:
            match = match.lower().strip()
            # Must have @ and at least 3 chars before @
            if '@' in match and len(match.split('@')[0]) >= 3:
                valid_upis.append(match)

        result = list(set(valid_upis))
        logger.debug(f"Extracted {len(result)} UPI IDs")
        return result

    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """Extract phone numbers with comprehensive validation."""
        matches = re.findall(IntelligenceExtractor.PHONE_PATTERN, text, re.VERBOSE)

        # Also try simpler patterns for edge cases
        simple_patterns = [
            r"\b\d{10}\b",                           # Simple 10 digits
            r"\b\+\d{1,3}[-.\s]?\d{10}\b",          # + country code + 10 digits
            r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b",     # US format: 123-456-7890
            r"\b\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}\b"  # (123) 456-7890
        ]

        for pattern in simple_patterns:
            matches.extend(re.findall(pattern, text))

        valid_numbers = []
        seen = set()

        for match in matches:
            # Clean the number
            clean = re.sub(r"[^\d+]", "", match)

            # Skip if too short or already seen
            if len(clean) < 10 or clean in seen:
                continue

            # Skip if it's just repeated digits (like 0000000000)
            if len(set(clean.replace('+', ''))) == 1:
                continue

            # Normalize format
            if clean.startswith('+'):
                normalized = clean
            elif clean.startswith('91') and len(clean) == 12:
                normalized = '+' + clean
            elif clean.startswith('0') and len(clean) == 11:
                # Indian format starting with 0
                normalized = '+91' + clean[1:]
            elif len(clean) == 10:
                # Assume Indian number
                normalized = '+91' + clean
            elif len(clean) == 11 and clean.startswith('1'):
                # US/Canada number
                normalized = '+' + clean
            else:
                normalized = '+' + clean if not clean.startswith('+') else clean

            seen.add(clean)
            valid_numbers.append(normalized)

        result = list(set(valid_numbers))
        logger.debug(f"Extracted {len(result)} phone numbers")
        return result

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs with comprehensive pattern matching."""
        matches = re.findall(IntelligenceExtractor.URL_PATTERN, text, re.VERBOSE | re.IGNORECASE)

        # Additional patterns for edge cases
        additional_patterns = [
            r"https?://[^\s<>\"'{}|\\^`\[\]]+",          # Standard HTTP/HTTPS
            r"www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s]*",  # www. domains
            r"\b[a-zA-Z0-9-]+\.(?:com|net|org|info|biz|io|co|in|xyz|online|site|shop|app|link|click|ltd|tech|store|live|pro|dev|me|tv|us|uk|ca|au|de|fr|jp|cn|ru)\b[^\s]*"  # Common TLDs
        ]

        for pattern in additional_patterns:
            matches.extend(re.findall(pattern, text, re.IGNORECASE))

        valid_urls = []
        for url in matches:
            url = url.strip()

            # Skip empty or very short matches
            if len(url) < 4:
                continue

            # Add protocol if missing
            if not url.startswith(('http://', 'https://', 'ftp://', 'ftps://')):
                if url.startswith('www.'):
                    url = 'http://' + url
                elif '.' in url:
                    url = 'http://' + url

            # Clean trailing punctuation
            url = re.sub(r'[,;:!?\.\)]+$', '', url)

            # Validate URL has domain structure
            if '.' in url and len(url) > 4:
                valid_urls.append(url)

        result = list(set(valid_urls))
        logger.debug(f"Extracted {len(result)} URLs")
        return result

    @staticmethod
    def extract_bank_accounts(text: str) -> List[str]:
        """Extract bank account numbers and IFSC codes."""
        results = []

        # Extract account numbers with context
        account_matches = re.findall(IntelligenceExtractor.BANK_ACCOUNT_PATTERN, text, re.IGNORECASE)
        for match in account_matches:
            if isinstance(match, tuple):
                # Get non-empty groups
                for group in match:
                    if group and len(group) >= 9:
                        results.append(group)
            elif match and len(match) >= 9:
                results.append(match)

        # Additional patterns for standalone account numbers
        standalone_patterns = [
            r"\b\d{9,18}\b",  # 9-18 digit numbers
            r"(?:IFSC|ifsc)\s*[:\-]?\s*([A-Z]{4}0[A-Z0-9]{6})",  # IFSC codes
            r"\b[A-Z]{4}0[A-Z0-9]{6}\b",  # IFSC without prefix
        ]

        for pattern in standalone_patterns:
            matches = re.findall(pattern, text)
            results.extend(matches)

        # Validate and filter
        valid_accounts = []
        for acc in results:
            acc = str(acc).strip()

            # Skip if too short
            if len(acc) < 4:
                continue

            # Check if it's an IFSC code (4 letters + 0 + 6 alphanumeric)
            if re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', acc):
                valid_accounts.append(f"IFSC: {acc}")
            # Check if it's a valid account number length
            elif acc.isdigit() and 9 <= len(acc) <= 18:
                # Skip if all same digits
                if len(set(acc)) > 1:
                    valid_accounts.append(f"Account: {acc}")

        result = list(set(valid_accounts))
        logger.debug(f"Extracted {len(result)} bank accounts/IFSC codes")
        return result

    @staticmethod
    def extract_with_llm_fallback(text: str) -> dict:
        """
        Use LLM to extract indicators if regex finds nothing.

        Args:
            text: The message text to analyze

        Returns:
            Dictionary with extracted indicators
        """
        # First try regex
        result = {
            "bank_accounts": IntelligenceExtractor.extract_bank_accounts(text),
            "upi_ids": IntelligenceExtractor.extract_upi_ids(text),
            "phone_numbers": IntelligenceExtractor.extract_phone_numbers(text),
            "phishing_urls": IntelligenceExtractor.extract_urls(text),
        }

        # If regex found something, return it
        if any(result.values()):
            return result

        # Otherwise, use LLM as fallback
        prompt = f"""Extract scam indicators from the text.

Text: "{text}"

Return ONLY valid indicators in this format:
bank_accounts: [list]
upi_ids: [list]
phone_numbers: [list]
phishing_urls: [list]

If none found, use empty lists."""

        llm = get_llm_provider()
        response_text = llm.generate_content(
            prompt=prompt,
            system_instruction=EXTRACTOR_AGENT_INSTRUCTIONS,
            temperature=0.1,
            max_tokens=800,  # More tokens for better extraction
            top_p=0.95,
            top_k=40,
            timeout=5,
        )

        # Parse LLM response
        try:
            lines = response_text.split("\n")
            for line in lines:
                if "bank_accounts:" in line.lower():
                    accounts = re.findall(r"\d{9,18}", line)
                    result["bank_accounts"] = list(set(accounts))
                elif "upi_ids:" in line.lower():
                    upis = re.findall(r"[\w\.-]+@upi", line, re.IGNORECASE)
                    result["upi_ids"] = [u.lower() for u in set(upis)]
                elif "phone_numbers:" in line.lower():
                    phones = re.findall(r"\+?\d{10,12}", line)
                    result["phone_numbers"] = list(set(phones))
                elif "phishing_urls:" in line.lower():
                    urls = re.findall(r"https?://\S+", line)
                    result["phishing_urls"] = list(set(urls))
        except Exception:
            pass

        logger.debug(f"LLM fallback extraction: {sum(len(v) for v in result.values())} total indicators")
        return result

    @staticmethod
    def extract(message: str) -> dict:
        """
        Extract scam intelligence from message.

        Args:
            message: The message text to analyze

        Returns:
            Dictionary with extracted indicators
        """
        result = IntelligenceExtractor.extract_with_llm_fallback(message)
        total_indicators = sum(len(v) for v in result.values())
        logger.info(f"Intelligence extraction complete: {total_indicators} indicators found")
        return result

    @staticmethod
    def convert_to_hackathon_format(intelligence: dict) -> dict:
        """
        Convert internal format to hackathon format.

        Args:
            intelligence: Dict with snake_case keys

        Returns:
            Dict with camelCase keys matching hackathon spec
        """
        return {
            "bankAccounts": list(intelligence.get("bank_accounts", [])),
            "upiIds": list(intelligence.get("upi_ids", [])),
            "phishingLinks": list(intelligence.get("phishing_urls", [])),
            "phoneNumbers": list(intelligence.get("phone_numbers", [])),
            "suspiciousKeywords": []  # Can be populated from scam detection
        }

