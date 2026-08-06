# Tasks: Grounded Conflict Assistant

**Input**: Design documents from `/specs/001-grounded-conflict-assistant/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included because the spec defines measurable success criteria (SC-001–SC-006) and the quickstart provides runnable validation scenarios. Tests are written first and must fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/`, `bot/` at repository root
- Backend: `backend/agents/`, `backend/modules/`, `backend/tools/`, `backend/tests/`
- Frontend: `frontend/src/`
- Bot: `bot/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend project structure with FastAPI dependencies in `backend/requirements.txt`
- [ ] T002 [P] Create frontend project scaffold in `frontend/` with React dependencies
- [ ] T003 [P] Create bot project scaffold in `bot/` with python-telegram-bot dependency
- [ ] T004 [P] Configure environment configuration management in `backend/.env.example` and `backend/config.py`
- [ ] T005 [P] Configure linting and formatting tools (ruff/black) in `backend/pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Setup Supabase database schema and migrations in `backend/modules/db/schema.sql` (users, conversations, messages, psychology_kb_chunks, style_examples, paper_cache)
- [ ] T007 [P] Setup pgvector extension and embedding column in `backend/modules/db/schema.sql`
- [ ] T008 [P] Implement database connection and client in `backend/modules/db/client.py`
- [ ] T009 [P] Setup API routing and middleware structure in `backend/main.py`
- [ ] T010 [P] Configure error handling and logging infrastructure in `backend/modules/chat/errors.py` and `backend/modules/chat/logging.py`
- [ ] T011 [P] Implement base ADK agent framework in `backend/agents/base.py`
- [ ] T012 [P] Implement Gemini model client in `backend/modules/db/llm.py` (Google AI Studio API)
- [ ] T013 [P] Implement embedding client for pgvector in `backend/modules/db/embeddings.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Text Conflict Analysis (Priority: P1) 🎯 MVP

**Goal**: User describes a conflict in text and receives a grounded, cited psychological analysis with a tone-calibrated suggested reply.

**Independent Test**: Submit a text description of a conflict via `POST /api/analyze` and verify the response contains a classified conflict type, a retrieved psychological framework, a verifiable source citation, and a suggested reply.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US1] Contract test for `POST /api/analyze` in `backend/tests/contract/test_analyze.py`
- [ ] T015 [P] [US1] Integration test for text conflict analysis journey in `backend/tests/integration/test_text_analysis.py`

### Implementation for User Story 1

- [ ] T016 [P] [US1] Implement Safety Agent in `backend/agents/safety_agent.py` (crisis override, runs first on every turn)
- [ ] T017 [P] [US1] Implement Classifier Agent in `backend/agents/classifier_agent.py` (tags domain, conflict type, emotional tone)
- [ ] T018 [P] [US1] Implement Retrieval Agent in `backend/agents/retrieval_agent.py` (queries pgvector core KB)
- [ ] T019 [P] [US1] Implement Reasoning Agent in `backend/agents/reasoning_agent.py` (produces structured psychological analysis)
- [ ] T020 [P] [US1] Implement Style Agent in `backend/agents/style_agent.py` (rewrites into tone-calibrated reply)
- [ ] T021 [P] [US1] Implement Citation Verification tool in `backend/tools/citation_verify_tool.py` (checks claims trace to retrieved source, fails closed)
- [ ] T022 [P] [US1] Implement vector search tool in `backend/tools/vector_search_tool.py` (pgvector similarity query)
- [ ] T023 [US1] Implement Coordinator Agent in `backend/agents/coordinator.py` (routes Safety → Classifier → Retrieval → Reasoning → Citation Verify → Style)
- [ ] T024 [US1] Implement `POST /api/analyze` endpoint in `backend/modules/chat/routes.py` (depends on T023)
- [ ] T025 [US1] Add validation and error handling for analyze endpoint in `backend/modules/chat/routes.py`
- [ ] T026 [US1] Add logging for text analysis operations in `backend/modules/chat/logging.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Follow-up Questions (Priority: P2)

**Goal**: User asks a follow-up question within the same conversation; the system retains context (classified type, retrieved framework, prior exchange) and answers consistently. Safety check and citation verification apply to every turn.

**Independent Test**: Submit an initial analysis, then submit a follow-up via `POST /api/follow-up` and verify the response is consistent with the original analysis and includes a verifiable source citation.

### Tests for User Story 2

- [ ] T027 [P] [US2] Contract test for `POST /api/follow-up` in `backend/tests/contract/test_follow_up.py`
- [ ] T028 [P] [US2] Integration test for multi-turn follow-up journey in `backend/tests/integration/test_follow_up.py`

### Implementation for User Story 2

- [ ] T029 [P] [US2] Implement conversation context service in `backend/modules/chat/context.py` (retains classified type, retrieved framework, prior exchange)
- [ ] T030 [US2] Implement `POST /api/follow-up` endpoint in `backend/modules/chat/routes.py` (depends on T029)
- [ ] T031 [US2] Integrate follow-up with Coordinator Agent context in `backend/agents/coordinator.py`
- [ ] T032 [US2] Add validation and error handling for follow-up endpoint in `backend/modules/chat/routes.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Screenshot Analysis (Priority: P3)

**Goal**: User uploads a conversation screenshot; the system parses it into text and processes it through the same grounded analysis pipeline.

**Independent Test**: Upload a clear conversation screenshot via `POST /api/analyze/screenshot` and verify the system parses it and returns a grounded, cited analysis.

### Tests for User Story 3

- [ ] T033 [P] [US3] Contract test for `POST /api/analyze/screenshot` in `backend/tests/contract/test_screenshot.py`
- [ ] T034 [P] [US3] Integration test for screenshot analysis journey in `backend/tests/integration/test_screenshot.py`

### Implementation for User Story 3

- [ ] T035 [P] [US3] Implement OCR tool in `backend/tools/ocr_tool.py` (vision-capable LLM call for screenshot parsing)
- [ ] T036 [US3] Implement `POST /api/analyze/screenshot` endpoint in `backend/modules/chat/routes.py` (depends on T035)
- [ ] T037 [US3] Add validation and error handling for screenshot endpoint in `backend/modules/chat/routes.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Low-Confidence Fallback (Priority: P4)

**Goal**: When the core KB has low confidence (< 0.75), the system falls back to real-time Semantic Scholar retrieval, marks responses as "supplementary," or returns a clear "insufficient grounded information" message.

**Independent Test**: Submit a situation with no strong KB match and verify the system either returns a supplementary cited response or a clear "insufficient grounded information" message — never an uncited claim.

### Tests for User Story 4

- [ ] T038 [P] [US4] Integration test for low-confidence fallback journey in `backend/tests/integration/test_fallback.py`

### Implementation for User Story 4

- [ ] T039 [P] [US4] Implement paper fetch tool in `backend/tools/paper_fetch_tool.py` (Semantic Scholar API, real-time)
- [ ] T040 [P] [US4] Implement paper cache service in `backend/modules/db/paper_cache.py` (cache fetched papers in `paper_cache` table)
- [ ] T041 [US4] Integrate fallback into Retrieval Agent in `backend/agents/retrieval_agent.py` (trigger below 0.75 threshold, mark "supplementary")
- [ ] T042 [US4] Add "insufficient grounded information" fallback response handling in `backend/modules/chat/routes.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T043 [P] Implement Telegram bot client in `bot/telegram_bot.py` (thin client forwarding to backend via HTTP)
- [ ] T044 [P] Implement frontend API service in `frontend/src/api/client.ts` (calls backend endpoints)
- [ ] T045 [P] Implement frontend chat components in `frontend/src/components/`
- [ ] T046 [P] Documentation updates in `docs/` (architecture, agents & skills)
- [ ] T047 Code cleanup and refactoring across `backend/`
- [ ] T048 Performance optimization across all stories (primary flow < 30s per SC-003)
- [ ] T049 Security hardening (API key management, input validation)
- [ ] T050 Run quickstart.md validation scenarios end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 (Coordinator Agent) for context integration
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 (analysis pipeline) for processing
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Depends on US1 (Retrieval Agent) for fallback integration

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for POST /api/analyze in backend/tests/contract/test_analyze.py"
Task: "Integration test for text conflict analysis journey in backend/tests/integration/test_text_analysis.py"

# Launch all agents for User Story 1 together:
Task: "Implement Safety Agent in backend/agents/safety_agent.py"
Task: "Implement Classifier Agent in backend/agents/classifier_agent.py"
Task: "Implement Retrieval Agent in backend/agents/retrieval_agent.py"
Task: "Implement Reasoning Agent in backend/agents/reasoning_agent.py"
Task: "Implement Style Agent in backend/agents/style_agent.py"
Task: "Implement Citation Verification tool in backend/tools/citation_verify_tool.py"
Task: "Implement vector search tool in backend/tools/vector_search_tool.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Constitution compliance: all agent code (Safety, Classifier, Retrieval, Reasoning, Style, Coordinator) MUST be human-reviewed before merge (principle III); Citation Verification enforces "Never Hallucinate a Source" (principle II); Safety Agent enforces "Crisis Override Is Absolute" (principle IV)