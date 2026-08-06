# Data Model: Grounded Conflict Assistant

**Phase 1 output** — entities, fields, relationships, and validation rules derived from the feature spec.

## Entities

### User
A person using the system via Telegram or the web frontend.

| Field | Type | Notes |
|-------|------|-------|
| id | uuid (pk) | Unique identifier |
| telegram_id | text | Present for Telegram users |
| web_session_id | text | Present for web frontend users |
| created_at | timestamp | When the user was created |

**Validation**: At least one of `telegram_id` or `web_session_id` MUST be present.

### Conversation
A sequence of messages between a user and the system; retains context across turns (multi-turn support).

| Field | Type | Notes |
|-------|------|-------|
| id | uuid (pk) | Unique identifier |
| user_id | uuid (fk → User) | Owning user |
| created_at | timestamp | When the conversation started |

**Relationships**: A User has many Conversations; a Conversation has many Messages.

### Message
A single exchange in a conversation, with a role and content.

| Field | Type | Notes |
|-------|------|-------|
| id | uuid (pk) | Unique identifier |
| conversation_id | uuid (fk → Conversation) | Parent conversation |
| role | enum (user/agent) | Who sent the message |
| content | text | Message text |
| created_at | timestamp | When the message was sent |

**Relationships**: A Conversation has many Messages.

### Psychological Framework
A curated research-based framework (e.g., "Rejection Sensitivity") matched to the user's situation.

| Field | Type | Notes |
|-------|------|-------|
| id | uuid (pk) | Unique identifier |
| source_title | text | e.g. "Downey & Feldman 1996" |
| domain | enum (romantic/family/workplace/general) | Conflict domain |
| framework_name | text | e.g. "Rejection Sensitivity" |
| conflict_stage | enum (acute/reflection/resolution) | Stage of conflict |
| content | text | Text chunk |
| embedding | vector | pgvector embedding |

**Validation**: `source_title` MUST be present (grounding requirement). `embedding` is used for similarity retrieval.

### Source Citation
A reference to the specific paper or framework a claim is grounded in.

| Field | Type | Notes |
|-------|------|-------|
| id | uuid (pk) | Unique identifier |
| source_title | text | Paper/framework title |
| source_url | text | Optional link to the source |
| framework_name | text | Framework the claim maps to |

**Validation**: Every `psychological_pattern` in a response MUST include a `source` field referencing a real retrieved chunk (constitution: Never Hallucinate a Source).

### Suggested Reply
A tone-calibrated reply generated for the user to use in their real conversation.

| Field | Type | Notes |
|-------|------|-------|
| id | uuid (pk) | Unique identifier |
| text | text | The suggested reply |
| tone | enum (casual/formal/playful/serious) | Calibration tone |
| age_bracket_fit | text | Age calibration |
| situation_type | text | Type of situation |
| source_url | text | Optional source reference |
| fetched_at | timestamp | When fetched (for cached tone examples) |

**Validation**: `tone` MUST be one of the defined enum values.

## Supporting Tables (from architecture)

### psychology_kb_chunks
Core knowledge base (pgvector). Fields: id, source_title, domain, framework_name, conflict_stage, content, embedding.

### style_examples
Reddit-sourced tone layer. Fields: id, text, tone, age_bracket_fit, situation_type, source_url, fetched_at.

### paper_cache
Real-time Semantic Scholar fallback cache. Fields: id, query, title, abstract, source_url, fetched_at.

## State Transitions

### Conversation lifecycle
1. **Created** — user starts a new conversation (first message).
2. **Active** — user sends messages; system responds. Context accumulates across turns.
3. **Closed** — conversation ends (user or system ends it).

### Message processing flow (per turn)
1. **Received** — user message arrives (text or screenshot).
2. **Safety-checked** — Safety Agent runs first; if crisis signal → short-circuit to supportive resources.
3. **Classified** — Classifier Agent tags domain, conflict type, emotional tone.
4. **Retrieved** — Retrieval Agent queries core KB (or falls back to Semantic Scholar).
5. **Reasoned** — Reasoning Agent produces structured analysis.
6. **Verified** — Citation Verification checks claims trace to retrieved source.
7. **Styled** — Style Agent rewrites into tone-calibrated reply.
8. **Delivered** — response returned to user.

## Validation Rules (from requirements)

- **FR-004**: Every psychological claim MUST trace to a real, cited source.
- **FR-006**: Conversation context MUST be retained across turns (classified type, retrieved framework, prior exchange).
- **FR-008**: Safety check and citation verification MUST apply to every turn, including follow-ups.
- **FR-010**: Fallback responses MUST be marked "supplementary."
- **FR-011**: When no reliable source is found, MUST return "insufficient grounded information" (never invent content).