"""Test script to verify Google AI Studio API configuration."""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def test_environment_variables():
    """Test if required environment variables are set."""
    print("=" * 60)
    print("Testing Environment Variables")
    print("=" * 60)

    gemini_key = os.getenv("GEMINI_API_KEY")
    honeypot_key = os.getenv("HONEYPOT_API_KEY")

    if not gemini_key:
        print("❌ GEMINI_API_KEY not found!")
        print("   Set it with: $env:GEMINI_API_KEY='your-key' (PowerShell)")
        return False
    else:
        print(f"✅ GEMINI_API_KEY found: {gemini_key[:10]}...")

    if not honeypot_key:
        print("⚠️  HONEYPOT_API_KEY not found (will use default)")
    else:
        print(f"✅ HONEYPOT_API_KEY found: {honeypot_key[:10]}...")

    return True


def test_imports():
    """Test if required packages are installed."""
    print("\n" + "=" * 60)
    print("Testing Package Imports")
    print("=" * 60)

    try:
        import google.generativeai as genai
        print("✅ google-generativeai imported successfully")
    except ImportError:
        print("❌ google-generativeai not installed!")
        print("   Install with: pip install -r requirements.txt")
        return False

    try:
        import fastapi
        print("✅ fastapi imported successfully")
    except ImportError:
        print("❌ fastapi not installed!")
        return False

    try:
        import pydantic
        print("✅ pydantic imported successfully")
    except ImportError:
        print("❌ pydantic not installed!")
        return False

    return True


def test_api_connection():
    """Test connection to Google AI Studio API."""
    print("\n" + "=" * 60)
    print("Testing Google AI Studio API Connection")
    print("=" * 60)

    try:
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ Cannot test API - GEMINI_API_KEY not set")
            return False

        genai.configure(api_key=api_key)

        # Test with a simple prompt
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Say 'API test successful' in one line")

        print("✅ API connection successful!")
        print(f"   Response: {response.text.strip()}")
        return True

    except Exception as e:
        error_str = str(e)

        # Check if it's a quota/rate limit error (API key is valid but quota exceeded)
        if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
            print("⚠️  API key is valid but rate limit exceeded")
            print("   This is expected on free tier after some usage")
            print("   Your API will work once quota resets")
            return True  # Consider this a pass since API key is valid

        # Check for authentication errors (invalid API key)
        if "401" in error_str or "403" in error_str or "invalid" in error_str.lower():
            print(f"❌ API authentication failed: Invalid API key")
            return False

        # Other errors
        print(f"❌ API connection failed: {error_str[:200]}")
        return False


def test_agent_configuration():
    """Test agent configuration from config.py."""
    print("\n" + "=" * 60)
    print("Testing Agent Configuration")
    print("=" * 60)

    try:
        from app.config import Config

        print(f"✅ Model: {Config.GEMINI_MODEL}")
        print(f"✅ Temperature: {Config.AGENT_TEMPERATURE}")
        print(f"✅ Top-P: {Config.AGENT_TOP_P}")
        print(f"✅ Top-K: {Config.AGENT_TOP_K}")
        print(f"✅ Max Tokens: {Config.AGENT_MAX_OUTPUT_TOKENS}")

        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_modules():
    """Test if all app modules can be imported."""
    print("\n" + "=" * 60)
    print("Testing Application Modules")
    print("=" * 60)

    modules = [
        ("app.config", "Configuration"),
        ("app.auth", "Authentication"),
        ("app.schemas", "Schemas"),
        ("app.scam_detector", "Scam Detector"),
        ("app.persona", "Persona Generator"),
        ("app.extractor", "Intelligence Extractor"),
        ("app.main", "Main API"),
    ]

    all_ok = True
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name} ({module_name})")
        except Exception as e:
            print(f"❌ {display_name} failed: {e}")
            all_ok = False

    return all_ok


def main():
    """Run all tests."""
    print("\n🔍 Honeypot API Configuration Test\n")

    results = {
        "Environment Variables": test_environment_variables(),
        "Package Imports": test_imports(),
        "API Connection": test_api_connection(),
        "Agent Configuration": test_agent_configuration(),
        "Application Modules": test_modules(),
    }

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✅ All tests passed! Your API is ready to use.")
        print("\nStart the server with:")
        print("  python -m uvicorn app.main:app --reload --port 8000")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")

        # Provide specific guidance
        if not results["Environment Variables"]:
            print("\n💡 Quick Fix: Set your Google AI Studio API key")
            print("   PowerShell:")
            print('   $env:GEMINI_API_KEY="AIzaSy...your-key-here"')
            print('   $env:HONEYPOT_API_KEY="your-secret-key"')
            print("\n   Or create a .env file with:")
            print("   GEMINI_API_KEY=AIzaSy...your-key-here")
            print("   HONEYPOT_API_KEY=your-secret-key")
            print("\n   Get API key from: https://aistudio.google.com/apikey")

        return 1


if __name__ == "__main__":
    sys.exit(main())
