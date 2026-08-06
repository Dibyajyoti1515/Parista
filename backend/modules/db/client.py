"""Supabase/Postgres database client.

Provides a thin wrapper around the Supabase client for the Parista backend.
Requires ``SUPABASE_URL`` and ``SUPABASE_KEY`` to be configured via the
environment (see ``backend/.env.example``).
"""

from functools import lru_cache

from supabase import Client, create_client

from backend.config import settings


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Create and cache a Supabase client instance."""
    if not settings.supabase_url or not settings.supabase_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be configured in the environment"
        )
    return create_client(settings.supabase_url, settings.supabase_key)


def get_db() -> Client:
    """Dependency-injectable accessor for FastAPI routes."""
    return get_supabase_client()