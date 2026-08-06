# API Contracts: Grounded Conflict Assistant

**Phase 1 output** — interface contracts for the backend HTTP API, Telegram webhook, and structured response schema.

## Backend HTTP API

Base URL: `https://<backend-host>/` (Render/Railway free tier)

### POST /api/analyze

Analyze a text description of an interpersonal conflict.

**Request**:
```json
{
  "conversation_id": "uuid (optional — omit to start a new conversation)",
  "text": "string — user's description of the conflict"
}
```

**Response (200)**:
```json
{
  "conversation_id": "uuid",
  "classification": {
    "domain": "romantic | family | workplace | general",
    "conflict_type": "string",
    "emotional_tone": "string"
  },
  "analysis": {
    "psychological_pattern": "string",
    "explanation": "string",
    "source": {
      "source_title": "string",
      "framework_name": "string",
      "source_url": "string (optional)"
    }
  },
  "suggested_reply": {
    "text": "string",
    "tone": "casual | formal | playful | serious"
  },
  "supplementary": false
}
```

**Response (200, low-confidence fallback)**:
```json
{
  "conversation_id": "uuid",
  "classification": { "domain": "...", "conflict_type": "...", "emotional_tone": "..." },
  "analysis": {
    "psychological_pattern": "string",
    "explanation": "string",
    "source": { "source_title": "string", "framework_name": "string", "source_url": "string" }
  },
  "suggested_reply": { "text": "string", "tone": "..." },
  "supplementary": true
}
```

**Response (200, insufficient grounded information)**:
```json
{
  "conversation_id": "uuid",
  "classification": { "domain": "...", "conflict_type": "...", "emotional_tone": "..." },
  "analysis": null,
  "message": "insufficient grounded information",
  "supplementary": false
}
```

**Response (200, crisis override)**:
```json
{
  "conversation_id": "uuid",
  "crisis_override": true,
  "message": "Supportive language and resources (not relationship advice)"
}
```

**Errors**:
- `400` — missing `text` field
- `422` — invalid request body

### POST /api/analyze/screenshot

Analyze an uploaded conversation screenshot.

**Request**: `multipart/form-data` with a `file` field (image) and optional `conversation_id`.

**Response**: Same schema as `POST /api/analyze`.

**Errors**:
- `400` — no file provided, or file unreadable/not an image
- `422` — invalid request

### POST /api/follow-up

Submit a follow-up question within an existing conversation.

**Request**:
```json
{
  "conversation_id": "uuid (required)",
  "text": "string — the follow-up question"
}
```

**Response**: Same schema as `POST /api/analyze`, with the analysis consistent with the original conversation's classified type and retrieved framework.

**Errors**:
- `400` — missing `conversation_id` or `text`
- `404` — conversation not found
- `422` — invalid request body

## Telegram Webhook Contract

Telegram bot is a thin client that forwards user messages to the backend via HTTP.

- **Endpoint**: Telegram webhook → bot → `POST /api/analyze` (or `/api/analyze/screenshot` for photos)
- **Mapping**: Telegram `chat_id` → backend `conversation_id` (bot maintains the mapping)
- **Response**: Bot sends the structured response back to the user in the Telegram chat

## Structured Response Schema (shared)

Every non-crisis, non-fallback response MUST include:
- `classification` — domain, conflict type, emotional tone
- `analysis.psychological_pattern` — the identified pattern
- `analysis.explanation` — grounded explanation
- `analysis.source` — MUST reference a real retrieved chunk (constitution: Never Hallucinate a Source)
- `suggested_reply` — tone-calibrated reply

**Validation**: The Citation Verification tool checks that `analysis.source` matches a chunk actually retrieved this turn. If verification fails, the response is regenerated or replaced with the "insufficient grounded information" fallback — never silently passed through.