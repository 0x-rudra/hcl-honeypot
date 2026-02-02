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

**Expected Response (403 Forbidden):**
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

### Test 6: Honeypot - Valid Scam Message (POST /honeypot)

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

**Expected Response (200 OK or 500 if GEMINI_API_KEY not configured):**
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
  "reasoning": "Message contains UPI ID, phone number, urgency keywords"
}
```

---

### Test 7: Honeypot - Non-Scam Message (POST /honeypot)

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
  "reasoning": "Normal greeting message, no scam indicators"
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

## Testing Checklist

- [ ] Server is running on port 8000
- [ ] GET / returns API info
- [ ] GET /health returns healthy status
- [ ] POST /honeypot without auth returns 401
- [ ] POST /honeypot with wrong key returns 403
- [ ] POST /honeypot with empty message returns 400
- [ ] POST /honeypot with valid scam message works
- [ ] Response includes extracted intelligence
- [ ] Response includes scam confidence score

---

## Common Issues & Solutions

### Issue 1: Connection Refused
**Error**: `Error: connect ECONNREFUSED 127.0.0.1:8000`

**Solution**:
- Check if server is running
- Run: `python -m uvicorn app.main:app --reload --port 8000`

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
curl http://127.0.0.1:8000/

# Test 2: Health check
curl http://127.0.0.1:8000/health

# Test 3: Honeypot (no auth)
curl -X POST http://127.0.0.1:8000/honeypot \
  -H "Content-Type: application/json" \
  -d '{"message": "Send money to scammer@upi"}'

# Test 4: Honeypot (with auth)
curl -X POST http://127.0.0.1:8000/honeypot \
  -H "Content-Type: application/json" \
  -H "x-api-key: honeypot-test-key-2026-secure" \
  -d '{"message": "Send money to scammer@upi urgently"}'
```

---

## Production Deployment Notes

⚠️ **IMPORTANT**: Before deploying to production:

1. **Change the API Key** - Do NOT use `honeypot-test-key-2026-secure`
2. **Set Strong API Key** - Use a cryptographically secure random key
3. **Configure GEMINI_API_KEY** - Required for full functionality
4. **Update .env file**:
   ```
   HONEYPOT_API_KEY=your-production-secure-key-here
   GEMINI_API_KEY=your-gemini-api-key
   ```
5. **Enable HTTPS** - Never use HTTP in production
6. **Add Rate Limiting** - Prevent API abuse
7. **Monitor Logs** - Track API usage and errors

---

## Support

For issues or questions:
- Check server logs in terminal
- Review error messages in Postman response
- Verify all prerequisites are met
- Ensure Python dependencies are installed
