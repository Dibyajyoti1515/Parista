# Agents and Skills — Parista

This document satisfies the hackathon's checkpoint 4 requirement: at least
one custom agent and one custom skill, committed to the repo and documented
here. Behavioral constraints for all agents are defined in `AGENTS.md` at
repo root. Full pipeline flow is in `docs/ARCHITECTURE.md`.

---

## Custom Agents (Google ADK)

Parista uses five ADK agents orchestrated by a root Coordinator Agent.
All are implemented under `backend/agents/`.

### 1. Coordinator Agent
`backend/agents/coordinator.py`
Root orchestrator. Receives the incoming user message, runs the Safety
Agent first, then routes sequentially through Classifier → Retrieval →
Reasoning → Style, and returns the final structured response.

### 2. Safety Agent
`backend/agents/safety_agent.py`
Runs on every single turn, before any other agent. Screens for crisis
signals (self-harm, suicidal ideation, abuse indicators). If triggered,
short-circuits the pipeline and returns supportive language plus
resources instead of relationship advice. This is a hard override — no
other agent runs after a crisis flag.

### 3. Classifier Agent
`backend/agents/classifier_agent.py`
Tags the incoming situation: domain (romantic / family / workplace),
conflict type, emotional tone, and age bracket where inferable. Produces
no advice itself — output is structured tags consumed by the Retrieval
Agent to condition search, rather than relying on raw semantic similarity
alone.

### 4. Retrieval Agent
`backend/agents/retrieval_agent.py`
**This is the primary custom agent for this checkpoint.**
Queries the core psychology knowledge base (Supabase pgvector) using the
Classifier Agent's tags. If the top result's similarity score is below
0.75, it calls the `paper_fetch_tool` (real-time Semantic Scholar query)
as a fallback rather than returning a low-confidence match or allowing
the Reasoning Agent to proceed ungrounded. This agent is what makes the
system's output "grounded and verifiable" per Track C's judging criteria,
rather than relying on the LLM's parametric knowledge.

### 5. Reasoning Agent
`backend/agents/reasoning_agent.py`
Takes the retrieved framework/chunk plus the user's situation and
produces a structured psychological analysis: pattern identified,
explanation, and source citation. Constrained by `AGENTS.md` to only
make claims traceable to the retrieved content.

### 6. Style Agent
`backend/agents/style_agent.py`
Rewrites the Reasoning Agent's verified output into a natural,
age-calibrated reply, drawing on cached tone examples in the
`style_examples` table. Only adjusts phrasing/tone — must not alter the
underlying psychological substance (enforced in `AGENTS.md`).

---

## Custom Skill: Citation Verification

`backend/tools/citation_verify_tool.py`

**What it does:**
Before any response reaches the user, this tool checks that every claim
in the Reasoning Agent's `psychological_pattern` output is actually
traceable to the specific chunk or paper that was retrieved for that
turn — not a claim the LLM generated from general training knowledge.

**How it works:**
1. Takes the Reasoning Agent's output and the retrieved source chunk(s)
   as input.
2. Checks that the cited `source` field matches a chunk that was actually
   returned by the Retrieval Agent this turn (not fabricated).
3. Flags any claim in the analysis that doesn't have reasonable textual
   support in the retrieved content.
4. If verification fails: the response is either regenerated with a
   stricter prompt, or replaced with a fallback "insufficient grounded
   information" message. It is never silently passed through.

**Why this is the skill we chose:**
Track C's stated judging bar is "the agent is reliable on messy input and
does not hallucinate... citation quality, refusal to invent answers."
This skill directly enforces that as a pipeline step rather than trusting
prompt instructions alone — it's the difference between *telling* the
model not to hallucinate and *checking* that it didn't.

**Invocation:**
Called automatically by the Coordinator Agent after the Reasoning Agent
step and before the Style Agent step, on every conversation turn.

---

## Supporting Tools (not counted as the custom agent/skill, but used by the above)

- `vector_search_tool.py` — pgvector similarity query against
  `psychology_kb_chunks`
- `paper_fetch_tool.py` — real-time Semantic Scholar API query, used by
  the Retrieval Agent as a fallback
- `ocr_tool.py` — vision-based parsing of uploaded chat screenshots into
  text before classification

---

## Human-in-the-Loop Note

All agent code above was scaffolded with Cline (Plan/Act approval flow)
and reviewed by the team before commit, per the hackathon's human-in-the-
loop requirement. Review notes are logged in `docs/DECISIONS.md`.