# Architecture — Parista

## Overview

Parista is an agentic system that analyzes a user's interpersonal conflict
(romantic, family, or workplace) and returns a psychologically-grounded,
cited, tone-calibrated response. It is built as a modular monolith backend
with a separate frontend and a thin Telegram bot client.

## Stack

- **Frontend:** React (separate deploy)
- **Bot interface:** Telegram, thin client forwarding to backend via HTTP
- **Backend:** FastAPI, modular monolith, Python
- **Agent orchestration:** Google ADK (multi-agent, tool-calling)
- **Database:** Supabase (Postgres)
- **Vector store:** Supabase pgvector extension (same Postgres instance —
  no separate vector DB service)
- **LLM:** Gemini (via Google AI Studio, free tier) for quality-sensitive
  agents; lighter model for routine rephrasing
- **Image input:** Vision-capable LLM call for OCR/screenshot parsing
  (not raw Tesseract — more reliable on messy chat screenshots)
- **CI/CD:** GitHub Actions

## High-Level Flow

1. User sends a message (text or screenshot) via Telegram or the web frontend.
2. Request hits the FastAPI backend, routed to the ADK Coordinator Agent.
3. **Safety Agent** runs first on every input — checks for crisis signals
   (self-harm, abuse). If triggered, pipeline short-circuits to a support
   response.
4. **Classifier Agent** tags the input: domain (romantic/family/workplace),
   conflict type, emotional tone, age bracket if inferable.
5. **Retrieval Agent** queries the core knowledge base (pgvector) using the
   classification tags to condition retrieval, not raw semantic search alone.
   - If similarity score ≥ 0.75 → use core KB result.
   - If below threshold → call the **paper_fetch tool** (Semantic Scholar
     API, real-time) as a fallback, cache result in `paper_cache` table.
6. **Reasoning Agent** takes the retrieved framework + situation, produces a
   structured psychological analysis (pattern, explanation, source).
7. **Citation Verification tool** checks the analysis only contains claims
   traceable to the retrieved chunk. Fails closed — if verification fails,
   response is regenerated or a fallback "insufficient grounded info"
   message is returned instead.
8. **Style Agent** rewrites the verified analysis into a natural,
   age-calibrated reply, using cached Reddit-sourced tone examples
   (`style_examples` table) for current, relatable phrasing.
9. Structured response returned to the user via Telegram/frontend.

## Data Model (Supabase / Postgres)

**users**
- id (uuid, pk)
- telegram_id / web_session_id
- created_at

**conversations**
- id (uuid, pk)
- user_id (fk)
- created_at

**messages**
- id (uuid, pk)
- conversation_id (fk)
- role (user/agent)
- content (text)
- created_at

**psychology_kb_chunks** (core knowledge base, pgvector)
- id (uuid, pk)
- source_title (e.g. "Downey & Feldman 1996")
- domain (romantic/family/workplace/general)
- framework_name (e.g. "Rejection Sensitivity")
- conflict_stage (acute/reflection/resolution)
- content (text chunk)
- embedding (vector)

**style_examples** (Reddit-sourced tone layer)
- id (uuid, pk)
- text
- tone (casual/formal/playful/serious)
- age_bracket_fit
- situation_type
- source_url
- fetched_at

**paper_cache** (real-time Semantic Scholar fallback)
- id (uuid, pk)
- query
- title
- abstract
- source_url
- fetched_at

## Agents (Google ADK)

See `docs/AGENTS_AND_SKILLS.md` for full agent and tool documentation.
Behavioral rules for all agents are defined in `AGENTS.md` at repo root.

## Deployment

- Backend: single FastAPI app, deployable on Render/Railway free tier
  (no GPU or local model weights required — all LLM/embedding calls are
  API-based)
- Frontend: Vercel/Netlify
- Database: Supabase hosted instance
- No separate vector DB infra — pgvector lives inside the same Postgres
  instance as application data, avoiding an extra service to deploy/manage

## Why This Design

- **Modular monolith over microservices**: keeps deployment and debugging
  simple for hackathon timeframe while preserving clean separation of
  concerns via ADK agents and backend modules.
- **Confidence-threshold fallback**: satisfies Track C's requirement that
  the agent handle messy/unexpected input gracefully without hallucinating,
  by falling back to real-time retrieval rather than guessing.
- **Citation verification as a distinct step**: makes "grounded and
  verifiable" output an enforced pipeline stage, not just a prompting
  instruction.