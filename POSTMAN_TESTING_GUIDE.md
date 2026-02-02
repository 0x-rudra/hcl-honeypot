# Postman Testing Guide for Honeypot API

## Quick Setup

### Temporary API Key
```
x-api-key: honeypot-test-key-2026-secure
```

## Server Setup

1. **Start the Server**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Verify Server is Running**
   - Server should be available at: `http://127.0.0.1:8000`
   - Check terminal for: `INFO: Application startup complete.`

---

## API Endpoints Summary

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/` | GET | No | API Information |
| `/health` | GET | No | Health Check |
| `/honeypot` | POST | Yes | Scam Detection & Intelligence Extraction |

---

## Postman Test Cases

### Test 1: Root Endpoint (GET /)
**No authentication needed**

**Request:**
```
Method: GET
URL: http://127.0.0.1:8000/
```

**Expected Response (200 OK):**
```json
{
  "name": "Agentic Honeypot API",
  "version": "1.0.0",
  "endpoint": "/honeypot",
  "method": "POST"
}
```

---

### Test 2: Health Check (GET /health)
**No authentication needed**

**Request:**
```
Method: GET
URL: http://127.0.0.1:8000/health
```

**Expected Response (200 OK):**
```json
{
  "status": "healthy"
}
```

---

### Test 3: Honeypot - Missing Authentication (POST /honeypot)

**Request:**
```
Method: POST
URL: http://127.0.0.1:8000/honeypot
Headers: (none)
Body (JSON):
{
  "message": "Send money to scammer@upi urgently"
}
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Missing x-api-key header"
}
```

---

### Test 4: Honeypot - Invalid API Key (POST /honeypot)

**Request:**
```
Method: POST
URL: http://127.0.0.1:8000/honeypot
Headers:
  x-api-key: wrong-key-123
Body (JSON):
{
  "message": "Send money to scammer@upi urgently"
}
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Invalid API key"
}
```

---

### Test 5: Honeypot - Empty Message (POST /honeypot)

**Request:**
```
Method: POST
URL: http://127.0.0.1:8000/honeypot
Headers:
  x-api-key: honeypot-test-key-2026-secure
Body (JSON):
{
  "message": ""
}
```

**Expected Response (400 Bad Request):**
```json
{
  "detail": "Message cannot be empty"
}
```

---

### Test 6: Honeypot - Valid Scam Message (First Message)

**Request:**
```
Method: POST
URL: http://127.0.0.1:8000/honeypot
Headers:
  x-api-key: honeypot-test-key-2026-secure
  Content-Type: application/json
Body (JSON):
{
  "message": "URGENT! Send money to scammer@paytm or call 9876543210. Account: 123456789012"
}
```

**Expected Response (200 OK):**
```json
{
  "is_scam": true,
  "confidence": 0.95,
  "agent_reply": "Oh no, that sounds urgent! Can you tell me more about this?",
  "extracted_intelligence": {
    "upi_ids": ["scammer@paytm"],
    "phone_numbers": ["+919876543210"],
    "bank_accounts": ["123456789012"],
    "phishing_urls": []
  },
  "reasoning": "Message contains UPI ID, phone number, urgency keywords",
  "session_id": "uuid-generated-here",
  "conversation_history": [
    {
      "role": "user",
      "content": "URGENT! Send money to scammer@paytm...",
      "timestamp": "2026-02-03T02:00:00.000000"
    },
    {
      "role": "assistant",
      "content": "Oh no, that sounds urgent!...",
      "timestamp": "2026-02-03T02:00:01.000000"
    }
  ],
  "accumulated_intelligence": {
    "upi_ids": ["scammer@paytm"],
    "phone_numbers": ["+919876543210"],
    "bank_accounts": ["123456789012"],
    "phishing_urls": []
  }
}
```

---

### Test 7: Honeypot - Continue Conversation (Second Message)

**Request:**
```
Method: POST
URL: http://127.0.0.1:8000/honeypot
Headers:
  x-api-key: honeypot-test-key-2026-secure
  Content-Type: application/json
Body (JSON):
{
  "message": "They said I need to send 5000 rupees. Can I use another UPI: fraud123@phonepe?",
  "session_id": "uuid-from-previous-response"
}
```

**Expected Response (200 OK):**
```json
{
  "is_scam": true,
  "confidence": 0.90,
  "agent_reply": "Oh, really? Could you tell me more details?",
  "extracted_intelligence": {
    "upi_ids": ["fraud123@phonepe"],
    "phone_numbers": [],
    "bank_accounts": [],
    "phishing_urls": []
  },
  "reasoning": "Continuation of scam conversation with new UPI ID",
  "session_id": "same-uuid-as-before",
  "conversation_history": [
---

### Test 9: Honeypot - Multiple Indicators (POST /honeypot)
      "timestamp": "2026-02-03T02:00:00.000000"
    },
    {
      "role": "assistant",
      "content": "Oh no, that sounds urgent!...",
      "timestamp": "2026-02-03T02:00:01.000000"
    },
    {
      "role": "user",
      "content": "They said I need to send 5000 rupees...",
      "timestamp": "2026-02-03T02:00:30.000000"
    },
    {
      "role": "assistant",
      "content": "Oh, really? Could you tell me more details?",
      "timestamp": "2026-02-03T02:00:31.000000"
    }
  ],
  "accumulated_intelligence": {
    "upi_ids": ["scammer@paytm", "fraud123@phonepe"],
    "phone_numbers": ["+919876543210"],
    "bank_accounts": ["123456789012"],
    "phishing_urls": []
  }
}
```

---

### Test 8: Honeypot - Non-Scam Message (POST /honeypot)

**Request:**
```
Method: POST
URL: http://127.0.0.1:8000/honeypot
Headers:
  x-api-key: honeypot-test-key-2026-secure
  Content-Type: application/json
Body (JSON):
{
  "message": "Hello, how are you doing today? I hope you're having a great day!"
}
```

**Expected Response (200 OK):**
```json
{
  "is_scam": false,
  "confidence": 0.05,
  "agent_reply": "",
  "extracted_intelligence": {
    "upi_ids": [],
    "phone_numbers": [],
    "bank_accounts": [],
    "phishing_urls": []
  },
  "reasoning": "Normal greeting message, no scam indicators",
  "session_id": "new-uuid-generated",
  "conversation_history": [
    {
      "role": "user",
      "content": "Hello, how are you doing today?...",
      "timestamp": "2026-02-03T02:05:00.000000"
    }
  ],
  "accumulated_intelligence": {
    "upi_ids": [],
    "phone_numbers": [],
    "bank_accounts": [],
    "phishing_urls": []
  }
}
```

---

### Test 8: Honeypot - Multiple Indicators (POST /honeypot)

**Request:**
```
Method: POST
URL: http://127.0.0.1:8000/honeypot
Headers:
  x-api-key: honeypot-test-key-2026-secure
  Content-Type: application/json
Body (JSON):
{
  "message": "Click http://phishing-site.com and send money to fraud@upi or victim123@phonepe. Call +91-9876543210 now! IFSC: SBIN0001234"
}
```

**Expected Response (200 OK):**
```json
{
  "is_scam": true,
  "confidence": 0.98,
  "agent_reply": "Generated honeypot reply...",
  "extracted_intelligence": {
    "upi_ids": ["fraud@upi", "victim123@phonepe"],
    "phone_numbers": ["+919876543210"],
    "bank_accounts": ["SBIN0001234"],
    "phishing_urls": ["http://phishing-site.com"]
  },
  "reasoning": "Multiple scam indicators detected"
}
```

---

## Step-by-Step Postman Setup

### Step 1: Create New Request
1. Open Postman
2. Click **"New"** → **"HTTP Request"**
3. Name it: "Honeypot API Test"

### Step 2: Configure Request
1. Set **Method**: POST
2. Set **URL**: `http://127.0.0.1:8000/honeypot`

### Step 3: Add Headers
1. Click **"Headers"** tab
2. Add header:
   - **Key**: `x-api-key`
   - **Value**: `honeypot-test-key-2026-secure`
3. Add header (auto-added):
   - **Key**: `Content-Type`
   - **Value**: `application/json`

### Step 4: Add Request Body
1. Click **"Body"** tab
2. Select **"raw"**
3. Select **"JSON"** from dropdown
4. Paste:
   ```json
   {
     "message": "Send money to scammer@upi urgently! Call 9876543210"
   }
   ```

### Step 5: Send Request
1. Click **"Send"** button
2. Check response in bottom panel

---

## Postman Collection Setup

### Create Environment
1. Click **"Environments"** (left sidebar)
2. Click **"+"** to create new environment
3. Name: "Honeypot Local"
4. Add variables:
   ```
   base_url: http://127.0.0.1:8000
   api_key: honeypot-test-key-2026-secure
   ```
5. Click **"Save"**
6. Select environment from dropdown (top right)

### Use Variables in Requests
- **URL**: `{{base_url}}/honeypot`
- **Header Value**: `{{api_key}}`

---

## Comprehensive Testing Scenarios (20-30+ Tests)

To thoroughly test all features, run these test sequences in Postman.

---

### 📋 Test Collection 1: Basic Functionality (10 tests)

**1.1 - Root Endpoint (5 times)**
- Method: GET
- URL: `http://127.0.0.1:8000/`
- Expected: 200 OK with API info
- Run 5 times to verify consistency

**1.2 - Health Check (5 times)**
- Method: GET
- URL: `http://127.0.0.1:8000/health`
- Expected: 200 OK with `{"status": "healthy"}`
- Run 5 times to verify stability

---

### 🔐 Test Collection 2: Authentication (15 tests)

**2.1 - Missing API Key (5 times)**
- Method: POST
- URL: `http://127.0.0.1:8000/honeypot`
- Headers: None
- Body: `{"message": "test"}`
- Expected: 401 Unauthorized
- Test with different messages each time

**2.2 - Invalid API Keys (5 times)**
Test with these invalid keys:
1. `wrong-key-1`
2. `invalid-123`
3. `fake-key-456`
4. `bad-api-key`
5. `unauthorized-key`

- Method: POST
- URL: `http://127.0.0.1:8000/honeypot`
- Headers: `x-api-key: <invalid-key>`
- Body: `{"message": "test"}`
- Expected: 401 Unauthorized for each

**2.3 - Valid API Key (5 times)**
- Method: POST
- URL: `http://127.0.0.1:8000/honeypot`
- Headers: `x-api-key: honeypot-test-key-2026-secure`
- Body: `{"message": "Hello, test message 1"}` (change number each time)
- Expected: 200 OK with valid response
- Wait 500ms between requests

---

### ✅ Test Collection 3: Input Validation (6 tests)

**3.1 - Empty Message (3 times)**
- Method: POST
- URL: `http://127.0.0.1:8000/honeypot`
- Headers: `x-api-key: honeypot-test-key-2026-secure`
- Body: `{"message": ""}`
- Expected: 400 Bad Request
- Test 3 times

**3.2 - Whitespace Only (3 times)**
Test with:
1. `{"message": "   "}`
2. `{"message": "\t\t\t"}`
3. `{"message": "\n\n\n"}`

- Expected: 400 Bad Request for each

---

### 📝 Test Collection 4: Non-Scam Messages (10 tests)

Test these legitimate messages (expect `is_scam: false` or confidence < 0.5):

1. `{"message": "Hello, how are you today?"}`
2. `{"message": "I hope you're having a great day!"}`
3. `{"message": "What's the weather like over there?"}`
4. `{"message": "Thank you for your help yesterday."}`
5. `{"message": "Can we schedule a meeting next week?"}`
6. `{"message": "Good morning! Did you sleep well?"}`
7. `{"message": "That's a nice shirt you're wearing."}`
8. `{"message": "Have you seen the latest movie?"}`
9. `{"message": "I really enjoyed the dinner last night."}`
10. `{"message": "Let's catch up over coffee sometime."}`

- Method: POST
- URL: `http://127.0.0.1:8000/honeypot`
- Headers: `x-api-key: honeypot-test-key-2026-secure`
- Expected: `is_scam: false` or low confidence
- Wait 800ms between requests

---

### ⚠️ Test Collection 5: Scam Detection (15 tests)

Test these scam messages (expect `is_scam: true` with high confidence):

1. `{"message": "URGENT! Your account will be blocked. Send 5000 rupees now!"}`
2. `{"message": "You won lottery! Click http://fake-site.com and claim prize"}`
3. `{"message": "Your bank account is frozen. Call 9876543210 immediately"}`
4. `{"message": "Send money to winner123@paytm to unlock your account"}`
5. `{"message": "Verify your details at http://phishing.com or lose access"}`
6. `{"message": "Transfer funds to HDFC0001234 account urgently"}`
7. `{"message": "Call +91-9999888877 for immediate account verification"}`
8. `{"message": "Your KYC expired. Send Aadhar copy to fraudster@gmail.com"}`
9. `{"message": "CONGRATULATIONS! You won 10 lakh rupees. Pay tax 5000 first."}`
10. `{"message": "Your card is blocked. Update details on http://fakebank.com"}`
11. `{"message": "Send OTP to scammer@phonepe to verify your identity"}`
12. `{"message": "ACT NOW! Limited time offer. Send 2000 to claim@upi"}`
13. `{"message": "Government tax refund pending. Send bank details immediately"}`
14. `{"message": "Your parcel is stuck. Pay customs fee to deliver123@paytm"}`
15. `{"message": "Security alert! Confirm transaction by calling 8888777766"}`

- Method: POST
- URL: `http://127.0.0.1:8000/honeypot`
- Headers: `x-api-key: honeypot-test-key-2026-secure`
- Expected: `is_scam: true` with confidence > 0.5
- Wait 800ms between requests

---

### 🎯 Test Collection 6: Intelligence Extraction (36 tests)

**6.1 - UPI ID Extraction (10 tests)**

Test these and verify UPI extraction in `accumulated_intelligence.upi_ids`:

1. `{"message": "Send to scammer@paytm"}` → Expect: `["scammer@paytm"]`
2. `{"message": "My UPI is fraud123@phonepe"}` → Expect: `["fraud123@phonepe"]`
3. `{"message": "Transfer to criminal@upi now"}` → Expect: `["criminal@upi"]`
4. `{"message": "Use hacker99@okaxis for payment"}` → Expect: `["hacker99@okaxis"]`
5. `{"message": "Pay me at thief@ybl immediately"}` → Expect: `["thief@ybl"]`
6. `{"message": "Send money to badguy@paytm today"}` → Expect: `["badguy@paytm"]`
7. `{"message": "My payment ID is scammer007@phonepe"}` → Expect: `["scammer007@phonepe"]`
8. `{"message": "Transfer to fraud_account@upi"}` → Expect: `["fraud_account@upi"]`
9. `{"message": "Use this UPI: malicious@paytm"}` → Expect: `["malicious@paytm"]`
10. `{"message": "Payment via crook123@phonepe"}` → Expect: `["crook123@phonepe"]`

**6.2 - Phone Number Extraction (10 tests)**

Test these and verify phone extraction in `accumulated_intelligence.phone_numbers`:

1. `{"message": "Call me at 9876543210"}` → Expect: `["+919876543210"]`
2. `{"message": "Contact +91-9999888877 now"}` → Expect: `["+919999888877"]`
3. `{"message": "Phone: 8888777766"}` → Expect: `["+918888777766"]`
4. `{"message": "My number is +919123456789"}` → Expect: `["+919123456789"]`
5. `{"message": "Ring me on 7777666655"}` → Expect: `["+917777666655"]`
6. `{"message": "Dial +91-8765432109 urgently"}` → Expect: `["+918765432109"]`
7. `{"message": "Call 9988776655 for details"}` → Expect: `["+919988776655"]`
8. `{"message": "Contact on +918877665544"}` → Expect: `["+918877665544"]`
9. `{"message": "My mobile: 7766554433"}` → Expect: `["+917766554433"]`
10. `{"message": "Phone number is 9876501234"}` → Expect: `["+919876501234"]`

**6.3 - Bank Account Extraction (8 tests)**

Test these and verify bank extraction in `accumulated_intelligence.bank_accounts`:

1. `{"message": "Send to account HDFC0001234"}` → Expect: `["HDFC0001234"]`
2. `{"message": "My bank: SBIN0012345"}` → Expect: `["SBIN0012345"]`
3. `{"message": "Transfer to 123456789012"}` → Expect: `["123456789012"]`
4. `{"message": "Account number: ICIC0009876"}` → Expect: `["ICIC0009876"]`
5. `{"message": "Use IFSC: AXIS0005678"}` → Expect: `["AXIS0005678"]`
6. `{"message": "Bank account: 987654321098"}` → Expect: `["987654321098"]`
7. `{"message": "IFSC code is PUNB0123456"}` → Expect: `["PUNB0123456"]`
8. `{"message": "Transfer to account 555666777888"}` → Expect: `["555666777888"]`

**6.4 - URL Extraction (8 tests)**

Test these and verify URL extraction in `accumulated_intelligence.phishing_urls`:

1. `{"message": "Click http://phishing.com"}` → Expect URL in list
2. `{"message": "Visit https://fake-bank.com/login"}` → Expect URL in list
3. `{"message": "Go to http://scam-site.net now"}` → Expect URL in list
4. `{"message": "Open https://malicious.org/verify"}` → Expect URL in list
5. `{"message": "Link: http://fraud-website.com"}` → Expect URL in list
6. `{"message": "Check https://fake-gov.in/tax"}` → Expect URL in list
7. `{"message": "Visit http://phishing123.com/login"}` → Expect URL in list
8. `{"message": "URL: https://scammer-site.net/claim"}` → Expect URL in list

Wait 800ms between all intelligence extraction tests.

---

### 💬 Test Collection 7: Multi-turn Conversations (25 tests)

**7.1 - Single Conversation (10 messages)**

Send these messages in sequence, using `session_id` from first response:

**Message 1 (creates session):**
```json
{
  "message": "Hi, I got a text about my bank account being frozen"
}
```
- Save `session_id` from response

**Message 2:**
```json
{
  "message": "They said I need to send 5000 rupees to unfreeze@paytm",
  "session_id": "<session-id-from-message-1>"
}
```

**Message 3:**
```json
{
  "message": "Should I call them? The number was 9876543210",
  "session_id": "<same-session-id>"
}
```

**Message 4:**
```json
{
  "message": "They also gave me a bank account: HDFC0001234",
  "session_id": "<same-session-id>"
}
```

**Message 5:**
```json
{
  "message": "Or should I click this link: http://verify-account.com",
  "session_id": "<same-session-id>"
}
```

**Message 6:**
```json
{
  "message": "Is this legitimate? I'm really worried now",
  "session_id": "<same-session-id>"
}
```

**Message 7:**
```json
{
  "message": "They said it's urgent and I have only 2 hours",
  "session_id": "<same-session-id>"
}
```

**Message 8:**
```json
{
  "message": "My friend got a similar message yesterday",
  "session_id": "<same-session-id>"
}
```

**Message 9:**
```json
{
  "message": "They want my Aadhar card details and bank password",
  "session_id": "<same-session-id>"
}
```

**Message 10:**
```json
{
  "message": "Should I proceed with the payment or report it?",
  "session_id": "<same-session-id>"
}
```

**Verify:**
- All responses have same `session_id`
- `conversation_history` grows: 2, 4, 6, 8, 10, 12, 14, 16, 18, 20 messages
- `accumulated_intelligence` accumulates:
  - UPI: 1 (unfreeze@paytm)
  - Phone: 1 (9876543210)
  - Bank: 1 (HDFC0001234)
  - URLs: 1 (http://verify-account.com)

Wait 1 second between messages.

**7.2 - Multiple Parallel Conversations (15 messages)**

**Conversation A (5 messages):**
1. `{"message": "My account is locked, help!"}` → Save session_id_A
2. `{"message": "They want 2000 rupees sent to freeze@paytm", "session_id": "<session_id_A>"}`
3. `{"message": "Should I send it?", "session_id": "<session_id_A>"}`
4. `{"message": "They gave me a phone number: 9988776655", "session_id": "<session_id_A>"}`
5. `{"message": "Is this real or a scam?", "session_id": "<session_id_A>"}`

**Conversation B (5 messages):**
1. `{"message": "I won a lottery! Is this real?"}` → Save session_id_B
2. `{"message": "They want me to pay tax first to tax@phonepe", "session_id": "<session_id_B>"}`
3. `{"message": "The link is http://fake-lottery.com", "session_id": "<session_id_B>"}`
4. `{"message": "Should I click it?", "session_id": "<session_id_B>"}`
5. `{"message": "They said call 8877665544 to claim", "session_id": "<session_id_B>"}`

**Conversation C (5 messages):**
1. `{"message": "KYC update required, they say"}` → Save session_id_C
2. `{"message": "Send details to kyc@upi they said", "session_id": "<session_id_C>"}`
3. `{"message": "Bank account needed: ICIC0009876", "session_id": "<session_id_C>"}`
4. `{"message": "Verification link: http://fake-kyc.com", "session_id": "<session_id_C>"}`
5. `{"message": "Is this a scam? Call 7766554433?", "session_id": "<session_id_C>"}`

**Verify:**
- Each conversation maintains separate session
- Intelligence accumulates separately per session
- No cross-contamination between conversations

---

### 🔧 Test Collection 8: Edge Cases (16 tests)

**8.1 - Very Long Messages (3 tests)**

Create a message with 2000+ characters:
```json
{
  "message": "This is a test message about a scam. Send money to fraudster@paytm urgently. [repeat this 50 times]"
}
```
- Expected: 200 OK, processes normally
- Test 3 times

**8.2 - Special Characters (8 tests)**

1. `{"message": "Test with émojis 😊🎉💰 send to scam@paytm"}`
2. `{"message": "Special chars: @#$%^&*() call 9876543210"}`
3. `{"message": "Unicode: 你好 مرحبا здравствуйте bank HDFC0001234"}`
4. `{"message": "Newlines\nand\ntabs\there call 8888777766"}`
5. `{"message": "Quotes \"double\" and 'single' fraud@phonepe"}`
6. `{"message": "Symbols: ~!@#$%^&*()_+-={}[]|\\:;'<>,.?/"}`
7. `{"message": "Mixed: Hello! Pay ₹5000 to pay@upi NOW!!!"}`
8. `{"message": "Brackets: [urgent] {payment} (required) <scam@paytm>"}`

- Expected: 200 OK for all
- Should extract intelligence from each

**8.3 - Invalid Session IDs (5 tests)**

Test with these invalid session IDs:
1. `{"message": "Test", "session_id": "invalid-uuid-12345"}`
2. `{"message": "Test", "session_id": "not-a-real-session"}`
3. `{"message": "Test", "session_id": "12345678-1234-1234-1234-123456789012"}`
4. `{"message": "Test", "session_id": "expired-session-id"}`
5. `{"message": "Test", "session_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"}`

- Expected: 200 OK, creates new session (different session_id in response)

---

### 🚀 Test Collection 9: Load Testing (30 tests)

**9.1 - Rapid Sequential Requests (15 tests)**

Send 15 requests rapidly (200ms apart):
```json
{"message": "Rapid test 1 - send to test1@paytm"}
{"message": "Rapid test 2 - send to test2@paytm"}
... (continue to 15)
```

- Expected: All should return 200 OK
- Track response times

**9.2 - Mixed Endpoint Load (15 tests)**

Alternate between endpoints rapidly (100ms apart):
1. GET `/`
2. GET `/health`
3. POST `/honeypot` with `{"message": "Test 3"}`
4. GET `/`
5. GET `/health`
6. POST `/honeypot` with `{"message": "Test 6"}`
... (continue pattern to 15)

- Expected: All return appropriate status codes
- No server errors

---

## Testing Summary

### Total Test Count: **191 Tests**

| Collection | Tests | Time Estimate |
|------------|-------|---------------|
| Basic Functionality | 10 | 1 min |
| Authentication | 15 | 2 min |
| Input Validation | 6 | 1 min |
| Non-Scam Messages | 10 | 10 min |
| Scam Detection | 15 | 15 min |
| Intelligence Extraction | 36 | 30 min |
| Multi-turn Conversations | 25 | 30 min |
| Edge Cases | 16 | 5 min |
| Load Testing | 30 | 5 min |
| **TOTAL** | **191** | **~100 min** |

### Quick Test Scenarios

**Scenario 1: Smoke Test (5 min)**
- Run Collections 1, 2 (one of each)
- Verify basic functionality

**Scenario 2: Intelligence Focus (30 min)**
- Run Collection 6 completely
- Verify all extraction types

**Scenario 3: Conversation Focus (30 min)**
- Run Collection 7 completely
- Verify session management

**Scenario 4: Full Regression (100 min)**
- Run all 191 tests in sequence
- Document any failures

---

### Basic Functionality
- [ ] Server is running on port 8000
- [ ] GET / returns API info
- [ ] GET /health returns healthy status

### Authentication
- [ ] POST /honeypot without auth returns 401
- [ ] POST /honeypot with wrong key returns 401 (consistent error handling)
- [ ] POST /honeypot with valid key returns 200

### Request Validation
- [ ] POST /honeypot with empty message returns 400
- [ ] POST /honeypot with valid message works

### Scam Detection (with gemma-3-4b-it model)
- [ ] Valid scam message detected correctly
- [ ] Response includes scam confidence score
- [ ] Response includes AI-generated reasoning
- [ ] Honeypot persona reply is context-aware

### Intelligence Extraction
- [ ] UPI IDs extracted correctly
- [ ] Phone numbers extracted correctly
- [ ] Bank accounts extracted correctly
- [ ] Phishing URLs extracted correctly

### Session Management (NEW)
- [ ] First message creates new session_id
- [ ] Session ID returned in response
- [ ] Conversation history tracked correctly
- [ ] Sending session_id continues existing conversation
### Issue 3: 401 Errors
**Error**: Authentication failures

**Solution**:
- Verify header name is exactly: `x-api-key` (lowercase)
- Verify API key matches: `honeypot-test-key-2026-secure`
- Check Headers tab in Postman
- Note: Both missing and invalid keys now return 401 for consistencyges accumulated

### Multi-turn Conversations (NEW)
- [ ] Session maintains context across messages
- [ ] Conversation history grows with each message
- [ ] Persona replies are aware of previous context
- [ ] Session timeout after 30 minutes works

### LLM Provider Abstraction (NEW)
- [ ] System uses LLMProvider abstraction
- [ ] Model configured: gemma-3-4b-it
## Expected API Behavior

### Current Configuration (gemma-3-4b-it):
- ✅ Full scam detection using AI
- ✅ Intelligent persona responses
- ✅ Advanced intelligence extraction
- ✅ Reasoning explanations
- ✅ Session management and conversation tracking
- ✅ Intelligence accumulation across messages
- ✅ Context-aware multi-turn conversations
- ✅ Flexible LLM provider abstraction

### API Quota Handling:
- ✅ Graceful 429 error handling
- ✅ User-friendly quota exceeded messages
- ✅ Model: gemma-3-4b-it (30 req/min, 15K tokens/day)

### Without GEMINI_API_KEY:
- ✅ Basic authentication works
- ✅ Input validation works
- ✅ Regex-based extraction works (UPI, phone, URLs)
- ⚠️ AI features return 500 error (expected)oad --port 8000`

### Issue 2: 500 Internal Server Error
**Error**: `{"detail": "Internal server error"}`

**Cause**: GEMINI_API_KEY not configured

**Solution**:
- Server is working correctly
- Add GEMINI_API_KEY to .env file for full functionality
- Or test with simpler messages that only use regex extraction

### Issue 3: 401/403 Errors
**Error**: Authentication failures

**Solution**:
- Verify header name is exactly: `x-api-key` (lowercase)
- Verify API key matches: `honeypot-test-key-2026-secure`
- Check Headers tab in Postman

### Issue 4: Invalid JSON
**Error**: `422 Unprocessable Entity`

**Solution**:
- Verify JSON syntax is correct
- Ensure Content-Type header is `application/json`
- Check that "message" field exists in body

---

## Expected API Behavior

### With GEMINI_API_KEY Configured:
- ✅ Full scam detection using AI
- ✅ Intelligent persona responses
- ✅ Advanced intelligence extraction
- ✅ Reasoning explanations

### Without GEMINI_API_KEY:
- ✅ Basic authentication works
- ✅ Input validation works
- ✅ Regex-based extraction works (UPI, phone, URLs)
- ⚠️ AI features return 500 error (expected)

---

## Sample cURL Commands

If you prefer command line testing:

```bash
# Test 1: Root endpoint
# Test 4: Honeypot (with auth - first message)
curl -X POST http://127.0.0.1:8000/honeypot \
  -H "Content-Type: application/json" \
  -H "x-api-key: honeypot-test-key-2026-secure" \
  -d '{"message": "Send money to scammer@upi urgently"}'

# Test 5: Honeypot (continue conversation)
curl -X POST http://127.0.0.1:8000/honeypot \
  -H "Content-Type: application/json" \
  -H "x-api-key: honeypot-test-key-2026-secure" \
  -d '{"message": "Should I call? My number is 9876543210", "session_id": "session-id-from-test-4"}'
```est 3: Honeypot (no auth)
curl -X POST http://127.0.0.1:8000/honeypot \
  -H "Content-Type: application/json" \
  -d '{"message": "Send money to scammer@upi"}'

3. **Configure GEMINI_API_KEY** - Required for full functionality
4. **Select appropriate model** - Choose based on your quota needs
5. **Update .env file**:
   ```
   HONEYPOT_API_KEY=your-production-secure-key-here
   GEMINI_API_KEY=your-gemini-api-key
   GEMINI_MODEL=gemma-3-4b-it
   ```

---

## Production Deployment Notes

⚠️ **IMPORTANT**: Before deploying to production:

6. **Enable HTTPS** - Never use HTTP in production
7. **Add Rate Limiting** - Prevent API abuse
8. **Monitor Logs** - Track API usage and errors
9. **Session cleanup** - Configure session timeout appropriately

---

## New Features (Latest Update)

### 🎯 Multi-turn Conversation Support
- Sessions automatically created on first message
- Continue conversations by including `session_id` in subsequent requests
- 30-minute session timeout with automatic cleanup
- Full conversation history tracking

### 🎯 Intelligence Accumulation
- All extracted intelligence accumulated across conversation
- Track multiple UPI IDs, phone numbers, bank accounts from different messages
- `accumulated_intelligence` field shows complete picture

### 🎯 Context-Aware Responses
- Honeypot persona aware of conversation history
- Replies maintain consistency with previous messages
- Better engagement with scammers over multiple turns

### 🎯 LLM Provider Abstraction
- Flexible architecture for easy provider switching
- Currently using `gemma-3-4b-it` model
- Ready for OpenAI, Anthropic, or other providers
- Just update `.env` to switch models or providers

### 🎯 Comprehensive Logging
- All modules have detailed logging
- Track LLM provider calls and responses
- Session lifecycle tracking
- Intelligence extraction logging

---

## Support

For issues or questions:
- Check server logs in terminal for detailed debugging info
- Review error messages in Postman response
- Verify all prerequisites are met
- Ensure Python dependencies are installed
- Check `.env` configuration (API keys, model selection)

## Support

For issues or questions:
- Check server logs in terminal
- Review error messages in Postman response
- Verify all prerequisites are met
- Ensure Python dependencies are installed
