"""Test script to verify hackathon format compliance."""

import requests
import json
import time

# Configuration
BASE_URL = "https://honeypoy-hcl-api-production.up.railway.app"
API_KEY = "honeypot-test-key-2026-secure"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def test_first_message():
    """Test the first message in a conversation (hackathon spec 6.1)"""
    print("\n" + "="*60)
    print("TEST 1: First Message (Scam Detection)")
    print("="*60)

    payload = {
        "sessionId": "test-session-001",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately.",
            "timestamp": 1770005528731
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }

    print(f"\n📤 Sending: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            f"{BASE_URL}/honeypot",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"\n✅ Status Code: {response.status_code}")
        print(f"📥 Response: {json.dumps(response.json(), indent=2)}")

        data = response.json()
        assert data.get("status") == "success", "Status should be 'success'"
        assert "reply" in data, "Reply should be present"
        print("\n✅ TEST 1 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        return False


def test_follow_up_message():
    """Test follow-up message with conversation history (hackathon spec 6.2)"""
    print("\n" + "="*60)
    print("TEST 2: Follow-Up Message with History")
    print("="*60)

    payload = {
        "sessionId": "test-session-002",
        "message": {
            "sender": "scammer",
            "text": "Share your UPI ID to avoid account suspension.",
            "timestamp": 1770005528731
        },
        "conversationHistory": [
            {
                "sender": "scammer",
                "text": "Your bank account will be blocked today. Verify immediately.",
                "timestamp": 1770005528731
            },
            {
                "sender": "user",
                "text": "Why will my account be blocked?",
                "timestamp": 1770005528731
            }
        ],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }

    print(f"\n📤 Sending: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            f"{BASE_URL}/honeypot",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"\n✅ Status Code: {response.status_code}")
        print(f"📥 Response: {json.dumps(response.json(), indent=2)}")

        data = response.json()
        assert data.get("status") == "success", "Status should be 'success'"
        assert "reply" in data, "Reply should be present"
        print("\n✅ TEST 2 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        return False


def test_intelligence_extraction():
    """Test intelligence extraction with multiple indicators"""
    print("\n" + "="*60)
    print("TEST 3: Intelligence Extraction")
    print("="*60)

    payload = {
        "sessionId": "test-session-003",
        "message": {
            "sender": "scammer",
            "text": "Send money to account 1234567890 or UPI scammer@paytm. Visit http://fake-bank.com urgently. Call +919876543210",
            "timestamp": 1770005528731
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "WhatsApp",
            "language": "English",
            "locale": "IN"
        }
    }

    print(f"\n📤 Sending: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            f"{BASE_URL}/honeypot",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"\n✅ Status Code: {response.status_code}")
        print(f"📥 Response: {json.dumps(response.json(), indent=2)}")

        data = response.json()
        assert data.get("status") == "success", "Status should be 'success'"
        print("\n✅ TEST 3 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        return False


def test_non_scam_message():
    """Test legitimate message handling"""
    print("\n" + "="*60)
    print("TEST 4: Non-Scam Message")
    print("="*60)

    payload = {
        "sessionId": "test-session-004",
        "message": {
            "sender": "user",
            "text": "Hello, how are you today?",
            "timestamp": 1770005528731
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "Chat",
            "language": "English",
            "locale": "IN"
        }
    }

    print(f"\n📤 Sending: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            f"{BASE_URL}/honeypot",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"\n✅ Status Code: {response.status_code}")
        print(f"📥 Response: {json.dumps(response.json(), indent=2)}")

        data = response.json()
        assert data.get("status") == "success", "Status should be 'success'"
        print("\n✅ TEST 4 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        return False


def test_response_format():
    """Verify response format matches hackathon spec section 8"""
    print("\n" + "="*60)
    print("TEST 5: Response Format Compliance")
    print("="*60)

    payload = {
        "sessionId": "test-session-005",
        "message": {
            "sender": "scammer",
            "text": "Urgent! Your account needs verification.",
            "timestamp": 1770005528731
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "Email",
            "language": "English",
            "locale": "IN"
        }
    }

    print(f"\n📤 Sending: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            f"{BASE_URL}/honeypot",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"\n✅ Status Code: {response.status_code}")
        data = response.json()
        print(f"📥 Response: {json.dumps(data, indent=2)}")

        # Verify required fields as per section 8
        assert "status" in data, "Response must have 'status' field"
        assert "reply" in data, "Response must have 'reply' field"
        assert data["status"] in ["success", "error"], "Status must be 'success' or 'error'"
        assert isinstance(data["reply"], str), "Reply must be a string"
        assert len(data["reply"]) > 0, "Reply cannot be empty"

        print("\n✅ Response format matches hackathon specification!")
        print("✅ TEST 5 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🚀"*30)
    print("HACKATHON FORMAT COMPLIANCE TEST SUITE")
    print("🚀"*30)

    results = []

    # Run all tests
    results.append(("First Message", test_first_message()))
    time.sleep(2)

    results.append(("Follow-Up Message", test_follow_up_message()))
    time.sleep(2)

    results.append(("Intelligence Extraction", test_intelligence_extraction()))
    time.sleep(2)

    results.append(("Non-Scam Message", test_non_scam_message()))
    time.sleep(2)

    results.append(("Response Format", test_response_format()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready for hackathon evaluation!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")


if __name__ == "__main__":
    main()
