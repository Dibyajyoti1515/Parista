# Implementation Plan: Grounded Conflict Assistant

**Branch**: `001-grounded-conflict-assistant` | **Date**: 2026-08-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-grounded-conflict-assistant/spec.md`

## Summary

Parista is an agentic system that helps users navigate interpersonal conflicts (romantic, family, workplace/HR) by analyzing their situation against a curated psychology research knowledge base and generating a grounded, cited, tone-calibrated response. The system must never hallucinate psychological claims: every insight must trace back to a real, cited source, with a fallback to real-time academic paper retrieval when the core knowledge base has low confidence. Users interact via Telegram or a React web frontend, and can optionally upload screenshots of conversations for analysis. The system supports multi-turn follow-up questions within the same conversation, retaining context (classified conflict type, retrieved framework, prior exchange) so follow-ups are answered consistently with the original analysis. Safety check and citation verification apply to every turn, including follow-ups.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/React (frontend)

**Primary Dependencies**: FastAPI, Google ADK, Supabase (Postgres + pgvector), Gemini (Google AI Studio), Semantic Scholar API, python-telegram-bot

**Storage**: Supabase Postgres with pgvector extension (no separate vector DB service)

**Testing**: pytest (backend), Playwright (e2e), React testing (frontend)

**Target Platform**: Linux server (Render/Railway), web (Vercel/Netlify), Telegram

**Project Type**: Web application (frontend + backend + bot client)

**Performance Goals**: Primary flow (describe → receive response) completes in under 30 seconds (SC-003)

**Constraints**: No GPU or local model weights anywhere — all LLM/embedding calls are API-based; free-tier deployable

**Scale/Scope**: Hackathon-scale; single FastAPI app + React frontend + thin Telegram client

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Never Diagnose** — Reasoning Agent identifies psychological *patterns* grounded in cited research; it never labels a user or situation with a clinical diagnosis. ✓
- **Never Hallucinate a Source** — Every claim traces to a real retrieved chunk (core KB or real-time fetch); below confidence threshold with no reliable source → explicit "insufficient grounded information" response. ✓
- **Human-Reviewed Development** — All agent-generated code reviewed by a team member before merge; review notes logged in `docs/DECISIONS.md`. ✓
- **Crisis Override Is Absolute** — Safety Agent intercepts the pipeline before any other agent on self-harm/suicidal/abuse signals; supportive language + resources, not relationship advice. ✓
- **Cultural Calibration, Not Stereotyping** — Style Agent adjusts tone based on user-stated context signals, never assuming identity attributes not stated. ✓

**Gate result: PASS** — No violations. The design below conforms to all five constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/001-grounded-conflict-assistant/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── agents/             # ADK agents (coordinator, safety, classifier, retrieval, reasoning, style)
├── modules/            # Backend modules (classification, retrieval, reasoning, style, safety)
├── tools/              # Tools (vector_search, paper_fetch, citation_verify, ocr)
├── tests/              # Backend tests
└── main.py             # FastAPI app entry point

bot/
└── telegram_bot.py     # Thin Telegram client forwarding to backend via HTTP

frontend/
└── src/                # React frontend

e2e/
└── playwright/         # End-to-end tests

data/
├── core_papers/        # Curated psychology research papers
└── markdown/            # Processed markdown chunks
```

**Structure Decision**: Modular monolith backend (FastAPI) with ADK agent orchestration, separate React frontend, and a thin Telegram bot client. This matches the existing repository structure and the architecture documented in `docs/ARCHITECTURE.md`. The modular monolith keeps deployment and debugging simple for the hackathon timeframe while preserving clean separation of concerns via ADK agents and backend modules.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations — this section is intentionally left empty.