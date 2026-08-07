"""Vector search tool for the Parista backend.

Queries the ``psychology_kb_chunks`` table (pgvector) for chunks similar to
the user's situation. Used by the Retrieval Agent.
"""

from typing import Any

from backend.modules.chat.logging import get_logger
from backend.modules.db.client import get_supabase_client
from backend.modules.embeddings import get_embedding

logger = get_logger("vector_search")

# Confidence threshold per the constitution: >=0.75 answers from the core KB.
CONFIDENCE_THRESHOLD = 0.75


class VectorSearchResult:
    """A single retrieval result from the knowledge base."""

    def __init__(self, chunk_id: str, source_title: str, framework_name: str, content: str, similarity: float) -> None:
        self.chunk_id = chunk_id
        self.source_title = source_title
        self.framework_name = framework_name
        self.content = content
        self.similarity = similarity

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "source_title": self.source_title,
            "framework_name": self.framework_name,
            "content": self.content,
            "similarity": self.similarity,
        }


def search_chunks(query_text: str, limit: int = 5) -> list[VectorSearchResult]:
    """Search the knowledge base for chunks similar to ``query_text``.

    Requires a Postgres RPC function ``match_psychology_kb_chunks`` that
    takes a query embedding and returns the top matches (defined in
    ``schema.sql``). Returns results sorted by similarity descending.
    """
    client = get_supabase_client()
    embedding = get_embedding(query_text)

    rpc_result = client.rpc(
        "match_psychology_kb_chunks",
        {
            "query_embedding": embedding,
            "match_count": limit,
        },
    ).execute()

    results: list[VectorSearchResult] = []
    for row in rpc_result.data:
        results.append(
            VectorSearchResult(
                chunk_id=row["id"],
                source_title=row.get("source_title", ""),
                framework_name=row.get("framework_name"),
                content=row.get("content", ""),
                similarity=float(row.get("similarity", 0.0)),
            )
        )

    logger.info("vector_search_completed", query_length=len(query_text), results=len(results))
    return results


def top_match(query_text: str) -> VectorSearchResult | None:
    """Return the top retrieval result, or ``None`` if below threshold."""
    results = search_chunks(query_text, limit=1)
    if not results:
        return None
    top = results[0]
    if top.similarity < CONFIDENCE_THRESHOLD:
        logger.info("below_confidence_threshold", similarity=top.similarity)
        return None
    return top