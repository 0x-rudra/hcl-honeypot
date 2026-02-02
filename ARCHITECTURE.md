# 🏗️ Honeypot API Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATION                            │
│                                                                   │
│  Sends scam message with x-api-key header                       │
└────────────────────────────┬──────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    HONEYPOT API SERVER                           │
│                    (FastAPI - main.py)                           │
│                                                                   │
│  1. Validate x-api-key (auth.py)                                │
│  2. Parse request (schemas.py)                                  │
│  3. Orchestrate agents                                           │
└────────────────────────────┬──────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ↓                    ↓                    ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   AGENT 1    │    │   AGENT 2    │    │   AGENT 3    │
│   🕵️ SCAM   │    │  🎭 PERSONA  │    │ 🔍 EXTRACT   │
│   DETECTOR   │    │  GENERATOR   │    │ INTELLIGENCE │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ↓
           ┌─────────────────────────────────┐
           │   GOOGLE AI STUDIO              │
           │   (Gemini 2.0 Flash)            │
           │                                 │
           │   - API Key: GEMINI_API_KEY    │
           │   - Model: gemini-2.0-flash    │
           └─────────────────────────────────┘
```

---

## Data Flow

```
POST /honeypot
    │
    │ {"message": "Your account is blocked..."}
    │ x-api-key: your-secret-key
    │
    ↓
[1] AUTH MODULE
    │ Validates x-api-key
    │ ✓ Authorized
    │
    ↓
[2] SCAM DETECTOR AGENT
    │ • Keyword scoring: 0.65
    │ • LLM analysis with agent instructions
    │ • System instruction: "You are a scam detection expert..."
    │ • Temperature: 0.7
    │
    ↓ Result
    │ is_scam: true
    │ confidence: 0.93
    │ reasoning: "Creates urgency, impersonates authority..."
    │
    ↓
[3] INTELLIGENCE EXTRACTOR AGENT
    │ • Regex extraction (primary)
    │ • LLM fallback if needed
    │ • System instruction: "You are an intelligence extraction agent..."
    │ • Temperature: 0.1
    │
    ↓ Result
    │ upi_ids: ["scammer@upi"]
    │ phone_numbers: []
    │ phishing_urls: []
    │ bank_accounts: []
    │
    ↓
[4] HONEYPOT PERSONA AGENT
    │ (Only if is_scam == true)
    │ • Generate human-like reply
    │ • System instruction: "You are a honeypot persona agent..."
    │ • Temperature: 0.9
    │
    ↓ Result
    │ agent_reply: "Oh no 😟 What should I do next?"
    │
    ↓
[5] RESPONSE BUILDER
    │ Assemble JSON (no LLM)
    │ Validate schema (Pydantic)
    │ Deduplicate & normalize
    │
    ↓
Response
{
  "is_scam": true,
  "confidence": 0.93,
  "agent_reply": "Oh no 😟 What should I do next?",
  "extracted_intelligence": {...},
  "reasoning": "..."
}
```

---

## Agent Details

### 🕵️ Agent 1: Scam Detector

**File**: `app/scam_detector.py`

**System Instructions**:
```
You are a scam detection expert agent. Your role is to analyze
messages and determine if they are scams.

Your expertise includes:
- Identifying phishing attempts and social engineering tactics
- Recognizing urgency manipulation and authority impersonation
- Detecting requests for sensitive information (OTP, passwords, etc.)
- Spotting suspicious patterns in financial transaction requests
```

**Configuration**:
- Model: `gemini-2.0-flash`
- Temperature: `0.7`
- Top-P: `0.95`
- Top-K: `40`
- Max Tokens: `2048`

**Input**: Message text + keyword score
**Output**: is_scam, confidence (0.0-1.0), reasoning

---

### 🎭 Agent 2: Honeypot Persona

**File**: `app/persona.py`

**System Instructions**:
```
You are a honeypot persona agent. Your role is to generate
human-like responses to scam messages.

Persona characteristics:
- Confused and uncertain about the situation
- Cooperative and eager to help/comply
- Uses casual language with occasional emojis
- Asks clarifying questions to encourage engagement
- Never sounds robotic, technical, or security-aware
```

**Configuration**:
- Model: `gemini-2.0-flash`
- Temperature: `0.9` (higher for variety)
- Top-P: `0.95`
- Top-K: `40`
- Max Tokens: `150` (short responses)

**Input**: Scam message text
**Output**: 1-2 sentence human-like reply

---

### 🔍 Agent 3: Intelligence Extractor

**File**: `app/extractor.py`

**System Instructions**:
```
You are an intelligence extraction agent specialized in
identifying scam indicators.

Your expertise includes:
- Extracting UPI IDs (format: user@upi)
- Identifying phone numbers (especially Indian format)
- Finding URLs and potentially malicious links
- Detecting bank account numbers

Be precise and only extract valid, complete indicators.
```

**Configuration**:
- Model: `gemini-2.0-flash`
- Temperature: `0.1` (low for precision)
- Top-P: `0.95`
- Top-K: `40`
- Max Tokens: `500`

**Primary Method**: Regex extraction
**Fallback**: LLM extraction if regex finds nothing

**Input**: Message text
**Output**: bank_accounts, upi_ids, phone_numbers, phishing_urls

---

## Configuration Hierarchy

```
Environment Variables (.env or system env)
    ↓
Config Module (app/config.py)
    ↓
┌───────────────┬──────────────┬──────────────┐
│               │              │              │
Scam Detector   Persona        Extractor
(agent 1)       (agent 2)      (agent 3)
```

**Config File Structure**:
```python
# app/config.py
class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    HONEYPOT_API_KEY = os.getenv("HONEYPOT_API_KEY")

    # Model
    GEMINI_MODEL = "gemini-2.0-flash"

    # Agent Parameters
    AGENT_TEMPERATURE = 0.7
    AGENT_TOP_P = 0.95
    AGENT_TOP_K = 40
    AGENT_MAX_OUTPUT_TOKENS = 2048
```

---

## API Key Usage

### Where API Keys Are Stored

1. **Environment Variable** (Recommended):
   ```powershell
   $env:GEMINI_API_KEY="AIzaSy...your-key"
   ```

2. **.env File** (Development):
   ```env
   GEMINI_API_KEY=AIzaSy...your-key
   ```

### Where API Keys Are Used

```
GEMINI_API_KEY (from Google AI Studio)
    ↓
    Used by: google.generativeai.configure()
    ↓
    In files:
    - app/scam_detector.py (line 8)
    - app/persona.py (line 8)
    - app/extractor.py (line 9)

HONEYPOT_API_KEY (your custom key)
    ↓
    Used by: app.auth.validate_api_key()
    ↓
    In files:
    - app/auth.py (line 20)
```

---

## Execution Timeline

```
Request arrives → 0ms
    ↓
API key validation → ~5ms
    ↓
Keyword scoring → ~10ms
    ↓
LLM scam detection → ~1000ms (Agent 1)
    ↓
Intelligence extraction → ~100ms (regex) or ~500ms (Agent 3 LLM)
    ↓
Persona generation → ~500ms (Agent 2)
    ↓
JSON assembly → ~5ms
    ↓
Response sent → Total: ~1.6-2.5 seconds
```

---

## Security Flow

```
Client Request
    │
    ↓ 1. Header Check
[x-api-key present?]
    │ No → 401 Unauthorized
    │ Yes
    ↓ 2. Key Validation
[x-api-key == HONEYPOT_API_KEY?]
    │ No → 403 Forbidden
    │ Yes
    ↓ 3. Process Request
[Agent pipeline]
    │
    ↓ 4. API Key for Google AI
[GEMINI_API_KEY used by agents]
    │ Invalid → 500 Internal Error
    │ Valid
    ↓ 5. Return Response
[JSON with results]
```

---

## Agent Communication

```
Main API (main.py)
    │
    ├─→ ScamDetector.detect(message)
    │       │
    │       └─→ genai.GenerativeModel(
    │               system_instruction=SCAM_DETECTOR_AGENT_INSTRUCTIONS
    │           )
    │
    ├─→ PersonaGenerator.generate_reply(message)
    │       │
    │       └─→ genai.GenerativeModel(
    │               system_instruction=HONEYPOT_AGENT_INSTRUCTIONS
    │           )
    │
    └─→ IntelligenceExtractor.extract(message)
            │
            └─→ genai.GenerativeModel(
                    system_instruction=EXTRACTOR_AGENT_INSTRUCTIONS
                )
```

---

## File Dependencies

```
main.py
  ├─ config.py (GEMINI_API_KEY)
  ├─ auth.py (HONEYPOT_API_KEY)
  ├─ schemas.py (request/response models)
  ├─ scam_detector.py
  │   ├─ config.py
  │   └─ google.generativeai
  ├─ persona.py
  │   ├─ config.py
  │   └─ google.generativeai
  └─ extractor.py
      ├─ config.py
      └─ google.generativeai
```

---

## Agent Comparison

| Feature | Scam Detector | Persona Generator | Intelligence Extractor |
|---------|--------------|-------------------|----------------------|
| **Purpose** | Classify scams | Generate replies | Extract indicators |
| **Temperature** | 0.7 (balanced) | 0.9 (creative) | 0.1 (precise) |
| **Output Length** | ~100-200 tokens | ~20-30 tokens | ~50-100 tokens |
| **Precision** | Medium | Low (varied) | High (exact) |
| **Creativity** | Medium | High | Low |
| **Backup Method** | Keyword scoring | None | Regex patterns |

---

## Error Handling Flow

```
Request → main.py
    │
    ├─ HTTPException (400, 401, 403)
    │   └─→ Return error JSON immediately
    │
    ├─ Agent error (LLM timeout, API quota)
    │   └─→ Catch, log, return 500
    │
    └─ Success
        └─→ Return result JSON
```

---

## Summary

- **3 Specialized Agents** powered by Google AI Studio
- **1 API Key** (GEMINI_API_KEY) shared across all agents
- **Agent-based architecture** for intelligent, context-aware responses
- **Stateless design** - no databases, no session management
- **Fast response times** - 1.6-2.5 seconds typical latency
