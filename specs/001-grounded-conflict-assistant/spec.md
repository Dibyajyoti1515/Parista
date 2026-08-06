# Feature Specification: Grounded Conflict Assistant

**Feature Branch**: `001-grounded-conflict-assistant`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "Parista is an agentic system that helps users navigate interpersonal conflicts — romantic breakups, family misunderstandings, workplace or HR conflicts — by analyzing their situation against a curated psychology research knowledge base and generating a grounded, cited, tone-calibrated response. Users interact via Telegram or a React web frontend, and can optionally upload screenshots of conversations for analysis. The system must never hallucinate psychological claims: every insight must trace back to a real, cited source, with a fallback to real-time academic paper retrieval when the core knowledge base has low confidence. Core user flow: user describes a situation or uploads a screenshot, the system classifies the conflict type and emotional tone, retrieves a matching psychological framework, verifies the claim is properly sourced, then returns a structured response with a suggested reply calibrated to a natural, modern tone."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Text Conflict Analysis (Priority: P1)

A user describes an interpersonal conflict situation in plain language (e.g., a romantic breakup, a family misunderstanding, or a workplace/HR conflict). The system analyzes the situation, classifies the conflict type and emotional tone, retrieves a matching psychological framework from the curated knowledge base, verifies every claim is properly sourced, and returns a structured response with a suggested reply calibrated to a natural, modern tone.

**Why this priority**: This is the core value proposition — the primary way users interact with the system. Without it, there is no product.

**Independent Test**: Can be fully tested by submitting a text description of a conflict and verifying the response contains a grounded psychological analysis, a verifiable source citation, and a tone-calibrated suggested reply.

**Acceptance Scenarios**:

1. **Given** a user submits a text description of a romantic conflict, **When** the system processes it, **Then** the response includes a classified conflict type, a retrieved psychological framework, a verifiable source citation, and a suggested reply.
2. **Given** a user submits a text description of a workplace conflict, **When** the system processes it, **Then** the response is grounded in a cited source and does not contain any uncited psychological claim.
3. **Given** a user submits a text description, **When** the system returns a response, **Then** every psychological claim in the response traces back to a real, cited source.

---

### User Story 2 - Follow-up Questions (Multi-Turn) (Priority: P2)

A user who has already received an analysis asks a follow-up question within the same conversation (e.g., "what should I say if she doesn't reply" or "what if he gets defensive"). The system retains context from prior turns — the classified conflict type, the retrieved framework, and the prior exchange — and answers the follow-up consistently with the original analysis rather than restarting from scratch. Each follow-up still goes through the same safety check and citation verification as the first turn.

**Why this priority**: Follow-up support significantly increases the usefulness of the product by allowing users to explore their situation iteratively, but it depends on the core analysis flow (P1) being in place.

**Independent Test**: Can be fully tested by submitting an initial conflict description, receiving an analysis, then submitting a follow-up question and verifying the response is consistent with the original analysis and includes a verifiable source citation.

**Acceptance Scenarios**:

1. **Given** a user has received an initial analysis, **When** they ask a follow-up question in the same conversation, **Then** the response retains the classified conflict type and retrieved framework from the original analysis.
2. **Given** a user asks a follow-up question, **When** the system processes it, **Then** the response is grounded in a cited source and does not contradict the original analysis.
3. **Given** a user asks a follow-up question, **When** the system processes it, **Then** the safety check and citation verification are applied to the follow-up turn just as they are to the first turn.

---

### User Story 3 - Screenshot Analysis (Priority: P3)

A user uploads a screenshot of a conversation (e.g., a chat exchange) for analysis. The system parses the screenshot into text, then processes it through the same classification, retrieval, verification, and response pipeline as a text description.

**Why this priority**: Screenshot support is a valuable convenience feature that broadens how users can input their situation, but it depends on the core analysis flow (P1) being in place.

**Independent Test**: Can be fully tested by uploading a clear conversation screenshot and verifying the system parses it and returns a grounded, cited analysis.

**Acceptance Scenarios**:

1. **Given** a user uploads a clear conversation screenshot, **When** the system processes it, **Then** the screenshot is parsed into text and the user receives a grounded, cited analysis.
2. **Given** a user uploads a blurry or unreadable screenshot, **When** the system processes it, **Then** the user receives a clear message that the screenshot could not be parsed.

---

### User Story 4 - Low-Confidence Fallback (Priority: P4)

When the core knowledge base has low confidence in matching a psychological framework to the user's situation, the system falls back to real-time academic paper retrieval. If a reliable source is found, the response is marked as "supplementary" and cites the fetched source. If no reliable source is found, the system returns a clear "insufficient grounded information" response rather than inventing content.

**Why this priority**: This is a critical reliability feature that ensures the system never hallucinates, but it is a fallback path that only activates when the primary retrieval path (P1) has low confidence.

**Independent Test**: Can be fully tested by submitting a situation that has no strong match in the core knowledge base and verifying the system either returns a supplementary cited response or a clear "insufficient grounded information" message — never an uncited claim.

**Acceptance Scenarios**:

1. **Given** the core knowledge base has low confidence in a match, **When** the system processes the situation, **Then** it retrieves a real-time academic paper and marks the response as "supplementary" with a citation.
2. **Given** the core knowledge base has low confidence and no reliable real-time source is found, **When** the system processes the situation, **Then** it returns a clear "insufficient grounded information" response rather than inventing content.

---

### Edge Cases

- What happens when a user's description spans multiple conflict domains (e.g., romantic and workplace)?
- How does the system handle a blurry or unreadable screenshot?
- What happens when no psychological framework matches the user's situation?
- How does the system respond to crisis signals (self-harm, suicidal ideation, abuse)?
- What happens when low-confidence retrieval finds no reliable real-time source?
- How does the system handle a follow-up question that drifts from or contradicts the original situation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept text descriptions of interpersonal conflicts from users.
- **FR-002**: System MUST classify the conflict domain (romantic/family/workplace), conflict type, and emotional tone of the user's situation.
- **FR-003**: System MUST retrieve a matching psychological framework from the curated knowledge base based on the classification.
- **FR-004**: System MUST verify that every psychological claim in the response traces back to a real, cited source.
- **FR-005**: System MUST return a structured response that includes a psychological analysis, a verifiable source citation, and a suggested reply calibrated to a natural, modern tone.
- **FR-006**: System MUST retain conversation context across turns, including the classified conflict type, retrieved framework, and prior exchange.
- **FR-007**: System MUST answer follow-up questions consistently with the original analysis, without restarting from scratch.
- **FR-008**: System MUST apply the safety check and citation verification to every turn, including follow-ups.
- **FR-009**: System MUST accept and parse uploaded conversation screenshots into text for analysis.
- **FR-010**: System MUST fall back to real-time academic paper retrieval when the core knowledge base has low confidence, and mark such responses as "supplementary."
- **FR-011**: System MUST return a clear "insufficient grounded information" response when no reliable source is found, rather than inventing content.
- **FR-012**: System MUST run a safety check on every input and short-circuit to supportive resources on crisis signals.

### Key Entities *(include if feature involves data)*

- **User**: A person using the system via Telegram or the web frontend; identified by a unique ID.
- **Conversation**: A sequence of messages between a user and the system; retains context across turns.
- **Message**: A single exchange in a conversation, with a role (user/agent) and content.
- **Psychological Framework**: A curated research-based framework (e.g., "Rejection Sensitivity") matched to the user's situation.
- **Source Citation**: A reference to the specific paper or framework a claim is grounded in.
- **Suggested Reply**: A tone-calibrated reply generated for the user to use in their real conversation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 90% of conflict descriptions receive a grounded, cited response.
- **SC-002**: 0% of responses contain an uncited psychological claim.
- **SC-003**: The primary flow (describe a situation → receive a response) completes in under 30 seconds.
- **SC-004**: At least 85% of clear conversation screenshots are successfully parsed and analyzed.
- **SC-005**: Every response includes a verifiable source citation.
- **SC-006**: At least 80% of follow-up questions are answered consistently with the original analysis, without contradicting the prior framework.

## Assumptions

- Users have stable internet connectivity.
- Screenshots uploaded by users are chat-style conversation screenshots.
- A curated psychology research knowledge base exists and is populated with relevant frameworks.
- Real-time academic paper retrieval is available as a fallback when the core knowledge base has low confidence.
- The conversations and messages data model supports multi-turn context retention.
- The system is a relationship-pattern assistant, not a clinical tool — it identifies patterns, never diagnoses.
- Safety (crisis override) takes precedence over all product behavior.

## Clarifications

None — all aspects of the feature have been resolved. The multi-turn follow-up behavior was clarified: users can ask follow-up questions within the same conversation, and the system retains context (classified conflict type, retrieved framework, prior exchange) so follow-ups are answered consistently with the original analysis. Safety check and citation verification apply to every turn, including follow-ups.