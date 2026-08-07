"""Contract tests for ``POST /api/analyze`` (spec task T014).

Uses FastAPI's ``TestClient`` — no live server is required. All calls that
would reach Supabase (pgvector) or Gemini are mocked with
``unittest.mock.patch`` so the tests run fully offline in CI without real
credentials. The endpoint orchestration logic in ``backend/modules/chat/routes.py``
is what is exercised end-to-end:

    Safety check → Classifier → Retrieval → Reasoning → Citation Verify → Style
"""

from unittest.mock import patch

from backend.tools.citation_verify_tool import INSUFFICIENT_GROUNDED_MESSAGE

# A well-known romantic-conflict source drawn from the core KB (Gottman &
# Levenson, 1992). Mocked retrieval returns a chunk citing this source so the
# pipeline can ground an analysis without a live database connection.
SOURCE_TITLE = "Gottman, J. M. & Levenson, R. W. (1992). Marital Discord and the Four Horsemen"
FRAMEWORK_NAME = "Four Horsemen"

# --- Fixed pipeline responses returned by the mocked CoordinatorAgent.process ---

CRISIS_PIPELINE = {
    "crisis_override": True,
    "message": (
        "I'm really sorry you're going through this. Your safety matters most, "
        "and I'm not the right resource for this right now. Please reach out to "
        "someone who can help immediately: 988 (US) or your local emergency services."
    ),
}

FALLBACK_PIPELINE = {
    "conversation_id": None,
    "classification": {
        "domain": "general",
        "conflict_type": "other",
        "emotional_tone": "neutral",
        "age_bracket": None,
    },
    "analysis": None,
    "suggested_reply": None,
    "supplementary": False,
    "fallback_needed": True,
    "message": "No confident match found in the core knowledge base.",
}

SUCCESS_PIPELINE = {
    "conversation_id": None,
    "classification": {
        "domain": "romantic",
        "conflict_type": "communication",
        "emotional_tone": "hurt",
        "age_bracket": None,
    },
    # routes.py reconstructs a VectorSearchResult from this dict before passing
    # it to the (mocked) ReasoningAgent.
    "retrieved_source": {
        "chunk_id": "chunk-1",
        "source_title": SOURCE_TITLE,
        "framework_name": FRAMEWORK_NAME,
        "content": (
            "The Four Horsemen — criticism, contempt, defensiveness, stonewalling — "
            "are habitual communication patterns that predict relationship breakdown."
        ),
        "similarity": 0.92,
    },
    "analysis": None,
    "suggested_reply": None,
    "supplementary": False,
    "fallback_needed": False,
}

# Fixed output returned by the mocked ReasoningAgent.reason.
REASONING_OUTPUT = {
    "psychological_pattern": {
        "pattern": "Four Horsemen: criticism escalating to stonewalling",
        "explanation": (
            "The user's boyfriend criticizes everything and then stonewalls, "
            "matching the Four Horsemen pattern of criticism escalating into "
            "stonewalling — a documented predictor of relationship breakdown."
        ),
        "source": {
            "source_title": SOURCE_TITLE,
            "framework_name": FRAMEWORK_NAME,
        },
    }
}

# Fixed output returned by the mocked StyleAgent.style.
SUGGESTED_REPLY = {
    "text": (
        "It sounds like criticism and stonewalling are making it hard to connect. "
        'You might try: "I felt hurt when our conversation went quiet — can we pause '
        'and try again?"'
    ),
    "tone": "casual",
}


def test_analyze_empty_text_returns_400(client):
    """Empty or whitespace-only text must be rejected with HTTP 400."""
    response = client.post("/api/analyze", json={"text": ""})
    assert response.status_code == 400
    assert "text must not be empty" in response.json()["detail"]

    response = client.post("/api/analyze", json={"text": "   "})
    assert response.status_code == 400


def test_analyze_crisis_signal_short_circuits(client):
    """A crisis-signal message returns crisis_override=True.

    routes.py returns the crisis payload immediately when
    ``pipeline["crisis_override"]`` is true, so the pipeline must NOT proceed to
    reasoning / citation verification / style.
    """
    with patch(
        "backend.agents.coordinator.CoordinatorAgent.process",
        return_value=CRISIS_PIPELINE,
    ) as process_mock, patch(
        "backend.agents.reasoning_agent.ReasoningAgent.reason"
    ) as reason_mock, patch(
        "backend.modules.chat.routes.verify_citation"
    ) as verify_mock, patch(
        "backend.agents.style_agent.StyleAgent.style"
    ) as style_mock:
        response = client.post(
            "/api/analyze",
            json={"text": "I keep thinking about killing myself and don't want to live anymore."},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["crisis_override"] is True
    assert "message" in body
    # Crisis short-circuits before analysis / reply are produced.
    assert body.get("analysis") is None
    assert body.get("suggested_reply") is None
    process_mock.assert_called_once()
    reason_mock.assert_not_called()
    verify_mock.assert_not_called()
    style_mock.assert_not_called()


def test_analyze_low_confidence_returns_insufficient_grounded(client):
    """Below-threshold retrieval yields the insufficient-grounded fallback."""
    with patch(
        "backend.agents.coordinator.CoordinatorAgent.process",
        return_value=FALLBACK_PIPELINE,
    ):
        response = client.post(
            "/api/analyze",
            json={"text": "Some obscure situation with no match in the knowledge base."},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["analysis"] is None
    assert body["suggested_reply"] is None
    assert body["supplementary"] is False
    assert body["message"] == INSUFFICIENT_GROUNDED_MESSAGE


def test_analyze_romantic_conflict_returns_full_schema(client):
    """A confident core-KB match returns classification, analysis, and reply."""
    with patch(
        "backend.agents.coordinator.CoordinatorAgent.process",
        return_value=SUCCESS_PIPELINE,
    ) as process_mock, patch(
        "backend.agents.reasoning_agent.ReasoningAgent.reason",
        return_value=REASONING_OUTPUT,
    ) as reason_mock, patch(
        "backend.modules.chat.routes.verify_citation",
        return_value={"verified": True, "analysis": REASONING_OUTPUT},
    ) as verify_mock, patch(
        "backend.agents.style_agent.StyleAgent.style",
        return_value=SUGGESTED_REPLY,
    ) as style_mock:
        response = client.post(
            "/api/analyze",
            json={"text": "My boyfriend criticizes everything I do and then stonewalls me for hours."},
        )

    assert response.status_code == 200
    body = response.json()

    # classification
    assert body["classification"]["domain"] == "romantic"

    # analysis.psychological_pattern.source — the verifiable citation.
    pattern = body["analysis"]["psychological_pattern"]
    assert pattern["source"]["source_title"] == SOURCE_TITLE
    assert pattern["source"]["framework_name"] == FRAMEWORK_NAME
    assert pattern["pattern"]
    assert pattern["explanation"]

    # suggested_reply
    reply = body["suggested_reply"]
    assert reply["text"]
    assert reply["tone"] == "casual"

    # A confident core-KB match is never supplementary or a fallback.
    assert body["supplementary"] is False
    assert body.get("fallback_needed") is not True

    # The mocked pipeline stages were each invoked exactly once.
    process_mock.assert_called_once()
    reason_mock.assert_called_once()
    verify_mock.assert_called_once()
    style_mock.assert_called_once()
