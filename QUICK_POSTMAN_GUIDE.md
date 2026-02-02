# 🚀 Quick Postman Test - Honeypot API

## Step 1: Start Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```

## Step 2: Import to Postman

### Quick Test Request
```
Method: POST
URL: http://127.0.0.1:8000/honeypot

Headers:
x-api-key: honeypot-test-key-2026-secure
Content-Type: application/json

Body (JSON):
{
  "message": "Send money to scammer@paytm urgently! Call 9876543210"
}
```

## Step 3: Expected Results

✅ **Status 200** - Request successful
✅ **is_scam: true** - Detected as scam
✅ **extracted_intelligence** - Contains UPI, phone number
✅ **confidence** - Score between 0-1

---

## All Endpoints Quick Reference

| Test | Method | URL | Headers | Expected |
|------|--------|-----|---------|----------|
| API Info | GET | `/` | None | 200 OK |
| Health | GET | `/health` | None | 200 OK |
| No Auth | POST | `/honeypot` | None | 401 |
| Bad Auth | POST | `/honeypot` | `x-api-key: wrong` | 403 |
| Valid | POST | `/honeypot` | `x-api-key: honeypot-test-key-2026-secure` | 200 |

---

## Test Messages

### Scam Message (High Confidence)
```json
{
  "message": "URGENT! Send money to fraud@upi or call +91-9876543210. Account: 123456789012. Click http://scam.com"
}
```

### Normal Message (Low Confidence)
```json
{
  "message": "Hello! How are you doing today?"
}
```

### Edge Case - Empty
```json
{
  "message": ""
}
```
Expected: 400 Bad Request

---

## ⚡ Fastest Test (Copy-Paste)

**cURL Command:**
```bash
curl -X POST http://127.0.0.1:8000/honeypot -H "Content-Type: application/json" -H "x-api-key: honeypot-test-key-2026-secure" -d "{\"message\": \"Send money to scammer@upi urgently\"}"
```

**PowerShell Command:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/honeypot" -Method Post -Headers @{"x-api-key"="honeypot-test-key-2026-secure"} -Body '{"message":"Send money to scammer@upi urgently"}' -ContentType "application/json"
```

---

## 🔑 API Key
```
honeypot-test-key-2026-secure
```

**⚠️ For testing only! Change in production!**
