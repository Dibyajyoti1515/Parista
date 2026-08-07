"""Retrieval Agent for the Parista backend.

Queries the core psychology knowledge base (Supabase pgvector) using the
Classifier Agent's tags (domain, conflict type, emotional tone) to condition
search, rather than relying on raw semantic similarity alone.

If the top result's similarity score is below 0.75, the real-time Semantic
Scholar fallback (``paper_fetch_tool``) is triggered in the US4 phase (T039).
Until then, a below-threshold result returns ``None`` so the pipeline signals
"insufficient grounded information" rather than proceeding ungrounded.
"""

from backend.agents.base import BaseAgent
from backend.modules.chat.logging import get_logger
from backend.tools.vector_search_tool import (
    CONFIDENCE_THRESHOLD,
    VectorSearchResult,
    search_chunks,
    top_match,
)

logger = get_logger("retrieval")


class RetrievalAgent(BaseAgent):
    """Retrieves a matching psychological framework from the core KB."""

    def __init__(self) -> None:
        super().__init__(
            name="retrieval_agent",
            instruction=(
                "You are the Retrieval Agent for Parista. Given the classifier's "
                "tags (domain, conflict type, emotional tone), retrieve the most "
                "relevant psychological framework from the curated knowledge "
                "base. If confidence is below threshold, trigger real-time "
                "academic paper retrieval. Never proceed ungrounded."
            ),
        )

    def retrieve(
        self,
        text: str,
        classification: dict,
        limit: int = 5,
    ) -> list[VectorSearchResult]:
        """Retrieve knowledge base chunks for the user's situation.

        The classifier's domain tag is used to condition the query text so
        retrieval is biased toward the right domain. Returns chunks sorted by
        similarity descending.
        """
        domain = classification.get("domain", "general")
        # Condition the query with the domain tag to improve precision.
        conditioned_query = f"{text} ({domain} conflict)"
        self.log("retrieving", domain=domain, limit=limit)
        return search_chunks(conditioned_query, limit=limit)

    def top_match(self, text: str, classification: dict) -> VectorSearchResult | None:
        """Return the top retrieval result, or ``None`` if below threshold.

        A ``None`` result signals that the core KB has no confident match;
        the Coordinator should then either trigger the real-time fallback
        (US4, T039) or return "insufficient grounded information".
        """
        domain = classification.get("domain", "general")
        conditioned_query = f"{text} ({domain} conflict)"
        result = top_match(conditioned_query)
        if result is None:
            logger.info(
                "no_confident_match",
                threshold=CONFIDENCE_THRESHOLD,
                domain=domain,
            )
        return result