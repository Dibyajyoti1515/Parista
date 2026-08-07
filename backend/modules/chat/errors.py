"""Error handling infrastructure for the Parista backend."""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class ParistaError(Exception):
    """Base class for Parista-specific errors."""

    status_code = 500
    detail = "An unexpected error occurred."

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class InsufficientGroundedInformationError(ParistaError):
    """Raised when no reliable source can be found for a claim."""

    status_code = 200  # returned as a structured fallback response, not an error
    detail = "insufficient grounded information"


class CrisisOverrideError(ParistaError):
    """Raised when the Safety Agent intercepts a crisis signal."""

    status_code = 200  # returned as a supportive response, not an error
    detail = "crisis override"


async def parista_error_handler(request: Request, exc: ParistaError) -> JSONResponse:
    """Convert a ParistaError into a JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Convert an HTTPException into a JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )