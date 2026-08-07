"""Chat API routes.

Endpoint implementations land here in US1+ (``/api/analyze``,
``/api/analyze/screenshot``, ``/api/follow-up``).
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}