"""Embedding client for the Parista backend.

Generates vector embeddings for the pgvector knowledge base. All calls are
API-based — no local model weights.
"""

from typing import Any

import google.generativeai as genai

from backend.config import settings
from backend.modules.chat.logging import get_logger

logger = get_logger("embeddings")

# Default embedding model and dimension (matches schema.sql vector(768))
EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIM = 768


def get_embedding(text: str) -> list[float]:
    """Generate an embedding vector for the given text.

    Requires ``GEMINI_API_KEY`` to be set in the environment.
    """
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY must be configured in the environment "
            "(see backend/.env.example)"
        )
    genai.configure(api_key=settings.gemini_api_key)
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        output_dimensionality=EMBEDDING_DIM,
    )
    embedding = result["embedding"]
    logger.info("generated_embedding", model=EMBEDDING_MODEL)
    return embedding


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts."""
    return [get_embedding(text) for text in texts]