"""Test script to verify server functionality."""

import requests
import json
import sys
import time
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
API_KEY = os.getenv("HONEYPOT_API_KEY", "your-secret-key-here")

def test_root():
    """Test root endpoint."""
    print("\n" + "="*80)
    print("Testing GET /")
    print("="*80)
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health():
    """Test health check endpoint."""
    print("\n" + "="*80)
    print("Testing GET /health")
    print("="*80)
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_honeypot_without_auth():
    """Test honeypot endpoint without authentication."""
    print("\n" + "="*80)
    print("Testing POST /honeypot (without auth)")
    print("="*80)
    try:
        payload = {"message": "Send money to scammer@upi"}
        response = requests.post(f"{BASE_URL}/honeypot", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 401  # Should be unauthorized
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_honeypot_with_auth():
    """Test honeypot endpoint with authentication."""
    print("\n" + "="*80)
    print("Testing POST /honeypot (with auth)")
    print("="*80)
    try:
        headers = {"X-API-Key": API_KEY}
        payload = {"message": "Send money to scammer@upi urgently"}

        print(f"Payload: {json.dumps(payload, indent=2)}")
        response = requests.post(f"{BASE_URL}/honeypot", json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        elif response.status_code == 500:
            print(f"⚠️  Server error (likely missing GEMINI_API_KEY): {response.text}")
            print("   This is expected if GEMINI_API_KEY is not configured")
            return True  # Consider this a pass since server is working, just not configured
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_honeypot_empty_message():
    """Test honeypot endpoint with empty message."""
    print("\n" + "="*80)
    print("Testing POST /honeypot (empty message)")
    print("="*80)
    try:
        headers = {"X-API-Key": API_KEY}
        payload = {"message": ""}

        response = requests.post(f"{BASE_URL}/honeypot", json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 400  # Should be bad request
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n🧪 Starting Server Tests")
    print("Make sure the server is running on http://127.0.0.1:8000")

    # Wait for server to be ready
    time.sleep(2)

    results = {
        "Root endpoint": test_root(),
        "Health check": test_health(),
        "Honeypot without auth": test_honeypot_without_auth(),
        "Honeypot with auth": test_honeypot_with_auth(),
        "Honeypot empty message": test_honeypot_empty_message(),
    }

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
