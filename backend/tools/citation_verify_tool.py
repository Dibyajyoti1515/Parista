"""Citation Verification tool for the Parista backend.

Before any response reaches the user, this tool checks that every claim in
the Reasoning Agent's ``psychological_pattern`` output is actually traceable
to the specific chunk or paper that was retrieved for that turn — not a
claim the LLM generated from general training knowledge.

Fails closed: if verification fails, the response is either regenerated with
a stricter prompt, or replaced with a fallback "insufficient grounded
information" message. It is never silently passed through.
"""

from typing import Any

from backend.modules.chat.logging import get_logger

logger = get_logger("citation_verify")

# Fallback message used when verification fails and no regeneration is possible.
INSUFFICIENT_GROUNDED_MESSAGE = "insufficient grounded information"


class CitationVerificationError(Exception):
    """Raised when a claim cannot be traced to a retrieved source."""


class CitationVerifyTool:
    """Checks that claims in an analysis trace back to retrieved sources."""

    def __init__(self) -> None:
        self.logger = get_logger("citation_verify")

    def verify(
        self,
        analysis: dict[str, Any],
        retrieved_chunks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Verify an analysis against the chunks retrieved this turn.

        The analysis is expected to contain a ``psychological_pattern`` with
        a ``source`` field (e.g., ``{"source_title": "...", "framework_name":
        "..."}``). The verification succeeds only if:

        1. The analysis has a ``psychological_pattern`` with a ``source``.
        2. The cited ``source_title`` matches a chunk that was actually
           retrieved this turn (not fabricated from training knowledge).

        Returns a dict with ``verified`` (bool) and, on success, the
        ``analysis``; on failure, a ``fallback`` message.
        """
        pattern = analysis.get("psychological_pattern")
        if not pattern or not isinstance(pattern, dict):
            self._fail("analysis missing psychological_pattern")
            return self._fallback()

        source = pattern.get("source")
        if not source or not source.get("source_title"):
            self._fail("psychological_pattern missing source")
            return self._fallback()

        claimed_title = source["source_title"]
        retrieved_titles = {
            chunk.get("source_title")
            for chunk in retrieved_chunks
            if chunk.get("source_title")
        }

        if claimed_title not in retrieved_titles:
            self._fail(
                "cited source not retrieved this turn",
                claimed_title=claimed_title,
                retrieved_titles=sorted(retrieved_titles),
            )
            return self._fallback()

        self.logger.info(
            "citation_verified",
            source_title=claimed_title,
            chunk_count=len(retrieved_chunks),
        )
        return {"verified": True, "analysis": analysis}

    def _fail(self, reason: str, **details: Any) -> None:
        self.logger.warning("citation_verification_failed", reason=reason, **details)

    def _fallback(self) -> dict[str, Any]:
        return {
            "verified": False,
            "fallback": INSUFFICIENT_GROUNDED_MESSAGE,
        }


citation_verify_tool = CitationVerifyTool()


def verify_citation(analysis: dict[str, Any], retrieved_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    """Module-level convenience wrapper around ``CitationVerifyTool.verify``."""
    return citation_verify_tool.verify(analysis, retrieved_chunks)