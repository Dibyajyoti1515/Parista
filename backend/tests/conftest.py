"""Shared pytest configuration for the Parista backend tests.

This file only exists to make the tests self-contained and runnable without
installing the ``backend`` package. It inserts the repository root onto
``sys.path`` so that ``import backend`` resolves regardless of how pytest is
invoked (``pytest backend/tests`` vs ``python -m pytest``).

No external services are started or contacted here. External calls (Supabase
pgvector / Gemini) are mocked within individual test modules.
"""

import sys
from pathlib import Path

# e:/Parista  ←  parents[2] from backend/tests/conftest.py
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest  # noqa: E402  (import after sys.path is configured)


@pytest.fixture
def client():
    """A FastAPI ``TestClient`` for the Parista app (no live server needed).

    Importing ``backend.main`` builds the real application and instantiates the
    agent singletons, but performs **no** network calls at import time. Any call
    that would reach Supabase or Gemini is mocked inside the individual tests.
    """
    from backend.main import app
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client
