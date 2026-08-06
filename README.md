# Parista

**Parikshya + Rista** — *examine the relationship, before you react.*

An agentic AI system that helps people navigate emotionally charged
situations — breakups, family misunderstandings, workplace conflicts with a
manager or HR — by grounding advice in real, cited psychological research
instead of generic chatbot sympathy.

Built for **Deploy or Die: HowToAlgo x GDG on Campus KIIT Hackathon**,
Track C — Knowledge and Compliance Agents.

---

## What it does

A user describes a situation (text, or a screenshot of a chat conversation)
via Telegram or the web app. Parista runs it through a multi-agent pipeline:

1. **Safety check** — screens every input for crisis signals before anything
   else runs.
2. **Classification** — tags the conflict's domain, type, and emotional tone.
3. **Retrieval** — matches the situation to a psychological framework from a
   curated research knowledge base, falling back to real-time academic paper
   retrieval when confidence is low.
4. **Reasoning** — produces a structured analysis grounded in the retrieved
   source.
5. **Citation verification** — checks every claim traces back to a real
   source before it reaches the user. Fails closed, never invents a citation.
6. **Style calibration** — rewrites the grounded analysis into a natural,
   age-appropriate suggested reply.

Every response is traceable back to the framework that produced it — no
hallucinated advice, and follow-up questions stay consistent with the
original analysis.

## Architecture

- **Frontend:** React
- **Bot interface:** Telegram (thin client)
- **Backend:** FastAPI, modular monolith
- **Agent orchestration:** Google ADK
- **Database & vector store:** Supabase (Postgres + pgvector)
- **LLM:** Gemini (Google AI Studio) for quality-sensitive steps, a lighter
  model for routine rephrasing
- **Image input:** vision-based OCR for screenshot parsing
- **Knowledge base:** curated psychology research corpus + real-time
  Semantic Scholar fallback

Full details in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Repository guide

| Path | What's there |
|---|---|
| `AGENTS.md` | Agent behavior rules / constitution |
| `docs/ARCHITECTURE.md` | Stack, data model, pipeline design |
| `docs/AGENTS_AND_SKILLS.md` | Custom agent + skill documentation |
| `docs/PRD.md` | Product requirements |
| `docs/DECISIONS.md` | Human-in-the-loop review notes |
| `specs/001-grounded-conflict-assistant/` | Spec Kit artifacts — spec, plan, tasks, data model, API contracts |
| `backend/` | FastAPI app, ADK agents, tools, modules, tests |
| `bot/` | Telegram bot (thin client) |
| `frontend/` | React app |
| `data/` | Core research corpus and reference markdown |
| `e2e/` | Playwright end-to-end tests |

## Getting started

> Setup instructions will be filled in as the backend, bot, and frontend are
> implemented (see `specs/001-grounded-conflict-assistant/tasks.md`).

```bash
# Backend
cd backend
pip install -r requirements.txt
# copy .env.example to .env and fill in Supabase + Gemini credentials

# Frontend
cd frontend
npm install

# Telegram bot
cd bot
pip install -r requirements.txt
```

## Status

🚧 In development. MVP scope: text-based conflict analysis (User Story 1).
Follow-up questions, screenshot analysis, and real-time fallback retrieval
are being built as subsequent user stories.

## Team

Team of 4 — Parista, built for KIIT Deploy or Die hackathon.