"""Unit tests for the Citation Verification tool.

Validates the "fails closed" guarantee from the Parista constitution: a claim
whose cited source was not among the chunks retrieved this turn is rejected
(``verified: false``), and only a claim that traces to a real retrieved chunk
is accepted (``verified: true``).

These tests use the ``CitationVerifyTool`` / ``verify_citation`` helper
directly — no Supabase, no Gemini, no network.
"""

from backend.tools.citation_verify_tool import (
    INSUFFICIENT_GROUNDED_MESSAGE,
    CitationVerifyTool,
    verify_citation,
)


def _analysis(source_title):
    """Build a minimal analysis dict claiming ``source_title`` as its source."""
    return {
        "psychological_pattern": {
            "pattern": "Four Horsemen",
            "explanation": "Criticism escalating to stonewalling.",
            "source": {
                "source_title": source_title,
                "framework_name": "Four Horsemen",
            },
        }
    }


def test_fails_closed_when_source_not_retrieved():
    """A claimed source absent from retrieved chunks → verified: False."""
    retrieved = [
        {"source_title": "Gottman, J. M. (1992). What Predicts Divorce?"},
        {"source_title": "Perel, E. (2005). The State of Affairs"},
    ]
    # The claim cites a source that was NOT among the retrieved chunks.
    analysis = _analysis("A fabricated source that was never retrieved")

    result = verify_citation(analysis, retrieved)

    assert result["verified"] is False
    assert result["fallback"] == INSUFFICIENT_GROUNDED_MESSAGE


def test_passes_when_source_matches_retrieved_chunk():
    """A claimed source that matches a retrieved chunk → verified: True."""
    title = "Gottman, J. M. (1992). What Predicts Divorce?"
    retrieved = [{"source_title": title}, {"source_title": "Another paper"}]
    analysis = _analysis(title)

    result = verify_citation(analysis, retrieved)

    assert result["verified"] is True
    assert result["analysis"] == analysis


def test_fails_closed_without_psychological_pattern():
    """An analysis lacking a psychological_pattern → verified: False."""
    result = verify_citation({"unrelated": True}, [{"source_title": "X"}])
    assert result["verified"] is False


def test_fails_closed_without_source_title():
    """A pattern whose source lacks source_title → verified: False."""
    analysis = {"psychological_pattern": {"pattern": "x", "source": {}}}

    result = verify_citation(analysis, [{"source_title": "X"}])

    assert result["verified"] is False


def test_tool_class_behaves_like_wrapper():
    """The ``CitationVerifyTool`` class mirrors the module-level wrapper."""
    tool = CitationVerifyTool()
    title = "Gottman, J. M. (1992). What Predicts Divorce?"

    verified_result = tool.verify(_analysis(title), [{"source_title": title}])
    assert verified_result["verified"] is True

    mismatch_result = tool.verify(_analysis("not retrieved"), [{"source_title": title}])
    assert mismatch_result["verified"] is False
    assert mismatch_result["fallback"] == INSUFFICIENT_GROUNDED_MESSAGE
