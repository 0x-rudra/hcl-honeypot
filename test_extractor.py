"""Test script for enhanced regex patterns in the extractor."""

from app.extractor import IntelligenceExtractor

# Test cases
test_messages = [
    # UPI IDs - various formats
    {
        "message": "Send money to scammer@upi or fraud@paytm or victim123@phonepe",
        "expected": "Should extract 3 UPI IDs"
    },
    {
        "message": "Payment to john.doe@googlepay please urgent",
        "expected": "Should extract UPI with dots"
    },

    # Phone numbers - various formats
    {
        "message": "Call me at 9876543210 or +91-9876543210",
        "expected": "Should extract and normalize phone numbers"
    },
    {
        "message": "Contact: +1-234-567-8900 or (123) 456-7890",
        "expected": "Should extract US phone numbers"
    },
    {
        "message": "Whatsapp: +971 50 123 4567 urgent",
        "expected": "Should extract UAE number"
    },

    # URLs - various formats
    {
        "message": "Click here: https://scam-site.com/verify?id=123",
        "expected": "Should extract full URL with query"
    },
    {
        "message": "Visit www.phishing.com or check bit.ly/scam",
        "expected": "Should extract domains without protocol"
    },
    {
        "message": "Go to suspicious-link.xyz for more details",
        "expected": "Should extract domain with xyz TLD"
    },

    # Bank accounts - various formats
    {
        "message": "Transfer to account number 1234567890123 IFSC: SBIN0001234",
        "expected": "Should extract account and IFSC"
    },
    {
        "message": "Bank acc: 98765432109 or a/c 1122334455667",
        "expected": "Should extract both account numbers"
    },

    # Mixed content
    {
        "message": """Your account is suspended!
        Contact: +91-9876543210
        Transfer ₹50,000 to account: 1234567890123
        UPI: scammer@paytm
        Visit: https://fake-bank.com/verify
        IFSC: HDFC0001234""",
        "expected": "Should extract all types"
    },
]

def run_tests():
    print("🧪 Testing Enhanced Regex Patterns\n")
    print("=" * 80)

    for i, test in enumerate(test_messages, 1):
        print(f"\n📝 Test Case {i}: {test['expected']}")
        print(f"Message: {test['message'][:80]}...")
        print("-" * 80)

        result = IntelligenceExtractor.extract(test['message'])

        print(f"✅ UPI IDs: {result['upi_ids']}")
        print(f"✅ Phone Numbers: {result['phone_numbers']}")
        print(f"✅ URLs: {result['phishing_urls']}")
        print(f"✅ Bank Accounts: {result['bank_accounts']}")
        print("=" * 80)

if __name__ == "__main__":
    run_tests()
