"""Smoke tests for the Parista backend.

Confirms that:
  * every agent module imports without error (no ``ImportError``), and
  * the FastAPI application ``backend.main:app`` loads successfully via
    FastAPI's ``TestClient`` and exposes the ``/api/analyze`` route.

These tests make **no** network calls. ``GET /api/health`` is a pure handler
that returns a static payload.
"""

import importlib

import pytest
from fastapi import FastAPI

AGENT_MODULES = [
    "backend.agents.safety_agent",
    "backend.agents.classifier_agent",
    "backend.agents.coordinator",
    "backend.agents.retrieval_agent",
    "backend.agents.reasoning_agent",
    "backend.agents.style_agent",
]


@pytest.mark.parametrize("module_name", AGENT_MODULES)
def test_agent_module_imports_without_error(module_name):
    """Each agent module must import cleanly."""
    module = importlib.import_module(module_name)
    assert module is not None


def test_main_app_loads():
    """``backend.main:app`` must be a FastAPI application instance."""
    from backend.main import app

    assert isinstance(app, FastAPI)


def test_health_endpoint(client):
    """``GET /api/health`` must return 200 with a status payload."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_route_is_registered():
    """``POST /api/analyze`` must be registered on the application."""
    from backend.main import app

    registered_paths = {route.path for route in app.routes if hasattr(route, "path")}
    assert "/api/analyze" in registered_paths
