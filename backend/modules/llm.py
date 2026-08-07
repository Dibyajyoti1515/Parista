"""Gemini model client for the Parista backend.

Wraps the Google AI Studio (Gemini) API for quality-sensitive agent steps.
All calls are API-based — no local model weights.
"""

from typing import Any

import google.generativeai as genai

from backend.config import settings
from backend.modules.chat.logging import get_logger

logger = get_logger("llm")


def get_gemini_model(model_name: str = "gemini-2.0-flash") -> Any:
    """Return a configured Gemini model instance.

    Requires ``GEMINI_API_KEY`` to be set in the environment.
    """
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY must be configured in the environment "
            "(see backend/.env.example)"
        )
    genai.configure(api_key=settings.gemini_api_key)
    return genai.GenerativeModel(model_name)


def generate_text(prompt: str, model_name: str = "gemini-2.0-flash") -> str:
    """Generate text from a prompt using the Gemini API."""
    model = get_gemini_model(model_name)
    response = model.generate_content(prompt)
    logger.info("generated_text", model=model_name)
    return response.text