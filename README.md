# 🍯 Agentic Honeypot API

An intelligent FastAPI application that detects scam messages, generates honeypot responses, extracts intelligence indicators, and maintains multi-turn conversations with scammers using Google's Gemini AI models.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-AI-orange.svg)](https://ai.google.dev/)

---

## 🌟 Features

### Core Capabilities
- **🤖 AI-Powered Scam Detection** - Uses Gemini LLM for intelligent threat analysis
- **🎭 Context-Aware Persona** - Generates human-like, confused responses to engage scammers
- **🔍 Intelligence Extraction** - Automatically extracts UPI IDs, phone numbers, bank accounts, and URLs
- **💬 Multi-turn Conversations** - Maintains session context across multiple messages
- **📊 Intelligence Accumulation** - Tracks and aggregates extracted data across entire conversation
- **🚪 Automatic Session Exit** - End conversations naturally with exit keywords (exit, bye, quit, etc.)
- **🔐 API Key Authentication** - Secured with x-api-key header validation
- **🔄 Flexible LLM Provider** - Easy switching between different AI models and providers

### Technical Highlights
- RESTful API with automatic OpenAPI documentation
- Session management with 30-minute timeout
- Comprehensive logging for debugging
- Regex + LLM fallback for robust extraction
- Conversation history tracking
- Provider abstraction for multi-LLM support

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Usage](#-api-usage)
- [Features Deep Dive](#-features-deep-dive)
- [Testing](#-testing)
- [Architecture](#-architecture)
- [Production Deployment](#-production-deployment)
- [Deploy to Render](#-deploy-to-render)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Google AI Studio API Key
- Git
- Strong interest in coding and practical programming skills
- ☕ Sleep is optional & 🧠 Errors are personal

### 1. Get API Key (2 minutes)
1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your key (starts with `AIza...`)

### 2. Clone & Setup (3 minutes)
```bash
# Clone repository
git clone https://github.com/0x-rudra/hcl-honeypot.git
cd hcl-honeypot

# Create virtual environment
python -m venv myenv

# Activate environment
# Windows:
.\myenv\Scripts\Activate.ps1
# Linux/Mac:
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env file and add your API key
# GEMINI_API_KEY=your-key-here
# HONEYPOT_API_KEY=honeypot-test-key-2026-secure
# GEMINI_MODEL=gemma-3-4b-it
```

### 4. Start Server
```bash
uvicorn app.main:app --reload
```

Server runs at: `https://127.0.0.1:8080`

### 5. Test It!
```bash
curl -X POST https://127.0.0.1:8080/honeypot \
  -H "x-api-key: honeypot-test-key-2026-secure" \
  -H "Content-Type: application/json" \
  -d '{"message": "URGENT! Send money to scammer@paytm or call 9876543210"}'
```

✅ **You're ready!** Visit `https://127.0.0.1:8080/docs` for interactive API documentation.

---

## 📁 Project Structure

```
HCL-honeypot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app & /honeypot endpoint
│   ├── auth.py              # API key authentication
│   ├── config.py            # Configuration & model settings
│   ├── scam_detector.py     # Scam detection logic
│   ├── persona.py           # Honeypot persona generator
│   ├── extractor.py         # Intelligence extraction
│   ├── schemas.py           # Pydantic models
│   ├── session.py           # Session management
│   └── llm_provider.py      # LLM provider abstraction
├── myenv/                   # Virtual environment
├── .env                     # Environment variables (not in git)
├── .env.example             # Example environment file
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
├── Dockerfile               # Docker configuration
├── README.md                # This file
├── POSTMAN_TESTING_GUIDE.md # Comprehensive testing guide
├── test_server.py           # Server tests
├── test_extractor.py        # Extraction tests
└── test_setup.py            # Setup verification
```

---

## 🔧 Installation

### Method 1: Local Development

**Step 1: Prerequisites**
```bash
# Verify Python version
python --version  # Should be 3.13+

# Verify pip
pip --version
```

**Step 2: Virtual Environment**
```bash
# Create environment
python -m venv myenv

# Activate
# Windows PowerShell:
.\myenv\Scripts\Activate.ps1
# Windows CMD:
.\myenv\Scripts\activate.bat
# Linux/Mac:
source myenv/bin/activate
```

**Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Verify Installation**
```bash
python test_setup.py
```

### Method 2: Docker

**Build Image:**
```bash
docker build -t honeypot-api .
```

**Run Container:**
```bash
docker run \
  -e GEMINI_API_KEY="your-key-here" \
  -e HONEYPOT_API_KEY="your-api-key" \
  -p 8000:8000 \
  honeypot-api
```

**Or with .env file:**
```bash
docker run --env-file .env -p 8000:8000 honeypot-api
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# ============================================================================
# LLM API CONFIGURATION
# ============================================================================
# Get your API key from: https://aistudio.google.com/apikey
GEMINI_API_KEY=AIzaSyA3KlnDI6KSdQbf8vkkW2CQPC_h1dpum98

# ============================================================================
# MODEL SELECTION - Change based on your quota/needs
# ============================================================================
# Current: gemma-3-4b-it (30 req/min, 15K tokens/day, 14.4K req/day)
#
# Available Options:
# - gemma-3-4b-it       : Balanced (30 req/min, 15K tokens/day)
# - gemini-1.5-flash    : High quota (15 req/min, 1M tokens/day)
# - gemini-2.0-flash    : Latest model (10 req/min, 1M tokens/day)
# - gemini-1.5-pro      : Most capable (2 req/min, 50K tokens/day)
#
GEMINI_MODEL=gemma-3-4b-it

# ============================================================================
# API AUTHENTICATION
# ============================================================================
# Honeypot API Authentication Key
HONEYPOT_API_KEY=honeypot-test-key-2026-secure

# ============================================================================
# AGENT PARAMETERS (Optional - has defaults)
# ============================================================================
AGENT_TEMPERATURE=0.7
AGENT_TOP_P=0.95
AGENT_TOP_K=40
AGENT_MAX_OUTPUT_TOKENS=2048
```

### Model Configuration

| Model | RPM | TPD | Best For |
|-------|-----|-----|----------|
| `gemma-3-4b-it` | 30 | 15K | Balanced performance |
| `gemini-1.5-flash` | 15 | 1M | High throughput |
| `gemini-2.0-flash` | 10 | 1M | Latest features |
| `gemini-1.5-pro` | 2 | 50K | Complex reasoning |

**To switch models:** Just update `GEMINI_MODEL` in `.env` and restart server.

### Session Configuration

Sessions automatically expire after **30 minutes** of inactivity. This is configured in `app/config.py`:

```python
SESSION_TIMEOUT_MINUTES = 30  # Adjust as needed
```

---

## 📡 API Usage

### Base URL
```
https://127.0.0.1:8080
```

### Authentication
All requests to `/honeypot` require the `x-api-key` header:
```
x-api-key: your-api-key-here
```

---

### Endpoints

#### 1. **GET /** - API Information
```bash
curl https://127.0.0.1:8080/
```

**Response:**
```json
{
  "name": "Agentic Honeypot API",
  "version": "1.0.0",
  "endpoint": "/honeypot",
  "method": "POST"
}
```

---

#### 2. **GET /health** - Health Check
```bash
curl https://127.0.0.1:8080/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

---

#### 3. **POST /honeypot** - Main Endpoint

**Headers:**
```
x-api-key: honeypot-test-key-2026-secure
Content-Type: application/json
```

**Request Body (First Message):**
```json
{
  "message": "URGENT! Your bank account is frozen. Send 5000 rupees to unfreeze@paytm"
}
```

**Response:**
```json
{
  "is_scam": true,
  "confidence": 0.95,
  "agent_reply": "Oh no, really? That sounds serious! Should I send it right away?",
  "extracted_intelligence": {
    "upi_ids": ["unfreeze@paytm"],
    "phone_numbers": [],
    "bank_accounts": [],
    "phishing_urls": []
  },
  "reasoning": "Message creates urgency, impersonates bank, requests immediate payment",
  "session_id": "abc123-def456-ghi789",
  "conversation_history": [
    {
      "role": "user",
      "content": "URGENT! Your bank account is frozen...",
      "timestamp": "2026-02-03T10:30:00.123456"
    },
    {
      "role": "assistant",
      "content": "Oh no, really? That sounds serious!...",
      "timestamp": "2026-02-03T10:30:02.456789"
    }
  ],
  "accumulated_intelligence": {
    "upi_ids": ["unfreeze@paytm"],
    "phone_numbers": [],
    "bank_accounts": [],
    "phishing_urls": []
  }
}
```

**Request Body (Continue Conversation):**
```json
{
  "message": "Yes, call this number: 9876543210 for verification",
  "session_id": "abc123-def456-ghi789"
}
```

**Response:**
```json
{
  "is_scam": true,
  "confidence": 0.90,
  "agent_reply": "Okay, I'll call them. What should I tell them?",
  "extracted_intelligence": {
    "upi_ids": [],
    "phone_numbers": ["+919876543210"],
    "bank_accounts": [],
    "phishing_urls": []
  },
  "reasoning": "Continuation of scam, now requesting phone contact",
  "session_id": "abc123-def456-ghi789",
  "conversation_history": [
    {
      "role": "user",
      "content": "URGENT! Your bank account is frozen...",
      "timestamp": "2026-02-03T10:30:00.123456"
    },
    {
      "role": "assistant",
      "content": "Oh no, really? That sounds serious!...",
      "timestamp": "2026-02-03T10:30:02.456789"
    },
    {
      "role": "user",
      "content": "Yes, call this number: 9876543210...",
      "timestamp": "2026-02-03T10:31:00.123456"
    },
    {
      "role": "assistant",
      "content": "Okay, I'll call them. What should I tell them?",
      "timestamp": "2026-02-03T10:31:02.456789"
    }
  ],
  "accumulated_intelligence": {
    "upi_ids": ["unfreeze@paytm"],
    "phone_numbers": ["+919876543210"],
    "bank_accounts": [],
    "phishing_urls": []
  }
}
```

---

### Error Responses

**401 Unauthorized - Missing API Key:**
```json
{
  "detail": "Missing x-api-key header"
}
```

**401 Unauthorized - Invalid API Key:**
```json
{
  "detail": "Invalid API key"
}
```

**400 Bad Request - Empty Message:**
```json
{
  "detail": "Message cannot be empty"
}
```

**500 Internal Server Error - API Quota:**
```json
{
  "detail": "Gemini API quota exceeded. Please try again later or switch to a different model."
}
```

---

## 🎯 Features Deep Dive

### 1. Multi-turn Conversations

The API maintains conversation context across multiple messages:

**How it works:**
- First message creates a new session
- `session_id` returned in response
- Include `session_id` in subsequent messages
- Session expires after 30 minutes of inactivity

**Example Flow:**
```
Message 1: "Account frozen" → session_id: abc123
Message 2: "Send money to scammer@paytm" + session_id: abc123
Message 3: "Call 9876543210" + session_id: abc123
```

### 2. Intelligence Accumulation

All extracted intelligence is accumulated across the entire conversation:

```json
{
  "accumulated_intelligence": {
    "upi_ids": ["scammer1@paytm", "scammer2@phonepe"],
    "phone_numbers": ["+919876543210", "+918888777766"],
    "bank_accounts": ["HDFC0001234"],
    "phishing_urls": ["http://fake-bank.com"]
  }
}
```

### 3. Context-Aware Persona

The honeypot persona is aware of previous conversation and maintains consistency:

**Message 1:** "Account frozen"
**Reply 1:** "Oh no, what should I do?"

**Message 2:** "Send 5000 rupees"
**Reply 2:** "Okay, where should I send it? I'm really worried now."
*(References previous context)*

### 4. Flexible LLM Provider

The system uses a provider abstraction that makes it easy to switch between:
- Different Gemini models (gemma-3-4b-it, gemini-1.5-flash, etc.)
- Future: OpenAI GPT models
- Future: Anthropic Claude models

**To switch providers:** Update `.env` file and restart. No code changes needed.

---

## 🧪 Testing

### Quick Test
```bash
python test_setup.py
```

### Server Tests
```bash
python test_server.py
```

### Extraction Tests
```bash
python test_extractor.py
```

### Exit Feature Tests
```bash
python test_exit_feature.py
```

**See:** [EXIT_FEATURE_GUIDE.md](EXIT_FEATURE_GUIDE.md) for detailed documentation on automatic session termination.

### Comprehensive Postman Tests

The project includes **191 comprehensive test cases** for Postman:

**See:** [POSTMAN_TESTING_GUIDE.md](POSTMAN_TESTING_GUIDE.md)

**Test Collections:**
1. Basic Functionality (10 tests)
2. Authentication (15 tests)
3. Input Validation (6 tests)
4. Non-Scam Messages (10 tests)
5. Scam Detection (15 tests)
6. Intelligence Extraction (36 tests)
7. Multi-turn Conversations (25 tests)
8. Edge Cases (16 tests)
9. Load Testing (30 tests)

**Total:** 191 tests covering all features.

---

## 🏗️ Architecture

### System Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /honeypot + x-api-key
       ▼
┌─────────────────────────┐
│  Authentication Layer   │
│     (auth.py)          │
└──────┬──────────────────┘
       │ Validate API key
       ▼
┌─────────────────────────┐
│   Session Manager       │
│    (session.py)         │
└──────┬──────────────────┘
       │ Get/Create session
       ▼
┌─────────────────────────┐
│   Scam Detector         │
│  (scam_detector.py)     │
└──────┬──────────────────┘
       │ Analyze message
       ▼
    is_scam?
       │
       ├─ NO → Return response
       │
       └─ YES ──┬──────────────────┐
                ▼                  ▼
        ┌───────────────┐  ┌──────────────┐
        │   Persona     │  │  Extractor   │
        │ (persona.py)  │  │(extractor.py)│
        └───────┬───────┘  └──────┬───────┘
                │                  │
                └────────┬─────────┘
                         ▼
                ┌─────────────────┐
                │  LLM Provider   │
                │(llm_provider.py)│
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Gemini API     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Build Response │
                │   (schemas.py)  │
                └────────┬────────┘
                         │
                         ▼
                   Return JSON
```

### Key Components

**1. Authentication (`auth.py`)**
- Validates `x-api-key` header
- Returns 401 for missing/invalid keys

**2. Session Manager (`session.py`)**
- Creates/retrieves sessions
- Tracks conversation history
- Accumulates intelligence
- Handles 30-min timeout

**3. Scam Detector (`scam_detector.py`)**
- Keyword scoring (pre-analysis)
- LLM classification (final decision)
- Returns: is_scam, confidence, reasoning

**4. Persona Generator (`persona.py`)**
- Context-aware response generation
- Uses conversation history
- Temperature: 0.9 for variety

**5. Intelligence Extractor (`extractor.py`)**
- Regex patterns (primary)
- LLM fallback (secondary)
- Extracts: UPI, phone, bank, URLs

**6. LLM Provider (`llm_provider.py`)**
- Abstraction layer for AI models
- Supports multiple providers
- Centralized configuration

---

## 🚀 Production Deployment

### Security Checklist

- [ ] Change `HONEYPOT_API_KEY` to a cryptographically secure random key
- [ ] Never commit `.env` file to version control
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Enable CORS with whitelist
- [ ] Set up monitoring and alerting
- [ ] Configure proper logging levels
- [ ] Use secrets management service (AWS Secrets Manager, Azure Key Vault)

### Environment Configuration

**Production .env:**
```env
GEMINI_API_KEY=your-production-key
HONEYPOT_API_KEY=super-secure-random-key-here
GEMINI_MODEL=gemini-1.5-flash
DEBUG=False
```

### Docker Production

```bash
docker build -t honeypot-api:prod .
docker run -d \
  --name honeypot-api \
  --env-file .env.production \
  -p 8000:8000 \
  --restart unless-stopped \
  honeypot-api:prod
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass https://hcl-honeypot-api.onrender.com;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Monitoring

**Health Check Endpoint:**
```bash
curl https://your-domain.com/health
```

**Prometheus Metrics:** (Future enhancement)
- Request count
- Response times
- Error rates
- Session count

---

## 🐛 Troubleshooting

### Issue: "Missing x-api-key header"
**Solution:** Add header to request:
```bash
-H "x-api-key: your-key-here"
```

### Issue: "Invalid API key"
**Solution:** Verify `HONEYPOT_API_KEY` in `.env` matches your request header.

### Issue: "Gemini API quota exceeded."
**Solution:**
1. Wait for quota reset
2. Switch to the model with a higher quota in `.env`:
   ```env
   GEMINI_MODEL=gemini-1.5-flash
   ```
3. Get paid API plan

### Issue: Server not starting
**Solution:**
1. Check if port 8000 is available:
   ```bash
   netstat -ano | findstr :8000
   ```
2. Use a different port:
   ```bash
   uvicorn app.main:app --port 8001
   ```

### Issue: Empty response
**Solution:** Check server logs for errors. Enable debug mode:
```env
DEBUG=True
```

### Issue: Session not persisting
**Solution:**
1. Verify you're sending the same `session_id`
2. Check session hasn't expired (30 min timeout)
3. Verify server hasn't restarted (sessions are in-memory)

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Development Setup
```bash
# Fork the repo
git clone https://github.com/your-username/hcl-honeypot.git
cd hcl-honeypot

# Create virtual environment
python -m venv myenv
source myenv/bin/activate  # or .\myenv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create feature branch
git checkout -b feature/your-feature-name
```

### Code Style
- Follow PEP 8
- Add docstrings to functions
- Include type hints
- Write tests for new features

### Pull Request Process
1. Update README if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Submit PR with a clear description

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google AI Studio** - For providing Gemini API
- **FastAPI** - For the excellent web framework
- **Pydantic** - For data validation
- **Uvicorn** - For ASGI server

---

## 🚀 Deploy to Render

### **Quick Deploy (5 Minutes):**

1. **Sign up at [Render.com](https://render.com)** (free, no credit card)

2. **Create New Web Service:**
   - Dashboard → "New +" → "Web Service"
   - Connect your GitHub: `0x-rudra/hcl-honeypot`
   - Render auto-detects `render.yaml`

3. **Set Environment Variable:**
   - Add `GEMINI_API_KEY` = your-api-key

4. **Deploy!**
   - Your API will be live at: `https://hcl-honeypot-api.onrender.com`

### **Features:**
- ✅ Automatic HTTPS
- ✅ Auto-deploy from GitHub
- ✅ Free 750 hours/month
- ✅ Built-in monitoring & logs

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/0x-rudra/hcl-honeypot/issues)
- **Documentation:** See `POSTMAN_TESTING_GUIDE.md` for comprehensive testing
- **Email:** rudransha.g9_cse@outlook.com

---

## 🎯 Project Status

✅ **Status:** IN Production 

**Latest Version:** 1.0.0

**Recent Updates:**
- ✅ Multi-turn conversation support
- ✅ Intelligence accumulation
- ✅ LLM provider abstraction
- ✅ Comprehensive logging
- ✅ 200+ Postman test cases
- ✅ Automatic session exit with 14+ exit keywords

**Upcoming:**
- [ ] OpenAI provider support
- [ ] Anthropic Claude integration
- [ ] Conversation export API
- [ ] Analytics dashboard
- [ ] Rate limiting middleware
- [ ] Portal With Dynamic Frontend 

---

## 📊 Stats

- **Lines of Code:** ~2000+
- **Test Cases:** 191+
- **API Endpoints:** 3
- **Supported Models:** 4+ (Gemini family)
- **Average Response Time:** 2-3 seconds
- **Session Timeout:** 30 minutes
- **This Server is using a free instance will spin down with inactivity of 15 minutes, which can delay requests by 15-50 seconds or more.**
---

**Made with ❤️ Love and Passion by [0x-rudra](https://github.com/0x-rudra)**
