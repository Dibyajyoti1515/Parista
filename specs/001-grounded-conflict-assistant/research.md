# Research: Grounded Conflict Assistant

**Phase 0 output** — consolidates decisions on technical unknowns, dependencies, and integrations.

## 1. ADK Agent Orchestration

- **Decision**: Use Google ADK multi-agent orchestration with a root Coordinator Agent that routes sequentially through Safety → Classifier → Retrieval → Reasoning → Style.
- **Rationale**: Matches the existing architecture (`docs/ARCHITECTURE.md`) and the constitution's agent roles. The Coordinator ensures the Safety Agent runs first on every turn (crisis override) and that Citation Verification runs before the Style Agent.
- **Alternatives considered**: Single-agent prompt pipeline (rejected — cannot enforce per-step safety/citation gates); LangGraph (rejected — ADK already chosen and documented).

## 2. pgvector Retrieval with Classification-Tag Conditioning

- **Decision**: Query the `psychology_kb_chunks` table (pgvector) using the Classifier Agent's tags (domain, conflict type, emotional tone) to condition retrieval, not raw semantic similarity alone.
- **Rationale**: Tag-conditioned retrieval improves precision over raw embedding search and aligns with the architecture's stated design.
- **Alternatives considered**: Pure semantic search (rejected — lower precision on messy input); separate vector DB (rejected — pgvector lives in the same Postgres instance, avoiding an extra service).

## 3. Confidence Threshold & Real-Time Fallback

- **Decision**: If the top retrieval result's similarity score < 0.75, call the `paper_fetch_tool` (Semantic Scholar API) as a fallback. Cache results in the `paper_cache` table. Mark fallback responses as "supplementary."
- **Rationale**: Satisfies the constitution's "Never Hallucinate a Source" principle and Track C's requirement to handle messy input without hallucinating. The 0.75 threshold is the documented confidence bar.
- **Alternatives considered**: Always answering from core KB (rejected — risks low-confidence hallucination); no fallback (rejected — would return "insufficient" too often).

## 4. Vision-Based Screenshot OCR

- **Decision**: Use a vision-capable LLM call for screenshot parsing (OCR), not raw Tesseract.
- **Rationale**: More reliable on messy chat screenshots per the architecture doc. The vision LLM call is API-based (no local model weights), consistent with the no-GPU constraint.
- **Alternatives considered**: Tesseract (rejected — less reliable on chat screenshots); manual text entry only (rejected — screenshot upload is a P3 user story).

## 5. Model Routing (Cost/Quality Split)

- **Decision**: Gemini (via Google AI Studio) for Classifier and Reasoning Agents (quality-sensitive steps); a lighter/faster model for the Style Agent (routine rephrasing).
- **Rationale**: Follows the constitution's model routing guidance — strongest model reserved for the hardest reasoning step, not applied uniformly.
- **Alternatives considered**: Uniform Gemini for all steps (rejected — higher cost, no quality benefit for rephrasing).

## 6. Multi-Turn Context Retention

- **Decision**: Retain conversation context across turns using the existing `conversations` and `messages` tables. Each follow-up reuses the classified conflict type, retrieved framework, and prior exchange. Safety check and citation verification apply to every turn.
- **Rationale**: Satisfies the clarified P2 user story (follow-up questions) and the spec's FR-006/FR-007/FR-008. The data model already supports this.
- **Alternatives considered**: Stateless single-shot responses (rejected — contradicts the clarified multi-turn requirement).

## 7. Citation Verification (Fails Closed)

- **Decision**: The Citation Verification tool checks every claim in the Reasoning Agent's output traces to a real retrieved chunk. If verification fails, the response is regenerated or replaced with a fallback "insufficient grounded information" message — never silently passed through.
- **Rationale**: Enforces the constitution's "Never Hallucinate a Source" principle as a pipeline step, not just a prompt instruction.
- **Alternatives considered**: Prompt-only instruction to not hallucinate (rejected — not enforceable; the tool is the difference between telling and checking).

## 8. Deployment

- **Decision**: Backend on Render/Railway free tier (single FastAPI app), frontend on Vercel/Netlify, database on Supabase hosted instance. No GPU or local model weights anywhere.
- **Rationale**: All LLM/embedding calls are API-based, so no GPU is needed. Matches the architecture's deployment section.
- **Alternatives considered**: Self-hosted models (rejected — violates no-GPU constraint); microservices (rejected — modular monolith is simpler for hackathon timeframe).