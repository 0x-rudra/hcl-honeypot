# Agentic Honeypot API

A stateless, intelligent API for detecting scam messages, generating honeypot replies, and extracting scam intelligence using **Google AI Studio agents**.

## 🚀 Features

- **🕵️ Agent-Based Scam Detection**: Uses Google AI Studio agents with expert scam detection instructions
- **🎭 Honeypot Persona Generation**: AI agents create human-like, confused responses to engage scammers
- **🔍 Intelligence Extraction**: Specialized agents extract UPI IDs, phone numbers, URLs, and bank accounts
- **⚡ Stateless Architecture**: Single request → single response, no databases needed
- **🔐 API Key Authentication**: Secured with `x-api-key` header validation

## 📚 Documentation

- **[⚡ Quick Start Guide](QUICK_START.md)** - Get running in 5 minutes!
- **[🏗️ Architecture Overview](ARCHITECTURE.md)** - Visual diagrams and detailed system architecture
- **[🔑 API Key Setup Guide](API_KEY_REFERENCE.md)** - Quick reference for where to put your Google AI Studio API key
- **[📖 Google AI Studio Setup](GOOGLE_AI_STUDIO_SETUP.md)** - Detailed guide for getting and configuring API keys
- **[✅ Setup Checklist](SETUP_CHECKLIST.md)** - Step-by-step setup verification
- **[📁 File Tree](FILE_TREE.md)** - Complete project file structure
- **[📄 Project Summary](PROJECT_SUMMARY.md)** - Complete overview of the project
- **[🧪 Test Your Setup](test_setup.py)** - Run this script to verify everything is configured correctly

## 📁 Project Structure

```
honeypot-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app and /honeypot endpoint
│   ├── auth.py              # API key validation
│   ├── config.py            # Configuration and agent settings
│   ├── scam_detector.py     # Scam detection agent
│   ├── persona.py           # Honeypot persona agent
│   ├── extractor.py         # Intelligence extraction agent
│   └── schemas.py           # Pydantic models
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── .env.example            # Environment variable template
├── .gitignore             # Git ignore rules
├── test_setup.py          # Configuration test script
├── API_KEY_REFERENCE.md   # API key quick reference
├── GOOGLE_AI_STUDIO_SETUP.md  # Detailed setup guide
└── README.md              # This file
```

## 🛠️ Installation

### Prerequisites

1. **Get Google AI Studio API Key**
   - Go to [Google AI Studio](https://aistudio.google.com/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy your API key (starts with `AIza...`)
   - This key is used for all agent-based operations (scam detection, persona generation, intelligence extraction)

### Local Setup

1. **Clone the repository**
   ```bash
   cd honeypot-api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:
   ```bash
   # Copy the example file
   cp .env.example .env
   ```

   Edit `.env` and add your keys:
   ```env
   # Your Google AI Studio API Key (from https://aistudio.google.com/apikey)
   GEMINI_API_KEY=AIzaSy...your-actual-key-here

   # Your custom API key for authentication
   HONEYPOT_API_KEY=your-secret-api-key

   # Optional settings
   DEBUG=False
   PORT=8000
   ```

   Or set them as environment variables:
   ```bash
   # Linux/Mac
   export GEMINI_API_KEY="AIzaSy...your-actual-key-here"
   export HONEYPOT_API_KEY="your-secret-api-key"

   # Windows PowerShell
   $env:GEMINI_API_KEY="AIzaSy...your-actual-key-here"
   $env:HONEYPOT_API_KEY="your-secret-api-key"
   ```

5. **Run the server**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

### Docker Setup

1. **Build the image**
   ```bash
   docker build -t honeypot-api .
   ```

2. **Run the container**
   ```bash
   docker run \
     -e GEMINI_API_KEY="AIzaSy...your-actual-key-here" \
     -e HONEYPOT_API_KEY="your-secret-api-key" \
     -p 8000:8000 \
     honeypot-api
   ```

   Or with a `.env` file:
   ```bash
   docker run --env-file .env -p 8000:8000 honeypot-api
   ```

## API Usage

### Endpoint: POST /honeypot

**Headers:**
```
x-api-key: your-secret-api-key
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Your account is blocked. Send UPI to verify."
}
```

**Response:**
```json
{
  "is_scam": true,
  "confidence": 0.93,
  "agent_reply": "Oh no 😟 I just received this message. What should I do next?",
  "extracted_intelligence": {
    "bank_accounts": [],
    "upi_ids": ["scammer@upi"],
    "phone_numbers": [],
    "phishing_urls": []
  },
  "reasoning": "Message creates urgency and impersonates a bank authority."
}
```

### Health Check: GET /health

**Response:**
```json
{
  "status": "healthy"
}
```

### Root Info: GET /

**Response:**
```json
{
  "name": "Agentic Honeypot API",
  "version": "1.0.0",
  "endpoint": "/honeypot",
  "method": "POST"
}
```

## Architecture

### Google AI Studio Agent-Based System

This API uses **Google AI Studio** to build specialized agents for each task:

1. **Scam Detector Agent**: Analyzes messages with expert instructions for identifying phishing, urgency manipulation, and social engineering
2. **Honeypot Persona Agent**: Generates human-like responses with a confused, cooperative character
3. **Intelligence Extractor Agent**: Precisely extracts scam indicators (UPI, phone, URLs, accounts)

Each agent is configured with:
- Custom system instructions defining its role and expertise
- Generation parameters (temperature, top_p, top_k) optimized for its task
- The Google AI Studio API key for authentication

### Module 1: Authentication (`auth.py`)
- Validates `x-api-key` header
- Rejects unauthorized requests with 401/403 status

### Module 2: Scam Detection (`scam_detector.py`)
- **Agent-Based Detection**: Uses Google AI Studio agent with scam detection expertise
- **Keyword Scoring**: Pre-analysis using weighted scam indicators
- **LLM Classification**: Agent provides final classification, confidence, and reasoning
- **Output**: `is_scam`, `confidence`, `reasoning`

### Module 3: Honeypot Persona (`persona.py`)
- **Agent-Based Generation**: Uses Google AI Studio agent with persona characteristics
- Generates 1-2 sentence replies with confused, cooperative tone
- Higher temperature (0.9) for varied, natural responses
- Encourages scammer engagement

### Module 4: Intelligence Extractor (`extractor.py`)
- **Agent-Based Extraction**: Google AI Studio agent for precise indicator extraction
- **Regex Extraction** (Primary):
  - UPI IDs: `user@upi` format
  - Phone Numbers: Indian format (+91XXXXXXXXXX)
  - URLs: HTTP/HTTPS links
  - Bank Accounts: Numeric patterns
- **LLM Fallback**: If regex finds nothing

### Module 5: Response Builder (`schemas.py`)
- Pydantic models for strict schema validation
- No LLM used for JSON formatting
- Automatic deduplication and normalization

## Execution Flow

```
POST /honeypot
    ↓
Validate x-api-key
    ↓
Detect Scam (Keyword + LLM)
    ↓
is_scam == false? → Return JSON with is_scam=false
    ↓
is_scam == true?
    ↓
Generate Honeypot Reply
    ↓
Extract Intelligence
    ↓
Build & Return JSON Response
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | **Required** | Google AI Studio API key (get from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)) |
| `HONEYPOT_API_KEY` | `your-secret-key-here` | Your custom API key for client authentication |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Google AI model to use |
| `PORT` | `8000` | Server port |
| `DEBUG` | `False` | Debug mode |

### Agent Configuration

These are pre-configured in `config.py` for optimal agent performance:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `AGENT_TEMPERATURE` | `0.7` | Balanced creativity/consistency for scam detection |
| `AGENT_TOP_P` | `0.95` | Nucleus sampling for diverse but relevant responses |
| `AGENT_TOP_K` | `40` | Top-k sampling for token selection |
| `AGENT_MAX_OUTPUT_TOKENS` | `2048` | Maximum response length |

**Note**: The persona generator uses temperature `0.9` for more varied responses, while the extractor uses `0.1` for precise extraction.

## Example cURL Requests

### Detect a Scam Message
```bash
curl -X POST http://localhost:8000/honeypot \
  -H "x-api-key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Your Amazon account has been compromised. Click here to verify your credentials immediately."
  }'
```

### Analyze a Legitimate Message
```bash
curl -X POST http://localhost:8000/honeypot \
  -H "x-api-key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi, how are you doing today?"
  }'
```

## Design Constraints

- ✅ **Stateless**: No session management or state persistence
- ✅ **Single Request-Response**: One call in, one JSON response out
- ✅ **No Databases**: All processing in-memory
- ✅ **No Local ML Models**: Uses Gemini API for intelligence
- ✅ **No File Storage**: Responses never persisted

## Error Handling

| Status | Reason |
|--------|--------|
| 200 | Success |
| 400 | Invalid request (empty message) |
| 401 | Missing API key |
| 403 | Invalid API key |
| 500 | Internal server error |

## Performance Notes

- **Scam Detection**: ~1-2 seconds (includes LLM call)
- **Reply Generation**: ~0.5-1 second
- **Intelligence Extraction**: <100ms (regex) or ~0.5 seconds (LLM fallback)
- **Total Latency**: ~2-3 seconds per request

## Security Notes

1. Never commit `.env` files with real API keys
2. Rotate `HONEYPOT_API_KEY` regularly
3. Use HTTPS in production
4. Rate limit the `/honeypot` endpoint
5. Monitor for suspicious patterns in extracted intelligence

## Future Enhancements

- [ ] Caching layer for repeated messages
- [ ] Batch processing endpoint
- [ ] Advanced ML models for entity recognition
- [ ] Integration with threat intelligence feeds
- [ ] Metrics and monitoring dashboard

## License

MIT License

## Support

For issues or questions, please contact the development team.

# ⚡ Quick Start Guide (5 Minutes)

Get your Honeypot API running in 5 minutes!

---

## Step 1: Get Google AI Studio API Key (2 min)

1. Open browser: https://aistudio.google.com/apikey
2. Sign in with Google account
3. Click "**Create API Key**"
4. Copy the key (starts with `AIza`)

✅ You now have your API key!

---

## Step 2: Setup Environment (1 min)

Open PowerShell in project directory:

```powershell
# Navigate to project
cd m:\Desktop\PROGRAMS\Project\HCL-honeypot

# Set API keys
$env:GEMINI_API_KEY="AIzaSy...paste-your-key-here"
$env:HONEYPOT_API_KEY="my-secret-key-123"
```

✅ Environment configured!

---

## Step 3: Install Dependencies (1 min)

```powershell
# Install packages
pip install -r requirements.txt
```

✅ Dependencies installed!

---

## Step 4: Test Configuration (30 sec)

```powershell
# Run test script
python test_setup.py
```

Expected output:
```
✅ PASS - Environment Variables
✅ PASS - Package Imports
✅ PASS - API Connection
✅ PASS - Agent Configuration
✅ PASS - Application Modules

✅ All tests passed!
```

✅ Everything works!

---

## Step 5: Start Server (30 sec)

```powershell
# Start the API server
python -m uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

✅ Server running!

---

## Step 6: Test API (30 sec)

Open a new PowerShell window and run:

```powershell
# Test the honeypot endpoint
$headers = @{
    "x-api-key" = "my-secret-key-123"
    "Content-Type" = "application/json"
}

$body = @{
    message = "Your account is blocked. Send UPI to verify."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/honeypot" -Method Post -Headers $headers -Body $body
```

Expected output:
```json
{
  "is_scam": true,
  "confidence": 0.93,
  "agent_reply": "Oh no 😟 What should I do next?",
  "extracted_intelligence": {
    "bank_accounts": [],
    "upi_ids": [],
    "phone_numbers": [],
    "phishing_urls": []
  },
  "reasoning": "Creates urgency and impersonates authority..."
}
```

✅ **Success! Your Honeypot API is working!**

---

## 🎯 You're Done!

Your API is now ready to:
- Detect scam messages
- Generate honeypot replies
- Extract scam intelligence

---

## 📚 Next Steps

### Want to learn more?
- Read `PROJECT_SUMMARY.md` for complete overview
- Read `ARCHITECTURE.md` for system design
- Read `README.md` for detailed documentation

### Want to customize?
- Edit `app/config.py` for agent settings
- Modify `app/scam_detector.py` for detection logic
- Change `app/persona.py` for different reply styles

### Want to deploy?
- Use Docker: `docker build -t honeypot-api .`
- Or deploy to cloud platforms

---

## 🐛 Troubleshooting

### Test script fails?
```powershell
# Make sure API key is set
$env:GEMINI_API_KEY

# Should output your key, not blank
```

### Server won't start?
```powershell
# Check if port is already in use
netstat -ano | findstr :8000

# Kill the process or use different port
python -m uvicorn app.main:app --reload --port 8001
```

### API returns errors?
- Check `x-api-key` header matches `HONEYPOT_API_KEY`
- Verify `GEMINI_API_KEY` is valid
- Check terminal logs for error messages

---

## 📋 Command Cheat Sheet

```powershell
# Set environment variables
$env:GEMINI_API_KEY="AIzaSy..."
$env:HONEYPOT_API_KEY="my-secret-key"

# Install dependencies
pip install -r requirements.txt

# Test configuration
python test_setup.py

# Start server
python -m uvicorn app.main:app --reload --port 8000

# Test API (in new window)
$headers = @{"x-api-key"="my-secret-key"; "Content-Type"="application/json"}
$body = @{message="Test message"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/honeypot" -Method Post -Headers $headers -Body $body
```

---

## 🎉 Congratulations!

You've successfully set up the Honeypot API with Google AI Studio agents!

**Total time**: ~5 minutes
**Result**: Fully functional scam detection API

---

## 💡 Tips

1. **Save your API keys** - Store them securely
2. **Use .env file** - For permanent configuration
3. **Monitor usage** - Check Google AI Studio dashboard
4. **Read docs** - Explore other documentation files
5. **Test thoroughly** - Try different scam messages

---

## 📞 Need Help?

- Check `SETUP_CHECKLIST.md` for detailed steps
- Read `GOOGLE_AI_STUDIO_SETUP.md` for API key help
- Review `API_KEY_REFERENCE.md` for quick reference
- Run `python test_setup.py` for diagnostics

---

**Built with Google AI Studio agents 🚀**
# 🎯 Honeypot API - Complete Summary

## What We Built

A **Google AI Studio Agent-Based Honeypot API** that:
1. Detects scam messages with AI-powered analysis
2. Generates human-like honeypot replies to engage scammers
3. Extracts scam intelligence (UPI IDs, phone numbers, URLs, bank accounts)
4. Returns everything in a single JSON response

---

## 📂 Project Files Created

### Core Application Files (app/)
```
app/
├── __init__.py           - Package initialization
├── main.py              - FastAPI server & /honeypot endpoint
├── auth.py              - x-api-key validation
├── config.py            - Configuration & agent settings
├── scam_detector.py     - 🕵️ Scam Detection Agent
├── persona.py           - 🎭 Honeypot Persona Agent
├── extractor.py         - 🔍 Intelligence Extraction Agent
└── schemas.py           - Pydantic request/response models
```

### Documentation Files
```
README.md                      - Main project documentation
ARCHITECTURE.md                - System architecture & diagrams
GOOGLE_AI_STUDIO_SETUP.md      - How to get API keys
API_KEY_REFERENCE.md           - Quick API key reference
```

### Configuration Files
```
requirements.txt         - Python dependencies
Dockerfile              - Docker container setup
.env.example            - Environment variable template
.gitignore             - Git ignore rules
test_setup.py          - Configuration verification script
```

---

## 🔑 Two API Keys Required

### 1. GEMINI_API_KEY (Google AI Studio)
- **Get it from**: https://aistudio.google.com/apikey
- **Used for**: All three AI agents (scam detection, persona, extraction)
- **Format**: `AIzaSy...` (starts with AIza)

### 2. HONEYPOT_API_KEY (Your Custom Key)
- **Set it yourself**: Any secret string you choose
- **Used for**: Client authentication (x-api-key header)
- **Format**: Any string (e.g., `my-secret-key-123`)

---

## 🏗️ Architecture: 3 Specialized Agents

### Agent 1: 🕵️ Scam Detector
**File**: `app/scam_detector.py`
- Analyzes messages for scam patterns
- Keyword scoring + LLM classification
- Temperature: 0.7 (balanced)
- **Output**: is_scam, confidence, reasoning

### Agent 2: 🎭 Honeypot Persona
**File**: `app/persona.py`
- Generates human-like replies
- Confused, cooperative tone
- Temperature: 0.9 (creative)
- **Output**: 1-2 sentence engaging reply

### Agent 3: 🔍 Intelligence Extractor
**File**: `app/extractor.py`
- Extracts scam indicators
- Regex + LLM fallback
- Temperature: 0.1 (precise)
- **Output**: UPI IDs, phones, URLs, accounts

---

## 🚀 Quick Start (3 Steps)

### Step 1: Get Google AI Studio API Key
```
1. Go to: https://aistudio.google.com/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key (AIzaSy...)
```

### Step 2: Configure Environment
```powershell
# PowerShell
$env:GEMINI_API_KEY="AIzaSy...your-actual-key"
$env:HONEYPOT_API_KEY="your-secret-key"

# Or create .env file:
copy .env.example .env
# Then edit .env with your keys
```

### Step 3: Install & Run
```powershell
# Install dependencies
pip install -r requirements.txt

# Test configuration
python test_setup.py

# Start server
python -m uvicorn app.main:app --reload --port 8000
```

---

## 📡 API Usage Example

### Request
```bash
POST http://localhost:8000/honeypot
Headers:
  x-api-key: your-secret-key
  Content-Type: application/json
Body:
  {
    "message": "Your account is blocked. Send UPI to verify."
  }
```

### Response
```json
{
  "is_scam": true,
  "confidence": 0.93,
  "agent_reply": "Oh no 😟 What should I do next?",
  "extracted_intelligence": {
    "bank_accounts": [],
    "upi_ids": ["scammer@upi"],
    "phone_numbers": [],
    "phishing_urls": []
  },
  "reasoning": "Message creates urgency and impersonates authority."
}
```

---

## 🎓 Where to Find Information

### Want to understand the system?
→ Read **[ARCHITECTURE.md](ARCHITECTURE.md)**

### Need to setup API keys?
→ Read **[GOOGLE_AI_STUDIO_SETUP.md](GOOGLE_AI_STUDIO_SETUP.md)**

### Quick API key reference?
→ Read **[API_KEY_REFERENCE.md](API_KEY_REFERENCE.md)**

### Want to test if everything works?
→ Run **`python test_setup.py`**

### General information?
→ Read **[README.md](README.md)**

---

## 🔍 Where API Keys Are Used

### GEMINI_API_KEY Flow
```
Environment Variable
    ↓
app/config.py (loads it)
    ↓
    ├─→ app/scam_detector.py (Agent 1)
    ├─→ app/persona.py (Agent 2)
    └─→ app/extractor.py (Agent 3)
```

### HONEYPOT_API_KEY Flow
```
Environment Variable
    ↓
app/config.py (loads it)
    ↓
app/auth.py (validates incoming requests)
```

---

## 📊 Key Features

### ✅ Agent-Based Intelligence
- Each agent has specialized system instructions
- Optimized temperature settings per task
- Uses Google AI Studio's Gemini 2.0 Flash model

### ✅ Stateless Design
- No databases
- No session management
- Single request → single response

### ✅ Security
- API key authentication
- Environment variable configuration
- .gitignore protects sensitive files

### ✅ Developer Friendly
- Comprehensive documentation
- Test scripts included
- Docker support
- Type hints with Pydantic

---

## 🧪 Testing Your Setup

Run the test script to verify everything:

```powershell
python test_setup.py
```

Expected output:
```
✅ PASS - Environment Variables
✅ PASS - Package Imports
✅ PASS - API Connection
✅ PASS - Agent Configuration
✅ PASS - Application Modules

✅ All tests passed! Your API is ready to use.
```

---

## 📦 Dependencies

From `requirements.txt`:
```
fastapi==0.104.1           # Web framework
uvicorn[standard]==0.24.0   # ASGI server
pydantic==2.5.0            # Data validation
google-generativeai==0.3.0  # Google AI Studio SDK
python-dotenv==1.0.0       # Environment variables
```

---

## 🐳 Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t honeypot-api .

# Run container
docker run \
  -e GEMINI_API_KEY="AIzaSy...your-key" \
  -e HONEYPOT_API_KEY="your-secret-key" \
  -p 8000:8000 \
  honeypot-api
```

---

## 🎯 What Each File Does

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI server, /honeypot endpoint, orchestrates agents |
| `app/auth.py` | Validates x-api-key header |
| `app/config.py` | Loads environment variables, agent settings |
| `app/scam_detector.py` | Agent 1: Detects scams with AI |
| `app/persona.py` | Agent 2: Generates honeypot replies |
| `app/extractor.py` | Agent 3: Extracts scam indicators |
| `app/schemas.py` | Pydantic models for request/response |
| `test_setup.py` | Verifies configuration is correct |
| `.env.example` | Template for environment variables |
| `.gitignore` | Prevents committing sensitive files |

---

## ✨ Key Innovations

1. **Agent-Based Architecture**: Each task handled by a specialized Google AI Studio agent
2. **System Instructions**: Agents have expert-level instructions defining their role
3. **Optimized Parameters**: Temperature, top_p, top_k tuned per agent
4. **Hybrid Extraction**: Regex for speed, LLM for fallback
5. **Stateless Design**: No persistence, pure API functionality

---

## 🎉 You're Ready!

Your Honeypot API is now fully configured with Google AI Studio agents!

**Next Steps**:
1. Run `python test_setup.py` to verify setup
2. Start the server: `python -m uvicorn app.main:app --reload --port 8000`
3. Test with curl or Postman
4. Integrate into your application

**Get Help**:
- Read the documentation files
- Check the architecture diagrams
- Review the test script output

---

## 📞 Support & Resources

- **Google AI Studio**: https://aistudio.google.com/
- **Gemini API Docs**: https://ai.google.dev/
- **FastAPI Docs**: https://fastapi.tiangolo.com/

---

**Built with ❤️ using Google AI Studio agents**
# Google AI Studio Setup Guide

This guide explains how to get your API key from Google AI Studio and configure it for the Honeypot API.

## Step 1: Get Your Google AI Studio API Key

1. **Visit Google AI Studio**
   - Go to: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

2. **Sign In**
   - Use your Google account to sign in
   - Accept any terms of service if prompted

3. **Create API Key**
   - Click the "**Create API Key**" button
   - Choose an existing Google Cloud project or create a new one
   - Your API key will be generated (format: `AIzaSy...`)

4. **Copy Your API Key**
   - Copy the entire API key to your clipboard
   - Store it securely (treat it like a password)

## Step 2: Configure the Honeypot API

### Option A: Using `.env` file (Recommended)

1. Navigate to your project directory:
   ```bash
   cd m:\Desktop\PROGRAMS\Project\HCL-honeypot
   ```

2. Copy the example file:
   ```bash
   copy .env.example .env
   ```

3. Edit `.env` and paste your API key:
   ```env
   GEMINI_API_KEY=AIzaSy...your-actual-key-here
   HONEYPOT_API_KEY=your-secret-api-key
   ```

4. Install the `python-dotenv` package (already in `requirements.txt`):
   ```bash
   pip install python-dotenv
   ```

### Option B: Using Environment Variables

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="AIzaSy...your-actual-key-here"
$env:HONEYPOT_API_KEY="your-secret-api-key"
```

**Windows CMD:**
```cmd
set GEMINI_API_KEY=AIzaSy...your-actual-key-here
set HONEYPOT_API_KEY=your-secret-api-key
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="AIzaSy...your-actual-key-here"
export HONEYPOT_API_KEY="your-secret-api-key"
```

## Step 3: Verify Configuration

Run this Python script to test your API key:

```python
import google.generativeai as genai
import os

# Test if API key is set
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not found!")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...")

# Test API connection
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Say hello")
    print("✅ API connection successful!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ API connection failed: {e}")
```

Save as `test_api.py` and run:
```bash
python test_api.py
```

## Step 4: Start the Honeypot API

```bash
python -m uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Where the API Key is Used

The `GEMINI_API_KEY` is used in three modules:

1. **`app/scam_detector.py`**
   - Configures the scam detection agent
   - Analyzes messages for scam indicators
   - Provides confidence scores and reasoning

2. **`app/persona.py`**
   - Configures the honeypot persona agent
   - Generates human-like replies to scammers
   - Creates confused, cooperative responses

3. **`app/extractor.py`**
   - Configures the intelligence extraction agent
   - Extracts UPI IDs, phone numbers, URLs, and bank accounts
   - Falls back to LLM when regex finds nothing

## Agent Configuration

Each agent uses the API key with specific settings:

```python
# From config.py
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL: str = "gemini-2.0-flash"
AGENT_TEMPERATURE: float = 0.7
AGENT_TOP_P: float = 0.95
AGENT_TOP_K: int = 40
AGENT_MAX_OUTPUT_TOKENS: int = 2048
```

## Security Best Practices

1. **Never commit `.env` files**
   - Add `.env` to `.gitignore`
   - Use `.env.example` for templates only

2. **Rotate API keys regularly**
   - Generate new keys periodically
   - Revoke old keys in Google AI Studio

3. **Use different keys for different environments**
   - Development: separate key
   - Production: separate key
   - Testing: separate key

4. **Monitor API usage**
   - Check [Google AI Studio dashboard](https://aistudio.google.com/)
   - Set up quota alerts
   - Track costs and usage patterns

## Troubleshooting

### Error: "GEMINI_API_KEY environment variable not set"
- Make sure you've set the environment variable
- Check for typos in the variable name
- Restart your terminal after setting variables

### Error: "Invalid API key"
- Verify your API key is correct (starts with `AIza`)
- Check for extra spaces or quotes
- Regenerate the key in Google AI Studio

### Error: "API connection failed"
- Check your internet connection
- Verify firewall/proxy settings
- Ensure Google AI Studio services are available

## Additional Resources

- [Google AI Studio Documentation](https://ai.google.dev/)
- [Gemini API Quickstart](https://ai.google.dev/tutorials/python_quickstart)
- [API Key Management](https://aistudio.google.com/apikey)
# 📁 Complete Project File Tree

```
HCL-honeypot/
│
├── 📁 app/                          # Core application code
│   ├── __init__.py                  # Package initialization
│   ├── main.py                      # FastAPI server & /honeypot endpoint
│   ├── auth.py                      # API key validation
│   ├── config.py                    # Configuration & agent settings
│   ├── scam_detector.py             # 🕵️ Agent 1: Scam Detection
│   ├── persona.py                   # 🎭 Agent 2: Honeypot Persona
│   ├── extractor.py                 # 🔍 Agent 3: Intelligence Extraction
│   └── schemas.py                   # Pydantic models
│
├── 📄 README.md                     # Main project documentation
├── 📄 PROJECT_SUMMARY.md            # Complete project overview
├── 📄 ARCHITECTURE.md               # System architecture & diagrams
├── 📄 GOOGLE_AI_STUDIO_SETUP.md     # How to get Google AI Studio API key
├── 📄 API_KEY_REFERENCE.md          # Quick API key reference
├── 📄 SETUP_CHECKLIST.md            # Step-by-step setup checklist
├── 📄 FILE_TREE.md                  # This file
│
├── 🐍 test_setup.py                 # Configuration verification script
├── 📦 requirements.txt               # Python dependencies
├── 🐳 Dockerfile                    # Docker container configuration
├── 📝 .env.example                  # Environment variable template
└── 🚫 .gitignore                    # Git ignore rules
```

---

## 📚 File Purposes

### Core Application Files

#### `app/main.py` (Main API Server)
- FastAPI application initialization
- `/honeypot` endpoint implementation
- Agent orchestration
- Request/response handling
- Error handling

#### `app/auth.py` (Authentication)
- `validate_api_key()` function
- Validates `x-api-key` header
- Returns 401/403 on auth failures

#### `app/config.py` (Configuration)
- Loads `GEMINI_API_KEY` from environment
- Loads `HONEYPOT_API_KEY` from environment
- Agent parameters (temperature, top_p, etc.)
- Server settings (host, port, debug)

#### `app/scam_detector.py` (Agent 1)
- `ScamDetector` class
- Keyword scoring algorithm
- Google AI Studio agent for scam classification
- System instructions: scam detection expertise
- Returns: is_scam, confidence, reasoning

#### `app/persona.py` (Agent 2)
- `PersonaGenerator` class
- Google AI Studio agent for reply generation
- System instructions: confused, cooperative persona
- Returns: human-like 1-2 sentence reply

#### `app/extractor.py` (Agent 3)
- `IntelligenceExtractor` class
- Regex patterns for extraction
- Google AI Studio agent as fallback
- System instructions: precise indicator extraction
- Returns: UPI IDs, phones, URLs, bank accounts

#### `app/schemas.py` (Data Models)
- `HoneypotRequest` - Request validation
- `HoneypotResponse` - Response schema
- `ExtractedIntelligence` - Intelligence structure

---

### Documentation Files

#### `README.md` (Main Documentation)
**Size**: ~8 KB | **Lines**: ~350
- Project overview
- Features list
- Installation instructions
- API usage examples
- Configuration guide
- Links to other docs

#### `PROJECT_SUMMARY.md` (Complete Overview)
**Size**: ~12 KB | **Lines**: ~400
- What we built
- File-by-file breakdown
- Quick start guide
- API key setup
- Testing instructions
- Next steps

#### `ARCHITECTURE.md` (System Design)
**Size**: ~15 KB | **Lines**: ~500
- Visual system diagrams
- Data flow charts
- Agent details
- Configuration hierarchy
- Execution timeline
- Agent comparison table

#### `GOOGLE_AI_STUDIO_SETUP.md` (API Key Setup)
**Size**: ~10 KB | **Lines**: ~300
- Step-by-step API key acquisition
- Environment configuration options
- Verification instructions
- Where API keys are used
- Security best practices
- Troubleshooting guide

#### `API_KEY_REFERENCE.md` (Quick Reference)
**Size**: ~8 KB | **Lines**: ~250
- Where to get API key
- Where to put API key
- Where it's used in code
- Agent configuration flow
- Quick start commands

#### `SETUP_CHECKLIST.md` (Setup Verification)
**Size**: ~7 KB | **Lines**: ~300
- Pre-installation checklist
- API key setup steps
- Installation verification
- Testing checklist
- Security checklist
- Success indicators

---

### Configuration Files

#### `requirements.txt` (Dependencies)
```
fastapi==0.104.1           # Web framework
uvicorn[standard]==0.24.0   # ASGI server
pydantic==2.5.0            # Data validation
google-generativeai==0.3.0  # Google AI Studio SDK
python-dotenv==1.0.0       # Environment variables
```

#### `.env.example` (Environment Template)
```env
# Google AI Studio API Key
GEMINI_API_KEY=your-google-ai-studio-api-key-here

# Honeypot API Authentication Key
HONEYPOT_API_KEY=your-secret-api-key-here

# Optional: Debug mode
DEBUG=False

# Optional: Server port
PORT=8000
```

#### `.gitignore` (Git Ignore)
- `.env` files (protect API keys)
- `__pycache__/` (Python cache)
- Virtual environments
- IDE files
- Logs

#### `Dockerfile` (Docker Config)
- Base: Python 3.11-slim
- Installs dependencies
- Copies application code
- Exposes port 8000
- Runs uvicorn server

---

### Testing Files

#### `test_setup.py` (Configuration Tests)
- Tests environment variables
- Tests package imports
- Tests Google AI Studio API connection
- Tests agent configuration
- Tests application modules
- Provides detailed error messages

---

## 📊 File Statistics

| Category | Files | Total Size | Purpose |
|----------|-------|------------|---------|
| **Core App** | 8 | ~15 KB | Application logic |
| **Documentation** | 6 | ~60 KB | Guides & references |
| **Configuration** | 4 | ~2 KB | Setup & dependencies |
| **Testing** | 1 | ~5 KB | Verification |
| **Total** | 19 | ~82 KB | Complete project |

---

## 🔍 Where to Find Things

### Need to...?

**Understand how the system works**
→ Read `ARCHITECTURE.md`

**Setup API keys**
→ Read `GOOGLE_AI_STUDIO_SETUP.md` or `API_KEY_REFERENCE.md`

**Get started quickly**
→ Read `PROJECT_SUMMARY.md`

**Follow step-by-step setup**
→ Use `SETUP_CHECKLIST.md`

**Test configuration**
→ Run `test_setup.py`

**Understand general info**
→ Read `README.md`

**Configure environment**
→ Copy `.env.example` to `.env`

**Install dependencies**
→ Run `pip install -r requirements.txt`

**Deploy with Docker**
→ Use `Dockerfile`

---

## 🎯 Key File Relationships

```
.env or Environment Variables
    ↓
app/config.py (loads configuration)
    ↓
    ├─→ app/auth.py (uses HONEYPOT_API_KEY)
    ├─→ app/scam_detector.py (uses GEMINI_API_KEY)
    ├─→ app/persona.py (uses GEMINI_API_KEY)
    └─→ app/extractor.py (uses GEMINI_API_KEY)
    ↓
app/main.py (orchestrates everything)
    ↓
Receives requests → Returns responses
```

---

## 📋 File Creation Order

If building from scratch:

1. `requirements.txt` - Dependencies first
2. `.env.example` - Environment template
3. `.gitignore` - Protect sensitive files
4. `app/__init__.py` - Package init
5. `app/config.py` - Configuration
6. `app/schemas.py` - Data models
7. `app/auth.py` - Authentication
8. `app/scam_detector.py` - Agent 1
9. `app/persona.py` - Agent 2
10. `app/extractor.py` - Agent 3
11. `app/main.py` - Main server
12. `test_setup.py` - Testing script
13. `Dockerfile` - Docker config
14. Documentation files
15. This file tree

---

## 🔐 Security Files

**Protected by .gitignore**:
- `.env` - Contains actual API keys
- `__pycache__/` - Python bytecode
- `venv/` - Virtual environment

**Public (safe to commit)**:
- `.env.example` - Template only
- All `.py` files - No hardcoded secrets
- All `.md` files - Documentation only

---

## 🚀 Execution Entry Points

**Development Server**:
```powershell
python -m uvicorn app.main:app --reload --port 8000
```
→ Starts `app/main.py`

**Configuration Test**:
```powershell
python test_setup.py
```
→ Runs `test_setup.py`

**Docker Container**:
```powershell
docker run honeypot-api
```
→ Uses `Dockerfile`

---

## 📖 Documentation Reading Order

**For New Users**:
1. `README.md` - Get overview
2. `GOOGLE_AI_STUDIO_SETUP.md` - Get API key
3. `API_KEY_REFERENCE.md` - Quick setup
4. `SETUP_CHECKLIST.md` - Follow steps
5. Run `test_setup.py` - Verify
6. `PROJECT_SUMMARY.md` - Full understanding

**For Developers**:
1. `ARCHITECTURE.md` - Understand system
2. `app/main.py` - Entry point
3. `app/scam_detector.py` - Agent 1
4. `app/persona.py` - Agent 2
5. `app/extractor.py` - Agent 3
6. `app/schemas.py` - Data models

---

## ✨ File Highlights

**Most Important Files**:
- ⭐ `app/main.py` - API server
- ⭐ `app/config.py` - Configuration
- ⭐ `.env` (your copy) - API keys
- ⭐ `GOOGLE_AI_STUDIO_SETUP.md` - Setup guide

**Most Helpful Files**:
- 💡 `PROJECT_SUMMARY.md` - Complete overview
- 💡 `SETUP_CHECKLIST.md` - Step-by-step
- 💡 `test_setup.py` - Verification
- 💡 `API_KEY_REFERENCE.md` - Quick help

---

**Total: 19 files | 3 agents | 2 API keys | 1 powerful scam detection API**
# 🔑 API Key Configuration - Quick Reference

## Where to Get the API Key

**Google AI Studio**: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

1. Sign in with Google account
2. Click "Create API Key"
3. Copy the key (format: `AIzaSy...`)

---

## Where to Put the API Key

### Option 1: `.env` File (Recommended) ⭐

**Location**: Project root directory

**File**: `m:\Desktop\PROGRAMS\Project\HCL-honeypot\.env`

**Content**:
```env
GEMINI_API_KEY=AIzaSy...your-actual-key-here
HONEYPOT_API_KEY=your-secret-api-key
```

**Steps**:
```powershell
# 1. Copy example file
copy .env.example .env

# 2. Edit .env file and paste your API key
notepad .env
```

---

### Option 2: Environment Variables

**Windows PowerShell**:
```powershell
$env:GEMINI_API_KEY="AIzaSy...your-actual-key-here"
$env:HONEYPOT_API_KEY="your-secret-api-key"
```

**Windows CMD**:
```cmd
set GEMINI_API_KEY=AIzaSy...your-actual-key-here
set HONEYPOT_API_KEY=your-secret-api-key
```

---

## Where the API Key is Used in Code

### 1. Configuration Module
**File**: `app/config.py`
```python
GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
```

### 2. Scam Detector Agent
**File**: `app/scam_detector.py`
```python
genai.configure(api_key=Config.GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name=Config.GEMINI_MODEL,
    generation_config=generation_config,
    system_instruction=SCAM_DETECTOR_AGENT_INSTRUCTIONS,
)
```

### 3. Honeypot Persona Agent
**File**: `app/persona.py`
```python
genai.configure(api_key=Config.GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name=Config.GEMINI_MODEL,
    generation_config=generation_config,
    system_instruction=HONEYPOT_AGENT_INSTRUCTIONS,
)
```

### 4. Intelligence Extractor Agent
**File**: `app/extractor.py`
```python
genai.configure(api_key=Config.GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name=Config.GEMINI_MODEL,
    generation_config=generation_config,
    system_instruction=EXTRACTOR_AGENT_INSTRUCTIONS,
)
```

---

## How to Verify Configuration

Run the test script:
```powershell
python test_setup.py
```

Expected output:
```
✅ GEMINI_API_KEY found: AIzaSy...
✅ API connection successful!
✅ All tests passed!
```

---

## Agent Configuration Flow

```
Environment Variable (GEMINI_API_KEY)
         ↓
    config.py (loads from env)
         ↓
    ┌────┴────┬──────────┬─────────────┐
    ↓         ↓          ↓             ↓
scam_detector persona  extractor    main.py
    ↓         ↓          ↓             ↓
 Agent 1   Agent 2   Agent 3      API Server
```

---

## Three Specialized Agents

### 🕵️ Agent 1: Scam Detector
- **Purpose**: Analyze messages for scam indicators
- **Temperature**: 0.7 (balanced)
- **Instructions**: Scam detection expertise
- **Output**: is_scam, confidence, reasoning

### 🎭 Agent 2: Honeypot Persona
- **Purpose**: Generate human-like replies
- **Temperature**: 0.9 (creative)
- **Instructions**: Confused, cooperative character
- **Output**: 1-2 sentence engaging reply

### 🔍 Agent 3: Intelligence Extractor
- **Purpose**: Extract scam indicators
- **Temperature**: 0.1 (precise)
- **Instructions**: Pattern extraction expertise
- **Output**: UPI IDs, phones, URLs, accounts

---

## Security Notes

- ✅ `.env` file is in `.gitignore` (won't be committed)
- ✅ Never hardcode API keys in source files
- ✅ Use different keys for dev/prod environments
- ✅ Rotate keys regularly in Google AI Studio

---

## Quick Start Commands

```powershell
# 1. Set API key
$env:GEMINI_API_KEY="AIzaSy...your-key"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test configuration
python test_setup.py

# 4. Start server
python -m uvicorn app.main:app --reload --port 8000

# 5. Test API
curl -X POST http://localhost:8000/honeypot `
  -H "x-api-key: your-secret-key" `
  -H "Content-Type: application/json" `
  -d '{"message": "Your account is blocked. Send UPI to verify."}'
```

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| `GEMINI_API_KEY not set` | Set environment variable or create `.env` file |
| `Invalid API key` | Check key format (should start with `AIza`) |
| `API connection failed` | Verify internet connection and API key validity |
| `Module not found` | Run `pip install -r requirements.txt` |

---

## Files Created for API Management

1. **`.env.example`** - Template for environment variables
2. **`.gitignore`** - Prevents committing sensitive files
3. **`GOOGLE_AI_STUDIO_SETUP.md`** - Detailed setup guide
4. **`test_setup.py`** - Configuration verification script
5. **`API_KEY_REFERENCE.md`** - This file (quick reference)
