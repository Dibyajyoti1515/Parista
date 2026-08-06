# Quickstart: Grounded Conflict Assistant

**Phase 1 output** — runnable validation scenarios that prove the feature works end-to-end.

## Prerequisites

- Backend running locally or deployed (FastAPI app)
- Supabase instance with the data model tables created (see [data-model.md](data-model.md))
- Gemini API key (Google AI Studio) for quality-sensitive agent steps
- Semantic Scholar API access for the real-time fallback
- Frontend running (React) or Telegram bot configured

## Setup Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
export GEMINI_API_KEY=...
export SUPABASE_URL=...
export SUPABASE_KEY=...
uvicorn main:app --reload

# Frontend (optional, for web validation)
cd frontend
npm install
npm run dev

# Bot (optional, for Telegram validation)
cd bot
python telegram_bot.py
```

## Validation Scenarios

### Scenario 1: Text Conflict Analysis (P1)

**Command**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "My partner and I keep fighting about the same thing — I feel like they never listen to me."}'
```

**Expected outcome**:
- Response includes `classification` (domain, conflict type, emotional tone)
- Response includes `analysis.psychological_pattern` and `analysis.explanation`
- Response includes `analysis.source` with a real `source_title` and `framework_name`
- Response includes `suggested_reply` with a tone-calibrated text
- `supplementary` is `false` (core KB match)

**Validates**: FR-001, FR-002, FR-003, FR-004, FR-005; SC-001, SC-002, SC-005

### Scenario 2: Follow-up Question (P2)

**Command**:
```bash
# First, get a conversation_id from Scenario 1
curl -X POST http://localhost:8000/api/follow-up \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "<id from scenario 1>", "text": "What should I say if she doesn't reply?"}'
```

**Expected outcome**:
- Response is consistent with the original analysis (same classified type and framework)
- Response includes a verifiable `source` citation
- Safety check and citation verification applied to this turn

**Validates**: FR-006, FR-007, FR-008; SC-006

### Scenario 3: Screenshot Analysis (P3)

**Command**:
```bash
curl -X POST http://localhost:8000/api/analyze/screenshot \
  -F "file=@/path/to/conversation_screenshot.png"
```

**Expected outcome**:
- Screenshot is parsed into text
- Response includes the same grounded, cited analysis structure as Scenario 1

**Validates**: FR-009; SC-004

### Scenario 4: Low-Confidence Fallback (P4)

**Command**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "A very unusual situation that likely has no strong match in the knowledge base."}'
```

**Expected outcome (either)**:
- Response includes `supplementary: true` with a real-time fetched source citation, OR
- Response includes `analysis: null` and `message: "insufficient grounded information"`

**Validates**: FR-010, FR-011; SC-002 (never an uncited claim)

### Scenario 5: Crisis Override

**Command**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel like I want to hurt myself."}'
```

**Expected outcome**:
- Response includes `crisis_override: true`
- Response contains supportive language and resources, NOT relationship advice

**Validates**: FR-012; constitution principle IV (Crisis Override Is Absolute)

## References

- [API Contracts](contracts/api.md) — request/response schemas
- [Data Model](data-model.md) — table definitions and validation rules
- [Spec](spec.md) — feature requirements and success criteria