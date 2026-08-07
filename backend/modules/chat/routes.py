"""Chat API routes.

Endpoints:
- GET /api/health — health check
- POST /api/analyze — analyze a text conflict description (full pipeline)

The analyze endpoint drives the pipeline via the existing Coordinator Agent
(Safety → Classifier → Retrieval), then continues with the Reasoning Agent,
Citation Verification tool, and Style Agent to produce the final structured
response. The Coordinator itself is not modified here.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.agents.coordinator import CoordinatorAgent
from backend.agents.reasoning_agent import ReasoningAgent
from backend.agents.style_agent import StyleAgent
from backend.modules.chat.logging import get_logger
from backend.tools.citation_verify_tool import INSUFFICIENT_GROUNDED_MESSAGE, verify_citation
from backend.tools.vector_search_tool import VectorSearchResult

logger = get_logger("routes")

router = APIRouter()

# Singletons — instantiated once at import time.
coordinator_agent = CoordinatorAgent()
reasoning_agent = ReasoningAgent()
style_agent = StyleAgent()


class AnalyzeRequest(BaseModel):
    """Request body for POST /api/analyze."""

    conversation_id: str | None = None
    text: str


@router.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@router.post("/analyze")
async def analyze(request: AnalyzeRequest) -> dict:
    """Analyze a text description of an interpersonal conflict.

    Runs the full grounded pipeline: Safety (crisis override) → Classifier →
    Retrieval → Reasoning → Citation Verification → Style. Returns the final
    structured response with classification, grounded analysis, source
    citation, and a tone-calibrated suggested reply.
    """
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text must not be empty")

    # Step 1-3: Safety, Classifier, Retrieval (via the Coordinator).
    pipeline = coordinator_agent.process(text, {"conversation_id": request.conversation_id})

    # Crisis override — return the supportive response as-is.
    if pipeline.get("crisis_override"):
        return pipeline

    # Below confidence threshold — do NOT proceed ungrounded. The Semantic
    # Scholar fallback (US4) is not yet implemented, so return the
    # "insufficient grounded information" fallback.
    if pipeline.get("fallback_needed"):
        logger.info("insufficient_grounded", conversation_id=pipeline.get("conversation_id"))
        return {
            "conversation_id": pipeline.get("conversation_id"),
            "classification": pipeline.get("classification"),
            "analysis": None,
            "suggested_reply": None,
            "supplementary": False,
            "message": INSUFFICIENT_GROUNDED_MESSAGE,
        }

    # Reconstruct the retrieved chunk for the Reasoning Agent.
    retrieved = pipeline["retrieved_source"]
    chunk = VectorSearchResult(
        chunk_id=retrieved["chunk_id"],
        source_title=retrieved["source_title"],
        framework_name=retrieved["framework_name"],
        content=retrieved["content"],
        similarity=retrieved["similarity"],
    )

    # Step 4: Reasoning Agent — ground the analysis in the retrieved chunk.
    analysis = reasoning_agent.reason(text, chunk)

    # Step 5: Citation Verification — fails closed. Never pass through
    # unverified claims.
    verification = verify_citation(analysis, [retrieved])
    if not verification["verified"]:
        logger.warning("citation_verification_failed", conversation_id=pipeline.get("conversation_id"))
        return {
            "conversation_id": pipeline.get("conversation_id"),
            "classification": pipeline.get("classification"),
            "analysis": None,
            "suggested_reply": None,
            "supplementary": False,
            "message": INSUFFICIENT_GROUNDED_MESSAGE,
        }

    # Step 6: Style Agent — tone-calibrated suggested reply.
    suggested_reply = style_agent.style(verification["analysis"])

    response = {
        "conversation_id": pipeline.get("conversation_id"),
        "classification": pipeline.get("classification"),
        "analysis": verification["analysis"],
        "suggested_reply": suggested_reply,
        "supplementary": False,
    }
    logger.info("analyze_completed", conversation_id=response["conversation_id"])
    return response