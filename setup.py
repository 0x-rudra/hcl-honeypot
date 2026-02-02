"""Interactive setup script for Honeypot API."""

import os
import sys


def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def main():
    print("\n🚀 Honeypot API Setup Wizard\n")
    print("This wizard will help you configure your API keys.\n")

    # Step 1: Check if .env exists
    env_file = ".env"
    env_exists = os.path.exists(env_file)

    if env_exists:
        print(f"✅ Found existing {env_file} file")
        use_existing = input("\nUse existing .env file? (y/n): ").lower()
        if use_existing != 'y':
            env_exists = False

    # Step 2: Get API keys
    if not env_exists:
        print_header("Step 1: Google AI Studio API Key")
        print("\n1. Open: https://aistudio.google.com/apikey")
        print("2. Sign in with your Google account")
        print("3. Click 'Create API Key'")
        print("4. Copy the API key (starts with 'AIza')")

        gemini_key = input("\nPaste your GEMINI_API_KEY (or press Enter to skip): ").strip()

        print_header("Step 2: Honeypot API Key")
        print("\nThis is YOUR custom key for client authentication.")
        print("Choose any secret string (e.g., 'my-secret-key-123')")

        honeypot_key = input("\nEnter your HONEYPOT_API_KEY (or press Enter for default): ").strip()
        if not honeypot_key:
            honeypot_key = "your-secret-key-here"

        # Step 3: Create .env file
        if gemini_key or honeypot_key:
            print_header("Step 3: Creating .env file")

            env_content = f"""# Google AI Studio API Key (from https://aistudio.google.com/apikey)
GEMINI_API_KEY={gemini_key if gemini_key else 'your-google-ai-studio-api-key-here'}

# Honeypot API Authentication Key
HONEYPOT_API_KEY={honeypot_key}

# Optional: Debug mode
DEBUG=False

# Optional: Server port
PORT=8000
"""

            try:
                with open(env_file, 'w') as f:
                    f.write(env_content)
                print(f"✅ Created {env_file} file")
            except Exception as e:
                print(f"❌ Failed to create {env_file}: {e}")
                return 1

    # Step 4: Set environment variables for current session
    print_header("Step 4: Setting Environment Variables")

    # Try to load from .env file
    if env_exists or os.path.exists(env_file):
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in ['GEMINI_API_KEY', 'HONEYPOT_API_KEY']:
                            os.environ[key] = value
                            if value and not value.startswith('your-'):
                                print(f"✅ Set {key}")
                            else:
                                print(f"⚠️  {key} needs to be configured")
        except Exception as e:
            print(f"❌ Error loading .env file: {e}")

    # Step 5: Verify configuration
    print_header("Step 5: Verification")

    gemini_key_set = os.getenv("GEMINI_API_KEY")
    honeypot_key_set = os.getenv("HONEYPOT_API_KEY")

    if gemini_key_set and not gemini_key_set.startswith("your-"):
        print("✅ GEMINI_API_KEY is configured")
    else:
        print("❌ GEMINI_API_KEY is not configured")
        print("   Set it with: $env:GEMINI_API_KEY='AIzaSy...' (PowerShell)")

    if honeypot_key_set:
        print("✅ HONEYPOT_API_KEY is configured")
    else:
        print("❌ HONEYPOT_API_KEY is not configured")

    # Step 6: Next steps
    print_header("Next Steps")

    if gemini_key_set and not gemini_key_set.startswith("your-"):
        print("\n✅ Configuration complete!\n")
        print("Run these commands:\n")
        print("1. Test configuration:")
        print("   python test_setup.py\n")
        print("2. Start the server:")
        print("   python -m uvicorn app.main:app --reload --port 8000\n")
        print("3. Test the API:")
        print("   See QUICK_START.md for examples")
        return 0
    else:
        print("\n⚠️  Setup incomplete. Please configure your API keys:\n")
        print("Option 1: Edit .env file and add your GEMINI_API_KEY")
        print("Option 2: Set environment variables:")
        print("   PowerShell:")
        print('   $env:GEMINI_API_KEY="AIzaSy...your-key"')
        print('   $env:HONEYPOT_API_KEY="your-secret-key"\n')
        print("Get your API key from: https://aistudio.google.com/apikey")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
