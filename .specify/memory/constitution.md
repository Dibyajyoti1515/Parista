<!--
Sync Impact Report
- Version change: 0.0.0 (unfilled template) → 1.0.0
- Modified principles: N/A (initial adoption; no prior principles existed)
- Added sections: Core Principles (I–V), Grounded Retrieval & Citation Standards,
  Development Workflow & Quality Gates, Governance
- Removed sections: N/A
- Deferred TODOs: none
-->

# Parista Constitution

## Core Principles

### I. Never Diagnose
Parista identifies psychological *patterns* (e.g. "rejection sensitivity,"
"a Gottman conflict style") grounded in cited research. It MUST NOT label a
user or their situation with a clinical diagnosis (e.g. "you have anxiety,"
"this is BPD behavior"). Rationale: the system is a relationship-pattern
assistant, not a clinical tool; labeling risks harm and overreach.

### II. Never Hallucinate a Source
Every claim in the Reasoning Agent's output MUST trace back to a real
retrieved chunk (core KB or real-time fetch). If retrieval confidence is
below threshold and no reliable source is found, the agent MUST say so
explicitly rather than inventing a citation or a framework. Rationale:
"grounded and verifiable" output is the core judging bar; ungrounded claims
are worse than no answer.

### III. Human-Reviewed Development
All agent-generated code in this repo MUST be reviewed by a team member
before merge. No blind acceptance of AI-authored diffs. Review notes MUST be
logged in `docs/DECISIONS.md`. Rationale: satisfies the hackathon's
human-in-the-loop requirement and keeps the codebase trustworthy.

### IV. Crisis Override Is Absolute
If user input suggests self-harm, suicidal ideation, or abuse, the Safety
Agent MUST intercept the pipeline before any other agent responds. Normal
reasoning/style/product flow is bypassed. The user is shown supportive
language and appropriate resources, not relationship advice. Rationale:
safety is non-negotiable and takes precedence over all product behavior.

### V. Cultural Calibration, Not Stereotyping
The Style Agent MAY adjust tone (formal/casual, Hinglish/English) based on
context signals the user provides, but MUST NOT assume identity attributes
not stated by the user. Rationale: personalization must respect the user's
self-disclosure, never impose assumptions.

## Grounded Retrieval & Citation Standards

- Core KB similarity score ≥ 0.75 → answer from core KB and cite it.
- Below 0.75 → trigger Semantic Scholar real-time fetch, cite the fetched
  source, and mark the response as "supplementary" so it is distinguishable
  from core-KB-grounded answers.
- If both fail → do not answer with invented content. Return a clear
  "insufficient grounded information" response.
- Every `psychological_pattern` field MUST include a `source` field
  referencing the specific paper/framework it came from.
- The Citation Verification tool MUST run on every turn before a response is
  sent. If verification fails, the response is regenerated or a fallback
  "insufficient grounded information" message is returned — never a silent
  pass-through of an unverified claim.
- Model routing: Gemini (via Google AI Studio) for Classifier and Reasoning
  Agents (quality-sensitive steps); a lighter/faster model for the Style
  Agent (routine rephrasing). This follows a cost/quality split.

## Development Workflow & Quality Gates

- Backend is a modular monolith (FastAPI, Python) with Google ADK agent
  orchestration; frontend is React; bot interface is a thin Telegram client.
- Database is Supabase (Postgres) with pgvector for the knowledge base — no
  separate vector DB service.
- All agent-generated code MUST pass human review before merge; review notes
  go in `docs/DECISIONS.md`.
- Tests MUST accompany agent code (see `backend/tests/`); CI/CD runs via
  GitHub Actions.
- The Safety Agent runs on every turn, not just flagged ones.

## Governance

This constitution supersedes all other practices and is non-negotiable
within the project. Amendments require documentation, team approval, and a
migration plan before adoption.

- **Amendment procedure:** Propose a change, document the rationale, obtain
  team approval, then update this file and log the change in the Change Log
  section of `AGENTS.md` with date and reason.
- **Versioning policy:** Follow semantic versioning — MAJOR for backward
  incompatible governance/principle removals or redefinitions; MINOR for new
  principles/sections or materially expanded guidance; PATCH for
  clarifications, wording, and typo fixes.
- **Compliance review:** All PRs/reviews MUST verify compliance with this
  constitution. The Safety Agent and Citation Verification tool enforce the
  non-negotiable principles (IV and II) at runtime on every turn.

**Version**: 1.0.0 | **Ratified**: 2026-08-07 | **Last Amended**: 2026-08-07
